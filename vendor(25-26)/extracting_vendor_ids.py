import pandas as pd

files = [
    "/home/thrymr/Desktop/purchases 25-26(apr-sep)/August_purchase(25-26)_with_state.xlsx",
    "/home/thrymr/Desktop/purchases 25-26(apr-sep)/july_purchase(25-26)_with_state.xlsx",
    "/home/thrymr/Desktop/purchases 25-26(apr-sep)/june_purchase_(25-26)_with_state.xlsx",
    "/home/thrymr/Desktop/purchases 25-26(apr-sep)/purchase_april_(25-26)_with_state.xlsx",
    "/home/thrymr/Desktop/purchases 25-26(apr-sep)/purchase_may_(25-26)_with_state.xlsx",
    "/home/thrymr/Desktop/purchases 25-26(apr-sep)/september_purchase(25-26)_with_state.xlsx"
]

df_list = [pd.read_excel(file) for file in files]
df = pd.concat(df_list, ignore_index=True)

state_district_map = {
    "Andhra Pradesh": ["Ananthapur", "Chittoor", "Cuddapah", "East Godavari", "Guntur", "Krishna", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Vijayawada", "Visakhapatnam", "Vizianagaram", "West Godavari"],
    "Karnataka": ["Bidar", "Ballari", "Kalabuargi", "Koppal", "Raichur", "Vijayanagara", "Yadagiri"],
    "Maharashtra": ["Ahmed Nagar", "Amravati", "Aurangabad", "Beed", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli", "Jalgaon", "Kolhapur", "Latur", "Mumbai", "Nagpur", "Nanded", "Osmanabad", "Pune", "Raigarh Mh", "Raigarh(Mh)", "Satara", "Solapur", "Thane", "Yavatmal"],
    "Odisha": ["Angul", "Balangir", "Balasore", "Baleswar", "Bargarh", "Bhadrak", "Boudh", "Cuttack", "Debagarh", "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghapur", "Jajapur", "Kalahandi", "Kendrapara", "Kendujhar", "Khorda", "Mayurbhanj", "Nayagarh", "Puri", "Rayagada", "Sonapur", "Sundergarh"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", "Erode", "Kanchipuram", "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Namakkal", "Nilgiris", "Ramanathapuram", "Salem", "Tiruchirappalli", "Tirunelveli", "Tiruppur", "Tiruvannamalai", "Vellore"],
    "Telangana": ["Adilabad", "Hyderabad", "Karim Nagar", "Khammam", "Mahabub Nagar", "Medak", "Nalgonda", "Nizamabad", "Rangareddy", "Sangareddy", "Vikarabad", "Wanaparthy", "Warangal"],
    "Madhya Pradesh": ["Dewas", "Dhar", "Indore", "Kukshi", "Ujjain"]
}

district_to_state = {
    district.lower(): state
    for state, districts in state_district_map.items()
    for district in districts
}

df["State"] = df["District"].str.strip().str.lower().map(district_to_state)

karnataka_df = df[df["State"] == "Tamil Nadu"]

vendor_df = (
    karnataka_df[["Vendor ID", "State", "District"]]
    .drop_duplicates(subset=["Vendor ID"])
    .sort_values(by=["District", "Vendor ID"])  
)

output_path = "/home/thrymr/Downloads/TamilNadu_Unique_Vendors.xlsx"
vendor_df.to_excel(output_path, index=False)

print("File saved successfully:", output_path)
print(vendor_df.head())
