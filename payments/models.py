from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING"
        PAID = "PAID"
        EXPIRED = "EXPIRED"

    class PaymentType(models.TextChoices):
        RENTAL = "RENTAL"
        CANCELLATION_FEE = "CANCELLATION_FEE"
        OVERDUE_FEE = "OVERDUE_FEE"

    status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )

    type = models.CharField(
        max_length=20,
        choices=PaymentType.choices,
    )
    rental = models.ForeignKey(
        "rentals.Rental", on_delete=models.PROTECT, related_name="payments"
    )
    session_url = models.URLField(max_length=1000)
    session_id = models.CharField(max_length=255, unique=True)
    money_to_pay = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return f"Payment #{self.id}: {self.type} {self.money_to_pay}$ ({self.status})"
