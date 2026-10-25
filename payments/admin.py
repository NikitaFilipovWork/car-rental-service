from django.contrib import admin
from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "rental",
        "type",
        "status",
        "money_to_pay"
    )

    list_filter = (
        "status",
        "type"
    )