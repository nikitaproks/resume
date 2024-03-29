from django.contrib.auth.models import User
from django.db import models


def default_state():
    state, _ = State.objects.get_or_create(name="Hold")
    return state.id


class Indicator(models.Model):
    name = models.CharField(max_length=25, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=25, unique=True)
    description = models.TextField()
    indicators = models.ManyToManyField(  # type: ignore
        Indicator, through="StateIndicator", related_name="states"
    )

    def __str__(self):
        return self.name


class StateIndicator(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    lower_threshold = models.FloatField()
    upper_threshold = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("state", "indicator"),)

    def __str__(self):
        return f"{self.state} - {self.indicator}"


class Stock(models.Model):
    name = models.CharField(max_length=100, default="No name")
    ticker = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ticker


class Subscription(models.Model):
    users = models.ManyToManyField(User, related_name="subscriptions")
    stock = models.ForeignKey(
        Stock, on_delete=models.CASCADE, related_name="subscriptions"
    )
    state = models.ForeignKey(
        State,
        on_delete=models.SET_DEFAULT,
        default=default_state,
        related_name="stocks",
    )
    period = models.CharField(max_length=10, default="6mo")
    interval = models.CharField(max_length=10, default="1d")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("stock", "period", "interval"),)

    def __str__(self):
        return f"{self.stock} {self.interval}/{self.period}"
