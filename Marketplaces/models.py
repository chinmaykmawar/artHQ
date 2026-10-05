from django.db import models
from Website.core.models import Marketplace, SubCategory

class MarketplaceSubcategory(models.Model):
    """
    Defines which ArtHQ SubCategory is supported by a particular Marketplace.

    Example:
        Amazon + Bracelet
        Amazon + Necklace
        Flipkart + Bracelet
    """

    marketplace = models.ForeignKey(Marketplace,on_delete=models.PROTECT,related_name="marketplace_subcategories",)
    subcategory = models.ForeignKey(SubCategory,on_delete=models.PROTECT,related_name="marketplace_configurations",)
    template_version = models.CharField(max_length=50,blank=True,)
    is_active = models.BooleanField(default=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "marketplace_subcategory"
        constraints = [models.UniqueConstraint(
                fields=["marketplace", "subcategory"],
                name="unique_marketplace_subcategory",
            ),
        ]
        ordering = ["marketplace", "subcategory"]
        verbose_name = "Marketplace Subcategory"
        verbose_name_plural = "Marketplace Subcategories"
    def __str__(self):
        return f"{self.marketplace.code} - {self.subcategory.name}"

class MarketplaceField(models.Model):
    """
    Defines a marketplace-specific field.

    This is the reusable definition of a field within a marketplace.

    Example:
        Amazon:
            Brand Name
            Product Id
            Product Id Type

        Flipkart:
            Brand
            Base Material
            Seller SKU ID
    """

    marketplace = models.ForeignKey(Marketplace,on_delete=models.PROTECT,related_name="fields",)
    name = models.CharField(max_length=255,)
    code = models.CharField(max_length=100,)
    description = models.TextField(blank=True,)
    is_active = models.BooleanField(default=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "marketplace_field"
        constraints = [models.UniqueConstraint(
                fields=["marketplace", "code"],
                name="unique_marketplace_field_code",
            ),
        ]
        ordering = ["marketplace", "name"]
        verbose_name = "Marketplace Field"
        verbose_name_plural = "Marketplace Fields"

    def __str__(self):
        return f"{self.marketplace.code} - {self.name}"

class MarketplaceSubcategoryField(models.Model):
    """
    Associates a MarketplaceField with a MarketplaceSubcategory and
    defines how that field behaves for that particular subcategory.
    """
    class DataType(models.TextChoices):
        TEXT = "TEXT", "Text"
        NUMBER = "NUMBER", "Number"
        DECIMAL = "DECIMAL", "Decimal"
        BOOLEAN = "BOOLEAN", "Boolean"
        URL = "URL", "URL"
        DATE = "DATE", "Date"
        DATETIME = "DATETIME", "DateTime"

    class Cardinality(models.TextChoices):
        SINGLE = "SINGLE", "Single"
        MULTI = "MULTI", "Multiple"

    class RequirementType(models.TextChoices):
        REQUIRED = "REQUIRED", "Required"
        CONDITIONAL = "CONDITIONAL", "Conditionally Required"
        OPTIONAL = "OPTIONAL", "Optional"
        RECOMMENDED = "RECOMMENDED", "Recommended"
        SYSTEM = "SYSTEM", "System Filled"

    marketplace_subcategory = models.ForeignKey(MarketplaceSubcategory,on_delete=models.CASCADE,related_name="fields",)
    marketplace_field = models.ForeignKey(MarketplaceField,on_delete=models.PROTECT,related_name="subcategory_configurations",)
    column_order = models.PositiveIntegerField()
    data_type = models.CharField(max_length=20,choices=DataType.choices,)
    cardinality = models.CharField(max_length=10,choices=Cardinality.choices,default=Cardinality.SINGLE,)
    requirement_type = models.CharField(max_length=20,choices=RequirementType.choices,default=RequirementType.OPTIONAL,)
    usage = models.JSONField(default=list,blank=True,)
    example = models.TextField(blank=True,)
    validation_config = models.JSONField(default=dict,blank=True,)
    is_active = models.BooleanField(default=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "marketplace_subcategory_field"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "marketplace_subcategory",
                    "marketplace_field",
                ],
                name="unique_marketplace_subcategory_field",
            ),
            models.UniqueConstraint(
                fields=[
                    "marketplace_subcategory",
                    "column_order",
                ],
                name="unique_marketplace_subcategory_column_order",
            ),
        ]
        ordering = ["marketplace_subcategory","column_order",]
        verbose_name = "Marketplace Subcategory Field"
        verbose_name_plural = "Marketplace Subcategory Fields"

    def __str__(self):
        return (
            f"{self.marketplace_subcategory} - "
            f"{self.marketplace_field.name}"
        )

class ValidValue(models.Model):
    """
    A possible value for a MarketplaceField.

    ValidValue belongs to a MarketplaceField, while the actual set of
    values allowed for a particular subcategory is defined through
    MarketplaceSubcategoryFieldValue.
    """
    marketplace_field = models.ForeignKey(MarketplaceField,on_delete=models.CASCADE,related_name="valid_values",)
    value = models.CharField(max_length=255,)
    display_value = models.CharField(max_length=255,blank=True,)
    code = models.CharField(max_length=100,blank=True,)
    sequence = models.PositiveIntegerField(default=0,)
    class Meta:
        db_table = "marketplace_valid_value"
        constraints = [
            models.UniqueConstraint(
                fields=["marketplace_field", "value"],
                name="unique_valid_value_per_marketplace_field",
            ),
        ]
        ordering = ["marketplace_field", "sequence", "value"]
        verbose_name = "Valid Value"
        verbose_name_plural = "Valid Values"
    def __str__(self):
        return self.display_value or self.value

class MarketplaceSubcategoryFieldValue(models.Model):
    """
    Defines which ValidValues are actually permitted for a field in a
    particular MarketplaceSubcategory.

    This is important because the same MarketplaceField can have
    different allowed values in different subcategories.
    """

    marketplace_subcategory_field = models.ForeignKey(MarketplaceSubcategoryField,on_delete=models.CASCADE,related_name="allowed_values",)
    valid_value = models.ForeignKey(ValidValue,on_delete=models.PROTECT,related_name="subcategory_usages",)
    sequence = models.PositiveIntegerField(default=0,)
    class Meta:
        db_table = "marketplace_subcategory_field_value"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "marketplace_subcategory_field",
                    "valid_value",
                ],
                name="unique_allowed_value_per_subcategory_field",
            ),
        ]
        ordering = ["marketplace_subcategory_field","sequence",]
        verbose_name = "Marketplace Subcategory Field Value"
        verbose_name_plural = "Marketplace Subcategory Field Values"

class MarketplaceFieldMapping(models.Model):
    """
    Defines where the value for a marketplace field comes from.

    The source can be an ArtHQ Product field, marketplace listing data,
    a constant, calculated value, generated value, etc.
    """
    class SourceType(models.TextChoices):
        PRODUCT = "PRODUCT", "Product"
        PRODUCT_VARIANT = "PRODUCT_VARIANT", "Product Variant"
        MARKETPLACE_LISTING = "MARKETPLACE_LISTING", "Marketplace Listing"
        CONSTANT = "CONSTANT", "Constant"
        CALCULATED = "CALCULATED", "Calculated"
        GENERATED = "GENERATED", "Generated"
        USER_INPUT = "USER_INPUT", "User Input"
        SYSTEM = "SYSTEM", "System"

    marketplace_subcategory_field = models.OneToOneField(MarketplaceSubcategoryField,on_delete=models.CASCADE,related_name="mapping",)
    source_type = models.CharField(max_length=30,choices=SourceType.choices,)
    source_field = models.CharField(max_length=255,blank=True,)
    transformation = models.CharField(max_length=100,blank=True,)
    transformation_config = models.JSONField(default=dict,blank=True,)
    is_active = models.BooleanField(default=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "marketplace_field_mapping"
        verbose_name = "Marketplace Field Mapping"
        verbose_name_plural = "Marketplace Field Mappings"
    def __str__(self):
        return (
            f"{self.marketplace_subcategory_field} -> "
            f"{self.source_type}:{self.source_field}"
        )

class MarketplaceFieldRule(models.Model):
    """
    Conditional validation / requirement rule for a marketplace field.

    Example:

        IF Product Id Type != "GTIN Exempt"
        THEN Product Id is REQUIRED
    """
    marketplace_subcategory_field = models.ForeignKey(MarketplaceSubcategoryField,on_delete=models.CASCADE,related_name="rules",)
    name = models.CharField(max_length=255,)
    condition = models.JSONField(default=dict,)
    action = models.JSONField(default=dict,)
    sequence = models.PositiveIntegerField(default=0,)
    is_active = models.BooleanField(default=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "marketplace_field_rule"
        ordering = ["marketplace_subcategory_field","sequence",]
        verbose_name = "Marketplace Field Rule"
        verbose_name_plural = "Marketplace Field Rules"
    def __str__(self):
        return self.name