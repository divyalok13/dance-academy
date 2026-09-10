from django.db import migrations
import uuid


def populate_coupon_tokens(apps, schema_editor):
    DandiyaRegistration = apps.get_model(
        "core",
        "DandiyaRegistration",
    )

    for registration in DandiyaRegistration.objects.filter(
        coupon_token__isnull=True
    ):
        registration.coupon_token = uuid.uuid4()
        registration.save(
            update_fields=["coupon_token"]
        )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_dandiyaregistration_coupon_token"),
    ]

    operations = [
        migrations.RunPython(
            populate_coupon_tokens,
            migrations.RunPython.noop,
        ),
    ]