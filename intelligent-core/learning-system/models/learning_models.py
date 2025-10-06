"""
Learning System Database Models

Schema: learning
"""

import sys
from pathlib import Path
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, Boolean
from sqlalchemy.sql import func

# Add shared to path
shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from database.base import Base


class ExerciseResult(Base):
    """
    Exercise execution results for learning

    Stores outcomes from scenario exercises
    """
    __tablename__ = "exercise_results"
    __table_args__ = {'schema': 'learning'}

    id = Column(Integer, primary_key=True, index=True)

    # Context
    tenant_id = Column(String(100), nullable=True, index=True)
    twin_id = Column(Integer, nullable=True, index=True)
    scenario_id = Column(Integer, nullable=True, index=True)

    # Exercise details
    exercise_name = Column(String(200), nullable=False)
    exercise_type = Column(String(50), nullable=False)  # tabletop/functional/full_scale
    scenario_type = Column(String(50), nullable=False)  # cyber/natural/supply_chain/etc

    # Performance metrics
    overall_score = Column(Float, nullable=False)  # 0-100
    response_time_minutes = Column(Integer, nullable=True)
    communication_score = Column(Float, nullable=True)
    decision_quality_score = Column(Float, nullable=True)
    coordination_score = Column(Float, nullable=True)

    # Outcomes
    objectives_met = Column(JSON, nullable=True)  # List of met objectives
    objectives_missed = Column(JSON, nullable=True)  # List of missed objectives
    key_issues = Column(JSON, nullable=True)  # Issues identified
    strengths = Column(JSON, nullable=True)  # What went well

    # Participants
    participant_count = Column(Integer, nullable=True)
    roles_involved = Column(JSON, nullable=True)

    # Metadata
    exercise_data = Column(JSON, nullable=True)  # Full exercise data

    # Timestamps
    conducted_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ScenarioLearning(Base):
    """
    Learning patterns from scenario execution

    Aggregated insights from multiple scenario runs
    """
    __tablename__ = "scenario_learning"
    __table_args__ = {'schema': 'learning'}

    id = Column(Integer, primary_key=True, index=True)

    # Scenario classification
    scenario_type = Column(String(50), nullable=False, index=True)
    threat_category = Column(String(50), nullable=True)
    complexity_level = Column(String(20), nullable=True)

    # Aggregated metrics
    execution_count = Column(Integer, default=0)
    avg_score = Column(Float, nullable=True)
    avg_response_time = Column(Float, nullable=True)
    success_rate = Column(Float, nullable=True)  # % achieving target score

    # Patterns
    common_failures = Column(JSON, nullable=True)  # Frequently occurring issues
    common_strengths = Column(JSON, nullable=True)  # Consistently strong areas
    improvement_trends = Column(JSON, nullable=True)  # Score trends over time

    # Recommendations
    recommended_improvements = Column(JSON, nullable=True)
    training_needs = Column(JSON, nullable=True)

    # Timestamps
    first_execution = Column(DateTime(timezone=True), nullable=True)
    last_execution = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Pattern(Base):
    """
    Detected patterns from learning

    Cross-cutting patterns across exercises, simulations, AI analyses
    """
    __tablename__ = "patterns"
    __table_args__ = {'schema': 'learning'}

    id = Column(Integer, primary_key=True, index=True)

    # Pattern classification
    pattern_type = Column(String(50), nullable=False, index=True)  # failure/success/trend/anomaly
    pattern_category = Column(String(50), nullable=False)  # exercise/simulation/ai_analysis

    # Pattern details
    pattern_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)

    # Evidence
    occurrence_count = Column(Integer, default=1)
    confidence = Column(Float, nullable=False)  # 0-1
    evidence_data = Column(JSON, nullable=True)  # Supporting data

    # Impact
    severity = Column(String(20), nullable=True)  # critical/high/medium/low
    affected_areas = Column(JSON, nullable=True)  # Areas impacted

    # Recommendations
    recommended_actions = Column(JSON, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    first_detected = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_detected = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
