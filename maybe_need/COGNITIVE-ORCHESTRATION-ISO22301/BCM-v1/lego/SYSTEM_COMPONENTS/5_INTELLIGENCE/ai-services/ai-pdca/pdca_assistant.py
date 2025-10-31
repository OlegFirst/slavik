"""
PDCA AI Assistant Service
Provides context-aware AI assistance for Plan-Do-Check-Act cycles
"""

import asyncio
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class PDCAPhase(str, Enum):
    PLAN = "plan"
    DO = "do" 
    CHECK = "check"
    ACT = "act"


class AssistantContext(str, Enum):
    OVERVIEW = "overview"
    EVENTS = "events"
    ORCHESTRATOR = "orchestrator"
    DOCUMENTS = "documents"
    EXERCISES = "exercises"
    GOVERNANCE = "governance"
    TRAINING = "training"
    ADMIN = "admin"


class ActionType(str, Enum):
    SUGGEST = "suggest"
    CREATE = "create"
    ANALYZE = "analyze"
    REPORT = "report"
    SCHEDULE = "schedule"
    REVIEW = "review"


class NextBestAction(BaseModel):
    id: str
    phase: PDCAPhase
    context: AssistantContext
    action_type: ActionType
    title: str
    description: str
    priority: str = "medium"  # low, medium, high, critical
    confidence: float = 0.8
    estimated_time: int = 15  # minutes
    prerequisites: List[str] = Field(default_factory=list)
    expected_outcome: str = ""
    api_endpoint: Optional[str] = None
    payload_template: Optional[Dict] = None


class PDCAScenario(BaseModel):
    id: str
    name: str
    phase: PDCAPhase
    context: AssistantContext
    triggers: List[str] = Field(default_factory=list)
    actions: List[NextBestAction] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    kpi_indicators: List[str] = Field(default_factory=list)


class AssistantMessage(BaseModel):
    id: str
    sender: str  # user, assistant
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    phase: Optional[PDCAPhase] = None
    context: Optional[AssistantContext] = None
    confidence: Optional[float] = None
    actions: List[NextBestAction] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PDCAAssistant:
    """AI Assistant with PDCA-aware context and suggestions"""
    
    def __init__(self, config: Dict[str, Any]):
        self.eventbus_url = config.get("eventbus_url", "http://localhost:8001")
        self.orchestrator_url = config.get("orchestrator_url", "http://localhost:8002")
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Context tracking
        self.current_phase = PDCAPhase.PLAN
        self.current_context = AssistantContext.OVERVIEW
        self.conversation_history = []
        self.user_preferences = {}
        
        # PDCA scenarios
        self.scenarios = {}
        self.phase_progress = {"plan": 25, "do": 50, "check": 75, "act": 100}
    
    async def __aenter__(self):
        await self._initialize_pdca_scenarios()
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.client.aclose()
    
    async def process_message(self, user_message: str, context: AssistantContext,
                            tenant_id: str = "demo") -> AssistantMessage:
        """Process user message and generate context-aware response"""
        try:
            self.current_context = context
            
            # Analyze user intent
            intent = await self._analyze_user_intent(user_message, context)
            
            # Generate response based on current PDCA phase and context
            response_content, actions = await self._generate_response(
                user_message, intent, context
            )
            
            # Create assistant message
            assistant_message = AssistantMessage(
                id=f"msg_{datetime.utcnow().timestamp()}",
                sender="assistant",
                content=response_content,
                phase=self.current_phase,
                context=context,
                confidence=0.85,
                actions=actions,
                metadata={"intent": intent, "tenant_id": tenant_id}
            )
            
            # Store in conversation history
            self.conversation_history.append(assistant_message)
            
            # Publish event
            await self._publish_assistant_event("message_processed", {
                "context": context.value,
                "phase": self.current_phase.value,
                "intent": intent,
                "actions_suggested": len(actions),
                "tenant_id": tenant_id
            })
            
            return assistant_message
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            raise
    
    async def get_next_best_actions(self, context: AssistantContext,
                                  tenant_id: str = "demo") -> List[NextBestAction]:
        """Get context and phase-aware next best actions"""
        try:
            scenario_key = f"{self.current_phase.value}_{context.value}"
            scenario = self.scenarios.get(scenario_key)
            
            if scenario:
                # Filter actions based on current state
                relevant_actions = []
                for action in scenario.actions:
                    # Check if prerequisites are met (simplified)
                    if await self._check_prerequisites(action, tenant_id):
                        relevant_actions.append(action)
                
                # Sort by priority and confidence
                relevant_actions.sort(
                    key=lambda x: (self._priority_weight(x.priority), -x.confidence),
                    reverse=True
                )
                
                return relevant_actions[:5]  # Return top 5 actions
            
            return []
        except Exception as e:
            logger.error(f"Failed to get next best actions: {e}")
            return []
    
    async def execute_action(self, action_id: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a suggested action through the orchestrator"""
        try:
            # Find action
            action = None
            for scenario in self.scenarios.values():
                for a in scenario.actions:
                    if a.id == action_id:
                        action = a
                        break
                if action:
                    break
            
            if not action:
                raise ValueError(f"Action {action_id} not found")
            
            # Prepare execution payload
            payload = action.payload_template or {}
            if parameters:
                payload.update(parameters)
            
            result = {"status": "success", "action": action.title}
            
            # Execute through appropriate service
            if action.api_endpoint:
                if action.api_endpoint.startswith("/orchestrator"):
                    response = await self.client.post(
                        f"{self.orchestrator_url}{action.api_endpoint}",
                        json=payload
                    )
                    if response.status_code == 200:
                        result.update(response.json())
                    
                elif action.api_endpoint.startswith("/eventbus"):
                    # Publish event through EventBus
                    await self._publish_assistant_event("action_executed", {
                        "action_id": action_id,
                        "action_type": action.action_type.value,
                        "context": self.current_context.value,
                        "parameters": parameters or {}
                    })
            
            return result
        except Exception as e:
            logger.error(f"Failed to execute action: {e}")
            raise
    
    async def update_phase_progress(self, phase: PDCAPhase, progress: float):
        """Update PDCA phase progress"""
        self.current_phase = phase
        self.phase_progress[phase.value] = min(100, max(0, progress))
        
        # Publish phase update
        await self._publish_assistant_event("phase_updated", {
            "phase": phase.value,
            "progress": progress
        })
    
    async def _analyze_user_intent(self, message: str, context: AssistantContext) -> str:
        """Analyze user intent from message"""
        message_lower = message.lower()
        
        # Intent patterns by context
        intent_patterns = {
            AssistantContext.TRAINING: {
                "schedule": ["schedule", "plan", "create course", "training"],
                "progress": ["progress", "status", "completion", "results"],
                "recommend": ["recommend", "suggest", "what should", "help me"]
            },
            AssistantContext.EXERCISES: {
                "create": ["create", "new exercise", "tabletop", "drill"],
                "schedule": ["schedule", "plan", "when", "calendar"],
                "results": ["results", "report", "analysis", "lessons"]
            },
            AssistantContext.GOVERNANCE: {
                "check": ["check", "status", "compliance", "quota"],
                "optimize": ["optimize", "improve", "recommend", "suggest"],
                "report": ["report", "summary", "dashboard", "metrics"]
            },
            AssistantContext.DOCUMENTS: {
                "analyze": ["analyze", "review", "check", "compliance"],
                "upload": ["upload", "add", "new document", "create"],
                "link": ["link", "connect", "audit", "evidence"]
            }
        }
        
        patterns = intent_patterns.get(context, {})
        for intent, keywords in patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent
        
        return "general"
    
    async def _generate_response(self, message: str, intent: str, 
                                context: AssistantContext) -> tuple[str, List[NextBestAction]]:
        """Generate contextual response and actions"""
        try:
            # Get relevant actions for current context
            actions = await self.get_next_best_actions(context)
            
            # Generate response based on context and intent
            responses = {
                AssistantContext.TRAINING: {
                    "schedule": f"I can help you schedule training sessions. Based on your current BCM maturity level, I recommend focusing on {self._get_training_recommendations()}. Would you like me to create a training plan?",
                    "progress": "Let me check your training progress. I'll analyze completion rates and identify any gaps in your team's BCM knowledge.",
                    "recommend": f"For the {self.current_phase.value} phase, I suggest focusing on competency development. Here are some personalized recommendations based on your organization's needs."
                },
                AssistantContext.EXERCISES: {
                    "create": f"I'll help you create a new exercise. For the {self.current_phase.value} phase, I recommend starting with a tabletop exercise focusing on your highest risk scenarios.",
                    "schedule": "Let me suggest optimal timing for your next exercise based on your organization's calendar and previous exercise outcomes.",
                    "results": "I'll analyze your recent exercise results and identify key improvement areas. This will help inform your next PDCA cycle."
                },
                AssistantContext.GOVERNANCE: {
                    "check": f"Let me check your governance status. I'll review quotas, compliance checks, and system health for any issues requiring attention.",
                    "optimize": f"Based on your current {self.current_phase.value} phase activities, I can suggest several optimization opportunities.",
                    "report": "I'll generate a comprehensive governance report including compliance status, resource utilization, and recommendations."
                },
                AssistantContext.DOCUMENTS: {
                    "analyze": f"I'll analyze your documents for ISO 22301 compliance and suggest improvements aligned with your current {self.current_phase.value} phase objectives.",
                    "upload": "You can drag and drop documents here, and I'll automatically analyze them for BCM compliance and suggest appropriate categorization.",
                    "link": "I can help you link documents to audit evidence and ensure proper traceability for compliance requirements."
                }
            }
            
            context_responses = responses.get(context, {})
            response = context_responses.get(intent, 
                f"I'm here to help with your BCM activities. Based on your current {self.current_phase.value} phase, here are some suggestions.")
            
            return response, actions[:3]  # Return top 3 actions
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return "I'm sorry, I encountered an error. Please try again.", []
    
    async def _check_prerequisites(self, action: NextBestAction, tenant_id: str) -> bool:
        """Check if action prerequisites are met"""
        if not action.prerequisites:
            return True
        
        # Simplified prerequisite checking
        # In production, this would check actual system state
        return True
    
    def _priority_weight(self, priority: str) -> int:
        """Convert priority to weight for sorting"""
        weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return weights.get(priority, 2)
    
    def _get_training_recommendations(self) -> str:
        """Get phase-specific training recommendations"""
        recommendations = {
            PDCAPhase.PLAN: "risk assessment, business impact analysis, and strategy development",
            PDCAPhase.DO: "implementation planning, procedure development, and team training",
            PDCAPhase.CHECK: "monitoring techniques, audit procedures, and performance measurement",
            PDCAPhase.ACT: "continuous improvement, corrective actions, and management review"
        }
        return recommendations.get(self.current_phase, "fundamental BCM concepts")
    
    async def _publish_assistant_event(self, event_type: str, data: Dict[str, Any]):
        """Publish assistant events to EventBus"""
        try:
            event = {
                "event_type": f"bcm.assistant.{event_type}",
                "tenant_id": data.get("tenant_id", "demo"),
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "pdca_assistant"
            }
            
            response = await self.client.post(
                f"{self.eventbus_url}/api/events/publish",
                json=event
            )
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to publish assistant event: {e}")
    
    async def _initialize_pdca_scenarios(self):
        """Initialize PDCA-context scenarios"""
        scenarios = [
            # PLAN phase scenarios
            PDCAScenario(
                id="plan_training",
                name="Training Planning",
                phase=PDCAPhase.PLAN,
                context=AssistantContext.TRAINING,
                actions=[
                    NextBestAction(
                        id="create_training_plan",
                        phase=PDCAPhase.PLAN,
                        context=AssistantContext.TRAINING,
                        action_type=ActionType.CREATE,
                        title="Create Comprehensive Training Plan",
                        description="Develop a role-based training plan covering all BCM competencies",
                        priority="high",
                        confidence=0.9,
                        estimated_time=30,
                        api_endpoint="/lms/api/training-plans",
                        payload_template={"tenant_id": "demo", "type": "comprehensive"}
                    ),
                    NextBestAction(
                        id="assess_competency_gaps",
                        phase=PDCAPhase.PLAN,
                        context=AssistantContext.TRAINING,
                        action_type=ActionType.ANALYZE,
                        title="Assess Competency Gaps",
                        description="Analyze current team competencies and identify training needs",
                        priority="high",
                        confidence=0.85,
                        estimated_time=20
                    )
                ]
            ),
            
            # DO phase scenarios  
            PDCAScenario(
                id="do_exercises",
                name="Exercise Execution",
                phase=PDCAPhase.DO,
                context=AssistantContext.EXERCISES,
                actions=[
                    NextBestAction(
                        id="schedule_tabletop",
                        phase=PDCAPhase.DO,
                        context=AssistantContext.EXERCISES,
                        action_type=ActionType.SCHEDULE,
                        title="Schedule Tabletop Exercise",
                        description="Schedule a tabletop exercise for your highest risk scenario",
                        priority="high",
                        confidence=0.9,
                        estimated_time=15,
                        api_endpoint="/sim/api/exercises",
                        payload_template={"type": "tabletop", "tenant_id": "demo"}
                    ),
                    NextBestAction(
                        id="create_scenario",
                        phase=PDCAPhase.DO,
                        context=AssistantContext.EXERCISES,
                        action_type=ActionType.CREATE,
                        title="Create Exercise Scenario",
                        description="Develop a new exercise scenario based on recent risk assessments",
                        priority="medium",
                        confidence=0.8,
                        estimated_time=45
                    )
                ]
            ),
            
            # CHECK phase scenarios
            PDCAScenario(
                id="check_governance",
                name="Governance Review",
                phase=PDCAPhase.CHECK,
                context=AssistantContext.GOVERNANCE,
                actions=[
                    NextBestAction(
                        id="run_compliance_check",
                        phase=PDCAPhase.CHECK,
                        context=AssistantContext.GOVERNANCE,
                        action_type=ActionType.REVIEW,
                        title="Run Compliance Assessment",
                        description="Execute comprehensive compliance checks against ISO 22301",
                        priority="critical",
                        confidence=0.95,
                        estimated_time=10,
                        api_endpoint="/governance/api/compliance/check",
                        payload_template={"tenant_id": "demo", "standard": "ISO22301"}
                    ),
                    NextBestAction(
                        id="analyze_metrics",
                        phase=PDCAPhase.CHECK,
                        context=AssistantContext.GOVERNANCE,
                        action_type=ActionType.ANALYZE,
                        title="Analyze Performance Metrics",
                        description="Review KPIs and identify trends requiring attention",
                        priority="high",
                        confidence=0.85,
                        estimated_time=20
                    )
                ]
            ),
            
            # ACT phase scenarios
            PDCAScenario(
                id="act_improvements",
                name="Continuous Improvement",
                phase=PDCAPhase.ACT,
                context=AssistantContext.ORCHESTRATOR,
                actions=[
                    NextBestAction(
                        id="create_improvement_plan",
                        phase=PDCAPhase.ACT,
                        context=AssistantContext.ORCHESTRATOR,
                        action_type=ActionType.CREATE,
                        title="Create Improvement Plan",
                        description="Develop action plan based on audit findings and exercise results",
                        priority="high",
                        confidence=0.9,
                        estimated_time=25
                    ),
                    NextBestAction(
                        id="schedule_management_review",
                        phase=PDCAPhase.ACT,
                        context=AssistantContext.ORCHESTRATOR,
                        action_type=ActionType.SCHEDULE,
                        title="Schedule Management Review",
                        description="Schedule management review meeting to approve improvements",
                        priority="medium",
                        confidence=0.85,
                        estimated_time=10
                    )
                ]
            )
        ]
        
        # Store scenarios by phase_context key
        for scenario in scenarios:
            key = f"{scenario.phase.value}_{scenario.context.value}"
            self.scenarios[key] = scenario


# FastAPI service endpoint
if __name__ == "__main__":
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    
    app = FastAPI(title="PDCA AI Assistant Service")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    config = {
        "eventbus_url": "http://localhost:8001",
        "orchestrator_url": "http://localhost:8002"
    }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "pdca_assistant"}
    
    @app.post("/api/message")
    async def process_message(
        message: str, 
        context: AssistantContext, 
        tenant_id: str = "demo"
    ):
        async with PDCAAssistant(config) as assistant:
            response = await assistant.process_message(message, context, tenant_id)
            return response.dict()
    
    @app.get("/api/actions")
    async def get_actions(context: AssistantContext, tenant_id: str = "demo"):
        async with PDCAAssistant(config) as assistant:
            actions = await assistant.get_next_best_actions(context, tenant_id)
            return {"actions": [a.dict() for a in actions]}
    
    @app.post("/api/actions/{action_id}/execute")
    async def execute_action(action_id: str, parameters: Dict[str, Any] = None):
        async with PDCAAssistant(config) as assistant:
            result = await assistant.execute_action(action_id, parameters)
            return result
    
    @app.post("/api/phase/update")
    async def update_phase(phase: PDCAPhase, progress: float):
        async with PDCAAssistant(config) as assistant:
            await assistant.update_phase_progress(phase, progress)
            return {"status": "success"}
    
    uvicorn.run(app, host="0.0.0.0", port=8010)
