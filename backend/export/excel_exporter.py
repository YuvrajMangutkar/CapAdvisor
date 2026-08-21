"""
export/excel_exporter.py — Generate color-coded openpyxl Excel file
"""
from __future__ import annotations

import io
from typing import List
from datetime import datetime

import openpyxl
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side, GradientFill
)
from openpyxl.utils import get_column_letter

TIER_COLORS = {
    "Reach": {"fill": "FFF3CD", "font": "856404", "badge": "FF8C00"},
    "Match": {"fill": "D1E7DD", "font": "0A3622", "badge": "198754"},
    "Safe":  {"fill": "CFE2FF", "font": "084298", "badge": "0D6EFD"},
    "Explore": {"fill": "E2E8F0", "font": "334155", "badge": "64748B"},
}

HEADER_FILL = "1A1A2E"
HEADER_FONT = "FFFFFF"


def _col_border():
    thin = Side(style="thin", color="DEE2E6")
    return Border(left=thin, right=thin, top=thin, bottom=thin)


def generate_excel(
    entries: list,
    student_percentile: float,
    category: str,
) -> io.BytesIO:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "CAP Preference List"

    # ── Title row ──────────────────────────────────────────────────────────────
    ws.merge_cells("A1:F1")
    title_cell = ws["A1"]
    title_cell.value = f"CAP Round 2025 — College Preference List"
    title_cell.font = Font(name="Calibri", bold=True, size=14, color=HEADER_FONT)
    title_cell.fill = PatternFill("solid", fgColor=HEADER_FILL)
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    # ── Subtitle ───────────────────────────────────────────────────────────────
    ws.merge_cells("A2:F2")
    sub = ws["A2"]
    sub.value = (
        f"Student Percentile: {student_percentile:.2f}  |  "
        f"Category: {category}  |  "
        f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}"
    )
    sub.font = Font(name="Calibri", italic=True, size=10, color="555555")
    sub.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 20

    # ── Legend ─────────────────────────────────────────────────────────────────
    ws.merge_cells("A3:F3")
    legend = ws["A3"]
    legend.value = (
        "Legend:   REACH = possible but competitive   |   "
        "MATCH = realistic chance   |   SAFE = very high probability"
    )
    legend.font = Font(name="Calibri", size=9, color="666666")
    legend.alignment = Alignment(horizontal="center")
    ws.row_dimensions[3].height = 18

    # ── Column Headers ─────────────────────────────────────────────────────────
    headers = [
        "Preference No.", "College Name", "District", "Branch",
        "Category", "Option Type"
    ]
    col_widths = [14, 45, 14, 36, 12, 14]

    for col_idx, (header, width) in enumerate(zip(headers, col_widths), start=1):
        cell = ws.cell(row=4, column=col_idx, value=header)
        cell.font = Font(name="Calibri", bold=True, size=10, color=HEADER_FONT)
        cell.fill = PatternFill("solid", fgColor="16213E")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = _col_border()
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    ws.row_dimensions[4].height = 36
    ws.freeze_panes = "A5"

    # ── Data Rows ──────────────────────────────────────────────────────────────
    for row_idx, entry in enumerate(entries, start=5):
        tier = entry.classification
        colors = TIER_COLORS[tier]
        fill = PatternFill("solid", fgColor=colors["fill"])
        font = Font(name="Calibri", size=9, color=colors["font"])
        bold_font = Font(name="Calibri", size=9, bold=True, color=colors["font"])

        row_data = [
            entry.rank,
            entry.college_name,
            entry.district,
            entry.branch_name,
            entry.category_code,
            tier,
        ]

        for col_idx, value in enumerate(row_data, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.fill = fill
            cell.border = _col_border()
            cell.alignment = Alignment(
                horizontal="center" if col_idx not in [2, 4] else "left",
                vertical="top",
                wrap_text=True,
            )
            if col_idx in [1, 6]:
                cell.font = bold_font
            else:
                cell.font = font

        ws.row_dimensions[row_idx].height = 42

    # ── Freeze + auto-filter ───────────────────────────────────────────────────
    ws.auto_filter.ref = f"A4:F{4 + len(entries)}"

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
