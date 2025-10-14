"""
Workflow Intelligence API Routes for Validation Service
ISO 22301 Clauses 8.5, 9.1, 9.2, 9.3, 10

Provides AI-powered workflow insights and case management for:
- Exercise Management (ISO 8.5)
- Performance Monitoring & KPIs (ISO 9.1)
- Internal Audits (ISO 9.2)
- Management Reviews (ISO 9.3)
- CAPA & Continuous Improvement (ISO 10)
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from workflow_intelligence import CaseQuery, TimeRange, WorkflowRecommendation
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
    case_id: Optional[str] = Query(None, description="Specific validation case ID"),
    case_type: Optional[str] = Query(None, description="Case type: exercise, audit, review, capa"),
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    engine=Depends(get_workflow_engine)
):
    """
    Get AI-powered workflow insights for validation processes

    **Features:**
    - Pattern detection in exercises, audits, reviews
    - Effectiveness analysis
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
            module="validation",
            case_type=case_type
        )

        return {
            "module": "validation",
            "case_id": case_id,
            "case_type": case_type,
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
    case_id: Optional[str] = Query(None, description="Specific validation case ID"),
    case_type: Optional[str] = Query(None, description="Case type: exercise, audit, review, capa"),
    limit: int = Query(5, description="Maximum number of recommendations", ge=1, le=20),
    engine=Depends(get_workflow_engine)
):
    """
    Get AI-powered workflow recommendations for validation processes

    **Recommendation Types:**
    - Process optimization
    - Exercise improvement
    - Audit effectiveness
    - CAPA strategies
    """
    try:
        recommendations = await engine.get_recommendations(
            case_id=case_id,
            module="validation",
            case_type=case_type,
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
    case_type: Optional[str] = Query(None, description="Case type filter"),
    status: Optional[str] = Query(None, description="Status filter"),
    limit: int = Query(20, description="Maximum results", ge=1, le=100),
    offset: int = Query(0, description="Pagination offset", ge=0),
    collector=Depends(get_case_collector)
):
    """
    Search validation cases with advanced filtering

    **Case Types:**
    - exercise: ISO 8.5 Exercises
    - audit: ISO 9.2 Internal Audits
    - review: ISO 9.3 Management Reviews
    - capa: ISO 10 CAPA
    - kpi: ISO 9.1 Performance Monitoring

    **Filters:**
    - Full-text search
    - Case type
    - Status
    - Pagination support
    """
    try:
        case_query = CaseQuery(
            module="validation",
            query_text=query,
            filters={
                "case_type": case_type,
                "status": status
            } if case_type or status else None,
            limit=limit,
            offset=offset
        )

        results = await collector.search_cases(case_query)

        return {
            "query": query,
            "filters": {
                "case_type": case_type,
                "status": status
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
    Find similar validation cases using AI similarity analysis

    **Similarity Factors:**
    - Case type and category
    - Objectives and scope
    - Findings and outcomes
    - Improvement actions
    """
    try:
        similar_cases = await collector.find_similar(
            case_id=case_id,
            module="validation",
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
    Get detailed timeline for a validation case

    **Timeline Events:**
    - Planning and preparation
    - Execution milestones
    - Findings and observations
    - Corrective actions
    - Closure and review
    """
    try:
        timeline = await collector.get_timeline(
            case_id=case_id,
            module="validation"
        )

        return {
            "case_id": case_id,
            "module": "validation",
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
    case_type: Optional[str] = Query(None, description="Filter by case type"),
    days: int = Query(90, description="Analysis period in days", ge=7, le=365),
    engine=Depends(get_workflow_engine)
):
    """
    Analyze validation workflow patterns using AI

    **Pattern Analysis:**
    - Exercise effectiveness trends
    - Audit finding patterns
    - CAPA success rates
    - Compliance gaps
    """
    try:
        time_range = TimeRange(
            start=datetime.utcnow() - timedelta(days=days),
            end=datetime.utcnow()
        )

        patterns = await engine.analyze_patterns(
            module="validation",
            case_type=case_type,
            time_range=time_range
        )

        return {
            "module": "validation",
            "case_type": case_type,
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
    case_type: Optional[str] = Query(None, description="Filter by case type"),
    days: int = Query(30, description="Metrics period in days", ge=1, le=365),
    engine=Depends(get_workflow_engine)
):
    """
    Get validation performance metrics (ISO 9.1)

    **Metrics:**
    - Exercise completion rate
    - Audit effectiveness
    - CAPA closure rate
    - Improvement velocity
    - KPI achievement
    """
    try:
        time_range = TimeRange(
            start=datetime.utcnow() - timedelta(days=days),
            end=datetime.utcnow()
        )

        metrics = await engine.get_performance_metrics(
            module="validation",
            case_type=case_type,
            time_range=time_range
        )

        return {
            "module": "validation",
            "case_type": case_type,
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
# Exercise Intelligence (ISO 8.5)
# ============================================================================

@router.get("/exercises/effectiveness", response_model=Dict[str, Any])
async def analyze_exercise_effectiveness(
    exercise_type: Optional[str] = Query(None, description="Exercise type filter"),
    days: int = Query(180, description="Analysis period in days", ge=30, le=730),
    engine=Depends(get_workflow_engine)
):
    """
    Analyze exercise effectiveness using AI

    **Analysis:**
    - Exercise success rates
    - Learning outcomes
    - Improvement actions taken
    - Readiness impact
    """
    try:
        time_range = TimeRange(
            start=datetime.utcnow() - timedelta(days=days),
            end=datetime.utcnow()
        )

        effectiveness = await engine.analyze_exercise_effectiveness(
            exercise_type=exercise_type,
            time_range=time_range
        )

        return {
            "module": "validation",
            "case_type": "exercise",
            "exercise_type": exercise_type,
            "period_days": days,
            "effectiveness": effectiveness,
            "analyzed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing exercise effectiveness: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Audit Intelligence (ISO 9.2)
# ============================================================================

@router.get("/audits/findings-analysis", response_model=Dict[str, Any])
async def analyze_audit_findings(
    severity: Optional[str] = Query(None, description="Severity filter"),
    days: int = Query(365, description="Analysis period in days", ge=30, le=1095),
    engine=Depends(get_workflow_engine)
):
    """
    Analyze audit findings patterns using AI

    **Analysis:**
    - Common non-conformities
    - Severity trends
    - Root cause patterns
    - Closure effectiveness
    """
    try:
        time_range = TimeRange(
            start=datetime.utcnow() - timedelta(days=days),
            end=datetime.utcnow()
        )

        findings_analysis = await engine.analyze_audit_findings(
            severity=severity,
            time_range=time_range
        )

        return {
            "module": "validation",
            "case_type": "audit",
            "severity_filter": severity,
            "period_days": days,
            "findings_analysis": findings_analysis,
            "analyzed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing audit findings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CAPA Intelligence (ISO 10)
# ============================================================================

@router.get("/capa/effectiveness", response_model=Dict[str, Any])
async def analyze_capa_effectiveness(
    action_type: Optional[str] = Query(None, description="corrective or preventive"),
    days: int = Query(180, description="Analysis period in days", ge=30, le=730),
    engine=Depends(get_workflow_engine)
):
    """
    Analyze CAPA effectiveness using AI

    **Analysis:**
    - Closure rates
    - Root cause elimination
    - Recurrence prevention
    - Implementation success
    """
    try:
        time_range = TimeRange(
            start=datetime.utcnow() - timedelta(days=days),
            end=datetime.utcnow()
        )

        effectiveness = await engine.analyze_capa_effectiveness(
            action_type=action_type,
            time_range=time_range
        )

        return {
            "module": "validation",
            "case_type": "capa",
            "action_type": action_type,
            "period_days": days,
            "effectiveness": effectiveness,
            "analyzed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing CAPA effectiveness: {e}")
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
            "module": "validation",
            "components": health_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "module": "validation",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
