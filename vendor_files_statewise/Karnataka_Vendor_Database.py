import pandas as pd
import random

# Your existing code
input_file = '/home/thrymr/Downloads/filtered_mod_karnataka.xlsx'
additional_info_file = '/home/thrymr/Desktop/Statewise_customerdata/Karnataka_original.xlsx'

df = pd.read_excel(input_file)
additional_info = pd.read_excel(additional_info_file)

selected_columns = df[['Mobile', 'Name']].copy()
selected_columns['District'] = None

districts = [
    'BAGALKOT', 'BANGALORE', 'BANGALORE RURAL', 'BELGAUM', 'BELLARY', 'BIDAR', 'BIJAPUR', 'CHAMRAJNAGAR', 'CHICKMAGALUR',
    'CHICKKABALLAPUR', 'CHITRADURGA', 'DAKSHINA KANNADA', 
    'DAVANGARE', 'DHARWARD', 'GADAG', 'GULBARGA', 'HASSAN', 'HAVERI', 'KOLAR', 'KOPPAL', 'MANDHYA', 'Mysuru', 'RAICHUR', 'RAMANAGAR', 'SHIMOGA', 'TUMKUR', 'UDUPI', 'UTTARA KANNADA'
]

vertical_labels = ["Agri Inputs", "Market Linkages", "Market Intervention", "FMCG", "White Label"]
all_districts_sample = pd.DataFrame()

# Pincode mapping based on district
district_pincode_mapping = {
    'BAGALKOT': ['587101', '587102', '587103'],
    'BANGALORE': ['560001', '560002', '560003'],
    'BANGALORE RURAL': ['562110', '562111', '562123'],
    'BELGAUM': ['590001', '590002', '591101'],
    'BELLARY': ['583101', '583102', '583201'],
    'BIDAR': ['585401', '585402', '585403'],
    'BIJAPUR': ['586101', '586102', '586103'],
    'CHAMRAJNAGAR': ['571313', '571127', '571441'],
    'CHICKMAGALUR': ['577101', '577102', '577111'],
    'CHICKKABALLAPUR': ['562101', '562102', '562103'],
    'CHITRADURGA': ['577501', '577502', '577503'],
    'DAKSHINA KANNADA': ['575001', '575002', '574001'],
    'DAVANGARE': ['577001', '577002', '577003'],
    'DHARWARD': ['580001', '580002', '580003'],
    'GADAG': ['582101', '582102', '582103'],
    'GULBARGA': ['585101', '585102', '585103'],
    'HASSAN': ['573201', '573202', '573211'],
    'HAVERI': ['581110', '581115', '581120'],
    'KOLAR': ['563101', '563102', '563103'],
    'KOPPAL': ['583231', '583232', '583233'],
    'MANDHYA': ['571401', '571402', '571403'],
    'Mysuru': ['570001', '570002', '570003'],
    'RAICHUR': ['584101', '584102', '584103'],
    'RAMANAGAR': ['562159', '562160', '562159'],
    'SHIMOGA': ['577201', '577202', '577203'],
    'TUMKUR': ['572101', '572102', '572103'],
    'UDUPI': ['576101', '576102', '576103'],
    'UTTARA KANNADA': ['581301', '581302', '581303']
}

# Generate all samples with district and vertical labels
for district in districts:
    if len(selected_columns) >= 75:
        num_rows = random.randint(75, 90)
        sampled_df = selected_columns.sample(n=min(num_rows, len(selected_columns)), replace=False)

        sampled_df['District'] = district
        sampled_df['State'] = 'KARNATAKA'

        sampled_df['Vertical'] = None
        for i, label in enumerate(vertical_labels):
            sampled_df.iloc[i * 15:(i + 1) * 15, sampled_df.columns.get_loc('Vertical')] = label

        remaining_rows = sampled_df[sampled_df['Vertical'].isnull()].index
        sampled_df.loc[remaining_rows, 'Vertical'] = random.choices(vertical_labels, k=len(remaining_rows))

        # Assign Pincode randomly based on District
        sampled_df['Pincode'] = sampled_df['District'].map(lambda district: random.choice(district_pincode_mapping[district]))

        all_districts_sample = pd.concat([all_districts_sample, sampled_df], ignore_index=True)
        selected_columns = selected_columns.drop(sampled_df.index)

# Assign addresses from additional_info
all_districts_sample['Address'] = None
all_districts_sample['Mandal'] = None

additional_info = additional_info.dropna(subset=['Address'])

fallback_districts = {
    'RAICHUR': 'GULBARGA',
    'BAGALKOT': 'HASSAN',
    'BANGALORE RURAL': "BANGALORE"
}

if not additional_info.empty:
    for district in districts:
        # Get the primary district info
        district_info = additional_info[
            (additional_info['District'] == district) &
            (additional_info['Address'].notna())
        ]

        # Check if the district has no valid address data and fallback is available
        if district_info.empty and district in fallback_districts:
            fallback_district = fallback_districts[district]
            district_info = additional_info[
                (additional_info['District'] == fallback_district) &
                (additional_info['Address'].notna())
            ]
            print(f"Using addresses from {fallback_district} for {district}")

        # Proceed with assigning addresses if data is available
        if not district_info.empty:
            district_addresses = district_info[['Address', 'Mandal']].values
            num_addresses = len(district_addresses)

            district_rows = all_districts_sample[all_districts_sample['District'] == district].index

            for i, row_index in enumerate(district_rows):
                address_index = i % num_addresses  
                all_districts_sample.loc[row_index, ['Address', 'Mandal']] = district_addresses[address_index]
        else:
            print(f"Warning: No valid address data found for district {district}")

# Assign VendorId
all_districts_sample['VendorId'] = None
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
            all_districts_sample.loc[row_index, 'VendorId'] = vendor_id
            count += 1

# Output to Excel
output_file = '/home/thrymr/Downloads/Karnataka_Vendor_Database.xlsx'
all_districts_sample.to_excel(output_file, index=False)

print("Random samples with unique VendorId for each district and vertical, and Pincode assigned have been saved to the output file.")
