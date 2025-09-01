import pandas as pd
import numpy as np
from datetime import datetime
import os

def create_sales_pivot(input_file_path, output_file_path):
    """
    Create pivot tables from sales data and save to specified Excel file with two sheets
    - Sheet 1: Product Quantities by District (sheet name: "Quantity")
    - Sheet 2: Taxable Values by District (sheet name: "Taxable value")
    """
    
    # Read the Excel file (assuming it's Excel format)
    print("Reading sales data...")
    try:
        # Try reading as Excel first, then CSV if that fails
        if input_file_path.endswith('.xlsx') or input_file_path.endswith('.xls'):
            df = pd.read_excel(input_file_path)
        else:
            df = pd.read_csv(input_file_path)
        print(f"Data loaded successfully: {len(df)} rows")
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Display basic info about the dataset
    print(f"Columns in dataset: {list(df.columns)}")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"Unique districts: {df['District'].nunique()}")
    print(f"Unique products: {df['Product Name'].nunique()}")
    
    # Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Clean and prepare data
    # Remove any rows with missing essential data
    essential_cols = ['Date', 'Sub Vertical', 'Product Name', 'HSN/SAC', 
                     'UOM', 'Category', 'Sub Category', 'gst_rate', 
                     'District', 'Quantity', 'Taxable Value']
    
    df_clean = df.dropna(subset=essential_cols)
    print(f"Rows after cleaning: {len(df_clean)}")
    
    # Create base dataframe with required columns
    base_cols = ['Date', 'Sub Vertical', 'Product Name', 'HSN/SAC', 
                'UOM', 'Category', 'Sub Category', 'gst_rate']
    
    # 1. CREATE QUANTITY PIVOT TABLE
    print("\nCreating Quantity Pivot Table...")
    
    # Create pivot table for quantities
    quantity_pivot = df_clean.pivot_table(
        index=base_cols,
        columns='District',
        values='Quantity',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    # Flatten column names
    quantity_pivot.columns.name = None
    
    print(f"Quantity pivot shape: {quantity_pivot.shape}")
    print(f"Districts in quantity pivot: {[col for col in quantity_pivot.columns if col not in base_cols]}")
    
    # 2. CREATE TAXABLE VALUE PIVOT TABLE
    print("\nCreating Taxable Value Pivot Table...")
    
    # Create pivot table for taxable values
    value_pivot = df_clean.pivot_table(
        index=base_cols,
        columns='District',
        values='Taxable Value',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    # Flatten column names
    value_pivot.columns.name = None
    
    print(f"Value pivot shape: {value_pivot.shape}")
    print(f"Districts in value pivot: {[col for col in value_pivot.columns if col not in base_cols]}")
    
    # 3. SAVE TO EXCEL FILE WITH TWO SHEETS
    print(f"\nSaving Excel file to: {output_file_path}")
    
    # Create the output Excel file with both sheets
    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
        # Sheet 1: Quantities (sheet name: "Quantity")
        quantity_pivot.to_excel(writer, sheet_name='Quantity', index=False)
        
        # Sheet 2: Taxable Values (sheet name: "Taxable value")  
        value_pivot.to_excel(writer, sheet_name='Taxable value', index=False)
        
        # Format both sheets
        for sheet_name in ['Quantity', 'Taxable value']:
            worksheet = writer.sheets[sheet_name]
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"✅ Excel file saved successfully with both sheets!")
    
    # 4. DISPLAY SUMMARY STATISTICS
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    
    # Get district columns (exclude base columns)
    district_cols = [col for col in quantity_pivot.columns if col not in base_cols]
    
    print(f"\n📊 DISTRICTS COVERED ({len(district_cols)}):")
    for i, district in enumerate(district_cols, 1):
        qty_total = quantity_pivot[district].sum()
        value_total = value_pivot[district].sum()
        print(f"{i:2d}. {district:15s} | Qty: {qty_total:10,.2f} | Value: ₹{value_total:12,.2f}")
    
    print(f"\n📈 OVERALL TOTALS:")
    total_qty = quantity_pivot[district_cols].sum().sum()
    total_value = value_pivot[district_cols].sum().sum()
    print(f"Total Quantity: {total_qty:,.2f}")
    print(f"Total Value: ₹{total_value:,.2f}")
    
    print(f"\n📦 PRODUCT CATEGORIES:")
    category_summary = df_clean.groupby('Category').agg({
        'Quantity': 'sum',
        'Taxable Value': 'sum'
    }).round(2)
    print(category_summary)
    
    print(f"\n🏢 SUB-VERTICAL SUMMARY:")
    subvertical_summary = df_clean.groupby('Sub Vertical').agg({
        'Quantity': 'sum',
        'Taxable Value': 'sum'
    }).round(2)
    print(subvertical_summary)
    
    return quantity_pivot, value_pivot

def create_combined_file(input_file_path, output_file_path):
    """
    Create a single Excel file with both quantity and value sheets
    """
    print("Creating Excel file with both sheets...")
    
    # Read the Excel file
    if input_file_path.endswith('.xlsx') or input_file_path.endswith('.xls'):
        df = pd.read_excel(input_file_path)
    else:
        df = pd.read_csv(input_file_path)
        
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Clean data
    essential_cols = ['Date', 'Sub Vertical', 'Product Name', 'HSN/SAC', 
                     'UOM', 'Category', 'Sub Category', 'gst_rate', 
                     'District', 'Quantity', 'Taxable Value']
    
    df_clean = df.dropna(subset=essential_cols)
    
    base_cols = ['Date', 'Sub Vertical', 'Product Name', 'HSN/SAC', 
                'UOM', 'Category', 'Sub Category', 'gst_rate']
    
    # Create both pivot tables
    quantity_pivot = df_clean.pivot_table(
        index=base_cols,
        columns='District',
        values='Quantity',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    value_pivot = df_clean.pivot_table(
        index=base_cols,
        columns='District',
        values='Taxable Value',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    # Clean column names
    quantity_pivot.columns.name = None
    value_pivot.columns.name = None
    
    # Save to specified output file
    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
        quantity_pivot.to_excel(writer, sheet_name='Quantity', index=False)
        value_pivot.to_excel(writer, sheet_name='Taxable value', index=False)
        
        # Format both sheets
        for sheet_name in ['Quantity', 'Taxable value']:
            worksheet = writer.sheets[sheet_name]
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"✅ Combined file saved: {output_file_path}")
    return output_file_path

# Example usage with your specific file paths:
if __name__ == "__main__":
    # Your specific file paths
    input_file = r"c:\Users\ksand\Downloads\sales(20-21)\apr_sales_with_customers.xlsx"
    output_file = r"c:\Users\ksand\Downloads\pivot.xlsx"
    
    try:
        # Create pivot tables and save to your specified output file
        print("Processing sales data with your file paths...")
        qty_pivot, val_pivot = create_sales_pivot(input_file, output_file)
        
        print(f"\n✅ File created successfully!")
        print(f"📁 Output file: {output_file}")
        print(f"📊 Sheets: 'Quantity' and 'Taxable value'")
        
        # You can now read the created file like this:
        # product_quantity = pd.read_excel(r"c:\Users\ksand\Downloads\Copy of mar_2019_sales(1).xlsx", sheet_name="Quantity")
        # product_gross = pd.read_excel(r"c:\Users\ksand\Downloads\Copy of mar_2019_sales(1).xlsx", sheet_name="Taxable value")
        
    except FileNotFoundError:
        print(f"❌ Input file not found: {input_file}")
        print("Please make sure the file exists at the specified location")
    except Exception as e:
        print(f"❌ Error: {e}")

# Function to read the created pivot data (for your reference)
def read_created_pivots():
    """
    Function to read the pivot data you just created
    """
    output_file = r"c:\Users\ksand\Downloads\pivot.xlsx"
    
    # Read both sheets
    product_quantity = pd.read_excel(output_file, sheet_name="Quantity")
    product_gross = pd.read_excel(output_file, sheet_name="Taxable value")
    
    print(f"Quantity sheet shape: {product_quantity.shape}")
    print(f"Taxable value sheet shape: {product_gross.shape}")
    
    return product_quantity, product_gross


