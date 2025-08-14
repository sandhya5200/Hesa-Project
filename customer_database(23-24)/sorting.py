import pandas as pd
import os
from math import ceil

# === CONFIGURATION ===
folder_path = "/home/thrymr/Desktop/Customer_data"  # Change this to your actual folder path
output_folder = "/home/thrymr/Desktop/Customer_data/sorted_output"  # Folder to save output files
rows_per_file = 1048500 # Adjust based on size of each file

# === CREATE OUTPUT FOLDER IF NOT EXISTS ===
os.makedirs(output_folder, exist_ok=True)

# === STEP 1: Load all files ===
all_dfs = []
for file in os.listdir(folder_path):
    if file.endswith(".xlsx"):
        df = pd.read_excel(os.path.join(folder_path, file))
        all_dfs.append(df)

# === STEP 2: Combine and Sort ===
combined_df = pd.concat(all_dfs, ignore_index=True)
combined_df.sort_values(by="CustomerID", inplace=True)

# === STEP 3: Split and Save into multiple Excel files ===
total_rows = len(combined_df)
num_files = ceil(total_rows / rows_per_file)

for i in range(num_files):
    start = i * rows_per_file
    end = (i + 1) * rows_per_file
    chunk_df = combined_df.iloc[start:end]
    
    output_path = os.path.join(output_folder, f"sorted_customers_part_{i+1}.xlsx")

    chunk_df.to_excel(output_path, index=False)

print(f"\n✅ Done! Saved {num_files} Excel files in: {output_folder}")

