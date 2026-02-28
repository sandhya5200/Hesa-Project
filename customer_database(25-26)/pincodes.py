import pandas as pd
import random


addr_df = pd.read_excel("/home/thrymr/Downloads/tamin_addresses.xlsx")
pin_df  = pd.read_excel("/home/thrymr/Downloads/tamilpincodes.xlsx")

def clean_district(x):
    if pd.isna(x):
        return x
    return x.upper().replace(" ", "").strip()

addr_df["district_clean"] = addr_df["District"].apply(clean_district)
pin_df["district_clean"]  = pin_df["district"].apply(clean_district)

# -----------------------------
# District → pincode mapping
# -----------------------------
district_pincode_map = (
    pin_df.groupby("district_clean")["pincode"]
    .apply(list)
    .to_dict()
)

# -----------------------------
# Fill missing pincodes randomly
# -----------------------------
def fill_random_pincode(row):
    if pd.isna(row["Pincode"]) or row["Pincode"] == "":
        pincodes = district_pincode_map.get(row["district_clean"], [])
        if pincodes:
            return random.choice(pincodes)
    return row["Pincode"]

addr_df["Pincode"] = addr_df.apply(fill_random_pincode, axis=1)

# -----------------------------
# Drop helper column & save
# -----------------------------
addr_df.drop(columns=["district_clean"], inplace=True)

addr_df.to_excel("/home/thrymr/Downloads/tamil_filled_addresses.xlsx", index=False)

print("✅ Missing pincodes filled district-wise (random selection)")
