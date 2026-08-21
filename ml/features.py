"""
ml/features.py — Feature engineering for cutoff prediction model
"""
from __future__ import annotations

import pandas as pd
import numpy as np
from typing import List, Dict


HISTORY_YEARS = [2022, 2023, 2024]   # years we have data for

CATEGORY_DISCOUNTS = {
    "GOPENH": 0.0,
    "GOBCNH": 6.0,
    "GSCNH": 18.0,
    "GSTNH": 28.0,
    "GEWSNH": 3.5,
    "LOPENS": 2.5,
}


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a feature matrix from the historical cutoffs DataFrame.

    Input columns expected:
        college_id, branch_id, category_code, year, round,
        closing_percentile, total_seats, filled_seats,
        nirf_rank_proxy, demand_factor

    Returns a DataFrame with ML-ready features + 'target' column.
    """
    df = df.copy()
    df = df.sort_values(["branch_id", "category_code", "year", "round"])

    # ── Lag features (previous years' closing percentile) ─────────────────────
    grp = df.groupby(["branch_id", "category_code", "round"])
    df["closing_lag1"] = grp["closing_percentile"].shift(1)
    df["closing_lag2"] = grp["closing_percentile"].shift(2)
    df["closing_lag3"] = grp["closing_percentile"].shift(3)

    # ── Rolling stats ──────────────────────────────────────────────────────────
    df["closing_roll2_mean"] = grp["closing_percentile"].transform(
        lambda x: x.shift(1).rolling(2).mean()
    )
    df["closing_roll3_mean"] = grp["closing_percentile"].transform(
        lambda x: x.shift(1).rolling(3).mean()
    )

    # ── Year-over-year trend ───────────────────────────────────────────────────
    df["yoy_delta"] = df["closing_percentile"] - df["closing_lag1"]

    # ── Fill rate (demand signal) ──────────────────────────────────────────────
    df["fill_rate"] = df["filled_seats"] / df["total_seats"].clip(lower=1)

    # ── Category discount (encode as numeric) ─────────────────────────────────
    df["category_discount"] = df["category_code"].map(CATEGORY_DISCOUNTS).fillna(5.0)

    # ── Encode round as numeric ───────────────────────────────────────────────
    df["round_num"] = df["round"].astype(float)

    # ── Normalized rank (college quality proxy, lower=better) ─────────────────
    max_rank = df["nirf_rank_proxy"].max()
    df["rank_norm"] = 1.0 - (df["nirf_rank_proxy"] - 1) / max(max_rank - 1, 1)

    # ── Branch demand factor (numeric) ────────────────────────────────────────
    # Already present as demand_factor

    # Drop rows without lag features (first year has NaN lags)
    df = df.dropna(subset=["closing_lag1"])

    # ── Target: closing percentile for prediction ──────────────────────────────
    df = df.rename(columns={"closing_percentile": "target"})

    return df


def build_inference_features(
    history: pd.DataFrame,
    college_id: int,
    branch_id: int,
    category_code: str,
    round_num: int,
    target_year: int,
) -> np.ndarray:
    """Build one model feature row for a future year and CAP round."""
    rows = history[
        (history["college_id"] == college_id)
        & (history["branch_id"] == branch_id)
        & (history["category_code"] == category_code)
        & (history["round"] == round_num)
    ].sort_values("year")
    if rows.empty:
        rows = history[
            (history["college_id"] == college_id)
            & (history["branch_id"] == branch_id)
            & (history["round"] == round_num)
        ].sort_values("year")
    if rows.empty:
        raise ValueError("No historical cutoff rows for this college, branch, and round")

    values = rows["closing_percentile"].astype(float).tolist()
    lag1 = values[-1]
    lag2 = values[-2] if len(values) > 1 else lag1
    rank = float(rows["nirf_rank_proxy"].iloc[-1])
    max_rank = max(float(history["nirf_rank_proxy"].max()), 2.0)
    seats = float(rows["total_seats"].iloc[-1])
    return np.array([
        lag1, lag2,
        float(np.mean(values[-2:])), float(np.mean(values[-3:])),
        lag1 - lag2,
        float(rows["filled_seats"].iloc[-1]) / max(seats, 1.0),
        CATEGORY_DISCOUNTS.get(category_code, 5.0), float(round_num),
        1.0 - (rank - 1.0) / (max_rank - 1.0),
        float(rows["demand_factor"].iloc[-1]), seats,
    ], dtype=float)


FEATURE_COLS = [
    "closing_lag1",
    "closing_lag2",
    "closing_roll2_mean",
    "closing_roll3_mean",
    "yoy_delta",
    "fill_rate",
    "category_discount",
    "round_num",
    "rank_norm",
    "demand_factor",
    "total_seats",
]
