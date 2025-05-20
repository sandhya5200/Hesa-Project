# import pandas as pd

# # Load the Excel file
# file_path = "/home/thrymr/Downloads/telangana_150_Vendors.xlsx"  # Replace with the actual file path
# data = pd.read_excel(file_path)

# # Initialize the VendorId column
# data['VendorId'] = None

# # Generate VendorId based on District and Sub Vertical
# for district, district_group in data.groupby('District'):
#     for sub_vertical, sub_vertical_group in district_group.groupby('Sub Vertical'):
#         for count, row_index in enumerate(sub_vertical_group.index, start=1):
#             vendor_id = f"HS-VED-{district}-{sub_vertical}-{count:04d}"
#             data.loc[row_index, 'VendorId'] = vendor_id

# # Save the updated file
# output_file = "/home/thrymr/Downloads/telangana_150_Vendors.xlsx"
# data.to_excel(output_file, index=False)

# print(f"Vendor IDs generated and saved to {output_file}")

