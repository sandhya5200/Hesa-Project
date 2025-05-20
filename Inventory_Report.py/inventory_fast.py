import pandas as pd

# Load sales and purchases files
print("Loading sales and purchases files...")
sales_df = pd.read_excel("/home/thrymr/Desktop/Input Files(2023-24)/new_november_(23-24).xlsx")
purchases_df = pd.read_excel("/home/thrymr/Desktop/purchases(2023-24)/Purchases_November(2023-24).xlsx")
print("Files loaded successfully.")

# Store original columns for output later
original_sales_df = sales_df[['Product Name']].copy()

columns_to_extract = ['Date', 'Product Name', 'Product Qty', 'Customer District', 'Sub Vertical', 'Order Id', 'State']
filtered_sales_df = sales_df[columns_to_extract].copy()
print(f"Extracted columns: {columns_to_extract}")

print("Converting 'Date' columns to datetime...")
filtered_sales_df['Date'] = pd.to_datetime(filtered_sales_df['Date'], format='%d-%m-%Y', errors='coerce')
purchases_df['Date'] = pd.to_datetime(purchases_df['Date'], format='%d-%m-%Y', errors='coerce')
print("Date conversion complete.")

print("Preprocessing text columns (Product Name, District, State)...")
filtered_sales_df['Product Name'] = filtered_sales_df['Product Name'].str.strip().str.replace(" ", "").str.lower()
filtered_sales_df['District'] = filtered_sales_df['Customer District'].str.strip().str.replace(" ", "").str.lower()
filtered_sales_df['State'] = filtered_sales_df['State'].str.strip().str.replace(" ", "").str.lower()
purchases_df['Product Name'] = purchases_df['Product Name'].str.strip().str.replace(" ", "").str.lower()
purchases_df['District'] = purchases_df['Vendor District'].str.strip().str.replace(" ", "").str.lower()
purchases_df['State'] = purchases_df['Vendor State'].str.strip().str.replace(" ", "").str.lower()
print("Text preprocessing complete.")

filtered_sales_df['Purchase Qty'] = None
filtered_sales_df['PO number'] = None
filtered_sales_df['Opening Inventory'] = None
filtered_sales_df['Closing Inventory'] = None
print("Initialized new columns for 'Purchase Qty', 'PO number', 'Opening Inventory', and 'Closing Inventory'.")

print("Starting manual row matching between sales and purchases files...")
for idx, sales_row in filtered_sales_df.iterrows():
    total_purchase_qty = 0  
    po_numbers = []  
    product_qty = sales_row['Product Qty']  
    matched = False  

    # First-level match: Match by Product Name, District, and State
    purchase_rows = purchases_df[
        (purchases_df['Product Name'] == sales_row['Product Name']) &
        (purchases_df['District'] == sales_row['District']) &
        (purchases_df['State'] == sales_row['State'])
    ]

    if not purchase_rows.empty:
        for purchase_idx, purchase_row in purchase_rows.iterrows():
            total_purchase_qty += purchase_row['Purchase Qty']
            po_numbers.append(purchase_row['PO number'])

            # Remove the matched row from purchases_df
            purchases_df.drop(index=purchase_idx, inplace=True)

            if total_purchase_qty >= product_qty:
                matched = True
                break

    # Second-level match: Match by Product Name and State
    elif not matched:
        purchase_rows = purchases_df[
            (purchases_df['Product Name'] == sales_row['Product Name']) &
            (purchases_df['State'] == sales_row['State'])
        ]

        if not purchase_rows.empty:
            for purchase_idx, purchase_row in purchase_rows.iterrows():
                total_purchase_qty += purchase_row['Purchase Qty']
                po_numbers.append(purchase_row['PO number'])

                # Remove the matched row from purchases_df
                purchases_df.drop(index=purchase_idx, inplace=True)

                if total_purchase_qty >= product_qty:
                    matched = True
                    break

    # Update filtered_sales_df based on matches
    if matched:
        filtered_sales_df.at[idx, 'Purchase Qty'] = total_purchase_qty
        filtered_sales_df.at[idx, 'PO number'] = ','.join(po_numbers)
        print(f"Match found for Sales Row {idx}: Product={sales_row['Product Name']}, "
              f"District={sales_row['District']}, State={sales_row['State']} -> "
              f"PO Numbers={','.join(po_numbers)}")
    else:
        filtered_sales_df.at[idx, 'Purchase Qty'] = 0
        filtered_sales_df.at[idx, 'PO number'] = ""
        print(f"No match found for Sales Row {idx}: Product={sales_row['Product Name']}, "
              f"District={sales_row['District']}, State={sales_row['State']}")

# Reset the index of purchases_df after rows have been dropped
purchases_df.reset_index(drop=True, inplace=True)

print("Calculating Opening and Closing Inventory with Transfer Inwards logic...")
previous_closing_inventory = {}

# Add a new column for transfer inwards initialized with 0
filtered_sales_df['Transfer Inwards'] = 0

for index, row in filtered_sales_df.iterrows():
    state = row['State']
    product = row['Product Name']
    district = row['District']

    # Key to identify the product-district combination
    key = (product, district, state)

    # Check if we have a previous closing inventory for this product and district
    opening_inventory = previous_closing_inventory.get(key, 0)

    # Update the opening inventory for the current row
    filtered_sales_df.at[index, 'Opening Inventory'] = opening_inventory

    # Calculate the closing inventory
    purchase_qty = row['Purchase Qty'] if pd.notna(row['Purchase Qty']) else 0
    closing_inventory = opening_inventory + purchase_qty - row['Product Qty']

    # Check if closing inventory is less than product quantity
    if closing_inventory < 0:
        # Transfer the transfer inwards to the 'Transfer Inwards' column
        filtered_sales_df.at[index, 'Transfer Inwards'] = abs(closing_inventory)
        closing_inventory = 0  # Set closing inventory to 0 as it cannot be carried forward

    # Update the closing inventory for the current row
    filtered_sales_df.at[index, 'Closing Inventory'] = closing_inventory

    # Update the previous_closing_inventory dictionary only if closing inventory is > 0
    if closing_inventory > 0:
        previous_closing_inventory[key] = closing_inventory
    else:
        # If closing inventory is 0, remove the key from the dictionary to stop carry-forward
        previous_closing_inventory.pop(key, None)

    # Print progress for every 100 rows
    if index % 100 == 0:
        print(f"Processed {index} rows (Inventory calculation)")

# Add a new column 'Transfer Outwards' initialized with 0
filtered_sales_df['Transfer Outwards'] = 0

# Group by state, product name, and district
print("Calculating 'Transfer Outwards' column...")
grouped = filtered_sales_df.groupby(['State', 'Product Name', 'District'])

for group_key, group_data in grouped:
    # Get the last row of the current group
    last_row_index = group_data.index[-1]
    closing_inventory = filtered_sales_df.at[last_row_index, 'Closing Inventory']

    # Move the Closing Inventory value to 'Transfer Outwards' column
    filtered_sales_df.at[last_row_index, 'Transfer Outwards'] = closing_inventory

    # Set the Closing Inventory to 0
    filtered_sales_df.at[last_row_index, 'Closing Inventory'] = 0

    print(f"Transfer Outwards set to {closing_inventory} and Closing Inventory set to 0 for group {group_key} at index {last_row_index}")

# Initialize the new columns
filtered_sales_df["transfer_inwards_updated"] = filtered_sales_df["Transfer Inwards"]
filtered_sales_df["appended_districts"] = ""

# Group by Product Name and State
grouped = filtered_sales_df.groupby(["Product Name", "State"])

# Iterate over each group
for (product, state), group in grouped:
    transfer_outwards = group["Transfer Outwards"].tolist()
    districts = group["District"].tolist()
    transfer_inwards = group["Transfer Inwards"].tolist()

    # Process each row in the group
    for i, row in group.iterrows():
        remaining_excess = row["Transfer Inwards"]
        appended_districts = []

        # Deduct Transfer Outwards values from Excess
        for j, transfer in enumerate(transfer_outwards):
            if transfer > 0 and remaining_excess > 0:
                deducted = min(transfer, remaining_excess)
                remaining_excess -= deducted
                transfer_outwards[j] -= deducted
                appended_districts.append(districts[j])

        # Update the excess_updated and appended_districts columns
        filtered_sales_df.loc[i, "transfer_inwards_updated"] = remaining_excess
        filtered_sales_df.loc[i, "appended_districts"] = ", ".join(appended_districts)

filtered_sales_df.rename(columns={"Product Qty": "Sales"}, inplace=True)
filtered_sales_df.rename(columns={"Purchase Qty": "Purchases"}, inplace=True)
filtered_sales_df['Product Name'] = original_sales_df['Product Name']


# Save updated DataFrame
output_file_path = "/home/thrymr/Downloads/updated_inventory_november_2023.xlsx"
print(f"Saving updated output with 'Transfer Outwards' and 'Closing Inventory' changes...")
filtered_sales_df.to_excel(output_file_path, index=False)
print("Updated output saved successfully.")
