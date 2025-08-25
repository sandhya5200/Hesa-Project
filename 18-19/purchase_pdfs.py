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

    first_page_table_y = middle_b - 4 * inch
    subsequent_page_table_y = middle_b

    row_limit = FIRST_PAGE_ROWS  
    total_amount = 0
    for i, item in enumerate(items, start=1):
        product_name = item['Product Name'][:26]  
        if len(item['Product Name']) > 26:
            product_name += ".."  
        hsn = item.get('HSN Code')
        # Calculate individual tax amounts (assuming CGST = SGST = GST Amount / 2)
        gst_amount = float(item['GST Amount'])
        cgst = gst_amount / 2
        sgst = gst_amount / 2
        # Use Gross Total for this line item
        amount = float(item['Gross Total'])
        total_amount += amount  # Add each line item's gross total to get final total  
        table_data.append([
            str(i),
            product_name,
            hsn,
            round(item['Product Qty'], 2),
            f"{float(item['Taxable Value']) / float(item['Product Qty']):.2f}",  # Rate per unit
            item["GST Rate"] * 100,
            round(cgst, 2),
            round(sgst, 2),
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

    logo_path = r"c:\Users\ksand\OneDrive\Pictures\Screenshots\Screenshot 2025-08-23 134435.png"
   
    try:
        logo = ImageReader(logo_path)
        if logo:
            c.drawImage(logo, margin_left, height - 4.5 * cm, width=6.5 * cm, height=3 * cm, preserveAspectRatio=True)
    except Exception as e:
        print(f"Error loading logo: {e}")
 
    # Company Information - SIMPLIFIED
    c.setFont("Helvetica-Bold", 10)
    company_info_y = height - 5 * cm
    c.drawString(margin_left, company_info_y, "RURAL YELLOW TIMES PVT.LTD")
    
    c.setFont("Helvetica", 9)
    # Company address lines
    c.drawString(margin_left, company_info_y - 12, "315, Block I, RV Manyatha Apartments,")
    c.drawString(margin_left, company_info_y - 24, "PJR Enclave Road, Chanda Nagar,")
    c.drawString(margin_left, company_info_y - 36, "Hyderabad - 500 050, Telangana, India.")
    c.drawString(margin_left, company_info_y - 48, "Pan No: AAFCR8177F")
    c.drawString(margin_left, company_info_y - 60, "GS Tax No: 36AAFCR8177F1Z1")
    
    # Vendor Address Section
    customer_info_y = company_info_y - 3 * cm

    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin_left, customer_info_y, "Vendor Address")

    c.setFont("Helvetica", 9)
    c.drawString(margin_left, customer_info_y - 12, f"{data['Name']}")
    
    customer_location = data.get('Address', '')
    
    if isinstance(customer_location, str):
        import textwrap
        wrapped_lines = textwrap.wrap(customer_location, width=60)

        line1 = wrapped_lines[0] if len(wrapped_lines) > 0 else ''
        line2 = wrapped_lines[1] if len(wrapped_lines) > 1 else ''
        line3 = wrapped_lines[2] if len(wrapped_lines) > 2 else ''
        
        # Draw lines on the PDF
        if line1:
            c.drawString(margin_left, customer_info_y - 24, line1)
        if line2:
            c.drawString(margin_left, customer_info_y - 36, line2)
        if line3:
            c.drawString(margin_left, customer_info_y - 48, line3)
        
        c.drawString(margin_left, customer_info_y - 60, f"{data.get('State')}, {data.get('District')}")
    else:
        c.drawString(margin_left, customer_info_y - 24, f"{data.get('State', '')}, {data.get('District', '')}")
    
    c.drawString(margin_left, customer_info_y - 72, f"GSTIN: Unregistered")

    # # Deliver To Section - SIMPLIFIED
    # c.setFont("Helvetica-Bold", 10)
    # c.drawString(margin_left, customer_info_y - 3.2 * cm, f"Deliver To")
    
    # c.setFont("Helvetica", 9)
    # c.drawString(margin_left, company_info_y - 6.6 * cm, f"{data['Hesaathi Code']}")
    
    # # Same deliver to address as company address
    # c.drawString(margin_left, company_info_y - 7 * cm, "315, Block I, RV Manyatha Apartments,")
    # c.drawString(margin_left, company_info_y - 7.4 * cm, "PJR Enclave Road, Chanda Nagar,")
    # c.drawString(margin_left, company_info_y - 7.8 * cm, "Hyderabad - 500 050, Telangana, India.")

    # Purchase Order Header
    c.setFont("Helvetica", 28)
    c.drawString(width - 8 * cm, height - 2.5 * cm, "Purchase Order")
    
    c.setFont("Helvetica", 10)
    c.drawString( margin_left + 5.4 * inch, height - 3 * cm, f"# {data['PO Number']}")

    if isinstance(data['Date'], pd.Timestamp):
        challan_date_str = data['Date'].strftime('%d-%m-%Y')
    else:
        challan_date_str = str(data['Date']) 
 
    c.drawString( margin_left + 5.5 * inch, company_info_y - 6 * cm ,f"Date: {challan_date_str}")

    c.setStrokeColor(colors.black) 
    c.setLineWidth(1.5)
    middle_b = 28 * cm

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
    grouped = df.groupby('PO Number')
    c = canvas.Canvas(output_pdf, pagesize=A4)
 
    for delivery_challan, group in grouped:
        first_row = group.iloc[0]
        last_row = group.iloc[-1]
 
        items = group[['Product Name', 'HSN Code','Product Qty', "Taxable Value", 'GST Rate', 'GST Amount', 'Gross Total']].to_dict('records')
 
        data = last_row.to_dict()
        create_challan_pdf(data, items, c)
        c.showPage()
 
    c.save()
 
    print(f"PDF generated as {output_pdf}")


excel_file = r"c:\Users\ksand\Downloads\purchases 19-20\mar_with_vendors.xlsx"
output_pdf = r"c:\Users\ksand\Downloads\purchases 19-20\mar_purchase_pdf_2019-20.pdf"
generate_challans_from_excel(excel_file, output_pdf)

