import json

from ..core.models import Product, Order, OrderItem, Marketplace, ProductMarketplace, ImageData
from .framework import (ProductManager,CategoryManager,SubCategoryManager,DesignManager,ColorManager,OrderManager,ImageDataManager,UserManager)

from decimal import Decimal
from django.db import transaction, DatabaseError
from django.utils import timezone
from django.db.models import Prefetch


from django.contrib.auth.models import User
from Website.core.models import CustomerProfile
from Website.helpers.custom import CustomJsonResponse
from .framework import UserManager

import logging

logger = logging.getLogger(__name__)

class PSQLProductManager(ProductManager):
    
    def get_all_products(self, all_images=False):
        try:
            website = Marketplace.objects.get(code="WEBSITE")
            if all_images:
                qs=ImageData.objects.all()
            # elif isinstance(all_images, int):
            #     qs=ImageData.objects.filter(display_order=all_images)
            # elif isinstance(all_images, list):
            #     qs=ImageData.objects.filter(display_order__in=all_images)
            else:
                qs=ImageData.objects.filter(display_order=1)
                #raise ValueError("image nos not recognized")
            products = Product.objects.filter(is_active=True).select_related("design__subcategory","color").prefetch_related(Prefetch("marketplace_data",queryset=ProductMarketplace.objects.filter(marketplace=website,is_active=True)),Prefetch("images",queryset=qs))
            products_json = []
            for p in products:
                marketplace = p.marketplace_data.first()
                images=p.images.all()
                if p.legacy_product_id is not None:
                    p_id = p.legacy_product_id
                else:
                    p_id = p.product_id
                logger.debug(f"{len(images)}// pid:{p_id}")
                products_json.append({
                    "Name": p.product_id,
                    "Price": float(marketplace.price) if marketplace else 0,
                    "Title": p.title,
                    "Description": p.description,
                    "Product_ID": p_id,
                    "Sub_Category": p.design.subcategory.name,
                    "Base_Color": p.color.base_color,
                    "Highlight": p.color.highlight,
                    "Design": p.design.design_code,
                    "Bar Code": "",
                    "Sub-Cat Code": p.design.subcategory.code,
                    "images": [i.public_id for i in images]
                })
            logger.info(f"Fetched {len(products_json)} products from PostgreSQL.")
            return products_json
        except Exception as ex:
            logger.exception(f"Error fetching products from PostgreSQL:{ex}")
            raise DatabaseError(f"Failed to fetch products from PostgreSQL with error {ex}")

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

class PSQLCategoryManager(CategoryManager):

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

class PSQLSubCategoryManager(SubCategoryManager):

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

class PSQLDesignManager(DesignManager):

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

class PSQLColorManager(ColorManager):

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

class PSQLOrderManager(OrderManager):

    @transaction.atomic
    def save_order(self, data):
        
        order = Order.objects.create(
            order_date=timezone.now(),

            order_id=data["paymentData"]["order_id"],
            payment_id=data["paymentData"]["transactionId"],

            customer_name=data["customer"]["name"],
            phone=data["customer"]["phone"],
            email=data["customer"]["email"],
            address=data["customer"]["address"],
            city=data["customer"]["city"],
            pincode=data["customer"]["pincode"],

            items_total=Decimal(data["totals"]["items_total"]) / 100,
            delivery_charge=Decimal(data["totals"]["delivery_charge"]) / 100,
            total=Decimal(data["totals"]["grand_total"]) / 100,
            order_status="Order Confirmed"
        )

        cart = data["cart"]
        product_ids = [item["Product_ID"] for item in cart]
        
        products = Product.objects.filter(product_id__in=product_ids)

        product_map = {product.product_id: product for product in products}
        order_total=Decimal('0.0')
        
        order_items = []

        for item in cart:
            product = product_map.get(item["Product_ID"])
            if product is None:
                raise ValueError(f"Product not found: {item['Product_ID']}")

            qty = item.get("qty", 1)
            price = Decimal(str(item["Price"]))

            order_items.append(
                OrderItem(
                    order=order,
                    product=product,

                    quantity=qty,
                    selling_price=price,

                    discount=Decimal("0.00"),
                    tax=Decimal("0.00"),

                    total=price * qty,
                )
            )
            order_total+=price * qty
            
        if order_total==(Decimal(data["totals"]["items_total"]) / 100):
            OrderItem.objects.bulk_create(order_items)
            logger.info(
                f"Order {order.order_id} saved successfully with "
                f"{len(order_items)} items."
            )
            return True
        else:
            logger.info(f"Order {order.order_id} items total does not match cart ")
            return False

    def get_order(self, order_id):
        raise NotImplementedError

    def get_orders(self, request, order_ids=None, phone=None):
        try:
            data = json.loads(request.body)

            order_ids = data.get("order_ids")
            phone = data.get("phone")

            orders = (
                Order.objects
                .prefetch_related(
                    Prefetch(
                        "items",
                        queryset=OrderItem.objects.select_related("product")
                    )
                )
                .order_by("-order_date")
            )

            if order_ids:
                order_id_list = [
                    x.strip()
                    for x in order_ids.split(",")
                    if x.strip()
                ]

                orders = orders.filter(order_id__in=order_id_list)

            elif phone:
                orders = orders.filter(phone=phone)

            else:
                return CustomJsonResponse(None, status="failed", error="No order_ids or phone provided")

            result = []

            for order in orders:
                order_summary = ", ".join(
                    f"{item.product.title} (x{item.quantity})"
                    for item in order.items.all()
                )

                result.append({
                    "order_id": order.order_id,
                    "created_at": (
                        order.order_date.strftime("%d-%b-%Y %I:%M %p")
                        if order.order_date
                        else ""
                        ),

                    "customer_name": order.customer_name,
                    "phone": order.phone,
                    "address": (
                        f"{order.address}, "
                        f"{order.city} - {order.pincode}"
                    ),

                    "order_summary": order_summary,
                    "total_amount": float(order.total),
                    "tracking_id": order.tracking_id or "",
                    "order_status": order.order_status or "Order Confirmed",
                    "payment_id": order.payment_id,
                })

            return CustomJsonResponse(result)

        except Exception:
            logger.exception("Error fetching orders")
            return CustomJsonResponse(None, status="failed", error="Failed to fetch orders")

    def update_order(self, order_id, data):
        raise NotImplementedError

    def update_tracking(self, order_id, tracking_id):
        raise NotImplementedError

    def delete_order(self, order_id):
        raise NotImplementedError
    
class PSQLUserManager(UserManager):

    def create_user(self,username,password,first_name,last_name,email,):

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        CustomerProfile.objects.create(
            user=user,
        )

        return user

    def get_user(self, username):
        return User.objects.filter(username=username).first()

    def get_user_by_id(self, user_id):
        return User.objects.filter(id=user_id).first()

    def get_profile(self, user):
        profile, _ = CustomerProfile.objects.get_or_create(user=user)
        return profile

    def update_profile(self,user,profile_data,):
        profile = self.get_profile(user)
        profile.phone = profile_data.get("phone",profile.phone)
        profile.address = profile_data.get("address",profile.address)
        profile.city = profile_data.get("city",profile.city)
        profile.state = profile_data.get("state",profile.state)
        profile.pincode = profile_data.get("pincode",profile.pincode)
        profile.save()
        return profile

    def delete_user(self, user):
        user.delete()
        
class PSQLImageDataManager(ImageDataManager):
    def create_ImageData(self, product,result,display_order, request):
        try:
            product_image = ImageData.objects.create(product=product,public_id=result["public_id"],secure_url=result["secure_url"],display_order=display_order)
            product_image.marketplaces.set(request.POST.getlist("marketplaces"))
            return True
        except Exception as e:
            logger.exception("Error creating ImageData")
            return False
    
    def get_ImageID(self, p_id, display_order):
        try:
            id=Product.objects.get(product_id=p_id).id
            return ImageData.objects.get(product_id=id,display_order=display_order).secure_url
        except Exception as e:
            logger.exception(f"Error retreiving public_id for {p_id}, {e}")
            return False
        
    def get_all_Images(self, p_id, marketplace_code="WEBSITE"):
            try:
                if not ProductMarketplace.objects.filter(product__product_id=p_id,marketplace__code=marketplace_code,is_active=True).exists():
                    logger.warning('Product, Marketplace combination is not active')
                    return False
                else:
                    return list(ImageData.objects.filter(product__product_id=p_id, marketplaces__code=marketplace_code).order_by("display_order").values_list("public_id",flat=True))
            except Exception as e:
                logger.exception(f"Error retreiving public_id for {p_id} and marketplace {marketplace_code}, {e}")
                return False