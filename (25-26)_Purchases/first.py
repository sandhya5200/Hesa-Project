import datetime
from fastapi import APIRouter
import random
import pandas as pd

month_map = [
    "April'25","May'25", "Jun'25", "Jul'25", "Aug'25","Sep'25", 
    "Oct'25", "Nov'25", "Dec'25","Jan'26", "Feb'26", "Mar'26"
]

business_dict = {
    "Agri Inputs": [9.09, 9.09, 9.10, 9.04, 9.05, 9.05, 9.06, 9.06, 9.07, 9.07, 9.08, 9.08],
    "Market Linkages Trading": [9.85, 9.85, 9.86, 9.80, 9.81, 9.81, 9.82, 9.82, 9.83, 9.83, 9.84, 9.84],
    "Market Linkages Value Intervention": [15.29, 15.29, 15.30, 15.24, 15.25, 15.25, 15.26, 15.26, 15.27, 15.27, 15.28, 15.28],
    "FMCG": [8.96, 8.96, 8.97, 8.91, 8.92, 8.92, 8.93, 8.93, 8.94, 8.94, 8.95, 8.95],
    "White Label": [24.56, 24.57, 24.57, 24.52, 24.52, 24.53, 24.53, 24.54, 24.54, 24.55, 24.55, 24.56, 24.56]
}


def purchase():
    print("before")
    product_quantity = pd.read_excel("/home/thrymr/Desktop/sales 25-26/final sales 25-26 (apr-sep)/sep_PIVOT.xlsx", sheet_name="Product Qty")
   
    product_gross = pd.read_excel("/home/thrymr/Desktop/sales 25-26/final sales 25-26 (apr-sep)/sep_PIVOT.xlsx", sheet_name="Taxable value")
    
    zone_df = pd.read_excel("/home/thrymr/Important/new_hessathi_with_additional_people_details (copy).xlsx")
    products_data = pd.read_excel("/home/thrymr/Important/my_products_file.xlsx")

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
            # Convert GST rate from percentage to decimal (e.g., 18 -> 0.18)
            if gst >= 1:
                gst = gst / 100
  
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
    df.to_excel("/home/thrymr/Downloads/SEPTEMBER.xlsx")
    print("completed")
    
purchase()