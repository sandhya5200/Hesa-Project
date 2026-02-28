# import pandas as pd

# # ====== INPUT / OUTPUT FILE PATHS ======
# input_file = "/home/thrymr/Downloads/odissa new database.xlsx"     # <-- your input file
# output_file = "/home/thrymr/Downloads/odissa new.xlsx"   # <-- generated output file

# # ====== READ FILE ======
# df = pd.read_excel(input_file)

# # ====== CLEAN EMPTY VALUES IN Vertical ======
# df['Vertical'] = df['Vertical'].replace('', pd.NA)

# # ====== FILL Vertical FROM Vendor ID (second-last part) ======
# df['Vertical'] = df['Vertical'].fillna(
#     df['Vendor ID'].astype(str).str.split('-').str[-2]
# )

# # ====== WRITE OUTPUT FILE ======
# df.to_excel(output_file, index=False)

# print("✅ Output file generated:", output_file)



# import pandas as pd
# from rapidfuzz import process, fuzz

# # ----------- Load files -----------
# major_db = pd.read_excel("/home/thrymr/Desktop/new_vendor_databases/Odissa_Vendor_Database.xlsx")   # File 1
# target_db = pd.read_excel("/home/thrymr/Downloads/odissa new.xlsx")     # File 2

# # Normalize text for matching
# def clean_text(x):
#     return str(x).strip().lower() if pd.notna(x) else ""

# major_db["District_clean"] = major_db["District"].apply(clean_text)
# target_db["District_clean"] = target_db["District"].apply(clean_text)

# # Rows where Name or Mobile is missing
# mask_missing = target_db["Name"].isna() | target_db["Mobile"].isna()
# missing_rows = target_db[mask_missing]

# used_major_indexes = set()

# # ----------- Fuzzy matching & fill -----------
# for idx, row in missing_rows.iterrows():
#     district = row["District_clean"]

#     # Skip if district itself missing
#     if district == "":
#         continue

#     # Only unused major DB rows
#     available_major = major_db.drop(index=list(used_major_indexes))

#     if available_major.empty:
#         break

#     match = process.extractOne(
#         district,
#         available_major["District_clean"],
#         scorer=fuzz.token_sort_ratio
#     )

#     if match and match[1] >= 50:   # 80% confidence
#         matched_row = available_major[available_major["District_clean"] == match[0]].iloc[0]

#         # Fill required fields
#         target_db.at[idx, "Name"] = matched_row["Name"]
#         target_db.at[idx, "Mobile"] = matched_row["Mobile"]
#         target_db.at[idx, "Address"] = matched_row["Address"]

#         # Mark this major DB row as used
#         used_major_indexes.add(matched_row.name)

# # ----------- Remove used rows from major DB -----------
# cleaned_major_db = major_db.drop(index=list(used_major_indexes))

# # ----------- Save FULL target file (same structure as input) -----------
# target_db.drop(columns=["District_clean"], inplace=True)
# target_db.to_excel("/home/thrymr/Downloads/odisa_new_filled.xlsx", index=False)

# # ----------- Save cleaned major DB -----------
# cleaned_major_db.drop(columns=["District_clean"], inplace=True)
# cleaned_major_db.to_excel(
#     "/home/thrymr/Desktop/new_vendor_databases/Odissa_Vendor_Database_cleaned.xlsx",
#     index=False
# )

# print("✅ Done.")
# print("1. maha_new_filled.xlsx  (same as input, missing values filled)")
# print("2. Maharastra_CLEANED_delete.xlsx (used rows removed)")


import pandas as pd

# -------- Load input file --------
input_file = "/home/thrymr/Desktop/new_vendor_databases/Vendor_databases_as_per_25-26/odisa_new_filled.xlsx"      # change path if needed
output_file = "/home/thrymr/Desktop/new_vendor_databases/Vendor_databases_as_per_25-26/odisa_Vendors.xlsx"

df = pd.read_excel(input_file)

# -------- Convert selected columns to UPPERCASE --------
upper_cols = ["District", "State", "Vendor ID", "Sub Vertical"]

for col in upper_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.upper()

# -------- Fill empty Address --------
def fill_address(row):
    address = row["Address"]
    
    if pd.isna(address) or str(address).strip() == "":
        parts = [
            str(row["District"]) if pd.notna(row["District"]) else "",
            str(row["State"]) if pd.notna(row["State"]) else "",
            "INDIA",
            str(row["Pincode"]) if pd.notna(row["Pincode"]) else ""
        ]
        return ", ".join([p for p in parts if p != ""])
    
    return address

df["Address"] = df.apply(fill_address, axis=1)

# -------- Save exact file --------
df.to_excel(output_file, index=False)

print("File saved successfully with uppercase columns and filled addresses.")
