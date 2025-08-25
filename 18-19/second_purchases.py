import pandas as pd
import random

# Load the Excel file
df = pd.read_excel(r"c:\Users\ksand\Downloads\mar.xlsx")

# Clean and format
df["District"] = df["District"].str.strip().str.upper()
df["Sub Vertical"] = df["Sub Vertical"].str.strip().str.upper()
df["__row_id__"] = df.index  # ✅ Unique ID for fast assignment

# Constants
MIN_VENDOR_IDS = 4
MAX_VENDOR_IDS = 5
MIN_TAXABLE = 50000
MAX_TAXABLE = 85000

# Step 1: Add Vendor ID column to DataFrame
df["Vendor ID"] = None
vendor_ids = []

# Step 2: Assign rows group-wise
grouped = df.groupby(["District", "Sub Vertical"])
for (district, sub_vertical), group_df in grouped:
    print(f"\n🚀 Processing group: {district}, {sub_vertical}")

    group_rows = df.loc[group_df.index].sample(frac=1, random_state=42).to_dict("records")

    # Create initial 25–30 vendor IDs
    vendor_count = random.randint(MIN_VENDOR_IDS, MAX_VENDOR_IDS)
    pool = []
    for i in range(1, vendor_count + 1):
        vendor = {
            "Vendor ID": f"HS-VED-{district}-{sub_vertical}-{i:04d}",
            "District": district,
            "Sub Vertical": sub_vertical,
            "Total Taxable": 0,  # ✅ Must be spelled exactly like this
            "Target Cap": random.uniform(MIN_TAXABLE, MAX_TAXABLE),
            "Rows": [],
        }

        vendor_ids.append(vendor)
        pool.append(vendor)

    # Assign rows randomly to vendors within ₹5L–₹8.5L
    for row in group_rows:
        row_taxable = row["Taxable Value"]
        random.shuffle(pool)  # Ensure randomness in vendor order

        assigned = False
        for vendor in pool:
            future_total = vendor["Total Taxable"] + row_taxable
            if future_total <= vendor["Target Cap"]:  # ✅ Use individual cap
                vendor["Rows"].append({**row})
                vendor["Total Taxable"] = future_total
                assigned = True
                break

        

        # If not assignable, create new vendor dynamically
        if not assigned:
            new_vendor_num = len([v for v in vendor_ids if v["District"] == district and v["Sub Vertical"] == sub_vertical]) + 1
            new_vendor_id = f"HS-VED-{district}-{sub_vertical}-{new_vendor_num:04d}"
            new_vendor = {
                "Vendor ID": new_vendor_id,
                "District": district,
                "Sub Vertical": sub_vertical,
                "Total Taxable": row_taxable,
                "Target Cap": random.uniform(MIN_TAXABLE, MAX_TAXABLE),
                "Rows": [{**row}],
            }

            vendor_ids.append(new_vendor)
            pool.append(new_vendor)
            print(f"➕ Created new vendor: {new_vendor_id} for ₹{row_taxable:.2f}")

    print(f"✅ Rows distributed among {len(pool)} vendors.")

# Step 3: Assign back to original DataFrame
print("\n📝 Assigning Vendor IDs to DataFrame using __row_id__...")

total_assigned = 0
for idx, vendor in enumerate(vendor_ids, start=1):
    for row in vendor["Rows"]:
        df.at[row["__row_id__"], "Vendor ID"] = vendor["Vendor ID"]
        total_assigned += 1
    print(f"✅ Vendor {idx}: {vendor['Vendor ID']} → {len(vendor['Rows'])} rows, ₹{vendor['Total Taxable']:.2f}")

print(f"\n🎯 Total rows assigned Vendor IDs: {total_assigned}")

# Step 4: Save output
df.drop(columns="__row_id__", inplace=True)
df.to_excel(r"c:\Users\ksand\Downloads\mar.xlsx", index=False)
