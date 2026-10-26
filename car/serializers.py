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
            "image",
        )
        read_only_fields = ("image",)

    def validate_year(self, value):
        current_year = date.today().year
        if not (1889 <= value <= current_year):
            raise serializers.ValidationError(
                f"Year must be between 1889 and {current_year}."
            )
        return value


class CarImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)

    class Meta:
        model = Car
        fields = ("id", "image")
