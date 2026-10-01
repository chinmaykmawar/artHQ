import cloudinary.uploader

class CloudinaryImageManager:
    def upload_image(self,image,product_id,public_id=None):
        return cloudinary.uploader.upload(image,folder=f"arthq/products/{product_id}",public_id=public_id)

    def delete_image(self,public_id):
        return cloudinary.uploader.destroy(public_id)
    