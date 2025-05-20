import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from math import isnan

def safe_str(value):
    """Convert value to string safely, replacing NaN or None with an empty string."""
    if value is None or (isinstance(value, float) and isnan(value)):
        return ""
    return str(value)

def create_pdf_with_borders(file_path, logo_path, signature_path, data):
    c = canvas.Canvas(file_path, pagesize=letter)
    border_margin = 0.5 * inch  
    width, height = letter

    left_margin = border_margin + 1.75 * inch  
    grouped_data = data.groupby('Invoice no.')


    for invoice_number, group in grouped_data:
        row_height = 0.3 * inch
        num_rows = len(group) + 1 
        table_height = row_height * num_rows

        first_row = group.iloc[0]
        last_row = group.iloc[-1]

        company_name = last_row['Facilitator']
        gstin = last_row['GSTIN']
        invoice_date = last_row['Challan Date'].strftime('%d-%m-%Y')
        due_date = last_row["Challan Date"].strftime('%d-%m-%Y')
        place_of_supply = last_row["Customer State"]

        customer_name = last_row["Customer Name"]
        customer_mobile = last_row['Customer Mobile']
        customer_district = last_row['Customer District']
        Customer_state = last_row['Customer State']
        customer_pincode = last_row['Pincode']

        customer_address = last_row["Customer Address"]
        hesathi_code = last_row["Hesaathi Code"]
        total_in_words =last_row["Total In Words"]
        sub_total = last_row["Total"]

        if hesathi_code in hesathi_mapping:
            hesathi_name, village, sub_district, district, state = hesathi_mapping[hesathi_code]
            village = (village[:40] + '...') if len(village) > 40 else village
        else:
            hesathi_name, village, sub_district, district, state = ('', '', 'Head - Office', '', '')
                                                                                                            
        company_address = last_row.get('Company Address', '')
        if isinstance(company_address, str):
            company_address_parts = company_address.split(', ')
        else:
            company_address_parts = ['']  

        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(2)  
        c.rect(border_margin, border_margin, width - 2 * border_margin, height - 2 * border_margin)

        c.setStrokeColor(colors.lightgrey)         #HORIZONTAL LINES margin_a,b,c,....
        c.setLineWidth(1.5)  
        middle_a = 9.5 * inch
        c.line(border_margin, middle_a, width - border_margin, middle_a)

        c.setFont("Helvetica", 24)
        first_column = border_margin + 5.3 * inch      #heading
        c.setFillColor(colors.black)
        text_x = 9.5 * inch + 0.1 * inch
        c.drawString(first_column, text_x, "TAX INVOICE")

        logo_x = border_margin + 0.1 * inch
        logo_y = height - 1.4 * inch  
        logo_width = 1.5 * inch
        logo_height = 0.80 * inch
        c.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height)

        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, height - 0.75 * inch, company_name)

        c.setFont("Helvetica", 10)
        address_y = height - 0.9 * inch
        if len(company_address_parts) > 2:
            line1 = ", ".join(company_address_parts[:2])  
            line2 = ", ".join(company_address_parts[2:-1])  
            line3 = company_address_parts[-1]  

            c.drawString(left_margin, address_y, line1)
            address_y -= 0.15 * inch
            c.drawString(left_margin, address_y, line2)
            address_y -= 0.15 * inch
            c.drawString(left_margin, address_y, line3)
        else:
            c.drawString(left_margin, address_y, company_address_parts[0])

        c.setFont("Helvetica", 10)
        c.drawString(left_margin, address_y - 0.15 * inch, f"GSTIN: {gstin}")

        c.setStrokeColor(colors.lightgrey) 
        c.setLineWidth(1)  
        middle_b = 8.5 * inch
        c.line(border_margin, middle_b, width - border_margin, middle_b)

        left_margin_a = border_margin + 0.1 * inch
        
        c.setFont("Helvetica", 10)
        c.drawString(left_margin_a, middle_a - 0.2 * inch , f"Invoice# : {invoice_number}")

        c.setFont("Helvetica", 10)
        c.drawString(left_margin_a, middle_a - 0.4 * inch , f"Invoice Date : {invoice_date}")

        c.setFont("Helvetica", 10)
        c.drawString(left_margin_a, middle_a - 0.6 * inch , "Terms : Due On Receipt")

        c.setFont("Helvetica", 10)
        c.drawString(left_margin_a, middle_a - 0.8 * inch , f"Due Date : {due_date}")

        middle_x = width / 2  + 0.1 * inch
        c.setFont("Helvetica", 10)
        c.drawString(middle_x, middle_a - 0.2 * inch , f"Place of Supply : {place_of_supply}")
    
        c.setStrokeColor(colors.lightgrey) 
        c.setLineWidth(1)  
        middle_c = 8.3 * inch
        c.line(border_margin, middle_c, width - border_margin, middle_c)

        bill_to_x = border_margin + 0.1 * inch        # FROM BILL TO AND SHIP TO                     
        ship_to_x = middle_x + 0.01 * inch  
        text_y = 8.3 * inch + 0.05 * inch
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(bill_to_x, text_y, "Bill To:")
        c.drawString(ship_to_x, text_y, "Ship To:")

        c.setFont("Helvetica", 10)

        c.drawString(left_margin_a, middle_c - 0.15 * inch, f"HESAATHI CODE: {hesathi_code}")             
        c.setFont("Helvetica", 10)
        
        c.drawString(left_margin_a, middle_c - 0.3 * inch, f"{hesathi_name}")
        c.drawString(left_margin_a, middle_c - 0.45 * inch, f"{village}")
        c.drawString(left_margin_a, middle_c - 0.6 * inch, f"{sub_district}")
        c.drawString(left_margin_a, middle_c - 0.75 * inch, f"{district}")
        c.drawString(left_margin_a, middle_c - 0.9 * inch, f"{state}")
        
        c.setFont("Helvetica", 10)
        c.drawString(left_margin_a, middle_c - 1.05 * inch, f"GSTIN : Unregistered")

        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(1)
        middle_d = 7 * inch
        c.line(border_margin, middle_d, width - border_margin, middle_d)

        c.setStrokeColor(colors.lightgrey)   #VERTICAL LINE
        c.setLineWidth(1)  
        middle_x = width / 2  
        c.line(middle_x, middle_a, middle_x, middle_d)


        c.setFont("Helvetica", 10)

        if isinstance(customer_address, str):
            # Split by commas if present
            if ',' in customer_address:
                customer_address_parts = customer_address.split(',')
                customer_address_parts = [part.strip() for part in customer_address_parts]  # Strip spaces

                # Construct the two lines with character limits
                line1 = ""
                line2 = ""

                for part in customer_address_parts:
                    # Add to line1 if it can fit
                    if len(line1) + len(part) + (2 if line1 else 0) <= 40:  # +2 accounts for ", "
                        line1 = f"{line1}, {part}".strip(", ")
                    # Otherwise, add to line2
                    elif len(line2) + len(part) + (2 if line2 else 0) <= 40:
                        line2 = f"{line2}, {part}".strip(", ")
                    else:
                        # Stop if line1 and line2 are full
                        break

                customer_address_parts = [line1, line2]
            else:
                # Handle case where no commas are present, split by character limit
                customer_address_parts = [
                    customer_address[:40].strip(),  # First 40 characters
                    customer_address[40:80].strip()  # Next 40 characters
                ]
        else:
            customer_address_parts = [''] * 2  # Default to two empty lines if not a string

        # Ensure we have exactly 2 lines
        if len(customer_address_parts) < 2:
            customer_address_parts += [''] * (2 - len(customer_address_parts))

        # Drawing the address on the PDF
        customer_address_y_2 = middle_c - 0.45 * inch
        for part in customer_address_parts:
            c.drawString(middle_x + 0.1 * inch, customer_address_y_2, part)
            customer_address_y_2 -= 0.15 * inch

        
        customer_name = safe_str(customer_name)

        c.setFont("Helvetica", 10)
        c.drawString(middle_x + 0.1 * inch, middle_c - 0.15 * inch, customer_name)
        c.drawString(middle_x + 0.1 * inch, middle_c - 0.30 * inch, str(customer_mobile))
        c.drawString(middle_x + 0.1 * inch, middle_c - 0.75 * inch, customer_district)
        c.drawString(middle_x + 0.1 * inch, middle_c - 0.90 * inch, Customer_state)
        #c.drawString(middle_x + 0.1 * inch, middle_c - 1.05 * inch, int(customer_pincode))
        if customer_pincode is None or (isinstance(customer_pincode, float) and isnan(customer_pincode)):
            formatted_pincode = ""  
        else:
            formatted_pincode = str(int(customer_pincode))  

        # Pass the formatted value to drawString
        c.drawString(middle_x + 0.1 * inch, middle_c - 1.05 * inch, formatted_pincode)
    


    #----------------------------------------------------------------------------------------------------------------------------------------------
        FIRST_PAGE_ROWS = 15
        SUBSEQUENT_PAGE_ROWS = 28

        # Setup table styles and margins
        column_widths = [0.3 * inch, 2 * inch, 0.8 * inch, 0.5 * inch, 0.9 * inch, 1.2 * inch, 0.5 * inch, 0.5 * inch, 0.8 * inch]
        invoice_items = [['#', 'Item & Description', 'HSN/SAC', 'Qty', 'Rate', 'Taxable Amount', 'GST', 'GST %', 'Total']]

        counter = 1
        rows_in_page = 0  # Keep track of the number of rows per page
        is_first_page = True
        row_limit = FIRST_PAGE_ROWS

        # Set initial y position for table drawing
        table_y_position = middle_d

        # Iterate through the rows and append them to the invoice_items
        for index, row in group.iterrows():
            taxable_amount = round(row['Quantity'] * row['Rate'], 2)
            total = round(taxable_amount + row['IGST'], 2)

            item_description = row['Product Name']
            if len(item_description) > 25:
                item_description = item_description[:25] + ".."
            
            invoice_items.append([
                counter,  
                item_description, 
                row['HSN/SAC'],
                round(row['Quantity'], 2),
                round(row['Rate'], 2), 
                round(taxable_amount, 2),
                round(row['IGST'], 2), 
                round(row['GST Rate'], 2),
                total
            ])
            
            
            counter += 1
            rows_in_page += 1

            # Check if the current page has reached the row limit
            if rows_in_page == row_limit:
                # Create the table
                table = Table(invoice_items, colWidths=column_widths)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header row background
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header text color
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Align the columns center
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding for header
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Body row background
                    ('GRID', (0, 0), (-1, -1), 1, colors.lightslategray),  # Border around cells
                ]))

                # Draw table on the current page
                table.wrapOn(c, width, height)
                table.drawOn(c, border_margin, table_y_position - len(invoice_items) * 18)

                

                # Reset for the next page
                invoice_items = [['#', 'Item & Description', 'HSN/SAC', 'Qty', 'Rate', 'Taxable Amount', 'GST', 'GST %', 'Total']]
                rows_in_page = 0
                c.showPage()  # Move to next page

                c.setStrokeColor(colors.lightgrey)
                c.setLineWidth(2)
                c.rect(border_margin, border_margin, width - 2 * border_margin, height - 2 * border_margin)


                # After the first page, update row_limit and table_y_position
                if is_first_page:
                    is_first_page = False
                    row_limit = SUBSEQUENT_PAGE_ROWS
                    table_y_position = middle_a  + 0.9 * inch # Update for the next page

                    
        # Draw remaining items if any exist after the loop
        if len(invoice_items) > 1 and rows_in_page > 0:  # Check if there are any items to show
            table = Table(invoice_items, colWidths=column_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header row background
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header text color
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Align the columns center
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding for header
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Body row background
                ('GRID', (0, 0), (-1, -1), 1, colors.lightslategray),  # Border around cells
            ]))

            table.wrapOn(c, width, height)
            table.drawOn(c, border_margin, table_y_position - len(invoice_items) * 18)

        line_y_position = table_y_position - len(invoice_items) * 18  # Adjusted for the total rows drawn

        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(1)
        middle_e = line_y_position - 0.4 * inch
        c.line(border_margin, middle_e, width - border_margin, middle_e)

        c.setFont("Helvetica-Bold", 10)
        sub_total = round(sub_total, 0)  # Ensure sub_total is defined
        c.drawString(left_margin_a + 5.8 * inch, middle_e + 0.1 * inch , f"Sub Total :  {sub_total}")



#-------------------------------------------------------------------------------------------------------------------------------------



        c.setFont("Helvetica", 10)
        c.drawString(left_margin_a, middle_e - 0.2 * inch , f"Total In Words :")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(left_margin_a, middle_e - 0.4 * inch , f"{total_in_words}")

        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(1)
        middle_f = border_margin + 1.6 * inch
        c.line(border_margin, middle_f, width - border_margin, middle_f)

        def fill_bank_details(company_name):                                  #TO ADD BANK
            if company_name == 'Hesa Consumer Products Private Limited':
                return {
                    'Name': 'HESA CONSUMER PRODUCTS PVT LTD',
                    'IFSC Code': '50200063044078',
                    'Account No': 'HDFC0000045',
                    'Bank': 'CHANDA NAGAR'
                }
            elif company_name == 'Hesa Enterprises Private Limited':
                return {
                    'Name': 'HESA ENTERPRISES PVT LTD',
                    'IFSC Code': '920020002599918',
                    'Account No': 'UTIB0003175',
                    'Bank': 'Axis Bank, Sainikpuri Branch'
                }
            elif company_name == 'Hesa Agritech Private Limited':
                return {
                    'Name': 'HESA AGRITECH PVT LTD',
                    'IFSC Code': '50200063083936',
                    'Account No': 'HDFC0000045',
                    'Bank': 'CHANDA NAGAR'
                }
            else:
                return {
                    'Name': 'Unknown',
                    'IFSC Code': '',
                    'Account No': '',
                    'Bank': ''
                }
        bank_details = fill_bank_details(company_name)

        c.setFont("Helvetica-Bold", 10)
        c.drawString(left_margin_a, middle_f - 0.2 * inch , f"Bank Details")
        c.setFont("Helvetica", 10)
        c.drawString(left_margin_a, middle_f - 0.4 * inch , f"Name:")
        c.setFont("Helvetica", 10)
        c.drawString(left_margin_a, middle_f - 0.6 * inch , f"IFSC Code:")
        c.setFont("Helvetica", 10)
        c.drawString(left_margin_a, middle_f - 0.8 * inch , f"Account No:")
        c.setFont("Helvetica", 10)
        c.drawString(left_margin_a, middle_f - 1 * inch , f"Bank:")

        c.setFont("Helvetica", 10)
        
        c.drawString(left_margin_a + 0.9 * inch, middle_f - 0.4 * inch, f"{bank_details['Name']}")
        c.drawString(left_margin_a + 0.9 * inch, middle_f - 0.6 * inch, f"{bank_details['IFSC Code']}")
        c.drawString(left_margin_a + 0.9 * inch, middle_f - 0.8 * inch, f"{bank_details['Account No']}")
        c.drawString(left_margin_a + 0.9 * inch, middle_f - 1 * inch, f"{bank_details['Bank']}")


        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(1)
        middle_g = middle_f - 1.1 * inch 
        c.line(border_margin, middle_g, width - border_margin, middle_g)

        vertical_x_position = (width / 2)        
        c.line(vertical_x_position, middle_f, vertical_x_position, middle_g)

        signature_x = width - 3.4 * inch  
        signature_y = middle_f - 0.9 * inch        
        signature_width = 1.5 * inch    
        signature_height = 0.8 * inch   
        c.drawImage(signature_path, signature_x, signature_y, width=signature_width, height=signature_height)

        c.setFont("Helvetica", 10)
        c.drawString(vertical_x_position + 1 * inch,middle_f - 1 * inch, f"Verifier Signature")

        c.setFont("Helvetica-Bold", 10)
        c.drawString(left_margin_a, middle_g - 0.2 * inch , f"Notes :")
        c.setFont("Helvetica", 10)
        c.drawString(left_margin_a, middle_g - 0.4 * inch , f"Thanks for your Bussiness")

        c.showPage()

    c.save()

logo_file_path = "/home/thrymr/Downloads/hesa_logo.png"  
signature_path = "/home/thrymr/Downloads/sir_signature-removebg-preview.png"
hesathi_data = pd.read_excel('/home/thrymr/Downloads/Copy of zone_user_24_25 latest one with new additions..xlsx')  

# List of Excel files to process
excel_file_paths = [
    

            # '/home/thrymr/Downloads/sales 23-24/ready_Final_Sales_Apr_23 (2).xlsx',
            # '/home/thrymr/Downloads/sales 23-24/ready_Final_Sales_May_23 (2).xlsx',
            # '/home/thrymr/Downloads/sales 23-24/ready_Final_Sales_june_23 (1).xlsx',
            # '/home/thrymr/Downloads/sales 23-24/ready_Final_Sales_july_23.xlsx',
            # '/home/thrymr/Downloads/sales 23-24/ready_Final_Sales_August_23 (1).xlsx',
            # '/home/thrymr/Downloads/sales 23-24/ready_Final_Sales_September_23 (1).xlsx',
            # '/home/thrymr/Downloads/sales 23-24/ready_Final_Sales_october_23 (1).xlsx',
            '/home/thrymr/Downloads/sales 23-24/ready_Final_Sales_Nov_23.xlsx',
            '/home/thrymr/Downloads/sales 23-24/ready_Final_Sales_dec_23.xlsx',
            '/home/thrymr/Downloads/sales 23-24/ready_Final_Sales_jan_24 (1).xlsx',
            '/home/thrymr/Downloads/sales 23-24/ready_Final_Sales_feb_24 (1).xlsx',
            '/home/thrymr/Downloads/sales 23-24/ready_Final_Sales_Mar_24 (1).xlsx'


]

# Create a PDF for each Excel file
for excel_file_path in excel_file_paths:
    data = pd.read_excel(excel_file_path)                         

    hesathi_mapping = pd.Series(
        hesathi_data[['Full Name', 'Village', 'Sub District', 'District', 'State']].values.tolist(), 
        index=hesathi_data['CODE']
    ).to_dict()

    # Generate a unique name for the PDF based on the Excel filename
    pdf_file_name = f"{excel_file_path.split('/')[-1].replace('.xlsx', '')}.pdf"
    final_pdf_path = f"/home/thrymr/Downloads/sales 23-24/invoice_{pdf_file_name}"

    # Create the PDF with all invoices
    create_pdf_with_borders(final_pdf_path, logo_file_path, signature_path, data)

    print(f"Merged PDF created: {final_pdf_path}")

