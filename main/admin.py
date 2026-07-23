from django.contrib import admin

from .models import (
    Category,
    SubCategory,
    Design,
    Color,
    Product,
)

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Design)
admin.site.register(Color)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_id",
        "title",
        "design",
        "color",
        "price",
        "is_active",
    )

    search_fields = (
        "product_id",
        "title",
    )

    list_filter = (
        "is_active",
        "design",
        "color",
    )