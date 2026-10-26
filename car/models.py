import pathlib
import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


def car_image_file_path(instance, filename):
    extension = pathlib.Path(filename).suffix.lower()
    name = slugify(f"{instance.brand}-{instance.model}")
    return f"uploads/cars/{name}-{uuid.uuid4()}{extension}"


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
    image = models.ImageField(null=True, blank=True, upload_to=car_image_file_path)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"
