from typing import Self
import json
from django import forms
from django.contrib import admin,messages
from django.db import transaction
from django.http import request
from django.shortcuts import get_object_or_404,redirect,render
from django.urls import path,reverse
from Website.core.models import Category,SubCategory,Design,Color,Product,Marketplace,ProductMarketplace,ImageData
from Website.core.views import product
from Website.helpers.factory import DataFactory,ImageFactory
from AI.Client import ollamaManager
from .images import ProductImageInline
import logging

logger=logging.getLogger(__name__)

class MultipleFileField(forms.FileField):
    def clean(self, data, initial=None):
        if not data:
            raise forms.ValidationError(
                "At least one product image is required."
            )
        
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(file, initial) for file in data]
        else:
            result = single_file_clean(data, initial)

        return result

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class InsertProductForm(forms.ModelForm):
    category=forms.ModelChoiceField(queryset=Category.objects.all())
    subcategory=forms.ModelChoiceField(queryset=SubCategory.objects.all())
    design_code=forms.CharField(max_length=5,required=False)
    create_design=forms.BooleanField(required=False,label="Create New Design")
    primary_color=forms.CharField(max_length=50,required=False)
    secondary_color=forms.CharField(max_length=50,required=False)
    multicolor=forms.BooleanField(required=False,label="Multicolor")
    product_images = MultipleFileField(required=False,label="Product Images",widget=MultipleFileInput(attrs={"multiple": True, "accept": "image/*"}))
    title = forms.CharField(required=False)
    description=forms.CharField(required=False)
    
    class Meta:
        model=Product
        fields=("category","subcategory","design_code","create_design","primary_color","secondary_color","multicolor","title","description","inventory","is_active")

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.testing=True
        self.fields["title"].required = False
        self.fields["description"].required = False
        if self.instance and self.instance.pk:
            product=self.instance
            design=product.design
            subcategory=design.subcategory
            color=product.color

            self.initial["category"]=subcategory.category
            self.initial["subcategory"]=subcategory
            self.initial["design_code"]=design.design_code
            self.initial["create_design"]=False
            self.initial["primary_color"]=color.base_color
            self.initial["secondary_color"]=color.highlight
            self.initial["multicolor"]=(color.code=="Mul")
        
        category_id=self.data.get("category") if self.is_bound else None
        if category_id:
            self.fields["subcategory"].queryset=SubCategory.objects.filter(category_id=category_id)
        self.fields["design_code"].widget.attrs["list"]="design-code-list"
        self.fields["design_code"].widget.attrs["autocomplete"]="off"

    def clean(self):
        data=super().clean()
        category=data.get("category")
        subcategory=data.get("subcategory")
        design_code=(data.get("design_code") or "").strip()
        create_design=data.get("create_design")
        primary=(data.get("primary_color") or "").strip()
        secondary=(data.get("secondary_color") or "").strip()
        multicolor=data.get("multicolor")

        logger.debug(f"Cleaning product form data: {data}")
        logger.debug(f"Category: {category}, Subcategory: {subcategory}, Design Code: {design_code}, Create Design: {create_design}, Primary Color: {primary}, Secondary Color: {secondary}, Multicolor: {multicolor}")

        if category and subcategory and subcategory.category_id!=category.id:
            self.add_error("subcategory","Subcategory does not belong to selected category.")

        if multicolor:
            primary="Multicolor"
            secondary=""
            data["primary_color"]=primary
            data["secondary_color"]=secondary
        elif not primary:
            self.add_error("primary_color","Enter the primary color.")
        elif secondary.lower()==primary.lower():
            self.add_error("secondary_color","Primary and secondary colors cannot be the same.")

        if subcategory:
            if create_design:
                design_code=self.get_next_design_code(subcategory)
                data["design_code"]=design_code
            elif not design_code:
                self.add_error("design_code","Enter an existing Design Code or select Create New Design.")
            elif not Design.objects.filter(subcategory=subcategory,design_code=design_code).exists():
                self.add_error("design_code","Design Code does not exist for this Subcategory.")

        if subcategory and design_code and not self.errors.get("design_code"):
            color_code=self.get_color_code(primary,secondary,multicolor)
            data["_color_code"]=color_code
            data["_product_id"]=f"{category.code}{subcategory.code}{design_code}{color_code}"

            if Product.objects.filter(product_id=data["_product_id"]).exists():
                self.add_error("design_code",f"Product {data['_product_id']} already exists.")

        return data

    def get_next_design_code(self,subcategory):
        if subcategory.category.code=="J":
            prefixes={"Earrings":"1","Necklace":"2","Bracelets":"3","Jewellery Sets":"4"}
            prefix=prefixes.get(subcategory.name)
            if not prefix:
                raise forms.ValidationError(f"No Design Code rule defined for {subcategory.name}.")
            minimum=int(f"{prefix}0000")
        else:
            minimum=0

        codes=Design.objects.filter(subcategory=subcategory, design_code__startswith=prefix).values_list("design_code",flat=True)
        numbers=[int(code) for code in codes if code.isdigit()]
        return str(max(numbers+[minimum])+1).zfill(5)

    @staticmethod
    def primary_code(color):
        codes={"black":"Bk","blue":"Bl","green":"Gr","red":"Re","white":"Wh","yellow":"Ye","orange":"Or","pink":"Pi","purple":"Pu","gold":"Go","silver":"Si","grey":"Gy","gray":"Gy","brown":"Br"}
        return codes.get(color.lower(),color[:2].title())

    def get_color_code(self,primary,secondary,multicolor):
        logger.debug(f"Generating color code for Primary: {primary}, Secondary: {secondary}, Multicolor: {multicolor}")

        if multicolor:
            logger.debug("Multicolor is selected, returning 'Mul' as color code.")
            return "Mul"

        if not secondary:
            code=primary[:3].title()

            if not Color.objects.filter(code=code).exists():
                return code

            for length in range(4,len(primary)+1):
                code=primary[:length].title()

                if not Color.objects.filter(code=code).exists():
                    return code

            raise forms.ValidationError(f"Unable to generate a unique color code for {primary}.")

        exact=Color.objects.filter(base_color=primary,highlight=secondary).first()

        if exact:
            return exact.code

        prefix=self.primary_code(primary)
        code=f"{prefix}{secondary[0].upper()}"

        if not Color.objects.filter(code=code).exists():
            return code

        for length in range(2,len(secondary)+1):
            code=f"{prefix}{secondary[:length].title()}"

            if not Color.objects.filter(code=code).exists():
                return code

        raise forms.ValidationError(f"Unable to generate a unique color code for {primary} + {secondary}.")

    def upload_image(self, image):
        im=ImageFactory.get_image_manager()
        idm=DataFactory.get_imageData_manager()
        result=im.upload_image(image,self.instance.product_id, test=self.testing)
        product=self.instance
        next_order=(product.images.order_by("-display_order").values_list("display_order",flat=True).first() or 0)+1
        res=idm.create_ImageData(product,result,next_order,marketplaces=None)
        if not res:
            raise forms.ValidationError("Failed to upload image.")

    def save(self,commit=True):
        logger.debug(f"Saving product form with cleaned data: {self.cleaned_data}")
        self.instance = super().save(commit=False)
        with transaction.atomic():
            subcategory=self.cleaned_data["subcategory"]
            design_code=self.cleaned_data["design_code"]
            design=Design.objects.filter(subcategory=subcategory,design_code=design_code).first()

            if not design:
                design=Design.objects.create(
                    subcategory=subcategory,
                    design_code=design_code
                )

            primary=self.cleaned_data["primary_color"]
            secondary=self.cleaned_data["secondary_color"]
            color_code=self.cleaned_data["_color_code"]

            if color_code == "Mul":
                color=Color.objects.get(code=color_code)
            else:
                color,created=Color.objects.get_or_create(
                base_color=primary,
                highlight=secondary,
                defaults={"code":color_code}
                )

            self.instance.design=design
            self.instance.color=color
            self.instance.product_id=self.cleaned_data["_product_id"]
            if self.testing:
                self.instance.product_id = self.instance.product_id+"temp"

            self.instance.title = "Generating Title......"
            self.instance.description = "Generating Description......"
            om = ollamaManager()
            if om.check_ollama():
                if self.testing:
                    self.instance.title = "Test Title"
                    self.instance.description = "Test Description"  
                else:
                    generated_data = om.generate_product_content(
                        details=f"Category: {self.cleaned_data['category'].name}, Subcategory: {subcategory.name}, Design Code: {design_code}, Primary Color: {primary}, Secondary Color: {secondary}, Multicolor: {self.cleaned_data['multicolor']}",
                        images=self.cleaned_data["product_images"]
                        )
                    data = json.loads(generated_data)
                    self.instance.title = data.get("title", "")
                    self.instance.description = data.get("description", "")
            else:
                raise forms.ValidationError("Ollama is not available. Please ensure Ollama is installed and running.")
            
            logger.debug(f"Product instance prepared: {self.instance}")
            
            if commit:
                self.instance.save()
            
        return self.instance

@admin.register(ProductMarketplace)
class ProductMarketplaceAdmin(admin.ModelAdmin):
    list_display=("product","marketplace","price","inventory","is_active")
    search_fields=("product__product_id","marketplace_product_id","marketplace_sku")
    list_filter=("marketplace","is_active")

class ProductMarketplaceInline(admin.TabularInline):
    model=ProductMarketplace
    extra=0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    change_form_template = "EditProduct.html"
    list_display=("product_id","inventory","is_active","title","design","color")
    search_fields=("product_id","title")
    list_filter=("is_active","design","color","design__subcategory")
    inlines=[ProductImageInline,ProductMarketplaceInline]

    @staticmethod
    def upload_image(image, product, marketplaces=None):
        im=ImageFactory.get_image_manager()
        idm=DataFactory.get_imageData_manager()
        result=im.upload_image(image,product.product_id)
        next_order=(product.images.order_by("-display_order").values_list("display_order",flat=True).first() or 0)+1
        res=idm.create_ImageData(product,result,next_order,marketplaces)
        if not res:
            return False
        return True
    
##################  Add Product  ######################

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs["form"] = InsertProductForm
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            form.base_fields["design_code"].help_text="Enter existing code or tick Create New Design."
        return form
    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        for image in form.cleaned_data.get("product_images", []):
            res=self.upload_image(image)
            if not res:
                raise ValueError("could not upload images")
    
##################  Edit Product  ######################
    
    def get_urls(self):
        urls=super().get_urls()

        custom_urls=[
            path(
                "<int:pk>/productImage_upload_form/",
                self.admin_site.admin_view(self.render_upload_form),
                name="productImage_upload"
            ),
            path(
                "<int:pk>/update_ImageData/",
                self.admin_site.admin_view(self.update_ImageData),
                name="update_ImageData"
            ),
        ]

        return custom_urls+urls

    def render_upload_form(self,request,pk):
        product=get_object_or_404(Product,id=pk)

        return render(
            request,
            "upload_image.html",
            {
                "product":product,
                "marketplaces":Marketplace.objects.filter(is_active=True),
                "opts":self.model._meta
            }
        )

    def update_ImageData(self,request,pk):
        product=get_object_or_404(Product,id=pk)
        image=request.FILES.get("image")
        if not image:
            messages.error(request,"Please select an image.")
            return redirect(request.path)
            
        res=self.upload_image(image, product.id)
        if not res:
            raise ValueError("Failed to upload image.")
        return redirect("admin:core_product_change",product.id)
    
    def change_view(self,request,object_id,form_url="",extra_context=None):
        extra_context=extra_context or {}

        extra_context["upload_image_url"]=reverse(
            "admin:productImage_upload",
            args=[object_id]
        )

        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context
        )

    def save_formset(self,request,form,formset,change):
        instances=formset.save(commit=False)

        for obj in formset.deleted_objects:
            if isinstance(obj,ImageData):
                ImageFactory.get_image_manager().delete_image(obj.public_id)

        for instance in instances:
            instance.save()

        formset.save_m2m()

        for obj in formset.deleted_objects:
            obj.delete()