from abc import ABC
import json
from django.http import HttpResponse, JsonResponse
import requests


from main import settings
from .framework import (
    ProductManager,
    CategoryManager,
    SubCategoryManager,
    DesignManager,
    ColorManager,
    OrderManager,
)

import logging

logger = logging.getLogger(__name__)

class GSProductManager(ProductManager):
    
    def get_all_products(self):
        response = requests.get(settings.GS_URL)
        logger.info(f"Fetching all products from Google Sheets. Status code: {response.status_code}")   
        if response.status_code == 200:
            return response.json()

    def get_product(self, product_id):
        raise NotImplementedError

    def create_product(self, data):
        raise NotImplementedError

    def update_product(self, product_id, data):
        raise NotImplementedError

    def delete_product(self, product_id):
        raise NotImplementedError

    def search_products(self, search_text):
        raise NotImplementedError

    def filter_products(
        self,
        categories=None,
        subcategories=None,
        colors=None,
        materials=None,
    ):
        raise NotImplementedError

class GSCategoryManager(CategoryManager):

    def get_all_categories(self):
        raise NotImplementedError

    def get_category(self, category):
        raise NotImplementedError

    def create_category(self, data):
        raise NotImplementedError

    def update_category(self, category, data):
        raise NotImplementedError

    def delete_category(self, category):
        raise NotImplementedError

class GSSubCategoryManager(SubCategoryManager):

    def get_all_subcategories(self):
        raise NotImplementedError

    def get_subcategory(self, category, subcategory):
        raise NotImplementedError

    def create_subcategory(self, data):
        raise NotImplementedError

    def update_subcategory(self, category, subcategory, data):
        raise NotImplementedError

    def delete_subcategory(self, category, subcategory):
        raise NotImplementedError

class GSDesignManager(DesignManager):

    def get_all_designs(self):
        raise NotImplementedError

    def get_design(self, design_code):
        raise NotImplementedError

    def create_design(self, data):
        raise NotImplementedError

    def update_design(self, design_code, data):
        raise NotImplementedError

    def delete_design(self, design_code):
        raise NotImplementedError

class GSColorManager(ColorManager):

    def get_all_colors(self):
        raise NotImplementedError

    def get_color(self, color_code):
        raise NotImplementedError

    def create_color(self, data):
        raise NotImplementedError

    def update_color(self, color_code, data):
        raise NotImplementedError

    def delete_color(self, color_code):
        raise NotImplementedError

class GSOrderManager(OrderManager):

    def save_order(self, data):
        cart_items = data.get("cart", [])

        logger.info(f"Saving order data to Google Sheets: {data}\n\n")

        cart_summary = []
        for item in cart_items:
            product_id = item.get("Product_ID")
            qty = item.get("qty", 1)
            cart_summary.append(f"{product_id} x {qty}")
        cart_string = ", ".join(cart_summary)

        payload = {
            "order_id": data["paymentData"].get("order_id"),
            "payment_id": data["paymentData"].get("transactionId"),

            "name": data["customer"].get("name"),
            "phone": data["customer"].get("phone"),
            'email': data["customer"].get("email"),
            "address": data["customer"].get("address"),
            "city": data["customer"].get("city"),
            "pincode": data["customer"].get("pincode"),

            "item_amount": data["totals"].get("items_total")/100,
            "delivery_charge": data["totals"].get("delivery_charge")/100,
            "total_amount": data["totals"].get("grand_total")/100,
            "cart": cart_string
        }

        logger.info(f"Payload: {payload}\n\n")

        try:
            response = requests.post(settings.GS_URL, json=payload)
            result=response.json()
            status=result.get("status")
            logger.info(f"Google Sheets response: {response.status_code} - {response.text}")
            if status=="success":
                return True
            else:
                raise Exception(result.get("message"))
        except Exception as e:
            logger.error(f"Error saving data to Google Sheets: {str(e)}")
            return False

    def get_order(self, order_id):
        raise NotImplementedError

    def get_orders(self, request, order_ids=None, phone=None):
        data = json.loads(request.body)

        try:
            response = requests.post(settings.GS_URL, json=data)
            logger.info(f"Get orders response: {response.status_code} - {response.text}")   
            return HttpResponse(response.text,content_type='application/json')
        except Exception as e:
            logger.error(f"Error fetching orders from Google Sheets: {str(e)}")
            return JsonResponse({"error": str(e)},status=500)

    def update_order(self, order_id, data):
        raise NotImplementedError

    def update_tracking(self, order_id, tracking_id):
        raise NotImplementedError

    def delete_order(self, order_id):
        raise NotImplementedError