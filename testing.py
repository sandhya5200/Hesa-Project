# import pandas as pd

# # Load the file (replace 'your_file.csv' with the actual path)
# df = pd.read_excel('/home/thrymr/Downloads/hesaathi_updated.xlsx')  # Modify with the actual path of your file

# # Find duplicates based on 'Full Name' column
# duplicates = df[df.duplicated(subset='Full Name', keep=False)]

# # Save duplicates to a new file
# duplicates.to_excel('/home/thrymr/Downloads/file.xlsx', index=False)

# print("Duplicates saved to 'duplicates.csv'")
  

# -----------------------------------------------to get name into full name column-------------------------------------------

# import pandas as pd

# # Load the Excel or CSV file
# df = pd.read_excel('/home/thrymr/Downloads/hesaathi_with_names.xlsx')  # or pd.read_csv('your_file.csv')

# # Replace 'Full Name' with 'Name' where 'Name' is not empty
# df['Full Name'] = df.apply(lambda row: row['Name'] if pd.notna(row['Name']) and row['Name'] != '' else row['Full Name'], axis=1)

# # Save the updated file
# df.to_excel('/home/thrymr/Downloads/hesaathi_with_names.xlsx', index=False)  # or df.to_csv('updated_file.csv', index=False)

# -----------------------------------------------------

# import pandas as pd

# # Load the file
# full_file = pd.read_excel('/home/thrymr/Downloads/hesaathi_with_names.xlsx')

# # Keep the first occurrence of each name and drop the subsequent ones
# full_file['Full Name'] = full_file['Full Name'].where(full_file.duplicated('Full Name') == False)

# # Save the result to a new Excel file
# output_file = '/home/thrymr/Downloads/hesaathi_with_namess.xlsx'
# full_file.to_excel(output_file, index=False)

# print(f"Output file saved as {output_file}")
# -----------------------------------------------------------------------------------
import pandas as pd

# Generate HS codes from HS021955 to HS038917
start_code = 21955
end_code = 38917

# Create a list of HS codes
hs_codes = [f"HS{str(i).zfill(6)}" for i in range(start_code, end_code + 1)]

# Create a DataFrame from the list of HS codes
df = pd.DataFrame(hs_codes, columns=["HS_Code"])

# Save to Excel
df.to_excel("/home/thrymr/Downloads/HS_Codes.xlsx", index=False)

print("HS codes have been successfully saved to HS_Codes.xlsx")
