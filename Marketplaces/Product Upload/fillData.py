import pandas as pd
import os

# ========== USER INPUTS ==========
fileDir = r"C:\Data\artHQ\Flipkart"   # <---- Update this
inputFileName = "C_earring_8c05f0197a4b40b4_0510-0750FK_REQL6H6Q2NHNX.xls"
outputFileName = "Flipkart_Earrings_Filled_ArtHQ.xls"
# =================================

# Build full paths
input_path = os.path.join(fileDir, inputFileName)
output_path = os.path.join(fileDir, outputFileName)

# Load the Flipkart Excel template
xls = pd.ExcelFile(input_path)
earring_df = xls.parse(xls.sheet_names[0])


product_to_be_Updated=["JBR30001BlW","JBR30002GrP","JBR30003WhG","JBR30004YeU","JNK20002Whi","JBR30005GrG","JNK20003WhU","JBR30006Mul","JBR30007PiW","JBR30008Gre","JBR30009PiG","JBR30010BlB","JER30001Blu"]

final_data = []


desc_df = pd.DataFrame(final_data, columns=["Product_ID", "Title", "Description", "Occasion", "Collection", "Design", "Ornamentation Type", "Trend"])

# Fill matching rows in Flipkart format
for _, row in desc_df.iterrows():
    mask = earring_df["Seller SKU ID"] == row["Product_ID"]
    earring_df.loc[mask, "Description"] = row["Description"]
    earring_df.loc[mask, "Occasion"] = row["Occasion"]
    earring_df.loc[mask, "Collection"] = row["Collection"]
    earring_df.loc[mask, "Design"] = row["Design"]
    earring_df.loc[mask, "Ornamentation Type"] = row["Ornamentation Type"]
    earring_df.loc[mask, "Trend"] = row["Trend"]
    earring_df.loc[mask, "Brand"] = "ArtHQ"
    earring_df.loc[mask, "Manufacturer Details"] = "Neha Nigam, Noida, Uttar Pradesh - 201304"
    earring_df.loc[mask, "Packer Details"] = "Neha Nigam, Noida, Uttar Pradesh - 201304"
    earring_df.loc[mask, "Country Of Origin"] = "India"
    earring_df.loc[mask, "Tax Code"] = "GST_3"
    earring_df.loc[mask, "HSN"] = "71179090"
    earring_df.loc[mask, "MRP (INR)"] = 599
    earring_df.loc[mask, "Your selling price (INR)"] = 599

# Save updated file
earring_df.to_excel(output_path, index=False)
print(f"✅ File saved successfully: {output_path}")




