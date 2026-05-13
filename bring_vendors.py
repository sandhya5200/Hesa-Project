import pandas as pd

# =========================
# 🔹 1. INPUT FILES
# =========================
input_files = [
    "/home/thrymr/Desktop/purchases 25-26(apr-sep)/purchase_april_(25-26)_with_state.xlsx",
    "/home/thrymr/Desktop/purchases 25-26(apr-sep)/purchase_may_(25-26)_with_state.xlsx",
    "/home/thrymr/Desktop/purchases 25-26(apr-sep)/june_purchase_(25-26)_with_state.xlsx",
    "/home/thrymr/Desktop/purchases 25-26(apr-sep)/july_purchase(25-26)_with_state.xlsx",
    "/home/thrymr/Desktop/purchases 25-26(apr-sep)/August_purchase(25-26)_with_state.xlsx",
    "/home/thrymr/Desktop/purchases 25-26(apr-sep)/september_purchase(25-26)_with_state.xlsx",
    "/home/thrymr/Desktop/purchases 25-26(oct-mar)/oct_purchase(25-26)_with_state.xlsx",
    "/home/thrymr/Desktop/purchases 25-26(oct-mar)/nov_purchase(25-26)_with_state.xlsx",
    "/home/thrymr/Desktop/purchases 25-26(oct-mar)/dec_purchase(25-26)_with_state.xlsx",
    "/home/thrymr/Desktop/purchases 25-26(oct-mar)/jan_purchase(25-26)_with_state.xlsx",
    "/home/thrymr/Desktop/purchases 25-26(oct-mar)/feb_purchase(25-26)_with_state.xlsx",
    "/home/thrymr/Desktop/purchases 25-26(oct-mar)/mar_purchase(25-26)_with_state.xlsx"
]

state_files = {
    "andhrapradesh": pd.read_excel("/home/thrymr/Desktop/new_vendor_databases/Vendor_databases_as_per_25-26/AP_Vendors.xlsx"),
    "maharashtra": pd.read_excel("/home/thrymr/Desktop/new_vendor_databases/Vendor_databases_as_per_25-26/Maharashtra_Vendors.xlsx"),
    "odisha": pd.read_excel("/home/thrymr/Desktop/new_vendor_databases/Vendor_databases_as_per_25-26/ODISSA_Vendors.xlsx"),
    "tamilnadu": pd.read_excel("/home/thrymr/Desktop/new_vendor_databases/Vendor_databases_as_per_25-26/tamilnadu_Vendors.xlsx"),
    "telangana": pd.read_excel("/home/thrymr/Desktop/new_vendor_databases/Vendor_databases_as_per_25-26/telangana_Vendors.xlsx"),
    "karnataka": pd.read_excel("/home/thrymr/Desktop/new_vendor_databases/Vendor_databases_as_per_25-26/Karnataka_vendors.xlsx"),
    # "haryana": pd.read_excel("/home/thrymr/Desktop/vendors/Haryana_Vendor_Database.xlsx"),
    # "bihar": pd.read_excel("/home/thrymr/Desktop/vendors/Bihar_Vendor_Database.xlsx"),
    "madhyapradesh": pd.read_excel("/home/thrymr/Desktop/new_vendor_databases/Vendor_databases_as_per_25-26/MP_Vendors.xlsx")
}



# =========================
# 🔹 3. LOAD VENDOR DATABASES
# =========================
state_dfs = {}

for state_key, df in state_files.items():
    df.columns = df.columns.str.strip()
    df['vendor_id_norm'] = df['Vendor ID'].astype(str).str.lower().str.replace(" ", "")
    state_dfs[state_key] = df

# =========================
# 🔹 4. GLOBAL UNMATCHED LIST
# =========================
all_unmatched = []

# =========================
# 🔹 5. PROCESS EACH FILE
# =========================
for file in input_files:
    print(f"Processing: {file}")

    df = pd.read_excel(file)

    df['vendor_id_norm'] = df['Vendor ID'].astype(str).str.lower().str.replace(" ", "")
    df['vendor_state_norm'] = df['State'].astype(str).str.lower().str.replace(" ", "")

    merged_rows = []

    for idx, row in df.iterrows():
        norm_state = row['vendor_state_norm']
        norm_id = row['vendor_id_norm']

        enriched_row = row.drop(['vendor_id_norm', 'vendor_state_norm']).to_dict()

        if norm_state in state_dfs:
            state_df = state_dfs[norm_state]
            match = state_df[state_df['vendor_id_norm'] == norm_id]

            if not match.empty:
                details_row = match.iloc[0]

                enriched_row.update({
                    'Mobile': details_row.get('Mobile'),
                    'Name': details_row.get('Name'),
                    'State_from_vendor': details_row.get('State'),
                    'Address': details_row.get('Address'),
                    'Pincode': details_row.get('Pincode'),
                })

                # preserve existing
                if 'District' not in enriched_row or pd.isna(enriched_row['District']):
                    enriched_row['District'] = details_row.get('District')

                if 'Sub Vertical' not in enriched_row or pd.isna(enriched_row['Sub Vertical']):
                    enriched_row['Sub Vertical'] = details_row.get('Sub Vertical')

            else:
                all_unmatched.append({
                    'Vendor ID': row.get('Vendor ID'),
                    'State': row.get('State'),
                    'District': row.get('District'),
                    'Sub Vertical': row.get('Sub Vertical'),
                    'Source File': file
                })

                enriched_row.setdefault('Mobile', None)
                enriched_row.setdefault('Name', None)
                enriched_row.setdefault('State_from_vendor', None)

        else:
            all_unmatched.append({
                'Vendor ID': row.get('Vendor ID'),
                'State': row.get('State'),
                'District': row.get('District'),
                'Sub Vertical': row.get('Sub Vertical'),
                'Source File': file
            })

        merged_rows.append(enriched_row)

    # =========================
    # 🔹 SAVE FILE-WISE MERGED OUTPUT
    # =========================
    file_name = file.split("/")[-1].replace(".xlsx", "")

    final_df = pd.DataFrame(merged_rows)
    final_df.to_excel(
        f"/home/thrymr/Downloads/{file_name}_with_vendor_data.xlsx",
        index=False
    )

    print(f"✅ Saved: {file_name}_with_vendor_data.xlsx")

# =========================
# 🔹 6. FINAL UNMATCHED FILE (DEDUPLICATED)
# =========================
unmatched_df = pd.DataFrame(all_unmatched)

# Remove duplicates based on Vendor ID
unmatched_df = unmatched_df.drop_duplicates(subset=['Vendor ID'])

unmatched_df.to_excel(
    "/home/thrymr/Downloads/all_unmatched_vendors.xlsx",
    index=False
)

print("⚠️ Combined unmatched vendors file saved!")