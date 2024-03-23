from unittest.mock import patch, MagicMock, ANY

from pandas import DataFrame

from django.contrib.auth.models import User
from django.test import TestCase


from core.models import UserProfile
from stocks.models import Stock, Subscription
from stocks.signals.signals import analytics_done


class TestSendTelegramNotification(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password"
        )
        self.user_profile = UserProfile.objects.get(user=self.user)
        self.user_profile.telegram_id = 0000
        self.user_profile.save()

        self.stock = Stock.objects.create(ticker="AAPL")
        self.stock_no_subscription = Stock.objects.create(ticker="MSFT")

        self.subscription = Subscription.objects.create(stock=self.stock)
        self.subscription.users.add(self.user)

    @patch("stocks.signals.signals.Subscription.objects.filter")
    def test_no_history(self, mock_filter):
        history = MagicMock()
        history.empty = True
        analytics_done.send(
            sender=Subscription.__class__,
            instance=self.subscription,
            history=history,
        )
        mock_filter.assert_not_called()

    @patch("stocks.signals.signals.TelegramAPI")
    @patch("stocks.signals.signals.get_fig_buffer")
    def test_no_active_updates(self, mock_get_fig_buffer, mock_TelegramAPI):
        self.user_profile.updates_active = False
        self.user_profile.save()
        data = [[70, 0.8, 70, 100]]
        mock_history = DataFrame(
            data, columns=["RSI", "BBands%", "RSI_SMA14", "Close"]
        )

        mock_telegram_api = mock_TelegramAPI.return_value

        analytics_done.send(
            sender=Subscription.__class__,
            instance=self.subscription,
            history=mock_history,
        )
        mock_telegram_api.send_photo_from_buffer.assert_not_called()

    @patch("stocks.signals.signals.TelegramAPI")
    @patch("stocks.signals.signals.get_fig_buffer")
    def test_subscriptions_exist(self, mock_get_fig_buffer, mock_TelegramAPI):
        data = [[70, 0.8, 70, 100]]
        mock_history = DataFrame(
            data, columns=["RSI", "BBands%", "RSI_SMA14", "Close"]
        )

        mock_telegram_api = mock_TelegramAPI.return_value

        analytics_done.send(
            sender=Subscription.__class__,
            instance=self.subscription,
            history=mock_history,
        )
        mock_telegram_api.send_photo_from_buffer.assert_called_once()

    @patch("stocks.signals.signals.TelegramAPI")
    @patch("stocks.signals.signals.get_fig_buffer")
    def test_telegram_ids_provided(
        self, mock_get_fig_buffer, mock_TelegramAPI
    ):
        data = [[70, 0.8, 70, 100]]
        mock_history = DataFrame(
            data, columns=["RSI", "BBands%", "RSI_SMA14", "Close"]
        )

        mock_telegram_api = mock_TelegramAPI.return_value

        analytics_done.send(
            sender=Subscription.__class__,
            instance=self.subscription,
            history=mock_history,
            telegram_ids=[self.user_profile.telegram_id],
        )
        mock_get_fig_buffer.assert_called_once()
        mock_telegram_api.send_photo_from_buffer.assert_called_once_with(
            self.user_profile.telegram_id, ANY, ANY
        )
