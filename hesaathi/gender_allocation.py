# import pandas as pd

# # Load Excel file
# df = pd.read_excel("/home/thrymr/Downloads/exam.xlsx")  

# # Replace gender values
# df["GENDER"] = df["GENDER"].replace({"M": "Male", "F": "Female"})

# # Remove duplicate names
# df_unique = df.drop_duplicates(subset="Name", keep="first")

# # Filter only required columns
# df_unique = df_unique[["Name", "GENDER"]]

# # Sample 2633 males and 5368 females
# males = df_unique[df_unique["GENDER"] == "Male"].sample(n=2653, random_state=42)
# females = df_unique[df_unique["GENDER"] == "Female"].sample(n=5368, random_state=42)

# # Combine them
# df_sampled = pd.concat([males, females]).sample(frac=1, random_state=42)  # shuffle

# # Save to Excel
# df_sampled.to_excel("/home/thrymr/Downloads/output_file.xlsx", index=False)

# # Optional: print the result
# print(df_sampled)

# import pandas as pd

# # Load input files
# hesaathi_df = pd.read_excel("/home/thrymr/Downloads/hesaathi_output.xlsx")
# names_df = pd.read_excel("/home/thrymr/Downloads/Names_with_Gender_Deep_Analysis.xlsx")

# # Create an empty list to store matched rows
# matched_rows = []

# # Group names by gender
# names_by_gender = names_df.groupby("Gender")["Name"].apply(list).to_dict()

# # Go through each row in the hesaathi file
# for gender in hesaathi_df["Gender"].unique():
#     hesaathi_subset = hesaathi_df[hesaathi_df["Gender"] == gender].copy()

#     available_names = names_by_gender.get(gender, [])
#     num_to_assign = min(len(hesaathi_subset), len(available_names))

#     if num_to_assign == 0:
#         continue  # No names for this gender

#     # Assign unique names
#     hesaathi_subset = hesaathi_subset.iloc[:num_to_assign].copy()
#     hesaathi_subset["Name"] = available_names[:num_to_assign]

#     matched_rows.append(hesaathi_subset)

# # Combine and save result
# if matched_rows:
#     result_df = pd.concat(matched_rows, ignore_index=True)
#     result_df.to_excel("/home/thrymr/Downloads/hesaathi_final_output.xlsx", index=False)
#     print("Matched names saved to hesaathi_named_output.csv")
# else:
#     print("No matches found.")


import pandas as pd
import random

# Load your Excel file
df = pd.read_excel("/home/thrymr/Downloads/hesaathi_filled_output.xlsx")

# Sort by 'S no'
df = df.sort_values("S no").reset_index(drop=True)

# Define the predefined mapping of states and districts
state_district_map = {
   
    "Odisha": ["Angul", "Balangir", "Balasore", "Baleswar", "Bargarh", "Bhadrak", "Boudh", "Cuttack", "Debagarh", "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghapur", "Jajapur", "Kalahandi", "Kendrapara", "Kendujhar", "Khorda", "Mayurbhanj", "Nayagarh", "Puri", "Rayagada", "Sonapur", "Sundergarh"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", "Erode", "Kanchipuram", "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Namakkal", "Nilgiris", "Ramanathapuram", "Salem", "Tiruchirappalli", "Tirunelveli", "Tiruppur", "Tiruvannamalai", "Vellore"],
   
}

# Flatten the mapping into (district, state) pairs
valid_locations = [(district, state) for state, districts in state_district_map.items() for district in districts]

# Function to fill missing District and State with random choice from predefined list
def fill_location(row):
    if pd.isna(row["District"]) or pd.isna(row["State"]):
        district, state = random.choice(valid_locations)
        row["District"] = district
        row["State"] = state
    return row

# Apply the filling function
df = df.apply(fill_location, axis=1)

# Save the result to a new Excel file
df.to_excel("/home/thrymr/Downloads/hesaathi_filled_output.xlsx", index=False)
print("Output saved to hesaathi_filled_output.xlsx")



