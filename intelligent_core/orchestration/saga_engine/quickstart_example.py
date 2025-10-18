"""
Saga Engine Quick Start Example
================================

A complete, runnable example demonstrating the Saga Pattern Engine.

Run this file to see the saga engine in action with mock services.
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

# Import saga engine components
from saga_definition import (
    SagaDefinition,
    SagaStepDefinition,
    SagaExecutionPolicy,
    CompensationStrategy
)
from saga_orchestrator import SagaOrchestrator
from saga_state_store import InMemorySagaStateStore

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==============================================================================
# Mock Services (simulate real platform services)
# ==============================================================================

class MockBIAService:
    """Mock BIA Service"""

    def __init__(self):
        self.assessments = {}

    async def create_assessment(
        self,
        organization_id: str,
        assessment_type: str = "comprehensive",
        scope: str = "organization",
        **kwargs
    ) -> Dict[str, Any]:
        """Create BIA assessment"""
        logger.info(f"📊 Creating BIA assessment for org {organization_id}")
        await asyncio.sleep(0.5)  # Simulate work

        assessment_id = f"bia_{organization_id}_{len(self.assessments)}"
        assessment = {
            "assessment_id": assessment_id,
            "organization_id": organization_id,
            "type": assessment_type,
            "scope": scope,
            "status": "created",
            "critical_processes": ["IT Systems", "Customer Service", "Supply Chain"]
        }

        self.assessments[assessment_id] = assessment
        logger.info(f"✅ BIA assessment created: {assessment_id}")

        return assessment

    async def delete_assessment(
        self,
        organization_id: str,
        assessment_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Delete BIA assessment (compensation)"""
        logger.info(f"🔄 Deleting BIA assessment: {assessment_id}")
        await asyncio.sleep(0.2)

        if assessment_id and assessment_id in self.assessments:
            del self.assessments[assessment_id]
            logger.info(f"✅ BIA assessment deleted: {assessment_id}")

        return {"status": "deleted"}


class MockPlansService:
    """Mock Plans Service"""

    def __init__(self):
        self.plans = {}

    async def create_plan_suite(
        self,
        organization_id: str,
        plan_types: list = None,
        based_on_bia: bool = False,
        critical_processes: list = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create plan suite"""
        logger.info(f"📋 Creating plans for org {organization_id}")
        await asyncio.sleep(0.5)

        plan_ids = []
        for plan_type in (plan_types or ["bcm"]):
            plan_id = f"{plan_type}_{organization_id}_{len(self.plans)}"
            plan = {
                "plan_id": plan_id,
                "organization_id": organization_id,
                "type": plan_type,
                "status": "created",
                "based_on_processes": critical_processes or []
            }
            self.plans[plan_id] = plan
            plan_ids.append(plan_id)

        logger.info(f"✅ Plans created: {plan_ids}")

        return {
            "plan_suite_id": f"suite_{organization_id}",
            "plan_ids": plan_ids,
            "count": len(plan_ids)
        }

    async def delete_plan_suite(
        self,
        organization_id: str,
        plan_suite_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Delete plan suite (compensation)"""
        logger.info(f"🔄 Deleting plan suite: {plan_suite_id}")
        await asyncio.sleep(0.2)

        # Delete all plans for org
        to_delete = [
            pid for pid, plan in self.plans.items()
            if plan["organization_id"] == organization_id
        ]

        for plan_id in to_delete:
            del self.plans[plan_id]

        logger.info(f"✅ Plans deleted: {to_delete}")

        return {"status": "deleted", "deleted_count": len(to_delete)}


class MockComplianceService:
    """Mock Compliance Service"""

    def __init__(self):
        self.programs = {}

    async def initialize_program(
        self,
        organization_id: str,
        standard: str = "ISO_22301",
        scope: str = "bcm_program",
        **kwargs
    ) -> Dict[str, Any]:
        """Initialize compliance program"""
        logger.info(f"✅ Initializing {standard} compliance for org {organization_id}")
        await asyncio.sleep(0.5)

        program_id = f"comp_{organization_id}_{standard}"
        program = {
            "program_id": program_id,
            "organization_id": organization_id,
            "standard": standard,
            "scope": scope,
            "status": "initialized",
            "compliance_score": 0.0
        }

        self.programs[program_id] = program
        logger.info(f"✅ Compliance program initialized: {program_id}")

        return program

    async def remove_program(
        self,
        organization_id: str,
        program_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Remove compliance program (compensation)"""
        logger.info(f"🔄 Removing compliance program: {program_id}")
        await asyncio.sleep(0.2)

        if program_id and program_id in self.programs:
            del self.programs[program_id]
            logger.info(f"✅ Compliance program removed: {program_id}")

        return {"status": "removed"}


class MockMonitoringService:
    """Mock Monitoring Service (non-critical)"""

    async def setup_program_monitoring(
        self,
        organization_id: str,
        metrics: list = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Setup monitoring"""
        logger.info(f"📊 Setting up monitoring for org {organization_id}")
        await asyncio.sleep(0.3)

        logger.info(f"✅ Monitoring setup complete: {metrics}")

        return {
            "monitoring_id": f"mon_{organization_id}",
            "metrics": metrics,
            "status": "active"
        }

    async def remove_monitoring(self, organization_id: str, **kwargs) -> Dict[str, Any]:
        """Remove monitoring (compensation)"""
        logger.info(f"🔄 Removing monitoring for org {organization_id}")
        return {"status": "removed"}


# ==============================================================================
# Service Invoker (routes saga actions to services)
# ==============================================================================

# Create service instances
services = {
    "bia_service": MockBIAService(),
    "plans_service": MockPlansService(),
    "compliance_service": MockComplianceService(),
    "monitoring_service": MockMonitoringService(),
}


async def service_invoker(action: str, params: Dict[str, Any]) -> Any:
    """
    Invoke a service method.

    Args:
        action: Service method in format "service_name.method_name"
        params: Method parameters
    """
    # Parse action
    service_name, method_name = action.split('.', 1)

    # Get service
    service = services.get(service_name)
    if not service:
        raise ValueError(f"Service not found: {service_name}")

    # Get method
    method = getattr(service, method_name)

    # Clean params (remove saga metadata)
    clean_params = {k: v for k, v in params.items() if not k.startswith('_')}

    # Invoke
    logger.info(f"🔧 Invoking {action}")
    result = await method(**clean_params)

    return result


# ==============================================================================
# Event Publisher (simulate EventBus)
# ==============================================================================

async def event_publisher(event_type: str, data: Dict[str, Any]) -> None:
    """Publish events (mock)"""
    logger.info(f"📢 Event: {event_type} - {data.get('saga_id', 'N/A')}")


# ==============================================================================
# Example Sagas
# ==============================================================================

def create_simple_saga() -> SagaDefinition:
    """Simple 2-step saga for demonstration"""

    saga = SagaDefinition(
        name="simple_bcm_setup",
        description="Simple BCM setup with BIA and Plans",
        execution_policy=SagaExecutionPolicy.SEQUENTIAL,
        compensation_strategy=CompensationStrategy.BACKWARD_RECOVERY
    )

    saga.add_step(
        SagaStepDefinition(
            name="create_bia",
            description="Create BIA assessment",
            forward_action="bia_service.create_assessment",
            compensation_action="bia_service.delete_assessment",
            timeout_seconds=10
        )
    )

    saga.add_step(
        SagaStepDefinition(
            name="create_plans",
            description="Create BCM plans",
            forward_action="plans_service.create_plan_suite",
            forward_params={"plan_types": ["bcm", "dr"]},
            compensation_action="plans_service.delete_plan_suite",
            timeout_seconds=10
        )
    )

    return saga


def create_full_program_saga() -> SagaDefinition:
    """Full BCM program creation saga"""

    saga = SagaDefinition(
        name="create_bcm_program",
        description="Create complete BCM program",
        execution_policy=SagaExecutionPolicy.SEQUENTIAL,
        compensation_strategy=CompensationStrategy.BACKWARD_RECOVERY
    )

    # Step 1: BIA
    saga.add_step(
        SagaStepDefinition(
            name="create_bia",
            description="Create BIA assessment",
            forward_action="bia_service.create_assessment",
            forward_params={"assessment_type": "comprehensive"},
            compensation_action="bia_service.delete_assessment",
            critical=True
        )
    )

    # Step 2: Plans
    saga.add_step(
        SagaStepDefinition(
            name="create_plans",
            description="Create plan suite",
            forward_action="plans_service.create_plan_suite",
            forward_params={"plan_types": ["bcm", "dr", "incident_response"]},
            compensation_action="plans_service.delete_plan_suite",
            critical=True
        )
    )

    # Step 3: Compliance
    saga.add_step(
        SagaStepDefinition(
            name="init_compliance",
            description="Initialize ISO 22301 compliance",
            forward_action="compliance_service.initialize_program",
            forward_params={"standard": "ISO_22301"},
            compensation_action="compliance_service.remove_program",
            critical=True
        )
    )

    # Step 4: Monitoring (non-critical)
    saga.add_step(
        SagaStepDefinition(
            name="setup_monitoring",
            description="Setup monitoring",
            forward_action="monitoring_service.setup_program_monitoring",
            forward_params={"metrics": ["plan_coverage", "compliance_score"]},
            compensation_action="monitoring_service.remove_monitoring",
            critical=False  # Won't be compensated if saga fails
        )
    )

    return saga


def create_failing_saga() -> SagaDefinition:
    """Saga that fails to demonstrate compensation"""

    saga = SagaDefinition(
        name="failing_saga",
        description="Saga that fails to demonstrate compensation",
        execution_policy=SagaExecutionPolicy.SEQUENTIAL
    )

    saga.add_step(
        SagaStepDefinition(
            name="create_bia",
            description="Create BIA (will succeed)",
            forward_action="bia_service.create_assessment",
            compensation_action="bia_service.delete_assessment"
        )
    )

    saga.add_step(
        SagaStepDefinition(
            name="create_plans",
            description="Create plans (will succeed)",
            forward_action="plans_service.create_plan_suite",
            compensation_action="plans_service.delete_plan_suite"
        )
    )

    # This step will fail (invalid service)
    saga.add_step(
        SagaStepDefinition(
            name="failing_step",
            description="This step will fail",
            forward_action="nonexistent_service.failing_method",
            compensation_action=None
        )
    )

    return saga


# ==============================================================================
# Demo Functions
# ==============================================================================

async def demo_successful_saga():
    """Demonstrate successful saga execution"""

    logger.info("\n" + "=" * 80)
    logger.info("DEMO 1: Successful Saga Execution")
    logger.info("=" * 80 + "\n")

    # Setup
    state_store = InMemorySagaStateStore()
    orchestrator = SagaOrchestrator(
        state_store=state_store,
        service_invoker=service_invoker,
        event_publisher=event_publisher
    )

    # Register saga
    saga_def = create_full_program_saga()
    orchestrator.register_saga(saga_def)

    # Execute
    execution = await orchestrator.execute_saga(
        saga_name="create_bcm_program",
        initial_context={
            "organization_id": "org-123",
            "created_by": "user-456"
        },
        tenant_id="tenant-abc"
    )

    # Results
    logger.info("\n" + "-" * 80)
    logger.info("EXECUTION RESULTS:")
    logger.info(f"  Saga ID: {execution.saga_id}")
    logger.info(f"  Status: {execution.status.value}")
    logger.info(f"  Completed Steps: {len(execution.get_completed_steps())}")
    logger.info(f"  Duration: {(execution.completed_at - execution.started_at).total_seconds():.2f}s")
    logger.info("-" * 80 + "\n")

    # Show detailed status
    status = await orchestrator.get_saga_status(execution.saga_id)
    logger.info("STEP DETAILS:")
    for step in status['steps']:
        logger.info(f"  {step['name']}: {step['status']} (attempts: {step['attempts']})")

    return execution


async def demo_failed_saga_with_compensation():
    """Demonstrate saga failure and compensation"""

    logger.info("\n" + "=" * 80)
    logger.info("DEMO 2: Failed Saga with Compensation")
    logger.info("=" * 80 + "\n")

    # Setup
    state_store = InMemorySagaStateStore()
    orchestrator = SagaOrchestrator(
        state_store=state_store,
        service_invoker=service_invoker,
        event_publisher=event_publisher
    )

    # Register failing saga
    saga_def = create_failing_saga()
    orchestrator.register_saga(saga_def)

    # Execute (will fail)
    execution = await orchestrator.execute_saga(
        saga_name="failing_saga",
        initial_context={"organization_id": "org-456"},
        tenant_id="tenant-xyz"
    )

    # Results
    logger.info("\n" + "-" * 80)
    logger.info("EXECUTION RESULTS:")
    logger.info(f"  Saga ID: {execution.saga_id}")
    logger.info(f"  Status: {execution.status.value}")
    logger.info(f"  Error: {execution.error}")
    logger.info(f"  Compensated: {execution.status.value == 'compensated'}")
    logger.info("-" * 80 + "\n")

    # Show compensation details
    from compensation_manager import CompensationManager

    comp_manager = CompensationManager(state_store, service_invoker)
    report = await comp_manager.get_compensation_report(execution)

    logger.info("COMPENSATION REPORT:")
    logger.info(f"  Compensated Steps: {report['compensated_count']}")
    logger.info(f"  Failed Compensations: {report['failed_count']}")

    for step in report['compensated_steps']:
        logger.info(f"  ✅ {step['step_name']} compensated")

    return execution


async def demo_saga_recovery():
    """Demonstrate saga recovery after simulated crash"""

    logger.info("\n" + "=" * 80)
    logger.info("DEMO 3: Saga Recovery After Crash")
    logger.info("=" * 80 + "\n")

    # Setup
    state_store = InMemorySagaStateStore()
    orchestrator = SagaOrchestrator(
        state_store=state_store,
        service_invoker=service_invoker,
        event_publisher=event_publisher
    )

    # Register saga
    saga_def = create_simple_saga()
    orchestrator.register_saga(saga_def)

    # Execute saga
    execution = await orchestrator.execute_saga(
        saga_name="simple_bcm_setup",
        initial_context={"organization_id": "org-789"}
    )

    logger.info(f"\nOriginal execution: {execution.status.value}")

    # Simulate crash and recovery
    logger.info("\n🔄 Simulating system restart...")

    # Create new orchestrator (simulating restart)
    new_orchestrator = SagaOrchestrator(
        state_store=state_store,  # Same state store (persistent)
        service_invoker=service_invoker,
        event_publisher=event_publisher
    )

    # Re-register sagas
    new_orchestrator.register_saga(saga_def)

    # Recover saga
    logger.info(f"🔄 Recovering saga {execution.saga_id}...")
    recovered = await new_orchestrator.recover_saga(execution.saga_id)

    logger.info(f"\n✅ Saga recovered: {recovered.status.value}")

    return recovered


async def main():
    """Run all demos"""

    logger.info("\n")
    logger.info("🚀 SAGA PATTERN ENGINE - QUICK START DEMO")
    logger.info("=" * 80)

    try:
        # Demo 1: Successful execution
        await demo_successful_saga()

        # Demo 2: Failure and compensation
        await demo_failed_saga_with_compensation()

        # Demo 3: Recovery
        await demo_saga_recovery()

        logger.info("\n" + "=" * 80)
        logger.info("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80 + "\n")

    except Exception as e:
        logger.error(f"❌ Demo failed: {e}", exc_info=True)


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())
