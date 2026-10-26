from django.db import migrations, models


def strip_cancellation_fee(apps, schema_editor):
    Payment = apps.get_model("payments", "Payment")
    Payment.objects.filter(type="CANCELLATION_FEE ").update(type="CANCELLATION_FEE")


def restore_cancellation_fee(apps, schema_editor):
    Payment = apps.get_model("payments", "Payment")
    Payment.objects.filter(type="CANCELLATION_FEE").update(type="CANCELLATION_FEE ")


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(strip_cancellation_fee, restore_cancellation_fee),
        migrations.AlterField(
            model_name="payment",
            name="type",
            field=models.CharField(
                choices=[
                    ("RENTAL", "Rental"),
                    ("CANCELLATION_FEE", "Cancellation Fee"),
                    ("OVERDUE_FEE", "Overdue Fee"),
                ],
                max_length=20,
            ),
        ),
    ]
