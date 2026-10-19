from Website.core.models import Product,Marketplace,SubCategory, ProductMarketplace, ImageData
from Marketplaces.models import MarketplaceSubcategory, MarketplaceSubcategoryField,MarketplaceFieldMapping, ValidValue
from AI.Client import ollamaManager
import base64
import logging
import requests
from django.db.models import Prefetch
import pandas as pd
import time
from datetime import date
from Website.helpers.image_utils import encode_image_to_base64  

logger=logging.getLogger("__name__")    

class CSVGenerator:
    def __init__(self, marketplace_code, subcategory_name):
        # Identifiers supplied by the caller
        self.marketplace = Marketplace.objects.get(code=marketplace_code)
        self.subcategory = SubCategory.objects.get(name=subcategory_name)
        self.marketplace_subCategory= MarketplaceSubcategory.objects.get(marketplace=self.marketplace, subcategory=self.subcategory)
        self.fields = {}
        start=time.perf_counter()
        self.load_fields_and_mappings()
        elapsed=time.perf_counter()-start
        print(f'load_fields_and_mappings took {elapsed}')
        self.data=None
        self.products = []

    def load_fields_and_mappings(self):
        fields = list(
            MarketplaceSubcategoryField.objects
            .filter(marketplace_subcategory=self.marketplace_subCategory)
            .select_related("marketplace_field", "mapping")
            .prefetch_related(Prefetch(
                "marketplace_field__valid_values",
                queryset=ValidValue.objects.order_by("id"),
                to_attr="validValues",
                )
            ).order_by("column_order")
        )
        if not fields:
            logger.debug(f"No fields configured for {self.marketplace_subCategory} ")
            raise ValueError(f"No fields configured for the MarketplaceSubcatgory")

        # Every physical field must have exactly one mapping.
        for field in fields:
            try:
                mapping = field.mapping
            except MarketplaceFieldMapping.DoesNotExist:
                logger.debug(f"Missing mapping for {field} ")
                raise ValueError(f"Missing mapping for field ")
            if field.is_active and mapping.is_active:
                self.fields[field.column_order]={
                    "data_type": field.data_type,
                    "cardinality":field.cardinality,
                    "requirement_type":field.requirement_type,
                    "value_type":mapping.value_type,
                    "value":mapping.value,
                    "transformation":mapping.transformation,
                    "name":field.marketplace_field.name,
                    "description":field.marketplace_field.description,
                    "valid_values":[v.value for v in field.marketplace_field.validValues]
                }

        # Ensure the configured physical columns are in sequence.
        actual_order = [field.column_order for field in fields]
        
        if actual_order != list(range(1, len(fields) + 1)):
            logger.debug(f"Order : {actual_order}")
            raise ValueError("Invalid column_order sequence.")
        logger.info(f"Loaded {len(self.fields)} fields mappings for {self.marketplace_subCategory}")
        print(f"Loaded {len(self.fields)} fields and mappings")

    def create_csv(self,product_IDs):
        self.load_products(product_IDs)
        self.data = pd.DataFrame(
            index=[product.id for product in self.products],
            columns=self.fields.keys()
            )
        self.update_values()
        self.export_csv(r'.\backups\output_csv.csv')
    
    def load_products(self, product_IDs):
            try:
                self.products=Product.objects.filter(product_id=product_IDs)
            except Exception:
                logger.exception(f"Could not load products for {product_IDs}")
    
    def update_values(self):
        columns={}
        for type in MarketplaceFieldMapping.ValueType:
            columns[type]=[]
                
        for column_order,field in self.fields.items():
            columns[field['value_type']].append(column_order)
        start=time.perf_counter()
        if not self.resolve_constant(columns[MarketplaceFieldMapping.ValueType.CONSTANT]):
            logger.warning('Failed to resolve constants')
            raise ValueError()
        end=time.perf_counter()
        print(f'resolve_constant took {end-start}')
        start=end
        if not self.resolve_database(columns[MarketplaceFieldMapping.ValueType.DATABASE]):
            logger.warning('Failed to resolve database colums')
            raise ValueError()
        end=time.perf_counter()
        print(f'resolve_database took {end-start}')
        start=end
        if not self.resolve_image(columns[MarketplaceFieldMapping.ValueType.IMAGE]):
            logger.warning('Failed to resolve image colums')
            raise ValueError()
        end=time.perf_counter()
        print(f'resolve_image took {end-start}')
        start=end
        if not self.resolve_ai(columns[MarketplaceFieldMapping.ValueType.AI]):
            logger.warning('Failed to resolve ai columns')
            raise ValueError()
        end=time.perf_counter()
        with open("gpu_usage.log", "a") as f:
                f.write(f"resolve_ai took {end-start}\n")
        print(f'resolve_ai took {end-start}')
        start=end
        if not self.resolve_calculated(columns[MarketplaceFieldMapping.ValueType.CALCULATED]):
            logger.warning('Failed to resolve calculated colums')
            raise ValueError()
        end=time.perf_counter()
        print(f'resolve_calculated took {end-start}')
        start=end
        if not self.resolve_blank(columns[MarketplaceFieldMapping.ValueType.BLANK]):
            logger.warning('Failed to resolve blank columns')
            raise ValueError()
        end=time.perf_counter()
        print(f'resolve_blank took {end-start}')
        start=end

    def resolve_constant(self, const_columns):
        for column_order in const_columns:
            self.data[column_order] = self.fields[column_order]["value"]
        print('constants Loaded')
        return True
    
    def resolve_database (self, db_columns):
        product_pks = [p.id for p in self.products]
        for column in db_columns:
            path = str(self.fields[column]["value"]).split(".")
            if path[0]=="product":
                path = path[1:]
                related_fields = path[:-1]
                queryset = Product.objects.filter(id__in=product_pks)
                if related_fields:
                    queryset = queryset.select_related(*["__".join(related_fields[:i]) for i in range(1, len(related_fields) + 1)])
                for product in queryset: 
                    value = product
                    for attribute in path:
                        value = getattr(value, attribute)
                    self.data.loc[product.id, column] = ("" if value is None else value)
            elif path[0]=="product_marketplace":
                path = path[1:]
                related_fields = path[:-1]
                queryset = ProductMarketplace.objects.filter(product_id__in=product_pks,marketplace=self.marketplace_subCategory.marketplace,)
                if related_fields:
                    queryset = queryset.select_related(*["__".join(related_fields[:i])for i in range(1, len(related_fields) + 1)])
                for pm in queryset: 
                    value = pm
                    for attribute in path:
                        value = getattr(value, attribute)
                    self.data.loc[pm.product.id, column] = ("" if value is None else value)
            else:
                logger.warning(f"incorrect path: {path}")
                raise ValueError
        print('DB Fields Loaded')
        return True

    def resolve_image(self, img_columns):
        product_pks = [p.id for p in self.products]
        # Separate the two image-column groups.
        image_url_columns = []
        image_location_columns = []
        for column in img_columns:
            name = self.fields[column]["name"]
            if "Image URL" in name:
                image_url_columns.append(column)
            elif "Image Location" in name:
                image_location_columns.append(column)

        # Fetch images associated with the requested marketplace.
        image_datas = (ImageData.objects
            .filter(product_id__in=product_pks)
            .order_by("product_id", "display_order", "pk")
            .values_list("product_id", "public_id")
            .distinct()
        )
        
        common_url = ("https://res.cloudinary.com/guixlbdm/image/upload/")
        transform_url = "c_auto/f_auto/q_auto/"

        product_images = {}

        for product_pk, public_id in image_datas:
            if public_id.split('_')=='1':
                product_images.setdefault(product_pk, []).append(common_url + 'e_background_removal' +transform_url + public_id)    
            else:
                product_images.setdefault(product_pk, []).append(common_url + transform_url + public_id)
 
        self.data.loc[:, image_url_columns] = ""
        self.data.loc[:, image_location_columns] = ""
    
        for product_pk, urls in product_images.items():
            for columns in (image_url_columns,image_location_columns,):
                for column, url in zip(columns, urls):
                    self.data.loc[product_pk, column] = url
        print('Img Fields Loaded')
        return True

    def resolve_ai(self, ai_columns):
        """Generate all AI-mapped values for each product in one Ollama request."""
        if not ai_columns:
            return True
        try:
            aim = ollamaManager()
            product_pks = [product.pk for product in self.products]
            image_rows = (ImageData.objects
                          .filter(product_id__in=product_pks)
                          .order_by("product_id", "display_order", "pk")
                          .values_list("product_id", "public_id")
                          )
            images_by_product = {}
            for product_pk, public_id in image_rows:
                images_by_product.setdefault(product_pk, []).append(public_id)
            cloudinary_base_url = ("https://res.cloudinary.com/guixlbdm/image/upload/c_auto/f_auto/q_auto/")
            fields=[]
            for k,v in self.fields.items():
                if k in ai_columns:
                    v['column_order']=k
                    fields.append(v)
            for product in self.products:
                public_ids = images_by_product.get(product.pk, [])
                if not public_ids:raise ValueError(f"No images found for product {product.product_id}")
                image_start = time.perf_counter()
                images = []
                for public_id in public_ids:
                    response = requests.get(f"{cloudinary_base_url}{public_id}",timeout=30,)
                    response.raise_for_status()
                    images.append(encode_image_to_base64(response.content))
                image_elapsed = time.perf_counter() - image_start
                print(f"Product {product.product_id}: {len(public_ids)} images downloaded in {image_elapsed:.2f}s")
                product_details = {"product_id": product.product_id,"design": str(product.design),"subcategory": product.design.subcategory.name,"color": str(product.color),}

                with open("gpu_usage.log", "a") as f:
                    f.write(f"===========Calling AI================\n")
                print('Calling AI')
                running, error=aim.check_ollama()
                if running:
                    ai_start = time.perf_counter()
                    result=aim.generate_field_values(product_details=product_details,fields=fields,images=images)
                    ai_elapsed = time.perf_counter() - ai_start
                    print(f"Product {product.product_id}: Ollama inference took {ai_elapsed:.2f}s")                
                else:
                    logger.warning(f'ld not connect to model with error : {error}')
                    return False
                
                for column in ai_columns:
                    value = result[str(column)]
                    self.data.loc[product.id, column] = ("" if value is None else str(value))
            print('AI Fields Loaded')
            return True

        except Exception:
            logger.exception("Failed to resolve AI columns")
            return False

    def resolve_calculated(self, calc_columns):
        """Populate calculated fields for all products."""
        if not calc_columns:
            return True

        today = date.today()

        for column in calc_columns:
            field_name = self.fields[column]["name"]

            match field_name:
                case "Model Year":
                    value = str(today.year)
                case "Product Site Launch Date":
                    value = today.strftime("%Y-%m-%d")
                case _:
                    logger.warning(f"Unsupported calculated field: {field_name}")
                    raise ValueError(f"No calculation defined for '{field_name}'")
            self.data.loc[:, column] = value
        return True

    def resolve_blank(self, blank_columns):
        for column_order in blank_columns:
            self.data[column_order] = ""
        return True

    def export_csv(self, output_path):
        columns = sorted(self.fields.keys())
        df = self.data.loc[:, columns].copy()
        df.columns = [self.fields[column]["name"] for column in columns]
        df.to_csv(output_path,index=False,encoding="utf-8-sig",)