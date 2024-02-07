from django.contrib.auth.models import User
from rest_framework import status

from tests.base import APIBaseTest

from core.models import UserProfile, InviteCode


class TestSubscription(APIBaseTest):
    def setUp(self):
        super().setUp()
        self.url = "/api/users/"
        self.telegram_id = 1234

        self.user = User.objects.create(username="test_user", password="1234")
        self.invite_code = InviteCode.objects.create(owner=self.user)

    def test_create_no_invite_code(self):
        data = {
            "email": "test@email.com",
            "telegram_id": self.telegram_id,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"invite_code": ["This field is required."]}
        )

    def test_create_user_exists(self):
        data = {
            "email": self.user.email,
            "telegram_id": self.telegram_id,
            "invite_code": self.invite_code.code,
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            response.json(),
            {"detail": "User already exists."},
        )

    def test_create_wrong_invite_code(self):
        data = {
            "email": "test@email.com",
            "telegram_id": 9999,
            "invite_code": "wrong_code",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"detail": "Valid invite code not found."},
        )

    def test_create(self):
        data = {
            "email": "test@email.com",
            "telegram_id": self.telegram_id,
            "invite_code": self.invite_code.code,
        }

        # Make POST request to the subscribe endpoint
        response = self.client.post(self.url, data)

        # Check that the response is 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        userprofile_query = UserProfile.objects.filter(
            telegram_id=data["telegram_id"]
        )
        user_query = User.objects.filter(email=data["email"])
        self.assertTrue(userprofile_query.exists())
        self.assertTrue(user_query.exists())

    def test_get_by_telegram_id(self):
        self.user_profile = UserProfile.objects.get(user=self.user)
        self.user_profile.telegram_id = self.telegram_id
        self.user_profile.save()

        response = self.client.get(
            self.url + "by_telegram_id/" + f"?telegram_id={self.telegram_id}"
        )

        # Check that the response is 201 CREATED
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["email"], self.user.email)
        self.assertEqual(response_data["telegram_id"], self.telegram_id)
