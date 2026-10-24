from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from car.models import Car
from notifications.tasks import (
    check_overdue_rentals,
    send_telegram_notification,
)
from rentals.models import Rental


class TelegramTaskTests(SimpleTestCase):
    @patch("notifications.tasks.send_telegram_message")
    def test_send_telegram_notification(self, mock_send):
        send_telegram_notification("Test notification")

        mock_send.assert_called_once_with("Test notification")


class OverdueRentalTaskTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword123",
        )

        self.car = Car.objects.create(
            brand="Toyota",
            model="Corolla",
            year=2020,
            daily_rate=Decimal("50.00"),
            inventory=1,
        )

    @patch("notifications.tasks.send_telegram_message")
    def test_marks_booked_rental_as_overdue(self, mock_send):
        rental = Rental.objects.create(
            user=self.user,
            car=self.car,
            start_date=timezone.localdate() - timedelta(days=5),
            end_date=timezone.localdate() - timedelta(days=1),
            status=Rental.RentalStatus.BOOKED,
            price_per_day=self.car.daily_rate,
        )

        check_overdue_rentals()

        rental.refresh_from_db()

        self.assertEqual(
            rental.status,
            Rental.RentalStatus.OVERDUE,
        )
        mock_send.assert_called_once()
