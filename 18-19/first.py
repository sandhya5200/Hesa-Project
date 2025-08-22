import pandas as pd
import numpy as np

# Constants
start_date = "2019-03-01"
end_date = "2019-03-31"
districts = ["Adilabad", "Khammam", "Warangal", "Hyderabad"]
state = "Telangana"
gst_rate = 18
total_amount = 2490745

# Split into FMCG and Agri Inputs
fmcg_total = round(total_amount * 0.70, 2)  # 70%
agri_total = round(total_amount * 0.30, 2)  # 30%

# Base multiples for agri
multiples = [2109.47, 2147.6]

# Generate Agri values as random multiples
agri_values = []
current_sum = 0

while True:
    base = np.random.choice(multiples)            # pick one base
    factor = np.random.randint(1, 6)              # random multiple (1 to 5 times)
    val = round(base * factor, 2)
    if current_sum + val > agri_total:            # stop if exceeding
        break
    agri_values.append(val)
    current_sum += val

# Leftover goes to FMCG
leftover = round(agri_total - current_sum, 2)
fmcg_total += leftover
agri_total = current_sum  # corrected agri sum

# --- Create FMCG rows (every date × district) ---
dates = pd.date_range(start_date, end_date)
rows = []
for d in dates:
    for dist in districts:
        rows.append([d, "FMCG", "Commerce Business", state, dist, gst_rate, 0])

df = pd.DataFrame(rows, columns=[
    "Date", "Sub Vertical", "Vertical", "State", "District", "GST Rate", "Taxable_Amount"
])

# --- Insert Agri Inputs randomly ---
fmcg_indices = df.index.tolist()
insert_positions = np.random.choice(fmcg_indices, size=len(agri_values), replace=True)

agri_rows = []
for pos, val in zip(insert_positions, agri_values):
    row = df.loc[pos].copy()
    row["Sub Vertical"] = "Agri Inputs"
    row["Vertical"] = "Agri Business"
    row["Taxable_Amount"] = val
    agri_rows.append(row)

# Add agri rows
df = pd.concat([df, pd.DataFrame(agri_rows)], ignore_index=True)

# Re-sort by Date, District
df.sort_values(by=["Date", "District"], inplace=True, ignore_index=True)

# --- FMCG allocation ---
remaining_fmcg = fmcg_total
fmcg_indices = df[df["Sub Vertical"] == "FMCG"].index
fmcg_random = np.random.randint(1000, 5000, len(fmcg_indices)).astype(float)
fmcg_random = fmcg_random / fmcg_random.sum() * remaining_fmcg
df.loc[fmcg_indices, "Taxable_Amount"] = np.round(fmcg_random, 2)

# Fix rounding drift
diff = total_amount - df["Taxable_Amount"].sum()
df.loc[fmcg_indices[0], "Taxable_Amount"] += diff

# % of total
df["percentage_of_total"] = (df["Taxable_Amount"] / total_amount) * 100

# Save Excel
output_file = "/home/thrymr/Downloads/mar_2019_taxable.xlsx"
df.to_excel(output_file, index=False)

print("Excel file generated:", output_file)
