import django_filters

from car.models import Car


class CarFilter(django_filters.FilterSet):
    brand = django_filters.CharFilter(field_name="brand", lookup_expr="icontains")
    fuel_type = django_filters.ChoiceFilter(
        field_name="fuel_type",
        choices=Car.FuelTypeChoices.choices,
    )
    min_year = django_filters.NumberFilter(field_name="year", lookup_expr="gte")
    max_year = django_filters.NumberFilter(field_name="year", lookup_expr="lte")
    available = django_filters.BooleanFilter(method="filter_available")

    class Meta:
        model = Car
        fields = ("brand", "fuel_type", "min_year", "max_year", "available")

    def filter_available(self, queryset, name, value):
        if value:
            return queryset.filter(inventory__gt=0)
        return queryset.filter(inventory=0)
