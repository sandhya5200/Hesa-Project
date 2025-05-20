import pandas as pd
import random

# Load data (Replace with actual file paths)
field_officers = pd.read_excel("/home/thrymr/Downloads/cleaned_field_officers.xlsx")
master_data = pd.read_excel("/home/thrymr/Downloads/master1.xlsx")
support_data = pd.read_excel("/home/thrymr/Downloads/support.xlsx")

# Function to get cohort order
def cohort_sort_key(cohort):
    month, year = cohort.split("'")
    month_order = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    return (int(year), month_order[month])

# Sort master and support data by cohort
master_data["Cohort"] = master_data["Cohort"].astype(str)
support_data["Cohort"] = support_data["Cohort"].astype(str)
master_data = master_data.sort_values(by="Cohort", key=lambda x: x.map(cohort_sort_key))
support_data = support_data.sort_values(by="Cohort", key=lambda x: x.map(cohort_sort_key))

allocation = []
used_master = set()
used_support = set()

for _, officer in field_officers.iterrows():
    officer_cohort = str(officer["FO_Cohort"])  # Ensure it's a string
    officer_state = officer["FO_State"]  # State of the field officer
    
    # **Prioritize same-state allocation**
    state_master_data = master_data[master_data["State"] == officer_state]
    state_support_data = support_data[support_data["State"] == officer_state]

    # **Fallback: If no state-wise matches, use full dataset**
    if state_master_data.empty:
        state_master_data = master_data
    if state_support_data.empty:
        state_support_data = support_data

    # **Get available cohorts**
    available_cohorts = sorted(state_master_data["Cohort"].unique(), key=cohort_sort_key)
    cohort_index = available_cohorts.index(officer_cohort) if officer_cohort in available_cohorts else -1

    # **Select Master Hesaathis**
    prev_cohort = available_cohorts[cohort_index - 1] if cohort_index > 0 else None
    prev_master = state_master_data[state_master_data["Cohort"] == prev_cohort].sample(
        n=min(5, len(state_master_data[state_master_data["Cohort"] == prev_cohort])),
        random_state=None
    ) if prev_cohort else pd.DataFrame()

    # Get remaining members from later cohorts
    later_master = state_master_data[state_master_data["Cohort"] > officer_cohort]

    # Fix: Ensure we don't sample from an empty dataset
    if later_master.empty:
        num_master_needed = 0
    else:
        num_master_needed = max(10, min(random.randint(10, 50 - len(prev_master)), len(later_master)))

    # Sample only if there are available records
    later_master = later_master.sample(n=num_master_needed, random_state=None) if num_master_needed > 0 else pd.DataFrame()


    selected_master = pd.concat([prev_master, later_master])
    selected_master["Classification"] = "Master"
    used_master.update(selected_master["Code"])

    # **Select Support Hesaathis**
    num_support_needed = min(random.randint(25, 100), len(state_support_data))  
    selected_support = state_support_data.sample(n=num_support_needed, random_state=None) if num_support_needed > 0 else pd.DataFrame()
    selected_support["Classification"] = "Support"
    used_support.update(selected_support["Code"])

    # **Assign all Field Officer details**
    for col in ["Employee ID", "DOJ", "Gender", "Entity", "FO_State", "FO_Cohort", "FO_Name"]:
        selected_master[col] = officer[col]
        selected_support[col] = officer[col]

    allocation.append(selected_master)
    allocation.append(selected_support)

# **Final Allocation**
final_allocation = pd.concat(allocation, ignore_index=True)

# **Find Unused Master & Support Records**
unused_master = master_data[~master_data["Code"].isin(used_master)]
unused_support = support_data[~support_data["Code"].isin(used_support)]
unused_field_officers = field_officers[~field_officers["FO_Name"].isin(final_allocation["FO_Name"].unique())]

# **Save Output Files**
final_allocation.to_excel("/home/thrymr/Downloads/allocated_hesaathis.xlsx", index=False)
unused_master.to_excel("/home/thrymr/Downloads/unused_master.xlsx", index=False)
unused_support.to_excel("/home/thrymr/Downloads/unused_support.xlsx", index=False)
unused_field_officers.to_excel("/home/thrymr/Downloads/unused_field_officers.xlsx", index=False)

print("Allocation complete! Files saved with correct assignments.")

