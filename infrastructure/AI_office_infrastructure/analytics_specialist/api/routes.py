"""
API Routes
==========

REST API endpoints for Analytics Specialist service.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks

from config import settings
from models import (
    AnalysisRequest,
    HealthCheckResponse,
    InsightsResponse,
    AnalysisType,
    CompetencyLevel,
)
from core import AnalyticsCore
from workflows import daily_health_check, investigate_incident

logger = logging.getLogger(__name__)

# Create routers
health_router = APIRouter(prefix="/health", tags=["Health"])
analysis_router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])
workflow_router = APIRouter(prefix="/api/v1/workflows", tags=["Workflows"])

# Service start time
SERVICE_START_TIME = datetime.now()


# ============================================================================
# HEALTH ENDPOINTS
# ============================================================================

@health_router.get("", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint

    Returns service health status and metadata.

    Example:
        ```bash
        curl http://localhost:8051/health
        ```
    """
    uptime = (datetime.now() - SERVICE_START_TIME).total_seconds()

    # Get available tools based on competency
    core = AnalyticsCore()
    available_tools = list(core.tools.keys())

    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        competency_level=CompetencyLevel(settings.COMPETENCY_LEVEL),
        available_tools=available_tools,
        uptime_seconds=uptime
    )


# ============================================================================
# ANALYSIS ENDPOINTS
# ============================================================================

@analysis_router.post("/analyze")
async def analyze_platform(request: AnalysisRequest) -> Dict[str, Any]:
    """
    Perform platform analysis

    Supports different analysis types:
    - platform_health: Comprehensive health analysis
    - process_mining: Process-specific analysis
    - dependency_analysis: Dependency conflicts
    - incident_investigation: Incident root cause

    Args:
        request: Analysis request with type and parameters

    Returns:
        Analysis report

    Example:
        ```bash
        curl -X POST http://localhost:8051/api/v1/analytics/analyze \\
          -H "Content-Type: application/json" \\
          -d '{
            "analysis_type": "platform_health",
            "requester": "ai-orchestrator"
          }'
        ```
    """
    try:
        core = AnalyticsCore()
        await core.initialize()

        logger.info(
            f"Analysis requested: type={request.analysis_type}, "
            f"requester={request.requester}"
        )

        if request.analysis_type == AnalysisType.PLATFORM_HEALTH:
            report = await core.analyze_platform_health()

        elif request.analysis_type == AnalysisType.INCIDENT_INVESTIGATION:
            incident_id = request.parameters.get("incident_id")
            if not incident_id:
                raise HTTPException(status_code=400, detail="incident_id required")

            report = await core.investigate_incident(incident_id)

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Analysis type {request.analysis_type} not yet implemented"
            )

        return {
            "status": "success",
            "report_id": report.id,
            "analysis_type": report.analysis_type.value,
            "health_score": report.overall_health_score,
            "summary": report.summary,
            "total_insights": len(report.insights),
            "critical_insights": len(report.critical_insights),
            "recommendations": len(report.recommendations),
            "generated_at": report.generated_at.isoformat(),
            "report": report.model_dump()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@analysis_router.get("/insights")
async def get_platform_insights(
    context_type: Optional[str] = None,
    timeframe_days: int = 7
) -> Dict[str, Any]:
    """
    Get platform insights for AI Orchestrator

    Provides cached insights from last analysis.

    Args:
        context_type: Type of context (optional)
        timeframe_days: Timeframe in days

    Returns:
        Platform insights

    Example:
        ```bash
        curl http://localhost:8051/api/v1/analytics/insights
        ```
    """
    try:
        core = AnalyticsCore()
        await core.initialize()

        insights = await core.get_platform_insights(
            context_type=context_type,
            timeframe_days=timeframe_days
        )

        return insights

    except Exception as e:
        logger.error(f"Failed to get insights: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WORKFLOW ENDPOINTS
# ============================================================================

@workflow_router.post("/daily-health-check")
async def trigger_daily_health_check(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Manually trigger daily health check workflow

    Can be used for testing or on-demand execution.

    Returns:
        Workflow trigger confirmation

    Example:
        ```bash
        curl -X POST http://localhost:8051/api/v1/workflows/daily-health-check
        ```
    """
    try:
        # Run in background
        background_tasks.add_task(daily_health_check)

        return {
            "status": "triggered",
            "workflow": "daily_health_check",
            "message": "Workflow started in background",
            "triggered_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to trigger workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@workflow_router.post("/investigate-incident")
async def trigger_incident_investigation(
    incident_id: str,
    incident_details: Optional[Dict[str, Any]] = None,
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """
    Trigger incident investigation workflow

    Args:
        incident_id: Incident identifier
        incident_details: Additional incident information
        background_tasks: FastAPI background tasks

    Returns:
        Investigation trigger confirmation

    Example:
        ```bash
        curl -X POST http://localhost:8051/api/v1/workflows/investigate-incident \\
          -H "Content-Type: application/json" \\
          -d '{
            "incident_id": "inc_001",
            "incident_details": {
              "type": "service_outage",
              "affected_service": "workflow_intelligence"
            }
          }'
        ```
    """
    try:
        # Run in background if background_tasks provided
        if background_tasks:
            background_tasks.add_task(
                investigate_incident,
                incident_id,
                incident_details
            )

            return {
                "status": "triggered",
                "workflow": "incident_investigation",
                "incident_id": incident_id,
                "message": "Investigation started in background",
                "triggered_at": datetime.now().isoformat()
            }
        else:
            # Run synchronously
            result = await investigate_incident(incident_id, incident_details)
            return result

    except Exception as e:
        logger.error(f"Failed to trigger investigation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TOOL ENDPOINTS
# ============================================================================

@analysis_router.post("/tools/ast-analysis")
async def run_ast_analysis(project_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Run AST analysis on Python code

    Returns:
        AST analysis results

    Example:
        ```bash
        curl -X POST http://localhost:8051/api/v1/analytics/tools/ast-analysis
        ```
    """
    try:
        core = AnalyticsCore()
        await core.initialize()

        if "ast_analyzer" not in core.tools:
            raise HTTPException(
                status_code=403,
                detail="AST Analyzer not available at current competency level"
            )

        tool = core.tools["ast_analyzer"]
        results = await tool.analyze_project(project_path)

        return {
            "status": "success",
            "tool": "ast_analyzer",
            **results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AST analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analysis_router.post("/tools/api-map")
async def run_api_mapping() -> Dict[str, Any]:
    """
    Map all API endpoints across services

    Returns:
        API map results
    """
    try:
        core = AnalyticsCore()
        await core.initialize()

        if "api_mapper" not in core.tools:
            raise HTTPException(
                status_code=403,
                detail="API Mapper not available at current competency level"
            )

        tool = core.tools["api_mapper"]
        results = await tool.map_all_apis()

        return {
            "status": "success",
            "tool": "api_mapper",
            **results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API mapping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analysis_router.post("/tools/dependency-validation")
async def run_dependency_validation() -> Dict[str, Any]:
    """
    Validate all dependencies

    Returns:
        Validation results with issues
    """
    try:
        core = AnalyticsCore()
        await core.initialize()

        if "dependency_validator" not in core.tools:
            raise HTTPException(
                status_code=403,
                detail="Dependency Validator not available at current competency level"
            )

        tool = core.tools["dependency_validator"]
        results = await tool.validate_all_dependencies()

        return {
            "status": "success",
            "tool": "dependency_validator",
            **results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dependency validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analysis_router.post("/tools/security-scan")
async def run_security_scan(project_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Run security scan on codebase

    Returns:
        Security scan results with vulnerabilities
    """
    try:
        core = AnalyticsCore()
        await core.initialize()

        if "security_scanner" not in core.tools:
            raise HTTPException(
                status_code=403,
                detail="Security Scanner not available at current competency level"
            )

        tool = core.tools["security_scanner"]
        results = await tool.scan_project(project_path)

        return {
            "status": "success",
            "tool": "security_scanner",
            **results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Security scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analysis_router.post("/tools/module-scan")
async def run_module_scan(project_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Scan all Python modules

    Returns:
        Module catalog
    """
    try:
        core = AnalyticsCore()
        await core.initialize()

        if "module_scanner" not in core.tools:
            raise HTTPException(
                status_code=403,
                detail="Module Scanner not available at current competency level"
            )

        tool = core.tools["module_scanner"]
        results = await tool.scan_all_modules(project_path)

        return {
            "status": "success",
            "tool": "module_scanner",
            **results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Module scanning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@analysis_router.get("/status")
async def get_service_status() -> Dict[str, Any]:
    """
    Get detailed service status

    Returns:
        Service status including all integrations

    Example:
        ```bash
        curl http://localhost:8051/api/v1/analytics/status
        ```
    """
    try:
        core = AnalyticsCore()
        await core.initialize()

        # Check all clients
        pa_health = await core.pa_client.health_check()
        mio_health = await core.mio_client.health_check()

        # Check tools
        tools_status = {}
        for name, tool in core.tools.items():
            tools_status[name] = {
                "available": tool.available,
                "description": tool.description,
                "competency_required": tool.competency_required
            }

        return {
            "service": "analytics-specialist",
            "status": "healthy",
            "version": "1.0.0",
            "competency_level": settings.COMPETENCY_LEVEL,
            "uptime_seconds": (datetime.now() - SERVICE_START_TIME).total_seconds(),

            # Integrations
            "integrations": {
                "process_analytics": pa_health.get("status", "unknown"),
                "mio_manager": mio_health.get("status", "unknown"),
            },

            # Tools
            "tools": tools_status,

            # Config
            "config": {
                "port": settings.PORT,
                "daily_health_check_enabled": settings.DAILY_HEALTH_CHECK_ENABLED,
                "continuous_improvement_enabled": settings.CONTINUOUS_IMPROVEMENT_ENABLED,
            }
        }

    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        return {
            "service": "analytics-specialist",
            "status": "error",
            "error": str(e)
        }
