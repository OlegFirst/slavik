"""
Base Workflow Engine

Базовый класс для всех воркфлоу в compliance модуле.
Обеспечивает:
- Управление состояниями (state machine)
- Валидацию переходов
- Публикацию событий
- Аудит-лог
- Guards (условия перехода)
"""

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass

from shared.audit import AuditLogger, AuditAction, AuditCategory

logger = logging.getLogger(__name__)


@dataclass
class WorkflowTransition:
    """Описание разрешенного перехода между состояниями"""
    from_state: Enum
    to_state: Enum
    event_name: str  # Имя события EventBus
    required_fields: List[str] = None  # Обязательные поля в metadata
    guards: List[str] = None  # Имена функций-guards для проверки
    actions: List[str] = None  # Имена функций-actions для выполнения
    description: str = ""

    def __post_init__(self):
        if self.required_fields is None:
            self.required_fields = []
        if self.guards is None:
            self.guards = []
        if self.actions is None:
            self.actions = []


@dataclass
class WorkflowGuard:
    """Guard - условие для разрешения перехода"""
    name: str
    check: Callable
    error_message: str


class WorkflowError(Exception):
    """Ошибка выполнения воркфлоу"""
    pass


class BaseWorkflow(ABC):
    """
    Базовый класс для всех воркфлоу

    Субклассы должны определить:
    - state_enum: Enum с состояниями
    - event_prefix: префикс для событий (например, "evidence")
    - transitions: словарь разрешенных переходов
    - guards: словарь guards-функций
    - actions: словарь actions-функций
    """

    def __init__(self, eventbus_client, repository, config=None, audit_logger: Optional[AuditLogger] = None):
        """
        Args:
            eventbus_client: Клиент для публикации событий
            repository: Репозиторий для работы с БД
            config: Опциональная конфигурация
            audit_logger: Audit logger for ISO 22301 compliance
        """
        self.eventbus = eventbus_client
        self.repository = repository
        self.config = config or {}
        self.audit = audit_logger

        # Инициализация субкласса
        self.state_enum = self._get_state_enum()
        self.event_prefix = self._get_event_prefix()
        self.transitions = self._define_transitions()
        self.guards = self._define_guards()
        self.actions = self._define_actions()

        # Валидация конфигурации
        self._validate_workflow_definition()

    @abstractmethod
    def _get_state_enum(self) -> type:
        """Вернуть Enum класс с состояниями"""
        pass

    @abstractmethod
    def _get_event_prefix(self) -> str:
        """Вернуть префикс для событий (например, 'evidence')"""
        pass

    @abstractmethod
    def _define_transitions(self) -> List[WorkflowTransition]:
        """Определить разрешенные переходы"""
        pass

    @abstractmethod
    def _define_guards(self) -> Dict[str, WorkflowGuard]:
        """Определить guards для проверки условий"""
        pass

    @abstractmethod
    def _define_actions(self) -> Dict[str, Callable]:
        """Определить actions для выполнения при переходах"""
        pass

    def _validate_workflow_definition(self):
        """Валидация корректности определения воркфлоу"""
        # Проверка, что все guards в transitions существуют
        for transition in self.transitions:
            for guard_name in transition.guards:
                if guard_name not in self.guards:
                    raise ValueError(f"Guard '{guard_name}' не определен в воркфлоу")

            for action_name in transition.actions:
                if action_name not in self.actions:
                    raise ValueError(f"Action '{action_name}' не определен в воркфлоу")

        logger.info(f"Workflow '{self.event_prefix}' validated successfully")

    def _find_transition(self, from_state: Enum, to_state: Enum) -> Optional[WorkflowTransition]:
        """Найти определение перехода"""
        for transition in self.transitions:
            if transition.from_state == from_state and transition.to_state == to_state:
                return transition
        return None

    async def can_transition(
        self,
        entity_id: str,
        from_state: Enum,
        to_state: Enum,
        actor_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Проверить, возможен ли переход

        Returns:
            (can_transition: bool, error_message: Optional[str])
        """
        metadata = metadata or {}

        # 1. Проверить, что переход определен
        transition = self._find_transition(from_state, to_state)
        if not transition:
            return False, f"Переход {from_state.value} → {to_state.value} не разрешен"

        # 2. Проверить обязательные поля
        for field in transition.required_fields:
            if field not in metadata:
                return False, f"Обязательное поле '{field}' отсутствует в metadata"

        # 3. Проверить guards
        for guard_name in transition.guards:
            guard = self.guards[guard_name]
            try:
                can_proceed = await guard.check(
                    entity_id=entity_id,
                    from_state=from_state,
                    to_state=to_state,
                    actor_id=actor_id,
                    metadata=metadata,
                    repository=self.repository
                )
                if not can_proceed:
                    return False, guard.error_message
            except Exception as e:
                logger.error(f"Guard '{guard_name}' failed with error: {e}")
                return False, f"Ошибка проверки условий: {str(e)}"

        return True, None

    async def transition(
        self,
        entity_id: str,
        from_state: Enum,
        to_state: Enum,
        actor_id: str,
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        publish_event: bool = True,
        expected_version: Optional[int] = None,
        request = None
    ) -> bool:
        """
        Выполнить переход состояния

        Args:
            entity_id: ID сущности (evidence, assessment, etc.)
            from_state: Исходное состояние
            to_state: Целевое состояние
            actor_id: ID пользователя, инициировавшего переход
            tenant_id: ID тенанта
            metadata: Дополнительные данные перехода
            publish_event: Публиковать ли событие в EventBus
            expected_version: Expected entity version for optimistic locking

        Returns:
            bool: True если переход выполнен успешно

        Raises:
            WorkflowError: если переход невозможен
        """
        metadata = metadata or {}

        # 1. Validate edge cases if workflow implements validation
        if hasattr(self, 'validate_transition_edge_cases'):
            try:
                await self.validate_transition_edge_cases(
                    entity_id,
                    from_state.value,
                    to_state.value,
                    metadata
                )
            except Exception as e:
                # Re-raise WorkflowValidationError as WorkflowError for consistency
                raise WorkflowError(f"Edge case validation failed: {str(e)}")

        # 2. Проверить возможность перехода
        can_proceed, error_msg = await self.can_transition(
            entity_id, from_state, to_state, actor_id, metadata
        )
        if not can_proceed:
            raise WorkflowError(error_msg)

        transition = self._find_transition(from_state, to_state)

        # 3. Получить текущую сущность из БД
        entity = await self.repository.get_by_id(entity_id)
        if not entity:
            raise WorkflowError(f"Сущность {entity_id} не найдена")

        # 4. Проверить текущее состояние
        current_state = self.state_enum(entity.status)
        if current_state != from_state:
            raise WorkflowError(
                f"Некорректное текущее состояние: ожидалось {from_state.value}, "
                f"фактически {current_state.value}"
            )

        # 4a. Use entity's current version if not provided
        if expected_version is None:
            expected_version = entity.version

        # 5. Выполнить actions "before"
        for action_name in transition.actions:
            if action_name.startswith("before_"):
                action_func = self.actions[action_name]
                try:
                    await action_func(
                        entity=entity,
                        from_state=from_state,
                        to_state=to_state,
                        actor_id=actor_id,
                        metadata=metadata,
                        repository=self.repository
                    )
                except Exception as e:
                    logger.error(f"Action '{action_name}' failed: {e}")
                    raise WorkflowError(f"Ошибка выполнения действия '{action_name}': {str(e)}")

        # 6. Обновить состояние в БД с optimistic locking
        try:
            await self.repository.update_status(
                id=entity_id,
                status=to_state.value,
                expected_version=expected_version
            )
        except Exception as e:
            logger.error(f"Failed to update status in DB: {e}")
            # Re-raise concurrency errors with more context
            if "ConcurrencyError" in str(type(e).__name__):
                raise WorkflowError(
                    f"Concurrent modification detected: {str(e)}"
                ) from e
            raise WorkflowError(f"Ошибка обновления состояния в БД: {str(e)}")

        # 7. Создать запись в audit log (legacy method)
        await self._create_audit_log(
            entity_id=entity_id,
            entity_type=self.event_prefix,
            from_state=from_state.value,
            to_state=to_state.value,
            actor_id=actor_id,
            tenant_id=tenant_id,
            metadata=metadata,
            transition_name=transition.event_name
        )

        # 7a. Also log via centralized audit logger if available
        if self.audit:
            try:
                # Get audit category for this workflow
                audit_category = self._get_audit_category()
                await self.audit.log_state_transition(
                    user_id=actor_id,
                    tenant_id=tenant_id,
                    category=audit_category,
                    entity_type=self.event_prefix,
                    entity_id=entity_id,
                    from_state=from_state.value,
                    to_state=to_state.value,
                    request=request,
                    metadata=metadata
                )
            except Exception as e:
                # Don't block transition if audit logging fails
                logger.warning(f"Centralized audit logging failed: {e}")

        # 8. Выполнить actions "after"
        for action_name in transition.actions:
            if action_name.startswith("after_"):
                action_func = self.actions[action_name]
                try:
                    await action_func(
                        entity=entity,
                        from_state=from_state,
                        to_state=to_state,
                        actor_id=actor_id,
                        metadata=metadata,
                        repository=self.repository
                    )
                except Exception as e:
                    # After-actions не должны блокировать переход
                    logger.error(f"After-action '{action_name}' failed: {e}")

        # 9. Публикация события в EventBus
        if publish_event and self.eventbus:
            event_data = {
                "event_type": f"bcm.compliance.{self.event_prefix}.{transition.event_name}",
                "tenant_id": tenant_id,
                "entity_id": entity_id,
                "from_state": from_state.value,
                "to_state": to_state.value,
                "actor_id": actor_id,
                "metadata": metadata,
                "timestamp": datetime.utcnow().isoformat()
            }

            try:
                await self.eventbus.publish(event_data)
                logger.info(
                    f"Published event: {event_data['event_type']} for {entity_id}"
                )
            except Exception as e:
                # Событие не критично для успешности перехода
                logger.error(f"Failed to publish event: {e}")

        logger.info(
            f"Transition completed: {self.event_prefix} {entity_id} "
            f"{from_state.value} → {to_state.value}"
        )

        return True

    async def _create_audit_log(
        self,
        entity_id: str,
        entity_type: str,
        from_state: str,
        to_state: str,
        actor_id: str,
        tenant_id: str,
        metadata: Dict[str, Any],
        transition_name: str
    ):
        """Создать запись в audit log"""
        try:
            await self.repository.create_audit_log({
                "entity_id": entity_id,
                "entity_type": entity_type,
                "action": f"transition_{transition_name}",
                "from_state": from_state,
                "to_state": to_state,
                "actor_id": actor_id,
                "tenant_id": tenant_id,
                "metadata": metadata,
                "timestamp": datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")

    def get_available_transitions(self, current_state: Enum) -> List[Dict[str, Any]]:
        """
        Получить список доступных переходов из текущего состояния

        Returns:
            List[Dict] с информацией о доступных переходах
        """
        available = []
        for transition in self.transitions:
            if transition.from_state == current_state:
                available.append({
                    "to_state": transition.to_state.value,
                    "event_name": transition.event_name,
                    "description": transition.description,
                    "required_fields": transition.required_fields
                })
        return available

    def _get_audit_category(self) -> AuditCategory:
        """
        Get audit category for this workflow.
        Subclasses can override to provide specific category.
        """
        # Map event prefix to audit category
        category_map = {
            "evidence": AuditCategory.EVIDENCE,
            "assessment": AuditCategory.ASSESSMENT,
            "gap": AuditCategory.GAP,
            "nonconformity": AuditCategory.NONCONFORMITY,
            "audit": AuditCategory.AUDIT
        }
        return category_map.get(self.event_prefix, AuditCategory.COMPLIANCE)

    def get_workflow_diagram(self) -> Dict[str, Any]:
        """
        Получить описание воркфлоу в виде диаграммы (для документации)

        Returns:
            Dict с полным описанием воркфлоу
        """
        states = [state.value for state in self.state_enum]
        transitions_list = [
            {
                "from": t.from_state.value,
                "to": t.to_state.value,
                "event": t.event_name,
                "description": t.description,
                "guards": t.guards,
                "actions": t.actions
            }
            for t in self.transitions
        ]

        return {
            "workflow_name": self.event_prefix,
            "states": states,
            "transitions": transitions_list,
            "guards": {name: guard.error_message for name, guard in self.guards.items()},
            "actions": list(self.actions.keys())
        }
