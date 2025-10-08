#!/usr/bin/env python3
"""
MIO Manager API Routes
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel

# Import from main (will be injected)
import sys
from pathlib import Path

router = APIRouter(prefix="/api", tags=["MIO Manager"])


# ============================================================================
# MODELS
# ============================================================================

class ServiceDiscoveryRequest(BaseModel):
    force_rescan: bool = False


class DependencyAnalysisRequest(BaseModel):
    service_name: Optional[str] = None


class ComplexityAnalysisRequest(BaseModel):
    service_name: str


class TaskDelegateRequest(BaseModel):
    task_type: str
    details: dict
    priority: str = "medium"


class EventAnalysisRequest(BaseModel):
    event_name: str
    publishers: list = []
    subscribers: list = []


class EventFeedbackRequest(BaseModel):
    suggestion_id: str
    decision: str  # accepted, rejected, modified
    outcome: str  # success, failure, partial


# ============================================================================
# ROUTES
# ============================================================================

@router.post("/discover")
async def discover_services(request: ServiceDiscoveryRequest):
    """
    Auto-discovery всех сервисов
    Запускает AST Analyzer для поиска /health и /metrics эндпоинтов
    """
    from main import toolkit_manager

    result = await toolkit_manager.discover_services()

    return {
        "status": "success",
        "data": result
    }


@router.post("/analyze/dependencies")
async def analyze_dependencies(request: DependencyAnalysisRequest):
    """
    Root cause analysis через dependency graph
    Если service_name указан - анализ только для него
    """
    from main import toolkit_manager

    result = await toolkit_manager.analyze_dependencies(
        service_name=request.service_name
    )

    return {
        "status": "success",
        "data": result
    }


@router.post("/analyze/complexity")
async def analyze_complexity(request: ComplexityAnalysisRequest):
    """
    Code complexity analysis через Radon
    """
    from main import toolkit_manager

    result = await toolkit_manager.analyze_code_complexity(
        service_name=request.service_name
    )

    return {
        "status": "success",
        "data": result
    }


@router.post("/security/scan")
async def security_scan():
    """
    Security scan через Bandit
    """
    from main import toolkit_manager

    result = await toolkit_manager.run_security_scan()

    return {
        "status": "success",
        "data": result
    }


@router.post("/tests/generate")
async def generate_tests():
    """
    Генерация Synthetic Monitoring тестов
    """
    from main import toolkit_manager

    result = await toolkit_manager.generate_synthetic_tests()

    return {
        "status": "success",
        "data": result
    }


@router.post("/monitoring/setup")
async def setup_monitoring():
    """
    Полная настройка мониторинга (ПРЯМАЯ ОБЯЗАННОСТЬ MIO Manager!):
    1. Service Discovery
    2. Prometheus config generation
    3. Grafana dashboard generation

    Автоматизирует сбор ВСЕХ метрик и настройку систем МиО
    """
    from main import toolkit_manager

    result = await toolkit_manager.setup_monitoring()

    return {
        "status": "success",
        "message": "Monitoring setup completed",
        "data": result
    }


@router.post("/monitoring/prometheus/config")
async def generate_prometheus_config():
    """
    Генерация Prometheus scrape configs
    Автоматически создает конфигурацию для всех сервисов с /metrics
    """
    from main import toolkit_manager

    # Сначала discover services
    discovery = await toolkit_manager.discover_services()
    services = discovery['services']

    # Генерация Prometheus config
    result = await toolkit_manager.generate_prometheus_config(services)

    return {
        "status": "success",
        "message": "Prometheus config generated",
        "data": result
    }


@router.post("/monitoring/grafana/dashboard")
async def generate_grafana_dashboard():
    """
    Генерация Grafana dashboard
    Автоматически создает dashboard для всех сервисов
    """
    from main import toolkit_manager

    # Сначала discover services
    discovery = await toolkit_manager.discover_services()
    services = discovery['services']

    # Генерация Grafana dashboard
    result = await toolkit_manager.generate_grafana_dashboard(services)

    return {
        "status": "success",
        "message": "Grafana dashboard generated",
        "data": result
    }


@router.post("/tasks/delegate")
async def delegate_task(request: TaskDelegateRequest):
    """
    Делегировать задачу Orchestrator
    """
    from main import toolkit_manager, orchestrator_client

    # Create task
    task = await toolkit_manager.create_improvement_task(
        issue_type=request.task_type,
        details=request.details
    )

    # Delegate to Orchestrator
    result = await orchestrator_client.delegate_task(task)

    return {
        "status": "success",
        "task": task,
        "orchestrator_response": result
    }


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Получить статус задачи
    """
    from main import orchestrator_client

    result = await orchestrator_client.get_task_status(task_id)

    return {
        "status": "success",
        "data": result
    }


@router.post("/gateway/register")
async def register_service_in_gateway(service_config: dict):
    """
    Регистрация сервиса в Gateway
    """
    from main import gateway_manager

    result = await gateway_manager.register_service(service_config)

    return {
        "status": "success",
        "data": result
    }


@router.get("/gateway/health/{service_name}")
async def get_service_health(service_name: str):
    """
    Проверка health сервиса через Gateway
    """
    from main import gateway_manager

    result = await gateway_manager.get_service_health(service_name)

    return {
        "status": "success",
        "data": result
    }


@router.get("/status")
async def get_mio_status():
    """
    Общий статус MIO Manager
    """
    from main import toolkit_manager

    return {
        "status": "operational",
        "last_discovery": toolkit_manager.last_discovery,
        "last_security_scan": toolkit_manager.last_security_scan,
        "services_monitored": toolkit_manager.last_discovery['monitored_services'] if toolkit_manager.last_discovery else 0
    }


# ============================================================================
# EVENT INTELLIGENCE ROUTES
# ============================================================================

@router.post("/events/analyze")
async def analyze_event(request: EventAnalysisRequest):
    """
    Анализ события через AI Event Manager

    Анализирует важность события, паттерны использования и дает рекомендации
    """
    from main import ai_event_manager_client

    result = await ai_event_manager_client.analyze_event(
        event_name=request.event_name,
        publishers=request.publishers,
        subscribers=request.subscribers
    )

    if result:
        return {
            "status": "success",
            "data": result
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Event analysis failed"
        )


@router.get("/events/recommendations")
async def get_event_recommendations(scope: str = 'all'):
    """
    Получить AI-рекомендации по EventBus паттернам

    Args:
        scope: 'all', 'architecture', 'performance', 'reliability'

    Returns:
        Список AI-рекомендаций с приоритетами и confidence scores
    """
    from main import ai_event_manager_client

    recommendations = await ai_event_manager_client.get_recommendations(scope=scope)

    return {
        "status": "success",
        "recommendations": recommendations
    }


@router.get("/events/architecture/insights")
async def get_architecture_insights(timeframe: str = '7d'):
    """
    Получить insights по event-driven архитектуре

    Args:
        timeframe: Период анализа (1d, 7d, 30d)

    Returns:
        Аналитика по event-driven архитектуре
    """
    from main import ai_event_manager_client

    insights = await ai_event_manager_client.get_architecture_insights(timeframe=timeframe)

    return {
        "status": "success",
        "insights": insights
    }


@router.get("/events/learning/stats")
async def get_event_learning_stats():
    """
    Получить статистику обучения AI Event Manager

    Returns:
        Статистика обучения модели
    """
    from main import ai_event_manager_client

    stats = await ai_event_manager_client.get_learning_stats()

    return {
        "status": "success",
        "learning": stats
    }


@router.post("/events/feedback")
async def record_event_feedback(request: EventFeedbackRequest):
    """
    Записать feedback по рекомендации для обучения AI

    Args:
        suggestion_id: ID рекомендации
        decision: Решение (accepted, rejected, modified)
        outcome: Результат (success, failure, partial)

    Returns:
        Результат записи feedback и обновления learning модели
    """
    from main import ai_event_manager_client

    result = await ai_event_manager_client.record_feedback(
        suggestion_id=request.suggestion_id,
        decision=request.decision,
        outcome=request.outcome
    )

    return {
        "status": "success",
        "feedback": result
    }
