import pandas as pd

# -----------------------------
# Load allocated sales file
# -----------------------------
input_path = r"c:\Users\ksand\Downloads\sales_with_bank_details_cons_april.xlsx"
df = pd.read_excel(input_path)

# -----------------------------
# Ensure date column
# -----------------------------
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# -----------------------------
# Group & Aggregate
# -----------------------------
summary = (
    df.groupby("Invoice No", dropna=False)
    .agg(
        Hesaathi_Code=("Assigned Hesaathi Code", "first"),
        Customer_Id=("Customer ID", "first"),
        Facilitator=("Facilitator", "first"),
        Order_Id=("Order ID", "first"),
        Zoho_Invoice=("Zoho Invoice", lambda x: x.dropna().iloc[0] if not x.dropna().empty else ""),
        
        Invoice_Total=("Total", "sum"),
        Paid_through_BT=("Bank Amount Allocated", "sum"),
        Paid_through_Wallet=("Wallet Amount", "sum"),

        # ---- BANK DETAILS (first non-null) ----
        Mode=("Mode", lambda x: x.dropna().iloc[0] if not x.dropna().empty else ""),
        Description=("Description", lambda x: x.dropna().iloc[0] if not x.dropna().empty else ""),
        Amount=("Amount", lambda x: x.dropna().iloc[0] if not x.dropna().empty else ""),
        Customer_Name=("Customer Name", lambda x: x.dropna().iloc[0] if not x.dropna().empty else ""),
        Deposit_To=("Deposit To", lambda x: x.dropna().iloc[0] if not x.dropna().empty else ""),

        Transaction_Date=("Date", "first")
    )
    .reset_index()
)

# -----------------------------
# Deposit To (Bank / Wallet) — Allocation based
# -----------------------------
summary["Deposit to"] = summary["Paid_through_BT"].apply(
    lambda x: "Bank" if x > 0 else "Wallet"
)

# -----------------------------
# Serial Number
# -----------------------------
summary.insert(0, "S_No", range(1, len(summary) + 1))

# -----------------------------
# Column Ordering (FINAL)
# -----------------------------
summary = summary[
    [
        "S_No",
        "Hesaathi_Code",
        "Customer_Id",
        "Facilitator",
        "Invoice No",
        "Zoho_Invoice",
        "Order_Id",

        "Deposit to",        # Bank / Wallet
        "Deposit_To",        # Bank column

        "Invoice_Total",
        "Paid_through_BT",
        "Paid_through_Wallet",

        "Mode",
        "Description",
        "Amount",
        "Customer_Name",

        "Transaction_Date",
    ]
]

# -----------------------------
# Save Summary File
# -----------------------------
output_path = r"c:\Users\ksand\Downloads\summary_of_april_cons.xlsx"
summary.to_excel(output_path, index=False)

print("✅ Summary file created:", output_path)
