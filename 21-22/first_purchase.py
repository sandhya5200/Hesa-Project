import datetime
from fastapi import APIRouter
import random
import pandas as pd

month_map = [
    "April'21", "May'21", "Jun'21", "Jul'21", "Aug'21", "Sep'21",
    "Oct'21", "Nov'21", "Dec'21", "Jan'22", "Feb'22", "Mar'22"
]

business_dict = {
  'Agri Inputs': [8.23, 6.91, 7.45, 8.78, 6.59, 8.15, 7.32, 6.95, 8.88, 7.09, 6.74, 8.32],
  'Market Linkages Trading': [7.81, 8.69, 6.44, 7.28, 8.12, 7.63, 6.05, 8.49, 7.77, 8.34, 6.92, 8.76],
  'FMCG': [6.41, 7.28, 8.95, 7.69, 8.01, 6.37, 7.80, 6.99, 8.54, 7.65, 6.87, 8.23],
}


def purchase():
    print("before")
    product_quantity = pd.read_excel("/home/thrymr/Downloads/sheets_split/month_wise_files/December_2021.xlsx", sheet_name="Products")
   
    product_gross = pd.read_excel("/home/thrymr/Downloads/sheets_split/month_wise_files/December_2021.xlsx", sheet_name="Taxable")
    
    zone_df = pd.read_excel("/home/thrymr/Important/new_hessathi_with_additional_people_details (copy).xlsx")
    products_data = pd.read_excel("/home/thrymr/Downloads/myyy.xlsx")
    col = product_gross.columns
    track = {}
    rows = []
    districts = {}
    old_gross = {}
    
    zone_df = zone_df[zone_df["Hesaathi Code"].notna() & (zone_df["Hesaathi Code"].str.strip() != "")]
    zone_df.insert(len(zone_df.columns), "Month_Index", "")

    zone_df["Month_Index"] = zone_df["Onboarding Month"].apply(lambda x: month_map.index(x) if x in month_map else -1)
    k = random.randint(20,25)
    d= None
    for ind,r in product_gross.iterrows():
        missed_quantity = 0
        row_data = r.to_list()
        subv = str(row_data[1])

        category = row_data[5]
        sub_category = row_data[6]

        print(row_data[0])

        # date_value = datetime.datetime.strptime(row_data[0], '%d-%m-%Y')
        date_value = datetime.datetime.strptime(str(row_data[0]), '%Y-%m-%d %H:%M:%S')

        
        next_day = date_value + datetime.timedelta(days=1)
        
        if next_day.month == date_value.month:
            date_value = next_day
        month = date_value.month
        
        if d!=date_value:
            d= date_value
            
        vertical = "Consumer Business" if subv in ["FMCG","White Label"] else "Agri Business"
        p_name = row_data[2]
        if pd.isna(p_name):
            continue
        
        # print(p_name)
        pr_empty = False
        pr = products_data[(products_data["Product Name"].str.lower()==p_name.lower())]
        if pr.empty:
            print("missed : ",p_name)
            pr_empty = True
            gst = 0.05
            # uom = row_data[3]
        else:
            pr= pr.sample(n=1).iloc[0]
            gst = row_data[7] 
            # Convert GST rate from percentage to decimal (e.g., 18 -> 0.18)
            if gst >= 1:
                gst = gst / 100
  
            # print(p_name)
            hsn_code = row_data[3]
        uom = row_data[4]
        
        for c in range(len(row_data)):
            if c<8:
                continue
            gross = row_data[c]
            dist = col[c]
            if not dist:
                continue
            if dist not in districts:
                districts[dist] = []
            if subv not in old_gross:
                old_gross[subv] = 0
                
            # print(dist)
            if gross and gross>0:
                gross = gross * (1+gst) # this is set based on input data if input is taxable keep this else comment out this
                margin = business_dict[subv][month-1]
                if old_gross[subv]!=0:
                    rand = old_gross[subv]*-1
                    old_gross[subv] = 0
                else:
                    rand = random.randint(-5,5)/100
                    old_gross[subv] = rand
                m = ((margin*(rand))+margin)/100                
                if month < 4:
                    hesas = zone_df[
                        (zone_df["District"].str.lower() == dist.lower()) &
                        (zone_df["Month_Index"] ==-1) | (zone_df["Month_Index"] <= month + 8)
                    ]
                    if hesas.empty:
                        hesas = zone_df[
                        (zone_df["District"].str.lower() == "HYDERABAD".lower()) &
                        (zone_df["Month_Index"] ==-1) | (zone_df["Month_Index"] <= month + 8)
                    ]
                else:
                    hesas = zone_df[
                        (zone_df["District"].str.lower() == dist.lower()) &
                        (zone_df["Month_Index"] ==-1) | (zone_df["Month_Index"] <= month - 4)
                    ]
                    if hesas.empty:
                        hesas = zone_df[
                        (zone_df["District"].str.lower() == "HYDERABAD".lower()) &
                        (zone_df["Month_Index"] ==-1) | (zone_df["Month_Index"] <= month - 4)
                    ]
                
                
                # gross -= gross*m
                quantity = product_quantity.iloc[ind].iloc[c]
                quantity += missed_quantity
                missed_quantity = 0
                init_q = quantity
                # print(quantity)
                if not pd.notna(quantity) or quantity==0:
                    break
                quantity = int(quantity) if quantity>=1 else 1
                
                taxable = gross/(1+gst)

                taxable -= taxable*m

                unit_p = taxable/quantity

                # Use a random percentage of the available quantity (70-100%)
                rnd = int(quantity * random.uniform(0.7, 1.0))
                if rnd <= 0:
                    rnd = 1
                    
                while quantity>0:  
                    # day = random.randint(1,20) if quantity>=bulk else calendar.monthrange(year,month)[1]   # below date 20 rest amount is falling to date 30
                    # date = datetime.datetime(year, month, day).strftime('%d-%m-%Y')

                    if hesas.empty:
                        print("empty ____________________---------------")
                        break
                    
                    cs_name = "" 
                    
                    if len(districts[dist])>k:
                        cs_name=random.choice(districts[dist])
                    else :
                        _counter = len(districts[dist])+1
                        cs_name = "HS-VED-"+dist+"-"+subv+"-"+f"{_counter:04d}"
                        districts[dist].append(cs_name)

                        
                    if cs_name in track:
                        # print(track[cs_name])
                        hesas = zone_df[(zone_df["Hesaathi Code"] == track[cs_name])]
                        hs = hesas.sample(n=1).iloc[0]
                    else:
                        hs = hesas.sample(n=1).iloc[0]
                        # print(hs)
                        hs_code = str(hs["Hesaathi Code"])
                        track[cs_name] = hs_code
                    # print(quantity)
                    if quantity-rnd<0:
                        rnd = quantity
                    ind_taxable = unit_p*rnd
                    gst_am = gst*ind_taxable
                    row = {
                        "Date": date_value.strftime('%d/%m/%Y'),
                        "District": dist,
                        "Vertical": vertical,
                        "Sub Vertical": subv,
                        "Category": category,
                        "Sub Category":sub_category,
                        "Product Name": p_name,
                        "HSN Code": hsn_code if not pr_empty else "",
                        "Product Qty": rnd,
                        "UOM": uom ,
                        "GST Rate": gst,
                        "Gross Total": ind_taxable+gst_am,
                        "Taxable Value": ind_taxable,
                        "GST Amount": gst_am
                    }
                    rows.append(row)
                    quantity-=rnd
                    init_q -= rnd
                missed_quantity+=init_q
    df = pd.DataFrame(rows)
    print(len(rows))                
    df.to_excel("/home/thrymr/Downloads/December.xlsx")
    print("completed")
    
purchase()




import pandas as pd
import random

# Load the Excel file
df = pd.read_excel("/home/thrymr/Downloads/December.xlsx")

# Clean and format
df["District"] = df["District"].str.strip().str.upper()
df["Sub Vertical"] = df["Sub Vertical"].str.strip().str.upper()
df["__row_id__"] = df.index  # ✅ Unique ID for fast assignment

# Constants
MIN_VENDOR_IDS = 10
MAX_VENDOR_IDS = 15
MIN_TAXABLE = 85000
MAX_TAXABLE = 150000

# Step 1: Add Vendor ID column to DataFrame
df["Vendor ID"] = None
vendor_ids = []

# Step 2: Assign rows group-wise
grouped = df.groupby(["District", "Sub Vertical"])
for (district, sub_vertical), group_df in grouped:
    print(f"\n🚀 Processing group: {district}, {sub_vertical}")

    group_rows = df.loc[group_df.index].sample(frac=1, random_state=42).to_dict("records")

    # Create initial 25–30 vendor IDs
    vendor_count = random.randint(MIN_VENDOR_IDS, MAX_VENDOR_IDS)
    pool = []
    for i in range(1, vendor_count + 1):
        vendor = {
            "Vendor ID": f"HS-VED-{district}-{sub_vertical}-{i:04d}",
            "District": district,
            "Sub Vertical": sub_vertical,
            "Total Taxable": 0,  # ✅ Must be spelled exactly like this
            "Target Cap": random.uniform(MIN_TAXABLE, MAX_TAXABLE),
            "Rows": [],
        }

        vendor_ids.append(vendor)
        pool.append(vendor)

    # Assign rows randomly to vendors within ₹5L–₹8.5L
    for row in group_rows:
        row_taxable = row["Taxable Value"]
        random.shuffle(pool)  # Ensure randomness in vendor order

        assigned = False
        for vendor in pool:
            future_total = vendor["Total Taxable"] + row_taxable
            if future_total <= vendor["Target Cap"]:  # ✅ Use individual cap
                vendor["Rows"].append({**row})
                vendor["Total Taxable"] = future_total
                assigned = True
                break

        

        # If not assignable, create new vendor dynamically
        if not assigned:
            new_vendor_num = len([v for v in vendor_ids if v["District"] == district and v["Sub Vertical"] == sub_vertical]) + 1
            new_vendor_id = f"HS-VED-{district}-{sub_vertical}-{new_vendor_num:04d}"
            new_vendor = {
                "Vendor ID": new_vendor_id,
                "District": district,
                "Sub Vertical": sub_vertical,
                "Total Taxable": row_taxable,
                "Target Cap": random.uniform(MIN_TAXABLE, MAX_TAXABLE),
                "Rows": [{**row}],
            }

            vendor_ids.append(new_vendor)
            pool.append(new_vendor)
            print(f"➕ Created new vendor: {new_vendor_id} for ₹{row_taxable:.2f}")

    print(f"✅ Rows distributed among {len(pool)} vendors.")

# Step 3: Assign back to original DataFrame
print("\n📝 Assigning Vendor IDs to DataFrame using __row_id__...")

total_assigned = 0
for idx, vendor in enumerate(vendor_ids, start=1):
    for row in vendor["Rows"]:
        df.at[row["__row_id__"], "Vendor ID"] = vendor["Vendor ID"]
        total_assigned += 1
    print(f"✅ Vendor {idx}: {vendor['Vendor ID']} → {len(vendor['Rows'])} rows, ₹{vendor['Total Taxable']:.2f}")

print(f"\n🎯 Total rows assigned Vendor IDs: {total_assigned}")

# Step 4: Save output
df.drop(columns="__row_id__", inplace=True)
df.to_excel("/home/thrymr/Downloads/December_1.xlsx", index=False)




import pandas as pd
import random

input_file = "/home/thrymr/Downloads/December_1.xlsx"


zone_file = "/home/thrymr/Important/new_hessathi_with_additional_people_details (copy).xlsx"
output_file = "/home/thrymr/Downloads/December_(2021-22).xlsx"

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
        po_tracker[key] = f"HS-PO-{prefix}-{po_counter:06d}"
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

