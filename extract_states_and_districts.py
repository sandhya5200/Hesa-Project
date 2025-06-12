import pandas as pd

# List of input Excel file paths
input_files = [
    "/home/thrymr/Downloads/Nov sales 24-25(Final).xlsx",
    "/home/thrymr/Downloads/Dec Sales 24-25(Final).xlsx",
    "/home/thrymr/Downloads/Jan Sales 24-25(Final) (2).xlsx",
    "/home/thrymr/Downloads/Feb Sales 24-25(Final).xlsx"
]

# Collect all state-district data
all_data = []

for file in input_files:
    xls = pd.ExcelFile(file)
    # Read only first two sheets
    df_list = [xls.parse(sheet) for sheet in xls.sheet_names[:2]]
    combined = pd.concat(df_list, ignore_index=True)
    if 'Customer State' in combined.columns and 'Customer District' in combined.columns:
        df = combined[['Customer State', 'Customer District']].dropna()
        all_data.append(df)

# Combine data from all files
full_df = pd.concat(all_data, ignore_index=True)

# Function to remove duplicate districts (case-insensitive)
def remove_duplicates_keep_order(districts):
    seen = set()
    result = []
    for d in districts:
        key = d.strip().lower()
        if key not in seen:
            seen.add(key)
            result.append(d.strip())
    return ', '.join(result)

# Group by state and apply function
grouped = full_df.groupby('Customer State')['Customer District'].apply(remove_duplicates_keep_order).reset_index()

# Save to Excel
output_path = "/home/thrymr/Downloads/state_district_combined_all_months.xlsx"
grouped.to_excel(output_path, index=False, header=["Customer State", "Districts"])

print(f"✅ Output saved to: {output_path}")
