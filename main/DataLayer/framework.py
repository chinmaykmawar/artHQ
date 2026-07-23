from abc import ABC, abstractmethod


class ProductManager(ABC):

    @abstractmethod
    def get_all_products(self):
        pass

    @abstractmethod
    def get_product(self, product_id):
        pass

    @abstractmethod
    def create_product(self, data):
        pass

    @abstractmethod
    def update_product(self, product_id, data):
        pass

    @abstractmethod
    def delete_product(self, product_id):
        pass

    @abstractmethod
    def search_products(self, search_text):
        pass

    @abstractmethod
    def filter_products(self,categories=None,subcategories=None,colors=None,materials=None,):
        pass

class CategoryManager(ABC):

    @abstractmethod
    def get_all_categories(self):
        pass

    @abstractmethod
    def get_category(self, category):
        pass

    @abstractmethod
    def create_category(self, data):
        pass

    @abstractmethod
    def update_category(self, category, data):
        pass

    @abstractmethod
    def delete_category(self, category):
        pass

class SubCategoryManager(ABC):

    @abstractmethod
    def get_all_subcategories(self):
        pass

    @abstractmethod
    def get_subcategory(self, category, subcategory):
        pass

    @abstractmethod
    def create_subcategory(self, data):
        pass

    @abstractmethod
    def update_subcategory(self, category, subcategory, data):
        pass

    @abstractmethod
    def delete_subcategory(self, category, subcategory):
        pass

class DesignManager(ABC):

    @abstractmethod
    def get_all_designs(self):
        pass

    @abstractmethod
    def get_design(self, design_code):
        pass

    @abstractmethod
    def create_design(self, data):
        pass

    @abstractmethod
    def update_design(self, design_code, data):
        pass

    @abstractmethod
    def delete_design(self, design_code):
        pass

class ColorManager(ABC):

    @abstractmethod
    def get_all_colors(self):
        pass

    @abstractmethod
    def get_color(self, color_code):
        pass

    @abstractmethod
    def create_color(self, data):
        pass

    @abstractmethod
    def update_color(self, color_code, data):
        pass

    @abstractmethod
    def delete_color(self, color_code):
        pass

class OrderManager(ABC):

    @abstractmethod
    def save_order(self, order_data):
        pass

    @abstractmethod
    def get_order(self, order_id):
        pass

    @abstractmethod
    def get_orders(self, order_ids=None, phone=None):
        pass

    @abstractmethod
    def update_order(self, order_id, data):
        pass

    @abstractmethod
    def update_tracking(self, order_id, tracking_id):
        pass

    @abstractmethod
    def delete_order(self, order_id):
        pass