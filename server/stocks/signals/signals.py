import logging

from django.dispatch import Signal, receiver
from stocks.analysis.functions import get_fig_buffer
from stocks.models import Stock, Subscription
from stocks.signals.classes import TelegramAPI

from server.settings import TELEGRAM_TOKEN

logger = logging.getLogger(__name__)

analytics_done = Signal()


# Write tests
@receiver(analytics_done)
def send_telegram_notification(instance: Stock, history, **kwargs):
    if not history:
        logger.error("Stock history was not provided")
        return

    buffer = get_fig_buffer(history, instance.ticker)
    telegram_ids = (
        Subscription.objects.filter(stock=instance, is_active=True)
        .select_related("user__userprofile")
        .values_list("user__userprofile__telegram_id", flat=True)
    )
    current_rsi = history["RSI"].iloc[-1]
    current_bbands_percent = history["BB_percent"].iloc[-1]

    # Sending telegram messages
    telegram_api = TelegramAPI(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}")
    for telegram_id in telegram_ids:
        message = (
            f"It is a good time to {instance.state} {instance.ticker}."
            f"\nRSI: {current_rsi}, BBands%: {current_bbands_percent}"
        )
        telegram_api.send_photo_from_buffer(telegram_id, buffer, message)
        logger.info(f"Sent message to {telegram_id}")
