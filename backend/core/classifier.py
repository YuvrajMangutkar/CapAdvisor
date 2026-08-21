"""
core/classifier.py
------------------
Classifies each (student, college-branch) pair as Reach / Match / Safe.

Logic (percentile scale: higher = better student/score):
  - 'closing_percentile' = the minimum score to get admitted (lower = easier).
  - If student_pct > upper_bound: student comfortably beats even the pessimistic
    cutoff → SAFE.
  - If lower_bound ≤ student_pct ≤ upper_bound (+ buffer): student is within the
    uncertainty range → MATCH.
  - If student_pct < lower_bound AND (lower_bound - student_pct) ≤ REACH_MARGIN:
    student is below the optimistic cutoff but not by much → REACH.
  - Below REACH_MARGIN from lower_bound → not shown.

Tunable constants:
  SAFE_BUFFER   — how many percentile points above upper_bound to be "safe"
  MATCH_BUFFER  — upper_bound + MATCH_BUFFER is still Match territory
  REACH_MARGIN  — max gap below lower_bound to still be a Reach
"""
from __future__ import annotations

from typing import Literal

Classification = Literal["Reach", "Match", "Safe", "Explore"]

SAFE_BUFFER   = 0.75
MATCH_BUFFER  = 0.50
REACH_MARGIN  = 1.50
EXPLORE_MARGIN = 15.0


def classify(
    student_pct: float,
    lower_bound: float,
    upper_bound: float,
) -> Classification | None:
    """
    Returns Reach | Match | Safe, or None if the college is out of range.

    Args:
        student_pct: Student's MHT-CET percentile (0–100, higher=better).
        lower_bound:  Optimistic predicted closing percentile (10th CI).
        upper_bound:  Pessimistic predicted closing percentile (90th CI).

    Returns:
        Classification string or None if unreachable.
    """
    if student_pct >= upper_bound + SAFE_BUFFER:
        return "Safe"
    elif student_pct >= lower_bound - MATCH_BUFFER:
        return "Match"
    elif student_pct >= lower_bound - REACH_MARGIN:
        return "Reach"
    elif student_pct >= lower_bound - EXPLORE_MARGIN:
      return "Explore"
    else:
        return None   # Too far above student's score — skip


def feasibility_score(
    student_pct: float,
    lower_bound: float,
    upper_bound: float,
) -> float:
    """
    Returns a 0–1 score representing how likely the student is to get admitted.
    Used for secondary sorting within tiers.

    Approach: linear interpolation around the predicted cutoff range.
      - student_pct >> upper_bound  → score ≈ 1.0 (definite admit)
      - student_pct ≈ predicted     → score ≈ 0.5
      - student_pct << lower_bound  → score ≈ 0.0
    """
    predicted = (lower_bound + upper_bound) / 2
    width = max(upper_bound - lower_bound, 1.0)

    # Sigmoid-like score centered on predicted cutoff
    delta = student_pct - predicted
    score = 1.0 / (1.0 + pow(2.71828, -delta / (width * 0.8)))
    return round(float(score), 4)
