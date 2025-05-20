import pandas as pd

# Load the files (Replace with actual file paths)
withdrawals_file = "/home/thrymr/Desktop/bank_purchases(22-23)/purchase_withdrawl_Purc Feb(23).xlsx"
excess_file = "/home/thrymr/Downloads/feb_unused_deposit_invoices.xlsx"

# Read data
withdrawals_df = pd.read_excel(withdrawals_file)
excess_df = pd.read_excel(excess_file)

# Convert dates to consistent datetime format
withdrawals_df["Date"] = pd.to_datetime(withdrawals_df["Date"], errors='coerce', dayfirst=True)
excess_df["CreatedDate"] = pd.to_datetime(excess_df["CreatedDate"], errors='coerce', dayfirst=True)

# Define target dates
target_dates = [  
    "01/02/2023", "02/02/2023", "03/02/2023", "04/02/2023","05/02/2023",
    "06/02/2023", "07/02/2023", "08/02/2023", "09/02/2023",
    "10/02/2023", "11/02/2023", "12/02/2023", "13/02/2023", "14/02/2023",
    "16/02/2023", "17/02/2023", "18/02/2023", "19/02/2023", "20/02/2023", "21/02/2023",
    "22/02/2023", "23/02/2023", "24/02/2023", "25/02/2023", "26/02/2023", "27/02/2023", 
]
target_dates = pd.to_datetime(target_dates, dayfirst=True)

# Find missing dates
missing_withdrawal_dates = [date for date in target_dates if date not in withdrawals_df["Date"].values]
missing_excess_dates = [date for date in target_dates if date not in excess_df["CreatedDate"].values]

# Check for missing dates and stop if any are found
if missing_withdrawal_dates or missing_excess_dates:
    print("⚠️ Missing Dates Found:")
    if missing_withdrawal_dates:
        print(f" - In Withdrawals File: {missing_withdrawal_dates}")
    if missing_excess_dates:
        print(f" - In Excess File: {missing_excess_dates}")
    print("❌ Stopping process due to missing dates.")
    exit()

print("✅ All target dates found in both files. Proceeding with allocation...")

# Add a new column to track allocated amounts
withdrawals_df["AllocatedAmount"] = 0  

# Process each target date separately
for target_date in target_dates:
    print(f"📅 Processing Date: {target_date.strftime('%d-%m-%Y')}")

    # Filter withdrawals and excess for the current date
    filtered_withdrawals = withdrawals_df[
        (withdrawals_df["Date"] == target_date) & 
        (withdrawals_df["DepositTo"] == "As Wallet")
    ].copy()

    filtered_excess = excess_df[excess_df["CreatedDate"] == target_date].copy()

    withdrawal_index = 0  
    excess_index = 0  

    while withdrawal_index < len(filtered_withdrawals) and excess_index < len(filtered_excess):
        withdraw_row = filtered_withdrawals.iloc[withdrawal_index]
        excess_row = filtered_excess.iloc[excess_index]

        withdraw_amount = withdraw_row["InvoiceAmount"]
        allocated_so_far = withdraw_row["AllocatedAmount"]
        excess_amount = excess_row["InvoiceAmount"]

        # Determine allocation amount
        allocation = min(excess_amount, withdraw_amount - allocated_so_far)

        # Update withdrawal record
        withdrawals_df.at[filtered_withdrawals.index[withdrawal_index], "SRID"] = excess_row["SRID"]
        withdrawals_df.at[filtered_withdrawals.index[withdrawal_index], "BDID"] = excess_row["BDID"]
        withdrawals_df.at[filtered_withdrawals.index[withdrawal_index], "Mode"] = excess_row["Mode"]
        withdrawals_df.at[filtered_withdrawals.index[withdrawal_index], "ReferenceNumber"] = excess_row["ReferenceNumber"]
        withdrawals_df.at[filtered_withdrawals.index[withdrawal_index], "PayerAmount"] = excess_row["PayerAmount"]
        withdrawals_df.at[filtered_withdrawals.index[withdrawal_index], "AmountReceived1"] = excess_row["AmountReceived1"]
        withdrawals_df.at[filtered_withdrawals.index[withdrawal_index], "DepositTo"] = excess_row["DepositTo"]
        withdrawals_df.at[filtered_withdrawals.index[withdrawal_index], "AllocatedAmount"] += allocation

        # Reduce the excess invoice amount by the allocated value
        excess_df.at[filtered_excess.index[excess_index], "InvoiceAmount"] -= allocation

        # If withdrawal is fully allocated, move to the next withdrawal row
        if withdrawals_df.at[filtered_withdrawals.index[withdrawal_index], "AllocatedAmount"] >= withdraw_amount:
            withdrawal_index += 1  

        # If excess invoice is fully used, move to the next excess invoice
        if excess_df.at[filtered_excess.index[excess_index], "InvoiceAmount"] <= 0:
            excess_index += 1  

# Extract unused excess records (remaining amounts > 0)
unused_excess_df = excess_df[excess_df["InvoiceAmount"] > 0]

# Save the updated withdrawals file
withdrawals_df.to_excel("/home/thrymr/Downloads/feb_updated_withdrawals.xlsx", index=False)
unused_excess_df.to_excel("/home/thrymr/Downloads/feb_unused_excess.xlsx", index=False)

print("✅ Processing complete. Updated files saved:")
print("   - Updated Withdrawals: 'jan_updated_withdrawals.xlsx'")
print("   - Unused Excess: 'jan_unused_excess.xlsx'")
