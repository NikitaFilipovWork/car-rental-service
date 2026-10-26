from collections import defaultdict
from datetime import date, timedelta

from django.db.models import Q
from django.utils import timezone

from rentals.models import Rental

ACTIVE_STATUSES = (Rental.RentalStatus.BOOKED, Rental.RentalStatus.OVERDUE)


def _overlapping_rentals(start_date: date, end_date: date):
    today = timezone.localdate()
    overlap = Q(end_date__gte=start_date)
    if start_date <= today:
        # A car that is not returned yet stays busy at least until today
        overlap |= Q(end_date__lt=today)
    return Rental.objects.filter(
        overlap,
        status__in=ACTIVE_STATUSES,
        start_date__lte=end_date,
    )


def _busy_period(start: date, end: date) -> tuple[date, date]:
    return start, max(end, timezone.localdate())


def max_cars_in_use(periods, start_date: date, end_date: date) -> int:
    """Biggest number of rentals that run on the same day within the period."""
    busiest = 0
    day = start_date
    while day <= end_date:
        in_use = sum(1 for start, end in periods if start <= day <= end)
        busiest = max(busiest, in_use)
        day += timedelta(days=1)
    return busiest


def cars_in_use(car, start_date: date, end_date: date) -> int:
    rentals = _overlapping_rentals(start_date, end_date).filter(car=car)
    periods = [
        _busy_period(start, end)
        for start, end in rentals.values_list("start_date", "end_date")
    ]
    return max_cars_in_use(periods, start_date, end_date)


def fully_booked_car_ids(start_date: date, end_date: date) -> set[int]:
    """Cars that have no free unit on at least one day of the period."""
    periods_by_car = defaultdict(list)
    inventory_by_car = {}
    rentals = _overlapping_rentals(start_date, end_date).values_list(
        "car_id", "car__inventory", "start_date", "end_date"
    )
    for car_id, inventory, start, end in rentals:
        periods_by_car[car_id].append(_busy_period(start, end))
        inventory_by_car[car_id] = inventory

    return {
        car_id
        for car_id, periods in periods_by_car.items()
        if max_cars_in_use(periods, start_date, end_date) >= inventory_by_car[car_id]
    }
