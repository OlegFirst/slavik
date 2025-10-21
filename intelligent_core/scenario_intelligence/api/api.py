"""
Scenario Intelligence API

REST API для выполнения и управления сценариями
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import os
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Scenario Intelligence API",
    description="Execute and manage scenarios for BCM platform",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ScenarioExecutionRequest(BaseModel):
    scenario_id: str
    context: Optional[Dict[str, Any]] = {}

class ScenarioRegisterRequest(BaseModel):
    scenario: Dict[str, Any]


# Endpoints

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "scenario-intelligence",
        "version": "1.0.0"
    }


@app.post("/scenarios/execute")
async def execute_scenario(request: ScenarioExecutionRequest):
    """
    Выполнить сценарий по ID

    Args:
        scenario_id: ID сценария
        context: Контекст выполнения

    Returns:
        Результаты выполнения
    """

    try:
        from storage.registry import global_registry
        from engines.scenario_engine import ScenarioEngine

        # Загрузить сценарий
        scenario = await global_registry.get_scenario_by_id(request.scenario_id)

        if not scenario:
            raise HTTPException(
                status_code=404,
                detail=f"Scenario {request.scenario_id} not found"
            )

        # Выполнить
        engine = ScenarioEngine()
        result = await engine.execute_scenario(scenario, request.context)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute scenario: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenarios/register")
async def register_scenario(request: ScenarioRegisterRequest):
    """
    Зарегистрировать новый сценарий

    Args:
        scenario: Сценарий в формате YAML dict

    Returns:
        Статус регистрации
    """

    try:
        from storage.registry import global_registry

        # Зарегистрировать
        success = await global_registry.register(request.scenario)

        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to register scenario"
            )

        scenario_id = request.scenario.get('meta', {}).get('id', 'unknown')

        return {
            "status": "registered",
            "scenario_id": scenario_id
        }

    except Exception as e:
        logger.error(f"Failed to register scenario: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str):
    """
    Получить сценарий по ID

    Args:
        scenario_id: ID сценария

    Returns:
        Сценарий
    """

    try:
        from storage.registry import global_registry

        scenario = await global_registry.get_scenario_by_id(scenario_id)

        if not scenario:
            raise HTTPException(
                status_code=404,
                detail=f"Scenario {scenario_id} not found"
            )

        return {
            "scenario_id": scenario_id,
            "scenario": scenario
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get scenario: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scenarios")
async def list_scenarios(
    level: Optional[int] = None,
    type: Optional[str] = None,
    module: Optional[str] = None
):
    """
    Получить список сценариев

    Args:
        level: Фильтр по level
        type: Фильтр по type
        module: Фильтр по module

    Returns:
        Список сценариев
    """

    try:
        from storage.registry import global_registry

        scenarios = await global_registry.find_scenarios(
            level=level,
            type=type,
            module=module
        )

        return {
            "count": len(scenarios),
            "scenarios": scenarios
        }

    except Exception as e:
        logger.error(f"Failed to list scenarios: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scenarios/statistics")
async def get_statistics():
    """
    Получить статистику по всем сценариям

    Returns:
        Статистика
    """

    try:
        from storage.registry import global_registry
        from learning.scenario_learner import global_learner

        registry_stats = await global_registry.get_statistics()
        execution_stats = await global_learner.get_all_statistics()

        return {
            "registry": registry_stats,
            "executions": execution_stats
        }

    except Exception as e:
        logger.error(f"Failed to get statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scenarios/{scenario_id}/statistics")
async def get_scenario_statistics(scenario_id: str):
    """
    Получить статистику по конкретному сценарию

    Args:
        scenario_id: ID сценария

    Returns:
        Статистика
    """

    try:
        from learning.scenario_learner import global_learner

        stats = await global_learner.get_statistics(scenario_id)

        if not stats:
            raise HTTPException(
                status_code=404,
                detail=f"No statistics for scenario {scenario_id}"
            )

        return stats

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scenarios/{scenario_id}/executions")
async def get_scenario_executions(scenario_id: str, limit: int = 10):
    """
    Получить последние executions сценария

    Args:
        scenario_id: ID сценария
        limit: Максимум результатов

    Returns:
        Список executions
    """

    try:
        from learning.scenario_learner import global_learner

        executions = await global_learner.get_recent_executions(
            scenario_id=scenario_id,
            limit=limit
        )

        return {
            "scenario_id": scenario_id,
            "count": len(executions),
            "executions": executions
        }

    except Exception as e:
        logger.error(f"Failed to get executions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    PORT = int(os.getenv("SCENARIO_INTELLIGENCE_PORT", "8090"))
    HOST = os.getenv("SCENARIO_INTELLIGENCE_HOST", "0.0.0.0")

    logger.info(f" Starting Scenario Intelligence API on {HOST}:{PORT}")

    uvicorn.run(
        "api:app",
        host=HOST,
        port=PORT,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )
