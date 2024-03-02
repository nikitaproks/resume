import logging

from pandas import DataFrame

from django.dispatch import Signal, receiver
from stocks.analysis.functions import get_fig_buffer
from stocks.models import Stock, Subscription
from stocks.signals.classes import TelegramAPI

from server.settings import TELEGRAM_TOKEN

logger = logging.getLogger(__name__)

analytics_done = Signal()


@receiver(analytics_done)
def send_telegram_notification(
    instance: Stock,
    history: DataFrame,
    telegram_ids: list[int] | None = None,
    **kwargs,
):
    if history.empty:
        logger.error("Stock history was not provided")
        return

    if not telegram_ids:
        telegram_ids = list(
            Subscription.objects.filter(stock=instance, is_active=True)
            .select_related("user__userprofile")
            .values_list("user__userprofile__telegram_id", flat=True)
        )

        if not telegram_ids:
            logger.info(f"No subscriptions for {instance.ticker}")
            return

    current_rsi = history["RSI"].iloc[-1]
    current_rsi_sma14 = history["RSI_SMA14"].iloc[-1]
    current_bbands_percent = history["BBands%"].iloc[-1]
    current_price = history["Close"].iloc[-1]

    # Sending telegram messages
    buffer = get_fig_buffer(history, instance.ticker)
    telegram_api = TelegramAPI(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}")
    for telegram_id in telegram_ids:
        message = (
            f"{instance.state} {instance.ticker}"
            f"\nPrice: {current_price:.2f}\nRSI: {current_rsi:.2f}\nRSI_SMA14: {current_rsi_sma14:.2f}\nBBands%: {current_bbands_percent:.2f}"
        )
        telegram_api.send_photo_from_buffer(telegram_id, buffer, message)
        logger.info(f"Sent message to {telegram_id}")
