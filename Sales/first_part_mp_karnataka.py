# import pandas as pd
# import random
# from datetime import datetime, timedelta

# input_file = '/home/thrymr/Downloads/to_know.xlsx'
# output_file = '/home/thrymr/Downloads/karnataka_maharshtra_separate_output.xlsx'

# # Constants
# district_data = {
#     "Karnataka": "Bidar, Ballari, Kalabuargi, Koppal, Raichur, Yadagiri, Vijayanagara",
#     "Madhya Pradesh": "Ujjain, Dhar, Kukshi, Indore, Dewas",
# }

# subvertical_data = {
#     "Agri Inputs": [0, 0.05, 0.12, 0.18],
#     "FMCG": [0, 0.05, 0.12, 0.18],
#     "Market Linkages Trading": [0, 0.05, 0.18],
#     "Market Linkages Value Intervention": [0],
#     "White Label": [0, 0.05]
# }

# gst_distribution_pct = {
#     0: 65,
#     0.05: 20,
#     0.12: 10,
#     0.18: 5
# }


# def pick_random_gst(sub_vertical):
#     allowed_rates = subvertical_data.get(sub_vertical, [0])
#     gst_candidates = [rate for rate in allowed_rates if rate != 0]
#     if not gst_candidates:
#         return 0
#     weights = [gst_distribution_pct.get(rate, 1) for rate in gst_candidates]
#     return random.choices(gst_candidates, weights=weights, k=1)[0]

# def random_date_in_april_2025():
#     start_date = datetime(2025, 5, 1)
#     end_date = datetime(2025, 5, 31)
#     delta = end_date - start_date
#     random_days = random.randint(0, delta.days)
#     return (start_date + timedelta(days=random_days)).date()



# def distribute_amount(row):
#     results = []
#     vertical = row['Vertical']
#     sub_vertical = row['Sub Vertical']
#     state = row['State']
#     amount_crore = row["May'25"]
#     amount = amount_crore * 1_00_00_000

#     districts = [d.strip() for d in district_data[state].split(',')]
#     random.shuffle(districts)

#     per_district_amount = amount / len(districts)

#     for district in districts:
#         gst_fraction = random.uniform(0.002, 0.05)
#         gst_amount_total = per_district_amount * gst_fraction
#         major_amount = per_district_amount - gst_amount_total

#         # Random number of sub-lines (1–4)
#         num_sub_lines = random.randint(1, 4)
#         subline_allocations = [random.random() for _ in range(num_sub_lines)]
#         total_alloc = sum(subline_allocations)
#         subline_allocations = [gst_amount_total * (x / total_alloc) for x in subline_allocations]

#         # Major line (GST 0)
#                 # Major line (GST 0)
#         results.append({
#             "Date": random_date_in_april_2025(),
#             "State": state,
#             "District": district,
#             "Vertical": vertical,
#             "Sub Vertical": sub_vertical,
#             "Taxable Value": round(major_amount, 2),
#             "GST Rate": 0,
#             "igst": 0,
#             "cgst": 0,
#             "sgst": 0,
#             "Total": round(major_amount, 2),
#         })

#         # Sub-lines with GST
#         for sub_amt in subline_allocations:
#             gst_rate = pick_random_gst(sub_vertical)
#             cgst = sub_amt * gst_rate / 2
#             sgst = sub_amt * gst_rate / 2
#             total = sub_amt + cgst + sgst
#             results.append({
#                 "Date": random_date_in_april_2025(),
#                 "State": state,
#                 "District": district,
#                 "Vertical": vertical,
#                 "Sub Vertical": sub_vertical,
#                 "Taxable Value": round(sub_amt, 2),
#                 "GST Rate": gst_rate,
#                 "igst": 0,
#                 "cgst": round(cgst, 2),
#                 "sgst": round(sgst, 2),
#                 "Total": round(total, 2),
#             })


#     return results


# def main():
#     df = pd.read_excel(input_file)
#     output_rows = []

#     for _, row in df.iterrows():
#         distributed = distribute_amount(row)
#         output_rows.extend(distributed)

#     out_df = pd.DataFrame(output_rows)
#     out_df.to_excel(output_file, index=False)
#     print(f"Output written to {output_file}")


# if __name__ == "__main__":
#     main()

