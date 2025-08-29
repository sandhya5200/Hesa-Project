import pandas as pd

# ✅ List of Excel files
excel_files = [
    "/home/thrymr/Downloads/jan_with_vendors.xlsx", 
    "/home/thrymr/Downloads/feb_with_vendors.xlsx",
    "/home/thrymr/Downloads/mar_with_vendors.xlsx", 
]

for file in excel_files:
    print(f"\n📂 Processing file: {file}")
    
    # Load Excel file
    df = pd.read_excel(file)

    if "District" not in df.columns:
        print("⚠️ Skipped (No 'District' column found)")
        continue

    # Count matches ignoring case & spaces
    mask = df["District"].astype(str).str.lower().str.strip() == "hydarabad"
    before_count = mask.sum()

    if before_count > 0:
        # Replace only matching rows
        df.loc[mask, "District"] = "Hyderabad"
        
        # Save back
        df.to_excel(file, index=False)

        print(f"✅ Replaced {before_count} occurrence(s) of 'Hydarabad' → 'Hyderabad'")
    else:
        print("ℹ️ No 'Hydarabad' found in this file.")
