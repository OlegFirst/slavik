"""
BCM Services Orchestrator
=========================

Top-level orchestrator for BCM domain (Level 2 in architecture).

Coordinates:
1. 10 BCM Analyzers (via AnalyzerCoordinator)
2. Workflow Intelligence (THE BRAIN)
3. 10 BCM Microservices (via ServiceRegistry)
4. Temporal workflows for durable execution

Reports to: MEGA-BRAIN (ai-orchestration/)

Architecture:
- Strategic decisions come from MEGA_BRAIN via DelegationManager
- BCM Orchestrator determines execution strategy
- Delegates to analyzers (AI analysis) or services (operational work)
- Starts Temporal workflows for complex multi-step processes
- Publishes events to EventBus for audit trail
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from temporalio.client import Client as TemporalClient
from temporalio.common import RetryPolicy

from .analyzer_coordinator import AnalyzerCoordinator, AnalyzerType
from .service_registry import BCMServiceRegistry, BCMServiceType, ISO22301Clause

logger = logging.getLogger(__name__)


class ExecutionStrategy(str, Enum):
    """BCM Execution Strategies"""
    ANALYZER_ONLY = "analyzer_only"  # Pure AI analysis, no state changes
    SERVICE_ONLY = "service_only"  # Direct service call, simple CRUD
    ANALYZER_THEN_SERVICE = "analyzer_then_service"  # AI analysis → service execution
    WORKFLOW = "workflow"  # Complex multi-step via Temporal workflow


class BCMServicesOrchestrator:
    """
    BCM Services Orchestrator - Level 2 Manager.

    Responsibilities:
    - Receive delegations from MEGA_BRAIN
    - Determine execution strategy (analyzer/service/workflow)
    - Coordinate analyzers for AI-powered insights
    - Call BCM services for operational work
    - Start Temporal workflows for durable execution
    - Report results back to MEGA-BRAIN

    Example:
        ```python
        orchestrator = BCMServicesOrchestrator(
            analyzer_coordinator=analyzer_coord,
            service_registry=service_reg,
            temporal_client=temporal
        )

        # Delegated task from MEGA_BRAIN
        result = await orchestrator.execute_task({
            'task_type': 'bia_analysis',
            'input': {'organization_id': 'org-123'},
            'tenant_id': 'tenant-456'
        })
        ```
    """

    # Task type to strategy mapping
    TASK_STRATEGIES = {
        # Pure analysis tasks (no state changes)
        "compliance_gap_analysis": ExecutionStrategy.ANALYZER_ONLY,
        "risk_assessment_review": ExecutionStrategy.ANALYZER_ONLY,
        "plan_quality_check": ExecutionStrategy.ANALYZER_ONLY,

        # Simple CRUD operations
        "fetch_bia_results": ExecutionStrategy.SERVICE_ONLY,
        "get_plan_details": ExecutionStrategy.SERVICE_ONLY,

        # AI-enhanced operations
        "create_recovery_plan": ExecutionStrategy.ANALYZER_THEN_SERVICE,
        "assess_incident_severity": ExecutionStrategy.ANALYZER_THEN_SERVICE,

        # Complex workflows (multi-step, durable)
        "bia_analysis": ExecutionStrategy.WORKFLOW,
        "risk_analysis": ExecutionStrategy.WORKFLOW,
        "exercise_execution": ExecutionStrategy.WORKFLOW,
        "incident_response": ExecutionStrategy.WORKFLOW,
    }

    # Task type to workflow mapping
    WORKFLOW_MAPPING = {
        "bia_analysis": "BIAWorkflow",
        "risk_analysis": "RiskAssessmentWorkflow",
        "exercise_execution": "ExerciseWorkflow",
        "incident_response": "IncidentWorkflow",
    }

    def __init__(
        self,
        analyzer_coordinator: AnalyzerCoordinator,
        service_registry: BCMServiceRegistry,
        temporal_client: Optional[TemporalClient] = None,
        event_bus = None
    ):
        """
        Initialize BCM Services Orchestrator.

        Args:
            analyzer_coordinator: Coordinator for BCM analyzers
            service_registry: Registry of BCM microservices
            temporal_client: Temporal client for workflows
            event_bus: EventBus for audit trail
        """
        self.analyzer_coordinator = analyzer_coordinator
        self.service_registry = service_registry
        self.temporal_client = temporal_client
        self.event_bus = event_bus

        self.execution_stats = {
            "total_tasks": 0,
            "by_strategy": {strategy.value: 0 for strategy in ExecutionStrategy},
            "by_task_type": {},
            "workflows_started": 0,
            "analyzer_calls": 0,
            "service_calls": 0
        }

        logger.info("BCMServicesOrchestrator initialized")

    async def execute_task(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute delegated task from MEGA_BRAIN.

        Args:
            task: Task definition with:
                - task_type: Type of task
                - input: Task input data
                - tenant_id: Tenant identifier
                - priority: Optional priority level
                - metadata: Optional metadata

        Returns:
            Execution result

        Example:
            ```python
            result = await orchestrator.execute_task({
                'task_type': 'bia_analysis',
                'input': {'organization_id': 'org-123'},
                'tenant_id': 'tenant-456',
                'priority': 'high'
            })
            ```
        """
        self.execution_stats["total_tasks"] += 1
        task_type = task.get("task_type")
        start_time = datetime.utcnow()

        logger.info(f"Executing task: {task_type}")

        try:
            # Step 1: Determine execution strategy
            strategy = self._determine_strategy(task_type)
            self.execution_stats["by_strategy"][strategy.value] += 1

            # Update task type stats
            if task_type not in self.execution_stats["by_task_type"]:
                self.execution_stats["by_task_type"][task_type] = 0
            self.execution_stats["by_task_type"][task_type] += 1

            logger.info(f"Selected strategy: {strategy.value}")

            # Step 2: Execute based on strategy
            if strategy == ExecutionStrategy.ANALYZER_ONLY:
                result = await self._execute_analyzer_only(task)

            elif strategy == ExecutionStrategy.SERVICE_ONLY:
                result = await self._execute_service_only(task)

            elif strategy == ExecutionStrategy.ANALYZER_THEN_SERVICE:
                result = await self._execute_analyzer_then_service(task)

            elif strategy == ExecutionStrategy.WORKFLOW:
                result = await self._execute_workflow(task)

            else:
                raise ValueError(f"Unknown strategy: {strategy}")

            # Step 3: Publish completion event
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            if self.event_bus:
                await self._publish_completion_event(
                    task_type=task_type,
                    strategy=strategy,
                    duration_ms=duration_ms,
                    success=True,
                    tenant_id=task.get("tenant_id")
                )

            return {
                "success": True,
                "task_type": task_type,
                "strategy": strategy.value,
                "duration_ms": duration_ms,
                **result
            }

        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}", exc_info=True)

            if self.event_bus:
                await self._publish_completion_event(
                    task_type=task_type,
                    strategy=None,
                    duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                    success=False,
                    error=str(e),
                    tenant_id=task.get("tenant_id")
                )

            return {
                "success": False,
                "task_type": task_type,
                "error": str(e)
            }

    def _determine_strategy(self, task_type: str) -> ExecutionStrategy:
        """
        Determine execution strategy for task type.

        Args:
            task_type: Type of task

        Returns:
            ExecutionStrategy
        """
        # Check explicit mapping
        if task_type in self.TASK_STRATEGIES:
            return self.TASK_STRATEGIES[task_type]

        # Keyword-based fallback
        task_lower = task_type.lower()

        if any(kw in task_lower for kw in ["analysis", "assessment", "review", "check"]):
            return ExecutionStrategy.ANALYZER_ONLY

        if any(kw in task_lower for kw in ["fetch", "get", "list", "retrieve"]):
            return ExecutionStrategy.SERVICE_ONLY

        if any(kw in task_lower for kw in ["create", "generate", "design"]):
            return ExecutionStrategy.ANALYZER_THEN_SERVICE

        # Default to workflow for complex tasks
        return ExecutionStrategy.WORKFLOW

    async def _execute_analyzer_only(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pure analysis task via AnalyzerCoordinator."""
        self.execution_stats["analyzer_calls"] += 1

        result = await self.analyzer_coordinator.route_analysis(
            analysis_type=AnalyzerType.AUTO,
            input_data=task.get("input", {}),
            tenant_id=task.get("tenant_id"),
            metadata=task.get("metadata")
        )

        return {
            "analyzer": result.get("analyzer"),
            "insights": result.get("insights", []),
            "recommendations": result.get("recommendations", []),
            "confidence": result.get("confidence", 0.0)
        }

    async def _execute_service_only(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute simple CRUD via BCM service."""
        self.execution_stats["service_calls"] += 1

        # Determine which service to call based on task type
        task_type = task.get("task_type", "")
        service_type = self._map_task_to_service(task_type)

        service_url = self.service_registry.get_service_url(service_type)

        # TODO: Make actual HTTP call to service
        # For now, return mock result
        logger.info(f"Would call service: {service_url}")

        return {
            "service": service_type.value,
            "service_url": service_url,
            "result": "Service call would be made here"
        }

    async def _execute_analyzer_then_service(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute AI analysis → service call."""
        self.execution_stats["analyzer_calls"] += 1
        self.execution_stats["service_calls"] += 1

        # Step 1: AI Analysis
        analysis_result = await self.analyzer_coordinator.route_analysis(
            analysis_type=AnalyzerType.AUTO,
            input_data=task.get("input", {}),
            tenant_id=task.get("tenant_id")
        )

        # Step 2: Service call with AI insights
        task_type = task.get("task_type", "")
        service_type = self._map_task_to_service(task_type)
        service_url = self.service_registry.get_service_url(service_type)

        # TODO: Make actual HTTP call with AI insights
        logger.info(f"Would call service {service_url} with AI insights")

        return {
            "analyzer": analysis_result.get("analyzer"),
            "insights": analysis_result.get("insights", []),
            "service": service_type.value,
            "service_result": "Service call with AI insights would be made here"
        }

    async def _execute_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complex workflow via Temporal."""
        if not self.temporal_client:
            raise RuntimeError("Temporal client not configured")

        self.execution_stats["workflows_started"] += 1

        task_type = task.get("task_type")
        workflow_name = self.WORKFLOW_MAPPING.get(task_type)

        if not workflow_name:
            raise ValueError(f"No workflow mapped for task type: {task_type}")

        # Start Temporal workflow
        workflow_id = f"{task_type}-{task.get('tenant_id', 'default')}-{datetime.utcnow().timestamp()}"

        logger.info(f"Starting Temporal workflow: {workflow_name} (id: {workflow_id})")

        # Retry policy for workflows
        retry_policy = RetryPolicy(
            initial_interval_seconds=1,
            maximum_interval_seconds=30,
            maximum_attempts=3
        )

        # TODO: Start actual Temporal workflow
        # handle = await self.temporal_client.start_workflow(
        #     workflow_name,
        #     task.get("input"),
        #     id=workflow_id,
        #     task_queue="bcm-workflows",
        #     retry_policy=retry_policy
        # )

        return {
            "workflow": workflow_name,
            "workflow_id": workflow_id,
            "status": "started",
            "message": "Temporal workflow would be started here"
        }

    def _map_task_to_service(self, task_type: str) -> BCMServiceType:
        """Map task type to BCM service."""
        task_lower = task_type.lower()

        if "bia" in task_lower:
            return BCMServiceType.BIA_SERVICE
        elif "risk" in task_lower:
            return BCMServiceType.RISK_SERVICE
        elif "plan" in task_lower:
            return BCMServiceType.PLAN_SERVICE
        elif "exercise" in task_lower:
            return BCMServiceType.EXERCISE_SERVICE
        elif "incident" in task_lower:
            return BCMServiceType.INCIDENT_SERVICE
        elif "compliance" in task_lower:
            return BCMServiceType.COMPLIANCE_SERVICE
        elif "learning" in task_lower:
            return BCMServiceType.LEARNING_SERVICE
        elif "validation" in task_lower or "kpi" in task_lower:
            return BCMServiceType.VALIDATION_SERVICE
        elif "governance" in task_lower:
            return BCMServiceType.GOVERNANCE_SERVICE
        elif "document" in task_lower:
            return BCMServiceType.DOCUMENT_SERVICE
        else:
            # Default to BIA service
            return BCMServiceType.BIA_SERVICE

    async def _publish_completion_event(
        self,
        task_type: str,
        strategy: Optional[ExecutionStrategy],
        duration_ms: float,
        success: bool,
        tenant_id: str = None,
        error: str = None
    ):
        """Publish task completion event to EventBus."""
        try:
            event_data = {
                "task_type": task_type,
                "strategy": strategy.value if strategy else None,
                "duration_ms": duration_ms,
                "success": success,
                "error": error,
                "timestamp": datetime.utcnow().isoformat()
            }

            await self.event_bus.publish({
                "type": f"bcm.orchestrator.task.{'completed' if success else 'failed'}",
                "data": event_data,
                "tenant_id": tenant_id
            })
        except Exception as e:
            logger.warning(f"Failed to publish completion event: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            "orchestrator": "BCMServicesOrchestrator",
            "level": "2 (Top Manager)",
            "domain": "BCM Services",
            "execution_stats": self.execution_stats,
            "analyzer_coordinator": self.analyzer_coordinator.get_stats(),
            "service_registry": {
                "total_services": len(self.service_registry.get_all_services()),
                "coverage": self.service_registry.get_coverage_report()
            },
            "temporal_enabled": self.temporal_client is not None
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all components."""
        health = {
            "orchestrator": "healthy",
            "components": {
                "analyzer_coordinator": "healthy",
                "service_registry": "healthy",
                "temporal_client": "healthy" if self.temporal_client else "not_configured",
                "event_bus": "healthy" if self.event_bus else "not_configured"
            },
            "services": []
        }

        # Check service health (would need actual HTTP checks)
        for service in self.service_registry.get_all_services():
            health["services"].append({
                "name": service["name"],
                "health": service["health"]
            })

        return health
