import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm , inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
import math

FIRST_PAGE_ROWS = 15
SUBSEQUENT_PAGE_ROWS = 35

def draw_product_table(c, items, margin_left, first_page_table_y, subsequent_page_table_y, width):
    table_data = [["S. No", "Item & Description", "HSN/SAC", "Qty", "Rate", "GST%", "CGST", "SGST", "Amount"]]  
    current_row = 0  
    is_first_page = True  
    
    c.setStrokeColor(colors.black)         
    c.setLineWidth(1.5)
    middle_b = 28 * cm
    #c.line(0, middle_b, width - 0, middle_b) 

    first_page_table_y = middle_b - 4.9 * inch
    subsequent_page_table_y = middle_b

    row_limit = FIRST_PAGE_ROWS  
    total_amount = 0
    for i, item in enumerate(items, start=1):
        product_name = item['Product_Name'][:26]  
        if len(item['Product_Name']) > 26:
            product_name += ".."  
        hsn = item.get('Hsn_Code')
        amount = (item['Product_Qty'] * float(item['Net_Price_Pu'])) + float(item['Cgst']) + float(item['Sgst'])
        total_amount += amount  
        table_data.append([
            str(i),
            product_name,
            hsn,
            round(item['Product_Qty'], 2),
            f"{float(item['Net_Price_Pu']):.2f}",
            item["GST_Rate"] * 100,
            round(item['Cgst'],2),
            round(item['Sgst'],2),
            f"{amount:.2f}" 
        ])
        
        current_row += 1 

        if current_row == row_limit:

            # Create and draw the table
            table = Table(table_data, colWidths=[1 * cm, 5 * cm, 1.8 * cm, 1.4 * cm, 1.9 * cm, 1.1 * cm,1.7 * cm,1.7 * cm, 2 * cm])

            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.2, 0.2)),  # Light black background
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header text color
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font bold
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),  # Padding for header
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grid for all cells
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Background for data rows
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Data rows font
            ]))


            table.wrapOn(c, width, first_page_table_y)
            table.drawOn(c, margin_left, first_page_table_y - len(table_data) * 18)
            is_first_page = False  # Set flag to False after first page
            row_limit = SUBSEQUENT_PAGE_ROWS  # Increase the row limit for subsequent pages

            table_data = [["S. No", "Item & Description", "HSN/SAC", "Qty", "Rate", "GST%", "CGST", "SGST", "Amount"]]
            current_row = 0  # Reset row count
            c.showPage()  # Create a new page

    # Draw any remaining items if they exist
    if current_row > 0:
        
        table = Table(table_data, colWidths=[1 * cm, 5 * cm, 1.8 * cm, 1.4 * cm, 1.9 * cm, 1.1 * cm,1.7 * cm,1.7 * cm, 2 * cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.2, 0.2)),  # Light black background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font bold
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),  # Padding for header
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grid for all cells
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Background for data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Data rows font
        ]))
        
        # Draw the remaining table on the correct page position
        if is_first_page:
            table.wrapOn(c, width, first_page_table_y)
            table.drawOn(c, margin_left, first_page_table_y - len(table_data) * 18)
            
        else:
            table.wrapOn(c, width, subsequent_page_table_y)
            table.drawOn(c, margin_left, subsequent_page_table_y - len(table_data) * 18)

        subtotal_y_position = (first_page_table_y if is_first_page else subsequent_page_table_y) - len(table_data) * 18 - 20
        c.setFont("Helvetica", 10)
        c.drawString(margin_left + 5.5 * inch, subtotal_y_position, f"Total:  {total_amount:.2f}")


def create_challan_pdf(data, items, c):
    width, height = A4
 

    margin_left = 2 * cm
    margin_bottom = 1.5 * cm

    logo_path = '/home/thrymr/Downloads/hesa_logo.png'
   
    try:
        logo = ImageReader(logo_path)
        if logo:
            c.drawImage(logo, margin_left, height - 4.5 * cm, width=6.5 * cm, height=3 * cm, preserveAspectRatio=True)
    except Exception as e:
        print(f"Error loading logo: {e}")
 
    # Company Information
    c.setFont("Helvetica-Bold", 10)
    company_info_y = height - 5 * cm
    c.drawString(margin_left, company_info_y, data['Purchaser'])
    c.setFont("Helvetica", 9)
    # c.drawString(margin_left, company_info_y - 0.3 * cm, data['Vendor State'])

    mapping = {
        # ("Hesa enterprises Private Limited", "Andhra Pradesh"): ("39-11-45, Bank Street, Muralinagar, Visakhapatnam, Andhra Pradesh, 530007", "37AAFCR8177F1ZZ"),
        # ("Hesa enterprises Private Limited", "Bihar"): ("B/124, Kankarbagh, Kankar Bagh Road, Patna, Bihar, 800020", "10AAFCR8177F1ZF"),
        # ("Hesa enterprises Private Limited", "Telangana"): ("Plot No 136, 1-4-158/136, Kapra, Saipuricolony, Hyderabad, Telangana, 500094", "36AAFCR8177F1Z1"),
        # ("Hesa enterprises Private Limited", "Karnataka"): ("H. No 2-90B/68/57, Sedam Road, Near Gurkul Vidya Mandir, Om Nagar, Kalaburagi, Kalaburagi, Karnataka, 585105", "29AAFCR8177F1ZW"),
        # ("Hesa enterprises Private Limited", "Odisha"): ("747/1170, PARAGON, Belagacchia, Khordha, Odisha, 754005", "21AAFCR8177F1ZC"),
        # ("Hesa enterprises Private Limited", "Jharkhand"): ("flat No-C, First Floor, Harmu Housing Colony, Ranchi Doranda, J harkhand, 834002", "Unregistered"),
        # ("Hesa enterprises Private Limited", "Tamil Nadu"): ("F28, AV HI FIELD APARTMENT, Visuvasapuram, Coimbatore, 641035", "Unregistered"),
        # ("Hesa enterprises Private Limited", "Haryana"): ("0, ADRASH NAGAR, Narnaul, Mahendragarh, Haryana, 123001", "06AAFCH9926E1ZH"),
        # ("Hesa enterprises Private Limited", "Maharashtra"): ("FIRST FLOOR, 101, SH 77, Near Latur Urban Bank, Latur, Latur, Maharashtra, 413512", "27AAFCH9722G1ZF"),

        # ("Hesa Enterprises Private Limited", "Andhra Pradesh"): ("39-11-45, Bank Street, Muralinagar, Visakhapatnam, Andhra Pradesh, 530007", "37AAFCR8177F1ZZ"),
        # ("Hesa Enterprises Private Limited", "Bihar"): ("B/124, Kankarbagh, Kankar Bagh Road, Patna, Bihar, 800020", "10AAFCR8177F1ZF"),
        # ("Hesa Enterprises Private Limited", "Telangana"): ("Plot No 136, 1-4-158/136, Kapra, Saipuricolony, Hyderabad, Telangana, 500094", "36AAFCR8177F1Z1"),
        # ("Hesa Enterprises Private Limited", "Karnataka"): ("H. No 2-90B/68/57, Sedam Road, Near Gurkul Vidya Mandir, Om Nagar, Kalaburagi, Kalaburagi, Karnataka, 585105", "29AAFCR8177F1ZW"),
        # ("Hesa Enterprises Private Limited", "Odisha"): ("747/1170, PARAGON, Belagacchia, Khordha, Odisha, 754005", "21AAFCR8177F1ZC"),
        # ("Hesa Enterprises Private Limited", "Jharkhand"): ("flat No-C, First Floor, Harmu Housing Colony, Ranchi Doranda, Jharkhand, 834002", "Unregistered"),
        # ("Hesa Enterprises Private Limited", "Tamil Nadu"): ("F28, AV HI FIELD APARTMENT, Visuvasapuram, Coimbatore, 641035", "Unregistered"),
        # ("Hesa Enterprises Private Limited", "Haryana"): ("0, ADRASH NAGAR, Narnaul, Mahendragarh, Haryana, 123001", "06AAFCH9926E1ZH"),
        # ("Hesa Enterprises Private Limited", "Maharashtra"): ("FIRST FLOOR, 101, SH 77, Near Latur Urban Bank, Latur, Latur, Maharashtra, 413512", "27AAFCH9722G1ZF"),
        

        ("Hesa Agritech Private Limited", "haryana"): ("0, Adarsh Nagar, Narnaul, Mahendragarh, Haryana, 123001", "06AAFCH9722G1ZJ"),
        ("Hesa Agritech Private Limited", "andhra pradesh"): ("39-11-45, Bank Street, Muralinagar, Visakhapatnam, Andhra Pradesh, 530007", "37AAFCH9722G1ZE"),
        ("Hesa Agritech Private Limited", "maharashtra"): ("FIRST FLOOR, 101, SH 77, Near Latur Urban Bank, Latur, Latur, Maharashtra, 413512", "27AAFCH9722G1ZF"),
        ("Hesa Agritech Private Limited", "Tamil Nadu"): ("H.No 2/361, Maryiyamman Kovil Street, Minnur, Tirupathur, Tamil Nadu, 635807", "33AAFCH9722G1ZM"),
        ("Hesa Agritech Private Limited", "Odisha"): ("747/1170, PARAGON, Belagacchia, Khordha, Odisha, 754005", "21AAFCH9722G1ZR"),
        ("Hesa Agritech Private Limited", "telangana"): ("Plot No 136, 1-4-158/136, Kapra, Saipuricolony, Hyderabad, Telangana, 500094", "36AAFCH9722G1ZG"),
        ("Hesa Agritech Private Limited", "jharkhand"): ("flat No-C, First Floor, Harmu Housing Colony, Ranchi Doranda, Jharkhand, 834002", "Unregistered"),
        ("Hesa Agritech Private Limited", "bihar"): ("B/124, Kankarbagh, Kankar Bagh Road, Patna, Bihar, 800020", "10AAFCR8177F1ZF"),
        ("Hesa Agritech Private Limited", "karnataka"): ("#318, Komarla Brigade Vista, Gowdanpalya Main Road, 3rd floor, Uttarahalli, Bengaluru, Karnataka, 560061", "Unregistered"),
        ("Hesa Agritech Private Limited", "madhya pradesh"): ("Ward No 10, Badnawar, Near Shaskiya government school, Borali, Dhar, Madhya Pradesh,454660","23AAFCH9926E1ZL"),
        
        
        
        ("Hesa Consumer Products Private Limited", "Odisha"): ("747/1170, PARAGON, Belagacchia, Khordha, Odisha, 754005", "21AAFCH9926E1ZP"),
        ("Hesa Consumer Products Private Limited", "andhra pradesh"): ("39-11-45, bank street, Muralinagar, Visakhapatnam, Visakhapatnam, Andhra Pradesh, 530007", "37AAFCH9926E1ZC"),
        ("Hesa Consumer Products Private Limited", "telangana"): ("1-4-158/136, Saipuri Colony, Kapra,Sainikpuri, Sainikpuri, Hyderabad, Telangana, 500094", "36AAFCH9926E1ZE"),
        ("Hesa Consumer Products Private Limited", "jharkhand"): ("flat No-C, First Floor, Harmu Housing Colony, Ranchi Doranda, Jharkhand, 834002", "Unregistered"),
        ("Hesa Consumer Products Private Limited", "Tamil Nadu"): ("H. No 2/361, Mariyammam Kovil Street, Ambur Taluk, Minnur, Tirupathur, Tamil Nadu, 635807", "33AAFCH9926E1ZK"),
        ("Hesa Consumer Products Private Limited", "maharashtra"): ("4TH, R-2/2418/7A, SURVEY NO 259, Latur Industrial Area Additional, Latur, Maharashtra, 413531", "27AAFCH9926E1ZD"),
        ("Hesa Consumer Products Private Limited", "Haryana"): ("0, ADRASH NAGAR, Narnaul, Mahendragarh, Haryana, 123001", "06AAFCH9926E1ZH"),
        ("Hesa Consumer Products Private Limited", "bihar"): ("Ground floor, vijaya rajit singh Bhavan, Bampali, Bhojpur, Bihar, 802312", "10AAFCH9926E1ZS"),
        ("Hesa Consumer Products Private Limited", "karnataka"): ("A3, Gangotri apartments, 3rd A Block, Gokulam, Mysore, Karnataka", "Unregistered"),
        ("Hesa Consumer Products Private Limited", "madhya pradesh"): ("Ward No 10, Badnawar, Near Shaskiya government school, Borali, Dhar, Madhya Pradesh,454660","23AAFCH9926E1ZL")
        
    }

    c.setFont("Helvetica-Bold", 9)
    company_info_y = height - 5 * cm
    # Normalize the input to lowercase
    normalized_purchaser = data['Purchaser'].lower()
    normalized_vendor_state = data['Vendor_State'].lower()

    # Create a case-insensitive lookup dictionary but retain original mapping values
    normalized_mapping = {
        (key[0].lower(), key[1].lower()): value for key, value in mapping.items()
    }

    # Retrieve the original value using the normalized keys
    company_address, gstin = normalized_mapping.get(
        (normalized_purchaser, normalized_vendor_state), 
        ("Address not found", "GSTIN not found")
    )

    # Output remains the same as in the original mapping


    #c.drawString(margin_left, company_info_y, purchaser)
    c.setFont("Helvetica", 9)

    c.drawString(margin_left, company_info_y - 60, f"GSTIN: {gstin}")

    if isinstance(company_address, str):
        company_address = company_address.split(', ')
    else:
        company_address = ['']  
 
    # Split the address into up to four lines
    line1 = ", ".join(company_address[:2]) if len(company_address) >= 1 else ""
    line2 = company_address[2] if len(company_address) > 2 else ""
    line3 = company_address[3] if len(company_address) > 3 else ""
    line4 = ", ".join(company_address[4:]) if len(company_address) > 4 else ""

    # Draw each line on the canvas
    c.drawString(margin_left, company_info_y - 12, line1)
    c.drawString(margin_left, company_info_y - 24, line2)
    c.drawString(margin_left, company_info_y - 36, line3)
    c.drawString(margin_left, company_info_y - 48, line4)
 
    
    customer_info_y = company_info_y - 3 * cm

    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin_left, customer_info_y, "Address")

    c.setFont("Helvetica", 9)
    c.drawString(margin_left, customer_info_y - 12, f"{data['Name']}")
    customer_location = data.get('Address', '')
    

    if isinstance(customer_location, str):
        # customer_location_parts = customer_location.split(',')
        # # Assign first two parts to line1 and line2
        # line1 = customer_location_parts[0][:60] if len(customer_location_parts) > 0 else ''
        # line2 = customer_location_parts[1][:60] if len(customer_location_parts) > 1 else ''
        # # Combine remaining parts for line3
        # line3 = ', '.join(customer_location_parts[2:])[:60] if len(customer_location_parts) > 2 else ''
        import textwrap

        customer_location = data.get('Address', '')
        
        wrapped_lines = textwrap.wrap(customer_location, width=60)

        line1 = wrapped_lines[0] if len(wrapped_lines) > 0 else ''
        line2 = wrapped_lines[1] if len(wrapped_lines) > 1 else ''
        line3 = wrapped_lines[2] if len(wrapped_lines) > 2 else ''

        
        # Draw lines on the PDF
        if line1:
            c.drawString(margin_left, customer_info_y - 24, line1)
        if line2:
            c.drawString(margin_left, customer_info_y - 36, line2)
        c.drawString(margin_left, customer_info_y - 48, f"{data.get('Vendor_State')}, {data.get('Vendor_District')}")
    else:
        c.drawString(margin_left, customer_info_y - 24, f"{data.get('Vendor_State', '')}, {data.get('Vendor_District', '')}")
        c.drawString(margin_left, customer_info_y - 48, f"{data.get('Vendor_State', '')}, {data.get('Vendor_District', '')}")
    c.drawString(margin_left, customer_info_y - 60, f"GSTIN: Unregistered")




    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_left, customer_info_y - 3.2 * cm, f"Deliver To")
    c.setFont("Helvetica", 10)
#--------------------------------------------------------------------------------------------------------------------------   
    # purchaser = data['Purchaser']
    # vendor_state = data['Vendor State']

    # company_address, gstin = mapping.get((purchaser, vendor_state), ("Address not found", "GSTIN not found"))
    # Create a case-insensitive lookup dictionary but retain original mapping values
    c.setFont("Helvetica-Bold", 9)
    company_info_y = height - 5 * cm
    # Normalize the input to lowercase
    normalized_purchaser = data['Purchaser'].lower()
    normalized_vendor_state = data['Vendor_State'].lower()

    # Create a case-insensitive lookup dictionary but retain original mapping values
    normalized_mapping = {
        (key[0].lower(), key[1].lower()): value for key, value in mapping.items()
    }

    # Retrieve the original value using the normalized keys
    company_address, gstin = normalized_mapping.get(
        (normalized_purchaser, normalized_vendor_state), 
        ("Address not found", "GSTIN not found")
    )
    c.setFont("Helvetica", 9)

    if isinstance(company_address, str):
        company_address = company_address.split(', ')
    else:
        company_address = ['']  

    # Prepare lines for address, ensuring up to 4 lines can be utilized
    line1 = company_address[0] if len(company_address) > 0 else ""
    line2 = company_address[1] if len(company_address) > 1 else ""
    line3 = company_address[2] if len(company_address) > 2 else ""
    line4 = ", ".join(company_address[3:]) if len(company_address) > 3 else ""
    
    c.drawString(margin_left, company_info_y - 6.6 * cm,f"{data['Hesaathi_Code']}")

    # Draw each line on the canvas at appropriate Y positions
    c.drawString(margin_left, company_info_y - 7 * cm, line1)
    c.drawString(margin_left, company_info_y - 7.4 * cm, line2)
    c.drawString(margin_left, company_info_y - 7.8 * cm, line3)
    c.drawString(margin_left, company_info_y - 8.2 * cm, line4)

#--------------------------------------------------------------------------------------------------------------------
    c.setFont("Helvetica", 28)
    c.drawString(width - 8 * cm, height - 2.5 * cm, "Purchase Order")
    
    c.setFont("Helvetica", 10)
    c.drawString( margin_left + 5.4 * inch, height - 3 * cm, f"# {data['Po_Number']}")

    if isinstance(data['Date'], pd.Timestamp):
        challan_date_str = data['Date'].strftime('%d-%m-%Y')
    else:
        challan_date_str = str(data['Date']) 
 
    c.drawString( margin_left + 5.5 * inch, company_info_y - 8.2 * cm ,f"Date: {challan_date_str}")

    c.setStrokeColor(colors.black) 
    c.setLineWidth(1.5)
    middle_b = 28 * cm
    #c.line(0, middle_b, width - 0, middle_b) 

    first_page_table_y = middle_b - 4.7 * inch
    subsequent_page_table_y = middle_b
    
    draw_product_table(c, items, margin_left, first_page_table_y, subsequent_page_table_y, width)

    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin_left, margin_bottom + 2.5 * cm, "Terms and Conditions")
    c.setFont("Helvetica", 9)
    c.drawString(margin_left, margin_bottom + 2 * cm, "1. This is a computer-generated document, Signature is not required")
    c.drawString(margin_left, margin_bottom + 1.5 * cm, "2. This PO is valid for 7 days from PO date")
    c.drawString(margin_left, margin_bottom + 1 * cm, "3. PO number should be mentioned on the invoice")
    c.drawString(margin_left, margin_bottom + 0.5 * cm, "4. Invoice should carry the same rate, quantity and SKUs as per PO")
    c.drawString(margin_left, margin_bottom , "5. Payment terms as per the agreement")
 
def generate_challans_from_excel(excel_file, output_pdf):
    df = pd.read_excel(excel_file)
    grouped = df.groupby('Po_Number')
    c = canvas.Canvas(output_pdf, pagesize=A4)
 
    for delivery_challan, group in grouped:
        first_row = group.iloc[0]
        last_row = group.iloc[-1]
 
        items = group[['Product_Name', 'Hsn_Code','Product_Qty', "Net_Price_Pu", 'GST_Rate', 'Cgst', 'Sgst']].to_dict('records')
 
        data = last_row.to_dict()
        create_challan_pdf(data, items, c)
        c.showPage()
 
    c.save()
 
    print(f"PDF generated as {output_pdf}")

excel_file = '/home/thrymr/Downloads/feb_with_vendors.xlsx'

output_pdf = '/home/thrymr/Downloads/PO_feb(24-25)_pdf.pdf'
 
generate_challans_from_excel(excel_file, output_pdf)

