import pandas as pd
import numpy as np

# Constants
start_date = "2020-05-01"
end_date = "2020-05-31"
districts = ["Adilabad", "Khammam", "Warangal", "Hyderabad", "Karim Nagar", "Nalgonda",
             "Medak", "RangaReddy", "Mahabub Nagar", "Nizamabad"]
state = "Telangana"

# 💰 Fill in your total money for each GST slab
gst_amounts = {
    0:  16638533,   # example
    0.05:  2059200,   # example
    0.12: 0,   # example
    0.18: 415796    # example
}
 

# --- Helper to create rows for a GST rate ---
def allocate_amounts(gst_rate, total_amount, agri_multiples=None, skip_market=False, skip_agri=False):
    dates = pd.date_range(start_date, end_date)
    selected_dates = np.random.choice(dates, size=int(len(dates) * 0.9), replace=False)
    selected_dates = pd.to_datetime(sorted(selected_dates))

    rows = []
    for d in selected_dates:
        for dist in districts:
            if not skip_market:
                rows.append([d, "Market Linkages Trading", "Agri Business", state, dist, gst_rate, 0])
            if not skip_agri:
                rows.append([d, "Agri Inputs", "Agri Business", state, dist, gst_rate, 0])
            rows.append([d, "FMCG", "Commerce Business", state, dist, gst_rate, 0])

    df = pd.DataFrame(rows, columns=["Date", "Sub Vertical", "Vertical", "State", "District", "GST Rate", "Taxable_Amount"])
    df.sort_values(by=["Date", "District", "Sub Vertical"], inplace=True, ignore_index=True)

    # --- Allocation rules ---
    if gst_rate in [0, 0.05]:
        market_total = round(total_amount * 0.35, 2)
        agri_total   = round(total_amount * 0.25, 2)
        fmcg_total   = round(total_amount * 0.40, 2)
    elif gst_rate == 0.12:
        market_total = 0
        agri_total   = round(total_amount * 0.20, 2)
        fmcg_total   = round(total_amount - agri_total, 2)
    elif gst_rate == 0.18:
        market_total = 0
        agri_total   = 0
        fmcg_total   = total_amount

    # Market
    if not skip_market and market_total > 0:
        market_indices = df[df["Sub Vertical"] == "Market Linkages Trading"].index
        market_random = np.random.randint(1000, 5000, len(market_indices)).astype(float)
        market_random = market_random / market_random.sum() * market_total
        df.loc[market_indices, "Taxable_Amount"] = np.round(market_random, 2)

    # Agri
    if not skip_agri and agri_total > 0:
        agri_indices = df[df["Sub Vertical"] == "Agri Inputs"].index
        if agri_multiples:  
            values = []
            remaining = agri_total
            while remaining >= min(agri_multiples):
                choice = np.random.choice(agri_multiples)
                if remaining - choice >= 0:
                    values.append(choice)
                    remaining -= choice
                else:
                    break
            values = values[:len(agri_indices)]
            values = values + [0]*(len(agri_indices)-len(values))
            np.random.shuffle(values)
            df.loc[agri_indices, "Taxable_Amount"] = values
        else:
            agri_random = np.random.randint(500, 4000, len(agri_indices)).astype(float)
            agri_random = agri_random / agri_random.sum() * agri_total
            df.loc[agri_indices, "Taxable_Amount"] = np.round(agri_random, 2)

    # FMCG
    if fmcg_total > 0:
        fmcg_indices = df[df["Sub Vertical"] == "FMCG"].index
        fmcg_random = np.random.randint(1000, 8000, len(fmcg_indices)).astype(float)
        fmcg_random = fmcg_random / fmcg_random.sum() * fmcg_total
        df.loc[fmcg_indices, "Taxable_Amount"] = np.round(fmcg_random, 2)

    # Fix rounding drift
    diff = round(total_amount - df["Taxable_Amount"].sum(), 2)
    if diff != 0:
        fmcg_indices = df[df["Sub Vertical"] == "FMCG"].index
        if len(fmcg_indices) > 0:
            df.loc[fmcg_indices[0], "Taxable_Amount"] += diff

    df["percentage_of_total"] = (df["Taxable_Amount"] / total_amount) * 100
    return df


# -----------------------------
# Process slabs
# -----------------------------
all_dfs = []

if gst_amounts.get(0, 0) > 0:
    all_dfs.append(allocate_amounts(0, gst_amounts[0]))

if gst_amounts.get(0.05, 0) > 0:
    all_dfs.append(allocate_amounts(0.05, gst_amounts[0.05]))

if gst_amounts.get(0.12, 0) > 0:
    all_dfs.append(allocate_amounts(0.12, gst_amounts[0.12],
                                   agri_multiples=[28676.08, 3424.2],
                                   skip_market=True))

if gst_amounts.get(0.18, 0) > 0:
    all_dfs.append(allocate_amounts(0.18, gst_amounts[0.18],
                                   skip_market=True, skip_agri=True))

# Combine and clean
if all_dfs:
    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df = final_df[final_df["Taxable_Amount"] > 0].reset_index(drop=True)  # remove zero rows
else:
    final_df = pd.DataFrame()


# Save Excel
output_file = r"c:\Users\ksand\Downloads\may_2020_taxable.xlsx"
final_df.to_excel(output_file, index=False)

print(f"✅ Excel generated: {output_file}")
print(f"Total rows: {len(final_df)}")
print("\nTotals by GST Rate:")
print(final_df.groupby("GST Rate")["Taxable_Amount"].sum())
