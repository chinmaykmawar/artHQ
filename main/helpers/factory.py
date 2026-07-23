from django.conf import settings
from main.PaymentLayer.RazorpayService import RazorpayService
from ..DataLayer.GoogleSheets import (
    GSProductManager,
    GSCategoryManager,
    GSSubCategoryManager,
    GSDesignManager,
    GSColorManager,
    GSOrderManager,
)

# from .DataLayer.PostgreSQL import (
#     PSQLProductManager,
#     PSQLCategoryManager,
#     PSQLSubCategoryManager,
#     PSQLDesignManager,
#     PSQLColorManager,
#     PSQLOrderManager,
# )

class DataFactory:
    _initialized = False

    @classmethod
    def initialize(cls):
        if cls._initialized:
            return

        if settings.DATA_BACKEND == "GOOGLE":
            cls._product_manager = GSProductManager()
            cls._category_manager = GSCategoryManager()
            cls._subcategory_manager = GSSubCategoryManager()
            cls._design_manager = GSDesignManager()
            cls._color_manager = GSColorManager()
            cls._order_manager = GSOrderManager()
        
        # elif settings.DATA_BACKEND == "POSTGRESQL":
        #     cls._product_manager = PSQLProductManager()
        #     cls._category_manager = PSQLCategoryManager()
        #     cls._subcategory_manager = PSQLSubCategoryManager()
        #     cls._design_manager = PSQLDesignManager()
        #     cls._color_manager = PSQLColorManager()
        #     cls._order_manager = PSQLOrderManager()
        
        else:
            raise ValueError(f"Unsupported DATA_BACKEND: {settings.DATA_BACKEND}")

        cls._initialized = True

    @classmethod
    
    def get_product_manager(cls):
        cls.initialize()
        return cls._product_manager

    @classmethod
    def get_category_manager(cls):
        cls.initialize()
        return cls._category_manager

    @classmethod
    def get_subcategory_manager(cls):
        cls.initialize()
        return cls._subcategory_manager

    @classmethod
    def get_design_manager(cls):
        cls.initialize()
        return cls._design_manager

    @classmethod
    def get_color_manager(cls):
        cls.initialize()
        return cls._color_manager

    @classmethod
    def get_order_manager(cls):
        cls.initialize()
        return cls._order_manager
         

class PaymentFactory:
    _initialized = False

    @classmethod
    def initialize(cls):
        if cls._initialized:
            return

        if settings.PAYMENT_SERVICE == "RAZORPAY":
            cls._payment_service = RazorpayService()
        
        else:
            raise ValueError(f"Unsupported DATA_BACKEND: {settings.DATA_BACKEND}")

        cls._initialized = True
    
    @classmethod
    def get_payment_service(cls):
        cls.initialize()
        return cls._payment_service