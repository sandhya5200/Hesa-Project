import pandas as pd

# File paths for customer database files
customer_files = [
    "/home/thrymr/Downloads/customer_database_part1.xlsx",
    "/home/thrymr/Downloads/Customer_database_part2a.xlsx",
    "/home/thrymr/Downloads/Customer_database_part2b.xlsx",
    "/home/thrymr/Downloads/Customer_database_part2c.xlsx",
    "/home/thrymr/Downloads/Customer_data/additional_database1.xlsx"
]

# Combine all customer databases into a single DataFrame
customer_data = pd.concat([pd.read_excel(file) for file in customer_files])

# Create dictionaries for quick lookups
customer_dict = dict(zip(customer_data['CustomerID'], customer_data['Name']))
address_dict = dict(zip(customer_data['CustomerID'], customer_data['Address']))
mobile_dict = dict(zip(customer_data['CustomerID'], customer_data['Mobile']))
mandal_dict = dict(zip(customer_data['CustomerID'], customer_data['Mandal']))
pincode_dict = dict(zip(customer_data['CustomerID'], customer_data['Pincode']))
 
# Load all sheets from the sales file
sales_file = "/home/thrymr/Desktop/input Files(24-25)/Consumer Sales - Sep 2024.xlsx"  

sheets_dict = pd.read_excel(sales_file, sheet_name=None)  # Load all sheets

# Combine all sheets into a single DataFrame
df_sales = pd.concat(sheets_dict.values(), ignore_index=True)

# Add new columns for customer details
df_sales['Customer Name'] = df_sales['Customer ID'].map(customer_dict)
df_sales['Customer Address'] = df_sales['Customer ID'].map(address_dict)
df_sales['Customer Mobile'] = df_sales['Customer ID'].map(mobile_dict)
df_sales['Customer Mandal'] = df_sales['Customer ID'].map(mandal_dict)
df_sales['Pincode'] = df_sales['Customer ID'].map(pincode_dict)

# Step 2: Calculate MCP using the updated sales file
def calculate_mcp(row):
    rate = row['Net Price PU']
    facilitator = row['Facilitator']
    mrp = row['MRP']

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

# Calculate MCP and add the column
df_sales['MCP'] = df_sales.apply(calculate_mcp, axis=1)

# Save the final output (split into multiple sheets if necessary)
final_output_file = "/home/thrymr/Desktop/input Files(24-25)/with_customerdata_cons_sales_Sep_24.xlsx"
MAX_ROWS = 1_048_576  # Excel row limit

with pd.ExcelWriter(final_output_file, engine='xlsxwriter') as writer:
    for i in range(0, len(df_sales), MAX_ROWS):
        df_sales.iloc[i:i+MAX_ROWS].to_excel(writer, sheet_name=f"Sheet_{i//MAX_ROWS + 1}", index=False)

print(f"Step 2 completed: Final Excel file saved as {final_output_file} (Split into multiple sheets).")