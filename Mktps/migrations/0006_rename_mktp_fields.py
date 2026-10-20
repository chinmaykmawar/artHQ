
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Marketplaces", "0005_rename_mktp_models_and_tables"),
        ("main", "0015_remove_legacy_product_id"),
    ]

    operations = [
        # Remove constraints before renaming their fields.
        migrations.RemoveConstraint(
            model_name="mktpfield",
            name="unique_marketplace_field_code",
        ),
        migrations.RemoveConstraint(
            model_name="mktpsubcat",
            name="unique_marketplace_subcategory",
        ),
        migrations.RemoveConstraint(
            model_name="mktpsubcatfield",
            name="unique_marketplace_subcategory_column_order",
        ),
        migrations.RemoveConstraint(
            model_name="mktpsubcatfieldvalue",
            name="unique_allowed_value_per_subcategory_field",
        ),
        migrations.RemoveConstraint(
            model_name="validvalue",
            name="unique_valid_value_per_marketplace_field",
        ),

        # Rename fields without discarding their existing values.
        migrations.RenameField(
            model_name="mktpfield",
            old_name="marketplace",
            new_name="mktp",
        ),
        migrations.RenameField(
            model_name="mktpsubcat",
            old_name="marketplace",
            new_name="mktp",
        ),
        migrations.RenameField(
            model_name="mktpsubcat",
            old_name="subcategory",
            new_name="subcat",
        ),
        migrations.RenameField(
            model_name="mktpsubcatfield",
            old_name="marketplace_subcategory",
            new_name="mktp_subcat",
        ),
        migrations.RenameField(
            model_name="mktpsubcatfield",
            old_name="marketplace_field",
            new_name="mktp_field",
        ),
        migrations.RenameField(
            model_name="mktpsubcatfieldvalue",
            old_name="marketplace_subcategory_field",
            new_name="mktp_subcat_field",
        ),
        migrations.RenameField(
            model_name="mktpfieldmapping",
            old_name="marketplace_subcategory_field",
            new_name="mktp_subcat_field",
        ),
        migrations.RenameField(
            model_name="mktpfieldrule",
            old_name="marketplace_subcategory_field",
            new_name="mktp_subcat_field",
        ),
        migrations.RenameField(
            model_name="validvalue",
            old_name="marketplace_field",
            new_name="mktp_field",
        ),

        # Update related names and field metadata.
        migrations.AlterField(
            model_name="mktpsubcat",
            name="mktp",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="mktp_subcats",
                to="main.mktp",
            ),
        ),
        migrations.AlterField(
            model_name="mktpsubcat",
            name="subcat",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="mktp_configurations",
                to="main.subcat",
            ),
        ),
        migrations.AlterField(
            model_name="mktpsubcatfield",
            name="mktp_field",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="subcat_configurations",
                to="Marketplaces.mktpfield",
            ),
        ),
        migrations.AlterField(
            model_name="mktpsubcatfieldvalue",
            name="valid_value",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="subcat_usages",
                to="Marketplaces.validvalue",
            ),
        ),

        # Update model ordering and display names.
        migrations.AlterModelOptions(
            name="mktpfield",
            options={
                "ordering": ["mktp", "name"],
                "verbose_name": "Mktp Field",
                "verbose_name_plural": "Mktp Fields",
            },
        ),
        migrations.AlterModelOptions(
            name="mktpfieldmapping",
            options={
                "verbose_name": "Mktp Field Mapping",
                "verbose_name_plural": "Mktp Field Mappings",
            },
        ),
        migrations.AlterModelOptions(
            name="mktpfieldrule",
            options={
                "ordering": ["mktp_subcat_field", "sequence"],
                "verbose_name": "Mktp Field Rule",
                "verbose_name_plural": "Mktp Field Rules",
            },
        ),
        migrations.AlterModelOptions(
            name="mktpsubcat",
            options={
                "ordering": ["mktp", "subcat"],
                "verbose_name": "Mktp SubCat",
                "verbose_name_plural": "Mktp SubCats",
            },
        ),
        migrations.AlterModelOptions(
            name="mktpsubcatfield",
            options={
                "ordering": ["mktp_subcat", "column_order"],
                "verbose_name": "Mktp SubCat Field",
                "verbose_name_plural": "Mktp SubCat Fields",
            },
        ),
        migrations.AlterModelOptions(
            name="mktpsubcatfieldvalue",
            options={
                "ordering": ["mktp_subcat_field", "sequence"],
                "verbose_name": "Mktp SubCat Field Value",
                "verbose_name_plural": "Mktp SubCat Field Values",
            },
        ),
        migrations.AlterModelOptions(
            name="validvalue",
            options={
                "ordering": ["mktp_field", "sequence", "value"],
                "verbose_name": "Valid Value",
                "verbose_name_plural": "Valid Values",
            },
        ),

        # Recreate constraints using the renamed fields.
        migrations.AddConstraint(
            model_name="mktpfield",
            constraint=models.UniqueConstraint(
                fields=("mktp", "code"),
                name="unique_mktp_field_code",
            ),
        ),
        migrations.AddConstraint(
            model_name="mktpsubcat",
            constraint=models.UniqueConstraint(
                fields=("mktp", "subcat"),
                name="unique_mktp_subcat",
            ),
        ),
        migrations.AddConstraint(
            model_name="mktpsubcatfield",
            constraint=models.UniqueConstraint(
                fields=("mktp_subcat", "column_order"),
                name="unique_mktp_subcat_column_order",
            ),
        ),
        migrations.AddConstraint(
            model_name="mktpsubcatfieldvalue",
            constraint=models.UniqueConstraint(
                fields=("mktp_subcat_field", "valid_value"),
                name="unique_allowed_value_per_subcat_field",
            ),
        ),
        migrations.AddConstraint(
            model_name="validvalue",
            constraint=models.UniqueConstraint(
                fields=("mktp_field", "value"),
                name="unique_valid_value_per_mktp_field",
            ),
        ),
    ]
