from contact.views import ContactViewSet
from core.views import DownloadDocument, UserViewSet
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from stocks.views import (
    SubscriptionViewSet,
    TelegramSubscriptionViewSet,
    TriggerAnalysis,
)

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"contacts", ContactViewSet)
router.register(r"telegram/subscriptions", TelegramSubscriptionViewSet)
router.register(r"subscriptions", SubscriptionViewSet)

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
    path("api/analysis/", TriggerAnalysis.as_view(), name="trigger-analysis"),
]
