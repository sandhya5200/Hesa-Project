# import pandas as pd
# import numpy as np
# import unicodedata
# import random
# from collections import defaultdict

# # Clean function
# def clean(text):
#     if pd.isna(text):
#         return ''
#     text = str(text)
#     text = unicodedata.normalize("NFKD", text)
#     text = text.strip().lower()
#     text = text.replace('\u200b', '')
#     text = ' '.join(text.split())
#     return text

# print("🔄 Loading input files...")
# sales_df1 = pd.read_excel(r"c:\Users\ksand\OneDrive\Desktop\hesa files\sales 25-26\Final_Agri_April_25_output_to_check.xlsx")
# sales_df2 = pd.read_excel(r"c:\Users\ksand\OneDrive\Desktop\hesa files\sales 25-26\Final_Cons_April_25_output_to_check.xlsx")
# hesaathi_df = pd.read_excel(r"c:\Users\ksand\OneDrive\Desktop\hesa files\new_hessathi_with_additional_people_details.xlsx")


# print("🧩 Combining and shuffling sales data...")
# sales_df = pd.concat([sales_df1, sales_df2], ignore_index=True)
# sales_df = sales_df.sample(frac=1, random_state=42).reset_index(drop=True)
# print(f"🧾 Total sales rows: {len(sales_df)}")

# print("🧼 Cleaning state and district fields...")
# sales_df['state_clean'] = sales_df['State'].apply(clean)
# sales_df['district_clean'] = sales_df['District'].apply(clean)

# hesaathi_df['state_clean'] = hesaathi_df['State'].apply(clean)
# hesaathi_df['district_clean'] = hesaathi_df['District'].apply(clean)

# print("📅 Filtering Hesaathi data by onboarding month...")
# selected_month = "April'25"
# month_order = [
#     "April'20", "May'20", "Jun'20", "Jul'20", "Aug'20", "Sep'20", "Oct'20", "Nov'20", "Dec'20",
#     "Jan'21", "Feb'21", "Mar'21", "April'21", "May'21", "Jun'21", "Jul'21", "Aug'21", "Sep'21", "Dec'21",
#     "Jan'22", "Feb'22", "Mar'22", "April'22", "May'22", "Jun'22", "Jul'22", "Aug'22", "Sep'22", "Oct'22", "Nov'22", "Dec'22",
#     "Jan'23", "Feb'23", "Mar'23", "April'23", "May'23", "Jun'23", "Jul'23", "Aug'23", "Sep'23", "Oct'23", "Nov'23", "Dec'23",
#     "Jan'24", "Feb'24", "Mar'24", "April'24", "May'24", "Jun'24", "Jul'24", "Aug'24", "Sep'24", "Oct'24", "Nov'24", "Dec'24",
#     "Jan'25", "Feb'25", "Mar'25", "April'25", "May'25", "Jun'25", "Jul'25", "Aug'25", "Sep'25", "Oct'25", "Nov'25", "Dec'25",
#     "Jan'26", "Feb'26", "Mar'26"
# ]
# valid_months = month_order[:month_order.index(selected_month) + 1]
# filtered_hesaathi_all = hesaathi_df[hesaathi_df['Onboarding Month'].isin(valid_months)].copy()

# # Step: Remove 8–10% per month prioritizing Non Performers
# print("✂️ Removing 8–10% of Hesaathis per month, prioritizing Non Performers...")
# used_hesaathi_list = []
# neglected_hesaathi_list = []

# for month in valid_months:
#     month_data = filtered_hesaathi_all[filtered_hesaathi_all['Onboarding Month'] == month]
#     total = len(month_data)
#     if total == 0:
#         continue
#     remove_pct = random.uniform(0.08, 0.10)
#     remove_count = int(total * remove_pct)

#     # Step 1: Try removing Non Performers
#     non_perf = month_data[month_data['Performance'].str.lower() == 'non performer']
#     remove_non_perf = non_perf.sample(min(len(non_perf), remove_count), random_state=42)
    
#     remaining_remove = remove_count - len(remove_non_perf)

#     # Step 2: Remove random from the rest if needed
#     rest = month_data.drop(remove_non_perf.index)
#     remove_extra = rest.sample(n=remaining_remove, random_state=42) if remaining_remove > 0 else pd.DataFrame()

#     # Combine neglected and used
#     neglected = pd.concat([remove_non_perf, remove_extra])
#     used = month_data.drop(neglected.index)

#     neglected_hesaathi_list.append(neglected)
#     used_hesaathi_list.append(used)

# filtered_hesaathi = pd.concat(used_hesaathi_list, ignore_index=True)
# neglected_hesaathis = pd.concat(neglected_hesaathi_list, ignore_index=True)

# print(f"✅ Selected {len(filtered_hesaathi)} Hesaathis for assignment.")
# print(f"🚫 Neglected {len(neglected_hesaathis)} Hesaathis.")

# # Save neglected list
# # neglected_hesaathis.to_excel("/home/thrymr/Downloads/neglected_hesaathis.xlsx", index=False)

# print("🔗 Creating merge keys and merging datasets...")
# sales_df['merge_key'] = sales_df['state_clean'] + '_' + sales_df['district_clean']
# filtered_hesaathi['merge_key'] = filtered_hesaathi['state_clean'] + '_' + filtered_hesaathi['district_clean']

# print("🎯 Creating mapping of merge_key to Hesaathi Codes...")
# hesaathi_map = (
#     filtered_hesaathi
#     .groupby('merge_key')['Hesaathi Code']
#     .apply(list)
#     .to_dict()
# )

# # Check for missing keys
# missing_keys = set(sales_df['merge_key']) - set(hesaathi_map.keys())
# if missing_keys:
#     print("❌ The following merge_keys were not matched to Hesaathis:")
#     for key in sorted(missing_keys):
#         print("  ➤", key)
#     raise ValueError("Fix state/district mismatches! Some keys not found in Hesaathi data.")

# print("🎲 Repeating Hesaathis 2–10 times per region and assigning...")
# expanded_hesaathi_map = defaultdict(list)

# for key, codes in hesaathi_map.items():
#     repeated_pool = []
#     for code in codes:
#         repeat_count = random.randint(2, 10)
#         repeated_pool.extend([code] * repeat_count)
#     random.shuffle(repeated_pool)
#     expanded_hesaathi_map[key] = repeated_pool

# assigned_codes = []
# key_counters = defaultdict(int)

# for key in sales_df['merge_key']:
#     pool = expanded_hesaathi_map[key]
#     idx = key_counters[key] % len(pool)
#     assigned_codes.append(pool[idx])
#     key_counters[key] += 1

# sales_df['Assigned Hesaathi Code'] = assigned_codes

# # Map onboarding month
# hesaathi_month_map = filtered_hesaathi.set_index('Hesaathi Code')['Onboarding Month'].to_dict()
# sales_df['Assigned Hesaathi Onboarding Month'] = sales_df['Assigned Hesaathi Code'].map(hesaathi_month_map)

# sales_df.drop(columns=['state_clean', 'district_clean', 'merge_key', '_row_id'], inplace=True, errors='ignore')

# print("📅 Sorting by date and splitting into two files...")
# sales_df['Date'] = pd.to_datetime(sales_df['Date'])
# sales_df = sales_df.sort_values(by='Date').reset_index(drop=True)

# half = len(sales_df) // 2
# first_half = sales_df.iloc[:half]
# second_half = sales_df.iloc[half:]



# first_half.to_excel(r"c:\Users\ksand\OneDrive\Desktop\hesa files\sales 25-26\sales_with_hesaathis_part1.xlsx", index=False)
# second_half.to_excel(r"c:\Users\ksand\OneDrive\Desktop\hesa files\sales 25-26\sales_with_hesaathis_part2.xlsx", index=False)


# print("✅ Output saved successfully:")
# print("  ➤ /home/thrymr/Downloads/part1.xlsx")
# print("  ➤ /home/thrymr/Downloads/part2.xlsx")
# print("  ➤ /home/thrymr/Downloads/neglected_hesaathis.xlsx")

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
sales_df1 = pd.read_excel("/home/thrymr/Desktop/sales 25-26/Final_Agri_April_25_output_to_check.xlsx")
sales_df2 = pd.read_excel("/home/thrymr/Desktop/sales 25-26/Final_Cons_April_25_output_to_check.xlsx")
hesaathi_df = pd.read_excel("/home/thrymr/Important/new_hessathi_with_additional_people_details.xlsx")

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

    non_perf = month_data[month_data['Performance'].str.lower() == 'non performer']
    remove_non_perf = non_perf.sample(min(len(non_perf), remove_count), random_state=42)

    remaining_remove = remove_count - len(remove_non_perf)
    rest = month_data.drop(remove_non_perf.index)
    remove_extra = rest.sample(n=remaining_remove, random_state=42) if remaining_remove > 0 else pd.DataFrame()

    neglected = pd.concat([remove_non_perf, remove_extra])
    used = month_data.drop(neglected.index)

    neglected_hesaathi_list.append(neglected)
    used_hesaathi_list.append(used)

filtered_hesaathi = pd.concat(used_hesaathi_list, ignore_index=True)
neglected_hesaathis = pd.concat(neglected_hesaathi_list, ignore_index=True)

print(f"✅ Selected {len(filtered_hesaathi)} Hesaathis for assignment.")
print(f"🚫 Neglected {len(neglected_hesaathis)} Hesaathis.")

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

# Check for missing keys
missing_keys = set(sales_df['merge_key']) - set(hesaathi_map.keys())
if missing_keys:
    print("❌ The following merge_keys were not matched to Hesaathis:")
    for key in sorted(missing_keys):
        print("  ➤", key)
    raise ValueError("Fix state/district mismatches! Some keys not found in Hesaathi data.")

print("🎲 Repeating Hesaathis 2–10 times per region and assigning with constraints...")
expanded_hesaathi_map = defaultdict(list)
for key, codes in hesaathi_map.items():
    repeated_pool = []
    for code in codes:
        repeat_count = random.randint(2, 10)
        repeated_pool.extend([code] * repeat_count)
    random.shuffle(repeated_pool)
    expanded_hesaathi_map[key] = repeated_pool

# Date format
sales_df['Date'] = pd.to_datetime(sales_df['Date'])

# Trackers
daily_used_hesaathis = defaultdict(list)  # (merge_key, date) => [used Hesaathi Codes]
hesaathi_taxable_tracker = defaultdict(float)  # Hesaathi Code => total assigned taxable value

# Map onboarding month
hesaathi_month_map = filtered_hesaathi.set_index('Hesaathi Code')['Onboarding Month'].to_dict()

assigned_codes = []

# Assignment with constraints
for _, row in sales_df.iterrows():
    key = row['merge_key']
    sale_date = row['Date'].date()
    taxable_value = row['Taxable Value']
    preferred_pool = daily_used_hesaathis[(key, sale_date)]
    fallback_pool = expanded_hesaathi_map[key]

    assigned = None
    for hcode in preferred_pool + fallback_pool:
        if hesaathi_taxable_tracker[hcode] + taxable_value <= 350000:
            assigned = hcode
            break

    if assigned is None:
        raise Exception(f"💥 No available Hesaathi in {key} for date {sale_date} under ₹3.5L cap")

    # Save assignment
    assigned_codes.append(assigned)
    daily_used_hesaathis[(key, sale_date)].append(assigned)
    hesaathi_taxable_tracker[assigned] += taxable_value

sales_df['Assigned Hesaathi Code'] = assigned_codes
sales_df['Assigned Hesaathi Onboarding Month'] = sales_df['Assigned Hesaathi Code'].map(hesaathi_month_map)

sales_df.drop(columns=['state_clean', 'district_clean', 'merge_key', '_row_id'], inplace=True, errors='ignore')

print("📅 Sorting by date and splitting into two files...")
sales_df = sales_df.sort_values(by='Date').reset_index(drop=True)
half = len(sales_df) // 2
first_half = sales_df.iloc[:half]
second_half = sales_df.iloc[half:]

first_half.to_excel("/home/thrymr/Desktop/sales 25-26/sales_with_hesaathis_part1.xlsx", index=False)
second_half.to_excel("/home/thrymr/Desktop/sales 25-26/sales_with_hesaathis_part2.xlsx", index=False)
# neglected_hesaathis.to_excel(r"c:\Users\ksand\OneDrive\Desktop\hesa files\sales 25-26\neglected_hesaathis.xlsx", index=False)

print("✅ Output saved successfully:")
print("  ➤ Part 1 & 2 sales assigned files")
print("  ➤ Neglected Hesaathis file")

