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

app = FastAPI(title="Purchases Debit Allocation API")

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
# Debit Allocation Function
# ---------------------------
def allocate_debits(purchases, debits, purchaser_name):
    purchases = purchases.copy()
    purchases = purchases[purchases['Purchaser'] == purchaser_name].copy()
    
    # Initialize columns
    for col in ['DATE', 'DESCRIPTION', 'REFERENCE NO.', 'AMOUNT', 'BANK', 
                'reference amount', 'wallet', 'status']:
        purchases[col] = None
    
    debits = debits.sort_values('DATE').copy()
    debits['POs'] = ""
    
    for idx, debit in debits.iterrows():
        debit_amount = debit['AMOUNT']
        txn_date = debit['DATE']
        txn_desc = debit.get('DESCRIPTION', '')
        txn_ref = debit.get('REFERENCE NO.', '')
        txn_bank = debit.get('BANK', '')
        
        pos_today = purchases[(purchases['Date'] == txn_date) & (purchases['status'].isna())]
        allocated_pos = []
        
        while debit_amount > 0 and not pos_today.empty:
            matched_invoice = pos_today[pos_today['Invoice Total'] <= debit_amount]
            
            if matched_invoice.empty:
                break
            
            inv_idx = matched_invoice.index[0]
            inv_total = purchases.at[inv_idx, 'Invoice Total']
            inv_number = purchases.at[inv_idx, 'Po_Number']
            
            purchases.at[inv_idx, 'DATE'] = txn_date
            purchases.at[inv_idx, 'DESCRIPTION'] = txn_desc
            purchases.at[inv_idx, 'REFERENCE NO.'] = txn_ref
            purchases.at[inv_idx, 'AMOUNT'] = debit['AMOUNT']
            purchases.at[inv_idx, 'BANK'] = txn_bank
            purchases.at[inv_idx, 'reference amount'] = inv_total
            purchases.at[inv_idx, 'wallet'] = 0
            purchases.at[inv_idx, 'status'] = 'paid'
            
            allocated_pos.append(inv_number)
            debit_amount -= inv_total
            pos_today = purchases[(purchases['Date'] == txn_date) & (purchases['status'].isna())]
        
        if debit_amount > 0 and len(purchases[purchases['status']=='paid']) > 0:
            last_paid_idx = purchases[purchases['status']=='paid'].index[-1]
            purchases.at[last_paid_idx, 'wallet'] = debit_amount
        
        if allocated_pos:
            debits.at[idx, 'POs'] = ",".join(map(str, allocated_pos))
    
    return purchases, debits

# ---------------------------
# Main Processing Endpoint
# ---------------------------
@app.post("/process")
async def process_files(
    purchases_files: List[UploadFile] = File(..., description="Purchases Excel files (1-5 files)"),
    agri_debits: UploadFile = File(..., description="Agri debits Excel file"),
    cons_debits: UploadFile = File(..., description="Consumer debits Excel file")
):
    try:
        # Validation
        if len(purchases_files) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 purchases files allowed")
        
        if len(purchases_files) == 0:
            raise HTTPException(status_code=400, detail="At least 1 purchases file required")
        
        # Validate file extensions
        for file in purchases_files + [agri_debits, cons_debits]:
            if not file.filename.endswith(('.xlsx', '.xls')):
                raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}")
        
        print("📥 Starting file processing...")
        
        # ============================================================================
        # PART 1: Load and Process Purchases Files
        # ============================================================================
        dfs = []
        for i, purchases_file in enumerate(purchases_files):
            print(f"   Loading purchases file {i+1}/{len(purchases_files)}: {purchases_file.filename}")
            
            # Save uploaded file temporarily
            temp_purchases_path = os.path.join(TEMP_DIR, f"purchases_{i}_{purchases_file.filename}")
            with open(temp_purchases_path, "wb") as buffer:
                shutil.copyfileobj(purchases_file.file, buffer)
            
            # Read Excel
            df = pd.read_excel(temp_purchases_path)
            dfs.append(df)
            
            # Clean up temp file
            os.remove(temp_purchases_path)
        
        # Concatenate all purchases dataframes
        print("   Concatenating purchases data...")
        df = pd.concat(dfs, ignore_index=True)
        
        # Generate invoice summary
        print("   Generating invoice summary...")
        first_info = df.groupby("Po_Number").first().reset_index()
        totals = df.groupby("Po_Number", as_index=False)["Total"].sum().rename(
            columns={"Total": "Invoice Total"}
        )
        summary = pd.merge(first_info, totals, on="Po_Number", how="inner")
        
        summary = summary[[
            "Date", "Hesaathi_Code", "Vendor_Id", "Vendor_State", "Vendor_District",
            "Purchaser", "Vertical", "Po_Number", "Invoice Total"
        ]]
        
        summary.insert(0, "Sl No", range(1, len(summary) + 1))
        
        # ============================================================================
        # PART 2: Load Debit Files
        # ============================================================================
        print("   Loading debit files...")
        
        # Save and load agri debits
        temp_agri_path = os.path.join(TEMP_DIR, f"agri_{agri_debits.filename}")
        with open(temp_agri_path, "wb") as buffer:
            shutil.copyfileobj(agri_debits.file, buffer)
        agri_debits_df = pd.read_excel(temp_agri_path)
        os.remove(temp_agri_path)
        
        # Save and load cons debits
        temp_cons_path = os.path.join(TEMP_DIR, f"cons_{cons_debits.filename}")
        with open(temp_cons_path, "wb") as buffer:
            shutil.copyfileobj(cons_debits.file, buffer)
        cons_debits_df = pd.read_excel(temp_cons_path)
        os.remove(temp_cons_path)
        
        # ============================================================================
        # PART 3: Process and Allocate Debits
        # ============================================================================
        print("   Processing debit allocation...")
        
        purchases_df = summary.copy()
        
        # Standardize date formats
        purchases_df['Date'] = pd.to_datetime(purchases_df['Date']).dt.date
        agri_debits_df['DATE'] = pd.to_datetime(agri_debits_df['DATE'], dayfirst=True).dt.date
        cons_debits_df['DATE'] = pd.to_datetime(cons_debits_df['DATE'], dayfirst=True).dt.date
        
        # Allocate for Agri
        print("   Allocating Agri debits...")
        agri_allocated, agri_debits_with_pos = allocate_debits(
            purchases_df, agri_debits_df, 'Hesa Agritech Private Limited'
        )
        
        # Allocate for Consumer
        print("   Allocating Consumer debits...")
        cons_allocated, cons_debits_with_pos = allocate_debits(
            purchases_df, cons_debits_df, 'Hesa Consumer Products Private Limited'
        )
        
        # Merge allocations
        final_allocations = pd.concat([agri_allocated, cons_allocated])
        cols_to_merge = ['Sl No','DATE','DESCRIPTION','REFERENCE NO.','AMOUNT','BANK',
                         'reference amount','wallet','status']
        final_purchases = purchases_df.merge(final_allocations[cols_to_merge], on='Sl No', how='left')
        final_purchases['wallet'] = final_purchases['wallet'].fillna(final_purchases['Invoice Total'])
        
        # ============================================================================
        # PART 4: Save Output Files
        # ============================================================================
        print("   Saving output files...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        output_purchases = os.path.join(OUTPUT_DIR, f"invoice_summary_matched_{timestamp}.xlsx")
        output_agri = os.path.join(OUTPUT_DIR, f"agri_debits_with_POs_{timestamp}.xlsx")
        output_cons = os.path.join(OUTPUT_DIR, f"cons_debits_with_POs_{timestamp}.xlsx")
        
        final_purchases.to_excel(output_purchases, index=False)
        agri_debits_with_pos.to_excel(output_agri, index=False)
        cons_debits_with_pos.to_excel(output_cons, index=False)
        
        print("✅ Processing complete!")
        
        return JSONResponse({
            "status": "success",
            "message": "Files processed successfully",
            "outputs": {
                "purchases_summary": f"invoice_summary_matched_{timestamp}.xlsx",
                "agri_debits": f"agri_debits_with_POs_{timestamp}.xlsx",
                "cons_debits": f"cons_debits_with_POs_{timestamp}.xlsx"
            },
            "stats": {
                "total_POs": len(final_purchases),
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
    return {"status": "running", "message": "Purchases Debit Allocation API"}

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