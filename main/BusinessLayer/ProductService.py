import os
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from main.helpers.factory import DataFactory

def get_all_products(request):
    pm = DataFactory.get_product_manager()
    products = pm.get_all_products()
    return JsonResponse(products, safe=False)

def get_product_images(product_id):
    folder = os.path.join(
        settings.BASE_DIR,
        'static/assets/Product_Images',
        product_id
    )

    images = []

    if os.path.exists(folder):
        for file in os.listdir(folder):
            if file.endswith('.jpg'):
                images.append(file)

    return JsonResponse(images, safe=False)