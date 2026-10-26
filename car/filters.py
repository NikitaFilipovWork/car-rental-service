import django_filters
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from car.models import Car
from rentals.availability import fully_booked_car_ids


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
        """Available now: at least one car of the model is not rented today."""
        today = timezone.localdate()
        busy_ids = fully_booked_car_ids(today, today)
        if value:
            return queryset.filter(inventory__gt=0).exclude(id__in=busy_ids)
        return queryset.filter(Q(inventory=0) | Q(id__in=busy_ids))

    def skip_filter(self, queryset, name, value):
        return queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        start_date = self.form.cleaned_data.get("start_date")
        end_date = self.form.cleaned_data.get("end_date")

        if not start_date and not end_date:
            return queryset
        if not start_date or not end_date:
            raise ValidationError("Both start_date and end_date are required.")
        if start_date > end_date:
            raise ValidationError("start_date cannot be later than end_date.")

        busy_ids = fully_booked_car_ids(start_date, end_date)
        return queryset.filter(inventory__gt=0).exclude(id__in=busy_ids)
