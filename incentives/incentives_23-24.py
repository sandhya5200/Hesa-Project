import pandas as pd
import numpy as np

print("loading")

master_file = pd.read_excel("/home/thrymr/Downloads/master1.xlsx")
support_file = pd.read_excel("/home/thrymr/Downloads/support.xlsx")
customer_sheets = pd.ExcelFile("/home/thrymr/Downloads/customers.xlsx")

print("loaded all files")

customers_file = pd.concat([customer_sheets.parse(sheet) for sheet in customer_sheets.sheet_names])

##Cons
sampling_counts = {
    'April': (6731, 0, 131824, 3771771, "Apr'23"),
    'May': (7585, 0, 260465, 4160559, "May'23"),
    'June': (7792, 0, 241477, 4528684, "Jun'23"),
    'July': (9061, 30258, 251293, 4880152, "Jul'23"),
    'August': (10356, 31859, 230797, 5261494, "Aug'23"),
    'September': (10185, 32176, 240145, 5606325, "Sep'23"),
    'October': (11521, 0, 315003, 5982258, "Oct'23"),
    'November': (12772, 0, 299290, 6348279, "Nov'23"),
    'December': (12852, 0, 330455, 6634091, "Dec'23"),
    'January': (13374, 0, 263592, 6866342, "Jan'24"),
    'February': (14472, 0, 242674, 7127339, "Feb'24"),
    'March': (14753, 0, 256148, 7368422, "Mar'24")
}


##Agri
# sampling_counts = {
#     'April': (6727, 0, 512268, 12289018, "Apr'23"),
#     'May': (7432, 0, 588899, 13555749, "May'23"),
#     'June': (7878, 0, 609653, 14755158, "Jun'23"),
#     'July': (9410, 31284, 619940, 15900294, "Jul'23"),
#     'August': (10097, 32911, 703879, 17142766, "Aug'23"),
#     'September': (10957, 30964, 731491, 18266280, "Sep'23"),
#     'October': (11237, 0, 793925, 19491128, "Oct'23"),
#     'November': (11739, 0, 876782, 20683683, "Nov'23"),
#     'December': (13778, 0, 957500, 21614902, "Dec'23" ),
#     'January': (13627, 0, 893573, 22371612, "Jan'24"),
#     'February': (13784, 0, 952606, 23221981, "Feb'24"),
#     'March': (14490, 0, 1057660, 24007466, "Mar'24")
# }

hardcoded_months = {"Apr'21", "May'21", "Jun'21", "Jul'21", "Aug'21", "Sep'21", "Dec'21", "Jan'22", "Feb'22", "Mar'22",
                    "Apr'22", "May'22", "Jun'22", "Jul'22", "Aug'22", "Sep'22", "Dec'22", "Jan'23", "Feb'23", "Mar'23"}

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
    filename = f"/home/thrymr/Downloads/Cons_Incentives(23-24)_output{file_index}.xlsx"
    chunk.to_excel(filename, index=False)
    file_index += 1

print("Data processing complete!")


