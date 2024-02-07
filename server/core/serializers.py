from django.contrib.auth.models import User
from rest_framework import serializers


class TelegramUserSerializer(serializers.ModelSerializer):
    telegram_id = serializers.IntegerField(required=True)
    invite_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["email", "telegram_id", "invite_code"]
