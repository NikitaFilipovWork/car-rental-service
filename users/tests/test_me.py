from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

ME_URL = reverse("users:manage")
TOKEN_URL = reverse("users:token_obtain_pair")


class UnauthenticatedMeTests(APITestCase):
    def test_get_requires_authentication(self):
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_requires_authentication(self):
        response = self.client.patch(ME_URL, {"email": "x@example.com"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_token_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token.here")

        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MeRealTokenTests(APITestCase):
    """Real JWT token test."""

    def test_me_with_real_access_token(self):
        User.objects.create_user(email="test@example.com", password="StrongPass123")
        login = self.client.post(
            TOKEN_URL,
            {"email": "test@example.com", "password": "StrongPass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZE=f"Bearer {login.data['access']}")

        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@example.com")


class AuthenticatedMeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="StrongPass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_get_returns_current_user(self):
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertFalse(response.data["is_staff"])

    def test_get_does_not_return_password(self):
        response = self.client.get(ME_URL)

        self.assertNotIn("password", response.data)

    def test_get_returns_only_own_data(self):
        User.objects.create_user(email="other@example.com", password="StrongPass123")

        response = self.client.get(ME_URL)

        self.assertEqual(response.data["email"], "test@example.com")

    def test_patch_email(self):
        response = self.client.patch(ME_URL, {"email": "new@example.com"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "new@example.com")

    def test_patch_own_email_unchanged_is_ok(self):
        response = self.client.patch(ME_URL, {"email": "test@example.com"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_email_taken_by_other_user(self):
        User.objects.create_user(email="other@example.com", password="StrongPass123")

        response = self.client.patch(ME_URL, {"email": "other@example.com"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "test@example.com")

    def test_patch_invalid_email(self):
        response = self.client.patch(ME_URL, {"email": "broken"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_password_is_hashed(self):
        response = self.client.patch(ME_URL, {"password": "NewPass123"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("password", response.data)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.password, "NewPass123")
        self.assertTrue(self.user.check_password("NewPass123"))
        self.assertFalse(self.user.check_password("StrongPass123"))

    def test_patch_password_too_short(self):
        response = self.client.patch(ME_URL, {"password": "1234"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("StrongPass123"))

    def test_login_with_new_password_after_change(self):
        self.client.patch(ME_URL, {"password": "NewPass123"}, format="json")
        self.client.force_authenticate(user=None)

        new_login = self.client.post(
            TOKEN_URL, {"email": "test@example.com", "password": "NewPass123"}, format="json"
        )
        old_login = self.client.post(
            TOKEN_URL, {"email": "test@example.com", "password": "StrongPass123"}, format="json"
        )

        self.assertEqual(new_login.status_code, status.HTTP_200_OK)
        self.assertEqual(old_login.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_cannot_escalate_is_staff(self):
        self.client.patch(ME_URL, {"is_staff": True}, format="json")

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)

    def test_patch_cannot_escalate_is_superuser(self):
        self.client.patch(ME_URL, {"is_superuser": True}, format="json")

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_superuser)

    def test_put_full_update(self):
        payload = {"email": "put@example.com", "password": "PutPass123"}

        response = self.client.put(ME_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "put@example.com")
        self.assertTrue(self.user.check_password("PutPass123"))

    def test_put_requires_all_fields(self):
        response = self.client.put(ME_URL, {"email": "put@example.com"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_delete_not_allowed(self):
        response = self.client.delete(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())

    def test_post_not_allowed(self):
        response = self.client.post(ME_URL, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
