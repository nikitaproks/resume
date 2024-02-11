import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver
from stocks.analysis.functions import get_fig_buffer, get_stock_history
from stocks.models import Stock, Subscription
from stocks.signals.classes import TelegramAPI

from server.settings import TELEGRAM_BOT_TOKEN

logger = logging.getLogger(__name__)


# Write tests
@receiver(pre_save, sender=Stock)
def send_telegram_notification(instance: Stock, **kwargs):
    if not instance.pk:
        return

    old_instance = Stock.objects.get(pk=instance.pk)
    if old_instance.state == instance.state or instance.state == "hold":
        return

    # Getting needed data
    history = get_stock_history(instance)
    buffer = get_fig_buffer(history, instance.ticker)
    telegram_ids = (
        Subscription.objects.filter(stock=instance, is_active=True)
        .select_related("user__userprofile")
        .values_list("user__userprofile__telegram_id", flat=True)
    )
    current_rsi = history["RSI"].iloc[-1]
    current_bbands_per = history["BB_percent"].iloc[-1]

    # Sending telegram messages
    telegram_api = TelegramAPI(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
    )
    for telegram_id in telegram_ids:
        message = (
            f"It is a good time to {instance.state} {instance.ticker}."
            f"\nRSI: {current_rsi}, BBands%: {current_bbands_per}"
        )
        telegram_api.send_photo_from_buffer(telegram_id, buffer, message)
        logger.info(f"Sent message to {telegram_id}")
