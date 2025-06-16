import pandas as pd
import random

# Load input files
cleaned_df = pd.read_excel(r"c:\Users\ksand\Downloads\cleaned_MAHARASHTRA.xlsx")
location_df = pd.read_excel(r"c:\Users\ksand\Downloads\Madhyapradesh_address.xlsx")

# Drop duplicates in name list
cleaned_df = cleaned_df.drop_duplicates(subset=["Name", "Mobile"]).reset_index(drop=True)

# Hardcoded values
state = "Madhya Pradesh"
districts = ["Dewas", "Dhar", "Indore", "Kukshi", "Ujjain"]
subverticals = ["Agri Inputs", "Market Linkages", "Market Intervention", "FMCG", "White Label"]

# Shuffle for randomness
cleaned_df = cleaned_df.sample(frac=1).reset_index(drop=True)
name_index = 0
assigned_rows = []

# Create a lookup for District -> Mandal/Village/Pincode
location_lookup = location_df.groupby("District").apply(lambda x: x.to_dict("records")).to_dict()

# Dictionary to track Vendor ID counts
vendor_id_counter = {}

for district in districts:
    for sub in subverticals:
        count = random.randint(30, 35)
        for _ in range(count):
            if name_index >= len(cleaned_df):
                raise ValueError("Not enough names in cleaned_excel to finish the allocation.")

            name = cleaned_df.loc[name_index, "Name"]
            mobile = cleaned_df.loc[name_index, "Mobile"]
            name_index += 1

            # Pick a random Mandal/Village/Pincode for the district
            if district in location_lookup:
                loc = random.choice(location_lookup[district])
                mandal = loc.get("Mandal", "")
                village = loc.get("Village", "")
                pincode = loc.get("Pincode", "")
            else:
                mandal = village = pincode = ""

            # Create address string
            address = f"{village}, {mandal}, {district}, {state}, {pincode}"

            # Create and increment Vendor ID
            combo_key = (district.upper(), sub.upper())
            vendor_id_counter[combo_key] = vendor_id_counter.get(combo_key, 0) + 1
            vendor_id = f"HS-VED-{combo_key[0]}-{combo_key[1]}-{vendor_id_counter[combo_key]:04d}"

            assigned_rows.append({
                "Name": name,
                "Mobile": mobile,
                "Subvertical": sub,
                "Village": village,
                "Address": address,
                "Mandal": mandal,
                "District": district,
                "State": state,
                "Pincode": pincode,
                "Vendor ID": vendor_id
            })

# Output assigned data and remaining names
assigned_df = pd.DataFrame(assigned_rows)
remaining_df = cleaned_df.iloc[name_index:].reset_index(drop=True)

# Define column order
final_columns = ["Name", "Mobile", "Subvertical", "Village", "Address", "Mandal", "District", "State", "Pincode", "Vendor ID"]
assigned_df = assigned_df[final_columns]

# Save to Excel
assigned_df.to_excel(r"c:\Users\ksand\Downloads\assigned_output.xlsx", index=False)
remaining_df.to_excel(r"c:\Users\ksand\Downloads\remaining_maharashtra.xlsx", index=False)

print("✅ Assignment complete. Files saved:")
print("- assigned_output.xlsx")
print("- remaining_maharashtra.xlsx")


