import os
from django.http import JsonResponse
from django.conf import settings
from django.http import  HttpResponse
from django.template import loader
from django.shortcuts import redirect, render

def index(request):
    #return render(request, 'homepage.html')
    return redirect('/products')

def products_grid(request):
    return render(request, 'products_grid.html')

def product(request, id):
    return render(request, 'product_page.html', {'id':id})

def test(request):
    return render(request, 'test.html')

def test2(request, id):
    return render(request, 'test.html', {'id':id})


def get_product_images(request, product_id):
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