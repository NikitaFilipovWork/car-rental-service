from django.contrib import admin

from rentals.models import Rental


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "car", "start_date", "end_date", "status")
    list_filter = ("status",)
    search_fields = ("user__email", "car__brand", "car__model")
    list_select_related = ("user", "car")
