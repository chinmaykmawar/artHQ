from . import products,images
from django.contrib import admin
from Website.core.models import Category,SubCategory,Design,Color,Marketplace,Order,OrderItem

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Design)
admin.site.register(Color)
admin.site.register(Marketplace)
admin.site.register(Order)
admin.site.register(OrderItem)