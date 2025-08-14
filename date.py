# import pandas as pd
# import numpy as np

# # Load both files into DataFrames
# df1 = pd.read_excel("/home/thrymr/Downloads/hesaathi_updated.xlsx")
# df2 = pd.read_excel("/home/thrymr/Downloads/mp.xlsx")


# # Check for empty Full Name cells in Tamil Nadu records
# tamil_nadu_mask = df1['State'].str.lower() == 'madhya pradesh'
# empty_name_mask = df1['Full Name'].isna() | (df1['Full Name'].str.strip() == '')

# # Combined filter: Tamil Nadu records with empty Full Name
# target_rows = tamil_nadu_mask & empty_name_mask

# print(f"\nFound {target_rows.sum()} records in Tamil Nadu with empty Full Name")

# if target_rows.sum() > 0:
#     print("\nRecords to be updated:")
#     print(df1[target_rows][['S no', 'CODE', 'Full Name', 'Gender', 'State']].head())
    
#     # Group target rows by gender
#     target_df = df1[target_rows].copy()
    
#     # Assuming df2 has columns like 'Name' and 'Gender' (adjust column names as needed)
#     # You may need to modify these column names based on your df2 structure
#     name_column = 'Name' if 'Name' in df2.columns else df2.columns[0]  # Adjust as needed
#     gender_column = 'Gender' if 'Gender' in df2.columns else None
    
#     print(f"\nUsing '{name_column}' column from df2 for names")
    
#     # Create a copy of df1 to work with
#     df1_updated = df1.copy()
    
#     # Track assignments to avoid duplicates - STRICT NO REUSE POLICY
#     used_names = set()
#     updates_made = 0
    
#     # Create a master list of all available names from df2
#     if gender_column and gender_column in df2.columns:
#         # If gender column exists, create separate pools for each gender
#         male_names = list(df2[df2[gender_column].str.lower() == 'male'][name_column].dropna().unique())
#         female_names = list(df2[df2[gender_column].str.lower() == 'female'][name_column].dropna().unique())
#         other_names = list(df2[~df2[gender_column].str.lower().isin(['male', 'female'])][name_column].dropna().unique())
        
#         print(f"Available name pools:")
#         print(f"  Male names: {len(male_names)}")
#         print(f"  Female names: {len(female_names)}")
#         print(f"  Other gender names: {len(other_names)}")
#     else:
#         # If no gender column, use all names for all genders
#         all_names = list(df2[name_column].dropna().unique())
#         male_names = all_names.copy()
#         female_names = all_names.copy()
#         other_names = all_names.copy()
#         print(f"Total available names (no gender distinction): {len(all_names)}")
    
#     # Get unique genders in target rows
#     target_genders = target_df['Gender'].unique()
    
#     for gender in target_genders:
#         print(f"\nProcessing gender: {gender}")
        
#         # Get rows for this gender
#         gender_rows = target_df[target_df['Gender'] == gender]
        
#         # Select appropriate name pool based on gender
#         if gender.lower() == 'male':
#             available_names = male_names
#         elif gender.lower() == 'female':
#             available_names = female_names
#         else:
#             available_names = other_names
        
#         print(f"Names available for {gender} BEFORE assignment: {len(available_names)}")
        
#         # Assign names to rows - REMOVE each name immediately after use
#         for original_idx, row in gender_rows.iterrows():
#             if available_names:  # Check if any names are still available
#                 # Take the first available name
#                 new_name = available_names.pop(0)  # REMOVE from list immediately
                
#                 # Update the dataframe
#                 df1_updated.at[original_idx, 'Full Name'] = new_name
                
#                 # Add to global used names set
#                 used_names.add(new_name)
                
#                 # ALSO remove from other gender pools to ensure NO REUSE
#                 if new_name in male_names and available_names != male_names:
#                     male_names.remove(new_name)
#                 if new_name in female_names and available_names != female_names:
#                     female_names.remove(new_name)
#                 if new_name in other_names and available_names != other_names:
#                     other_names.remove(new_name)
                
#                 updates_made += 1
#                 print(f"  ✓ Updated row {original_idx}: CODE {row['CODE']} -> {new_name}")
#                 print(f"    Remaining {gender} names: {len(available_names)}")
                
#             else:
#                 print(f"  ❌ No more names available for {gender}! Row {original_idx} (CODE: {row['CODE']}) remains empty")
    
#     print(f"\n" + "="*50)
#     print(f"FINAL SUMMARY:")
#     print(f"Total updates made: {updates_made}")
#     print(f"Total names used (will NEVER be reused): {len(used_names)}")
#     print(f"Remaining male names: {len(male_names) if gender_column else 'N/A'}")
#     print(f"Remaining female names: {len(female_names) if gender_column else 'N/A'}")
#     print(f"Remaining other names: {len(other_names) if gender_column else 'N/A'}")
#     print("="*50)
    
#     # Display updated records
#     print("\nUpdated records:")
#     updated_rows = df1_updated[target_rows]
#     print(updated_rows[['S no', 'CODE', 'Full Name', 'Gender', 'State']].head(10))
    
#     # Save the updated dataframe
#     output_file = "/home/thrymr/Downloads/hesaathi_updated.xlsx"
#     df1_updated.to_excel(output_file, index=False)
#     print(f"\nUpdated file saved as: {output_file}")
    
#     # Show summary statistics
#     remaining_empty = (df1_updated['Full Name'].isna() | (df1_updated['Full Name'].str.strip() == '')) & tamil_nadu_mask
#     print(f"\nRemaining empty Full Name cells in Tamil Nadu: {remaining_empty.sum()}")

# else:
#     print("No records found matching the criteria.")

# # Optional: Show sample of df2 structure to help with column mapping
# print("\nSample of df2 structure:")
# print(df2.head())
# print("\nDF2 column info:")
# for col in df2.columns:
#     print(f"  {col}: {df2[col].dtype}, non-null: {df2[col].notna().sum()}")

import pandas as pd

# Load the input file
df = pd.read_excel("/home/thrymr/Downloads/add.xlsx")

# Define the order of Onboarding Months
onboarding_order = [
    "Sep'24", "Oct'24", "Nov'24", "Dec'24", 
    "Jan'25", "Feb'25", "Mar'25", "April'25", "May'25", "Jun'25", "Jul'25", "Aug'25", 
    "Sep'25", "Oct'25", "Nov'25", "Dec'25", 
    "Jan'26", "Feb'26", "Mar'26"
]

# Create a dictionary to map Onboarding Month to the sorting index
month_sort_dict = {month: idx for idx, month in enumerate(onboarding_order)}

# Add a new column for sorting based on Onboarding Month
df['Sort Order'] = df['Onboarding Month'].map(month_sort_dict)

# Sort the dataframe by the new Sort Order column
df_sorted = df.sort_values(by='Sort Order').reset_index(drop=True)

# Add "S no" and "Hesaathi Code" columns
df_sorted['S no'] = range(1, len(df_sorted) + 1)
df_sorted['Hesaathi Code'] = ['HS021955' for _ in range(len(df_sorted))]

# Now adjust S no and Hesaathi Code for sequential numbering
s_no_start = 21954
hesaathi_code_start = "HS021955"

df_sorted['S no'] = range(s_no_start, s_no_start + len(df_sorted))
df_sorted['Hesaathi Code'] = [hesaathi_code_start for _ in range(len(df_sorted))]

# Save the updated dataframe to a new file
df_sorted.to_excel("/home/thrymr/Downloads/updated_file_with_sno_and_code.xlsx", index=False)
