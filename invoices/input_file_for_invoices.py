#this code is to get the invoice number from the sales file to delivery challan file 

import pandas as pd
import re

invoice_sales = pd.read_excel('/home/thrymr/Downloads/Jan-Mar(2022-23)sales file.xlsx')#, sheet_name="Main sheet")        #sales
invoices_tds = pd.read_excel('/home/thrymr/Downloads/Delivery_challan_input_Jan-Mar(2022-23).xlsx')   #tds

print("Invoice Sales Data:\n", invoice_sales.head())
print("Invoices TDS Data:\n", invoices_tds.head())

# Function to extract the Delivery Challan number
def extract_delivery_challan(invoice_no):
    match = re.search(r'HS-INV-(?:CG|AG)-(\d{2})-\d{2}-(\d{6})', invoice_no)
    if match:
        month = match.group(1)
        last_six = match.group(2)
        return f"DC-{month}-{last_six}"
    return None

# Apply the function to extract Delivery Challan numbers
invoice_sales['Delivery Challan'] = invoice_sales['Invoice no.'].apply(extract_delivery_challan)

print("Extracted Delivery Challan:\n", invoice_sales[['Invoice no.', 'Delivery Challan']].head())

# Remove duplicate Delivery Challan entries from invoice_sales, keeping the first instance only
invoice_sales_unique = invoice_sales.drop_duplicates(subset=['Delivery Challan'])

# Perform the merge to bring Invoice no. into invoices_tds
merged_df = invoices_tds.merge(invoice_sales_unique[['Invoice no.', 'Delivery Challan']], 
                               on='Delivery Challan', 
                               how='left')

# Update invoices_tds with the Invoice No.
invoices_tds['Invoice No.'] = merged_df['Invoice no.']

# Reorder the columns to place 'Invoice No.' at the third position
cols = list(invoices_tds.columns)
if 'Invoice No.' in cols:
    cols.insert(2, cols.pop(cols.index('Invoice No.')))
invoices_tds = invoices_tds[cols]

# Save the updated file
invoices_tds.to_excel('/home/thrymr/Desktop/Input Files(2022-23)/input_for_invoices_Jan-Mar_(2022-23).xlsx', index=False)
print("The updated invoices_tds file has been saved.")

