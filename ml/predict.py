"""
ml/predict.py — Inference wrapper for cutoff prediction.

Priority:
  1. LightGBM model files (if trained and available)
  2. Weighted-average fallback (no model file needed)

This module is imported by the backend at startup.
"""
from __future__ import annotations

import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
DATA_DIR   = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

# Weights for weighted-average fallback (more recent = higher weight)
YEAR_WEIGHTS = {2022: 0.15, 2023: 0.25, 2024: 0.35, 2025: 0.25}

# CI width for weighted-average fallback (no quantile model)
FALLBACK_CI_HALF_WIDTH = 2.5


@dataclass
class PredictionResult:
    predicted_closing: float
    lower_bound: float
    upper_bound: float
    model_used: str
    confidence: float  # 0–1 heuristic


class CutoffPredictor:
    """Loads ML models once at startup and provides fast inference."""

    def __init__(self):
        self._model_mean  = None
        self._model_lo    = None
        self._model_hi    = None
        self._feature_cols: List[str] = []
        self._meta: Dict = {}
        self._cutoffs_df: Optional[pd.DataFrame] = None
        self._branches_df: Optional[pd.DataFrame] = None
        self._colleges_df: Optional[pd.DataFrame] = None
        self._loaded = False
        self._load()

    def _load(self):
        meta_path = os.path.join(MODELS_DIR, "model_meta.json")
        mean_path = os.path.join(MODELS_DIR, "cutoff_mean.joblib")

        if os.path.exists(meta_path) and os.path.exists(mean_path):
            try:
                with open(meta_path) as f:
                    self._meta = json.load(f)
                self._feature_cols = self._meta.get("feature_cols", [])
                self._model_mean = joblib.load(mean_path)
                lo_path = os.path.join(MODELS_DIR, "cutoff_lower.joblib")
                hi_path = os.path.join(MODELS_DIR, "cutoff_upper.joblib")
                if os.path.exists(lo_path):
                    self._model_lo = joblib.load(lo_path)
                if os.path.exists(hi_path):
                    self._model_hi = joblib.load(hi_path)
                self._loaded = True
            except Exception as exc:
                # The model files may have been serialized with an incompatible NumPy
                # BitGenerator / joblib stack. In that case, we intentionally fall back
                # to the historical weighted-average predictor instead of crashing startup.
                self._model_mean = None
                self._model_lo = None
                self._model_hi = None
                self._loaded = False
                self._meta = {}
                self._feature_cols = []
                print(f"[WARN] Unable to load saved model files; using weighted fallback. Details: {exc}")

        # Always load reference CSVs for the weighted-avg fallback
        try:
            self._cutoffs_df  = pd.read_csv(os.path.join(DATA_DIR, "cutoffs.csv"))
            self._branches_df = pd.read_csv(os.path.join(DATA_DIR, "branches.csv"))
            self._colleges_df = pd.read_csv(os.path.join(DATA_DIR, "colleges.csv"))
        except FileNotFoundError:
            pass  # Will fail gracefully if CSVs not present

    def _weighted_avg_predict(
        self, college_id: int, branch_id: int, category_code: str, target_year: int
    ) -> PredictionResult:
        """
        Fallback: weighted average of last 3 years' Round 1 closing percentile.
        CI = mean ± FALLBACK_CI_HALF_WIDTH * std_factor
        """
        if self._cutoffs_df is None:
            raise RuntimeError("No cutoffs CSV and no trained model available.")

        df = self._cutoffs_df
        hist = df[
            (df["college_id"] == college_id)
            & (df["branch_id"] == branch_id)
            & (df["category_code"] == category_code)
        ].copy()

        if hist.empty:
            # Fall back to overall mean for this branch at this college (any category, any year, Round 1)
            hist = df[
                (df["college_id"] == college_id)
                & (df["branch_id"] == branch_id)
            ].copy()

        if hist.empty:
            raise ValueError(f"No historical data for college_id={college_id}, branch_id={branch_id}")

        total_weight = 0.0
        weighted_sum = 0.0
        values = []
        for _, row in hist.iterrows():
            w = YEAR_WEIGHTS.get(int(row["year"]), 0.10)
            weighted_sum += w * row["closing_percentile"]
            total_weight += w
            values.append(row["closing_percentile"])

        predicted = weighted_sum / max(total_weight, 1e-9)

        # CI based on historical std
        std = float(np.std(values)) if len(values) > 1 else FALLBACK_CI_HALF_WIDTH
        ci = max(std * 1.5, 1.0)
        lower = max(10.0, predicted - ci)
        upper = min(99.99, predicted + ci)

        # Trend adjustment: use YoY delta of last two years if available
        if len(values) >= 2:
            trend = values[-1] - values[-2]  # last vs second-to-last
            predicted = min(99.99, max(10.0, predicted + trend * 0.3))

        return PredictionResult(
            predicted_closing=round(predicted, 2),
            lower_bound=round(lower, 2),
            upper_bound=round(upper, 2),
            model_used="weighted_avg_fallback",
            confidence=0.65,
        )

    def predict(
        self,
        college_id: int,
        branch_id: int,
        category_code: str,
        target_year: int,
        features: Optional[np.ndarray] = None,
    ) -> PredictionResult:
        """
        Return (predicted_closing, lower_bound, upper_bound).

        If ML models are loaded and features provided, use them.
        Otherwise, fall back to weighted average.
        """
        if self._loaded and features is not None:
            try:
                feats = features.reshape(1, -1)
                mean_pred = float(self._model_mean.predict(feats)[0])
                lo = float(self._model_lo.predict(feats)[0]) if self._model_lo else mean_pred - FALLBACK_CI_HALF_WIDTH
                hi = float(self._model_hi.predict(feats)[0]) if self._model_hi else mean_pred + FALLBACK_CI_HALF_WIDTH
                # Clamp and ensure lo < mean < hi
                lo = max(10.0, min(lo, mean_pred - 0.5))
                hi = min(99.99, max(hi, mean_pred + 0.5))
                model_kind = "lightgbm" if self._meta.get("has_lightgbm") else "hist_gradient_boosting"
                return PredictionResult(
                    predicted_closing=round(mean_pred, 2),
                    lower_bound=round(lo, 2),
                    upper_bound=round(hi, 2),
                    model_used=f"{model_kind}_{self._meta.get('target_year', target_year)}",
                    confidence=0.80,
                )
            except Exception as e:
                pass  # fallthrough to weighted avg

        return self._weighted_avg_predict(college_id, branch_id, category_code, target_year)


# Singleton — loaded once when module is imported
_predictor: Optional[CutoffPredictor] = None


def get_predictor() -> CutoffPredictor:
    global _predictor
    if _predictor is None:
        _predictor = CutoffPredictor()
    return _predictor
