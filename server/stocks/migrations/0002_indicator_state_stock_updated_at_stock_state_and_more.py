# Generated by Django 5.0.2 on 2024-02-11 16:03

import django.db.models.deletion
import stocks.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("stocks", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Indicator",
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
                ("name", models.CharField(max_length=25, unique=True)),
                ("description", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="State",
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
                ("name", models.CharField(max_length=25, unique=True)),
                ("description", models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name="stock",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="stock",
            name="state",
            field=models.ForeignKey(
                default=stocks.models.default_state,
                on_delete=django.db.models.deletion.SET_DEFAULT,
                related_name="stocks",
                to="stocks.state",
            ),
        ),
        migrations.CreateModel(
            name="StateIndicator",
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
                ("lower_threshold", models.FloatField()),
                ("upper_threshold", models.FloatField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "indicator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="stocks.indicator",
                    ),
                ),
                (
                    "state",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="stocks.state"
                    ),
                ),
            ],
            options={
                "unique_together": {("state", "indicator")},
            },
        ),
        migrations.AddField(
            model_name="state",
            name="indicators",
            field=models.ManyToManyField(
                related_name="states",
                through="stocks.StateIndicator",
                to="stocks.indicator",
            ),
        ),
    ]
