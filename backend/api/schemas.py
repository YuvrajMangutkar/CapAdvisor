"""
api/schemas.py — Pydantic request/response models
"""
from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


# ── Request Schemas ────────────────────────────────────────────────────────────

class GenerateListRequest(BaseModel):
    percentile: float = Field(
        ..., ge=0.0, le=100.0,
        description="Student's MHT-CET percentile (0–100)"
    )
    category_code: str = Field(
        ..., pattern="^(GOPENH|GOBCNH|GSCNH|GSTNH|GEWSNH|LOPENS)$",
        description="Admission category code"
    )
    preferred_districts: List[str] = Field(
        default=[],
        description="Preferred districts in order of preference",
        max_length=10
    )
    preferred_branch_codes: List[str] = Field(
        default=[],
        description="Preferred branch codes in priority order (e.g. ['CE','IT','AIDS'])",
        max_length=7
    )
    max_reach: int = Field(default=100, ge=1, le=200)
    max_match: int = Field(default=100, ge=1, le=200)
    max_safe:  int = Field(default=100, ge=1, le=200)

    @field_validator("preferred_branch_codes", mode="before")
    @classmethod
    def uppercase_branches(cls, v):
        return [b.upper() for b in v] if v else v


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: str = Field(..., min_length=5, max_length=254)
    subject: str = Field(..., min_length=3, max_length=180)
    message: str = Field(..., min_length=10, max_length=5000)

    @field_validator("name", "subject", "message")
    @classmethod
    def strip_text(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()
        if "\n" in value or "\r" in value or value.count("@") != 1:
            raise ValueError("Enter a valid email address")
        local, domain = value.rsplit("@", 1)
        if not local or not domain or "." not in domain or " " in value:
            raise ValueError("Enter a valid email address")
        return value


# ── Response Schemas ───────────────────────────────────────────────────────────

class CollegeEntryResponse(BaseModel):
    rank: int
    college_id: int
    college_name: str
    district: str
    branch_id: int
    branch_name: str
    branch_code: str
    category_code: str
    classification: Literal["Reach", "Match", "Safe", "Explore"]
    predicted_closing: float
    lower_bound: float
    upper_bound: float
    total_seats: int
    nirf_rank_proxy: int
    composite_score: float
    feasibility: float
    model_used: str
    explanation: str

    model_config = {"from_attributes": True}


class GenerateListResponse(BaseModel):
    session_id: str
    student_percentile: float
    category_code: str
    target_year: int
    total_entries: int
    reach_count: int
    match_count: int
    safe_count: int
    explore_count: int
    entries: List[CollegeEntryResponse]


class CollegeResponse(BaseModel):
    college_id: int
    college_name: str
    district: str
    college_type: str
    nirf_rank_proxy: int

    model_config = {"from_attributes": True}


class BranchResponse(BaseModel):
    branch_id: int
    branch_name: str
    branch_code: str
    demand_factor: float

    model_config = {"from_attributes": True}


class CategoryResponse(BaseModel):
    code: str
    label: str


class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool


class CompareTop5Request(BaseModel):
    student_percentile: float = Field(..., ge=0.0, le=100.0)
    category_code: str
    top_entries: List[CollegeEntryResponse]


class CollegeComparisonItem(BaseModel):
    rank: int
    college_id: int
    college_name: str
    district: str
    branch_name: str
    branch_code: str
    predicted_closing: float
    nirf_rank_proxy: int
    placement_rate: float
    avg_package_lpa: float
    highest_package_lpa: float
    top_recruiters: List[str]
    lab_quality_rating: float
    infrastructure_rating: float
    image_url: str
    highlights: str
    data_source: str = "Verified snapshot"
    fetched_at: Optional[str] = None


class CompareTop5Response(BaseModel):
    student_percentile: float
    category_code: str
    comparison_items: List[CollegeComparisonItem]
    ai_decision_summary: str
