"""
Pydantic схемы для валидации входных данных workflow-intelligence модуля.

Этот модуль содержит схемы для валидации:
- Workflow контекста
- Action данных
- Workflow case
- Organization контекста
- Embeddings
"""

from pydantic import BaseModel, validator, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class WorkflowContextSchema(BaseModel):
    """
    Схема для валидации контекста workflow.

    Attributes:
        workflow_id: Уникальный идентификатор workflow
        module: Название модуля (compliance, bia, risk и т.д.)
        tenant_id: Идентификатор тенанта/организации
        context: Словарь с контекстными данными
    """
    workflow_id: str = Field(..., min_length=1, max_length=255, description="Workflow ID")
    module: str = Field(..., min_length=1, max_length=100, description="Module name")
    tenant_id: str = Field(..., min_length=1, max_length=255, description="Tenant ID")
    context: Dict[str, Any] = Field(..., description="Workflow context data")

    @validator('context')
    def validate_context_size(cls, v):
        """Проверяет что context не превышает 1MB."""
        context_json = json.dumps(v)
        if len(context_json) > 1_000_000:  # 1MB limit
            raise ValueError('Context too large (max 1MB)')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "wf_123456",
                "module": "compliance",
                "tenant_id": "tenant_001",
                "context": {
                    "user_id": "user_123",
                    "step": "risk_assessment",
                    "data": {}
                }
            }
        }


class ActionDataSchema(BaseModel):
    """
    Схема для валидации данных действия.

    Attributes:
        action: Название действия
        data: Данные действия
        user_id: Опциональный ID пользователя
    """
    action: str = Field(..., min_length=1, max_length=100, description="Action name")
    data: Dict[str, Any] = Field(..., description="Action data")
    user_id: Optional[str] = Field(None, max_length=255, description="User ID")

    @validator('action')
    def validate_action(cls, v):
        """Проверяет что action содержит только alphanumeric символы и underscore."""
        if not v.replace('_', '').isalnum():
            raise ValueError('Invalid action name: only alphanumeric and underscore allowed')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "action": "submit_assessment",
                "data": {
                    "assessment_id": "assess_123",
                    "score": 85
                },
                "user_id": "user_123"
            }
        }


class WorkflowCaseSchema(BaseModel):
    """
    Схема для валидации workflow case.

    Attributes:
        case_id: Уникальный идентификатор кейса
        module: Название модуля
        tenant_id: Идентификатор тенанта
        journey: Список шагов в journey
        org_context: Опциональный контекст организации
        metrics: Опциональные метрики
    """
    case_id: str = Field(..., min_length=1, max_length=255, description="Case ID")
    module: str = Field(..., min_length=1, max_length=100, description="Module name")
    tenant_id: str = Field(..., min_length=1, max_length=255, description="Tenant ID")
    journey: List[Dict[str, Any]] = Field(..., description="Journey steps")
    org_context: Optional[Dict[str, Any]] = Field(None, description="Organization context")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Case metrics")

    @validator('journey')
    def validate_journey(cls, v):
        """Проверяет что journey не превышает 1000 шагов."""
        if len(v) > 1000:  # Max 1000 steps
            raise ValueError('Journey too long (max 1000 steps)')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "case_123",
                "module": "compliance",
                "tenant_id": "tenant_001",
                "journey": [
                    {
                        "step": "start",
                        "timestamp": "2025-10-03T12:00:00Z",
                        "action": "init"
                    }
                ],
                "org_context": {
                    "industry": "finance",
                    "size": "medium"
                },
                "metrics": {
                    "duration": 3600,
                    "steps_count": 5
                }
            }
        }


class OrganizationContextSchema(BaseModel):
    """
    Схема для валидации контекста организации.

    Attributes:
        industry: Отрасль организации
        size: Размер организации
        maturity_level: Уровень зрелости
    """
    industry: Optional[str] = Field(None, max_length=100, description="Industry type")
    size: Optional[str] = Field(None, max_length=50, description="Organization size")
    maturity_level: Optional[str] = Field(None, max_length=50, description="Maturity level")

    @validator('size')
    def validate_size(cls, v):
        """Проверяет что размер организации из допустимого списка."""
        if v and v not in ['small', 'medium', 'large', 'enterprise']:
            raise ValueError('Invalid org size: must be one of [small, medium, large, enterprise]')
        return v

    @validator('maturity_level')
    def validate_maturity_level(cls, v):
        """Проверяет что уровень зрелости из допустимого списка."""
        if v and v not in ['initial', 'developing', 'defined', 'managed', 'optimizing']:
            raise ValueError('Invalid maturity level: must be one of [initial, developing, defined, managed, optimizing]')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "industry": "finance",
                "size": "medium",
                "maturity_level": "managed"
            }
        }


class EmbeddingSchema(BaseModel):
    """
    Схема для валидации embedding векторов.

    Attributes:
        embedding: Вектор embedding (1536 измерений для OpenAI text-embedding-3-small)
    """
    embedding: List[float] = Field(
        ...,
        min_length=1536,
        max_length=1536,
        description="Embedding vector (1536 dimensions)"
    )

    @validator('embedding')
    def validate_embedding_values(cls, v):
        """Проверяет что все значения embedding - числа."""
        if not all(isinstance(x, (int, float)) for x in v):
            raise ValueError('All embedding values must be numeric')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "embedding": [0.1] * 1536  # Example with 1536 dimensions
            }
        }


class WorkflowMetricsSchema(BaseModel):
    """
    Схема для валидации метрик workflow.

    Attributes:
        duration: Длительность в секундах
        steps_count: Количество шагов
        success: Успешность выполнения
        error_count: Количество ошибок
    """
    duration: Optional[float] = Field(None, ge=0, description="Duration in seconds")
    steps_count: Optional[int] = Field(None, ge=0, description="Number of steps")
    success: Optional[bool] = Field(None, description="Success status")
    error_count: Optional[int] = Field(None, ge=0, description="Number of errors")

    class Config:
        json_schema_extra = {
            "example": {
                "duration": 3600.5,
                "steps_count": 10,
                "success": True,
                "error_count": 0
            }
        }


class UserActionSchema(BaseModel):
    """
    Схема для валидации пользовательского действия.

    Attributes:
        user_id: ID пользователя
        action_type: Тип действия
        timestamp: Временная метка
        metadata: Дополнительные метаданные
    """
    user_id: str = Field(..., min_length=1, max_length=255, description="User ID")
    action_type: str = Field(..., min_length=1, max_length=100, description="Action type")
    timestamp: Optional[datetime] = Field(None, description="Action timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    @validator('timestamp', pre=True, always=True)
    def set_timestamp(cls, v):
        """Устанавливает текущее время если не указано."""
        return v or datetime.utcnow()

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "action_type": "click",
                "timestamp": "2025-10-03T12:00:00Z",
                "metadata": {
                    "button": "submit",
                    "page": "assessment"
                }
            }
        }
