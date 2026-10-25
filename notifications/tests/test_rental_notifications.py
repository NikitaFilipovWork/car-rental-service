from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from car.models import Car
from rentals.models import Rental
from rentals.services.rental_service import create_rental, return_rental, cancel_rental


class RentalNotificationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="rental@example.com",
            password="testpassword123",
        )

        self.car = Car.objects.create(
            brand="Toyota",
            model="Corolla",
            year=2020,
            daily_rate=Decimal("50.00"),
            inventory=1,
        )

    @patch("notifications.rental_notifications.send_telegram_notification.delay")
    def test_create_rental_sends_notification(self, mock_delay):
        start_date = timezone.localdate() + timedelta(days=1)
        end_date = start_date + timedelta(days=3)

        rental = create_rental(
            user=self.user,
            car=self.car,
            start_date=start_date,
            end_date=end_date,
        )

        self.assertIsNotNone(rental.pk)
        mock_delay.assert_called_once()

    @patch("rentals.services.rental_service.send_telegram_notification.delay")
    def test_return_rental_sends_notification(self, mock_delay):
        today = timezone.localdate()

        rental = Rental.objects.create(
            user=self.user,
            car=self.car,
            start_date=today - timedelta(days=2),
            end_date=today + timedelta(days=2),
            price_per_day=self.car.daily_rate,
        )

        return_rental(rental)

        rental.refresh_from_db()
        self.assertEqual(rental.status, Rental.RentalStatus.COMPLETED)
        self.assertEqual(rental.actual_return_date, today)
        mock_delay.assert_called_once()

    @patch("rentals.services.rental_service.send_telegram_notification.delay")
    def test_cancel_rental_sends_notification(self, mock_delay):
        today = timezone.localdate()

        rental = Rental.objects.create(
            user=self.user,
            car=self.car,
            start_date=today + timedelta(days=5),
            end_date=today + timedelta(days=10),
            price_per_day=self.car.daily_rate,
        )

        cancel_rental(rental)

        rental.refresh_from_db()
        self.assertEqual(rental.status, Rental.RentalStatus.CANCELED)
        mock_delay.assert_called_once()
