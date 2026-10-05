import os
from django.conf import settings
from Website.helpers.custom import CustomJsonResponse
from Website.helpers.factory import DataFactory

def get_all_products(request, all_images):
    pm = DataFactory.get_product_manager()
    try:
        if all_images=='y':
            products = pm.get_all_products(True)
        else:
            products=pm.get_all_products(False)
        return CustomJsonResponse(products)
    except Exception as ex:
        return CustomJsonResponse(None, status="failed", error=f"Failed to fetch products: {ex}")

def get_product_images(product_id, marketplace_code="WEBSITE"):
    pm = DataFactory.get_imageData_manager()
    try:
        images=pm.get_ImageData(product_id,marketplace_code)
        if images:
            return CustomJsonResponse(images)
        else:
            return CustomJsonResponse(None, status="failed", error=f"Product images not found for product_id: {product_id}")
    except Exception as ex:
        return CustomJsonResponse(None, status="failed", error=f"Failed to fetch product images: {ex}")