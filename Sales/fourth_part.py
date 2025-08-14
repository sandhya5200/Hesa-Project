import pandas as pd
import numpy as np
from random import randint, sample

print("📥 Reading input Excel files...")

# Step 1: Read and combine the Excel files
file1 = "/home/thrymr/Desktop/sales 25-26/after hesaathis allocation/july_sales_with_hesaathis_part1.xlsx"
file2 = "/home/thrymr/Desktop/sales 25-26/after hesaathis allocation/july_sales_with_hesaathis_part2.xlsx"


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
            invoice_id = f"HS-INV-{prefix}-{month_str}-{year_str}-{cg_counter:08d}"
            cg_counter += 1
        else:
            prefix = "AG"
            invoice_id = f"HS-INV-{prefix}-{month_str}-{year_str}-{ag_counter:08d}"
            ag_counter += 1
        
        # --- Order ID (integer) ---
        order_id = order_counter  
        
        # Assign values
        df.loc[group.index, "Invoice No"] = invoice_id
        df.loc[group.index, "Order ID"] = order_id
        
        order_counter += 1
    
    return df



def generate_dummy_invoices(df):
    """
    Generate Dummy Invoice:
    HS-INV-[AG/CG]-[STATE CODE]-[MM]-[YY]-000001
    """
    print("🧾 Generating Dummy Invoices...")
    df["Dummy Invoice"] = None
    
    # State codes mapping
    state_codes = {
        "Telangana": "TG",
        "Maharashtra": "MH",
        "Odisha": "OD",
        "Karnataka": "KA",
        "Tamil Nadu": "TN",
        "Madhya Pradesh": "MP",
        "Andhra Pradesh": "AP"
    }
    
    # Dictionary to hold counters for Dummy Invoice (per prefix + state + month/year)
    dummy_counters = {}
    
    for (date, cid, vertical, state), group in df.groupby(["Date", "Customer ID", "Vertical", "State"]):
        
        # Determine AG or CG
        if "Commerce Business" in vertical:
            prefix = "CG"
        else:
            prefix = "AG"
        
        # Get state code
        state_code = state_codes.get(state, "XX")  # Default to 'XX' if not found
        
        # Extract month/year from Date
        month_str = f"{date.month:02d}"
        year_str = str(date.year)[-2:]
        
        # Key for counter
        dummy_key = f"{prefix}-{state_code}-{month_str}-{year_str}"
        
        # Initialize counter if not exists
        if dummy_key not in dummy_counters:
            dummy_counters[dummy_key] = 1
        
        dummy_counter = dummy_counters[dummy_key]
        dummy_invoice = f"HS-INV-{prefix}-{state_code}-{month_str}-{year_str}-{dummy_counter:06d}"
        
        # Assign values
        df.loc[group.index, "Dummy Invoice"] = dummy_invoice
        
        # Increment for next
        dummy_counters[dummy_key] += 1
    
    return df

df = generate_customer_ids(df)
df = generate_invoice_numbers(df)    
df = generate_dummy_invoices(df)


print("✂️ Splitting DataFrame into two halves...")

# Step 5: Split the DataFrame into two halves
mid_index = len(df) // 2
df1_out = df.iloc[:mid_index].reset_index(drop=True)
df2_out = df.iloc[mid_index:].reset_index(drop=True)

# Step 6: Save to two output Excel files
print("💾 Saving output files...")
df1_out.to_excel("/home/thrymr/Downloads/july_sales_with_customers_part1.xlsx", index=False)
df2_out.to_excel("/home/thrymr/Downloads/july_sales_with_customers_part2.xlsx", index=False)
print("✅ Processing complete. Files saved successfully.")
