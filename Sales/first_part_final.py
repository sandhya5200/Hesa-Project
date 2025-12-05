# import pandas as pd

# file1 = "/home/thrymr/Downloads/karnataka_maharshtra_separate_output.xlsx"
# file2 = "/home/thrymr/Downloads/output_first_part_April.xlsx"

# df1 = pd.read_excel(file1)
# df2 = pd.read_excel(file2)

# merged_df = pd.concat([df1, df2], ignore_index=True)

# merged_df['Date'] = pd.to_datetime(merged_df['Date'])
# merged_df = merged_df.sort_values(by='Date')

# merged_df['Month'] = "Apr'25"

# final_df = merged_df[[
#     'Date', 'State', 'District', 'Vertical', 'Sub Vertical',
#     'Taxable Value', 'GST Rate', 'igst', 'cgst', 'sgst', 'Total', 'Month'
# ]]


# output_path = "/home/thrymr/Downloads/final_output_April.xlsx"
# final_df.to_excel(output_path, index=False)

# print(f"Final merged file saved to: {output_path}")

