from django.contrib import admin

from notifications.models import FailedNotification


@admin.register(FailedNotification)
class FailedNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "message")
