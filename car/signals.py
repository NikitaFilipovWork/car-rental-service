from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.db import transaction

from car.cache import invalidate_cars_cache
from car.models import Car


@receiver([post_save, post_delete], sender=Car)
def car_changed(sender, **kwargs):
    transaction.on_commit(invalidate_cars_cache)
