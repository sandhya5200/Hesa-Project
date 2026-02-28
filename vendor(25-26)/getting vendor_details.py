import pandas as pd
import os

# -----------------------------
# Paths
# -----------------------------
purchase_folder = "/home/thrymr/Desktop/purchases 25-26(apr-sep)"
vendor_file = "/home/thrymr/Downloads/odissa new database.xlsx"
output_folder = "/home/thrymr/Downloads"

# -----------------------------
# Purchase files
# -----------------------------
purchase_files = [
    "purchase_april_(25-26)_with_state.xlsx",
    "purchase_may_(25-26)_with_state.xlsx",
    "june_purchase_(25-26)_with_state.xlsx",
    "july_purchase(25-26)_with_state.xlsx",
    "August_purchase(25-26)_with_state.xlsx",
    "september_purchase(25-26)_with_state.xlsx"
]

# -----------------------------
# Load vendor master once
# -----------------------------
vendor = pd.read_excel(vendor_file)
vendor["VendorID_clean"] = (
    vendor["Vendor ID"]
    .astype(str)
    .str.replace(" ", "")
    .str.strip()
)

# -----------------------------
# Loop through purchase files
# -----------------------------
for file in purchase_files:
    print(f"Processing: {file}")

    purchase_path = os.path.join(purchase_folder, file)
    purchase = pd.read_excel(purchase_path)

    # Clean Vendor ID
    purchase["VendorID_clean"] = (
        purchase["Vendor ID"]
        .astype(str)
        .str.replace(" ", "")
        .str.strip()
    )

    # Merge
    output = purchase.merge(
        vendor,
        on="VendorID_clean",
        how="left",
        suffixes=("", "_vendor")
    )

    # Drop temp column
    output = output.drop(columns=["VendorID_clean"])

    # Output file name
    out_file = file.replace("_with_state.xlsx", "_with_vendor_details_tn.xlsx")
    out_path = os.path.join(output_folder, out_file)

    # Save
    output.to_excel(out_path, index=False)

print("✅ All purchase files merged with vendor details successfully")
