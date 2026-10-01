import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","main.settings")
import django
django.setup()
import cloudinary.uploader

# Set your Cloudinary credentials
# ==============================
from dotenv import load_dotenv
load_dotenv()

# Import the Cloudinary libraries
# ==============================
import cloudinary
from cloudinary import CloudinaryImage
import cloudinary.uploader
import cloudinary.api

# Import to format the JSON responses
# ==============================
import json

# Set configuration parameter: return "https" URLs by setting secure=True  
# ==============================
config = cloudinary.config(secure=True)

# Log the configuration
# ==============================
print("****1. Set up and configure the SDK:****\nCredentials: ", config.cloud_name, config.api_key, "\n")

def uploadImage():

  # Upload the image and get its URL
  # ==============================

  # Upload the image.
  # Set the asset's public ID and allow overwriting the asset with new versions
  cloudinary.uploader.upload("C:\\Data\\artHQ\\Website_django\\static\\assets\\common\\logo.jpg", public_id="logo", unique_filename = False, overwrite=True)

  # Build the URL for the image and save it in the variable 'srcURL'
  srcURL = CloudinaryImage("logo").build_url()

  # Log the image URL to the console. 
  # Copy this URL in a browser tab to generate the image on the fly.
  print("****2. Upload an image****\nDelivery URL: ", srcURL, "\n")
  
def getAssetInfo():

  # Get and use details of the image
  # ==============================

  # Get image details and save it in the variable 'image_info'.
  image_info=cloudinary.api.resource("logo")
  print("****3. Get and use details of the image****\nUpload response:\n", json.dumps(image_info,indent=2), "\n")

  # Assign tags to the uploaded image based on its width. Save the response to the update in the variable 'update_resp'.
  if image_info["width"]>900:
    update_resp=cloudinary.api.update("logo", tags = "large")
  elif image_info["width"]>500:
    update_resp=cloudinary.api.update("logo", tags = "medium")
  else:
    update_resp=cloudinary.api.update("logo", tags = "small")

  # Log the new tag to the console.
  print("New tag: ", update_resp["tags"], "\n")
  
def createTransformation():

  # Transform the image
  # ==============================

  transformedURL = CloudinaryImage("logo").build_url(width = 100, height = 150, crop = "fill")

  # Log the URL to the console
  print("****4. Transform the image****\nTransfrmation URL: ", transformedURL, "\n")

  # Use this code instead if you want to create a complete HTML image element:
  # imageTag = cloudinary.CloudinaryImage("quickstart_butterfly").image(radius="max", effect="sepia")
  # print("****4. Transform the image****\nTransfrmation URL: ", imageTag, "\n")

# DB stores ImageData.public_id, e.g.
# "arthq/products/JBR30001BlW/JBR30001BlW_1"

def homepage_image(public_id):
    return CloudinaryImage(public_id).build_url(
        width=400,height=400,crop="fit",quality="auto",fetch_format="auto"
    )

def product_page_image(public_id):
    return CloudinaryImage(public_id).build_url(
        width=1600,height=1600,crop="limit",quality="auto",fetch_format="auto"
    )

def product_details_images(image_data):
    return [
        CloudinaryImage(image.public_id).build_url(
            width=800,height=800,crop="fit",quality="auto",fetch_format="auto"
        )
        for image in image_data
    ]

# Example:
# url = homepage_image(product.images.order_by("display_order").first().public_id)
# url = product_page_image(product.images.order_by("display_order").first().public_id)
# urls = product_details_images(product.images.order_by("display_order"))

if __name__ == "__main__":
    public_id = "arthq/products/JBR30001BlW/JBR30001BlW_1"
    print("Homepage:", homepage_image(public_id))
    print("Product page:", product_page_image(public_id))
