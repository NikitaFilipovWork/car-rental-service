from django.utils import timezone
from rest_framework import serializers

from car.serializers import CarSerializer
from payments.serializers import PaymentListSerializer
from rentals.models import Rental
from users.serializers import UserSerializer


class RentalListViewSerializer(serializers.ModelSerializer):
    car = serializers.StringRelatedField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Rental
        fields = (
            "id",
            "car",
            "user",
            "start_date",
            "end_date",
            "actual_return_date",
            "status",
            "price_per_day",
        )


class RentalDetailViewSerializer(serializers.ModelSerializer):
    car = CarSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    payments = PaymentListSerializer(many=True, read_only=True)

    class Meta:
        model = Rental
        fields = (
            "id",
            "car",
            "user",
            "start_date",
            "end_date",
            "actual_return_date",
            "status",
            "price_per_day",
            "payments",
        )


class RentalCreateViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = (
            "id",
            "car",
            "start_date",
            "end_date",
            "status",
            "price_per_day",
        )
        read_only_fields = ("price_per_day", "status")

    def validate(self, attrs):
        start_date = attrs["start_date"]
        if start_date < timezone.localdate():
            raise serializers.ValidationError(
                f"Start date: {start_date} cannot be earlier than current date: {timezone.localdate()}"
            )
        end_date = attrs["end_date"]
        if start_date > end_date:
            raise serializers.ValidationError(
                f"Start date: {start_date} cannot be later than end date: {end_date}"
            )
        return attrs


class ReturnRentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = ("id", "car", "start_date", "end_date", "actual_return_date")
        read_only_fields = ("car", "start_date", "end_date")

    def validate_actual_return_date(self, value):
        if value is None or value < self.instance.start_date:
            raise serializers.ValidationError(
                "Return date cannot be earlier than start date"
            )
        return value


class EmptySerializer(serializers.Serializer):
    pass
