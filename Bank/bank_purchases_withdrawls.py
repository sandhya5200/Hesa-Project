import pandas as pd

sales_df = pd.read_excel("/home/thrymr/Desktop/bank_purchases(22-23)/Purc Mar 23.xlsx", sheet_name="Purchases Mar 23")
deposits_df = pd.read_excel("/home/thrymr/Desktop/bank_purchases(22-23)/Purc Mar 23.xlsx", sheet_name="Withdrawals")

columns_to_extract = [
    "SRID", "BDID", "Date", "Mode", "DepositTo", "ReferenceNumber",
    "InvoiceNumber", "InvoiceAmount", "PayerAmount", "CreatedDate",
    "OrderId", "InvoiceNumber", "AmountReceived1"
]

sales_df.sort_values(by=["PO Number", "Total"], ascending=[True, True], inplace=True)

deposits_df.sort_values(by=["InvoiceNumber", "InvoiceAmount"], ascending=[True, True], inplace=True)

for col in columns_to_extract:
    if col not in sales_df.columns:
        sales_df[col] = None

def allocate_deposits_fifo(invoice_no, sales_group):
    deposit_rows = deposits_df[deposits_df["InvoiceNumber"] == invoice_no]
    deposit_rows = deposit_rows.sort_values(by="CreatedDate")  
    remaining_deposits = deposit_rows.copy()
    
    for idx, row in sales_group.iterrows():
        if not deposit_rows.empty:
            deposit_data = deposit_rows.iloc[0]
            deposit_rows = deposit_rows.iloc[1:]
            remaining_deposits = deposit_rows.copy()
            for col in columns_to_extract:
                if col != "Date":
                    sales_df.at[idx, col] = deposit_data[col]
    
    return remaining_deposits

for invoice_no, group in sales_df.groupby("PO Number"):
    sales_rows = len(group)
    deposit_rows = len(deposits_df[deposits_df["InvoiceNumber"] == invoice_no])
    
    if sales_rows > deposit_rows:
        remaining_deposits = allocate_deposits_fifo(invoice_no, group)
    elif sales_rows < deposit_rows:
        remaining_deposits = allocate_deposits_fifo(invoice_no, group)
        
        if not remaining_deposits.empty:
            empty_row_index = group.index[-1]
            total_invoice_amount = remaining_deposits["InvoiceAmount"].sum()
            sales_df.at[empty_row_index, "InvoiceAmount"] += total_invoice_amount if pd.notna(sales_df.at[empty_row_index, "InvoiceAmount"]) else total_invoice_amount
            
            for col in columns_to_extract:
                if col != "InvoiceAmount" and col != "Date":
                    existing_value = sales_df.at[empty_row_index, col]
                    new_value = ", ".join(remaining_deposits[col].astype(str).dropna())
                    sales_df.at[empty_row_index, col] = f"{existing_value}, {new_value}" if pd.notna(existing_value) else new_value
    elif sales_rows == deposit_rows:
        matching_deposits = deposits_df[deposits_df["InvoiceNumber"] == invoice_no]
        for idx, (s_idx, d_idx) in enumerate(zip(group.index, matching_deposits.index)):
            for col in columns_to_extract:
                if col != "Date":
                    sales_df.at[s_idx, col] = matching_deposits.at[d_idx, col]

if "Total" not in sales_df.columns:
    raise ValueError("Column 'Total' not found in sales file. Please check the column name.")

grouped_totals = sales_df.groupby("PO Number").agg({"Total": "sum", "InvoiceAmount": "sum"}).reset_index()

total_dict = dict(zip(grouped_totals["PO Number"], grouped_totals["Total"]))
invoice_amount_dict = dict(zip(grouped_totals["PO Number"], grouped_totals["InvoiceAmount"]))

sales_df["Wallet"] = None 

for invoice_no, group in sales_df.groupby("PO Number"):
    total_sum = total_dict[invoice_no]
    invoice_amount_sum = group["InvoiceAmount"].sum()
    wallet_value = total_sum - invoice_amount_sum
    last_index = group.index[-1]
    sales_df.at[last_index, "Wallet"] = wallet_value

unmatched_invoices = sales_df.groupby("PO Number").apply(lambda group: group["InvoiceAmount"].isna().all()).reset_index(name="Unmatched")
unmatched_invoices = unmatched_invoices[unmatched_invoices["Unmatched"]]["PO Number"].unique()
unmatched_df = pd.DataFrame({"unmatched invoices": unmatched_invoices})
unmatched_df.to_excel("/home/thrymr/Downloads/unmatched_purchases_Mar.xlsx", index=False)

sales_df["CreatedDate"].fillna(sales_df["Date"], inplace=True)
sales_df.rename(columns={"CreatedDate": "Transaction Date"}, inplace=True)

sales_df["Hesaathi Excess Credit"] = 0
negative_wallet_mask = sales_df["Wallet"] < 0
sales_df.loc[negative_wallet_mask, "Hesaathi Excess Credit"] = abs(sales_df.loc[negative_wallet_mask, "Wallet"])
sales_df.loc[negative_wallet_mask, "Wallet"] = 0

sales_df.to_excel("/home/thrymr/Downloads/withdrawls_purchases_Mar(22-23).xlsx", index=False)

used_invoices = sales_df["PO Number"].dropna().unique()
used_deposits_df = deposits_df[deposits_df["InvoiceNumber"].isin(used_invoices)]
unused_deposits_df = deposits_df.loc[~deposits_df.index.isin(used_deposits_df.index)]
unused_deposits_df.to_excel("/home/thrymr/Downloads/unused_withdrawls_Mar.xlsx", index=False)

print("Matched content is found")
print("The resolving content has been found")
print("Unused deposit entries have been saved.")
