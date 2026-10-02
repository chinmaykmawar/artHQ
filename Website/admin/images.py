from django import forms
from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from Website.core.models import ImageData


class ProductImageInline(admin.TabularInline):
    model=ImageData
    template="product_image_inline.html"
    extra=0
    fields=("image_preview","display_order","marketplaces")
    readonly_fields=("image_preview",)
    verbose_name="Product Image"
    verbose_name_plural="Product Images"
    formfield_overrides={models.ManyToManyField:{"widget":forms.CheckboxSelectMultiple}}

    class Media:
        css={"all":("css/product_image_inline.css",)}

    def has_add_permission(self,request,obj=None):
        return False

    def image_preview(self,obj):
        if not obj.secure_url:
            return "-"
        return format_html('<img src="{}" class="product-image-preview">',obj.secure_url)