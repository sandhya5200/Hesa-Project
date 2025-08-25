import pandas as pd
import numpy as np
import random

# File paths
sales_path = r"c:\Users\ksand\Downloads\mar_2020_taxable.xlsx"
products_path = r"c:\Users\ksand\Downloads\myyy.xlsx"

# Load data
sales_df = pd.read_excel(sales_path)
products_df = pd.read_excel(products_path)

PRICE_ADJUSTMENT = 0.02
DECIMAL_UOM = ["kg", "ltr", "gm"]
MINIMUM_LINE_TOTAL = 1

matched_rows = []
unmatched_sales = []
fmcg_matched_rows = []  # For FMCG matches from remaining amounts
adjusted_price_cache = {}
used_products_per_sale = {}

def round_price(price):
    rounded_010 = round(round(price * 10) / 10, 2)  # Nearest 0.10
    rounded_10 = round(round(price / 10) * 10, 2)   # Nearest 10
    return rounded_010 if abs(price - rounded_010) <= abs(price - rounded_10) else rounded_10

def adjust_price(original_price, sale_date, district, product_name):
    key = (sale_date, district, product_name)
    if key in adjusted_price_cache:
        return adjusted_price_cache[key]
    variation = np.random.uniform(-PRICE_ADJUSTMENT, PRICE_ADJUSTMENT)
    adjusted = original_price * (1 + variation)
    adjusted = round_price(adjusted)
    adjusted_price_cache[key] = adjusted
    return adjusted

def get_available_products(subvertical, products_df, sale_date, district, sale_idx, used_products):
    """Get products for subvertical, excluding already used ones for variety"""
    filtered = products_df[products_df["Sub Vertical"] == subvertical].copy()
    
    if filtered.empty:
        return []
    
    # Add adjusted prices
    filtered["Adjusted Price"] = filtered.apply(
        lambda row: adjust_price(row["Net Price"], sale_date, district, row["Product Name"]), axis=1
    )
    
    # Remove already used products for this sale to ensure variety
    if used_products:
        filtered = filtered[~filtered["Product Name"].isin(used_products)]
    
    # If we've used all products, allow reuse but shuffle for variety
    if filtered.empty:
        filtered = products_df[products_df["Sub Vertical"] == subvertical].copy()
        filtered["Adjusted Price"] = filtered.apply(
            lambda row: adjust_price(row["Net Price"], sale_date, district, row["Product Name"]), axis=1
        )
    
    # Shuffle products for variety instead of sorting by price
    filtered = filtered.sample(frac=1).reset_index(drop=True)
    
    return list(filtered.to_dict(orient="records"))

def get_fmcg_products(products_df, sale_date, district, used_products=None):
    """Get FMCG products for remaining amounts"""
    # Look for FMCG related subverticals - adjust these based on your data
    fmcg_subverticals = ['FMCG', 'Consumer Goods', 'Grocery', 'Food & Beverages', 'Personal Care']
    
    # Try to find FMCG products - first check if any of these subverticals exist
    fmcg_products = products_df[products_df["Sub Vertical"].isin(fmcg_subverticals)].copy()
    
    # If no specific FMCG subverticals found, look for any non-Agri products
    if fmcg_products.empty:
        fmcg_products = products_df[~products_df["Sub Vertical"].str.contains("Agri", case=False, na=False)].copy()
    
    # If still empty, use all products as fallback
    if fmcg_products.empty:
        fmcg_products = products_df.copy()
    
    if fmcg_products.empty:
        return []
    
    # Add adjusted prices
    fmcg_products["Adjusted Price"] = fmcg_products.apply(
        lambda row: adjust_price(row["Net Price"], sale_date, district, row["Product Name"]), axis=1
    )
    
    # Remove already used products if specified
    if used_products:
        fmcg_products = fmcg_products[~fmcg_products["Product Name"].isin(used_products)]
    
    # Shuffle for variety
    fmcg_products = fmcg_products.sample(frac=1).reset_index(drop=True)
    
    return list(fmcg_products.to_dict(orient="records"))

def match_remaining_with_fmcg(sale_row, remaining_amount, products_df):
    """Match remaining amount with FMCG products"""
    sale_date = pd.to_datetime(sale_row.get("Date"))
    district = sale_row.get("District", "nodistrict")
    remaining = remaining_amount
    matched_items = []
    used_products = set()
    
    max_attempts = 50
    attempts = 0
    
    while remaining > MINIMUM_LINE_TOTAL and attempts < max_attempts:
        fmcg_products = get_fmcg_products(products_df, sale_date, district, used_products)
        
        if not fmcg_products:
            break
        
        added = False
        
        for prod in fmcg_products:
            if remaining <= MINIMUM_LINE_TOTAL:
                break
                
            price = prod["Adjusted Price"]
            uom = prod["UOM"].lower()
            max_qty = prod["Consumer Range To"]
            product_name = prod["Product Name"]

            if price <= 0 or max_qty <= 0:
                continue

            # Calculate quantity based on UOM
            if uom in DECIMAL_UOM:
                max_possible_qty = min(remaining / price, max_qty)
                if max_possible_qty < 0.1:
                    continue
                qty = round(random.uniform(0.1, max_possible_qty), 2)
            else:
                max_possible_qty = min(int(remaining / price), int(max_qty))
                if max_possible_qty < 1:
                    continue
                qty = random.randint(1, max_possible_qty)

            line_total = round(price * qty, 2)
            if line_total <= 0 or line_total > remaining:
                continue

            # Create FMCG matched item with original sale info but FMCG product details
            matched_items.append({
                **sale_row.to_dict(),
                "Product Name": product_name,
                "HSN Code": prod["HSN Code"],
                "Category": prod["Category"],
                "Sub Category": prod["Sub Category"],
                "Sub Vertical": prod["Sub Vertical"],  # This will be FMCG subvertical
                "Vertical": prod.get("Vertical", sale_row["Vertical"]),  # Use product's vertical or keep original
                "MRP": prod["MRP"],
                "UOM": prod["UOM"],
                "Adjusted Price": round(price, 2),
                "Qty": qty,
                "Line Total": line_total,
                "Applied GST": prod["gst_rate"],
                "Source": "FMCG_Remaining"  # Tag to identify these records
            })

            remaining -= line_total
            used_products.add(product_name)
            added = True
            break

        if not added:
            # Try with minimum quantities
            for prod in fmcg_products:
                price = prod["Adjusted Price"]
                uom = prod["UOM"].lower()
                product_name = prod["Product Name"]
                
                if price <= 0:
                    continue
                
                if uom in DECIMAL_UOM:
                    qty = 0.1
                else:
                    qty = 1
                
                line_total = round(price * qty, 2)
                if line_total <= 0 or line_total > remaining:
                    continue

                matched_items.append({
                    **sale_row.to_dict(),
                    "Product Name": product_name,
                    "HSN Code": prod["HSN Code"],
                    "Category": prod["Category"],
                    "Sub Category": prod["Sub Category"],
                    "Sub Vertical": prod["Sub Vertical"],
                    "Vertical": prod.get("Vertical", sale_row["Vertical"]),
                    "MRP": prod["MRP"],
                    "UOM": prod["UOM"],
                    "Adjusted Price": round(price, 2),
                    "Qty": qty,
                    "Line Total": line_total,
                    "Applied GST": prod["gst_rate"],
                    "Source": "FMCG_Remaining"
                })

                remaining -= line_total
                used_products.add(product_name)
                added = True
                break
            
            if not added:
                break
        
        attempts += 1

    final_remaining = round(remaining, 2)
    return matched_items, final_remaining

def match_products(sale_row, products_df, sale_idx):
    target = sale_row["Taxable_Amount"]
    subvertical = sale_row["Sub Vertical"]
    sale_date = pd.to_datetime(sale_row.get("Date"))
    district = sale_row.get("District", "nodistrict")
    remaining = target
    matched_items = []
    
    # Track used products for this sale
    used_products = set()
    
    # Try to match products with variety
    max_attempts = 100
    attempts = 0
    
    while remaining > MINIMUM_LINE_TOTAL and attempts < max_attempts:
        product_list = get_available_products(subvertical, products_df, sale_date, district, sale_idx, used_products)
        
        if not product_list:
            break
            
        added = False
        
        for prod in product_list:
            if remaining <= MINIMUM_LINE_TOTAL:
                break
                
            price = prod["Adjusted Price"]
            uom = prod["UOM"].lower()
            max_qty = prod["Consumer Range To"]
            product_name = prod["Product Name"]

            if price <= 0 or max_qty <= 0:
                continue

            # Calculate quantity based on UOM
            if uom in DECIMAL_UOM:
                max_possible_qty = min(remaining / price, max_qty)
                if max_possible_qty < 0.1:
                    continue
                qty = round(random.uniform(0.1, max_possible_qty), 2)
            else:
                max_possible_qty = min(int(remaining / price), int(max_qty))
                if max_possible_qty < 1:
                    continue
                qty = random.randint(1, max_possible_qty)

            line_total = round(price * qty, 2)
            if line_total <= 0 or line_total > remaining:
                continue

            matched_items.append({
                **sale_row.to_dict(),
                "Product Name": product_name,
                "HSN Code": prod["HSN Code"],
                "Category": prod["Category"],
                "Sub Category": prod["Sub Category"],
                "MRP": prod["MRP"],
                "UOM": prod["UOM"],
                "Adjusted Price": round(price, 2),
                "Qty": qty,
                "Line Total": line_total,
                "Applied GST": prod["gst_rate"],
                "Source": "Original"  # Tag original matches
            })

            remaining -= line_total
            used_products.add(product_name)
            added = True
            break

        if not added:
            # Try with smaller quantities
            for prod in product_list:
                price = prod["Adjusted Price"]
                uom = prod["UOM"].lower()
                product_name = prod["Product Name"]
                
                if price <= 0:
                    continue
                
                if uom in DECIMAL_UOM:
                    qty = 0.1
                    if price * qty > remaining:
                        continue
                else:
                    qty = 1
                    if price * qty > remaining:
                        continue
                
                line_total = round(price * qty, 2)
                if line_total <= 0:
                    continue

                matched_items.append({
                    **sale_row.to_dict(),
                    "Product Name": product_name,
                    "HSN Code": prod["HSN Code"],
                    "Category": prod["Category"],
                    "Sub Category": prod["Sub Category"],
                    "MRP": prod["MRP"],
                    "UOM": prod["UOM"],
                    "Adjusted Price": round(price, 2),
                    "Qty": qty,
                    "Line Total": line_total,
                    "Applied GST": prod["gst_rate"],
                    "Source": "Original"
                })

                remaining -= line_total
                used_products.add(product_name)
                added = True
                break
            
            if not added:
                break
        
        attempts += 1

    total_used = sum(i["Line Total"] for i in matched_items)
    remaining_amount = round(target - total_used, 2)

    return matched_items, remaining_amount

# Process sales
for idx, sale_row in sales_df.iterrows():
    print(f"Processing sale row {idx+1}/{len(sales_df)}")
    matches, remaining_amt = match_products(sale_row, products_df, idx)
    
    if matches:
        matched_rows.extend(matches)
    
    # If there's remaining amount > MINIMUM_LINE_TOTAL, try to match with FMCG
    if remaining_amt > MINIMUM_LINE_TOTAL:
        print(f"  -> Trying to match remaining {remaining_amt} with FMCG products")
        fmcg_matches, final_remaining = match_remaining_with_fmcg(sale_row, remaining_amt, products_df)
        
        if fmcg_matches:
            fmcg_matched_rows.extend(fmcg_matches)
            print(f"  -> Matched {len(fmcg_matches)} FMCG products, remaining: {final_remaining}")
        
        # Only add to unmatched if still has significant remaining
        if final_remaining > MINIMUM_LINE_TOTAL:
            unmatched_sales.append({**sale_row.to_dict(), "Remaining Amount": final_remaining})

# Combine all matched rows
all_matched_rows = matched_rows + fmcg_matched_rows

# Save unmatched sales if any
if unmatched_sales:
    unmatched_df = pd.DataFrame(unmatched_sales)
    unmatched_path = r"c:\Users\ksand\Downloads\unmatched.xlsx"
    unmatched_df.to_excel(unmatched_path, index=False)
    print(f"Unmatched sales saved to {unmatched_path}")
else:
    print("No unmatched sales found - all remaining amounts matched with FMCG!")

# Create final dataframe
matched_df = pd.DataFrame(all_matched_rows)

if matched_df.empty:
    print("No matches found!")
    exit()

# Add row index for processing
matched_df["row_index"] = matched_df.index

# Combine small quantities (< 0.5)
group_cols = ["Date", "Product Name", "District"]
below_half = matched_df[matched_df["Qty"] < 0.5].copy()
above_half = matched_df[matched_df["Qty"] >= 0.5].copy()

print(f"Found {len(below_half)} rows with Qty < 0.5")

def combine_values(series):
    unique_vals = series.dropna().astype(str).unique()
    return unique_vals[0] if len(unique_vals) == 1 else ", ".join(unique_vals)

agg_dict = {
    "Qty": "sum",
    "Line Total": "sum"
}
for col in matched_df.columns:
    if col in group_cols + ["Qty", "Line Total", "row_index"]:
        continue
    else:
        agg_dict[col] = combine_values

if not below_half.empty:
    merged = below_half.groupby(group_cols, as_index=False).agg(agg_dict)
    merged["row_index"] = below_half.groupby(group_cols)["row_index"].min().values
    final_df = pd.concat([above_half, merged], ignore_index=True)
else:
    final_df = above_half.copy()

final_df = final_df.sort_values("row_index").drop(columns=["row_index"]).reset_index(drop=True)

# Calculate additional fields
final_df["Line Total"] = pd.to_numeric(final_df["Line Total"], errors="coerce")
final_df["Applied GST"] = pd.to_numeric(final_df["Applied GST"], errors="coerce")
final_df["Applied GST"] = final_df["Applied GST"].fillna(0)
final_df["MRP"] = pd.to_numeric(final_df["MRP"], errors="coerce")
final_df["Adjusted Price"] = pd.to_numeric(final_df["Adjusted Price"], errors="coerce")

# Calculate derived fields
final_df["Disc_percent"] = (final_df["Adjusted Price"] * (1 + final_df["Applied GST"]/100)).round(2)
final_df["Disc PU"] = ((final_df["MRP"] - final_df["Adjusted Price"]) / final_df["MRP"]).round(2)
final_df["Currency"] = "INR"
final_df["Facilitator"] = ""

# Set facilitator based on vertical
final_df.loc[final_df["Vertical"] == "Agri Business", "Facilitator"] = "Hesa Agritech Private Limited"
final_df.loc[final_df["Vertical"] == "Commerce Business", "Facilitator"] = "Hesa Consumer Products Private Limited"

# Calculate GST amounts
final_df["igst"] = 0.0
final_df["cgst"] = (final_df["Line Total"] * final_df["Applied GST"] / 200).round(2)
final_df["sgst"] = final_df["cgst"] 
final_df["Total"] = (final_df["Line Total"] + final_df["cgst"] + final_df["sgst"] + final_df["igst"]).round(2)

# Clean up columns
final_df = final_df.drop(columns=["Taxable_Amount", "GST Rate", "Remaining Amount", "percentage_of_total", "normalized_percentage"], errors="ignore")

# Rename columns
final_df = final_df.rename(columns={
    "Applied GST": "gst_rate",
    "Adjusted Price": "Net Price PU",
    "Qty": "Product Qty",
    "Line Total": "Taxable Value"
})

# Save output
output_path = r"c:\Users\ksand\Downloads\mar_2020_products.xlsx"
final_df.to_excel(output_path, index=False)

# Print summary
print(f"\n=== PROCESSING SUMMARY ===")
print(f"Original matches: {len(matched_rows)}")
print(f"FMCG matches (from remaining): {len(fmcg_matched_rows)}")
print(f"Total final records: {len(final_df)}")
print(f"Unmatched sales: {len(unmatched_sales)}")
print(f"Final output saved to {output_path}")

# Show breakdown by source
if 'Source' in final_df.columns:
    source_breakdown = final_df['Source'].value_counts()
    print(f"\nBreakdown by source:")
    for source, count in source_breakdown.items():
        print(f"  {source}: {count} records")

print("Done!")
