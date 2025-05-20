import pandas as pd

# Load the file
df = pd.read_excel('/home/thrymr/Desktop/purchases(2024-25)/Hesa Agritech Private Limited/Agri Purchase Jun-24.xlsx')

# Define the district-to-state mapping
district_to_state = {
    'Sangareddy': 'Telangana',
    'Vijayawada': 'Andhra Pradesh',
    'Vikarabad': 'Telangana',
    'Wanaparthy': 'Telangana'
}

# Find rows where Vendor_State is empty (NaN or blank)
mask = df['Vendor_State'].isna() | (df['Vendor_State'].astype(str).str.strip() == '')

# Apply the mapping based on Vendor_District for empty Vendor_State
for district, state in district_to_state.items():
    condition = mask & (df['Vendor_District'] == district)
    df.loc[condition, 'Vendor_State'] = state

df.to_excel('/home/thrymr/Desktop/purchases(2024-25)/Hesa Agritech Private Limited/aAgri Purchase Jun-24.xlsx', index=False)
