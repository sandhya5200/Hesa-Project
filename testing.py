# import pandas as pd

# # === Step 1: Load Files ===
# new_file_path = "/path/to/new_products_file.xlsx"
# old_file_path = "/path/to/old_products_file.xlsx"
# output_file_path = "/path/to/output_missing_products.xlsx"

# df_new = pd.read_excel(new_file_path)
# df_old = pd.read_excel(old_file_path)

# # === Step 2: Normalize Product Name Columns for Comparison ===
# df_new['Corrected Product Name'] = df_new['Corrected Product Name'].astype(str).str.strip().str.lower()
# df_old['Product Name'] = df_old['Product Name'].astype(str).str.strip().str.lower()

# # === Step 3: Get Set of Product Names from Old File ===
# old_product_names = set(df_old['Product Name'])

# # === Step 4: Filter Products NOT Present in Old File ===
# df_missing = df_new[~df_new['Corrected Product Name'].isin(old_product_names)]

# # === Step 5: Export Result ===
# df_missing.to_excel(output_file_path, index=False)
# print(f"✅ Output saved to: {output_file_path}")
import pandas as pd

# Load your files
old_df = pd.read_excel("/home/thrymr/Important/my_products_file_after_hsn_code_updatation.xlsx")
new_df = pd.read_excel("/home/thrymr/Downloads/Corrected New HSN CODES.xlsx")

# # Normalize product names
# old_df["prod_clean"] = old_df["Product Name"].astype(str).str.strip().str.lower()
# new_df["prod_clean"] = new_df["Corrected Product Name"].astype(str).str.strip().str.lower()

# # Convert 'Corrected GST Rate' like '12%' to 0.12
# def convert_percent_to_decimal(x):
#     if isinstance(x, str) and "%" in x:
#         try:
#             return float(x.strip().replace("%", "")) / 100
#         except:
#             return None
#     elif isinstance(x, (int, float)):
#         return float(x)
#     else:
#         return None

# new_df["Corrected GST Rate"] = new_df["Corrected GST Rate"].apply(convert_percent_to_decimal)

# # Create mapping
# gst_rate_map = dict(zip(new_df["prod_clean"], new_df["Corrected GST Rate"]))

# # Add flag column
# old_df["gst_updated"] = False

# # Update function
# def update_gst(row):
#     prod = row["prod_clean"]
#     if prod in gst_rate_map:
#         new_rate = gst_rate_map[prod]
#         if pd.notna(new_rate) and row["gst_rate"] != new_rate:
#             row["gst_rate"] = new_rate
#             row["gst_updated"] = True
#     return row

# # Apply updates
# old_df = old_df.apply(update_gst, axis=1)

# # Cleanup
# old_df.drop(columns=["prod_clean"], inplace=True)

# # Save to file
# old_df.to_excel("/home/thrymr/Downloads/old_products_with_updated_gst.xlsx", index=False)
# print("✅ GST rates updated with proper conversion. File saved.")

# --- Step 1: Reuse the cleaned version of new_df and old_df ---

# Ensure product names are clean again
new_df["prod_clean"] = new_df["Corrected Product Name"].astype(str).str.strip().str.lower()
old_product_names = old_df["Product Name"].astype(str).str.strip().str.lower()

# Convert GST rate to decimal again (if starting fresh)
def convert_percent_to_decimal(x):
    if isinstance(x, str) and "%" in x:
        try:
            return float(x.strip().replace("%", "")) / 100
        except:
            return None
    elif isinstance(x, (int, float)):
        return float(x)
    else:
        return None

new_df["Corrected GST Rate"] = new_df["Corrected GST Rate"].apply(convert_percent_to_decimal)

# --- Step 2: Filter new products to only those with GST 0 or 0.05 ---
filtered_new = new_df[
    new_df["Corrected GST Rate"].isin([0.0, 0.05])
]

# --- Step 3: Exclude products already present in the old file ---
unmatched_rows = filtered_new[~filtered_new["prod_clean"].isin(old_product_names)]

# --- Step 4: Save result ---
output_path = "/home/thrymr/Downloads/unmatched_low_gst_new_products.xlsx"
unmatched_rows.to_excel(output_path, index=False)
print(f"✅ Unmatched new products with 0% or 5% GST saved to:\n{output_path}")
