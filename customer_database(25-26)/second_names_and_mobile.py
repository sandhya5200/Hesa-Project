# import pandas as pd
# import numpy as np

# # --------------------------------------------------
# # Load files
# # --------------------------------------------------
# assigned_df = pd.read_excel("/home/thrymr/Downloads/telangana_customers.xlsx")
# cleaned_db = pd.read_excel("/home/thrymr/Downloads/telangana_cleaned_database.xlsx")
# address_db = pd.read_excel("/home/thrymr/Downloads/telangana_addresses_filled.xlsx")

# # --------------------------------------------------
# # Normalize text
# # --------------------------------------------------
# assigned_df["District"] = assigned_df["District"].str.strip().str.lower()
# address_db["District"] = address_db["District"].str.strip().str.lower()
# address_db["State"] = address_db["State"].str.strip().str.lower()

# cleaned_db = cleaned_db.reset_index(drop=True)

# # --------------------------------------------------
# # STEP 1: Fill Name & Mobile (NO district match)
# # --------------------------------------------------
# mask_nm = (
#     assigned_df["Name"].isna() | (assigned_df["Name"] == "") |
#     assigned_df["Mobile"].isna() | (assigned_df["Mobile"] == "")
# )

# for idx in assigned_df[mask_nm].index:
#     if cleaned_db.empty:
#         break  # nothing left to assign

#     row = cleaned_db.sample(1).iloc[0]

#     assigned_df.at[idx, "Name"] = row["Name"]
#     assigned_df.at[idx, "Mobile"] = str(row["Mobile"])

#     # drop used row
#     cleaned_db = cleaned_db.drop(row.name)

# # --------------------------------------------------
# # STEP 2: Fill Address & Pincode (district based)
# # --------------------------------------------------
# mask_ap = (
#     assigned_df["Address"].isna() | (assigned_df["Address"] == "") |
#     assigned_df["Pincode"].isna() | (assigned_df["Pincode"] == "")
# )

# for idx in assigned_df[mask_ap].index:
#     district = assigned_df.at[idx, "District"]

#     matches = address_db[address_db["District"] == district]

#     if not matches.empty:
#         row = matches.sample(1).iloc[0]

#         address = (
#             f"{row['Village Name']}, "
#             f"{row['Mandal Name']}, "
#             f"{row['District']}, "
#             f"{row['State']} - {row['Pincode']}"
#         )

#         assigned_df.at[idx, "Address"] = address
#         assigned_df.at[idx, "Pincode"] = row["Pincode"]


# # --------------------------------------------------
# # Save outputs
# # --------------------------------------------------
# assigned_df.to_excel("/home/thrymr/Downloads/telangana_customerdatabase.xlsx", index=False)
# cleaned_db.to_excel("/home/thrymr/Downloads/final_cleaned_telangana.xlsx", index=False)

# print("✅ Name & Mobile filled")
# print("✅ Address & Pincode generated")
# print("✅ Used rows deleted correctly")
