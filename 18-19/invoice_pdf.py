# from reportlab.lib.pagesizes import letter, A4
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from reportlab.lib import colors
# from reportlab.pdfgen import canvas
# from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
# import pandas as pd
# import os
# from datetime import datetime

# def read_excel_data():
#     """Read data from Excel file"""
#     excel_path = "/home/thrymr/Downloads/split_taxable_random.xlsx"
#     try:
#         df = pd.read_excel(excel_path, sheet_name="Sheet1")
#         return df
#     except Exception as e:
#         print(f"Error reading Excel file: {str(e)}")
#         return None

# def format_date(date_str):
#     """Format date string"""
#     try:
#         if pd.isna(date_str):
#             return "N/A"
#         # Handle different date formats
#         if isinstance(date_str, str):
#             return date_str
#         else:
#             return str(date_str)
#     except:
#         return "N/A"

# def format_address(address):
#     """Split address into two parts for better formatting"""
#     if pd.isna(address) or address == "":
#         return "N/A", ""
    
#     address_str = str(address)
#     # Split address roughly in the middle at a comma or space
#     parts = address_str.split(',')
#     if len(parts) > 2:
#         mid = len(parts) // 2
#         part1 = ','.join(parts[:mid])
#         part2 = ','.join(parts[mid:])
#         return part1, part2
#     else:
#         return address_str, ""

# def create_invoice_page(invoice_data, styles, logo_path):
#     """Create elements for a single invoice page"""
#     elements = []
    
#     # Custom styles
#     title_style = ParagraphStyle(
#         'CustomTitle',
#         parent=styles['Heading1'],
#         fontSize=24,
#         spaceAfter=20,
#         alignment=TA_RIGHT
#     )
    
#     header_style = ParagraphStyle(
#         'HeaderStyle',
#         parent=styles['Normal'],
#         fontSize=10,
#         spaceAfter=6,
#         alignment=TA_LEFT
#     )
    
#     bold_style = ParagraphStyle(
#         'BoldStyle',
#         parent=styles['Normal'],
#         fontSize=10,
#         spaceAfter=6,
#         alignment=TA_LEFT,
#         fontName='Helvetica-Bold'
#     )
    
#     # Get invoice details from first row
#     first_row = invoice_data.iloc[0]
#     invoice_no = str(first_row.get('Invoice No', 'N/A'))
#     date = format_date(first_row.get('Date', 'N/A'))
#     customer_name = str(first_row.get('Customer Name', 'N/A'))
#     inv = str(first_row.get('GSTIN/UIN of Recipient', 'N/A'))
#     customer_address = str(first_row.get('Customer Address', 'N/A'))
    
#     # Header with logo and invoice title
#     if os.path.exists(logo_path):
#         logo = Image(logo_path, width=2*inch, height=0.8*inch)
#         header_table = Table([
#             [logo, Paragraph("INVOICE", title_style)]
#         ], colWidths=[5*inch, 2*inch])
#     else:
#         logo_text = Paragraph("Rural <b>Yellow</b>", ParagraphStyle(
#             'LogoStyle',
#             parent=styles['Normal'],
#             fontSize=16,
#             fontName='Helvetica-Bold',
#             textColor=colors.black
#         ))
#         header_table = Table([
#             [logo_text, Paragraph("INVOICE", title_style)]
#         ], colWidths=[5*inch, 2*inch])
    
#     header_table.setStyle(TableStyle([
#         ('ALIGN', (0, 0), (0, 0), 'LEFT'),
#         ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
#         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
#     ]))
    
#     elements.append(header_table)
#     elements.append(Spacer(1, 20))
    
#     # Company details and invoice info
#     company_info = """
#     <b>RURAL YELLOW TIMES PVT.LTD</b><br/>
#     315, Block I,<br/>
#     RV Manyatha Apartments,<br/>
#     PJR Enclave Road, Chanda Nagar,<br/>
#     Hyderabad - 500 050,<br/>
#     Telangana, India.<br/>
#     Pan No: AAFCR8177F<br/>
#     GS Tax No: 36AAFCR8177F1Z1
#     """
    
#     invoice_info = f"""
#     <br/><br/><br/>
#     TAX INVOICE NO#: {invoice_no}<br/>
#     DATE: {date}
#     """
    
#     info_table = Table([
#         [Paragraph(company_info, header_style), Paragraph(invoice_info, header_style)]
#     ], colWidths=[5*inch, 2*inch])
    
#     info_table.setStyle(TableStyle([
#         ('ALIGN', (0, 0), (0, 0), 'LEFT'),
#         ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
#         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#     ]))
    
#     elements.append(info_table)
#     elements.append(Spacer(1, 20))
    
#     # Format customer address
#     addr_part1, addr_part2 = format_address(customer_address)
    
#     # To section with customer details
#     # to_info = f"""
#     # <b>To</b><br/>
#     # {customer_name}<br/>
#     # {addr_part1}<br/>
#     # {addr_part2 if addr_part2 else ''}<br/>
#     # GSTIN: {inv}<br/>
#     # """
#     # GSTIN: {inv}<br/>

#     # elements.append(Paragraph(to_info, header_style))
#     elements.append(Spacer(1, 20))
    
#     # Create invoice table with products
#     table_data = [['S.NO', 'DESCRIPTION', 'HSN/SAC', 'QTY', 'RATE', 'TAX AMT', 'GST%', 'CGST', 'SGST', 'TOTAL']]
    
#     total_taxable = 0
#     total_cgst = 0
#     total_sgst = 0
#     total_amount = 0
    
#     for idx, row in invoice_data.iterrows():
#         s_no = len(table_data)  # Serial number
#         product_name = str(row.get('Product Name', 'N/A'))
#         hsn_sac = str(row.get('HSN/SAC', 'N/A'))
#         quantity = row.get('Quantity', 0)
#         rate = row.get('Rate', 0)
#         taxable_value = row.get('Taxable Value', 0)
#         gst_rate = row.get('gst_rate', 0)
#         cgst = row.get('cgst', 0)
#         sgst = row.get('sgst', 0)
#         total = row.get('Total', 0)
        
#         # Add to totals
#         total_taxable += taxable_value
#         total_cgst += cgst
#         total_sgst += sgst
#         total_amount += total
        
#         table_data.append([
#             str(s_no),
#             product_name,
#             hsn_sac,
#             str(quantity),
#             f"{rate:.2f}",
#             f"{taxable_value:.2f}",
#             f"{gst_rate}%",
#             f"{cgst:.2f}",
#             f"{sgst:.2f}",
#             f"{total:.2f}"
#         ])
    
#     # Add total row
#     table_data.append([
#         '', 'TOTAL', '', '', '', 
#         f"{total_taxable:.2f}", '', 
#         f"{total_cgst:.2f}", 
#         f"{total_sgst:.2f}", 
#         f"{total_amount:.2f}"
#     ])
    
#     # Create table
#     invoice_table = Table(table_data, colWidths=[
#         0.4*inch,  # S.NO
#         2.0*inch,  # DESCRIPTION
#         0.6*inch,  # HSN/SAC
#         0.4*inch,  # QTY
#         0.6*inch,  # RATE
#         0.8*inch,  # TAXABLE AMT
#         0.5*inch,  # GST%
#         0.6*inch,  # CGST
#         0.6*inch,  # SGST
#         0.6*inch   # TOTAL
#     ])
    
#     invoice_table.setStyle(TableStyle([
#         # Header row
#         ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, 0), 8),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        
#         # Data rows
#         ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
#         ('FONTSIZE', (0, 1), (-1, -2), 7),
#         ('ALIGN', (1, 1), (1, -2), 'LEFT'),    # Description column left aligned
#         ('ALIGN', (4, 1), (-1, -2), 'RIGHT'),  # Rate, amounts right aligned
        
#         # Total row formatting
#         ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, -1), (-1, -1), 8),
#         ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
#         ('ALIGN', (4, -1), (-1, -1), 'RIGHT'),  # Total row amounts right aligned
        
#         # Grid
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
#         # Padding
#         ('TOPPADDING', (0, 0), (-1, -1), 4),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
#         ('LEFTPADDING', (0, 0), (-1, -1), 3),
#         ('RIGHTPADDING', (0, 0), (-1, -1), 3),
#     ]))
    
#     elements.append(invoice_table)
#     elements.append(Spacer(1, 20))
    
#     # Terms and conditions
#     terms_title = Paragraph("<b>TERMS AND CONDITIONS</b>", bold_style)
#     elements.append(terms_title)
#     elements.append(Spacer(1, 10))
    
#     terms_text = """
#     1. Please Remit Payment to<br/>
#     &nbsp;&nbsp;&nbsp;&nbsp;Bank Details:<br/>
#     &nbsp;&nbsp;&nbsp;&nbsp;• Account Name: Rural Yellow Times Pvt Ltd<br/>
#     &nbsp;&nbsp;&nbsp;&nbsp;• Account No: 23902560000097<br/>
#     &nbsp;&nbsp;&nbsp;&nbsp;• Bank Name: HDFC Bank, Madeenaguda Branch, Hyderabad<br/>
#     &nbsp;&nbsp;&nbsp;&nbsp;• Bank IFSC Code: HDFC0002390<br/><br/>
#     2. Payment Terms - 100% Due Now<br/><br/>
#     3. This is a digitally generated invoice and does not require a physical stamp or signature.<br/><br/>
#     <b>Thank you for your business!</b>
#     """
    
#     elements.append(Paragraph(terms_text, header_style))
    
#     return elements

# def create_invoices():
#     # Read Excel data
#     df = read_excel_data()
#     if df is None:
#         print("Failed to read Excel data")
#         return
    
#     # Output path and logo path
#     output_path = "/home/thrymr/Downloads/SET2igst.pdf"
#     logo_path = "/home/thrymr/Downloads/rural_yellow_logo.png"
    
#     # Create the PDF document
#     doc = SimpleDocTemplate(
#         output_path,
#         pagesize=A4,
#         rightMargin=40,
#         leftMargin=40,
#         topMargin=40,
#         bottomMargin=40
#     )
    
#     # Container for all elements
#     all_elements = []
    
#     # Get styles
#     styles = getSampleStyleSheet()
    
#     # Group data by Invoice No
#     invoice_groups = df.groupby('Invoice No')
    
#     print(f"Found {len(invoice_groups)} unique invoices")
    
#     # Process each invoice
#     for invoice_no, invoice_data in invoice_groups:
#         print(f"Processing invoice: {invoice_no}")
        
#         # Create elements for this invoice
#         invoice_elements = create_invoice_page(invoice_data, styles, logo_path)
        
#         # Add to all elements
#         all_elements.extend(invoice_elements)
        
#         # Add page break except for the last invoice
#         if invoice_no != list(invoice_groups.groups.keys())[-1]:
#             all_elements.append(PageBreak())
    
#     # Build PDF
#     try:
#         doc.build(all_elements)
#         print(f"All invoices PDF generated successfully at: {output_path}")
#         print(f"Total pages: {len(invoice_groups)}")
#     except Exception as e:
#         print(f"Error generating PDF: {str(e)}")

# if __name__ == "__main__":
#     create_invoices()

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
import pandas as pd
import os
from datetime import datetime

def read_excel_data():
    """Read data from Excel file"""
    excel_path = "/home/thrymr/Downloads/split_taxable_random.xlsx"
    try:
        df = pd.read_excel(excel_path, sheet_name="Sheet1")
        return df
    except Exception as e:
        print(f"Error reading Excel file: {str(e)}")
        return None

def format_date(date_str):
    """Format date string"""
    try:
        if pd.isna(date_str):
            return "N/A"
        # Handle different date formats
        if isinstance(date_str, str):
            return date_str
        else:
            return str(date_str)
    except:
        return "N/A"

def format_address(address):
    """Split address into two parts for better formatting"""
    if pd.isna(address) or address == "":
        return "N/A", ""
    
    address_str = str(address)
    # Split address roughly in the middle at a comma or space
    parts = address_str.split(',')
    if len(parts) > 2:
        mid = len(parts) // 2
        part1 = ','.join(parts[:mid])
        part2 = ','.join(parts[mid:])
        return part1, part2
    else:
        return address_str, ""

def create_invoice_page(invoice_data, styles, logo_path):
    """Create elements for a single invoice page"""
    elements = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=20,
        alignment=TA_RIGHT
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    # Get invoice details from first row
    first_row = invoice_data.iloc[0]
    invoice_no = str(first_row.get('Invoice No', 'N/A'))
    date = format_date(first_row.get('Date', 'N/A'))
    customer_name = str(first_row.get('Customer Name', 'N/A'))
    inv = str(first_row.get('GSTIN/UIN of Recipient', 'N/A'))
    customer_address = str(first_row.get('Customer Address', 'N/A'))
    
    # Header with logo and invoice title
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2*inch, height=0.8*inch)
        header_table = Table([
            [logo, Paragraph("INVOICE", title_style)]
        ], colWidths=[5*inch, 2*inch])
    else:
        logo_text = Paragraph("Rural <b>Yellow</b>", ParagraphStyle(
            'LogoStyle',
            parent=styles['Normal'],
            fontSize=16,
            fontName='Helvetica-Bold',
            textColor=colors.black
        ))
        header_table = Table([
            [logo_text, Paragraph("INVOICE", title_style)]
        ], colWidths=[5*inch, 2*inch])
    
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 20))
    
    # Company details and invoice info
    company_info = """
    <b>RURAL YELLOW TIMES PVT.LTD</b><br/>
    315, Block I,<br/>
    RV Manyatha Apartments,<br/>
    PJR Enclave Road, Chanda Nagar,<br/>
    Hyderabad - 500 050,<br/>
    Telangana, India.<br/>
    Pan No: AAFCR8177F<br/>
    GS Tax No: 36AAFCR8177F1Z1
    """
    
    invoice_info = f"""
    <br/><br/><br/>
    TAX INVOICE NO#: {invoice_no}<br/>
    DATE: {date}
    """
    
    info_table = Table([
        [Paragraph(company_info, header_style), Paragraph(invoice_info, header_style)]
    ], colWidths=[5*inch, 2*inch])
    
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # Format customer address
    addr_part1, addr_part2 = format_address(customer_address)
    
    # To section with customer details
    # to_info = f"""
    # <b>To</b><br/>
    # {customer_name}<br/>
    # {addr_part1}<br/>
    # {addr_part2 if addr_part2 else ''}<br/>
    # GSTIN: {inv}<br/>
    # """
    # GSTIN: {inv}<br/>

    # elements.append(Paragraph(to_info, header_style))
    elements.append(Spacer(1, 20))
    
    # Create invoice table with products
    table_data = [['S.NO', 'DESCRIPTION', 'HSN/SAC', 'QTY', 'RATE', 'TAX AMT', 'GST%', 'IGST', 'TOTAL']]
    
    total_taxable = 0
    total_cgst = 0
    # total_sgst = 0
    total_amount = 0
    
    for idx, row in invoice_data.iterrows():
        s_no = len(table_data)  # Serial number
        product_name = str(row.get('Product Name', 'N/A'))
        hsn_sac = str(row.get('HSN/SAC', 'N/A'))
        quantity = row.get('Quantity', 0)
        rate = row.get('Rate', 0)
        taxable_value = row.get('Taxable Value', 0)
        gst_rate = row.get('gst_rate', 0)
        cgst = row.get('igst', 0)
        # sgst = row.get('sgst', 0)
        total = row.get('Total', 0)
        
        # Add to totals
        total_taxable += taxable_value
        total_cgst += cgst
        # total_sgst += sgst
        total_amount += total
        
        table_data.append([
            str(s_no),
            product_name,
            hsn_sac,
            str(quantity),
            f"{rate:.2f}",
            f"{taxable_value:.2f}",
            f"{gst_rate}%",
            f"{cgst:.2f}",
            # f"{sgst:.2f}",
            f"{total:.2f}"
        ])
    
    # Add total row
    table_data.append([
        '', 'TOTAL', '', '', '', 
        f"{total_taxable:.2f}", '', 
        f"{total_cgst:.2f}", 
        # f"{total_sgst:.2f}", 
        f"{total_amount:.2f}"
    ])
    
    # Create table
    invoice_table = Table(table_data, colWidths=[
        0.4*inch,  # S.NO
        2.0*inch,  # DESCRIPTION
        0.6*inch,  # HSN/SAC
        0.4*inch,  # QTY
        0.6*inch,  # RATE
        0.8*inch,  # TAXABLE AMT
        0.5*inch,  # GST%
        0.6*inch,  # CGST
        # 0.6*inch,  # SGST
        0.6*inch   # TOTAL
    ])
    
    invoice_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 7),
        ('ALIGN', (1, 1), (1, -2), 'LEFT'),    # Description column left aligned
        ('ALIGN', (4, 1), (-1, -2), 'RIGHT'),  # Rate, amounts right aligned
        
        # Total row formatting
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 8),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('ALIGN', (4, -1), (-1, -1), 'RIGHT'),  # Total row amounts right aligned
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    elements.append(invoice_table)
    elements.append(Spacer(1, 20))
    
    # Terms and conditions
    terms_title = Paragraph("<b>TERMS AND CONDITIONS</b>", bold_style)
    elements.append(terms_title)
    elements.append(Spacer(1, 10))
    
    terms_text = """
    1. Please Remit Payment to<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;Bank Details:<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;• Account Name: Rural Yellow Times Pvt Ltd<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;• Account No: 23902560000097<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;• Bank Name: HDFC Bank, Madeenaguda Branch, Hyderabad<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;• Bank IFSC Code: HDFC0002390<br/><br/>
    2. Payment Terms - 100% Due Now<br/><br/>
    3. This is a digitally generated invoice and does not require a physical stamp or signature.<br/><br/>
    <b>Thank you for your business!</b>
    """
    
    elements.append(Paragraph(terms_text, header_style))
    
    return elements

def create_invoices():
    # Read Excel data
    df = read_excel_data()
    if df is None:
        print("Failed to read Excel data")
        return
    
    # Output path and logo path
    output_path = "/home/thrymr/Downloads/SET2igst.pdf"
    logo_path = "/home/thrymr/Downloads/rural_yellow_logo.png"
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    # Container for all elements
    all_elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Group data by Invoice No
    invoice_groups = df.groupby('Invoice No')
    
    print(f"Found {len(invoice_groups)} unique invoices")
    
    # Process each invoice
    for invoice_no, invoice_data in invoice_groups:
        print(f"Processing invoice: {invoice_no}")
        
        # Create elements for this invoice
        invoice_elements = create_invoice_page(invoice_data, styles, logo_path)
        
        # Add to all elements
        all_elements.extend(invoice_elements)
        
        # Add page break except for the last invoice
        if invoice_no != list(invoice_groups.groups.keys())[-1]:
            all_elements.append(PageBreak())
    
    # Build PDF
    try:
        doc.build(all_elements)
        print(f"All invoices PDF generated successfully at: {output_path}")
        print(f"Total pages: {len(invoice_groups)}")
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")

if __name__ == "__main__":
    create_invoices()
