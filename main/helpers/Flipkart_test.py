import os
from pathlib import Path
import pandas as pd

import sys
from pathlib import Path

BASE_DIR = r"C:\Data\artHQ\Website_django"

sys.path.insert(0, str(BASE_DIR))
print(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE","main.core.settings")
import django
django.setup()

from main.core.models import Product,ProductMarketplace,Marketplace

INPUT_DIR = Path.home() / "Downloads"
OUTPUT_DIR = r"C:\Data\artHQ\Website_django\main\helpers"

def verify_flipkart():
    file = max(INPUT_DIR.glob("*.xls"),key=lambda x:x.stat().st_mtime)
    df = pd.read_excel(file)

    marketplace = Marketplace.objects.get(code="FLIPKART")
    db = ProductMarketplace.objects.filter(marketplace=marketplace).select_related("product")

    db_data = {
        pm.product.product_id: {
            "listing_id": pm.marketplace_product_id,
            "serial": pm.marketplace_sku,
            "price": float(pm.price),
            "inventory": pm.inventory,
            "active": pm.is_active,
            "legacy_product_id": pm.product.legacy_product_id
        }
        for pm in db
    }

    discrepancies = []

    for product_id, db_data_row in db_data.items():
        if db_data_row['active']:
            if (df['Seller SKU Id']==product_id).any():
                fk_data_row=df[df['Seller SKU Id']==product_id]
            elif (df['Seller SKU Id']==db_data_row['legacy_product_id']).any():
                fk_data_row=df[df['Seller SKU Id']==db_data_row['legacy_product_id']]
            else:
                discrepancies.append([product_id,"LISTING","Active in DB","Inactive in Flipkart"])
                continue
            
            check={
                "Listing ID":(db_data_row['listing_id'],str(fk_data_row["Listing ID"].values[0])),
                "Serial Number":(db_data_row['serial'],str(fk_data_row["Flipkart Serial Number"].values[0])),
                "Price": (db_data_row['price'],float(fk_data_row["Your Selling Price"].values[0])),
                "Inventory": (db_data_row['inventory'],int(fk_data_row["System Stock count"].values[0])),
            }
            
            for prop, (db_val, fk_val) in check.items():
                if db_val != fk_val:
                    discrepancies.append([product_id,prop,db_val,fk_val])
        else:
            if ((df['Seller SKU Id']==product_id).any()) or ((df['Seller SKU Id']==db_data_row['legacy_product_id']).any()):
                discrepancies.append([product_id,"LISTING","Inactive in DB","Active in Flipkart"])
    
    result = pd.DataFrame(discrepancies,columns=["Product ID","Field","DB (Expected)","Flipkart (Current)"])

    if result.empty:
        print("Flipkart listing matches DB. No discrepancies found.")
    else:
        print("\nDISCREPANCIES:\n")
        print(result.to_string(index=False))
        result.to_string(OUTPUT_DIR + "\\flipkart_discrepancies.txt",index=False)

if __name__ == "__main__":
    verify_flipkart()