"""
core/ranker.py
--------------
Generates the correctly-ordered CAP preference list for a student.

Ordering logic (critical — this is the whole point of the product):
  1. Reach   (best colleges first, by weighted score)
  2. Match   (best first)
  3. Safe    (best first)

This ensures the CAP algorithm tries the student's best realistic options
before falling back to safer ones — fixing the most common student mistake.

Weighted score formula:
  score = feasibility * W_FEASIBILITY
        + location_match * W_LOCATION
        + branch_match * W_BRANCH
        + quality * W_QUALITY
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from core.classifier import classify, feasibility_score, Classification

# Scoring weights
W_FEASIBILITY = 0.50
W_LOCATION    = 0.20
W_BRANCH      = 0.20
W_QUALITY     = 0.10

# Tier sort order (lower number = earlier in the final list)
TIER_ORDER = {"Reach": 0, "Match": 1, "Safe": 2, "Explore": 3}


@dataclass
class CollegeEntry:
    """A single entry in the student's preference list."""
    rank: int                   = 0   # Final CAP list position (1-indexed)
    college_id: int             = 0
    college_name: str           = ""
    district: str               = ""
    branch_id: int              = 0
    branch_name: str            = ""
    branch_code: str            = ""
    category_code: str          = ""
    classification: Classification = "Match"
    predicted_closing: float    = 0.0
    lower_bound: float          = 0.0
    upper_bound: float          = 0.0
    total_seats: int            = 60
    nirf_rank_proxy: int        = 10
    model_used: str             = ""
    composite_score: float      = 0.0
    feasibility: float          = 0.0
    explanation: str            = ""


@dataclass
class StudentProfile:
    percentile: float
    category_code: str
    preferred_districts: List[str] = field(default_factory=list)    # ordered preference
    preferred_branch_codes: List[str] = field(default_factory=list) # ordered preference


def _location_score(district: str, preferred_districts: List[str]) -> float:
    """1.0 for top preference, graded down; 0.2 if not in list."""
    if not preferred_districts:
        return 0.5  # neutral if student has no preference
    for i, pref in enumerate(preferred_districts):
        if pref.strip().lower() == district.strip().lower():
            return max(0.4, 1.0 - i * 0.15)
    return 0.2


def _branch_score(branch_code: str, preferred_branch_codes: List[str]) -> float:
    """1.0 for top branch preference, graded down; 0.3 if not in list."""
    if not preferred_branch_codes:
        return 0.5
    for i, pref in enumerate(preferred_branch_codes):
        if pref.strip().upper() == branch_code.strip().upper():
            return max(0.4, 1.0 - i * 0.12)
    return 0.3


def _quality_score(nirf_rank_proxy: int, max_rank: int = 20) -> float:
    """Normalize rank: rank 1 → 1.0, rank 20 → 0.05."""
    return round(1.0 - (nirf_rank_proxy - 1) / max(max_rank - 1, 1), 3)


def rank_list(
    candidates: List[Dict],
    student: StudentProfile,
    max_reach: int = 8,
    max_match: int = 20,
    max_safe: int = 8,
) -> List[CollegeEntry]:
    """
    Takes a list of candidate college-branch combos (with predictions) and
    returns the correctly ordered CAP preference list.

    Each candidate dict must have:
        college_id, college_name, district, nirf_rank_proxy,
        branch_id, branch_name, branch_code,
        category_code, predicted_closing, lower_bound, upper_bound,
        total_seats, model_used

    Returns: ordered list of CollegeEntry objects (Reach → Match → Safe).
    """
    entries: Dict[str, List[CollegeEntry]] = {
        "Reach": [], "Match": [], "Safe": [], "Explore": []
    }

    for c in candidates:
        # Exclude low-cutoff colleges below the student's score (keep exact merit & higher merit colleges)
        if c["predicted_closing"] < (student.percentile - 1.0):
            continue

        tier = classify(
            student.percentile, c["lower_bound"], c["upper_bound"]
        )
        if tier is None:
            continue  # Out of range — skip

        feat  = feasibility_score(student.percentile, c["lower_bound"], c["upper_bound"])
        loc   = _location_score(c["district"], student.preferred_districts)
        brnch = _branch_score(c["branch_code"], student.preferred_branch_codes)
        qual  = _quality_score(c["nirf_rank_proxy"])

        score = (
            feat  * W_FEASIBILITY +
            loc   * W_LOCATION    +
            brnch * W_BRANCH      +
            qual  * W_QUALITY
        )

        entry = CollegeEntry(
            college_id        = c["college_id"],
            college_name      = c["college_name"],
            district          = c["district"],
            branch_id         = c["branch_id"],
            branch_name       = c["branch_name"],
            branch_code       = c["branch_code"],
            category_code     = c["category_code"],
            classification    = tier,
            predicted_closing = c["predicted_closing"],
            lower_bound       = c["lower_bound"],
            upper_bound       = c["upper_bound"],
            total_seats       = c.get("total_seats", 60),
            nirf_rank_proxy   = c.get("nirf_rank_proxy", 10),
            model_used        = c.get("model_used", ""),
            composite_score   = round(score, 4),
            feasibility       = feat,
        )
        entries[tier].append(entry)

    # Sort within each tier: highest composite_score first (best college in tier)
    for tier in entries:
        entries[tier].sort(key=lambda e: e.composite_score, reverse=True)

    # Trim to limits
    reach_entries = entries["Reach"][:max_reach]
    match_entries = entries["Match"][:max_match]
    safe_entries  = entries["Safe"][:max_safe]
    explore_entries = entries["Explore"][:max_safe]

    # Concatenate: Reach → Match → Safe (this is the key ordering)
    final = reach_entries + match_entries + safe_entries + explore_entries

    # Assign 1-indexed ranks
    for i, entry in enumerate(final, start=1):
        entry.rank = i

    return final
