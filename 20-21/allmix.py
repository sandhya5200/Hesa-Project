# import pandas as pd
# import numpy as np

# # Constants
# start_date = "2021-03-01"
# end_date = "2021-03-31"
# districts = ["Adilabad", "Khammam", "Warangal", "Hyderabad", "Karim Nagar", "Nalgonda",
#              "Medak", "RangaReddy", "Mahabub Nagar", "Nizamabad", "Kurnool"]
# state = "Telangana"

# # Define state mapping for districts
# district_state_map = {
#     "Adilabad": "Telangana",
#     "Khammam": "Telangana", 
#     "Warangal": "Telangana",
#     "Hyderabad": "Telangana",
#     "Karim Nagar": "Telangana",
#     "Nalgonda": "Telangana",
#     "Medak": "Telangana",
#     "RangaReddy": "Telangana",
#     "Mahabub Nagar": "Telangana",
#     "Nizamabad": "Telangana",
#     "Kurnool": "Andhra Pradesh"
# }

# # Fill in your total money for each GST slab by state
# # Telangana: 12,50,20,499.39 = 125020499.39
# # Andhra Pradesh: 2740740.26
# gst_amounts = {
#     "Telangana": {
#         0: 125020499.39,
#         0.05: 0,
#         0.12: 0, 
#         0.18: 0
#     },
#     "Andhra Pradesh": {
#         0: 2740740.26,
#         0.05: 0,
#         0.12: 0,
#         0.18: 0
#     }
# }

# # --- Helper to create rows for a GST rate ---
# def allocate_amounts_by_state(gst_rate, state_amounts, agri_multiples=None, skip_market=False, skip_agri=False):
#     dates = pd.date_range(start_date, end_date)
#     selected_dates = np.random.choice(dates, size=int(len(dates) * 0.9), replace=False)
#     selected_dates = pd.to_datetime(sorted(selected_dates))

#     all_rows = []
    
#     # Process each state separately
#     for state_name, total_amount in state_amounts.items():
#         if total_amount == 0:
#             continue
            
#         # Get districts for this state
#         state_districts = [dist for dist, st in district_state_map.items() if st == state_name]
        
#         rows = []
#         for d in selected_dates:
#             for dist in state_districts:
#                 if not skip_market:
#                     rows.append([d, "Market Linkages Trading", "Agri Business", state_name, dist, gst_rate, 0])
#                 if not skip_agri:
#                     rows.append([d, "Agri Inputs", "Agri Business", state_name, dist, gst_rate, 0])
#                 rows.append([d, "FMCG", "Commerce Business", state_name, dist, gst_rate, 0])

#         df = pd.DataFrame(rows, columns=["Date", "Sub Vertical", "Vertical", "State", "District", "GST Rate", "Taxable_Amount"])
#         df.sort_values(by=["Date", "District", "Sub Vertical"], inplace=True, ignore_index=True)

#         # --- Allocation rules ---
#         if gst_rate in [0, 0.05]:
#             market_total = round(total_amount * 0.35, 2)
#             agri_total   = round(total_amount * 0.25, 2)
#             fmcg_total   = round(total_amount * 0.40, 2)
#         elif gst_rate == 0.12:
#             market_total = 0
#             agri_total   = round(total_amount * 0.20, 2)
#             fmcg_total   = round(total_amount - agri_total, 2)
#         elif gst_rate == 0.18:
#             market_total = 0
#             agri_total   = 0
#             fmcg_total   = total_amount

#         # Market
#         if not skip_market and market_total > 0:
#             market_indices = df[df["Sub Vertical"] == "Market Linkages Trading"].index
#             if len(market_indices) > 0:
#                 market_random = np.random.randint(1000, 5000, len(market_indices)).astype(float)
#                 market_random = market_random / market_random.sum() * market_total
#                 df.loc[market_indices, "Taxable_Amount"] = np.round(market_random, 2)

#         # Agri
#         if not skip_agri and agri_total > 0:
#             agri_indices = df[df["Sub Vertical"] == "Agri Inputs"].index
#             if len(agri_indices) > 0:
#                 if agri_multiples:  
#                     values = []
#                     remaining = agri_total
#                     while remaining >= min(agri_multiples):
#                         choice = np.random.choice(agri_multiples)
#                         if remaining - choice >= 0:
#                             values.append(choice)
#                             remaining -= choice
#                         else:
#                             break
#                     values = values[:len(agri_indices)]
#                     values = values + [0]*(len(agri_indices)-len(values))
#                     np.random.shuffle(values)
#                     df.loc[agri_indices, "Taxable_Amount"] = values
#                 else:
#                     agri_random = np.random.randint(500, 4000, len(agri_indices)).astype(float)
#                     agri_random = agri_random / agri_random.sum() * agri_total
#                     df.loc[agri_indices, "Taxable_Amount"] = np.round(agri_random, 2)

#         # FMCG
#         if fmcg_total > 0:
#             fmcg_indices = df[df["Sub Vertical"] == "FMCG"].index
#             if len(fmcg_indices) > 0:
#                 fmcg_random = np.random.randint(1000, 8000, len(fmcg_indices)).astype(float)
#                 fmcg_random = fmcg_random / fmcg_random.sum() * fmcg_total
#                 df.loc[fmcg_indices, "Taxable_Amount"] = np.round(fmcg_random, 2)

#         # Fix rounding drift
#         diff = round(total_amount - df["Taxable_Amount"].sum(), 2)
#         if diff != 0:
#             fmcg_indices = df[df["Sub Vertical"] == "FMCG"].index
#             if len(fmcg_indices) > 0:
#                 df.loc[fmcg_indices[0], "Taxable_Amount"] += diff

#         df["percentage_of_total"] = (df["Taxable_Amount"] / total_amount) * 100
#         all_rows.append(df)
    
#     # Combine all states
#     if all_rows:
#         return pd.concat(all_rows, ignore_index=True)
#     else:
#         return pd.DataFrame()


# # -----------------------------
# # Process slabs by state
# # -----------------------------
# all_dfs = []

# for gst_rate in [0, 0.05, 0.12, 0.18]:
#     # Create state amounts dict for current GST rate
#     state_amounts = {}
#     for state_name in ["Telangana", "Andhra Pradesh"]:
#         amount = gst_amounts[state_name].get(gst_rate, 0)
#         if amount > 0:
#             state_amounts[state_name] = amount
    
#     if state_amounts:
#         if gst_rate == 0:
#             all_dfs.append(allocate_amounts_by_state(gst_rate, state_amounts))
#         elif gst_rate == 0.05:
#             all_dfs.append(allocate_amounts_by_state(gst_rate, state_amounts))
#         elif gst_rate == 0.12:
#             all_dfs.append(allocate_amounts_by_state(gst_rate, state_amounts,
#                                            agri_multiples=[28676.08, 3424.2],
#                                            skip_market=True))
#         elif gst_rate == 0.18:
#             all_dfs.append(allocate_amounts_by_state(gst_rate, state_amounts,
#                                            skip_market=True, skip_agri=True))

# # Combine and clean
# if all_dfs:
#     final_df = pd.concat(all_dfs, ignore_index=True)
#     final_df = final_df[final_df["Taxable_Amount"] > 0].reset_index(drop=True)  # remove zero rows
# else:
#     final_df = pd.DataFrame()


# # Save Excel
# output_file = r"c:\Users\ksand\Downloads\mar_2021_taxable.xlsx"
# final_df.to_excel(output_file, index=False)

# print(f"Excel generated: {output_file}")
# print(f"Total rows: {len(final_df)}")
# print("\nTotals by GST Rate:")
# print(final_df.groupby("GST Rate")["Taxable_Amount"].sum())
# print("\nState Distribution:")
# print(final_df["State"].value_counts())



#----------------------------------------------------------------------------------------------------------------

# import pandas as pd
# import numpy as np
# import random

# # File paths
# sales_path = r"c:\Users\ksand\Downloads\mar_2021_taxable.xlsx"
# products_path = r"c:\Users\ksand\Downloads\myyy.xlsx"

# # Load data
# sales_df = pd.read_excel(sales_path)
# products_df = pd.read_excel(products_path)

# # Convert decimal GST rates to percentages in BOTH files
# # 0.05 -> 5, 0.12 -> 12, 0.18 -> 18, 0.00 -> 0
# print(f"Original GST rates in sales data: {sorted(sales_df['GST Rate'].unique())}")
# print(f"Original GST rates in products data: {sorted(products_df['gst_rate'].unique())}")

# # Handle the conversion more carefully for both zero and non-zero values
# sales_df["GST Rate"] = (sales_df["GST Rate"] * 100).round(0).astype(int)
# products_df["gst_rate"] = (products_df["gst_rate"] * 100).round(0).astype(int)

# print(f"\nConverted GST rates in sales data: {sorted(sales_df['GST Rate'].unique())}")
# print(f"Converted GST rates in products data: {sorted(products_df['gst_rate'].unique())}")

# # Check for zero GST rates specifically
# zero_gst_sales = len(sales_df[sales_df['GST Rate'] == 0])
# zero_gst_products = len(products_df[products_df['gst_rate'] == 0])
# print(f"\nZero GST entries - Sales: {zero_gst_sales}, Products: {zero_gst_products}")

# PRICE_ADJUSTMENT = 0.02
# DECIMAL_UOM = ["kg", "ltr", "gm"]
# MINIMUM_LINE_TOTAL = 1

# matched_rows = []
# unmatched_sales = []
# fmcg_matched_rows = []  # For FMCG matches from remaining amounts
# adjusted_price_cache = {}
# used_products_per_sale = {}

# def round_price(price):
#     rounded_010 = round(round(price * 10) / 10, 2)  # Nearest 0.10
#     rounded_10 = round(round(price / 10) * 10, 2)   # Nearest 10
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

# def get_available_products(subvertical, gst_rate, products_df, sale_date, district, sale_idx, used_products):
#     """Get products for subvertical and specific GST rate, excluding already used ones for variety"""
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
    
#     # Remove already used products for this sale to ensure variety
#     if used_products:
#         filtered = filtered[~filtered["Product Name"].isin(used_products)]
    
#     # If we've used all products, allow reuse but shuffle for variety
#     if filtered.empty:
#         filtered = products_df[
#             (products_df["Sub Vertical"] == subvertical) & 
#             (products_df["gst_rate"] == gst_rate)
#         ].copy()
#         filtered["Adjusted Price"] = filtered.apply(
#             lambda row: adjust_price(row["Net Price"], sale_date, district, row["Product Name"]), axis=1
#         )
    
#     # Shuffle products for variety instead of sorting by price
#     filtered = filtered.sample(frac=1).reset_index(drop=True)
    
#     return list(filtered.to_dict(orient="records"))

# def get_fmcg_products(gst_rate, products_df, sale_date, district, used_products=None):
#     """Get FMCG products for remaining amounts with matching GST rate"""
#     # Look for FMCG related subverticals - adjust these based on your data
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
    
#     # Remove already used products if specified
#     if used_products:
#         fmcg_products = fmcg_products[~fmcg_products["Product Name"].isin(used_products)]
    
#     # Shuffle for variety
#     fmcg_products = fmcg_products.sample(frac=1).reset_index(drop=True)
    
#     return list(fmcg_products.to_dict(orient="records"))

# def match_remaining_with_fmcg(sale_row, remaining_amount, products_df):
#     """Match remaining amount with FMCG products that have the same GST rate - STRICT GST MATCHING"""
#     sale_date = pd.to_datetime(sale_row.get("Date"))
#     district = sale_row.get("District", "nodistrict")
#     sale_gst_rate = sale_row.get("GST Rate", 0)  # Get the original GST rate from sale
#     remaining = remaining_amount
#     matched_items = []
#     used_products = set()
    
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
                
#             # Verify GST rate match (extra safety check)
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

#             # Create FMCG matched item - PRESERVE ORIGINAL SALE'S GST RATE
#             matched_items.append({
#                 **sale_row.to_dict(),
#                 "Product Name": product_name,
#                 "HSN Code": prod["HSN Code"],
#                 "Category": prod["Category"],
#                 "Sub Category": prod["Sub Category"],
#                 "Sub Vertical": prod["Sub Vertical"],  # This will be FMCG subvertical
#                 "Vertical": prod.get("Vertical", sale_row["Vertical"]),  # Use product's vertical or keep original
#                 "MRP": prod["MRP"],
#                 "UOM": prod["UOM"],
#                 "Adjusted Price": round(price, 2),
#                 "Qty": qty,
#                 "Line Total": line_total,
#                 "Applied GST": sale_gst_rate,  # KEEP ORIGINAL SALE'S GST RATE
#                 "Source": f"FMCG_Remaining_GST{sale_gst_rate}%"  # Tag to identify these records
#             })

#             remaining -= line_total
#             used_products.add(product_name)
#             added = True
#             break

#         if not added:
#             # Try with minimum quantities but still maintain GST rate consistency
#             for prod in fmcg_products:
#                 # Verify GST rate match (extra safety check)
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
#                     "Applied GST": sale_gst_rate,  # KEEP ORIGINAL SALE'S GST RATE
#                     "Source": f"FMCG_Remaining_GST{sale_gst_rate}%"
#                 })

#                 remaining -= line_total
#                 used_products.add(product_name)
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
#     sale_gst_rate = sale_row["GST Rate"]  # Get the GST rate from the sale
#     sale_date = pd.to_datetime(sale_row.get("Date"))
#     district = sale_row.get("District", "nodistrict")
#     remaining = target
#     matched_items = []
    
#     # Track used products for this sale
#     used_products = set()
    
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
#                 "Applied GST": prod["gst_rate"],  # This will always match the sale's GST rate
#                 "Source": "Original"  # Tag original matches
#             })

#             remaining -= line_total
#             used_products.add(product_name)
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
#                     "Applied GST": prod["gst_rate"],  # This will always match the sale's GST rate
#                     "Source": "Original"
#                 })

#                 remaining -= line_total
#                 used_products.add(product_name)
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
# output_path = r"c:\Users\ksand\Downloads\mar_2021_products.xlsx"
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





# #------------------------------------------------------------------------------------------------------------------

# import pandas as pd
# import numpy as np
# import unicodedata
# import random
# from collections import defaultdict

# # Clean function
# def clean(text):
#     if pd.isna(text):
#         return ''
#     text = str(text)
#     text = unicodedata.normalize("NFKD", text)
#     text = text.strip().lower()
#     text = text.replace('\u200b', '')
#     text = ' '.join(text.split())
#     return text

# print("Loading input files...")
# hesaathi_df = pd.read_excel(r"c:\Users\ksand\Downloads\Important 2\Important\new_hessathi_with_additional_people_details (copy).xlsx")

# print("Combining and shuffling sales data...")
# sales_df = pd.read_excel(r"c:\Users\ksand\Downloads\mar_2021_products.xlsx")
# sales_df = sales_df.sample(frac=1, random_state=42).reset_index(drop=True)
# print(f"Total sales rows: {len(sales_df)}")

# print("Cleaning state and district fields...")
# sales_df['state_clean'] = sales_df['State'].apply(clean)
# sales_df['district_clean'] = sales_df['District'].apply(clean)

# hesaathi_df['state_clean'] = hesaathi_df['State'].apply(clean)
# hesaathi_df['district_clean'] = hesaathi_df['District'].apply(clean)

# print("Filtering Hesaathi data by onboarding month...")
# selected_month = "Dec'22"
# month_order = [
#     "April'20", "May'20", "Jun'20", "Jul'20", "Aug'20", "Sep'20", "Oct'20", "Nov'20", "Dec'20",
#     "Jan'21", "Feb'21", "Mar'21", "April'21", "May'21", "Jun'21", "Jul'21", "Aug'21", "Sep'21", "Dec'21",
#     "Jan'22", "Feb'22", "Mar'22", "April'22", "May'22", "Jun'22", "Jul'22", "Aug'22", "Sep'22", "Oct'22", "Nov'22", "Dec'22",
#     "Jan'23", "Feb'23", "Mar'23", "April'23", "May'23", "Jun'23", "Jul'23", "Aug'23", "Sep'23", "Oct'23", "Nov'23", "Dec'23",
#     "Jan'24", "Feb'24", "Mar'24", "April'24", "May'24", "Jun'24", "Jul'24", "Aug'24", "Sep'24", "Oct'24", "Nov'24", "Dec'24",
#     "Jan'25", "Feb'25", "Mar'25", "April'25", "May'25", "Jun'25", "Jul'25", "Aug'25", "Sep'25", "Oct'25", "Nov'25", "Dec'25",
#     "Jan'26", "Feb'26", "Mar'26"
# ]
# valid_months = month_order[:month_order.index(selected_month) + 1]
# filtered_hesaathi_all = hesaathi_df[hesaathi_df['Onboarding Month'].isin(valid_months)].copy()

# # Step: Remove 8–10% per month prioritizing Non Performers
# print("Removing 8–10% of Hesaathis per month, prioritizing Non Performers...")
# used_hesaathi_list = []
# neglected_hesaathi_list = []

# for month in valid_months:
#     month_data = filtered_hesaathi_all[filtered_hesaathi_all['Onboarding Month'] == month]
#     total = len(month_data)
#     if total == 0:
#         continue
#     remove_pct = random.uniform(0.08, 0.10)
#     remove_count = int(total * remove_pct)

#     # Step 1: Try removing Non Performers
#     non_perf = month_data[month_data['Performance'].str.lower() == 'non performer']
#     remove_non_perf = non_perf.sample(min(len(non_perf), remove_count), random_state=42)
    
#     remaining_remove = remove_count - len(remove_non_perf)

#     # Step 2: Remove random from the rest if needed
#     rest = month_data.drop(remove_non_perf.index)
#     remove_extra = rest.sample(n=remaining_remove, random_state=42) if remaining_remove > 0 else pd.DataFrame()

#     # Combine neglected and used
#     neglected = pd.concat([remove_non_perf, remove_extra])
#     used = month_data.drop(neglected.index)

#     neglected_hesaathi_list.append(neglected)
#     used_hesaathi_list.append(used)

# filtered_hesaathi = pd.concat(used_hesaathi_list, ignore_index=True)
# neglected_hesaathis = pd.concat(neglected_hesaathi_list, ignore_index=True)

# print(f"Selected {len(filtered_hesaathi)} Hesaathis for assignment.")
# print(f"Neglected {len(neglected_hesaathis)} Hesaathis.")

# # Create mapping for AP districts to use random Telangana Hesaathis
# print("Creating AP-to-Telangana Hesaathi mapping...")

# # Get all Telangana districts from Hesaathi data
# telangana_districts = filtered_hesaathi[filtered_hesaathi['state_clean'] == 'telangana']['district_clean'].unique()
# print(f"Available Telangana districts in Hesaathi data: {list(telangana_districts)}")

# # Select 5 random Telangana districts for AP mapping
# random.seed(42)  # For reproducible results
# selected_telangana_districts = random.sample(list(telangana_districts), min(5, len(telangana_districts)))
# print(f"Selected Telangana districts for AP mapping: {selected_telangana_districts}")

# # Create AP sales entries with Telangana district mappings
# ap_sales = sales_df[sales_df['state_clean'] == 'andhra pradesh'].copy()
# if not ap_sales.empty:
#     print(f"Found {len(ap_sales)} AP sales records to remap")
    
#     # For each AP sale, randomly assign one of the selected Telangana districts
#     ap_sales['original_district'] = ap_sales['district_clean']  # Backup original
#     ap_sales['district_clean'] = np.random.choice(selected_telangana_districts, size=len(ap_sales))
#     ap_sales['state_clean'] = 'telangana'  # Change state to telangana for mapping
    
#     # Update the main sales dataframe
#     sales_df.loc[ap_sales.index, 'district_clean'] = ap_sales['district_clean']
#     sales_df.loc[ap_sales.index, 'state_clean'] = ap_sales['state_clean']
    
#     print(f"Remapped AP sales to use Telangana districts for Hesaathi assignment")

# print("Creating merge keys and mapping datasets...")
# sales_df['merge_key'] = sales_df['state_clean'] + '_' + sales_df['district_clean']
# filtered_hesaathi['merge_key'] = filtered_hesaathi['state_clean'] + '_' + filtered_hesaathi['district_clean']

# print("Creating mapping of merge_key to Hesaathi Codes...")
# hesaathi_map = (
#     filtered_hesaathi
#     .groupby('merge_key')['Hesaathi Code']
#     .apply(list)
#     .to_dict()
# )

# # Check for missing keys
# missing_keys = set(sales_df['merge_key']) - set(hesaathi_map.keys())
# if missing_keys:
#     print("The following merge_keys were not matched to Hesaathis:")
#     for key in sorted(missing_keys):
#         print(f"  -> {key}")
#     raise ValueError("Fix state/district mismatches! Some keys not found in Hesaathi data.")

# print("Starting Vertical-wise assignment with taxable value constraints...")

# # Constants for taxable value range (3-3.5 lakhs)
# MIN_TAXABLE_VALUE = 300000  # 3 lakhs
# MAX_TAXABLE_VALUE = 350000  # 3.5 lakhs

# # Sort sales data by Date for consistent processing
# sales_df['Date'] = pd.to_datetime(sales_df['Date'])
# sales_df = sales_df.sort_values(by='Date').reset_index(drop=True)

# # Initialize tracking dictionaries
# # Structure: {(merge_key, hesaathi_code, vertical): current_taxable_value}
# hesaathi_vertical_allocation = defaultdict(float)

# # Create hesaathi onboarding month mapping
# hesaathi_month_map = filtered_hesaathi.set_index('Hesaathi Code')['Onboarding Month'].to_dict()

# # Lists to store assignments
# assigned_codes = []
# assigned_months = []

# print("Processing each transaction for optimal assignment...")

# for idx, row in sales_df.iterrows():
#     merge_key = row['merge_key']
#     vertical = row['Vertical']
#     taxable_value = float(row['Taxable Value'])
    
#     available_hesaathis = hesaathi_map.get(merge_key, [])
    
#     assigned = False
#     best_hesaathi = None
    
#     # Try to find a hesaathi that can accommodate this transaction
#     for hesaathi_code in available_hesaathis:
#         key = (merge_key, hesaathi_code, vertical)
#         current_allocation = hesaathi_vertical_allocation[key]
        
#         # Check if this hesaathi can accommodate the transaction
#         if current_allocation + taxable_value <= MAX_TAXABLE_VALUE:
#             # If current allocation is 0 or adding this keeps us within range
#             if current_allocation == 0 or current_allocation + taxable_value >= MIN_TAXABLE_VALUE:
#                 best_hesaathi = hesaathi_code
#                 break
#             # If adding this transaction would put us in the valid range
#             elif current_allocation < MIN_TAXABLE_VALUE and current_allocation + taxable_value >= MIN_TAXABLE_VALUE:
#                 best_hesaathi = hesaathi_code
#                 break
    
#     # If no hesaathi found, try to find one with minimum current allocation
#     if best_hesaathi is None:
#         min_allocation = float('inf')
#         for hesaathi_code in available_hesaathis:
#             key = (merge_key, hesaathi_code, vertical)
#             current_allocation = hesaathi_vertical_allocation[key]
#             if current_allocation < min_allocation and current_allocation + taxable_value <= MAX_TAXABLE_VALUE:
#                 min_allocation = current_allocation
#                 best_hesaathi = hesaathi_code
    
#     # Assign to best hesaathi if found
#     if best_hesaathi is not None:
#         key = (merge_key, best_hesaathi, vertical)
#         hesaathi_vertical_allocation[key] += taxable_value
#         assigned_codes.append(best_hesaathi)
#         assigned_months.append(hesaathi_month_map[best_hesaathi])
#         assigned = True
    
#     # If still not assigned, use HS-CO
#     if not assigned:
#         assigned_codes.append('HS-CO')
#         assigned_months.append('')  # Empty onboarding month for HS-CO
        
#         # Log overflow case
#         if idx % 1000 == 0:  # Log every 1000th overflow to avoid spam
#             print(f"Overflow at row {idx}: {taxable_value} assigned to HS-CO in {merge_key}, {vertical}")

# # Assign the results
# sales_df['Assigned Hesaathi Code'] = assigned_codes
# sales_df['Assigned Hesaathi Onboarding Month'] = assigned_months

# # Clean up temporary columns
# sales_df.drop(columns=['state_clean', 'district_clean', 'merge_key'], inplace=True, errors='ignore')

# print("Assignment Summary:")
# regular_assignments = sum(1 for code in assigned_codes if code != 'HS-CO')
# overflow_assignments = sum(1 for code in assigned_codes if code == 'HS-CO')
# print(f"Regular assignments: {regular_assignments}")
# print(f"HS-CO assignments: {overflow_assignments}")

# # Print allocation summary per hesaathi-vertical combination
# print("\nHesaathi-Vertical Allocation Summary:")
# allocation_summary = defaultdict(lambda: defaultdict(float))
# for (merge_key, hesaathi_code, vertical), total_value in hesaathi_vertical_allocation.items():
#     if total_value > 0:
#         allocation_summary[hesaathi_code][vertical] = total_value

# # Save full file (no splitting into halves)
# print("\nSaving final sales file...")
# sales_df.to_excel(r"c:\Users\ksand\Downloads\mar_after_hesaathis.xlsx", index=False)

# print("Processing complete! File saved successfully.")




# # #--------------------------------------------------------------------------------------------------------------------


# import pandas as pd
# import numpy as np
# from random import randint, sample

# print("📥 Reading input Excel files...")

# print("🔗 Concatenating and sorting data...")

# # Combine and sort
# df = pd.read_excel(r"c:\Users\ksand\Downloads\mar_after_hesaathis.xlsx")
# df['Date'] = pd.to_datetime(df['Date'])  # Ensure datetime format
# df.sort_values(by='Date', inplace=True)

# # Step 2: Generate Customer IDs
# def generate_customer_ids(df):
#     print("🧾 Generating Customer IDs...")
#     df["Customer ID"] = None

#     for (date, hesaathi), group in df.groupby(["Date", "Assigned Hesaathi Code"]):
#         count = len(group)
#         base = f"CS-{hesaathi}-"
        
#         if count <= 5:
#             cid = base + f"{randint(1, 50):04d}"
#             df.loc[group.index, "Customer ID"] = cid

#         elif 6 <= count <= 10:
#             cids = sample(range(1, 51), 2)
#             cid1 = base + f"{cids[0]:04d}"
#             cid2 = base + f"{cids[1]:04d}"
#             mid = count // 2
#             df.loc[group.index[:mid], "Customer ID"] = cid1
#             df.loc[group.index[mid:], "Customer ID"] = cid2

#         else:  # count > 10
#             cids = sample(range(1, 51), 3)
#             cid1 = base + f"{cids[0]:04d}"
#             cid2 = base + f"{cids[1]:04d}"
#             cid3 = base + f"{cids[2]:04d}"
#             third = count // 3
#             df.loc[group.index[:third], "Customer ID"] = cid1
#             df.loc[group.index[third:2*third], "Customer ID"] = cid2
#             df.loc[group.index[2*third:], "Customer ID"] = cid3

#     return df

# def generate_invoice_numbers(df):
#     """
#     Generate Invoice No (AG & CG separate sequences) and Order ID (continuous integer).
#     Month & Year are taken from the Date column.
#     """
#     print("🧾 Generating Invoice Numbers and Order IDs...")
#     df["Invoice No"] = None
#     df["Order ID"] = None
    
#     # Continuous counter for Order IDs
#     order_counter = 1  
    
#     # Separate counters for AG & CG
#     ag_counter = 1
#     cg_counter = 1
    
#     for (date, cid, vertical), group in df.groupby(["Date", "Customer ID", "Vertical"]):
        
#         # Extract month/year from the first row's Date
#         month_str = f"{date.month:02d}"
#         year_str = str(date.year)[-2:]  # Last 2 digits
        
#         # --- Invoice No (AG / CG) ---
#         if "Commerce Business" in vertical:
#             prefix = "CG"
#             invoice_id = f"2020-21/RY/{month_str}/{cg_counter:04d}"
#             cg_counter += 1
#         else:
#             prefix = "AG"
#             invoice_id = f"2020-21/RY/{month_str}/{cg_counter:04d}"
#             ag_counter += 1
        
#         # --- Order ID (integer) ---
#         order_id = order_counter  
        
#         # Assign values
#         df.loc[group.index, "Invoice No"] = invoice_id
#         df.loc[group.index, "Order ID"] = order_id
        
#         order_counter += 1
    
#     return df


# # Apply functions
# df = generate_customer_ids(df)
# df = generate_invoice_numbers(df)    


# # Save as one file (no split)
# print("💾 Saving output file...")
# df.to_excel(r"c:\Users\ksand\Downloads\mar_2020_sales.xlsx", index=False)

# print("✅ Processing complete. File saved successfully.")





# #------------------------------------------------------------------------------------------------------


import pandas as pd
import os
import math

# Load and merge all customer databases
customer_files = [
    r"c:\Users\ksand\Downloads\sorted_customers_part_1.xlsx",
    r"c:\Users\ksand\Downloads\sorted_customers_part_2.xlsx",
    # "/home/thrymr/Desktop/Customer_data/Customer_database_part2b.xlsx",
    # "/home/thrymr/Desktop/Customer_data/Customer_database_part2c.xlsx",
    # "/home/thrymr/Desktop/Customer_data/additional_database1.xlsx",
    # "/home/thrymr/Desktop/Customer_data/additional_database_2.xlsx"
]
customer_data = pd.concat([pd.read_excel(file) for file in customer_files])

# Create lookup dictionaries
customer_dict = dict(zip(customer_data['CustomerID'], customer_data['Name']))
address_dict = dict(zip(customer_data['CustomerID'], customer_data['Address']))
mobile_dict = dict(zip(customer_data['CustomerID'], customer_data['Mobile']))
mandal_dict = dict(zip(customer_data['CustomerID'], customer_data['Mandal']))
pincode_dict = dict(zip(customer_data['CustomerID'], customer_data['Pincode']))

# Sales files list
sales_files = [

    r"c:\Users\ksand\Downloads\mar_2020_sales.xlsx"
    
]

# MCP calculation function
def calculate_mcp(row):
    rate = row['Rate']
    facilitator = row['Facilitator']
    mrp = row['MRP']
    
    if facilitator == "Hesa Agritech Private Limited":
        mcp = rate + (rate * 1.5 / 100)
    elif facilitator == "Hesa Consumer Products Private Limited":
        mcp = rate + (rate * 2.5 / 100)
    else:
        mcp = rate

    return min(mcp, mrp)

# Excel limit
MAX_ROWS = 1048575

# Process each sales file
for file_path in sales_files:
    print(f"Processing: {file_path}")
    
    # Read all sheets
    all_sheets = pd.read_excel(file_path, sheet_name=None)
    df_sales = pd.concat(all_sheets.values(), ignore_index=True)
    
    # Add customer details
    df_sales['Customer Name'] = df_sales['Customer ID'].map(customer_dict)
    df_sales['Customer Address'] = df_sales['Customer ID'].map(address_dict)
    df_sales['Customer Mobile'] = df_sales['Customer ID'].map(mobile_dict)
    df_sales['Customer Mandal'] = df_sales['Customer ID'].map(mandal_dict)
    df_sales['Pincode'] = df_sales['Customer ID'].map(pincode_dict)

    # Rename columns for consistency
    df_sales.rename(columns={
        'Hesaathi Code': 'Hesaathi Code',
        'Customer ID': 'CustomerID',
        'Customer State': 'Customer State',
        'Customer District': 'CustomerDistrict',
        'Product Name': 'Product Name',
        'HSN Code': 'HSN/SAC',
        'Product Qty': 'Quantity',
        'UOM': 'UOM',
        'Net Price PU': 'Rate',
        'Taxable Value': 'Taxable Value',
        'GST Rate': 'GST Rate',
        'Total Value': 'Sub total',
        'General': 'Invoice No',
    }, inplace=True)

    # Calculate MCP
    df_sales['MCP'] = df_sales.apply(calculate_mcp, axis=1)
    
    # Split into multiple parts if needed
    total_rows = len(df_sales)
    base_filename = os.path.splitext(os.path.basename(file_path))[0].replace(" ", "_")
    num_parts = math.ceil(total_rows / MAX_ROWS)

    for i in range(num_parts):
        start = i * MAX_ROWS
        end = min((i + 1) * MAX_ROWS, total_rows)
        part = df_sales.iloc[start:end].copy()
        output_file = r"c:\Users\ksand\Downloads\mar_sales_with_customers.xlsx"
        part.to_excel(output_file, index=False)
        print(f"✅ Saved: {output_file} ({len(part)} rows)")
