import pandas as pd
import os

# -------------------------------------------------
# 1. LOAD CUSTOMER DATABASES (ONCE)
# -------------------------------------------------
customer_files = [
    "/home/thrymr/Desktop/Customer_data/sorted_output_until_25-26(apr-sep)/new_hessathis_customerdatabase_according_to_25-26_1.xlsx",
    "/home/thrymr/Desktop/Customer_data/sorted_output_until_25-26(apr-sep)/sorted_customers_part_1.xlsx",
    "/home/thrymr/Desktop/Customer_data/sorted_output_until_25-26(apr-sep)/sorted_customers_part_2.xlsx"
]

customer_df = pd.concat(
    [pd.read_excel(f) for f in customer_files],
    ignore_index=True
)

customer_df["CustomerID"] = customer_df["CustomerID"].astype(str).str.strip()

customer_df = customer_df[
    [
        "CustomerID",
        "State",
        "District",
        "Name",
        "Mobile",
        "Address",
        "Pincode",
        "Mandal"
    ]
]

customer_df.rename(
    columns={
        "State": "Customer State",
        "District": "CustomerDistrict",
        "Name": "Customer Name",
        "Mobile": "Customer Mobile",
        "Address": "Customer Address"
    },
    inplace=True
)

# -------------------------------------------------
# 2. SALES FILE LIST
# -------------------------------------------------
sales_files = [
    "/home/thrymr/Desktop/sales 25-26/final_revised_sales(25-26)_oct-mar/dec_agri_sale(25-26).xlsx",
    "/home/thrymr/Desktop/sales 25-26/final_revised_sales(25-26)_oct-mar/dec_cons_sale(25-26).xlsx",
    "/home/thrymr/Desktop/sales 25-26/final_revised_sales(25-26)_oct-mar/feb_agri_sale(25-26).xlsx",
    "/home/thrymr/Desktop/sales 25-26/final_revised_sales(25-26)_oct-mar/feb_cons_sale(25-26).xlsx",
    "/home/thrymr/Desktop/sales 25-26/final_revised_sales(25-26)_oct-mar/jan_agri_sale(25-26).xlsx",
    "/home/thrymr/Desktop/sales 25-26/final_revised_sales(25-26)_oct-mar/jan_cons_sale(25-26).xlsx",
    "/home/thrymr/Desktop/sales 25-26/final_revised_sales(25-26)_oct-mar/mar_agri_sale(25-26).xlsx",
    "/home/thrymr/Desktop/sales 25-26/final_revised_sales(25-26)_oct-mar/mar_cons_sale(25-26).xlsx",
    "/home/thrymr/Desktop/sales 25-26/final_revised_sales(25-26)_oct-mar/nov_agri_sale(25-26).xlsx",
    "/home/thrymr/Desktop/sales 25-26/final_revised_sales(25-26)_oct-mar/nov_cons_sale(25-26).xlsx",
    "/home/thrymr/Desktop/sales 25-26/final_revised_sales(25-26)_oct-mar/oct_agri_sale(25-26).xlsx",
    "/home/thrymr/Desktop/sales 25-26/final_revised_sales(25-26)_oct-mar/oct_cons_sale(25-26).xlsx"

]

# -------------------------------------------------
# 3. COLLECT MISSING CUSTOMER RECORDS
# -------------------------------------------------
missing_customers_all = []

# -------------------------------------------------
# 4. PROCESS EACH SALES FILE
# -------------------------------------------------
for sales_file in sales_files:
    print(f"🔄 Processing: {sales_file}")

    sheets = pd.read_excel(sales_file, sheet_name=None)
    sales_df = pd.concat(sheets.values(), ignore_index=True)

    sales_df["Customer ID"] = sales_df["Customer ID"].astype(str).str.strip()

    final_df = sales_df.merge(
        customer_df,
        how="left",
        left_on="Customer ID",
        right_on="CustomerID"
    )

    final_df.drop(columns=["CustomerID"], inplace=True)

    # -----------------------------
    # Capture missing customers
    # -----------------------------
    missing_df = final_df[final_df["Customer Name"].isna()]

    if not missing_df.empty:
        missing_customers_all.append(
            missing_df[
                ["Customer ID", "State", "District"]
            ].assign(Source_File=os.path.basename(sales_file))
        )

    # -----------------------------
    # Save sales output
    # -----------------------------
    output_file = f"{os.path.splitext(sales_file)[0]}_WITH_CUSTOMERS.xlsx"
    final_df.to_excel(output_file, index=False)

    print(f"✅ Saved: {output_file}")
    print(f"📊 Rows: {len(final_df)}\n")

# -------------------------------------------------
# 5. SAVE MISSING CUSTOMER REPORT
# -------------------------------------------------
if missing_customers_all:
    missing_final = pd.concat(missing_customers_all, ignore_index=True)

    # Remove duplicates
    missing_final = missing_final.drop_duplicates(
        subset=["Customer ID", "State", "District"]
    )

    missing_output = "/home/thrymr/Downloads/missing_customer_ids_from_sales.xlsx"
    missing_final.to_excel(missing_output, index=False)

    print(f"⚠️ Missing customer report saved: {missing_output}")
    print(f"📌 Unique missing customers: {len(missing_final)}")
else:
    print("🎉 No missing customers found!")
