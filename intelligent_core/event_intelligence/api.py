"""
Event Intelligence API Router

FastAPI endpoints для event_intelligence модуля
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging

from .analyzer import EventAnalyzer, EventAnalysis
from .learner import EventLearner, LearningExample
from .predictor import EventPredictor
from .knowledge_base import EventKnowledgeBase
from .services.ai_foundation_integration import get_event_ai_foundation, EventIntelligenceAIFoundation

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/event-intelligence", tags=["Event Intelligence"])

# Global instances (будут инициализированы при startup)
analyzer: Optional[EventAnalyzer] = None
learner: Optional[EventLearner] = None
predictor: Optional[EventPredictor] = None
knowledge_base: Optional[EventKnowledgeBase] = None
ai_foundation: Optional[EventIntelligenceAIFoundation] = None


# Request/Response Models
class AnalyzeEventRequest(BaseModel):
    event_name: str
    publishers: List[str] = []
    subscribers: List[str] = []
    historical_data: Optional[Dict[str, Any]] = None


class AnalyzeEventResponse(BaseModel):
    event_name: str
    importance_score: float
    usage_pattern: str
    recommendations: List[str]
    ai_insights: str


class RecordSuggestionRequest(BaseModel):
    event_name: str
    suggested_action: str  # 'implement', 'postpone', 'reject'
    confidence: float


class RecordFeedbackRequest(BaseModel):
    suggestion_id: str
    developer_decision: str  # 'approved', 'rejected', 'postponed'
    outcome: Optional[str] = None  # 'success', 'failure', 'neutral'


class PredictGapsRequest(BaseModel):
    current_events: Dict[str, Dict[str, List[str]]]  # {event_name: {publishers: [], subscribers: []}}
    context: Optional[Dict[str, Any]] = None


class PredictGapsResponse(BaseModel):
    predicted_gaps: List[Dict[str, Any]]
    predictions_count: int
    confidence: float


# Initialization
async def initialize_event_intelligence():
    """Initialize Event Intelligence components"""
    global analyzer, learner, predictor, knowledge_base, ai_foundation

    logger.info(" Initializing Event Intelligence...")

    # Initialize AI Foundation (RAG + LLM)
    try:
        ai_foundation = await get_event_ai_foundation()
        logger.info(" AI Foundation (RAG + LLM) initialized for Event Intelligence")
    except Exception as e:
        logger.error(f" AI Foundation initialization failed: {e}")
        ai_foundation = None

    analyzer = EventAnalyzer()
    learner = EventLearner()
    predictor = EventPredictor()
    knowledge_base = EventKnowledgeBase()

    logger.info(" Event Intelligence initialized successfully")


# Endpoints
@router.get("/health")
async def health_check():
    """Health check for Event Intelligence"""
    return {
        "status": "healthy",
        "components": {
            "analyzer": analyzer is not None,
            "learner": learner is not None,
            "predictor": predictor is not None,
            "knowledge_base": knowledge_base is not None,
            "ai_foundation": ai_foundation is not None
        }
    }


@router.post("/analyze", response_model=AnalyzeEventResponse)
async def analyze_event(request: AnalyzeEventRequest):
    """
    Analyze single event

    Provides:
    - Importance scoring
    - Usage pattern detection
    - AI-powered recommendations
    - Insights
    """
    if not analyzer:
        raise HTTPException(status_code=503, detail="Event Intelligence not initialized")

    try:
        analysis = await analyzer.analyze_event(
            event_name=request.event_name,
            publishers=request.publishers,
            subscribers=request.subscribers,
            historical_data=request.historical_data
        )

        # Store in knowledge base
        if knowledge_base:
            await knowledge_base.store_event_analysis(
                request.event_name,
                {
                    'importance_score': analysis.importance_score,
                    'usage_pattern': analysis.usage_pattern,
                    'recommendations': analysis.recommendations,
                    'ai_insights': analysis.ai_insights
                }
            )

        return AnalyzeEventResponse(
            event_name=analysis.event_name,
            importance_score=analysis.importance_score,
            usage_pattern=analysis.usage_pattern,
            recommendations=analysis.recommendations,
            ai_insights=analysis.ai_insights
        )

    except Exception as e:
        logger.error(f" Event analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/domain")
async def analyze_domain(domain: str, events: List[Dict[str, Any]]):
    """
    Analyze all events in a domain

    Returns aggregated statistics and health metrics
    """
    if not analyzer:
        raise HTTPException(status_code=503, detail="Event Intelligence not initialized")

    try:
        result = await analyzer.analyze_domain(domain, events)
        return result

    except Exception as e:
        logger.error(f" Domain analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learning/suggest")
async def record_suggestion(request: RecordSuggestionRequest):
    """
    Record a suggestion for learning

    Returns suggestion_id for tracking
    """
    if not learner:
        raise HTTPException(status_code=503, detail="Learning system not initialized")

    try:
        suggestion_id = await learner.record_suggestion(
            event_name=request.event_name,
            suggested_action=request.suggested_action,
            confidence=request.confidence
        )

        return {
            "suggestion_id": suggestion_id,
            "event_name": request.event_name,
            "status": "recorded"
        }

    except Exception as e:
        logger.error(f" Recording suggestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learning/feedback")
async def record_feedback(request: RecordFeedbackRequest):
    """
    Record developer feedback on suggestion

    Enables learning from decisions
    """
    if not learner:
        raise HTTPException(status_code=503, detail="Learning system not initialized")

    try:
        await learner.record_feedback(
            suggestion_id=request.suggestion_id,
            developer_decision=request.developer_decision,
            outcome=request.outcome
        )

        return {
            "suggestion_id": request.suggestion_id,
            "decision": request.developer_decision,
            "status": "recorded"
        }

    except Exception as e:
        logger.error(f" Recording feedback failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning/stats")
async def get_learning_stats():
    """Get learning statistics"""
    if not learner:
        raise HTTPException(status_code=503, detail="Learning system not initialized")

    try:
        stats = await learner.get_learning_stats()
        return stats

    except Exception as e:
        logger.error(f" Getting stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning/report")
async def get_learning_report():
    """Export comprehensive learning report"""
    if not learner:
        raise HTTPException(status_code=503, detail="Learning system not initialized")

    try:
        report = await learner.export_learning_report()
        return report

    except Exception as e:
        logger.error(f" Generating report failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/gaps", response_model=PredictGapsResponse)
async def predict_gaps(request: PredictGapsRequest):
    """
    Predict missing event handlers/publishers

    Uses ML to identify potential gaps in event architecture
    """
    if not predictor:
        raise HTTPException(status_code=503, detail="Predictor not initialized")

    try:
        predictions = await predictor.predict_missing_handlers(
            current_events=request.current_events,
            context=request.context
        )

        return PredictGapsResponse(
            predicted_gaps=predictions,
            predictions_count=len(predictions),
            confidence=sum(p.get('confidence', 0) for p in predictions) / len(predictions) if predictions else 0
        )

    except Exception as e:
        logger.error(f" Gap prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/similar/{event_name}")
async def get_similar_events(event_name: str, limit: int = 5):
    """Find similar events in knowledge base"""
    if not knowledge_base:
        raise HTTPException(status_code=503, detail="Knowledge base not initialized")

    try:
        similar = await knowledge_base.get_similar_events(event_name, limit)
        return {
            "event_name": event_name,
            "similar_events": similar,
            "count": len(similar)
        }

    except Exception as e:
        logger.error(f" Similar events search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/patterns/{event_name}")
async def get_relevant_patterns(event_name: str, limit: int = 3):
    """Get relevant patterns for event"""
    if not knowledge_base:
        raise HTTPException(status_code=503, detail="Knowledge base not initialized")

    try:
        patterns = await knowledge_base.get_relevant_patterns(event_name, limit)
        return {
            "event_name": event_name,
            "patterns": patterns,
            "count": len(patterns)
        }

    except Exception as e:
        logger.error(f" Pattern search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/stats")
async def get_knowledge_stats():
    """Get knowledge base statistics"""
    if not knowledge_base:
        raise HTTPException(status_code=503, detail="Knowledge base not initialized")

    try:
        stats = await knowledge_base.get_learning_stats()
        return stats

    except Exception as e:
        logger.error(f" Getting knowledge stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Export router and init function
__all__ = ['router', 'initialize_event_intelligence']
