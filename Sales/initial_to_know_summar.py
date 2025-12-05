import pandas as pd

# Load your Excel file
df = pd.read_excel("/home/thrymr/Downloads/output_summary_feb.xlsx")

# Group by state, district, sub_vertical, gst_rate and sum taxable_value
grouped = df.groupby(
    ['Date', 'Vertical', 'Sub Vertical', 'State', 'District', 'GST Rate'],
    as_index=False
)['Taxable Value'].sum()

# Calculate overall total
total_taxable = df['Taxable Value'].sum()

# Add percentage column
grouped['percentage_of_total'] = (grouped['Taxable Value'] / total_taxable) * 100

# Round for better readability
grouped['percentage_of_total'] = grouped['percentage_of_total'].round(100)
grouped['Taxable Value'] = grouped['Taxable Value'].round(100)

# Save to Excel
grouped.to_excel("/home/thrymr/Important/output_summary_Feb.xlsx", index=False)