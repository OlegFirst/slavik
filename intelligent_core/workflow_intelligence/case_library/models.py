"""
 CASE LIBRARY - Data Models

Cases хранят успешные прохождения workflows для обучения AI и пользователей.

Philosophy: Every completed workflow is a lesson for future users.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, computed_field
from enum import Enum


# ============================================================================
# CASE MODELS
# ============================================================================

class ChallengeResolution(BaseModel):
    """Проблема которая возникла и как её решили"""
    type: str = Field(..., description="Тип проблемы (insufficient_data, validation_error, etc)")
    description: str = Field(..., description="Описание проблемы")
    resolution: str = Field(..., description="Как решили")
    time_to_resolve_hours: float = Field(..., description="Сколько времени заняло решение")
    ai_assisted: bool = Field(default=False, description="Помогал ли AI")


class AIInteraction(BaseModel):
    """Взаимодействие с AI во время workflow"""
    type: str = Field(..., description="suggest, analyze, validate, etc")
    prompt_summary: str = Field(..., description="О чём был вопрос/запрос")
    response_summary: str = Field(..., description="Что ответил AI")
    accepted: bool = Field(..., description="Принял ли пользователь рекомендацию")
    helpful_rating: Optional[int] = Field(None, ge=1, le=5, description="Насколько полезно")


class WorkflowStepRecord(BaseModel):
    """Один шаг в workflow journey"""
    stage: str = Field(..., description="Название стадии")
    started_at: datetime
    completed_at: datetime
    duration_hours: float

    actions_taken: List[Dict[str, Any]] = Field(default_factory=list)
    challenges: List[ChallengeResolution] = Field(default_factory=list)
    ai_interactions: List[AIInteraction] = Field(default_factory=list)

    # Метрики шага
    step_metrics: Dict[str, Any] = Field(default_factory=dict)

    @computed_field
    @property
    def ai_assistance_level(self) -> str:
        """Уровень помощи AI на этом шаге"""
        ai_count = len([i for i in self.ai_interactions if i.accepted])

        if ai_count == 0:
            return "none"
        elif ai_count <= 2:
            return "low"
        elif ai_count <= 5:
            return "medium"
        else:
            return "high"


class OrganizationContext(BaseModel):
    """Anonymized контекст организации"""
    industry: str = Field(..., description="Индустрия")
    size: str = Field(..., description="small/medium/large/enterprise")
    org_type: str = Field(..., description="Тип организации")
    maturity_level: str = Field(
        ...,
        description="BCM maturity: none/basic/intermediate/advanced/optimized"
    )
    region: Optional[str] = Field(None, description="Регион (опционально)")

    # NO identifiable info: no names, emails, addresses, etc!


class WorkflowMetrics(BaseModel):
    """Метрики успеха workflow"""
    total_duration_days: float = Field(..., description="Общая длительность")
    total_steps: int = Field(..., description="Количество шагов")

    # Специфичные для модуля метрики
    processes_identified: Optional[int] = None
    critical_processes: Optional[int] = None
    risks_identified: Optional[int] = None
    plans_generated: Optional[int] = None

    # AI usage
    ai_recommendations_used: int = Field(default=0)
    ai_recommendations_rejected: int = Field(default=0)

    # Quality
    user_satisfaction: Optional[float] = Field(None, ge=1, le=5)
    completed_successfully: bool = Field(default=True)
    certification_ready: bool = Field(default=False)

    # Rework
    revisions_needed: int = Field(default=0)
    rejections: int = Field(default=0)

    @computed_field
    @property
    def ai_acceptance_rate(self) -> float:
        """Процент принятых AI рекомендаций"""
        total = self.ai_recommendations_used + self.ai_recommendations_rejected
        if total == 0:
            return 0.0
        return self.ai_recommendations_used / total


class WorkflowCase(BaseModel):
    """
    Полный case успешного прохождения workflow

    Это главная структура Case Library.
    """

    # Идентификация
    case_id: str = Field(..., description="Уникальный ID case")
    module: str = Field(..., description="bia, risk, planning, etc")
    workflow_name: str = Field(..., description="Название workflow")

    # Контекст организации (anonymized!)
    organization_context: OrganizationContext

    # Journey через workflow
    journey: List[WorkflowStepRecord] = Field(
        ...,
        description="Полный путь от начала до конца"
    )

    # Метрики
    metrics: WorkflowMetrics

    # Insights
    success_patterns: List[str] = Field(
        default_factory=list,
        description="Что сработало хорошо (для AI prompts)"
    )

    lessons_learned: List[str] = Field(
        default_factory=list,
        description="Уроки (для будущих пользователей)"
    )

    best_practices: List[str] = Field(
        default_factory=list,
        description="Best practices продемонстрированные"
    )

    # Для ML: feature vector
    features: Dict[str, Any] = Field(
        default_factory=dict,
        description="Features для ML моделей"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0")

    # Privacy & Compliance
    anonymized: bool = Field(default=True)
    consent_given: bool = Field(default=True)

    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "case-bia-20251003-001",
                "module": "bia",
                "workflow_name": "bia_process",
                "organization_context": {
                    "industry": "healthcare",
                    "size": "medium",
                    "org_type": "hospital",
                    "maturity_level": "basic"
                },
                "metrics": {
                    "total_duration_days": 14,
                    "total_steps": 8,
                    "processes_identified": 12,
                    "ai_recommendations_used": 15,
                    "completed_successfully": True
                },
                "success_patterns": [
                    "Used AI early - saved 2 days",
                    "Involved process owners",
                ],
                "lessons_learned": [
                    "Start with critical processes first"
                ]
            }
        }


# ============================================================================
# QUERY MODELS
# ============================================================================

class CaseQuery(BaseModel):
    """Запрос для поиска похожих cases"""
    module: str
    industry: Optional[str] = None
    org_size: Optional[str] = None
    maturity_level: Optional[str] = None
    current_stage: Optional[str] = None

    # Semantic search query
    query_text: Optional[str] = None

    # Filters
    min_success_rate: Optional[float] = Field(None, ge=0, le=1)
    min_satisfaction: Optional[float] = Field(None, ge=1, le=5)
    max_duration_days: Optional[float] = None

    # Sorting
    sort_by: str = Field(default="similarity", description="similarity/duration/satisfaction")
    limit: int = Field(default=5, ge=1, le=20)


class CaseSearchResult(BaseModel):
    """Результат поиска case"""
    case: WorkflowCase
    similarity_score: float = Field(..., ge=0, le=1)
    relevance_factors: List[str] = Field(
        default_factory=list,
        description="Почему этот case релевантен"
    )


# ============================================================================
# BENCHMARK MODELS
# ============================================================================

class BenchmarkStats(BaseModel):
    """Статистика по cases для benchmarking"""
    module: str
    industry: Optional[str] = None
    total_cases: int

    # Duration
    avg_duration_days: float
    median_duration_days: float
    p95_duration_days: float

    # Success
    success_rate: float = Field(..., ge=0, le=1)
    avg_user_satisfaction: Optional[float] = None

    # AI Usage
    avg_ai_usage: float
    ai_acceptance_rate: float

    # Common patterns
    common_challenges: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Наиболее частые проблемы"
    )

    best_practices: List[str] = Field(
        default_factory=list,
        description="Best practices от успешных cases"
    )

    # Quality metrics
    avg_processes_identified: Optional[float] = None
    avg_revisions: Optional[float] = None

    # Timestamp
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# PATTERN MODELS
# ============================================================================

class SuccessPattern(BaseModel):
    """Паттерн успеха обнаруженный в cases"""
    pattern_id: str
    pattern_type: str = Field(..., description="action_sequence, timing, ai_usage, etc")
    description: str

    # Evidence
    observed_in_cases: List[str] = Field(..., description="Case IDs где наблюдался")
    frequency: float = Field(..., ge=0, le=1, description="В скольких успешных cases")

    # Impact
    impact_on_duration: Optional[float] = Field(
        None,
        description="Изменение duration (отрицательное = быстрее)"
    )
    impact_on_success: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Корреляция с success"
    )

    # Recommendation
    recommended_for: List[str] = Field(
        default_factory=list,
        description="Для каких industries/sizes рекомендуется"
    )

    confidence: float = Field(..., ge=0, le=1)

    discovered_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# CASE COLLECTION SETTINGS
# ============================================================================

class CaseCollectionConfig(BaseModel):
    """Настройки сбора cases"""
    enabled: bool = Field(default=True)

    # Privacy
    anonymize_data: bool = Field(default=True)
    require_consent: bool = Field(default=True)

    # Quality filters
    min_duration_hours: float = Field(default=1.0, description="Минимальная длительность")
    min_steps: int = Field(default=3, description="Минимум шагов")
    require_successful_completion: bool = Field(default=True)

    # What to collect
    collect_ai_interactions: bool = Field(default=True)
    collect_challenges: bool = Field(default=True)
    collect_user_feedback: bool = Field(default=True)

    # Retention
    retention_days: int = Field(default=1095, description="3 года по умолчанию")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_features_for_ml(case: WorkflowCase) -> Dict[str, Any]:
    """
    Извлечь features для ML моделей

    Returns:
        Feature vector для обучения моделей
    """
    org = case.organization_context

    # Categorical features
    features = {
        # Organization
        "industry": org.industry,
        "size": org.size,
        "maturity_level": org.maturity_level,

        # Workflow characteristics
        "total_steps": len(case.journey),
        "ai_assistance_level": _calculate_overall_ai_level(case.journey),

        # Team characteristics (if available)
        "had_consultant": any("consultant" in bp.lower() for bp in case.best_practices),
        "team_size": case.features.get("team_size", 2),  # Default estimate

        # Process
        "used_templates": any("template" in bp.lower() for bp in case.best_practices),
        "early_ai_usage": _used_ai_early(case.journey),

        # Outcomes
        "success": case.metrics.completed_successfully,
        "duration_days": case.metrics.total_duration_days,
        "satisfaction": case.metrics.user_satisfaction or 3.0,
        "ai_acceptance_rate": case.metrics.ai_acceptance_rate,
    }

    # Module-specific features
    if case.module == "bia":
        features.update({
            "processes_identified": case.metrics.processes_identified or 0,
            "critical_processes": case.metrics.critical_processes or 0,
        })

    return features


def _calculate_overall_ai_level(journey: List[WorkflowStepRecord]) -> str:
    """Общий уровень использования AI"""
    levels = [step.ai_assistance_level for step in journey]

    if not levels:
        return "none"

    # Majority vote
    from collections import Counter
    counter = Counter(levels)
    return counter.most_common(1)[0][0]


def _used_ai_early(journey: List[WorkflowStepRecord]) -> bool:
    """Использовался ли AI на ранних стадиях"""
    if len(journey) < 2:
        return False

    # Проверяем первые 2 шага
    early_steps = journey[:2]
    return any(
        len(step.ai_interactions) > 0
        for step in early_steps
    )
