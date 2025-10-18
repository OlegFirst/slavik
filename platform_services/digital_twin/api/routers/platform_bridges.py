"""
Platform Integration Bridges API
Endpoints for connecting to platform services via bridges
- SimulationService (Port 8095) - 7 simulation engines
- SystemBCM (Port 8050) - Business Continuity Management
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from core.integrations.simulation_service_bridge import SimulationServiceBridge
from core.integrations.system_bcm_bridge import SystemBCMBridge
from api.auth.dependencies import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# REQUEST/RESPONSE MODELS - SIMULATION SERVICE
# ============================================

class CreateSimulationRequest(BaseModel):
    """Create simulation request"""
    name: str = Field(..., description="Simulation name")
    simulation_type: str = Field(..., description="Type: monte_carlo, what_if, scenario, etc.")
    parameters: Dict[str, Any] = Field(..., description="Simulation parameters")


class MonteCarloRequest(BaseModel):
    """Monte Carlo simulation request"""
    name: str = Field(..., description="Simulation name")
    variables: Dict[str, Dict[str, Any]] = Field(..., description="Variables with distributions")
    iterations: int = Field(default=1000, ge=100, le=100000, description="Number of iterations")


class WhatIfRequest(BaseModel):
    """What-If analysis request"""
    name: str = Field(..., description="Analysis name")
    baseline: Dict[str, Any] = Field(..., description="Baseline scenario")
    scenarios: List[Dict[str, Any]] = Field(..., description="Alternative scenarios")


class ScenarioGenerateRequest(BaseModel):
    """AI scenario generation request"""
    category: str = Field(..., description="Scenario category: cyber, pandemic, natural_disaster, etc.")
    complexity: int = Field(default=3, ge=1, le=5, description="Complexity level 1-5")
    industry: Optional[str] = Field(None, description="Industry type")
    organization_size: Optional[str] = Field(None, description="Organization size: small, medium, large")


# REQUEST/RESPONSE MODELS - SYSTEM BCM
# ============================================

class TriggerRecoveryRequest(BaseModel):
    """Trigger recovery request"""
    service: str = Field(..., description="Service name")
    incident_type: str = Field(
        ...,
        description="Incident type: failure, degradation, connection_error, timeout, resource_exhaustion"
    )


# ============================================
# SIMULATION SERVICE ENDPOINTS
# ============================================

@router.get("/simulation-service/health")
async def get_simulation_service_health(
    current_user = Depends(get_current_active_user)
):
    """
    Check simulation_service health

    Returns health status and available engines.
    """
    try:
        async with SimulationServiceBridge() as bridge:
            is_healthy = await bridge.is_connected

            if not is_healthy:
                return {
                    "status": "unavailable",
                    "message": "simulation_service is not running (Port 8095)"
                }

            engines = await bridge.get_available_engines()

            return {
                "status": "healthy",
                "connected": True,
                "available_engines": len(engines),
                "engines": engines
            }

    except Exception as e:
        logger.error(f"Failed to check simulation service health: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/simulation-service/engines")
async def list_simulation_engines(
    current_user = Depends(get_current_active_user)
):
    """
    List available simulation engines

    Returns list of 7 simulation engines:
    - JaamSim - Discrete event simulation
    - Monte Carlo - Probabilistic analysis
    - Scenario - BCM scenario execution
    - What-If - Decision analysis
    - BCM Queue - Queue theory (M/M/c)
    - Advanced BIA - Multi-resource BIA
    - JaamSim Client - BCM exercise orchestrator
    """
    try:
        async with SimulationServiceBridge() as bridge:
            engines = await bridge.get_available_engines()

            return {
                "total": len(engines),
                "engines": engines
            }

    except Exception as e:
        logger.error(f"Failed to list engines: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulation-service/simulations")
async def create_simulation_via_bridge(
    request: CreateSimulationRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Create simulation via simulation_service

    Creates simulation in simulation_service and returns simulation ID.
    Use this to access 7 simulation engines.

    **Multi-tenancy:** Automatically scoped to user's organization.
    """
    try:
        user_id = current_user.get('id')
        tenant_id = current_user.get('tenant_id') or current_user.get('organization_id')

        logger.info(f"User {user_id} creating simulation via bridge: {request.name}")

        async with SimulationServiceBridge() as bridge:
            simulation = await bridge.create_simulation(
                name=request.name,
                simulation_type=request.simulation_type,
                parameters=request.parameters,
                tenant_id=tenant_id
            )

            return {
                "status": "created",
                "simulation": simulation,
                "message": "Simulation created in simulation_service"
            }

    except Exception as e:
        logger.error(f"Failed to create simulation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulation-service/simulations/{simulation_id}/execute")
async def execute_simulation_via_bridge(
    simulation_id: str,
    auto_start: bool = Query(True, description="Auto-start execution"),
    current_user = Depends(get_current_active_user)
):
    """
    Execute simulation

    Triggers simulation execution in simulation_service.
    """
    try:
        logger.info(f"Executing simulation: {simulation_id}")

        async with SimulationServiceBridge() as bridge:
            execution = await bridge.execute_simulation(
                simulation_id=simulation_id,
                auto_start=auto_start
            )

            return {
                "status": "executing",
                "execution": execution
            }

    except Exception as e:
        logger.error(f"Failed to execute simulation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/simulation-service/simulations/{simulation_id}/status")
async def get_simulation_status_via_bridge(
    simulation_id: str,
    current_user = Depends(get_current_active_user)
):
    """
    Get simulation status

    Returns current status of simulation.
    """
    try:
        async with SimulationServiceBridge() as bridge:
            status = await bridge.get_simulation_status(simulation_id)

            return status

    except Exception as e:
        logger.error(f"Failed to get simulation status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/simulation-service/executions/{execution_id}/results")
async def get_execution_results_via_bridge(
    execution_id: str,
    current_user = Depends(get_current_active_user)
):
    """
    Get execution results

    Returns results from completed simulation execution.
    """
    try:
        async with SimulationServiceBridge() as bridge:
            results = await bridge.get_execution_results(execution_id)

            return results

    except Exception as e:
        logger.error(f"Failed to get execution results: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulation-service/monte-carlo")
async def run_monte_carlo_via_bridge(
    request: MonteCarloRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Run Monte Carlo simulation (convenience endpoint)

    Runs complete Monte Carlo simulation and returns results.
    This is a convenience endpoint that creates, executes, and retrieves results.

    **Example variables:**
    ```json
    {
      "recovery_time": {
        "distribution": "normal",
        "mean": 48,
        "std": 12
      },
      "financial_impact": {
        "distribution": "uniform",
        "min": 100000,
        "max": 500000
      }
    }
    ```
    """
    try:
        user_id = current_user.get('id')
        tenant_id = current_user.get('tenant_id') or current_user.get('organization_id')

        logger.info(f"User {user_id} running Monte Carlo simulation")

        async with SimulationServiceBridge() as bridge:
            results = await bridge.run_monte_carlo_simulation(
                name=request.name,
                variables=request.variables,
                iterations=request.iterations,
                tenant_id=tenant_id
            )

            return {
                "status": "completed",
                "results": results
            }

    except Exception as e:
        logger.error(f"Failed to run Monte Carlo: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulation-service/what-if")
async def run_what_if_via_bridge(
    request: WhatIfRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Run What-If analysis (convenience endpoint)

    Compares baseline scenario with alternatives.
    Returns comparative analysis.

    **Example:**
    ```json
    {
      "name": "Recovery Strategy Comparison",
      "baseline": {
        "strategy": "manual_recovery",
        "rto_hours": 48
      },
      "scenarios": [
        {
          "strategy": "automated_recovery",
          "rto_hours": 4
        },
        {
          "strategy": "hot_standby",
          "rto_hours": 0.5
        }
      ]
    }
    ```
    """
    try:
        user_id = current_user.get('id')
        tenant_id = current_user.get('tenant_id') or current_user.get('organization_id')

        logger.info(f"User {user_id} running What-If analysis")

        async with SimulationServiceBridge() as bridge:
            results = await bridge.run_what_if_analysis(
                name=request.name,
                baseline=request.baseline,
                scenarios=request.scenarios,
                tenant_id=tenant_id
            )

            return {
                "status": "completed",
                "results": results
            }

    except Exception as e:
        logger.error(f"Failed to run What-If: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulation-service/scenarios/generate")
async def generate_scenario_via_bridge(
    request: ScenarioGenerateRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Generate AI-powered BCM scenario

    Uses simulation_service AI to generate contextual BCM scenarios.

    **Categories:**
    - cyber: Cyberattack scenarios
    - pandemic: Pandemic/health crisis
    - natural_disaster: Earthquakes, floods, hurricanes
    - infrastructure: Power, network, facility failures
    - supply_chain: Supply chain disruptions
    - personnel: Key personnel loss
    """
    try:
        user_id = current_user.get('id')

        logger.info(f"User {user_id} generating AI scenario: {request.category}")

        async with SimulationServiceBridge() as bridge:
            scenario = await bridge.generate_scenario(
                category=request.category,
                complexity=request.complexity,
                industry=request.industry,
                organization_size=request.organization_size
            )

            return {
                "status": "generated",
                "scenario": scenario
            }

    except Exception as e:
        logger.error(f"Failed to generate scenario: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/simulation-service/scenarios/search")
async def search_scenarios_via_bridge(
    query: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=100),
    current_user = Depends(get_current_active_user)
):
    """
    Search scenario library

    Searches simulation_service scenario library.
    """
    try:
        async with SimulationServiceBridge() as bridge:
            scenarios = await bridge.search_scenarios(
                query=query,
                category=category,
                limit=limit
            )

            return {
                "total": len(scenarios),
                "scenarios": scenarios
            }

    except Exception as e:
        logger.error(f"Failed to search scenarios: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SYSTEM BCM ENDPOINTS
# ============================================

@router.get("/system-bcm/health")
async def get_system_bcm_health(
    current_user = Depends(get_current_active_user)
):
    """
    Check System BCM service health

    Returns BCM service health and running status.
    """
    try:
        async with SystemBCMBridge() as bridge:
            is_healthy = await bridge.is_healthy()

            if not is_healthy:
                return {
                    "status": "unavailable",
                    "message": "System BCM service is not running (Port 8050)"
                }

            health = await bridge.get_health()

            return {
                "status": "healthy",
                "connected": True,
                "bcm_data": health
            }

    except Exception as e:
        logger.error(f"Failed to check System BCM health: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/system-bcm/status")
async def get_system_bcm_status(
    current_user = Depends(get_current_active_user)
):
    """
    Get detailed System BCM status

    Returns comprehensive BCM status including:
    - Running status
    - Cycle count
    - Last cycle result
    - Total improvements applied
    """
    try:
        async with SystemBCMBridge() as bridge:
            status = await bridge.get_status()

            return status

    except Exception as e:
        logger.error(f"Failed to get BCM status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system-bcm/cycle/trigger")
async def trigger_bcm_cycle(
    current_user = Depends(get_current_active_user)
):
    """
    Manually trigger BCM cycle

    **BCM Cycle includes:**
    1. Health Check - Check all services
    2. Analyze - Identify issues
    3. Improve - Apply improvements
    4. Verify - Verify improvements worked

    **Use when:**
    - You want to force immediate BCM check
    - After platform changes
    - During incident response

    **Permission:** Requires admin or manager role.
    """
    try:
        user_id = current_user.get('id')
        role = current_user.get('role', 'user')

        # Permission check
        if role not in ['admin', 'manager']:
            raise HTTPException(
                status_code=403,
                detail="Permission denied. BCM cycle triggering requires admin or manager role."
            )

        logger.info(f"User {user_id} ({role}) triggering BCM cycle")

        async with SystemBCMBridge() as bridge:
            result = await bridge.trigger_cycle()

            return {
                "status": "completed",
                "cycle_result": result,
                "triggered_by": user_id
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger BCM cycle: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system-bcm/recovery/trigger")
async def trigger_recovery_via_bridge(
    request: TriggerRecoveryRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Manually trigger recovery for a service

    **Incident types:**
    - failure: Complete service failure
    - degradation: Performance degradation
    - connection_error: Connection issues
    - timeout: Timeout issues
    - resource_exhaustion: Resource issues

    **Permission:** Requires admin or manager role.
    """
    try:
        user_id = current_user.get('id')
        role = current_user.get('role', 'user')

        # Permission check
        if role not in ['admin', 'manager']:
            raise HTTPException(
                status_code=403,
                detail="Permission denied. Recovery triggering requires admin or manager role."
            )

        logger.info(
            f"User {user_id} ({role}) triggering recovery for "
            f"{request.service} ({request.incident_type})"
        )

        async with SystemBCMBridge() as bridge:
            result = await bridge.trigger_recovery(
                service=request.service,
                incident_type=request.incident_type
            )

            return {
                "status": "triggered",
                "recovery_result": result,
                "triggered_by": user_id
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger recovery: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-bcm/platform-continuity")
async def get_platform_continuity_status(
    current_user = Depends(get_current_active_user)
):
    """
    Get overall platform business continuity status

    Returns comprehensive continuity status including:
    - BCM running status
    - Last cycle information
    - Total cycles executed
    - Improvements applied
    - Platform health assessment

    **Use for:**
    - Executive dashboard
    - Compliance reporting
    - BCM maturity assessment
    """
    try:
        logger.info(f"User {current_user.get('id')} requesting platform continuity status")

        async with SystemBCMBridge() as bridge:
            status = await bridge.get_platform_continuity_status()

            return status

    except Exception as e:
        logger.error(f"Failed to get platform continuity status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-bcm/metrics")
async def get_bcm_metrics(
    current_user = Depends(get_current_active_user)
):
    """
    Get BCM Prometheus metrics

    Returns metrics in Prometheus format for monitoring integration.
    """
    try:
        async with SystemBCMBridge() as bridge:
            metrics = await bridge.get_metrics()

            return {
                "format": "prometheus",
                "metrics": metrics
            }

    except Exception as e:
        logger.error(f"Failed to get BCM metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# COMBINED HEALTH CHECK
# ============================================

@router.get("/health")
async def check_all_bridges_health(
    current_user = Depends(get_current_active_user)
):
    """
    Check health of all platform integration bridges

    Returns health status of:
    - simulation_service bridge
    - system_bcm bridge

    Useful for platform health dashboard.
    """
    try:
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "bridges": {}
        }

        # Check simulation_service
        try:
            async with SimulationServiceBridge() as sim_bridge:
                is_connected = sim_bridge.is_connected
                health_status["bridges"]["simulation_service"] = {
                    "status": "healthy" if is_connected else "unavailable",
                    "port": 8095,
                    "connected": is_connected
                }
        except Exception as e:
            health_status["bridges"]["simulation_service"] = {
                "status": "error",
                "error": str(e)
            }

        # Check system_bcm
        try:
            async with SystemBCMBridge() as bcm_bridge:
                is_healthy = await bcm_bridge.is_healthy()
                health_status["bridges"]["system_bcm"] = {
                    "status": "healthy" if is_healthy else "unavailable",
                    "port": 8050,
                    "healthy": is_healthy
                }
        except Exception as e:
            health_status["bridges"]["system_bcm"] = {
                "status": "error",
                "error": str(e)
            }

        return health_status

    except Exception as e:
        logger.error(f"Failed to check bridges health: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
