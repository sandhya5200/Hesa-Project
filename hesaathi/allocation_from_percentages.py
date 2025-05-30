import pandas as pd
import numpy as np
import calendar
import random

hesaathi_df = pd.read_excel("/home/thrymr/Downloads/hesaathis.xlsx") 
percentage_df = pd.read_excel("/home/thrymr/Downloads/Hesaathi_percentages.xlsx")  

def extract_month_name(onboarding_month):
    try:
        month_abbr = onboarding_month.split("'")[0][:3].capitalize()
        month_number = list(calendar.month_abbr).index(month_abbr)
        return calendar.month_name[month_number]
    except Exception:
        return None

hesaathi_df['Month'] = hesaathi_df['Onboarding Month'].apply(extract_month_name)


final_rows = []


for month, group_df in hesaathi_df.groupby('Month'):
    total_members = len(group_df)
    if month not in percentage_df['Month'].values:
        continue  
    percent_group = percentage_df[percentage_df['Month'] == month].copy()
    percent_group['Percentage'] = percent_group['Percentage'] / percent_group['Percentage'].sum()
    percent_group['Count'] = (percent_group['Percentage'] * total_members).astype(int)

    assigned = percent_group['Count'].sum()
    remaining = total_members - assigned

    if remaining > 0:
        choices = percent_group.index.tolist()
        for _ in range(remaining):
            rand_idx = random.choice(choices)
            percent_group.at[rand_idx, 'Count'] += 1

    hesaathi_codes = group_df[['S no', 'Hesaathi Code', 'Onboarding Month']].values.tolist()
    idx = 0

    for _, row in percent_group.iterrows():
        for _ in range(int(row['Count'])):
            if idx >= len(hesaathi_codes):
                break
            sno, code, onboard_month = hesaathi_codes[idx]
            final_rows.append({
                'S no': sno,
                'Hesaathi Code': code,
                'Onboarding Month': onboard_month,
                'Category': row['Category'],
                'Sub Category': row['Sub Category'],
                'Gender': row['Gender']
            })
            idx += 1

output_df = pd.DataFrame(final_rows)
output_df.to_excel("/home/thrymr/Downloads/hesaathi_output.xlsx", index=False)
print("Output file 'hesaathi_output.xlsx' generated successfully!")
