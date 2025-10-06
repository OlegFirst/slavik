"""
BIA Service - Business Logic

Core business logic for BIA processes.
Extracted from original endpoints without loss of functionality.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import Request

from ..models.domain import BIAProcess, BIAProcessCreate
from ..models.enums import CriticalityLevel, ProcessStatus
from ..repositories.bia_repository import BIARepository
from ..utils.calculations import calculate_criticality_score, determine_who_tier
from shared.eventbus import publish_event
from shared.exceptions import EntityNotFoundError, TenantMismatchError
from shared.audit import AuditLogger, AuditAction, AuditCategory
from shared.utils.parallel import parallel_map, BulkOperationReport
from shared.utils.metrics import MetricsCollector
from shared.cache import get_cache, cached

logger = logging.getLogger(__name__)
metrics = MetricsCollector()


class BIAService:
    """BIA Service - Core business logic"""

    def __init__(self, repository: BIARepository, audit_logger: Optional[AuditLogger] = None):
        self.repo = repository
        self.audit = audit_logger

    async def create_process(
        self,
        data: BIAProcessCreate,
        user_id: str = "system",
        request: Optional[Request] = None
    ) -> BIAProcess:
        """
        Create new BIA process with full validation and event publishing.

        All original logic from POST /api/bia/processes preserved.
        """
        # Calculate criticality score
        criticality_score = calculate_criticality_score(data.criticality)

        # Auto-calculate WHO tier for healthcare processes
        who_tier = None
        if data.patient_safety_impact or data.who_tier:
            who_tier = determine_who_tier(
                criticality=data.criticality,
                rto_hours=data.rto_hours,
                patient_safety_impact=data.patient_safety_impact
            )

        # Create process
        process = BIAProcess(
            tenant_id=data.tenant_id,
            name=data.name,
            description=data.description,
            department=data.department,
            process_owner=data.process_owner,
            criticality=data.criticality,
            criticality_score=criticality_score,
            who_tier=who_tier,  # Auto-calculated for healthcare
            industry=data.industry,
            geographical_scope=data.geographical_scope,
            rto_hours=data.rto_hours,
            rpo_hours=data.rpo_hours,
            mtpd_hours=data.mtpd_hours,
            financial_impact=data.financial_impact,
            operational_impact=data.operational_impact,
            reputational_impact=data.reputational_impact,
            regulatory_impact=data.regulatory_impact,
            patient_safety_impact=data.patient_safety_impact,
            dependencies=data.dependencies or [],
            resources_required=data.resources_required or []
        )

        # Save to repository
        created_process = await self.repo.create(process)

        # Audit log creation
        if self.audit:
            try:
                await self.audit.log_create(
                    user_id=user_id,
                    tenant_id=data.tenant_id,
                    category=AuditCategory.BIA,
                    entity_type="BIAProcess",
                    entity_id=str(created_process.id),
                    entity_data={
                        "name": created_process.name,
                        "department": created_process.department,
                        "criticality": created_process.criticality.value,
                        "rto_hours": created_process.rto_hours,
                        "rpo_hours": created_process.rpo_hours
                    },
                    request=request
                )
            except Exception as e:
                # Log audit failure but don't block operation
                logger.warning(f"Audit logging failed for BIA process creation: {e}")

        # Publish event (original functionality)
        await publish_event("bcm.bia.started", {
            "tenant_id": data.tenant_id,
            "bia_process_id": created_process.id,
            "process_name": data.name
        }, source="bia")

        return created_process

    async def list_processes(
        self,
        tenant_id: str,
        criticality: Optional[CriticalityLevel] = None,
        status: Optional[ProcessStatus] = None
    ) -> List[BIAProcess]:
        """
        List BIA processes with filters.

        Original logic from GET /api/bia/processes preserved.
        """
        processes = await self.repo.list(tenant_id)

        # Apply filters (original logic)
        if criticality:
            processes = [p for p in processes if p.criticality == criticality]

        if status:
            processes = [p for p in processes if p.status == status]

        return processes

    @cached(ttl=300, key_prefix="bia:process")
    async def get_process(
        self,
        process_id: int,
        tenant_id: str
    ) -> BIAProcess:
        """
        Get BIA process with tenant validation.

        Cached for 300 seconds (5 minutes) per tenant.

        Original logic from GET /api/bia/processes/{id} preserved.
        """
        process = await self.repo.get(process_id)

        if not process:
            raise EntityNotFoundError("BIAProcess", str(process_id))

        if process.tenant_id != tenant_id:
            raise TenantMismatchError(tenant_id, process.tenant_id)

        return process

    async def update_process(
        self,
        process_id: int,
        tenant_id: str,
        updates: Dict[str, Any],
        user_id: str = "system",
        request: Optional[Request] = None
    ) -> BIAProcess:
        """
        Update BIA process.

        Original logic from PUT /api/bia/processes/{id} preserved.
        """
        process = await self.get_process(process_id, tenant_id)  # Reuse validation

        # Capture before state for audit
        before_state = {
            "criticality": process.criticality.value,
            "rto_hours": process.rto_hours,
            "rpo_hours": process.rpo_hours,
            "status": process.status.value
        }

        # Auto-recalculate WHO tier if relevant fields changed
        if any(key in updates for key in ["criticality", "rto_hours", "patient_safety_impact"]):
            criticality = updates.get("criticality", process.criticality)
            rto_hours = updates.get("rto_hours", process.rto_hours)
            patient_safety_impact = updates.get("patient_safety_impact", process.patient_safety_impact)

            if patient_safety_impact or process.who_tier:
                updates["who_tier"] = determine_who_tier(
                    criticality=criticality,
                    rto_hours=rto_hours,
                    patient_safety_impact=patient_safety_impact
                )

        # Recalculate criticality score if criticality changed
        if "criticality" in updates:
            updates["criticality_score"] = calculate_criticality_score(updates["criticality"])

        # Add updated_at (original logic)
        updates["updated_at"] = datetime.now()

        updated_process = await self.repo.update(process_id, updates)

        # Invalidate cache for this process
        try:
            cache = get_cache()
            cache_key = f"bia:process:get_process:{process_id}:{tenant_id}"
            await cache.delete(cache_key, tenant_id=tenant_id)
        except Exception as e:
            logger.warning(f"Failed to invalidate cache for process {process_id}: {e}")

        # Audit log update
        if self.audit:
            try:
                after_state = {
                    "criticality": updated_process.criticality.value,
                    "rto_hours": updated_process.rto_hours,
                    "rpo_hours": updated_process.rpo_hours,
                    "status": updated_process.status.value
                }
                await self.audit.log_update(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    category=AuditCategory.BIA,
                    entity_type="BIAProcess",
                    entity_id=str(process_id),
                    before=before_state,
                    after=after_state,
                    request=request
                )
            except Exception as e:
                logger.warning(f"Audit logging failed for BIA process update: {e}")

        return updated_process

    async def delete_process(
        self,
        process_id: int,
        tenant_id: str,
        user_id: str = "system",
        request: Optional[Request] = None
    ) -> Dict[str, Any]:
        """
        Delete BIA process.

        Original logic from DELETE /api/bia/processes/{id} preserved.
        """
        await self.get_process(process_id, tenant_id)  # Validate access

        # Audit log deletion BEFORE deleting
        if self.audit:
            try:
                await self.audit.log_delete(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    category=AuditCategory.BIA,
                    entity_type="BIAProcess",
                    entity_id=str(process_id),
                    request=request
                )
            except Exception as e:
                logger.warning(f"Audit logging failed for BIA process deletion: {e}")

        await self.repo.delete(process_id)

        # Invalidate cache for this process
        try:
            cache = get_cache()
            cache_key = f"bia:process:get_process:{process_id}:{tenant_id}"
            await cache.delete(cache_key, tenant_id=tenant_id)
        except Exception as e:
            logger.warning(f"Failed to invalidate cache for process {process_id}: {e}")

        return {"status": "deleted", "process_id": process_id}

    async def complete_process(
        self,
        process_id: int,
        tenant_id: str,
        user_id: str = "system",
        request: Optional[Request] = None
    ) -> Dict[str, Any]:
        """
        Mark BIA process as completed with full event publishing.

        Original logic from POST /api/bia/processes/{id}/complete preserved.
        """
        process = await self.get_process(process_id, tenant_id)

        # Store previous status for audit
        previous_status = process.status

        # Update status (original logic)
        process.status = ProcessStatus.COMPLETED
        process.completed_at = datetime.now()
        await self.repo.update(process_id, {
            "status": process.status,
            "completed_at": process.completed_at
        })

        # Audit log state transition
        if self.audit:
            try:
                await self.audit.log_state_transition(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    category=AuditCategory.BIA,
                    entity_type="BIAProcess",
                    entity_id=str(process_id),
                    from_state=previous_status.value,
                    to_state=ProcessStatus.COMPLETED.value,
                    request=request,
                    metadata={
                        "criticality_score": process.criticality_score,
                        "rto_hours": process.rto_hours,
                        "rpo_hours": process.rpo_hours
                    }
                )
            except Exception as e:
                logger.warning(f"Audit logging failed for BIA process completion: {e}")

        # Publish completion event (original logic)
        await publish_event("bcm.bia.completed", {
            "tenant_id": tenant_id,
            "bia_process_id": process_id,
            "rto_hours": process.rto_hours,
            "rpo_hours": process.rpo_hours,
            "criticality": process.criticality_score,
            "critical_process": process.criticality_score >= 4
        }, source="bia")

        # If critical, publish additional event (original logic)
        if process.criticality_score >= 4:
            await publish_event("bcm.bia.critical_process_identified", {
                "tenant_id": tenant_id,
                "process_id": process_id,
                "criticality": process.criticality_score,
                "rto_hours": process.rto_hours,
                "mtpd_hours": process.mtpd_hours
            }, source="bia")

        return {"status": "completed", "process": process}

    # ==================== BULK OPERATIONS ====================

    async def bulk_create_processes(
        self,
        processes: List[BIAProcessCreate],
        user_id: str = "system",
        max_concurrency: int = 10,
        request: Optional[Request] = None
    ) -> BulkOperationReport:
        """
        Create multiple BIA processes in parallel.

        Args:
            processes: List of BIA processes to create
            user_id: User performing the operation
            max_concurrency: Maximum number of concurrent creations (default: 10)
            request: FastAPI request for audit logging

        Returns:
            BulkOperationReport with success/failure statistics
        """
        logger.info(f"Starting bulk create of {len(processes)} BIA processes")

        # Track metrics
        with metrics.track_time("bia_bulk_create_duration_seconds"):
            report = await parallel_map(
                items=processes,
                func=lambda p: self.create_process(p, user_id, request),
                max_concurrency=max_concurrency,
                timeout_per_item=30.0,  # 30 seconds per process
                continue_on_error=True
            )

        # Record metrics
        metrics.inc_counter(
            "bia_bulk_operations_total",
            labels={"operation": "create", "status": "completed"}
        )
        metrics.set_gauge(
            "bia_bulk_operation_success_rate",
            report.success_rate,
            labels={"operation": "create"}
        )

        logger.info(
            f"Bulk create completed: {report.success_count}/{report.total_count} succeeded, "
            f"{report.failure_count} failed in {report.total_duration_ms:.0f}ms"
        )

        return report

    async def bulk_update_processes(
        self,
        updates: List[Dict[str, Any]],
        tenant_id: str,
        user_id: str = "system",
        max_concurrency: int = 10,
        request: Optional[Request] = None
    ) -> BulkOperationReport:
        """
        Update multiple BIA processes in parallel.

        Args:
            updates: List of update dicts with 'process_id' and update fields
            tenant_id: Tenant ID for validation
            user_id: User performing the operation
            max_concurrency: Maximum number of concurrent updates (default: 10)
            request: FastAPI request for audit logging

        Returns:
            BulkOperationReport with success/failure statistics

        Example:
            updates = [
                {"process_id": 1, "rto_hours": 4, "status": "completed"},
                {"process_id": 2, "criticality": "high"}
            ]
        """
        logger.info(f"Starting bulk update of {len(updates)} BIA processes")

        async def update_single(update_dict: Dict[str, Any]) -> BIAProcess:
            """Update single process from dict"""
            process_id = update_dict.pop("process_id")
            return await self.update_process(
                process_id=process_id,
                tenant_id=tenant_id,
                updates=update_dict,
                user_id=user_id,
                request=request
            )

        with metrics.track_time("bia_bulk_update_duration_seconds"):
            report = await parallel_map(
                items=updates,
                func=update_single,
                max_concurrency=max_concurrency,
                timeout_per_item=20.0,  # 20 seconds per update
                continue_on_error=True
            )

        metrics.inc_counter(
            "bia_bulk_operations_total",
            labels={"operation": "update", "status": "completed"}
        )

        logger.info(
            f"Bulk update completed: {report.success_count}/{report.total_count} succeeded, "
            f"{report.failure_count} failed"
        )

        return report

    async def bulk_delete_processes(
        self,
        process_ids: List[int],
        tenant_id: str,
        user_id: str = "system",
        max_concurrency: int = 10,
        request: Optional[Request] = None
    ) -> BulkOperationReport:
        """
        Delete multiple BIA processes in parallel.

        Args:
            process_ids: List of process IDs to delete
            tenant_id: Tenant ID for validation
            user_id: User performing the operation
            max_concurrency: Maximum number of concurrent deletions (default: 10)
            request: FastAPI request for audit logging

        Returns:
            BulkOperationReport with success/failure statistics
        """
        logger.info(f"Starting bulk delete of {len(process_ids)} BIA processes")

        with metrics.track_time("bia_bulk_delete_duration_seconds"):
            report = await parallel_map(
                items=process_ids,
                func=lambda pid: self.delete_process(pid, tenant_id, user_id, request),
                max_concurrency=max_concurrency,
                timeout_per_item=15.0,  # 15 seconds per deletion
                continue_on_error=True
            )

        metrics.inc_counter(
            "bia_bulk_operations_total",
            labels={"operation": "delete", "status": "completed"}
        )

        logger.info(
            f"Bulk delete completed: {report.success_count}/{report.total_count} succeeded, "
            f"{report.failure_count} failed"
        )

        return report

    async def bulk_validate_processes(
        self,
        processes: List[BIAProcessCreate],
        max_concurrency: int = 20
    ) -> BulkOperationReport:
        """
        Validate multiple BIA processes in parallel without creating them.

        Useful for pre-validating bulk imports before actual creation.

        Args:
            processes: List of BIA processes to validate
            max_concurrency: Maximum number of concurrent validations (default: 20)

        Returns:
            BulkOperationReport with validation results
        """
        logger.info(f"Starting bulk validation of {len(processes)} BIA processes")

        async def validate_single(process: BIAProcessCreate) -> Dict[str, Any]:
            """Validate single process"""
            try:
                # Perform validation without saving
                criticality_score = calculate_criticality_score(process.criticality)

                who_tier = None
                if process.patient_safety_impact or process.who_tier:
                    who_tier = determine_who_tier(
                        criticality=process.criticality,
                        rto_hours=process.rto_hours,
                        patient_safety_impact=process.patient_safety_impact
                    )

                # Validate business rules
                if process.rto_hours > process.mtpd_hours:
                    raise ValueError("RTO cannot exceed MTPD")

                if process.rpo_hours > process.rto_hours:
                    raise ValueError("RPO cannot exceed RTO")

                return {
                    "valid": True,
                    "name": process.name,
                    "criticality_score": criticality_score,
                    "who_tier": who_tier.value if who_tier else None
                }
            except Exception as e:
                raise ValueError(f"Validation failed for {process.name}: {str(e)}")

        report = await parallel_map(
            items=processes,
            func=validate_single,
            max_concurrency=max_concurrency,
            timeout_per_item=5.0,  # Quick validation
            continue_on_error=True
        )

        logger.info(
            f"Bulk validation completed: {report.success_count}/{report.total_count} valid, "
            f"{report.failure_count} invalid"
        )

        return report
