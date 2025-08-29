# import pandas as pd

# def calculate_difference_for_all(input_file, output_file):
#     input_df = pd.read_excel(input_file)
#     output_df = pd.read_excel(output_file)

#     # Normalize 'Sub Vertical' and 'District' in both DataFrames
#     input_df['Sub Vertical'] = input_df['Sub Vertical'].astype(str).str.strip().str.lower()
#     output_df['Sub Vertical'] = output_df['Sub Vertical'].astype(str).str.strip().str.lower()
#     output_df['District'] = output_df['District'].astype(str).str.strip().str.lower()

#     # Note: These should also be in lowercase now
#     sub_verticals = ["agri inputs", "market linkages", "value intervention", "fmcg", "white label"]
#     districts = input_df.columns[8:]

#     results = []
#     for sub_vertical in sub_verticals:
#         input_filtered = input_df[input_df['Sub Vertical'] == sub_vertical]

#         for district in districts:
#             district_normalized = str(district).strip().lower()
#             if not pd.api.types.is_numeric_dtype(input_filtered[district]):
#                 print(f"Skipping non-numeric column: {district}")
#                 continue

#             x = input_filtered[district].sum()

#             output_filtered = output_df[
#                 (output_df['Sub Vertical'] == sub_vertical) &
#                 (output_df['District'] == district_normalized)
#             ]

#             if 'Taxable Value' not in output_filtered.columns:
#                 print(f"Error: 'Taxable Value' column not found in the output file for {district}.")
#                 continue

#             y = output_filtered['Taxable Value'].sum()

#             if x == 0:
#                 percentage_difference = "X is zero, cannot calculate."
#             else:
#                 percentage_difference = ((x - y) / x) * 100

#             results.append({
#                 "Sub Vertical": sub_vertical.title(),  # To make output readable
#                 "District": district,
#                 "X (Input)": x,
#                 "Y (Output)": y,
#                 "Percentage Difference": percentage_difference
#             })

#             print(f"Processed Sub Vertical: {sub_vertical}, District: {district}, X: {x}, Y: {y}")

#     results_df = pd.DataFrame(results)
#     return results_df

# input_file = "/home/thrymr/Downloads/Nov sales (1).xlsx"
# output_file = "/home/thrymr/Desktop/purchase_oct-mar(24-25)/dec_final_purchase(24-25).xlsx"

# results_df = calculate_difference_for_all(input_file, output_file)
# results_df.to_excel("/home/thrymr/Downloads/taxable_dec_testing.xlsx", index=False)


#--------------------------------------------------------------------THIS DOWN CODE IS FOR QUANTITY----------------

import pandas as pd

def calculate_difference_for_all(input_file, output_file):
    input_df = pd.read_excel(input_file, sheet_name='Taxable value')
    output_df = pd.read_excel(output_file)

    # Normalize 'Sub Vertical' and 'District' in both DataFrames
    input_df['Sub Vertical'] = input_df['Sub Vertical'].astype(str).str.strip().str.lower()
    output_df['Sub Vertical'] = output_df['Sub Vertical'].astype(str).str.strip().str.lower()
    output_df["District"] = output_df["District"].astype(str).str.strip().str.lower()

    # Also use lowercase sub_verticals list for matching
    sub_verticals = ["agri inputs", "market linkages trading", "fmcg"]
    districts = input_df.columns[8:]

    results = []
    for sub_vertical in sub_verticals:
        input_filtered = input_df[input_df['Sub Vertical'] == sub_vertical]

        # Loop through each district
        for district in districts:
            district_normalized = str(district).strip().lower()
            if not pd.api.types.is_numeric_dtype(input_filtered[district]):
                print(f"Skipping non-numeric column: {district}")
                continue

            x = input_filtered[district].sum()

            output_filtered = output_df[
                (output_df['Sub Vertical'] == sub_vertical) &
                (output_df['District'] == district_normalized)
            ]

            # if 'Product Qty' not in output_filtered.columns:
            #     print(f"Error: 'Product Qty' column not found in the output file for {district}.")
            #     continue

            # y = output_filtered['Product Qty'].sum()

            if 'Taxable Value' not in output_filtered.columns:
                print(f"Error: 'Product Qty' column not found in the output file for {district}.")
                continue

            y = output_filtered['Taxable Value'].sum()

            # Calculate the quantity difference
            if x == 0:
                qty_difference = "X is zero, cannot calculate."
            else:
                qty_difference = x - y

            # Store the result
            results.append({
                "Sub Vertical": sub_vertical.title(),  # For better readability
                "District": district,
                "X (Input)": x,
                "Y (Output)": y,
                "Quantity Difference": qty_difference
            })

            print(f"Processed Sub Vertical: {sub_vertical}, District: {district}, X: {x}, Y: {y}")

    results_df = pd.DataFrame(results)
    return results_df

input_file = "/home/thrymr/Downloads/pivot.xlsx"
output_file = "/home/thrymr/Downloads/aug_3.xlsx"

results_df = calculate_difference_for_all(input_file, output_file)
results_df.to_excel("/home/thrymr/Downloads/TV_testing.xlsx", index=False)
