"""
Management API for System BCM Service
Provides endpoints for real-time dashboard and system management
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import asyncio
import json

from database.queries import (
    get_recent_cycles,
    get_cycle_by_id,
    get_recent_recoveries,
    get_recovery_by_id,
    get_recent_insights,
    get_insight_by_id,
    get_platform_health_current,
    get_platform_health_history,
    get_recent_patterns,
    get_recent_improvements,
    get_dashboard_stats,
    get_system_metrics
)
from engines.bcm_cycle_engine import BCMCycleEngine
from engines.recovery_engine import RecoveryEngine
from engines.learning_engine import LearningEngine
from config import settings

router = APIRouter(prefix="/management", tags=["management"])

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)

manager = ConnectionManager()

# Response Models
class DashboardStatsResponse(BaseModel):
    """Dashboard statistics"""
    total_cycles: int = Field(..., description="Total BCM cycles executed")
    successful_cycles: int = Field(..., description="Successful cycles")
    failed_cycles: int = Field(..., description="Failed cycles")
    success_rate: float = Field(..., description="Success rate percentage")
    total_recoveries: int = Field(..., description="Total recovery executions")
    successful_recoveries: int = Field(..., description="Successful recoveries")
    recovery_success_rate: float = Field(..., description="Recovery success rate percentage")
    rto_compliance_rate: float = Field(..., description="RTO compliance rate percentage")
    total_insights: int = Field(..., description="Total insights generated")
    insights_pending: int = Field(..., description="Insights pending action")
    insights_applied: int = Field(..., description="Insights applied")
    total_improvements: int = Field(..., description="Total improvements applied")
    avg_improvement_effectiveness: float = Field(..., description="Average improvement effectiveness")
    healthy_services: int = Field(..., description="Number of healthy services")
    total_services: int = Field(..., description="Total monitored services")
    platform_health_score: float = Field(..., description="Overall platform health score")
    current_status: str = Field(..., description="Current system status")
    last_cycle_time: Optional[datetime] = Field(None, description="Last cycle execution time")
    next_cycle_time: Optional[datetime] = Field(None, description="Next scheduled cycle time")

class CycleListResponse(BaseModel):
    """BCM cycle list item"""
    id: str
    cycle_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    status: str
    insights_generated: int
    improvements_applied: int
    rto_compliance_rate: Optional[float]
    learning_effectiveness: Optional[float]

class CycleDetailResponse(BaseModel):
    """Detailed BCM cycle information"""
    id: str
    cycle_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    status: str
    phases: List[Dict[str, Any]]
    bia_results: Optional[Dict[str, Any]]
    risk_results: Optional[Dict[str, Any]]
    recovery_results: Optional[Dict[str, Any]]
    priority_results: Optional[Dict[str, Any]]
    learning_results: Optional[Dict[str, Any]]
    insights_generated: int
    improvements_applied: int
    rto_compliance_rate: Optional[float]
    learning_effectiveness: Optional[float]
    platform_version: Optional[str]
    bcm_version: Optional[str]

class RecoveryListResponse(BaseModel):
    """Recovery execution list item"""
    id: str
    recovery_id: str
    procedure_name: str
    triggered_at: datetime
    completed_at: Optional[datetime]
    status: str
    duration_seconds: Optional[float]
    target_rto_seconds: int
    rto_met: Optional[bool]
    success: Optional[bool]

class RecoveryDetailResponse(BaseModel):
    """Detailed recovery execution information"""
    id: str
    recovery_id: str
    procedure_name: str
    triggered_by: str
    triggered_at: datetime
    completed_at: Optional[datetime]
    status: str
    duration_seconds: Optional[float]
    target_rto_seconds: int
    rto_met: Optional[bool]
    success: Optional[bool]
    steps_executed: Optional[Dict[str, Any]]
    error_message: Optional[str]
    metrics_before: Optional[Dict[str, Any]]
    metrics_after: Optional[Dict[str, Any]]

class InsightResponse(BaseModel):
    """Insight information"""
    id: str
    insight_id: str
    generated_at: datetime
    type: str
    category: str
    severity: str
    title: str
    description: str
    evidence: Optional[Dict[str, Any]]
    recommendations: Optional[Dict[str, Any]]
    status: str
    confidence_score: float
    priority: str
    applied: bool
    applied_at: Optional[datetime]
    effectiveness_score: Optional[float]

class PlatformHealthResponse(BaseModel):
    """Platform health information"""
    service_name: str
    status: str
    response_time_ms: Optional[float]
    last_check: datetime
    tier: str
    dependency_level: int
    error_message: Optional[str]

class PatternResponse(BaseModel):
    """Detected pattern information"""
    id: str
    pattern_id: str
    detected_at: datetime
    pattern_type: str
    description: str
    frequency: int
    confidence_score: float
    impact_level: str
    related_services: List[str]
    time_pattern: Optional[str]

class ImprovementResponse(BaseModel):
    """Applied improvement information"""
    id: str
    improvement_id: str
    applied_at: datetime
    type: str
    description: str
    based_on_insight_id: str
    confidence_score: float
    priority: str
    changes_made: Dict[str, Any]
    expected_impact: str
    actual_impact: Optional[str]
    effectiveness_score: Optional[float]
    status: str

class SystemMetricsResponse(BaseModel):
    """System metrics information"""
    timestamp: datetime
    cpu_usage_percent: float
    memory_usage_mb: float
    memory_usage_percent: float
    active_connections: int
    eventbus_queue_size: int
    database_pool_size: int
    response_time_ms: float
    uptime_hours: float

# Dashboard Overview
@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats_api():
    """
    Get dashboard statistics and overview

    Returns comprehensive statistics for the dashboard:
    - Cycle statistics (total, success rate)
    - Recovery statistics (total, RTO compliance)
    - Learning statistics (insights, improvements)
    - Platform health (services, health score)
    - System status (current, last/next cycle)
    """
    try:
        stats = await get_dashboard_stats()
        return DashboardStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard stats: {str(e)}")

# BCM Cycles
@router.get("/cycles", response_model=List[CycleListResponse])
async def get_cycles_list(
    limit: int = Query(50, ge=1, le=500, description="Number of cycles to return"),
    offset: int = Query(0, ge=0, description="Number of cycles to skip"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """
    Get list of BCM cycles

    Parameters:
    - limit: Maximum number of cycles to return (1-500)
    - offset: Number of cycles to skip (for pagination)
    - status: Filter by status (running, completed, failed)

    Returns list of recent BCM cycles with summary information
    """
    try:
        cycles = await get_recent_cycles(limit=limit, offset=offset, status_filter=status)
        return [CycleListResponse(**cycle) for cycle in cycles]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cycles: {str(e)}")

@router.get("/cycles/{cycle_id}", response_model=CycleDetailResponse)
async def get_cycle_detail(cycle_id: str):
    """
    Get detailed information for specific BCM cycle

    Parameters:
    - cycle_id: Unique cycle identifier

    Returns complete cycle information including:
    - All phase results
    - Generated insights
    - Applied improvements
    - Performance metrics
    """
    try:
        cycle = await get_cycle_by_id(cycle_id)
        if not cycle:
            raise HTTPException(status_code=404, detail=f"Cycle {cycle_id} not found")
        return CycleDetailResponse(**cycle)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cycle detail: {str(e)}")

# Recovery Executions
@router.get("/recoveries", response_model=List[RecoveryListResponse])
async def get_recoveries_list(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    procedure: Optional[str] = Query(None, description="Filter by procedure name"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """
    Get list of recovery executions

    Parameters:
    - limit: Maximum number of recoveries to return
    - offset: Number of recoveries to skip
    - procedure: Filter by procedure name
    - status: Filter by status

    Returns list of recent recovery executions
    """
    try:
        recoveries = await get_recent_recoveries(
            limit=limit,
            offset=offset,
            procedure_filter=procedure,
            status_filter=status
        )
        return [RecoveryListResponse(**recovery) for recovery in recoveries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recoveries: {str(e)}")

@router.get("/recoveries/{recovery_id}", response_model=RecoveryDetailResponse)
async def get_recovery_detail(recovery_id: str):
    """
    Get detailed information for specific recovery execution

    Returns complete recovery information including:
    - Execution steps
    - RTO compliance
    - Metrics before/after
    - Error details (if failed)
    """
    try:
        recovery = await get_recovery_by_id(recovery_id)
        if not recovery:
            raise HTTPException(status_code=404, detail=f"Recovery {recovery_id} not found")
        return RecoveryDetailResponse(**recovery)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recovery detail: {str(e)}")

# Insights
@router.get("/insights", response_model=List[InsightResponse])
async def get_insights_list(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, description="Filter by status"),
    type: Optional[str] = Query(None, description="Filter by type"),
    priority: Optional[str] = Query(None, description="Filter by priority")
):
    """
    Get list of generated insights

    Parameters:
    - limit: Maximum number of insights to return
    - offset: Number of insights to skip
    - status: Filter by status (pending, applied, rejected)
    - type: Filter by type (optimization, risk, pattern, etc.)
    - priority: Filter by priority (critical, high, medium, low)
    """
    try:
        insights = await get_recent_insights(
            limit=limit,
            offset=offset,
            status_filter=status,
            type_filter=type,
            priority_filter=priority
        )
        return [InsightResponse(**insight) for insight in insights]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch insights: {str(e)}")

@router.get("/insights/{insight_id}", response_model=InsightResponse)
async def get_insight_detail(insight_id: str):
    """Get detailed information for specific insight"""
    try:
        insight = await get_insight_by_id(insight_id)
        if not insight:
            raise HTTPException(status_code=404, detail=f"Insight {insight_id} not found")
        return InsightResponse(**insight)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch insight detail: {str(e)}")

# Platform Health
@router.get("/health/current", response_model=List[PlatformHealthResponse])
async def get_platform_health():
    """
    Get current platform health status for all services

    Returns health information for all monitored platform services:
    - Service status (healthy, degraded, down)
    - Response times
    - Error messages
    - Service tier and dependencies
    """
    try:
        health_data = await get_platform_health_current()
        return [PlatformHealthResponse(**service) for service in health_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch platform health: {str(e)}")

@router.get("/health/history")
async def get_health_history(
    service: Optional[str] = Query(None, description="Filter by service name"),
    hours: int = Query(24, ge=1, le=720, description="Hours of history to retrieve")
):
    """
    Get platform health history

    Parameters:
    - service: Filter by specific service (optional)
    - hours: Hours of history to retrieve (1-720)

    Returns historical health data for charting
    """
    try:
        history = await get_platform_health_history(service_filter=service, hours=hours)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch health history: {str(e)}")

# Patterns
@router.get("/patterns", response_model=List[PatternResponse])
async def get_patterns_list(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    pattern_type: Optional[str] = Query(None, description="Filter by pattern type")
):
    """
    Get list of detected patterns

    Returns behavioral patterns detected by the learning engine:
    - Service degradation patterns
    - Recovery patterns
    - Performance patterns
    - Failure patterns
    """
    try:
        patterns = await get_recent_patterns(
            limit=limit,
            offset=offset,
            type_filter=pattern_type
        )
        return [PatternResponse(**pattern) for pattern in patterns]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch patterns: {str(e)}")

# Improvements
@router.get("/improvements", response_model=List[ImprovementResponse])
async def get_improvements_list(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """
    Get list of applied improvements

    Returns improvements applied through practice learning:
    - Auto-applied improvements
    - Manual improvements
    - Effectiveness tracking
    """
    try:
        improvements = await get_recent_improvements(
            limit=limit,
            offset=offset,
            status_filter=status
        )
        return [ImprovementResponse(**improvement) for improvement in improvements]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch improvements: {str(e)}")

# System Metrics
@router.get("/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics_api():
    """
    Get current system metrics

    Returns real-time system performance metrics:
    - CPU and memory usage
    - Active connections
    - Queue sizes
    - Response times
    - Uptime
    """
    try:
        metrics = await get_system_metrics()
        return SystemMetricsResponse(**metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch system metrics: {str(e)}")

# Control Actions
@router.post("/cycles/trigger")
async def trigger_bcm_cycle():
    """
    Manually trigger a BCM cycle

    Starts a new BCM cycle execution immediately.
    Returns cycle_id for tracking.
    """
    try:
        engine = BCMCycleEngine()
        cycle_id = await engine.trigger_cycle()

        # Broadcast to WebSocket clients
        await manager.broadcast({
            "type": "cycle_triggered",
            "cycle_id": cycle_id,
            "timestamp": datetime.utcnow().isoformat()
        })

        return {
            "status": "success",
            "message": "BCM cycle triggered",
            "cycle_id": cycle_id,
            "triggered_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger cycle: {str(e)}")

@router.post("/recoveries/{procedure_name}/execute")
async def execute_recovery(procedure_name: str):
    """
    Manually execute a recovery procedure

    Parameters:
    - procedure_name: Name of recovery procedure to execute

    Valid procedures:
    - database_reconnect
    - redis_reconnect
    - service_health_check
    - event_pipeline_recovery
    - metrics_collection_recovery
    - memory_optimization
    - full_restart
    """
    try:
        engine = RecoveryEngine()
        recovery_id = await engine.execute_procedure(procedure_name, triggered_by="manual")

        # Broadcast to WebSocket clients
        await manager.broadcast({
            "type": "recovery_triggered",
            "procedure_name": procedure_name,
            "recovery_id": recovery_id,
            "timestamp": datetime.utcnow().isoformat()
        })

        return {
            "status": "success",
            "message": f"Recovery procedure '{procedure_name}' executed",
            "recovery_id": recovery_id,
            "triggered_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute recovery: {str(e)}")

@router.post("/insights/{insight_id}/apply")
async def apply_insight(insight_id: str):
    """
    Manually apply an insight

    Parameters:
    - insight_id: ID of insight to apply

    Applies the recommended changes from the insight.
    """
    try:
        engine = LearningEngine()
        result = await engine.apply_insight(insight_id)

        # Broadcast to WebSocket clients
        await manager.broadcast({
            "type": "insight_applied",
            "insight_id": insight_id,
            "timestamp": datetime.utcnow().isoformat()
        })

        return {
            "status": "success",
            "message": "Insight applied",
            "insight_id": insight_id,
            "applied_at": datetime.utcnow().isoformat(),
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply insight: {str(e)}")

@router.post("/insights/{insight_id}/reject")
async def reject_insight(insight_id: str, reason: str = None):
    """
    Reject an insight

    Parameters:
    - insight_id: ID of insight to reject
    - reason: Reason for rejection (optional)
    """
    try:
        engine = LearningEngine()
        await engine.reject_insight(insight_id, reason)

        return {
            "status": "success",
            "message": "Insight rejected",
            "insight_id": insight_id,
            "rejected_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reject insight: {str(e)}")

# WebSocket for Real-Time Updates
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time dashboard updates

    Sends real-time updates for:
    - Cycle progress
    - Recovery executions
    - New insights
    - Platform health changes
    - System metrics

    Message format:
    {
        "type": "event_type",
        "data": {...},
        "timestamp": "2025-10-09T12:34:56Z"
    }
    """
    await manager.connect(websocket)

    try:
        # Send initial connection success
        await manager.send_personal_message({
            "type": "connected",
            "message": "WebSocket connected successfully",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)

        # Keep connection alive and send periodic updates
        while True:
            try:
                # Send heartbeat every 30 seconds
                await asyncio.sleep(30)
                await manager.send_personal_message({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)

                # Send current metrics
                metrics = await get_system_metrics()
                await manager.send_personal_message({
                    "type": "metrics_update",
                    "data": metrics,
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)

            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket error: {e}")
                break

    finally:
        manager.disconnect(websocket)

# Export router
__all__ = ["router", "manager"]
