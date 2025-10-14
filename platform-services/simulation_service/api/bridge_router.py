"""
Exercise Bridge Router
======================

Unified API for managing BCM exercises across multiple simulation engines
(JaamSim, NICS, Hybrid).

Provides:
- Exercise lifecycle management
- Real-time WebSocket updates
- Multi-engine orchestration
- Background task processing

Adapted from: /simulation/exercise_simulators/bridge_service.py
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from pydantic import BaseModel, Field

from ..engines.jaamsim_engine import JaamSimEngine
from ..integration.nics_client import NICSClient, BCMNICSIntegration
from ..core.scenario_flow_manager import ScenarioFlowManager
from ..core.ai_scenario_generator import ScenarioParameters

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/bridge", tags=["Exercise Bridge"])


# ============================================================================
# Pydantic Models
# ============================================================================

class SimulationEngine(str, Enum):
    """Available simulation engines"""
    JAAMSIM = "jaamsim"
    NICS = "nics"
    HYBRID = "hybrid"


class BCMExerciseRequest(BaseModel):
    """Request to create BCM exercise"""
    name: str
    description: str
    scenario_type: str  # tabletop, functional, simulation, full_scale
    company_id: str
    duration_minutes: int = 120
    participants: List[str] = Field(default_factory=list)
    objectives: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    injects: List[Dict[str, Any]] = Field(default_factory=list)
    location: Optional[Dict[str, Any]] = None
    commander: Optional[str] = None
    priority: str = "medium"
    simulation_engine: SimulationEngine = SimulationEngine.JAAMSIM


class ExerciseInjectRequest(BaseModel):
    """Request to inject event into running exercise"""
    exercise_id: str
    title: str
    description: str
    event_type: str  # failure, recovery, communication, decision
    target_entity: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    requires_response: bool = True
    delay_minutes: Optional[float] = None


class ExerciseUpdateRequest(BaseModel):
    """Request to update exercise"""
    exercise_id: str
    status: Optional[str] = None
    participants: Optional[List[str]] = None
    notes: Optional[str] = None


# ============================================================================
# WebSocket Connection Manager
# ============================================================================

class ConnectionManager:
    """Manages WebSocket connections for real-time exercise updates"""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, exercise_id: str):
        """Connect WebSocket client to exercise"""
        await websocket.accept()
        if exercise_id not in self.active_connections:
            self.active_connections[exercise_id] = []
        self.active_connections[exercise_id].append(websocket)
        logger.info(f"WebSocket connected for exercise: {exercise_id}")

    def disconnect(self, websocket: WebSocket, exercise_id: str):
        """Disconnect WebSocket client from exercise"""
        if exercise_id in self.active_connections:
            if websocket in self.active_connections[exercise_id]:
                self.active_connections[exercise_id].remove(websocket)
            if not self.active_connections[exercise_id]:
                del self.active_connections[exercise_id]
        logger.info(f"WebSocket disconnected for exercise: {exercise_id}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket"""
        await websocket.send_json({"message": message})

    async def broadcast_to_exercise(self, exercise_id: str, message: dict):
        """Broadcast message to all connected clients for exercise"""
        if exercise_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[exercise_id]:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.append(websocket)

            # Remove disconnected websockets
            for ws in disconnected:
                if ws in self.active_connections[exercise_id]:
                    self.active_connections[exercise_id].remove(ws)


# Global connection manager
connection_manager = ConnectionManager()

# In-memory storage for active exercises (replace with database in production)
active_exercises: Dict[str, Dict[str, Any]] = {}

# Global service clients (initialized at startup)
jaamsim_engine: Optional[Any] = None
nics_integration: Optional[Any] = None


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/exercises/create")
async def create_exercise(
    request: BCMExerciseRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Create BCM exercise using specified simulation engine

    Engines:
    - jaamsim: Discrete-event simulation
    - nics: ICS incident command system
    - hybrid: Both JaamSim and NICS
    """
    try:
        logger.info(f"Creating BCM exercise: {request.name} ({request.simulation_engine})")

        exercise_id = f"bcm_ex_{int(datetime.now().timestamp())}"

        # Store exercise metadata
        active_exercises[exercise_id] = {
            "id": exercise_id,
            "name": request.name,
            "description": request.description,
            "scenario_type": request.scenario_type,
            "engine": request.simulation_engine,
            "status": "creating",
            "created_at": datetime.now().isoformat(),
            "participants": request.participants,
            "objectives": request.objectives
        }

        # Create exercise based on engine type
        if request.simulation_engine == SimulationEngine.JAAMSIM:
            background_tasks.add_task(
                _create_jaamsim_exercise,
                exercise_id,
                request
            )
        elif request.simulation_engine == SimulationEngine.NICS:
            background_tasks.add_task(
                _create_nics_exercise,
                exercise_id,
                request
            )
        elif request.simulation_engine == SimulationEngine.HYBRID:
            background_tasks.add_task(
                _create_hybrid_exercise,
                exercise_id,
                request
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid simulation engine")

        return {
            "status": "accepted",
            "message": "Exercise creation initiated",
            "exercise_id": exercise_id,
            "simulation_engine": request.simulation_engine
        }

    except Exception as e:
        logger.error(f"Failed to create exercise: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exercises/{exercise_id}/start")
async def start_exercise(exercise_id: str) -> Dict[str, Any]:
    """Start BCM exercise execution"""
    try:
        logger.info(f"Starting exercise: {exercise_id}")

        exercise = active_exercises.get(exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        if exercise["status"] != "prepared":
            raise HTTPException(
                status_code=400,
                detail=f"Exercise not ready (status: {exercise['status']})"
            )

        # Update status
        exercise["status"] = "running"
        exercise["started_at"] = datetime.now().isoformat()

        # Broadcast start event
        await connection_manager.broadcast_to_exercise(exercise_id, {
            "type": "exercise_started",
            "exercise_id": exercise_id,
            "name": exercise["name"],
            "timestamp": datetime.now().isoformat(),
            "engine": exercise["engine"]
        })

        return {
            "status": "started",
            "exercise_id": exercise_id,
            "engine": exercise["engine"],
            "started_at": exercise["started_at"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start exercise: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exercises/{exercise_id}/inject")
async def inject_event(
    exercise_id: str,
    request: ExerciseInjectRequest
) -> Dict[str, Any]:
    """Inject event into running exercise"""
    try:
        logger.info(f"Injecting event into exercise {exercise_id}: {request.title}")

        exercise = active_exercises.get(exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        if exercise["status"] != "running":
            raise HTTPException(
                status_code=400,
                detail=f"Exercise not running (status: {exercise['status']})"
            )

        # Record inject
        if "injects" not in exercise:
            exercise["injects"] = []

        inject_data = {
            "title": request.title,
            "description": request.description,
            "event_type": request.event_type,
            "timestamp": datetime.now().isoformat(),
            "requires_response": request.requires_response
        }
        exercise["injects"].append(inject_data)

        # Broadcast inject event
        await connection_manager.broadcast_to_exercise(exercise_id, {
            "type": "event_injected",
            "exercise_id": exercise_id,
            "inject": inject_data,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "status": "injected",
            "exercise_id": exercise_id,
            "inject": inject_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to inject event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exercises/{exercise_id}/status")
async def get_exercise_status(exercise_id: str) -> Dict[str, Any]:
    """Get exercise status and progress"""
    try:
        exercise = active_exercises.get(exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        return {
            "exercise_id": exercise_id,
            "name": exercise["name"],
            "engine": exercise["engine"],
            "status": exercise["status"],
            "created_at": exercise["created_at"],
            "started_at": exercise.get("started_at"),
            "completed_at": exercise.get("completed_at"),
            "participants_count": len(exercise.get("participants", [])),
            "objectives_count": len(exercise.get("objectives", [])),
            "injects_count": len(exercise.get("injects", []))
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get exercise status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exercises/{exercise_id}/complete")
async def complete_exercise(exercise_id: str) -> Dict[str, Any]:
    """Complete and close exercise"""
    try:
        logger.info(f"Completing exercise: {exercise_id}")

        exercise = active_exercises.get(exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        # Update status
        exercise["status"] = "completed"
        exercise["completed_at"] = datetime.now().isoformat()

        # Calculate duration if started
        if "started_at" in exercise and "completed_at" in exercise:
            start = datetime.fromisoformat(exercise["started_at"])
            end = datetime.fromisoformat(exercise["completed_at"])
            duration_minutes = (end - start).total_seconds() / 60
            exercise["duration_minutes"] = duration_minutes

        # Broadcast completion
        await connection_manager.broadcast_to_exercise(exercise_id, {
            "type": "exercise_completed",
            "exercise_id": exercise_id,
            "timestamp": datetime.now().isoformat(),
            "engine": exercise["engine"],
            "duration_minutes": exercise.get("duration_minutes")
        })

        return {
            "status": "completed",
            "exercise_id": exercise_id,
            "completed_at": exercise["completed_at"],
            "duration_minutes": exercise.get("duration_minutes")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete exercise: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exercises")
async def list_exercises(
    status: Optional[str] = None,
    engine: Optional[SimulationEngine] = None
) -> Dict[str, Any]:
    """List all exercises"""
    try:
        exercises = list(active_exercises.values())

        # Apply filters
        if status:
            exercises = [e for e in exercises if e.get("status") == status]
        if engine:
            exercises = [e for e in exercises if e.get("engine") == engine]

        return {
            "exercises": exercises,
            "total": len(exercises),
            "filters": {
                "status": status,
                "engine": engine
            }
        }

    except Exception as e:
        logger.error(f"Failed to list exercises: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{exercise_id}")
async def websocket_endpoint(websocket: WebSocket, exercise_id: str):
    """WebSocket endpoint for real-time exercise updates"""
    await connection_manager.connect(websocket, exercise_id)
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "exercise_id": exercise_id,
            "timestamp": datetime.now().isoformat()
        })

        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            logger.debug(f"Received WebSocket message: {data}")

            # Echo back (can implement custom message handling here)
            await connection_manager.send_personal_message(
                f"Message received: {data}", websocket
            )

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, exercise_id)
        logger.info(f"WebSocket disconnected: {exercise_id}")


@router.get("/metrics")
async def get_bridge_metrics() -> Dict[str, Any]:
    """Get bridge service metrics"""
    try:
        exercises = list(active_exercises.values())

        metrics = {
            "service": "exercise-bridge",
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "exercises": {
                "total": len(exercises),
                "by_status": {
                    "creating": len([e for e in exercises if e.get("status") == "creating"]),
                    "prepared": len([e for e in exercises if e.get("status") == "prepared"]),
                    "running": len([e for e in exercises if e.get("status") == "running"]),
                    "completed": len([e for e in exercises if e.get("status") == "completed"])
                },
                "by_engine": {
                    "jaamsim": len([e for e in exercises if e.get("engine") == "jaamsim"]),
                    "nics": len([e for e in exercises if e.get("engine") == "nics"]),
                    "hybrid": len([e for e in exercises if e.get("engine") == "hybrid"])
                }
            },
            "websocket_connections": sum(
                len(conns) for conns in connection_manager.active_connections.values()
            )
        }

        return metrics

    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Background Tasks
# ============================================================================

async def _create_jaamsim_exercise(exercise_id: str, request: BCMExerciseRequest):
    """Background task to create JaamSim exercise"""
    try:
        logger.info(f"Creating JaamSim exercise: {exercise_id}")

        # Create JaamSim engine instance
        engine = JaamSimEngine(
            simulation_id=exercise_id,
            parameters={
                "scenario_name": request.name,
                "scenario_type": request.scenario_type,
                "duration_minutes": request.duration_minutes
            }
        )

        # Update exercise status
        if exercise_id in active_exercises:
            active_exercises[exercise_id]["status"] = "prepared"
            active_exercises[exercise_id]["engine_instance"] = engine

        logger.info(f"JaamSim exercise created: {exercise_id}")

        # Broadcast event
        await connection_manager.broadcast_to_exercise(exercise_id, {
            "type": "exercise_prepared",
            "exercise_id": exercise_id,
            "engine": "jaamsim",
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Failed to create JaamSim exercise: {e}")
        if exercise_id in active_exercises:
            active_exercises[exercise_id]["status"] = "error"
            active_exercises[exercise_id]["error"] = str(e)


async def _create_nics_exercise(exercise_id: str, request: BCMExerciseRequest):
    """Background task to create NICS exercise"""
    try:
        logger.info(f"Creating NICS exercise: {exercise_id}")

        # Create NICS integration (would use actual NICS client in production)
        # For now, just mark as prepared
        if exercise_id in active_exercises:
            active_exercises[exercise_id]["status"] = "prepared"
            active_exercises[exercise_id]["nics_incident_id"] = f"nics_{exercise_id}"

        logger.info(f"NICS exercise created: {exercise_id}")

        # Broadcast event
        await connection_manager.broadcast_to_exercise(exercise_id, {
            "type": "exercise_prepared",
            "exercise_id": exercise_id,
            "engine": "nics",
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Failed to create NICS exercise: {e}")
        if exercise_id in active_exercises:
            active_exercises[exercise_id]["status"] = "error"
            active_exercises[exercise_id]["error"] = str(e)


async def _create_hybrid_exercise(exercise_id: str, request: BCMExerciseRequest):
    """Background task to create hybrid exercise (JaamSim + NICS)"""
    try:
        logger.info(f"Creating hybrid exercise: {exercise_id}")

        # Create both JaamSim and NICS exercises in parallel
        await asyncio.gather(
            _create_jaamsim_exercise(exercise_id, request),
            _create_nics_exercise(exercise_id, request)
        )

        if exercise_id in active_exercises:
            active_exercises[exercise_id]["engine"] = "hybrid"
            active_exercises[exercise_id]["hybrid_config"] = {
                "jaamsim_enabled": True,
                "nics_enabled": True,
                "synchronization": "realtime"
            }

        logger.info(f"Hybrid exercise created: {exercise_id}")

        # Broadcast hybrid creation event
        await connection_manager.broadcast_to_exercise(exercise_id, {
            "type": "hybrid_exercise_prepared",
            "exercise_id": exercise_id,
            "engines": ["jaamsim", "nics"],
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Failed to create hybrid exercise: {e}")
        if exercise_id in active_exercises:
            active_exercises[exercise_id]["status"] = "error"
            active_exercises[exercise_id]["error"] = str(e)


# ============================================================================
# Additional Hybrid Exercise Endpoints
# ============================================================================

@router.post("/exercises/{exercise_id}/inject-realtime")
async def inject_realtime_event(
    exercise_id: str,
    inject: ExerciseInjectRequest
) -> Dict[str, Any]:
    """
    Inject event into running exercise with real-time propagation

    Supports both JaamSim and NICS engines for hybrid exercises
    """
    try:
        exercise = active_exercises.get(exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        if exercise["status"] != "running":
            raise HTTPException(
                status_code=400,
                detail=f"Exercise not running (status: {exercise['status']})"
            )

        inject_id = f"inject_{int(datetime.now().timestamp())}"
        inject_data = {
            "inject_id": inject_id,
            "title": inject.title,
            "description": inject.description,
            "event_type": inject.event_type,
            "target_entity": inject.target_entity,
            "parameters": inject.parameters,
            "requires_response": inject.requires_response,
            "injected_at": datetime.now().isoformat()
        }

        # Store inject
        if "injects" not in exercise:
            exercise["injects"] = []
        exercise["injects"].append(inject_data)

        # Broadcast to all connected clients immediately
        await connection_manager.broadcast_to_exercise(exercise_id, {
            "type": "realtime_inject",
            "exercise_id": exercise_id,
            "inject": inject_data,
            "timestamp": datetime.now().isoformat(),
            "requires_response": inject.requires_response
        })

        # Schedule delayed inject if specified
        if inject.delay_minutes:
            asyncio.create_task(
                _delayed_inject_notification(
                    exercise_id,
                    inject_data,
                    inject.delay_minutes
                )
            )

        return {
            "status": "injected",
            "inject_id": inject_id,
            "exercise_id": exercise_id,
            "timestamp": inject_data["injected_at"],
            "broadcast_sent": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to inject realtime event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _delayed_inject_notification(
    exercise_id: str,
    inject_data: Dict,
    delay_minutes: float
):
    """Send delayed inject notification after specified time"""
    await asyncio.sleep(delay_minutes * 60)

    await connection_manager.broadcast_to_exercise(exercise_id, {
        "type": "delayed_inject_notification",
        "exercise_id": exercise_id,
        "inject": inject_data,
        "timestamp": datetime.now().isoformat()
    })


@router.get("/exercises/{exercise_id}/participants")
async def get_exercise_participants(exercise_id: str) -> Dict[str, Any]:
    """Get list of participants connected via WebSocket"""
    try:
        exercise = active_exercises.get(exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        connections = connection_manager.active_connections.get(exercise_id, [])

        return {
            "exercise_id": exercise_id,
            "participants": exercise.get("participants", []),
            "connected_count": len(connections),
            "websocket_active": len(connections) > 0,
            "status": exercise["status"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get participants: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exercises/{exercise_id}/broadcast")
async def broadcast_message(
    exercise_id: str,
    message: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Broadcast custom message to all exercise participants

    Useful for coordinator announcements, warnings, or updates
    """
    try:
        exercise = active_exercises.get(exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        # Add metadata
        message["exercise_id"] = exercise_id
        message["timestamp"] = datetime.now().isoformat()
        message["type"] = message.get("type", "coordinator_message")

        # Broadcast
        await connection_manager.broadcast_to_exercise(exercise_id, message)

        return {
            "status": "broadcast_sent",
            "exercise_id": exercise_id,
            "message_type": message["type"],
            "timestamp": message["timestamp"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to broadcast message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
