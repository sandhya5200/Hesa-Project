#This code is used to generate input files for genearting delivery challan PDF'S and Invoices PDF'S .

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
import pandas as pd
from io import BytesIO
from num2words import num2words
import re
 
app = FastAPI()
 
def convert_number_to_words(number):
    """Convert a numeric value to words in Indian numbering system."""
    try:
        # Convert the number to words, formatted in Indian Rupee context
        words = num2words(number, lang='en_IN').replace('-', ' ').title()
        return f"Indian Rupee {words} Only"
    except Exception as e:
        return "Invalid Number"
 
@app.post("/process-excel/")
async def process_excel(file: UploadFile = File(...)):
    # Read the uploaded Excel file
    contents = await file.read()
    input_df = pd.read_excel(BytesIO(contents)) #sheet index

    # Define the expected columns and their mappings
    columns_mapping = {
        'Hesaathi Code': 'Hesaathi Code',
        'Invoice No': 'Invoice no.',                #to get even invoicenumber for generating invoices
        'Customer Name': 'Customer Name',
        'MCP' : 'MCP',
        'Customer Address': 'Customer Address',
        'Customer Mobile': 'Customer Mobile',

        'CustomerID':'New CustomerID',
        'Customer State':'Customer State',
        'Customer Mandal':'Customer Mandal',
        'CustomerDistrict':'Customer District',
        'Pincode':'Pincode',

        'Product Name': 'Product Name',
        'HSN Code': 'HSN/SAC',
        'Product Qty': 'Quantity',
        'UOM': 'UOM',
        'Net Price PU': 'Rate',
        'Facilitator': 'Facilitator',
        'GST Rate': 'GST Rate',
        'CGST': 'CGST',
        'SGST': 'SGST',
        'IGST': 'IGST',
    }

    # Rename columns
    input_df.rename(columns={col: new_col for col, new_col in columns_mapping.items() if col in input_df.columns}, inplace=True)

    # Add 'Delivery Challan' column using the last six digits of 'Invoice no.'
    if 'Invoice no.' in input_df.columns:
        input_df['Delivery Challan'] = input_df['Invoice no.'].apply(lambda x: f'DC-{x[10:12]}-{x[-6:]}')

    # Add 'Challan Date' column by adding two days to the 'Date'
    if 'Date' in input_df.columns:
        input_df['Challan Date'] = (pd.to_datetime(input_df['Date'], dayfirst=True) + pd.Timedelta(days=2)).dt.date

    # Add 'Amount' as the product of 'Quantity' and 'Rate'
    if 'Quantity' in input_df.columns and 'Rate' in input_df.columns:
        input_df['Amount'] = input_df['Quantity'] * input_df['Rate']

    # Ensure 'Facilitator' and 'Place of Supply' columns are cleaned
    if 'Quantity' in input_df.columns and 'Rate' in input_df.columns:
        input_df['Amount'] = input_df['Quantity'] * input_df['Rate']

    # Ensure 'Facilitator' and 'Place of Supply' columns are cleaned
    input_df['Facilitator'] = input_df['Facilitator'].fillna('').astype(str).str.strip()
    input_df['Customer State'] = input_df['Customer State'].fillna('').astype(str).str.strip()

    def normalize_text(text):
        return re.sub(r'\s+', ' ', str(text)).strip().casefold()

# # Normalize mapping keys to lowercase and strip spaces
#     normalized_mapping = {
#         (key[0].strip().lower(), key[1].strip().lower()): value
#         for key, value in {
#             ("Hesa enterprises Private Limited", "Andhra Pradesh"): ("39-11-45, Bank Street, Muralinagar, Visakhapatnam, Andhra Pradesh, 530007", "37AAFCR8177F1ZZ"),
#             ("Hesa enterprises Private Limited", "Bihar"): ("B/124, Kankarbagh, Kankar Bagh Road, Patna, Bihar, 800020", "10AAFCR8177F1ZF"),
#             ("Hesa enterprises Private Limited", "Telangana"): ("Plot No 136, 1-4-158/136, Kapra, Saipuricolony, Hyderabad, Telangana, 500094", "36AAFCR8177F1Z1"),
#             ("Hesa enterprises Private Limited", "Karnataka"): ("H. No 2-90B/68/57, Sedam Road, Near Gurkul Vidya Mandir, Om Nagar, Kalaburagi, Kalaburagi, Karnataka, 585105", "29AAFCR8177F1ZW"),
#             ("Hesa enterprises Private Limited", "Odisha"): ("747/1170, PARAGON, Belagacchia, Khordha, Odisha, 754005", "21AAFCR8177F1ZC"),
#             ("Hesa enterprises Private Limited", "Jharkhand"): ("flat No-C, First Floor, Harmu Housing Colony, Ranchi Doranda, J harkhand, 834002", "Unregistered"),
#             ("Hesa enterprises Private Limited", "Tamil Nadu"): ("F28, AV HI FIELD APARTMENT, Visuvasapuram, Coimbatore, 641035", "Unregistered"),
#             ("Hesa enterprises Private Limited", "Haryana"): ("0, ADRASH NAGAR, Narnaul, Mahendragarh, Haryana, 123001", "06AAFCH9926E1ZH"),
#             ("Hesa enterprises Private Limited", "Maharashtra"): ("FIRST FLOOR, 101, SH 77, Near Latur Urban Bank, Latur, Latur, Maharashtra, 413512", "27AAFCH9722G1ZF"),

#             ("Hesa Enterprises Private Limited", "Andhra Pradesh"): ("39-11-45, Bank Street, Muralinagar, Visakhapatnam, Andhra Pradesh, 530007", "37AAFCR8177F1ZZ"),
#             ("Hesa Enterprises Private Limited", "Bihar"): ("B/124, Kankarbagh, Kankar Bagh Road, Patna, Bihar, 800020", "10AAFCR8177F1ZF"),
#             ("Hesa Enterprises Private Limited", "Telangana"): ("Plot No 136, 1-4-158/136, Kapra, Saipuricolony, Hyderabad, Telangana, 500094", "36AAFCR8177F1Z1"),
#             ("Hesa Enterprises Private Limited", "Karnataka"): ("H. No 2-90B/68/57, Sedam Road, Near Gurkul Vidya Mandir, Om Nagar, Kalaburagi, Kalaburagi, Karnataka, 585105", "29AAFCR8177F1ZW"),
#             ("Hesa Enterprises Private Limited", "Odisha"): ("747/1170, PARAGON, Belagacchia, Khordha, Odisha, 754005", "21AAFCR8177F1ZC"),
#             ("Hesa Enterprises Private Limited", "Jharkhand"): ("flat No-C, First Floor, Harmu Housing Colony, Ranchi Doranda, Jharkhand, 834002", "Unregistered"),
#             ("Hesa Enterprises Private Limited", "Tamil Nadu"): ("F28, AV HI FIELD APARTMENT, Visuvasapuram, Coimbatore, 641035", "Unregistered"),
#             ("Hesa Enterprises Private Limited", "Haryana"): ("0, ADRASH NAGAR, Narnaul, Mahendragarh, Haryana, 123001", "06AAFCH9926E1ZH"),
#             ("Hesa Enterprises Private Limited", "Maharashtra"): ("FIRST FLOOR, 101, SH 77, Near Latur Urban Bank, Latur, Latur, Maharashtra, 413512", "27AAFCH9722G1ZF"),
            

#             ("Hesa Agritech Private Limited", "haryana"): ("0, Adarsh Nagar, Narnaul, Mahendragarh, Haryana, 123001", "06AAFCH9722G1ZJ"),
#             ("Hesa Agritech Private Limited", "andhra pradesh"): ("39-11-45, Bank Street, Muralinagar, Visakhapatnam, Andhra Pradesh, 530007", "37AAFCH9722G1ZE"),
#             ("Hesa Agritech Private Limited", "maharashtra"): ("FIRST FLOOR, 101, SH 77, Near Latur Urban Bank, Latur, Latur, Maharashtra, 413512", "27AAFCH9722G1ZF"),
#             ("Hesa Agritech Private Limited", "Tamil Nadu"): ("H.No 2/361, Maryiyamman Kovil Street, Minnur, Tirupathur, Tamil Nadu, 635807", "33AAFCH9722G1ZM"),
#             ("Hesa Agritech Private Limited", "Odisha"): ("747/1170, PARAGON, Belagacchia, Khordha, Odisha, 754005", "21AAFCH9722G1ZR"),
#             ("Hesa Agritech Private Limited", "telangana"): ("Plot No 136, 1-4-158/136, Kapra, Saipuricolony, Hyderabad, Telangana, 500094", "36AAFCH9722G1ZG"),
#             ("Hesa Agritech Private Limited", "jharkhand"): ("flat No-C, First Floor, Harmu Housing Colony, Ranchi Doranda, Jharkhand, 834002", "Unregistered"),
#             ("Hesa Agritech Private Limited", "bihar"): ("B/124, Kankarbagh, Kankar Bagh Road, Patna, Bihar, 800020", "10AAFCR8177F1ZF"),
#             ("Hesa Agritech Private Limited", "karnataka"): ("#318, Komarla Brigade Vista, Gowdanpalya Main Road, 3rd floor, Uttarahalli, Bengaluru, Karnataka, 560061", "Unregistered"),
            
            
            
#             ("Hesa Consumer Products Private Limited", "Odisha"): ("747/1170, PARAGON, Belagacchia, Khordha, Odisha, 754005", "21AAFCH9926E1ZP"),
#             ("Hesa Consumer Products Private Limited", "andhra pradesh"): ("39-11-45, bank street, Muralinagar, Visakhapatnam, Visakhapatnam, Andhra Pradesh, 530007", "37AAFCH9926E1ZC"),
#             ("Hesa Consumer Products Private Limited", "telangana"): ("1-4-158/136, Saipuri Colony, Kapra,Sainikpuri, Sainikpuri, Hyderabad, Telangana, 500094", "36AAFCH9926E1ZE"),
#             ("Hesa Consumer Products Private Limited", "jharkhand"): ("flat No-C, First Floor, Harmu Housing Colony, Ranchi Doranda, Jharkhand, 834002", "Unregistered"),
#             ("Hesa Consumer Products Private Limited", "Tamil Nadu"): ("H. No 2/361, Mariyammam Kovil Street, Ambur Taluk, Minnur, Tirupathur, Tamil Nadu, 635807", "33AAFCH9926E1ZK"),
#             ("Hesa Consumer Products Private Limited", "maharashtra"): ("4TH, R-2/2418/7A, SURVEY NO 259, Latur Industrial Area Additional, Latur, Maharashtra, 413531", "27AAFCH9926E1ZD"),
#             ("Hesa Consumer Products Private Limited", "Haryana"): ("0, ADRASH NAGAR, Narnaul, Mahendragarh, Haryana, 123001", "06AAFCH9926E1ZH"),
#             ("Hesa Consumer Products Private Limited", "bihar"): ("Ground floor, vijaya rajit singh Bhavan, Bampali, Bhojpur, Bihar, 802312", "10AAFCH9926E1ZS"),
#             ("Hesa Consumer Products Private Limited", "karnataka"): ("A3, Gangotri apartments, 3rd A Block, Gokulam, Mysore, Karnataka", "Unregistered")

#         }.items()

#     }

    normalized_mapping = {
        ("hesa agritech private limited", "haryana"): (
            "0, Adarsh Nagar, Narnaul, Mahendragarh, Haryana, 123001",
            "06AAFCH9722G1ZJ"
        ),
        ("hesa agritech private limited", "andhra pradesh"): (
            "39-11-45, Bank Street, Muralinagar, Visakhapatnam, Andhra Pradesh, 530007",
            "37AAFCH9722G1ZE"
        ),
        ("hesa agritech private limited", "maharashtra"): (
            "FIRST FLOOR, 101, SH 77, Near Latur Urban Bank, Latur, Latur, Maharashtra, 413512",
            "27AAFCH9722G1ZF"
        ),
        ("hesa agritech private limited", "tamil nadu"): (
            "H.No 2/361, Maryiyamman Kovil Street, Minnur, Tirupathur, Tamil Nadu, 635807",
            "33AAFCH9722G1ZM"
        ),
        ("hesa agritech private limited", "odisha"): (
            "747/1170, PARAGON, Belagacchia, Khordha, Odisha, 754005",
            "21AAFCH9722G1ZR"
        ),
        ("hesa agritech private limited", "telangana"): (
            "Plot No 136, 1-4-158/136, Kapra, Saipuricolony, Hyderabad, Telangana, 500094",
            "36AAFCH9722G1ZG"
        ),
        ("hesa agritech private limited", "jharkhand"): (
            "flat No-C, First Floor, Harmu Housing Colony, Ranchi Doranda, Jharkhand, 834002",
            "Unregistered"
        ),
        ("hesa agritech private limited", "bihar"): (
            "B/124, Kankarbagh, Kankar Bagh Road, Patna, Bihar, 800020",
            "10AAFCR8177F1ZF"
        ),
        ("hesa agritech private limited", "karnataka"): (
            "#318, Komarla Brigade Vista, Gowdanpalya Main Road, 3rd floor, Uttarahalli, Bengaluru, Karnataka, 560061",
            "Unregistered"
        ),

        ("hesa consumer products private limited", "odisha"): (
            "747/1170, PARAGON, Belagacchia, Khordha, Odisha, 754005",
            "21AAFCH9926E1ZP"
        ),
        ("hesa consumer products private limited", "andhra pradesh"): (
            "39-11-45, bank street, Muralinagar, Visakhapatnam, Visakhapatnam, Andhra Pradesh, 530007",
            "37AAFCH9926E1ZC"
        ),
        ("hesa consumer products private limited", "telangana"): (
            "1-4-158/136, Saipuri Colony, Kapra,Sainikpuri, Sainikpuri, Hyderabad, Telangana, 500094",
            "36AAFCH9926E1ZE"
        ),
        ("hesa consumer products private limited", "jharkhand"): (
            "flat No-C, First Floor, Harmu Housing Colony, Ranchi Doranda, Jharkhand, 834002",
            "Unregistered"
        ),
        ("hesa consumer products private limited", "tamil nadu"): (
            "H. No 2/361, Mariyammam Kovil Street, Ambur Taluk, Minnur, Tirupathur, Tamil Nadu, 635807",
            "33AAFCH9926E1ZK"
        ),
        ("hesa consumer products private limited", "maharashtra"): (
            "4TH, R-2/2418/7A, SURVEY NO 259, Latur Industrial Area Additional, Latur, Maharashtra, 413531",
            "27AAFCH9926E1ZD"
        ),
        ("hesa consumer products private limited", "haryana"): (
            "0, ADRASH NAGAR, Narnaul, Mahendragarh, Haryana, 123001",
            "06AAFCH9926E1ZH"
        ),
        ("hesa consumer products private limited", "bihar"): (
            "Ground floor, vijaya rajit singh Bhavan, Bampali, Bhojpur, Bihar, 802312",
            "10AAFCH9926E1ZS"
        ),
        ("hesa consumer products private limited", "karnataka"): (
            "A3, Gangotri apartments, 3rd A Block, Gokulam, Mysore, Karnataka",
            "Unregistered"
        )
    }


    input_df['Company Address'] = input_df.apply(
        lambda row: normalized_mapping.get(
            (normalize_text(row['Facilitator']), normalize_text(row['Customer State'])),
            ("", "")
        )[0],
        axis=1
    )

    input_df['GSTIN'] = input_df.apply(
        lambda row: normalized_mapping.get(
            (normalize_text(row['Facilitator']), normalize_text(row['Customer State'])),
            ("", "")
        )[1],
        axis=1
    )



    # Add 'Challan Type' column with 'Sales'
    input_df['Challan Type'] = 'Sales'

    # Generate sequential S.NO for each unique 'Invoice no.'
    unique_invoices = input_df['Invoice no.'].unique()
    invoice_to_sno = {invoice: idx + 1 for idx, invoice in enumerate(unique_invoices)}
    input_df['S.NO'] = input_df['Invoice no.'].map(invoice_to_sno)

    # Calculate 'Sub total' as the sum of 'Taxable Value' grouped by 'Invoice no.'
    if 'Taxable Value' in input_df.columns and 'Invoice no.' in input_df.columns:
        input_df['Taxable Value'] = pd.to_numeric(input_df['Taxable Value'], errors='coerce')
        
    # Calculate the subtotal
    subtotal_series = input_df.groupby('Invoice no.')['Taxable Value'].transform('sum')
    input_df['Sub total'] = None
    input_df.loc[input_df.duplicated('Invoice no.', keep='last') == False, 'Sub total'] = subtotal_series

    # Calculate the subtotal and round to 2 decimal points
    input_df['Subtotal'] = input_df.groupby('Invoice no.')['Amount'].transform('sum').round(2)

    # Calculate CGST, SGST, IGST sums and round to 2 decimal points
    input_df['CGST_sum'] = input_df.groupby('Invoice no.')['CGST'].transform('sum').round(2)
    input_df['SGST_sum'] = input_df.groupby('Invoice no.')['SGST'].transform('sum').round(2)
    input_df['IGST_sum'] = input_df.groupby('Invoice no.')['IGST'].transform('sum').round(2)

    # Calculate the total
    input_df['Total'] = input_df['Subtotal'] + input_df['CGST_sum'] + input_df['SGST_sum'] + input_df['IGST_sum']
    input_df = input_df.drop(columns=['CGST_sum', 'SGST_sum', 'IGST_sum'])

    # Ensure 'Total' is rounded to 2 decimal points and formatted correctly
    input_df['Total'] = input_df.groupby('Invoice no.')['Total'].transform(lambda x: x.where(x.index == x.index[-1], 0)).apply(lambda x: int(x)).astype(float)

    input_df['Total'].fillna(0, inplace=True)
    input_df['Total'] = input_df['Total'].round(2).astype(float)
    input_df['Total'] = input_df['Total'].map('{:.2f}'.format)

    # Convert 'Total' to words
    input_df['Total In Words'] = input_df['Total'].apply(lambda x: convert_number_to_words(float(x)))

    # Define the output columns
    output_columns = ['Hesaathi Code', 'Delivery Challan', 'Invoice no.', 'New CustomerID', 'Customer Name', 
                    'Customer Mobile', 'Customer Address', 'Customer Mandal','Customer District','Customer State','Pincode',
                    'Facilitator', 'Product Name', 'HSN/SAC', 
                    'Quantity', 'UOM', 'Rate', 'Company Address', 'GSTIN', 'Challan Date', 
                    'Amount', 'Challan Type', 'S.NO', 'Sub total', 'GST Rate', 'CGST', 'SGST', 
                    'IGST', 'Total', 'Total In Words', 'MCP']

    # Reindex the dataframe with the required columns
    output_df = input_df.reindex(columns=output_columns)

    # Save the new dataframe to an Excel file
    output_stream = BytesIO()
    output_df.to_excel(output_stream, index=False)
    output_stream.seek(0)

    # Return the Excel file as a response
    return StreamingResponse(
        output_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=ready_{file.filename}"}
    )
