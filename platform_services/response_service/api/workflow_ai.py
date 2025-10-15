"""
Workflow Intelligence API Routes for Response Service
ISO 22301:2019 Clause 8.4 - Incident Response

Provides AI-powered workflow insights and case management
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from intelligent_core.workflow_intelligence import CaseQuery, TimeRange, WorkflowRecommendation
from workflow_intelligence.monitoring import health_checker
import main

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/workflow-ai", tags=["Workflow Intelligence"])


# ============================================================================
# Dependency: Get Workflow Components
# ============================================================================

def get_workflow_engine():
    """Dependency to get workflow engine instance"""
    if main.workflow_engine is None:
        raise HTTPException(status_code=503, detail="Workflow Intelligence not initialized")
    return main.workflow_engine


def get_case_collector():
    """Dependency to get case collector instance"""
    if main.case_collector is None:
        raise HTTPException(status_code=503, detail="Case Collector not initialized")
    return main.case_collector


# ============================================================================
# Workflow Insights & Recommendations
# ============================================================================

@router.get("/insights", response_model=Dict[str, Any])
async def get_workflow_insights(
    case_id: Optional[str] = Query(None, description="Specific incident case ID"),
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    engine=Depends(get_workflow_engine)
):
    """
    Get AI-powered workflow insights for incident response

    **Features:**
    - Pattern detection in incident handling
    - Response time analysis
    - Efficiency recommendations
    - Historical trend analysis
    """
    try:
        time_range = TimeRange(
            start=datetime.utcnow() - timedelta(days=days),
            end=datetime.utcnow()
        )

        insights = await engine.get_insights(
            case_id=case_id,
            time_range=time_range,
            module="response"
        )

        return {
            "module": "response",
            "case_id": case_id,
            "time_range": {
                "start": time_range.start.isoformat(),
                "end": time_range.end.isoformat(),
                "days": days
            },
            "insights": insights,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting workflow insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations", response_model=List[WorkflowRecommendation])
async def get_recommendations(
    case_id: Optional[str] = Query(None, description="Specific incident case ID"),
    limit: int = Query(5, description="Maximum number of recommendations", ge=1, le=20),
    engine=Depends(get_workflow_engine)
):
    """
    Get AI-powered workflow recommendations for incident response

    **Recommendation Types:**
    - Response optimization
    - Resource allocation
    - Escalation procedures
    - Communication strategies
    """
    try:
        recommendations = await engine.get_recommendations(
            case_id=case_id,
            module="response",
            limit=limit
        )

        return recommendations
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Case Management & Analysis
# ============================================================================

@router.get("/cases/search", response_model=Dict[str, Any])
async def search_cases(
    query: Optional[str] = Query(None, description="Search query"),
    status: Optional[str] = Query(None, description="Incident status filter"),
    severity: Optional[str] = Query(None, description="Incident severity filter"),
    limit: int = Query(20, description="Maximum results", ge=1, le=100),
    offset: int = Query(0, description="Pagination offset", ge=0),
    collector=Depends(get_case_collector)
):
    """
    Search incident cases with advanced filtering

    **Filters:**
    - Full-text search
    - Status (reported, investigating, contained, resolved, closed)
    - Severity (low, medium, high, critical)
    - Pagination support
    """
    try:
        case_query = CaseQuery(
            module="response",
            query_text=query,
            filters={
                "status": status,
                "severity": severity
            } if status or severity else None,
            limit=limit,
            offset=offset
        )

        results = await collector.search_cases(case_query)

        return {
            "query": query,
            "filters": {
                "status": status,
                "severity": severity
            },
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(results)
            },
            "results": results
        }
    except Exception as e:
        logger.error(f"Error searching cases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cases/{case_id}/similar", response_model=List[Dict[str, Any]])
async def find_similar_cases(
    case_id: str,
    limit: int = Query(5, description="Maximum similar cases", ge=1, le=20),
    collector=Depends(get_case_collector)
):
    """
    Find similar incident cases using AI similarity analysis

    **Similarity Factors:**
    - Incident type and category
    - Impact and severity
    - Response actions taken
    - Resolution outcomes
    """
    try:
        similar_cases = await collector.find_similar(
            case_id=case_id,
            module="response",
            limit=limit
        )

        return similar_cases
    except Exception as e:
        logger.error(f"Error finding similar cases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cases/{case_id}/timeline", response_model=Dict[str, Any])
async def get_case_timeline(
    case_id: str,
    collector=Depends(get_case_collector)
):
    """
    Get detailed timeline for an incident case

    **Timeline Events:**
    - Incident detection
    - Initial response
    - Investigation milestones
    - Containment actions
    - Resolution and closure
    """
    try:
        timeline = await collector.get_timeline(
            case_id=case_id,
            module="response"
        )

        return {
            "case_id": case_id,
            "module": "response",
            "timeline": timeline,
            "retrieved_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting case timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Analytics & Metrics
# ============================================================================

@router.get("/analytics/patterns", response_model=Dict[str, Any])
async def analyze_patterns(
    days: int = Query(90, description="Analysis period in days", ge=7, le=365),
    engine=Depends(get_workflow_engine)
):
    """
    Analyze incident response patterns using AI

    **Pattern Analysis:**
    - Common incident types
    - Response effectiveness
    - Resolution time trends
    - Bottleneck identification
    """
    try:
        time_range = TimeRange(
            start=datetime.utcnow() - timedelta(days=days),
            end=datetime.utcnow()
        )

        patterns = await engine.analyze_patterns(
            module="response",
            time_range=time_range
        )

        return {
            "module": "response",
            "analysis_period_days": days,
            "time_range": {
                "start": time_range.start.isoformat(),
                "end": time_range.end.isoformat()
            },
            "patterns": patterns,
            "analyzed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/performance", response_model=Dict[str, Any])
async def get_performance_metrics(
    days: int = Query(30, description="Metrics period in days", ge=1, le=365),
    engine=Depends(get_workflow_engine)
):
    """
    Get incident response performance metrics

    **Metrics:**
    - Mean time to detect (MTTD)
    - Mean time to respond (MTTR)
    - Resolution rate
    - SLA compliance
    """
    try:
        time_range = TimeRange(
            start=datetime.utcnow() - timedelta(days=days),
            end=datetime.utcnow()
        )

        metrics = await engine.get_performance_metrics(
            module="response",
            time_range=time_range
        )

        return {
            "module": "response",
            "period_days": days,
            "time_range": {
                "start": time_range.start.isoformat(),
                "end": time_range.end.isoformat()
            },
            "metrics": metrics,
            "retrieved_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Response Playbook Intelligence
# ============================================================================

@router.get("/playbooks/recommend", response_model=Dict[str, Any])
async def recommend_playbooks(
    incident_type: Optional[str] = Query(None, description="Incident type"),
    severity: Optional[str] = Query(None, description="Incident severity"),
    limit: int = Query(3, description="Maximum playbooks", ge=1, le=10),
    engine=Depends(get_workflow_engine)
):
    """
    Get AI-recommended response playbooks for incident scenarios

    **Playbook Selection:**
    - Historical effectiveness
    - Incident type matching
    - Severity-appropriate actions
    - Resource requirements
    """
    try:
        playbooks = await engine.recommend_playbooks(
            module="response",
            incident_type=incident_type,
            severity=severity,
            limit=limit
        )

        return {
            "module": "response",
            "filters": {
                "incident_type": incident_type,
                "severity": severity
            },
            "playbooks": playbooks,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error recommending playbooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health & Status
# ============================================================================

@router.get("/health", response_model=Dict[str, Any])
async def workflow_health_check():
    """
    Check Workflow Intelligence system health

    **Health Checks:**
    - Database connectivity
    - AI engine status
    - Case collector status
    - Performance metrics
    """
    try:
        health_status = await health_checker.check_health()

        return {
            "status": "healthy" if health_status.get("overall_healthy") else "degraded",
            "module": "response",
            "components": health_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "module": "response",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
