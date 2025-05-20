import pandas as pd


def get_customer_details(state, district, state_df):
    # Check if district is a string
    if not isinstance(district, str):
        return '', '', '', '', '', '', ''
    
    # Convert to lowercase for case-insensitive comparison
    district = district.strip().lower()
    
    # Filter by district and match case-insensitively
    filtered_df = state_df[state_df['District'].str.lower() == district]
    
    if not filtered_df.empty:
        # Select a random row from the filtered results
        random_row = filtered_df.sample(n=1)
        
        return random_row.iloc[0][['Name', 'Mobile', 'Address', 'Pincode', 'Mandal', 'District', 'State']]
    else:
        # If district not found, select any random row from the state_df
        return state_df.sample(n=1).iloc[0][['Name', 'Mobile', 'Address', 'Pincode', 'Mandal', 'District', 'State']]


# Read your DataFrames
df = pd.read_excel('/home/thrymr/Downloads/december(23-24).xlsx')
maharashtra_df = pd.read_excel('/home/thrymr/Desktop/Statewise_customerdata/Maharashtra_dummy.xlsx')
telangana_df = pd.read_excel('/home/thrymr/Desktop/Statewise_customerdata/Telangana_dummy.xlsx')
haryana_df = pd.read_excel('/home/thrymr/Desktop/Statewise_customerdata/Haryana_dummy.xlsx')

# Filter rows with "HESA-HO-SL" in "Hesaathi Code"
filtered_df = df[df['Hesaathi Code'] == "HESA-HO-SL"]

# Initialize a list to keep track of rows with missing district matches
missing_districts = []

# Print initial status
print(f"Found {len(filtered_df)} rows with 'HESA-HO-SL' in 'Hesaathi Code'.")

# Iterate over filtered rows
for index, row in filtered_df.iterrows():
    state = row['State']
    district = row['District']
    
    print(f"Processing row {index + 1}: State = {state}, District = {district}")

    # Determine which state-specific file to use based on the state
    if state.lower() == 'maharashtra':
        name, mobile, address, pincode, mandal, district, state = get_customer_details(state, district, maharashtra_df)
    elif state.lower() == 'telangana':
        name, mobile, address, pincode, mandal, district, state = get_customer_details(state, district, telangana_df)
    elif state.lower() == 'haryana':
        name, mobile, address, pincode, mandal, district, state = get_customer_details(state, district, haryana_df)
    else:
        # If state is not in any of the three, set to empty
        name, mobile, address, pincode, mandal, district, state = '', '', '', '', '', '', ''
    
    # If no matching district was found, log the row index
    if not name or not mobile:
        missing_districts.append((index, district, state))
    
    # Update the DataFrame with the fetched details
    df.at[index, 'Customer Name'] = name
    df.at[index, 'Mobile'] = mobile
    df.at[index, 'Customer Address'] = address
    df.at[index, 'Mandal'] = mandal
    df.at[index, 'Pincode'] = pincode
    df.at[index, 'Customer District'] = district
    df.at[index, 'Customer State'] = state

    print(f"Updated row {index + 1}: Customer Name = {name}, Mobile = {mobile}, Address = {address}, Mandal = {mandal}, Pincode = {pincode}, District = {district}, State = {state}")

output_file = '/home/thrymr/Downloads/check_december_(23-24).xlsx'
df.to_excel(output_file, index=False)