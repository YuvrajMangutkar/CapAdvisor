"""
export/excel_exporter.py — Generate clean, simple Excel file for direct CAP round import/copying.
"""
from __future__ import annotations

import io
from typing import List
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Realistic MHT-CET College Codes (4-digit DTE codes)
COLLEGE_CODES = {
    1: 6006,  # COEP
    2: 3012,  # VJTI
    3: 3022,  # ICT
    4: 6271,  # PICT
    5: 6273,  # VIT Pune
    6: 3185,  # DJ Sanghvi
    7: 3207,  # KJ Somaiya
    8: 3014,  # SPCE
    9: 6284,  # MIT Pune
    10: 3146, # RAIT
    11: 3148, # FRCRCE
    12: 3182, # Thadomal
    13: 6278, # AIT
    14: 6275, # Walchand
    15: 2008, # GCE Aurangabad
    16: 4115, # YCCE
    17: 1002, # GCE Amravati
    18: 3196, # LTCE
    19: 6187, # Sinhgad
    20: 6272, # DY Patil
}

# DTE Branch code suffix mapping (5-digit DTE codes)
BRANCH_NUMS = {
    "CE": "19110",
    "IT": "24610",
    "AIDS": "26310",
    "ETE": "37210",
    "MECH": "61210",
    "CIVIL": "19110",
    "EE": "29310",
}


def _col_border():
    thin = Side(style="thin", color="CCCCCC")
    return Border(left=thin, right=thin, top=thin, bottom=thin)


def generate_excel(
    entries: list,
    student_percentile: float,
    category: str,
) -> io.BytesIO:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "CAP Preference List"

    # ── Column Headers (Row 1) ─────────────────────────────────────────────────
    # We place headers directly on Row 1 so the sheet is easy to import / parse
    headers = [
        "Preference No.", 
        "Choice Code", 
        "College Name", 
        "Branch", 
        "District", 
        "Category", 
        "Option Type"
    ]
    col_widths = [16, 18, 45, 36, 14, 12, 14]

    # Simple clean headers (dark gray fill with bold white text)
    header_fill = PatternFill("solid", fgColor="333333")
    header_font = Font(name="Calibri", bold=True, size=10, color="FFFFFF")

    for col_idx, (header, width) in enumerate(zip(headers, col_widths), start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = _col_border()
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    ws.row_dimensions[1].height = 28
    ws.freeze_panes = "A2"

    # ── Data Rows (Row 2+) ─────────────────────────────────────────────────────
    # Standard text style with no colored backgrounds (except clean light borders)
    data_font = Font(name="Calibri", size=10, color="000000")
    bold_data_font = Font(name="Calibri", size=10, bold=True, color="000000")

    for row_offset, entry in enumerate(entries, start=2):
        c_code = COLLEGE_CODES.get(entry.college_id, 6000 + entry.college_id)
        b_num  = BRANCH_NUMS.get(entry.branch_code, "19110")
        choice_code = f"{c_code}{b_num}"

        row_data = [
            entry.rank,
            choice_code,
            entry.college_name,
            entry.branch_name,
            entry.district,
            entry.category_code,
            entry.classification,
        ]

        for col_idx, value in enumerate(row_data, start=1):
            cell = ws.cell(row=row_offset, column=col_idx, value=value)
            cell.border = _col_border()
            cell.font = bold_data_font if col_idx in [1, 2] else data_font
            
            # Alignments (numbers/codes center, names left)
            cell.alignment = Alignment(
                horizontal="center" if col_idx in [1, 2, 5, 6, 7] else "left",
                vertical="center",
                wrap_text=True,
            )

        ws.row_dimensions[row_offset].height = 24

    # Apply auto-filter on all data
    ws.auto_filter.ref = f"A1:G{1 + len(entries)}"

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
