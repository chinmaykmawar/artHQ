
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Marketplaces", "0004_alter_marketplacefieldmapping_value"),
        ("main", "0015_remove_legacy_product_id"),
    ]

    operations = [
        # Rename models while preserving their existing records.
        migrations.RenameModel(
            old_name="MarketplaceSubcategory",
            new_name="MktpSubCat",
        ),
        migrations.RenameModel(
            old_name="MarketplaceField",
            new_name="MktpField",
        ),
        migrations.RenameModel(
            old_name="MarketplaceSubcategoryField",
            new_name="MktpSubCatField",
        ),
        migrations.RenameModel(
            old_name="MarketplaceSubcategoryFieldValue",
            new_name="MktpSubCatFieldValue",
        ),
        migrations.RenameModel(
            old_name="MarketplaceFieldMapping",
            new_name="MktpFieldMapping",
        ),
        migrations.RenameModel(
            old_name="MarketplaceFieldRule",
            new_name="MktpFieldRule",
        ),

        # Rename physical tables.
        migrations.AlterModelTable(
            name="mktpsubcat",
            table="mktp_subcat",
        ),
        migrations.AlterModelTable(
            name="mktpfield",
            table="mktp_field",
        ),
        migrations.AlterModelTable(
            name="mktpsubcatfield",
            table="mktp_subcat_field",
        ),
        migrations.AlterModelTable(
            name="validvalue",
            table="mktp_valid_value",
        ),
        migrations.AlterModelTable(
            name="mktpsubcatfieldvalue",
            table="mktp_subcat_field_value",
        ),
        migrations.AlterModelTable(
            name="mktpfieldmapping",
            table="mktp_field_mapping",
        ),
        migrations.AlterModelTable(
            name="mktpfieldrule",
            table="mktp_field_rule",
        ),
    ]
