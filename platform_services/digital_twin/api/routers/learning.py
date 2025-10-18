"""
Passive Learning API Router

Endpoints for Passive Learning System:
- Context viewing
- Learning event history
- Pattern analysis
- Recommendations
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query

from core.learning.passive_learning_engine_db import PassiveLearningEngineDB, LearningEvent, LearningSource
from core.learning.context_builder_db import ContextBuilderDB, OrganizationContext

from api.dependencies import (
    get_passive_learning_engine,
    get_context_builder
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/learning", tags=["learning"])


# ============================================
# CONTEXT ENDPOINTS
# ============================================

@router.get("/context/{twin_id}", response_model=OrganizationContext)
async def get_organization_context(
    twin_id: str,
    builder: ContextBuilderDB = Depends(get_context_builder)
):
    """
    Get complete organizational context

    Returns rich, dynamic profile built from learning
    """
    logger.info(f"Getting context for twin: {twin_id}")

    context = await builder.build_context(twin_id)

    return context


@router.get("/context/{twin_id}/summary")
async def get_context_summary(
    twin_id: str,
    builder: ContextBuilderDB = Depends(get_context_builder)
):
    """Get summarized context (quick overview)"""
    summary = await builder.get_context_summary(twin_id)

    return summary


@router.post("/context/{twin_id}/update")
async def update_context_from_event(
    twin_id: str,
    event_source: str,
    event_data: Dict[str, Any],
    builder: ContextBuilderDB = Depends(get_context_builder)
):
    """
    Update context from new event

    Args:
        twin_id: Twin ID
        event_source: Source type (bia, risk_assessment, incident, training, document)
        event_data: Event data

    Returns:
        Updated context
    """
    logger.info(f"Updating context for {twin_id} from {event_source}")

    context = await builder.update_context_from_event(
        twin_id=twin_id,
        event_data=event_data,
        event_source=event_source
    )

    return context


@router.get("/context/compare/{twin_id_a}/{twin_id_b}")
async def compare_contexts(
    twin_id_a: str,
    twin_id_b: str,
    builder: ContextBuilderDB = Depends(get_context_builder)
):
    """Compare contexts of two organizations"""
    comparison = await builder.compare_contexts(twin_id_a, twin_id_b)

    return comparison


@router.get("/context/{twin_id}/evolution")
async def get_context_evolution(
    twin_id: str,
    time_period_days: int = Query(default=90, ge=1, le=365),
    builder: ContextBuilderDB = Depends(get_context_builder)
):
    """Analyze how context has evolved over time"""
    evolution = await builder.get_evolution(twin_id, time_period_days)

    return evolution


# ============================================
# LEARNING EVENT ENDPOINTS
# ============================================

@router.get("/events/{twin_id}", response_model=List[LearningEvent])
async def get_learning_events(
    twin_id: str,
    source: Optional[LearningSource] = None,
    limit: int = Query(default=100, ge=1, le=500),
    engine: PassiveLearningEngineDB = Depends(get_passive_learning_engine)
):
    """Get learning event history"""
    events = await engine.get_learning_history(
        twin_id=twin_id,
        source=source,
        limit=limit
    )

    return events


@router.get("/insights/{twin_id}")
async def get_accumulated_insights(
    twin_id: str,
    engine: PassiveLearningEngineDB = Depends(get_passive_learning_engine)
):
    """Get all accumulated insights"""
    insights = await engine.get_insights(twin_id)

    return insights


@router.get("/insights/{twin_id}/{insight_type}")
async def get_specific_insight(
    twin_id: str,
    insight_type: str,
    engine: PassiveLearningEngineDB = Depends(get_passive_learning_engine)
):
    """Get specific insight"""
    insight = await engine.get_insight(twin_id, insight_type)

    if insight is None:
        raise HTTPException(status_code=404, detail=f"Insight '{insight_type}' not found")

    return {"insight_type": insight_type, "value": insight}


# ============================================
# PATTERN ANALYSIS ENDPOINTS
# ============================================

@router.get("/patterns/{twin_id}")
async def detect_patterns(
    twin_id: str,
    engine: PassiveLearningEngineDB = Depends(get_passive_learning_engine)
):
    """Detect behavioral patterns"""
    patterns = await engine.detect_patterns(twin_id)

    return patterns


# ============================================
# RECOMMENDATIONS ENDPOINTS
# ============================================

@router.get("/recommendations/{twin_id}")
async def get_recommendations(
    twin_id: str,
    builder: ContextBuilderDB = Depends(get_context_builder)
):
    """
    Get recommendations based on context

    Returns:
        List of actionable recommendations
    """
    recommendations = await builder.get_recommendations(twin_id)

    return recommendations


# ============================================
# LEARNING ENGINE HOOKS
# ============================================

@router.post("/learn/bia/{twin_id}", response_model=LearningEvent)
async def learn_from_bia(
    twin_id: str,
    bia_data: Dict[str, Any],
    engine: PassiveLearningEngineDB = Depends(get_passive_learning_engine)
):
    """
    Learn from BIA completion

    This endpoint should be called by BIA Service when BIA is completed
    """
    logger.info(f"Processing BIA learning event for twin: {twin_id}")

    event = await engine.learn_from_bia(twin_id, bia_data)

    return event


@router.post("/learn/risk/{twin_id}", response_model=LearningEvent)
async def learn_from_risk_assessment(
    twin_id: str,
    risk_data: Dict[str, Any],
    engine: PassiveLearningEngineDB = Depends(get_passive_learning_engine)
):
    """
    Learn from risk assessment

    Called by Risk Service
    """
    event = await engine.learn_from_risk_assessment(twin_id, risk_data)

    return event


@router.post("/learn/incident/{twin_id}", response_model=LearningEvent)
async def learn_from_incident(
    twin_id: str,
    incident_data: Dict[str, Any],
    engine: PassiveLearningEngineDB = Depends(get_passive_learning_engine)
):
    """
    Learn from incident report

    Called by Incident Service
    """
    event = await engine.learn_from_incident(twin_id, incident_data)

    return event


@router.post("/learn/training/{twin_id}", response_model=LearningEvent)
async def learn_from_training(
    twin_id: str,
    training_data: Dict[str, Any],
    engine: PassiveLearningEngineDB = Depends(get_passive_learning_engine)
):
    """
    Learn from training completion

    Called by Training/Learning Service
    """
    event = await engine.learn_from_training(twin_id, training_data)

    return event


@router.post("/learn/document/{twin_id}", response_model=LearningEvent)
async def learn_from_document(
    twin_id: str,
    document_data: Dict[str, Any],
    engine: PassiveLearningEngineDB = Depends(get_passive_learning_engine)
):
    """
    Learn from document upload

    Called by Document Service
    """
    event = await engine.learn_from_document(twin_id, document_data)

    return event


# ============================================
# STATISTICS
# ============================================

@router.get("/statistics")
async def get_learning_statistics(
    engine: PassiveLearningEngineDB = Depends(get_passive_learning_engine),
    builder: ContextBuilderDB = Depends(get_context_builder)
):
    """Get learning engine statistics"""
    engine_stats = engine.get_statistics()
    builder_stats = builder.get_statistics()

    return {
        "engine": engine_stats,
        "builder": builder_stats
    }


# ============================================
# HEALTH CHECK
# ============================================

@router.get("/health")
async def learning_health_check():
    """Health check for learning services"""
    return {
        "status": "healthy",
        "services": {
            "passive_learning_engine": "operational",
            "context_builder": "operational"
        }
    }
