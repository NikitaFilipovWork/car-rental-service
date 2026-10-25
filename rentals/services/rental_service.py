from datetime import date, timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from car.models import Car
from notifications.rental_notifications import (
    notify_rental_created,
    notify_rental_returned,
    notify_rental_canceled,
)
from rentals.models import Rental

BOOKED = Rental.RentalStatus.BOOKED
OVERDUE = Rental.RentalStatus.OVERDUE
COMPLETED = Rental.RentalStatus.COMPLETED
CANCELED = Rental.RentalStatus.CANCELED


def _check_new_rental_date_overlap(car: Car, start_date: date, end_date: date) -> None:
    queryset = (
        Car.objects.prefetch_related("rentals")
        .filter(pk=car.pk, rentals__status__in=[BOOKED, OVERDUE])
        .values_list("rentals__start_date", "rentals__end_date")
    )
    for pair in queryset:
        reserved_start_date, reserved_end_date = pair
        if reserved_start_date <= start_date <= reserved_end_date:
            raise ValidationError(
                f"This car is reserved from {start_date} till {min(end_date, reserved_end_date)}"
            )
        if reserved_start_date <= end_date <= reserved_end_date:
            raise ValidationError(
                f"This car is reserved from {max(start_date, reserved_start_date)} till {end_date}"
            )


def _check_car_can_be_booked(car: Car) -> None:
    car = Car.objects.get(pk=car.pk)
    if car.inventory < 1:
        raise ValidationError("Car does not have free rental slots")


def create_rental(user, car, start_date, end_date) -> Rental:
    with transaction.atomic():
        _check_car_can_be_booked(car)
        _check_new_rental_date_overlap(car, start_date, end_date)

        car.inventory -= 1
        car.save(update_fields=["inventory"])

        rental = Rental.objects.create(
            user=user,
            car=car,
            start_date=start_date,
            end_date=end_date,
            price_per_day=car.daily_rate,
        )

    notify_rental_created(rental)

    return rental


def return_rental(rental) -> Rental:
    with transaction.atomic():
        if rental.status not in [BOOKED, OVERDUE]:
            raise ValidationError("Only active rentals can be returned")

        actual_return_date = timezone.localdate()
        if actual_return_date < rental.start_date:
            raise ValidationError(
                "Before rental period started rental can only be canceled"
            )
        car = rental.car
        car.inventory += 1
        rental.car.save(update_fields=["inventory"])

        rental.status = COMPLETED

        rental.actual_return_date = actual_return_date
        rental.save(update_fields=["actual_return_date", "status"])

        if actual_return_date <= rental.end_date:
            # create normal Payment for rent (car returned in time)
            print("Car returned in time")
            ...
        else:
            # create Payment + Payment OVERDUE_FEE (car is overdue)
            print("Car returned not in time")
            ...

    notify_rental_returned(rental)
    return rental


def cancel_rental(rental: Rental) -> Rental:
    with transaction.atomic():
        if rental.status != BOOKED:
            raise ValidationError("Can cancel only booked rentals")

        cancel_date = timezone.localdate()
        if cancel_date >= rental.start_date:
            raise ValidationError(
                "Cancelling rental after rental period has started not allowed"
            )
        if cancel_date >= rental.start_date - timedelta(days=1):
            print("canceled less than 1 day before start of rental")
            # CANCELLATION_FEE for cancelling too late
        car = rental.car
        car.inventory += 1
        car.save(update_fields=["inventory"])
        rental.status = CANCELED
        rental.save(update_fields=["status"])

    notify_rental_canceled(rental)

    return rental
