import pandas as pd
from rapidfuzz import process, fuzz

# --- FILE PATHS ---
zoho_path = "/home/thrymr/Downloads/agri.xlsx"
products_path = "/home/thrymr/Important/my_products_file.xlsx"

# --- READ FILES ---
zoho = pd.read_excel(zoho_path, sheet_name='Sheet1')
products = pd.read_excel(products_path)

# Columns for matching
zoho_col = "Product Name"
prod_col_new = "Product Name"
prod_col_old = "OLD Product Name"

# Combined column for matching
products["combined_name"] = (
    products[prod_col_new].fillna("") + " || " + products[prod_col_old].fillna("")
)

choices = products["combined_name"].tolist()

# Fuzzy matching function
def get_best_match(name):
    if pd.isna(name):
        return None, 0, None
    match, score, idx = process.extractOne(name, choices, scorer=fuzz.WRatio)
    return match, score, idx

# Apply fuzzy match only for rows where category/subcategory is empty
needs_fill = zoho["Category"].isna() | zoho["Sub Category"].isna()

zoho.loc[needs_fill, "match_data"] = zoho.loc[needs_fill, zoho_col].apply(get_best_match)

# Extract match details
zoho["match_index"] = zoho["match_data"].apply(lambda x: x[2] if isinstance(x, tuple) else None)
zoho["Match_Score"] = zoho["match_data"].apply(lambda x: x[1] if isinstance(x, tuple) else None)

# Fill ONLY empty fields
zoho.loc[needs_fill, "Category"] = zoho.loc[needs_fill, "match_index"].apply(
    lambda i: products.loc[i, "Category"] if i is not None else None
)

zoho.loc[needs_fill, "Sub Category"] = zoho.loc[needs_fill, "match_index"].apply(
    lambda i: products.loc[i, "Sub Category"] if i is not None else None
)

# ------------ REMOVE EXTRA COLUMNS ------------
zoho = zoho.drop(columns=["match_data", "match_index", "Match_Score"], errors="ignore")

# Save the output file
output_path = "/home/thrymr/Downloads/agri_zoho_filled_categories.xlsx"
zoho.to_excel(output_path, index=False)

print("Done! File saved at:", output_path)
