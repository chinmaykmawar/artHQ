from ollama import chat,Client


class ollamaManager:
    def __init__(self,model="qwen2.5vl:7b"):
        self.model=model
        self.ollama_client = Client(host="http://localhost:11434")

    def check_ollama(self):
        try:
            models = self.ollama_client.list()

        except Exception:
            return False, "Ollama server is not running."
        model_names = [
            model.model
            for model in models.models
        ]
        if "qwen2.5vl:7b" not in model_names:
            return False, "Model qwen2.5vl:7b is not installed."
        return True
    
    def _get_context(self):
        context="""
1. What is ArtHQ?
ArtHQ is an Indian design and lifestyle brand focused on creating handcrafted artificial jewellery and decorative products that combine creativity, color, and contemporary styling. ArtHQ products are designed with an emphasis on unique handmade designs, attractive visual appeal, affordability, and everyday usability. The brand creates products primarily for customers looking for distinctive accessories and décor pieces that add personality and style without the premium pricing associated with fine jewellery or luxury products.
2. What kind of products does ArtHQ do?
ArtHQ primarily creates handmade artificial jewellery and fashion accessories, including bracelets, beaded jewellery, and other decorative wearable pieces, along with selected home décor products. Jewellery designs may use seed beads, glass beads, crystals, metal findings, cords, chains, and other suitable craft materials, depending on the individual product. Products can include different colors or variants of the same underlying design. Product descriptions should accurately reflect the actual product shown in the supplied images or product information, including its design, colors, construction, closure, adjustability, intended wearer, and styling possibilities. Do not assume or claim a material, gemstone, durability characteristic, size, plating, or functional feature unless it is explicitly provided or clearly established from the product information.
3. Guidelines for generating Title, Description and Keywords for e-commerce websites
Generate accurate, search-friendly, and customer-oriented titles, descriptions, and keywords based only on the product information and images provided. The title should clearly identify the brand (ArtHQ), product type, primary design/style, important color or material characteristics when relevant, and intended wearer or use; keep it natural and readable rather than stuffing keywords. If the product is a color variation of an existing design, retain the core design name/structure and modify only the relevant color or variant attributes. The description should explain the product's appearance, design, materials when known, construction, notable features, fit/closure where known, styling/use occasions, and gifting suitability in a natural and persuasive manner, without making unsupported claims. The keywords should contain relevant search terms that a customer might realistically use, including product type, design, color, material, audience, style, occasion, and common synonyms. Avoid irrelevant keywords, repetition, competitor/marketplace brand names, misleading claims, excessive promotional language, and keyword stuffing. Never invent specifications such as dimensions, material composition, gemstone type, plating, hypoallergenic properties, waterproofing, durability, or age suitability unless those details are explicitly supplied.
4. Rules:
- Use only information visible in the images or supplied in Product details.
- Do not invent material, dimensions, gemstones, certifications or other properties.
- Title should be concise and suitable for an Indian ecommerce marketplace.
- Description should accurately describe the product.
- Keywords should contain 8-12 relevant search terms.
        """
        return context

    def _get_system_message(self):
        return {
        "role": "system",
        "content": self._get_context(),
        }

    def _get_image_bytes(self, images):
        image_bytes = []
        for image in images:
            image.seek(0)
            image_bytes.append(image.read())
        return image_bytes

    def _get_user_message(self, details, images):
        prompt=f"""
Generate ecommerce content for this product.
Product details:
{details}

Provide the output in JSON format with the following keys:
- title: A concise, search-friendly product title suitable for an Indian ecommerce marketplace.(3-10 words)
- description: A detailed product description. 
- 1 word keywords: A list of relevant 1-word search terms, separated by commas, and suitable for an Indian ecommerce marketplace.
- 2 word keywords: A list of relevant 2-word search phrases, separated by commas, and suitable for an Indian ecommerce marketplace.
"""
        if isinstance(images, list) and len(images) > 0:
            if not isinstance(images[0], str):
                images = self._get_image_bytes(images)
        else:
            raise ValueError("At least one product image is required.") 
        return {
            "role": "user",
            "content": prompt,
            "images": images
        }

    def _get_format(self):
        response_format = {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string"
                },
            "description": {
                "type": "string"
            },
            "1 word keywords": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 5,
                "maxItems": 10
            },
            "2 word keywords": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 0,
                "maxItems": 3
            }
        },
        "required": [
            "title",
            "description",
            "1 word keywords",
            "2 word keywords"
        ]
    }
        return response_format

    def generate_product_content(self, details, images, think=False):
        messages=[self._get_system_message(),self._get_user_message(details, images)]
        response=chat(
            model=self.model,
            messages=messages,
            format=self._get_format(),
            options={"temperature":0.0,"num_ctx":32768},
            think=think)
        return response["message"]["content"]