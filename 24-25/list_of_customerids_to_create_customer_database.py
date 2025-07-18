#first we have files normally in bring_customers_mcp code then that output files we have to keep here 
#for that output code we have to generate additional database then add that database and rerun in same code again

#basically after bringing the customers some customer ids did not have the details in customer database throough this code we will get the list of that ids 
# and we have create new customer database for that ids and again give input and run in bring_customers_code



import pandas as pd
import os

# List your 10 file paths here
file_paths = [
    "/home/thrymr/Downloads/Sheet1_Part1.xlsx",
    "/home/thrymr/Downloads/Sheet2_Part1.xlsx",
    "/home/thrymr/Downloads/Sheet3_Part1.xlsx"

]

all_customer_ids = set()

for path in file_paths:
    df = pd.read_excel(path)
    
    # Normalize column names (in case of extra spaces or capitalization issues)
    df.columns = df.columns.str.strip()
    
    # Check for missing customer names
    if 'Customer Name' in df.columns and 'CustomerID' in df.columns:
        filtered_ids = df[df['Customer Name'].isna()]['CustomerID'].dropna().unique()
        all_customer_ids.update(filtered_ids)

# Convert to DataFrame
result_df = pd.DataFrame({'CustomerID': list(all_customer_ids)})

# Save to Excel
result_df.to_excel("/home/thrymr/Downloads/empty_name_customer_ids_dec.xlsx", index=False)

print("✅ Done. File saved as 'empty_name_customer_ids.xlsx'")


