"""
Platform Integration API Router

Demonstrates integration with shared platform services:
- RAG (Retrieval-Augmented Generation)
- ML Platform (Machine Learning)
- Knowledge Base
- Shared TOOLS

Provides unified endpoints using platform-wide services
"""

import sys
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Add shared to path
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

# Import shared components
from integrations.rag_connector import RAGConnector, RAGQueryBuilder
from integrations.ml_platform_client import MLPlatformClient, FeatureBuilder
from integrations.knowledge_client import KnowledgeClient, KnowledgeType

# Import integrated engines
engines_path = Path(__file__).parent.parent / "engines"
sys.path.insert(0, str(engines_path))

from knowledge_base_connector_integrated import IntegratedKnowledgeConnector, ExternalKnowledgeSyncManager
from ml_predictor_integrated import IntegratedMLPredictor

router = APIRouter()


# Pydantic schemas
class RAGSearchRequest(BaseModel):
    """RAG search request"""
    query: str = Field(..., description="Search query")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters")
    limit: int = Field(10, ge=1, le=50, description="Max results")


class MLPredictionRequest(BaseModel):
    """ML prediction request"""
    scenario_type: str
    team_size: int = Field(..., ge=1)
    avg_competency: float = Field(..., ge=0, le=1)
    days_since_last_exercise: int = Field(0, ge=0)
    historical_scores: Optional[List[float]] = None


class FeedbackRequest(BaseModel):
    """Feedback submission request"""
    prediction_id: str
    actual_score: float = Field(..., ge=0, le=100)
    metadata: Optional[Dict[str, Any]] = None


class LearningPathRequest(BaseModel):
    """Learning path creation request"""
    user_id: str
    competency_gap: str
    competency_level: Optional[str] = "intermediate"


# Initialize connectors (singleton pattern)
_rag_connector = None
_ml_client = None
_kb_connector = None
_ml_predictor = None


def get_rag_connector() -> RAGConnector:
    """Get RAG connector instance"""
    global _rag_connector
    if _rag_connector is None:
        _rag_connector = RAGConnector()
    return _rag_connector


def get_ml_client() -> MLPlatformClient:
    """Get ML Platform client instance"""
    global _ml_client
    if _ml_client is None:
        _ml_client = MLPlatformClient()
    return _ml_client


def get_kb_connector() -> IntegratedKnowledgeConnector:
    """Get integrated KB connector instance"""
    global _kb_connector
    if _kb_connector is None:
        _kb_connector = IntegratedKnowledgeConnector()
    return _kb_connector


def get_ml_predictor() -> IntegratedMLPredictor:
    """Get integrated ML predictor instance"""
    global _ml_predictor
    if _ml_predictor is None:
        _ml_predictor = IntegratedMLPredictor()
    return _ml_predictor


# ============================================================================
# RAG INTEGRATION ENDPOINTS
# ============================================================================

@router.post("/rag/search")
async def search_unified_knowledge(
    request: RAGSearchRequest,
    rag: RAGConnector = Depends(get_rag_connector)
):
    """
    Search unified knowledge base using RAG

    Uses platform-wide semantic search across ALL knowledge:
    - Documents
    - Procedures
    - Patterns
    - Lessons learned
    - ISO standards
    - Threat intelligence

    Example:
        POST /api/learning/platform/rag/search
        {
            "query": "How to handle cyber incident escalation",
            "context": {"domain": "BCM", "user_id": "user123"},
            "filters": {"type": ["procedure", "guideline"]},
            "limit": 10
        }
    """
    results = await rag.search_knowledge(
        query=request.query,
        context=request.context,
        filters=request.filters,
        limit=request.limit
    )

    return {
        'query': request.query,
        'result_count': len(results),
        'results': results
    }


@router.post("/rag/add-knowledge")
async def contribute_knowledge_to_rag(
    content: str,
    metadata: Dict[str, Any],
    knowledge_type: str,
    rag: RAGConnector = Depends(get_rag_connector)
):
    """
    Contribute knowledge to unified RAG

    Learning System can contribute patterns, lessons learned, etc.
    to platform-wide knowledge base

    Example:
        POST /api/learning/platform/rag/add-knowledge
        {
            "content": "Pattern: Communication delays in cyber incidents...",
            "metadata": {
                "title": "Communication Delay Pattern",
                "category": "pattern",
                "severity": "high"
            },
            "knowledge_type": "pattern"
        }
    """
    knowledge_id = await rag.add_knowledge(
        content=content,
        metadata=metadata,
        knowledge_type=knowledge_type,
        source="learning_system"
    )

    if knowledge_id:
        return {
            'status': 'success',
            'knowledge_id': knowledge_id,
            'message': 'Knowledge added to unified RAG'
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to add knowledge")


# ============================================================================
# ML PLATFORM INTEGRATION ENDPOINTS
# ============================================================================

@router.post("/ml/predict-success")
async def predict_exercise_success(
    request: MLPredictionRequest,
    ml_predictor: IntegratedMLPredictor = Depends(get_ml_predictor)
):
    """
    Predict exercise success using shared ML Platform

    Uses platform-wide ML models that learn from ALL services

    Example:
        POST /api/learning/platform/ml/predict-success
        {
            "scenario_type": "cyber_incident",
            "team_size": 12,
            "avg_competency": 0.75,
            "days_since_last_exercise": 45,
            "historical_scores": [78, 82, 85]
        }

    Returns:
        {
            "predicted_score": 83.5,
            "confidence": 0.82,
            "success_probability": 0.85,
            "risk_level": "low",
            "recommendations": [...]
        }
    """
    # Build team composition
    team_composition = {
        'size': request.team_size,
        'avg_competency': request.avg_competency
    }

    # Build historical performance
    historical_performance = []
    if request.historical_scores:
        for score in request.historical_scores:
            historical_performance.append({
                'overall_score': score,
                'conducted_at': datetime.utcnow()  # Simplified
            })

    # Add days since last
    if request.days_since_last_exercise > 0 and historical_performance:
        from datetime import timedelta
        historical_performance[-1]['conducted_at'] = datetime.utcnow() - timedelta(days=request.days_since_last_exercise)

    prediction = await ml_predictor.predict_exercise_success(
        scenario_type=request.scenario_type,
        team_composition=team_composition,
        historical_performance=historical_performance
    )

    return prediction


@router.post("/ml/submit-feedback")
async def submit_prediction_feedback(
    request: FeedbackRequest,
    ml_predictor: IntegratedMLPredictor = Depends(get_ml_predictor)
):
    """
    Submit actual exercise result (closes ML feedback loop)

    Actual results are sent to ML Platform, triggering:
    - Error calculation
    - Model retraining
    - Performance tracking

    All services benefit from shared learning

    Example:
        POST /api/learning/platform/ml/submit-feedback
        {
            "prediction_id": "pred_abc123",
            "actual_score": 82.0,
            "metadata": {
                "exercise_id": "ex_123",
                "duration_minutes": 120
            }
        }
    """
    await ml_predictor.submit_actual_result(
        prediction_id=request.prediction_id,
        actual_score=request.actual_score,
        exercise_metadata=request.metadata
    )

    return {
        'status': 'success',
        'message': 'Feedback submitted to ML Platform',
        'prediction_id': request.prediction_id
    }


@router.get("/ml/performance")
async def get_ml_performance(
    ml_predictor: IntegratedMLPredictor = Depends(get_ml_predictor)
):
    """
    Get ML model performance metrics

    Shows how well models are performing:
    - Accuracy
    - MAE (Mean Absolute Error)
    - Model drift
    - Improvement over time
    """
    performance = await ml_predictor.get_model_performance()

    return {
        'status': 'success',
        'performance': performance,
        'timestamp': datetime.utcnow().isoformat()
    }


@router.get("/ml/feature-importance")
async def get_feature_importance(
    model_type: str = "exercise_success",
    ml_predictor: IntegratedMLPredictor = Depends(get_ml_predictor)
):
    """
    Get feature importance for ML model

    Shows which features most influence predictions
    """
    importance = await ml_predictor.get_feature_importance(model_type)

    if importance:
        return {
            'model_type': model_type,
            'feature_importance': importance
        }
    else:
        raise HTTPException(status_code=404, detail="Model not found")


# ============================================================================
# KNOWLEDGE BASE INTEGRATION ENDPOINTS
# ============================================================================

@router.post("/kb/create-learning-path")
async def create_learning_path(
    request: LearningPathRequest,
    kb_connector: IntegratedKnowledgeConnector = Depends(get_kb_connector)
):
    """
    Create personalized learning path from KB resources

    Searches unified knowledge base and creates structured path

    Example:
        POST /api/learning/platform/kb/create-learning-path
        {
            "user_id": "user123",
            "competency_gap": "escalation",
            "competency_level": "intermediate"
        }
    """
    # Search for resources
    resources = await kb_connector.search_resources_for_gap(
        gap_keyword=request.competency_gap,
        user_id=request.user_id,
        competency_level=request.competency_level
    )

    # Create learning path
    learning_path = await kb_connector.create_learning_path_from_resources(
        user_id=request.user_id,
        competency_gap=request.competency_gap,
        resources=resources
    )

    return {
        'status': 'success',
        'learning_path': learning_path
    }


@router.post("/kb/auto-create-from-pattern")
async def auto_create_knowledge_from_pattern(
    pattern: Dict[str, Any],
    background_tasks: BackgroundTasks,
    kb_connector: IntegratedKnowledgeConnector = Depends(get_kb_connector)
):
    """
    Auto-create knowledge article from detected pattern

    When patterns reach threshold (5+ occurrences), auto-create KB article

    Example:
        POST /api/learning/platform/kb/auto-create-from-pattern
        {
            "pattern_name": "Communication Delay Pattern",
            "description": "Communication delays in cyber incidents...",
            "occurrence_count": 8,
            "confidence": 0.85,
            "severity": "high",
            "recommended_actions": [...]
        }
    """
    # Run in background to avoid blocking
    async def create_article():
        article_id = await kb_connector.auto_create_knowledge_from_pattern(pattern)
        if article_id:
            print(f"Auto-created KB article: {article_id}")

    background_tasks.add_task(create_article)

    return {
        'status': 'accepted',
        'message': 'Article creation queued',
        'pattern_name': pattern.get('pattern_name')
    }


@router.post("/kb/sync-external")
async def sync_external_knowledge(
    background_tasks: BackgroundTasks,
    kb_connector: IntegratedKnowledgeConnector = Depends(get_kb_connector)
):
    """
    Sync external knowledge sources

    Syncs:
    - ISO standards updates
    - Threat intelligence feeds
    - Industry best practices

    Runs in background
    """
    async def run_sync():
        sync_manager = ExternalKnowledgeSyncManager(kb_connector)
        results = await sync_manager.sync_all()
        print(f"External sync complete: {results}")

    background_tasks.add_task(run_sync)

    return {
        'status': 'accepted',
        'message': 'External knowledge sync started',
        'timestamp': datetime.utcnow().isoformat()
    }


# ============================================================================
# UNIFIED WORKFLOW ENDPOINTS
# ============================================================================

@router.post("/unified/predict-and-recommend")
async def unified_prediction_workflow(
    request: MLPredictionRequest,
    ml_predictor: IntegratedMLPredictor = Depends(get_ml_predictor),
    kb_connector: IntegratedKnowledgeConnector = Depends(get_kb_connector)
):
    """
    Unified workflow: Predict success + Recommend resources

    Combines:
    1. ML Platform prediction
    2. RAG knowledge search
    3. KB resource recommendations

    Example workflow:
    - Predict exercise will score 65 (medium risk)
    - Search for resources to improve weak areas
    - Return prediction + learning resources
    """
    # Step 1: Get ML prediction
    team_composition = {
        'size': request.team_size,
        'avg_competency': request.avg_competency
    }

    historical_performance = []
    if request.historical_scores:
        for score in request.historical_scores:
            historical_performance.append({
                'overall_score': score,
                'conducted_at': datetime.utcnow()
            })

    prediction = await ml_predictor.predict_exercise_success(
        scenario_type=request.scenario_type,
        team_composition=team_composition,
        historical_performance=historical_performance
    )

    # Step 2: If risk is medium/high, search for learning resources
    learning_resources = []
    if prediction.get('risk_level') in ['medium', 'high']:
        resources = await kb_connector.search_resources_for_gap(
            gap_keyword=request.scenario_type,
            competency_level='intermediate'
        )
        learning_resources = resources[:5]  # Top 5

    return {
        'prediction': prediction,
        'learning_resources': learning_resources,
        'workflow': 'unified_predict_recommend',
        'timestamp': datetime.utcnow().isoformat()
    }


@router.get("/status")
async def platform_integration_status(
    rag: RAGConnector = Depends(get_rag_connector),
    ml_client: MLPlatformClient = Depends(get_ml_client)
):
    """
    Check platform integration status

    Tests connectivity to:
    - RAG Service (port 8050)
    - ML Platform (port 8060)
    - Knowledge Base (port 8040)
    """
    status = {
        'rag_service': 'unknown',
        'ml_platform': 'unknown',
        'kb_service': 'unknown'
    }

    # Test RAG
    try:
        test_results = await rag.search_knowledge("test", limit=1)
        status['rag_service'] = 'connected' if test_results else 'available'
    except:
        status['rag_service'] = 'unavailable'

    # Test ML Platform
    try:
        models = await ml_client.list_available_models()
        status['ml_platform'] = 'connected' if models else 'available'
    except:
        status['ml_platform'] = 'unavailable'

    # Test KB
    kb_client = KnowledgeClient()
    try:
        await kb_client.search("test", limit=1)
        status['kb_service'] = 'connected'
    except:
        status['kb_service'] = 'unavailable'
    finally:
        await kb_client.close()

    return {
        'status': status,
        'timestamp': datetime.utcnow().isoformat()
    }
