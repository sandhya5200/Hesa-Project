import pandas as pd

# Load input file
input_df = pd.read_excel("/home/thrymr/Desktop/purchases(2024-25)/Hesa Agritech Private Limited/Agri Purchase Sep-24.xlsx")  # Change to .csv if needed

input_df['vendor_id_norm'] = input_df['Vendor_Id'].astype(str).str.lower().str.replace(" ", "")
input_df['vendor_state_norm'] = input_df['Vendor_State'].astype(str).str.lower().str.replace(" ", "")

# State files mapping
state_files = {
    "andhrapradesh": pd.read_excel("/home/thrymr/Desktop/vendors/Andrapradesh_with_updates_vendors.xlsx"),
    "maharashtra": pd.read_excel("/home/thrymr/Desktop/vendors/Maharashtra_with_updates_vendors.xlsx"),
    "odisha": pd.read_excel("/home/thrymr/Desktop/vendors/odissa_with_updates_vendors.xlsx"),
    "tamilnadu": pd.read_excel("/home/thrymr/Desktop/vendors/TAMILNADU_Vendor_Database.xlsx"),
    "telangana": pd.read_excel("/home/thrymr/Desktop/vendors/telangana_with_updates_vendors.xlsx"),
    "karnataka": pd.read_excel("/home/thrymr/Desktop/vendors/Karnataka_Vendor_Database.xlsx"),
    "haryana": pd.read_excel("/home/thrymr/Desktop/vendors/Haryana_Vendor_Database.xlsx"),
    "bihar": pd.read_excel("/home/thrymr/Desktop/vendors/Bihar_Vendor_Database.xlsx")
}


# Normalize columns in state files
for state_key, df in state_files.items():
    df.columns = df.columns.str.strip()
    df['vendor_id_norm'] = df['Vendor_Id'].astype(str).str.lower().str.replace(" ", "")
    state_files[state_key] = df

# Prepare result list
merged_rows = []

# Iterate through each row in input
for idx, row in input_df.iterrows():
    norm_state = row['vendor_state_norm']
    norm_id = row['vendor_id_norm']

    if norm_state in state_files:
        state_df = state_files[norm_state]

        # Match using normalized ID
        match = state_df[state_df['vendor_id_norm'] == norm_id]

        if not match.empty:
            details_row = match.iloc[0]
            enriched_row = row.drop(['vendor_id_norm', 'vendor_state_norm']).to_dict()  # Keep original values

            # Add additional vendor details
            enriched_row.update({
                'Mobile': details_row.get('Mobile'),
                'Name': details_row.get('Name'),
                'District': details_row.get('District'),
                'State': details_row.get('State'),
                'Sub Vertical': details_row.get('Sub Vertical'),
                'Address': details_row.get('Address'),
                'Pincode': details_row.get('Pincode'),
                # 'Vendor_id': details_row.get('Vendor_Id')
            })

            merged_rows.append(enriched_row)
        else:
            print("ok")
    else:
        print(f"Vendor_State {row['Vendor_State']} not recognized")

# Convert result to DataFrame
final_df = pd.DataFrame(merged_rows)

# Save to Excel
final_df.to_excel("/home/thrymr/Downloads/with_vendordata_Agri Purchase September-24.xlsx", index=False)
print("✅ Merged output saved!")
