"""
Simulation Adapter for BCM Platform

Integrates with simulation engines for business continuity exercise automation:
- JaamSim for discrete event simulation
- AnyLogic PLE for system dynamics
- Custom simulation scenarios for BCM exercises
- Automated metrics collection and analysis
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

from config import Config
from models import (
    SimulationRequest, SimulationResult, ExerciseScenario,
    SimulationStatus, ExerciseMetrics
)
# from services.eventbus import EventBusService
# from services.simulation_engine import SimulationEngine
# from services.processor import SimulationProcessor

# Simplified simulation adapter - basic functionality

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BCM Simulation Adapter",
    description="Business continuity exercise simulation and automation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simplified services
config = Config()
simulation_status = "ready"

@app.on_event("startup")
async def startup():
    """Initialize services and event subscriptions"""
    global eventbus_service, simulation_engine, processor
    
    logger.info("Starting Simulation Adapter...")
    
    # Initialize services
    eventbus_service = EventBusService(config)
    simulation_engine = SimulationEngine(config)
    processor = SimulationProcessor(eventbus_service, simulation_engine)
    
    # Connect to services
    await eventbus_service.connect()
    await simulation_engine.initialize()
    
    # Subscribe to relevant events
    await eventbus_service.subscribe("bcm.exercise.scheduled", processor.handle_exercise_scheduled)
    await eventbus_service.subscribe("bcm.exercise.started", processor.handle_exercise_started)
    await eventbus_service.subscribe("bcm.simulation.requested", processor.handle_simulation_requested)
    
    logger.info("Simulation Adapter started successfully")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    if eventbus_service:
        await eventbus_service.disconnect()
    if simulation_engine:
        await simulation_engine.shutdown()
    logger.info("Simulation Adapter shut down")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    dependencies = {
        "eventbus": "healthy" if eventbus_service and eventbus_service.is_connected() else "unhealthy",
        "simulation_engine": "healthy" if simulation_engine and simulation_engine.is_ready() else "unhealthy"
    }
    
    status = "healthy" if all(dep == "healthy" for dep in dependencies.values()) else "unhealthy"
    
    return {
        "status": status,
        "service": "simulation-adapter",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": dependencies,
        "engine": config.SIMULATION_ENGINE,
        "running_simulations": len(simulation_engine.active_simulations) if simulation_engine else 0
    }

@app.post("/api/simulations/start")
async def start_simulation(simulation_request: SimulationRequest, background_tasks: BackgroundTasks):
    """Start a new simulation"""
    try:
        # Validate simulation request
        if not await simulation_engine.validate_scenario(simulation_request.scenario):
            raise HTTPException(status_code=400, detail="Invalid simulation scenario")
        
        # Start simulation in background
        simulation_id = await simulation_engine.start_simulation(simulation_request)
        
        if simulation_id:
            # Publish simulation started event
            await eventbus_service.publish({
                "event_type": "bcm.simulation.started",
                "tenant_id": simulation_request.tenant_id,
                "data": {
                    "simulation_id": simulation_id,
                    "exercise_id": simulation_request.exercise_id,
                    "scenario": simulation_request.scenario.name,
                    "engine": config.SIMULATION_ENGINE,
                    "estimated_duration": simulation_request.scenario.duration_minutes
                }
            })
            
            return {
                "status": "success",
                "simulation_id": simulation_id,
                "message": "Simulation started successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to start simulation")
            
    except Exception as e:
        logger.error(f"Failed to start simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/simulations/{simulation_id}/status")
async def get_simulation_status(simulation_id: str, tenant_id: str):
    """Get simulation status and progress"""
    try:
        status = await simulation_engine.get_simulation_status(simulation_id, tenant_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Simulation not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get simulation status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/simulations/{simulation_id}/results")
async def get_simulation_results(simulation_id: str, tenant_id: str):
    """Get simulation results and metrics"""
    try:
        results = await simulation_engine.get_simulation_results(simulation_id, tenant_id)
        
        if not results:
            raise HTTPException(status_code=404, detail="Simulation results not found")
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get simulation results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/simulations/{simulation_id}/stop")
async def stop_simulation(simulation_id: str, tenant_id: str):
    """Stop running simulation"""
    try:
        success = await simulation_engine.stop_simulation(simulation_id, tenant_id)
        
        if success:
            # Publish simulation stopped event
            await eventbus_service.publish({
                "event_type": "bcm.simulation.stopped",
                "tenant_id": tenant_id,
                "data": {
                    "simulation_id": simulation_id,
                    "stopped_manually": True,
                    "stopped_at": datetime.utcnow().isoformat()
                }
            })
            
            return {"status": "success", "message": "Simulation stopped"}
        else:
            raise HTTPException(status_code=404, detail="Simulation not found or already stopped")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scenarios")
async def list_scenarios():
    """List available simulation scenarios"""
    try:
        scenarios = await simulation_engine.get_available_scenarios()
        return {"scenarios": scenarios}
        
    except Exception as e:
        logger.error(f"Failed to list scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scenarios/{scenario_name}")
async def get_scenario_details(scenario_name: str):
    """Get detailed information about a scenario"""
    try:
        scenario = await simulation_engine.get_scenario_details(scenario_name)
        
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        return scenario
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get scenario details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scenarios/validate")
async def validate_scenario(scenario: ExerciseScenario):
    """Validate simulation scenario configuration"""
    try:
        is_valid = await simulation_engine.validate_scenario(scenario)
        validation_errors = await simulation_engine.get_validation_errors(scenario)
        
        return {
            "valid": is_valid,
            "errors": validation_errors,
            "scenario_name": scenario.name
        }
        
    except Exception as e:
        logger.error(f"Failed to validate scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/exercises/{exercise_id}/simulations")
async def get_exercise_simulations(exercise_id: str, tenant_id: str):
    """Get all simulations for an exercise"""
    try:
        simulations = await simulation_engine.get_exercise_simulations(exercise_id, tenant_id)
        
        return {
            "exercise_id": exercise_id,
            "simulations": simulations,
            "total_count": len(simulations)
        }
        
    except Exception as e:
        logger.error(f"Failed to get exercise simulations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics/{tenant_id}")
async def get_simulation_metrics(tenant_id: str, period: str = "30d"):
    """Get simulation metrics for tenant"""
    try:
        metrics = await simulation_engine.get_simulation_metrics(tenant_id, period)
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get simulation metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scenarios/custom")
async def create_custom_scenario(scenario_data: Dict[str, Any]):
    """Create custom simulation scenario"""
    try:
        scenario_id = await simulation_engine.create_custom_scenario(scenario_data)
        
        if scenario_id:
            return {
                "status": "success",
                "scenario_id": scenario_id,
                "message": "Custom scenario created successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create custom scenario")
            
    except Exception as e:
        logger.error(f"Failed to create custom scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/templates")
async def get_scenario_templates():
    """Get available scenario templates"""
    try:
        templates = await simulation_engine.get_scenario_templates()
        
        return {
            "templates": templates,
            "categories": list(set(t.get("category", "general") for t in templates))
        }
        
    except Exception as e:
        logger.error(f"Failed to get scenario templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/batch/simulations")
async def run_batch_simulations(batch_request: Dict[str, Any]):
    """Run multiple simulations in batch"""
    try:
        batch_id = await simulation_engine.start_batch_simulations(batch_request)
        
        if batch_id:
            return {
                "status": "success",
                "batch_id": batch_id,
                "message": "Batch simulations started"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to start batch simulations")
            
    except Exception as e:
        logger.error(f"Failed to start batch simulations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/{simulation_id}")
async def generate_simulation_report(simulation_id: str, tenant_id: str, format: str = "json"):
    """Generate simulation report"""
    try:
        report = await simulation_engine.generate_report(simulation_id, tenant_id, format)
        
        if not report:
            raise HTTPException(status_code=404, detail="Simulation not found")
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8005,
        log_level="info"
    )
