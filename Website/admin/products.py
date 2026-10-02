from django import forms
from django.contrib import admin,messages
from django.db import transaction
from django.shortcuts import get_object_or_404,redirect,render
from django.urls import path,reverse
from Website.core.models import Category,SubCategory,Design,Color,Product,Marketplace,ProductMarketplace,ImageData
from Website.helpers.factory import DataFactory,ImageFactory
from .images import ProductImageInline


class InsertProductForm(forms.ModelForm):
    category=forms.ModelChoiceField(queryset=Category.objects.all())
    subcategory=forms.ModelChoiceField(queryset=SubCategory.objects.all())
    design_code=forms.CharField(max_length=5)
    create_design=forms.BooleanField(required=False,label="Create New Design")
    primary_color=forms.CharField(max_length=50)
    secondary_color=forms.CharField(max_length=50,required=False)
    multicolor=forms.BooleanField(required=False,label="Multicolor")

    class Meta:
        model=Product
        fields=("category","subcategory","design_code","create_design","primary_color","secondary_color","multicolor","title","description","inventory","is_active")

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
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

        codes=Design.objects.filter(subcategory=subcategory).values_list("design_code",flat=True)
        numbers=[int(code) for code in codes if code.isdigit()]
        return str(max(numbers+[minimum])+1).zfill(5)

    @staticmethod
    def primary_code(color):
        codes={"black":"Bk","blue":"Bl","green":"Gr","red":"Re","white":"Wh","yellow":"Ye","orange":"Or","pink":"Pi","purple":"Pu","gold":"Go","silver":"Si","grey":"Gy","gray":"Gy","brown":"Br"}
        return codes.get(color.lower(),color[:2].title())

    def get_color_code(self,primary,secondary,multicolor):
        if multicolor:
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

    def save(self,commit=True):
        with transaction.atomic():
            subcategory=self.cleaned_data["subcategory"]
            design_code=self.cleaned_data["design_code"]
            design=Design.objects.filter(subcategory=subcategory,design_code=design_code).first()

            if not design:
                design=Design.objects.create(subcategory=subcategory,design_code=design_code)

            primary=self.cleaned_data["primary_color"]
            secondary=self.cleaned_data["secondary_color"]
            color_code=self.cleaned_data["_color_code"]

            color,created=Color.objects.get_or_create(
                base_color=primary,
                highlight=secondary,
                defaults={"code":color_code}
            )

            self.instance.design=design
            self.instance.color=color
            self.instance.product_id=self.cleaned_data["_product_id"]

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
    form=InsertProductForm
    change_form_template="change_form.html"
    list_display=("product_id","inventory","is_active","title","design","color")
    search_fields=("product_id","title")
    list_filter=("is_active","design","color","design__subcategory")
    inlines=[ProductImageInline,ProductMarketplaceInline]

    def get_form(self,request,obj=None,**kwargs):
        form=super().get_form(request,obj,**kwargs)
        if obj is None:
            form.base_fields["design_code"].help_text="Enter existing code or tick Create New Design."
        return form

    def get_urls(self):
        urls=super().get_urls()
        custom_urls=[
            path("<int:pk>/upload-image-form/",self.admin_site.admin_view(self.render_upload_image_form),name="product_upload_image"),
            path("<int:pk>/upload-image/",self.admin_site.admin_view(self.upload_image),name="product_upload_image_save"),
        ]
        return custom_urls+urls

    def render_upload_image_form(self,request,pk):
        product=get_object_or_404(Product,id=pk)
        return render(request,"upload_image.html",{"product":product,"marketplaces":Marketplace.objects.filter(is_active=True),"opts":self.model._meta})

    def upload_image(self,request,pk):
        product=get_object_or_404(Product,id=pk)
        image=request.FILES.get("image")
        if not image:
            messages.error(request,"Please select an image.")
            return redirect(request.path)

        im=ImageFactory.get_image_manager()
        idm=DataFactory.get_imageData_manager()
        result=im.upload_image(image,product.product_id)
        next_order=(product.images.order_by("-display_order").values_list("display_order",flat=True).first() or 0)+1
        res=idm.create_ImageData(product,result,next_order,request)

        if res:
            messages.success(request,"Image uploaded successfully.")
        else:
            messages.error(request,"Failed to upload image.")

        return redirect("admin:core_product_change",product.id)

    def change_view(self,request,object_id,form_url="",extra_context=None):
        extra_context=extra_context or {}
        extra_context["upload_image_url"]=reverse("admin:product_upload_image",args=[object_id])
        return super().change_view(request,object_id,form_url,extra_context=extra_context)

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