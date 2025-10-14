"""Execution Tracker - отслеживание выполнения команд."""
import uuid
import asyncio
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
from models.schemas import ExecutionStatus, ExecutionStep, ExecutionResponse


class ExecutionTracker:
    """Tracks execution of AI intents and manages state."""

    def __init__(self):
        # In-memory storage (в продакшене будет PostgreSQL)
        self.executions: Dict[str, Dict[str, Any]] = {}

    async def create_execution(self, intent: Dict[str, Any]) -> str:
        """Create new execution record."""
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"

        execution = {
            "execution_id": execution_id,
            "intent": intent,
            "status": ExecutionStatus.PENDING,
            "steps": [],
            "result": None,
            "error": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        self.executions[execution_id] = execution
        return execution_id

    async def add_step(self, execution_id: str, action: str, status: ExecutionStatus):
        """Add execution step."""
        if execution_id not in self.executions:
            raise ValueError(f"Execution {execution_id} not found")

        execution = self.executions[execution_id]
        step_number = len(execution["steps"]) + 1

        step = {
            "step": step_number,
            "action": action,
            "status": status,
            "started_at": datetime.utcnow() if status == ExecutionStatus.RUNNING else None,
            "completed_at": datetime.utcnow() if status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED] else None,
            "result": None,
            "error": None,
        }

        execution["steps"].append(step)
        execution["updated_at"] = datetime.utcnow()

    async def update_step(
        self,
        execution_id: str,
        step_number: int,
        status: ExecutionStatus,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """Update execution step."""
        if execution_id not in self.executions:
            raise ValueError(f"Execution {execution_id} not found")

        execution = self.executions[execution_id]
        if step_number > len(execution["steps"]):
            raise ValueError(f"Step {step_number} not found")

        step = execution["steps"][step_number - 1]
        step["status"] = status
        step["result"] = result
        step["error"] = error

        if status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
            step["completed_at"] = datetime.utcnow()

        execution["updated_at"] = datetime.utcnow()

    async def update_status(
        self,
        execution_id: str,
        status: ExecutionStatus,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None
    ):
        """Update execution status."""
        if execution_id not in self.executions:
            raise ValueError(f"Execution {execution_id} not found")

        execution = self.executions[execution_id]
        execution["status"] = status
        execution["result"] = result
        execution["error"] = error
        execution["updated_at"] = datetime.utcnow()

    async def execute_command(
        self,
        execution_id: str,
        command: Dict[str, Any]
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Execute API command.

        Returns:
            (success, result, error)
        """
        # Step 1: Validate command
        await self.add_step(execution_id, "validate_command", ExecutionStatus.RUNNING)
        # Validation done by command_interpreter
        await self.update_step(execution_id, len(self.executions[execution_id]["steps"]), ExecutionStatus.COMPLETED)

        # Step 2: Execute API call
        await self.add_step(execution_id, "execute_api_call", ExecutionStatus.RUNNING)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=command["method"],
                    url=command["url"],
                    json=command.get("body"),
                    headers=command.get("headers", {}),
                )

                if response.status_code >= 400:
                    error = f"API call failed: {response.status_code} - {response.text}"
                    await self.update_step(
                        execution_id,
                        len(self.executions[execution_id]["steps"]),
                        ExecutionStatus.FAILED,
                        error=error
                    )
                    return False, None, error

                result = response.json() if response.text else {}

                await self.update_step(
                    execution_id,
                    len(self.executions[execution_id]["steps"]),
                    ExecutionStatus.COMPLETED,
                    result=result
                )

                # Step 3: Store result
                await self.add_step(execution_id, "store_result", ExecutionStatus.RUNNING)
                await self.update_status(execution_id, ExecutionStatus.COMPLETED, result=result)
                await self.update_step(
                    execution_id,
                    len(self.executions[execution_id]["steps"]),
                    ExecutionStatus.COMPLETED
                )

                return True, result, None

        except httpx.TimeoutException:
            error = "API call timeout"
            await self.update_step(
                execution_id,
                len(self.executions[execution_id]["steps"]),
                ExecutionStatus.FAILED,
                error=error
            )
            await self.update_status(execution_id, ExecutionStatus.FAILED, error={"message": error})
            return False, None, error

        except Exception as e:
            error = f"API call error: {str(e)}"
            await self.update_step(
                execution_id,
                len(self.executions[execution_id]["steps"]),
                ExecutionStatus.FAILED,
                error=error
            )
            await self.update_status(execution_id, ExecutionStatus.FAILED, error={"message": error})
            return False, None, error

    async def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution by ID."""
        return self.executions.get(execution_id)

    async def list_executions(
        self,
        tenant_id: Optional[str] = None,
        status: Optional[ExecutionStatus] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List executions with filters."""
        executions = list(self.executions.values())

        # Filter by tenant_id
        if tenant_id:
            executions = [
                e for e in executions
                if e["intent"].get("context", {}).get("tenant_id") == tenant_id
            ]

        # Filter by status
        if status:
            executions = [e for e in executions if e["status"] == status]

        # Sort by created_at desc
        executions.sort(key=lambda x: x["created_at"], reverse=True)

        return executions[:limit]

    async def rollback_execution(self, execution_id: str, reason: str) -> bool:
        """
        Rollback execution.

        Note: Actual rollback logic depends on the tool.
        For now, we just mark it as rollback_pending.
        """
        if execution_id not in self.executions:
            return False

        execution = self.executions[execution_id]

        # Mark as rollback pending
        await self.update_status(
            execution_id,
            ExecutionStatus.ROLLBACK_PENDING,
            error={"rollback_reason": reason}
        )

        # TODO: Implement actual rollback logic
        # This would require calling rollback endpoints on tools
        # For example: DELETE /api/bia/processes/{id} if we created it

        # For now, simulate rollback
        await asyncio.sleep(0.5)

        await self.update_status(execution_id, ExecutionStatus.ROLLBACK_COMPLETED)

        return True


# Global tracker instance
execution_tracker = ExecutionTracker()
