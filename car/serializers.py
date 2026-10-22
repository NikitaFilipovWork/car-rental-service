from datetime import date

from rest_framework import serializers

from car.models import Car


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = (
            "id",
            "brand",
            "model",
            "year",
            "fuel_type",
            "daily_rate",
            "inventory",
        )

    def validate_year(self, value):
        current_year = date.today().year
        if not (1889 <= value <= current_year):
            raise serializers.ValidationError(
                f"Year must be between 1889 and {current_year}."
            )
        return value
