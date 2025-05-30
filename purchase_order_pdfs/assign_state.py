import pandas as pd

# Step 1: Define the state-district mapping
state_district_map = {
    "Andhra Pradesh": [
        "ananthapur", "chittoor", "cuddapah", "east godavari", "guntur", "krishna",
        "kurnool", "nellore", "prakasam", "srikakulam", "vijayawada", "visakhapatnam",
        "vizianagaram", "west godavari"
    ],
    "Karnataka": ["bidar"],
    "Maharashtra": [
        "ahmed nagar", "amravati", "aurangabad", "beed", "buldhana", "chandrapur",
        "dhule", "gadchiroli", "jalgaon", "kolhapur", "latur", "mumbai", "nagpur",
        "nanded", "osmanabad", "pune", "raigarh mh", "raigarh(mh)", "satara",
        "solapur", "thane", "yavatmal"
    ],
    "Odisha": [
        "angul", "balangir", "balasore", "baleswar", "bargarh", "bhadrak", "boudh",
        "cuttack", "debagarh", "dhenkanal", "gajapati", "ganjam", "jagatsinghapur",
        "jajapur", "kalahandi", "kendrapara", "kendujhar", "khorda", "mayurbhanj",
        "nayagarh", "puri", "rayagada", "sonapur", "sundergarh"
    ],
    "Tamil Nadu": [
        "chennai", "coimbatore", "cuddalore", "dharmapuri", "erode", "kanchipuram",
        "kanyakumari", "karur", "krishnagiri", "madurai", "namakkal", "nilgiris",
        "ramanathapuram", "salem", "tiruchirappalli", "tirunelveli", "tiruppur",
        "tiruvannamalai", "vellore"
    ],
    "Telangana": [
        "adilabad", "hyderabad", "karim nagar", "khammam", "mahabub nagar", "medak",
        "nalgonda", "nizamabad", "rangareddy", "sangareddy", "vikarabad",
        "wanaparthy", "warangal"
    ]
}

# Step 2: Create district to state mapping
district_to_state = {}
for state, districts in state_district_map.items():
    for district in districts:
        district_to_state[district.strip().lower()] = state

# Step 3: Load input Excel
input_file = "/home/thrymr/Desktop/purchases(2024-25)/Hesa Consumer Products Private Limited/purchases May-24.xlsx"     # Replace with your actual file name
output_file = "/home/thrymr/Desktop/purchases(2024-25)/Hesa Consumer Products Private Limited/May-24.xlsx"

df = pd.read_excel(input_file)

# Step 4: Map State
df["State"] = df["District"].str.strip().str.lower().map(district_to_state)

# Step 5: Save to output Excel
df.to_excel(output_file, index=False)

print(f"✅ Output written to {output_file}")
