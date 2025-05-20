#first we have files normally in bring_customers_mcp code then that output files we have to keep here 
#for that output code we have to generate additional database then add that database and rerun in same code again

#basically after bringing the customers some customer ids did not have the details in customer database throough this code we will get the list of that ids 
# and we have create new customer database for that ids and again give input and run in bring_customers_code
import pandas as pd

file_paths = [
    "/home/thrymr/Downloads/agri_sales_apr_24.xlsx",
    "/home/thrymr/Downloads/agri_sales_may_24.xlsx",
    "/home/thrymr/Downloads/agri_sales_june_24.xlsx",
    "/home/thrymr/Downloads/agri_sales_july_24.xlsx",
    "/home/thrymr/Downloads/agri_sales_Aug_24.xlsx",
    "/home/thrymr/Downloads/agri_sales_Sep_24.xlsx",
    "/home/thrymr/Downloads/cons_sales_apr_24.xlsx",
    "/home/thrymr/Downloads/cons_sales_May_24.xlsx",
    "/home/thrymr/Downloads/cons_sales_june_24.xlsx",
    "/home/thrymr/Downloads/cons_sales_july_24.xlsx",
    "/home/thrymr/Downloads/cons_sales_Aug_24.xlsx",
    "/home/thrymr/Downloads/cons_sales_Sep_24.xlsx"
]  

customer_data = []

print("Starting the file processing...")

for file in file_paths:
    print(f"Processing file: {file}")
    xls = pd.ExcelFile(file)

    for sheet_name in xls.sheet_names:
        print(f"  Reading sheet: {sheet_name}")
        df = pd.read_excel(xls, sheet_name=sheet_name)

        if "Customer Name" in df.columns and "Customer ID" in df.columns and "Hesaathi Code" in df.columns:
            print("  Required columns found. Filtering data...")
            # Filter rows where "Customer Name" is empty
            filtered_df = df[df["Customer Name"].isna()][["Customer ID", "Hesaathi Code"]]
            customer_data.append(filtered_df)
            print(f"  {len(filtered_df)} rows extracted from {sheet_name}")
        else:
            print("  Skipping sheet - Required columns not found.")

print("Merging data from all files...")
# Concatenate all data and remove duplicates
if customer_data:
    final_df = pd.concat(customer_data, ignore_index=True).drop_duplicates()
    print(f"Total unique records found: {len(final_df)}")
    
    # Save to a new Excel file
    output_file = "/home/thrymr/Downloads/Important.xlsx"
    final_df.to_excel(output_file, index=False)
    print(f"Processed successfully! File saved as {output_file}")
else:
    print("No matching data found across the files.")

print("Task completed!")