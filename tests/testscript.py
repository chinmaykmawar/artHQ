import os
import sys
import django

sys.path.append(r"C:\Data\artHQ\Website_django")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Website.core.settings")
os.chdir(r"C:\Data\artHQ\Website_django")
django.setup()

from django.test import RequestFactory
from Website.BusinessLayer.ProductService import get_all_products

rf = RequestFactory()
request = rf.get("/products/")

response = get_all_products(request)

with open ("test_output.txt", "w") as f:
    f.write(response.content.decode())
    f.write("\n\n\n\n\n\n")

from Website.BusinessLayer.ProductService import get_product_images

response = get_product_images("JBR30003WhG")

with open ("test_output.txt", "a") as f:
    f.write(response.content.decode())
    f.write("\n\n\n\n\n\n")
