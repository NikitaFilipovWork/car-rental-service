from django.core.validators import MinValueValidator
from django.db import models


class Car(models.Model):
    class FuelTypeChoices(models.TextChoices):
        GAS = "GAS", "Gas"
        DIESEL = "DIESEL", "Diesel"
        HYBRID = "HYBRID", "Hybrid"
        ELECTRIC = "ELECTRIC", "Electric"

    brand = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    fuel_type = models.CharField(
        max_length=10,
        choices=FuelTypeChoices.choices,
        default=FuelTypeChoices.GAS,
    )
    daily_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    inventory = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"
