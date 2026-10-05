from AI.Client import ollamaManager
import time

details={
    "category":"Jewellery",
    "subcategory":"Bracelets",
    "primary_color":"Blue",
    "secondary_color":"Green",
    "design_code":"30001"
}

images=[r"C:\Data\artHQ\Product Images\JBR30007PiW\JBR30007PiW_1.jpg", r"C:\Data\artHQ\Product Images\JBR30007PiW\JBR30007PiW_2.jpg", r"C:\Data\artHQ\Product Images\JBR30007PiW\JBR30007PiW_3.jpg", r"C:\Data\artHQ\Product Images\JBR30007PiW\JBR30007PiW_4.jpg"]

for (model, think) in [("qwen2.5vl:7b", False),("qwen3-vl:8b-thinking", False), ("qwen3-vl:8b-thinking", True)]:
    with open("gpu_usage.log", "a") as f:
        f.write(f"===================Starting model={model}, think={think}=====================\n")
    om = ollamaManager(model=model)
    start = time.perf_counter()
    result = om.generate_product_content(details,images,think=think)
    elapsed = time.perf_counter() - start
    with open("gpu_usage.log", "a") as f:
        f.write(f"===============================think={think} execution time: {elapsed:.3f} sec===============================\n")
        f.write(f"Generated result: {result}\n")
