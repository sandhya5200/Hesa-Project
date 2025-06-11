import pandas as pd

# 1. Load LibreOffice .ods file
df = pd.read_excel("/home/thrymr/Downloads/Oct Sales Pivot Updated.xlsx")  # Replace with your actual file path

# 2. Convert 'Date' column (replace 'Date' with your actual column name)
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)

# 3. Reformat to MM/DD/YYYY
df['Date'] = df['Date'].dt.strftime('%m/%d/%Y')

# 4. Save back if needed (as Excel or CSV)
df.to_excel("/home/thrymr/Downloads/Oct_qty.xlsx", index=False)  # Optional
