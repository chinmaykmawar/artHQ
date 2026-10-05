import cloudinary.uploader

from Website.helpers import test

class CloudinaryImageManager:
    def upload_image(self,image,product_id,public_id=None, test=False):
        if test:
            res=cloudinary.uploader.upload(image,folder=f"arthq/test/{product_id}",public_id=public_id)
        else:
            res=cloudinary.uploader.upload(image,folder=f"arthq/products/{product_id}",public_id=public_id)
        return 

    def delete_image(self,public_id):
        return cloudinary.uploader.destroy(public_id)
    