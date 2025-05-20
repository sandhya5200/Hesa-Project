import pandas as pd
df = pd.read_excel("/home/thrymr/Downloads/Cons_April_25_output_to_check.xlsx")

df["row_index"] = df.index

group_cols = ["Date", "Product Name", "District"]
numeric_cols = ["GST Rate","HSN Code", "Price", "Taxable Value","Adjusted Price", "Line Total","Qty", "Applied GST"]

below_half = df[df["Qty"] < 0.5].copy()
above_half = df[df["Qty"] >= 0.5].copy()

print(f"Found {len(below_half)} rows with Qty < 0.5")

def combine_values(series):
    unique_vals = series.dropna().astype(str).unique()
    return unique_vals[0] if len(unique_vals) == 1 else ", ".join(unique_vals)

agg_dict = {
    "Qty": "sum",
    "Line Total": "sum"
}
for col in df.columns:
    if col in group_cols + ["Qty", "Line Total", "row_index"]:
        continue
    elif col in numeric_cols:
        agg_dict[col] = "first"
    else:
        agg_dict[col] = combine_values

merged = below_half.groupby(group_cols, as_index=False).agg(agg_dict)
merged["row_index"] = below_half.groupby(group_cols)["row_index"].min().values

final_df = pd.concat([above_half, merged], ignore_index=True)
final_df = final_df.sort_values("row_index").drop(columns=["row_index"]).reset_index(drop=True)

#--------------------------------------------------------------------------------------------------------------

final_df["Line Total"] = pd.to_numeric(final_df["Line Total"], errors="coerce")
final_df["Applied GST"] = pd.to_numeric(final_df["Applied GST"], errors="coerce")
final_df["Applied GST"] = final_df["Applied GST"].fillna(0)


final_df["Currency"] = "INR"
final_df["igst"] = 0.0
final_df["cgst"] = (final_df["Line Total"] * final_df["Applied GST"] / 2).round(2)
final_df["sgst"] = final_df["cgst"] 
final_df["Total"] = (final_df["Line Total"] + final_df["cgst"] + final_df["sgst"] + final_df["igst"]).round(2)

final_df = final_df.drop(columns=["Taxable_Amount", "GST Rate", "Remaining Amount"], errors="ignore")

# Step 2: Rename columns
final_df = final_df.rename(columns={
    "Applied GST": "gst_rate",
    "Adjusted Price": "Net Price PU",
    "Qty": "Product Qty",
    "Line Total": "Taxable Value"
})

final_df.to_excel("/home/thrymr/Downloads/Final_Cons_April_25_output_to_check.xlsx", index=False)
print("Done. Output written with correct order and numeric types.")
