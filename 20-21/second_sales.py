import pandas as pd
import numpy as np
import random

# File paths
sales_path = r"c:\Users\ksand\Downloads\dec_2020_taxable.xlsx"
products_path = r"c:\Users\ksand\Downloads\myyy.xlsx"

# Load data
sales_df = pd.read_excel(sales_path)
products_df = pd.read_excel(products_path)

# Convert decimal GST rates to percentages in BOTH files
# 0.05 -> 5, 0.12 -> 12, 0.18 -> 18, 0.00 -> 0
print(f"Original GST rates in sales data: {sorted(sales_df['GST Rate'].unique())}")
print(f"Original GST rates in products data: {sorted(products_df['gst_rate'].unique())}")

# Handle the conversion more carefully for both zero and non-zero values
sales_df["GST Rate"] = (sales_df["GST Rate"] * 100).round(0).astype(int)
products_df["gst_rate"] = (products_df["gst_rate"] * 100).round(0).astype(int)

print(f"\nConverted GST rates in sales data: {sorted(sales_df['GST Rate'].unique())}")
print(f"Converted GST rates in products data: {sorted(products_df['gst_rate'].unique())}")

# Check for zero GST rates specifically
zero_gst_sales = len(sales_df[sales_df['GST Rate'] == 0])
zero_gst_products = len(products_df[products_df['gst_rate'] == 0])
print(f"\nZero GST entries - Sales: {zero_gst_sales}, Products: {zero_gst_products}")

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

def get_available_products(subvertical, gst_rate, products_df, sale_date, district, sale_idx, used_products):
    """Get products for subvertical and specific GST rate, excluding already used ones for variety"""
    # First filter by subvertical AND GST rate
    filtered = products_df[
        (products_df["Sub Vertical"] == subvertical) & 
        (products_df["gst_rate"] == gst_rate)
    ].copy()
    
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
        filtered = products_df[
            (products_df["Sub Vertical"] == subvertical) & 
            (products_df["gst_rate"] == gst_rate)
        ].copy()
        filtered["Adjusted Price"] = filtered.apply(
            lambda row: adjust_price(row["Net Price"], sale_date, district, row["Product Name"]), axis=1
        )
    
    # Shuffle products for variety instead of sorting by price
    filtered = filtered.sample(frac=1).reset_index(drop=True)
    
    return list(filtered.to_dict(orient="records"))

def get_fmcg_products(gst_rate, products_df, sale_date, district, used_products=None):
    """Get FMCG products for remaining amounts with matching GST rate"""
    # Look for FMCG related subverticals - adjust these based on your data
    fmcg_subverticals = ['FMCG', 'Consumer Goods', 'Grocery', 'Food & Beverages', 'Personal Care']
    
    # Try to find FMCG products with matching GST rate
    fmcg_products = products_df[
        (products_df["Sub Vertical"].isin(fmcg_subverticals)) &
        (products_df["gst_rate"] == gst_rate)
    ].copy()
    
    # If no specific FMCG subverticals found, look for any non-Agri products with matching GST
    if fmcg_products.empty:
        fmcg_products = products_df[
            (~products_df["Sub Vertical"].str.contains("Agri", case=False, na=False)) &
            (products_df["gst_rate"] == gst_rate)
        ].copy()
    
    # If still empty, use all products with matching GST as fallback
    if fmcg_products.empty:
        fmcg_products = products_df[products_df["gst_rate"] == gst_rate].copy()
    
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
    """Match remaining amount with FMCG products that have the same GST rate - STRICT GST MATCHING"""
    sale_date = pd.to_datetime(sale_row.get("Date"))
    district = sale_row.get("District", "nodistrict")
    sale_gst_rate = sale_row.get("GST Rate", 0)  # Get the original GST rate from sale
    remaining = remaining_amount
    matched_items = []
    used_products = set()
    
    print(f"    -> Trying to match remaining {remaining_amount} with products having GST rate {sale_gst_rate}%")
    
    max_attempts = 50
    attempts = 0
    
    while remaining > MINIMUM_LINE_TOTAL and attempts < max_attempts:
        fmcg_products = get_fmcg_products(sale_gst_rate, products_df, sale_date, district, used_products)
        
        if not fmcg_products:
            print(f"    -> No FMCG products available with GST rate {sale_gst_rate}% for remaining amount")
            break
        
        added = False
        
        for prod in fmcg_products:
            if remaining <= MINIMUM_LINE_TOTAL:
                break
                
            # Verify GST rate match (extra safety check)
            if prod["gst_rate"] != sale_gst_rate:
                continue
                
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

            # Create FMCG matched item - PRESERVE ORIGINAL SALE'S GST RATE
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
                "Applied GST": sale_gst_rate,  # KEEP ORIGINAL SALE'S GST RATE
                "Source": f"FMCG_Remaining_GST{sale_gst_rate}%"  # Tag to identify these records
            })

            remaining -= line_total
            used_products.add(product_name)
            added = True
            break

        if not added:
            # Try with minimum quantities but still maintain GST rate consistency
            for prod in fmcg_products:
                # Verify GST rate match (extra safety check)
                if prod["gst_rate"] != sale_gst_rate:
                    continue
                    
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
                    "Applied GST": sale_gst_rate,  # KEEP ORIGINAL SALE'S GST RATE
                    "Source": f"FMCG_Remaining_GST{sale_gst_rate}%"
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
    sale_gst_rate = sale_row["GST Rate"]  # Get the GST rate from the sale
    sale_date = pd.to_datetime(sale_row.get("Date"))
    district = sale_row.get("District", "nodistrict")
    remaining = target
    matched_items = []
    
    # Track used products for this sale
    used_products = set()
    
    # Try to match products with variety and SAME GST rate
    max_attempts = 100
    attempts = 0
    
    while remaining > MINIMUM_LINE_TOTAL and attempts < max_attempts:
        product_list = get_available_products(subvertical, sale_gst_rate, products_df, sale_date, district, sale_idx, used_products)
        
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
                "Applied GST": prod["gst_rate"],  # This will always match the sale's GST rate
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
                    "Applied GST": prod["gst_rate"],  # This will always match the sale's GST rate
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

# Get unique GST rates from sales and sort them
unique_gst_rates = sorted(sales_df["GST Rate"].unique())
print(f"\nProcessing GST rates in order: {unique_gst_rates}")

# Verify that products have matching GST rates
product_gst_rates = sorted(products_df["gst_rate"].unique())
print(f"Available product GST rates: {product_gst_rates}")

# Check for potential mismatches
missing_gst_rates = set(unique_gst_rates) - set(product_gst_rates)
if missing_gst_rates:
    print(f"WARNING: Sales have GST rates {missing_gst_rates} but no products available for these rates!")

# Process sales by GST rate groups
for gst_rate in unique_gst_rates:
    print(f"\n=== PROCESSING GST RATE: {gst_rate}% ===")
    
    # Filter sales for current GST rate
    current_gst_sales = sales_df[sales_df["GST Rate"] == gst_rate].copy()
    print(f"Found {len(current_gst_sales)} sales with GST rate {gst_rate}%")
    
    # Filter products for current GST rate
    current_gst_products = products_df[products_df["gst_rate"] == gst_rate].copy()
    print(f"Found {len(current_gst_products)} products with GST rate {gst_rate}%")
    
    if current_gst_products.empty:
        print(f"No products found for GST rate {gst_rate}% - adding all sales to unmatched")
        for idx, sale_row in current_gst_sales.iterrows():
            unmatched_sales.append({
                **sale_row.to_dict(), 
                "Remaining Amount": sale_row["Taxable_Amount"],
                "Reason": f"No products available for GST rate {gst_rate}%"
            })
        continue
    
    # Process each sale in this GST rate group
    for idx, sale_row in current_gst_sales.iterrows():
        print(f"Processing sale row {idx+1} (GST: {gst_rate}%)")
        matches, remaining_amt = match_products(sale_row, current_gst_products, idx)
        
        if matches:
            matched_rows.extend(matches)
            print(f"  -> Matched {len(matches)} products, remaining: {remaining_amt}")
        
        # If there's remaining amount > MINIMUM_LINE_TOTAL, try to match with FMCG products with SAME GST rate
        if remaining_amt > MINIMUM_LINE_TOTAL:
            print(f"  -> Trying to match remaining {remaining_amt} with FMCG products (GST: {gst_rate}%)")
            fmcg_matches, final_remaining = match_remaining_with_fmcg(sale_row, remaining_amt, current_gst_products)
            
            if fmcg_matches:
                fmcg_matched_rows.extend(fmcg_matches)
                print(f"  -> Matched {len(fmcg_matches)} FMCG products, remaining: {final_remaining}")
            
            # Only add to unmatched if still has significant remaining
            if final_remaining > MINIMUM_LINE_TOTAL:
                unmatched_sales.append({
                    **sale_row.to_dict(), 
                    "Remaining Amount": final_remaining,
                    "Reason": f"Could not fully match with GST rate {gst_rate}% products"
                })

# Combine all matched rows
all_matched_rows = matched_rows + fmcg_matched_rows

# Save unmatched sales if any
if unmatched_sales:
    unmatched_df = pd.DataFrame(unmatched_sales)
    unmatched_path = r"c:\Users\ksand\Downloads\unmatched.xlsx"
    unmatched_df.to_excel(unmatched_path, index=False)
    print(f"\nUnmatched sales saved to {unmatched_path}")
else:
    print("\nNo unmatched sales found - all remaining amounts matched with correct GST rates!")

# Create final dataframe
matched_df = pd.DataFrame(all_matched_rows)

if matched_df.empty:
    print("No matches found!")
    exit()

# Verify GST rate consistency
print(f"\n=== GST RATE VERIFICATION ===")
gst_mismatch = matched_df[matched_df["GST Rate"] != matched_df["Applied GST"]]
if not gst_mismatch.empty:
    print(f"WARNING: Found {len(gst_mismatch)} rows with GST rate mismatch!")
    print("This should not happen with the new logic.")
else:
    print("✓ All matched products have consistent GST rates with their sales!")

# Add row index for processing
matched_df["row_index"] = matched_df.index

# Combine small quantities (< 0.5)
group_cols = ["Date", "Product Name", "District"]
below_half = matched_df[matched_df["Qty"] < 0.5].copy()
above_half = matched_df[matched_df["Qty"] >= 0.5].copy()

print(f"\nFound {len(below_half)} rows with Qty < 0.5")

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

# Calculate GST amounts - using the correct GST rate
final_df["igst"] = 0.0
final_df["cgst"] = (final_df["Line Total"] * final_df["Applied GST"] / 200).round(2)
final_df["sgst"] = final_df["cgst"] 
final_df["Total"] = (final_df["Line Total"] + final_df["cgst"] + final_df["sgst"] + final_df["igst"]).round(2)

# Clean up columns
final_df = final_df.drop(columns=["Taxable_Amount", "GST Rate", "Remaining Amount", "percentage_of_total", "normalized_percentage", "Reason"], errors="ignore")

# Rename columns
final_df = final_df.rename(columns={
    "Applied GST": "gst_rate",
    "Adjusted Price": "Net Price PU",
    "Qty": "Product Qty",
    "Line Total": "Taxable Value"
})

# Save output
output_path = r"c:\Users\ksand\Downloads\dec_2020_products.xlsx"
final_df.to_excel(output_path, index=False)

# Print summary
print(f"\n=== PROCESSING SUMMARY ===")
print(f"Original matches: {len(matched_rows)}")
print(f"FMCG matches (from remaining): {len(fmcg_matched_rows)}")
print(f"Total final records: {len(final_df)}")
print(f"Unmatched sales: {len(unmatched_sales)}")
print(f"Final output saved to {output_path}")

# Show breakdown by source and GST rate
if 'Source' in final_df.columns:
    print(f"\nBreakdown by source:")
    source_breakdown = final_df['Source'].value_counts()
    for source, count in source_breakdown.items():
        print(f"  {source}: {count} records")

print(f"\nBreakdown by GST rate:")
gst_breakdown = final_df['gst_rate'].value_counts().sort_index()
for gst_rate, count in gst_breakdown.items():
    print(f"  {gst_rate}%: {count} records")

# Final verification
print(f"\n=== FINAL GST VERIFICATION ===")
original_gst_distribution = sales_df['GST Rate'].value_counts().sort_index()
final_gst_distribution = final_df['gst_rate'].value_counts().sort_index()

print("Original sales GST distribution:")
for gst_rate, count in original_gst_distribution.items():
    print(f"  {gst_rate}%: {count} sales")

print("Final products GST distribution:")
for gst_rate, count in final_gst_distribution.items():
    print(f"  {gst_rate}%: {count} product lines")

print("Done!")

# import pandas as pd
# import numpy as np
# import random

# # File paths
# sales_path = r"c:\Users\ksand\Downloads\may_2020_taxable.xlsx"
# products_path = r"c:\Users\ksand\Downloads\myyy.xlsx"

# # Load data
# sales_df = pd.read_excel(sales_path)
# products_df = pd.read_excel(products_path)

# # PRIORITY PRODUCTS LIST - These will appear more frequently
# PRIORITY_PRODUCTS = [
#     "Surya Chilli Powder 500g",
#     "Vittle Foods Toor Dall 1k", 
#     "Sugar 1 kg",
#     "Sona Masoori Rice (G) 25",
#     "Whole Wheat atta 1 kg",
#     "Aashirvaad free flow salt",
#     "Aplus Chakki atta 1 kg",
#     "Tur Dal 1kg",
#     "Trust refined Sugar 1 kg",
#     "TATA Salt 1 kg",
#     "Parijat chilli powder 100g",
#     "Sougat chakki atta 1kg",
#     "Shubalaxmi chilli powder 100g",
#     "Aashirvaad salt 1kg",
#     "Madhur Sugar S30 1 kg",
#     "Rewa Super kg",
#     "Subhalaxmi tur dal economy 1 kg",
#     "Shudhh Aadhar maida 1kg",
#     "BSF Chilli powder 100g",
#     "Reeth parmal raw rice 5kg",
#     "Chilli powder 100gms",
#     "Madhuram steam rice (half boiled) Deluxe",
#     "Madhuram toor dall deluxe",
#     "Onion 55MM fresh - kg",
#     "Potato fresh - kg",
#     "Sooji kg",
#     "Sugar (S30)",
#     "Table Salt kg",
#     "Tamarind kg"
# ]

# # PRIORITY MULTIPLIER - How many times more likely priority products should appear
# PRIORITY_MULTIPLIER = 5  # Priority products are 5x more likely to be selected

# # Convert decimal GST rates to percentages in BOTH files
# print(f"Original GST rates in sales data: {sorted(sales_df['GST Rate'].unique())}")
# print(f"Original GST rates in products data: {sorted(products_df['gst_rate'].unique())}")

# sales_df["GST Rate"] = (sales_df["GST Rate"] * 100).round(0).astype(int)
# products_df["gst_rate"] = (products_df["gst_rate"] * 100).round(0).astype(int)

# print(f"\nConverted GST rates in sales data: {sorted(sales_df['GST Rate'].unique())}")
# print(f"Converted GST rates in products data: {sorted(products_df['gst_rate'].unique())}")

# # Check for zero GST rates specifically
# zero_gst_sales = len(sales_df[sales_df['GST Rate'] == 0])
# zero_gst_products = len(products_df[products_df['gst_rate'] == 0])
# print(f"\nZero GST entries - Sales: {zero_gst_sales}, Products: {zero_gst_products}")

# # Check which priority products exist in the dataset
# existing_priority_products = []
# for product in PRIORITY_PRODUCTS:
#     if product in products_df["Product Name"].values:
#         existing_priority_products.append(product)
#     else:
#         print(f"WARNING: Priority product '{product}' not found in products dataset")

# print(f"\nFound {len(existing_priority_products)} priority products in dataset:")
# for product in existing_priority_products[:5]:  # Show first 5
#     print(f"  - {product}")
# if len(existing_priority_products) > 5:
#     print(f"  ... and {len(existing_priority_products) - 5} more")

# PRICE_ADJUSTMENT = 0.02
# DECIMAL_UOM = ["kg", "ltr", "gm"]
# MINIMUM_LINE_TOTAL = 1

# matched_rows = []
# unmatched_sales = []
# fmcg_matched_rows = []
# adjusted_price_cache = {}
# used_products_per_sale = {}

# def round_price(price):
#     rounded_010 = round(round(price * 10) / 10, 2)
#     rounded_10 = round(round(price / 10) * 10, 2)
#     return rounded_010 if abs(price - rounded_010) <= abs(price - rounded_10) else rounded_10

# def adjust_price(original_price, sale_date, district, product_name):
#     key = (sale_date, district, product_name)
#     if key in adjusted_price_cache:
#         return adjusted_price_cache[key]
#     variation = np.random.uniform(-PRICE_ADJUSTMENT, PRICE_ADJUSTMENT)
#     adjusted = original_price * (1 + variation)
#     adjusted = round_price(adjusted)
#     adjusted_price_cache[key] = adjusted
#     return adjusted

# def get_weighted_product_selection(products_list, priority_products):
#     """
#     Create a weighted selection where priority products have higher chance of being selected
#     """
#     if not products_list:
#         return []
    
#     # Create weighted list
#     weighted_products = []
    
#     for product in products_list:
#         product_name = product["Product Name"]
        
#         # Add priority products multiple times to increase their selection probability
#         if product_name in priority_products:
#             # Add priority product multiple times
#             for _ in range(PRIORITY_MULTIPLIER):
#                 weighted_products.append(product)
#         else:
#             # Add regular product once
#             weighted_products.append(product)
    
#     # Shuffle the weighted list
#     random.shuffle(weighted_products)
#     return weighted_products

# def get_available_products(subvertical, gst_rate, products_df, sale_date, district, sale_idx, used_products):
#     """Get products for subvertical and specific GST rate, with priority weighting"""
#     # First filter by subvertical AND GST rate
#     filtered = products_df[
#         (products_df["Sub Vertical"] == subvertical) & 
#         (products_df["gst_rate"] == gst_rate)
#     ].copy()
    
#     if filtered.empty:
#         return []
    
#     # Add adjusted prices
#     filtered["Adjusted Price"] = filtered.apply(
#         lambda row: adjust_price(row["Net Price"], sale_date, district, row["Product Name"]), axis=1
#     )
    
#     # Convert to list of dictionaries
#     product_list = list(filtered.to_dict(orient="records"))
    
#     # Apply priority weighting
#     weighted_products = get_weighted_product_selection(product_list, existing_priority_products)
    
#     # Remove already used products for this sale (but allow some reuse for priority products)
#     if used_products:
#         # For priority products, allow reuse after using them twice
#         available_products = []
#         for product in weighted_products:
#             product_name = product["Product Name"]
#             if product_name in existing_priority_products:
#                 # Priority products can be reused more often
#                 usage_count = used_products.get(product_name, 0)
#                 if usage_count < 3:  # Allow priority products to be used up to 3 times
#                     available_products.append(product)
#             else:
#                 # Regular products - use only once
#                 if product_name not in used_products:
#                     available_products.append(product)
        
#         if available_products:
#             return available_products
    
#     # If no products available due to usage restrictions, reset and allow reuse
#     return weighted_products

# def get_fmcg_products(gst_rate, products_df, sale_date, district, used_products=None):
#     """Get FMCG products for remaining amounts with matching GST rate and priority weighting"""
#     # Look for FMCG related subverticals
#     fmcg_subverticals = ['FMCG', 'Consumer Goods', 'Grocery', 'Food & Beverages', 'Personal Care']
    
#     # Try to find FMCG products with matching GST rate
#     fmcg_products = products_df[
#         (products_df["Sub Vertical"].isin(fmcg_subverticals)) &
#         (products_df["gst_rate"] == gst_rate)
#     ].copy()
    
#     # If no specific FMCG subverticals found, look for any non-Agri products with matching GST
#     if fmcg_products.empty:
#         fmcg_products = products_df[
#             (~products_df["Sub Vertical"].str.contains("Agri", case=False, na=False)) &
#             (products_df["gst_rate"] == gst_rate)
#         ].copy()
    
#     # If still empty, use all products with matching GST as fallback
#     if fmcg_products.empty:
#         fmcg_products = products_df[products_df["gst_rate"] == gst_rate].copy()
    
#     if fmcg_products.empty:
#         return []
    
#     # Add adjusted prices
#     fmcg_products["Adjusted Price"] = fmcg_products.apply(
#         lambda row: adjust_price(row["Net Price"], sale_date, district, row["Product Name"]), axis=1
#     )
    
#     # Convert to list and apply priority weighting
#     product_list = list(fmcg_products.to_dict(orient="records"))
#     weighted_products = get_weighted_product_selection(product_list, existing_priority_products)
    
#     return weighted_products

# def match_remaining_with_fmcg(sale_row, remaining_amount, products_df):
#     """Match remaining amount with FMCG products that have the same GST rate - STRICT GST MATCHING"""
#     sale_date = pd.to_datetime(sale_row.get("Date"))
#     district = sale_row.get("District", "nodistrict")
#     sale_gst_rate = sale_row.get("GST Rate", 0)
#     remaining = remaining_amount
#     matched_items = []
#     used_products = {}  # Changed to dict to track usage count
    
#     print(f"    -> Trying to match remaining {remaining_amount} with products having GST rate {sale_gst_rate}%")
    
#     max_attempts = 50
#     attempts = 0
    
#     while remaining > MINIMUM_LINE_TOTAL and attempts < max_attempts:
#         fmcg_products = get_fmcg_products(sale_gst_rate, products_df, sale_date, district, used_products)
        
#         if not fmcg_products:
#             print(f"    -> No FMCG products available with GST rate {sale_gst_rate}% for remaining amount")
#             break
        
#         added = False
        
#         for prod in fmcg_products:
#             if remaining <= MINIMUM_LINE_TOTAL:
#                 break
                
#             # Verify GST rate match
#             if prod["gst_rate"] != sale_gst_rate:
#                 continue
                
#             price = prod["Adjusted Price"]
#             uom = prod["UOM"].lower()
#             max_qty = prod["Consumer Range To"]
#             product_name = prod["Product Name"]

#             if price <= 0 or max_qty <= 0:
#                 continue

#             # Calculate quantity based on UOM
#             if uom in DECIMAL_UOM:
#                 max_possible_qty = min(remaining / price, max_qty)
#                 if max_possible_qty < 0.1:
#                     continue
#                 qty = round(random.uniform(0.1, max_possible_qty), 2)
#             else:
#                 max_possible_qty = min(int(remaining / price), int(max_qty))
#                 if max_possible_qty < 1:
#                     continue
#                 qty = random.randint(1, max_possible_qty)

#             line_total = round(price * qty, 2)
#             if line_total <= 0 or line_total > remaining:
#                 continue

#             # Create FMCG matched item
#             matched_items.append({
#                 **sale_row.to_dict(),
#                 "Product Name": product_name,
#                 "HSN Code": prod["HSN Code"],
#                 "Category": prod["Category"],
#                 "Sub Category": prod["Sub Category"],
#                 "Sub Vertical": prod["Sub Vertical"],
#                 "Vertical": prod.get("Vertical", sale_row["Vertical"]),
#                 "MRP": prod["MRP"],
#                 "UOM": prod["UOM"],
#                 "Adjusted Price": round(price, 2),
#                 "Qty": qty,
#                 "Line Total": line_total,
#                 "Applied GST": sale_gst_rate,
#                 "Source": f"FMCG_Remaining_GST{sale_gst_rate}%"
#             })

#             remaining -= line_total
#             # Track usage count
#             used_products[product_name] = used_products.get(product_name, 0) + 1
#             added = True
#             break

#         if not added:
#             # Try with minimum quantities but still maintain GST rate consistency
#             for prod in fmcg_products:
#                 if prod["gst_rate"] != sale_gst_rate:
#                     continue
                    
#                 price = prod["Adjusted Price"]
#                 uom = prod["UOM"].lower()
#                 product_name = prod["Product Name"]
                
#                 if price <= 0:
#                     continue
                
#                 if uom in DECIMAL_UOM:
#                     qty = 0.1
#                 else:
#                     qty = 1
                
#                 line_total = round(price * qty, 2)
#                 if line_total <= 0 or line_total > remaining:
#                     continue

#                 matched_items.append({
#                     **sale_row.to_dict(),
#                     "Product Name": product_name,
#                     "HSN Code": prod["HSN Code"],
#                     "Category": prod["Category"],
#                     "Sub Category": prod["Sub Category"],
#                     "Sub Vertical": prod["Sub Vertical"],
#                     "Vertical": prod.get("Vertical", sale_row["Vertical"]),
#                     "MRP": prod["MRP"],
#                     "UOM": prod["UOM"],
#                     "Adjusted Price": round(price, 2),
#                     "Qty": qty,
#                     "Line Total": line_total,
#                     "Applied GST": sale_gst_rate,
#                     "Source": f"FMCG_Remaining_GST{sale_gst_rate}%"
#                 })

#                 remaining -= line_total
#                 used_products[product_name] = used_products.get(product_name, 0) + 1
#                 added = True
#                 break
            
#             if not added:
#                 break
        
#         attempts += 1

#     final_remaining = round(remaining, 2)
#     return matched_items, final_remaining

# def match_products(sale_row, products_df, sale_idx):
#     target = sale_row["Taxable_Amount"]
#     subvertical = sale_row["Sub Vertical"]
#     sale_gst_rate = sale_row["GST Rate"]
#     sale_date = pd.to_datetime(sale_row.get("Date"))
#     district = sale_row.get("District", "nodistrict")
#     remaining = target
#     matched_items = []
    
#     # Track used products for this sale (changed to dict for usage counting)
#     used_products = {}
    
#     # Try to match products with variety and SAME GST rate
#     max_attempts = 100
#     attempts = 0
    
#     while remaining > MINIMUM_LINE_TOTAL and attempts < max_attempts:
#         product_list = get_available_products(subvertical, sale_gst_rate, products_df, sale_date, district, sale_idx, used_products)
        
#         if not product_list:
#             break
            
#         added = False
        
#         for prod in product_list:
#             if remaining <= MINIMUM_LINE_TOTAL:
#                 break
                
#             price = prod["Adjusted Price"]
#             uom = prod["UOM"].lower()
#             max_qty = prod["Consumer Range To"]
#             product_name = prod["Product Name"]

#             if price <= 0 or max_qty <= 0:
#                 continue

#             # Calculate quantity based on UOM
#             if uom in DECIMAL_UOM:
#                 max_possible_qty = min(remaining / price, max_qty)
#                 if max_possible_qty < 0.1:
#                     continue
#                 qty = round(random.uniform(0.1, max_possible_qty), 2)
#             else:
#                 max_possible_qty = min(int(remaining / price), int(max_qty))
#                 if max_possible_qty < 1:
#                     continue
#                 qty = random.randint(1, max_possible_qty)

#             line_total = round(price * qty, 2)
#             if line_total <= 0 or line_total > remaining:
#                 continue

#             matched_items.append({
#                 **sale_row.to_dict(),
#                 "Product Name": product_name,
#                 "HSN Code": prod["HSN Code"],
#                 "Category": prod["Category"],
#                 "Sub Category": prod["Sub Category"],
#                 "MRP": prod["MRP"],
#                 "UOM": prod["UOM"],
#                 "Adjusted Price": round(price, 2),
#                 "Qty": qty,
#                 "Line Total": line_total,
#                 "Applied GST": prod["gst_rate"],
#                 "Source": "Original"
#             })

#             remaining -= line_total
#             # Track usage count
#             used_products[product_name] = used_products.get(product_name, 0) + 1
#             added = True
#             break

#         if not added:
#             # Try with smaller quantities
#             for prod in product_list:
#                 price = prod["Adjusted Price"]
#                 uom = prod["UOM"].lower()
#                 product_name = prod["Product Name"]
                
#                 if price <= 0:
#                     continue
                
#                 if uom in DECIMAL_UOM:
#                     qty = 0.1
#                     if price * qty > remaining:
#                         continue
#                 else:
#                     qty = 1
#                     if price * qty > remaining:
#                         continue
                
#                 line_total = round(price * qty, 2)
#                 if line_total <= 0:
#                     continue

#                 matched_items.append({
#                     **sale_row.to_dict(),
#                     "Product Name": product_name,
#                     "HSN Code": prod["HSN Code"],
#                     "Category": prod["Category"],
#                     "Sub Category": prod["Sub Category"],
#                     "MRP": prod["MRP"],
#                     "UOM": prod["UOM"],
#                     "Adjusted Price": round(price, 2),
#                     "Qty": qty,
#                     "Line Total": line_total,
#                     "Applied GST": prod["gst_rate"],
#                     "Source": "Original"
#                 })

#                 remaining -= line_total
#                 used_products[product_name] = used_products.get(product_name, 0) + 1
#                 added = True
#                 break
            
#             if not added:
#                 break
        
#         attempts += 1

#     total_used = sum(i["Line Total"] for i in matched_items)
#     remaining_amount = round(target - total_used, 2)

#     return matched_items, remaining_amount

# # Get unique GST rates from sales and sort them
# unique_gst_rates = sorted(sales_df["GST Rate"].unique())
# print(f"\nProcessing GST rates in order: {unique_gst_rates}")

# # Verify that products have matching GST rates
# product_gst_rates = sorted(products_df["gst_rate"].unique())
# print(f"Available product GST rates: {product_gst_rates}")

# # Check for potential mismatches
# missing_gst_rates = set(unique_gst_rates) - set(product_gst_rates)
# if missing_gst_rates:
#     print(f"WARNING: Sales have GST rates {missing_gst_rates} but no products available for these rates!")

# # Process sales by GST rate groups
# for gst_rate in unique_gst_rates:
#     print(f"\n=== PROCESSING GST RATE: {gst_rate}% ===")
    
#     # Filter sales for current GST rate
#     current_gst_sales = sales_df[sales_df["GST Rate"] == gst_rate].copy()
#     print(f"Found {len(current_gst_sales)} sales with GST rate {gst_rate}%")
    
#     # Filter products for current GST rate
#     current_gst_products = products_df[products_df["gst_rate"] == gst_rate].copy()
#     print(f"Found {len(current_gst_products)} products with GST rate {gst_rate}%")
    
#     if current_gst_products.empty:
#         print(f"No products found for GST rate {gst_rate}% - adding all sales to unmatched")
#         for idx, sale_row in current_gst_sales.iterrows():
#             unmatched_sales.append({
#                 **sale_row.to_dict(), 
#                 "Remaining Amount": sale_row["Taxable_Amount"],
#                 "Reason": f"No products available for GST rate {gst_rate}%"
#             })
#         continue
    
#     # Process each sale in this GST rate group
#     for idx, sale_row in current_gst_sales.iterrows():
#         print(f"Processing sale row {idx+1} (GST: {gst_rate}%)")
#         matches, remaining_amt = match_products(sale_row, current_gst_products, idx)
        
#         if matches:
#             matched_rows.extend(matches)
#             print(f"  -> Matched {len(matches)} products, remaining: {remaining_amt}")
        
#         # If there's remaining amount > MINIMUM_LINE_TOTAL, try to match with FMCG products with SAME GST rate
#         if remaining_amt > MINIMUM_LINE_TOTAL:
#             print(f"  -> Trying to match remaining {remaining_amt} with FMCG products (GST: {gst_rate}%)")
#             fmcg_matches, final_remaining = match_remaining_with_fmcg(sale_row, remaining_amt, current_gst_products)
            
#             if fmcg_matches:
#                 fmcg_matched_rows.extend(fmcg_matches)
#                 print(f"  -> Matched {len(fmcg_matches)} FMCG products, remaining: {final_remaining}")
            
#             # Only add to unmatched if still has significant remaining
#             if final_remaining > MINIMUM_LINE_TOTAL:
#                 unmatched_sales.append({
#                     **sale_row.to_dict(), 
#                     "Remaining Amount": final_remaining,
#                     "Reason": f"Could not fully match with GST rate {gst_rate}% products"
#                 })

# # Combine all matched rows
# all_matched_rows = matched_rows + fmcg_matched_rows

# # Save unmatched sales if any
# if unmatched_sales:
#     unmatched_df = pd.DataFrame(unmatched_sales)
#     unmatched_path = r"c:\Users\ksand\Downloads\unmatched.xlsx"
#     unmatched_df.to_excel(unmatched_path, index=False)
#     print(f"\nUnmatched sales saved to {unmatched_path}")
# else:
#     print("\nNo unmatched sales found - all remaining amounts matched with correct GST rates!")

# # Create final dataframe
# matched_df = pd.DataFrame(all_matched_rows)

# if matched_df.empty:
#     print("No matches found!")
#     exit()

# # Verify GST rate consistency
# print(f"\n=== GST RATE VERIFICATION ===")
# gst_mismatch = matched_df[matched_df["GST Rate"] != matched_df["Applied GST"]]
# if not gst_mismatch.empty:
#     print(f"WARNING: Found {len(gst_mismatch)} rows with GST rate mismatch!")
#     print("This should not happen with the new logic.")
# else:
#     print("✓ All matched products have consistent GST rates with their sales!")

# # PRIORITY PRODUCT USAGE ANALYSIS
# print(f"\n=== PRIORITY PRODUCT USAGE ANALYSIS ===")
# if 'Product Name' in matched_df.columns:
#     product_usage = matched_df['Product Name'].value_counts()
#     priority_usage = {}
    
#     for product in existing_priority_products:
#         count = product_usage.get(product, 0)
#         if count > 0:
#             priority_usage[product] = count
    
#     print(f"Priority products used:")
#     for product, count in sorted(priority_usage.items(), key=lambda x: x[1], reverse=True):
#         print(f"  {product}: {count} times")
    
#     total_priority_usage = sum(priority_usage.values())
#     total_records = len(matched_df)
#     priority_percentage = (total_priority_usage / total_records) * 100 if total_records > 0 else 0
    
#     print(f"\nPriority products represent {priority_percentage:.1f}% of all product lines")
#     print(f"({total_priority_usage} out of {total_records} total records)")

# # Add row index for processing
# matched_df["row_index"] = matched_df.index

# # Combine small quantities (< 0.5)
# group_cols = ["Date", "Product Name", "District"]
# below_half = matched_df[matched_df["Qty"] < 0.5].copy()
# above_half = matched_df[matched_df["Qty"] >= 0.5].copy()

# print(f"\nFound {len(below_half)} rows with Qty < 0.5")

# def combine_values(series):
#     unique_vals = series.dropna().astype(str).unique()
#     return unique_vals[0] if len(unique_vals) == 1 else ", ".join(unique_vals)

# agg_dict = {
#     "Qty": "sum",
#     "Line Total": "sum"
# }
# for col in matched_df.columns:
#     if col in group_cols + ["Qty", "Line Total", "row_index"]:
#         continue
#     else:
#         agg_dict[col] = combine_values

# if not below_half.empty:
#     merged = below_half.groupby(group_cols, as_index=False).agg(agg_dict)
#     merged["row_index"] = below_half.groupby(group_cols)["row_index"].min().values
#     final_df = pd.concat([above_half, merged], ignore_index=True)
# else:
#     final_df = above_half.copy()

# final_df = final_df.sort_values("row_index").drop(columns=["row_index"]).reset_index(drop=True)

# # Calculate additional fields
# final_df["Line Total"] = pd.to_numeric(final_df["Line Total"], errors="coerce")
# final_df["Applied GST"] = pd.to_numeric(final_df["Applied GST"], errors="coerce")
# final_df["Applied GST"] = final_df["Applied GST"].fillna(0)
# final_df["MRP"] = pd.to_numeric(final_df["MRP"], errors="coerce")
# final_df["Adjusted Price"] = pd.to_numeric(final_df["Adjusted Price"], errors="coerce")

# # Calculate derived fields
# final_df["Disc_percent"] = (final_df["Adjusted Price"] * (1 + final_df["Applied GST"]/100)).round(2)
# final_df["Disc PU"] = ((final_df["MRP"] - final_df["Adjusted Price"]) / final_df["MRP"]).round(2)
# final_df["Currency"] = "INR"
# final_df["Facilitator"] = ""

# # Set facilitator based on vertical
# final_df.loc[final_df["Vertical"] == "Agri Business", "Facilitator"] = "Hesa Agritech Private Limited"
# final_df.loc[final_df["Vertical"] == "Commerce Business", "Facilitator"] = "Hesa Consumer Products Private Limited"

# # Calculate GST amounts - using the correct GST rate
# final_df["igst"] = 0.0
# final_df["cgst"] = (final_df["Line Total"] * final_df["Applied GST"] / 200).round(2)
# final_df["sgst"] = final_df["cgst"] 
# final_df["Total"] = (final_df["Line Total"] + final_df["cgst"] + final_df["sgst"] + final_df["igst"]).round(2)

# # Clean up columns
# final_df = final_df.drop(columns=["Taxable_Amount", "GST Rate", "Remaining Amount", "percentage_of_total", "normalized_percentage", "Reason"], errors="ignore")

# # Rename columns
# final_df = final_df.rename(columns={
#     "Applied GST": "gst_rate",
#     "Adjusted Price": "Net Price PU",
#     "Qty": "Product Qty",
#     "Line Total": "Taxable Value"
# })

# # Save output
# output_path = r"c:\Users\ksand\Downloads\may_2020_products.xlsx"
# final_df.to_excel(output_path, index=False)

# # Print summary
# print(f"\n=== PROCESSING SUMMARY ===")
# print(f"Original matches: {len(matched_rows)}")
# print(f"FMCG matches (from remaining): {len(fmcg_matched_rows)}")
# print(f"Total final records: {len(final_df)}")
# print(f"Unmatched sales: {len(unmatched_sales)}")
# print(f"Final output saved to {output_path}")

# # Show breakdown by source and GST rate
# if 'Source' in final_df.columns:
#     print(f"\nBreakdown by source:")
#     source_breakdown = final_df['Source'].value_counts()
#     for source, count in source_breakdown.items():
#         print(f"  {source}: {count} records")

# print(f"\nBreakdown by GST rate:")
# gst_breakdown = final_df['gst_rate'].value_counts().sort_index()
# for gst_rate, count in gst_breakdown.items():
#     print(f"  {gst_rate}%: {count} records")

# # Final verification
# print(f"\n=== FINAL GST VERIFICATION ===")
# original_gst_distribution = sales_df['GST Rate'].value_counts().sort_index()
# final_gst_distribution = final_df['gst_rate'].value_counts().sort_index()

# print("Original sales GST distribution:")
# for gst_rate, count in original_gst_distribution.items():
#     print(f"  {gst_rate}%: {count} sales")

# print("Final products GST distribution:")
# for gst_rate, count in final_gst_distribution.items():
#     print(f"  {gst_rate}%: {count} product lines")

# print("Done!")