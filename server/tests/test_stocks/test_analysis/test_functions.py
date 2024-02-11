from django.test import TestCase
from stocks.analysis.functions import analyse_stock
from stocks.models import Indicator, State, StateIndicator


class TestAnalyseStock(TestCase):
    def setUp(self):
        self.rsi = Indicator.objects.create(
            name="RSI", description="Relative Strength Index"
        )
        self.bbands = Indicator.objects.create(
            name="BBands%", description="Bollinger Bands Percentage"
        )
        self.strong_buy = State.objects.create(
            name="Strong Buy", description="Strongly advised to buy stock"
        )
        self.strong_sell = State.objects.create(
            name="Strong Sell", description="Strongly advised to sell stock"
        )

        self.strong_buy_rsi = StateIndicator.objects.create(
            state=self.strong_buy,
            indicator=self.rsi,
            lower_threshold=0,
            upper_threshold=30,
        )

        self.strong_buy_bbands = StateIndicator.objects.create(
            state=self.strong_buy,
            indicator=self.bbands,
            lower_threshold=-1.0,
            upper_threshold=0.2,
        )

        self.strong_sell_rsi = StateIndicator.objects.create(
            state=self.strong_sell,
            indicator=self.rsi,
            lower_threshold=70,
            upper_threshold=300,
        )

        self.strong_sell_bbands = StateIndicator.objects.create(
            state=self.strong_sell,
            indicator=self.bbands,
            lower_threshold=0.8,
            upper_threshold=2.0,
        )

    def test_strong_buy(self):
        result = analyse_stock(20, 0.1)
        self.assertEqual(result, self.strong_buy)

    def test_strong_sell(self):
        result = analyse_stock(90, 1.0)
        self.assertEqual(result, self.strong_sell)
