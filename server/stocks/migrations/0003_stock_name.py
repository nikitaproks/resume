# Generated by Django 5.0.2 on 2024-03-03 12:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("stocks", "0002_indicator_state_stock_updated_at_stock_state_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="stock",
            name="name",
            field=models.CharField(default="No name", max_length=100),
        ),
    ]
