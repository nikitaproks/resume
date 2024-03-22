from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from rest_framework_api_key.models import AbstractAPIKey


def get_invite_code():
    return get_random_string(length=16)


class InviteCode(models.Model):
    code = models.CharField(
        unique=True, editable=False, default=get_invite_code
    )
    is_usable = models.BooleanField(default=True)
    owner = models.OneToOneField(
        User,
        editable=False,
        unique=True,
        on_delete=models.CASCADE,
        related_name="invite_code",
    )

    def save(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        if not self.pk and user:
            self.owner = user
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="userprofile"
    )
    invite_code = models.ForeignKey(
        InviteCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invited_user_profiles",
    )
    telegram_id = models.IntegerField(blank=True, null=True, unique=True)
    subscriptions_limit = models.PositiveIntegerField(default=5)
    updates_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class UserAPIKey(AbstractAPIKey):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )

    class Meta(AbstractAPIKey.Meta):
        verbose_name = "User API key"
        verbose_name_plural = "User API keys"


class Document(models.Model):
    title = models.CharField(max_length=100, unique=True)
    file = models.FileField(upload_to="documents/")
    public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
