from core.serializers import UserProfileForUserSerializer
from django.contrib.auth.models import User
from rest_framework import serializers

from stocks.models import Stock, Subscription


class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileForUserSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["userprofile"]


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = "__all__"


class TelegramSubscriptionSerializer(serializers.Serializer):
    ticker = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    telegram_id = serializers.CharField(required=True)
    period = serializers.CharField(required=True)
    interval = serializers.CharField(required=True)


class TelegramSubscriptionSerializerUnsubscribe(serializers.Serializer):
    ticker = serializers.CharField(required=True)
    telegram_id = serializers.CharField(required=True)

    class Meta:
        fields = ("ticker", "telegram_id")
