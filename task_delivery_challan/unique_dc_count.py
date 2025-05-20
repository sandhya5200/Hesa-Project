#To know the count of unique delivery challan numbers just to know how many papers will be there in pdf

import pandas as pd
file_path = '/home/thrymr/Downloads/ready_new_April_(23-24).xlsx'  
df = pd.read_excel(file_path)
unique_challan_count = df['Invoice no.'].nunique()
print("Count of unique delivery challans:", unique_challan_count)
