from email.mime import image

from django.contrib import admin,messages
from django.shortcuts import get_object_or_404,redirect,render
from django.urls import path, reverse
from django.utils.html import format_html
from django import forms
from django.db import models
from urllib3 import request

from main.helpers.factory import DataFactory, ImageFactory
from .models import Category,SubCategory,Design,Color,Product,Marketplace,ProductMarketplace,Order,OrderItem,ImageData
import logging

logger = logging.getLogger(__name__)

@admin.register(ProductMarketplace)
class ProductMarketplaceAdmin(admin.ModelAdmin):
    list_display = ("product","marketplace","price","inventory","is_active")
    search_fields = ("product__product_id","marketplace_product_id","marketplace_sku")
    list_filter = ("marketplace","is_active")

class ProductMarketplaceInline(admin.TabularInline):
    model = ProductMarketplace
    extra = 0

class ProductImageInline(admin.TabularInline):
    model = ImageData
    template = "product_image_inline.html"
    extra = 0
    fields = ("image_preview","display_order","marketplaces")
    readonly_fields = ("image_preview",)
    verbose_name = "Product Image"
    verbose_name_plural = "Product Images"
    formfield_overrides = {models.ManyToManyField: {"widget": forms.CheckboxSelectMultiple}}

    class Media:
        css = {"all": ("css/product_image_inline.css",)}

    def has_add_permission(self,request,obj=None):
        return False

    def image_preview(self,obj):
        if not obj.secure_url:
            return "-"
        return format_html('<img src="{}" class="product-image-preview">',obj.secure_url)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    change_form_template = "change_form.html"
    list_display = ("product_id","inventory","is_active","title","design","color")
    search_fields = ("product_id","title")
    list_filter = ("is_active","design","color", "design__subcategory")
    inlines = [ProductImageInline, ProductMarketplaceInline]
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("<int:pk>/upload-image-form/",self.admin_site.admin_view(self.render_upload_image_form),name="product_upload_image"),
            path("<int:pk>/upload-image/",self.admin_site.admin_view(self.upload_image),name="product_upload_image_save"),
        ]
        return custom_urls + urls
        
    def render_upload_image_form(self,request,pk):
        product = get_object_or_404(Product,id=pk)
        return render(request,"upload_image.html",{"product":product,"marketplaces":Marketplace.objects.filter(is_active=True),"opts":self.model._meta})

    def upload_image(self,request,pk):
        product = get_object_or_404(Product,id=pk)
        image = request.FILES.get("image")
        if not image:
            messages.error(request,"Please select an image.")
            return redirect(request.path)

        im = ImageFactory.get_image_manager()
        idm = DataFactory.get_imageData_manager()
        result = im.upload_image(image,product.product_id)
        next_order = (product.images.order_by("-display_order").values_list("display_order",flat=True).first() or 0) + 1
        res = idm.create_ImageData(product,result,next_order,request)

        if res:
            messages.success(request,"Image uploaded successfully.")
        else:
            messages.error(request,"Failed to upload image.")
        return redirect("admin:core_product_change",product.id)

    def change_view(self,request,object_id,form_url="",extra_context=None):
        extra_context = extra_context or {}
        extra_context["upload_image_url"] = reverse("admin:product_upload_image",args=[object_id])
        return super().change_view(request,object_id,form_url,extra_context=extra_context) 
    
    def save_formset(self,request,form,formset,change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            if isinstance(obj,ImageData):
                ImageFactory.get_image_manager().delete_image(obj.public_id)
        for instance in instances:
            instance.save()
        formset.save_m2m()
        for obj in formset.deleted_objects:
            obj.delete()
    
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Design)
admin.site.register(Color)
admin.site.register(Marketplace)
admin.site.register(Order)
admin.site.register(OrderItem)