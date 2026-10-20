
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0012_rename_core_models_and_tables"),
    ]

    operations = [
        # Rename existing fields without deleting their data.
        migrations.RenameField(
            model_name="design",
            old_name="subcategory",
            new_name="subcat",
        ),
        migrations.RenameField(
            model_name="productmktp",
            old_name="marketplace",
            new_name="mktp",
        ),
        migrations.RenameField(
            model_name="productmktp",
            old_name="marketplace_product_id",
            new_name="mktp_listing_id",
        ),
        migrations.RenameField(
            model_name="productmktp",
            old_name="marketplace_sku",
            new_name="mktp_sku",
        ),
        migrations.RenameField(
            model_name="imagedata",
            old_name="marketplaces",
            new_name="mktps",
        ),
        migrations.RenameField(
            model_name="order",
            old_name="marketplace",
            new_name="mktp",
        ),
        migrations.RenameField(
            model_name="order",
            old_name="marketplace_fee",
            new_name="mktp_fee",
        ),

        # Update related_name metadata.
        migrations.AlterField(
            model_name="subcat",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="subcats",
                to="main.category",
            ),
        ),
        migrations.AlterField(
            model_name="productmktp",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="mktp_data",
                to="main.product",
            ),
        ),

        # Rename the existing constraints.
        migrations.RemoveConstraint(
            model_name="subcat",
            name="unique_subcategory_per_category",
        ),
        migrations.AddConstraint(
            model_name="subcat",
            constraint=models.UniqueConstraint(
                fields=("category", "code"),
                name="unique_subcat_per_category",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="design",
            name="unique_design_per_subcategory",
        ),
        migrations.AddConstraint(
            model_name="design",
            constraint=models.UniqueConstraint(
                fields=("subcat", "design_code"),
                name="unique_design_per_subcat",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="productmktp",
            name="unique_product_marketplace",
        ),
        migrations.AddConstraint(
            model_name="productmktp",
            constraint=models.UniqueConstraint(
                fields=("product", "mktp"),
                name="unique_product_mktp",
            ),
        ),
    ]
