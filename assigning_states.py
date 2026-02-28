# import pandas as pd

# # Step 1: Load your Excel file
# df = pd.read_excel("/home/thrymr/Desktop/purchases 25-26(apr-sep)/purchase_april_(25-26).xlsx")  # replace with your actual file path

# # Step 2: Define state to districts mapping
# state_district_map = {
#     "Andhra Pradesh": ["Ananthapur", "Chittoor", "Cuddapah", "East Godavari", "Guntur", "Krishna", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Vijayawada", "Visakhapatnam", "Vizianagaram", "West Godavari"],
#     "Karnataka": ["Bidar", "Ballari", "Kalabuargi", "Koppal", "Raichur", "Vijayanagara", "Yadagiri"],
#     "Maharashtra": ["Ahmed Nagar", "Amravati", "Aurangabad", "Beed", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli", "Jalgaon", "Kolhapur", "Latur", "Mumbai", "Nagpur", "Nanded", "Osmanabad", "Pune", "Raigarh Mh", "Raigarh(Mh)", "Satara", "Solapur", "Thane", "Yavatmal"],
#     "Odisha": ["Angul", "Balangir", "Balasore", "Baleswar", "Bargarh", "Bhadrak", "Boudh", "Cuttack", "Debagarh", "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghapur", "Jajapur", "Kalahandi", "Kendrapara", "Kendujhar", "Khorda", "Mayurbhanj", "Nayagarh", "Puri", "Rayagada", "Sonapur", "Sundergarh"],
#     "Tamil Nadu": ["Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", "Erode", "Kanchipuram", "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Namakkal", "Nilgiris", "Ramanathapuram", "Salem", "Tiruchirappalli", "Tirunelveli", "Tiruppur", "Tiruvannamalai", "Vellore"],
#     "Telangana": ["Adilabad", "Hyderabad", "Karim Nagar", "Khammam", "Mahabub Nagar", "Medak", "Nalgonda", "Nizamabad", "Rangareddy", "Sangareddy", "Vikarabad", "Wanaparthy", "Warangal"],
#     "Madhya Pradesh": ["Dewas", "Dhar", "Indore", "Kukshi", "Ujjain"]
# }

# # Step 3: Create district-to-state reverse mapping
# district_to_state = {}
# for state, districts in state_district_map.items():
#     for district in districts:
#         district_to_state[district.strip().lower()] = state

# # Step 4: Map the 'customer_district' column to state
# df["State"] = df["District"].str.strip().str.lower().map(district_to_state)

# # Step 5 (Optional): Save or display result
# df.to_excel("/home/thrymr/Desktop/purchases 25-26(apr-sep)/purchase_april_(25-26).xlsx", index=False)
# print(df.head())



import pandas as pd
import os

# Step 1: Folder path
folder_path = "/home/thrymr/Desktop/purchases 25-26(apr-sep)"

# Step 2: List of Excel files
files = [
    "purchase_april_(25-26).xlsx",
    "purchase_may_(25-26).xlsx",
    "june_purchase_(25-26).xlsx",
    "july_purchase(25-26).xlsx",
    "August_purchase(25-26).xlsx",
    "september_purchase(25-26).xlsx"
]

# Step 3: Define state to districts mapping
state_district_map = {
    "Andhra Pradesh": ["Ananthapur", "Chittoor", "Cuddapah", "East Godavari", "Guntur", "Krishna", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Vijayawada", "Visakhapatnam", "Vizianagaram", "West Godavari"],
    "Karnataka": ["Bidar", "Ballari", "Kalabuargi", "Koppal", "Raichur", "Vijayanagara", "Yadagiri"],
    "Maharashtra": ["Ahmed Nagar", "Amravati", "Aurangabad", "Beed", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli", "Jalgaon", "Kolhapur", "Latur", "Mumbai", "Nagpur", "Nanded", "Osmanabad", "Pune", "Raigarh Mh", "Raigarh(Mh)", "Satara", "Solapur", "Thane", "Yavatmal"],
    "Odisha": ["Angul", "Balangir", "Balasore", "Baleswar", "Bargarh", "Bhadrak", "Boudh", "Cuttack", "Debagarh", "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghapur", "Jajapur", "Kalahandi", "Kendrapara", "Kendujhar", "Khorda", "Mayurbhanj", "Nayagarh", "Puri", "Rayagada", "Sonapur", "Sundergarh"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", "Erode", "Kanchipuram", "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Namakkal", "Nilgiris", "Ramanathapuram", "Salem", "Tiruchirappalli", "Tirunelveli", "Tiruppur", "Tiruvannamalai", "Vellore"],
    "Telangana": ["Adilabad", "Hyderabad", "Karim Nagar", "Khammam", "Mahabub Nagar", "Medak", "Nalgonda", "Nizamabad", "Rangareddy", "Sangareddy", "Vikarabad", "Wanaparthy", "Warangal"],
    "Madhya Pradesh": ["Dewas", "Dhar", "Indore", "Kukshi", "Ujjain"]
}

# Step 4: Create district-to-state mapping
district_to_state = {
    district.strip().lower(): state
    for state, districts in state_district_map.items()
    for district in districts
}

# Step 5: Loop through each file
for file in files:
    file_path = os.path.join(folder_path, file)
    
    print(f"Processing: {file}")
    
    df = pd.read_excel(file_path)
    
    # Map District to State
    df["State"] = df["District"].astype(str).str.strip().str.lower().map(district_to_state)

    df.to_excel(file_path.replace(".xlsx", "_with_state.xlsx"), index=False)

print("✅ All files processed successfully")
