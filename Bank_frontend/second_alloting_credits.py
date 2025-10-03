# import pandas as pd

# # ---- Input files ----
# sales_file = "/home/thrymr/Downloads/invoice_summary.xlsx"
# agri_credits_file = "/home/thrymr/Downloads/agri_credits.xlsx"
# cons_credits_file = "/home/thrymr/Downloads/cons_credits.xlsx"

# # ---- Output file ----
# output_file = "/home/thrymr/Downloads/invoice_summary_matched.xlsx"

# # ---------------------------
# # Load files
# # ---------------------------
# sales_df = pd.read_excel(sales_file)
# agri_credits_df = pd.read_excel(agri_credits_file)
# cons_credits_df = pd.read_excel(cons_credits_file)

# # Standardize date formats
# sales_df['Date'] = pd.to_datetime(sales_df['Date']).dt.date
# agri_credits_df['DATE'] = pd.to_datetime(agri_credits_df['DATE'], dayfirst=True).dt.date
# cons_credits_df['DATE'] = pd.to_datetime(cons_credits_df['DATE'], dayfirst=True).dt.date

# # ---------------------------
# # Function to allocate credits
# # ---------------------------
# def allocate_credits(sales, credits, facilitator_name):
#     sales = sales.copy()
#     sales = sales[sales['Facilitator'] == facilitator_name].copy()
    
#     # Initialize columns
#     for col in ['DATE', 'DESCRIPTION', 'REFERENCE NO.', 'AMOUNT', 'BANK', 'reference amount', 'wallet', 'status']:
#         sales[col] = None
    
#     credits = credits.sort_values('DATE')
    
#     for idx, credit in credits.iterrows():
#         credit_amount = credit['AMOUNT']
#         txn_date = credit['DATE']
#         txn_desc = credit.get('DESCRIPTION', '')
#         txn_ref = credit.get('REFERENCE NO.', '')
#         txn_bank = credit.get('BANK', '')
        
#         # Get sales invoices on same date
#         invoices_today = sales[(sales['Date'] == txn_date) & (sales['status'].isna())]
        
#         while credit_amount > 0 and not invoices_today.empty:
#             # Find invoices that can fully fit in remaining credit
#             matched_invoice = invoices_today[invoices_today['Invoice Total'] <= credit_amount]
            
#             if matched_invoice.empty:
#                 # Cannot fully allocate remaining credit to any invoice, break
#                 break
            
#             # Take the first invoice that fits
#             inv_idx = matched_invoice.index[0]
#             inv_total = sales.at[inv_idx, 'Invoice Total']
            
#             # Allocate invoice
#             # Allocate invoice
#             sales.at[inv_idx, 'DATE'] = txn_date
#             sales.at[inv_idx, 'DESCRIPTION'] = txn_desc
#             sales.at[inv_idx, 'REFERENCE NO.'] = txn_ref
#             sales.at[inv_idx, 'AMOUNT'] = credit['AMOUNT']        # <- bank txn amount
#             sales.at[inv_idx, 'BANK'] = txn_bank
#             sales.at[inv_idx, 'reference amount'] = inv_total    # <- invoice total
#             sales.at[inv_idx, 'wallet'] = 0
#             sales.at[inv_idx, 'status'] = 'paid'

            
#             # Reduce credit_amount
#             credit_amount -= inv_total
            
#             # Refresh today's invoices
#             invoices_today = sales[(sales['Date'] == txn_date) & (sales['status'].isna())]
        
#         # Any leftover credit that could not fully match invoices goes to wallet
#         if credit_amount > 0:
#             # Append to the last invoice row for that facilitator or leave separate row
#             # Here, we append to the last allocated invoice
#             last_paid_idx = sales[sales['status']=='paid'].index[-1]
#             sales.at[last_paid_idx, 'wallet'] = credit_amount
    
#     return sales

# # ---------------------------
# # Allocate for Agri
# # ---------------------------
# agri_allocated = allocate_credits(sales_df, agri_credits_df, 'Hesa Agritech Private Limited')

# # ---------------------------
# # Allocate for Consumer
# # ---------------------------
# cons_allocated = allocate_credits(sales_df, cons_credits_df, 'Hesa Consumer Products Private Limited')

# # ---------------------------
# # Merge allocations back to original sales
# # ---------------------------
# final_allocations = pd.concat([agri_allocated, cons_allocated])

# # Merge allocated columns with original sales_df
# cols_to_merge = ['Sl No','DATE','DESCRIPTION','REFERENCE NO.','AMOUNT','BANK','reference amount','wallet','status']
# final_sales = sales_df.merge(final_allocations[cols_to_merge], on='Sl No', how='left')

# # ---------------------------
# # Fill empty wallet with invoice total for unallocated rows
# # ---------------------------
# final_sales['wallet'] = final_sales['wallet'].fillna(final_sales['Invoice Total'])

# # ---------------------------
# # Save output
# # ---------------------------
# final_sales.to_excel(output_file, index=False)
# print(f"✅ Allocation complete. Output saved as: {output_file}")


import pandas as pd

# ---- Input files ----
sales_file = "/home/thrymr/Downloads/MARCH_invoice_summary.xlsx"
agri_credits_file = "/home/thrymr/Downloads/agri_credits.xlsx"
cons_credits_file = "/home/thrymr/Downloads/cons_credits.xlsx"

# ---- Output files ----
output_file = "/home/thrymr/Downloads/March_invoice_summary_matched.xlsx"
agri_output_file = "/home/thrymr/Downloads/agri_credits_with_invoices.xlsx"
cons_output_file = "/home/thrymr/Downloads/cons_credits_with_invoices.xlsx"

# ---------------------------
# Load files
# ---------------------------
sales_df = pd.read_excel(sales_file)
agri_credits_df = pd.read_excel(agri_credits_file)
cons_credits_df = pd.read_excel(cons_credits_file)

# Standardize date formats
sales_df['Date'] = pd.to_datetime(sales_df['Date']).dt.date
agri_credits_df['DATE'] = pd.to_datetime(agri_credits_df['DATE'], dayfirst=True).dt.date
cons_credits_df['DATE'] = pd.to_datetime(cons_credits_df['DATE'], dayfirst=True).dt.date

# ---------------------------
# Function to allocate credits
# ---------------------------
def allocate_credits(sales, credits, facilitator_name):
    sales = sales.copy()
    sales = sales[sales['Facilitator'] == facilitator_name].copy()
    
    # Initialize columns
    for col in ['DATE', 'DESCRIPTION', 'REFERENCE NO.', 'AMOUNT', 'BANK', 
                'reference amount', 'wallet', 'status']:
        sales[col] = None
    
    credits = credits.sort_values('DATE').copy()
    credits['Invoices'] = ""   # new column to hold allocated invoices
    
    for idx, credit in credits.iterrows():
        credit_amount = credit['AMOUNT']
        txn_date = credit['DATE']
        txn_desc = credit.get('DESCRIPTION', '')
        txn_ref = credit.get('REFERENCE NO.', '')
        txn_bank = credit.get('BANK', '')
        
        invoices_today = sales[(sales['Date'] == txn_date) & (sales['status'].isna())]
        
        allocated_invoices = []
        
        while credit_amount > 0 and not invoices_today.empty:
            matched_invoice = invoices_today[invoices_today['Invoice Total'] <= credit_amount]
            
            if matched_invoice.empty:
                break
            
            inv_idx = matched_invoice.index[0]
            inv_total = sales.at[inv_idx, 'Invoice Total']
            inv_number = sales.at[inv_idx, 'Invoice No']
            
            # Allocate invoice
            sales.at[inv_idx, 'DATE'] = txn_date
            sales.at[inv_idx, 'DESCRIPTION'] = txn_desc
            sales.at[inv_idx, 'REFERENCE NO.'] = txn_ref
            sales.at[inv_idx, 'AMOUNT'] = credit['AMOUNT']  # txn amount
            sales.at[inv_idx, 'BANK'] = txn_bank
            sales.at[inv_idx, 'reference amount'] = inv_total
            sales.at[inv_idx, 'wallet'] = 0
            sales.at[inv_idx, 'status'] = 'paid'
            
            # Track invoice allocation in bank file
            allocated_invoices.append(inv_number)
            
            credit_amount -= inv_total
            invoices_today = sales[(sales['Date'] == txn_date) & (sales['status'].isna())]
        
        # Any leftover → wallet
        if credit_amount > 0 and len(sales[sales['status']=='paid']) > 0:
            last_paid_idx = sales[sales['status']=='paid'].index[-1]
            sales.at[last_paid_idx, 'wallet'] = credit_amount
        
        # Update invoices back to credits row
        if allocated_invoices:
            credits.at[idx, 'Invoices'] = ",".join(map(str, allocated_invoices))
    
    return sales, credits

# ---------------------------
# Allocate for Agri
# ---------------------------
agri_allocated, agri_credits_with_invoices = allocate_credits(
    sales_df, agri_credits_df, 'Hesa Agritech Private Limited'
)

# ---------------------------
# Allocate for Consumer
# ---------------------------
cons_allocated, cons_credits_with_invoices = allocate_credits(
    sales_df, cons_credits_df, 'Hesa Consumer Products Private Limited'
)

# ---------------------------
# Merge allocations back to original sales
# ---------------------------
final_allocations = pd.concat([agri_allocated, cons_allocated])
cols_to_merge = ['Sl No','DATE','DESCRIPTION','REFERENCE NO.','AMOUNT','BANK',
                 'reference amount','wallet','status']
final_sales = sales_df.merge(final_allocations[cols_to_merge], on='Sl No', how='left')

# Fill empty wallet with invoice total for unallocated rows
final_sales['wallet'] = final_sales['wallet'].fillna(final_sales['Invoice Total'])

# ---------------------------
# Save outputs
# ---------------------------
final_sales.to_excel(output_file, index=False)
agri_credits_with_invoices.to_excel(agri_output_file, index=False)
cons_credits_with_invoices.to_excel(cons_output_file, index=False)

print(f"✅ Allocation complete.")
print(f"   Sales output   → {output_file}")
print(f"   Agri bank file → {agri_output_file}")
print(f"   Cons bank file → {cons_output_file}")
