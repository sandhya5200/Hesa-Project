import datetime
from fastapi import APIRouter
import random
import pandas as pd

month_map = [
    "April'20", "May'20", "Jun'20", "Jul'20", "Aug'20", "Sep'20", 
    "Oct'20", "Nov'20", "Dec'20", "Jan'21", "Feb'21", "Mar'21"
]

business_dict = {
    "Agri Inputs": [7.10, 7.25, 7.40, 7.55, 7.70, 7.85, 8.00, 8.15, 8.30, 8.45, 8.60, 8.75],                #these are in the order of  jan-dec
    "Market Linkages Trading": [7.50, 7.65, 7.80, 7.95, 8.10, 8.25, 8.40, 8.55, 8.70, 8.85, 8.95, 9.00],
    "FMCG": [ 7.20, 7.35, 7.50, 7.65, 7.80, 7.95, 8.10, 8.25, 8.40, 8.55, 8.70, 8.85],

}

def purchase():
    print("before")
    product_quantity = pd.read_excel(r"c:\Users\ksand\Downloads\pivot.xlsx", sheet_name="Quantity")
   
    product_gross = pd.read_excel(r"c:\Users\ksand\Downloads\pivot.xlsx", sheet_name="Taxable value")
    
    zone_df = pd.read_excel(r"c:\Users\ksand\Downloads\Important 2\Important\new_hessathi_with_additional_people_details (copy).xlsx")
    products_data = pd.read_excel(r"c:\Users\ksand\Downloads\myyy.xlsx")
    #vendor = pd.read_excel("/home/thrymr/Downloads/Vendor data 1 1.xlsx",sheet_name="10-15 vendors from this data")
    col = product_gross.columns
    track = {}
    rows = []
    districts = {}
    old_gross = {}
    
    zone_df = zone_df[zone_df["Hesaathi Code"].notna() & (zone_df["Hesaathi Code"].str.strip() != "")]
    zone_df.insert(len(zone_df.columns), "Month_Index", "")

    zone_df["Month_Index"] = zone_df["Onboarding Month"].apply(lambda x: month_map.index(x) if x in month_map else -1)
    k = random.randint(20,25)
    d= None
    for ind,r in product_gross.iterrows():
        missed_quantity = 0
        row_data = r.to_list()
        subv = str(row_data[1])

        category = row_data[5]
        sub_category = row_data[6]

        print(row_data[0])

        # date_value = datetime.datetime.strptime(row_data[0], '%d-%m-%Y')
        date_value = datetime.datetime.strptime(str(row_data[0]), '%Y-%m-%d %H:%M:%S')

        
        next_day = date_value + datetime.timedelta(days=1)
        
        if next_day.month == date_value.month:
            date_value = next_day
        month = date_value.month
        
        if d!=date_value:
            d= date_value
            
        vertical = "Consumer Business" if subv in ["FMCG","White Label"] else "Agri Business"
        p_name = row_data[2]
        if pd.isna(p_name):
            continue
        
        # print(p_name)
        pr_empty = False
        pr = products_data[(products_data["Product Name"].str.lower()==p_name.lower())]
        if pr.empty:
            print("missed : ",p_name)
            pr_empty = True
            gst = 0.05
            # uom = row_data[3]
        else:
            pr= pr.sample(n=1).iloc[0]
            gst = row_data[7] 
            # print(p_name)
            hsn_code = row_data[3]
        uom = row_data[4]
        
        for c in range(len(row_data)):
            if c<8:
                continue
            gross = row_data[c]
            dist = col[c]
            if not dist:
                continue
            if dist not in districts:
                districts[dist] = []
            if subv not in old_gross:
                old_gross[subv] = 0
                
            # print(dist)
            if gross and gross>0:
                gross = gross * (1+gst) # this is set based on input data if input is taxable keep this else comment out this
                margin = business_dict[subv][month-1]
                if old_gross[subv]!=0:
                    rand = old_gross[subv]*-1
                    old_gross[subv] = 0
                else:
                    rand = random.randint(-5,5)/100
                    old_gross[subv] = rand
                m = ((margin*(rand))+margin)/100                
                if month < 4:
                    hesas = zone_df[
                        (zone_df["District"].str.lower() == dist.lower()) &
                        (zone_df["Month_Index"] ==-1) | (zone_df["Month_Index"] <= month + 8)
                    ]
                    if hesas.empty:
                        hesas = zone_df[
                        (zone_df["District"].str.lower() == "HYDERABAD".lower()) &
                        (zone_df["Month_Index"] ==-1) | (zone_df["Month_Index"] <= month + 8)
                    ]
                else:
                    hesas = zone_df[
                        (zone_df["District"].str.lower() == dist.lower()) &
                        (zone_df["Month_Index"] ==-1) | (zone_df["Month_Index"] <= month - 4)
                    ]
                    if hesas.empty:
                        hesas = zone_df[
                        (zone_df["District"].str.lower() == "HYDERABAD".lower()) &
                        (zone_df["Month_Index"] ==-1) | (zone_df["Month_Index"] <= month - 4)
                    ]
                
                
                # gross -= gross*m
                quantity = product_quantity.iloc[ind].iloc[c]
                quantity += missed_quantity
                missed_quantity = 0
                init_q = quantity
                # print(quantity)
                if not pd.notna(quantity) or quantity==0:
                    break
                quantity = int(quantity) if quantity>=1 else 1
                
                taxable = gross/(1+gst)

                taxable -= taxable*m

                unit_p = taxable/quantity

                # Use a random percentage of the available quantity (70-100%)
                rnd = int(quantity * random.uniform(0.7, 1.0))
                if rnd <= 0:
                    rnd = 1
                    
                while quantity>0:  
                    # day = random.randint(1,20) if quantity>=bulk else calendar.monthrange(year,month)[1]   # below date 20 rest amount is falling to date 30
                    # date = datetime.datetime(year, month, day).strftime('%d-%m-%Y')

                    if hesas.empty:
                        print("empty ____________________---------------")
                        break
                    
                    cs_name = "" 
                    
                    if len(districts[dist])>k:
                        cs_name=random.choice(districts[dist])
                    else :
                        _counter = len(districts[dist])+1
                        cs_name = "HS-VED-"+dist+"-"+subv+"-"+f"{_counter:04d}"
                        districts[dist].append(cs_name)

                        
                    if cs_name in track:
                        # print(track[cs_name])
                        hesas = zone_df[(zone_df["Hesaathi Code"] == track[cs_name])]
                        hs = hesas.sample(n=1).iloc[0]
                    else:
                        hs = hesas.sample(n=1).iloc[0]
                        # print(hs)
                        hs_code = str(hs["Hesaathi Code"])
                        track[cs_name] = hs_code
                    # print(quantity)
                    if quantity-rnd<0:
                        rnd = quantity
                    ind_taxable = unit_p*rnd
                    gst_am = gst*ind_taxable
                    row = {
                        "Date": date_value.strftime('%d/%m/%Y'),
                        "District": dist,
                        "Vertical": vertical,
                        "Sub Vertical": subv,
                        "Category": category,
                        "Sub Category":sub_category,
                        "Product Name": p_name,
                        "HSN Code": hsn_code if not pr_empty else "",
                        "Product Qty": rnd,
                        "UOM": uom ,
                        "GST Rate": gst,
                        "Gross Total": ind_taxable+gst_am,
                        "Taxable Value": ind_taxable,
                        "GST Amount": gst_am
                    }
                    rows.append(row)
                    quantity-=rnd
                    init_q -= rnd
                missed_quantity+=init_q
    df = pd.DataFrame(rows)
    print(len(rows))                
    df.to_excel(r"c:\Users\ksand\Downloads\apr.xlsx")
    print("completed")
    
purchase()