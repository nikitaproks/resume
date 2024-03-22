from unittest.mock import patch
from pandas import DataFrame

from django.contrib.auth.models import User
from rest_framework import status


from core.models import UserProfile
from stocks.models import Stock, Subscription, State
from tests.base_case import APIBaseTest


class TestTelegramSubscription(APIBaseTest):
    def setUp(self):
        super().setUp()
        self.url = "/api/telegram/subscriptions/"
        self.telegram_id = 1234

        self.user = User.objects.create(username="test_user", password="1234")

        self.user_profile = UserProfile.objects.get(user=self.user)
        self.user_profile.telegram_id = self.telegram_id
        self.user_profile.save()

        self.stock = Stock.objects.create(ticker="AAPL", name="Apple Inc.")
        self.subscription = Subscription.objects.create(
            user=self.user, stock=self.stock
        )

        self.post_data = {
            "ticker": "QBIT",
            "name": "Some name",
            "telegram_id": self.user_profile.telegram_id,
        }

    def test_list_no_telegram_id(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_telegram_id_not_registered(self):
        response = self.client.get(f"{self.url}?telegram_id=123")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_success(self):
        response = self.client.get(
            f"{self.url}?telegram_id={self.telegram_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_no_telegram_id(self):
        self.post_data.pop("telegram_id")
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_telegram_id_not_registered(self):
        self.post_data["telegram_id"] = 123
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_limit_reached(self):
        googl = Stock.objects.create(ticker="GOOGL", name="Alphabet Inc.")
        msft = Stock.objects.create(
            ticker="MSFT", name="Microsoft Corporation"
        )
        amzn = Stock.objects.create(ticker="AMZN", name="Amazon.com Inc.")
        tsla = Stock.objects.create(ticker="TSLA", name="Tesla Inc.")
        Subscription.objects.create(user=self.user, stock=googl)
        Subscription.objects.create(user=self.user, stock=msft)
        Subscription.objects.create(user=self.user, stock=amzn)
        Subscription.objects.create(user=self.user, stock=tsla)

        # Make POST request to the subscribe endpoint
        response = self.client.post(self.url, self.post_data)

        # Check that the response is 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_already_subscribed(self):
        self.post_data["ticker"] = self.subscription.stock.ticker
        self.post_data["name"] = self.subscription.stock.name
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_already_subscribed_inactive(self):
        self.subscription.is_active = False
        self.subscription.save()
        self.post_data["ticker"] = self.subscription.stock.ticker
        self.post_data["name"] = self.subscription.stock.name
        self.post_data["period"] = "3mo"
        self.post_data["interval"] = "1d"

        response = self.client.post(self.url, self.post_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.subscription.refresh_from_db()
        self.assertTrue(self.subscription.is_active)

    def test_create_success(self):
        self.post_data["period"] = "3mo"
        self.post_data["interval"] = "1d"
        # Make POST request to the subscribe endpoint
        response = self.client.post(self.url, self.post_data)

        # Check that the response is 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        stock_query = Stock.objects.filter(ticker=self.post_data["ticker"])
        self.assertTrue(stock_query.exists())
        self.assertTrue(
            Subscription.objects.filter(
                user=self.user,
                stock=stock_query.first(),
                period="3mo",
                interval="1d",
            ).exists()
        )

    def test_unsubscribe_no_telegram_id(self):
        response = self.client.post(f"{self.url}unsubscribe/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsubscribe_telegram_id_not_registered(self):
        self.post_data["telegram_id"] = 123
        response = self.client.post(f"{self.url}unsubscribe/", self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsubscribe_no_stock(self):
        response = self.client.post(f"{self.url}unsubscribe/", self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Stock does not exist"})

    def test_unsubscribe_not_subscribed(self):
        Stock.objects.create(ticker=self.post_data["ticker"])
        response = self.client.post(f"{self.url}unsubscribe/", self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {"error": "User is not subscribed to this stock"}
        )

    def test_unsubscribe_success(self):
        self.post_data["ticker"] = self.subscription.stock.ticker
        response = self.client.post(f"{self.url}unsubscribe/", self.post_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.subscription.refresh_from_db()
        self.assertFalse(self.subscription.is_active)


class TestTriggerAnalysis(APIBaseTest):
    def setUp(self):
        super().setUp()
        self.url = "/api/analysis/"
        self.mock_analytics_done = patch("stocks.views.analytics_done").start()
        self.mock_get_stock_history = patch(
            "stocks.views.get_stock_history"
        ).start()

        self.user = User.objects.create(username="test_user", password="1234")
        self.user_profile = UserProfile.objects.get(user=self.user)
        self.user_profile.telegram_id = 1234
        self.user_profile.save()

    def test_no_active_stocks(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "No active stocks"})

    def test_telegram_id_provided_no_active_stocks(self):
        response = self.client.get(self.url + "?telegram_id=1234")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "No active stocks"})

    @patch("stocks.views.analyse_stock")
    def test_telegram_id_provided_current_state_hold(self, mock_analyse_stock):
        stock = Stock.objects.create(ticker="AAPL")
        Subscription.objects.create(user=self.user, stock=stock)

        data = [[70, 0.8, 70, 100]]
        mock_history = DataFrame(
            data, columns=["RSI", "BBands%", "RSI_SMA14", "Close"]
        )

        self.mock_get_stock_history.return_value = mock_history
        mock_analyse_stock.return_value = stock.state

        response = self.client.get(
            self.url + f"?telegram_id={self.user_profile.telegram_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mock_analytics_done.send.assert_not_called()

    @patch("stocks.views.analyse_stock")
    def test_telegram_id_provided_current_state_not_hold(
        self, mock_analyse_stock
    ):
        state = State.objects.create(name="Buy")
        stock = Stock.objects.create(ticker="AAPL", state=state)
        Subscription.objects.create(user=self.user, stock=stock)

        data = [[70, 0.8, 70, 100]]
        mock_history = DataFrame(
            data, columns=["RSI", "BBands%", "RSI_SMA14", "Close"]
        )

        self.mock_get_stock_history.return_value = mock_history
        mock_analyse_stock.return_value = stock.state

        response = self.client.get(
            self.url + f"?telegram_id={self.user_profile.telegram_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mock_analytics_done.send.assert_called_once_with(
            sender=Stock.__class__,
            instance=stock,
            history=mock_history,
            telegram_ids=[str(self.user_profile.telegram_id)],
            new_state=state,
        )

        self.assertEqual(response.data, {"message": "success"})

    @patch("stocks.views.analyse_stock")
    def test_current_state_not_changed(self, mock_analyse_stock):
        stock = Stock.objects.create(ticker="AAPL")
        Subscription.objects.create(user=self.user, stock=stock)

        data = [[70, 0.8, 70, 100]]
        mock_history = DataFrame(
            data, columns=["RSI", "BBands%", "RSI_SMA14", "Close"]
        )

        self.mock_get_stock_history.return_value = mock_history
        mock_analyse_stock.return_value = stock.state

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mock_analytics_done.send.assert_not_called()
        self.assertEqual(response.data, {"message": "success"})

    @patch("stocks.views.analyse_stock")
    def test_current_state_changed(self, mock_analyse_stock):
        new_state = State.objects.create(name="Buy")
        stock = Stock.objects.create(ticker="AAPL")
        Subscription.objects.create(user=self.user, stock=stock)

        data = [[70, 0.8, 70, 100]]
        mock_history = DataFrame(
            data, columns=["RSI", "BBands%", "RSI_SMA14", "Close"]
        )

        self.mock_get_stock_history.return_value = mock_history
        mock_analyse_stock.return_value = new_state

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mock_analytics_done.send.assert_called_once_with(
            sender=Stock.__class__,
            instance=stock,
            history=mock_history,
        )
        self.assertEqual(response.data, {"message": "success"})
        stock.refresh_from_db()
        self.assertEqual(stock.state, new_state)
