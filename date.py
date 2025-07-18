# import pandas as pd
# import os

# # List of Excel file paths
# file_paths = [
#     "/home/thrymr/Downloads/Dec_Sales_24-25(Final)_Part1.xlsx",
#     "/home/thrymr/Downloads/Dec_Sales_24-25(Final)_Part2.xlsx",
#     "/home/thrymr/Downloads/Dec_Sales_24-25(Final)_Part3.xlsx",
#     "/home/thrymr/Downloads/Jan_Sales_24-25(Final)_Part1.xlsx",
#     "/home/thrymr/Downloads/Feb_Sales_24-25(Final)_Part1.xlsx",
#     "/home/thrymr/Downloads/Feb_Sales_24-25(Final)_Part2.xlsx",
#     "/home/thrymr/Downloads/Feb_Sales_24-25(Final)_Part3.xlsx",
#     "/home/thrymr/Downloads/Mar_Sales_24-25(Final)_Part1.xlsx",
#     "/home/thrymr/Downloads/Mar_Sales_24-25(Final)_Part2.xlsx",
#     "/home/thrymr/Downloads/Mar_Sales_24-25(Final)_Part3.xlsx"

# ]

# for path in file_paths:
#     if os.path.exists(path):
#         try:
#             df = pd.read_excel(path)
#             if "Date" in df.columns:
#                 df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True).dt.date
#                 df.to_excel(path, index=False)
#                 print(f"✅ Processed: {os.path.basename(path)}")
#             else:
#                 print(f"⚠️ 'Date' column not found in: {os.path.basename(path)}")
#         except Exception as e:
#             print(f"❌ Error processing {os.path.basename(path)}: {e}")
#     else:
#         print(f"🚫 File not found: {path}")

import pandas as pd

# Load the Excel file with possible duplicates
input_path = "/home/thrymr/Downloads/unmatched_low_gst_new_products.xlsx"
df = pd.read_excel(input_path)

# Drop exact duplicate rows (all columns must match)
df_cleaned = df.drop_duplicates()

# Save the cleaned data to a new Excel file
output_path = "/home/thrymr/Downloads/unmatched_low_gst_new_products_deduplicated.xlsx"
df_cleaned.to_excel(output_path, index=False)

print(f"✅ Duplicates removed and saved to: {output_path}")
