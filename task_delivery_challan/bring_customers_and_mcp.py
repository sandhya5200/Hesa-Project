import pandas as pd

# File paths for customer database files
customer_files = [
    "/home/thrymr/Downloads/customer_database_part1.xlsx",
    "/home/thrymr/Downloads/Customer_database_part2a.xlsx",
    "/home/thrymr/Downloads/Customer_database_part2b.xlsx",
    "/home/thrymr/Downloads/Customer_database_part2c.xlsx",
]

# Combine all customer databases into a single DataFrame
customer_data = pd.concat([pd.read_excel(file) for file in customer_files])

# Create dictionaries for quick lookups
customer_dict = dict(zip(customer_data['CustomerID'], customer_data['Name']))
address_dict = dict(zip(customer_data['CustomerID'], customer_data['Address']))
mobile_dict = dict(zip(customer_data['CustomerID'], customer_data['Mobile']))
mandal_dict = dict(zip(customer_data['CustomerID'], customer_data['Mandal']))
pincode_dict = dict(zip(customer_data['CustomerID'], customer_data['Pincode']))

# Load the sales file

sales_file = "/home/thrymr/Desktop/sales(2023-24)/Sales_Apr_23.xlsx"
df_sales = pd.read_excel(sales_file)

# Add new columns for customer details
df_sales['Customer Name'] = df_sales['CustomerID'].map(customer_dict)
df_sales['Customer Address'] = df_sales['CustomerID'].map(address_dict)
df_sales['Customer Mobile'] = df_sales['CustomerID'].map(mobile_dict)
df_sales['Customer Mandal'] = df_sales['CustomerID'].map(mandal_dict)
df_sales['Pincode'] = df_sales['CustomerID'].map(pincode_dict)

# Rename columns as needed
df_sales.rename(
    columns={
        'Hesaathi_Code': 'Hesaathi Code',
        'CustomerID': 'CustomerID',
        'Customer_State': 'Customer State',
        'Customer_District': 'CustomerDistrict',
        'Product_Name': 'Product Name',
        'Hsn_Code': 'HSN/SAC',
        'Product_Qty': 'Quantity',
        'Uom': 'UOM',
        'Net_Price_Pu': 'Rate',
        'Taxable_Value': 'Taxable Value',
        'Gst_Rate': 'GST Rate',
        'Total': 'Sub total',
        'Invoice_No': 'Invoice No',
    },
    inplace=True,
)

# Save the updated sales file
updated_sales_file = "/home/thrymr/Downloads/sales 23-24/delete.xlsx"
df_sales.to_excel(updated_sales_file, index=False)
print(f"Step 1 completed: Updated Excel file saved as: {updated_sales_file}")

# Step 2: Calculate MCP using the updated sales file
def calculate_mcp(row):
    rate = row['Rate']
    facilitator = row['Facilitator']
    mrp = row['Mrp']

    # Calculate MCP based on Facilitator
    if facilitator == "Hesa Agritech Private Limited":
        mcp = rate + (rate * 1.5 / 100)
    elif facilitator == "Hesa Consumer Products Private Limited":
        mcp = rate + (rate * 2.5 / 100)
    else:
        mcp = rate  # Default to the rate if no condition matches

    # Ensure MCP does not exceed MRP
    if mcp > mrp:
        mcp = mrp

    return mcp

# Load the updated sales file
df_sales = pd.read_excel(updated_sales_file)

# Calculate MCP and add the column
df_sales['MCP'] = df_sales.apply(calculate_mcp, axis=1)

# Save the final output
final_output_file = "/home/thrymr/Downloads/sales 23-24/Final_Sales_Mar_24.xlsx"
df_sales.to_excel(final_output_file, index=False)
print(f"Step 2 completed: Final Excel file saved as: {final_output_file}")
