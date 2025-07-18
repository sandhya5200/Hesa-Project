import pandas as pd

# --- Step 1: Load the two Excel files ---
file1 = "/home/thrymr/Desktop/sales 25-26/sales_with_hesaathis_part1.xlsx"  # Replace with your actual path
file2 = "/home/thrymr/Desktop/sales 25-26/sales_with_hesaathis_part2.xlsx"

df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

# --- Step 2: Group by Hesaathi Code and calculate sum of Taxable Value ---
grouped_df1 = df1.groupby("Hesaathi Code", as_index=False)["Taxable Value"].sum()
grouped_df1.rename(columns={"Taxable Value": "Taxable Value (File 1)"}, inplace=True)

grouped_df2 = df2.groupby("Hesaathi Code", as_index=False)["Taxable Value"].sum()
grouped_df2.rename(columns={"Taxable Value": "Taxable Value (File 2)"}, inplace=True)

# --- Step 3: Merge both summaries on Hesaathi Code (Optional) ---
merged_df = pd.merge(grouped_df1, grouped_df2, on="Hesaathi Code", how="outer")

# --- Step 4: Save to Excel ---
merged_df.to_excel("/home/thrymr/hesaathi_taxable_summary.xlsx", index=False)

print("✅ Output saved as 'hesaathi_taxable_summary.xlsx")
