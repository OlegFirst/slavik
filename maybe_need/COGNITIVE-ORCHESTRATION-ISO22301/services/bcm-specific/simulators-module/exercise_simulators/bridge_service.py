# -*- coding: utf-8 -*-
"""
Exercise Simulators Bridge Service for BCM Platform
Provides unified API for JaamSim and NICS integrations for BCM exercises
"""
import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import structlog
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn
from contextlib import asynccontextmanager

from jaamsim_client import JaamSimClient, ExerciseScenario, BCMExerciseSimulator
from nics_client import NICSClient, BCMNICSIntegration, NICSIncident, NICSRole

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Pydantic models for API
class BCMExerciseRequest(BaseModel):
    name: str
    description: str
    scenario_type: str  # tabletop, functional, simulation, nics_command
    company_id: str
    duration_minutes: int = 120
    participants: List[str] = []
    objectives: List[str] = []
    success_criteria: List[str] = []
    injects: List[Dict[str, Any]] = []
    location: Optional[Dict[str, Any]] = None
    commander: Optional[str] = None
    priority: str = "medium"
    simulation_engine: str = "jaamsim"  # jaamsim, nics, hybrid

class ExerciseInjectRequest(BaseModel):
    exercise_id: str
    title: str
    description: str
    event_type: str  # failure, recovery, communication, decision
    target_entity: Optional[str] = None
    parameters: Dict[str, Any] = {}
    requires_response: bool = True
    delay_minutes: Optional[float] = None

class ExerciseUpdateRequest(BaseModel):
    exercise_id: str
    status: Optional[str] = None
    participants: Optional[List[str]] = None
    notes: Optional[str] = None

class ConnectionManager:
    """WebSocket connection manager for real-time exercise updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, exercise_id: str):
        await websocket.accept()
        if exercise_id not in self.active_connections:
            self.active_connections[exercise_id] = []
        self.active_connections[exercise_id].append(websocket)
        logger.info(f"WebSocket connected for exercise: {exercise_id}")
    
    def disconnect(self, websocket: WebSocket, exercise_id: str):
        if exercise_id in self.active_connections:
            self.active_connections[exercise_id].remove(websocket)
            if not self.active_connections[exercise_id]:
                del self.active_connections[exercise_id]
        logger.info(f"WebSocket disconnected for exercise: {exercise_id}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast_to_exercise(self, exercise_id: str, message: dict):
        if exercise_id in self.active_connections:
            message_json = json.dumps(message)
            disconnected = []
            for websocket in self.active_connections[exercise_id]:
                try:
                    await websocket.send_text(message_json)
                except:
                    disconnected.append(websocket)
            
            # Remove disconnected websockets
            for ws in disconnected:
                self.active_connections[exercise_id].remove(ws)

# Security
security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key for requests"""
    expected_key = os.getenv('BRIDGE_API_KEY')
    if not expected_key or credentials.credentials != expected_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return credentials.credentials

# Global variables for clients
jaamsim_client: Optional[JaamSimClient] = None
nics_client: Optional[NICSClient] = None
bcm_simulator: Optional[BCMExerciseSimulator] = None
nics_integration: Optional[BCMNICSIntegration] = None
connection_manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global jaamsim_client, nics_client, bcm_simulator, nics_integration
    
    logger.info("Initializing Exercise Simulators Bridge Service")
    
    # Initialize JaamSim client
    jaamsim_path = os.getenv('JAAMSIM_PATH', '/opt/jaamsim')
    working_dir = os.getenv('SIMULATORS_WORKING_DIR', '/tmp/bcm_exercises')
    
    jaamsim_client = JaamSimClient(jaamsim_path, working_dir)
    bcm_simulator = BCMExerciseSimulator(jaamsim_client)
    
    # Initialize NICS client if configured
    nics_url = os.getenv('NICS_URL')
    nics_api_key = os.getenv('NICS_API_KEY')
    
    if nics_url and nics_api_key:
        nics_client = NICSClient(nics_url, nics_api_key)
        bcm_api_url = os.getenv('BCM_API_URL', 'http://localhost:8069')
        bcm_api_key = os.getenv('BCM_API_KEY')
        
        nics_integration = BCMNICSIntegration(nics_client, bcm_api_url, bcm_api_key)
        logger.info("NICS integration enabled")
    else:
        logger.info("NICS integration disabled - missing configuration")
    
    logger.info("Bridge service initialized successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Exercise Simulators Bridge Service")

# FastAPI app
app = FastAPI(
    title="Exercise Simulators Bridge Service",
    description="Unified API for BCM exercise simulation engines (JaamSim, NICS)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "jaamsim": jaamsim_client is not None,
            "nics": nics_client is not None,
            "bcm_simulator": bcm_simulator is not None,
            "nics_integration": nics_integration is not None
        }
    }

@app.post("/api/v1/exercises/create")
async def create_exercise(
    request: BCMExerciseRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Create BCM exercise using specified simulation engine"""
    try:
        logger.info(f"Creating BCM exercise: {request.name}")
        
        exercise_scenario = ExerciseScenario(
            id=f"bcm_ex_{int(datetime.now().timestamp())}",
            name=request.name,
            description=request.description,
            scenario_type=request.scenario_type,
            duration_minutes=request.duration_minutes,
            participants=request.participants,
            objectives=request.objectives,
            injects=[],  # Will be added via inject endpoint
            success_criteria=request.success_criteria,
            resources_required=[],
            company_id=request.company_id
        )
        
        if request.simulation_engine == "jaamsim":
            # Create JaamSim exercise
            background_tasks.add_task(
                _create_jaamsim_exercise_task, exercise_scenario
            )
        elif request.simulation_engine == "nics":
            # Create NICS exercise
            if not nics_integration:
                raise HTTPException(status_code=503, detail="NICS integration not available")
            
            background_tasks.add_task(
                _create_nics_exercise_task, exercise_scenario, request.dict()
            )
        elif request.simulation_engine == "hybrid":
            # Create both JaamSim and NICS
            background_tasks.add_task(
                _create_hybrid_exercise_task, exercise_scenario, request.dict()
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid simulation engine")
        
        return {
            "status": "accepted",
            "message": "Exercise creation initiated",
            "exercise_id": exercise_scenario.id,
            "simulation_engine": request.simulation_engine
        }
        
    except Exception as e:
        logger.error(f"Failed to create exercise: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/exercises/{exercise_id}/start")
async def start_exercise(
    exercise_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Start BCM exercise execution"""
    try:
        logger.info(f"Starting exercise: {exercise_id}")
        
        # Check JaamSim exercises
        if bcm_simulator:
            try:
                status = bcm_simulator.get_exercise_status(exercise_id)
                if status["status"] == "prepared":
                    # Execute JaamSim exercise
                    result = await bcm_simulator.execute_exercise(exercise_id)
                    
                    # Broadcast start event
                    await connection_manager.broadcast_to_exercise(exercise_id, {
                        "type": "exercise_started",
                        "exercise_id": exercise_id,
                        "timestamp": datetime.now().isoformat(),
                        "engine": "jaamsim"
                    })
                    
                    return {
                        "status": "started",
                        "exercise_id": exercise_id,
                        "engine": "jaamsim",
                        "result": result.__dict__
                    }
            except ValueError:
                pass  # Exercise not in JaamSim
        
        # Check NICS exercises
        if nics_integration:
            try:
                status = nics_integration.get_exercise_status(exercise_id)
                if status["status"] == "active":
                    # NICS exercise is already running
                    await connection_manager.broadcast_to_exercise(exercise_id, {
                        "type": "exercise_started",
                        "exercise_id": exercise_id,
                        "timestamp": datetime.now().isoformat(),
                        "engine": "nics"
                    })
                    
                    return {
                        "status": "started",
                        "exercise_id": exercise_id,
                        "engine": "nics",
                        "nics_incident_id": status.get("nics_incident_id")
                    }
            except ValueError:
                pass  # Exercise not in NICS
        
        raise HTTPException(status_code=404, detail="Exercise not found or not ready")
        
    except Exception as e:
        logger.error(f"Failed to start exercise: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/exercises/{exercise_id}/inject")
async def inject_event(
    exercise_id: str,
    request: ExerciseInjectRequest,
    api_key: str = Depends(verify_api_key)
):
    """Inject event into running exercise"""
    try:
        logger.info(f"Injecting event into exercise {exercise_id}: {request.title}")
        
        # Inject into NICS if available
        if nics_integration:
            try:
                success = await nics_integration.inject_exercise_event(
                    exercise_id, 
                    {
                        "title": request.title,
                        "description": request.description,
                        "event_type": request.event_type,
                        "requires_response": request.requires_response
                    }
                )
                
                if success:
                    # Broadcast inject event
                    await connection_manager.broadcast_to_exercise(exercise_id, {
                        "type": "event_injected",
                        "exercise_id": exercise_id,
                        "inject": request.dict(),
                        "timestamp": datetime.now().isoformat(),
                        "engine": "nics"
                    })
                    
                    return {
                        "status": "injected",
                        "exercise_id": exercise_id,
                        "inject_id": request.title,
                        "engine": "nics"
                    }
            except ValueError:
                pass  # Exercise not in NICS
        
        # For JaamSim exercises, events are predefined in scenario
        # Real-time injection would require custom JaamSim modifications
        
        raise HTTPException(status_code=404, detail="Exercise not found or injection not supported")
        
    except Exception as e:
        logger.error(f"Failed to inject event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/exercises/{exercise_id}/status")
async def get_exercise_status(
    exercise_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get exercise status and progress"""
    try:
        # Check JaamSim exercises
        if bcm_simulator:
            try:
                status = bcm_simulator.get_exercise_status(exercise_id)
                return {
                    "exercise_id": exercise_id,
                    "engine": "jaamsim",
                    "status": status["status"],
                    "scenario": status["scenario"].__dict__,
                    "created_at": status["created_at"].isoformat(),
                    "started_at": status.get("started_at", {}).isoformat() if status.get("started_at") else None,
                    "completed_at": status.get("completed_at", {}).isoformat() if status.get("completed_at") else None
                }
            except ValueError:
                pass
        
        # Check NICS exercises
        if nics_integration:
            try:
                status = nics_integration.get_exercise_status(exercise_id)
                return {
                    "exercise_id": exercise_id,
                    "engine": "nics",
                    "status": status["status"],
                    "nics_incident_id": status.get("nics_incident_id"),
                    "scenario": status["scenario"],
                    "start_time": status["start_time"].isoformat(),
                    "events_count": len(status["events"])
                }
            except ValueError:
                pass
        
        raise HTTPException(status_code=404, detail="Exercise not found")
        
    except Exception as e:
        logger.error(f"Failed to get exercise status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/exercises/{exercise_id}/complete")
async def complete_exercise(
    exercise_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Complete and close exercise"""
    try:
        logger.info(f"Completing exercise: {exercise_id}")
        
        # Complete NICS exercise
        if nics_integration:
            try:
                report = await nics_integration.complete_exercise(exercise_id)
                
                # Broadcast completion
                await connection_manager.broadcast_to_exercise(exercise_id, {
                    "type": "exercise_completed",
                    "exercise_id": exercise_id,
                    "timestamp": datetime.now().isoformat(),
                    "engine": "nics",
                    "report": report
                })
                
                return {
                    "status": "completed",
                    "exercise_id": exercise_id,
                    "engine": "nics",
                    "report": report
                }
            except ValueError:
                pass
        
        # Complete JaamSim exercise
        if bcm_simulator:
            try:
                # JaamSim exercises complete automatically
                # Just clean up resources
                bcm_simulator.cleanup_exercise(exercise_id)
                
                await connection_manager.broadcast_to_exercise(exercise_id, {
                    "type": "exercise_completed",
                    "exercise_id": exercise_id,
                    "timestamp": datetime.now().isoformat(),
                    "engine": "jaamsim"
                })
                
                return {
                    "status": "completed",
                    "exercise_id": exercise_id,
                    "engine": "jaamsim"
                }
            except ValueError:
                pass
        
        raise HTTPException(status_code=404, detail="Exercise not found")
        
    except Exception as e:
        logger.error(f"Failed to complete exercise: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/exercises")
async def list_exercises(
    api_key: str = Depends(verify_api_key)
):
    """List all active exercises"""
    try:
        exercises = []
        
        # Get JaamSim exercises
        if bcm_simulator:
            jaamsim_exercises = bcm_simulator.list_active_exercises()
            for ex in jaamsim_exercises:
                exercises.append({
                    "exercise_id": ex["scenario"].id,
                    "name": ex["scenario"].name,
                    "engine": "jaamsim",
                    "status": ex["status"],
                    "created_at": ex["created_at"].isoformat()
                })
        
        # Get NICS exercises
        if nics_integration:
            nics_exercises = nics_integration.list_active_exercises()
            for ex in nics_exercises:
                exercises.append({
                    "exercise_id": ex["scenario"]["id"],
                    "name": ex["scenario"]["name"],
                    "engine": "nics",
                    "status": ex["status"],
                    "start_time": ex["start_time"].isoformat()
                })
        
        return {
            "exercises": exercises,
            "total": len(exercises)
        }
        
    except Exception as e:
        logger.error(f"Failed to list exercises: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{exercise_id}")
async def websocket_endpoint(websocket: WebSocket, exercise_id: str):
    """WebSocket endpoint for real-time exercise updates"""
    await connection_manager.connect(websocket, exercise_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back any messages from clients
            await connection_manager.send_personal_message(
                f"Message received: {data}", websocket
            )
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, exercise_id)

@app.get("/api/v1/metrics")
async def get_metrics(api_key: str = Depends(verify_api_key)):
    """Get service metrics"""
    try:
        active_jaamsim = len(bcm_simulator.list_active_exercises()) if bcm_simulator else 0
        active_nics = len(nics_integration.list_active_exercises()) if nics_integration else 0
        
        metrics = {
            "service": "exercise-simulators-bridge",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "active_exercises": {
                "jaamsim": active_jaamsim,
                "nics": active_nics,
                "total": active_jaamsim + active_nics
            },
            "websocket_connections": sum(len(conns) for conns in connection_manager.active_connections.values()),
            "engines": {
                "jaamsim_available": jaamsim_client is not None,
                "nics_available": nics_client is not None
            }
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background tasks
async def _create_jaamsim_exercise_task(exercise_scenario: ExerciseScenario):
    """Background task to create JaamSim exercise"""
    try:
        await bcm_simulator.create_bcm_exercise(exercise_scenario)
        logger.info(f"JaamSim exercise created: {exercise_scenario.id}")
    except Exception as e:
        logger.error(f"Failed to create JaamSim exercise: {e}")

async def _create_nics_exercise_task(exercise_scenario: ExerciseScenario, request_data: dict):
    """Background task to create NICS exercise"""
    try:
        async with nics_client:
            await nics_client.authenticate()
            await nics_integration.create_bcm_exercise_in_nics(request_data)
        logger.info(f"NICS exercise created: {exercise_scenario.id}")
    except Exception as e:
        logger.error(f"Failed to create NICS exercise: {e}")

async def _create_hybrid_exercise_task(exercise_scenario: ExerciseScenario, request_data: dict):
    """Background task to create hybrid exercise"""
    try:
        # Create both JaamSim and NICS exercises
        await _create_jaamsim_exercise_task(exercise_scenario)
        if nics_integration:
            await _create_nics_exercise_task(exercise_scenario, request_data)
        logger.info(f"Hybrid exercise created: {exercise_scenario.id}")
    except Exception as e:
        logger.error(f"Failed to create hybrid exercise: {e}")

if __name__ == "__main__":
    # Load configuration
    port = int(os.getenv('PORT', '8094'))
    host = os.getenv('HOST', '0.0.0.0')
    log_level = os.getenv('LOG_LEVEL', 'info').lower()
    
    # Run server
    uvicorn.run(
        "bridge_service:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=False,
        access_log=True
    )
