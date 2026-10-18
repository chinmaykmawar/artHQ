import os
from pathlib import Path
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE","Website.core.settings")
import django
django.setup()

from django.db import transaction
from Website.core.models import Product,ProductMarketplace,Marketplace

LEGACY_MAP = {
    "JNK10001Pink": "JNK20001Pin",
    "JBR30009PiG": "JBR30009PiGr",
}

FLIPKART_FILE = Path.home() / "Downloads" / "S_listing--ui--group_8c05f0197a4b40b4_2609-160503_default.xls"

df = pd.read_excel(FLIPKART_FILE)
marketplace = Marketplace.objects.get(code="FLIPKART")

with transaction.atomic():
    for legacy_id,current_id in LEGACY_MAP.items():
        row = df[df["Seller SKU Id"].astype(str).str.strip() == legacy_id].iloc[0]
        product = Product.objects.get(product_id=current_id)
        listing = ProductMarketplace.objects.get(product=product,marketplace=marketplace)

        listing.marketplace_sku = str(row["Flipkart Serial Number"]).strip()
        listing.marketplace_product_id = str(row["Listing ID"]).strip()
        listing.is_active = True
        listing.save(update_fields=["marketplace_sku","marketplace_product_id","is_active","updated_at"])

        print(f"UPDATED: {current_id} <- {legacy_id}")

print("Done.")