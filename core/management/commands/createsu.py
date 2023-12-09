from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os
from dotenv import load_dotenv

load_dotenv()


class Command(BaseCommand):
    help = "Create a superuser"

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser {username} created successfully."
                )
            )
        else:
            self.stdout.write("Superuser already exists.")
