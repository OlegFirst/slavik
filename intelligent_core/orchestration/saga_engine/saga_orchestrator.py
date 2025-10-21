"""
Saga Orchestrator
=================

Main orchestrator for executing saga-based distributed transactions.
Handles step execution, failure recovery, compensation, and state management.
"""

from typing import Dict, Any, Optional, List, Callable, Awaitable
from datetime import datetime
import logging
import asyncio
import uuid

from .saga_definition import (
    SagaDefinition, SagaStepDefinition, SagaExecution, SagaStepExecution,
    SagaStatus, SagaStepStatus, SagaExecutionPolicy
)
from .saga_state_store import SagaStateStore
from .compensation_manager import CompensationManager

logger = logging.getLogger(__name__)


class SagaOrchestrator:
    """
    Orchestrates execution of saga-based distributed transactions.

    Features:
    - Sequential and parallel execution
    - Automatic retry with exponential backoff
    - Compensation on failure
    - State persistence for recovery
    - Event publishing for monitoring
    """

    def __init__(
        self,
        state_store: SagaStateStore,
        service_invoker: Optional[Callable[[str, Dict[str, Any]], Awaitable[Any]]] = None,
        event_publisher: Optional[Callable[[str, Dict[str, Any]], Awaitable[None]]] = None
    ):
        """
        Initialize saga orchestrator.

        Args:
            state_store: Persistent state storage
            service_invoker: Async function to invoke service methods
                           Signature: async def invoke(action: str, params: dict) -> Any
            event_publisher: Async function to publish events
                           Signature: async def publish(event_type: str, data: dict) -> None
        """
        self.state_store = state_store
        self.service_invoker = service_invoker
        self.event_publisher = event_publisher
        self.compensation_manager = CompensationManager(state_store, service_invoker)
        self.saga_definitions: Dict[str, SagaDefinition] = {}
        self.logger = logger

    def register_saga(self, definition: SagaDefinition) -> None:
        """
        Register a saga definition.

        Args:
            definition: Saga definition to register
        """
        # Validate definition
        errors = definition.validate()
        if errors:
            raise ValueError(f"Invalid saga definition: {', '.join(errors)}")

        self.saga_definitions[definition.name] = definition
        self.logger.info(f" Registered saga: {definition.name} (v{definition.version})")

    async def execute_saga(
        self,
        saga_name: str,
        initial_context: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> SagaExecution:
        """
        Execute a saga by name.

        Args:
            saga_name: Name of the registered saga to execute
            initial_context: Initial execution context (input data)
            tenant_id: Tenant ID for multi-tenancy
            correlation_id: Correlation ID for tracing

        Returns:
            SagaExecution with final status and results
        """
        # Get saga definition
        definition = self.saga_definitions.get(saga_name)
        if not definition:
            raise ValueError(f"Saga not found: {saga_name}")

        # Create saga execution
        saga = SagaExecution(
            saga_id=str(uuid.uuid4()),
            definition_name=definition.name,
            definition_version=definition.version,
            execution_context=initial_context or {},
            tenant_id=tenant_id,
            correlation_id=correlation_id or str(uuid.uuid4())
        )

        self.logger.info(
            f" Starting saga execution: {saga_name} "
            f"(saga_id={saga.saga_id}, tenant={tenant_id})"
        )

        # Save initial state
        saga.status = SagaStatus.EXECUTING
        saga.started_at = datetime.utcnow()
        await self.state_store.save_saga(saga)

        # Publish start event
        await self._publish_event("saga.started", {
            "saga_id": saga.saga_id,
            "saga_name": saga_name,
            "tenant_id": tenant_id
        })

        # Execute on_start hook if defined
        if definition.on_start:
            await self._execute_hook(definition.on_start, saga)

        try:
            # Execute based on policy
            if definition.execution_policy == SagaExecutionPolicy.SEQUENTIAL:
                success = await self._execute_sequential(saga, definition)
            elif definition.execution_policy == SagaExecutionPolicy.PARALLEL:
                success = await self._execute_parallel(saga, definition)
            elif definition.execution_policy == SagaExecutionPolicy.PIPELINE:
                success = await self._execute_pipeline(saga, definition)
            else:
                raise ValueError(f"Unknown execution policy: {definition.execution_policy}")

            if success:
                # Saga completed successfully
                saga.status = SagaStatus.COMPLETED
                saga.completed_at = datetime.utcnow()
                await self.state_store.save_saga(saga)

                self.logger.info(f" Saga {saga.saga_id} completed successfully")

                # Execute on_complete hook
                if definition.on_complete:
                    await self._execute_hook(definition.on_complete, saga)

                # Publish completion event
                await self._publish_event("saga.completed", {
                    "saga_id": saga.saga_id,
                    "saga_name": saga_name,
                    "result": saga.result
                })

            else:
                # Saga failed - initiate compensation
                saga.status = SagaStatus.FAILED
                await self.state_store.save_saga(saga)

                self.logger.error(f" Saga {saga.saga_id} failed")

                # Publish failure event
                await self._publish_event("saga.failed", {
                    "saga_id": saga.saga_id,
                    "saga_name": saga_name,
                    "error": saga.error
                })

                # Execute on_failure hook
                if definition.on_failure:
                    await self._execute_hook(definition.on_failure, saga)

                # Compensate
                compensation_success = await self.compensation_manager.compensate_saga(
                    saga, definition
                )

                if compensation_success:
                    # Execute on_compensated hook
                    if definition.on_compensated:
                        await self._execute_hook(definition.on_compensated, saga)

                    # Publish compensated event
                    await self._publish_event("saga.compensated", {
                        "saga_id": saga.saga_id,
                        "saga_name": saga_name
                    })
                else:
                    # Publish compensation failed event
                    await self._publish_event("saga.compensation_failed", {
                        "saga_id": saga.saga_id,
                        "saga_name": saga_name
                    })

        except Exception as e:
            self.logger.error(f" Saga {saga.saga_id} error: {e}", exc_info=True)
            saga.status = SagaStatus.FAILED
            saga.error = str(e)
            saga.completed_at = datetime.utcnow()
            await self.state_store.save_saga(saga)

            # Publish error event
            await self._publish_event("saga.error", {
                "saga_id": saga.saga_id,
                "saga_name": saga_name,
                "error": str(e)
            })

            # Attempt compensation
            try:
                await self.compensation_manager.compensate_saga(saga, definition)
            except Exception as comp_error:
                self.logger.error(f"Compensation error: {comp_error}", exc_info=True)

        return saga

    async def _execute_sequential(
        self,
        saga: SagaExecution,
        definition: SagaDefinition
    ) -> bool:
        """Execute saga steps sequentially"""
        self.logger.info(f"Executing saga {saga.saga_id} sequentially")

        for step_def in definition.steps:
            success = await self._execute_step(saga, step_def)

            if not success:
                failed_step = saga.step_executions.get(step_def.name)
                saga.error = f"Step {step_def.name} failed: {failed_step.error if failed_step else 'unknown error'}"
                return False

        return True

    async def _execute_parallel(
        self,
        saga: SagaExecution,
        definition: SagaDefinition
    ) -> bool:
        """Execute saga steps in parallel where possible (respecting dependencies)"""
        self.logger.info(f"Executing saga {saga.saga_id} in parallel")

        # Get execution levels (steps that can execute in parallel)
        levels = definition.get_dependency_order()

        for level_idx, level_steps in enumerate(levels):
            self.logger.info(
                f"Executing level {level_idx + 1}/{len(levels)}: "
                f"{len(level_steps)} steps"
            )

            # Execute all steps in this level concurrently
            tasks = []
            for step_name in level_steps:
                step_def = definition.get_step(step_name)
                if step_def:
                    tasks.append(self._execute_step(saga, step_def))

            # Wait for all steps in this level to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check for failures
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Step {level_steps[i]} raised exception: {result}")
                    saga.error = f"Step {level_steps[i]} failed with exception"
                    return False
                elif not result:
                    saga.error = f"Step {level_steps[i]} failed"
                    return False

        return True

    async def _execute_pipeline(
        self,
        saga: SagaExecution,
        definition: SagaDefinition
    ) -> bool:
        """
        Execute saga steps in pipeline mode.
        Output from each step flows to the next step's input.
        """
        self.logger.info(f"Executing saga {saga.saga_id} in pipeline mode")

        for step_def in definition.steps:
            success = await self._execute_step(saga, step_def)

            if not success:
                failed_step = saga.step_executions.get(step_def.name)
                saga.error = f"Pipeline failed at step {step_def.name}: {failed_step.error if failed_step else 'unknown error'}"
                return False

            # Pipeline: output becomes input for next step
            step_exec = saga.step_executions.get(step_def.name)
            if step_exec and step_exec.output_context:
                saga.execution_context.update(step_exec.output_context)

        return True

    async def _execute_step(
        self,
        saga: SagaExecution,
        step_def: SagaStepDefinition
    ) -> bool:
        """
        Execute a single saga step with retry logic.

        Returns:
            True if step completed successfully, False otherwise
        """
        # Check if step already exists (recovery scenario)
        step_exec = saga.step_executions.get(step_def.name)

        if not step_exec:
            # Create new step execution
            step_exec = SagaStepExecution(
                step_id=step_def.step_id,
                step_name=step_def.name,
                saga_id=saga.saga_id,
                max_attempts=step_def.max_retries + 1,
                idempotency_key=step_def.get_idempotency_key(saga.execution_context)
            )
            saga.step_executions[step_def.name] = step_exec

        # Check if already completed (idempotency)
        if step_exec.status == SagaStepStatus.COMPLETED:
            self.logger.info(f"Step {step_def.name} already completed - skipping")
            return True

        self.logger.info(f"️ Executing step: {step_def.name}")

        # Retry loop
        while step_exec.can_retry():
            step_exec.status = SagaStepStatus.EXECUTING
            step_exec.started_at = datetime.utcnow()
            step_exec.attempts += 1
            await self.state_store.save_step(saga.saga_id, step_exec)

            # Publish step started event
            await self._publish_event("saga.step.started", {
                "saga_id": saga.saga_id,
                "step_name": step_def.name,
                "attempt": step_exec.attempts
            })

            try:
                # Execute step
                result = await self._invoke_service(
                    step_def.forward_action,
                    self._build_step_params(step_def, saga),
                    timeout=step_def.timeout_seconds
                )

                # Step succeeded
                step_exec.status = SagaStepStatus.COMPLETED
                step_exec.completed_at = datetime.utcnow()
                step_exec.result = result

                # Update output context
                if isinstance(result, dict):
                    step_exec.output_context = result

                await self.state_store.save_step(saga.saga_id, step_exec)

                self.logger.info(f" Step {step_def.name} completed successfully")

                # Publish step completed event
                await self._publish_event("saga.step.completed", {
                    "saga_id": saga.saga_id,
                    "step_name": step_def.name,
                    "result": result
                })

                return True

            except asyncio.TimeoutError:
                error_msg = f"Step timeout after {step_def.timeout_seconds}s"
                self.logger.warning(f"⏱️ {error_msg}")
                step_exec.error = error_msg
                step_exec.error_details = {"timeout": step_def.timeout_seconds}

            except Exception as e:
                error_msg = str(e)
                self.logger.error(f" Step {step_def.name} failed: {error_msg}")
                step_exec.error = error_msg
                step_exec.error_details = {
                    "exception_type": type(e).__name__,
                    "exception_message": str(e)
                }

            # Retry delay
            if step_exec.can_retry():
                self.logger.info(
                    f"Retrying step {step_def.name} in {step_def.retry_delay_seconds}s "
                    f"(attempt {step_exec.attempts + 1}/{step_exec.max_attempts})"
                )
                await asyncio.sleep(step_def.retry_delay_seconds)

        # All retries exhausted
        step_exec.status = SagaStepStatus.FAILED
        await self.state_store.save_step(saga.saga_id, step_exec)

        self.logger.error(
            f" Step {step_def.name} failed after {step_exec.attempts} attempts"
        )

        # Publish step failed event
        await self._publish_event("saga.step.failed", {
            "saga_id": saga.saga_id,
            "step_name": step_def.name,
            "error": step_exec.error,
            "attempts": step_exec.attempts
        })

        return False

    def _build_step_params(
        self,
        step_def: SagaStepDefinition,
        saga: SagaExecution
    ) -> Dict[str, Any]:
        """
        Build parameters for step execution.

        Merges:
        - Step definition params
        - Saga execution context
        """
        params = dict(step_def.forward_params)

        # Add saga context
        params.update(saga.execution_context)

        # Add metadata
        params['_saga_id'] = saga.saga_id
        params['_step_name'] = step_def.name
        params['_tenant_id'] = saga.tenant_id

        return params

    async def _invoke_service(
        self,
        action: str,
        params: Dict[str, Any],
        timeout: int = 30
    ) -> Any:
        """
        Invoke a service method.

        Args:
            action: Service method name (e.g., "bia_service.create_assessment")
            params: Method parameters
            timeout: Execution timeout in seconds

        Returns:
            Result from service invocation
        """
        if not self.service_invoker:
            # Mock mode for testing
            self.logger.warning(
                f"No service invoker configured - mock execution: {action}"
            )
            return {"status": "mock_success", "action": action}

        # Invoke with timeout
        return await asyncio.wait_for(
            self.service_invoker(action, params),
            timeout=timeout
        )

    async def _execute_hook(
        self,
        hook_action: str,
        saga: SagaExecution
    ) -> None:
        """Execute a lifecycle hook"""
        try:
            self.logger.info(f"Executing hook: {hook_action}")
            await self._invoke_service(hook_action, {
                "saga_id": saga.saga_id,
                "status": saga.status.value,
                "context": saga.execution_context
            })
        except Exception as e:
            self.logger.error(f"Hook {hook_action} failed: {e}", exc_info=True)
            # Hooks are non-critical, so we don't fail the saga

    async def _publish_event(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> None:
        """Publish an event"""
        if not self.event_publisher:
            return

        try:
            await self.event_publisher(event_type, data)
        except Exception as e:
            self.logger.error(f"Failed to publish event {event_type}: {e}", exc_info=True)
            # Event publishing is non-critical

    async def recover_saga(self, saga_id: str) -> Optional[SagaExecution]:
        """
        Recover a saga execution from persistent state.

        Used after system restart or failure to resume saga execution.

        Args:
            saga_id: ID of saga to recover

        Returns:
            Recovered saga execution or None if not found
        """
        self.logger.info(f" Recovering saga: {saga_id}")

        # Load saga state
        saga = await self.state_store.get_saga(saga_id)
        if not saga:
            self.logger.error(f"Saga {saga_id} not found for recovery")
            return None

        # Check if saga is in a recoverable state
        if saga.status not in [SagaStatus.EXECUTING, SagaStatus.COMPENSATING]:
            self.logger.info(
                f"Saga {saga_id} is in {saga.status.value} state - no recovery needed"
            )
            return saga

        # Get saga definition
        definition = self.saga_definitions.get(saga.definition_name)
        if not definition:
            self.logger.error(
                f"Saga definition {saga.definition_name} not found for recovery"
            )
            return None

        self.logger.info(f"Resuming saga {saga_id} from {saga.status.value} state")

        # Resume execution based on current status
        if saga.status == SagaStatus.EXECUTING:
            # Find last completed step and continue from there
            completed_steps = {s.step_name for s in saga.get_completed_steps()}

            # Execute remaining steps
            for step_def in definition.steps:
                if step_def.name not in completed_steps:
                    success = await self._execute_step(saga, step_def)
                    if not success:
                        saga.status = SagaStatus.FAILED
                        await self.compensation_manager.compensate_saga(saga, definition)
                        return saga

            # All steps completed
            saga.status = SagaStatus.COMPLETED
            saga.completed_at = datetime.utcnow()
            await self.state_store.save_saga(saga)

        elif saga.status == SagaStatus.COMPENSATING:
            # Resume compensation
            await self.compensation_manager.compensate_saga(saga, definition)

        return saga

    async def get_saga_status(self, saga_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of a saga execution.

        Returns detailed status including all steps.
        """
        saga = await self.state_store.get_saga(saga_id)
        if not saga:
            return None

        steps_status = []
        for step_name, step_exec in saga.step_executions.items():
            steps_status.append({
                "name": step_name,
                "status": step_exec.status.value,
                "attempts": step_exec.attempts,
                "started_at": step_exec.started_at.isoformat() if step_exec.started_at else None,
                "completed_at": step_exec.completed_at.isoformat() if step_exec.completed_at else None,
                "error": step_exec.error
            })

        return {
            "saga_id": saga.saga_id,
            "definition_name": saga.definition_name,
            "status": saga.status.value,
            "started_at": saga.started_at.isoformat() if saga.started_at else None,
            "completed_at": saga.completed_at.isoformat() if saga.completed_at else None,
            "error": saga.error,
            "steps": steps_status,
            "tenant_id": saga.tenant_id,
            "correlation_id": saga.correlation_id
        }
