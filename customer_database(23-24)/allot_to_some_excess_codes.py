import pandas as pd
import numpy as np

# Read the input file
df = pd.read_excel("/home/thrymr/Downloads/december(23-24)_with_customer_details.xlsx")

# Group by 'HSCode'
grouped_df = df.groupby('HSCode', group_keys=False)  # group_keys=False ensures no additional index is added

# Function to fill missing values randomly
def fill_missing_values_randomly(group):
    for col in group.columns:
        if group[col].isnull().any():  # Check if there are missing values
            available_values = group[col].dropna().values
            if available_values.size > 0:  # Ensure there are available values to choose from
                group[col] = group[col].apply(
                    lambda x: x if pd.notnull(x) else np.random.choice(available_values)
                )
            else:
                # If no available values, leave NaNs or use a default value
                group[col] = group[col].fillna(np.nan)  # Adjust 'Default' as needed
    return group

# Apply the function to each group and retain the original order
filled_df = grouped_df.apply(fill_missing_values_randomly).reset_index(drop=True)

# Save the result to a new Excel file
filled_df.to_excel("/home/thrymr/Downloads/december(23-24).xlsx", index=False)

