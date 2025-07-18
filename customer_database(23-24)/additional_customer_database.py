import pandas as pd
import os

# File paths
unmatched_codes_path = "/home/thrymr/Downloads/deduplicated_with_hesaathi.xlsx"
zone_file_path = "/home/thrymr/Important/new_hessathi_with_additional_people_details.xlsx"

# Output folder
output_folder = "/home/thrymr/Desktop/vendors/sandhya/second_time_updated_state_files_after_assignig_to_second_additional_database"
os.makedirs(output_folder, exist_ok=True)

# State file paths (with original keys)
state_files_raw = {
    'TELANGANA': '/home/thrymr/Desktop/vendors/sandhya/updated_state_files_after_assignig_to_additional_database/cleaned_TELANGANA.xlsx',
    'BIHAR': '/home/thrymr/Desktop/vendors/sandhya/updated_state_files_after_assignig_to_additional_database/cleaned_BIHAR.xlsx',
    'ANDHRA PRADESH': '/home/thrymr/Desktop/vendors/sandhya/updated_state_files_after_assignig_to_additional_database/cleaned_ANDHRA PRADESH.xlsx',
    'TAMIL NADU': '/home/thrymr/Desktop/vendors/sandhya/updated_state_files_after_assignig_to_additional_database/cleaned_TAMILNADU.xlsx',
    'ODISHA': '/home/thrymr/Desktop/vendors/sandhya/updated_state_files_after_assignig_to_additional_database/cleaned_ODISHA.xlsx',
    'HARYANA': '/home/thrymr/Desktop/vendors/sandhya/updated_state_files_after_assignig_to_additional_database/cleaned_HARYANA.xlsx',
    'MAHARASHTRA': '/home/thrymr/Desktop/vendors/sandhya/updated_state_files_after_assignig_to_additional_database/cleaned_MP.xlsx',
    'KARNATAKA': '/home/thrymr/Desktop/vendors/sandhya/updated_state_files_after_assignig_to_additional_database/cleaned_KARNATAKA.xlsx',
    "MADHYA PRADESH": "/home/thrymr/Desktop/vendors/sandhya/updated_state_files_after_assignig_to_additional_database/cleaned_MAHARASHTRA.xlsx"
}

# Normalize state keys
def normalize_state_name(name):
    return name.strip().upper().replace(" ", "")

state_files = {normalize_state_name(k): v for k, v in state_files_raw.items()}

# Load data
input_df = pd.read_excel(unmatched_codes_path, engine='openpyxl')
zone_df = pd.read_excel(zone_file_path, engine='openpyxl')
state_dfs = {normalize_state_name(state): pd.read_excel(path, engine='openpyxl') for state, path in state_files.items()}

# Output records
output_rows = []
failed_rows = []

for _, row in input_df.iterrows():
    customer_id = row['Unmatched_codes']
    hs_code = row['CODE']

    zone_match = zone_df[zone_df['CODE'].astype(str).str.strip().str.upper() == str(hs_code).strip().upper()]
    if zone_match.empty:
        print(f"⚠️ Zone match not found for: {hs_code}")
        failed_rows.append({'CustomerID': customer_id, 'HSCode': hs_code, 'Reason': 'HSCode not found in zone'})
        continue

    state = zone_match.iloc[0]['State']
    district = zone_match.iloc[0]['District']

    normalized_state = normalize_state_name(state)
    print(f"🔍 Matching HSCode: {hs_code} | State: {state} | District: {district} → Normalized: {normalized_state}")

    state_df = state_dfs.get(normalized_state)
    if state_df is None:
        print(f"❌ State file not found: {state}")
        failed_rows.append({'CustomerID': customer_id, 'HSCode': hs_code, 'Reason': f"State '{state}' not found in files"})
        continue

    # Normalize for district comparison
    state_df['District_cleaned'] = state_df['District'].astype(str).str.strip().str.lower()
    district_cleaned = str(district).strip().lower()

    district_match = state_df[state_df['District_cleaned'] == district_cleaned]

    if not district_match.empty:
        selected_row = district_match.iloc[0]
        print(f"✅ Found exact district match for {district}")
    else:
        print(f"⚠️ No exact match for '{district}', using fallback row.")
        if state_df.empty:
            failed_rows.append({'CustomerID': customer_id, 'HSCode': hs_code, 'Reason': 'No data in state file'})
            continue
        selected_row = state_df.iloc[0]

    # Prepare output row
    output_rows.append({
    'CustomerID': customer_id,
    'Mobile': selected_row.get('Mobile', ''),
    'Name': selected_row.get('Name', ''),
    'Pincode': selected_row.get('Pincode', ''),  # fallback if Pincode missing
    'HSCode': hs_code,
    'State': state,
    'District': selected_row.get('District', '')
})

    # Drop used row
    state_dfs[normalized_state] = state_df.drop(selected_row.name).drop(columns=['District_cleaned'], errors='ignore')

# Save final output
output_df = pd.DataFrame(output_rows)
output_df.to_excel("/home/thrymr/Downloads/final_output.xlsx", index=False, engine='openpyxl')
print(f"\n✅ Final output saved: {len(output_df)} rows")

# Save updated state files
for state_key, df in state_dfs.items():
    # Get original file path from normalized key
    original_filename = os.path.basename(state_files[state_key])
    new_path = os.path.join(output_folder, original_filename)
    df.to_excel(new_path, index=False, engine='openpyxl')
    print(f"📝 Updated state file written: {state_key}")

# Save failed assignments
if failed_rows:
    failed_df = pd.DataFrame(failed_rows)
    failed_df.to_excel("/home/thrymr/Downloads/failed_assignments.xlsx", index=False, engine='openpyxl')
    print(f"\n❌ Failed to assign {len(failed_df)} codes. File saved.")
