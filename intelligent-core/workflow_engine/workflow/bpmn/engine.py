"""
BPMN Engine

Orchestrates BPMN process execution
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

logger = logging.getLogger(__name__)


class BPMNEngine:
    """
    BPMN 2.0 Process Execution Engine

    Manages:
    - Process deployment
    - Instance creation and execution
    - Task lifecycle
    - Event publishing

    TODO Phase 2: Replace in-memory storage with PostgreSQL repositories
    """

    def __init__(self, use_persistence: bool = False):
        """
        Initialize BPMN Engine

        Args:
            use_persistence: If True, use PostgreSQL (Phase 2)
                           If False, use in-memory (Phase 1 - current)
        """
        self.use_persistence = use_persistence

        # Phase 1: In-memory storage (will be replaced in Phase 2)
        self.processes: Dict[str, BPMNProcess] = {}
        self.instances: Dict[str, ProcessInstance] = {}
        self.tasks: Dict[str, Task] = {}

        # Event handlers (for integration with Workflow Intelligence)
        self._event_handlers: Dict[str, List[Callable]] = {}

        logger.info(f"BPMNEngine initialized (persistence={use_persistence})")

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
        version: str = "1.0"
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

        Returns:
            str: Process ID

        Raises:
            ValueError: If BPMN XML is invalid
        """
        # Validate BPMN XML
        BPMNParser.validate_bpmn_xml(bpmn_xml)

        # Create process
        process = BPMNProcess(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            module=module,
            name=name,
            description=description,
            bpmn_xml=bpmn_xml,
            version=version,
            created_at=datetime.utcnow()
        )

        # Save (in-memory for now, PostgreSQL in Phase 2)
        self.processes[process.id] = process

        logger.info(f"Deployed BPMN process {process.id}: {process.name}")

        # Publish event
        await self._publish_event("bpmn.process.deployed", {
            "process_id": process.id,
            "process_name": process.name,
            "tenant_id": tenant_id,
            "module": module,
            "version": version
        })

        return process.id

    async def get_process(self, process_id: str) -> Optional[BPMNProcess]:
        """Get process by ID"""
        return self.processes.get(process_id)

    async def list_processes(
        self,
        tenant_id: str,
        module: Optional[str] = None
    ) -> List[BPMNProcess]:
        """List processes for tenant"""
        processes = [
            p for p in self.processes.values()
            if p.tenant_id == tenant_id
        ]

        if module:
            processes = [p for p in processes if p.module == module]

        return processes

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
        # Get process
        process = await self.get_process(process_id)
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

        # Parse BPMN and create initial tasks
        root = BPMNParser.parse_bpmn_xml(process.bpmn_xml)
        start_events = BPMNParser.find_start_events(root)

        if start_events:
            # Find tasks connected to start events
            for start_event in start_events:
                next_elements = BPMNParser.get_next_elements(root, start_event)

                for next_elem in next_elements:
                    await self._create_task(
                        instance_id=instance.id,
                        activity_id=next_elem["id"],
                        name=next_elem["name"],
                        task_type=next_elem["type"]
                    )

                    instance.current_activities.append(next_elem["id"])

        # Save instance
        self.instances[instance.id] = instance

        logger.info(f"Started process instance {instance.id} for process {process_id}")

        # Publish event
        await self._publish_event("bpmn.instance.started", {
            "instance_id": instance.id,
            "process_id": process_id,
            "tenant_id": tenant_id,
            "variables": variables,
            "started_by": started_by
        })

        return instance.id

    async def get_instance(self, instance_id: str) -> Optional[ProcessInstance]:
        """Get process instance by ID"""
        return self.instances.get(instance_id)

    async def has_instance(self, instance_id: str) -> bool:
        """Check if instance exists"""
        return instance_id in self.instances

    async def list_instances(
        self,
        tenant_id: str,
        status: Optional[ProcessStatus] = None
    ) -> List[ProcessInstance]:
        """List instances for tenant"""
        instances = [
            i for i in self.instances.values()
            if i.tenant_id == tenant_id
        ]

        if status:
            instances = [i for i in instances if i.status == status]

        return instances

    async def update_variables(
        self,
        instance_id: str,
        variables: Dict[str, Any]
    ):
        """Update process instance variables"""
        instance = await self.get_instance(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")

        instance.variables.update(variables)

    # ========== TASK MANAGEMENT ==========

    async def _create_task(
        self,
        instance_id: str,
        activity_id: str,
        name: str,
        task_type: str
    ) -> str:
        """Create new task (internal)"""
        task = Task(
            id=str(uuid.uuid4()),
            process_instance_id=instance_id,
            activity_id=activity_id,
            name=name,
            task_type=TaskType[task_type] if task_type in TaskType.__members__ else TaskType.USER_TASK,
            created_at=datetime.utcnow()
        )

        self.tasks[task.id] = task

        logger.info(f"Created task {task.id}: {task.name}")

        # Publish event
        instance = await self.get_instance(instance_id)
        await self._publish_event("bpmn.task.created", {
            "task_id": task.id,
            "instance_id": instance_id,
            "activity_id": activity_id,
            "name": name,
            "tenant_id": instance.tenant_id if instance else None
        })

        return task.id

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)

    async def get_active_tasks(
        self,
        instance_id: str
    ) -> List[Task]:
        """Get active tasks for instance"""
        return [
            t for t in self.tasks.values()
            if t.instance_id == instance_id and t.status == TaskStatus.ACTIVE
        ]

    async def get_tasks_for_assignee(
        self,
        tenant_id: str,
        assignee: str,
        status: Optional[TaskStatus] = TaskStatus.ACTIVE
    ) -> List[Task]:
        """Get tasks assigned to user"""
        tasks = []
        for task in self.tasks.values():
            if task.assignee == assignee:
                instance = await self.get_instance(task.instance_id)
                if instance and instance.tenant_id == tenant_id:
                    if status is None or task.status == status:
                        tasks.append(task)
        return tasks

    async def assign_task(
        self,
        task_id: str,
        assignee: str
    ):
        """Assign task to user"""
        task = await self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.assignee = assignee
        logger.info(f"Assigned task {task_id} to {assignee}")

    async def update_task(
        self,
        task_id: str,
        data: Dict[str, Any]
    ):
        """Update task data (e.g., AI recommendations)"""
        task = await self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Update allowed fields
        if "ai_recommendations" in data:
            task.ai_recommendations = data["ai_recommendations"]
        if "ai_predicted_duration_hours" in data:
            task.ai_predicted_duration_hours = data["ai_predicted_duration_hours"]

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
        task = await self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        instance = await self.get_instance(task.instance_id)
        if not instance:
            raise ValueError(f"Instance {task.instance_id} not found")

        # Update task
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.variables.update(variables or {})

        # Update instance variables
        instance.variables.update(variables or {})

        # Remove from current activities
        if task.activity_id in instance.current_activities:
            instance.current_activities.remove(task.activity_id)

        # Find next activities
        process = await self.get_process(instance.process_id)
        root = BPMNParser.parse_bpmn_xml(process.bpmn_xml)
        current_element = BPMNParser.find_element_by_id(root, task.activity_id)

        if current_element is not None:
            next_elements = BPMNParser.get_next_elements(root, current_element)

            if not next_elements:
                # No more tasks - process completed
                instance.status = ProcessStatus.COMPLETED
                instance.completed_at = datetime.utcnow()

                logger.info(f"Process instance {instance.id} completed")

                await self._publish_event("bpmn.instance.completed", {
                    "instance_id": instance.id,
                    "process_id": instance.process_id,
                    "tenant_id": instance.tenant_id,
                    "variables": instance.variables
                })
            else:
                # Create next tasks
                for next_elem in next_elements:
                    # Check if it's end event
                    if BPMNParser.is_end_event(next_elem["element"]):
                        instance.status = ProcessStatus.COMPLETED
                        instance.completed_at = datetime.utcnow()

                        await self._publish_event("bpmn.instance.completed", {
                            "instance_id": instance.id,
                            "process_id": instance.process_id,
                            "tenant_id": instance.tenant_id,
                            "variables": instance.variables
                        })
                    else:
                        # Create new task
                        await self._create_task(
                            instance_id=instance.id,
                            activity_id=next_elem["id"],
                            name=next_elem["name"],
                            task_type=next_elem["type"]
                        )

                        instance.current_activities.append(next_elem["id"])

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
        instance = await self.get_instance(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")

        instance.status = ProcessStatus.TERMINATED
        instance.completed_at = datetime.utcnow()

        # Cancel all active tasks
        for task in await self.get_active_tasks(instance_id):
            task.status = TaskStatus.CANCELLED

        logger.info(f"Terminated instance {instance_id}: {reason}")

        await self._publish_event("bpmn.instance.terminated", {
            "instance_id": instance_id,
            "tenant_id": instance.tenant_id,
            "reason": reason
        })
