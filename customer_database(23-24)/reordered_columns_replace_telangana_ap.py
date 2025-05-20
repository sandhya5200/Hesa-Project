import pandas as pd

# Step 1: Read the input Excel file
file_path = '/home/thrymr/Downloads/check_december_(23-24).xlsx'
df = pd.read_excel(file_path)

# Step 2: Filter and update data
df_filtered = df[df['State'] == 'Andhra Pradesh']
df_filtered.loc[df_filtered['Customer State'] == 'Telangana', 'Customer State'] = 'Andhra Pradesh'
df_filtered['Customer District'] = df_filtered['District']
df_filtered['Customer Address'] = df_filtered['Mandal']
df.update(df_filtered)

# Step 3: Drop unnecessary columns
columns_to_drop = ['HSCode', 'Customer State', 'Filing Entity']
df = df.drop(columns=columns_to_drop)

# Step 4: Rename columns
columns_to_rename = {
    'Customer ID': 'Old Customer ID',
    'Mobile': 'Customer Mobile',
    'Mandal': 'Customer Mandal',
    'State': 'Customer State',
    'District': 'Old District'
}
df = df.rename(columns=columns_to_rename)

# Step 5: Reorder columns
columns_order = [
    'S.NO', 'Date', 'Order Id', 'Hesaathi Code', 'Invoice no.', 
    'Old Customer ID', 'Old District', 'Customer Name', 
    'Customer Mobile', 'Customer Address', 'Customer Mandal', 
    'Pincode', 'Customer District', 'Customer State', 'New CustomerID', 
    'GST Reg Status', 'GSTIN', 'Facilitator', 'Sub Vertical', 
    'Category', 'Sub Category', 'Product Name', 'Categeory', 
    'Sub categeory', 'HSN Code', 'Product Qty', 'UOM', 
    'Currency', 'MRP', 'Disc %', 'Disc PU', 'Net Price PU', 
    'Taxable Value', 'GST Rate', 'IGST', 'CGST', 'SGST', 'Total'
]
df = df[columns_order]

# Step 6: Save the updated DataFrame to a new Excel file
output_file_path = '/home/thrymr/Desktop/Input Files(2023-24)/sandhya.xlsx'
df.to_excel(output_file_path, index=False)

print("Excel file updated and saved successfully.")
