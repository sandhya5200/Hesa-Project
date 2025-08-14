import pandas as pd

# --- Step 1: Load the two Excel files ---
file1 = "/home/thrymr/Downloads/aug_sales_with_hesaathis_part1.xlsx"  # Replace with your actual path
file2 = "/home/thrymr/Downloads/aug_sales_with_hesaathis_part2.xlsx"


df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

# --- Step 2: Group by Hesaathi Code, State, District and calculate sum of Taxable Value ---
grouped_df1 = df1.groupby(
    ["Assigned Hesaathi Code", "State", "District"], as_index=False)["Taxable Value"].sum()
grouped_df1.rename(columns={"Taxable Value": "Taxable Value (File 1)"}, inplace=True)

grouped_df2 = df2.groupby(
    ["Assigned Hesaathi Code", "State", "District"], as_index=False)["Taxable Value"].sum()
grouped_df2.rename(columns={"Taxable Value": "Taxable Value (File 2)"}, inplace=True)

# --- Step 3: Merge both summaries on Hesaathi Code, State, and District ---
merged_df = pd.merge(grouped_df1, grouped_df2, on=["Assigned Hesaathi Code", "State", "District"], how="outer")

# --- Step 4: Add a new column for the sum of both taxable values ---
merged_df["Total Taxable Value"] = merged_df["Taxable Value (File 1)"].fillna(0) + merged_df["Taxable Value (File 2)"].fillna(0)

# --- Step 5: Save to Excel ---
merged_df.to_excel("/home/thrymr/Downloads/hesaathi_taxable_summary_with_state_districtaug.xlsx", index=False)

print("✅ Output saved as 'hesaathi_taxable_summary_with_state_district.xlsx'")