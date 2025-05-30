import datetime
from fastapi import APIRouter
import random
import pandas as pd

app = APIRouter(tags=["/purchases-24"])


month_map = [
    "April'24","May'24", "Jun'24", "Jul'24", "Aug'24","Sep'24", 
    "Oct'24", "Nov'24", "Dec'24","Jan'25", "Feb'25", "Mar'25"
]
business_dict = {
    "Agri inputs": [8.92, 8.95, 9.04, 8.75, 8.72, 8.76, 8.75, 8.76, 8.71, 8.77, 8.90, 8.91],                #these are in the order of  jan-dec
    "Market Linkages": [9.75, 9.77, 9.80, 9.6, 9.65, 9.69, 9.68, 9.69, 9.69, 9.70, 9.73, 9.74],
    "Value Intervention": [14.87, 15.23, 15.24, 14.71, 14.74, 14.78, 14.77, 14.75, 14.79, 14.79, 14.85, 14.86],
    "Fmcg": [8.87, 8.88, 8.91, 8.77, 8.79, 8.79, 8.78, 8.79, 8.80, 8.81, 8.91, 8.86],
    "White Label": [24.48, 24.50, 24.52, 24.39, 24.44, 24.45, 24.44, 24.45, 24.45, 24.47, 24.47, 24.48]
}

# @app.post("/purchases")
def purchase():
    print("before")
    product_quantity = pd.read_excel("/home/thrymr/Downloads/oct_qty.xlsx")
    product_gross = pd.read_excel("/home/thrymr/Downloads/oct-gross.xlsx")
    zone_df = pd.read_excel("/home/thrymr/Downloads/zone_user_category (5) 1.xlsx",sheet_name="Data")
    products_data = pd.read_excel("/home/thrymr/Downloads/Copy of telangana_logics_new (1)(1).xlsx",sheet_name="Products")
    #vendor = pd.read_excel("/home/thrymr/Downloads/Vendor data 1 1.xlsx",sheet_name="10-15 vendors from this data")
    col = product_gross.columns
    track = {}
    rows = []
    districts = {}
    old_gross = {}
    
    zone_df = zone_df[zone_df["CODE"].notna() & (zone_df["CODE"].str.strip() != "")]
    zone_df.insert(len(zone_df.columns), "Month_Index", "")

    zone_df["Month_Index"] = zone_df["Month"].apply(lambda x: month_map.index(x) if x in month_map else -1)
    k = random.randint(20,25)
    d= None
    for ind,r in product_gross.iterrows():
        missed_quantity = 0
        row_data = r.to_list()
        subv = str(row_data[1])

        category = row_data[5]
        sub_category = row_data[6]

        print(row_data[0])

        date_value = datetime.datetime.strptime(row_data[0], '%d-%m-%Y')
        # date_value = datetime.datetime.strptime(str(row_data[0]), '%Y-%m-%d %H:%M:%S')

        
        next_day = date_value + datetime.timedelta(days=1)
        
        if next_day.month == date_value.month:
            date_value = next_day
        month = date_value.month
        
        if d!=date_value:
            d= date_value
            
        vertical = "Consumer Business" if subv in ["Fmcg","White Label"] else "Agri Business"
        p_name = row_data[2]
        if pd.isna(p_name):
            continue
        
        # print(p_name)
        pr_empty = False
        pr = products_data[(products_data["Name of product"].str.lower()==p_name.lower())]
        if pr.empty:
            print("missed : ",p_name)
            pr_empty = True
            gst = 0.05
            avg_q = 10
            # uom = row_data[3]
        else:
            pr= pr.sample(n=1).iloc[0]
            gst = row_data[7] 
            # print(p_name)
            avg_q = int(pr["Avg purchase qty"])
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
                if pr_empty:
                    avg_q = quantity
                taxable = gross/(1+gst)

                taxable -= taxable*m

                unit_p = taxable/quantity

                # bulk = quantity*0.8
                if avg_q>=quantity:
                        rnd = quantity
                else:
                    min = avg_q-(avg_q*0.10)
                    max = avg_q+(avg_q*0.10)
                    rnd = int(random.uniform(min,max))
                    if rnd<=0:
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
                        hesas = zone_df[(zone_df["CODE"] == track[cs_name])]
                        hs = hesas.sample(n=1).iloc[0]
                    else:
                        hs = hesas.sample(n=1).iloc[0]
                        # print(hs)
                        hs_code = str(hs.iloc[15])
                        track[cs_name] = hs_code
                    # print(quantity)
                    if quantity-rnd<0:
                        rnd = quantity
                    ind_taxable = unit_p*rnd
                    gst_am = gst*ind_taxable
                    row = {
                        "Date": date_value.strftime('%d/%m/%Y'),
                        "Purchase Order Number": None,
                        "Cohort Month": hs.iloc[6],
                        "Hesaathi Code": hs_code,
                        "Customer Name": cs_name,
                        "Customer Number": "",
                        "District": dist,
                        "Customer State": "",
                        "Customer Location":  "",
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
    df["Purchase Order Number"] = "HS-PO-AG-"+(df.groupby(["Date", "Customer Name"]).ngroup() + 1).apply(lambda x: f"{x:06d}")
    print(len(rows))                
    df.to_excel("/home/thrymr/Downloads/october.xlsx")
    print("completed")
    
purchase()