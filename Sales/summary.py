# import pandas as pd

# # ----------- INPUT FILES ----------------
# file1 = "/home/thrymr/Desktop/input Files(2024-2025)_first_six_months_only/original_sales(24-25)(6months agri,cons)/Agri Sales May-24.xlsx"
# file2 = "/home/thrymr/Desktop/input Files(2024-2025)_first_six_months_only/original_sales(24-25)(6months agri,cons)/Consumer Sales - May 2024.xlsx"

# df_list = []

# def load_and_clean(path):
#     """Load all sheets and fix column names"""
#     xls = pd.ExcelFile(path)
#     for sheet in xls.sheet_names:
#         df = pd.read_excel(path, sheet_name=sheet)

#         # Fix wrong spelling inside each sheet BEFORE concat
#         df = df.rename(columns={
#             "Customer Distict": "Customer District",    # wrong → correct
#             "Customer  Distict": "Customer District",   # any extra space case
#             "Customer_Distict": "Customer District"
#         })

#         # Clean column names (normalize)
#         df.columns = df.columns.str.strip()

#         df_list.append(df)

# # Load both files
# load_and_clean(file1)
# load_and_clean(file2)

# # ----------- COMBINE ALL SHEETS ----------------
# df = pd.concat(df_list, ignore_index=True)

# # Ensure Customer District exists
# if "Customer District" not in df.columns:
#     raise Exception("❌ Neither 'Customer District' nor 'Customer Distict' found!")

# # ----------- GROUPING ----------------
# grouped = df.groupby(
#     ['Date', 'Vertical', 'Sub Vertical', 'Customer State', 'Customer District', 'GST Rate'],
#     as_index=False
# )['Taxable Value'].sum()

# # ----------- CALCULATE PERCENTAGE ----------------
# total_taxable = df['Taxable Value'].sum()
# grouped['percentage_of_total'] = (grouped['Taxable Value'] / total_taxable) * 100

# # ----------- ROUNDING ----------------
# grouped['Taxable Value'] = grouped['Taxable Value'].round(2)
# grouped['percentage_of_total'] = grouped['percentage_of_total'].round(10)

# # ----------- SAVE OUTPUT ----------------
# output_file = "/home/thrymr/Downloads/output_sales_summary.xlsx"
# grouped.to_excel(output_file, index=False)

# print("Summary file created:", output_file)
