"""
Pydantic схемы для валидации данных workflow-intelligence модуля.

Этот пакет экспортирует все схемы валидации для использования в API endpoints,
внутренних сервисах и интеграциях.

Доступные схемы:
- WorkflowContextSchema: Валидация контекста workflow
- ActionDataSchema: Валидация данных действий
- WorkflowCaseSchema: Валидация workflow case
- OrganizationContextSchema: Валидация контекста организации
- EmbeddingSchema: Валидация embedding векторов
- WorkflowMetricsSchema: Валидация метрик workflow
- UserActionSchema: Валидация пользовательских действий

Пример использования:
    >>> from workflow_intelligence.schemas import WorkflowContextSchema
    >>>
    >>> data = {
    ...     "workflow_id": "wf_123",
    ...     "module": "compliance",
    ...     "tenant_id": "tenant_001",
    ...     "context": {"step": "init"}
    ... }
    >>>
    >>> validated = WorkflowContextSchema(**data)
    >>> print(validated.workflow_id)
    'wf_123'
"""

from workflow_intelligence.schemas.validation import (
    WorkflowContextSchema,
    ActionDataSchema,
    WorkflowCaseSchema,
    OrganizationContextSchema,
    EmbeddingSchema,
    WorkflowMetricsSchema,
    UserActionSchema,
)

__all__ = [
    # Core workflow schemas
    "WorkflowContextSchema",
    "ActionDataSchema",
    "WorkflowCaseSchema",

    # Context schemas
    "OrganizationContextSchema",

    # AI/ML schemas
    "EmbeddingSchema",

    # Metrics and tracking
    "WorkflowMetricsSchema",
    "UserActionSchema",
]

# Версия схем для отслеживания изменений
SCHEMAS_VERSION = "1.0.0"
