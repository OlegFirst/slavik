"""
Change History API
Provides endpoints for retrieving field-level change history
"""

from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from shared.history import ChangeTracker, EntityHistory, FieldChange
from ..database.connection import get_db

router = APIRouter(prefix="/api/bia/history", tags=["History"])


@router.get("/processes/{process_id}", response_model=EntityHistory)
async def get_process_history(
    process_id: int,
    tenant_id: str = Query(..., description="Tenant ID"),
    limit: int = Query(100, le=1000, description="Maximum number of changes to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete change history for BIA process.

    Returns all field-level changes with who/when/what information.
    Useful for audit trails and compliance reporting.

    Args:
        process_id: BIA process ID
        tenant_id: Tenant identifier
        limit: Maximum number of changes (default: 100, max: 1000)

    Returns:
        EntityHistory: Complete change history with metadata
    """
    try:
        tracker = ChangeTracker(db)
        return await tracker.get_entity_history(
            entity_type="BIAProcess",
            entity_id=str(process_id),
            tenant_id=tenant_id,
            limit=limit
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/processes/{process_id}/fields/{field_name}", response_model=List[FieldChange])
async def get_field_history(
    process_id: int,
    field_name: str,
    tenant_id: str = Query(..., description="Tenant ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get change history for specific field.

    Track how a single field value changed over time.
    Useful for investigating specific data changes or compliance audits.

    Args:
        process_id: BIA process ID
        field_name: Name of field to track (e.g., "rto_hours", "criticality")
        tenant_id: Tenant identifier

    Returns:
        List[FieldChange]: All changes for the specified field
    """
    tracker = ChangeTracker(db)
    return await tracker.get_field_history(
        entity_type="BIAProcess",
        entity_id=str(process_id),
        field_name=field_name,
        tenant_id=tenant_id
    )


@router.get("/processes/{process_id}/snapshot/{version}", response_model=dict)
async def get_process_snapshot(
    process_id: int,
    version: int,
    tenant_id: str = Query(..., description="Tenant ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get process state at specific version.

    Retrieve a complete snapshot of the entity at a specific point in time.
    Useful for rollback scenarios or point-in-time auditing.

    Args:
        process_id: BIA process ID
        version: Version number
        tenant_id: Tenant identifier

    Returns:
        dict: Complete entity snapshot at specified version
    """
    from sqlalchemy import select
    from shared.history import ChangeHistoryModel

    stmt = (
        select(ChangeHistoryModel)
        .where(ChangeHistoryModel.entity_type == "BIAProcess")
        .where(ChangeHistoryModel.entity_id == str(process_id))
        .where(ChangeHistoryModel.tenant_id == tenant_id)
        .where(ChangeHistoryModel.version_number == version)
        .where(ChangeHistoryModel.snapshot.isnot(None))
        .order_by(ChangeHistoryModel.changed_at.desc())
        .limit(1)
    )

    result = await db.execute(stmt)
    change = result.scalar_one_or_none()

    if not change or not change.snapshot:
        raise HTTPException(
            status_code=404,
            detail=f"No snapshot found for version {version}"
        )

    return change.snapshot
