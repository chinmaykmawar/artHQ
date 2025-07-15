from django.http import  HttpResponse
from django.template import loader
from django.shortcuts import render

def index(request):
    return render(request, 'homepage.html')

def products_grid(request):
    return render(request, 'products_grid.html')

def product(request, id):
    return render(request, 'product_page.html', {'id':id})

def test(request):
    return render(request, 'test.html')

def test2(request, id):
    return render(request, 'test2.html', {'abc':id})

