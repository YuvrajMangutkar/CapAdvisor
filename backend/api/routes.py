"""
api/routes.py — FastAPI route handlers
"""
from __future__ import annotations

import io
import uuid
import os
import sys
import smtplib
import socket
from email.message import EmailMessage
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List, Optional

from api.schemas import (
    GenerateListRequest, GenerateListResponse, ContactRequest, CollegeEntryResponse,
    CollegeResponse, BranchResponse, CategoryResponse, HealthResponse,
    CompareTop5Request, CompareTop5Response, CollegeComparisonItem
)
from core.prediction_service import generate_preference_list, TARGET_YEAR
from core.college_comparison import get_enriched_metrics, generate_groq_ai_summary
from ml.predict import get_predictor

router = APIRouter(prefix="/api/v1", tags=["CAP Platform"])

SUPPORT_EMAIL = "yuvrajmangutkar70@gmail.com"

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")

CATEGORIES = [
    {"code": "GOPENH",  "label": "Open (Home University)"},
    {"code": "GOBCNH",  "label": "OBC-NCL (Home University)"},
    {"code": "GSCNH",   "label": "SC (Home University)"},
    {"code": "GSTNH",   "label": "ST (Home University)"},
    {"code": "GEWSNH",  "label": "EWS (Home University)"},
    {"code": "LOPENS",  "label": "Open (Other than Home University)"},
]

DISTRICTS = [
    "Pune", "Mumbai", "Navi Mumbai", "Thane", "Nagpur", "Aurangabad",
    "Nashik", "Kolhapur", "Solapur", "Sangli", "Satara", "Amravati",
    "Latur", "Jalgaon", "Akola"
]

BRANCHES = [
    {"code": "CE",    "name": "Computer Engineering"},
    {"code": "IT",    "name": "Information Technology"},
    {"code": "AIDS",  "name": "Artificial Intelligence & Data Science"},
    {"code": "ETE",   "name": "Electronics & Telecommunication Engg"},
    {"code": "MECH",  "name": "Mechanical Engineering"},
    {"code": "CIVIL", "name": "Civil Engineering"},
    {"code": "EE",    "name": "Electrical Engineering"},
]


@router.get("/health", response_model=HealthResponse)
def health_check():
    predictor = get_predictor()
    return {
        "status": "ok",
        "version": "1.0.0",
        "model_loaded": predictor._loaded,
    }


@router.get("/categories", response_model=List[CategoryResponse])
def list_categories():
    path = os.path.join(DATA_DIR, "categories.csv")
    if os.path.exists(path):
        categories = pd.read_csv(path)
        return [
            {"code": row["category_code"], "label": row["category_label"]}
            for _, row in categories.iterrows()
        ]
    return CATEGORIES


@router.get("/districts")
def list_districts():
    path = os.path.join(DATA_DIR, "colleges.csv")
    if os.path.exists(path):
        colleges = pd.read_csv(path)
        return {"districts": sorted(colleges["district"].dropna().unique().tolist())}
    return {"districts": DISTRICTS}


@router.get("/branches")
def list_branches():
    path = os.path.join(DATA_DIR, "branches.csv")
    if os.path.exists(path):
        branches = pd.read_csv(path)
        return {
            "branches": [
                {"code": row["branch_code"], "name": row["branch_name"]}
                for _, row in branches.iterrows()
            ]
        }
    return {"branches": BRANCHES}


@router.post("/generate-list", response_model=GenerateListResponse)
def generate_list(req: GenerateListRequest):
    """
    Core endpoint: given a student profile, return a correctly ordered
    CAP preference list (Reach → Match → Safe).
    """
    try:
        entries = generate_preference_list(
            percentile=req.percentile,
            category_code=req.category_code,
            preferred_districts=req.preferred_districts,
            preferred_branch_codes=req.preferred_branch_codes,
            max_reach=req.max_reach,
            max_match=req.max_match,
            max_safe=req.max_safe,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not entries:
        raise HTTPException(
            status_code=404,
            detail="No colleges found matching your criteria. Try relaxing branch or district filters."
        )

    session_id = str(uuid.uuid4())

    reach_count = sum(1 for e in entries if e.classification == "Reach")
    match_count = sum(1 for e in entries if e.classification == "Match")
    safe_count  = sum(1 for e in entries if e.classification == "Safe")
    explore_count = sum(1 for e in entries if e.classification == "Explore")

    return GenerateListResponse(
        session_id=session_id,
        student_percentile=req.percentile,
        category_code=req.category_code,
        target_year=TARGET_YEAR,
        total_entries=len(entries),
        reach_count=reach_count,
        match_count=match_count,
        safe_count=safe_count,
        explore_count=explore_count,
        entries=[
            CollegeEntryResponse(
                rank=e.rank,
                college_id=e.college_id,
                college_name=e.college_name,
                district=e.district,
                branch_id=e.branch_id,
                branch_name=e.branch_name,
                branch_code=e.branch_code,
                category_code=e.category_code,
                classification=e.classification,
                predicted_closing=e.predicted_closing,
                lower_bound=e.lower_bound,
                upper_bound=e.upper_bound,
                total_seats=e.total_seats,
                nirf_rank_proxy=e.nirf_rank_proxy,
                composite_score=e.composite_score,
                feasibility=e.feasibility,
                model_used=e.model_used,
                explanation=e.explanation,
            )
            for e in entries
        ],
    )


@router.post("/compare-top5", response_model=CompareTop5Response)
def compare_top5_colleges(req: CompareTop5Request):
    """
    Enriches top 5 matched colleges with placement stats, recruiters,
    lab quality ratings, campus image galleries, and generates AI insights.
    """
    top_5 = req.top_entries[:5]
    if not top_5:
        raise HTTPException(status_code=400, detail="No college entries provided for comparison")

    comparison_items = []
    enriched_for_ai = []

    for entry in top_5:
        metrics = get_enriched_metrics(entry.college_name)
        item = CollegeComparisonItem(
            rank=entry.rank,
            college_id=entry.college_id,
            college_name=entry.college_name,
            district=entry.district,
            branch_name=entry.branch_name,
            branch_code=entry.branch_code,
            predicted_closing=entry.predicted_closing,
            nirf_rank_proxy=entry.nirf_rank_proxy,
            placement_rate=metrics["placement_rate"],
            avg_package_lpa=metrics["avg_package_lpa"],
            highest_package_lpa=metrics["highest_package_lpa"],
            top_recruiters=metrics["top_recruiters"],
            lab_quality_rating=metrics["lab_quality_rating"],
            infrastructure_rating=metrics["infrastructure_rating"],
            image_url=metrics["image_url"],
            highlights=metrics["highlights"],
            data_source=metrics.get("data_source", "Verified snapshot"),
            fetched_at=metrics.get("fetched_at"),
        )
        comparison_items.append(item)
        enriched_for_ai.append(item.model_dump())

    ai_summary = generate_groq_ai_summary(
        student_percentile=req.student_percentile,
        category_code=req.category_code,
        top_colleges=enriched_for_ai
    )

    return CompareTop5Response(
        student_percentile=req.student_percentile,
        category_code=req.category_code,
        comparison_items=comparison_items,
        ai_decision_summary=ai_summary
    )


@router.post("/contact")
def contact_support(req: ContactRequest):
    """Validate and deliver a support message through the configured SMTP server."""
    domain = req.email.rsplit("@", 1)[1]
    try:
        socket.getaddrinfo(domain, 25, type=socket.SOCK_STREAM)
    except socket.gaierror:
        raise HTTPException(status_code=422, detail="That email domain does not exist")

    smtp_host = os.getenv("SMTP_HOST")
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    if not smtp_host or not smtp_username or not smtp_password:
        raise HTTPException(status_code=503, detail="Support email delivery is not configured")

    try:
        message = EmailMessage()
        message["From"] = os.getenv("SMTP_FROM_EMAIL", smtp_username)
        message["To"] = SUPPORT_EMAIL
        message["Reply-To"] = req.email
        message["Subject"] = f"CAP Advisor: {req.subject}"
        message.set_content(f"Name: {req.name}\nEmail: {req.email}\n\n{req.message}")

        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)
    except (OSError, ValueError, smtplib.SMTPException) as exc:
        raise HTTPException(status_code=502, detail="The support email could not be sent") from exc

    return {"message": "Your message was sent successfully"}


@router.get("/export/excel")
def export_excel(
    percentile: float = Query(...),
    category_code: str = Query(...),
    preferred_districts: str = Query(default=""),
    preferred_branch_codes: str = Query(default=""),
):
    """Generate and download a color-coded Excel preference list."""
    from export.excel_exporter import generate_excel

    districts = [d.strip() for d in preferred_districts.split(",") if d.strip()]
    branches  = [b.strip() for b in preferred_branch_codes.split(",") if b.strip()]

    entries = generate_preference_list(
        percentile=percentile,
        category_code=category_code,
        preferred_districts=districts,
        preferred_branch_codes=branches,
    )

    buffer = generate_excel(entries, student_percentile=percentile, category=category_code)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=CAP_Preference_List.xlsx"},
    )


@router.get("/export/pdf")
def export_pdf(
    percentile: float = Query(...),
    category_code: str = Query(...),
    preferred_districts: str = Query(default=""),
    preferred_branch_codes: str = Query(default=""),
):
    """Generate and download a PDF preference list."""
    from export.pdf_exporter import generate_pdf

    districts = [d.strip() for d in preferred_districts.split(",") if d.strip()]
    branches  = [b.strip() for b in preferred_branch_codes.split(",") if b.strip()]

    entries = generate_preference_list(
        percentile=percentile,
        category_code=category_code,
        preferred_districts=districts,
        preferred_branch_codes=branches,
    )

    buffer = generate_pdf(entries, student_percentile=percentile, category=category_code)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=CAP_Preference_List.pdf"},
    )
