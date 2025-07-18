# import pandas as pd

# # File paths for customer database files
# customer_files = [
#     "/home/thrymr/Desktop/Customer_data/customer_database_part1.xlsx",
#     "/home/thrymr/Desktop/Customer_data/Customer_database_part2a.xlsx",
#     "/home/thrymr/Desktop/Customer_data/Customer_database_part2b.xlsx",
#     "/home/thrymr/Desktop/Customer_data/Customer_database_part2c.xlsx",
#     "/home/thrymr/Desktop/Customer_data/additional_database1.xlsx"
# ]

# # Combine all customer databases into a single DataFrame
# customer_data = pd.concat([pd.read_excel(file) for file in customer_files])

# # Create dictionaries for quick lookups
# customer_dict = dict(zip(customer_data['CustomerID'], customer_data['Name']))
# address_dict = dict(zip(customer_data['CustomerID'], customer_data['Address']))
# mobile_dict = dict(zip(customer_data['CustomerID'], customer_data['Mobile']))
# mandal_dict = dict(zip(customer_data['CustomerID'], customer_data['Mandal']))
# pincode_dict = dict(zip(customer_data['CustomerID'], customer_data['Pincode']))

# # Load the sales file

# sales_file = "/home/thrymr/Downloads/Oct Sales part 1 24-25(Final).xlsx"
# df_sales = pd.read_excel(sales_file)

# # Add new columns for customer details
# df_sales['Customer Name'] = df_sales['Customer ID'].map(customer_dict)
# df_sales['Customer Address'] = df_sales['Customer ID'].map(address_dict)
# df_sales['Customer Mobile'] = df_sales['Customer ID'].map(mobile_dict)
# df_sales['Customer Mandal'] = df_sales['Customer ID'].map(mandal_dict)
# df_sales['Pincode'] = df_sales['Customer ID'].map(pincode_dict)

# # Rename columns as needed
# df_sales.rename(
#     columns={
#         'Hesaathi Code': 'Hesaathi Code',
#         'Customer ID': 'CustomerID',
#         'Customer State': 'Customer State',
#         'Customer District': 'CustomerDistrict',
#         'Product Name': 'Product Name',
#         'HSN Code': 'HSN/SAC',
#         'Product Qty': 'Quantity',
#         'UOM': 'UOM',
#         'Net Price PU': 'Rate',
#         'Taxable Value': 'Taxable Value',
#         'GST Rate': 'GST Rate',
#         'Total Value': 'Sub total',
#         'General': 'Invoice No',
#     },
#     inplace=True,
# )

# # Save the updated sales file
# updated_sales_file = "/home/thrymr/Downloads/delete.xlsx"
# df_sales.to_excel(updated_sales_file, index=False)
# print(f"Step 1 completed: Updated Excel file saved as: {updated_sales_file}")

# # Step 2: Calculate MCP using the updated sales file
# def calculate_mcp(row):
#     rate = row['Rate']
#     facilitator = row['Facilitator']
#     mrp = row['MRP']

#     # Calculate MCP based on Facilitator
#     if facilitator == "Hesa Agritech Private Limited":
#         mcp = rate + (rate * 1.5 / 100)
#     elif facilitator == "Hesa Consumer Products Private Limited":
#         mcp = rate + (rate * 2.5 / 100)
#     else:
#         mcp = rate  # Default to the rate if no condition matches

#     # Ensure MCP does not exceed MRP
#     if mcp > mrp:
#         mcp = mrp

#     return mcp

# # Load the updated sales file
# df_sales = pd.read_excel(updated_sales_file)

# # Calculate MCP and add the column
# df_sales['MCP'] = df_sales.apply(calculate_mcp, axis=1)

# # Save the final output
# final_output_file = "/home/thrymr/Downloads/check.xlsx"
# df_sales.to_excel(final_output_file, index=False)
# print(f"Step 2 completed: Final Excel file saved as: {final_output_file}")


################# for huge files i have done this below code consider above code only ###############################


import pandas as pd
import os
import math

# Load and merge all customer databases
customer_files = [
    "/home/thrymr/Desktop/Customer_data/customer_database_part1.xlsx",
    "/home/thrymr/Desktop/Customer_data/Customer_database_part2a.xlsx",
    "/home/thrymr/Desktop/Customer_data/Customer_database_part2b.xlsx",
    "/home/thrymr/Desktop/Customer_data/Customer_database_part2c.xlsx",
    "/home/thrymr/Desktop/Customer_data/additional_database1.xlsx",
    "/home/thrymr/Desktop/Customer_data/additional_database_2.xlsx"
]
customer_data = pd.concat([pd.read_excel(file) for file in customer_files])

# Create lookup dictionaries
customer_dict = dict(zip(customer_data['CustomerID'], customer_data['Name']))
address_dict = dict(zip(customer_data['CustomerID'], customer_data['Address']))
mobile_dict = dict(zip(customer_data['CustomerID'], customer_data['Mobile']))
mandal_dict = dict(zip(customer_data['CustomerID'], customer_data['Mandal']))
pincode_dict = dict(zip(customer_data['CustomerID'], customer_data['Pincode']))

# Sales files list
sales_files = [

    "/home/thrymr/Downloads/Sheet1.xlsx",
    "/home/thrymr/Downloads/Sheet2.xlsx",
    "/home/thrymr/Downloads/Sheet3.xlsx"

]

# MCP calculation function
def calculate_mcp(row):
    rate = row['Rate']
    facilitator = row['Facilitator']
    mrp = row['MRP']
    
    if facilitator == "Hesa Agritech Private Limited":
        mcp = rate + (rate * 1.5 / 100)
    elif facilitator == "Hesa Consumer Products Private Limited":
        mcp = rate + (rate * 2.5 / 100)
    else:
        mcp = rate

    return min(mcp, mrp)

# Excel limit
MAX_ROWS = 1048575

# Process each sales file
for file_path in sales_files:
    print(f"Processing: {file_path}")
    
    # Read all sheets
    all_sheets = pd.read_excel(file_path, sheet_name=None)
    df_sales = pd.concat(all_sheets.values(), ignore_index=True)
    
    # Add customer details
    df_sales['Customer Name'] = df_sales['Customer ID'].map(customer_dict)
    df_sales['Customer Address'] = df_sales['Customer ID'].map(address_dict)
    df_sales['Customer Mobile'] = df_sales['Customer ID'].map(mobile_dict)
    df_sales['Customer Mandal'] = df_sales['Customer ID'].map(mandal_dict)
    df_sales['Pincode'] = df_sales['Customer ID'].map(pincode_dict)

    # Rename columns for consistency
    df_sales.rename(columns={
        'Hesaathi Code': 'Hesaathi Code',
        'Customer ID': 'CustomerID',
        'Customer State': 'Customer State',
        'Customer District': 'CustomerDistrict',
        'Product Name': 'Product Name',
        'HSN Code': 'HSN/SAC',
        'Product Qty': 'Quantity',
        'UOM': 'UOM',
        'Net Price PU': 'Rate',
        'Taxable Value': 'Taxable Value',
        'GST Rate': 'GST Rate',
        'Total Value': 'Sub total',
        'General': 'Invoice No',
    }, inplace=True)

    # Calculate MCP
    df_sales['MCP'] = df_sales.apply(calculate_mcp, axis=1)
    
    # Split into multiple parts if needed
    total_rows = len(df_sales)
    base_filename = os.path.splitext(os.path.basename(file_path))[0].replace(" ", "_")
    num_parts = math.ceil(total_rows / MAX_ROWS)

    for i in range(num_parts):
        start = i * MAX_ROWS
        end = min((i + 1) * MAX_ROWS, total_rows)
        part = df_sales.iloc[start:end].copy()
        output_file = f"/home/thrymr/Downloads/{base_filename}_Part{i+1}.xlsx"
        part.to_excel(output_file, index=False)
        print(f"✅ Saved: {output_file} ({len(part)} rows)")
