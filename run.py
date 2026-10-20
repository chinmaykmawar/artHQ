import os
import sys
from pathlib import Path
import csv
import hashlib

BASE_DIR = r"C:\Data\artHQ\Website_django"

sys.path.insert(0, str(BASE_DIR))
print(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE","Website.core.settings")
import django
django.setup()

from Mktps.Product_Upload.file_generator import CSVGenerator

gen=CSVGenerator('AMAZON', 'Bracelet')
gen.create_csv('JBR30016ReW')
with open('./backups/felds_dump.txt', 'w') as f:
    f.write(str(gen.fields))