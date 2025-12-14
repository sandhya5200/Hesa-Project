import pandas as pd
from random import randint, sample

# -----------------------------
# Load your files
# -----------------------------
consumer_path = r"c:\Users\ksand\Downloads\agri.xlsx"
agri_path = r"c:\Users\ksand\Downloads\consumer.xlsx"

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
# df["Invoice No"] = None
# df["Order ID"] = None

# order_counter = 1
# ag_counter = 1
# cg_counter = 1

# # ---- INVOICE ALWAYS GENERATED (Zoho ignored for invoice) ----
# invoice_groups = df.groupby(["Date", "Customer ID", "Vertical"])

# for (date, cid, vertical), group in invoice_groups:

#     month_str = f"{date.month:02d}"
#     year_str = str(date.year)[-2:]

#     if "Commerce Business" in vertical:
#         prefix = "CG"
#         invoice_id = f"HS-INV-{prefix}-{month_str}-{year_str}-{cg_counter:08d}"
#         cg_counter += 1
#     else:
#         prefix = "AG"
#         invoice_id = f"HS-INV-{prefix}-{month_str}-{year_str}-{ag_counter:08d}"
#         ag_counter += 1

#     df.loc[group.index, "Invoice No"] = invoice_id

# =========================================================
#   INVOICE NO ALWAYS GENERATED + NEW ORDER ID GROUP LOGIC
# =========================================================
df["Invoice No"] = None
df["Order ID"] = None

order_counter = 1

# 🔹 IMPORTANT: start counters from existing max if needed
ag_counter = 1
cg_counter = 1

# ---- INVOICE ALWAYS GENERATED (Zoho CONTROLS COUNTER) ----
invoice_groups = df.groupby(
    ["Date", "Customer ID", "Vertical", "Zoho Invoice"],
    dropna=False
)

for (date, cid, vertical, zoho_inv), group in invoice_groups:

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
df[df["Vertical"] == "Agri Business"].to_excel(r"c:\Users\ksand\Downloads\april_agri_cleaned_sale.xlsx", index=False)
df[df["Vertical"] == "Commerce Business"].to_excel(r"c:\Users\ksand\Downloads\april_cons_cleaned_sale.xlsx", index=False)

print("🎉 DONE! Files saved successfully.")
