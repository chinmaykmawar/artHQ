
from django.db import migrations, models


def copy_flipkart_product_ids(apps, schema_editor):
    Product = apps.get_model("main", "Product")
    ProductMktp = apps.get_model("main", "ProductMktp")

    db_alias = schema_editor.connection.alias

    flipkart_listings = ProductMktp.objects.using(db_alias).filter(
        mktp__code="FLIPKART",
        product__legacy_product_id__isnull=False,
    ).exclude(
        product__legacy_product_id=""
    )

    # Copy only to Flipkart listings; do not overwrite an existing value.
    for listing in flipkart_listings.iterator():
        if not listing.mktp_product_id:
            listing.mktp_product_id = (
                Product.objects.using(db_alias)
                .values_list("legacy_product_id", flat=True)
                .get(pk=listing.product_id)
            )
            listing.save(
                using=db_alias,
                update_fields=["mktp_product_id"],
            )


def reverse_copy_flipkart_product_ids(apps, schema_editor):
    ProductMktp = apps.get_model("main", "ProductMktp")
    db_alias = schema_editor.connection.alias

    ProductMktp.objects.using(db_alias).filter(
        mktp__code="FLIPKART",
        mktp_product_id=models.F("product__legacy_product_id"),
    ).update(mktp_product_id="")


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0013_rename_core_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="productmktp",
            name="mktp_product_id",
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.RunPython(
            copy_flipkart_product_ids,
            reverse_copy_flipkart_product_ids,
        ),
    ]
