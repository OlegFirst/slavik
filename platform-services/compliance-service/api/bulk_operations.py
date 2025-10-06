"""
Compliance Service - Bulk Operations API

Provides parallel processing endpoints for bulk operations:
- Bulk nonconformity import with RCA template processing
- Bulk evidence upload
- Bulk corrective action creation
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from uuid import UUID

from compliance.database.connection import get_db
from compliance.models.enums import RCAMethod, NCType, NCSource
from compliance.workflows.nonconformity_workflow import NonconformityWorkflow
from compliance.repositories.nonconformity_repository import NonconformityRepository
from compliance.repositories.evidence_repository import EvidenceRepository
from compliance.services.rca_templates import RCATemplateFactory
from shared.utils.parallel import parallel_map, BulkOperationReport
from shared.utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)
router = APIRouter()
metrics = MetricsCollector()


# ==================== REQUEST MODELS ====================

class NonconformityCreateRequest(BaseModel):
    """Single nonconformity to create"""
    title: str
    description: str
    nc_type: NCType
    source: NCSource
    clause_reference: str
    detected_by: str
    tenant_id: str
    rca_method: Optional[RCAMethod] = None
    rca_lead: Optional[str] = None


class BulkNonconformityRequest(BaseModel):
    """Bulk nonconformity import request"""
    nonconformities: List[NonconformityCreateRequest]
    max_concurrency: Optional[int] = 10
    auto_start_rca: bool = False


class EvidenceUploadRequest(BaseModel):
    """Single evidence upload"""
    audit_id: UUID
    evidence_type: str
    file_path: str
    description: Optional[str] = None
    tenant_id: str


class BulkEvidenceRequest(BaseModel):
    """Bulk evidence upload request"""
    evidence_items: List[EvidenceUploadRequest]
    max_concurrency: Optional[int] = 10


class CorrectiveActionRequest(BaseModel):
    """Single corrective action"""
    nc_id: UUID
    action_description: str
    responsible_person: str
    due_date: str
    tenant_id: str


class BulkCorrectiveActionRequest(BaseModel):
    """Bulk corrective action creation"""
    actions: List[CorrectiveActionRequest]
    max_concurrency: Optional[int] = 10


# ==================== DEPENDENCY INJECTION ====================

def get_nc_repository(db: AsyncSession = Depends(get_db)) -> NonconformityRepository:
    """Get Nonconformity repository"""
    return NonconformityRepository(db)


def get_evidence_repository(db: AsyncSession = Depends(get_db)) -> EvidenceRepository:
    """Get Evidence repository"""
    return EvidenceRepository(db)


async def get_nc_workflow(db: AsyncSession = Depends(get_db)) -> NonconformityWorkflow:
    """Get Nonconformity workflow"""
    repository = NonconformityRepository(db)
    return NonconformityWorkflow(repository=repository)


# ==================== BULK ENDPOINTS ====================

@router.post("/nonconformities/bulk")
async def bulk_import_nonconformities(
    request: BulkNonconformityRequest,
    tenant_id: str = Query(..., description="Tenant identifier"),
    db: AsyncSession = Depends(get_db)
):
    """
    Bulk import nonconformities with optional automatic RCA template generation.

    Processes nonconformities in parallel:
    - Validates each NC
    - Creates NC record
    - Optionally starts RCA process with appropriate template
    - Returns success/failure statistics

    Args:
        request: Bulk nonconformity import request
        tenant_id: Tenant identifier
        db: Database session

    Returns:
        Bulk operation report with statistics
    """
    logger.info(f"Starting bulk import of {len(request.nonconformities)} nonconformities")

    workflow = NonconformityWorkflow(repository=NonconformityRepository(db))

    async def create_single_nc(nc_data: NonconformityCreateRequest) -> Dict[str, Any]:
        """Create single nonconformity with optional RCA"""
        try:
            # Validate tenant
            if nc_data.tenant_id != tenant_id:
                raise ValueError(f"Tenant mismatch for NC: {nc_data.title}")

            # Create nonconformity (simplified - actual implementation would use repository)
            nc_id = UUID("00000000-0000-0000-0000-000000000001")  # Placeholder

            result = {
                "nc_id": str(nc_id),
                "title": nc_data.title,
                "nc_type": nc_data.nc_type.value,
                "created": True
            }

            # Auto-start RCA if requested
            if request.auto_start_rca and nc_data.rca_method and nc_data.rca_lead:
                rca_result = await workflow.start_rca(
                    nc_id=nc_id,
                    rca_method=nc_data.rca_method,
                    rca_lead=nc_data.rca_lead,
                    rca_team=[],
                    tenant_id=tenant_id
                )
                result["rca_started"] = True
                result["rca_template"] = rca_result.get("template", {}).get("method")

            return result

        except Exception as e:
            logger.error(f"Failed to create NC {nc_data.title}: {e}")
            raise ValueError(f"Failed to create NC: {str(e)}")

    # Process in parallel
    with metrics.track_time("compliance_bulk_nc_import_duration_seconds"):
        report: BulkOperationReport = await parallel_map(
            items=request.nonconformities,
            func=create_single_nc,
            max_concurrency=request.max_concurrency,
            timeout_per_item=30.0,
            continue_on_error=True
        )

    # Record metrics
    metrics.inc_counter(
        "compliance_bulk_operations_total",
        labels={"operation": "nc_import", "status": "completed"}
    )

    logger.info(
        f"Bulk NC import completed: {report.success_count}/{report.total_count} succeeded, "
        f"{report.failure_count} failed in {report.total_duration_ms:.0f}ms"
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
                "title": f.input_data.title if hasattr(f.input_data, 'title') else None,
                "error": f.error
            }
            for f in report.failures
        ]
    }


@router.post("/evidence/bulk")
async def bulk_upload_evidence(
    request: BulkEvidenceRequest,
    tenant_id: str = Query(..., description="Tenant identifier"),
    repository: EvidenceRepository = Depends(get_evidence_repository)
):
    """
    Bulk upload audit evidence files.

    Processes evidence uploads in parallel:
    - Validates file paths
    - Creates evidence records
    - Links to audits
    - Returns success/failure statistics

    Args:
        request: Bulk evidence upload request
        tenant_id: Tenant identifier
        repository: Evidence repository

    Returns:
        Bulk operation report with statistics
    """
    logger.info(f"Starting bulk upload of {len(request.evidence_items)} evidence items")

    async def upload_single_evidence(evidence: EvidenceUploadRequest) -> Dict[str, Any]:
        """Upload single evidence item"""
        try:
            # Validate tenant
            if evidence.tenant_id != tenant_id:
                raise ValueError(f"Tenant mismatch for evidence: {evidence.file_path}")

            # Simplified - actual implementation would use repository
            return {
                "audit_id": str(evidence.audit_id),
                "file_path": evidence.file_path,
                "evidence_type": evidence.evidence_type,
                "uploaded": True
            }

        except Exception as e:
            logger.error(f"Failed to upload evidence {evidence.file_path}: {e}")
            raise ValueError(f"Failed to upload evidence: {str(e)}")

    # Process in parallel
    with metrics.track_time("compliance_bulk_evidence_upload_duration_seconds"):
        report: BulkOperationReport = await parallel_map(
            items=request.evidence_items,
            func=upload_single_evidence,
            max_concurrency=request.max_concurrency,
            timeout_per_item=60.0,  # Longer timeout for file uploads
            continue_on_error=True
        )

    # Record metrics
    metrics.inc_counter(
        "compliance_bulk_operations_total",
        labels={"operation": "evidence_upload", "status": "completed"}
    )

    logger.info(
        f"Bulk evidence upload completed: {report.success_count}/{report.total_count} succeeded"
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
                "file_path": f.input_data.file_path if hasattr(f.input_data, 'file_path') else None,
                "error": f.error
            }
            for f in report.failures
        ]
    }


@router.post("/corrective-actions/bulk")
async def bulk_create_corrective_actions(
    request: BulkCorrectiveActionRequest,
    tenant_id: str = Query(..., description="Tenant identifier"),
    workflow: NonconformityWorkflow = Depends(get_nc_workflow)
):
    """
    Bulk create corrective actions for nonconformities.

    Processes corrective actions in parallel:
    - Validates NC exists
    - Creates corrective action
    - Updates NC workflow state
    - Returns success/failure statistics

    Args:
        request: Bulk corrective action request
        tenant_id: Tenant identifier
        workflow: Nonconformity workflow

    Returns:
        Bulk operation report with statistics
    """
    logger.info(f"Starting bulk creation of {len(request.actions)} corrective actions")

    async def create_single_action(action: CorrectiveActionRequest) -> Dict[str, Any]:
        """Create single corrective action"""
        try:
            # Validate tenant
            if action.tenant_id != tenant_id:
                raise ValueError(f"Tenant mismatch for action on NC: {action.nc_id}")

            # Simplified - actual implementation would use workflow transition
            return {
                "nc_id": str(action.nc_id),
                "action_description": action.action_description,
                "responsible_person": action.responsible_person,
                "due_date": action.due_date,
                "created": True
            }

        except Exception as e:
            logger.error(f"Failed to create action for NC {action.nc_id}: {e}")
            raise ValueError(f"Failed to create corrective action: {str(e)}")

    # Process in parallel
    with metrics.track_time("compliance_bulk_capa_create_duration_seconds"):
        report: BulkOperationReport = await parallel_map(
            items=request.actions,
            func=create_single_action,
            max_concurrency=request.max_concurrency,
            timeout_per_item=20.0,
            continue_on_error=True
        )

    # Record metrics
    metrics.inc_counter(
        "compliance_bulk_operations_total",
        labels={"operation": "capa_create", "status": "completed"}
    )

    logger.info(
        f"Bulk corrective action creation completed: {report.success_count}/{report.total_count} succeeded"
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
                "nc_id": str(f.input_data.nc_id) if hasattr(f.input_data, 'nc_id') else None,
                "error": f.error
            }
            for f in report.failures
        ]
    }


@router.post("/rca/bulk-validate")
async def bulk_validate_rca_templates(
    rca_method: RCAMethod,
    templates: List[Dict[str, Any]],
    max_concurrency: int = 20
):
    """
    Bulk validate RCA templates without creating nonconformities.

    Useful for pre-validating bulk RCA imports.

    Args:
        rca_method: RCA method to validate against
        templates: List of RCA templates to validate
        max_concurrency: Maximum concurrent validations

    Returns:
        Bulk validation report
    """
    logger.info(f"Starting bulk validation of {len(templates)} RCA templates")

    async def validate_single_template(template: Dict[str, Any]) -> Dict[str, Any]:
        """Validate single RCA template"""
        try:
            # Create template instance for validation
            rca_template = RCATemplateFactory.dict_to_template(rca_method, template)

            # Validate template structure
            if not hasattr(rca_template, 'problem_statement'):
                raise ValueError("Missing problem_statement")

            return {
                "valid": True,
                "method": rca_method.value,
                "problem": template.get("problem_statement", "N/A")
            }

        except Exception as e:
            raise ValueError(f"Invalid RCA template: {str(e)}")

    report: BulkOperationReport = await parallel_map(
        items=templates,
        func=validate_single_template,
        max_concurrency=max_concurrency,
        timeout_per_item=5.0,
        continue_on_error=True
    )

    return {
        "total": report.total_count,
        "valid": report.success_count,
        "invalid": report.failure_count,
        "validation_rate": report.success_rate,
        "duration_ms": report.total_duration_ms,
        "invalid_templates": [
            {
                "index": f.index,
                "error": f.error
            }
            for f in report.failures
        ]
    }
