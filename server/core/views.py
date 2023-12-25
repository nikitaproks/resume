import os

from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.models import Document


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
