"""FastAPI routes for Coordination Center."""
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from datetime import datetime

from models.schemas import (
    Intent,
    ExecutionCreate,
    ExecutionResponse,
    ExecutionListResponse,
    ExecutionStatus,
    ExecutionStep,
    ApprovalRequest,
    RollbackRequest,
    ToolListResponse,
    HealthCheckResponse,
    AuditLogEntry,
)
from core.command_interpreter import command_interpreter
from core.execution_tracker import execution_tracker
from core.tool_registry import tool_registry
from core.security_layer import security_layer


router = APIRouter(prefix="/coordination", tags=["coordination"])


@router.post("/execute", response_model=ExecutionResponse, status_code=status.HTTP_202_ACCEPTED)
async def execute_intent(request: ExecutionCreate):
    """
    Execute AI intent.

    Flow:
    1. Security check (permissions, rate limit)
    2. Parse intent
    3. Create execution record
    4. Execute command
    5. Return execution ID

    AI can poll GET /executions/{id} for status.
    """
    intent = request.intent

    # Create execution record
    execution_id = await execution_tracker.create_execution(intent.model_dump())

    try:
        # 1. Security authorization
        is_authorized, auth_reason, requires_approval = await security_layer.authorize_request(
            execution_id=execution_id,
            action=intent.action,
            entity=intent.entity,
            user_id=intent.context.user_id,
            tenant_id=intent.context.tenant_id,
            details={"params": intent.params}
        )

        if not is_authorized:
            await execution_tracker.update_status(
                execution_id,
                ExecutionStatus.FAILED,
                error={"message": auth_reason}
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=auth_reason)

        # If requires approval, mark as pending and return
        if requires_approval:
            await execution_tracker.update_status(
                execution_id,
                ExecutionStatus.REQUIRES_APPROVAL,
                result={"message": "Waiting for human approval"}
            )

            execution = await execution_tracker.get_execution(execution_id)
            return ExecutionResponse(**execution)

        # 2. Parse intent
        await execution_tracker.add_step(execution_id, "parse_intent", ExecutionStatus.RUNNING)

        success, error, command = command_interpreter.parse_intent(intent)

        if not success:
            await execution_tracker.update_step(
                execution_id, 1, ExecutionStatus.FAILED, error=error
            )
            await execution_tracker.update_status(
                execution_id, ExecutionStatus.FAILED, error={"message": error}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

        await execution_tracker.update_step(
            execution_id, 1, ExecutionStatus.COMPLETED, result={"command": command}
        )

        # 3. Execute command
        await execution_tracker.update_status(execution_id, ExecutionStatus.RUNNING)

        success, result, error = await execution_tracker.execute_command(execution_id, command)

        if not success:
            # Log failure
            security_layer.log_execution(
                execution_id, intent.action, intent.context.user_id,
                intent.context.tenant_id, {"command": command}, "failed"
            )
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)

        # Log success
        security_layer.log_execution(
            execution_id, intent.action, intent.context.user_id,
            intent.context.tenant_id, {"command": command, "result": result}, "completed"
        )

        # Return execution
        execution = await execution_tracker.get_execution(execution_id)
        return ExecutionResponse(**execution)

    except HTTPException:
        raise
    except Exception as e:
        await execution_tracker.update_status(
            execution_id,
            ExecutionStatus.FAILED,
            error={"message": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(execution_id: str):
    """Get execution status."""
    execution = await execution_tracker.get_execution(execution_id)

    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found"
        )

    return ExecutionResponse(**execution)


@router.get("/executions", response_model=ExecutionListResponse)
async def list_executions(
    tenant_id: Optional[str] = None,
    status: Optional[ExecutionStatus] = None,
    limit: int = 100
):
    """List executions with filters."""
    executions = await execution_tracker.list_executions(tenant_id, status, limit)

    return ExecutionListResponse(
        executions=[ExecutionResponse(**e) for e in executions],
        total=len(executions)
    )


@router.post("/executions/{execution_id}/approve", response_model=ExecutionResponse)
async def approve_execution(execution_id: str, request: ApprovalRequest):
    """
    Approve execution (for critical actions).

    Only needed when execution.status == REQUIRES_APPROVAL
    """
    execution = await execution_tracker.get_execution(execution_id)

    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found"
        )

    if execution["status"] != ExecutionStatus.REQUIRES_APPROVAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Execution is not pending approval (status: {execution['status']})"
        )

    # Log approval decision
    security_layer.log_execution(
        execution_id,
        "approve" if request.approved else "reject",
        request.approved_by,
        execution["intent"]["context"]["tenant_id"],
        {"reason": request.reason},
        "approval_decision"
    )

    if not request.approved:
        # Reject execution
        await execution_tracker.update_status(
            execution_id,
            ExecutionStatus.FAILED,
            error={"message": f"Rejected by {request.approved_by}: {request.reason}"}
        )

        execution = await execution_tracker.get_execution(execution_id)
        return ExecutionResponse(**execution)

    # Execute after approval
    intent = Intent(**execution["intent"])

    # Parse intent
    success, error, command = command_interpreter.parse_intent(intent)

    if not success:
        await execution_tracker.update_status(
            execution_id, ExecutionStatus.FAILED, error={"message": error}
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    # Execute
    await execution_tracker.update_status(execution_id, ExecutionStatus.RUNNING)

    success, result, error = await execution_tracker.execute_command(execution_id, command)

    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)

    execution = await execution_tracker.get_execution(execution_id)
    return ExecutionResponse(**execution)


@router.post("/executions/{execution_id}/rollback", response_model=ExecutionResponse)
async def rollback_execution(execution_id: str, request: RollbackRequest):
    """Rollback execution."""
    execution = await execution_tracker.get_execution(execution_id)

    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found"
        )

    if execution["status"] != ExecutionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only rollback completed executions"
        )

    # Log rollback
    security_layer.log_execution(
        execution_id,
        "rollback",
        request.initiated_by,
        execution["intent"]["context"]["tenant_id"],
        {"reason": request.reason},
        "rollback_initiated"
    )

    # Perform rollback
    success = await execution_tracker.rollback_execution(execution_id, request.reason)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rollback failed"
        )

    execution = await execution_tracker.get_execution(execution_id)
    return ExecutionResponse(**execution)


@router.get("/tools", response_model=ToolListResponse)
async def list_tools(category: Optional[str] = None):
    """List all available tools."""
    tools = tool_registry.list_tools(category)

    return ToolListResponse(
        tools=tools,
        total=len(tools)
    )


@router.get("/tools/{tool_id}")
async def get_tool(tool_id: str):
    """Get tool definition."""
    tool = tool_registry.get_tool(tool_id)

    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool {tool_id} not found"
        )

    return tool


@router.get("/audit", response_model=List[AuditLogEntry])
async def get_audit_logs(
    execution_id: Optional[str] = None,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    limit: int = 100
):
    """Get audit logs."""
    logs = security_layer.audit_logger.get_logs(
        execution_id=execution_id,
        user_id=user_id,
        tenant_id=tenant_id,
        limit=limit
    )

    return [AuditLogEntry(**log) for log in logs]


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        services={
            "command_interpreter": True,
            "execution_tracker": True,
            "tool_registry": True,
            "security_layer": True,
        }
    )
