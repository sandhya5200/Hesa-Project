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
sales_path = r"c:\Users\ksand\Downloads\april_cons_cleaned_sale.xlsx"
bank_path  = r"c:\Users\ksand\Downloads\bank_cons_april.xlsx"

sales = pd.read_excel(sales_path)
bank  = pd.read_excel(bank_path)

# -----------------------------
# Clean invoice columns (NO nan strings)
# -----------------------------
sales["Zoho Invoice"] = sales["Zoho Invoice"].apply(
    lambda x: x.strip() if isinstance(x, str) else x
)

bank["Invoice Number"] = bank["Invoice Number"].apply(
    lambda x: x.strip() if isinstance(x, str) else x
)

# -----------------------------
# Add allocation columns
# -----------------------------
sales["Bank Amount Allocated"] = 0.0
sales["Wallet Amount"] = 0.0
sales["Allocation"] = "Wallet"   # default

# -----------------------------
# RULE 1: Empty Zoho Invoice → Wallet
# -----------------------------
empty_invoice_mask = sales["Zoho Invoice"].isna() | (sales["Zoho Invoice"] == "")

sales.loc[empty_invoice_mask, "Wallet Amount"] = sales.loc[empty_invoice_mask, "Total"]
sales.loc[empty_invoice_mask, "Allocation"] = "Wallet"

# -----------------------------
# Allocation Logic (MATCH ONLY ON INVOICE)
# -----------------------------
for _, bank_row in bank.iterrows():

    bank_amount = bank_row["Amount"]
    bank_invoice = bank_row["Invoice Number"]

    # Skip empty bank invoice
    if pd.isna(bank_invoice) or bank_invoice == "":
        continue

    # Match ONLY on invoice
    match = sales[sales["Zoho Invoice"] == bank_invoice]

    if match.empty:
        continue

    for idx, sale_row in match.iterrows():

        if bank_amount <= 0:
            break

        sale_total = sale_row["Total"]
        alloc = min(bank_amount, sale_total)

        # Allocate
        sales.loc[idx, "Bank Amount Allocated"] += alloc
        sales.loc[idx, "Allocation"] = "Bank"

        # Copy bank row values directly (no prefix)
        for col in bank.columns:
            if col not in sales.columns:
                sales[col] = None
            sales.loc[idx, col] = bank_row[col]

        bank_amount -= alloc

    # Leftover → Wallet
    if bank_amount > 0:
        last_idx = match.index[-1]
        sales.loc[last_idx, "Wallet Amount"] += bank_amount

# -----------------------------
# Final cleanup
# -----------------------------
sales["Zoho Invoice"] = sales["Zoho Invoice"].fillna("")

output_path = r"c:\Users\ksand\Downloads\sales_with_bank_details_cons_april.xlsx"
sales.to_excel(output_path, index=False)

print("Completed. File Saved:", output_path)
