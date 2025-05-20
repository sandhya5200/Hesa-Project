import pandas as pd

# Load input files
sample_df = pd.read_excel("/home/thrymr/Downloads/output_summary_september.xlsx")
projections_df = pd.read_excel("/home/thrymr/Downloads/projections_input_without_karnataka&mp.xlsx")

# Rename and convert amount
projections_df.rename(columns={"Apr'25": "projected_amount_cr"}, inplace=True)
projections_df['projected_amount'] = projections_df['projected_amount_cr'] * 1_00_00_000

# Merge projection data into sample
merged_df = pd.merge(
    sample_df,
    projections_df[['Vertical', 'Sub Vertical', 'State', 'projected_amount']],
    on=['Vertical', 'Sub Vertical', 'State'],
    how='left'
)

# Drop rows with missing projections
merged_df = merged_df.dropna(subset=['projected_amount'])

# Normalize percentages within each group
group_totals = merged_df.groupby(['Vertical', 'Sub Vertical', 'State'])['percentage_of_total'].transform('sum')
merged_df['normalized_percentage'] = merged_df['percentage_of_total'] / group_totals

# Allocate amount
merged_df['Taxable_Amount'] = (merged_df['normalized_percentage'] * merged_df['projected_amount']).round(2)

# Fix GST Rate column name (lowercase)
merged_df.rename(columns={'GST Rate': 'gst_rate'}, inplace=True)

# Replace all dates with the same day in April 2025
merged_df['Date'] = pd.to_datetime(merged_df['Date'])
merged_df['Date'] = merged_df['Date'].apply(lambda d: pd.Timestamp(year=2025, month=4, day=d.day))

# Calculate GST components
merged_df['igst'] = 0  # IGST is 0 in this logic
merged_df['cgst'] = round(merged_df['Taxable_Amount'] * merged_df['gst_rate'] / 2, 2)
merged_df['sgst'] = round(merged_df['Taxable_Amount'] * merged_df['gst_rate'] / 2, 2)
merged_df['Total'] = round(merged_df['Taxable_Amount'] + merged_df['cgst'] + merged_df['sgst'], 2)

merged_df.rename(columns={'gst_rate': 'GST Rate'}, inplace=True)



# Select final columns
final_df = merged_df[[
    'Date', 'Vertical', 'Sub Vertical', 'State', 'District',
    'GST Rate', 'percentage_of_total', 'normalized_percentage',
    'Taxable_Amount', 'igst', 'cgst', 'sgst', 'Total'
]]

# Save to output file
final_df.to_excel("/home/thrymr/Downloads/output_first_part_April.xlsx", index=False)


