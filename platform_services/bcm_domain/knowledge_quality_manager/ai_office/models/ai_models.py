"""
AI Intelligence Database Models

Schema: ai_intelligence
"""

import sys
from pathlib import Path
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# Add shared to path
shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from database.base import Base


class AnalysisSession(Base):
    """
    AI Analysis Session

    Records full AI analysis invocations
    """
    __tablename__ = "analysis_sessions"
    __table_args__ = {'schema': 'ai_intelligence'}

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)

    # Context
    tenant_id = Column(String(100), nullable=True, index=True)
    twin_id = Column(Integer, nullable=True, index=True)  # FK to digital_twin.organizations
    analysis_type = Column(String(50), nullable=False)  # comprehensive/risk/compliance/etc.

    # Metadata
    organs_invoked = Column(JSON, nullable=False)  # List of organ names
    context_data = Column(JSON, nullable=True)  # Input context

    # Results
    results = Column(JSON, nullable=True)  # Full results from all organs
    summary = Column(JSON, nullable=True)  # Aggregated summary

    # Status
    status = Column(String(20), default='running')  # running/completed/failed
    error_message = Column(Text, nullable=True)

    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    organ_results = relationship("OrganResult", back_populates="session", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="session", cascade="all, delete-orphan")


class OrganResult(Base):
    """
    Individual Organ Result

    Stores result from each organ invocation
    """
    __tablename__ = "organ_results"
    __table_args__ = {'schema': 'ai_intelligence'}

    id = Column(Integer, primary_key=True, index=True)

    # Session
    session_id = Column(Integer, ForeignKey('ai_intelligence.analysis_sessions.id', ondelete='CASCADE'), nullable=False, index=True)

    # Organ info
    organ_name = Column(String(50), nullable=False, index=True)
    organ_emoji = Column(String(10), nullable=True)

    # Results
    insights = Column(JSON, nullable=False)  # List of insights
    recommendations = Column(JSON, nullable=False)  # List of recommendations
    confidence = Column(Float, nullable=False)
    metadata = Column(JSON, nullable=True)  # Organ-specific metadata

    # Performance
    execution_time_ms = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    session = relationship("AnalysisSession", back_populates="organ_results")


class Insight(Base):
    """
    AI Insight

    Individual actionable insight from any organ
    """
    __tablename__ = "insights"
    __table_args__ = {'schema': 'ai_intelligence'}

    id = Column(Integer, primary_key=True, index=True)

    # Context
    tenant_id = Column(String(100), nullable=True, index=True)
    twin_id = Column(Integer, nullable=True, index=True)
    session_id = Column(Integer, ForeignKey('ai_intelligence.analysis_sessions.id', ondelete='SET NULL'), nullable=True, index=True)

    # Organ
    organ_name = Column(String(50), nullable=False, index=True)

    # Insight
    insight_type = Column(String(50), nullable=False, index=True)  # risk/gap/opportunity/warning/etc.
    content = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)

    # Metadata
    metadata = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)  # Searchable tags

    # Status
    is_acknowledged = Column(Boolean, default=False)
    is_actioned = Column(Boolean, default=False)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    session = relationship("AnalysisSession", back_populates="insights")
