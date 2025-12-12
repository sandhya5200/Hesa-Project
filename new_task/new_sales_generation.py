# import pandas as pd
# from random import randint, sample

# # -----------------------------
# # Load your files
# # -----------------------------
# consumer_path = "/home/thrymr/Downloads/consumer.xlsx"
# agri_path = "/home/thrymr/Downloads/agri.xlsx"

# df_consumer = pd.read_excel(consumer_path)
# df_agri = pd.read_excel(agri_path)

# # -----------------------------
# # Merge & sort
# # -----------------------------
# df = pd.concat([df_consumer, df_agri], ignore_index=True)
# df["Date"] = pd.to_datetime(df["Date"])
# df = df.sort_values("Date").reset_index(drop=True)

# # -----------------------------
# # DELETE & RENAME columns
# # -----------------------------
# df = df.drop(columns=["Product Qty", "Taxable Value"], errors="ignore")

# df = df.rename(columns={
#     "Helper Qty": "Product Qty",
#     "Helper Value": "Taxable Value"
# })

# # -----------------------------
# # DELETE old discount columns
# # -----------------------------
# df = df.drop(columns=["Disc_percent", "Disc PU"], errors="ignore")

# # -----------------------------
# # Generate Discount columns
# # -----------------------------
# df["Disc PU"] = df["MRP"] - (df["Net Price PU"] * (1 + df["gst_rate"]))
# df["Disc_percent"] = (df["Disc PU"] / df["MRP"]) * 100

# # -----------------------------
# # Delete old GST columns
# # -----------------------------
# df = df.drop(columns=["igst", "cgst", "sgst", "Total"], errors="ignore")

# # -----------------------------
# # Generate new GST columns
# # -----------------------------
# df["igst"] = 0.0
# df["cgst"] = (df["Taxable Value"] * df["gst_rate"] / 2).round(2)
# df["sgst"] = df["cgst"]
# df["Total"] = (df["Taxable Value"] + df["cgst"] + df["sgst"]).round(2)

# # -----------------------------
# # Fill blank Hesaathi Code
# # -----------------------------
# df["Assigned Hesaathi Code"] = df["Assigned Hesaathi Code"].fillna("HS-CO")
# df.loc[df["Assigned Hesaathi Code"] == "", "Assigned Hesaathi Code"] = "HS-CO"

# # -----------------------------
# # DELETE specific columns
# # -----------------------------
# df = df.drop(columns=["Customer ID", "Invoice No", "Order ID", "Dummy Invoice"], errors="ignore")

# # =========================================================
# #      GENERATE CUSTOMER ID
# # =========================================================
# def generate_customer_ids(df):
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

#         else:    # > 10
#             cids = sample(range(1, 51), 3)
#             cid1 = base + f"{cids[0]:04d}"
#             cid2 = base + f"{cids[1]:04d}"
#             cid3 = base + f"{cids[2]:04d}"
#             third = count // 3
#             df.loc[group.index[:third], "Customer ID"] = cid1
#             df.loc[group.index[third:2*third], "Customer ID"] = cid2
#             df.loc[group.index[2*third:], "Customer ID"] = cid3

#     return df

# df = generate_customer_ids(df)

# # =========================================================
# #      GENERATE INVOICE NO & ORDER ID
# # =========================================================
# def generate_invoice_numbers(df):
#     df["Invoice No"] = None
#     df["Order ID"] = None
    
#     order_counter = 1
#     ag_counter = 1
#     cg_counter = 1
    
#     for (date, cid, vertical), group in df.groupby(["Date", "Customer ID", "Vertical"]):
        
#         month_str = f"{date.month:02d}"
#         year_str = str(date.year)[-2:]
        
#         if "Commerce Business" in vertical:
#             prefix = "CG"
#             invoice_id = f"HS-INV-{prefix}-{month_str}-{year_str}-{cg_counter:08d}"
#             cg_counter += 1
#         else:
#             prefix = "AG"
#             invoice_id = f"HS-INV-{prefix}-{month_str}-{year_str}-{ag_counter:08d}"
#             ag_counter += 1
        
#         df.loc[group.index, "Invoice No"] = invoice_id
#         df.loc[group.index, "Order ID"] = order_counter
        
#         order_counter += 1
    
#     return df

# df = generate_invoice_numbers(df)

# # -----------------------------
# # FINAL COLUMN ORDER
# # -----------------------------
# final_columns = [
#     "Date",
#     "Vertical",
#     "Sub Vertical",
#     "State",
#     "District",
#     "Product Name",
#     "HSN Code",
#     "Category",
#     "Sub Category",
#     "MRP",
#     "UOM",
#     "Net Price PU",
#     "Product Qty",
#     "Taxable Value",
#     "gst_rate",
#     "Disc_percent",
#     "Disc PU",
#     "Currency",
#     "Facilitator",
#     "igst",
#     "cgst",
#     "sgst",
#     "Total",
#     "Assigned Hesaathi Code",
#     "Assigned Hesaathi Onboarding Month",
#     "Customer ID",
#     "Invoice No",
#     "Order ID",
#     "Zoho Invoice"
# ]

# df = df[final_columns]

# # -----------------------------
# # SAVE SPLIT FILES
# # -----------------------------
# df_agri_out = df[df["Vertical"] == "Agri Business"]
# df_consumer_out = df[df["Vertical"] == "Commerce Business"]

# df_agri_out.to_excel("/home/thrymr/Downloads/OUTPUT_agri.xlsx", index=False)
# df_consumer_out.to_excel("/home/thrymr/Downloads/OUTPUT_consumer.xlsx", index=False)

# print("🎉 DONE! Files saved successfully.")



# here some more changes he want now


# 1) after calculating the Disc PU if that is negative u have to update the Net Price PU by decreasing 20% and calculate the Disc PU and then calculate the Disc_percent
# do until the Disc PU gets positive

# 2) # -----------------------------
# # Fill blank Hesaathi Code
# # -----------------------------
# df["Assigned Hesaathi Code"] = df["Assigned Hesaathi Code"].fillna("HS-CO")
# df.loc[df["Assigned Hesaathi Code"] == "", "Assigned Hesaathi Code"] = "HS-CO"

# here u have to fill HS-HO-SL and the corresponding customer_id column should have CS-HO 

# and replace in the entire column where ever there is HS-CO TO HS-HO-SL and the corresponding customer_id column to CS-HO 


# and while alloting the customer id also neglect the rows where HS-CO is there in the Assigned Hesaathi Code column


# 3) now while alloting the Invoice_id and Order_id generate_invoice_numbers:

# where ever there is 'Zoho Invoice' has data dont allot the invoice number over there leave that cells empty and fill hat cells with zoho invoice and then generate the order id 
# considering that column


# import pandas as pd
# from random import randint, sample

# # -----------------------------
# # Load your files
# # -----------------------------
# consumer_path = "/home/thrymr/Downloads/consumer.xlsx"
# agri_path = "/home/thrymr/Downloads/agri.xlsx"

# df_consumer = pd.read_excel(consumer_path)
# df_agri = pd.read_excel(agri_path)

# # -----------------------------
# # Merge & sort
# # -----------------------------
# df = pd.concat([df_consumer, df_agri], ignore_index=True)
# df["Date"] = pd.to_datetime(df["Date"])
# df = df.sort_values("Date").reset_index(drop=True)

# # -----------------------------
# # DELETE & RENAME columns
# # -----------------------------
# df = df.drop(columns=["Product Qty", "Taxable Value"], errors="ignore")

# df = df.rename(columns={
#     "Helper Qty": "Product Qty",
#     "Helper Value": "Taxable Value"
# })

# # -----------------------------
# # DELETE old discount columns
# # -----------------------------
# df = df.drop(columns=["Disc_percent", "Disc PU"], errors="ignore")

# # =========================================================
# #      FIX NEGATIVE Disc PU (20% price reduction loop)
# # =========================================================
# def fix_negative_discount(row):
#     net_price = row["Net Price PU"]
#     mrp = row["MRP"]
#     gst = row["gst_rate"]

#     # Calculate initial discount
#     disc = mrp - (net_price * (1 + gst))

#     # Loop until discount becomes positive
#     while disc < 0:
#         net_price = net_price * 0.8
#         disc = mrp - (net_price * (1 + gst))

#     return pd.Series([net_price, disc])

# df[["Net Price PU", "Disc PU"]] = df.apply(fix_negative_discount, axis=1)
# df["Disc_percent"] = (df["Disc PU"] / df["MRP"]) * 100

# # -----------------------------
# # Delete old GST columns
# # -----------------------------
# df = df.drop(columns=["igst", "cgst", "sgst", "Total"], errors="ignore")

# # -----------------------------
# # Generate new GST columns
# # -----------------------------
# df["igst"] = 0.0
# df["cgst"] = (df["Taxable Value"] * df["gst_rate"] / 2).round(2)
# df["sgst"] = df["cgst"]
# df["Total"] = (df["Taxable Value"] + df["cgst"] + df["sgst"]).round(2)

# # =========================================================
# #  REPLACE HS-CO WITH HS-HO-SL AND SET CUSTOMER ID = CS-HO
# # =========================================================
# df["Assigned Hesaathi Code"] = df["Assigned Hesaathi Code"].fillna("")
# df.loc[df["Assigned Hesaathi Code"].str.strip() == "", "Assigned Hesaathi Code"] = "HS-CO"

# df.loc[df["Assigned Hesaathi Code"] == "HS-CO", "Assigned Hesaathi Code"] = "HS-HO-SL"

# # Pre-fill Customer ID for HO rows
# df.loc[df["Assigned Hesaathi Code"] == "HS-HO-SL", "Customer ID"] = "CS-HO"

# # Remove these rows from Customer ID grouping
# mask_non_ho = df["Assigned Hesaathi Code"] != "HS-HO-SL"

# df_non_ho = df[mask_non_ho]  # rows eligible for customer ID generation

# # =========================================================
# #      GENERATE CUSTOMER ID for non-HO rows
# # =========================================================
# def generate_customer_ids(df):
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

#         else:
#             cids = sample(range(1, 51), 3)
#             cid1 = base + f"{cids[0]:04d}"
#             cid2 = base + f"{cids[1]:04d}"
#             cid3 = base + f"{cids[2]:04d}"
#             third = count // 3
#             df.loc[group.index[:third], "Customer ID"] = cid1
#             df.loc[group.index[third:2*third], "Customer ID"] = cid2
#             df.loc[group.index[2*third:], "Customer ID"] = cid3

#     return df

# df_non_ho = generate_customer_ids(df_non_ho)

# # Reinsert generated IDs back into main df
# df.loc[mask_non_ho, "Customer ID"] = df_non_ho["Customer ID"]

# # =========================================================
# #    GENERATE INVOICE NO & ORDER ID (Zoho Invoice logic)
# # =========================================================
# # =========================================================
# #      UPDATED ORDER ID + INVOICE LOGIC
# # =========================================================
# df["Invoice No"] = None
# df["Order ID"] = None

# order_counter = 1
# ag_counter = 1
# cg_counter = 1

# # ---- FIRST HANDLE ZOHO INVOICE GROUPS ----
# zoho_groups = df[df["Zoho Invoice"].notna() & (df["Zoho Invoice"] != "")] \
#                 .groupby(["Date", "Zoho Invoice", "Vertical"])

# for (date, zoho_inv, vertical), group in zoho_groups:
#     # Set Invoice No = Zoho Invoice value
#     df.loc[group.index, "Invoice No"] = zoho_inv

#     # Assign Order ID (shared for entire group)
#     df.loc[group.index, "Order ID"] = order_counter
#     order_counter += 1


# # ---- HANDLE NON-ZOHO INVOICE GROUPS ----
# non_zoho_df = df[(df["Zoho Invoice"].isna()) | (df["Zoho Invoice"] == "")]

# non_zoho_groups = non_zoho_df.groupby(["Date", "Customer ID", "Vertical"])

# for (date, cid, vertical), group in non_zoho_groups:

#     month_str = f"{date.month:02d}"
#     year_str = str(date.year)[-2:]

#     # Generate Invoice No for non-zoho rows
#     if "Commerce Business" in vertical:
#         prefix = "CG"
#         invoice_id = f"HS-INV-{prefix}-{month_str}-{year_str}-{cg_counter:08d}"
#         cg_counter += 1
#     else:
#         prefix = "AG"
#         invoice_id = f"HS-INV-{prefix}-{month_str}-{year_str}-{ag_counter:08d}"
#         ag_counter += 1

#     df.loc[group.index, "Invoice No"] = invoice_id

#     # Assign order ID after non-zoho invoice creation
#     df.loc[group.index, "Order ID"] = order_counter
#     order_counter += 1


# # -----------------------------
# # FINAL COLUMN ORDER
# # -----------------------------
# final_columns = [
#     "Date",
#     "Vertical",
#     "Sub Vertical",
#     "State",
#     "District",
#     "Product Name",
#     "HSN Code",
#     "Category",
#     "Sub Category",
#     "MRP",
#     "UOM",
#     "Net Price PU",
#     "Product Qty",
#     "Taxable Value",
#     "gst_rate",
#     "Disc_percent",
#     "Disc PU",
#     "Currency",
#     "Facilitator",
#     "igst",
#     "cgst",
#     "sgst",
#     "Total",
#     "Assigned Hesaathi Code",
#     "Assigned Hesaathi Onboarding Month",
#     "Customer ID",
#     "Invoice No",
#     "Order ID",
#     "Zoho Invoice"
# ]

# df = df[final_columns]

# # -----------------------------
# # SAVE SPLIT FILES
# # -----------------------------
# df[df["Vertical"] == "Agri Business"].to_excel("/home/thrymr/Downloads/OUTPUT_agri.xlsx", index=False)
# df[df["Vertical"] == "Commerce Business"].to_excel("/home/thrymr/Downloads/OUTPUT_consumer.xlsx", index=False)

# print("🎉 DONE! Files saved successfully.")











import pandas as pd
from random import randint, sample

# -----------------------------
# Load your files
# -----------------------------
consumer_path = "/home/thrymr/Downloads/consumer.xlsx"
agri_path = "/home/thrymr/Downloads/agri.xlsx"

df_consumer = pd.read_excel(consumer_path)
df_agri = pd.read_excel(agri_path)

# -----------------------------
# Merge & sort
# -----------------------------
df = pd.concat([df_consumer, df_agri], ignore_index=True)
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date").reset_index(drop=True)

# -----------------------------
# DELETE & RENAME columns
# -----------------------------
df = df.drop(columns=["Product Qty", "Taxable Value"], errors="ignore")

df = df.rename(columns={
    "Helper Qty": "Product Qty",
    "Helper Value": "Taxable Value"
})

# -----------------------------
# DELETE old discount columns
# -----------------------------
df = df.drop(columns=["Disc_percent", "Disc PU"], errors="ignore")

# =========================================================
#      FIX NEGATIVE Disc PU (20% price reduction loop)
# =========================================================
def fix_negative_discount(row):
    net_price = row["Net Price PU"]
    mrp = row["MRP"]
    gst = row["gst_rate"]

    disc = mrp - (net_price * (1 + gst))

    while disc < 0:
        net_price = net_price * 0.8
        disc = mrp - (net_price * (1 + gst))

    return pd.Series([net_price, disc])

df[["Net Price PU", "Disc PU"]] = df.apply(fix_negative_discount, axis=1)
df["Disc_percent"] = (df["Disc PU"] / df["MRP"]) * 100

# -----------------------------
# Delete old GST columns
# -----------------------------
df = df.drop(columns=["igst", "cgst", "sgst", "Total"], errors="ignore")

# -----------------------------
# Generate new GST columns
# -----------------------------
df["igst"] = 0.0
df["cgst"] = (df["Taxable Value"] * df["gst_rate"] / 2)
df["sgst"] = df["cgst"]
df["Total"] = (df["Taxable Value"] + df["cgst"] + df["sgst"])

# =========================================================
#  REPLACE HS-CO WITH HS-HO-SL AND SET CUSTOMER ID = CS-HO
# =========================================================
df["Assigned Hesaathi Code"] = df["Assigned Hesaathi Code"].fillna("")
df.loc[df["Assigned Hesaathi Code"].str.strip() == "", "Assigned Hesaathi Code"] = "HS-CO"

df.loc[df["Assigned Hesaathi Code"] == "HS-CO", "Assigned Hesaathi Code"] = "HS-HO-SL"

df.loc[df["Assigned Hesaathi Code"] == "HS-HO-SL", "Customer ID"] = "CS-HO"

mask_non_ho = df["Assigned Hesaathi Code"] != "HS-HO-SL"
df_non_ho = df[mask_non_ho].copy()

# =========================================================
#      GENERATE CUSTOMER ID for non-HO rows
# =========================================================
def generate_customer_ids(df):
    df["Customer ID"] = None

    for (date, hesaathi), group in df.groupby(["Date", "Assigned Hesaathi Code"]):
        count = len(group)
        base = f"CS-{hesaathi}-"

        if count <= 5:
            cid = base + f"{randint(1, 50):04d}"
            df.loc[group.index, "Customer ID"] = cid

        elif 6 <= count <= 10:
            cids = sample(range(1, 51), 2)
            mid = count // 2
            df.loc[group.index[:mid], "Customer ID"] = base + f"{cids[0]:04d}"
            df.loc[group.index[mid:], "Customer ID"] = base + f"{cids[1]:04d}"

        else:
            cids = sample(range(1, 51), 3)
            third = count // 3
            df.loc[group.index[:third], "Customer ID"] = base + f"{cids[0]:04d}"
            df.loc[group.index[third:2*third], "Customer ID"] = base + f"{cids[1]:04d}"
            df.loc[group.index[2*third:], "Customer ID"] = base + f"{cids[2]:04d}"

    return df

df_non_ho = generate_customer_ids(df_non_ho)
df.loc[mask_non_ho, "Customer ID"] = df_non_ho["Customer ID"]

# =========================================================
#   INVOICE NO ALWAYS GENERATED + NEW ORDER ID GROUP LOGIC
# =========================================================
df["Invoice No"] = None
df["Order ID"] = None

order_counter = 1
ag_counter = 1
cg_counter = 1

# ---- INVOICE ALWAYS GENERATED (Zoho ignored for invoice) ----
invoice_groups = df.groupby(["Date", "Customer ID", "Vertical"])

for (date, cid, vertical), group in invoice_groups:

    month_str = f"{date.month:02d}"
    year_str = str(date.year)[-2:]

    if "Commerce Business" in vertical:
        prefix = "CG"
        invoice_id = f"HS-INV-{prefix}-{month_str}-{year_str}-{cg_counter:08d}"
        cg_counter += 1
    else:
        prefix = "AG"
        invoice_id = f"HS-INV-{prefix}-{month_str}-{year_str}-{ag_counter:08d}"
        ag_counter += 1

    df.loc[group.index, "Invoice No"] = invoice_id


# ---- ORDER ID LOGIC ----
# 1️⃣ Zoho Invoice groups
zoho_groups = df[df["Zoho Invoice"].notna() & (df["Zoho Invoice"] != "")] \
                .groupby(["Date", "Zoho Invoice", "Vertical"])

for (date, zoho_inv, vertical), group in zoho_groups:
    df.loc[group.index, "Order ID"] = order_counter
    order_counter += 1

# 2️⃣ Non-Zoho groups
non_zoho_groups = df[(df["Zoho Invoice"].isna()) | (df["Zoho Invoice"] == "")] \
                    .groupby(["Date", "Customer ID", "Vertical"])

for (date, cid, vertical), group in non_zoho_groups:
    df.loc[group.index, "Order ID"] = order_counter
    order_counter += 1

# -----------------------------
# ROUND ALL NUMERIC COLUMNS
# -----------------------------
round_cols = [
    "Net Price PU", "Disc PU", "Disc_percent",
    "cgst", "sgst", "Total", "Taxable Value"
]

for c in round_cols:
    df[c] = df[c].astype(float).round(2)

# -----------------------------
# FINAL COLUMN ORDER
# -----------------------------
final_columns = [
    "Date", "Vertical", "Sub Vertical", "State", "District",
    "Product Name", "HSN Code", "Category", "Sub Category",
    "MRP", "UOM", "Net Price PU", "Product Qty", "Taxable Value",
    "gst_rate", "Disc_percent", "Disc PU", "Currency", "Facilitator",
    "igst", "cgst", "sgst", "Total",
    "Assigned Hesaathi Code", "Assigned Hesaathi Onboarding Month",
    "Customer ID", "Invoice No", "Order ID", "Zoho Invoice"
]

df = df[final_columns]

# -----------------------------
# SAVE OUTPUT FILES
# -----------------------------
df[df["Vertical"] == "Agri Business"].to_excel("/home/thrymr/Downloads/sales_april_agri_with_zoho.xlsx", index=False)
df[df["Vertical"] == "Commerce Business"].to_excel("/home/thrymr/Downloads/sales_april_consumer_with_zoho.xlsx", index=False)

print("🎉 DONE! Files saved successfully.")
