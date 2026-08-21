"""
db/models.py — SQLAlchemy ORM models for the CAP platform
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class College(Base):
    __tablename__ = "colleges"

    id             = Column(Integer, primary_key=True, index=True)
    name           = Column(String(255), nullable=False)
    district       = Column(String(100), nullable=False)
    college_type   = Column(String(50))   # Government, Aided, Unaided, Autonomous
    nirf_rank_proxy = Column(Integer)     # 1 = best, higher = lower tier
    description    = Column(Text, default="")
    created_at     = Column(DateTime(timezone=True), server_default=func.now())

    branches = relationship("Branch", back_populates="college", lazy="selectin")


class Branch(Base):
    __tablename__ = "branches"

    id           = Column(Integer, primary_key=True, index=True)
    college_id   = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False)
    branch_name  = Column(String(200), nullable=False)
    branch_code  = Column(String(20), nullable=False)
    demand_factor = Column(Float, default=1.0)
    total_seats  = Column(Integer, default=60)

    college  = relationship("College", back_populates="branches")
    cutoffs  = relationship("Cutoff", back_populates="branch", lazy="selectin")
    predictions = relationship("CutoffPrediction", back_populates="branch")

    __table_args__ = (
        UniqueConstraint("college_id", "branch_code", name="uq_college_branch"),
    )


class Cutoff(Base):
    __tablename__ = "cutoffs"

    id                  = Column(Integer, primary_key=True, index=True)
    branch_id           = Column(Integer, ForeignKey("branches.id", ondelete="CASCADE"), nullable=False)
    category_code       = Column(String(20), nullable=False)
    year                = Column(Integer, nullable=False)
    round               = Column(Integer, nullable=False)
    opening_percentile  = Column(Float)
    closing_percentile  = Column(Float)
    total_seats         = Column(Integer)
    filled_seats        = Column(Integer)
    source_pdf          = Column(String(255), default="sample_data")
    confidence_score    = Column(Float, default=1.0)

    branch = relationship("Branch", back_populates="cutoffs")

    __table_args__ = (
        UniqueConstraint("branch_id", "category_code", "year", "round",
                         name="uq_cutoff_combo"),
        Index("ix_cutoff_lookup", "branch_id", "category_code", "year"),
    )


class CutoffPrediction(Base):
    """Stores ML-predicted cutoffs for the upcoming CAP round."""
    __tablename__ = "cutoff_predictions"

    id                   = Column(Integer, primary_key=True, index=True)
    branch_id            = Column(Integer, ForeignKey("branches.id", ondelete="CASCADE"), nullable=False)
    category_code        = Column(String(20), nullable=False)
    target_year          = Column(Integer, nullable=False)
    predicted_closing    = Column(Float, nullable=False)
    lower_bound          = Column(Float, nullable=False)   # 10th percentile CI
    upper_bound          = Column(Float, nullable=False)   # 90th percentile CI
    model_version        = Column(String(50), default="weighted_avg_v1")
    created_at           = Column(DateTime(timezone=True), server_default=func.now())

    branch = relationship("Branch", back_populates="predictions")

    __table_args__ = (
        UniqueConstraint("branch_id", "category_code", "target_year",
                         name="uq_prediction_combo"),
    )


class StudentSession(Base):
    """Ephemeral student preference sessions (no account needed)."""
    __tablename__ = "student_sessions"

    id              = Column(String(36), primary_key=True)  # UUID
    percentile      = Column(Float, nullable=False)
    category_code   = Column(String(20), nullable=False)
    preferred_districts = Column(String(500), default="")   # comma-separated
    preferred_branch_codes = Column(String(200), default="") # comma-separated, ordered by pref
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed   = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
