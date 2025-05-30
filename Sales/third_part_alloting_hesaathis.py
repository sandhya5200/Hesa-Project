import pandas as pd
import random

# --- 1. Input Setup ---
target_month = "April'25"
month_order = [
    "April'20", "May'20", "Jun'20", "Jul'20", "Aug'20", "Sep'20", "Oct'20", "Nov'20", "Dec'20",
    "Jan'21", "Feb'21", "Mar'21", "April'21", "May'21", "Jun'21", "Jul'21", "Aug'21", "Sep'21", "Dec'21",
    "Jan'22", "Feb'22", "Mar'22", "April'22", "May'22", "Jun'22", "Jul'22", "Aug'22", "Sep'22", "Oct'22", "Nov'22", "Dec'22",
    "Jan'23", "Feb'23", "Mar'23", "April'23", "May'23", "Jun'23", "Jul'23", "Aug'23", "Sep'23", "Oct'23", "Nov'23", "Dec'23",
    "Jan'24", "Feb'24", "Mar'24", "April'24", "May'24", "Jun'24", "Jul'24", "Aug'24", "Sep'24", "Oct'24", "Nov'24", "Dec'24",
    "Jan'25", "Feb'25", "Mar'25", "April'25", "May'25", "Jun'25", "Jul'25", "Aug'25", "Sep'25", "Oct'25", "Nov'25", "Dec'25",
    "Jan'26", "Feb'26", "Mar'26"
]

# --- 2. Read and shuffle sales data ---
sales1 = pd.read_excel("/home/thrymr/Desktop/sales 25-26/Final_Agri_April_25_output_to_check.xlsx")
sales2 = pd.read_excel("/home/thrymr/Desktop/sales 25-26/Final_Cons_April_25_output_to_check.xlsx")
sales_df = pd.concat([sales1, sales2], ignore_index=True)
sales_df = sales_df.sample(frac=1, random_state=42).reset_index(drop=True)

# --- 3. Load hesaathi data ---
hesaathi_df = pd.read_excel("/home/thrymr/Important/new_hessathi_with_additional_people_details.xlsx")

# --- 4. Filter relevant months ---
target_index = month_order.index(target_month)
relevant_months = month_order[:target_index + 1]

# --- 5. Assign hesaathis month-wise with preference to exclude non-performers ---
all_hesaathis = {}

for month in relevant_months:
    month_df = hesaathi_df[hesaathi_df['Onboarding Month'] == month]
    month_hesaathis = month_df['Hesaathi Code'].tolist()
    random.shuffle(month_hesaathis)

    keep_pct = random.uniform(0.85, 0.90)
    keep_count = int(len(month_hesaathis) * keep_pct)

    # Prioritize non-performers in drop list
    non_perf = month_df[month_df['Performance'] == 'Non Performer']['Hesaathi Code'].tolist()
    medium_perf = month_df[month_df['Performance'] == 'Medium Performer']['Hesaathi Code'].tolist()
    high_perf = month_df[month_df['Performance'] == 'High Performer']['Hesaathi Code'].tolist()

    drop_candidates = non_perf + medium_perf + high_perf
    drop_candidates = [h for h in drop_candidates if h in month_hesaathis]

    drop_count = len(month_hesaathis) - keep_count
    drop_list = drop_candidates[:drop_count]  # drop more non-performers naturally
    keep = [h for h in month_hesaathis if h not in drop_list]

    all_hesaathis[month] = keep

# --- 6. Final Hesaathi pool ---
final_hesaathi_pool = [h for m in relevant_months for h in all_hesaathis[m]]

# --- 7. Assign Hesaathi codes with up to 10 reps per date ---
grouped = sales_df.groupby('Date')
hesaathi_assignments = []
max_repeat_per_day = 10

for date, group in grouped:
    num_rows = len(group)
    assigned_codes = []
    hesaathi_counts = {}

    while len(assigned_codes) < num_rows:
        hesaathi = random.choice(final_hesaathi_pool)
        count = hesaathi_counts.get(hesaathi, 0)
        if count >= max_repeat_per_day:
            continue
        repeat_times = random.randint(1, min(max_repeat_per_day - count, num_rows - len(assigned_codes)))
        assigned_codes.extend([hesaathi] * repeat_times)
        hesaathi_counts[hesaathi] = count + repeat_times

    random.shuffle(assigned_codes)
    hesaathi_assignments.extend(assigned_codes)

sales_df['Hesaathi Code'] = hesaathi_assignments[:len(sales_df)]
sales_df['Onboarding Month'] = sales_df['Hesaathi Code'].map(hesaathi_df.set_index('Hesaathi Code')['Onboarding Month'])

# --- 8. Final Export ---
sales_df = sales_df.sort_values(by='Date').reset_index(drop=True)
max_rows = 727595

sales_df.iloc[:max_rows].to_excel("/home/thrymr/Desktop/sales 25-26/sales_with_hesaathis_part1.xlsx", index=False)
if len(sales_df) > max_rows:
    sales_df.iloc[max_rows:].to_excel("/home/thrymr/Desktop/sales 25-26/sales_with_hesaathis_part2+.xlsx", index=False)
