from asyncio.log import logger


from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.shortcuts import redirect, render
from main.helpers.factory import DataFactory
from main.BusinessLayer import OrderService, ProductService 
from django.views.decorators.csrf import csrf_exempt

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

def checkout_view(request):
    return render(request, 'checkout.html')

def order_success(request):
    order_id = request.GET.get('order_id', '')
    return render(request, 'order_success.html', {"order_id": order_id})

def track_order(request):
    return render(request,'track_order.html')

def returns_exchange(request):
    return render(request, 'returns_exchange.html')

def privacy_policy(request):
    return render(request,'privacy_policy.html')

def terms(request):
    return render(request,'terms.html')

def our_story(request):
    return render(request,'our_story.html')

def contact_us(request):
    return render(request,'contact_us.html')

def get_all_products(request):
    return ProductService.get_all_products(request)

def get_product_images(request, product_id):
    return ProductService.get_product_images(product_id)

@csrf_exempt
def create_order(request):
    return OrderService.create_order(request)

@csrf_exempt
def verify_payment(request):
    return OrderService.verify_payment(request)

@csrf_exempt
def get_orders(request):
    return OrderService.get_orders(request)