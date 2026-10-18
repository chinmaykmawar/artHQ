import cloudinary.uploader
from PIL import Image
from io import BytesIO

class CloudinaryImageManager:
    def upload_image(self,image,product_id,public_id=None, test=False):
        max_size = 10 * 1024 * 1024

        if image.size > max_size:
            img = Image.open(image)
            img.thumbnail((3000, 3000))
            buffer = BytesIO()
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            img.save(buffer, format="JPEG", quality=85, optimize=True)
            buffer.seek(0)
            image = buffer

        folder = f"arthq/test/{product_id}" if test else f"arthq/products/{product_id}"
        return cloudinary.uploader.upload(image, folder=folder, public_id=public_id)

    def delete_image(self,public_id):
        return cloudinary.uploader.destroy(public_id)
    
    def delete_all_product_images(self, product_id):
        public_ids = []
        for folder in ("arthq/test", "arthq/products"):
            res = cloudinary.api.resources(type="upload", prefix=f"{folder}/{product_id}", max_results=500)
            public_ids.extend(r["public_id"] for r in res["resources"]
                          if r["public_id"].split("/")[-1].startswith(product_id))
        return all(self.delete_image(public_id).get("result") == "ok" for public_id in public_ids)
        
    