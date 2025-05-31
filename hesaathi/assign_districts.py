import pandas as pd
import random

# Read your Excel input
df = pd.read_excel("/home/thrymr/Downloads/performance_assigned_output.xlsx")  # Replace with your file


# State and District map
state_district_map = {
    "Andhra Pradesh": ["Ananthapur", "Chittoor", "Cuddapah", "East Godavari", "Guntur", "Krishna", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Vijayawada", "Visakhapatnam", "Vizianagaram", "West Godavari"],
    "Karnataka": ["Bidar", "Vijayanagara", "Ballari", "Raichur", "Koppal", "Yadagiri", "Kalabuargi"],
    "Maharashtra": ["Ahmed Nagar", "Amravati", "Aurangabad", "Beed", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli", "Jalgaon", "Kolhapur", "Latur", "Mumbai", "Nagpur", "Nanded", "Osmanabad", "Pune", "Raigarh Mh", "Raigarh(Mh)", "Satara", "Solapur", "Thane", "Yavatmal"],
    "Odisha": ["Angul", "Balangir", "Balasore", "Baleswar", "Bargarh", "Bhadrak", "Boudh", "Cuttack", "Debagarh", "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghapur", "Jajapur", "Kalahandi", "Kendrapara", "Kendujhar", "Khorda", "Mayurbhanj", "Nayagarh", "Puri", "Rayagada", "Sonapur", "Sundergarh"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", "Erode", "Kanchipuram", "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Namakkal", "Nilgiris", "Ramanathapuram", "Salem", "Tiruchirappalli", "Tirunelveli", "Tiruppur", "Tiruvannamalai", "Vellore"],
    "Telangana": ["Adilabad", "Hyderabad", "Karim Nagar", "Khammam", "Mahabub Nagar", "Medak", "Nalgonda", "Nizamabad", "Rangareddy", "Sangareddy", "Vikarabad", "Wanaparthy", "Warangal"],
    "Madhya Pradesh": ["Ujjain", "Kukshi", "Indore", "Dhar", "Dewas"]
}

# Get all Hesaathi Codes
unique_codes = df['Hesaathi Code'].unique()

# Shuffle state list to distribute fairly
state_list = list(state_district_map.keys())
random.shuffle(state_list)

# Map for state and district assignments
assignments = {}

for i, code in enumerate(unique_codes):
    state = state_list[i % len(state_list)]
    district = random.choice(state_district_map[state])
    assignments[code] = (state, district)

# Fill missing values
def fill_row(row):
    if pd.isna(row['State']) or pd.isna(row['District']):
        state, district = assignments[row['Hesaathi Code']]
        row['State'] = state
        row['District'] = district
    return row

df = df.apply(fill_row, axis=1)

# Save the updated Excel
df.to_excel("/home/thrymr/Downloads/performance_assigned_outputt.xlsx", index=False)



