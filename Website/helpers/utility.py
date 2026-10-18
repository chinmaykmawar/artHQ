import os
import re

import sys

BASE_DIR = r"C:\Data\artHQ\Website_django"

sys.path.insert(0, str(BASE_DIR))
print(BASE_DIR)


os.environ.setdefault("DJANGO_SETTINGS_MODULE","Website.core.settings")
import django
django.setup()

from Website.core.models import ImageData

def fix_display_order():
    updated = 0
    skipped = 0

    for image in ImageData.objects.all():
        match = re.search(r"_(\d+)$",image.public_id)

        if not match:
            print(f"SKIP: {image.public_id}")
            skipped += 1
            continue

        new_order = int(match.group(1))

        if image.display_order != new_order:
            print(f"{image.product.product_id}: {image.display_order} -> {new_order}")
            image.display_order = new_order
            image.save(update_fields=["display_order","updated_at"])
            updated += 1

    print(f"\nUpdated: {updated}")
    print(f"Skipped: {skipped}")

if __name__ == "__main__":
    fix_display_order()