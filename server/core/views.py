import os

from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_api_key.permissions import BaseHasAPIKey

from core.models import Document, InviteCode, UserAPIKey, UserProfile
from core.serializers import TelegramUserSerializer


class HasAPIKey(BaseHasAPIKey):
    model = UserAPIKey  # Or a custom model

    def get_key(self, request):
        if request.META.get("HTTP_AUTHORIZATION"):
            return request.META["HTTP_AUTHORIZATION"].split()[1]
        return None


class APIkeyViewSet(GenericViewSet):
    permission_classes = [HasAPIKey]

    def get_queryset(self):
        key = self.request.META["HTTP_AUTHORIZATION"].split()[1]
        api_key = UserAPIKey.objects.get_from_key(key)

        if not self.queryset:
            raise NotImplementedError("queryset not implemented")

        user = api_key.user
        if user.is_superuser:
            return self.queryset

        return self.queryset.filter(user=user)


class UserViewSet(APIkeyViewSet, CreateModelMixin, RetrieveModelMixin):
    queryset = User.objects.all()
    serializer_class = TelegramUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        telegram_id = serializer.validated_data.pop("telegram_id")
        invite_code_str = serializer.validated_data.pop("invite_code")
        email = serializer.validated_data.pop("email")

        user_query = User.objects.filter(email=email)
        if user_query.exists():
            return Response(
                {"detail": "User already exists."},
                status=status.HTTP_409_CONFLICT,
            )

        try:
            invite_code = InviteCode.objects.get(
                code=invite_code_str, is_usable=True
            )
        except InviteCode.DoesNotExist:
            return Response(
                {"detail": "Valid invite code not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User(
            username=email,
            email=email,
        )
        user.set_unusable_password()
        user.save()

        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response(
                {"detail": "User profile does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_profile.telegram_id = telegram_id
        user_profile.invite_code = invite_code
        user_profile.save()
        return Response(
            serializer.validated_data, status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["get"])
    def by_telegram_id(self, request):
        telegram_id = request.query_params.get("telegram_id")
        if not telegram_id:
            return Response(
                {"detail": "No telegram_id provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_profile = UserProfile.objects.get(telegram_id=telegram_id)
            user = user_profile.user
            return Response(
                {"email": user.email, "telegram_id": user_profile.telegram_id},
                status=status.HTTP_200_OK,
            )
        except UserProfile.DoesNotExist:
            return Response(
                {"detail": "User does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )


class DownloadDocument(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        title = request.query_params.get("title", None)

        if not title:
            return Response(
                {"error": "Title parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = Document.objects.filter(title=title)

        if not queryset.exists():
            return Response(
                {"error": "Document does not exist in the database."},
                status=status.HTTP_404_NOT_FOUND,
            )

        document = queryset.first()

        if not document.public:
            return Response(
                {"error": "Document is not public."},
                status=status.HTTP_403_FORBIDDEN,
            )

        file_path = document.file.path

        if not os.path.exists(file_path):
            return Response(
                {"error": "File does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            # Read the PDF file in binary mode
            with open(file_path, "rb") as pdf:
                response = HttpResponse(
                    pdf.read(), content_type="application/pdf"
                )
                response[
                    "Content-Disposition"
                ] = f'attachment; filename="{document.title}.pdf"'
                return response
        except Exception:
            return Response(
                {"error": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
