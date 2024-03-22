from django.contrib.auth.models import User

from core.models import UserProfile
from tests.base_case import APIBaseTest


class TestUserProfileEndpoints(APIBaseTest):
    def setUp(self):
        super().setUp()
        self.url = "/api/userprofiles/"

        self.user = User.objects.create(username="test_user", password="1234")
        self.user_profile = UserProfile.objects.get(user=self.user)
        self.user_profile.telegram_id = 1234
        self.user_profile.save()

    def test_change_updates_payload_not_valid(self):
        response = self.client.post(
            self.url + "change_updates/",
            data={"telegram_id": self.user_profile.telegram_id},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"error": {"updates_active": ["This field is required."]}},
        )

    def test_change_updates_user_profile_does_not_exist(self):
        response = self.client.post(
            self.url + "change_updates/",
            data={"telegram_id": 2222, "updates_active": 1},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {"error": "Telegram user is not registered"}
        )

    def test_change_updates_success(self):
        response = self.client.post(
            self.url + "change_updates/",
            data={
                "telegram_id": self.user_profile.telegram_id,
                "updates_active": 0,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.user_profile.refresh_from_db()
        self.assertFalse(self.user_profile.updates_active)
