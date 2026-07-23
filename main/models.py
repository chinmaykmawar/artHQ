from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = "category"
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category,on_delete=models.PROTECT,related_name="subcategories",)

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, db_index=True)

    class Meta:
        db_table = "subcategory"
        ordering = ["category", "name"]

        constraints = [
            models.UniqueConstraint(
                fields=["category", "code"],
                name="unique_subcategory_per_category",
            )
        ]
        verbose_name_plural = "Sub Categories"

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Design(models.Model):
    subcategory = models.ForeignKey(SubCategory,on_delete=models.PROTECT,related_name="designs",)
    search_criteria = models.CharField(max_length=255, blank=True)
    design_code = models.CharField(max_length=5, db_index=True)
    legacy_design_code = models.CharField(max_length=5,null=True,blank=True)

    class Meta:
        db_table = "design"
        ordering = ["design_code"]
        constraints = [models.UniqueConstraint(
            fields=["subcategory", "design_code"],
            name="unique_design_per_subcategory",
            )
        ]
        verbose_name_plural = "Designs"

    def __str__(self):
        return self.design_code

class Color(models.Model):
    base_color = models.CharField(max_length=50)
    highlight = models.CharField(max_length=50)
    code = models.CharField(max_length=10, unique=True, db_index=True,)

    class Meta:
        db_table = "color"
        ordering = ["base_color", "highlight"]
        constraints = [
        models.UniqueConstraint(
            fields=["base_color", "highlight"],
            name="unique_color_combination",
            )
        ]
        verbose_name_plural = "Colors"

    def __str__(self):
        return f"{self.base_color} / {self.highlight}"

class Product(models.Model):
    design = models.ForeignKey(Design,on_delete=models.PROTECT,related_name="products",)
    color = models.ForeignKey(Color,on_delete=models.PROTECT,related_name="products",)
    product_id = models.CharField(max_length=30,unique=True,db_index=True,)
    legacy_product_id = models.CharField(max_length=30,unique=True,null=True,blank=True,)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2,)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product"
        ordering = ["product_id"]
        verbose_name_plural = "Products"

    def __str__(self):
        return self.product_id

class Order(models.Model):

    # Current fields (Mandatory)
    order_date = models.DateTimeField()
    order_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
    )

    payment_id = models.CharField(
        max_length=100,
        blank=True,
    )

    customer_name = models.CharField(max_length=200)

    phone = models.CharField(max_length=20)

    email = models.EmailField()

    address = models.TextField()

    city = models.CharField(max_length=100)

    pincode = models.CharField(max_length=10)

    items_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    delivery_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    tracking_id = models.CharField(
        max_length=100,
        blank=True,
    )

    # Future fields
    marketplace = models.CharField(
        max_length=30,
        blank=True,
    )

    order_status = models.CharField(
        max_length=30,
        blank=True,
    )

    payment_type = models.CharField(
        max_length=30,
        blank=True,
    )

    dispatch_date = models.DateTimeField(
        null=True,
        blank=True,
    )

    delivery_date = models.DateTimeField(
        null=True,
        blank=True,
    )

    state = models.CharField(
        max_length=100,
        blank=True,
    )

    marketplace_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    shipping_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    net_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    remarks = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "orders"
        ordering = ["-order_date"]

    def __str__(self):
        return self.order_id
    
class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    quantity = models.PositiveIntegerField(default=1)

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        db_table = "order_items"
        constraints = [
            models.UniqueConstraint(
                fields=["order", "product"],
                name="unique_product_per_order", 
            )
        ]