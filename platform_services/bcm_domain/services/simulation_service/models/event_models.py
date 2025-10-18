"""
Simulation Event Models
=======================

Типизированные модели событий для EventBus интеграции.

Обеспечивают:
- Type-safe коммуникацию между сервисами
- Четкие контракты событий
- Автоматическую валидацию
- Простую интеграцию с EventBus

Адаптировано из BCM Incident module EventBus patterns.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class EventPriority(str, Enum):
    """Приоритет события"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SimulationStatus(str, Enum):
    """Статус симуляции"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BaseSimulationEvent(BaseModel):
    """
    Базовое событие симуляции

    Все события наследуют от этого класса.
    """
    event_type: str = Field(..., description="Тип события")
    event_id: str = Field(..., description="Уникальный ID события")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Время создания события"
    )
    simulation_id: str = Field(..., description="ID симуляции")
    source_service: str = Field(
        default="simulation-service",
        description="Сервис-источник"
    )
    priority: EventPriority = Field(
        default=EventPriority.MEDIUM,
        description="Приоритет события"
    )
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Дополнительные данные"
    )
    correlation_id: Optional[str] = Field(
        default=None,
        description="ID для связи связанных событий"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Теги для категоризации"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "simulation.event",
                "event_id": "evt_123456",
                "timestamp": "2025-10-13T10:00:00Z",
                "simulation_id": "sim_123",
                "source_service": "simulation-service",
                "priority": "medium",
                "data": {},
                "tags": ["bcm", "exercise"]
            }
        }


# ========================================================================
# LIFECYCLE EVENTS
# ========================================================================

class SimulationCreatedEvent(BaseSimulationEvent):
    """Событие: симуляция создана"""
    event_type: str = "simulation.created"
    scenario_id: str = Field(..., description="ID сценария")
    scenario_title: str = Field(..., description="Название сценария")
    created_by: str = Field(..., description="Кто создал")
    organization_id: str = Field(..., description="ID организации")


class SimulationStartedEvent(BaseSimulationEvent):
    """Событие: симуляция запущена"""
    event_type: str = "simulation.started"
    scenario_id: str
    engine_used: str = Field(..., description="Использованный движок")
    estimated_duration_seconds: int = Field(
        ...,
        description="Ожидаемая продолжительность"
    )
    participants: int = Field(default=0, description="Количество участников")
    configuration: Dict[str, Any] = Field(
        default_factory=dict,
        description="Конфигурация симуляции"
    )


class SimulationProgressEvent(BaseSimulationEvent):
    """Событие: прогресс выполнения симуляции"""
    event_type: str = "simulation.progress"
    progress_percentage: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Процент выполнения"
    )
    current_phase: str = Field(..., description="Текущая фаза")
    elapsed_seconds: int = Field(..., description="Прошло времени")
    estimated_remaining_seconds: Optional[int] = Field(
        default=None,
        description="Осталось времени"
    )
    message: Optional[str] = Field(
        default=None,
        description="Сообщение о прогрессе"
    )


class SimulationPausedEvent(BaseSimulationEvent):
    """Событие: симуляция приостановлена"""
    event_type: str = "simulation.paused"
    reason: str = Field(..., description="Причина приостановки")
    paused_by: str = Field(..., description="Кто приостановил")
    can_resume: bool = Field(default=True, description="Можно возобновить")


class SimulationResumedEvent(BaseSimulationEvent):
    """Событие: симуляция возобновлена"""
    event_type: str = "simulation.resumed"
    resumed_by: str = Field(..., description="Кто возобновил")
    paused_duration_seconds: int = Field(
        ...,
        description="Длительность паузы"
    )


class SimulationCompletedEvent(BaseSimulationEvent):
    """Событие: симуляция успешно завершена"""
    event_type: str = "simulation.completed"
    status: str = Field(default="completed", description="Статус завершения")
    duration_seconds: int = Field(..., description="Общая продолжительность")
    success_rate: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Процент успешности"
    )
    quality_score: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        description="Оценка качества"
    )
    participants_count: int = Field(
        default=0,
        description="Количество участников"
    )
    metrics_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Сводка метрик"
    )


class SimulationFailedEvent(BaseSimulationEvent):
    """Событие: симуляция завершилась с ошибкой"""
    event_type: str = "simulation.failed"
    error_type: str = Field(..., description="Тип ошибки")
    error_message: str = Field(..., description="Сообщение об ошибке")
    error_code: Optional[str] = Field(default=None, description="Код ошибки")
    stack_trace: Optional[str] = Field(
        default=None,
        description="Stack trace (для отладки)"
    )
    recovery_possible: bool = Field(
        default=False,
        description="Возможно восстановление"
    )
    failed_at_phase: Optional[str] = Field(
        default=None,
        description="Фаза при которой произошел сбой"
    )


class SimulationCancelledEvent(BaseSimulationEvent):
    """Событие: симуляция отменена"""
    event_type: str = "simulation.cancelled"
    cancelled_by: str = Field(..., description="Кто отменил")
    reason: str = Field(..., description="Причина отмены")
    completion_percentage: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Процент выполнения на момент отмены"
    )


# ========================================================================
# ANALYSIS & RESULTS EVENTS
# ========================================================================

class ResultsGeneratedEvent(BaseSimulationEvent):
    """Событие: результаты сгенерированы"""
    event_type: str = "simulation.results_generated"
    results_id: str = Field(..., description="ID результатов")
    result_type: str = Field(..., description="Тип результатов")
    quality_score: float = Field(..., description="Оценка качества")
    has_recommendations: bool = Field(
        default=False,
        description="Есть рекомендации"
    )
    has_lessons_learned: bool = Field(
        default=False,
        description="Есть извлеченные уроки"
    )


class AnalysisCompletedEvent(BaseSimulationEvent):
    """Событие: анализ результатов завершен"""
    event_type: str = "simulation.analysis_completed"
    analysis_type: str = Field(..., description="Тип анализа")
    findings_count: int = Field(..., description="Количество находок")
    risk_level: str = Field(..., description="Уровень риска")
    recommendations_count: int = Field(
        default=0,
        description="Количество рекомендаций"
    )


class LearningCapturedEvent(BaseSimulationEvent):
    """Событие: извлечены уроки из симуляции"""
    event_type: str = "simulation.learning_captured"
    scenario_id: str = Field(..., description="ID сценария")
    lessons_learned: List[str] = Field(
        default_factory=list,
        description="Список извлеченных уроков"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Список рекомендаций"
    )
    improvement_areas: List[str] = Field(
        default_factory=list,
        description="Области для улучшения"
    )
    effectiveness_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Оценка эффективности"
    )
    learning_quality: str = Field(
        ...,
        description="Качество обучения (high/medium/low)"
    )


class MetricsUpdatedEvent(BaseSimulationEvent):
    """Событие: обновлены метрики симуляции"""
    event_type: str = "simulation.metrics_updated"
    metric_type: str = Field(..., description="Тип метрики")
    metrics: Dict[str, float] = Field(
        ...,
        description="Словарь метрик"
    )
    aggregation_period: Optional[str] = Field(
        default=None,
        description="Период агрегации"
    )


# ========================================================================
# INTEGRATION EVENTS
# ========================================================================

class ScenarioRequestedEvent(BaseSimulationEvent):
    """Событие: запрошен сценарий"""
    event_type: str = "simulation.scenario_requested"
    scenario_type: str = Field(..., description="Тип сценария")
    complexity: int = Field(..., ge=1, le=5, description="Сложность")
    requested_by: str = Field(..., description="Кто запросил")
    requirements: Dict[str, Any] = Field(
        default_factory=dict,
        description="Требования к сценарию"
    )


class AIAnalysisRequestedEvent(BaseSimulationEvent):
    """Событие: запрошен AI анализ"""
    event_type: str = "simulation.ai_analysis_requested"
    analysis_type: str = Field(..., description="Тип анализа")
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Контекст для анализа"
    )
    priority: EventPriority = Field(
        default=EventPriority.MEDIUM,
        description="Приоритет запроса"
    )


class IntegrationSyncEvent(BaseSimulationEvent):
    """Событие: синхронизация с внешней системой"""
    event_type: str = "simulation.integration_sync"
    target_system: str = Field(..., description="Целевая система")
    sync_type: str = Field(..., description="Тип синхронизации")
    sync_status: str = Field(..., description="Статус синхронизации")
    records_synced: int = Field(default=0, description="Синхронизировано записей")
    errors_count: int = Field(default=0, description="Количество ошибок")


# ========================================================================
# NOTIFICATION EVENTS
# ========================================================================

class ParticipantNotificationEvent(BaseSimulationEvent):
    """Событие: уведомление участника"""
    event_type: str = "simulation.participant_notification"
    participant_id: str = Field(..., description="ID участника")
    notification_type: str = Field(..., description="Тип уведомления")
    message: str = Field(..., description="Сообщение")
    action_required: bool = Field(
        default=False,
        description="Требуется действие"
    )
    deadline: Optional[datetime] = Field(
        default=None,
        description="Срок действия"
    )


class AlertEvent(BaseSimulationEvent):
    """Событие: критическое предупреждение"""
    event_type: str = "simulation.alert"
    priority: EventPriority = EventPriority.HIGH
    alert_type: str = Field(..., description="Тип предупреждения")
    alert_message: str = Field(..., description="Сообщение")
    severity: str = Field(..., description="Серьезность")
    requires_immediate_action: bool = Field(
        default=False,
        description="Требует немедленного действия"
    )
    alert_recipients: List[str] = Field(
        default_factory=list,
        description="Получатели предупреждения"
    )


# ========================================================================
# RESOURCE EVENTS
# ========================================================================

class ResourceAllocatedEvent(BaseSimulationEvent):
    """Событие: ресурсы выделены"""
    event_type: str = "simulation.resource_allocated"
    resource_type: str = Field(..., description="Тип ресурса")
    resource_id: str = Field(..., description="ID ресурса")
    allocation_amount: float = Field(..., description="Количество")
    allocation_unit: str = Field(..., description="Единица измерения")


class ResourceReleasedEvent(BaseSimulationEvent):
    """Событие: ресурсы освобождены"""
    event_type: str = "simulation.resource_released"
    resource_type: str = Field(..., description="Тип ресурса")
    resource_id: str = Field(..., description="ID ресурса")
    released_amount: float = Field(..., description="Освобождено")
    usage_duration_seconds: int = Field(
        ...,
        description="Длительность использования"
    )


# ========================================================================
# EVENT FACTORY
# ========================================================================

class SimulationEventFactory:
    """
    Фабрика для создания событий симуляции

    Упрощает создание правильно типизированных событий.
    """

    EVENT_TYPE_MAP = {
        "simulation.created": SimulationCreatedEvent,
        "simulation.started": SimulationStartedEvent,
        "simulation.progress": SimulationProgressEvent,
        "simulation.paused": SimulationPausedEvent,
        "simulation.resumed": SimulationResumedEvent,
        "simulation.completed": SimulationCompletedEvent,
        "simulation.failed": SimulationFailedEvent,
        "simulation.cancelled": SimulationCancelledEvent,
        "simulation.results_generated": ResultsGeneratedEvent,
        "simulation.analysis_completed": AnalysisCompletedEvent,
        "simulation.learning_captured": LearningCapturedEvent,
        "simulation.metrics_updated": MetricsUpdatedEvent,
        "simulation.scenario_requested": ScenarioRequestedEvent,
        "simulation.ai_analysis_requested": AIAnalysisRequestedEvent,
        "simulation.integration_sync": IntegrationSyncEvent,
        "simulation.participant_notification": ParticipantNotificationEvent,
        "simulation.alert": AlertEvent,
        "simulation.resource_allocated": ResourceAllocatedEvent,
        "simulation.resource_released": ResourceReleasedEvent,
    }

    @classmethod
    def create_event(
        cls,
        event_type: str,
        **kwargs
    ) -> BaseSimulationEvent:
        """
        Создать событие по типу

        Args:
            event_type: Тип события (например "simulation.started")
            **kwargs: Параметры события

        Returns:
            Типизированное событие

        Raises:
            ValueError: Если тип события неизвестен
        """
        event_class = cls.EVENT_TYPE_MAP.get(event_type)

        if not event_class:
            raise ValueError(f"Unknown event type: {event_type}")

        return event_class(**kwargs)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseSimulationEvent:
        """
        Создать событие из словаря

        Args:
            data: Словарь с данными события (должен содержать 'event_type')

        Returns:
            Типизированное событие
        """
        event_type = data.get("event_type")
        if not event_type:
            raise ValueError("Missing 'event_type' in data")

        return cls.create_event(event_type, **data)

    @classmethod
    def get_available_event_types(cls) -> List[str]:
        """Получить список доступных типов событий"""
        return list(cls.EVENT_TYPE_MAP.keys())


# ========================================================================
# EVENT VALIDATOR
# ========================================================================

class EventValidator:
    """Валидатор событий"""

    @staticmethod
    def validate_event(event: BaseSimulationEvent) -> bool:
        """
        Проверить валидность события

        Args:
            event: Событие для проверки

        Returns:
            True если валидно, False иначе
        """
        try:
            # Pydantic автоматически валидирует при создании
            # Дополнительные проверки можно добавить здесь
            return True
        except Exception:
            return False

    @staticmethod
    def validate_event_sequence(
        events: List[BaseSimulationEvent]
    ) -> bool:
        """
        Проверить логическую последовательность событий

        Например:
        - "started" должно быть после "created"
        - "completed" не может быть до "started"
        """
        event_order = {
            "simulation.created": 1,
            "simulation.started": 2,
            "simulation.progress": 3,
            "simulation.completed": 4,
            "simulation.failed": 4,
            "simulation.cancelled": 4
        }

        last_order = 0
        for event in events:
            current_order = event_order.get(event.event_type, 99)
            if current_order < last_order:
                return False
            last_order = max(last_order, current_order)

        return True
