import os
from PyPDF2 import PdfReader, PdfWriter

def split_pdf(input_pdf, pages_per_file=100000):
    # Extract filename without extension
    base_name = os.path.splitext(os.path.basename(input_pdf))[0]
    
    # Create a folder with the input filename
    output_folder = base_name
    os.makedirs(output_folder, exist_ok=True)

    # Open the input PDF
    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)

    # Split and save
    for i in range(0, total_pages, pages_per_file):
        writer = PdfWriter()
        for j in range(i, min(i + pages_per_file, total_pages)):
            writer.add_page(reader.pages[j])
        
        # Define output file name
        output_pdf = os.path.join(output_folder, f"/home/thrymr/Downloads/invoices_24-25(oct-mar)/inv_oct(24-25)/{base_name}_paper{(i // pages_per_file) + 1}.pdf")
        
        # Write the output file
        with open(output_pdf, "wb") as f:
            writer.write(f)

    print(f"PDF split into {total_pages // pages_per_file + (1 if total_pages % pages_per_file else 0)} files in '{output_folder}' folder.")

# Example usage
split_pdf("/home/thrymr/Downloads/invoices_24-25(oct-mar)/invoice_oct_24_combined.pdf")  # Replace with your actual PDF file path