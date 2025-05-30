# import pandas as pd

# # Load the files
# hesaathi_df = pd.read_excel("/home/thrymr/Important/new_hessathi_with_additional_people_details.xlsx")  # Replace with your actual file name
# zone_df = pd.read_excel("/home/thrymr/Downloads/zone_user_category_modified.xlsx")          # Replace with your actual file name

# # Merge based on matching Hesaathi Code and code column
# merged_df = hesaathi_df.merge(zone_df[['CODE', 'Category']], 
#                               left_on='Hesaathi Code', right_on='CODE', 
#                               how='left')

# # Rename Category column to Performance
# merged_df.rename(columns={'Category': 'Performance'}, inplace=True)

# # Drop the 'code' column from Zone file if you don't want it in output
# merged_df.drop(columns=['CODE'], inplace=True)

# # Save the output
# merged_df.to_excel("/home/thrymr/Downloads/HESATHI.xlsx", index=False)
# print("Output saved to output_file.xlsx")
#---------------------------------------------------------------------------------------------------------------------------
# import pandas as pd

# df = pd.read_excel("/home/thrymr/Downloads/performance_assigned_output.xlsx")  


# performance_counts = df.groupby(['Onboarding Month', 'Performance']).size().reset_index(name='Count')


# total_per_month = df.groupby('Onboarding Month').size().reset_index(name='Total')

# merged = performance_counts.merge(total_per_month, on='Onboarding Month')
# merged['Percentage'] = (merged['Count'] / merged['Total']) * 100

# pivot_df = merged.pivot(index='Onboarding Month', columns='Performance', values='Percentage').fillna(0)
# pivot_df = pivot_df.reset_index()

# pivot_df.to_excel("/home/thrymr/Downloads/HESATHI_analysis.xlsx", index=False)
# print("")

#----------------------------------------------------------------------------------------------------------------------------------




# import pandas as pd
# import numpy as np

# # Load the input file
# df = pd.read_excel("/home/thrymr/Downloads/HESATHI_analysis.xlsx")  # Replace with your actual input file name

# # Define performance allocation percentages
# allocation = {
#     'High Performer': 0.18,
#     'Medium Performer': 0.42,
#     'Non Performer': 0.40
# }

# # Function to assign performance labels based on percentages
# def assign_performance(group):
#     n = len(group)
#     high_n = int(n * allocation['High Performer'])
#     medium_n = int(n * allocation['Medium Performer'])
#     non_n = n - high_n - medium_n  # Ensures total adds up to n

#     performance_labels = (
#         ['High Performer'] * high_n +
#         ['Medium Performer'] * medium_n +
#         ['Non Performer'] * non_n
#     )
#     np.random.shuffle(performance_labels)
#     group['Performance'] = performance_labels
#     return group

# # Apply the assignment by group
# df = df.groupby(['Onboarding Month', 'Category_x'], group_keys=False).apply(assign_performance)

# # Save to Excel
# df.to_excel("/home/thrymr/Downloads/performance_assigned_output.xlsx", index=False)
# print("Saved performance-assigned data to performance_assigned_output.xlsx")


#----------------------------------------------------------------------------------------------------------

import pandas as pd

# Load Excel file
file_path = '/home/thrymr/Downloads/kyc.xlsx'

# Read both sheets
sheet1 = pd.read_excel(file_path, sheet_name=0)  # Sheet 1 (index 0)
sheet2 = pd.read_excel(file_path, sheet_name=1)  # Sheet 2 (index 1)

# Assume the name column is called "Name" in both sheets (adjust if different)
# Get names from sheet1
names_in_sheet1 = set(sheet1['Name'].dropna().str.strip())

# Filter sheet2 to keep only rows where 'Name' is NOT in sheet1
sheet2_filtered = sheet2[~sheet2['Name'].str.strip().isin(names_in_sheet1)]

# Output result
print(sheet2_filtered)

# Optionally, save to a new file
sheet2_filtered.to_excel('/home/thrymr/Downloads/KY.xlsx', index=False)
