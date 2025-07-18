import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm , inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
import os

# Constants for row limits
FIRST_PAGE_ROWS = 20
SUBSEQUENT_PAGE_ROWS = 35

# Function to create the product details table
def draw_product_table(c, items, margin_left, first_page_table_y, subsequent_page_table_y, width):
    table_data = [["S. No", "Item & Description", "HSN/SAC", "Qty", "MCP"]]  # Header
    current_row = 0  # To track the current row in pagination
    is_first_page = True  # Flag to check if it's the first page
    
    c.setStrokeColor(colors.black)         
    c.setLineWidth(1.5)
    middle_b = 28 * cm
    # c.line(0, middle_b, width - 0, middle_b) 

    first_page_table_y = middle_b - 4 * inch
    subsequent_page_table_y = middle_b 
    
    row_limit = FIRST_PAGE_ROWS  # Start with first page row limit
    
    for i, item in enumerate(items, start=1):
        product_name = item['Product Name'][:35]  # Truncate product name to 40 characters
        if len(item['Product Name']) > 35:
            product_name += "..."  # Append ellipsis if truncated
        table_data.append([
            str(i),
            product_name,
            item['HSN/SAC'],
            round(item['Quantity'], 2),
            f"{float(item['MCP']):.2f}"
        ])
        
        current_row += 1  # Increment the current row count

        # If the number of rows reaches the page row limit, draw the table
        if current_row == row_limit:
            # Create and draw the table
            table = Table(table_data, colWidths=[1 * cm, 7 * cm, 3 * cm, 3 * cm, 3 * cm])
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
            
            # Draw the table on the first page
            if is_first_page:
                table.wrapOn(c, width, first_page_table_y)
                table.drawOn(c, margin_left, first_page_table_y - len(table_data) * 18)
                is_first_page = False  # Set flag to False after first page
                row_limit = SUBSEQUENT_PAGE_ROWS  # Increase the row limit for subsequent pages
            else:
                # For subsequent pages, use a different Y-position
                table.wrapOn(c, width, subsequent_page_table_y)
                table.drawOn(c, margin_left, subsequent_page_table_y - len(table_data) * 18)
            
            # Reset for next page
            table_data = [["S. No", "Item & Description", "HSN/SAC", "Qty", "MCP"]]  # Reset table data
            current_row = 0  # Reset row count
            c.showPage()  # Create a new page

    # Draw any remaining items if they exist
    if current_row > 0:
        table = Table(table_data, colWidths=[1 * cm, 7 * cm, 3 * cm, 3 * cm, 3 * cm])
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

def create_challan_pdf(data, items, c):
    width, height = A4
 
    # Set margins
    margin_left = 2 * cm
    margin_bottom = 3 * cm

    # Company logo (adjust image path to your actual file)
    logo_path = '/home/thrymr/Downloads/hesa_logo.png'
   
    try:
        logo = ImageReader(logo_path)
        # Check if logo is loaded successfully
        if logo:
            c.drawImage(logo, margin_left, height - 4.5 * cm, width=6.5 * cm, height=3 * cm, preserveAspectRatio=True)
    except Exception as e:
        print(f"Error loading logo: {e}")
 
    # Company Information
    c.setFont("Helvetica-Bold", 10)
    company_info_y = height - 5 * cm
    c.drawString(margin_left, company_info_y, data['Facilitator'])
    c.setFont("Helvetica", 9)
 
    # Check if the value is a valid string before using split
    company_address = data.get('Company Address', '')
    if isinstance(company_address, str):
        company_address = company_address.split(', ')
    else:
        company_address = ['']  # Handle missing or invalid data
 
    if len(company_address) > 2:
        # Join parts into three lines
        line1 = ", ".join(company_address[:2])  # Combines the first two parts
        line2 = ", ".join(company_address[2:-2])  # Combines the middle parts
        line3 = company_address[-2]  # Keeps the second last part as is
 
        c.drawString(margin_left, company_info_y - 12, line1)
        c.drawString(margin_left, company_info_y - 24, line2)
        c.drawString(margin_left, company_info_y - 36, line3)
    else:
        c.drawString(margin_left, company_info_y - 12, company_address[0])
 
    c.drawString(margin_left, company_info_y - 48, f"GSTIN: {data['GSTIN']}")
    c.setFont("Helvetica-Bold", 24)
    c.drawString(width - 5 * cm, height - 2 * cm, "DELIVERY")
    c.drawString(width - 5 * cm, height - 3 * cm, "CHALLAN")
    c.setFont("Helvetica", 10)
    c.drawString(width - 6 * cm, height - 3.5 * cm, f"Delivery Challan# {data['Delivery Challan']}")
    if isinstance(data['Challan Date'], pd.Timestamp):
        challan_date_str = data['Challan Date'].strftime('%d-%m-%Y')
    else:
        challan_date_str = str(data['Challan Date'])  
 
    c.drawString(width - 6.5 * cm, height - 9.5 * cm, f"Challan Date: {challan_date_str}")
    c.drawString(width - 6.5 * cm, height - 10 * cm, f"Challan Type: {data['Challan Type']}")
    c.drawString(width - 6.5 * cm, height - 10.5 * cm, str(data['Hesaathi Code']))
 
    
    customer_info_y = height - 8.5 * cm

    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_left, customer_info_y, "Ship To")
    c.setFont("Helvetica", 9)
    c.drawString(margin_left, customer_info_y - 12, str(data['Customer Name']))

    customer_location = data.get('Customer Address', '')
 
    if isinstance(customer_location, str):

        
        customer_location_parts = customer_location.split(',')  
        if len(customer_location_parts) > 1:
            line1 = customer_location_parts[0][:60]
            line2 = customer_location_parts[1][:60] if len(customer_location_parts) > 1 else ''
            line3 = customer_location_parts[2][:60] if len(customer_location_parts) > 2 else ''
        else:
            line1 = customer_location[:40]
            line2 = customer_location[40:80]  
            line3 = customer_location[80:]  
 
        if line1:
            c.drawString(margin_left, customer_info_y - 32, line1)
        if line2:
            c.drawString(margin_left, customer_info_y - 42, line2)
        if line3:
            c.drawString(margin_left, customer_info_y - 52, line3)
    else:
        c.drawString(margin_left, customer_info_y - 24, "")
 
    c.drawString(margin_left, customer_info_y - 22, str(data['Customer Mobile']))
    c.drawString(margin_left, customer_info_y - 62, str(data['Customer District']))
    c.drawString(margin_left, customer_info_y - 72, str(data['Customer State']))
    c.drawString(margin_left, customer_info_y - 82, f"Place Of Supply: {data['Customer State']}")

    c.setStrokeColor(colors.lightgrey)         #HORIZONTAL LINES margin_a,b,c,....
    c.setLineWidth(1.5)  
    middle_a = 28 * cm
    # c.line(0, middle_a, width - 0, middle_a)                 # ******IMPORTANT **************
 
    table_start_y = middle_a - 10.2 * cm
    first_page_table_y = middle_a 
    subsequent_page_table_y = middle_a 
    
    draw_product_table(c, items, margin_left, first_page_table_y, subsequent_page_table_y, width)
 
    signature_path = '/home/thrymr/Downloads/sir_signature-removebg-preview.png'
   
    try:
        sign = ImageReader(signature_path)
        if sign:
            signature_height = 1.5 * cm
            c.drawImage(sign, margin_left + 1 * cm, margin_bottom,width = 6 * cm,height = signature_height, preserveAspectRatio=True)
    except Exception as f:
        print(f"Error loading logo: {f}")
 
    c.drawString(margin_left, margin_bottom, "Verifier Signature ____________________")
 


# excel_file = '/home/thrymr/Downloads/sales 23-24/ready_Final_Sales_Apr_23 (2).xlsx'


# output_pdf = '/home/thrymr/Downloads/sales 23-24/DC_Apr_23.pdf'

 
# generate_challans_from_excel(excel_file, output_pdf)

# ✅ Updated function: accepts DataFrame, not file path
def generate_challans_from_dataframe(df, output_pdf):
    grouped = df.groupby('Delivery Challan')
    c = canvas.Canvas(output_pdf, pagesize=A4)

    for delivery_challan, group in grouped:
        items = group[['Product Name', 'MCP', 'HSN/SAC', 'Quantity']].to_dict('records')
        data = group.iloc[-1].to_dict()  # Use last row for header info
        create_challan_pdf(data, items, c)
        c.showPage()

    c.save()
    print(f"PDF generated as {output_pdf}")

# 📁 Dictionary with months and list of Excel files
monthly_excel_files = {
    'oct': [
        '/home/thrymr/Downloads/Oct/processed_Sheet1_part1.xlsx',
        '/home/thrymr/Downloads/Oct/processed_Sheet1_part2.xlsx'
    ],
    'nov': [
        '/home/thrymr/Downloads/Nov/processed_Sheet1_part1.xlsx',
        '/home/thrymr/Downloads/Nov/processed_Sheet1_part2.xlsx'
    ]
    # Add more months and files as needed
}

output_dir = '/home/thrymr/Downloads/delivery_challans_24-25(oct-mar)/'
os.makedirs(output_dir, exist_ok=True)

# 🔁 Process each month
for month, file_list in monthly_excel_files.items():
    df_list = [pd.read_excel(file) for file in file_list]
    combined_df = pd.concat(df_list, ignore_index=True)

    output_pdf = os.path.join(output_dir, f'DC_{month.lower()}.pdf')

    # ✅ Use correct function for DataFrame input
    generate_challans_from_dataframe(combined_df, output_pdf)
