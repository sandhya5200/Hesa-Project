
# import pandas as pd

# file_path = "/home/thrymr/Downloads/September wallet file.xlsx"
# output_folder = "/home/thrymr/Downloads/"

# # Read all sheets
# sheets = pd.read_excel(file_path, sheet_name=None)

# # Combine
# df = pd.concat(sheets.values(), ignore_index=True)

# # Clean columns
# df.columns = df.columns.str.strip()

# # Convert date
# df['Transcation Date'] = pd.to_datetime(
#     df['Transcation Date'],
#     format='%d/%m/%Y',
#     errors='coerce'
# )

# df = df.dropna(subset=['Transcation Date'])

# # Extract month/year
# df['Month'] = df['Transcation Date'].dt.strftime('%b')
# df['Year'] = df['Transcation Date'].dt.year

# grouped = df.groupby(['Year', 'Month'])

# for (year, month), data in grouped:

#     # ✅ SORT by date ONLY (keep days ordered)
#     data = data.sort_values(by='Transcation Date')

#     # ✅ SHUFFLE within each date
#     data = data.groupby('Transcation Date', group_keys=False)\
#                .apply(lambda x: x.sample(frac=1))\
#                .reset_index(drop=True)

#     # Drop helper cols
#     data = data.drop(columns=['Month', 'Year'])

#     output_file = f"{output_folder}{month}_{year}_Wallet_Statement.xlsx"
#     data.to_excel(output_file, index=False)

#     print(f"Saved: {output_file}")




import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
import openpyxl
from datetime import datetime

# ════════════════════════════════════════════════════════════
#  CONFIG — EDIT THESE
# ════════════════════════════════════════════════════════════

INPUT_EXCEL  = "/home/thrymr/Downloads/san/Feb_2026_Wallet_Statement.xlsx"
OUTPUT_PDF   = "/home/thrymr/Downloads/san/Feb_2026_Wallet_Statement.pdf"
LOGO_PATH    = "/home/thrymr/Pictures/Screenshots/Screenshot from 2026-04-21 15-32-55.png"

ENTITY_NAME      = "Hesa Enterprises Private Limited"
SUB_WALLET       = "Hesa Consumer Products Private Limited"
CIN              = "U72500TG2020PTC143242"
ADDRESS_LINE1    = "SS Mansion Apartment, First Floor"
ADDRESS_LINE2    = "H. No. 36-137/6, Plot No. 61, Defence Colony"
ADDRESS_LINE3    = "Sainikpuri, Secunderabad, Telangana 500094"

W, H   = A4
MARGIN = 5 * mm

C_BLACK     = colors.HexColor("#1a1a1a")
C_DARK_GRAY = colors.HexColor("#444444")
C_MID_GRAY  = colors.HexColor("#888888")
C_BORDER    = colors.HexColor("#BBBBBB")
C_HDR_BG    = colors.HexColor("#DDDDDD")
C_WHITE     = colors.white

PAGE_LEFT  = MARGIN
PAGE_RIGHT = W - MARGIN
PAGE_TOP   = H - MARGIN
PAGE_BOT   = MARGIN
CONTENT_W  = PAGE_RIGHT - PAGE_LEFT

HDR_H   = 72
HDR_TOP = PAGE_TOP
HDR_BOT = PAGE_TOP - HDR_H

TABLE_START = HDR_BOT - 6

FOOTER_H  = 16
TABLE_BOT = PAGE_BOT + FOOTER_H + 4

ROW_H     = 14
TBL_HDR_H = 16

HEADERS = ["S.No", "Date", "Description", "Reference Number",
           "Dr/Cr", "Amount (Rs.)", "Transaction ID", "Status"]
RAW_W   = [32, 52, 124, 108, 28, 60, 120, 32]
_trw    = sum(RAW_W)
COL_W   = [w * CONTENT_W / _trw for w in RAW_W]

# ════════════════════════════════════════════════════════════
#  TEXT WRAP HELPER — splits on spaces AND after hyphens
# ════════════════════════════════════════════════════════════

def wrap_text(text, font_name, font_size, max_width):
    """
    Split text into lines fitting max_width.
    Splits on whitespace and also after hyphens so hyphen-joined
    strings like HS-VED-VISAKHAPATNAM-FMCG-0011 can break.
    """
    # Split on spaces; also split after every hyphen so long
    # hyphenated tokens can wrap at a hyphen boundary.
    tokens = []
    for part in text.split():
        # further split after each hyphen, keeping the hyphen with the left piece
        sub = re.split(r'(?<=-)', part)
        tokens.extend(sub)

    lines   = []
    current = ""
    for token in tokens:
        test = (current + token).strip()
        if stringWidth(test, font_name, font_size) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            # if single token is itself too wide, let it overflow (unavoidable)
            current = token
    if current:
        lines.append(current)
    return lines if lines else [""]


def calc_row_height(desc_text, txn_text, desc_col_width, txn_col_width):
    """Calculate row height needed based on wrapped description AND transaction ID lines."""
    desc_lines = wrap_text(desc_text, "Helvetica", 7.5, desc_col_width - 6)
    txn_lines  = wrap_text(txn_text,  "Helvetica", 5.8, txn_col_width  - 4)
    num_lines  = max(len(desc_lines), len(txn_lines), 1)
    return max(ROW_H, num_lines * 9 + 5)


# ════════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════════

def fmt(val):
    try:
        return f"{float(val):,.2f}" if val else "0.00"
    except Exception:
        return str(val) if val else "0.00"


def read_excel(path):
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    rows = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue
        if not any(c for c in row):
            continue
        rows.append(row)
    return rows

# ════════════════════════════════════════════════════════════
#  WATERMARK
# ════════════════════════════════════════════════════════════

def draw_watermark(cv):
    if not os.path.exists(LOGO_PATH):
        return
    cv.saveState()
    cv.setFillAlpha(0.07)
    cv.setStrokeAlpha(0.07)
    img = ImageReader(LOGO_PATH)
    sz  = 350
    cv.drawImage(img, W/2 - sz/2, H/2 - sz/2,
                 width=sz, height=sz, preserveAspectRatio=True)
    cv.restoreState()

# ════════════════════════════════════════════════════════════
#  PAGE BORDER
# ════════════════════════════════════════════════════════════

def draw_page_border(cv):
    cv.setStrokeColor(C_BORDER)
    cv.setLineWidth(0.6)
    cv.rect(PAGE_LEFT, PAGE_BOT, CONTENT_W, PAGE_TOP - PAGE_BOT, fill=0, stroke=1)

# ════════════════════════════════════════════════════════════
#  HEADER
# ════════════════════════════════════════════════════════════

def draw_header(cv):
    cv.setStrokeColor(C_BORDER)
    cv.setLineWidth(0.6)
    cv.rect(PAGE_LEFT, HDR_BOT, CONTENT_W, HDR_H, fill=0, stroke=1)

    mid = PAGE_LEFT + CONTENT_W * 0.46
    cv.setLineWidth(0.5)
    cv.line(mid, HDR_BOT, mid, HDR_TOP)

    logo_x = PAGE_LEFT + 6
    logo_y = HDR_BOT + 11
    if os.path.exists(LOGO_PATH):
        img = ImageReader(LOGO_PATH)
        cv.drawImage(img, logo_x, logo_y, width=48, height=48,
                     mask='auto', preserveAspectRatio=True)

    tx = logo_x + 54
    cv.setFillColor(C_BLACK)
    cv.setFont("Helvetica-Bold", 11.5)
    cv.drawString(tx, HDR_BOT + 50, "Digital India Payments Limited")
    cv.setFont("Helvetica", 8)
    cv.setFillColor(C_DARK_GRAY)
    cv.drawString(tx, HDR_BOT + 37, "Wallet Account Statement")

    rx = mid + 8
    cv.setFillColor(C_BLACK)
    cv.setFont("Helvetica-Bold", 9)
    cv.drawString(rx, HDR_BOT + 61, ENTITY_NAME)

    cv.setFont("Helvetica", 8)
    cv.setFillColor(C_DARK_GRAY)
    cv.drawString(rx, HDR_BOT + 52, "Sub Wallet Account : " + SUB_WALLET)
    cv.drawString(rx, HDR_BOT + 42, ADDRESS_LINE1)
    cv.drawString(rx, HDR_BOT + 32, ADDRESS_LINE2)
    cv.drawString(rx, HDR_BOT + 23, ADDRESS_LINE3)
    cv.drawString(rx, HDR_BOT + 13, "CIN : " + CIN)
    cv.drawString(rx, HDR_BOT + 2, "Statement Period : 01-Feb-2026 TO 28-Feb-2026")

# ════════════════════════════════════════════════════════════
#  TABLE HEADER ROW
# ════════════════════════════════════════════════════════════

def draw_table_header_row(cv, top_y):
    cv.setFillColor(C_HDR_BG)
    cv.rect(PAGE_LEFT, top_y - TBL_HDR_H, CONTENT_W, TBL_HDR_H, fill=1, stroke=0)
    cv.setStrokeColor(C_BORDER)
    cv.setLineWidth(0.5)
    cv.rect(PAGE_LEFT, top_y - TBL_HDR_H, CONTENT_W, TBL_HDR_H, fill=0, stroke=1)

    cv.setFont("Helvetica-Bold", 7.5)
    cv.setFillColor(C_BLACK)
    x = PAGE_LEFT
    for i, (h, cw) in enumerate(zip(HEADERS, COL_W)):
        cv.drawCentredString(x + cw/2, top_y - TBL_HDR_H + 4, h)
        if i < len(HEADERS) - 1:
            cv.setStrokeColor(C_BORDER)
            cv.setLineWidth(0.4)
            cv.line(x + cw, top_y, x + cw, top_y - TBL_HDR_H)
        x += cw
    return top_y - TBL_HDR_H

# ════════════════════════════════════════════════════════════
#  DATA ROW — description wraps, all other columns clipped
# ════════════════════════════════════════════════════════════

def draw_data_row(cv, row_data, y, idx):
    sno, txn_date, val_date, desc, ref_num, dr_cr, amount, txn_id, status = row_data

    # ── Dynamic row height driven by description AND transaction ID wrapping ──
    desc_col_w = COL_W[2]
    txn_col_w  = COL_W[6]
    desc_lines = wrap_text(str(desc)   if desc   else "", "Helvetica", 7.5, desc_col_w - 6)
    txn_lines  = wrap_text(str(txn_id) if txn_id else "", "Helvetica", 5.8, txn_col_w  - 4)
    num_lines  = max(len(desc_lines), len(txn_lines), 1)
    row_height = max(ROW_H, num_lines * 9 + 5)

    # ── Cell background ──
    cv.setFillColor(C_WHITE)
    cv.rect(PAGE_LEFT, y - row_height, CONTENT_W, row_height, fill=1, stroke=0)

    # ── Row borders ──
    cv.setStrokeColor(C_BORDER)
    cv.setLineWidth(0.3)
    cv.line(PAGE_LEFT,  y - row_height, PAGE_RIGHT, y - row_height)  # bottom
    cv.line(PAGE_LEFT,  y,              PAGE_LEFT,  y - row_height)  # left
    cv.line(PAGE_RIGHT, y,              PAGE_RIGHT, y - row_height)  # right

    cells = [sno, txn_date, desc, ref_num, dr_cr, amount, txn_id, status]

    x = PAGE_LEFT
    for ci, (cell, cw) in enumerate(zip(cells, COL_W)):
        cell_str = str(cell) if cell is not None else ""
        text_y   = y - row_height / 2 - 3   # vertical center for single-line cols

        if ci == 2:
            # ── Description: wrap + top-align ──
            lines  = wrap_text(cell_str, "Helvetica", 7.5, cw - 6)
            line_y = y - 9
            cv.setFillColor(C_BLACK)
            cv.setFont("Helvetica", 7.5)
            for line in lines:
                if line_y > (y - row_height + 2):
                    cv.drawString(x + 3, line_y, line)
                line_y -= 9

        elif ci == 3:
            # ── Reference Number: clip to column so it never bleeds right ──
            cv.setFillColor(C_BLACK)
            cv.setFont("Helvetica", 7.5)
            cv.saveState()
            p = cv.beginPath()
            p.rect(x + 1, y - row_height, cw - 2, row_height)
            cv.clipPath(p, stroke=0, fill=0)
            cv.drawString(x + 3, text_y, cell_str)
            cv.restoreState()

        elif ci == 0:
            cv.setFillColor(C_DARK_GRAY)
            cv.setFont("Helvetica", 7.5)
            cv.drawCentredString(x + cw/2, text_y, cell_str)

        elif ci == 4:
            cv.setFillColor(C_BLACK)
            cv.setFont("Helvetica-Bold", 7.5)
            cv.drawCentredString(x + cw/2, text_y, cell_str)

        elif ci == 5:
            cv.setFillColor(C_BLACK)
            cv.setFont("Helvetica", 7.5)
            cv.drawRightString(x + cw - 3, text_y, cell_str)

        elif ci == 6:
            # ── Transaction ID: wrap + top-align (same as Description) ──
            lines  = wrap_text(cell_str, "Helvetica", 5.8, cw - 4)
            line_y = y - 9
            cv.setFillColor(C_DARK_GRAY)
            cv.setFont("Helvetica", 5.8)
            for line in lines:
                if line_y > (y - row_height + 2):
                    cv.drawString(x + 2, line_y, line)
                line_y -= 9

        elif ci == 7:
            cv.setFillColor(C_DARK_GRAY)
            cv.setFont("Helvetica", 7.5)
            cv.drawCentredString(x + cw/2, text_y, cell_str)

        else:
            cv.setFillColor(C_BLACK)
            cv.setFont("Helvetica", 7.5)
            cv.drawString(x + 3, text_y, cell_str)

        # ── Vertical column divider ──
        if ci < len(cells) - 1:
            cv.setStrokeColor(C_BORDER)
            cv.setLineWidth(0.3)
            cv.line(x + cw, y, x + cw, y - row_height)
        x += cw

    return y - row_height

# ════════════════════════════════════════════════════════════
#  FOOTER
# ════════════════════════════════════════════════════════════

def draw_footer(cv, page_num, total_pages):
    y = PAGE_BOT + 4
    cv.setFont("Helvetica", 7)
    cv.setFillColor(C_MID_GRAY)
    cv.drawString(PAGE_LEFT, y,
        "Digital India Payments Limited  |  System-generated statement. Does not require a signature.")
    cv.drawRightString(PAGE_RIGHT, y, f"Page {page_num} of {total_pages}")

# ════════════════════════════════════════════════════════════
#  SMART PAGINATION — respects variable row heights
# ════════════════════════════════════════════════════════════

def paginate_rows(display_rows):
    pages   = []
    current = []
    y       = TABLE_START - TBL_HDR_H

    for row in display_rows:
        _, _, _, desc, _, _, _, txn_id, _ = row
        rh = calc_row_height(
            str(desc)   if desc   else "",
            str(txn_id) if txn_id else "",
            COL_W[2], COL_W[6]
        )

        if y - rh < TABLE_BOT and current:
            pages.append(current)
            current = []
            y = TABLE_START - TBL_HDR_H

        current.append(row)
        y -= rh

    if current:
        pages.append(current)

    return pages

# ════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════

def generate_pdf(input_excel, output_pdf):
    raw_rows = read_excel(input_excel)

    def fmt_date(val):
        if not val:
            return ""
        if hasattr(val, 'strftime'):
            return val.strftime("%d-%b-%Y")
        s = str(val).strip()
        for fmt_str in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(s, fmt_str).strftime("%d-%b-%Y")
            except ValueError:
                pass
        return s

    display_rows = []
    for sno, r in enumerate(raw_rows, 1):
        txn_date = fmt_date(r[0])
        desc     = str(r[1]) if r[1] else ""
        ref_num  = str(r[3]) if r[3] else ""
        debit    = r[4]
        credit   = r[5]
        val_date = fmt_date(r[6])
        txn_id   = str(r[7]) if r[7] else ""
        status   = str(r[8]) if r[8] else ""

        if credit and float(credit) > 0:
            dr_cr  = "C"
            amount = fmt(credit)
        else:
            dr_cr  = "D"
            amount = fmt(debit)

        display_rows.append((str(sno), txn_date, val_date, desc, ref_num,
                              dr_cr, amount, txn_id, status))

    pages       = paginate_rows(display_rows)
    total_pages = len(pages)

    cv = canvas.Canvas(output_pdf, pagesize=A4)

    for page_num, page_rows in enumerate(pages, 1):
        draw_page_border(cv)
        draw_header(cv)

        y = draw_table_header_row(cv, TABLE_START)

        for ri, row in enumerate(page_rows):
            y = draw_data_row(cv, row, y, ri)

        draw_watermark(cv)
        draw_footer(cv, page_num, total_pages)
        cv.showPage()

    cv.save()
    print(f"PDF saved  : {output_pdf}")
    print(f"Pages      : {total_pages}")
    print(f"Rows       : {len(display_rows)}")


if __name__ == "__main__":
    generate_pdf(INPUT_EXCEL, OUTPUT_PDF)