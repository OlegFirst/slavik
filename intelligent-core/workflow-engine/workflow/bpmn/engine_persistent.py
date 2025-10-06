"""
BPMN Engine with PostgreSQL Persistence

Production-ready BPMN engine using database repositories
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import uuid
import logging

from .models import (
    BPMNProcess, ProcessInstance, Task,
    ProcessStatus, TaskStatus, TaskType
)
from .parser import BPMNParser
from .gateway_evaluator import GatewayEvaluator
from ..persistence.database import DatabaseManager
from ..persistence.repositories import (
    ProcessRepository,
    InstanceRepository,
    TaskRepository
)

logger = logging.getLogger(__name__)


class BPMNEnginePersistent:
    """
    BPMN 2.0 Process Execution Engine with PostgreSQL Persistence

    Manages:
    - Process deployment (via ProcessRepository)
    - Instance creation and execution (via InstanceRepository)
    - Task lifecycle (via TaskRepository)
    - Event publishing
    """

    def __init__(self, db_manager: DatabaseManager, tenant_id: str):
        """
        Initialize BPMN Engine with database

        Args:
            db_manager: DatabaseManager instance
            tenant_id: Tenant identifier for RLS
        """
        self.db_manager = db_manager
        self.tenant_id = tenant_id

        # Gateway evaluator
        self.gateway_evaluator = GatewayEvaluator()

        # Event handlers (for integration with Workflow Intelligence)
        self._event_handlers: Dict[str, List[Callable]] = {}

        logger.info(f"BPMNEnginePersistent initialized for tenant {tenant_id}")

    # ========== EVENT SYSTEM ==========

    def on_event(self, event_type: str, handler: Callable):
        """
        Register event handler

        Usage:
            @engine.on_event("bpmn.instance.started")
            async def on_started(event):
                print(event.data)
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []

        self._event_handlers[event_type].append(handler)

    async def _publish_event(self, event_type: str, data: Dict[str, Any]):
        """
        Publish event to handlers

        Events:
        - bpmn.process.deployed
        - bpmn.instance.started
        - bpmn.task.created
        - bpmn.task.completed
        - bpmn.instance.completed
        - bpmn.instance.terminated
        """
        event = {
            "event_type": event_type,
            "timestamp": datetime.utcnow(),
            "data": data
        }

        # Call registered handlers
        handlers = self._event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Event handler error ({event_type}): {e}", exc_info=True)

        logger.debug(f"Event published: {event_type}")

    # ========== PROCESS MANAGEMENT ==========

    async def deploy_process(
        self,
        bpmn_xml: str,
        tenant_id: str,
        name: str,
        module: Optional[str] = None,
        description: Optional[str] = None,
        version: str = "1.0",
        created_by: Optional[str] = None
    ) -> str:
        """
        Deploy BPMN process definition

        Args:
            bpmn_xml: BPMN 2.0 XML content
            tenant_id: Tenant identifier
            name: Process name
            module: BCM module (bia, risk, compliance, etc)
            description: Process description
            version: Version string
            created_by: User who deployed

        Returns:
            str: Process ID

        Raises:
            ValueError: If BPMN XML is invalid
        """
        # Validate BPMN XML
        BPMNParser.validate_bpmn_xml(bpmn_xml)

        # Create process model
        process = BPMNProcess(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            module=module,
            name=name,
            description=description,
            bpmn_xml=bpmn_xml,
            version=version,
            created_by=created_by,
            created_at=datetime.utcnow()
        )

        # Save to database
        async with self.db_manager.get_session() as session:
            await self.db_manager.set_tenant(session, tenant_id)
            repo = ProcessRepository(session)
            process_id = await repo.create(process)

        logger.info(f"Deployed BPMN process {process_id}: {name}")

        # Publish event
        await self._publish_event("bpmn.process.deployed", {
            "process_id": process_id,
            "process_name": name,
            "tenant_id": tenant_id,
            "module": module,
            "version": version
        })

        return process_id

    async def get_process(self, process_id: str) -> Optional[BPMNProcess]:
        """Get process by ID"""
        async with self.db_manager.get_session() as session:
            await self.db_manager.set_tenant(session, self.tenant_id)
            repo = ProcessRepository(session)
            return await repo.get_by_id(process_id)

    async def list_processes(
        self,
        tenant_id: str,
        module: Optional[str] = None
    ) -> List[BPMNProcess]:
        """List processes for tenant"""
        async with self.db_manager.get_session() as session:
            await self.db_manager.set_tenant(session, tenant_id)
            repo = ProcessRepository(session)
            return await repo.list_by_tenant(tenant_id, module=module)

    # ========== INSTANCE MANAGEMENT ==========

    async def start_process(
        self,
        process_id: str,
        tenant_id: str,
        variables: Dict[str, Any] = None,
        started_by: Optional[str] = None
    ) -> str:
        """
        Start new process instance

        Args:
            process_id: Process definition ID
            tenant_id: Tenant identifier
            variables: Initial process variables
            started_by: User who started the process

        Returns:
            str: Instance ID
        """
        async with self.db_manager.get_session() as session:
            await self.db_manager.set_tenant(session, tenant_id)

            # Get process
            process_repo = ProcessRepository(session)
            process = await process_repo.get_by_id(process_id)

            if not process:
                raise ValueError(f"Process {process_id} not found")

            if process.tenant_id != tenant_id:
                raise ValueError(f"Access denied: Process belongs to different tenant")

            # Create instance
            instance = ProcessInstance(
                id=str(uuid.uuid4()),
                process_id=process_id,
                tenant_id=tenant_id,
                status=ProcessStatus.ACTIVE,
                variables=variables or {},
                started_by=started_by,
                started_at=datetime.utcnow()
            )

            # Save instance
            instance_repo = InstanceRepository(session)
            instance_id = await instance_repo.create(instance)

            # Parse BPMN and create initial tasks
            root = BPMNParser.parse_bpmn_xml(process.bpmn_xml)
            start_events = BPMNParser.find_start_events(root)

            task_repo = TaskRepository(session)

            if start_events:
                # Find tasks connected to start events
                for start_event in start_events:
                    next_elements = BPMNParser.get_next_elements(root, start_event)

                    for next_elem in next_elements:
                        task_id = await self._create_task_persistent(
                            session=session,
                            instance_id=instance_id,
                            activity_id=next_elem["id"],
                            name=next_elem["name"],
                            task_type=next_elem["type"]
                        )

                        # Add to current activities
                        await instance_repo.add_activity(
                            instance_id=instance_id,
                            activity_id=next_elem["id"]
                        )

        logger.info(f"Started process instance {instance_id} for process {process_id}")

        # Publish event
        await self._publish_event("bpmn.instance.started", {
            "instance_id": instance_id,
            "process_id": process_id,
            "tenant_id": tenant_id,
            "variables": variables,
            "started_by": started_by
        })

        return instance_id

    async def _create_task_persistent(
        self,
        session,
        instance_id: str,
        activity_id: str,
        name: str,
        task_type: str
    ) -> str:
        """Create new task (internal helper)"""
        task = Task(
            id=str(uuid.uuid4()),
            process_instance_id=instance_id,
            activity_id=activity_id,
            name=name,
            task_type=TaskType[task_type] if task_type in TaskType.__members__ else TaskType.USER_TASK,
            created_at=datetime.utcnow()
        )

        task_repo = TaskRepository(session)
        task_id = await task_repo.create(task)

        logger.info(f"Created task {task_id}: {name}")

        # Publish event
        await self._publish_event("bpmn.task.created", {
            "task_id": task_id,
            "instance_id": instance_id,
            "activity_id": activity_id,
            "name": name,
            "tenant_id": self.tenant_id
        })

        return task_id

    async def get_instance(self, instance_id: str) -> Optional[ProcessInstance]:
        """Get process instance by ID"""
        async with self.db_manager.get_session() as session:
            await self.db_manager.set_tenant(session, self.tenant_id)
            repo = InstanceRepository(session)
            return await repo.get_by_id(instance_id)

    async def has_instance(self, instance_id: str) -> bool:
        """Check if instance exists"""
        instance = await self.get_instance(instance_id)
        return instance is not None

    async def list_instances(
        self,
        tenant_id: str,
        status: Optional[ProcessStatus] = None
    ) -> List[ProcessInstance]:
        """List instances for tenant"""
        async with self.db_manager.get_session() as session:
            await self.db_manager.set_tenant(session, tenant_id)
            repo = InstanceRepository(session)
            return await repo.list_by_tenant(tenant_id, status=status)

    async def update_variables(
        self,
        instance_id: str,
        variables: Dict[str, Any]
    ):
        """Update process instance variables"""
        async with self.db_manager.get_session() as session:
            await self.db_manager.set_tenant(session, self.tenant_id)
            repo = InstanceRepository(session)
            await repo.update_variables(instance_id, variables, merge=True)

    # ========== TASK MANAGEMENT ==========

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        async with self.db_manager.get_session() as session:
            await self.db_manager.set_tenant(session, self.tenant_id)
            repo = TaskRepository(session)
            return await repo.get_by_id(task_id)

    async def get_active_tasks(
        self,
        instance_id: str
    ) -> List[Task]:
        """Get active tasks for instance"""
        async with self.db_manager.get_session() as session:
            await self.db_manager.set_tenant(session, self.tenant_id)
            repo = TaskRepository(session)
            return await repo.list_by_instance(instance_id, status=TaskStatus.ACTIVE)

    async def get_tasks_for_assignee(
        self,
        tenant_id: str,
        assignee: str,
        status: Optional[TaskStatus] = TaskStatus.ACTIVE
    ) -> List[Task]:
        """Get tasks assigned to user"""
        async with self.db_manager.get_session() as session:
            await self.db_manager.set_tenant(session, tenant_id)
            repo = TaskRepository(session)
            return await repo.list_by_assignee(tenant_id, assignee, status=status)

    async def assign_task(
        self,
        task_id: str,
        assignee: str
    ):
        """Assign task to user"""
        async with self.db_manager.get_session() as session:
            await self.db_manager.set_tenant(session, self.tenant_id)
            repo = TaskRepository(session)
            await repo.assign(task_id, assignee)

        logger.info(f"Assigned task {task_id} to {assignee}")

    async def update_task(
        self,
        task_id: str,
        data: Dict[str, Any]
    ):
        """Update task data (e.g., AI recommendations)"""
        async with self.db_manager.get_session() as session:
            await self.db_manager.set_tenant(session, self.tenant_id)
            repo = TaskRepository(session)

            # Update allowed fields
            if "ai_recommendations" in data:
                await repo.update_ai_recommendations(task_id, data["ai_recommendations"])

            if "ai_predicted_duration_hours" in data:
                await repo.update_ai_prediction(task_id, data["ai_predicted_duration_hours"])

    async def complete_task(
        self,
        task_id: str,
        variables: Dict[str, Any] = None,
        completed_by: Optional[str] = None
    ):
        """
        Complete task and advance process

        Args:
            task_id: Task ID
            variables: Variables to merge into process
            completed_by: User who completed the task
        """
        async with self.db_manager.get_session() as session:
            await self.db_manager.set_tenant(session, self.tenant_id)

            task_repo = TaskRepository(session)
            instance_repo = InstanceRepository(session)
            process_repo = ProcessRepository(session)

            # Get task
            task = await task_repo.get_by_id(task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found")

            # Get instance
            instance = await instance_repo.get_by_id(task.instance_id)
            if not instance:
                raise ValueError(f"Instance {task.instance_id} not found")

            # Complete task
            await task_repo.complete(task_id, variables=variables)

            # Update instance variables
            if variables:
                await instance_repo.update_variables(instance.id, variables, merge=True)

            # Remove from current activities
            await instance_repo.remove_activity(instance.id, task.activity_id)

            # Find next activities
            process = await process_repo.get_by_id(instance.process_id)
            root = BPMNParser.parse_bpmn_xml(process.bpmn_xml)
            current_element = BPMNParser.find_element_by_id(root, task.activity_id)

            if current_element is not None:
                next_elements = BPMNParser.get_next_elements(root, current_element)

                if not next_elements:
                    # No more tasks - process completed
                    await instance_repo.update_status(
                        instance.id,
                        ProcessStatus.COMPLETED,
                        completed_at=datetime.utcnow()
                    )

                    logger.info(f"Process instance {instance.id} completed")

                    await self._publish_event("bpmn.instance.completed", {
                        "instance_id": instance.id,
                        "process_id": instance.process_id,
                        "tenant_id": instance.tenant_id,
                        "variables": instance.variables
                    })
                else:
                    # Process next elements (tasks, gateways, events)
                    await self._process_next_elements(
                        session=session,
                        root=root,
                        instance=instance,
                        next_elements=next_elements,
                        incoming_flow_id=None  # TODO: track flow IDs
                    )

        logger.info(f"Completed task {task_id}")

        # Publish event
        await self._publish_event("bpmn.task.completed", {
            "task_id": task_id,
            "instance_id": instance.id,
            "activity_id": task.activity_id,
            "tenant_id": instance.tenant_id,
            "variables": variables,
            "completed_by": completed_by
        })

    async def terminate_instance(
        self,
        instance_id: str,
        reason: Optional[str] = None
    ):
        """Terminate process instance"""
        async with self.db_manager.get_session() as session:
            await self.db_manager.set_tenant(session, self.tenant_id)

            instance_repo = InstanceRepository(session)
            task_repo = TaskRepository(session)

            # Get instance
            instance = await instance_repo.get_by_id(instance_id)
            if not instance:
                raise ValueError(f"Instance {instance_id} not found")

            # Update instance status
            await instance_repo.update_status(
                instance_id,
                ProcessStatus.TERMINATED,
                completed_at=datetime.utcnow()
            )

            # Cancel all active tasks
            await task_repo.cancel_by_instance(instance_id)

        logger.info(f"Terminated instance {instance_id}: {reason}")

        await self._publish_event("bpmn.instance.terminated", {
            "instance_id": instance_id,
            "tenant_id": instance.tenant_id,
            "reason": reason
        })

    # ========== GATEWAY HANDLING (NEW!) ==========

    async def _process_next_elements(
        self,
        session,
        root: Any,
        instance: ProcessInstance,
        next_elements: List[Dict],
        incoming_flow_id: Optional[str] = None
    ):
        """
        Process next elements (tasks, gateways, events) with gateway support

        Args:
            session: Database session
            root: BPMN XML root
            instance: Process instance
            next_elements: List of next elements from parser
            incoming_flow_id: ID of incoming flow (for gateway join tracking)
        """
        instance_repo = InstanceRepository(session)

        for next_elem in next_elements:
            element = next_elem["element"]
            elem_id = next_elem["id"]
            elem_name = next_elem["name"]
            elem_type = next_elem["type"]

            # Check if it's END event
            if BPMNParser.is_end_event(element):
                await instance_repo.update_status(
                    instance.id,
                    ProcessStatus.COMPLETED,
                    completed_at=datetime.utcnow()
                )

                await self._publish_event("bpmn.instance.completed", {
                    "instance_id": instance.id,
                    "process_id": instance.process_id,
                    "tenant_id": instance.tenant_id,
                    "variables": instance.variables
                })

                logger.info(f"Instance {instance.id} completed (reached end event)")
                return

            # Check if it's GATEWAY
            if BPMNParser.is_gateway(element):
                await self._process_gateway(
                    session=session,
                    root=root,
                    instance=instance,
                    gateway_element=element,
                    gateway_id=elem_id,
                    incoming_flow_id=incoming_flow_id
                )
                return

            # Regular task - create it
            await self._create_task_persistent(
                session=session,
                instance_id=instance.id,
                activity_id=elem_id,
                name=elem_name,
                task_type=elem_type
            )

            await instance_repo.add_activity(instance.id, elem_id)

            logger.info(f"Created task {elem_name} ({elem_id}) for instance {instance.id}")

    async def _process_gateway(
        self,
        session,
        root: Any,
        instance: ProcessInstance,
        gateway_element: Any,
        gateway_id: str,
        incoming_flow_id: Optional[str] = None
    ):
        """
        Process gateway (XOR, AND, OR)

        Args:
            session: Database session
            root: BPMN XML root
            instance: Process instance
            gateway_element: Gateway XML element
            gateway_id: Gateway ID
            incoming_flow_id: Incoming flow ID (for join tracking)
        """
        gateway_type = self.gateway_evaluator.get_gateway_type(gateway_element)
        instance_repo = InstanceRepository(session)

        logger.info(f"Processing gateway {gateway_id} ({gateway_type})")

        # ===== EXCLUSIVE GATEWAY (XOR) =====
        if gateway_type == "exclusiveGateway":
            # Evaluate condition, select ONE flow
            selected_flow_id = await self.gateway_evaluator.evaluate_exclusive_gateway(
                root=root,
                gateway_element=gateway_element,
                instance_variables=instance.variables
            )

            if selected_flow_id:
                # Follow selected flow
                seq_flow = BPMNParser.find_sequence_flow(root, selected_flow_id)
                if seq_flow is not None:
                    target_ref = seq_flow.get("targetRef")
                    if target_ref:
                        target_element = BPMNParser.find_element_by_id(root, target_ref)
                        if target_element is not None:
                            # Process target element
                            await self._process_next_elements(
                                session=session,
                                root=root,
                                instance=instance,
                                next_elements=[{
                                    "element": target_element,
                                    "id": target_ref,
                                    "name": target_element.get("name", target_ref),
                                    "type": BPMNParser.get_element_type(target_element)
                                }],
                                incoming_flow_id=selected_flow_id
                            )
            else:
                logger.warning(f"No flow selected at Exclusive Gateway {gateway_id}")

        # ===== PARALLEL GATEWAY (AND) =====
        elif gateway_type == "parallelGateway":
            is_fork = self.gateway_evaluator.is_gateway_fork(gateway_element)
            is_join = self.gateway_evaluator.is_gateway_join(gateway_element)

            if is_fork:
                # FORK: Take ALL outgoing flows
                flow_ids = await self.gateway_evaluator.evaluate_parallel_gateway_fork(
                    gateway_element=gateway_element
                )

                # Create tasks for ALL flows
                for flow_id in flow_ids:
                    seq_flow = BPMNParser.find_sequence_flow(root, flow_id)
                    if seq_flow is not None:
                        target_ref = seq_flow.get("targetRef")
                        if target_ref:
                            target_element = BPMNParser.find_element_by_id(root, target_ref)
                            if target_element is not None:
                                await self._process_next_elements(
                                    session=session,
                                    root=root,
                                    instance=instance,
                                    next_elements=[{
                                        "element": target_element,
                                        "id": target_ref,
                                        "name": target_element.get("name", target_ref),
                                        "type": BPMNParser.get_element_type(target_element)
                                    }],
                                    incoming_flow_id=flow_id
                                )

            elif is_join:
                # JOIN: Wait for ALL incoming flows
                # Track which flows have completed
                gateway_state = instance.gateway_state.get(gateway_id, {
                    "incoming_completed": [],
                    "incoming_total": BPMNParser.get_incoming_flows(gateway_element)
                })

                # Add incoming flow to completed list
                if incoming_flow_id and incoming_flow_id not in gateway_state["incoming_completed"]:
                    gateway_state["incoming_completed"].append(incoming_flow_id)

                # Update instance gateway_state
                instance.gateway_state[gateway_id] = gateway_state
                await instance_repo.update(instance.id, {"gateway_state": instance.gateway_state})

                # Check if ALL incoming flows completed
                can_proceed = await self.gateway_evaluator.check_parallel_gateway_join(
                    gateway_element=gateway_element,
                    completed_incoming_flows=gateway_state["incoming_completed"]
                )

                if can_proceed:
                    # All flows completed - proceed to next element
                    outgoing_flows = BPMNParser.get_outgoing_flows(gateway_element)
                    if outgoing_flows:
                        flow_id = outgoing_flows[0]  # Should be only 1 for join
                        seq_flow = BPMNParser.find_sequence_flow(root, flow_id)
                        if seq_flow is not None:
                            target_ref = seq_flow.get("targetRef")
                            if target_ref:
                                target_element = BPMNParser.find_element_by_id(root, target_ref)
                                if target_element is not None:
                                    await self._process_next_elements(
                                        session=session,
                                        root=root,
                                        instance=instance,
                                        next_elements=[{
                                            "element": target_element,
                                            "id": target_ref,
                                            "name": target_element.get("name", target_ref),
                                            "type": BPMNParser.get_element_type(target_element)
                                        }],
                                        incoming_flow_id=flow_id
                                    )

                    # Clear gateway state
                    del instance.gateway_state[gateway_id]
                    await instance_repo.update(instance.id, {"gateway_state": instance.gateway_state})
                else:
                    logger.info(
                        f"Parallel Gateway JOIN {gateway_id}: "
                        f"Waiting for {len(gateway_state['incoming_total']) - len(gateway_state['incoming_completed'])} more flows"
                    )

        # ===== INCLUSIVE GATEWAY (OR) =====
        elif gateway_type == "inclusiveGateway":
            # Evaluate conditions, select ALL matching flows
            selected_flow_ids = await self.gateway_evaluator.evaluate_inclusive_gateway(
                root=root,
                gateway_element=gateway_element,
                instance_variables=instance.variables
            )

            # Create tasks for ALL selected flows
            for flow_id in selected_flow_ids:
                seq_flow = BPMNParser.find_sequence_flow(root, flow_id)
                if seq_flow is not None:
                    target_ref = seq_flow.get("targetRef")
                    if target_ref:
                        target_element = BPMNParser.find_element_by_id(root, target_ref)
                        if target_element is not None:
                            await self._process_next_elements(
                                session=session,
                                root=root,
                                instance=instance,
                                next_elements=[{
                                    "element": target_element,
                                    "id": target_ref,
                                    "name": target_element.get("name", target_ref),
                                    "type": BPMNParser.get_element_type(target_element)
                                }],
                                incoming_flow_id=flow_id
                            )

        else:
            logger.warning(f"Unknown gateway type: {gateway_type}")

    # ========== EXISTING HELPER METHODS ==========
