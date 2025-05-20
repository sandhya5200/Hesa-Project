import pandas as pd
import numpy as np

print("loading")

master_file = pd.read_excel("/home/thrymr/Downloads/master1.xlsx")
support_file = pd.read_excel("/home/thrymr/Downloads/support.xlsx")
customer_sheets = pd.ExcelFile("/home/thrymr/Downloads/customers.xlsx")

print("loaded all files")

customers_file = pd.concat([customer_sheets.parse(sheet) for sheet in customer_sheets.sheet_names])

sampling_counts = {
    "April": (np.random.randint(1297, 1461), np.random.randint(2989, 3363), np.random.randint(63793, 71768), 2445871, "Apr'21"),
    "May": (np.random.randint(1470, 1654), np.random.randint(4464, 5022), np.random.randint(72861, 81968), 2830663, "May'21"),
    "June": (np.random.randint(1614, 1816), np.random.randint(5694, 6406), np.random.randint(80408, 90459), 3151194, "Jun'21"),
    "July": (np.random.randint(1759, 1979), np.random.randint(7552, 8496), np.random.randint(88124, 99139), 3500292, "Jul'21"),
    "August": (np.random.randint(1918, 2158), np.random.randint(9593, 10792), np.random.randint(96877, 108986), 3893793, "Aug'21"),
    "September": (np.random.randint(2026, 2279), np.random.randint(10969, 12339), np.random.randint(102573, 115394), 4151672, "Sep'21"),
    "October": (0, 0, 0, 4151672, "Oct'21"),
    "November": (0, 0, 0, 4151672, "Nov'21"),
    "December": (np.random.randint(2223, 2501), np.random.randint(17160, 19305), np.random.randint(113509, 127697), 4774054, "Dec'21"),
    "January": (np.random.randint(2412, 2713), np.random.randint(18637, 20967), np.random.randint(124013, 139515), 5211296, "Jan'22"),
    "February": (np.random.randint(2641, 2972), np.random.randint(20433, 22988), np.random.randint(136739, 153831), 5741222, "Feb'22"),
    "March": (np.random.randint(2826, 3180), np.random.randint(21876, 24610), np.random.randint(147042, 165422), 6169814, "Mar'22")
}

final_data = []
past_data = []

for month, (master_size, support_size, customer_size, total_amount, cohort) in sampling_counts.items():
    
    if master_size == 0:
        master_filtered = pd.concat(past_data)  # 100% from past months
        support_filtered = pd.concat(past_data)
        customer_filtered = pd.concat(past_data)
    else:
        master_filtered = master_file[master_file["Cohort"] == cohort]
        support_filtered = support_file[support_file["Cohort"] == cohort]
        customer_filtered = customers_file[customers_file["Cohort"] == cohort]
        
        past_master = pd.concat(past_data) if past_data else pd.DataFrame()
        
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
    filename = f"/home/thrymr/Downloads/output_21_22_{file_index}.xlsx"
    chunk.to_excel(filename, index=False)
    file_index += 1

print("Data processing complete!")



