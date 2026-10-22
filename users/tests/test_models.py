from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserManagerTests(TestCase):
    def test_create_user_success(self):
        user = User.objects.create_user(email="test@example.com", password="StrongPass123")

        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("StrongPass123"))
        self.assertNotEqual(user.password, "StrongPass123")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_has_no_username(self):
        user = User.objects.create_user(email="test@example.com", password="StrongPass123")

        self.assertIsNone(user.username)

    def test_create_user_normalizes_email_domain(self):
        user = User.objects.create_user(email="Test@EXAMPLE.com", password="StrongPass123")

        self.assertEqual(user.email, "Test@example.com")

    def test_create_user_without_email_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="StrongPass123")

    def test_create_superuser_success(self):
        admin = User.objects.create_superuser(email="admin@example.com", password="StrongPass123")

        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_create_superuser_with_is_staff_false_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin@example.com", password="StrongPass123", is_staff=False
            )

    def test_create_superuser_with_is_superuser_false_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin@example.com", password="StrongPass123", is_superuser=False
            )