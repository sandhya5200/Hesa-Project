# import pandas as pd

# # Load the Excel file
# file_path = "/home/thrymr/Desktop/bank_Purchases(23-24)/Purchases_Apr_23.xlsx"

# # Read the relevant sheets
# sales_df = pd.read_excel(file_path, sheet_name="Purchases_April_23")
# deposits_df = pd.read_excel(file_path, sheet_name="Bank File")

# # Group sales data by PO Number and sum the Total column
# sales_summary = sales_df.groupby("Invoice_No").agg({
#     "Total": "sum",
#     "Date": lambda x: ", ".join(map(str, x.dropna().unique()))  # Concatenate unique Date values
# }).reset_index()

# # Group deposits data by InvoiceNumber and sum the InvoiceAmount column
# deposits_summary = deposits_df.groupby("InvoiceNumber").agg({
#     "InvoiceAmount": "sum",
#     "ReferenceNumber": lambda x: ", ".join(map(str, x.dropna().unique())),  
#     "CreatedDate": lambda x: ", ".join(map(str, x.dropna().unique())),
#     "SRID": lambda x: ", ".join(map(str, x.dropna().unique())),
#     "BDID": lambda x: ", ".join(map(str, x.dropna().unique())),
#     "Mode": lambda x: ", ".join(map(str, x.dropna().unique())),
#     "DepositTo": lambda x: ", ".join(map(str, x.dropna().unique())),
#     "PayerAmount": "sum",
#     "OrderId": lambda x: ", ".join(map(str, x.dropna().unique())),
#     "InvoiceNo": lambda x: ", ".join(map(str, x.dropna().unique())),
#     "AmountReceived1": "sum"
# }).reset_index()

# # Convert sales and deposits invoices to sets
# sales_invoices = set(sales_summary["Invoice_No"])
# deposits_invoices = set(deposits_summary["InvoiceNumber"])

# # Find unused invoices
# unused_sales_invoices = sales_invoices - deposits_invoices
# unused_deposit_invoices = deposits_invoices - sales_invoices

# # Create an output list to store results
# output_data = []

# # Track used deposits
# used_deposits = set()

# # Iterate through sales invoices
# for _, row in sales_summary.iterrows():
#     invoice_no = row["Invoice_No"]
#     total_sales = row["Total"]
#     sales_dates = row["Date"]

#     # Find matching deposit row
#     matching_deposit = deposits_summary[deposits_summary["InvoiceNumber"] == invoice_no]

#     if not matching_deposit.empty:
#         total_deposit = matching_deposit["InvoiceAmount"].values[0]
#         reference_numbers = matching_deposit["ReferenceNumber"].values[0]
#         used_deposits.add(invoice_no)  # Mark deposit as used
#     else:
#         total_deposit = 0  # No deposit found for this invoice
#         reference_numbers = ""  # No reference number

#     wallet = total_sales - total_deposit
#     hesaathi_excess_credits = wallet if wallet < 0 else 0  # Store negative values only
#     wallet = max(wallet, 0)  # Replace negative values in "Wallet" with 0

#     # Store output row
#     output_data.append([
#         invoice_no, total_sales, sales_dates, 
#         total_deposit, reference_numbers, wallet, hesaathi_excess_credits
#     ])

# # Convert to DataFrame
# output_df = pd.DataFrame(output_data, columns=[
#     "Invoice_No", "Total Sales", "Sales Dates", 
#     "Total Deposit", "Reference Numbers", "Wallet", "Hesaathi Excess Credits"
# ])

# # Save the output file
# output_file = "/home/thrymr/Downloads/_summary.xlsx"
# output_df.to_excel(output_file, index=False)

# # Save unused sales invoices
# unused_sales_df = pd.DataFrame({"Unused Sales Invoice_No": list(unused_sales_invoices)})
# unused_sales_df.to_excel("/home/thrymr/Downloads/feb_unused_sales_invoices.xlsx", index=False)

# # Save unused deposits with all requested columns
# unused_deposits_df = deposits_summary[deposits_summary["InvoiceNumber"].isin(unused_deposit_invoices)][[
#     "InvoiceNumber", "InvoiceAmount", "CreatedDate", "SRID", "BDID", "Mode", "DepositTo",
#     "ReferenceNumber", "PayerAmount", "OrderId", "InvoiceNo", "AmountReceived1"
# ]]
# unused_deposits_df.to_excel("/home/thrymr/Downloads/Mar_unused_deposit_invoices.xlsx", index=False)


# print("Unused sales invoices saved: unused_sales_invoices.xlsx")
# print("Unused deposit invoices saved: unused_deposit_invoices.xlsx")

# -----------------------------------------------up for purchases----------------------------------------------------------------------------

import pandas as pd

# Load the Excel file
file_path = "/home/thrymr/Downloads/Sales_Apr_23.xlsx"

# Read the relevant sheets
sales_df = pd.read_excel(file_path, sheet_name="April_23")
deposits_df = pd.read_excel(file_path, sheet_name="Bank file")

# Group sales data by PO Number and sum the Total column
sales_summary = sales_df.groupby("Invoice_No").agg({
    "Total": "sum",
    "Date": lambda x: ", ".join(map(str, x.dropna().unique()))  # Concatenate unique Date values
}).reset_index()

# Group deposits data by InvoiceNumber and sum the InvoiceAmount column
deposits_summary = deposits_df.groupby("InvoiceNumber").agg({
    "InvoiceAmount": "sum",
    "ReferenceNumber": lambda x: ", ".join(map(str, x.dropna().unique())),  
    "CreatedDate": lambda x: ", ".join(map(str, x.dropna().unique())),
    "SRID": lambda x: ", ".join(map(str, x.dropna().unique())),
    "BDID": lambda x: ", ".join(map(str, x.dropna().unique())),
    "Mode": lambda x: ", ".join(map(str, x.dropna().unique())),
    "DepositTo": lambda x: ", ".join(map(str, x.dropna().unique())),
    "PayerAmount": "sum",
    "OrderId": lambda x: ", ".join(map(str, x.dropna().unique())),
    "InvoiceNo": lambda x: ", ".join(map(str, x.dropna().unique())),
    "AmountReceived1": "sum"
}).reset_index()

# Convert sales and deposits invoices to sets
sales_invoices = set(sales_summary["Invoice_No"])
deposits_invoices = set(deposits_summary["InvoiceNumber"])

# Find unused invoices
unused_sales_invoices = sales_invoices - deposits_invoices
unused_deposit_invoices = deposits_invoices - sales_invoices

# Create an output list to store results
output_data = []

# Track used deposits
used_deposits = set()

# Iterate through sales invoices
for _, row in sales_summary.iterrows():
    invoice_no = row["Invoice_No"]
    total_sales = row["Total"]
    sales_dates = row["Date"]

    # Find matching deposit row
    matching_deposit = deposits_summary[deposits_summary["InvoiceNumber"] == invoice_no]

    if not matching_deposit.empty:
        total_deposit = matching_deposit["InvoiceAmount"].values[0]
        reference_numbers = matching_deposit["ReferenceNumber"].values[0]
        used_deposits.add(invoice_no)  # Mark deposit as used
    else:
        total_deposit = 0  # No deposit found for this invoice
        reference_numbers = ""  # No reference number

    wallet = total_sales - total_deposit
    hesaathi_excess_credits = wallet if wallet < 0 else 0  # Store negative values only
    wallet = max(wallet, 0)  # Replace negative values in "Wallet" with 0

    # Store output row
    output_data.append([
        invoice_no, total_sales, sales_dates, 
        total_deposit, reference_numbers, wallet, hesaathi_excess_credits
    ])

# Convert to DataFrame
output_df = pd.DataFrame(output_data, columns=[
    "Invoice_No", "Total Sales", "Sales Dates", 
    "Total Deposit", "Reference Numbers", "Wallet", "Hesaathi Excess Credits"
])

# Save the output file
output_file = "/home/thrymr/Downloads/_summary_sales.xlsx"
output_df.to_excel(output_file, index=False)

# Save unused sales invoices
unused_sales_df = pd.DataFrame({"Unused Sales Invoice_No": list(unused_sales_invoices)})
unused_sales_df.to_excel("/home/thrymr/Downloads/sales_invoices.xlsx", index=False)

# Save unused deposits with all requested columns
unused_deposits_df = deposits_summary[deposits_summary["InvoiceNumber"].isin(unused_deposit_invoices)][[
    "InvoiceNumber", "InvoiceAmount", "CreatedDate", "SRID", "BDID", "Mode", "DepositTo",
    "ReferenceNumber", "PayerAmount", "OrderId", "InvoiceNo", "AmountReceived1"
]]
unused_deposits_df.to_excel("/home/thrymr/Downloads/deposit_invoices.xlsx", index=False)


print("Unused sales invoices saved: unused_sales_invoices.xlsx")
print("Unused deposit invoices saved: unused_deposit_invoices.xlsx")
