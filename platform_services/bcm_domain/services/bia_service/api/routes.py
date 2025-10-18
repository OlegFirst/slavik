"""
BIA API Routes

All 12 BIA endpoints from original main.py.
Thin routing layer - business logic in services.
Now with PostgreSQL persistence via dependency injection.
JWT-based authentication with RBAC.
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ..models.domain import (
    BIAProcess,
    BIAProcessCreate,
    AIRTOSuggestion,
    BIASummaryReport,
)
from ..models.enums import CriticalityLevel, ProcessStatus
from ..services.bia_service import BIAService
from ..services.ai_service import AIService
from ..services.report_service import ReportService
from ..repositories.bia_repository import BIARepository
from ..database.connection import get_db
from shared.auth import get_current_user, Permission, require_permission
from shared.exceptions import TenantMismatchError
from shared.utils.parallel import BulkOperationReport

logger = logging.getLogger(__name__)


# Pydantic models for bulk operations
class BulkCreateRequest(BaseModel):
    """Request model for bulk create operations"""
    processes: List[BIAProcessCreate]
    max_concurrency: Optional[int] = 10


class BulkUpdateRequest(BaseModel):
    """Request model for bulk update operations"""
    updates: List[Dict[str, Any]]
    max_concurrency: Optional[int] = 10


class BulkDeleteRequest(BaseModel):
    """Request model for bulk delete operations"""
    process_ids: List[int]
    max_concurrency: Optional[int] = 10

# Create router
router = APIRouter(prefix="/api/bia")


# Dependency injection factories
def get_bia_repository(db: AsyncSession = Depends(get_db)) -> BIARepository:
    """Get BIA repository with database session"""
    return BIARepository(db)


def get_bia_service(repo: BIARepository = Depends(get_bia_repository)) -> BIAService:
    """Dependency injection for BIA Service"""
    return BIAService(repo)


def get_ai_service(repo: BIARepository = Depends(get_bia_repository)) -> AIService:
    """Dependency injection for AI Service"""
    return AIService(repo)


def get_report_service(repo: BIARepository = Depends(get_bia_repository)) -> ReportService:
    """Dependency injection for Report Service"""
    return ReportService(repo)


def verify_tenant_access(current_user: dict, tenant_id: str) -> None:
    """Verify user has access to tenant"""
    if current_user.get("tenant_id") != tenant_id:
        raise TenantMismatchError(
            user_tenant=current_user.get("tenant_id"),
            resource_tenant=tenant_id
        )


# ===== ENDPOINTS (12 total) =====

@router.post("/processes", response_model=BIAProcess, tags=["BIA"],
             summary="Create BIA Process",
             responses={
                 201: {"description": "BIA Process created successfully"},
                 400: {"description": "Validation error - invalid input data"},
                 401: {"description": "Unauthorized - missing or invalid JWT token"},
                 403: {"description": "Forbidden - tenant mismatch or insufficient permissions"},
                 422: {"description": "Business rule violation"}
             })
@require_permission(Permission.BIA_CREATE)
async def create_bia_process(
    process: BIAProcessCreate,
    service: BIAService = Depends(get_bia_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Create new Business Impact Analysis process.

    **ISO 22301:2019 Clause 8.2.2** - Business Impact Analysis

    Creates a comprehensive BIA process with:
    - **Criticality Assessment**: Classify process as CRITICAL, HIGH, MEDIUM, or LOW
    - **Recovery Objectives**: Define RTO (Recovery Time Objective), RPO (Recovery Point Objective), MTPD (Maximum Tolerable Period of Disruption)
    - **Impact Analysis**: Document financial, operational, reputational, and regulatory impacts
    - **Dependency Mapping**: Identify upstream/downstream dependencies
    - **Resource Requirements**: Specify personnel, facilities, technology, and information needs

    **Request Body Example:**
    ```json
    {
      "tenant_id": "tenant-123",
      "name": "Payment Processing System",
      "description": "Core payment processing for customer transactions",
      "department": "Finance Operations",
      "process_owner": "jane.smith@company.com",
      "criticality": "CRITICAL",
      "rto_hours": 2,
      "rpo_hours": 1,
      "mtpd_hours": 4,
      "financial_impact": {
        "1_hour": 50000,
        "4_hours": 200000,
        "24_hours": 1200000
      },
      "dependencies": [
        {
          "type": "technology",
          "name": "Payment Gateway API",
          "criticality": 5,
          "required": true
        }
      ]
    }
    ```

    **Response (201 Created):**
    Returns the created BIA process with generated ID and timestamps.

    **Permissions Required:** BIA_CREATE
    """
    # Verify tenant access
    verify_tenant_access(current_user, process.tenant_id)

    return await service.create_process(process)


@router.get("/processes", response_model=List[BIAProcess])
@require_permission(Permission.BIA_VIEW)
async def list_bia_processes(
    tenant_id: str = Query(...),
    criticality: Optional[CriticalityLevel] = None,
    status: Optional[ProcessStatus] = None,
    service: BIAService = Depends(get_bia_service),
    current_user: dict = Depends(get_current_user)
):
    """
    List BIA processes with filters.

    Original: GET /api/bia/processes
    Requires: BIA_VIEW permission
    """
    # Verify tenant access
    verify_tenant_access(current_user, tenant_id)

    return await service.list_processes(tenant_id, criticality, status)


@router.get("/processes/{process_id}", response_model=BIAProcess)
@require_permission(Permission.BIA_VIEW)
async def get_bia_process(
    process_id: int,
    tenant_id: str = Query(...),
    service: BIAService = Depends(get_bia_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Get BIA process by ID.

    Original: GET /api/bia/processes/{process_id}
    Requires: BIA_VIEW permission
    """
    # Verify tenant access
    verify_tenant_access(current_user, tenant_id)

    return await service.get_process(process_id, tenant_id)


@router.put("/processes/{process_id}", response_model=BIAProcess)
@require_permission(Permission.BIA_UPDATE)
async def update_bia_process(
    process_id: int,
    updates: Dict[str, Any],
    tenant_id: str = Query(...),
    service: BIAService = Depends(get_bia_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Update BIA process.

    Original: PUT /api/bia/processes/{process_id}
    Requires: BIA_UPDATE permission
    """
    # Verify tenant access
    verify_tenant_access(current_user, tenant_id)

    return await service.update_process(process_id, tenant_id, updates)


@router.delete("/processes/{process_id}")
@require_permission(Permission.BIA_DELETE)
async def delete_bia_process(
    process_id: int,
    tenant_id: str = Query(...),
    service: BIAService = Depends(get_bia_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete BIA process.

    Original: DELETE /api/bia/processes/{process_id}
    Requires: BIA_DELETE permission
    """
    # Verify tenant access
    verify_tenant_access(current_user, tenant_id)

    return await service.delete_process(process_id, tenant_id)


@router.post("/processes/{process_id}/complete")
@require_permission(Permission.BIA_COMPLETE)
async def complete_bia_process(
    process_id: int,
    tenant_id: str = Query(...),
    service: BIAService = Depends(get_bia_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Mark BIA process as completed.

    Original: POST /api/bia/processes/{process_id}/complete
    Requires: BIA_COMPLETE permission
    """
    # Verify tenant access
    verify_tenant_access(current_user, tenant_id)

    return await service.complete_process(process_id, tenant_id)


@router.post("/processes/{process_id}/suggest-rto", response_model=AIRTOSuggestion, tags=["AI Analysis"],
             summary="AI-Powered RTO/RPO/MTPD Suggestion",
             responses={
                 200: {"description": "AI suggestions generated successfully"},
                 404: {"description": "BIA process not found"},
                 401: {"description": "Unauthorized"},
                 403: {"description": "Forbidden - insufficient permissions"}
             })
@require_permission(Permission.BIA_AI_SUGGEST)
async def suggest_rto(
    process_id: int,
    tenant_id: str = Query(...),
    ai_service: AIService = Depends(get_ai_service),
    current_user: dict = Depends(get_current_user)
):
    """
    AI-powered RTO/RPO/MTPD suggestion based on process characteristics.

    Uses machine learning to analyze:
    - **Process Criticality**: CRITICAL processes get shorter RTOs
    - **Financial Impact**: Higher impact → stricter recovery objectives
    - **Industry Benchmarks**: Compare against industry standards
    - **Regulatory Requirements**: Factor in compliance mandates
    - **Dependency Complexity**: More dependencies → longer RTOs

    **Response Example:**
    ```json
    {
      "process_id": 123,
      "suggested_rto_hours": 2,
      "suggested_rpo_hours": 1,
      "suggested_mtpd_hours": 4,
      "confidence_score": 0.92,
      "reasoning": "CRITICAL process with $200K/4hr impact. Financial services benchmark: 1-4hr RTO.",
      "industry_benchmark": {
        "industry": "financial_services",
        "typical_rto_range": "1-4 hours",
        "regulatory_drivers": ["PCI-DSS", "SOX"]
      },
      "alternative_scenarios": [
        {
          "rto_hours": 1,
          "cost_increase": 150000,
          "description": "Premium recovery (1hr RTO) requires hot standby"
        }
      ]
    }
    ```

    **Permissions Required:** BIA_AI_SUGGEST
    """
    # Verify tenant access
    verify_tenant_access(current_user, tenant_id)

    return await ai_service.suggest_rto(process_id, tenant_id)


@router.post("/processes/{process_id}/discover-dependencies")
@require_permission(Permission.BIA_AI_SUGGEST)
async def discover_dependencies(
    process_id: int,
    tenant_id: str = Query(...),
    ai_service: AIService = Depends(get_ai_service),
    current_user: dict = Depends(get_current_user)
):
    """
    AI-powered dependency discovery.

    Original: POST /api/bia/processes/{process_id}/discover-dependencies
    Requires: BIA_AI_SUGGEST permission
    """
    # Verify tenant access
    verify_tenant_access(current_user, tenant_id)

    return await ai_service.discover_dependencies(process_id, tenant_id)


@router.get("/reports/summary", response_model=BIASummaryReport)
@require_permission(Permission.BIA_VIEW)
async def get_summary_report(
    tenant_id: str = Query(...),
    report_service: ReportService = Depends(get_report_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Get BIA summary report for tenant.

    Original: GET /api/bia/reports/summary
    Requires: BIA_VIEW permission
    """
    # Verify tenant access
    verify_tenant_access(current_user, tenant_id)

    return await report_service.get_summary_report(tenant_id)


@router.get("/reports/critical-processes")
@require_permission(Permission.BIA_VIEW)
async def get_critical_processes_report(
    tenant_id: str = Query(...),
    report_service: ReportService = Depends(get_report_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Get critical processes report.

    Original: GET /api/bia/reports/critical-processes
    Requires: BIA_VIEW permission
    """
    # Verify tenant access
    verify_tenant_access(current_user, tenant_id)

    return await report_service.get_critical_processes_report(tenant_id)


@router.get("/reports/dependencies")
@require_permission(Permission.BIA_VIEW)
async def get_dependencies_report(
    tenant_id: str = Query(...),
    report_service: ReportService = Depends(get_report_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Get dependencies mapping report.

    Original: GET /api/bia/reports/dependencies
    Requires: BIA_VIEW permission
    """
    # Verify tenant access
    verify_tenant_access(current_user, tenant_id)

    return await report_service.get_dependencies_report(tenant_id)


# ===== BULK OPERATIONS ENDPOINTS =====

@router.post("/processes/bulk", response_model=Dict[str, Any])
@require_permission(Permission.BIA_CREATE)
async def bulk_create_processes(
    request: BulkCreateRequest,
    tenant_id: str = Query(...),
    service: BIAService = Depends(get_bia_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Create multiple BIA processes in parallel.

    Processes up to max_concurrency items concurrently.
    Returns success/failure statistics with partial success support.

    Requires: BIA_CREATE permission
    """
    # Verify tenant access for first process (all must be same tenant)
    if request.processes:
        verify_tenant_access(current_user, request.processes[0].tenant_id)

    report: BulkOperationReport = await service.bulk_create_processes(
        processes=request.processes,
        user_id=current_user.get("sub", "unknown"),
        max_concurrency=request.max_concurrency
    )

    return {
        "total": report.total_count,
        "success": report.success_count,
        "failed": report.failure_count,
        "timeout": report.timeout_count,
        "success_rate": report.success_rate,
        "duration_ms": report.total_duration_ms,
        "failures": [
            {
                "index": f.index,
                "name": f.input_data.name if hasattr(f.input_data, 'name') else None,
                "error": f.error
            }
            for f in report.failures
        ]
    }


@router.patch("/processes/bulk", response_model=Dict[str, Any])
@require_permission(Permission.BIA_UPDATE)
async def bulk_update_processes(
    request: BulkUpdateRequest,
    tenant_id: str = Query(...),
    service: BIAService = Depends(get_bia_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Update multiple BIA processes in parallel.

    Each update dict must contain 'process_id' field plus fields to update.

    Example:
        {
            "updates": [
                {"process_id": 1, "rto_hours": 4},
                {"process_id": 2, "criticality": "high"}
            ]
        }

    Requires: BIA_UPDATE permission
    """
    # Verify tenant access
    verify_tenant_access(current_user, tenant_id)

    report: BulkOperationReport = await service.bulk_update_processes(
        updates=request.updates,
        tenant_id=tenant_id,
        user_id=current_user.get("sub", "unknown"),
        max_concurrency=request.max_concurrency
    )

    return {
        "total": report.total_count,
        "success": report.success_count,
        "failed": report.failure_count,
        "success_rate": report.success_rate,
        "duration_ms": report.total_duration_ms,
        "failures": [
            {
                "index": f.index,
                "process_id": f.input_data.get("process_id"),
                "error": f.error
            }
            for f in report.failures
        ]
    }


@router.delete("/processes/bulk", response_model=Dict[str, Any])
@require_permission(Permission.BIA_DELETE)
async def bulk_delete_processes(
    request: BulkDeleteRequest,
    tenant_id: str = Query(...),
    service: BIAService = Depends(get_bia_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete multiple BIA processes in parallel.

    Requires: BIA_DELETE permission
    """
    # Verify tenant access
    verify_tenant_access(current_user, tenant_id)

    report: BulkOperationReport = await service.bulk_delete_processes(
        process_ids=request.process_ids,
        tenant_id=tenant_id,
        user_id=current_user.get("sub", "unknown"),
        max_concurrency=request.max_concurrency
    )

    return {
        "total": report.total_count,
        "success": report.success_count,
        "failed": report.failure_count,
        "success_rate": report.success_rate,
        "duration_ms": report.total_duration_ms,
        "failures": [
            {
                "index": f.index,
                "process_id": f.input_data,
                "error": f.error
            }
            for f in report.failures
        ]
    }


@router.post("/processes/bulk/validate", response_model=Dict[str, Any])
@require_permission(Permission.BIA_VIEW)
async def bulk_validate_processes(
    request: BulkCreateRequest,
    service: BIAService = Depends(get_bia_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Validate multiple BIA processes without creating them.

    Useful for pre-validating bulk imports before actual creation.

    Requires: BIA_VIEW permission
    """
    report: BulkOperationReport = await service.bulk_validate_processes(
        processes=request.processes,
        max_concurrency=request.max_concurrency
    )

    return {
        "total": report.total_count,
        "valid": report.success_count,
        "invalid": report.failure_count,
        "validation_rate": report.success_rate,
        "duration_ms": report.total_duration_ms,
        "invalid_processes": [
            {
                "index": f.index,
                "name": f.input_data.name if hasattr(f.input_data, 'name') else None,
                "error": f.error
            }
            for f in report.failures
        ]
    }
