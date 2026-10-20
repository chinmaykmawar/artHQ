
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0014_productmktp_mktp_product_id"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="legacy_product_id",
        ),
    ]
