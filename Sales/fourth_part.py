import pandas as pd
import numpy as np
from random import randint, sample

print("📥 Reading input Excel files...")

# Step 1: Read and combine the Excel files
file1 = r"c:\Users\ksand\OneDrive\Desktop\hesa files\sales 25-26\sales_with_hesaathis_part1.xlsx"
file2 = r"c:\Users\ksand\OneDrive\Desktop\hesa files\sales 25-26\sales_with_hesaathis_part2.xlsx"

df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

print("🔗 Concatenating and sorting data...")

# Combine and sort
df = pd.concat([df1, df2], ignore_index=True)
df['Date'] = pd.to_datetime(df['Date'])  # Ensure datetime format
df.sort_values(by='Date', inplace=True)

# Step 2: Generate Customer IDs
def generate_customer_ids(df):
    print("🧾 Generating Customer IDs...")
    df["Customer ID"] = None

    for (date, hesaathi), group in df.groupby(["Date", "Hesaathi Code"]):
        count = len(group)
        base = f"CS-{hesaathi}-"
        
        if count <= 5:
            cid = base + f"{randint(1, 50):04d}"
            df.loc[group.index, "Customer ID"] = cid

        elif 6 <= count <= 10:
            cids = sample(range(1, 51), 2)
            cid1 = base + f"{cids[0]:04d}"
            cid2 = base + f"{cids[1]:04d}"
            mid = count // 2
            df.loc[group.index[:mid], "Customer ID"] = cid1
            df.loc[group.index[mid:], "Customer ID"] = cid2

        else:  # count > 10
            cids = sample(range(1, 51), 3)
            cid1 = base + f"{cids[0]:04d}"
            cid2 = base + f"{cids[1]:04d}"
            cid3 = base + f"{cids[2]:04d}"
            third = count // 3
            df.loc[group.index[:third], "Customer ID"] = cid1
            df.loc[group.index[third:2*third], "Customer ID"] = cid2
            df.loc[group.index[2*third:], "Customer ID"] = cid3

    return df

# Step 3: Generate Invoice Numbers
def generate_invoice_numbers(df, month="04", year="25"):
    print("🧾 Generating Invoice Numbers...")
    df["Invoice No"] = None
    counter = 1

    for (date, cid, vertical), group in df.groupby(["Date", "Customer ID", "Vertical"]):
        prefix = "CG" if "Consumer" in vertical else "AG"
        invoice_id = f"HS-INV-{prefix}-{month}-{year}-{counter:08d}"
        df.loc[group.index, "Invoice No"] = invoice_id
        counter += 1

    return df

# Step 4: Apply the functions
df = generate_customer_ids(df)
df = generate_invoice_numbers(df)

print("✂️ Splitting DataFrame into two halves...")

# Step 5: Split the DataFrame into two halves
mid_index = len(df) // 2
df1_out = df.iloc[:mid_index].reset_index(drop=True)
df2_out = df.iloc[mid_index:].reset_index(drop=True)

# Step 6: Save to two output Excel files
print("💾 Saving output files...")
df1_out.to_excel(r"c:\Users\ksand\OneDrive\Desktop\hesa files\sales 25-26\sales_with_hesaathis_part111.xlsx", index=False)
df2_out.to_excel(r"c:\Users\ksand\OneDrive\Desktop\hesa files\sales 25-26\sales_with_hesaathis_part222.xlsx", index=False)

print("✅ Processing complete. Files saved successfully.")
