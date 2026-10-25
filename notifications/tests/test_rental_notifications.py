from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from car.models import Car
from rentals.services.rental_service import create_rental


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

    @patch(
        "rentals.services.rental_service.send_telegram_notification.delay"
    )
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
