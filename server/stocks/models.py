from django.contrib.auth.models import User
from django.db import models


def default_state():
    state, _ = State.objects.get_or_create(name="Hold")
    return state


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
    indicators = models.ManyToManyField(
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
    ticker = models.CharField(max_length=10, unique=True)
    state = models.ForeignKey(
        State,
        on_delete=models.SET_DEFAULT,
        default=default_state,
        related_name="stocks",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ticker


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriptions"
    )
    stock = models.ForeignKey(
        Stock, on_delete=models.CASCADE, related_name="subscriptions"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("user", "stock"),)

    def __str__(self):
        return f"{self.user} - {self.stock}"
