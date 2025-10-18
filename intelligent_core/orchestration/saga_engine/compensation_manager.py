"""
Compensation Manager
===================

Handles rollback of distributed transactions through compensating actions.
Implements various compensation strategies and handles partial failures.
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import logging
import asyncio

from .saga_definition import (
    SagaDefinition, SagaStepDefinition, SagaExecution, SagaStepExecution,
    SagaStatus, SagaStepStatus, CompensationStrategy
)
from .saga_state_store import SagaStateStore

logger = logging.getLogger(__name__)


class CompensationManager:
    """
    Manages compensation (rollback) of saga transactions.

    Strategies:
    - Backward Recovery: Rollback all completed steps in reverse order
    - Forward Recovery: Try to complete saga despite errors
    - Partial Compensation: Only rollback critical steps
    """

    def __init__(
        self,
        state_store: SagaStateStore,
        service_invoker: Optional[Callable] = None
    ):
        """
        Initialize compensation manager.

        Args:
            state_store: Saga state storage
            service_invoker: Function to invoke service methods
        """
        self.state_store = state_store
        self.service_invoker = service_invoker
        self.logger = logger

    async def compensate_saga(
        self,
        saga: SagaExecution,
        definition: SagaDefinition
    ) -> bool:
        """
        Compensate (rollback) a failed saga.

        Args:
            saga: Saga execution to compensate
            definition: Saga definition with compensation logic

        Returns:
            True if compensation successful, False otherwise
        """
        self.logger.info(
            f"🔄 Starting compensation for saga {saga.saga_id} "
            f"(strategy: {definition.compensation_strategy.value})"
        )

        # Update saga status
        saga.status = SagaStatus.COMPENSATING
        await self.state_store.save_saga(saga)

        try:
            # Choose compensation strategy
            if definition.compensation_strategy == CompensationStrategy.BACKWARD_RECOVERY:
                success = await self._backward_recovery(saga, definition)
            elif definition.compensation_strategy == CompensationStrategy.FORWARD_RECOVERY:
                success = await self._forward_recovery(saga, definition)
            elif definition.compensation_strategy == CompensationStrategy.PARTIAL_COMPENSATION:
                success = await self._partial_compensation(saga, definition)
            else:
                self.logger.error(f"Unknown compensation strategy: {definition.compensation_strategy}")
                success = False

            # Update final status
            if success:
                saga.status = SagaStatus.COMPENSATED
                self.logger.info(f"✅ Saga {saga.saga_id} compensated successfully")
            else:
                saga.status = SagaStatus.COMPENSATION_FAILED
                self.logger.error(f"❌ Saga {saga.saga_id} compensation failed")

            saga.completed_at = datetime.utcnow()
            await self.state_store.save_saga(saga)

            return success

        except Exception as e:
            self.logger.error(f"❌ Compensation error for saga {saga.saga_id}: {e}", exc_info=True)
            saga.status = SagaStatus.COMPENSATION_FAILED
            saga.error = f"Compensation error: {str(e)}"
            saga.completed_at = datetime.utcnow()
            await self.state_store.save_saga(saga)
            return False

    async def _backward_recovery(
        self,
        saga: SagaExecution,
        definition: SagaDefinition
    ) -> bool:
        """
        Backward recovery: Rollback all completed steps in reverse order.

        This is the default and most common strategy.
        """
        self.logger.info(f"Performing backward recovery for saga {saga.saga_id}")

        # Get completed steps in reverse order
        completed_steps = saga.get_completed_steps()
        completed_steps.reverse()  # Reverse order for rollback

        compensation_failures = []

        for step_exec in completed_steps:
            # Get step definition
            step_def = definition.get_step(step_exec.step_name)
            if not step_def:
                self.logger.warning(f"Step definition not found: {step_exec.step_name}")
                continue

            # Check if step has compensation
            if not step_def.is_compensatable():
                self.logger.info(f"Step {step_exec.step_name} has no compensation - skipping")
                continue

            # Compensate the step
            success = await self._compensate_step(saga, step_exec, step_def)

            if not success:
                compensation_failures.append(step_exec.step_name)
                self.logger.error(f"Failed to compensate step: {step_exec.step_name}")

                # Decide whether to continue or stop
                # For now, we continue compensating other steps
                # In production, this could be configurable

        # Success if all compensations succeeded
        return len(compensation_failures) == 0

    async def _forward_recovery(
        self,
        saga: SagaExecution,
        definition: SagaDefinition
    ) -> bool:
        """
        Forward recovery: Try to complete the saga despite errors.

        This is useful when the saga can continue with partial success,
        or when compensation is more expensive than completion.
        """
        self.logger.info(f"Performing forward recovery for saga {saga.saga_id}")

        # Find the failed step
        failed_step = saga.get_failed_step()
        if not failed_step:
            self.logger.warning("No failed step found for forward recovery")
            return False

        # Get remaining steps
        step_definitions = definition.steps
        failed_index = next(
            (i for i, s in enumerate(step_definitions) if s.name == failed_step.step_name),
            None
        )

        if failed_index is None:
            self.logger.warning(f"Failed step {failed_step.step_name} not found in definition")
            return False

        # Try to execute remaining steps
        remaining_steps = step_definitions[failed_index + 1:]

        self.logger.info(f"Attempting to execute {len(remaining_steps)} remaining steps")

        for step_def in remaining_steps:
            # Create step execution
            step_exec = SagaStepExecution(
                step_id=step_def.step_id,
                step_name=step_def.name,
                saga_id=saga.saga_id,
                max_attempts=step_def.max_retries + 1
            )

            # Execute the step
            success = await self._execute_step(saga, step_exec, step_def)

            if not success:
                self.logger.error(f"Forward recovery failed at step: {step_def.name}")
                return False

        self.logger.info("Forward recovery completed successfully")
        return True

    async def _partial_compensation(
        self,
        saga: SagaExecution,
        definition: SagaDefinition
    ) -> bool:
        """
        Partial compensation: Only compensate critical steps.

        This is useful when some steps can be left as-is without causing issues.
        For example, logging or notification steps might not need compensation.
        """
        self.logger.info(f"Performing partial compensation for saga {saga.saga_id}")

        # Get completed steps
        completed_steps = saga.get_completed_steps()
        completed_steps.reverse()

        compensation_failures = []

        for step_exec in completed_steps:
            # Get step definition
            step_def = definition.get_step(step_exec.step_name)
            if not step_def:
                continue

            # Only compensate critical steps
            if not step_def.critical:
                self.logger.info(f"Skipping non-critical step: {step_exec.step_name}")
                continue

            # Check if step has compensation
            if not step_def.is_compensatable():
                if step_def.critical:
                    self.logger.warning(
                        f"Critical step {step_exec.step_name} has no compensation!"
                    )
                continue

            # Compensate the step
            success = await self._compensate_step(saga, step_exec, step_def)

            if not success:
                compensation_failures.append(step_exec.step_name)

        return len(compensation_failures) == 0

    async def _compensate_step(
        self,
        saga: SagaExecution,
        step_exec: SagaStepExecution,
        step_def: SagaStepDefinition
    ) -> bool:
        """
        Compensate a single step.

        Args:
            saga: Saga execution
            step_exec: Step execution to compensate
            step_def: Step definition with compensation logic

        Returns:
            True if compensation successful
        """
        self.logger.info(f"🔄 Compensating step: {step_exec.step_name}")

        # Update status
        step_exec.status = SagaStepStatus.COMPENSATING
        step_exec.compensation_started_at = datetime.utcnow()
        await self.state_store.save_step(saga.saga_id, step_exec)

        try:
            # Invoke compensation action
            if self.service_invoker:
                # Build compensation params
                comp_params = self._build_compensation_params(
                    step_def, step_exec, saga
                )

                # Invoke compensation
                result = await self.service_invoker(
                    step_def.compensation_action,
                    comp_params
                )

                # Store result
                step_exec.compensation_result = result
                step_exec.status = SagaStepStatus.COMPENSATED
                step_exec.compensation_completed_at = datetime.utcnow()

                self.logger.info(f"✅ Step {step_exec.step_name} compensated successfully")
                await self.state_store.save_step(saga.saga_id, step_exec)
                return True
            else:
                # No service invoker - log only mode
                self.logger.warning(
                    f"No service invoker configured - would call: "
                    f"{step_def.compensation_action}"
                )
                step_exec.status = SagaStepStatus.COMPENSATED
                step_exec.compensation_completed_at = datetime.utcnow()
                await self.state_store.save_step(saga.saga_id, step_exec)
                return True

        except Exception as e:
            self.logger.error(
                f"❌ Compensation failed for step {step_exec.step_name}: {e}",
                exc_info=True
            )

            step_exec.status = SagaStepStatus.COMPENSATION_FAILED
            step_exec.compensation_error = str(e)
            step_exec.compensation_completed_at = datetime.utcnow()
            await self.state_store.save_step(saga.saga_id, step_exec)
            return False

    def _build_compensation_params(
        self,
        step_def: SagaStepDefinition,
        step_exec: SagaStepExecution,
        saga: SagaExecution
    ) -> Dict[str, Any]:
        """
        Build parameters for compensation action.

        Merges:
        - Compensation params from definition
        - Original step execution result
        - Saga execution context
        """
        params = dict(step_def.compensation_params)

        # Add original execution result if available
        if step_exec.result:
            params['original_result'] = step_exec.result

        # Add saga context
        params['saga_context'] = saga.execution_context

        # Add step metadata
        params['step_name'] = step_exec.step_name
        params['saga_id'] = saga.saga_id

        return params

    async def _execute_step(
        self,
        saga: SagaExecution,
        step_exec: SagaStepExecution,
        step_def: SagaStepDefinition
    ) -> bool:
        """
        Execute a step (used in forward recovery).

        This is a simplified version - in production, this would use
        the full SagaOrchestrator execution logic.
        """
        self.logger.info(f"▶️ Executing step: {step_def.name}")

        step_exec.status = SagaStepStatus.EXECUTING
        step_exec.started_at = datetime.utcnow()
        step_exec.attempts += 1
        await self.state_store.save_step(saga.saga_id, step_exec)

        try:
            if self.service_invoker:
                # Build params
                params = dict(step_def.forward_params)
                params.update(saga.execution_context)

                # Invoke service
                result = await self.service_invoker(
                    step_def.forward_action,
                    params
                )

                # Store result
                step_exec.result = result
                step_exec.status = SagaStepStatus.COMPLETED
                step_exec.completed_at = datetime.utcnow()

                # Update context
                if isinstance(result, dict):
                    step_exec.output_context = result
                    saga.execution_context.update(result)

                await self.state_store.save_step(saga.saga_id, step_exec)
                return True
            else:
                self.logger.warning("No service invoker - mock execution")
                step_exec.status = SagaStepStatus.COMPLETED
                step_exec.completed_at = datetime.utcnow()
                await self.state_store.save_step(saga.saga_id, step_exec)
                return True

        except Exception as e:
            self.logger.error(f"Step {step_def.name} failed: {e}", exc_info=True)
            step_exec.status = SagaStepStatus.FAILED
            step_exec.error = str(e)
            await self.state_store.save_step(saga.saga_id, step_exec)
            return False

    async def get_compensation_report(
        self,
        saga: SagaExecution
    ) -> Dict[str, Any]:
        """
        Generate a compensation report for a saga.

        Returns details about which steps were compensated,
        which failed, and the overall compensation status.
        """
        compensated_steps = []
        failed_compensations = []
        skipped_steps = []

        for step_name, step_exec in saga.step_executions.items():
            if step_exec.status == SagaStepStatus.COMPENSATED:
                compensated_steps.append({
                    'step_name': step_name,
                    'compensated_at': step_exec.compensation_completed_at.isoformat()
                    if step_exec.compensation_completed_at else None,
                    'result': step_exec.compensation_result
                })
            elif step_exec.status == SagaStepStatus.COMPENSATION_FAILED:
                failed_compensations.append({
                    'step_name': step_name,
                    'error': step_exec.compensation_error,
                    'attempted_at': step_exec.compensation_started_at.isoformat()
                    if step_exec.compensation_started_at else None
                })
            elif step_exec.status == SagaStepStatus.COMPLETED:
                # Completed but not compensated
                skipped_steps.append({
                    'step_name': step_name,
                    'reason': 'no_compensation_defined_or_not_critical'
                })

        return {
            'saga_id': saga.saga_id,
            'compensation_status': saga.status.value,
            'total_steps': len(saga.step_executions),
            'compensated_count': len(compensated_steps),
            'failed_count': len(failed_compensations),
            'skipped_count': len(skipped_steps),
            'compensated_steps': compensated_steps,
            'failed_compensations': failed_compensations,
            'skipped_steps': skipped_steps,
            'completed_at': saga.completed_at.isoformat() if saga.completed_at else None
        }
