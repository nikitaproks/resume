# Generated by Django 5.0 on 2024-02-04 01:11

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="UserAPIKey",
            fields=[
                (
                    "id",
                    models.CharField(
                        editable=False,
                        max_length=150,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("prefix", models.CharField(editable=False, max_length=8, unique=True)),
                ("hashed_key", models.CharField(editable=False, max_length=150)),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "name",
                    models.CharField(
                        default=None,
                        help_text="A free-form name for the API key. Need not be unique. 50 characters max.",
                        max_length=50,
                    ),
                ),
                (
                    "revoked",
                    models.BooleanField(
                        blank=True,
                        default=False,
                        help_text="If the API key is revoked, clients cannot use it anymore. (This cannot be undone.)",
                    ),
                ),
                (
                    "expiry_date",
                    models.DateTimeField(
                        blank=True,
                        help_text="Once API key expires, clients cannot use it anymore.",
                        null=True,
                        verbose_name="Expires",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="api_keys",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "User API key",
                "verbose_name_plural": "User API keys",
                "ordering": ("-created",),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "telegram_id",
                    models.IntegerField(blank=True, null=True, unique=True),
                ),
                ("subscriptions_limit", models.PositiveIntegerField(default=5)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="userprofile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
