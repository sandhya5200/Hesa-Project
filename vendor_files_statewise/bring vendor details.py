import pandas as pd

# File paths for customer database files
customer_files = [
    "/home/thrymr/Downloads/new_vendor_databases/telangana_150_Vendors.xlsx",
    "/home/thrymr/Downloads/new_vendor_databases/ap_150_vendors.xlsx",
    "/home/thrymr/Downloads/new_vendor_databases/Odissa_Vendor_Database.xlsx",
    "/home/thrymr/Downloads/new_vendor_databases/MAHARASHTRA.xlsx",
    "/home/thrymr/Downloads/new_vendor_databases/JHARKHAND_Vendor_Database.xlsx",
    '/home/thrymr/Downloads/new_vendor_databases/Bihar_Vendor_Database.xlsx',
    '/home/thrymr/Downloads/new_vendor_databases/haryana_150_Vendors.xlsx',
    '/home/thrymr/Downloads/new_vendor_databases/karnataka_150_Vendors.xlsx',
    '/home/thrymr/Downloads/new_vendor_databases/tamilnadu_150_Vendors.xlsx'

   
]

# Load and clean customer database files
customer_data_list = []
for file in customer_files:
    df = pd.read_excel(file)
    df['Vendor ID'] = df['Vendor ID'].astype(str).str.strip().str.lower()  # Clean Vendor ID
    customer_data_list.append(df)

# Combine all customer databases into a single DataFrame
customer_data = pd.concat(customer_data_list, ignore_index=True)

# Create dictionaries for quick lookups with cleaned keys
customer_dict = dict(zip(customer_data['Vendor ID'], customer_data['Name']))
address_dict = dict(zip(customer_data['Vendor ID'], customer_data['Address']))
mobile_dict = dict(zip(customer_data['Vendor ID'], customer_data['Mobile']))
pincode_dict = dict(zip(customer_data['Vendor ID'], customer_data['Pincode']))
state_dict = dict(zip(customer_data['Vendor ID'], customer_data['State']))
district_dict = dict(zip(customer_data['Vendor ID'], customer_data['District']))

# Load and clean sales file
sales_file = "/home/thrymr/Desktop/purchases(2023-24)/Purchases_Mar_24.xlsx"
df_sales = pd.read_excel(sales_file)
df_sales['Vendor_Id'] = df_sales['Vendor_Id'].astype(str).str.strip().str.lower()  # Clean Vendor ID

# Add new columns for customer details using the cleaned keys
df_sales['Vendor Name'] = df_sales['Vendor_Id'].map(customer_dict)
df_sales['Vendor Address'] = df_sales['Vendor_Id'].map(address_dict)
df_sales['Vendor Mobile'] = df_sales['Vendor_Id'].map(mobile_dict)
df_sales['Pincode'] = df_sales['Vendor_Id'].map(pincode_dict)
df_sales['Vendor State'] = df_sales['Vendor_Id'].map(state_dict)
df_sales['Vendor District'] = df_sales['Vendor_Id'].map(district_dict)

# Save the updated sales file
updated_sales_file = "/home/thrymr/Desktop/purchases(2023-24)/Check_Purchases_Mar_24.xlsx"
df_sales.to_excel(updated_sales_file, index=False)

print(f"Step 1 completed: Updated Excel file saved as: {updated_sales_file}")
