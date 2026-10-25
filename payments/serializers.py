from rest_framework import serializers

from payments.models import Payment
from rentals.models import Rental


class PaymentRentalSerializer(serializers.ModelSerializer):
    """Short rental info for payment details (local to avoid circular imports)."""

    car = serializers.StringRelatedField()
    user = serializers.StringRelatedField()

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


class PaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "money_to_pay",
            "rental",
            "session_url",
        )
        read_only_fields = fields


class PaymentDetailSerializer(serializers.ModelSerializer):
    rental = PaymentRentalSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "money_to_pay",
            "rental",
            "session_url",
            "session_id",
        )
        read_only_fields = fields
