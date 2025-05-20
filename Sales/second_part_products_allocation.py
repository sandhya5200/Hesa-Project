import pandas as pd
import numpy as np
import random

# File paths
sales_path = "/home/thrymr/Downloads/cons_april_input.xlsx"
products_path = "/home/thrymr/Downloads/my_products_file.xlsx"
output_matched = "/home/thrymr/Downloads/Cons_April_25_output_to_check.xlsx"
output_unmatched = "/home/thrymr/Downloads/unmatched_sales.xlsx"

# Load data
sales_df = pd.read_excel(sales_path)
products_df = pd.read_excel(products_path)

PRICE_ADJUSTMENT = 0.02
DECIMAL_UOM = ["kg", "ltr", "gm"]
MINIMUM_LINE_TOTAL = 1

matched_rows = []
unmatched_sales = []
product_pools = {}
adjusted_price_cache = {}  # To cache price per (date, district, product)

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

def get_product_pool(date, district, subvertical, gst_rate, products_df, high_value):
    key = (date, district, subvertical, gst_rate)
    if key not in product_pools or not product_pools[key]:
        filtered = products_df[
            (products_df["Sub Vertical"] == subvertical) &
            (products_df["gst_rate"] == gst_rate)
        ].copy()

        if filtered.empty:
            return []

        filtered["Adjusted Price"] = filtered.apply(
            lambda row: adjust_price(row["Net Price"], date, district, row["Product Name"]), axis=1
        )

        filtered.sort_values("Adjusted Price", ascending=not high_value, inplace=True)
        filtered = filtered.sample(frac=1).reset_index(drop=True)
        product_pools[key] = list(filtered.to_dict(orient="records"))

    return product_pools[key]

def match_products(sale_row, products_df):
    target = sale_row["Taxable_Amount"]
    subvertical = sale_row["Sub Vertical"]
    original_gst = sale_row["GST Rate"]
    sale_date = pd.to_datetime(sale_row.get("Date"))
    district = sale_row.get("District", "nodistrict")
    remaining = target
    matched_items = []

    high_value = target >= 1_00_000

    while remaining > MINIMUM_LINE_TOTAL:
        product_list = get_product_pool(sale_date, district, subvertical, original_gst, products_df, high_value)
        added = False
        while product_list:
            prod = product_list.pop(0)
            price = prod["Adjusted Price"]
            uom = prod["UOM"].lower()
            max_qty = prod["Consumer Range To"]

            if price <= 0 or max_qty <= 0:
                continue

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
                "Product Name": prod["Product Name"],
                "HSN Code": prod["HSN Code"],
                "Category": prod["Category"],
                "Sub Category": prod["Sub Category"],
                "UOM": prod["UOM"],
                "Adjusted Price": round(price, 2),
                "Qty": qty,
                "Line Total": line_total,
                "Applied GST": prod["gst_rate"]
            })

            remaining -= line_total
            added = True
            break

        if not added:
            break

    if remaining > 0.5:
        fallback_decimal = products_df[
            (products_df["Sub Vertical"] == subvertical) &
            (products_df["UOM"].str.lower().isin(DECIMAL_UOM))
        ].copy()

        if not fallback_decimal.empty:
            fallback_decimal["Adjusted Price"] = fallback_decimal.apply(
                lambda row: adjust_price(row["Net Price"], sale_date, district, row["Product Name"]), axis=1
            )
            fallback_decimal.sort_values("Adjusted Price", inplace=True)

            for _, prod in fallback_decimal.iterrows():
                price = prod["Adjusted Price"]
                max_qty = prod["Consumer Range To"]
                if price <= 0 or max_qty <= 0:
                    continue

                qty = round(min(max_qty, remaining / price), 2)
                if qty < 0.1:
                    continue

                line_total = round(price * qty, 2)
                if line_total <= 0 or line_total > remaining + 0.2:
                    continue

                matched_items.append({
                    **sale_row.to_dict(),
                    "Product Name": prod["Product Name"],
                    "HSN Code": prod["HSN Code"],
                    "Category": prod["Category"],
                    "Sub Category": prod["Sub Category"],
                    "UOM": prod["UOM"],
                    "Adjusted Price": round(price, 2),
                    "Qty": qty,
                    "Line Total": line_total,
                    "Applied GST": prod["gst_rate"]
                })

                remaining -= line_total
                if remaining <= 0.5:
                    break

            attempts = 0
            while remaining > 0.5 and attempts < 20:
                prod = fallback_decimal.sample(1).iloc[0]
                price = prod["Adjusted Price"]
                max_qty = prod["Consumer Range To"]
                if price <= 0 or max_qty <= 0:
                    attempts += 1
                    continue

                qty = round(min(max_qty, remaining / price), 2)
                if qty < 0.1:
                    attempts += 1
                    continue

                line_total = round(price * qty, 2)
                if line_total <= 0 or line_total > remaining + 0.2:
                    attempts += 1
                    continue

                matched_items.append({
                    **sale_row.to_dict(),
                    "Product Name": prod["Product Name"],
                    "HSN Code": prod["HSN Code"],
                    "Category": prod["Category"],
                    "Sub Category": prod["Sub Category"],
                    "UOM": prod["UOM"],
                    "Adjusted Price": round(price, 2),
                    "Qty": qty,
                    "Line Total": line_total,
                    "Applied GST": prod["gst_rate"]
                })

                remaining -= line_total
                attempts += 1

    # Final fallback: Repeat products from same sub-vertical with any GST rate
    if remaining > 0.5:
        fallback_any_gst = products_df[
            (products_df["Sub Vertical"] == subvertical)
        ].copy()

        if not fallback_any_gst.empty:
            fallback_any_gst["Adjusted Price"] = fallback_any_gst.apply(
                lambda row: adjust_price(row["Net Price"], sale_date, district, row["Product Name"]), axis=1
            )
            fallback_any_gst.sort_values("Adjusted Price", inplace=True)

            # Continue until remaining is small enough
            attempts = 0
            max_attempts = 1000  # prevent infinite loop

            while attempts < max_attempts:
                reduced = False
                for _, prod in fallback_any_gst.iterrows():
                    price = prod["Adjusted Price"]
                    uom = prod["UOM"].lower()
                    max_qty = prod["Consumer Range To"]

                    if price <= 0 or max_qty <= 0:
                        continue

                    if uom in DECIMAL_UOM:
                        max_possible_qty = round(min(max_qty, remaining / price), 2)
                        if max_possible_qty < 0.1:
                            continue
                        qty = round(random.uniform(0.1, max_possible_qty), 2)
                    else:
                        max_possible_qty = min(max_qty, int(remaining / price))
                        if max_possible_qty < 1:
                            continue
                        qty = random.randint(1, max_possible_qty)

                    line_total = round(price * qty, 2)
                    if line_total <= 0 or line_total > remaining:
                        continue

                    matched_items.append({
                        **sale_row.to_dict(),
                        "Product Name": prod["Product Name"],
                        "HSN Code": prod["HSN Code"],
                        "Category": prod["Category"],
                        "Sub Category": prod["Sub Category"],
                        "UOM": prod["UOM"],
                        "Adjusted Price": round(price, 2),
                        "Qty": qty,
                        "Line Total": line_total,
                        "Applied GST": prod["gst_rate"]
                    })

                    remaining -= line_total
                    reduced = True
                    break  # try next iteration with updated remaining

                if not reduced:
                    # Can't reduce any further with available products
                    break
                attempts += 1

    total_used = sum(i["Line Total"] for i in matched_items)
    remaining_amount = round(target - total_used, 2)

    if matched_items:
        for item in matched_items:
            item["Remaining Amount"] = None
        matched_items[-1]["Remaining Amount"] = remaining_amount

    return matched_items, remaining_amount

# Run the matching
for idx, sale_row in sales_df.iterrows():
    print(f"\U0001f6d2 Processing sale row {idx+1}/{len(sales_df)}")
    matches, remaining_amt = match_products(sale_row, products_df)
    if matches:
        matched_rows.extend(matches)
    if remaining_amt > MINIMUM_LINE_TOTAL:
        unmatched_sales.append({**sale_row.to_dict(), "Remaining Amount": remaining_amt})

# Save matched rows
matched_df = pd.DataFrame(matched_rows)
matched_df.to_excel(output_matched, index=False)

# Save unmatched/underused rows
unmatched_df = pd.DataFrame(unmatched_sales)
unmatched_df.to_excel(output_unmatched, index=False)

print("\n✅ Matching complete.")
print(f"✔️ Matched products file: {output_matched}")
print(f"❗ Unmatched/remaining sales rows file: {output_unmatched}")



