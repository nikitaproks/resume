from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from core.models import UserAPIKey, UserProfile


class APIBaseTest(APITestCase):
    def setUp(self):
        self.super_user = User.objects.create_user(
            username="testuser", password="password", is_superuser=True
        )
        self.superuser_profile = UserProfile.objects.get(user=self.super_user)
        self.superuser_profile.telegram_id = 0000
        self.superuser_profile.save()
        _, self.superuser_key = UserAPIKey.objects.create_key(
            name="test_key", user=self.super_user
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Api-Key {self.superuser_key}"
        )
