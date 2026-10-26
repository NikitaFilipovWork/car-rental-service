from datetime import date, timedelta

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from car.models import Car
from notifications.rental_notifications import (
    notify_rental_created,
    notify_rental_returned,
    notify_rental_canceled,
)
from payments.helper import create_payment
from rentals.models import Rental
from payments.models import Payment

BOOKED = Rental.RentalStatus.BOOKED
OVERDUE = Rental.RentalStatus.OVERDUE
COMPLETED = Rental.RentalStatus.COMPLETED
CANCELED = Rental.RentalStatus.CANCELED

RENTAL = Payment.PaymentType.RENTAL
OVERDUE_FEE = Payment.PaymentType.OVERDUE_FEE
CANCELLATION_FEE = Payment.PaymentType.CANCELLATION_FEE


def _check_new_rental_date_overlap(car: Car, start_date: date, end_date: date) -> None:
    overlapping = (
        Rental.objects.filter(
            car=car,
            status__in=[BOOKED, OVERDUE],
            start_date__lte=end_date,
            end_date__gte=start_date,
        )
        .order_by("start_date")
        .first()
    )
    if overlapping:
        raise ValidationError(
            f"This car is reserved from {overlapping.start_date} "
            f"till {overlapping.end_date}"
        )


def _lock_car(car: Car) -> Car:
    return Car.objects.select_for_update().get(pk=car.pk)


def _lock_rental(rental: Rental) -> Rental:
    return (
        Rental.objects.select_for_update()
        .select_related("car", "user")
        .get(pk=rental.pk)
    )


def _change_inventory(car: Car, delta: int) -> None:
    Car.objects.filter(pk=car.pk).update(inventory=F("inventory") + delta)
    car.refresh_from_db(fields=["inventory"])


def create_rental(user, car, start_date, end_date) -> Rental:
    with transaction.atomic():
        car = _lock_car(car)
        if car.inventory < 1:
            raise ValidationError("Car does not have free rental slots")
        _check_new_rental_date_overlap(car, start_date, end_date)

        _change_inventory(car, -1)

        rental = Rental.objects.create(
            user=user,
            car=car,
            start_date=start_date,
            end_date=end_date,
            price_per_day=car.daily_rate,
        )

    notify_rental_created(rental)

    return rental


def return_rental(rental: Rental, request=None) -> Rental:
    with transaction.atomic():
        rental = _lock_rental(rental)
        if rental.status not in [BOOKED, OVERDUE]:
            raise ValidationError("Only active rentals can be returned")

        actual_return_date = timezone.localdate()
        if actual_return_date < rental.start_date:
            raise ValidationError(
                "Before rental period started rental can only be canceled"
            )

        _change_inventory(rental.car, 1)

        rental.status = COMPLETED
        rental.actual_return_date = actual_return_date
        rental.save(update_fields=["actual_return_date", "status"])

        create_payment(rental, RENTAL, request)
        if actual_return_date > rental.end_date:
            create_payment(rental, OVERDUE_FEE, request)

    notify_rental_returned(rental)
    return rental


def cancel_rental(rental: Rental, request=None) -> Rental:
    with transaction.atomic():
        rental = _lock_rental(rental)
        if rental.status != BOOKED:
            raise ValidationError("Can cancel only booked rentals")

        cancel_date = timezone.localdate()
        if cancel_date >= rental.start_date:
            raise ValidationError(
                "Cancelling rental after rental period has started not allowed"
            )

        _change_inventory(rental.car, 1)
        rental.status = CANCELED
        rental.save(update_fields=["status"])

        if cancel_date >= rental.start_date - timedelta(days=1):
            create_payment(rental, CANCELLATION_FEE, request)

    notify_rental_canceled(rental)

    return rental
