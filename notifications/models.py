from django.db import models

from rentals.models import Rental


class FailedNotification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
