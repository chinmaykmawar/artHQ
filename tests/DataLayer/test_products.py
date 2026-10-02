import pytest
from unittest.mock import patch
from django.db import DatabaseError
from Website.helpers.factory import DataFactory

# class TestProductTable:
    
#     @pytest.mark.parametrize("case",EXPECTED["get_all_products"]["cases"],ids=lambda case: case["name"],)
#     def test_get_all_products(self,case,rf):
#         request = rf.get("/products/")
#         if case["name"] == "Products Not Retrieved":
#             with patch("Website.DataLayer.PostgreSQL.PSQLProductManager.get_all_products") as mock_get_all_products:
#                 mock_get_all_products.side_effect = DatabaseError("Unable to connect to PostgreSQL")
#                 response = get_all_products(request)
#         else:
#             response = get_all_products(request)
        
#         body = json.loads(response.content)
#         product_ids = []
        
#         assert body["status"] == case["expected_status"]
        
#         if case["expected_status"] != "success":
#             assert body["data"] is None
#             if case["expected_error"] != "ANY":
#                 assert (body["error"]== case["expected_error"])
#             else:
#                 assert body["error"] is not None
#         else:
#             assert body["error"] is None
#             assert body["data"] is not None
#             assert isinstance(body["data"], list)
#             assert (len(body["data"])== case["expected_product_count"])

#             for product in body["data"]:
#                 for key in case["required_keys"]:
#                     assert key in product
#                 for field in case["mandatory_fields"]:
#                     assert product[field] is not None
#                     assert str(product[field]).strip() != ""
#                 product_ids.append(product["Product_ID"])
#             assert len(product_ids) == len(set(product_ids))

#     @pytest.mark.parametrize("case",EXPECTED["get_product_images"]["cases"],ids=lambda case: case["name"],)
#     def test_get_product_images(self,case,rf):
#         request = rf.get(f"/products/{case['product_id']}/images/")
#         if case["name"] == "Unable To Fetch Images":
#             with patch("Website.BusinessLayer.ProductService.get_product_images") as mock_get_product_images:
#                 mock_get_product_images.side_effect = DatabaseError("Unable to connect to PostgreSQL")
#                 response = get_product_images(case["product_id"])
#         else:
#             response = get_product_images(case["product_id"])

#         body = json.loads(response.content)
        
#         assert body["status"] == case["expected_status"]
#         if case["expected_status"] != "success":
#             assert body["data"] is None
#             if case["expected_error"] != "ANY":
#                 assert (body["error"]== case["expected_error"])
#             else:
#                 assert body["error"] is not None
#         else:
#             assert body["data"] == case["expected_images"]
#             expected = [f'{case["product_id"]}_{i}.jpg'for i in range(1,len(body["data"]) + 1,)]
#             assert body["data"] == expected