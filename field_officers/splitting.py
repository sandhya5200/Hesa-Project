#just to split the names and assign to new Employee ID with -

# import pandas as pd

# # Load the Excel file
# df = pd.read_excel("/home/thrymr/Downloads/dupli.xlsx")

# # Initialize a list to store the transformed rows
# expanded_rows = []

# # Iterate through each row
# for _, row in df.iterrows():
#     names = row["Name"].split(", ")  # Split names by comma
#     dojs = row["DOJ"].split(", ")    # Split DOJ by comma
    
#     for i in range(len(names)):
#         new_row = row.copy()
#         new_row["Name"] = names[i]
#         new_row["DOJ"] = dojs[i] if i < len(dojs) else ""
        
#         # Append -1 to Employee ID for the second row
#         if i > 0:
#             new_row["Employee ID"] = f"{row['Employee ID']}-1"
        
#         expanded_rows.append(new_row)

# # Create a new DataFrame
# expanded_df = pd.DataFrame(expanded_rows)

# # Save to a new Excel file
# expanded_df.to_excel("/home/thrymr/Downloads/dupliiiiiii.xlsx", index=False)

#---------------------------------------------------------------------------------------------------------------------------------------------------

#just to get cohort from date

import pandas as pd

# Load the Excel file
file_path = "/home/thrymr/Downloads/cleaned_field_officers.xlsx"  # Replace with your actual file path
df = pd.read_excel(file_path)

# Convert DOJ column to datetime format
df['DOJ'] = pd.to_datetime(df['DOJ'], errors='coerce')

# Create the Cohort column in "MMM'YY" format
df['Cohort'] = df['DOJ'].dt.strftime("%b'%y")

# Save the modified DataFrame back to an Excel file
output_file = "/home/thrymr/Downloads/ccleaned_field_officers.xlsx"  # Output file name
df.to_excel(output_file, index=False)

print(f"File saved as {output_file}")
