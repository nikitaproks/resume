import logging

from pandas import DataFrame

from core.models import UserProfile
from core.views import APIkeyViewSet, HasAPIKey
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from stocks.analysis.functions import (
    analyse_stock,
    get_stock_history,
)
from stocks.models import Stock, Subscription, State
from stocks.serializers import (
    SubscriptionSerializer,
    TelegramSubscriptionSerializer,
    TelegramSubscriptionSerializerUnsubscribe,
)
from stocks.signals.signals import analytics_done

logger = logging.getLogger(__name__)


class SubscriptionViewSet(APIkeyViewSet, mixins.ListModelMixin):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        queryset = Subscription.objects.all()
        is_active: str | None = self.request.query_params.get(
            "is_active", None
        )
        if is_active:
            queryset = queryset.filter(is_active=is_active.capitalize())
        return queryset


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
        name = serializer.validated_data.get("name")
        telegram_id = serializer.validated_data.get("telegram_id")

        try:
            user_profile = UserProfile.objects.get(telegram_id=telegram_id)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Telegram user is not registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stock, _ = Stock.objects.get_or_create(ticker=ticker, name=name)
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

    @action(detail=False, methods=["post"])
    def unsubscribe(self, request, *args, **kwargs):
        # Create serializer
        serializer = TelegramSubscriptionSerializerUnsubscribe(
            data=request.data
        )

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


class TriggerAnalysis(APIView):
    permission_classes = [HasAPIKey]

    # TODO: Make this async
    def get(self, request, format=None):
        message: str
        telegram_id = request.GET.get("telegram_id", None)

        if telegram_id:
            active_stocks = Stock.objects.filter(
                subscriptions__is_active=True,
                subscriptions__user__userprofile__telegram_id=telegram_id,
            ).distinct()
        else:
            active_stocks = Stock.objects.filter(
                subscriptions__is_active=True
            ).distinct()

        if active_stocks.count() == 0:
            message = "No active stocks"
            logger.info(message)
            return Response(
                status=status.HTTP_200_OK, data={"message": message}
            )

        for stock in active_stocks:
            logger.info(f"Analyzing {stock.ticker}")
            history: DataFrame = get_stock_history(stock)
            if history.empty:
                logger.error(f"Failed to get history for {stock.ticker}")
                continue

            # current_rsi = history["RSI"].iloc[-1]
            # current_rsi_sma14 = history["RSI_SMA14"].iloc[-1]
            current_bbands_percent = history["BBands%"].iloc[-1]
            new_state = analyse_stock(current_bbands_percent)

            if telegram_id and new_state != State.objects.get(name="Hold"):
                analytics_done.send(
                    sender=Stock.__class__,
                    instance=stock,
                    history=history,
                    telegram_ids=[telegram_id],
                    new_state=new_state,
                )
                continue

            if not telegram_id and new_state != stock.state:
                stock.state = new_state
                stock.save()
                logger.info(f"{stock} has new state: {new_state}")
                analytics_done.send(
                    sender=Stock.__class__,
                    instance=stock,
                    history=history,
                )
                continue

        return Response(status=status.HTTP_200_OK, data={"message": "success"})
