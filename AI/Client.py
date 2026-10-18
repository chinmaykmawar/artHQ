from ollama import chat,Client
import json

class ollamaManager:
    def __init__(self,model="qwen2.5vl:7b"):
        self.model=model
        self.ollama_client = Client(host="http://localhost:11434")

    def check_ollama(self)-> tuple[bool,str]:
        try:
            models = self.ollama_client.list()

        except Exception:
            return (False, "Ollama server is not running.")
        model_names = [
            model.model
            for model in models.models
        ]
        if "qwen2.5vl:7b" not in model_names:
            return (False, "Model qwen2.5vl:7b is not installed.")
        return (True,'')
    
    def _get_context(self)->str:
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
        """
        return context
    
    def _get_system_message(self)->dict:
        return {
        "role": "system",
        "content": self._get_context(),
        }
    
    def _get_prompt(self, product_details, fields)->str:
        prompt= f"""
        Task: Generate values for specific fields of ArtHQ products based on the product images and field details provided 
        with the aim of maximizing visibility and target audience of the product on the online marketplace
        
        Data: 
        1) Product details (JSON of a dictionary of basic details of the product):
        {json.dumps(product_details, ensure_ascii=False, default=str)}
                 
        2) Fields to generate (JSON of a list of dictionaries with each element of the list providing details of one field for which a value is required, uniquely identified by their attribute column_order):
        {json.dumps(fields, ensure_ascii=False, default=str)}
                
        Response Format: Response should be JSON of a dictionary with key = column_order and value=generated string value for that field
                        
        Rules:
        1) GENERATED VALUES:
            - If valid_values are provided, value must be from within valid_values.
            - Respect the field description, data type, cardinality and transformation while generating value
            - Generate values appropriate to each field.
            - Guidelines, if provided, represent additional suggestions for value generation
        2) REPEATED FIELD NAMES:
            - Fields may have the repeated name and description with different column_order. 
            - Such fields should be treated as single field with multiple possible values
            - So add as many logically reasonable values for the fields as possible to maximize product visibility
            - If valid_values are provided, all values must be from within valid_values.
        3) MATERIAL ACCURACY:
            - If a field asks for the material, describe the material of the main components (pendant, beads, cord, thread, decorative elements, etc.) of the product instead of the material of the hardware (Clasp, chain, or loop etc.)
            - While the hardware is normally metal, the main components are rarely made of metal. They are generally made of gemstones, glass, or acrylic.
            - If the material cannot be established, for beads and pendants, use glass as the material. 
            - If a field specifically asks for clasp material, answer only for the clasp.
        4) BLANK VALUES:
            - Try to minimize blank field values
            - As long as a logically reasonable value can be found for a column, do not leave the value blank
            - Use a blank value only when the field is not relevant for describing the product. For example for a bracelet, pendant value can be left blank as pendants are only relevant for necklaces and not bracelets
            - Never invent a specification just to avoid a blank.
        5) COLOR:
            - Try to infer the color of the product from its images
            - Use only 20-30 major colors such as Red, Blue, Green, White, Black, Grey, Purple, Violet, Maroon, Yellow, Orange, Brown, Teal, Mustard, Aqua etc.
            - Avoid niche colors such as Chartreuse, Brick, Chilli red, Flamingo, AquaMarine, Heliotrope, Rouge, Sienna
            - Each product can have a maximum of 2 colors, one base_color and one highlight_color.
            - In case a product has a uniform mix of more han 2 colors, its base_color will be Multicolor and highlight_color will be Nil
        6) CONSISTENCY: Keep values consistent across repeated or related fields.
            """
        return prompt
    
    def _get_user_message_for_field_values(self, product_details, fields, images)->dict:
        return {"role": "user","content": self._get_prompt(product_details,fields),"images": images}
    
    def _get_response_constraints(self,fields:list)-> dict:
        keys_details = {str(field['column_order']): {"type": "string"} for field in fields}
        response_constraints = {"type": "object",
                            "properties": keys_details,
                            "required": list(keys_details.keys()),
                            "additionalProperties": False,}
        return response_constraints
    
    def generate_field_values(self, product_details:dict ,fields:list, images:list, think:bool=False)->dict[str,str]:
        response_constraints= self._get_response_constraints(fields)
        response = chat(model=self.model,
                        messages=[self._get_system_message(), 
                                  self._get_user_message_for_field_values(product_details, fields, images)],
                        format=response_constraints,
                        options={"temperature": 0.0, "num_ctx": 32768},
                        think=think)
        content = response.message.content
        result = json.loads(content)
        expected_keys = set(response_constraints["properties"].keys())
        if set(result.keys()) != expected_keys:raise ValueError("Ollama returned missing or unexpected field keys.")
        if not all(isinstance(value, str) for value in result.values()):raise ValueError("Ollama returned a non-string field value.")
        return result