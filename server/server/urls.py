from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from contact.views import ContactViewSet
from core.views import DownloadDocument

router = DefaultRouter()
router.register(r"contacts", ContactViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    path("api/", include(router.urls)),
    path("api/download/", DownloadDocument.as_view(), name="download"),
]
