import pandas as pd
import numpy as np
from datetime import datetime
import os

def create_sales_pivot(input_file_path, output_file_path):
    """
    Create pivot tables from sales data and save to specified Excel file with two sheets
    - Sheet 1: Product Quantities by District (sheet name: "Quantity")
    - Sheet 2: Taxable Values by District (sheet name: "Taxable value")
    """
    
    # Read the Excel file (assuming it's Excel format)
    print("Reading sales data...")
    try:
        # Try reading as Excel first, then CSV if that fails
        if input_file_path.endswith('.xlsx') or input_file_path.endswith('.xls'):
            df = pd.read_excel(input_file_path)
        else:
            df = pd.read_csv(input_file_path)
        print(f"Data loaded successfully: {len(df)} rows")
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Display basic info about the dataset
    print(f"Columns in dataset: {list(df.columns)}")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"Unique districts: {df['District'].nunique()}")
    print(f"Unique products: {df['Product Name'].nunique()}")
    
    # Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Clean and prepare data
    # Remove any rows with missing essential data
    essential_cols = ['Date', 'Sub Vertical', 'Product Name', 'HSN/SAC', 
                     'UOM', 'Category', 'Sub Category', 'gst_rate', 
                     'District', 'Quantity', 'Taxable Value']
    
    df_clean = df.dropna(subset=essential_cols)
    print(f"Rows after cleaning: {len(df_clean)}")
    
    # Create base dataframe with required columns
    base_cols = ['Date', 'Sub Vertical', 'Product Name', 'HSN/SAC', 
                'UOM', 'Category', 'Sub Category', 'gst_rate']
    
    # 1. CREATE QUANTITY PIVOT TABLE
    print("\nCreating Quantity Pivot Table...")
    
    # Create pivot table for quantities
    quantity_pivot = df_clean.pivot_table(
        index=base_cols,
        columns='District',
        values='Quantity',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    # Flatten column names
    quantity_pivot.columns.name = None
    
    print(f"Quantity pivot shape: {quantity_pivot.shape}")
    print(f"Districts in quantity pivot: {[col for col in quantity_pivot.columns if col not in base_cols]}")
    
    # 2. CREATE TAXABLE VALUE PIVOT TABLE
    print("\nCreating Taxable Value Pivot Table...")
    
    # Create pivot table for taxable values
    value_pivot = df_clean.pivot_table(
        index=base_cols,
        columns='District',
        values='Taxable Value',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    # Flatten column names
    value_pivot.columns.name = None
    
    print(f"Value pivot shape: {value_pivot.shape}")
    print(f"Districts in value pivot: {[col for col in value_pivot.columns if col not in base_cols]}")
    
    # 3. SAVE TO EXCEL FILE WITH TWO SHEETS
    print(f"\nSaving Excel file to: {output_file_path}")
    
    # Create the output Excel file with both sheets
    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
        # Sheet 1: Quantities (sheet name: "Quantity")
        quantity_pivot.to_excel(writer, sheet_name='Quantity', index=False)
        
        # Sheet 2: Taxable Values (sheet name: "Taxable value")  
        value_pivot.to_excel(writer, sheet_name='Taxable value', index=False)
        
        # Format both sheets
        for sheet_name in ['Quantity', 'Taxable value']:
            worksheet = writer.sheets[sheet_name]
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"✅ Excel file saved successfully with both sheets!")
    
    # 4. DISPLAY SUMMARY STATISTICS
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    
    # Get district columns (exclude base columns)
    district_cols = [col for col in quantity_pivot.columns if col not in base_cols]
    
    print(f"\n📊 DISTRICTS COVERED ({len(district_cols)}):")
    for i, district in enumerate(district_cols, 1):
        qty_total = quantity_pivot[district].sum()
        value_total = value_pivot[district].sum()
        print(f"{i:2d}. {district:15s} | Qty: {qty_total:10,.2f} | Value: ₹{value_total:12,.2f}")
    
    print(f"\n📈 OVERALL TOTALS:")
    total_qty = quantity_pivot[district_cols].sum().sum()
    total_value = value_pivot[district_cols].sum().sum()
    print(f"Total Quantity: {total_qty:,.2f}")
    print(f"Total Value: ₹{total_value:,.2f}")
    
    print(f"\n📦 PRODUCT CATEGORIES:")
    category_summary = df_clean.groupby('Category').agg({
        'Quantity': 'sum',
        'Taxable Value': 'sum'
    }).round(2)
    print(category_summary)
    
    print(f"\n🏢 SUB-VERTICAL SUMMARY:")
    subvertical_summary = df_clean.groupby('Sub Vertical').agg({
        'Quantity': 'sum',
        'Taxable Value': 'sum'
    }).round(2)
    print(subvertical_summary)
    
    return quantity_pivot, value_pivot

def create_combined_file(input_file_path, output_file_path):
    """
    Create a single Excel file with both quantity and value sheets
    """
    print("Creating Excel file with both sheets...")
    
    # Read the Excel file
    if input_file_path.endswith('.xlsx') or input_file_path.endswith('.xls'):
        df = pd.read_excel(input_file_path)
    else:
        df = pd.read_csv(input_file_path)
        
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Clean data
    essential_cols = ['Date', 'Sub Vertical', 'Product Name', 'HSN/SAC', 
                     'UOM', 'Category', 'Sub Category', 'gst_rate', 
                     'District', 'Quantity', 'Taxable Value']
    
    df_clean = df.dropna(subset=essential_cols)
    
    base_cols = ['Date', 'Sub Vertical', 'Product Name', 'HSN/SAC', 
                'UOM', 'Category', 'Sub Category', 'gst_rate']
    
    # Create both pivot tables
    quantity_pivot = df_clean.pivot_table(
        index=base_cols,
        columns='District',
        values='Quantity',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    value_pivot = df_clean.pivot_table(
        index=base_cols,
        columns='District',
        values='Taxable Value',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    # Clean column names
    quantity_pivot.columns.name = None
    value_pivot.columns.name = None
    
    # Save to specified output file
    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
        quantity_pivot.to_excel(writer, sheet_name='Quantity', index=False)
        value_pivot.to_excel(writer, sheet_name='Taxable value', index=False)
        
        # Format both sheets
        for sheet_name in ['Quantity', 'Taxable value']:
            worksheet = writer.sheets[sheet_name]
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"✅ Combined file saved: {output_file_path}")
    return output_file_path

# Example usage with your specific file paths:
if __name__ == "__main__":
    # Your specific file paths
    input_file = "/home/thrymr/Downloads/sales(20-21)/may_sales_with_customers.xlsx"
    output_file = "/home/thrymr/Downloads/May_pivot.xlsx"
    
    try:
        # Create pivot tables and save to your specified output file
        print("Processing sales data with your file paths...")
        qty_pivot, val_pivot = create_sales_pivot(input_file, output_file)
        
        print(f"\n✅ File created successfully!")
        print(f"📁 Output file: {output_file}")
        print(f"📊 Sheets: 'Quantity' and 'Taxable value'")
        
        
    except FileNotFoundError:
        print(f"❌ Input file not found: {input_file}")
        print("Please make sure the file exists at the specified location")
    except Exception as e:
        print(f"❌ Error: {e}")

# Function to read the created pivot data (for your reference)
def read_created_pivots():
    """
    Function to read the pivot data you just created
    """
    output_file = "/home/thrymr/Downloads/May_pivot.xlsx"
    
    # Read both sheets
    product_quantity = pd.read_excel(output_file, sheet_name="Quantity")
    product_gross = pd.read_excel(output_file, sheet_name="Taxable value")
    
    print(f"Quantity sheet shape: {product_quantity.shape}")
    print(f"Taxable value sheet shape: {product_gross.shape}")
    
    return product_quantity, product_gross






#-----------------------------------------------------------------------------------------------------------








import datetime
from fastapi import APIRouter
import random
import pandas as pd

month_map = [
    "April'20", "May'20", "Jun'20", "Jul'20", "Aug'20", "Sep'20", 
    "Oct'20", "Nov'20", "Dec'20", "Jan'21", "Feb'21", "Mar'21"
]

business_dict = {
    "Agri Inputs": [7.10, 7.25, 7.40, 7.55, 7.70, 7.85, 8.00, 8.15, 8.30, 8.45, 8.60, 8.75],                #these are in the order of  jan-dec
    "Market Linkages Trading": [7.50, 7.65, 7.80, 7.95, 8.10, 8.25, 8.40, 8.55, 8.70, 8.85, 8.95, 9.00],
    "FMCG": [ 7.20, 7.35, 7.50, 7.65, 7.80, 7.95, 8.10, 8.25, 8.40, 8.55, 8.70, 8.85],

}

def purchase():
    print("before")
    product_quantity = pd.read_excel("/home/thrymr/Downloads/May_pivot.xlsx", sheet_name="Quantity")
   
    product_gross = pd.read_excel("/home/thrymr/Downloads/May_pivot.xlsx", sheet_name="Taxable value")
    
    zone_df = pd.read_excel("/home/thrymr/Important/new_hessathi_with_additional_people_details (copy).xlsx")
    products_data = pd.read_excel("/home/thrymr/Downloads/myyy.xlsx")
    #vendor = pd.read_excel("/home/thrymr/Downloads/Vendor data 1 1.xlsx",sheet_name="10-15 vendors from this data")
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
    df.to_excel("/home/thrymr/Downloads/May.xlsx")
    print("completed")
    
purchase()



#-----------------------------------------------------------------------------------------------------





import pandas as pd
import random

# Load the Excel file
df = pd.read_excel("/home/thrymr/Downloads/May.xlsx")

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
df.to_excel("/home/thrymr/Downloads/May.xlsx", index=False)





#-----------------------------------------------------------------------------------------------------





import pandas as pd
import random

input_file = "/home/thrymr/Downloads/May.xlsx"


zone_file = "/home/thrymr/Important/new_hessathi_with_additional_people_details (copy).xlsx"
output_file = "/home/thrymr/Downloads/May_final.xlsx"

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
        po_tracker[key] = f"2020-21/HS/PO/{po_counter:06d}"
        po_counter += 1
    
    return po_tracker[key]


# Apply function
input_df["PO Number"] = input_df.apply(generate_po_number, axis=1)

# Create a mapping of districts to available Hesaathi Codes
district_hesaathi_map = zone_df.groupby("District")["Hesaathi Code"].apply(list).to_dict()

# Custom district mappings for fallback logic
district_code_mappings = {
    "vijayawada": ["srikakulam", "kurnool", "guntur", "visakhapatnam"],
    # "wanaparthy": ["medak", "warangal", "adilabad", "nalgonda"],
    # "balasore": ["angul", "balangir", "boudh", "cuttak"],
    # "sangareddy": ["karim nagar", "nizamabad", "rangareddy", "warangal"],
    # "vikarabad": ["medak", "warangal","nizamabad", "rangareddy"],
    # "ujjain": ["dhule", "jalgaon", "buldhana", "amravati"],
    # "dhar": ["dhule", "jalgaon", "buldhana", "amravati"]

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




#-----------------------------------------------------------------------------------------------------------




import pandas as pd

# Load input file
input_df = pd.read_excel("/home/thrymr/Downloads/May_final.xlsx")  # Change to .csv if needed

input_df['vendor_id_norm'] = input_df['Vendor ID'].astype(str).str.lower().str.replace(" ", "")
input_df['vendor_state_norm'] = input_df['State'].astype(str).str.lower().str.replace(" ", "")

state_files = {
    # "andhrapradesh": pd.read_excel("/home/thrymr/Desktop/vendors/Andrapradesh_with_updates_vendors.xlsx"),
    # "maharashtra": pd.read_excel("/home/thrymr/Desktop/vendors/Maharashtra_with_updates_vendors.xlsx"),
    # "odisha": pd.read_excel("/home/thrymr/Desktop/vendors/odissa_with_updates_vendors.xlsx"),
    # "tamilnadu": pd.read_excel("/home/thrymr/Desktop/vendors/TAMILNADU_Vendor_Database.xlsx"),
    "telangana": pd.read_excel("/home/thrymr/Downloads/telangana_150_Vendors (1).xlsx"),
    # "karnataka": pd.read_excel("/home/thrymr/Desktop/vendors/Karnataka_Vendor_Database.xlsx"),
    # "haryana": pd.read_excel("/home/thrymr/Desktop/vendors/Haryana_Vendor_Database.xlsx"),
    # "bihar": pd.read_excel("/home/thrymr/Desktop/vendors/Bihar_Vendor_Database.xlsx"),
    # "madhyapradesh": pd.read_excel("/home/thrymr/Desktop/vendors/mp_with_updates_vendors.xlsx")
}

# Normalize columns in state files
for state_key, df in state_files.items():
    df.columns = df.columns.str.strip()
    df['vendor_id_norm'] = df['Vendor ID'].astype(str).str.lower().str.replace(" ", "")
    state_files[state_key] = df

# Prepare result list
merged_rows = []

# Iterate through each row in input
for idx, row in input_df.iterrows():
    norm_state = row['vendor_state_norm']
    norm_id = row['vendor_id_norm']

    enriched_row = row.drop(['vendor_id_norm', 'vendor_state_norm']).to_dict()  # Keep original values

    if norm_state in state_files:
        state_df = state_files[norm_state]

        # Match using normalized ID
        match = state_df[state_df['vendor_id_norm'] == norm_id]

        if not match.empty:
            details_row = match.iloc[0]

            # Add additional vendor details
            enriched_row.update({
                'Mobile': details_row.get('Mobile'),
                'Name': details_row.get('Name'),
                'District': details_row.get('District'),
                'State_from_vendor': details_row.get('State'),   # renamed to avoid overwrite
                'Sub Vertical': details_row.get('Sub Vertical'),
                'Address': details_row.get('Address'),
                'Pincode': details_row.get('Pincode'),
            })
        else:
            # If no match, vendor details remain blank (NaN)
            enriched_row.update({
                'Mobile': None,
                'Name': None,
                'District': None,
                'State_from_vendor': None,
                'Sub Vertical': None,
                'Address': None,
                'Pincode': None,
            })
    else:
        # State not found in mapping, still keep the row
        enriched_row.update({
            'Mobile': None,
            'Name': None,
            'District': None,
            'State_from_vendor': None,
            'Sub Vertical': None,
            'Address': None,
            'Pincode': None,
        })

    merged_rows.append(enriched_row)

# Convert result to DataFrame
final_df = pd.DataFrame(merged_rows)

# Save to Excel
final_df.to_excel("/home/thrymr/Downloads/purchase(20-21)/May_purchase_with_vendors.xlsx", index=False)
print("✅ Merged output saved! (all rows preserved)")
