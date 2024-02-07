from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from core.views import DownloadDocument, UserViewSet
from contact.views import ContactViewSet
from stocks.views import TelegramSubscriptionViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"contacts", ContactViewSet)
router.register(r"telegram/subscriptions", TelegramSubscriptionViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    path("api/download/", DownloadDocument.as_view(), name="download"),
    path("api/", include(router.urls)),
]
