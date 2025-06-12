import pandas as pd
import random

# Load address and pincode data
address_df = pd.read_excel("/home/thrymr/Downloads/madhya_pradesh_address.xlsx")      # your address data
pincode_df = pd.read_excel("/home/thrymr/Downloads/mp_pincode.xlsx")      # your pincode reference data
output_df = address_df.copy()

# Normalize state names
address_df['State'] = address_df['State'].replace({
    'MadhyaPradesh': 'Madhya Pradesh'
})


district_override = {
    'kukshi': 'dhar',                       ##########change kukshi not available thefore bringing from dhar###########
   
}

# Generate lowercase matching keys
address_df['state_key'] = address_df['State'].str.strip().str.lower()

# Apply district override before matching
address_df['district_key'] = address_df['District'].str.strip().str.lower()
address_df['district_key'] = address_df['district_key'].apply(
    lambda d: district_override.get(d, d)  # override if present
)

pincode_df['state_key'] = pincode_df['State'].str.strip().str.lower()
pincode_df['district_key'] = pincode_df['District'].str.strip().str.lower()

# Build pincode map
pincode_map = (
    pincode_df.groupby(['state_key', 'district_key'])['Pincode']
    .apply(list)
    .to_dict()
)

# Assign random pincode
output_df['Pincode'] = address_df.apply(
    lambda row: random.choice(pincode_map.get((row['state_key'], row['district_key']), [None])),
    axis=1
)

# Save result
output_df.to_excel("/home/thrymr/Downloads/output_with_pincodes.xlsx", index=False)
