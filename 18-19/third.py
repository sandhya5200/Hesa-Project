import pandas as pd
import numpy as np
import unicodedata
import random
from collections import defaultdict

# Clean function
def clean(text):
    if pd.isna(text):
        return ''
    text = str(text)
    text = unicodedata.normalize("NFKD", text)
    text = text.strip().lower()
    text = text.replace('\u200b', '')
    text = ' '.join(text.split())
    return text

print("🔄 Loading input files...")
# sales_df1 = pd.read_excel("/home/thrymr/Desktop/sales 25-26/products_agri_sep.xlsx")
# sales_df2 = pd.read_excel("/home/thrymr/Desktop/sales 25-26/products_cons_sep.xlsx")
hesaathi_df = pd.read_excel(r"c:\Users\ksand\Downloads\Important 2\Important\new_hessathi_with_additional_people_details (copy).xlsx")

print("🧩 Combining and shuffling sales data...")
sales_df = pd.read_excel(r"c:\Users\ksand\Downloads\may_2020_products.xlsx")
sales_df = sales_df.sample(frac=1, random_state=42).reset_index(drop=True)
print(f"🧾 Total sales rows: {len(sales_df)}")

print("🧼 Cleaning state and district fields...")
sales_df['state_clean'] = sales_df['State'].apply(clean)
sales_df['district_clean'] = sales_df['District'].apply(clean)

hesaathi_df['state_clean'] = hesaathi_df['State'].apply(clean)
hesaathi_df['district_clean'] = hesaathi_df['District'].apply(clean)

print("📅 Filtering Hesaathi data by onboarding month...")
selected_month = "Mar'22"            ###################################################################----CHANGE-----#################################################################################
month_order = [
    "April'20", "May'20", "Jun'20", "Jul'20", "Aug'20", "Sep'20", "Oct'20", "Nov'20", "Dec'20",
    "Jan'21", "Feb'21", "Mar'21", "April'21", "May'21", "Jun'21", "Jul'21", "Aug'21", "Sep'21", "Dec'21",
    "Jan'22", "Feb'22", "Mar'22", "April'22", "May'22", "Jun'22", "Jul'22", "Aug'22", "Sep'22", "Oct'22", "Nov'22", "Dec'22",
    "Jan'23", "Feb'23", "Mar'23", "April'23", "May'23", "Jun'23", "Jul'23", "Aug'23", "Sep'23", "Oct'23", "Nov'23", "Dec'23",
    "Jan'24", "Feb'24", "Mar'24", "April'24", "May'24", "Jun'24", "Jul'24", "Aug'24", "Sep'24", "Oct'24", "Nov'24", "Dec'24",
    "Jan'25", "Feb'25", "Mar'25", "April'25", "May'25", "Jun'25", "Jul'25", "Aug'25", "Sep'25", "Oct'25", "Nov'25", "Dec'25",
    "Jan'26", "Feb'26", "Mar'26"
]
valid_months = month_order[:month_order.index(selected_month) + 1]
filtered_hesaathi_all = hesaathi_df[hesaathi_df['Onboarding Month'].isin(valid_months)].copy()

# Step: Remove 8–10% per month prioritizing Non Performers
print("✂️ Removing 8–10% of Hesaathis per month, prioritizing Non Performers...")
used_hesaathi_list = []
neglected_hesaathi_list = []

for month in valid_months:
    month_data = filtered_hesaathi_all[filtered_hesaathi_all['Onboarding Month'] == month]
    total = len(month_data)
    if total == 0:
        continue
    remove_pct = random.uniform(0.08, 0.10)
    remove_count = int(total * remove_pct)

    # Step 1: Try removing Non Performers
    non_perf = month_data[month_data['Performance'].str.lower() == 'non performer']
    remove_non_perf = non_perf.sample(min(len(non_perf), remove_count), random_state=42)
    
    remaining_remove = remove_count - len(remove_non_perf)

    # Step 2: Remove random from the rest if needed
    rest = month_data.drop(remove_non_perf.index)
    remove_extra = rest.sample(n=remaining_remove, random_state=42) if remaining_remove > 0 else pd.DataFrame()

    # Combine neglected and used
    neglected = pd.concat([remove_non_perf, remove_extra])
    used = month_data.drop(neglected.index)

    neglected_hesaathi_list.append(neglected)
    used_hesaathi_list.append(used)

filtered_hesaathi = pd.concat(used_hesaathi_list, ignore_index=True)
neglected_hesaathis = pd.concat(neglected_hesaathi_list, ignore_index=True)

print(f"✅ Selected {len(filtered_hesaathi)} Hesaathis for assignment.")
print(f"🚫 Neglected {len(neglected_hesaathis)} Hesaathis.")

print("🔗 Creating merge keys and mapping datasets...")
sales_df['merge_key'] = sales_df['state_clean'] + '_' + sales_df['district_clean']
filtered_hesaathi['merge_key'] = filtered_hesaathi['state_clean'] + '_' + filtered_hesaathi['district_clean']

print("🎯 Creating mapping of merge_key to Hesaathi Codes...")
hesaathi_map = (
    filtered_hesaathi
    .groupby('merge_key')['Hesaathi Code']
    .apply(list)
    .to_dict()
)

# Check for missing keys
missing_keys = set(sales_df['merge_key']) - set(hesaathi_map.keys())
if missing_keys:
    print("❌ The following merge_keys were not matched to Hesaathis:")
    for key in sorted(missing_keys):
        print("  ➤", key)
    raise ValueError("Fix state/district mismatches! Some keys not found in Hesaathi data.")

print("💰 Starting Vertical-wise assignment with taxable value constraints...")

# Constants for taxable value range (3-3.5 lakhs)
MIN_TAXABLE_VALUE = 300000  # 3 lakhs
MAX_TAXABLE_VALUE = 350000  # 3.5 lakhs

# Sort sales data by Date for consistent processing
sales_df['Date'] = pd.to_datetime(sales_df['Date'])
sales_df = sales_df.sort_values(by='Date').reset_index(drop=True)

# Initialize tracking dictionaries
# Structure: {(merge_key, hesaathi_code, vertical): current_taxable_value}
hesaathi_vertical_allocation = defaultdict(float)

# Create hesaathi onboarding month mapping
hesaathi_month_map = filtered_hesaathi.set_index('Hesaathi Code')['Onboarding Month'].to_dict()

# Lists to store assignments
assigned_codes = []
assigned_months = []

print("🎲 Processing each transaction for optimal assignment...")

for idx, row in sales_df.iterrows():
    merge_key = row['merge_key']
    vertical = row['Vertical']
    taxable_value = float(row['Taxable Value'])
    
    available_hesaathis = hesaathi_map.get(merge_key, [])
    
    assigned = False
    best_hesaathi = None
    
    # Try to find a hesaathi that can accommodate this transaction
    for hesaathi_code in available_hesaathis:
        key = (merge_key, hesaathi_code, vertical)
        current_allocation = hesaathi_vertical_allocation[key]
        
        # Check if this hesaathi can accommodate the transaction
        if current_allocation + taxable_value <= MAX_TAXABLE_VALUE:
            # If current allocation is 0 or adding this keeps us within range
            if current_allocation == 0 or current_allocation + taxable_value >= MIN_TAXABLE_VALUE:
                best_hesaathi = hesaathi_code
                break
            # If adding this transaction would put us in the valid range
            elif current_allocation < MIN_TAXABLE_VALUE and current_allocation + taxable_value >= MIN_TAXABLE_VALUE:
                best_hesaathi = hesaathi_code
                break
    
    # If no hesaathi found, try to find one with minimum current allocation
    if best_hesaathi is None:
        min_allocation = float('inf')
        for hesaathi_code in available_hesaathis:
            key = (merge_key, hesaathi_code, vertical)
            current_allocation = hesaathi_vertical_allocation[key]
            if current_allocation < min_allocation and current_allocation + taxable_value <= MAX_TAXABLE_VALUE:
                min_allocation = current_allocation
                best_hesaathi = hesaathi_code
    
    # Assign to best hesaathi if found
    if best_hesaathi is not None:
        key = (merge_key, best_hesaathi, vertical)
        hesaathi_vertical_allocation[key] += taxable_value
        assigned_codes.append(best_hesaathi)
        assigned_months.append(hesaathi_month_map[best_hesaathi])
        assigned = True
    
    # If still not assigned, use HS-CO
    if not assigned:
        assigned_codes.append('HS-CO')
        assigned_months.append('')  # Empty onboarding month for HS-CO
        
        # Log overflow case
        if idx % 1000 == 0:  # Log every 1000th overflow to avoid spam
            print(f"⚠️  Overflow at row {idx}: {taxable_value} assigned to HS-CO in {merge_key}, {vertical}")

# Assign the results
sales_df['Assigned Hesaathi Code'] = assigned_codes
sales_df['Assigned Hesaathi Onboarding Month'] = assigned_months

# Clean up temporary columns
sales_df.drop(columns=['state_clean', 'district_clean', 'merge_key'], inplace=True, errors='ignore')

print("📊 Assignment Summary:")
regular_assignments = sum(1 for code in assigned_codes if code != 'HS-CO')
overflow_assignments = sum(1 for code in assigned_codes if code == 'HS-CO')
print(f"✅ Regular assignments: {regular_assignments}")
print(f"⚠️  HS-CO assignments: {overflow_assignments}")

# Print allocation summary per hesaathi-vertical combination
print("\n💼 Hesaathi-Vertical Allocation Summary:")
allocation_summary = defaultdict(lambda: defaultdict(float))
for (merge_key, hesaathi_code, vertical), total_value in hesaathi_vertical_allocation.items():
    if total_value > 0:
        allocation_summary[hesaathi_code][vertical] = total_value

# Save full file (no splitting into halves)
print("\n📂 Saving final sales file...")
sales_df.to_excel(r"c:\Users\ksand\Downloads\may_after_hesaathis.xlsx", index=False)

print("✅ Processing complete! File saved successfully.")
