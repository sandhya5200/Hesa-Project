import pandas as pd

# Load the Excel files
field_officers = pd.read_excel("/home/thrymr/Downloads/field_officers.xlsx")
exit_file = pd.read_excel("/home/thrymr/Downloads/exit.xlsx")

# Define the key columns for filtering
key_columns = ["Employee ID", "DOJ", "Entity"]

# Function to process each Employee ID
def process_employee_id(group, exit_df):
    emp_id = group["Employee ID"].iloc[0]
    print(f"Processing Employee ID: {emp_id}")
    exit_match = exit_df[exit_df["Employee ID"] == emp_id]
    
    if not exit_match.empty:
        print(f"Employee ID {emp_id} found in exit file")
        for _, row in group.iterrows():
            match = exit_match[(exit_match["DOJ"] == row["DOJ"]) & (exit_match["Entity"] == row["Entity"])]
            if not match.empty:
                print(f"Match found for Employee ID {emp_id} with DOJ {row['DOJ']} and Entity {row['Entity']}")
                return row.to_frame().T  # Keep only the matched row
    
    # If no match found in exit file, concatenate column values
    print(f"No match found in exit file for Employee ID {emp_id}, concatenating values")
    for col in group.columns:
        if col != "Employee ID":
            group[col] = group[col].astype(str).str.upper().drop_duplicates().str.cat(sep=", ")
    return group.head(1)  # Keep only one row per Employee ID

# Process the field officers file
deduplicated_df = field_officers.groupby("Employee ID", group_keys=False).apply(lambda x: process_employee_id(x, exit_file))

deduplicated_df.reset_index(drop=True, inplace=True)


# Save the cleaned file
deduplicated_df.to_excel("/home/thrymr/Downloads/cleaned_field_officers.xlsx", index=False)











