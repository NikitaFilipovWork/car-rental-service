from django.db import migrations
from django.db.models import Count, F, Q

ACTIVE = ("BOOKED", "OVERDUE")


def to_fleet_size(apps, schema_editor):
    """Inventory used to drop by one per active rental; now it is the fleet size."""
    Car = apps.get_model("car", "Car")
    cars = Car.objects.annotate(
        active=Count("rentals", filter=Q(rentals__status__in=ACTIVE))
    ).filter(active__gt=0)
    for car in cars:
        Car.objects.filter(pk=car.pk).update(inventory=F("inventory") + car.active)


def to_free_slots(apps, schema_editor):
    Car = apps.get_model("car", "Car")
    cars = Car.objects.annotate(
        active=Count("rentals", filter=Q(rentals__status__in=ACTIVE))
    ).filter(active__gt=0)
    for car in cars:
        Car.objects.filter(pk=car.pk).update(
            inventory=max(car.inventory - car.active, 0)
        )


class Migration(migrations.Migration):

    dependencies = [
        ("car", "0002_car_image"),
        ("rentals", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(to_fleet_size, to_free_slots),
    ]
