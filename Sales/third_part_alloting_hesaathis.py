import pandas as pd
import numpy as np
import unicodedata

# Robust clean function to handle hidden characters and normalize
def clean(text):
    if pd.isna(text):
        return ''
    text = str(text)
    text = unicodedata.normalize("NFKD", text)  # Normalize unicode characters
    text = text.strip().lower()                # Remove leading/trailing spaces + lowercase
    text = text.replace('\u200b', '')          # Remove zero-width space
    text = ' '.join(text.split())              # Remove duplicate internal spaces
    return text

print("🔄 Loading input files...")
sales_df1 = pd.read_excel("/home/thrymr/Desktop/sales 25-26/Final_Agri_April_25_output_to_check.xlsx")
sales_df2 = pd.read_excel("/home/thrymr/Desktop/sales 25-26/Final_Cons_April_25_output_to_check.xlsx")
hesaathi_df = pd.read_excel("/home/thrymr/Important/new_hessathi_with_additional_people_details.xlsx")
print("✅ Files loaded successfully.")

print("🧩 Combining and shuffling sales data...")
sales_df = pd.concat([sales_df1, sales_df2], ignore_index=True)
sales_df = sales_df.sample(frac=1, random_state=42).reset_index(drop=True)
print(f"🧾 Total sales rows: {len(sales_df)}")

print("🧼 Cleaning state and district fields...")
sales_df['state_clean'] = sales_df['State'].apply(clean)
sales_df['district_clean'] = sales_df['District'].apply(clean)

hesaathi_df['state_clean'] = hesaathi_df['State'].apply(clean)
hesaathi_df['district_clean'] = hesaathi_df['District'].apply(clean)

print("📅 Filtering Hesaathi data by onboarding month...")
selected_month = "April'25"
month_order = [
    "April'20", "May'20", "Jun'20", "Jul'20", "Aug'20", "Sep'20", "Oct'20", "Nov'20", "Dec'20",
    "Jan'21", "Feb'21", "Mar'21", "April'21", "May'21", "Jun'21", "Jul'21", "Aug'21", "Sep'21", "Dec'21",
    "Jan'22", "Feb'22", "Mar'22", "April'22", "May'22", "Jun'22", "Jul'22", "Aug'22", "Sep'22", "Oct'22", "Nov'22", "Dec'22",
    "Jan'23", "Feb'23", "Mar'23", "April'23", "May'23", "Jun'23", "Jul'23", "Aug'23", "Sep'23", "Oct'23", "Nov'23", "Dec'23",
    "Jan'24", "Feb'24", "Mar'24", "April'24", "May'24", "Jun'24", "Jul'24", "Aug'24", "Sep'24", "Oct'24", "Nov'24", "Dec'24",
    "Jan'25", "Feb'25", "Mar'25", "April'25", "May'25", "Jun'25", "Jul'25", "Aug'25", "Sep'25", "Oct'25", "Nov'25", "Dec'25",
    "Jan'26", "Feb'26", "Mar'26"
]
valid_months = month_order[:month_order.index(selected_month)]
filtered_hesaathi = hesaathi_df[hesaathi_df['Onboarding Month'].isin(valid_months)].copy()
print(f"✅ Filtered Hesaathis: {len(filtered_hesaathi)}")

print("🔗 Creating merge keys and merging datasets...")
sales_df['merge_key'] = sales_df['state_clean'] + '_' + sales_df['district_clean']
filtered_hesaathi['merge_key'] = filtered_hesaathi['state_clean'] + '_' + filtered_hesaathi['district_clean']

print("🎯 Creating mapping of merge_key to Hesaathi Codes...")
hesaathi_map = (
    filtered_hesaathi
    .groupby('merge_key')['Hesaathi Code']
    .apply(list)
    .to_dict()
)

# Debug print: find keys in sales_df that are missing in Hesaathi mapping
missing_keys = set(sales_df['merge_key']) - set(hesaathi_map.keys())
if missing_keys:
    print("❌ The following merge_keys were not matched to Hesaathis:")
    for key in sorted(missing_keys):
        print("  ➤", key)
    raise ValueError("Fix state/district mismatches! Some keys not found in Hesaathi data.")

from collections import defaultdict
import random

print("🎲 Repeating Hesaathis 2–10 times per region and assigning...")

# Step 1: Create a new expanded Hesaathi pool with repeats
expanded_hesaathi_map = defaultdict(list)

for key, codes in hesaathi_map.items():
    repeated_pool = []
    for code in codes:
        repeat_count = random.randint(2, 10)
        repeated_pool.extend([code] * repeat_count)
    random.shuffle(repeated_pool)
    expanded_hesaathi_map[key] = repeated_pool

# Step 2: Assign Hesaathis from pool
assigned_codes = []

key_counters = defaultdict(int)

for key in sales_df['merge_key']:
    pool = expanded_hesaathi_map[key]
    idx = key_counters[key] % len(pool)
    assigned_codes.append(pool[idx])
    key_counters[key] += 1

sales_df['Assigned Hesaathi Code'] = assigned_codes


# Get onboarding month for each assigned code
hesaathi_month_map = filtered_hesaathi.set_index('Hesaathi Code')['Onboarding Month'].to_dict()
sales_df['Assigned Hesaathi Onboarding Month'] = sales_df['Assigned Hesaathi Code'].map(hesaathi_month_map)

sales_df.drop(columns=['state_clean', 'district_clean', 'merge_key', '_row_id'], inplace=True, errors='ignore')

print("📅 Sorting by date and splitting into two files...")
sales_df['Date'] = pd.to_datetime(sales_df['Date'])
sales_df = sales_df.sort_values(by='Date').reset_index(drop=True)

half = len(sales_df) // 2
first_half = sales_df.iloc[:half]
second_half = sales_df.iloc[half:]

first_half.to_excel("/home/thrymr/Downloads/part1.xlsx", index=False)
second_half.to_excel("/home/thrymr/Downloads/part2.xlsx", index=False)

print("✅ Output saved successfully:")
print("  ➤ /home/thrymr/Downloads/part1.xlsx")
print("  ➤ /home/thrymr/Downloads/part2.xlsx")

