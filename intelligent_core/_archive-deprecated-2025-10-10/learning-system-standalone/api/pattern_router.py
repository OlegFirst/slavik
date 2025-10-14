"""
Pattern Detection API Router
"""

import sys
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta

# Add shared to path
shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from database.base import get_db

# Add engines to path
engines_path = Path(__file__).parent.parent / "engines"
sys.path.insert(0, str(engines_path))

from pattern_detector import PatternDetector

# Import models
models_path = Path(__file__).parent.parent / "models"
sys.path.insert(0, str(models_path))

from learning_models import ExerciseResult, Pattern

router = APIRouter()

# Pydantic schemas
class PatternResponse(BaseModel):
    """Pattern response"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    pattern_type: str
    pattern_category: str
    pattern_name: str
    description: str
    occurrence_count: int
    confidence: float
    severity: Optional[str] = None
    affected_areas: Optional[List[str]] = None
    recommended_actions: Optional[List[str]] = None
    is_active: bool = True
    first_detected: Optional[str] = None
    last_detected: Optional[str] = None


class PatternDetectionRequest(BaseModel):
    """Request to detect patterns"""
    model_config = ConfigDict(from_attributes=True)

    time_period_days: int = Field(default=90, description="Look back period in days")
    scenario_type: Optional[str] = Field(None, description="Filter by scenario type")
    min_confidence: float = Field(default=0.7, description="Minimum confidence threshold")


# Pattern detector instance
detector = PatternDetector()


@router.post("/detect", response_model=List[PatternResponse])
async def detect_patterns(
    request: PatternDetectionRequest,
    db: Session = Depends(get_db)
):
    """
    Detect patterns from exercise history

    Analyzes recent exercise results and identifies:
    - Recurring failures
    - Success patterns
    - Performance trends
    - Anomalies
    """

    # Get exercise results from time period
    since_date = datetime.utcnow() - timedelta(days=request.time_period_days)

    query = db.query(ExerciseResult).filter(
        ExerciseResult.conducted_at >= since_date
    )

    if request.scenario_type:
        query = query.filter(ExerciseResult.scenario_type == request.scenario_type)

    exercise_results = query.order_by(desc(ExerciseResult.conducted_at)).all()

    if not exercise_results:
        return []

    # Convert to dict for pattern detector
    results_data = [
        {
            'exercise_name': r.exercise_name,
            'scenario_type': r.scenario_type,
            'overall_score': r.overall_score,
            'response_time_minutes': r.response_time_minutes,
            'key_issues': r.key_issues or [],
            'strengths': r.strengths or [],
            'roles_involved': r.roles_involved or [],
            'conducted_at': r.conducted_at
        }
        for r in exercise_results
    ]

    # Detect patterns
    detected_patterns = detector.detect_patterns(results_data)

    # Filter by confidence
    filtered_patterns = [
        p for p in detected_patterns
        if p.get('confidence', 0) >= request.min_confidence
    ]

    # Save new patterns to database
    saved_patterns = []
    for pattern_data in filtered_patterns:
        # Check if pattern already exists
        existing = db.query(Pattern).filter(
            Pattern.pattern_name == pattern_data['pattern_name'],
            Pattern.is_active == True
        ).first()

        if existing:
            # Update existing pattern
            existing.occurrence_count = pattern_data['occurrence_count']
            existing.confidence = pattern_data['confidence']
            existing.last_detected = datetime.utcnow()
            saved_patterns.append(existing)
        else:
            # Create new pattern
            new_pattern = Pattern(
                pattern_type=pattern_data['pattern_type'],
                pattern_category=pattern_data['pattern_category'],
                pattern_name=pattern_data['pattern_name'],
                description=pattern_data['description'],
                occurrence_count=pattern_data['occurrence_count'],
                confidence=pattern_data['confidence'],
                severity=pattern_data.get('severity'),
                affected_areas=pattern_data.get('affected_areas'),
                recommended_actions=pattern_data.get('recommended_actions'),
                evidence_data=pattern_data.get('evidence_data')
            )
            db.add(new_pattern)
            saved_patterns.append(new_pattern)

    db.commit()

    # Convert to response
    return [
        PatternResponse(
            id=p.id,
            pattern_type=p.pattern_type,
            pattern_category=p.pattern_category,
            pattern_name=p.pattern_name,
            description=p.description,
            occurrence_count=p.occurrence_count,
            confidence=p.confidence,
            severity=p.severity,
            affected_areas=p.affected_areas,
            recommended_actions=p.recommended_actions,
            is_active=p.is_active,
            first_detected=p.first_detected.isoformat() if p.first_detected else None,
            last_detected=p.last_detected.isoformat() if p.last_detected else None
        )
        for p in saved_patterns
    ]


@router.get("/", response_model=List[PatternResponse])
async def list_patterns(
    pattern_type: Optional[str] = None,
    is_active: bool = True,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List detected patterns

    Filters:
    - pattern_type: failure/success/trend/anomaly
    - is_active: Show active patterns only
    """
    query = db.query(Pattern)

    if pattern_type:
        query = query.filter(Pattern.pattern_type == pattern_type)

    if is_active:
        query = query.filter(Pattern.is_active == True)

    patterns = query.order_by(desc(Pattern.last_detected)).limit(limit).all()

    return [
        PatternResponse(
            id=p.id,
            pattern_type=p.pattern_type,
            pattern_category=p.pattern_category,
            pattern_name=p.pattern_name,
            description=p.description,
            occurrence_count=p.occurrence_count,
            confidence=p.confidence,
            severity=p.severity,
            affected_areas=p.affected_areas,
            recommended_actions=p.recommended_actions,
            is_active=p.is_active,
            first_detected=p.first_detected.isoformat() if p.first_detected else None,
            last_detected=p.last_detected.isoformat() if p.last_detected else None
        )
        for p in patterns
    ]


@router.get("/{pattern_id}", response_model=PatternResponse)
async def get_pattern(
    pattern_id: int,
    db: Session = Depends(get_db)
):
    """Get specific pattern by ID"""
    pattern = db.query(Pattern).filter(Pattern.id == pattern_id).first()

    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")

    return PatternResponse(
        id=pattern.id,
        pattern_type=pattern.pattern_type,
        pattern_category=pattern.pattern_category,
        pattern_name=pattern.pattern_name,
        description=pattern.description,
        occurrence_count=pattern.occurrence_count,
        confidence=pattern.confidence,
        severity=pattern.severity,
        affected_areas=pattern.affected_areas,
        recommended_actions=pattern.recommended_actions,
        is_active=pattern.is_active,
        first_detected=pattern.first_detected.isoformat() if pattern.first_detected else None,
        last_detected=pattern.last_detected.isoformat() if pattern.last_detected else None
    )


@router.post("/{pattern_id}/acknowledge")
async def acknowledge_pattern(
    pattern_id: int,
    acknowledged_by: str,
    db: Session = Depends(get_db)
):
    """Acknowledge a pattern"""
    pattern = db.query(Pattern).filter(Pattern.id == pattern_id).first()

    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")

    pattern.is_acknowledged = True
    pattern.acknowledged_by = acknowledged_by
    pattern.acknowledged_at = datetime.utcnow()

    db.commit()

    return {"message": "Pattern acknowledged", "pattern_id": pattern_id}


@router.delete("/{pattern_id}")
async def deactivate_pattern(
    pattern_id: int,
    db: Session = Depends(get_db)
):
    """Deactivate a pattern (soft delete)"""
    pattern = db.query(Pattern).filter(Pattern.id == pattern_id).first()

    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")

    pattern.is_active = False
    db.commit()

    return {"message": "Pattern deactivated", "pattern_id": pattern_id}
