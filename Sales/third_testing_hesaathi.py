import pandas as pd

# # Load both September parts
sep1 = pd.read_excel("/home/thrymr/Downloads/part1.xlsx")
sep2 = pd.read_excel("/home/thrymr/Downloads/part2.xlsx")
full_september = pd.concat([sep1, sep2], ignore_index=True)
# full_september = pd.read_excel("/home/thrymr/Desktop/sales 25-26/sales_with_hesaathis_part2_DUMMY.xlsx")

# Load master file
master = pd.read_excel("/home/thrymr/Important/new_hessathi_with_additional_people_details.xlsx")

# full_september = full_september.drop(columns=["Onboarding Month"])

# Step 1: Get total onboarded per cohort
total_per_cohort = master.groupby('Onboarding Month').agg(
    total_count=('Hesaathi Code', 'nunique')
).reset_index()

# Step 2: Merge sales with onboarding info
merged = pd.merge(
    full_september,
    master[['Hesaathi Code', 'Onboarding Month']],
    on='Hesaathi Code',
    how='left'
)

# Step 3: Sales stats per cohort
sales_stats = merged.groupby('Onboarding Month').agg(
    hesaathi_count=('Hesaathi Code', 'nunique'),
    taxable_value=('Taxable Value', 'sum')
).reset_index()

# Step 4: Merge with total onboarded
summary = pd.merge(sales_stats, total_per_cohort, on='Onboarding Month', how='left')

print(summary.columns)

# Step 5: Calculate percent of total sales and percent used
total_taxable = summary['taxable_value'].sum()
summary['percent_of_total'] = (summary['taxable_value'] / total_taxable) * 100
summary['percent_used'] = (summary['hesaathi_count'] / summary['total_count']) * 100


# Step 6: Map onboarding month to financial year
def get_financial_year(month_str):
    try:
        if pd.isna(month_str):
            return "Unknown"
        month, year = month_str.split("'")
        month = month.strip().lower()
        year = int(year)
        month_map = {
            'april': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
            'jan': 1, 'feb': 2, 'mar': 3
        }
        if month_map.get(month, 0) >= 4:
            return f"FY {year}-{year+1}"
        else:
            return f"FY {year-1}-{year}"
    except:
        return "Unknown"

summary['business_year'] = summary['Onboarding Month'].apply(get_financial_year)

# Step 7: Format percentage columns
summary['percent_of_total'] = summary['percent_of_total'].round(2)
summary['percent_used'] = summary['percent_used'].round(2)

# Step 8: Reorder and sort
summary = summary[[
    'business_year', 'Onboarding Month', 'hesaathi_count', 'total_count',
    'percent_used', 'taxable_value', 'percent_of_total'
]]


# Define the custom order for onboarding months
custom_order = [
        "April'20", "May'20", "Jun'20", "Jul'20", "Aug'20", "Sep'20", "Oct'20", "Nov'20", "Dec'20",
    "Jan'21", "Feb'21", "Mar'21", "April'21", "May'21", "Jun'21", "Jul'21", "Aug'21", "Sep'21", "Dec'21",
    "Jan'22", "Feb'22", "Mar'22", "April'22", "May'22", "Jun'22", "Jul'22", "Aug'22", "Sep'22", "Oct'22", "Nov'22", "Dec'22",
    "Jan'23", "Feb'23", "Mar'23", "April'23", "May'23", "Jun'23", "Jul'23", "Aug'23", "Sep'23", "Oct'23", "Nov'23", "Dec'23",
    "Jan'24", "Feb'24", "Mar'24", "April'24", "May'24", "Jun'24", "Jul'24", "Aug'24", "Sep'24", "Oct'24", "Nov'24", "Dec'24",
    "Jan'25", "Feb'25", "Mar'25", "April'25"
]

# Convert the column to categorical type with the custom order
summary['Onboarding Month'] = pd.Categorical(summary['Onboarding Month'], categories=custom_order, ordered=True)

# Now sort by this column
df_sorted = summary.sort_values('Onboarding Month')

# Save or display
df_sorted.to_excel("/home/thrymr/Downloads/analyzed_report_DUMMY.xlsx", index=False)
print(df_sorted)

