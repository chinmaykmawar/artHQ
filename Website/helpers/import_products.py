import os

import django
import pandas as pd
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Website.core.settings")
django.setup()

from Website.core.models import Category, SubCat, Design, Color, Product, Mktp, ProductMktp, Order


# --------------------------------------------------------------------
# CSV Files
# --------------------------------------------------------------------

CATEGORY_FILE = "SKU List - Categories.csv"
SUBCAT_FILE = "SKU List - Sub-Categories.csv"
DESIGN_FILE = "SKU List - Design.csv"
COLOR_FILE = "SKU List - Colors.csv"
PRODUCT_FILE = "SKU List - SKUs.csv"


# --------------------------------------------------------------------
# Helper
# --------------------------------------------------------------------

def clean(value):
    if pd.isna(value):
        return None
    return str(value).strip()

def get_sc_and_design_code(row):
    ldc=None
    d_code = row["Code"]
    if d_code < 1000:
        ldc= f"{int(row['Code']):02d}"
    d_code = f"{int(row['Code']):05d}"
    sc_code = clean(row["Sub-Category"])
    sc_qs = SubCat.objects.filter(code=sc_code)
    sc_obj = sc_qs.first()

    if sc_qs.count() > 1:
        i=1
        while Design.objects.filter(design_code=d_code, subcat=sc_obj).exists():
            sc_obj = sc_qs[i]
            i+=1
    return ldc, d_code, sc_obj

# --------------------------------------------------------------------
# Read CSVs
# --------------------------------------------------------------------

categories_df = pd.read_csv(CATEGORY_FILE)
subcats_df = pd.read_csv(SUBCAT_FILE)
designs_df = pd.read_csv(DESIGN_FILE)
colors_df = pd.read_csv(COLOR_FILE)
products_df = pd.read_csv(PRODUCT_FILE)

products_df = products_df.drop_duplicates(subset=["Product_ID"])


# --------------------------------------------------------------------
# Import
# --------------------------------------------------------------------

with transaction.atomic():

    print("Deleting existing data...")

    Order.objects.all().delete()
    ProductMktp.objects.all().delete()
    Product.objects.all().delete()
    Design.objects.all().delete()
    Color.objects.all().delete()
    SubCat.objects.all().delete()
    Category.objects.all().delete()

    print("Importing Categories...")
    for _, row in categories_df.iterrows():
        Category.objects.create(
            name=clean(row["Categories"]),
            code=clean(row["Code"]),
        )
    print(f"  {len(Category.objects.all())} Categories imported")

    print("Importing SubCats...")
    for _, row in subcats_df.iterrows():
        category = Category.objects.get(name=clean(row["Category"]))
        key = (clean(row["Category"]),clean(row["Sub Cat Code"]),)
        SubCat.objects.create(
            category=category,
            name=clean(row["Sub-Category"]),
            code=clean(row["Sub Cat Code"]),
        )
    print(f"  {len(SubCat.objects.all())} SubCats imported")

    print("Importing Designs...")
    for _, row in designs_df.iterrows():
        
        ldc, design_code, sc_obj = get_sc_and_design_code(row)
        
        Design.objects.create(
            subcat=sc_obj,
            search_criteria=clean(row["Search Criteria"]) or "",
            design_code=design_code,
            legacy_design_code=ldc,
        )
    print(f"  {len(Design.objects.all())} Designs imported")
    
    print("Importing Colors...")
    for _, row in colors_df.iterrows():

        color = Color.objects.create(
            base_color=clean(row["Base Color"]),
            highlight=clean(row["Highlight/Desc"]),
            code=clean(row["Code"]),
        )
    print(f"  {len(Color.objects.all())} Colors imported")
    
    website = Mktp.objects.get(code="WEBSITE")
    flipkart = Mktp.objects.get(code="FLIPKART")
    amazon = Mktp.objects.get(code="AMAZON")
    
    print("Importing Products...")
    for _, row in products_df.iterrows():
        p_id=clean(row["Product_ID"])
        sc=clean(row["Sub_Category"])
        sc_obj=SubCat.objects.get(name=sc)
        c_obj=sc_obj.category
        des_code=(row["Design Code"])
        col_code=clean(row["Color Code"])
        flipkart_product_id=None
        if des_code <1000:
            design=Design.objects.get(legacy_design_code=clean(f"{int(des_code):02d}"), subcat_id=sc_obj.id)
            flipkart_product_id= p_id
            p_id = f"{flipkart_product_id[:3]}{int(des_code):05d}{col_code}"
        else:
            design=Design.objects.get(design_code=clean(f"{int(des_code):05d}"), subcat_id=sc_obj.id)

        product = Product.objects.create(
            design=design, 
            color=Color.objects.get(code=clean(row["Color Code"])), 
            product_id=p_id, 
            title=clean(row["Title"]), 
            description=clean(row["Description"]), 
            inventory=0, 
            is_active=True
            )
        
        for mktp in (website, flipkart, amazon):
            if mktp==flipkart:
                fpid=flipkart_product_id
            else:
                fpid=''    
            ProductMktp.objects.create(
                product=product, 
                mktp=mktp,
                mktp_product_id=fpid,
                price=row["Price"], 
                commission=0, 
                inventory=0, 
                is_active=True)
       
    print(f"  {len(Product.objects.all())} Products imported")


print("\n===================================")
print("Database import completed.")
print("===================================")