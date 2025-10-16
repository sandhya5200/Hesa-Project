from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import tempfile
import shutil
from typing import List
from datetime import datetime
import traceback

app = FastAPI(title="Sales Credit Allocation API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary directory for processing
TEMP_DIR = tempfile.mkdtemp()
OUTPUT_DIR = os.path.join(TEMP_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------
# Credit Allocation Function
# ---------------------------
def allocate_credits(sales, credits, facilitator_name):
    sales = sales.copy()
    sales = sales[sales['Facilitator'] == facilitator_name].copy()
    
    # Initialize columns
    for col in ['DATE', 'DESCRIPTION', 'REFERENCE NO.', 'AMOUNT', 'BANK', 
                'reference amount', 'wallet', 'status']:
        sales[col] = None
    
    credits = credits.sort_values('DATE').copy()
    credits['Invoices'] = ""
    
    for idx, credit in credits.iterrows():
        credit_amount = credit['AMOUNT']
        txn_date = credit['DATE']
        txn_desc = credit.get('DESCRIPTION', '')
        txn_ref = credit.get('REFERENCE NO.', '')
        txn_bank = credit.get('BANK', '')
        
        invoices_today = sales[(sales['Date'] == txn_date) & (sales['status'].isna())]
        allocated_invoices = []
        
        while credit_amount > 0 and not invoices_today.empty:
            matched_invoice = invoices_today[invoices_today['Invoice Total'] <= credit_amount]
            
            if matched_invoice.empty:
                break
            
            inv_idx = matched_invoice.index[0]
            inv_total = sales.at[inv_idx, 'Invoice Total']
            inv_number = sales.at[inv_idx, 'Invoice No']
            
            sales.at[inv_idx, 'DATE'] = txn_date
            sales.at[inv_idx, 'DESCRIPTION'] = txn_desc
            sales.at[inv_idx, 'REFERENCE NO.'] = txn_ref
            sales.at[inv_idx, 'AMOUNT'] = credit['AMOUNT']
            sales.at[inv_idx, 'BANK'] = txn_bank
            sales.at[inv_idx, 'reference amount'] = inv_total
            sales.at[inv_idx, 'wallet'] = 0
            sales.at[inv_idx, 'status'] = 'paid'
            
            allocated_invoices.append(inv_number)
            credit_amount -= inv_total
            invoices_today = sales[(sales['Date'] == txn_date) & (sales['status'].isna())]
        
        if credit_amount > 0 and len(sales[sales['status']=='paid']) > 0:
            last_paid_idx = sales[sales['status']=='paid'].index[-1]
            sales.at[last_paid_idx, 'wallet'] = credit_amount
        
        if allocated_invoices:
            credits.at[idx, 'Invoices'] = ",".join(map(str, allocated_invoices))
    
    return sales, credits

# ---------------------------
# Main Processing Endpoint
# ---------------------------
@app.post("/process")
async def process_files(
    sales_files: List[UploadFile] = File(..., description="Sales Excel files (1-5 files)"),
    agri_credits: UploadFile = File(..., description="Agri credits Excel file"),
    cons_credits: UploadFile = File(..., description="Consumer credits Excel file")
):
    try:
        # Validation
        if len(sales_files) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 sales files allowed")
        
        if len(sales_files) == 0:
            raise HTTPException(status_code=400, detail="At least 1 sales file required")
        
        # Validate file extensions
        for file in sales_files + [agri_credits, cons_credits]:
            if not file.filename.endswith(('.xlsx', '.xls')):
                raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}")
        
        print("📥 Starting file processing...")
        
        # ============================================================================
        # PART 1: Load and Process Sales Files
        # ============================================================================
        dfs = []
        for i, sales_file in enumerate(sales_files):
            print(f"   Loading sales file {i+1}/{len(sales_files)}: {sales_file.filename}")
            
            # Save uploaded file temporarily
            temp_sales_path = os.path.join(TEMP_DIR, f"sales_{i}_{sales_file.filename}")
            with open(temp_sales_path, "wb") as buffer:
                shutil.copyfileobj(sales_file.file, buffer)
            
            # Read Excel
            df = pd.read_excel(temp_sales_path)
            dfs.append(df)
            
            # Clean up temp file
            os.remove(temp_sales_path)
        
        # Concatenate all sales dataframes
        print("   Concatenating sales data...")
        df = pd.concat(dfs, ignore_index=True)
        
        # Generate invoice summary
        print("   Generating invoice summary...")
        first_info = df.groupby("Invoice No").first().reset_index()
        totals = df.groupby("Invoice No", as_index=False)["Sub total"].sum().rename(
            columns={"Sub total": "Invoice Total"}
        )
        summary = pd.merge(first_info, totals, on="Invoice No", how="inner")
        
        summary = summary[[
            "Date", "Hesaathi Code", "CustomerID", "Customer State", "CustomerDistrict",
            "Facilitator", "Vertical", "Order_Id", "Invoice No", "Invoice Total"
        ]]
        
        summary.insert(0, "Sl No", range(1, len(summary) + 1))
        
        # ============================================================================
        # PART 2: Load Credit Files
        # ============================================================================
        print("   Loading credit files...")
        
        # Save and load agri credits
        temp_agri_path = os.path.join(TEMP_DIR, f"agri_{agri_credits.filename}")
        with open(temp_agri_path, "wb") as buffer:
            shutil.copyfileobj(agri_credits.file, buffer)
        agri_credits_df = pd.read_excel(temp_agri_path)
        os.remove(temp_agri_path)
        
        # Save and load cons credits
        temp_cons_path = os.path.join(TEMP_DIR, f"cons_{cons_credits.filename}")
        with open(temp_cons_path, "wb") as buffer:
            shutil.copyfileobj(cons_credits.file, buffer)
        cons_credits_df = pd.read_excel(temp_cons_path)
        os.remove(temp_cons_path)
        
        # ============================================================================
        # PART 3: Process and Allocate Credits
        # ============================================================================
        print("   Processing credit allocation...")
        
        sales_df = summary.copy()
        
        # Standardize date formats
        sales_df['Date'] = pd.to_datetime(sales_df['Date']).dt.date
        agri_credits_df['DATE'] = pd.to_datetime(agri_credits_df['DATE'], dayfirst=True).dt.date
        cons_credits_df['DATE'] = pd.to_datetime(cons_credits_df['DATE'], dayfirst=True).dt.date
        
        # Allocate for Agri
        print("   Allocating Agri credits...")
        agri_allocated, agri_credits_with_invoices = allocate_credits(
            sales_df, agri_credits_df, 'Hesa Agritech Private Limited'
        )
        
        # Allocate for Consumer
        print("   Allocating Consumer credits...")
        cons_allocated, cons_credits_with_invoices = allocate_credits(
            sales_df, cons_credits_df, 'Hesa Consumer Products Private Limited'
        )
        
        # Merge allocations
        final_allocations = pd.concat([agri_allocated, cons_allocated])
        cols_to_merge = ['Sl No','DATE','DESCRIPTION','REFERENCE NO.','AMOUNT','BANK',
                         'reference amount','wallet','status']
        final_sales = sales_df.merge(final_allocations[cols_to_merge], on='Sl No', how='left')
        final_sales['wallet'] = final_sales['wallet'].fillna(final_sales['Invoice Total'])
        
        # ============================================================================
        # PART 4: Save Output Files
        # ============================================================================
        print("   Saving output files...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        output_sales = os.path.join(OUTPUT_DIR, f"invoice_summary_matched_{timestamp}.xlsx")
        output_agri = os.path.join(OUTPUT_DIR, f"agri_credits_with_invoices_{timestamp}.xlsx")
        output_cons = os.path.join(OUTPUT_DIR, f"cons_credits_with_invoices_{timestamp}.xlsx")
        
        final_sales.to_excel(output_sales, index=False)
        agri_credits_with_invoices.to_excel(output_agri, index=False)
        cons_credits_with_invoices.to_excel(output_cons, index=False)
        
        print("✅ Processing complete!")
        
        return JSONResponse({
            "status": "success",
            "message": "Files processed successfully",
            "outputs": {
                "sales_summary": f"invoice_summary_matched_{timestamp}.xlsx",
                "agri_credits": f"agri_credits_with_invoices_{timestamp}.xlsx",
                "cons_credits": f"cons_credits_with_invoices_{timestamp}.xlsx"
            },
            "stats": {
                "total_invoices": len(final_sales),
                "agri_matched": int(agri_allocated['status'].notna().sum()),
                "cons_matched": int(cons_allocated['status'].notna().sum())
            }
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# ---------------------------
# Download Endpoint
# ---------------------------
@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ---------------------------
# Health Check
# ---------------------------
@app.get("/")
async def root():
    return {"status": "running", "message": "Sales Credit Allocation API"}

# ---------------------------
# Cleanup old files on startup
# ---------------------------
@app.on_event("startup")
async def startup_event():
    print("🚀 API Server Started")
    print(f"   Temp Directory: {TEMP_DIR}")
    print(f"   Output Directory: {OUTPUT_DIR}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)