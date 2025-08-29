import pandas as pd
import numpy as np

# Constants
start_date = "2020-03-01"
end_date = "2020-03-31"
districts = ["Adilabad", "Khammam", "Warangal", "Hyderabad", "Karim Nagar", "Nalgonda"]
state = "Telangana"
gst_rate = 0  # Changed to 0%
total_amount = 8000000

# Split into three categories with new percentages
market_linkages_total = round(total_amount * 0.30, 2)  # 45%
agri_total = round(total_amount * 0.25, 2)             # 30%
fmcg_total = round(total_amount * 0.45, 2)             # 25%

print(f"Market Linkages Trading: {market_linkages_total}")
print(f"Agri Inputs: {agri_total}")
print(f"FMCG: {fmcg_total}")

# --- Select only 90% random dates ---
dates = pd.date_range(start_date, end_date)
selected_dates = np.random.choice(dates, size=int(len(dates) * 0.9), replace=False)
selected_dates = pd.to_datetime(sorted(selected_dates))  # keep them in order

rows = []

# Create rows only for selected dates
for d in selected_dates:
    for dist in districts:
        # FMCG rows
        rows.append([d, "FMCG", "Commerce Business", state, dist, gst_rate, 0])
        # Agri Inputs rows  
        rows.append([d, "Agri Inputs", "Agri Business", state, dist, gst_rate, 0])
        # Market Linkages Trading rows
        rows.append([d, "Market Linkages Trading", "Agri Business", state, dist, gst_rate, 0])

df = pd.DataFrame(rows, columns=[
    "Date", "Sub Vertical", "Vertical", "State", "District", "GST Rate", "Taxable_Amount"
])

# Sort by Date, District, Sub Vertical
df.sort_values(by=["Date", "District", "Sub Vertical"], inplace=True, ignore_index=True)

# --- Allocate amounts randomly within each category ---

# Market Linkages Trading allocation
market_indices = df[df["Sub Vertical"] == "Market Linkages Trading"].index
market_random = np.random.randint(1000, 5000, len(market_indices)).astype(float)
market_random = market_random / market_random.sum() * market_linkages_total
df.loc[market_indices, "Taxable_Amount"] = np.round(market_random, 2)

# Agri Inputs allocation (no multiples needed for 0% GST)
agri_indices = df[df["Sub Vertical"] == "Agri Inputs"].index
agri_random = np.random.randint(500, 4000, len(agri_indices)).astype(float)
agri_random = agri_random / agri_random.sum() * agri_total
df.loc[agri_indices, "Taxable_Amount"] = np.round(agri_random, 2)

# FMCG allocation
fmcg_indices = df[df["Sub Vertical"] == "FMCG"].index
fmcg_random = np.random.randint(1000, 8000, len(fmcg_indices)).astype(float)
fmcg_random = fmcg_random / fmcg_random.sum() * fmcg_total
df.loc[fmcg_indices, "Taxable_Amount"] = np.round(fmcg_random, 2)

# Fix any rounding drift by adjusting the largest category (Market Linkages Trading)
current_total = df["Taxable_Amount"].sum()
diff = round(total_amount - current_total, 2)
if diff != 0:
    df.loc[market_indices[0], "Taxable_Amount"] += diff

# Calculate percentage of total
df["percentage_of_total"] = (df["Taxable_Amount"] / total_amount) * 100

# Verify totals
print(f"\nActual totals:")
print(f"Market Linkages Trading: {df[df['Sub Vertical'] == 'Market Linkages Trading']['Taxable_Amount'].sum()}")
print(f"Agri Inputs: {df[df['Sub Vertical'] == 'Agri Inputs']['Taxable_Amount'].sum()}")
print(f"FMCG: {df[df['Sub Vertical'] == 'FMCG']['Taxable_Amount'].sum()}")
print(f"Total: {df['Taxable_Amount'].sum()}")

# Save Excel
output_file = r"c:\Users\ksand\Downloads\mar_2020_taxable.xlsx"
df.to_excel(output_file, index=False)

print(f"\nExcel file generated: {output_file}")
print(f"Total rows: {len(df)}")
