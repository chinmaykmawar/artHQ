import os
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE","Website.core.settings")
import django
django.setup()

from Website.core.models import Product,ImageData
from Website.helpers.factory import ImageFactory

IMAGE_ROOT = Path("static/assets/Product_Images")
EXTENSIONS = {".jpg",".jpeg",".png",".webp"}

def upload_product_images():
    manager = ImageFactory.get_image_manager()

    for folder in sorted(IMAGE_ROOT.iterdir()):
        if not folder.is_dir() or folder.name == "product_page_images":
            continue

        try:
            product = Product.objects.get(product_id=folder.name)
        except Product.DoesNotExist:
            print(f"PRODUCT NOT FOUND: {folder.name}")
            continue

        images = sorted(folder.iterdir(),key=lambda x:int(x.stem.rsplit("_",1)[1]) if "_" in x.stem and x.stem.rsplit("_",1)[1].isdigit() else 0)

        for order,image in enumerate(images,1):
            if image.suffix.lower() not in EXTENSIONS:
                continue

            if ImageData.objects.filter(product=product,display_order=order).exists():
                print(f"SKIP: {folder.name}/{image.name}")
                continue

            try:
                result = manager.upload_image(image,product.product_id,public_id=image.stem)
                ImageData.objects.create(product=product,public_id=result["public_id"],secure_url=result["secure_url"],display_order=order)
                print(f"UPLOADED: {folder.name}/{image.name}")
            except Exception as e:
                print(f"FAILED: {folder.name}/{image.name} - {e}")

if __name__ == "__main__":
    upload_product_images()