#This code will how many invoice numbers or delivery challan we have more than 30 products appended 
import pandas as pd

df = pd.read_excel('/home/thrymr/Downloads/ready_new_April_(23-24).xlsx')

if 'Delivery Challan' not in df.columns or 'Product Name' not in df.columns:
    raise ValueError("The required columns 'Delivery Challan' or 'Item' are not in the DataFrame.")

product_counts = df.groupby('Delivery Challan').size()
filtered_counts = product_counts[product_counts > 30]

unique_count = filtered_counts.count()

print(f"Number of unique Delivery Challan numbers with more than 25 products: {unique_count}")

if unique_count > 0:
    print("Delivery Challan numbers with more than 25 products:")
    print(filtered_counts)

    output_file = '/home/thrymr/Downloads/sandhyakonda.xlsx'
    filtered_counts.to_excel(output_file, sheet_name='Filtered_Challan_Counts', header=['Product Count'])
    print(f"The filtered counts have been saved to {output_file}")
else:
    print("No Delivery Challan numbers have more than 25 products.") 
    