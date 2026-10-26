from decimal import Decimal

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from car.models import Car
from rentals.models import Rental
from rentals.services import rental_service
from rentals.tests.test_base import (
    StripeMockMixin,
    sample_user,
    sample_car,
    today_plus_days,
    BOOKED,
    sample_rental,
    CANCELED,
    today_minus_days,
    today,
    COMPLETED,
    OVERDUE,
)


class CreateRentalServiceTests(TestCase):
    def setUp(self):
        self.user = sample_user(email="user1@test.com")
        self.other = sample_user(email="user2@test.com")
        self.car = sample_car(inventory=2, daily_rate=Decimal("70.00"))

    def test_creates_rental_and_decrements_inventory(self):
        rental = rental_service.create_rental(
            user=self.user,
            car=self.car,
            start_date=today_plus_days(2),
            end_date=today_plus_days(4),
        )
        self.car.refresh_from_db()
        self.assertEqual(self.car.inventory, 1)
        self.assertEqual(rental.status, BOOKED)
        self.assertEqual(rental.price_per_day, Decimal("70.00"))
        self.assertTrue(Rental.objects.filter(pk=rental.id).exists())

    def test_price_is_a_snapshot_of_current_rate(self):
        rental = rental_service.create_rental(
            user=self.user,
            car=self.car,
            start_date=today_plus_days(2),
            end_date=today_plus_days(4),
        )
        self.car.daily_rate = Decimal("99.00")
        self.car.save()
        rental.refresh_from_db()
        self.assertEqual(rental.price_per_day, Decimal("70.00"))

    def test_zero_inventory_raises_and_creates_nothing(self):
        self.car.inventory = 0
        self.car.save()
        with self.assertRaises(ValidationError):
            rental_service.create_rental(
                user=self.user,
                car=self.car,
                start_date=today_plus_days(2),
                end_date=today_plus_days(4),
            )
        self.assertEqual(Rental.objects.count(), 0)

    def test_overlapping_active_rental_blocks_booking(self):
        sample_rental(
            self.other,
            self.car,
            start_date=today_plus_days(2),
            end_date=today_plus_days(4),
        )
        with self.assertRaises(ValidationError):
            rental_service.create_rental(
                user=self.user,
                car=self.car,
                start_date=today_plus_days(3),
                end_date=today_plus_days(8),
            )
        self.assertFalse(Rental.objects.filter(pk=self.other.id).exists())

    def test_new_rental_covering_existing_one_is_blocked(self):
        sample_rental(
            self.other,
            self.car,
            start_date=today_plus_days(4),
            end_date=today_plus_days(5),
        )
        with self.assertRaises(ValidationError):
            rental_service.create_rental(
                user=self.user,
                car=self.car,
                start_date=today_plus_days(2),
                end_date=today_plus_days(8),
            )

    def test_inventory_uses_db_value_not_stale_instance(self):
        stale_car = self.car
        Car.objects.filter(pk=self.car.pk).update(inventory=0)
        with self.assertRaises(ValidationError):
            rental_service.create_rental(
                user=self.user,
                car=stale_car,
                start_date=today_plus_days(2),
                end_date=today_plus_days(4),
            )
        self.car.refresh_from_db()
        self.assertEqual(self.car.inventory, 0)

    def test_non_overlapping_dates_allowed(self):
        sample_rental(self.other, self.car)
        rental = rental_service.create_rental(
            user=self.user,
            car=self.car,
            start_date=today_plus_days(10),
            end_date=today_plus_days(12),
        )
        self.assertEqual(rental.status, BOOKED)

    def test_canceled_rental_does_not_block_dates(self):
        sample_rental(
            self.other,
            self.car,
            start_date=today_plus_days(2),
            end_date=today_plus_days(4),
            status=CANCELED,
        )
        rental = rental_service.create_rental(
            user=self.user,
            car=self.car,
            start_date=today_plus_days(3),
            end_date=today_plus_days(5),
        )
        self.assertEqual(rental.status, BOOKED)


class ReturnRentalServiceTests(StripeMockMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user = sample_user()
        self.car = sample_car(inventory=0)

    def test_return_sets_date_status_and_restores_inventory(self):
        rental = sample_rental(
            self.user,
            self.car,
            start_date=today_minus_days(2),
            end_date=today(),
        )
        result = rental_service.return_rental(rental)
        self.car.refresh_from_db()
        self.assertEqual(result.status, COMPLETED)
        self.assertEqual(result.actual_return_date, today())
        self.assertEqual(self.car.inventory, 1)

    def test_return_of_overdue_rental_allowed(self):
        rental = sample_rental(
            self.user,
            self.car,
            start_date=today_minus_days(3),
            end_date=today_minus_days(1),
            status=OVERDUE,
        )
        result = rental_service.return_rental(rental)
        self.assertEqual(result.status, COMPLETED)
        self.car.refresh_from_db()
        self.assertEqual(self.car.inventory, 1)

    def test_return_of_inactive_rental_raises(self):
        for status_value in (COMPLETED, CANCELED):
            rental = sample_rental(
                self.user,
                self.car,
                start_date=today_minus_days(2),
                status=status_value,
            )
            with self.assertRaises(ValidationError):
                rental_service.return_rental(rental)
        self.car.refresh_from_db()
        self.assertEqual(self.car.inventory, 0)

    def test_return_before_start_raises(self):
        rental = sample_rental(self.user, self.car)
        with self.assertRaises(ValidationError):
            rental_service.return_rental(rental)


class CancelRentalServiceTests(StripeMockMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user = sample_user()
        self.car = sample_car(inventory=0)

    def test_cancel_sets_status_and_restores_inventory(self):
        rental = sample_rental(self.user, self.car)
        result = rental_service.cancel_rental(rental)
        self.car.refresh_from_db()
        self.assertEqual(result.status, CANCELED)
        self.assertEqual(self.car.inventory, 1)

    def test_cancel_started_rental_raises(self):
        rental = sample_rental(self.user, self.car, start_date=today())
        with self.assertRaises(ValidationError):
            rental_service.cancel_rental(rental)
        self.car.refresh_from_db()
        self.assertEqual(self.car.inventory, 0)
        rental.refresh_from_db()
        self.assertEqual(rental.status, BOOKED)

    def test_cancel_non_booked_raises(self):
        for status_value in (COMPLETED, CANCELED, OVERDUE):
            rental = sample_rental(self.user, self.car, status=status_value)
            with self.assertRaises(ValidationError):
                rental_service.cancel_rental(rental)
        self.car.refresh_from_db()
        self.assertEqual(self.car.inventory, 0)
