import pandas as pd
import random
import calendar

# Input data
data = {
    "Month-Year": ["05-20", "06-20", "07-20", "09-20", "11-20", "12-20"],
    "Total": [623694.60, 288381.60, 158085.00, 189520.20, 89100.00, 143820.00]
}

df = pd.DataFrame(data)

# Function to split amount into 7–8 random parts
def split_amount(total, n_parts, max_value=250000):
    parts = []
    remaining = total
    for i in range(n_parts - 1):
        # Ensure no part exceeds max and leaves enough for remaining parts
        max_possible = min(max_value, remaining - (n_parts - i - 1))
        part = round(random.uniform(1, max_possible / (n_parts - i)), 2)
        parts.append(part)
        remaining -= part
    parts.append(round(remaining, 2))  # Last part = remaining
    return parts

rows = []

for _, row in df.iterrows():
    month, year = row["Month-Year"].split("-")
    year = int("20" + year)  # convert to full year e.g. 2020
    month = int(month)
    
    # Pick random 7–8 dates
    n_parts = random.randint(7, 8)
    days_in_month = calendar.monthrange(year, month)[1]
    dates = random.sample(range(1, days_in_month + 1), n_parts)
    dates.sort()
    
    # Split total into random parts
    splits = split_amount(row["Total"], n_parts)
    
    for d, amt in zip(dates, splits):
        taxable = round(amt * 18 / 100, 2)
        cgst = round(taxable / 2, 2)
        sgst = round(taxable / 2, 2)
        rows.append({
            "Date": f"{year}-{month:02d}-{d:02d}",
            "Amount": amt,
            "Taxable_18%": taxable,
            "CGST_9%": cgst,
            "SGST_9%": sgst
        })

# Final DataFrame
output_df = pd.DataFrame(rows)

# Save to Excel
output_df.to_excel(r"c:\Users\ksand\Downloads\monthly_split.xlsx")

print(output_df)
