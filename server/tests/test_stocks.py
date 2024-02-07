from django.contrib.auth.models import User
from rest_framework import status

from tests.base import APIBaseTest

from core.models import UserProfile
from stocks.models import Subscription, Stock


class TestTelegramSubscription(APIBaseTest):
    def setUp(self):
        super().setUp()
        self.url = "/api/telegram/subscriptions/"
        self.telegram_id = 1234

        self.user = User.objects.create(username="test_user", password="1234")

        self.user_profile = UserProfile.objects.get(user=self.user)
        self.user_profile.telegram_id = self.telegram_id
        self.user_profile.save()

        self.stock = Stock.objects.create(ticker="AAPL")
        self.subscription = Subscription.objects.create(
            user=self.user, stock=self.stock
        )

        self.post_data = {
            "ticker": "QBIT",
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
        googl = Stock.objects.create(ticker="GOOGL")
        msft = Stock.objects.create(ticker="MSFT")
        amzn = Stock.objects.create(ticker="AMZN")
        tsla = Stock.objects.create(ticker="TSLA")
        Subscription.objects.create(user=self.user, stock=googl)
        Subscription.objects.create(user=self.user, stock=msft)
        Subscription.objects.create(user=self.user, stock=amzn)
        Subscription.objects.create(user=self.user, stock=tsla)

        # Make POST request to the subscribe endpoint
        response = self.client.post(self.url, self.post_data)

        # Check that the response is 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_already_subscribed(self):
        self.post_data["ticker"] = "AAPL"
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_already_subscribed_inactive(self):
        self.subscription.is_active = False
        self.subscription.save()
        self.post_data["ticker"] = self.subscription.stock.ticker

        response = self.client.post(self.url, self.post_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.subscription.refresh_from_db()
        self.assertTrue(self.subscription.is_active)

    def test_create_success(self):
        # Make POST request to the subscribe endpoint
        response = self.client.post(self.url, self.post_data)

        # Check that the response is 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        stock_query = Stock.objects.filter(ticker=self.post_data["ticker"])
        self.assertTrue(stock_query.exists())
        self.assertTrue(
            Subscription.objects.filter(
                user=self.user, stock=stock_query.first()
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
