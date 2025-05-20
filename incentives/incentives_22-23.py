import pandas as pd
import numpy as np

print("loading")

master_file = pd.read_excel("/home/thrymr/Downloads/master1.xlsx")
support_file = pd.read_excel("/home/thrymr/Downloads/support.xlsx")
customer_sheets = pd.ExcelFile("/home/thrymr/Downloads/customers.xlsx")

print("loaded all files")

customers_file = pd.concat([customer_sheets.parse(sheet) for sheet in customer_sheets.sheet_names])

sampling_counts = {
    "April": (3051, 23127, 0, 447956, "Apr'22"),
    "May": (3358, 25800, 0, 490219, "May'22"),
    "June": (3660, 25427, 0, 529097, "Jun'22"),
    "July": (3881, 27937, 0, 564406, "Jul'22"),
    "August": (4019, 27714, 0, 610121, "Aug'22"),
    "September": (4408, 30593, 0, 652307, "Sep'22"),
    "October": (4452, 31296, 0, 698500, "Oct'22"),
    "November": (4805, 30418, 0, 736214, "Nov'22"),
    "December": (4895, 30197, 0, 806295, "Dec'22"),
    "January": (5458, 0, 32389, 871697, "Jan'23"),
    "February": (5574, 0, 31349, 933025, "Feb'23"),
    "March": (5824, 0, 32187, 999068, "Mar'23")
}

hardcoded_months = {"Apr'21", "May'21", "Jun'21", "Jul'21", "Aug'21", "Sep'21", "Dec'21", "Jan'22", "Feb'22", "Mar'22"}

final_data = []
past_data = []

hardcoded_data = []
for cohort in hardcoded_months:
    hardcoded_master = master_file[master_file["Cohort"] == cohort]
    hardcoded_support = support_file[support_file["Cohort"] == cohort]
    hardcoded_customer = customers_file[customers_file["Cohort"] == cohort]
    hardcoded_data.append(pd.concat([hardcoded_master, hardcoded_support, hardcoded_customer]))

past_data.extend(hardcoded_data)

for month, (master_size, support_size, customer_size, total_amount, cohort) in sampling_counts.items():
    past_master = pd.concat(past_data) if past_data else pd.DataFrame()
    
    master_filtered = master_file[master_file["Cohort"] == cohort]
    support_filtered = support_file[support_file["Cohort"] == cohort]
    customer_filtered = customers_file[customers_file["Cohort"] == cohort]
    
    if not past_master.empty:
        master_past_sample = past_master.sample(int(master_size * 0.1), replace=True, random_state=42)
        support_past_sample = past_master.sample(int(support_size * 0.1), replace=True, random_state=42)
        customer_past_sample = past_master.sample(int(customer_size * 0.1), replace=True, random_state=42)
    else:
        master_past_sample = support_past_sample = customer_past_sample = pd.DataFrame()
    
    master_sample = master_filtered.sample(int(master_size * 0.9), replace=True, random_state=42)
    support_sample = support_filtered.sample(int(support_size * 0.9), replace=True, random_state=42)
    customer_sample = customer_filtered.sample(int(customer_size * 0.9), replace=True, random_state=42)
    
    master_sample = pd.concat([master_sample, master_past_sample])
    support_sample = pd.concat([support_sample, support_past_sample])
    customer_sample = pd.concat([customer_sample, customer_past_sample])
    
    master_sample["Classification"] = "Master Hesaathi"
    support_sample["Classification"] = "Support Hesaathi"
    customer_sample["Classification"] = "Customer"
    
    month_data = pd.concat([master_sample, support_sample, customer_sample])
    past_data.append(month_data)
    
    n = len(month_data)
    print(f"Number of recipients for {month}: {n}")
    
    amounts = np.random.uniform(10, 50, n)
    amounts = (amounts / amounts.sum()) * total_amount  
    amounts = np.clip(amounts, 10, 50)
    amounts = amounts.astype(int)

    diff = total_amount - amounts.sum()
    
    while diff != 0:
        idx = np.random.randint(0, n)  
        
        if diff > 0 and amounts[idx] < 50:
            add = min(diff, 50 - amounts[idx])
            amounts[idx] += add
            diff -= add
        elif diff < 0 and amounts[idx] > 10:
            sub = min(abs(diff), amounts[idx] - 10)
            amounts[idx] -= sub
            diff += sub
    
    print(f"Final Sum for {month}: {amounts.sum()} (Target: {total_amount})")
    
    month_data["Incentive Amount"] = amounts  
    month_data["Month"] = month
    month_data["Year"] = cohort
    
    final_data.append(month_data)

final_data = pd.concat(final_data)

max_rows = 1048576
file_index = 1
while not final_data.empty:


    chunk, final_data = final_data.iloc[:max_rows], final_data.iloc[max_rows:]
    filename = f"/home/thrymr/Downloads/outputcheck_22_23_{file_index}.xlsx"
    chunk.to_excel(filename, index=False)
    file_index += 1

print("Data processing complete!")



