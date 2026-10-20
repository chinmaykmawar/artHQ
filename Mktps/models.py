from django.db import models
from Website.core.models import Mktp, SubCat

class MktpSubCat(models.Model):
    """
    Defines which ArtHQ SubCat is supported by a particular Mktp.

    Example:
        Amazon + Bracelet
        Amazon + Necklace
        Flipkart + Bracelet
    """

    mktp = models.ForeignKey(Mktp,on_delete=models.PROTECT,related_name="mktp_subcats",)
    subcat = models.ForeignKey(SubCat,on_delete=models.PROTECT,related_name="mktp_configurations",)
    template_version = models.CharField(max_length=50,blank=True,)
    is_active = models.BooleanField(default=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "mktp_subcat"
        constraints = [models.UniqueConstraint(
                fields=["mktp", "subcat"],
                name="unique_mktp_subcat",
            ),
        ]
        ordering = ["mktp", "subcat"]
        verbose_name = "Mktp SubCat"
        verbose_name_plural = "Mktp SubCats"
    def __str__(self):
        return f"{self.mktp.code} - {self.subcat.name}"

class MktpField(models.Model):
    """
    Defines a mktp-specific field.

    This is the reusable definition of a field within a mktp.

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

    mktp = models.ForeignKey(Mktp,on_delete=models.PROTECT,related_name="fields",)
    name = models.CharField(max_length=255,)
    code = models.CharField(max_length=100,)
    description = models.TextField(blank=True,)
    is_active = models.BooleanField(default=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "mktp_field"
        constraints = [models.UniqueConstraint(
                fields=["mktp", "code"],
                name="unique_mktp_field_code",
            ),
        ]
        ordering = ["mktp", "name"]
        verbose_name = "Mktp Field"
        verbose_name_plural = "Mktp Fields"

    def __str__(self):
        return f"{self.mktp.code} - {self.name}"

class MktpSubCatField(models.Model):
    """
    Associates a MktpField with a MktpSubCat and
    defines how that field behaves for that particular subcat.
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

    mktp_subcat = models.ForeignKey(MktpSubCat,on_delete=models.CASCADE,related_name="fields",)
    mktp_field = models.ForeignKey(MktpField,on_delete=models.PROTECT,related_name="subcat_configurations",)
    column_order = models.PositiveIntegerField()
    attribute_path = models.CharField(max_length=500, null=True, blank=True)
    column_label = models.CharField(max_length=255, null=True, blank=True)
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
        db_table = "mktp_subcat_field"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "mktp_subcat",
                    "column_order",
                ],
                name="unique_mktp_subcat_column_order",
            ),
        ]
        ordering = ["mktp_subcat","column_order",]
        verbose_name = "Mktp SubCat Field"
        verbose_name_plural = "Mktp SubCat Fields"

    def __str__(self):
        return (
            f"{self.mktp_subcat} - "
            f"{self.mktp_field.name}"
        )

class ValidValue(models.Model):
    """
    A possible value for a MktpField.

    ValidValue belongs to a MktpField, while the actual set of
    values allowed for a particular subcat is defined through
    MktpSubCatFieldValue.
    """
    mktp_field = models.ForeignKey(MktpField,on_delete=models.CASCADE,related_name="valid_values",)
    value = models.CharField(max_length=255,)
    display_value = models.CharField(max_length=255,blank=True,)
    code = models.CharField(max_length=100,blank=True,)
    sequence = models.PositiveIntegerField(default=0,)
    class Meta:
        db_table = "mktp_valid_value"
        constraints = [
            models.UniqueConstraint(
                fields=["mktp_field", "value"],
                name="unique_valid_value_per_mktp_field",
            ),
        ]
        ordering = ["mktp_field", "sequence", "value"]
        verbose_name = "Valid Value"
        verbose_name_plural = "Valid Values"
    def __str__(self):
        return self.display_value or self.value

class MktpSubCatFieldValue(models.Model):
    """
    Defines which ValidValues are actually permitted for a field in a
    particular MktpSubCat.

    This is important because the same MktpField can have
    different allowed values in different subcats.
    """

    mktp_subcat_field = models.ForeignKey(MktpSubCatField,on_delete=models.CASCADE,related_name="allowed_values",)
    valid_value = models.ForeignKey(ValidValue,on_delete=models.PROTECT,related_name="subcat_usages",)
    sequence = models.PositiveIntegerField(default=0,)
    class Meta:
        db_table = "mktp_subcat_field_value"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "mktp_subcat_field",
                    "valid_value",
                ],
                name="unique_allowed_value_per_subcat_field",
            ),
        ]
        ordering = ["mktp_subcat_field","sequence",]
        verbose_name = "Mktp SubCat Field Value"
        verbose_name_plural = "Mktp SubCat Field Values"

class MktpFieldMapping(models.Model):
    """
    Defines where the value for a mktp field comes from.

    The source can be an ArtHQ Product field, mktp listing data,
    a constant, calculated value, generated value, etc.
    """
    class ValueType(models.TextChoices):
        CONSTANT = "CONSTANT", "Constant"
        DATABASE = "DATABASE", "Database table, column"
        IMAGE = "IMAGE", "Image (Cloudinary)"
        AI = "AI", "AI-generated (Ollama)"
        CALCULATED = "CALCULATED", "Calculated"
        BLANK = "BLANK", "Blank"

    mktp_subcat_field = models.OneToOneField(MktpSubCatField,on_delete=models.CASCADE,related_name="mapping",)
    value_type = models.CharField(max_length=30,choices=ValueType.choices,)
    value = models.CharField(max_length=255,blank=True,null=True)
    transformation = models.JSONField(default=dict,blank=True,)
    is_active = models.BooleanField(default=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "mktp_field_mapping"
        verbose_name = "Mktp Field Mapping"
        verbose_name_plural = "Mktp Field Mappings"
    def __str__(self):
        return (f"{self.mktp_subcat_field} -> {self.value_type}:{self.value}")

class MktpFieldRule(models.Model):
    """
    Conditional validation / requirement rule for a mktp field.

    Example:

        IF Product Id Type != "GTIN Exempt"
        THEN Product Id is REQUIRED
    """
    mktp_subcat_field = models.ForeignKey(MktpSubCatField,on_delete=models.CASCADE,related_name="rules",)
    name = models.CharField(max_length=255,)
    condition = models.JSONField(default=dict,)
    action = models.JSONField(default=dict,)
    sequence = models.PositiveIntegerField(default=0,)
    is_active = models.BooleanField(default=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "mktp_field_rule"
        ordering = ["mktp_subcat_field","sequence",]
        verbose_name = "Mktp Field Rule"
        verbose_name_plural = "Mktp Field Rules"
    def __str__(self):
        return self.name