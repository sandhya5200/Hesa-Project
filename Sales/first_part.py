import pandas as pd

sample_df = pd.read_excel("/home/thrymr/Important/output_summary_April.xlsx")
projections_df = pd.read_excel("/home/thrymr/Important/projections_for_sales_25-26.xlsx")

projections_df.rename(columns={"Nov'25": "projected_amount_cr"}, inplace=True) ####################---CHANGE---############################
projections_df['projected_amount'] = projections_df['projected_amount_cr'] * 1_00_00_000

merged_df = pd.merge(
    sample_df,
    projections_df[['Vertical', 'Sub Vertical', 'State', 'projected_amount']],
    on=['Vertical', 'Sub Vertical', 'State'],
    how='left'
)

merged_df = merged_df.dropna(subset=['projected_amount'])
group_totals = merged_df.groupby(['Vertical', 'Sub Vertical', 'State'])['percentage_of_total'].transform('sum')
merged_df['normalized_percentage'] = merged_df['percentage_of_total'] / group_totals

merged_df['Taxable_Amount'] = (merged_df['normalized_percentage'] * merged_df['projected_amount']).round(2)

merged_df.rename(columns={'GST Rate': 'gst_rate'}, inplace=True)

merged_df['Date'] = pd.to_datetime(merged_df['Date'])
merged_df['Date'] = merged_df['Date'].apply(lambda d: pd.Timestamp(year=2025, month=11, day=d.day))   #############---CHANGE---###############

merged_df["Cohort"] = "Nov'25"  #######################---CHANGE---#####################


# merged_df['igst'] = 0 
# merged_df['cgst'] = round(merged_df['Taxable_Amount'] * merged_df['gst_rate'] / 2, 2)
# merged_df['sgst'] = round(merged_df['Taxable_Amount'] * merged_df['gst_rate'] / 2, 2)
# merged_df['Total'] = round(merged_df['Taxable_Amount'] + merged_df['cgst'] + merged_df['sgst'], 2)



merged_df.rename(columns={'gst_rate': 'GST Rate'}, inplace=True)

final_df = merged_df[[
    'Date', 'Vertical', 'Sub Vertical', 'State', 'District',
    'GST Rate', 'percentage_of_total', 'normalized_percentage',
    'Taxable_Amount'
]]

# final_df.to_excel("/home/thrymr/Downloads/output_first_part_july.xlsx", index=False)

agri_df = final_df[final_df['Vertical'] == 'Agri Business']
agri_df.to_excel("/home/thrymr/Downloads/output_agri_Nov.xlsx", index=False)

consumer_df = final_df[final_df['Vertical'] == 'Commerce Business']
consumer_df.to_excel("/home/thrymr/Downloads/output_cons_Nov.xlsx", index=False)


