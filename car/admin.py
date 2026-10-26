from django.contrib import admin

from car.models import Car


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("id", "brand", "model", "year", "daily_rate", "inventory", "image")
    list_filter = ("fuel_type",)
    search_fields = ("brand", "model")
