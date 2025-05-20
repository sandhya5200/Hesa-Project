# import pandas as pd

# def calculate_difference_for_all(input_file, output_file):
#     input_df = pd.read_excel(input_file)
#     output_df = pd.read_excel(output_file)


#     output_df["District"] = output_df["District"].astype(str).str.strip().str.lower()

#     sub_verticals = ["Agri inputs", "Market Linkages", "Value Intervention", "Fmcg", "White Label"]
#     districts = input_df.columns[8:]

#     results = []
#     for sub_vertical in sub_verticals:
#         input_filtered = input_df[input_df['Sub Vertical'] == sub_vertical]

#         # Loop through each district
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

#             # Calculate the percentage difference
#             if x == 0:
#                 percentage_difference = "X is zero, cannot calculate."
#             else:
#                 percentage_difference = ((x - y) / x) * 100

#             # Store the result
#             results.append({
#                 "Sub Vertical": sub_vertical,
#                 "District": district,
#                 "X (Input)": x,
#                 "Y (Output)": y,
#                 "Percentage Difference": percentage_difference
#             })

#             print(f"Processed Sub Vertical: {sub_vertical}, District: {district}, X: {x}, Y: {y}")

#     results_df = pd.DataFrame(results)
#     return results_df

# input_file = "/home/thrymr/Downloads/Agri sales taxable feb-25.xlsx"
# output_file = "/home/thrymr/Downloads/Puchase_Agri_Feb_24-25.xlsx"

# results_df = calculate_difference_for_all(input_file, output_file)
# results_df.to_excel("/home/thrymr/Downloads/taxable_feb_testing.xlsx", index=False)

# print("Results saved to 'xyz.xlsx'")

#--------------------------------------------------------------------THIS DOWN CODE IS FOR QUANTITY----------------

import pandas as pd

def calculate_difference_for_all(input_file, output_file):
    input_df = pd.read_excel(input_file)
    output_df = pd.read_excel(output_file)


    output_df["District"] = output_df["District"].astype(str).str.strip().str.lower()

    sub_verticals = ["Agri inputs", "Market Linkages", "Value Intervention", "Fmcg", "White Label"]
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

            if 'Product Qty' not in output_filtered.columns:
                print(f"Error: 'Product Qty' column not found in the output file for {district}.")
                continue

            y = output_filtered['Product Qty'].sum()

            # Calculate the percentage difference
            if x == 0:
                qty_difference = "X is zero, cannot calculate."
            else:
                qty_difference = x-y

            # Store the result
            results.append({
                "Sub Vertical": sub_vertical,
                "District": district,
                "X (Input)": x,
                "Y (Output)": y,
                "Quantity difference": qty_difference
            })

            print(f"Processed Sub Vertical: {sub_vertical}, District: {district}, X: {x}, Y: {y}")

    results_df = pd.DataFrame(results)
    return results_df

input_file = "/home/thrymr/Downloads/FEB -Quantity.xlsx"
output_file = "/home/thrymr/Downloads/Puchase_Agri_Feb_24-25.xlsx"

results_df = calculate_difference_for_all(input_file, output_file)
results_df.to_excel("/home/thrymr/Downloads/QTY_feb_testing.xlsx", index=False)

print("Results saved to 'xyz.xlsx'")