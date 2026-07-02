# import pandas as pd
# import numpy as np
# from random import randint, sample
# import math

# print("📥 Reading input Excel files...")

# # Step 1: Read and combine the Excel files
# file1 = "/home/thrymr/Downloads/apr_sales_with_hesaathis_part1.xlsx"
# file2 = "/home/thrymr/Downloads/apr_sales_with_hesaathis_part2.xlsx"
# # file3 = "/home/thrymr/Downloads/jan_sales_with_hesaathis_part3.xlsx"


# df1 = pd.read_excel(file1)
# df2 = pd.read_excel(file2)
# # df3 = pd.read_excel(file3)

# print("🔗 Concatenating and sorting data...")

# # Combine and sort
# df = pd.concat([df1, df2], ignore_index=True)
# # df = pd.concat([df1, df2], ignore_index=True)
# df['Date'] = pd.to_datetime(df['Date'])  # Ensure datetime format
# df.sort_values(by='Date', inplace=True)

# # Step 2: Generate Customer IDs
# def generate_customer_ids(df):
#     print("🧾 Generating Customer IDs...")
#     df["Customer ID"] = None

#     for (date, hesaathi), group in df.groupby(["Date", "Assigned Hesaathi Code"]):
#         count = len(group)
#         base = f"CS-{hesaathi}-"
        
#         if count <= 5:
#             cid = base + f"{randint(1, 50):04d}"
#             df.loc[group.index, "Customer ID"] = cid

#         elif 6 <= count <= 10:
#             cids = sample(range(1, 51), 2)
#             cid1 = base + f"{cids[0]:04d}"
#             cid2 = base + f"{cids[1]:04d}"
#             mid = count // 2
#             df.loc[group.index[:mid], "Customer ID"] = cid1
#             df.loc[group.index[mid:], "Customer ID"] = cid2

#         else:  # count > 10
#             cids = sample(range(1, 51), 3)
#             cid1 = base + f"{cids[0]:04d}"
#             cid2 = base + f"{cids[1]:04d}"
#             cid3 = base + f"{cids[2]:04d}"
#             third = count // 3
#             df.loc[group.index[:third], "Customer ID"] = cid1
#             df.loc[group.index[third:2*third], "Customer ID"] = cid2
#             df.loc[group.index[2*third:], "Customer ID"] = cid3

#     return df

# def generate_invoice_numbers(df):
#     """
#     Generate Invoice No (AG & CG separate sequences) and Order ID (continuous integer).
#     Month & Year are taken from the Date column.
#     """
#     print("🧾 Generating Invoice Numbers and Order IDs...")
#     df["Invoice No"] = None
#     df["Order ID"] = None
    
#     # Continuous counter for Order IDs
#     order_counter = 1  
    
#     # Separate counters for AG & CG
#     ag_counter = 1
#     cg_counter = 1
    
#     for (date, cid, vertical), group in df.groupby(["Date", "Customer ID", "Vertical"]):
        
#         # Extract month/year from the first row's Date
#         month_str = f"{date.month:02d}"
#         year_str = str(date.year)[-2:]  # Last 2 digits
        
#         # --- Invoice No (AG / CG) ---
#         if "Commerce Business" in vertical:
#             prefix = "CG"
#             invoice_id = f"HS-INV-{prefix}-{month_str}-{year_str}-{cg_counter:08d}"
#             cg_counter += 1
#         else:
#             prefix = "AG"
#             invoice_id = f"HS-INV-{prefix}-{month_str}-{year_str}-{ag_counter:08d}"
#             ag_counter += 1
        
#         # --- Order ID (integer) ---
#         order_id = order_counter  
        
#         # Assign values
#         df.loc[group.index, "Invoice No"] = invoice_id
#         df.loc[group.index, "Order ID"] = order_id
        
#         order_counter += 1
    
#     return df



# def generate_dummy_invoices(df):
#     """
#     Generate Dummy Invoice:
#     HS-INV-[AG/CG]-[STATE CODE]-[MM]-[YY]-000001
#     """
#     print("🧾 Generating Dummy Invoices...")
#     df["Dummy Invoice"] = None
    
#     # State codes mapping
#     state_codes = {
#         "Telangana": "TG",
#         "Maharashtra": "MH",
#         "Odisha": "OD",
#         "Karnataka": "KA",
#         "Tamil Nadu": "TN",
#         "Madhya Pradesh": "MP",
#         "Andhra Pradesh": "AP"
#     }
    
#     # Dictionary to hold counters for Dummy Invoice (per prefix + state + month/year)
#     dummy_counters = {}
    
#     for (date, cid, vertical, state), group in df.groupby(["Date", "Customer ID", "Vertical", "State"]):
        
#         # Determine AG or CG
#         if "Commerce Business" in vertical:
#             prefix = "CG"
#         else:
#             prefix = "AG"
        
#         # Get state code
#         state_code = state_codes.get(state, "XX")  # Default to 'XX' if not found
        
#         # Extract month/year from Date
#         month_str = f"{date.month:02d}"
#         year_str = str(date.year)[-2:]
        
#         # Key for counter
#         dummy_key = f"{prefix}-{state_code}-{month_str}-{year_str}"
        
#         # Initialize counter if not exists
#         if dummy_key not in dummy_counters:
#             dummy_counters[dummy_key] = 1
        
#         dummy_counter = dummy_counters[dummy_key]
#         dummy_invoice = f"HS-INV-{prefix}-{state_code}-{month_str}-{year_str}-{dummy_counter:06d}"
        
#         # Assign values
#         df.loc[group.index, "Dummy Invoice"] = dummy_invoice
        
#         # Increment for next
#         dummy_counters[dummy_key] += 1
    
#     return df

# df = generate_customer_ids(df)
# df = generate_invoice_numbers(df)    
# df = generate_dummy_invoices(df)


# print("✂️ Splitting DataFrame into chunks of 10 lakh rows...")
# # Define chunk size
# chunk_size = 1_000_000
# # Calculate number of output files
# num_files = math.ceil(len(df) / chunk_size)
# print(f"Total rows: {len(df)}, will generate {num_files} files...")
# # Loop and create files with 10 lakh rows each
# for i in range(num_files):
#     start_row = i * chunk_size
#     end_row = start_row + chunk_size
#     df_chunk = df.iloc[start_row:end_row].reset_index(drop=True)

#     output_path = f"/home/thrymr/Downloads/apr_sales_with_customerids_part{i+1}.xlsx"
    
#     print(f"💾 Saving rows {start_row} to {end_row} into {output_path}...")
#     df_chunk.to_excel(output_path, index=False)

# print("✅ Processing complete. All files saved successfully.")

# import pandas as pd
# from random import randint, sample

# print("=" * 60)
# print("Starting Sales Data Processing...")
# print("=" * 60)

# # -----------------------------
# # Load your files
# # -----------------------------
# print("\n[1/8] Loading input files...")

# agri_path = "/home/thrymr/Downloads/apr_sales_with_hesaathis_part1.xlsx"
# consumer_path = "/home/thrymr/Downloads/apr_sales_with_hesaathis_part2.xlsx"

# df_consumer = pd.read_excel(consumer_path)
# df_agri = pd.read_excel(agri_path)

# print(f"Consumer rows loaded : {len(df_consumer):,}")
# print(f"Agri rows loaded     : {len(df_agri):,}")

# # -----------------------------
# # Merge & sort
# # -----------------------------
# print("\n[2/8] Merging and sorting data...")

# df = pd.concat([df_consumer, df_agri], ignore_index=True)
# print(f"Total rows after merge: {len(df):,}")

# df["Date"] = pd.to_datetime(df["Date"])
# df = df.sort_values("Date").reset_index(drop=True)

# print("Data sorted successfully.")

# # -----------------------------
# # Remove old discount columns
# # -----------------------------
# print("\n[3/8] Cleaning old discount columns...")

# df = df.drop(columns=["Disc_percent", "Disc PU"], errors="ignore")

# print("Old discount columns removed.")

# # -----------------------------
# # Fix negative discounts
# # -----------------------------
# print("\n[4/8] Recalculating discounts...")

# def fix_negative_discount(row):
#     net_price = row["Net Price PU"]
#     mrp = row["MRP"]
#     gst = row["gst_rate"]

#     disc = mrp - (net_price * (1 + gst))

#     while disc < 0:
#         net_price *= 0.8
#         disc = mrp - (net_price * (1 + gst))

#     return pd.Series([net_price, disc])

# df[["Net Price PU", "Disc PU"]] = df.apply(fix_negative_discount, axis=1)
# df["Disc_percent"] = (df["Disc PU"] / df["MRP"]) * 100

# print("Discount calculation completed.")

# # -----------------------------
# # GST columns
# # -----------------------------
# print("\n[5/8] Regenerating GST columns...")

# df = df.drop(columns=["igst", "cgst", "sgst", "Cgst", "Sgst", "Total"], errors="ignore")

# df["igst"] = 0.0
# df["cgst"] = df["Taxable Value"] * df["gst_rate"] / 2
# df["sgst"] = df["cgst"]
# df["Total"] = df["Taxable Value"] + df["cgst"] + df["sgst"]

# print("GST columns generated.")

# # -----------------------------
# # Hesaathi Cleanup
# # -----------------------------
# print("\n[6/8] Processing Hesaathi Codes...")

# df["Assigned Hesaathi Code"] = df["Assigned Hesaathi Code"].fillna("")
# df.loc[df["Assigned Hesaathi Code"].str.strip() == "", "Assigned Hesaathi Code"] = "HS-CO"
# df.loc[df["Assigned Hesaathi Code"] == "HS-CO", "Assigned Hesaathi Code"] = "HS-HO-SL"
# df.loc[df["Assigned Hesaathi Code"] == "HS-HO-SL", "Customer ID"] = "CS-HO"

# mask_non_ho = df["Assigned Hesaathi Code"] != "HS-HO-SL"
# df_non_ho = df[mask_non_ho].copy()

# print(f"Non-HO records: {len(df_non_ho):,}")

# # -----------------------------
# # Customer IDs
# # -----------------------------
# print("\nGenerating Customer IDs...")

# def generate_customer_ids(data):
#     data["Customer ID"] = None

#     total_groups = data.groupby(["Date","Assigned Hesaathi Code"]).ngroups
#     print(f"Groups to process: {total_groups}")

#     processed = 0

#     for (date, hesaathi), group in data.groupby(["Date","Assigned Hesaathi Code"]):

#         processed += 1
#         if processed % 100 == 0:
#             print(f"Processed {processed}/{total_groups} groups...")

#         cnt = len(group)
#         base = f"CS-{hesaathi}-"

#         if cnt <= 5:
#             cid = base + f"{randint(1,50):04d}"
#             data.loc[group.index, "Customer ID"] = cid

#         elif cnt <= 10:
#             ids = sample(range(1,51),2)
#             mid = cnt // 2
#             data.loc[group.index[:mid], "Customer ID"] = base + f"{ids[0]:04d}"
#             data.loc[group.index[mid:], "Customer ID"] = base + f"{ids[1]:04d}"

#         else:
#             ids = sample(range(1,51),3)
#             third = cnt // 3
#             data.loc[group.index[:third], "Customer ID"] = base + f"{ids[0]:04d}"
#             data.loc[group.index[third:2*third], "Customer ID"] = base + f"{ids[1]:04d}"
#             data.loc[group.index[2*third:], "Customer ID"] = base + f"{ids[2]:04d}"

#     print("Customer ID generation completed.")

#     return data

# df_non_ho = generate_customer_ids(df_non_ho)
# df.loc[mask_non_ho, "Customer ID"] = df_non_ho["Customer ID"]

# # -----------------------------
# # Invoice Generation
# # -----------------------------
# print("\n[7/8] Generating Invoice Numbers...")

# df = df.drop(columns=["Invoice No", "Order ID"], errors="ignore")

# df["Invoice No"] = None
# df["Order ID"] = None

# order_counter = 1
# ag_counter = 1
# cg_counter = 1

# groups = df.groupby(["Date","Customer ID","Vertical"], sort=False)

# print(f"Invoice groups: {groups.ngroups}")

# for i, ((date, customer_id, vertical), group) in enumerate(groups, start=1):

#     if i % 500 == 0:
#         print(f"Invoices generated: {i}/{groups.ngroups}")

#     month = f"{date.month:02d}"
#     year = str(date.year)[-2:]

#     if vertical == "Commerce Business":
#         invoice = f"HS-INV-CG-{month}-{year}-{cg_counter:08d}"
#         cg_counter += 1
#     else:
#         invoice = f"HS-INV-AG-{month}-{year}-{ag_counter:08d}"
#         ag_counter += 1

#     df.loc[group.index, "Invoice No"] = invoice
#     df.loc[group.index, "Order ID"] = order_counter
#     order_counter += 1

# print("Invoice generation completed.")

# # -----------------------------
# # Rounding
# # -----------------------------
# print("\nRounding numeric columns...")

# for col in [
#     "Net Price PU","Disc PU","Disc_percent",
#     "cgst","sgst","Total","Taxable Value"
# ]:
#     df[col] = pd.to_numeric(df[col], errors="coerce").round(2)

# # -----------------------------
# # Save
# # -----------------------------
# print("\n[8/8] Saving output files...")

# agri_rows = len(df[df["Vertical"]=="Agri Business"])
# consumer_rows = len(df[df["Vertical"]=="Commerce Business"])

# df[df["Vertical"]=="Agri Business"].to_excel(
#     "/home/thrymr/Downloads/apr_agri_cleaned_sale_26-27.xlsx",
#     index=False
# )

# print(f"Agri file saved ({agri_rows:,} rows)")

# df[df["Vertical"]=="Commerce Business"].to_excel(
#     "/home/thrymr/Downloads/apr_cons_cleaned_sale_26-27.xlsx",
#     index=False
# )

# print(f"Commerce file saved ({consumer_rows:,} rows)")

# print("\n" + "="*60)
# print("PROCESS COMPLETED SUCCESSFULLY!")
# print(f"Total records processed : {len(df):,}")
# print(f"Total Orders Generated  : {order_counter-1:,}")
# print(f"Agri Invoices           : {ag_counter-1:,}")
# print(f"Commerce Invoices       : {cg_counter-1:,}")
# print("="*60)


import pandas as pd
import numpy as np
from random import randint, sample

print("=" * 60)
print("Starting Sales Data Processing...")
print("=" * 60)

# -----------------------------
# Load your files
# -----------------------------
print("\n[1/8] Loading input files...")

agri_path = "/home/thrymr/Downloads/apr_sales_with_hesaathis_part1.xlsx"
consumer_path = "/home/thrymr/Downloads/apr_sales_with_hesaathis_part2.xlsx"

df_consumer = pd.read_excel(consumer_path)
df_agri = pd.read_excel(agri_path)

print(f"Consumer rows loaded : {len(df_consumer):,}")
print(f"Agri rows loaded     : {len(df_agri):,}")

# -----------------------------
# Merge & sort
# -----------------------------
print("\n[2/8] Merging and sorting data...")

df = pd.concat([df_consumer, df_agri], ignore_index=True)
print(f"Total rows after merge: {len(df):,}")

df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date").reset_index(drop=True)

print("Data sorted successfully.")

# -----------------------------
# Remove old discount columns
# -----------------------------
print("\n[3/8] Cleaning old discount columns...")

df = df.drop(columns=["Disc_percent", "Disc PU"], errors="ignore")

print("Old discount columns removed.")

# -----------------------------
# Fix negative discounts
# -----------------------------
# SAME LOGIC AS BEFORE:
#   disc = mrp - net_price*(1+gst)
#   while disc < 0: net_price *= 0.8; recompute disc
# Vectorized below instead of df.apply(axis=1), but produces identical
# results for every row (same iterative halving-by-0.8 rule).
print("\n[4/8] Recalculating discounts...")

net_price = df["Net Price PU"].to_numpy(dtype=float)
mrp = df["MRP"].to_numpy(dtype=float)
gst = df["gst_rate"].to_numpy(dtype=float)

disc = mrp - net_price * (1 + gst)
needs_fix = disc < 0

# Closed-form equivalent of the while loop: find smallest integer n>=0
# such that mrp - net_price*(0.8**n)*(1+gst) >= 0
with np.errstate(divide="ignore", invalid="ignore"):
    ratio = mrp / (net_price * (1 + gst))
    n_needed = np.ceil(np.log(ratio) / np.log(0.8))

n_needed = np.where(needs_fix, n_needed, 0)
n_needed = np.nan_to_num(n_needed, nan=0, posinf=0, neginf=0)
n_needed = np.maximum(n_needed, 0)

net_price_fixed = net_price * (0.8 ** n_needed)
disc_fixed = mrp - net_price_fixed * (1 + gst)

# Safety net: in rare floating point edge cases the closed form can be
# off by one step from the while loop. Nudge any still-negative rows
# forward exactly like the original while loop would.
still_negative = disc_fixed < 0
while still_negative.any():
    net_price_fixed[still_negative] *= 0.8
    disc_fixed[still_negative] = (
        mrp[still_negative] - net_price_fixed[still_negative] * (1 + gst[still_negative])
    )
    still_negative = disc_fixed < 0

df["Net Price PU"] = net_price_fixed
df["Disc PU"] = disc_fixed
df["Disc_percent"] = (df["Disc PU"] / df["MRP"]) * 100

print("Discount calculation completed.")

# -----------------------------
# GST columns
# -----------------------------
print("\n[5/8] Regenerating GST columns...")

df = df.drop(columns=["igst", "cgst", "sgst", "Cgst", "Sgst", "Total"], errors="ignore")

df["igst"] = 0.0
df["cgst"] = df["Taxable Value"] * df["gst_rate"] / 2
df["sgst"] = df["cgst"]
df["Total"] = df["Taxable Value"] + df["cgst"] + df["sgst"]

print("GST columns generated.")

# -----------------------------
# Hesaathi Cleanup
# -----------------------------
print("\n[6/8] Processing Hesaathi Codes...")

df["Assigned Hesaathi Code"] = df["Assigned Hesaathi Code"].fillna("")
df.loc[df["Assigned Hesaathi Code"].str.strip() == "", "Assigned Hesaathi Code"] = "HS-CO"
df.loc[df["Assigned Hesaathi Code"] == "HS-CO", "Assigned Hesaathi Code"] = "HS-HO-SL"
df.loc[df["Assigned Hesaathi Code"] == "HS-HO-SL", "Customer ID"] = "CS-HO"

mask_non_ho = df["Assigned Hesaathi Code"] != "HS-HO-SL"
df_non_ho = df[mask_non_ho].copy()

print(f"Non-HO records: {len(df_non_ho):,}")

# -----------------------------
# Customer IDs
# -----------------------------
# SAME LOGIC AS BEFORE (group-size tiers: <=5 -> 1 id, <=10 -> 2 ids,
# else -> 3 ids, split evenly across the group's row order).
# Uses groupby(...).indices (positions) instead of iterating full
# group DataFrames + repeated .loc writes, which is what was slow.
print("\nGenerating Customer IDs...")

def generate_customer_ids(data):
    data = data.reset_index(drop=True)
    n = len(data)
    customer_ids = np.empty(n, dtype=object)

    grouped = data.groupby(["Date", "Assigned Hesaathi Code"], sort=False).indices
    total_groups = len(grouped)
    print(f"Groups to process: {total_groups}")

    processed = 0
    for (date, hesaathi), idx in grouped.items():
        processed += 1
        if processed % 100 == 0:
            print(f"Processed {processed}/{total_groups} groups...")

        cnt = len(idx)
        base = f"CS-{hesaathi}-"

        if cnt <= 5:
            cid = base + f"{randint(1,50):04d}"
            customer_ids[idx] = cid

        elif cnt <= 10:
            ids = sample(range(1, 51), 2)
            mid = cnt // 2
            customer_ids[idx[:mid]] = base + f"{ids[0]:04d}"
            customer_ids[idx[mid:]] = base + f"{ids[1]:04d}"

        else:
            ids = sample(range(1, 51), 3)
            third = cnt // 3
            customer_ids[idx[:third]] = base + f"{ids[0]:04d}"
            customer_ids[idx[third:2*third]] = base + f"{ids[1]:04d}"
            customer_ids[idx[2*third:]] = base + f"{ids[2]:04d}"

    print("Customer ID generation completed.")
    data["Customer ID"] = customer_ids
    return data

df_non_ho = generate_customer_ids(df_non_ho)
df.loc[mask_non_ho, "Customer ID"] = df_non_ho["Customer ID"].to_numpy()

# -----------------------------
# Invoice Generation
# -----------------------------
# SAME LOGIC AS BEFORE (one invoice number per (Date, Customer ID,
# Vertical) group; separate AG/CG counters; one Order ID per group).
# Uses groupby(...).indices + numpy array writes instead of per-group
# .loc writes into the full DataFrame.
print("\n[7/8] Generating Invoice Numbers...")

df = df.drop(columns=["Invoice No", "Order ID"], errors="ignore")

n = len(df)
invoice_arr = np.empty(n, dtype=object)
order_arr = np.empty(n, dtype=np.int64)

order_counter = 1
ag_counter = 1
cg_counter = 1

grouped = df.groupby(["Date", "Customer ID", "Vertical"], sort=False).indices
total_invoice_groups = len(grouped)
print(f"Invoice groups: {total_invoice_groups}")

for i, ((date, customer_id, vertical), idx) in enumerate(grouped.items(), start=1):
    if i % 500 == 0:
        print(f"Invoices generated: {i}/{total_invoice_groups}")

    month = f"{date.month:02d}"
    year = str(date.year)[-2:]

    if vertical == "Commerce Business":
        invoice = f"HS-INV-CG-{month}-{year}-{cg_counter:08d}"
        cg_counter += 1
    else:
        invoice = f"HS-INV-AG-{month}-{year}-{ag_counter:08d}"
        ag_counter += 1

    invoice_arr[idx] = invoice
    order_arr[idx] = order_counter
    order_counter += 1

df["Invoice No"] = invoice_arr
df["Order ID"] = order_arr

print("Invoice generation completed.")

# -----------------------------
# Rounding
# -----------------------------
print("\nRounding numeric columns...")

for col in [
    "Net Price PU", "Disc PU", "Disc_percent",
    "cgst", "sgst", "Total", "Taxable Value"
]:
    df[col] = pd.to_numeric(df[col], errors="coerce").round(2)

# -----------------------------
# Save
# -----------------------------
print("\n[8/8] Saving output files...")

agri_rows = len(df[df["Vertical"] == "Agri Business"])
consumer_rows = len(df[df["Vertical"] == "Commerce Business"])

df[df["Vertical"] == "Agri Business"].to_excel(
    "/home/thrymr/Downloads/aprcheck_agri_cleaned_sale_26-27.xlsx",
    index=False
)

print(f"Agri file saved ({agri_rows:,} rows)")

df[df["Vertical"] == "Commerce Business"].to_excel(
    "/home/thrymr/Downloads/aprcheck_cons_cleaned_sale_26-27.xlsx",
    index=False
)

print(f"Commerce file saved ({consumer_rows:,} rows)")

print("\n" + "=" * 60)
print("PROCESS COMPLETED SUCCESSFULLY!")
print(f"Total records processed : {len(df):,}")
print(f"Total Orders Generated  : {order_counter-1:,}")
print(f"Agri Invoices           : {ag_counter-1:,}")
print(f"Commerce Invoices       : {cg_counter-1:,}")
print("=" * 60)



