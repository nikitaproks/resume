import logging

from pandas import DataFrame

from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import UserProfile
from core.views import APIkeyViewSet, HasAPIKey

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
            users=user_profile.user
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
        period = serializer.validated_data.get("period")
        interval = serializer.validated_data.get("interval")

        # Get if telegram user is registered
        try:
            user_profile = UserProfile.objects.get(telegram_id=telegram_id)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Telegram user is not registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if subscription limit reached
        if (
            user_profile.user.subscriptions.count()
            >= user_profile.subscriptions_limit
        ):
            return Response(
                {"error": "User has exceeded the subscription limit of 5"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get if stock or subscription exists
        stock, _ = Stock.objects.get_or_create(ticker=ticker, name=name)
        subscription, _ = Subscription.objects.get_or_create(
            stock=stock,
            period=period,
            interval=interval,
        )

        # Check if user is already subscribed
        if subscription.users.filter(id=user_profile.user.id).exists():
            return Response(
                {"error": "User is already subscribed this stock"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.users.add(user_profile.user)
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

        # Get if user is subscribed
        try:
            subscription = Subscription.objects.get(
                users=user_profile.user, stock__ticker=ticker
            )
        except Subscription.DoesNotExist:
            return Response(
                {"error": "User is not subscribed to this stock"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.users.remove(user_profile.user)

        return Response(
            {"success": "User unsubscribed from stock"},
            status=status.HTTP_200_OK,
        )


class TriggerAnalysis(APIView):
    permission_classes = [HasAPIKey]

    # TODO: Make this async
    def get(self, _, format=None):
        active_subscriptions = Subscription.objects.all()
        if active_subscriptions.count() == 0:
            logger.info("No active subscriptions")
            return Response(
                status=status.HTTP_200_OK,
                data={"message": "No active subscriptions"},
            )

        for sub in active_subscriptions:
            logger.info(f"Analyzing {sub.stock.ticker}")
            history: DataFrame = get_stock_history(sub)
            if history.empty:
                logger.error(f"Failed to get history for {sub.stock.ticker}")
                continue

            current_bbands_percent = history["BBands%"].iloc[-1]
            new_state = analyse_stock(current_bbands_percent)

            if new_state != sub.state:
                sub.state = new_state
                sub.save()
                logger.info(
                    f"{sub.stock} {sub.interval}/{sub.period} has new state: {new_state}"
                )
                analytics_done.send(
                    sender=Subscription.__class__,
                    instance=sub,
                    history=history,
                )

        return Response(status=status.HTTP_200_OK, data={"message": "success"})


class TriggerUserAnalysis(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request, format=None):
        telegram_id = request.GET.get("telegram_id", None)

        active_subscriptions = Subscription.objects.filter(
            users__userprofile__telegram_id=telegram_id,
        )

        if active_subscriptions.count() == 0:
            logger.info("No active subscriptions")
            return Response(
                status=status.HTTP_200_OK,
                data={"message": "No active subscriptions"},
            )

        for sub in active_subscriptions:
            logger.info(f"Analyzing {sub.stock.ticker}")
            history: DataFrame = get_stock_history(sub)
            if history.empty:
                logger.error(f"Failed to get history for {sub.stock.ticker}")
                continue

            current_bbands_percent = history["BBands%"].iloc[-1]
            new_state = analyse_stock(current_bbands_percent)

            if new_state != State.objects.get(name="Hold"):
                analytics_done.send(
                    sender=Subscription.__class__,
                    instance=sub,
                    history=history,
                    telegram_ids=[telegram_id],
                    new_state=new_state,
                )

        return Response(status=status.HTTP_200_OK, data={"message": "success"})
