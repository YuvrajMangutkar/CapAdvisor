"""
core/prediction_service.py
--------------------------
Orchestrates the full pipeline:
  CSV data → ML predictions → Reach/Match/Safe classification → Ranked list

Used by the API layer.
"""
from __future__ import annotations

import os
import sys
import pandas as pd
from typing import List, Dict, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ml.predict import get_predictor
from ml.features import build_inference_features
from core.classifier import classify
from core.ranker import rank_list, StudentProfile, CollegeEntry
from core.explainer import explain_batch

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")

# Cache DataFrames at module level (loaded once)
_colleges_df: Optional[pd.DataFrame] = None
_branches_df: Optional[pd.DataFrame] = None
_cutoffs_df:  Optional[pd.DataFrame] = None


def _load_data():
    global _colleges_df, _branches_df, _cutoffs_df
    if _colleges_df is None:
        _colleges_df = pd.read_csv(os.path.join(DATA_DIR, "colleges.csv"))
        _branches_df = pd.read_csv(os.path.join(DATA_DIR, "branches.csv"))
        _cutoffs_df  = pd.read_csv(os.path.join(DATA_DIR, "cutoffs.csv"))


TARGET_YEAR = 2026


def generate_preference_list(
    percentile: float,
    category_code: str,
    preferred_districts: List[str],
    preferred_branch_codes: List[str],
    max_reach: int = 100,
    max_match: int = 100,
    max_safe: int = 100,
) -> List[CollegeEntry]:
    """
    Main service function.
    """
    _load_data()
    predictor = get_predictor()

    student = StudentProfile(
        percentile=percentile,
        category_code=category_code,
        preferred_districts=preferred_districts,
        preferred_branch_codes=preferred_branch_codes,
    )

    # Build a lookup: branch_id → branch info
    branch_lookup = {
        int(row["branch_id"]): row
        for _, row in _branches_df.iterrows()
    }

    # Build the candidate pool from (college, branch) pairs found in cutoffs
    # We use the cutoffs CSV to discover which branches exist per college
    cutoffs_summary = _cutoffs_df.groupby(
        ["college_id", "branch_id"]
    ).first().reset_index()[["college_id", "branch_id", "total_seats"]]

    college_lookup = {
        int(row["college_id"]): row
        for _, row in _colleges_df.iterrows()
    }

    candidates: List[Dict] = []

    for _, cb in cutoffs_summary.iterrows():
        c_id = int(cb["college_id"])
        b_id = int(cb["branch_id"])

        if c_id not in college_lookup or b_id not in branch_lookup:
            continue

        college = college_lookup[c_id]
        branch  = branch_lookup[b_id]
        b_code  = str(branch["branch_code"])
        district = str(college["district"])

        # Filter by district preference (if specified)
        if preferred_districts and district.lower() not in [d.lower() for d in preferred_districts]:
            continue

        # Filter by branch preference (if specified)
        if preferred_branch_codes and b_code not in [p.upper() for p in preferred_branch_codes]:
            continue

        try:
            college_ranks = (
                _colleges_df.drop_duplicates("college_id")
                .set_index("college_id")["nirf_rank_proxy"]
            )
            branch_demand = (
                _branches_df.drop_duplicates("branch_id")
                .set_index("branch_id")["demand_factor"]
            )
            enriched_cutoffs = _cutoffs_df.assign(
                nirf_rank_proxy=_cutoffs_df["college_id"].map(college_ranks),
                demand_factor=_cutoffs_df["branch_id"].map(branch_demand),
            )
            round_predictions = []
            for round_no in sorted(enriched_cutoffs["round"].unique()):
                features = build_inference_features(
                    enriched_cutoffs, c_id, b_id, category_code,
                    int(round_no), TARGET_YEAR,
                )
                round_predictions.append(
                    predictor.predict(c_id, b_id, category_code, TARGET_YEAR, features)
                )
            if not round_predictions:
                raise ValueError("No round predictions available")
            pred = type(round_predictions[0])(
                predicted_closing=sum(p.predicted_closing for p in round_predictions) / len(round_predictions),
                lower_bound=min(p.lower_bound for p in round_predictions),
                upper_bound=max(p.upper_bound for p in round_predictions),
                model_used="all_rounds_" + round_predictions[0].model_used,
                confidence=min(p.confidence for p in round_predictions),
            )
        except Exception:
            continue

        candidates.append({
            "college_id":        c_id,
            "college_name":      str(college["college_name"]),
            "district":          str(college["district"]),
            "nirf_rank_proxy":   int(college["nirf_rank_proxy"]),
            "branch_id":         b_id,
            "branch_name":       str(branch["branch_name"]),
            "branch_code":       b_code,
            "category_code":     category_code,
            "predicted_closing": pred.predicted_closing,
            "lower_bound":       pred.lower_bound,
            "upper_bound":       pred.upper_bound,
            "total_seats":       int(cb.get("total_seats", 60)),
            "model_used":        pred.model_used,
        })

    # Rank the candidates
    ranked = rank_list(
        candidates, student,
        max_reach=max_reach,
        max_match=max_match,
        max_safe=max_safe,
    )

    # Add explanations
    explain_batch(ranked)

    return ranked
