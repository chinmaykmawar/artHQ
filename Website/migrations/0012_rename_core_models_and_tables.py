from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
    ("main", "0011_productimage_marketplaces"),
    ("Marketplaces", "0004_alter_marketplacefieldmapping_value"),
    ]

    operations = [
        # Rename core models first.
        migrations.RenameModel(
            old_name="SubCategory",
            new_name="SubCat",
        ),
        migrations.RenameModel(
            old_name="Marketplace",
            new_name="Mktp",
        ),
        migrations.RenameModel(
            old_name="ProductMarketplace",
            new_name="ProductMktp",
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RenameModel(
                    old_name="ProductImage",
                    new_name="ImageData",
                ),
            ],
        ),

        # Rename the physical tables to their target names.
        migrations.AlterModelTable(
            name="subcat",
            table="subcat",
        ),
        migrations.AlterModelTable(
            name="mktp",
            table="mktp",
        ),
        migrations.AlterModelTable(
            name="productmktp",
            table="product_mktp",
        ),
        # ImageData already uses the product_image table.
    ]