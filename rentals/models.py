from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Rental(models.Model):
    class RentalStatus(models.TextChoices):
        BOOKED = "BOOKED"
        COMPLETED = "COMPLETED"
        CANCELED = "CANCELED"
        OVERDUE = "OVERDUE"

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(start_date__lte=models.F("end_date")),
                name="start_date_lte_end_date",
            ),
        ]

    car = models.ForeignKey("car.Car", on_delete=models.PROTECT, related_name="rentals")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="rentals",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        choices=RentalStatus.choices,
        default=RentalStatus.BOOKED,
        max_length=15,
    )
    price_per_day = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    def __str__(self):
        return f"Rental: {self.user} - {self.start_date} - {self.end_date}"
