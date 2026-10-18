import base64


def encode_image_to_base64(image):
    """
    Accept raw image bytes or a Django UploadedFile.
    Return a base64-encoded string.
    """
    if isinstance(image, bytes):
        image_bytes = image
    else:
        # Preserve the file's current read position.
        position = image.tell()
        try:
            image.seek(0)
            image_bytes = image.read()
        finally:
            image.seek(position)

    return base64.b64encode(image_bytes).decode("utf-8")