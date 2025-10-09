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
