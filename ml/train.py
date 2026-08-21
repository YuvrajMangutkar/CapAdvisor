"""
ml/train.py — Train LightGBM quantile regression models for cutoff prediction.

Trains two models:
  - alpha=0.10 → lower_bound (optimistic cutoff)
  - alpha=0.90 → upper_bound (pessimistic cutoff)

Also trains a mean prediction model (objective=regression).

Usage:
    python ml/train.py

Outputs model files to ml/models/
"""
from __future__ import annotations

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    import lightgbm as lgb
    HAS_LGB = True
except ImportError:
    HAS_LGB = False
    print("[WARN] lightgbm not installed. Using sklearn HistGradientBoosting fallback.")
    from sklearn.ensemble import HistGradientBoostingRegressor

from ml.features import build_feature_matrix, FEATURE_COLS

DATA_DIR   = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)


def load_data() -> pd.DataFrame:
    cutoffs   = pd.read_csv(os.path.join(DATA_DIR, "cutoffs.csv"))
    colleges  = pd.read_csv(os.path.join(DATA_DIR, "colleges.csv"))
    branches  = pd.read_csv(os.path.join(DATA_DIR, "branches.csv"))

    # Merge to get nirf_rank_proxy and demand_factor
    df = cutoffs.merge(
        branches[["branch_id", "branch_code", "demand_factor"]],
        on="branch_id", how="left"
    ).merge(
        colleges[["college_id", "nirf_rank_proxy"]],
        on="college_id", how="left"
    )
    return df


def train_model(X_train, y_train, alpha: float | None = None):
    """Train a single LightGBM model (quantile or regression)."""
    if HAS_LGB:
        if alpha is not None:
            params = dict(
                objective="quantile",
                alpha=alpha,
                n_estimators=400,
                learning_rate=0.05,
                num_leaves=31,
                min_child_samples=5,
                subsample=0.8,
                colsample_bytree=0.8,
                verbose=-1,
            )
        else:
            params = dict(
                objective="regression",
                n_estimators=400,
                learning_rate=0.05,
                num_leaves=31,
                min_child_samples=5,
                subsample=0.8,
                colsample_bytree=0.8,
                verbose=-1,
            )
        model = lgb.LGBMRegressor(**params)
    else:
        # sklearn fallback — HistGradientBoosting handles NaN natively
        model = HistGradientBoostingRegressor(
            max_iter=200, learning_rate=0.05, max_depth=5
        )

    model.fit(X_train, y_train)
    return model


def evaluate(model, X_test, y_test, label: str) -> dict:
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2  = r2_score(y_test, preds)
    print(f"  [{label}] MAE={mae:.3f}  R2={r2:.3f}")
    return {"label": label, "mae": mae, "r2": r2}


def main():
    print("Loading data...")
    df = load_data()

    print(f"Building feature matrix from {len(df)} rows...")
    feat_df = build_feature_matrix(df)
    print(f"Feature matrix: {len(feat_df)} rows after dropping NaN lags")

    X = feat_df[FEATURE_COLS].values
    y = feat_df["target"].values
    groups = feat_df["branch_id"].values  # group by branch for cross-val




    # Leave-one-year-out cross-validation (if multiple years available)
    years = sorted(feat_df["year"].unique())
    if len(years) > 1:
        test_year = years[-1]  # most recent year as test set
        train_mask = feat_df["year"] < test_year
        test_mask  = feat_df["year"] == test_year
    else:
        # Single year: use 70/30 train/test split
        from sklearn.model_selection import train_test_split
        test_year = years[0]
        indices = np.arange(len(X))
        train_idx, test_idx = train_test_split(
            indices, test_size=0.3, random_state=42
        )
        train_mask = np.zeros(len(X), dtype=bool)
        test_mask = np.zeros(len(X), dtype=bool)
        train_mask[train_idx] = True
        test_mask[test_idx] = True

    X_train, y_train = X[train_mask], y[train_mask]
    X_test,  y_test  = X[test_mask],  y[test_mask]

    print(f"Train: {train_mask.sum()} rows | Test (year={test_year}): {test_mask.sum()} rows")
    results = []

    # ── Mean prediction model ──────────────────────────────────────────────────
    print("\nTraining mean prediction model...")
    model_mean = train_model(X_train, y_train, alpha=None)
    results.append(evaluate(model_mean, X_test, y_test, "mean"))
    joblib.dump(model_mean, os.path.join(MODELS_DIR, "cutoff_mean.joblib"))

    # ── Lower bound model (alpha=0.10) ────────────────────────────────────────
    print("Training lower bound model (alpha=0.10)...")
    model_lo = train_model(X_train, y_train, alpha=0.10)
    results.append(evaluate(model_lo, X_test, y_test, "lower_bound"))
    joblib.dump(model_lo, os.path.join(MODELS_DIR, "cutoff_lower.joblib"))

    # ── Upper bound model (alpha=0.90) ────────────────────────────────────────
    print("Training upper bound model (alpha=0.90)...")
    model_hi = train_model(X_train, y_train, alpha=0.90)
    results.append(evaluate(model_hi, X_test, y_test, "upper_bound"))
    joblib.dump(model_hi, os.path.join(MODELS_DIR, "cutoff_upper.joblib"))

    # Save metadata
    meta = {
        "trained_on_years": sorted(feat_df["year"].unique().tolist()),
        "test_year": int(test_year),
        "target_year": int(test_year) + 1,
        "feature_cols": FEATURE_COLS,
        "has_lightgbm": HAS_LGB,
        "results": results,
    }
    with open(os.path.join(MODELS_DIR, "model_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\nModels saved to {MODELS_DIR}/")
    print("Training complete.")


if __name__ == "__main__":
    main()
