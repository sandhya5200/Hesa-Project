import pandas as pd
import numpy as np
from rapidfuzz import process, fuzz

# ==================================================
# PART 1: LOAD INPUT FILES
# ==================================================

hesaathi_df = pd.read_excel(
    "/home/thrymr/Downloads/tamil_hesaathis.xlsx"
)

customer_df = pd.read_excel(
    "/home/thrymr/Desktop/vendors/sandhya/second_time_updated_state_files_after_assignig_to_second_additional_database/cleaned_TAMILNADU.xlsx"
)

address_db = pd.read_excel(
    "/home/thrymr/Downloads/tamil_filled_addresses.xlsx"
)

# ==================================================
# PART 2: NORMALIZE TEXT
# ==================================================

hesaathi_df["District"] = hesaathi_df["District"].str.strip().str.lower()
customer_df["District"] = customer_df["District"].str.strip().str.lower()

address_db["District"] = address_db["District"].str.strip().str.lower()
address_db["State"] = address_db["State"].str.strip().str.lower()

customer_df = customer_df.reset_index(drop=True)

# ==================================================
# PART 3: FUZZY DISTRICT MATCH HELPER
# ==================================================

def fuzzy_match_district(target, choices, threshold=85):
    result = process.extractOne(
        target, choices, scorer=fuzz.token_sort_ratio
    )
    if result and result[1] >= threshold:
        return result[0]
    return None

# ==================================================
# PART 4: ASSIGN CUSTOMERS TO HESAATHI
# ==================================================

assigned_rows = []

for _, h_row in hesaathi_df.iterrows():
    h_code = h_row["Hesaathi_code"]
    h_district = h_row["District"]

    # -------- Exact match --------
    matched_customers = customer_df[
        customer_df["District"] == h_district
    ]

    # -------- Fuzzy match if exact empty --------
    if matched_customers.empty:
        unique_districts = customer_df["District"].unique().tolist()
        fuzzy_district = fuzzy_match_district(h_district, unique_districts)

        if fuzzy_district:
            matched_customers = customer_df[
                customer_df["District"] == fuzzy_district
            ]

    matched_customers = matched_customers.head(50)

    # -------- Create EXACTLY 50 rows --------
    for i in range(1, 51):
        customer_id = f"CS-{h_code}-{str(i).zfill(4)}"

        if i <= len(matched_customers):
            c_row = matched_customers.iloc[i - 1]

            assigned_rows.append({
                "Customer_ID": customer_id,
                "Hesaathi_code": h_code,
                "State": "Tamil Nadu",
                "District": h_district,
                "Name": c_row.get("Name"),
                "Mobile": c_row.get("Mobile"),
                "Address": c_row.get("Address"),
                "Pincode": c_row.get("Pincode")
            })
        else:
            assigned_rows.append({
                "Customer_ID": customer_id,
                "Hesaathi_code": h_code,
                "State": "Tamil Nadu",
                "District": h_district,
                "Name": "",
                "Mobile": "",
                "Address": "",
                "Pincode": ""
            })

    # -------- Remove used customers --------
    customer_df = customer_df.drop(matched_customers.index)

# ==================================================
# PART 5: FINAL DATAFRAMES
# ==================================================

assigned_df = pd.DataFrame(assigned_rows)
cleaned_db = customer_df.reset_index(drop=True)

# ==================================================
# PART 6: FILL NAME & MOBILE (RANDOM, NO DISTRICT)
# ==================================================

mask_nm = (
    assigned_df["Name"].isna() | (assigned_df["Name"] == "") |
    assigned_df["Mobile"].isna() | (assigned_df["Mobile"] == "")
)

for idx in assigned_df[mask_nm].index:
    if cleaned_db.empty:
        break

    row = cleaned_db.sample(1).iloc[0]

    assigned_df.at[idx, "Name"] = row["Name"]
    assigned_df.at[idx, "Mobile"] = (
        "" if pd.isna(row["Mobile"]) else str(int(row["Mobile"]))
    )

    cleaned_db = cleaned_db.drop(row.name)

# ==================================================
# PART 7: FILL ADDRESS & PINCODE (DISTRICT BASED)
# ==================================================
assigned_df["District"] = assigned_df["District"].str.lower().str.strip()
address_db["District"] = address_db["District"].str.lower().str.strip()

used_address_indices = set()
mask_ap = (
    assigned_df["Address"].isna() | (assigned_df["Address"] == "") |
    assigned_df["Pincode"].isna() | (assigned_df["Pincode"] == "")
)

for idx in assigned_df[mask_ap].index:
    district = assigned_df.at[idx, "District"]

    # Only unused addresses from same district
    matches = address_db[
        (address_db["District"] == district) &
        (~address_db.index.isin(used_address_indices))
    ]

    # If district-specific addresses are exhausted, allow reuse
    if matches.empty:
        matches = address_db[address_db["District"] == district]

    if not matches.empty:
        row = matches.sample(1).iloc[0]
        used_address_indices.add(row.name)

        if not assigned_df.at[idx, "Address"]:
            assigned_df.at[idx, "Address"] = (
                f"{row['Village Name']}, "
                f"{row['Mandal Name']}, "
                f"{row['District'].upper()}, "
                f"{row['State'].upper()} - {row['Pincode']}"
            )

        if not assigned_df.at[idx, "Pincode"]:
            assigned_df.at[idx, "Pincode"] = str(row["Pincode"])

# ==================================================
# PART 8: FINAL SAVE (ONLY ONCE)
# ==================================================

assigned_df["Pincode"] = assigned_df["Pincode"].astype(str)
assigned_df["District"] = assigned_df["District"].str.upper()
assigned_df["State"] = assigned_df["State"].str.upper()

assigned_df.to_excel(
    "/home/thrymr/Downloads/tamilnadu_customerdatabase.xlsx",
    index=False
)

cleaned_db.to_excel(
    "/home/thrymr/Downloads/tamil_nadu_CLEANED.xlsx",
    index=False
)

print("✅ 50 customers created for EACH Hesaathi")
print("✅ Name & Mobile filled")
print("✅ Address & Pincode generated")
print("✅ Used rows deleted correctly")
print("💾 Final files saved successfully")

