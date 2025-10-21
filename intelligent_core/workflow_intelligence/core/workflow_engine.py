"""
 WORKFLOW ENGINE - Универсальный движок для любых workflows

Это ЯДРО Workflow Intelligence Platform.
Управляет state machines, событиями, валидацией и контекстом.

Philosophy: Don't reinvent - enhance existing state machines with intelligence.
"""

from typing import Dict, List, Optional, Any, Callable, Protocol
from datetime import datetime
from enum import Enum
import asyncio
import logging
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


# ============================================================================
# PROTOCOLS & TYPES
# ============================================================================

class StateProtocol(Protocol):
    """Protocol для state enums"""
    value: str


class StateMachineProtocol(Protocol):
    """Protocol для существующих state machines (например BIAWorkflowEngine)"""

    @staticmethod
    def can_transition(from_state: str, action: str) -> bool:
        """Проверка возможности перехода"""
        ...

    @staticmethod
    def get_next_state(from_state: str, action: str) -> Optional[str]:
        """Получить следующее состояние"""
        ...

    @staticmethod
    def get_allowed_actions(state: str) -> List[str]:
        """Получить разрешенные действия"""
        ...

    @staticmethod
    def validate_transition(data: Dict, action: str) -> tuple[bool, Optional[str]]:
        """Валидация перехода"""
        ...


# ============================================================================
# EVENTS
# ============================================================================

@dataclass
class WorkflowEvent:
    """Событие в workflow"""
    event_type: str
    workflow_id: str
    module: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "workflow_id": self.workflow_id,
            "module": self.module,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "metadata": self.metadata
        }


class EventBus:
    """Simple in-memory event bus для workflow events"""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_pattern: str, handler: Callable):
        """
        Подписка на события

        event_pattern может быть:
        - "workflow.stage.changed" - точное совпадение
        - "workflow.*" - любое событие начинающееся с workflow
        - "*" - все события
        """
        self._subscribers[event_pattern].append(handler)

    async def publish(self, event: WorkflowEvent):
        """Публикация события"""
        # Точное совпадение
        for handler in self._subscribers.get(event.event_type, []):
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Event handler error: {e}", exc_info=True)

        # Wildcard patterns
        for pattern, handlers in self._subscribers.items():
            if "*" in pattern:
                if pattern == "*" or event.event_type.startswith(pattern.replace("*", "")):
                    for handler in handlers:
                        try:
                            await handler(event)
                        except Exception as e:
                            logger.error(f"Event handler error: {e}", exc_info=True)

        # Логируем все события
        logger.info(
            f"Event: {event.event_type}",
            extra={
                "workflow_id": event.workflow_id,
                "module": event.module,
                "data": event.data
            }
        )


# Global event bus instance
event_bus = EventBus()


# ============================================================================
# WORKFLOW CONTEXT
# ============================================================================

@dataclass
class WorkflowContext:
    """Полный контекст workflow для AI Advisor"""

    # Базовая информация
    workflow_id: str
    module: str
    current_stage: str
    current_stage_label: str

    # Прогресс
    progress_percentage: float
    started_at: Optional[datetime]
    updated_at: datetime
    estimated_completion: Optional[datetime] = None

    # Данные
    current_stage_data: Dict[str, Any] = field(default_factory=dict)
    workflow_data: Dict[str, Any] = field(default_factory=dict)

    # Что не хватает
    gaps: List[Dict[str, Any]] = field(default_factory=list)
    issues: List[Dict[str, Any]] = field(default_factory=list)

    # Что можно делать
    available_actions: List[Dict[str, Any]] = field(default_factory=list)
    next_stage: Optional[str] = None
    can_proceed_to_next_stage: bool = False

    # История
    completed_steps: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dict for serialization"""
        return {
            "workflow_id": self.workflow_id,
            "module": self.module,
            "current_stage": self.current_stage,
            "current_stage_label": self.current_stage_label,
            "progress_percentage": self.progress_percentage,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "updated_at": self.updated_at.isoformat(),
            "estimated_completion": self.estimated_completion.isoformat() if self.estimated_completion else None,
            "current_stage_data": self.current_stage_data,
            "workflow_data": self.workflow_data,
            "gaps": self.gaps,
            "issues": self.issues,
            "available_actions": self.available_actions,
            "next_stage": self.next_stage,
            "can_proceed_to_next_stage": self.can_proceed_to_next_stage,
            "completed_steps": self.completed_steps,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "metadata": self.metadata
        }


# ============================================================================
# WORKFLOW ENGINE
# ============================================================================

class WorkflowEngine:
    """
    Универсальный Workflow Engine

    Оборачивает существующие state machines и добавляет:
    - Event publishing
    - Context generation для AI
    - Gap analysis
    - Action validation
    - Audit trail
    """

    def __init__(
        self,
        module: str,
        state_machine: StateMachineProtocol,
        storage_adapter,  # Адаптер для хранения (DB, file, etc)
        workflow_definition: Optional[Dict] = None,
        event_bus: EventBus = event_bus
    ):
        """
        Args:
            module: Название модуля (bia, risk, planning, etc)
            state_machine: Существующий state machine (например BIAWorkflowEngine)
            storage_adapter: Адаптер для хранения данных
            workflow_definition: YAML определение workflow (для governance)
            event_bus: Event bus для публикации событий
        """
        self.module = module
        self.state_machine = state_machine
        self.storage = storage_adapter
        self.workflow_definition = workflow_definition or {}
        self.event_bus = event_bus

        logger.info(f"Workflow Engine initialized for module: {module}")

    # ========================================================================
    # CORE WORKFLOW OPERATIONS
    # ========================================================================

    async def start(self, workflow_id: str, initial_data: Dict = None, **kwargs) -> Dict:
        """
        Запустить новый workflow

        Args:
            workflow_id: Уникальный ID workflow
            initial_data: Начальные данные
            **kwargs: tenant_id, user_id, etc

        Returns:
            Начальный context
        """
        initial_data = initial_data or {}

        # Создать запись в storage
        workflow_record = {
            "workflow_id": workflow_id,
            "module": self.module,
            "current_stage": self._get_initial_state(),
            "workflow_data": initial_data,
            "started_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "completed_steps": [],
            "tenant_id": kwargs.get("tenant_id"),
            "user_id": kwargs.get("user_id"),
            "metadata": kwargs.get("metadata", {})
        }

        await self.storage.create_workflow(workflow_record)

        # Публикуем событие
        await self.event_bus.publish(WorkflowEvent(
            event_type=f"{self.module}.workflow.started",
            workflow_id=workflow_id,
            module=self.module,
            data={"initial_state": workflow_record["current_stage"]},
            metadata={"tenant_id": kwargs.get("tenant_id")}
        ))

        logger.info(f"Workflow started: {workflow_id} ({self.module})")

        return await self.get_context(workflow_id)

    async def execute_action(
        self,
        workflow_id: str,
        action: str,
        action_data: Dict = None,
        **kwargs
    ) -> Dict:
        """
        Выполнить действие в workflow

        Args:
            workflow_id: ID workflow
            action: Название действия (например "suggest_rto")
            action_data: Данные для действия
            **kwargs: user_id, etc

        Returns:
            Updated context
        """
        action_data = action_data or {}

        # Загрузить текущее состояние
        workflow = await self.storage.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")

        current_state = workflow["current_stage"]

        # Проверить можно ли выполнить действие
        can_transition = self.state_machine.can_transition(current_state, action)
        if not can_transition:
            raise ValueError(
                f"Action '{action}' not allowed in state '{current_state}'. "
                f"Allowed actions: {self.state_machine.get_allowed_actions(current_state)}"
            )

        # Валидация (если есть в state machine)
        if hasattr(self.state_machine, 'validate_transition'):
            valid, error = self.state_machine.validate_transition(
                {**workflow["workflow_data"], **action_data},
                action
            )
            if not valid:
                raise ValueError(f"Validation failed: {error}")

        # Получить следующее состояние
        next_state = self.state_machine.get_next_state(current_state, action)

        # Обновить данные
        updated_data = {**workflow["workflow_data"], **action_data}
        workflow["workflow_data"] = updated_data
        workflow["current_stage"] = next_state if next_state else current_state
        workflow["updated_at"] = datetime.utcnow()

        # Добавить в историю
        workflow["completed_steps"].append({
            "action": action,
            "from_state": current_state,
            "to_state": next_state if next_state else current_state,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": kwargs.get("user_id"),
            "data": action_data
        })

        # Сохранить
        await self.storage.update_workflow(workflow_id, workflow)

        # Публикуем события
        await self.event_bus.publish(WorkflowEvent(
            event_type=f"{self.module}.action.executed",
            workflow_id=workflow_id,
            module=self.module,
            data={
                "action": action,
                "from_state": current_state,
                "to_state": next_state if next_state else current_state
            },
            metadata={"user_id": kwargs.get("user_id")}
        ))

        if next_state and next_state != current_state:
            await self.event_bus.publish(WorkflowEvent(
                event_type=f"{self.module}.stage.changed",
                workflow_id=workflow_id,
                module=self.module,
                data={
                    "from_state": current_state,
                    "to_state": next_state,
                    "action": action
                }
            ))

        logger.info(
            f"Action executed: {action} on {workflow_id}",
            extra={
                "from_state": current_state,
                "to_state": next_state,
                "module": self.module
            }
        )

        return await self.get_context(workflow_id)

    async def complete(self, workflow_id: str, **kwargs) -> Dict:
        """Завершить workflow"""

        workflow = await self.storage.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow["completed_at"] = datetime.utcnow()
        workflow["updated_at"] = datetime.utcnow()

        await self.storage.update_workflow(workflow_id, workflow)

        # Событие завершения - ВАЖНО для Case Library!
        await self.event_bus.publish(WorkflowEvent(
            event_type=f"{self.module}.workflow.completed",
            workflow_id=workflow_id,
            module=self.module,
            data={
                "duration_seconds": (
                    workflow["completed_at"] - workflow["started_at"]
                ).total_seconds(),
                "total_steps": len(workflow["completed_steps"])
            }
        ))

        logger.info(f"Workflow completed: {workflow_id}")

        return await self.get_context(workflow_id)

    # ========================================================================
    # CONTEXT GENERATION (для AI Advisor)
    # ========================================================================

    async def get_context(self, workflow_id: str) -> WorkflowContext:
        """
        Получить ПОЛНЫЙ контекст workflow для AI Advisor

        Это главный метод который даёт AI всю нужную информацию.
        """
        workflow = await self.storage.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")

        current_state = workflow["current_stage"]

        # Прогресс
        progress = self._calculate_progress(current_state)

        # Gaps (что не хватает)
        gaps = await self._identify_gaps(workflow)

        # Issues (проблемы)
        issues = await self._identify_issues(workflow)

        # Available actions
        available_actions = self._get_available_actions(current_state, workflow)

        # Можем ли двигаться дальше
        can_proceed, next_stage = self._can_proceed_to_next_stage(
            current_state,
            gaps,
            workflow
        )

        context = WorkflowContext(
            workflow_id=workflow_id,
            module=self.module,
            current_stage=current_state,
            current_stage_label=self._get_stage_label(current_state),
            progress_percentage=progress,
            started_at=workflow.get("started_at"),
            updated_at=workflow["updated_at"],
            estimated_completion=self._estimate_completion(workflow, progress),
            current_stage_data=self._extract_stage_data(workflow, current_state),
            workflow_data=workflow["workflow_data"],
            gaps=gaps,
            issues=issues,
            available_actions=available_actions,
            next_stage=next_stage,
            can_proceed_to_next_stage=can_proceed,
            completed_steps=workflow["completed_steps"],
            tenant_id=workflow.get("tenant_id"),
            user_id=workflow.get("user_id"),
            metadata=workflow.get("metadata", {})
        )

        return context

    # ========================================================================
    # INTERNAL HELPERS
    # ========================================================================

    def _get_initial_state(self) -> str:
        """Получить начальное состояние"""
        # Предполагаем что в state machine есть INITIAL или подобное
        if hasattr(self.state_machine, 'INITIAL'):
            return self.state_machine.INITIAL.value
        # Или просто возвращаем первое состояние из transitions
        return "initial"

    def _calculate_progress(self, current_state: str) -> float:
        """Рассчитать прогресс (0-100)"""
        # Если у state machine есть метод get_completion_percentage
        if hasattr(self.state_machine, 'get_completion_percentage'):
            return self.state_machine.get_completion_percentage(current_state) * 100

        # Иначе примерная оценка на основе workflow definition
        if self.workflow_definition and "stages" in self.workflow_definition:
            stages = self.workflow_definition["stages"]
            try:
                current_index = stages.index(current_state)
                return (current_index / len(stages)) * 100
            except ValueError:
                return 0.0

        return 0.0

    async def _identify_gaps(self, workflow: Dict) -> List[Dict]:
        """
        Найти что не хватает для продолжения

        Returns:
            [{"type": "missing_field", "field": "rto_hours", "message": "...", "severity": "high"}]
        """
        gaps = []
        current_state = workflow["current_stage"]

        # Если у state machine есть метод get_required_fields
        if hasattr(self.state_machine, 'get_required_fields'):
            required_fields = self.state_machine.get_required_fields(current_state)
            workflow_data = workflow["workflow_data"]

            for field in required_fields:
                if not workflow_data.get(field):
                    gaps.append({
                        "type": "missing_field",
                        "field": field,
                        "message": f"Required field '{field}' is missing",
                        "severity": "high"
                    })

        # Кастомная логика из workflow_definition
        if self.workflow_definition:
            custom_gaps = await self._check_custom_gaps(workflow)
            gaps.extend(custom_gaps)

        return gaps

    async def _check_custom_gaps(self, workflow: Dict) -> List[Dict]:
        """Проверить кастомные gaps из workflow definition"""
        gaps = []

        # Например, проверка минимального количества элементов
        # if workflow_definition["requirements"]["min_processes"] > len(workflow_data["processes"])

        # TODO: Реализовать на основе workflow_definition YAML

        return gaps

    async def _identify_issues(self, workflow: Dict) -> List[Dict]:
        """
        Найти проблемы (warnings, не критичные)

        Returns:
            [{"type": "low_quality", "message": "...", "severity": "medium"}]
        """
        issues = []

        # Проверки качества данных
        workflow_data = workflow["workflow_data"]

        # Пример: если есть processes, проверить их качество
        if "processes" in workflow_data:
            for proc in workflow_data["processes"]:
                if not proc.get("description"):
                    issues.append({
                        "type": "missing_optional_field",
                        "message": f"Process '{proc.get('name')}' missing description",
                        "severity": "low"
                    })

        # Проверка прогресса
        if len(workflow["completed_steps"]) == 0:
            duration = datetime.utcnow() - workflow["started_at"]
            if duration.days > 7:
                issues.append({
                    "type": "stale_workflow",
                    "message": f"Workflow inactive for {duration.days} days",
                    "severity": "medium"
                })

        return issues

    def _get_available_actions(self, current_state: str, workflow: Dict) -> List[Dict]:
        """
        Получить доступные действия

        Returns:
            [{"id": "suggest_rto", "label": "Suggest RTO/RPO", "type": "ai", "requires_ai": True}]
        """
        # Получить из state machine
        actions = self.state_machine.get_allowed_actions(current_state)

        # Обогатить metadata из workflow_definition
        enriched_actions = []

        for action in actions:
            action_config = self._get_action_config(action)

            enriched_actions.append({
                "id": action,
                "label": action_config.get("label", action.replace("_", " ").title()),
                "type": action_config.get("type", "standard"),
                "requires_ai": action_config.get("requires_ai", False),
                "description": action_config.get("description", ""),
                "icon": action_config.get("icon", "")
            })

        return enriched_actions

    def _get_action_config(self, action: str) -> Dict:
        """Получить конфигурацию действия из workflow_definition"""
        if self.workflow_definition and "actions" in self.workflow_definition:
            return self.workflow_definition["actions"].get(action, {})
        return {}

    def _can_proceed_to_next_stage(
        self,
        current_state: str,
        gaps: List[Dict],
        workflow: Dict
    ) -> tuple[bool, Optional[str]]:
        """
        Проверить можно ли двигаться на следующую стадию

        Returns:
            (can_proceed, next_stage)
        """
        # Если есть критичные gaps, нельзя
        critical_gaps = [g for g in gaps if g.get("severity") == "high"]
        if critical_gaps:
            return False, None

        # Получить возможные следующие стадии
        allowed_actions = self.state_machine.get_allowed_actions(current_state)

        # Найти "transition" действия (не параллельные)
        for action in allowed_actions:
            next_state = self.state_machine.get_next_state(current_state, action)
            if next_state and next_state != current_state:
                # Это transition action
                return True, next_state

        return False, None

    def _get_stage_label(self, stage: str) -> str:
        """Человекочитаемое название стадии"""
        if self.workflow_definition and "stages" in self.workflow_definition:
            stage_config = self.workflow_definition["stages"].get(stage, {})
            return stage_config.get("label", stage.replace("_", " ").title())

        return stage.replace("_", " ").title()

    def _extract_stage_data(self, workflow: Dict, stage: str) -> Dict:
        """Извлечь данные относящиеся к текущей стадии"""
        # TODO: Умная фильтрация данных по стадии
        # Пока возвращаем всё
        return workflow["workflow_data"]

    def _estimate_completion(
        self,
        workflow: Dict,
        current_progress: float
    ) -> Optional[datetime]:
        """Оценка времени завершения"""
        if current_progress == 0:
            return None

        started = workflow.get("started_at")
        if not started:
            return None

        elapsed = datetime.utcnow() - started
        estimated_total = elapsed / (current_progress / 100)

        return started + estimated_total

    # ========================================================================
    # CLASS METHOD: Create from existing state machine
    # ========================================================================

    @classmethod
    def from_existing_state_machine(
        cls,
        module: str,
        state_machine: StateMachineProtocol,
        storage_adapter,
        workflow_definition: Optional[Dict] = None
    ) -> "WorkflowEngine":
        """
        Создать Workflow Engine из существующего state machine

        Example:
            from bia.workflows.state_machine import BIAWorkflowEngine

            workflow = WorkflowEngine.from_existing_state_machine(
                module="bia",
                state_machine=BIAWorkflowEngine,
                storage_adapter=storage
            )
        """
        return cls(
            module=module,
            state_machine=state_machine,
            storage_adapter=storage_adapter,
            workflow_definition=workflow_definition
        )


# ============================================================================
# STORAGE ADAPTER (Interface)
# ============================================================================

class WorkflowStorageAdapter(Protocol):
    """Interface для storage адаптеров"""

    async def create_workflow(self, workflow: Dict) -> Dict:
        """Создать workflow"""
        ...

    async def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """Получить workflow по ID"""
        ...

    async def update_workflow(self, workflow_id: str, workflow: Dict) -> Dict:
        """Обновить workflow"""
        ...

    async def list_workflows(
        self,
        module: Optional[str] = None,
        tenant_id: Optional[str] = None,
        **filters
    ) -> List[Dict]:
        """Список workflows с фильтрами"""
        ...


# ============================================================================
# IN-MEMORY STORAGE (для тестирования)
# ============================================================================

class InMemoryStorageAdapter:
    """In-memory storage для тестирования"""

    def __init__(self):
        self._workflows: Dict[str, Dict] = {}

    async def create_workflow(self, workflow: Dict) -> Dict:
        workflow_id = workflow["workflow_id"]
        self._workflows[workflow_id] = workflow
        return workflow

    async def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        return self._workflows.get(workflow_id)

    async def update_workflow(self, workflow_id: str, workflow: Dict) -> Dict:
        self._workflows[workflow_id] = workflow
        return workflow

    async def list_workflows(
        self,
        module: Optional[str] = None,
        tenant_id: Optional[str] = None,
        **filters
    ) -> List[Dict]:
        workflows = list(self._workflows.values())

        if module:
            workflows = [w for w in workflows if w.get("module") == module]

        if tenant_id:
            workflows = [w for w in workflows if w.get("tenant_id") == tenant_id]

        return workflows
