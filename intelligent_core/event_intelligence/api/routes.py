"""
Event Intelligence API Router

FastAPI endpoints for event_intelligence module
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import logging

from ..analyzer import EventAnalyzer, EventAnalysis
from ..learner import EventLearner, LearningExample
from ..predictor import EventPredictor
from ..knowledge_base import EventKnowledgeBase

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/event-intelligence", tags=["Event Intelligence"])

# Global instances (initialized at startup)
analyzer: Optional[EventAnalyzer] = None
learner: Optional[EventLearner] = None
predictor: Optional[EventPredictor] = None
knowledge_base: Optional[EventKnowledgeBase] = None


# ============= REQUEST/RESPONSE MODELS =============

class AnalyzeEventRequest(BaseModel):
    """Request to analyze single event"""
    event_name: str = Field(..., description="Event name (e.g., 'user.registered')")
    publishers: List[str] = Field(default=[], description="List of services publishing this event")
    subscribers: List[str] = Field(default=[], description="List of services subscribing to this event")
    historical_data: Optional[Dict[str, Any]] = Field(None, description="Historical event data for ML analysis")


class AnalyzeEventResponse(BaseModel):
    """Event analysis results"""
    event_name: str
    importance_score: float = Field(..., ge=0, le=1, description="Event importance (0-1)")
    usage_pattern: str = Field(..., description="critical, frequent, rare, or unused")
    recommendations: List[str] = Field(..., description="AI-powered recommendations")
    ai_insights: str = Field(..., description="Detailed AI analysis and insights")


class AnalyzeDomainRequest(BaseModel):
    """Request to analyze domain events"""
    domain: str = Field(..., description="Domain name (e.g., 'authentication')")
    events: List[Dict[str, Any]] = Field(..., description="List of events in domain")


class AnalyzeDomainResponse(BaseModel):
    """Domain analysis results"""
    domain: str
    total_events: int
    critical_events: int
    health_score: float
    recommendations: List[str]
    patterns: List[str]


class RecordSuggestionRequest(BaseModel):
    """Request to record AI suggestion"""
    event_name: str
    suggested_action: str = Field(..., description="'implement', 'postpone', 'reject'")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    context: Optional[Dict[str, Any]] = None


class RecordSuggestionResponse(BaseModel):
    """Suggestion recording result"""
    suggestion_id: str
    event_name: str
    status: str
    tracked_for_learning: bool


class RecordFeedbackRequest(BaseModel):
    """Request to record developer feedback"""
    suggestion_id: str
    developer_decision: str = Field(..., description="'approved', 'rejected', 'postponed'")
    outcome: Optional[str] = Field(None, description="'success', 'failure', 'neutral'")
    feedback_notes: Optional[str] = None


class RecordFeedbackResponse(BaseModel):
    """Feedback recording result"""
    suggestion_id: str
    decision: str
    status: str
    learning_updated: bool


class PredictGapsRequest(BaseModel):
    """Request to predict event gaps"""
    current_events: Dict[str, Dict[str, List[str]]] = Field(
        ...,
        description="Event mapping: {event_name: {publishers: [], subscribers: []}}"
    )
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for ML model")


class PredictGapsResponse(BaseModel):
    """Gap prediction results"""
    predicted_gaps: List[Dict[str, Any]]
    predictions_count: int
    average_confidence: float
    high_priority_gaps: List[Dict[str, Any]]


class LearningStatsResponse(BaseModel):
    """Learning statistics"""
    total_suggestions: int
    approved_count: int
    rejected_count: int
    postponed_count: int
    success_rate: float
    improvement_trend: str


class KnowledgeStatsResponse(BaseModel):
    """Knowledge base statistics"""
    total_events: int
    total_patterns: int
    total_analyses: int
    knowledge_coverage: float


# ============= INITIALIZATION =============

async def initialize_event_intelligence():
    """Initialize Event Intelligence components"""
    global analyzer, learner, predictor, knowledge_base

    logger.info("🧠 Initializing Event Intelligence components...")

    try:
        analyzer = EventAnalyzer()
        learner = EventLearner()
        predictor = EventPredictor()
        knowledge_base = EventKnowledgeBase()

        logger.info("✅ Event Intelligence initialized successfully")

        return {
            "status": "initialized",
            "components": {
                "analyzer": "ready",
                "learner": "ready",
                "predictor": "ready",
                "knowledge_base": "ready"
            }
        }
    except Exception as e:
        logger.error(f"❌ Event Intelligence initialization failed: {e}")
        raise


# ============= HEALTH & STATUS ENDPOINTS =============

@router.get("/health")
async def health_check():
    """
    Health check for Event Intelligence service

    Returns status of all components
    """
    return {
        "status": "healthy",
        "service": "event-intelligence",
        "components": {
            "analyzer": analyzer is not None,
            "learner": learner is not None,
            "predictor": predictor is not None,
            "knowledge_base": knowledge_base is not None
        },
        "capabilities": [
            "event_analysis",
            "pattern_detection",
            "gap_prediction",
            "ml_learning",
            "knowledge_management"
        ]
    }


@router.get("/status")
async def get_status():
    """Get detailed service status"""
    return {
        "service": "Event Intelligence",
        "version": "1.0.0",
        "components": {
            "analyzer": {
                "status": "active" if analyzer else "inactive",
                "description": "Event analysis with importance scoring"
            },
            "learner": {
                "status": "active" if learner else "inactive",
                "description": "ML learning from feedback"
            },
            "predictor": {
                "status": "active" if predictor else "inactive",
                "description": "Gap prediction engine"
            },
            "knowledge_base": {
                "status": "active" if knowledge_base else "inactive",
                "description": "Event knowledge storage"
            }
        }
    }


# ============= EVENT ANALYSIS ENDPOINTS =============

@router.post("/analyze", response_model=AnalyzeEventResponse)
async def analyze_event(request: AnalyzeEventRequest):
    """
    Analyze single event

    Provides:
    - Importance scoring (0-1)
    - Usage pattern classification
    - AI-powered recommendations
    - Detailed insights

    Example:
    ```json
    {
        "event_name": "user.registered",
        "publishers": ["auth-service"],
        "subscribers": ["email-service", "analytics-service"]
    }
    ```
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
        logger.error(f"❌ Event analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/domain", response_model=AnalyzeDomainResponse)
async def analyze_domain(request: AnalyzeDomainRequest):
    """
    Analyze all events in a domain

    Returns:
    - Aggregated statistics
    - Health metrics
    - Domain-wide recommendations
    - Pattern analysis

    Example:
    ```json
    {
        "domain": "authentication",
        "events": [
            {"event_name": "user.login", "publishers": [...], "subscribers": [...]},
            {"event_name": "user.logout", "publishers": [...], "subscribers": [...]}
        ]
    }
    ```
    """
    if not analyzer:
        raise HTTPException(status_code=503, detail="Event Intelligence not initialized")

    try:
        result = await analyzer.analyze_domain(request.domain, request.events)

        return AnalyzeDomainResponse(
            domain=request.domain,
            total_events=result.get('total_events', 0),
            critical_events=result.get('critical_events', 0),
            health_score=result.get('health_score', 0.0),
            recommendations=result.get('recommendations', []),
            patterns=result.get('patterns', [])
        )

    except Exception as e:
        logger.error(f"❌ Domain analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Domain analysis failed: {str(e)}")


@router.post("/analyze/bulk")
async def analyze_bulk_events(events: List[AnalyzeEventRequest]):
    """
    Analyze multiple events in batch

    Useful for initial system analysis or periodic audits
    """
    if not analyzer:
        raise HTTPException(status_code=503, detail="Event Intelligence not initialized")

    results = []
    for event_request in events:
        try:
            analysis = await analyzer.analyze_event(
                event_name=event_request.event_name,
                publishers=event_request.publishers,
                subscribers=event_request.subscribers,
                historical_data=event_request.historical_data
            )
            results.append({
                "event_name": event_request.event_name,
                "status": "success",
                "analysis": {
                    "importance_score": analysis.importance_score,
                    "usage_pattern": analysis.usage_pattern,
                    "recommendations": analysis.recommendations
                }
            })
        except Exception as e:
            results.append({
                "event_name": event_request.event_name,
                "status": "failed",
                "error": str(e)
            })

    return {
        "total_events": len(events),
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "failed"]),
        "results": results
    }


# ============= LEARNING ENDPOINTS =============

@router.post("/learning/suggest", response_model=RecordSuggestionResponse)
async def record_suggestion(request: RecordSuggestionRequest):
    """
    Record AI suggestion for learning

    Returns suggestion_id for tracking feedback

    Example:
    ```json
    {
        "event_name": "order.created",
        "suggested_action": "implement",
        "confidence": 0.85
    }
    ```
    """
    if not learner:
        raise HTTPException(status_code=503, detail="Learning system not initialized")

    try:
        suggestion_id = await learner.record_suggestion(
            event_name=request.event_name,
            suggested_action=request.suggested_action,
            confidence=request.confidence
        )

        return RecordSuggestionResponse(
            suggestion_id=suggestion_id,
            event_name=request.event_name,
            status="recorded",
            tracked_for_learning=True
        )

    except Exception as e:
        logger.error(f"❌ Recording suggestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Recording failed: {str(e)}")


@router.post("/learning/feedback", response_model=RecordFeedbackResponse)
async def record_feedback(request: RecordFeedbackRequest):
    """
    Record developer feedback on suggestion

    Enables learning from real-world decisions

    Example:
    ```json
    {
        "suggestion_id": "uuid",
        "developer_decision": "approved",
        "outcome": "success"
    }
    ```
    """
    if not learner:
        raise HTTPException(status_code=503, detail="Learning system not initialized")

    try:
        await learner.record_feedback(
            suggestion_id=request.suggestion_id,
            developer_decision=request.developer_decision,
            outcome=request.outcome
        )

        return RecordFeedbackResponse(
            suggestion_id=request.suggestion_id,
            decision=request.developer_decision,
            status="recorded",
            learning_updated=True
        )

    except Exception as e:
        logger.error(f"❌ Recording feedback failed: {e}")
        raise HTTPException(status_code=500, detail=f"Feedback recording failed: {str(e)}")


@router.get("/learning/stats", response_model=LearningStatsResponse)
async def get_learning_stats():
    """
    Get learning statistics

    Returns metrics about AI suggestions and feedback
    """
    if not learner:
        raise HTTPException(status_code=503, detail="Learning system not initialized")

    try:
        stats = await learner.get_learning_stats()

        return LearningStatsResponse(
            total_suggestions=stats.get('total_suggestions', 0),
            approved_count=stats.get('approved_count', 0),
            rejected_count=stats.get('rejected_count', 0),
            postponed_count=stats.get('postponed_count', 0),
            success_rate=stats.get('success_rate', 0.0),
            improvement_trend=stats.get('improvement_trend', 'neutral')
        )

    except Exception as e:
        logger.error(f"❌ Getting stats failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")


@router.get("/learning/report")
async def get_learning_report():
    """
    Export comprehensive learning report

    Includes:
    - All suggestions and feedback
    - Success/failure analysis
    - Improvement recommendations
    """
    if not learner:
        raise HTTPException(status_code=503, detail="Learning system not initialized")

    try:
        report = await learner.export_learning_report()
        return report

    except Exception as e:
        logger.error(f"❌ Generating report failed: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


# ============= PREDICTION ENDPOINTS =============

@router.post("/predict/gaps", response_model=PredictGapsResponse)
async def predict_gaps(request: PredictGapsRequest):
    """
    Predict missing event handlers/publishers

    Uses ML to identify potential gaps in event architecture

    Example:
    ```json
    {
        "current_events": {
            "user.registered": {
                "publishers": ["auth-service"],
                "subscribers": ["email-service"]
            }
        }
    }
    ```
    """
    if not predictor:
        raise HTTPException(status_code=503, detail="Predictor not initialized")

    try:
        predictions = await predictor.predict_missing_handlers(
            current_events=request.current_events,
            context=request.context
        )

        high_priority = [p for p in predictions if p.get('confidence', 0) >= 0.8]
        avg_confidence = sum(p.get('confidence', 0) for p in predictions) / len(predictions) if predictions else 0

        return PredictGapsResponse(
            predicted_gaps=predictions,
            predictions_count=len(predictions),
            average_confidence=avg_confidence,
            high_priority_gaps=high_priority
        )

    except Exception as e:
        logger.error(f"❌ Gap prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/predict/recommendations/{event_name}")
async def get_event_recommendations(event_name: str):
    """
    Get AI recommendations for specific event

    Returns actionable suggestions based on analysis and patterns
    """
    if not analyzer or not knowledge_base:
        raise HTTPException(status_code=503, detail="Services not initialized")

    try:
        # Get similar events
        similar = await knowledge_base.get_similar_events(event_name, limit=5)

        # Get patterns
        patterns = await knowledge_base.get_relevant_patterns(event_name, limit=3)

        return {
            "event_name": event_name,
            "similar_events": similar,
            "patterns": patterns,
            "recommendations": [
                f"Consider implementing patterns from {len(similar)} similar events",
                f"Review {len(patterns)} relevant patterns for best practices"
            ]
        }

    except Exception as e:
        logger.error(f"❌ Recommendations failed: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")


# ============= KNOWLEDGE BASE ENDPOINTS =============

@router.get("/knowledge/similar/{event_name}")
async def get_similar_events(
    event_name: str,
    limit: int = Query(default=5, ge=1, le=20, description="Number of similar events to return")
):
    """
    Find similar events in knowledge base

    Uses semantic similarity and pattern matching
    """
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
        logger.error(f"❌ Similar events search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/knowledge/patterns/{event_name}")
async def get_relevant_patterns(
    event_name: str,
    limit: int = Query(default=3, ge=1, le=10, description="Number of patterns to return")
):
    """
    Get relevant patterns for event

    Returns best practices and common patterns
    """
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
        logger.error(f"❌ Pattern search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pattern search failed: {str(e)}")


@router.get("/knowledge/stats", response_model=KnowledgeStatsResponse)
async def get_knowledge_stats():
    """
    Get knowledge base statistics

    Returns metrics about stored knowledge
    """
    if not knowledge_base:
        raise HTTPException(status_code=503, detail="Knowledge base not initialized")

    try:
        stats = await knowledge_base.get_learning_stats()

        return KnowledgeStatsResponse(
            total_events=stats.get('total_events', 0),
            total_patterns=stats.get('total_patterns', 0),
            total_analyses=stats.get('total_analyses', 0),
            knowledge_coverage=stats.get('knowledge_coverage', 0.0)
        )

    except Exception as e:
        logger.error(f"❌ Getting knowledge stats failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")


@router.post("/knowledge/export")
async def export_knowledge():
    """
    Export all knowledge base data

    Returns complete dump of event knowledge
    """
    if not knowledge_base:
        raise HTTPException(status_code=503, detail="Knowledge base not initialized")

    try:
        export_data = await knowledge_base.export_knowledge()
        return {
            "status": "success",
            "export_date": "2025-10-08",
            "data": export_data
        }

    except Exception as e:
        logger.error(f"❌ Knowledge export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


# ============= UTILITY ENDPOINTS =============

@router.get("/metrics")
async def get_metrics():
    """
    Get comprehensive service metrics

    Includes all component statistics
    """
    metrics = {}

    try:
        if learner:
            metrics['learning'] = await learner.get_learning_stats()

        if knowledge_base:
            metrics['knowledge'] = await knowledge_base.get_learning_stats()

        metrics['status'] = 'healthy'
        return metrics

    except Exception as e:
        logger.error(f"❌ Metrics collection failed: {e}")
        return {
            "status": "partial",
            "error": str(e),
            "metrics": metrics
        }


# Export router and init function
__all__ = ['router', 'initialize_event_intelligence']
