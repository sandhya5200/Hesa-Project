# import pandas as pd

# # -----------------------------
# # Load your files
# # -----------------------------
# sales_path = "/home/thrymr/Downloads/sales.xlsx"
# bank_path  = "/home/thrymr/Downloads/bank_agri_april.xlsx"

# sales = pd.read_excel(sales_path)
# bank  = pd.read_excel(bank_path)

# # -----------------------------
# # Clean and standardize columns
# # -----------------------------
# sales["Zoho Invoice"] = sales["Zoho Invoice"].astype(str).str.strip()
# bank["Invoice Number"] = bank["Invoice Number"].astype(str).str.strip()


# # Convert dates
# sales["Date"] = pd.to_datetime(sales["Date"]).dt.date
# bank["Date"]  = pd.to_datetime(bank["Date"]).dt.date

# # -----------------------------
# # Add columns for allocation
# # -----------------------------
# sales["Bank Amount Allocated"] = 0.0
# sales["Wallet Amount"] = 0.0

# # To store expanded bank data in sales rows
# bank_cols = [c for c in bank.columns]
# for c in bank_cols:
#     sales["BANK_" + c] = None

# # -----------------------------
# # Allocation Logic
# # -----------------------------
# for _, bank_row in bank.iterrows():

#     bank_amount = bank_row["Amount"]
#     bank_invoice = bank_row["Invoice Number"]
#     bank_date = bank_row["Date"]

#     # Find matching sales rows by invoice 
#     match = sales[
#         (sales["Zoho Invoice"] == bank_invoice)
#     ]

#     # If no match → whole amount goes to wallet (store separately)
#     if match.empty:
#         continue

#     # allocate to each sale row in same order
#     for idx, sale_row in match.iterrows():
#         sale_total = sale_row["Total"]

#         if bank_amount <= 0:
#             break

#         alloc = min(bank_amount, sale_total)

#         # Update sale row
#         sales.loc[idx, "Bank Amount Allocated"] += alloc

#         # Add the full bank row details
#         for c in bank_cols:
#             sales.loc[idx, "BANK_" + c] = bank_row[c]

#         # Reduce remaining amount
#         bank_amount -= alloc

#     # If leftover cannot be allocated → wallet entry added in last matched row
#     if bank_amount > 0:
#         last_idx = match.index[-1]
#         sales.loc[last_idx, "Wallet Amount"] += bank_amount

# # -----------------------------
# # Save final output
# # -----------------------------
# output_path = "/home/thrymr/Downloads/sales_with_bank_allocations.xlsx"
# sales.to_excel(output_path, index=False)

# print("Completed. File Saved:", output_path)


import pandas as pd

# -----------------------------
# Load your files
# -----------------------------
sales_path = "/home/thrymr/Downloads/sales.xlsx"
bank_path  = "/home/thrymr/Downloads/bank_agri_april.xlsx"

sales = pd.read_excel(sales_path)
bank  = pd.read_excel(bank_path)

# -----------------------------
# Clean and standardize columns
# -----------------------------
sales["Zoho Invoice"] = sales["Zoho Invoice"].astype(str).str.strip()
bank["Invoice Number"] = bank["Invoice Number"].astype(str).str.strip()

# Convert dates to date only
sales["Date"] = pd.to_datetime(sales["Date"]).dt.date
bank["Date"]  = pd.to_datetime(bank["Date"]).dt.date

# -----------------------------
# Add columns for allocation
# -----------------------------
sales["Bank Amount Allocated"] = 0.0
sales["Wallet Amount"] = 0.0

# Add bank column placeholders
bank_cols = list(bank.columns)
for c in bank_cols:
    sales["BANK_" + c] = None

# -----------------------------
# RULE 1: If Zoho Invoice is empty → send full Total to Wallet
# -----------------------------
empty_invoice_rows = sales[sales["Zoho Invoice"].isin(["", "nan", "None", None])]
for idx, row in empty_invoice_rows.iterrows():
    sales.loc[idx, "Wallet Amount"] = row["Total"]

# -----------------------------
# Allocation Logic
# -----------------------------
for _, bank_row in bank.iterrows():

    bank_amount = bank_row["Amount"]
    bank_invoice = bank_row["Invoice Number"]
    bank_date = bank_row["Date"]

    # Match by invoice AND date
    match = sales[
        (sales["Zoho Invoice"] == bank_invoice) &
        (sales["Date"] == bank_date)
    ]

    # No match → skip (wallet not updated here)
    if match.empty:
        continue

    # Allocate amount in order
    for idx, sale_row in match.iterrows():

        sale_total = sale_row["Total"]

        if bank_amount <= 0:
            break

        allocation = min(bank_amount, sale_total)

        # Bank allocation
        sales.loc[idx, "Bank Amount Allocated"] += allocation

        # Copy full bank metadata
        for c in bank_cols:
            sales.loc[idx, "BANK_" + c] = bank_row[c]

        # Reduce remaining bank balance
        bank_amount -= allocation

    # If leftover remains → move to wallet (on last matching row)
    if bank_amount > 0:
        last_idx = match.index[-1]
        sales.loc[last_idx, "Wallet Amount"] += bank_amount

# -----------------------------
# Save final output
# -----------------------------
output_path = "/home/thrymr/Downloads/sales_with_bank_allocations.xlsx"
sales.to_excel(output_path, index=False)

print("Completed. File Saved:", output_path)
