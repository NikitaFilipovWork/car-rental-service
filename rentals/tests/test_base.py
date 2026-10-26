from datetime import timedelta
from decimal import Decimal
from itertools import count
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from car.models import Car
from rentals.models import Rental

User = get_user_model()

BOOKED = Rental.RentalStatus.BOOKED
OVERDUE = Rental.RentalStatus.OVERDUE
COMPLETED = Rental.RentalStatus.COMPLETED
CANCELED = Rental.RentalStatus.CANCELED


def sample_user(**params):
    default = {
        "email": "user_test@test.com",
        "password": "1qazcde3",
        "is_staff": False,
    }
    default.update(params)
    return User.objects.create_user(**default)


def sample_user_staff(**params):
    default = {
        "email": "admin_test@test.com",
        "password": "1qazcde3",
        "is_staff": True,
    }
    default.update(params)
    return User.objects.create_user(**default)


def sample_car(**params):
    defaults = {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2020,
        "fuel_type": Car.FuelTypeChoices.GAS,
        "daily_rate": Decimal("45.00"),
        "inventory": 5,
    }
    defaults.update(params)
    return Car.objects.create(**defaults)


def today():
    return timezone.localdate()


def today_plus_days(days):
    return today() + timedelta(days=days)


def today_minus_days(days):
    return today() - timedelta(days=days)


def sample_rental(
    user,
    car,
    **kwargs,
):
    defaults = {
        "user": user,
        "car": car,
        "start_date": today_plus_days(2),
        "end_date": today_plus_days(6),
        "status": Rental.RentalStatus.BOOKED,
        "price_per_day": car.daily_rate,
    }
    defaults.update(kwargs)
    return Rental.objects.create(**defaults)


def get_rental_list_url():
    return reverse("rentals:rental-list")


def get_rental_detail_url(pk):
    return reverse("rentals:rental-detail", kwargs={"pk": pk})


def get_rental_return_url(pk):
    return reverse("rentals:rental-return", kwargs={"pk": pk})


def get_rental_cancel_url(pk):
    return reverse("rentals:rental-cancel", kwargs={"pk": pk})


class StripeMockMixin:
    """Replace Stripe Checkout Session creation with a local fake."""

    def setUp(self):
        super().setUp()
        session_ids = count(1)

        def fake_session(**kwargs):
            session_id = f"cs_test_{next(session_ids)}"
            return type(
                "Session",
                (),
                {"id": session_id, "url": f"https://stripe.test/{session_id}"},
            )()

        patcher = patch(
            "payments.helper.stripe.checkout.Session.create",
            side_effect=fake_session,
        )
        self.stripe_session_create = patcher.start()
        self.addCleanup(patcher.stop)
