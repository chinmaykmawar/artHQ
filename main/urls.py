"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('products', views.products_grid, name='products_grid'),
    path('product/<slug:id>', views.product, name='product_page'),
    path('test/<slug:id>', views.test2, name='test2'),
    path('test', views.test, name='test1'),
    path('get-images/<str:product_id>/', views.get_product_images),
    path('checkout/', views.checkout_view, name='checkout'),
    path('create-order/', views.create_order),
    path('verify-payment/', views.verify_payment),
    path('order-success/', views.order_success),
    path('track-order/', views.track_order, name='track_order'),
    path('get-orders/',views.get_orders,name='get_orders'),
    path('returns-exchange', views.returns_exchange, name='returns_exchange'),
    path('privacy-policy',views.privacy_policy,name='privacy_policy'),
    path('terms',views.terms,name='terms'),
    path('our-story',views.our_story,name='our_story'),
    path('contact-us',views.contact_us,name='contact_us'),
]
