"""
Simulation Adapter for BCM Exercise Management
Manages tabletop exercises, drills, and simulations
"""

import asyncio
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum
import logging
import json
import uuid

logger = logging.getLogger(__name__)


class ExerciseType(str, Enum):
    TABLETOP = "tabletop"
    FUNCTIONAL = "functional"
    FULL_SCALE = "full_scale"
    DRILL = "drill"
    WALKTHROUGH = "walkthrough"


class ExerciseStatus(str, Enum):
    PLANNED = "planned"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DEFERRED = "deferred"


class ParticipantRole(str, Enum):
    FACILITATOR = "facilitator"
    OBSERVER = "observer"
    PARTICIPANT = "participant"
    EVALUATOR = "evaluator"
    CONTROLLER = "controller"


class ScenarioComplexity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Participant(BaseModel):
    user_id: str
    name: str
    email: str
    role: ParticipantRole
    department: Optional[str] = None
    position: Optional[str] = None
    experience_level: str = "intermediate"
    notifications_enabled: bool = True


class Scenario(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    complexity: ScenarioComplexity
    duration_minutes: int = 120
    objectives: List[str] = Field(default_factory=list)
    injects: List[Dict[str, Any]] = Field(default_factory=list)
    affected_processes: List[str] = Field(default_factory=list)
    required_roles: List[str] = Field(default_factory=list)
    iso_requirements: List[str] = Field(default_factory=lambda: ["ISO 22301:2019"])


class Inject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scenario_id: str
    sequence: int
    title: str
    description: str
    trigger_time: int  # minutes from start
    expected_response: str
    evaluation_criteria: List[str] = Field(default_factory=list)
    hints: List[str] = Field(default_factory=list)
    delivered: bool = False
    response_received: Optional[str] = None


class Exercise(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = "demo"
    name: str
    description: Optional[str] = None
    exercise_type: ExerciseType
    scenario: Scenario
    status: ExerciseStatus = ExerciseStatus.PLANNED
    scheduled_date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: int = 120
    participants: List[Participant] = Field(default_factory=list)
    objectives: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    lessons_learned: List[str] = Field(default_factory=list)
    action_items: List[Dict[str, Any]] = Field(default_factory=list)
    evaluation_score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = "system"


class ExerciseResult(BaseModel):
    exercise_id: str
    participant_responses: Dict[str, List[Dict]] = Field(default_factory=dict)
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    objectives_met: Dict[str, bool] = Field(default_factory=dict)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    lessons_learned: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    overall_score: float = 0.0
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class SimAdapter:
    """Adapter for managing BCM exercises and simulations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.eventbus_url = config.get("eventbus_url", "http://localhost:8001")
        self.orchestrator_url = config.get("orchestrator_url", "http://localhost:8002")
        self.notification_url = config.get("notification_url", "http://localhost:8004")
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # In-memory storage for demo (replace with database)
        self.exercises = {}
        self.scenarios = {}
        self.results = {}
    
    async def __aenter__(self):
        await self._initialize_sample_scenarios()
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.client.aclose()
    
    async def publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish exercise events to EventBus"""
        try:
            event = {
                "event_type": event_type,
                "tenant_id": data.get("tenant_id", "demo"),
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "sim_adapter",
                "event_id": str(uuid.uuid4())
            }
            
            response = await self.client.post(
                f"{self.eventbus_url}/api/events/publish",
                json=event
            )
            response.raise_for_status()
            logger.info(f"Published event: {event_type}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
    
    # Scenario Management
    async def create_scenario(self, scenario: Scenario) -> Scenario:
        """Create a new exercise scenario"""
        try:
            self.scenarios[scenario.id] = scenario
            
            # Publish event
            await self.publish_event("bcm.exercise.scenario_created", {
                "scenario_id": scenario.id,
                "name": scenario.name,
                "complexity": scenario.complexity,
                "tenant_id": "demo"
            })
            
            return scenario
        except Exception as e:
            logger.error(f"Failed to create scenario: {e}")
            raise
    
    async def get_scenarios(self, complexity: Optional[ScenarioComplexity] = None) -> List[Scenario]:
        """Get available scenarios"""
        scenarios = list(self.scenarios.values())
        if complexity:
            scenarios = [s for s in scenarios if s.complexity == complexity]
        return scenarios
    
    async def _initialize_sample_scenarios(self):
        """Initialize sample scenarios"""
        scenarios = [
            Scenario(
                id="SCN-001",
                name="Cyber Attack Response",
                description="Ransomware attack on critical systems",
                complexity=ScenarioComplexity.HIGH,
                duration_minutes=180,
                objectives=[
                    "Activate Incident Response Team",
                    "Isolate affected systems",
                    "Communicate with stakeholders",
                    "Implement recovery procedures"
                ],
                affected_processes=["IT Services", "Operations", "Customer Service"],
                required_roles=["IT Manager", "CISO", "Communications Lead"],
                injects=[
                    {
                        "sequence": 1,
                        "title": "Initial Alert",
                        "description": "Security team detects unusual network activity",
                        "trigger_time": 0,
                        "expected_response": "Activate incident response procedures"
                    },
                    {
                        "sequence": 2,
                        "title": "Scope Expansion",
                        "description": "Multiple systems showing signs of compromise",
                        "trigger_time": 30,
                        "expected_response": "Escalate to crisis management team"
                    }
                ]
            ),
            Scenario(
                id="SCN-002",
                name="Supply Chain Disruption",
                description="Key supplier unable to deliver critical components",
                complexity=ScenarioComplexity.MEDIUM,
                duration_minutes=120,
                objectives=[
                    "Assess impact on production",
                    "Activate alternate suppliers",
                    "Communicate with customers",
                    "Implement mitigation strategies"
                ],
                affected_processes=["Manufacturing", "Procurement", "Customer Service"],
                required_roles=["Operations Manager", "Procurement Lead", "Customer Service Manager"]
            ),
            Scenario(
                id="SCN-003",
                name="Natural Disaster Response",
                description="Earthquake damages primary facility",
                complexity=ScenarioComplexity.CRITICAL,
                duration_minutes=240,
                objectives=[
                    "Ensure personnel safety",
                    "Assess facility damage",
                    "Activate alternate site",
                    "Resume critical operations"
                ],
                affected_processes=["All Operations", "Facilities", "HR"],
                required_roles=["Crisis Manager", "Facilities Manager", "HR Director", "Safety Officer"]
            )
        ]
        
        for scenario in scenarios:
            self.scenarios[scenario.id] = scenario
    
    # Exercise Management
    async def create_exercise(self, exercise: Exercise) -> Exercise:
        """Create a new exercise"""
        try:
            self.exercises[exercise.id] = exercise
            
            # Publish event
            await self.publish_event("bcm.exercise.created", {
                "exercise_id": exercise.id,
                "name": exercise.name,
                "type": exercise.exercise_type,
                "scenario_id": exercise.scenario.id,
                "scheduled_date": exercise.scheduled_date.isoformat() if exercise.scheduled_date else None,
                "tenant_id": exercise.tenant_id
            })
            
            return exercise
        except Exception as e:
            logger.error(f"Failed to create exercise: {e}")
            raise
    
    async def schedule_exercise(self, exercise_id: str, scheduled_date: datetime,
                               participants: List[Participant]) -> Exercise:
        """Schedule an exercise"""
        try:
            exercise = self.exercises.get(exercise_id)
            if not exercise:
                raise ValueError(f"Exercise {exercise_id} not found")
            
            exercise.scheduled_date = scheduled_date
            exercise.participants = participants
            exercise.status = ExerciseStatus.SCHEDULED
            
            # Send notifications to participants
            for participant in participants:
                await self._send_participant_notification(participant, exercise)
            
            # Publish event
            await self.publish_event("bcm.exercise.scheduled", {
                "exercise_id": exercise_id,
                "scheduled_date": scheduled_date.isoformat(),
                "participant_count": len(participants),
                "tenant_id": exercise.tenant_id
            })
            
            return exercise
        except Exception as e:
            logger.error(f"Failed to schedule exercise: {e}")
            raise
    
    async def start_exercise(self, exercise_id: str) -> Exercise:
        """Start an exercise"""
        try:
            exercise = self.exercises.get(exercise_id)
            if not exercise:
                raise ValueError(f"Exercise {exercise_id} not found")
            
            exercise.status = ExerciseStatus.IN_PROGRESS
            exercise.start_time = datetime.utcnow()
            
            # Initialize result tracking
            result = ExerciseResult(exercise_id=exercise_id)
            self.results[exercise_id] = result
            
            # Schedule inject delivery
            await self._schedule_injects(exercise)
            
            # Publish event
            await self.publish_event("bcm.exercise.started", {
                "exercise_id": exercise_id,
                "name": exercise.name,
                "participant_count": len(exercise.participants),
                "duration_minutes": exercise.duration_minutes,
                "tenant_id": exercise.tenant_id
            })
            
            return exercise
        except Exception as e:
            logger.error(f"Failed to start exercise: {e}")
            raise
    
    async def complete_exercise(self, exercise_id: str, 
                               evaluation_data: Dict[str, Any]) -> ExerciseResult:
        """Complete an exercise and generate results"""
        try:
            exercise = self.exercises.get(exercise_id)
            if not exercise:
                raise ValueError(f"Exercise {exercise_id} not found")
            
            exercise.status = ExerciseStatus.COMPLETED
            exercise.end_time = datetime.utcnow()
            exercise.evaluation_score = evaluation_data.get("overall_score", 0.0)
            exercise.lessons_learned = evaluation_data.get("lessons_learned", [])
            exercise.action_items = evaluation_data.get("action_items", [])
            
            # Generate results
            result = self.results.get(exercise_id) or ExerciseResult(exercise_id=exercise_id)
            result.overall_score = evaluation_data.get("overall_score", 0.0)
            result.lessons_learned = evaluation_data.get("lessons_learned", [])
            result.improvement_areas = evaluation_data.get("improvement_areas", [])
            result.performance_metrics = evaluation_data.get("metrics", {})
            result.completed_at = datetime.utcnow()
            
            self.results[exercise_id] = result
            
            # Publish event
            await self.publish_event("bcm.exercise.completed", {
                "exercise_id": exercise_id,
                "name": exercise.name,
                "duration_actual": (exercise.end_time - exercise.start_time).seconds / 60,
                "score": result.overall_score,
                "objectives_met": len([o for o, met in result.objectives_met.items() if met]),
                "lessons_count": len(result.lessons_learned),
                "tenant_id": exercise.tenant_id
            })
            
            return result
        except Exception as e:
            logger.error(f"Failed to complete exercise: {e}")
            raise
    
    async def get_exercises(self, tenant_id: str = "demo", 
                           status: Optional[ExerciseStatus] = None) -> List[Exercise]:
        """Get exercises for tenant"""
        exercises = [e for e in self.exercises.values() if e.tenant_id == tenant_id]
        if status:
            exercises = [e for e in exercises if e.status == status]
        return exercises
    
    async def get_exercise_results(self, exercise_id: str) -> Optional[ExerciseResult]:
        """Get results for an exercise"""
        return self.results.get(exercise_id)
    
    # Inject Management
    async def _schedule_injects(self, exercise: Exercise):
        """Schedule injects for an exercise"""
        for inject_data in exercise.scenario.injects:
            inject = Inject(
                scenario_id=exercise.scenario.id,
                sequence=inject_data["sequence"],
                title=inject_data["title"],
                description=inject_data["description"],
                trigger_time=inject_data["trigger_time"],
                expected_response=inject_data["expected_response"]
            )
            
            # Schedule inject delivery (simplified for demo)
            asyncio.create_task(
                self._deliver_inject_after_delay(exercise.id, inject, inject.trigger_time * 60)
            )
    
    async def _deliver_inject_after_delay(self, exercise_id: str, inject: Inject, delay_seconds: int):
        """Deliver an inject after specified delay"""
        await asyncio.sleep(delay_seconds)
        
        # Publish inject event
        await self.publish_event("bcm.exercise.inject_delivered", {
            "exercise_id": exercise_id,
            "inject_id": inject.id,
            "title": inject.title,
            "description": inject.description,
            "sequence": inject.sequence,
            "tenant_id": "demo"
        })
        
        inject.delivered = True
    
    async def submit_inject_response(self, exercise_id: str, inject_id: str,
                                   participant_id: str, response: str) -> Dict[str, Any]:
        """Submit response to an inject"""
        try:
            result = self.results.get(exercise_id)
            if not result:
                result = ExerciseResult(exercise_id=exercise_id)
                self.results[exercise_id] = result
            
            # Record response
            if participant_id not in result.participant_responses:
                result.participant_responses[participant_id] = []
            
            response_data = {
                "inject_id": inject_id,
                "response": response,
                "timestamp": datetime.utcnow().isoformat()
            }
            result.participant_responses[participant_id].append(response_data)
            
            # Publish event
            await self.publish_event("bcm.exercise.response_submitted", {
                "exercise_id": exercise_id,
                "inject_id": inject_id,
                "participant_id": participant_id,
                "tenant_id": "demo"
            })
            
            return {"status": "success", "message": "Response recorded"}
        except Exception as e:
            logger.error(f"Failed to submit response: {e}")
            raise
    
    # Notifications
    async def _send_participant_notification(self, participant: Participant, exercise: Exercise):
        """Send notification to exercise participant"""
        try:
            if not participant.notifications_enabled:
                return
            
            notification_data = {
                "user_id": participant.user_id,
                "title": f"Exercise Scheduled: {exercise.name}",
                "message": f"You have been invited to participate in {exercise.name} on {exercise.scheduled_date}",
                "type": "exercise_invitation",
                "priority": "medium",
                "data": {
                    "exercise_id": exercise.id,
                    "role": participant.role
                }
            }
            
            await self.client.post(
                f"{self.notification_url}/api/notify",
                json=notification_data
            )
        except Exception as e:
            logger.error(f"Failed to send participant notification: {e}")
    
    # Analytics
    async def get_exercise_metrics(self, tenant_id: str = "demo") -> Dict[str, Any]:
        """Get exercise metrics for dashboard"""
        try:
            exercises = [e for e in self.exercises.values() if e.tenant_id == tenant_id]
            completed = [e for e in exercises if e.status == ExerciseStatus.COMPLETED]
            
            metrics = {
                "total_exercises": len(exercises),
                "completed_exercises": len(completed),
                "upcoming_exercises": len([e for e in exercises if e.status == ExerciseStatus.SCHEDULED]),
                "in_progress": len([e for e in exercises if e.status == ExerciseStatus.IN_PROGRESS]),
                "avg_score": sum(e.evaluation_score or 0 for e in completed) / max(len(completed), 1),
                "exercise_types": {
                    "tabletop": len([e for e in exercises if e.exercise_type == ExerciseType.TABLETOP]),
                    "functional": len([e for e in exercises if e.exercise_type == ExerciseType.FUNCTIONAL]),
                    "full_scale": len([e for e in exercises if e.exercise_type == ExerciseType.FULL_SCALE]),
                    "drill": len([e for e in exercises if e.exercise_type == ExerciseType.DRILL])
                },
                "completion_rate": len(completed) / max(len(exercises), 1) * 100,
                "avg_participants": sum(len(e.participants) for e in exercises) / max(len(exercises), 1),
                "lessons_learned_total": sum(len(e.lessons_learned) for e in completed),
                "action_items_total": sum(len(e.action_items) for e in completed)
            }
            return metrics
        except Exception as e:
            logger.error(f"Failed to get exercise metrics: {e}")
            return {}


# FastAPI service endpoint
if __name__ == "__main__":
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    
    app = FastAPI(title="Simulation Adapter Service")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    config = {
        "eventbus_url": "http://localhost:8001",
        "orchestrator_url": "http://localhost:8002",
        "notification_url": "http://localhost:8004"
    }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "sim_adapter"}
    
    @app.get("/api/scenarios")
    async def get_scenarios(complexity: Optional[ScenarioComplexity] = None):
        async with SimAdapter(config) as adapter:
            scenarios = await adapter.get_scenarios(complexity)
            return {"scenarios": [s.dict() for s in scenarios]}
    
    @app.post("/api/exercises")
    async def create_exercise(exercise: Exercise):
        async with SimAdapter(config) as adapter:
            result = await adapter.create_exercise(exercise)
            return result.dict()
    
    @app.get("/api/exercises")
    async def get_exercises(tenant_id: str = "demo", status: Optional[ExerciseStatus] = None):
        async with SimAdapter(config) as adapter:
            exercises = await adapter.get_exercises(tenant_id, status)
            return {"exercises": [e.dict() for e in exercises]}
    
    @app.post("/api/exercises/{exercise_id}/start")
    async def start_exercise(exercise_id: str):
        async with SimAdapter(config) as adapter:
            exercise = await adapter.start_exercise(exercise_id)
            return exercise.dict()
    
    @app.post("/api/exercises/{exercise_id}/complete")
    async def complete_exercise(exercise_id: str, evaluation_data: Dict[str, Any]):
        async with SimAdapter(config) as adapter:
            result = await adapter.complete_exercise(exercise_id, evaluation_data)
            return result.dict()
    
    @app.get("/api/metrics")
    async def get_metrics(tenant_id: str = "demo"):
        async with SimAdapter(config) as adapter:
            metrics = await adapter.get_exercise_metrics(tenant_id)
            return metrics
    
    uvicorn.run(app, host="0.0.0.0", port=8008)
