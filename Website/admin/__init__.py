from . import products,images
from django.contrib import admin
from Website.core.models import Category,SubCat,Design,Color,Mktp,Order,OrderItem

admin.site.register(Category)
admin.site.register(SubCat)
admin.site.register(Design)
admin.site.register(Color)
admin.site.register(Mktp)
admin.site.register(Order)
admin.site.register(OrderItem)