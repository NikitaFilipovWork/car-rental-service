from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

CREATE_URL = reverse("users:create")


class RegisterTests(APITestCase):
    def setUp(self):
        self.payload = {"email": "test@example.com", "password": "StrongPass123"}

    def test_register_success(self):
        response = self.client.post(CREATE_URL, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_register_does_not_return_password(self):
        response = self.client.post(CREATE_URL, self.payload, format="json")

        self.assertNotIn("password", response.data)

    def test_register_hashes_password(self):
        self.client.post(CREATE_URL, self.payload, format="json")
        user = User.objects.get(email="test@example.com")

        self.assertNotEqual(user.password, "StrongPass123")
        self.assertTrue(user.check_password("StrongPass123"))

    def test_register_available_without_authentication(self):
        response = self.client.post(CREATE_URL, self.payload, format="json")

        self.assertNotIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_register_cannot_set_is_staff(self):
        payload = {**self.payload, "is_staff": True}

        response = self.client.post(CREATE_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="test@example.com")
        self.assertFalse(user.is_staff)
        self.assertFalse(response.data["is_staff"])

    def test_register_cannot_set_is_superuser(self):
        payload = {**self.payload, "is_superuser": True}

        self.client.post(CREATE_URL, payload, format="json")

        user = User.objects.get(email="test@example.com")
        self.assertFalse(user.is_superuser)

    def test_register_duplicate_email(self):
        User.objects.create_user(email="test@example.com", password="StrongPass123")

        response = self.client.post(CREATE_URL, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(User.objects.filter(email="test@example.com").count(), 1)

    def test_register_password_too_short(self):
        payload = {**self.payload, "password": "1234"}

        response = self.client.post(CREATE_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertFalse(User.objects.filter(email="test@example.com").exists())

    def test_register_password_min_length_boundary(self):
        payload = {**self.payload, "password": "12345"}

        response = self.client.post(CREATE_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_invalid_email(self):
        payload = {**self.payload, "email": "not-an-email"}

        response = self.client.post(CREATE_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_missing_fields(self):
        response = self.client.post(CREATE_URL, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("password", response.data)

    def test_register_get_not_allowed(self):
        response = self.client.get(CREATE_URL)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
