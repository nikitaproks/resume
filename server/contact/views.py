from rest_framework import viewsets, permissions
from rest_framework.response import Response

from contact.models import Contact
from contact.serializers import ContactSerializer
from contact.functions import (
    verify_recaptcha,
)


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [permissions.AllowAny]
            return [permission() for permission in permission_classes]
        else:
            return super().get_permissions()

    # TODO: Register and add captcha
    # def create(self, request, *args, **kwargs):
    #     recaptcha_response = request.data.get("recaptcha")
    #     if not verify_recaptcha(recaptcha_response):
    #         return Response({"error": "Invalid reCAPTCHA."}, status=400)
    #     return super().create(request, *args, **kwargs)
