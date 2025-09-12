# import pandas as pd
# import random
# import calendar

# # Input data
# data = {
#     "Month-Year": ["05-20", "06-20", "07-20", "09-20", "11-20", "12-20"],
#     "Total": [623694.60, 288381.60, 158085.00, 189520.20, 89100.00, 143820.00]
# }

# df = pd.DataFrame(data)

# # Function to split amount into 7–8 random parts
# def split_amount(total, n_parts, max_value=250000):
#     parts = []
#     remaining = total
#     for i in range(n_parts - 1):
#         # Ensure no part exceeds max and leaves enough for remaining parts
#         max_possible = min(max_value, remaining - (n_parts - i - 1))
#         part = round(random.uniform(1, max_possible / (n_parts - i)), 2)
#         parts.append(part)
#         remaining -= part
#     parts.append(round(remaining, 2))  # Last part = remaining
#     return parts

# rows = []

# for _, row in df.iterrows():
#     month, year = row["Month-Year"].split("-")
#     year = int("20" + year)  # convert to full year e.g. 2020
#     month = int(month)
    
#     # Pick random 7–8 dates
#     n_parts = random.randint(7, 8)
#     days_in_month = calendar.monthrange(year, month)[1]
#     dates = random.sample(range(1, days_in_month + 1), n_parts)
#     dates.sort()
    
#     # Split total into random parts
#     splits = split_amount(row["Total"], n_parts)
    
#     for d, amt in zip(dates, splits):
#         taxable = round(amt * 18 / 100, 2)
#         cgst = round(taxable / 2, 2)
#         sgst = round(taxable / 2, 2)
#         rows.append({
#             "Date": f"{year}-{month:02d}-{d:02d}",
#             "Amount": amt,
#             "Taxable_18%": taxable,
#             "CGST_9%": cgst,
#             "SGST_9%": sgst
#         })

# # Final DataFrame
# output_df = pd.DataFrame(rows)

# # Save to Excel
# output_df.to_excel(r"c:\Users\ksand\Downloads\monthly_split.xlsx")

# print(output_df)


# import pandas as pd

# # ✅ List of Excel files
# excel_files = [
# # "/home/thrymr/Downloads/purchase(20-21)/april_purchase_with_vendors.xlsx", 



# # "/home/thrymr/Downloads/purchase(20-21)/August_purchase_with_vendors.xlsx", 
# # "/home/thrymr/Downloads/purchase(20-21)/December_purchase_with_vendors.xlsx",
# # "/home/thrymr/Downloads/purchase(20-21)/july_purchase_with_vendors.xlsx", 
# # "/home/thrymr/Downloads/purchase(20-21)/june_purchase_with_vendors.xlsx", 
# "/home/thrymr/Downloads/purchase(20-21)/May_purchase_with_vendors.xlsx", 
# "/home/thrymr/Downloads/purchase(20-21)/November_purchase_with_vendors.xlsx", 
# "/home/thrymr/Downloads/purchase(20-21)/October_purchase_with_vendors.xlsx", 
# "/home/thrymr/Downloads/purchase(20-21)/September_purchase_with_vendors.xlsx"
# ]
# for file in excel_files:
#     print(f"\n📂 Processing file: {file}")
    
#     # Load Excel file
#     df = pd.read_excel(file)

#     if "District" not in df.columns:
#         print("⚠️ Skipped (No 'District' column found)")
#         continue

#     # Count matches ignoring case & spaces
#     mask = df["District"].astype(str).str.lower().str.strip() == "hydarabad"
#     before_count = mask.sum()

#     if before_count > 0:
#         # Replace only matching rows
#         df.loc[mask, "District"] = "Hyderabad"
        
#         # Save back
#         df.to_excel(file, index=False)

#         print(f"✅ Replaced {before_count} occurrence(s) of 'Hydarabad' → 'Hyderabad'")
#     else:
#         print("ℹ️ No 'Hydarabad' found in this file.")


import pandas as pd
from pathlib import Path

# ✅ Your files
FILES = [
    "/home/thrymr/Downloads/sales(20-21)/aug_sales_with_customers.xlsx",
    "/home/thrymr/Downloads/sales(20-21)/dec_sales_with_customers.xlsx",
    "/home/thrymr/Downloads/sales(20-21)/july_sales_with_customers.xlsx",
    "/home/thrymr/Downloads/sales(20-21)/june_sales_with_customers.xlsx",
    "/home/thrymr/Downloads/sales(20-21)/may_sales_with_customers.xlsx",
    "/home/thrymr/Downloads/sales(20-21)/nov_sales_with_customers.xlsx",
    "/home/thrymr/Downloads/sales(20-21)/oct_sales_with_customers.xlsx",
    "/home/thrymr/Downloads/sales(20-21)/sep_sales_with_customers.xlsx",
]

FACILITATOR_VALUE = "Hesa Enterprises Private Limited"
OVERWRITE = False  # 🔁 set to True to overwrite original files

def find_col(cols, target):
    """Case/space-insensitive exact match with a couple of common variants."""
    norm = {c: ''.join(str(c).lower().split()) for c in cols}
    t = ''.join(target.lower().split())

    # direct match first
    for c, n in norm.items():
        if n == t:
            return c

    # fallbacks for common header variants
    variants = {t}
    if t == "invoiceno":
        variants.update({"invoicenumber", "invoice#", "invoiceid"})
    if t == "facilitator":
        variants.update({"facilitatorname"})

    for c, n in norm.items():
        if n in variants:
            return c
    return None

for f in FILES:
    print(f"\nProcessing: {f}")
    df = pd.read_excel(f)

    fac_col = find_col(df.columns, "Facilitator")
    inv_col = find_col(df.columns, "Invoice No")

    # 1) Set Facilitator column value for all rows (no deletions)
    if fac_col is not None:
        df[fac_col] = FACILITATOR_VALUE
        print(f"  • Set `{fac_col}` to '{FACILITATOR_VALUE}' for {len(df)} rows.")
    else:
        print("  ⚠️ 'Facilitator' column not found — skipped.")

    # 2) Replace /RY/ with /HS/ in Invoice No (only for string values)
    if inv_col is not None:
        before = sum(1 for v in df[inv_col] if isinstance(v, str) and "/RY/" in v)
        df[inv_col] = df[inv_col].map(lambda x: x.replace("/RY/", "/HS/") if isinstance(x, str) else x)
        print(f"  • Replaced '/RY/' → '/HS/' in {before} invoice(s) within `{inv_col}`.")
    else:
        print("  ⚠️ 'Invoice No' column not found — skipped.")

    # Save
    out_path = f if OVERWRITE else str(Path(f).with_name(Path(f).stem + "_edited.xlsx"))
    df.to_excel(out_path, index=False)
    print(f"  ✅ Saved: {out_path}")
