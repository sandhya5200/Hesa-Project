import pandas as pd
import numpy as np
from random import randint, sample

print("📥 Reading input Excel files...")

print("🔗 Concatenating and sorting data...")

# Combine and sort
df = pd.read_excel(r"c:\Users\ksand\Downloads\may_after_hesaathis.xlsx")
df['Date'] = pd.to_datetime(df['Date'])  # Ensure datetime format
df.sort_values(by='Date', inplace=True)

# Step 2: Generate Customer IDs
def generate_customer_ids(df):
    print("🧾 Generating Customer IDs...")
    df["Customer ID"] = None

    for (date, hesaathi), group in df.groupby(["Date", "Assigned Hesaathi Code"]):
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

def generate_invoice_numbers(df):
    """
    Generate Invoice No (AG & CG separate sequences) and Order ID (continuous integer).
    Month & Year are taken from the Date column.
    """
    print("🧾 Generating Invoice Numbers and Order IDs...")
    df["Invoice No"] = None
    df["Order ID"] = None
    
    # Continuous counter for Order IDs
    order_counter = 1  
    
    # Separate counters for AG & CG
    ag_counter = 1
    cg_counter = 1
    
    for (date, cid, vertical), group in df.groupby(["Date", "Customer ID", "Vertical"]):
        
        # Extract month/year from the first row's Date
        month_str = f"{date.month:02d}"
        year_str = str(date.year)[-2:]  # Last 2 digits
        
        # --- Invoice No (AG / CG) ---
        if "Commerce Business" in vertical:
            prefix = "CG"
            invoice_id = f"2020-21/RY/{month_str}/{cg_counter:04d}"
            cg_counter += 1
        else:
            prefix = "AG"
            invoice_id = f"2020-21/RY/{month_str}/{cg_counter:04d}"
            ag_counter += 1
        
        # --- Order ID (integer) ---
        order_id = order_counter  
        
        # Assign values
        df.loc[group.index, "Invoice No"] = invoice_id
        df.loc[group.index, "Order ID"] = order_id
        
        order_counter += 1
    
    return df


# Apply functions
df = generate_customer_ids(df)
df = generate_invoice_numbers(df)    


# Save as one file (no split)
print("💾 Saving output file...")
df.to_excel(r"c:\Users\ksand\Downloads\may_2020_sales.xlsx", index=False)

print("✅ Processing complete. File saved successfully.")

