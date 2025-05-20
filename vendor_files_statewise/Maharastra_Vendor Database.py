import pandas as pd
import random

input_file = '/home/thrymr/Downloads/filtered_mod_maharashtra.xlsx'
additional_info_file = '/home/thrymr/Desktop/Statewise_customerdata/Maharashtra_original.xlsx'

df = pd.read_excel(input_file)
additional_info = pd.read_excel(additional_info_file)

selected_columns = df[['Mobile', 'Name']].copy()
selected_columns['District'] = None

districts = [
#     'AHMEDNAGAR', 'AKOLA', 'AMRAVATI', 'AURANGABAD', 'BEED', 'BULDHANA', 'CHANDRAPUR', 
#     'DHULE', 'GADCHIROLI', 'JALGAON', 'KOLHAPUR', 'LATUR', 'NAGPUR', 'NANDED', 'OSMANABAD','RAIGARH',
#    'RAIGARH(MH)', 'SATARA', 'SOLAPUR', 'THANE', 'KHED','MUMBAI','PUNE','RAIGARHMH','YAVATMAL'
'PATNA',
]

vertical_labels = ["AgriInputs", "MarketLinkages", "MarketIntervention", "FMCG", "WhiteLabel"]
all_districts_sample = pd.DataFrame()

for district in districts:
    if len(selected_columns) >= 125:
        num_rows = random.randint(125, 150)
        sampled_df = selected_columns.sample(n=min(num_rows, len(selected_columns)), replace=False)

        sampled_df['District'] = district
        sampled_df['State'] = 'MAHARASHTRA'

        sampled_df['Vertical'] = None
        for i, label in enumerate(vertical_labels):
            sampled_df.iloc[i * 25:(i + 1) * 25, sampled_df.columns.get_loc('Vertical')] = label

        remaining_rows = sampled_df[sampled_df['Vertical'].isnull()].index
        sampled_df.loc[remaining_rows, 'Vertical'] = random.choices(vertical_labels, k=len(remaining_rows))

        all_districts_sample = pd.concat([all_districts_sample, sampled_df], ignore_index=True)
        selected_columns = selected_columns.drop(sampled_df.index)

all_districts_sample['Address'] = None
all_districts_sample['Mandal'] = None
all_districts_sample['Pincode'] = None

additional_info = additional_info.dropna(subset=['Address'])

if not additional_info.empty:
    for district in districts:
        district_info = additional_info[
            (additional_info['District'] == district) &
            (additional_info['Address'].notna()) &
            (additional_info['Pincode'].notna())
        ]

        if not district_info.empty:
            district_addresses = district_info[['Address', 'Mandal', 'Pincode']].values
            num_addresses = len(district_addresses)

            district_rows = all_districts_sample[all_districts_sample['District'] == district].index

            for i, row_index in enumerate(district_rows):
                address_index = i % num_addresses  
                all_districts_sample.loc[row_index, ['Address', 'Mandal', 'Pincode']] = district_addresses[address_index]
        else:
            print(f"Warning: No valid address data found for district {district}")

all_districts_sample['Vendor ID'] = None
for district in districts:
    # Filter rows for the current district
    district_rows = all_districts_sample[all_districts_sample['District'] == district]
    
    # Group rows by vertical within the district
    vertical_groups = district_rows.groupby('Vertical')

    for vertical, group in vertical_groups:
        # Reset counter for each vertical
        count = 1

        # Assign VendorId for each row in the current vertical group
        for row_index in group.index:
            vendor_id = f"HS-VED-{district}-{vertical}-{count:04d}"
            all_districts_sample.loc[row_index, 'Vendor ID'] = vendor_id
            count += 1


output_file = '/home/thrymr/Downloads/new_vendor_databases/MAHARASCCCCHTRA.xlsx'
all_districts_sample.to_excel(output_file, index=False)

print("Random samples with unique VendorId for each district and vertical have been saved to the output file.")
