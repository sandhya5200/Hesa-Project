import pandas as pd
import random

input_file = "/home/thrymr/Downloads/mar_2.xlsx"


zone_file = "/home/thrymr/Important/new_hessathi_with_additional_people_details (copy).xlsx"
output_file = "/home/thrymr/Downloads/mar_3.xlsx"

# Load data
input_df = pd.read_excel(input_file)
zone_df = pd.read_excel(zone_file)
zone_df.rename(columns={"District": "District", "Hesaathi Code": "Hesaathi Code"}, inplace=True)

# Remove rows where 'Hesaathi Code' is empty or NaN
zone_df = zone_df[zone_df["Hesaathi Code"].notna() & (zone_df["Hesaathi Code"] != '')]

# Normalize district names
zone_df["District"] = zone_df["District"].str.strip().str.lower()
input_df["District"] = input_df["District"].str.strip().str.lower()

# Function to replace middle data with Sub Vertical
# def update_customer_name(row):
#     parts = row["Customer Name"].split("-")
#     if len(parts) > 3:
#         parts[3] = row["Sub Vertical"]
#     return "-".join(parts)

# Apply function
input_df["Vendor ID"] = input_df["Vendor ID"]

# Dictionary to store unique PO numbers for each combination
po_tracker = {}
po_counter = 1

# Function to generate a PO number
def generate_po_number(row):
    global po_counter
    if row["Sub Vertical"] in ["FMCG", "WHITE LABEL"]:
        prefix = "CG"
    elif row["Sub Vertical"] in ["AGRI INPUTS", "MARKET LINKAGES TRADING"]:
        prefix = "AG"
    else:
        prefix = " "

    key = (row["Date"], row["Sub Vertical"], row["District"], row["Vendor ID"])
    
    if key not in po_tracker:
        po_tracker[key] = f"2018-19/RY/PO/{po_counter:06d}"
        po_counter += 1
    
    return po_tracker[key]


# Apply function
input_df["PO Number"] = input_df.apply(generate_po_number, axis=1)

# Create a mapping of districts to available Hesaathi Codes
district_hesaathi_map = zone_df.groupby("District")["Hesaathi Code"].apply(list).to_dict()

# Custom district mappings for fallback logic
district_code_mappings = {
    "vijayawada": ["srikakulam", "kurnool", "guntur", "visakhapatnam"],
    "wanaparthy": ["medak", "warangal", "adilabad", "nalgonda"],
    "balasore": ["angul", "balangir", "boudh", "cuttak"],
    "sangareddy": ["karim nagar", "nizamabad", "rangareddy", "warangal"],
    "vikarabad": ["medak", "warangal","nizamabad", "rangareddy"],
    "ujjain": ["dhule", "jalgaon", "buldhana", "amravati"],
    "dhar": ["dhule", "jalgaon", "buldhana", "amravati"]

}

def get_hesaathi_for_district(district):
    if district in district_hesaathi_map:
        return random.choice(district_hesaathi_map[district])
    return None

def get_fallback_hesaathi(district):
    if district in district_code_mappings:
        mapped_districts = district_code_mappings[district]
        possible_codes = [code for d in mapped_districts if d in district_hesaathi_map for code in district_hesaathi_map[d]]
        if possible_codes:
            return random.choice(possible_codes)
    return None

# Group by 'PO Number' and assign Hesaathi Code
po_grouped = input_df.groupby("PO Number")

hesaathi_assignments = {}
for po_number, group in po_grouped:
    first_district = group["District"].iloc[0]
    assigned_code = get_hesaathi_for_district(first_district) or get_fallback_hesaathi(first_district)
    hesaathi_assignments[po_number] = assigned_code

# Apply assignments to the dataframe
input_df["Hesaathi Code"] = input_df["PO Number"].map(hesaathi_assignments)
# Apply assignments to the dataframe
input_df["Hesaathi Code"] = input_df["PO Number"].map(hesaathi_assignments)

input_df["State"] = "Telangana"

input_df.to_excel(output_file, index=False)
print(f"Updated file saved as {output_file}")
