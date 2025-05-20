import pandas as pd

def process_excel(input_file, output_file, hardcoded_dates):
    # Read the Excel file
    df = pd.read_excel(input_file, sheet_name="Bank File")

    # Standardize Date column
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True).dt.strftime("%d/%m/%Y")

    print("Original Data Columns:", df.columns)
    print("Total Rows in Original Data:", len(df))

    # Check available dates in the data
    available_dates = df["Date"].dropna().unique()
    print("Available Dates in Data:", available_dates)

    # Check if hardcoded dates exist in the data
    for date in hardcoded_dates:
        if date in available_dates:
            print(f"Date {date} is available in data.")
        else:
            print(f"Date {date} is NOT available in data.")

    # Filter based on hardcoded dates
    df = df[df["Date"].isin(hardcoded_dates)]
    print("Filtered Rows Count:", len(df))

    # Ensure numeric columns are correctly parsed
    df["PayerAmount"] = pd.to_numeric(df["PayerAmount"], errors="coerce")
    df["InvoiceAmount"] = pd.to_numeric(df["InvoiceAmount"], errors="coerce")

    # Prepare output list
    output_data = []

    # Get unique PayerAmount values excluding empty ones
    unique_payer_amounts = df["PayerAmount"].dropna().unique()
    print("Unique PayerAmount values:", unique_payer_amounts)

    for payer_amount in unique_payer_amounts:
        payer_df = df[df["PayerAmount"] == payer_amount]

        # Get unique BDID values
        unique_bdid_values = payer_df["BDID"].dropna().unique()
        print(f"PayerAmount: {payer_amount}, Unique BDIDs: {unique_bdid_values}")

        for bdid in unique_bdid_values:
            bdid_df = payer_df[payer_df["BDID"] == bdid]

            # Ensure all PayerAmount values are the same in this subset
            assert bdid_df["PayerAmount"].nunique() == 1

            # Get additional details safely
            mode = bdid_df["Mode"].iloc[0] if "Mode" in bdid_df.columns else None
            deposit_to = bdid_df["DepositTo"].iloc[0] if "DepositTo" in bdid_df.columns else None
            reference_number = bdid_df["ReferenceNumber"].iloc[0] if "ReferenceNumber" in bdid_df.columns else None

            # Calculate sum of InvoiceAmount
            invoice_sum = bdid_df["InvoiceAmount"].sum()

            # Compute balance
            balance = payer_amount - invoice_sum

            # Store result
            output_data.append({
                "BDID": bdid,
                "Date": bdid_df["Date"].iloc[0],
                "Amount Credited": payer_amount,
                "Allocated Amount": invoice_sum,
                "Balance": balance,
                "Mode": mode,
                "Bank Name": deposit_to,
                "Reference No": reference_number
            })

    # Convert to DataFrame and save to Excel
    output_df = pd.DataFrame(output_data)
    print("Output Rows Count:", len(output_df))

    output_df.to_excel(output_file, index=False)
    print("Processing complete. Output saved to:", output_file)

# Example usage
hardcoded_dates = [f"{str(i).zfill(2)}/07/2022" for i in range(1, 32)]  # Generate dates from 01/05/2023 to 31/05/2023
demo_input = "/home/thrymr/Desktop/bank_sales(22-23)/Sales_July_22.xlsx"
demo_output = "/home/thrymr/Desktop/bank_sales(22-23)/Bank_reports(22-23)/Bank_report_July(22-23).xlsx"
process_excel(demo_input, demo_output, hardcoded_dates)


