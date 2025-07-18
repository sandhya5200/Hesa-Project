import pandas as pd

df = pd.read_excel("/home/thrymr/Downloads/october.xlsx") 

state_district_map = {
    "Andhra Pradesh": ["Ananthapur", "Chittoor", "Cuddapah", "East Godavari", "Guntur", "Krishna", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Vijayawada", "Visakhapatnam", "Vizianagaram", "West Godavari"],
    "Karnataka": ["Bidar", "Ballari", "Kalabuargi", "Koppal", "Raichur", "Vijayanagara", "Yadagiri"],
    "Maharashtra": ["Ahmed Nagar", "Amravati", "Aurangabad", "Beed", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli", "Jalgaon", "Kolhapur", "Latur", "Mumbai", "Nagpur", "Nanded", "Osmanabad", "Pune", "Raigarh Mh", "Raigarh(Mh)", "Satara", "Solapur", "Thane", "Yavatmal"],
    "Odisha": ["Angul", "Balangir", "Balasore", "Baleswar", "Bargarh", "Bhadrak", "Boudh", "Cuttack", "Debagarh", "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghapur", "Jajapur", "Kalahandi", "Kendrapara", "Kendujhar", "Khorda", "Mayurbhanj", "Nayagarh", "Puri", "Rayagada", "Sonapur", "Sundergarh"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", "Erode", "Kanchipuram", "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Namakkal", "Nilgiris", "Ramanathapuram", "Salem", "Tiruchirappalli", "Tirunelveli", "Tiruppur", "Tiruvannamalai", "Vellore"],
    "Telangana": ["Adilabad", "Hyderabad", "Karim Nagar", "Khammam", "Mahabub Nagar", "Medak", "Nalgonda", "Nizamabad", "Rangareddy", "Sangareddy", "Vikarabad", "Wanaparthy", "Warangal"],
    "Madhya Pradesh": ["Dewas", "Dhar", "Indore", "Kukshi", "Ujjain"]
}

district_to_state = {}
for state, districts in state_district_map.items():
    for district in districts:
        district_to_state[district.strip().lower()] = state

df["State"] = df["District"].str.strip().str.lower().map(district_to_state)

df.to_excel("/home/thrymr/Downloads/purchase_October(24-25).xlsx", index=False)

print(df.head())
