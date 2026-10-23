import django_filters
from rest_framework.exceptions import ValidationError

from car.models import Car
from rentals.models import Rental


ACTIVE_RENTAL_STATUSES = (
    Rental.RentalStatus.BOOKED,
    Rental.RentalStatus.OVERDUE,
)


class CarFilter(django_filters.FilterSet):
    brand = django_filters.CharFilter(field_name="brand", lookup_expr="icontains")
    fuel_type = django_filters.ChoiceFilter(
        field_name="fuel_type",
        choices=Car.FuelTypeChoices.choices,
    )
    min_year = django_filters.NumberFilter(field_name="year", lookup_expr="gte")
    max_year = django_filters.NumberFilter(field_name="year", lookup_expr="lte")
    available = django_filters.BooleanFilter(method="filter_available")
    start_date = django_filters.DateFilter(method="skip_filter")
    end_date = django_filters.DateFilter(method="skip_filter")

    class Meta:
        model = Car
        fields = (
            "brand",
            "fuel_type",
            "min_year",
            "max_year",
            "available",
            "start_date",
            "end_date",
        )

    def filter_available(self, queryset, name, value):
        if value:
            return queryset.filter(inventory__gt=0)
        return queryset.filter(inventory=0)

    def skip_filter(self, queryset, name, value):
        return queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        start_date = self.form.cleaned_data.get("start_date")
        end_date = self.form.cleaned_data.get("end_date")

        if not start_date and not end_date:
            return queryset
        if not start_date or not end_date:
            raise ValidationError(
                "Both start_date and end_date are required."
            )
        if start_date > end_date:
            raise ValidationError(
                "start_date cannot be later than end_date."
            )

        busy_car_ids = Rental.objects.filter(
            status__in=ACTIVE_RENTAL_STATUSES,
            start_date__lte=end_date,
            end_date__gte=start_date,
        ).values("car_id")

        return queryset.filter(inventory__gt=0).exclude(id__in=busy_car_ids)
