import pandas as pd

file1 = "/home/thrymr/Downloads/sales file with customer data 24-25(oct-mar)/March_2025_Sales_Data-2_Sheet1.xlsx"
file2 = "/home/thrymr/Downloads/sales file with customer data 24-25(oct-mar)/March_2025_Sales_Data-2_Sheet2.xlsx"
file3 = "/home/thrymr/Downloads/sales file with customer data 24-25(oct-mar)/March_2025_Sales_Data-2_Sheet3.xlsx"

df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)
df3 = pd.read_excel(file3)
df = pd.concat([df1, df2, df3], ignore_index=True)

first_info = df.groupby("Invoice No").first().reset_index()
totals = df.groupby("Invoice No", as_index=False)["Sub total"].sum().rename(columns={"Sub total": "Invoice Total"})
summary = pd.merge(first_info, totals, on="Invoice No", how="inner")
summary = summary[[
    "Date", "Hesaathi Code", "CustomerID", "Customer State", "CustomerDistrict",
    "Facilitator", "Vertical", "Order_Id", "Invoice No", "Invoice Total"
]]

summary.insert(0, "Sl No", range(1, len(summary) + 1))

print(f"✅ Invoice summary created in memory")

agri_credits_file = "/home/thrymr/Downloads/agri_credits.xlsx"
cons_credits_file = "/home/thrymr/Downloads/cons_credits.xlsx"

output_file = "/home/thrymr/Downloads/March_invoice_summary_matched.xlsx"
agri_output_file = "/home/thrymr/Downloads/agri_credits_with_invoices.xlsx"
cons_output_file = "/home/thrymr/Downloads/cons_credits_with_invoices.xlsx"

agri_credits_df = pd.read_excel(agri_credits_file)
cons_credits_df = pd.read_excel(cons_credits_file)

sales_df = summary.copy()

sales_df['Date'] = pd.to_datetime(sales_df['Date']).dt.date
agri_credits_df['DATE'] = pd.to_datetime(agri_credits_df['DATE'], dayfirst=True).dt.date
cons_credits_df['DATE'] = pd.to_datetime(cons_credits_df['DATE'], dayfirst=True).dt.date

def allocate_credits(sales, credits, facilitator_name):
    sales = sales.copy()
    sales = sales[sales['Facilitator'] == facilitator_name].copy()
    
    for col in ['DATE', 'DESCRIPTION', 'REFERENCE NO.', 'AMOUNT', 'BANK', 
                'reference amount', 'wallet', 'status']:
        sales[col] = None
    
    credits = credits.sort_values('DATE').copy()
    credits['Invoices'] = ""   
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
            
            sales.at[inv_idx, 'DATE'] = txn_date
            sales.at[inv_idx, 'DESCRIPTION'] = txn_desc
            sales.at[inv_idx, 'REFERENCE NO.'] = txn_ref
            sales.at[inv_idx, 'AMOUNT'] = credit['AMOUNT'] 
            sales.at[inv_idx, 'BANK'] = txn_bank
            sales.at[inv_idx, 'reference amount'] = inv_total
            sales.at[inv_idx, 'wallet'] = 0
            sales.at[inv_idx, 'status'] = 'paid'
            
            allocated_invoices.append(inv_number)
            
            credit_amount -= inv_total
            invoices_today = sales[(sales['Date'] == txn_date) & (sales['status'].isna())]
        
        if credit_amount > 0 and len(sales[sales['status']=='paid']) > 0:
            last_paid_idx = sales[sales['status']=='paid'].index[-1]
            sales.at[last_paid_idx, 'wallet'] = credit_amount
        
        if allocated_invoices:
            credits.at[idx, 'Invoices'] = ",".join(map(str, allocated_invoices))
    
    return sales, credits

agri_allocated, agri_credits_with_invoices = allocate_credits(
    sales_df, agri_credits_df, 'Hesa Agritech Private Limited'
)

cons_allocated, cons_credits_with_invoices = allocate_credits(
    sales_df, cons_credits_df, 'Hesa Consumer Products Private Limited'
)

final_allocations = pd.concat([agri_allocated, cons_allocated])
cols_to_merge = ['Sl No','DATE','DESCRIPTION','REFERENCE NO.','AMOUNT','BANK',
                 'reference amount','wallet','status']
final_sales = sales_df.merge(final_allocations[cols_to_merge], on='Sl No', how='left')

final_sales['wallet'] = final_sales['wallet'].fillna(final_sales['Invoice Total'])

final_sales.to_excel(output_file, index=False)
agri_credits_with_invoices.to_excel(agri_output_file, index=False)
cons_credits_with_invoices.to_excel(cons_output_file, index=False)

print(f"\n✅ Allocation complete.")
print(f"   Sales output   → {output_file}")
print(f"   Agri bank file → {agri_output_file}")
print(f"   Cons bank file → {cons_output_file}")