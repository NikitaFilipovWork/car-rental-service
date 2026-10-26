from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from car.cache import invalidate_cars_cache
from car.models import Car


@receiver([post_save, post_delete], sender=Car)
def car_changed(sender, **kwargs):
    transaction.on_commit(invalidate_cars_cache)


@receiver(pre_save, sender=Car)
def delete_replaced_image(sender, instance, **kwargs):
    if not instance.pk:
        return
    old_image = Car.objects.filter(pk=instance.pk).values_list("image", flat=True)
    old_name = old_image.first()
    if old_name and old_name != instance.image.name:
        storage = instance.image.storage
        transaction.on_commit(lambda: storage.delete(old_name))


@receiver(post_delete, sender=Car)
def delete_image_file(sender, instance, **kwargs):
    if instance.image:
        image = instance.image
        transaction.on_commit(lambda: image.storage.delete(image.name))
