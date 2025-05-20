#This code has been used to allot customers to hesaathis ,only to the hesaathis which are not in the Harish sent file  
import pandas as pd
import random

# Load input files
unmatched_df = pd.read_excel('/home/thrymr/Downloads/important.xlsx')
zone_df = pd.read_excel('/home/thrymr/Downloads/zone_user_category_modified.xlsx')

# Load state data files
state_files = {
    'TELANGANA': '/home/thrymr/Desktop/Statewise_customerdata/Telangana_new_final.xlsx',
    'BIHAR': '/home/thrymr/Desktop/Statewise_customerdata/Bihar_new_final.xlsx',
    'ANDHRA PRADESH': '/home/thrymr/Desktop/Statewise_customerdata/Andrapradesh_new_final.xlsx',
    'TAMIL NADU': '/home/thrymr/Desktop/Statewise_customerdata/Tamilnadu_new_final.xlsx',
    'ODISHA': '/home/thrymr/Desktop/Statewise_customerdata/Odissa_new_final.xlsx',
    'HARYANA': "/home/thrymr/Desktop/Statewise_customerdata/Haryana_new_final.xlsx",
    'MAHARASHTRA': '/home/thrymr/Desktop/Statewise_customerdata/Maharashtra_new_final.xlsx',
    'KARNATAKA': '/home/thrymr/Desktop/Statewise_customerdata/Karnataka_new_final.xlsx'
}
state_dataframes = {state: pd.read_excel(file_path) for state, file_path in state_files.items()}


# Initialize output data list
output_data = []

# Process each unmatched code
for _, row in unmatched_df.iterrows():
    code = row['Unmatched_codes']
    mod_count = row['Mod']  # Existing count from the Mod column
    
    match = zone_df[zone_df['CODE'] == code]
    
    if not match.empty:
        state = match.iloc[0]['State']
        month = match.iloc[0]['Month']
        district = match.iloc[0]['District']
        
        # Determine the number of additional customers needed
        target_count = random.randint(55, 70)
        additional_needed = target_count - mod_count
        
        # Get the state DataFrame
        state_df = state_dataframes.get(state.upper())
        
        if state_df is not None and additional_needed > 0:
            # Filter customers in the same district
            district_customers = state_df[state_df['District'].str.upper() == district.upper()]
            
            # If not enough customers, fetch additional customers from other districts
            if len(district_customers) < additional_needed:
                required_customers = additional_needed - len(district_customers)
                
                # Fetch additional customers from other districts
                additional_customers = state_df[state_df['District'].str.upper() != district.upper()]
                additional_customers_sample = additional_customers.sample(n=required_customers, random_state=1)
                
                # Track the source district for additional customers
                additional_customers_sample['Source District'] = additional_customers_sample['District']
                
                # Combine district and additional customers
                district_customers = pd.concat([district_customers, additional_customers_sample])
            
            # Sample only the required number of additional customers
            district_customers = district_customers.sample(n=additional_needed, random_state=1)
            
            
            # Append data to output
            for _, customer_row in district_customers.iterrows():
                source_district = customer_row['Source District'] if 'Source District' in customer_row else district
                
                output_data.append({
                    'Hesathi code': code,
                    'State': state,
                    'Month': month,
                    'District': district,
                    'Source District': source_district,
                    'Mobile': customer_row['Mobile'],
                    'Name': customer_row['Name'],
                    'Address': customer_row.get('Address', ""),
                    'Mandal': customer_row.get('Mandal', ""),
                    'Pincode': customer_row.get('Pincode', "")
                })

            state_dataframes[state.upper()] = state_df.loc[~state_df.index.isin(district_customers.index)]
        else:
            # If no state data or additional customers not needed, indicate this in the output
            output_data.append({
                'Hesathi code': code,
                'State': state,
                'Month': month,
                'District': district,
                'Source District': "N/A",
                'Mobile': None,
                'Name': None,
                'Address': "",
                'Mandal': "",
                'Pincode': ""
            })

# Save updated state DataFrames back to Excel files
for state, updated_df in state_dataframes.items():
    state_file_path = state_files.get(state)
    if state_file_path:
        updated_df.to_excel(state_file_path, index=False)

# Save output data to Excel
output_df = pd.DataFrame(output_data)

# Split into chunks of 500,000 rows if needed
num_chunks = len(output_df) // 500000 + (1 if len(output_df) % 500000 != 0 else 0)
for i in range(num_chunks):
    start_row = i * 500000
    end_row = (i + 1) * 500000
    chunk_df = output_df.iloc[start_row:end_row]
    chunk_file_path = f'/home/thrymr/Downloads/additional_customer_database{i+1}.xlsx'
    chunk_df.to_excel(chunk_file_path, index=False)
    print(f"Chunk {i+1} saved with rows {start_row} to {end_row - 1}.")

print("Task completed! Output files have been generated in chunks of 500,000 rows.")