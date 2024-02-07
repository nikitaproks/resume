from rest_framework import serializers

from stocks.models import Subscription, Stock


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = "__all__"


class TelegramSubscriptionSerializer(serializers.Serializer):
    ticker = serializers.CharField(required=True)
    telegram_id = serializers.CharField(required=True)

    class Meta:
        fields = ("ticker", "telegram_id")