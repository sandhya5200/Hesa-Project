# import pandas as pd
# import os

# # File paths
# output_folder = "/home/thrymr/Desktop/vendors/sandhya/updated_state_files_after_assignig_to_additional_database"
# master_output_file = "/home/thrymr/Downloads/Master_Assigned_Persons.xlsx"
# no_zone_codes_file = "/home/thrymr/Downloads/No_Zone_Codes.xlsx"

# # Ensure output folder exists
# os.makedirs(output_folder, exist_ok=True)

# # Load data
# unmatched_df = pd.read_excel('/home/thrymr/Downloads/important.xlsx')
# zone_df = pd.read_excel('/home/thrymr/Downloads/Copy of zone_user_24_25 latest one with new additions..xlsx')

# # Convert columns to uppercase for matching
# unmatched_df["Unmatched_codes"] = unmatched_df["Unmatched_codes"].astype(str).str.upper()
# zone_df["CODE"] = zone_df["CODE"].astype(str).str.upper()

# # Define paths for each state
# state_files = {
#     'TELANGANA': '/home/thrymr/Desktop/vendors/sandhya/after creating 40k people used to make additional customerdatabase/cleaned_Telangana.xlsx',
#     'BIHAR': '/home/thrymr/Desktop/vendors/sandhya/after creating 40k people used to make additional customerdatabase/cleaned_Bihar_mod.xlsx',
#     'ANDHRA PRADESH': '/home/thrymr/Desktop/vendors/sandhya/after creating 40k people used to make additional customerdatabase/cleaned_AP.xlsx',
#     'TAMIL NADU': '/home/thrymr/Desktop/vendors/sandhya/after creating 40k people used to make additional customerdatabase/cleaned_Tamilnadu_mod.xlsx',
#     'ODISHA': '/home/thrymr/Desktop/vendors/sandhya/after creating 40k people used to make additional customerdatabase/cleaned_Odisha.xlsx',
#     'HARYANA': "/home/thrymr/Desktop/vendors/sandhya/after creating 40k people used to make additional customerdatabase/cleaned_Haryana_mod.xlsx",
#     'MAHARASHTRA': '/home/thrymr/Desktop/vendors/sandhya/after creating 40k people used to make additional customerdatabase/cleaned_Maharashtra.xlsx',
#     'KARNATAKA': '/home/thrymr/Desktop/vendors/sandhya/after creating 40k people used to make additional customerdatabase/cleaned_Karnataka.xlsx'
# }

# # Dictionary to store state data
# state_data = {}
# for state, file_path in state_files.items():
#     try:
#         df = pd.read_excel(file_path)
#         df["District"] = df["District"].astype(str).str.upper()
#         state_data[state] = df
#     except Exception as e:
#         print(f"Error loading {file_path}: {e}")
#         state_data[state] = pd.DataFrame()  # Empty DataFrame if loading fails

# # List to store master output records
# assigned_records = []

# # Track unmatched codes
# no_zone_codes_set = []

# # Process each unmatched code (keeping duplicates)
# for _, row in unmatched_df.iterrows():
#     code = row["Unmatched_codes"]
#     state_row = zone_df[zone_df["CODE"] == code]

#     if state_row.empty:
#         print(f"Code {code} not found in zone file.")
#         no_zone_codes_set.append(code)
#         continue

#     # Handle NaN cases safely
#     state_name = state_row["State"].values[0] if pd.notna(state_row["State"].values[0]) else "UNKNOWN"
#     district_name = state_row["District"].values[0] if pd.notna(state_row["District"].values[0]) else "UNKNOWN"

#     state_name = str(state_name).strip().upper()
#     district_name = str(district_name).strip().upper()

#     if state_name == "UNKNOWN":
#         print(f"State not found for code {code}. Skipping...")
#         no_zone_codes_set.append(code)
#         continue

#     if state_name not in state_data:
#         print(f"State {state_name} not found in state files.")
#         continue

#     state_df = state_data[state_name]

#     # Filter available persons in the same district
#     available_persons = state_df[state_df["District"] == district_name]

#     # If no match in the same district, get data from any district
#     if available_persons.empty:
#         available_persons = state_df

#     if available_persons.empty:
#         print(f"No available persons found for code {code} in {state_name}.")
#         no_zone_codes_set.append(code)
#         continue

#     # Select a random person (even if they were used before)
#     selected_row = available_persons.sample(n=1)
#     person_id = selected_row.index[0]

#     # Append assigned person details to the master output
#     assigned_person = selected_row.iloc[0].to_dict()
#     assigned_person["HESATHIS_Code"] = code
#     assigned_person["Assigned_State"] = state_name
#     assigned_person["Assigned_District"] = district_name
#     assigned_records.append(assigned_person)

#     # Drop assigned person from state data to avoid reusing too often
#     state_data[state_name].drop(index=person_id, inplace=True)

# # Save master assigned persons file
# if assigned_records:
#     master_df = pd.DataFrame(assigned_records)
#     master_df.to_excel(master_output_file, index=False)
#     print(f"Master output saved at: {master_output_file}")
# else:
#     print("No assignments were made.")

# # Save unmatched codes
# if no_zone_codes_set:
#     no_zone_codes_df = pd.DataFrame({"Unmatched_Code": list(no_zone_codes_set)})
#     no_zone_codes_df.to_excel(no_zone_codes_file, index=False)
#     print(f"Unmatched codes saved at: {no_zone_codes_file}")
# else:
#     print("No unmatched codes found.")

# # Save updated state files
# for state_name, df in state_data.items():
#     updated_file_path = os.path.join(output_folder, f"cleaned_{state_name}.xlsx")
#     df.to_excel(updated_file_path, index=False)

# print("Processing complete. Updated state files saved in:", output_folder)

import pandas as pd
import os

# File paths
output_folder = "/home/thrymr/Desktop/vendors/sandhya/updated_state_files_after_assignig_to_additional_database"
master_output_file = "/home/thrymr/Downloads/Master_Assigned_Persons.xlsx"
no_zone_codes_file = "/home/thrymr/Downloads/No_Zone_Codes.xlsx"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Load data
unmatched_df = pd.read_excel('/home/thrymr/Downloads/important.xlsx')
zone_df = pd.read_excel('/home/thrymr/Downloads/Copy of zone_user_24_25 latest one with new additions..xlsx')

# Convert columns to uppercase for matching
unmatched_df["Unmatched_codes"] = unmatched_df["Unmatched_codes"].astype(str).str.upper()
zone_df["CODE"] = zone_df["CODE"].astype(str).str.upper()

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

# Dictionary to store state data
state_data = {}
for state, file_path in state_files.items():
    try:
        df = pd.read_excel(file_path)
        df["District"] = df["District"].astype(str).str.upper()
        state_data[state] = df
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        state_data[state] = pd.DataFrame()  # Empty DataFrame if loading fails

# List to store master output records
assigned_records = []

# Track unmatched codes
no_zone_codes_set = []

# Process each unmatched code and keep all rows from unmatched_df
for _, row in unmatched_df.iterrows():
    code = row["Unmatched_codes"]
    state_row = zone_df[zone_df["CODE"] == code]

    if state_row.empty:
        print(f"Code {code} not found in zone file.")
        no_zone_codes_set.append(code)
        state_name = "UNKNOWN"
        district_name = "UNKNOWN"
    else:
        state_name = state_row["State"].values[0] if pd.notna(state_row["State"].values[0]) else "UNKNOWN"
        district_name = state_row["District"].values[0] if pd.notna(state_row["District"].values[0]) else "UNKNOWN"

    state_name = str(state_name).strip().upper()
    district_name = str(district_name).strip().upper()

    if state_name != "UNKNOWN" and state_name in state_data:
        state_df = state_data[state_name]

        # Filter available persons in the same district
        available_persons = state_df[state_df["District"] == district_name]

        # If no match in the same district, get data from any district
        if available_persons.empty:
            available_persons = state_df

        if available_persons.empty:
            print(f"No available persons found for code {code} in {state_name}.")
            selected_person = {"Assigned_Person": "NO_PERSON_FOUND"}
        else:
            # Select a random person (even if they were used before)
            selected_row = available_persons.sample(n=1)
            person_id = selected_row.index[0]
            selected_person = selected_row.iloc[0].to_dict()

            # Drop assigned person from state data to avoid reusing too often
            state_data[state_name].drop(index=person_id, inplace=True)
    else:
        selected_person = {"Assigned_Person": "NO_STATE_FOUND"}

    # Merge original row with selected person
    merged_record = row.to_dict()
    merged_record.update(selected_person)
    merged_record["HESATHIS_Code"] = code
    merged_record["Assigned_State"] = state_name
    merged_record["Assigned_District"] = district_name

    assigned_records.append(merged_record)

# Save master assigned persons file
master_df = pd.DataFrame(assigned_records)
master_df.to_excel(master_output_file, index=False)
print(f"Master output saved at: {master_output_file}")

# Save unmatched codes
if no_zone_codes_set:
    no_zone_codes_df = pd.DataFrame({"Unmatched_Code": list(no_zone_codes_set)})
    no_zone_codes_df.to_excel(no_zone_codes_file, index=False)
    print(f"Unmatched codes saved at: {no_zone_codes_file}")
else:
    print("No unmatched codes found.")

# Save updated state files
for state_name, df in state_data.items():
    updated_file_path = os.path.join(output_folder, f"cleaned_{state_name}.xlsx")
    df.to_excel(updated_file_path, index=False)

print("Processing complete. Updated state files saved in:", output_folder)

