#This code is used to make sure all the hesathis in the harish sent file has 55-70 in range customers
import pandas as pd
import random

# Load unmatched codes and zone details
unmatched_df = pd.read_excel('/home/thrymr/Downloads/important.xlsx')
zone_df = pd.read_excel('/home/thrymr/Downloads/zone_user_category_modified.xlsx')

# Define paths for each state
state_files = {
    'TELANGANA': '/home/thrymr/Desktop/vendors/sandhya/after creating 40k people used to make additional customerdatabase/cleaned_Telangana.xlsx',
    'BIHAR': '/home/thrymr/Desktop/vendors/sandhya/after creating 40k people used to make additional customerdatabase/cleaned_Bihar_mod.xlsx',
    'ANDHRA PRADESH': '/home/thrymr/Desktop/vendors/sandhya/after creating 40k people used to make additional customerdatabase/cleaned_AP.xlsx',
    'TAMIL NADU': '/home/thrymr/Desktop/vendors/sandhya/after creating 40k people used to make additional customerdatabase/cleaned_Tamilnadu_mod.xlsx',
    'ODISHA': '/home/thrymr/Desktop/vendors/sandhya/after creating 40k people used to make additional customerdatabase/cleaned_Odisha.xlsx',
    'HARYANA': "/home/thrymr/Desktop/vendors/sandhya/after creating 40k people used to make additional customerdatabase/cleaned_Haryana_mod.xlsx",
    'MAHARASHTRA': '/home/thrymr/Desktop/vendors/sandhya/after creating 40k people used to make additional customerdatabase/cleaned_Maharashtra.xlsx',
    'KARNATAKA': '/home/thrymr/Desktop/vendors/sandhya/after creating 40k people used to make additional customerdatabase/cleaned_Karnataka.xlsx'
}

# Load data for each state
state_dataframes = {state: pd.read_excel(file_path) for state, file_path in state_files.items()}

# Initialize output data list
output_data = []

# Process each unmatched code
for code in unmatched_df['Unmatched_codes']:
    match = zone_df[zone_df['CODE'] == code]
    
    if not match.empty:
        state = match.iloc[0]['State']
        month = match.iloc[0]['Month']
        district = match.iloc[0]['District']
        print(f"Processing Hesathi code {code} for State: {state}, District: {district}")

        # Get the state DataFrame
        state_df = state_dataframes.get(state.upper())
        
        if state_df is not None:
            # Filter customers in the same district
            district_customers = state_df[state_df['District'].str.upper() == district.upper()]

            # If not enough customers, fetch additional customers from other districts
            if len(district_customers) < 55:
                print(f"Not enough customers in {district}, fetching from other districts")
                required_customers = 55 - len(district_customers)
                
                # Select additional customers from other districts
                additional_customers = state_df[state_df['District'].str.upper() != district.upper()]
                
                # Limit to available rows if fewer than required
                required_customers = min(required_customers, len(additional_customers))
                
                # Sample additional customers
                additional_customers_sample = additional_customers.sample(n=required_customers, random_state=1)
                
                # Track the source district for additional customers
                additional_customers_sample['Source District'] = additional_customers_sample['District']
                
                # Concatenate district customers and additional customers
                district_customers = pd.concat([district_customers, additional_customers_sample])

            # Sample between 55 and 70 customers from the combined DataFrame
            sample_size = random.randint(55, 70)
            sample_size = min(sample_size, len(district_customers))
            district_customers = district_customers.sample(n=sample_size, random_state=1)

            # Append data to output and remove used rows
            for _, customer_row in district_customers.iterrows():
                # Track the district where each customer came from
                source_district = customer_row['Source District'] if 'Source District' in customer_row else district
                
                output_data.append({
                    'Hesathi code': code,
                    'State': state,
                    'Month': month,
                    'District': district,
                    'Source District': source_district,  # Source district for transparency
                    'Mobile': customer_row['Mobile'],
                    'Name': customer_row['Name'],
                    'Address': customer_row.get('Address', ""),
                    'Mandal': customer_row.get('Mandal', ""),
                    'Pincode': customer_row.get('Pincode', "")
                })

            # Remove selected customers from state DataFrame but keep the unselected rows
            state_dataframes[state.upper()] = state_df.loc[~state_df.index.isin(district_customers.index)]

        else:
            print(f"State file not found for {state}.")
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

# Save the final output file in chunks of 500,000 rows
output_df = pd.DataFrame(output_data)

# Calculate the number of chunks needed
num_chunks = len(output_df) // 500000 + (1 if len(output_df) % 500000 != 0 else 0)

# Save each chunk to a separate file
for i in range(num_chunks):
    start_row = i * 500000
    end_row = (i + 1) * 500000
    chunk_df = output_df.iloc[start_row:end_row]
    chunk_file_path = f'/home/thrymr/Downloads/file_part_{i+1}.xlsx'
    chunk_df.to_excel(chunk_file_path, index=False)
    print(f"Chunk {i+1} saved with rows {start_row} to {end_row - 1}.")

print("Task completed! Output files have been generated in chunks of 500,000 rows.")
