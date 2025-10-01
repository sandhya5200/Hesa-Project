import pandas as pd

file1 = "/home/thrymr/Downloads/sales file with customer data 24-25(oct-mar)/March_2025_Sales_Data-2_Sheet1.xlsx"
file2 = "/home/thrymr/Downloads/sales file with customer data 24-25(oct-mar)/March_2025_Sales_Data-2_Sheet2.xlsx"
file3 = "/home/thrymr/Downloads/sales file with customer data 24-25(oct-mar)/March_2025_Sales_Data-2_Sheet3.xlsx"

df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)
df3 = pd.read_excel(file3)

df = pd.concat([df1, df2, df3], ignore_index=True)

first_info = df.groupby("Invoice No").first().reset_index()

totals = df.groupby("Invoice No", as_index=False)["Sub total"].sum().rename(columns={"Sub total": "Invoice Total"})

summary = pd.merge(first_info, totals, on="Invoice No", how="inner")

summary = summary[[
    "Date", "Hesaathi Code", "CustomerID", "Customer State", "CustomerDistrict",
    "Facilitator", "Vertical", "Order_Id", "Invoice No", "Invoice Total"
]]

summary.insert(0, "Sl No", range(1, len(summary) + 1))

output_file = "/home/thrymr/Downloads/invoice_summary.xlsx"
summary.to_excel(output_file, index=False)

print(f"✅ Summary file generated: {output_file}")





