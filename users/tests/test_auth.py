from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.views import LoginView

User = get_user_model()

TOKEN_URL = reverse("users:token_obtain_pair")
REFRESH_URL = reverse("users:token_refresh")


class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="StrongPass123"
        )
        self.credentials = {"email": "test@example.com", "password": "StrongPass123"}

    def test_login_success_returns_tokens(self):
        response = self.client.post(TOKEN_URL, self.credentials, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password(self):
        payload = {**self.credentials, "password": "wrong-password"}

        response = self.client.post(TOKEN_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)

    def test_login_unknown_email(self):
        payload = {"email": "nobody@example.com", "password": "StrongPass123"}

        response = self.client.post(TOKEN_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(TOKEN_URL, self.credentials, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        response = self.client.post(TOKEN_URL, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_after_registration(self):
        """Сквозной тест: регистрация -> логин."""
        payload = {"email": "new@example.com", "password": "NewPass123"}
        self.client.post(reverse("users:create"), payload, format="json")

        response = self.client.post(TOKEN_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TokenRefreshTests(APITestCase):
    def setUp(self):
        User.objects.create_user(email="test@example.com", password="StrongPass123")
        login = self.client.post(
            TOKEN_URL,
            {"email": "test@example.com", "password": "StrongPass123"},
            format="json",
        )
        self.refresh = login.data["refresh"]

    def test_refresh_returns_new_access_token(self):
        response = self.client.post(
            REFRESH_URL, {"refresh": self.refresh}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_with_invalid_token(self):
        response = self.client.post(REFRESH_URL, {"refresh": "garbage"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_without_token(self):
        response = self.client.post(REFRESH_URL, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginThrottleTests(APITestCase):
    def test_login_uses_login_throttle_scope(self):
        self.assertEqual(LoginView.throttle_scope, "login")
