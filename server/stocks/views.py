from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action

from core.models import UserProfile
from core.views import APIkeyViewSet

from stocks.models import Stock, Subscription
from stocks.serializers import (
    TelegramSubscriptionSerializer,
    SubscriptionSerializer,
)


class TelegramSubscriptionViewSet(
    APIkeyViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    queryset = Subscription.objects.all()
    serializer_class = TelegramSubscriptionSerializer

    def list(self, request, *args, **kwargs):
        # Create serializer
        telegram_id = request.query_params.get("telegram_id")
        if not telegram_id:
            return Response(
                {"error": "Telegram ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get user profile
        try:
            user_profile = UserProfile.objects.get(telegram_id=telegram_id)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Telegram user is not registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription_query = Subscription.objects.filter(
            user=user_profile.user, is_active=True
        )

        return Response(
            SubscriptionSerializer(subscription_query, many=True).data,
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        # Create serializer
        serializer = TelegramSubscriptionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        # Get validated data
        ticker = serializer.validated_data.get("ticker")
        telegram_id = serializer.validated_data.get("telegram_id")

        try:
            user_profile = UserProfile.objects.get(telegram_id=telegram_id)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Telegram user is not registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stock, _ = Stock.objects.get_or_create(ticker=ticker)
        if (
            user_profile.user.subscriptions.count()
            >= user_profile.subscriptions_limit
        ):
            return Response(
                {"error": "User has exceeded the subscription limit of 5"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription, created = Subscription.objects.get_or_create(
            user=user_profile.user, stock=stock
        )

        if not created:
            if subscription.is_active:
                return Response(
                    {"error": "User is already subscribed this stock"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                subscription.is_active = True
                subscription.save()

        return Response(
            {"success": "User subscribed to stock"},
            status=status.HTTP_201_CREATED,
        )

    # TODO: Implement tests
    @action(detail=False, methods=["post"])
    def unsubscribe(self, request, *args, **kwargs):
        # Create serializer
        serializer = TelegramSubscriptionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        # Get validated data
        ticker = serializer.validated_data.get("ticker")
        telegram_id = serializer.validated_data.get("telegram_id")

        # Get user profile
        try:
            user_profile = UserProfile.objects.get(telegram_id=telegram_id)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Telegram user is not registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get stock
        try:
            stock = Stock.objects.get(ticker=ticker)
        except Stock.DoesNotExist:
            return Response(
                {"error": "Stock does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            subscription = Subscription.objects.get(
                user=user_profile.user, stock=stock
            )
        except Subscription.DoesNotExist:
            return Response(
                {"error": "User is not subscribed to this stock"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.is_active = False
        subscription.save()

        return Response(
            {"success": "User unsubscribed from stock"},
            status=status.HTTP_200_OK,
        )
