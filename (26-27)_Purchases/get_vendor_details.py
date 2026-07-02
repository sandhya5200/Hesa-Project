import pandas as pd

# File 1: full vendor details (MASTER)
df_master = pd.read_excel("/home/thrymr/Downloads/odisa_new_filled.xlsx")

# File 2: vendor IDs to validate
df_check = pd.read_excel("/home/thrymr/Downloads/Odisha_Unique_Vendors.xlsx")

# ---- Clean Vendor ID ----
df_master['Vendor ID'] = df_master['Vendor ID'].astype(str).str.strip()
df_check['Vendor ID'] = df_check['Vendor ID'].astype(str).str.strip()

# ---- Optional cleaning ----
df_master['Name'] = df_master['Name'].astype(str).str.strip().str.title()
df_master['Mobile'] = df_master['Mobile'].astype(str).str.strip().str.lower()

# ---- MERGE (bring ALL columns from master) ----
merged = df_check.merge(
    df_master,
    on='Vendor ID',
    how='left'
)

# ---- Vendors not found in master ----
missing_vendors = merged[merged.isna().any(axis=1)]

# ---- Save outputs ----
merged.to_excel("/home/thrymr/Downloads/ovendor_full_details.xlsx", index=False)
# missing_vendors.to_excel("/home/thrymr/Downloads/omissing_vendor_ids.xlsx", index=False)

