import pandas as pd

# Load input file
input_df = pd.read_excel(r"c:\Users\ksand\Downloads\april_final.xlsx")  # Change to .csv if needed

input_df['vendor_id_norm'] = input_df['Vendor ID'].astype(str).str.lower().str.replace(" ", "")
input_df['vendor_state_norm'] = input_df['State'].astype(str).str.lower().str.replace(" ", "")

state_files = {
    # "andhrapradesh": pd.read_excel("/home/thrymr/Desktop/vendors/Andrapradesh_with_updates_vendors.xlsx"),
    # "maharashtra": pd.read_excel("/home/thrymr/Desktop/vendors/Maharashtra_with_updates_vendors.xlsx"),
    # "odisha": pd.read_excel("/home/thrymr/Desktop/vendors/odissa_with_updates_vendors.xlsx"),
    # "tamilnadu": pd.read_excel("/home/thrymr/Desktop/vendors/TAMILNADU_Vendor_Database.xlsx"),
    "telangana": pd.read_excel(r"c:\Users\ksand\Downloads\telangana_150_Vendors (1).xlsx"),
    # "karnataka": pd.read_excel("/home/thrymr/Desktop/vendors/Karnataka_Vendor_Database.xlsx"),
    # "haryana": pd.read_excel("/home/thrymr/Desktop/vendors/Haryana_Vendor_Database.xlsx"),
    # "bihar": pd.read_excel("/home/thrymr/Desktop/vendors/Bihar_Vendor_Database.xlsx"),
    # "madhyapradesh": pd.read_excel("/home/thrymr/Desktop/vendors/mp_with_updates_vendors.xlsx")
}

# Normalize columns in state files
for state_key, df in state_files.items():
    df.columns = df.columns.str.strip()
    df['vendor_id_norm'] = df['Vendor ID'].astype(str).str.lower().str.replace(" ", "")
    state_files[state_key] = df

# Prepare result list
merged_rows = []

# Iterate through each row in input
for idx, row in input_df.iterrows():
    norm_state = row['vendor_state_norm']
    norm_id = row['vendor_id_norm']

    enriched_row = row.drop(['vendor_id_norm', 'vendor_state_norm']).to_dict()  # Keep original values

    if norm_state in state_files:
        state_df = state_files[norm_state]

        # Match using normalized ID
        match = state_df[state_df['vendor_id_norm'] == norm_id]

        if not match.empty:
            details_row = match.iloc[0]

            # Add additional vendor details
            enriched_row.update({
                'Mobile': details_row.get('Mobile'),
                'Name': details_row.get('Name'),
                'District': details_row.get('District'),
                'State_from_vendor': details_row.get('State'),   # renamed to avoid overwrite
                'Sub Vertical': details_row.get('Sub Vertical'),
                'Address': details_row.get('Address'),
                'Pincode': details_row.get('Pincode'),
            })
        else:
            # If no match, vendor details remain blank (NaN)
            enriched_row.update({
                'Mobile': None,
                'Name': None,
                'District': None,
                'State_from_vendor': None,
                'Sub Vertical': None,
                'Address': None,
                'Pincode': None,
            })
    else:
        # State not found in mapping, still keep the row
        enriched_row.update({
            'Mobile': None,
            'Name': None,
            'District': None,
            'State_from_vendor': None,
            'Sub Vertical': None,
            'Address': None,
            'Pincode': None,
        })

    merged_rows.append(enriched_row)

# Convert result to DataFrame
final_df = pd.DataFrame(merged_rows)

# Save to Excel
final_df.to_excel(r"c:\Users\ksand\Downloads\purchases(20-21)\apr_purchase_with_vendors.xlsx", index=False)
print("✅ Merged output saved! (all rows preserved)")
