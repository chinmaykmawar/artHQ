from asyncio.log import logger


from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.shortcuts import redirect, render
from Website.helpers.factory import DataFactory
from Website.BusinessLayer import OrderService, ProductService, UserService
from django.views.decorators.csrf import csrf_exempt

def index(request):
    #return render(request, 'homepage.html')
    return redirect('/products')

def products_grid(request):
    return render(request, 'core/products_grid.html')

def product(request, id):
    return render(request, 'core/product_page.html', {'id':id})

def test(request):
    return render(request, 'misc/test.html')

def test2(request, id):
    return render(request, 'misc/test2.html', {'id':id})

def checkout_view(request):
    return render(request, 'nav/checkout.html')

def order_success(request):
    order_id = request.GET.get('order_id', '')
    return render(request, 'nav/order_success.html', {"order_id": order_id})

def track_order(request):
    return render(request,'nav/track_order.html')

def returns_exchange(request):
    return render(request, 'common/returns_exchange.html')

def privacy_policy(request):
    return render(request,'common/privacy_policy.html')
    
def terms(request):
    return render(request,'common/terms.html')

def our_story(request):
    return render(request,'common/our_story.html')

def contact_us(request):
    return render(request,'common/contact_us.html')

def get_all_products(request,all_images):
    return ProductService.get_all_products(request, all_images)

def get_product_images(request, product_id):
    return ProductService.get_product_images(product_id, "WEBSITE")

@csrf_exempt
def create_order(request):
    return OrderService.create_order(request)

@csrf_exempt
def verify_payment(request):
    return OrderService.verify_payment(request)

@csrf_exempt
def get_orders(request):
    return OrderService.get_orders(request)

def login_page(request):
    return render(request, "nav/login.html")

def login_user(request):
    return UserService.login(request)

def logout_user(request):
    return UserService.logout(request)