"""
db/crud.py — Database read/write operations
"""
from __future__ import annotations

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from db.models import College, Branch, Cutoff, CutoffPrediction, StudentSession


# ── Colleges ─────────────────────────────────────────────────────────────────

def get_all_colleges(db: Session) -> List[College]:
    return db.execute(select(College).order_by(College.nirf_rank_proxy)).scalars().all()


def get_college(db: Session, college_id: int) -> Optional[College]:
    return db.get(College, college_id)


# ── Branches ─────────────────────────────────────────────────────────────────

def get_branches_for_college(db: Session, college_id: int) -> List[Branch]:
    return db.execute(
        select(Branch).where(Branch.college_id == college_id)
    ).scalars().all()


def get_all_branches(db: Session) -> List[Branch]:
    return db.execute(select(Branch)).scalars().all()


# ── Cutoffs ───────────────────────────────────────────────────────────────────

def get_historical_cutoffs(
    db: Session,
    branch_id: int,
    category_code: str,
    years: Optional[List[int]] = None,
) -> List[Cutoff]:
    stmt = select(Cutoff).where(
        and_(
            Cutoff.branch_id == branch_id,
            Cutoff.category_code == category_code,
        )
    )
    if years:
        stmt = stmt.where(Cutoff.year.in_(years))
    return db.execute(stmt.order_by(Cutoff.year, Cutoff.round)).scalars().all()


def get_latest_cutoff(
    db: Session, branch_id: int, category_code: str
) -> Optional[Cutoff]:
    """Return the Round 1 cutoff from the most recent year."""
    return db.execute(
        select(Cutoff)
        .where(
            and_(
                Cutoff.branch_id == branch_id,
                Cutoff.category_code == category_code,
                Cutoff.round == 1,
            )
        )
        .order_by(Cutoff.year.desc())
        .limit(1)
    ).scalar_one_or_none()


# ── Predictions ───────────────────────────────────────────────────────────────

def upsert_prediction(db: Session, prediction: CutoffPrediction) -> CutoffPrediction:
    existing = db.execute(
        select(CutoffPrediction).where(
            and_(
                CutoffPrediction.branch_id == prediction.branch_id,
                CutoffPrediction.category_code == prediction.category_code,
                CutoffPrediction.target_year == prediction.target_year,
            )
        )
    ).scalar_one_or_none()

    if existing:
        existing.predicted_closing = prediction.predicted_closing
        existing.lower_bound = prediction.lower_bound
        existing.upper_bound = prediction.upper_bound
        existing.model_version = prediction.model_version
        db.commit()
        db.refresh(existing)
        return existing
    else:
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return prediction


def get_prediction(
    db: Session, branch_id: int, category_code: str, target_year: int
) -> Optional[CutoffPrediction]:
    return db.execute(
        select(CutoffPrediction).where(
            and_(
                CutoffPrediction.branch_id == branch_id,
                CutoffPrediction.category_code == category_code,
                CutoffPrediction.target_year == target_year,
            )
        )
    ).scalar_one_or_none()


def get_all_predictions_for_year(
    db: Session, target_year: int
) -> List[CutoffPrediction]:
    return db.execute(
        select(CutoffPrediction).where(
            CutoffPrediction.target_year == target_year
        )
    ).scalars().all()


# ── Student Sessions ──────────────────────────────────────────────────────────

def create_session(db: Session, session: StudentSession) -> StudentSession:
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, session_id: str) -> Optional[StudentSession]:
    return db.get(StudentSession, session_id)
