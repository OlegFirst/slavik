# Integration Requirements - Simulation Service

**Document Version**: 1.0
**Last Updated**: 2025-10-12
**Service**: Simulation & Modeling Service (Port 8095)

---

## 📋 Overview

This document specifies integration requirements for the Simulation Service with 8 platform services. Each integration is designed with graceful degradation - the service functions even if integrations are unavailable.

**Integration Architecture**: Event-driven choreography via EventBus + Direct HTTP clients for synchronous operations.

---

## 🔗 Integration Map

| Service | Port | Priority | Type | Status |
|---------|------|----------|------|--------|
| EventBus | 8055 | CRITICAL | Both | Required |
| AI Orchestrator | 8026 | HIGH | Both | Required |
| Workflow Intelligence | 8037 | HIGH | Both | Required |
| AI Foundation | 8025 | HIGH | Both | Required |
| Knowledge Center | 8038 | MEDIUM | Async | Optional |
| Community Intelligence | 8030 | MEDIUM | Async | Optional |
| Predictive Journey | 8031 | MEDIUM | Sync | Optional |
| Digital Twin | 8096 | LOW | Sync | Optional |

**Type Legend**:
- **Both**: Synchronous API calls + Asynchronous events
- **Async**: Event-based only
- **Sync**: API calls only

---

## 1️⃣ EventBus Integration (Port 8055)

**Priority**: CRITICAL
**Type**: Event Choreography
**Status**: Required

### Purpose
- Platform-wide event distribution
- Asynchronous service coordination
- Real-time progress broadcasting
- Automatic Case Library integration

### Events Published

#### 1.1 simulation.created
```json
{
  "type": "simulation.created",
  "source": "simulation-service",
  "timestamp": "2025-10-12T10:00:00Z",
  "payload": {
    "simulation_id": "sim_abc123",
    "specification_id": "spec_xyz789",
    "scenario_id": "scenario_def456",
    "engine": "jaamsim",
    "created_by": "user_123",
    "organization_id": "org_456",
    "metadata": {
      "goal": "Test BIA process resilience",
      "type": "exercise",
      "complexity": "high"
    }
  }
}
```

**Subscribers**: Knowledge Center, Community Intelligence, Workflow Intelligence

#### 1.2 simulation.started
```json
{
  "type": "simulation.started",
  "source": "simulation-service",
  "timestamp": "2025-10-12T10:01:00Z",
  "payload": {
    "simulation_id": "sim_abc123",
    "engine": "jaamsim",
    "start_time": "2025-10-12T10:01:00Z",
    "estimated_duration": 3600,
    "resource_allocation": {
      "cpu_cores": 2,
      "memory_mb": 2048
    }
  }
}
```

**Subscribers**: AI Orchestrator, Monitoring

#### 1.3 simulation.progress.updated
```json
{
  "type": "simulation.progress.updated",
  "source": "simulation-service",
  "timestamp": "2025-10-12T10:05:00Z",
  "payload": {
    "simulation_id": "sim_abc123",
    "progress_percent": 25,
    "current_step": "Running incident injection phase",
    "metrics": {
      "events_processed": 150,
      "resources_utilized": 45,
      "errors": 0
    }
  }
}
```

**Subscribers**: Real-time Dashboard, AI Orchestrator

#### 1.4 simulation.completed
```json
{
  "type": "simulation.completed",
  "source": "simulation-service",
  "timestamp": "2025-10-12T11:00:00Z",
  "payload": {
    "simulation_id": "sim_abc123",
    "status": "success",
    "duration_seconds": 3540,
    "summary": {
      "total_events": 1250,
      "incidents_handled": 12,
      "recovery_time": 180,
      "success_rate": 0.95
    },
    "results_url": "/api/v1/simulations/sim_abc123/results"
  }
}
```

**Subscribers**: Knowledge Center, Community Intelligence, Workflow Intelligence, Predictive Journey

#### 1.5 simulation.failed
```json
{
  "type": "simulation.failed",
  "source": "simulation-service",
  "timestamp": "2025-10-12T10:30:00Z",
  "payload": {
    "simulation_id": "sim_abc123",
    "error": "Engine timeout after 1800s",
    "error_code": "ENGINE_TIMEOUT",
    "partial_results": true,
    "recovery_possible": true
  }
}
```

**Subscribers**: AI Orchestrator, Monitoring, Knowledge Center

#### 1.6 simulation.case.created
```json
{
  "type": "simulation.case.created",
  "source": "simulation-service",
  "timestamp": "2025-10-12T11:05:00Z",
  "payload": {
    "case_id": "case_sim_123",
    "case_type": "simulation",
    "simulation_id": "sim_abc123",
    "quality_score": 8.5,
    "lessons_learned": [
      "Incident response time improved by 40%",
      "Communication protocol effective"
    ],
    "recommendations": [
      "Increase backup capacity",
      "Update recovery procedures"
    ],
    "metadata": {
      "scenario_type": "bia_exercise",
      "participants": 10,
      "complexity": "high"
    }
  }
}
```

**Subscribers**: Workflow Intelligence (Case Library), Knowledge Center

#### 1.7 simulation.knowledge.stored
```json
{
  "type": "simulation.knowledge.stored",
  "source": "simulation-service",
  "timestamp": "2025-10-12T11:06:00Z",
  "payload": {
    "simulation_id": "sim_abc123",
    "knowledge_id": "knowledge_xyz",
    "category": "best_practice",
    "title": "Effective BIA Exercise Protocol",
    "content": "...",
    "tags": ["bia", "exercise", "hospital", "high-complexity"]
  }
}
```

**Subscribers**: Knowledge Center, RAG Pipeline

#### 1.8 simulation.community.contributed
```json
{
  "type": "simulation.community.contributed",
  "source": "simulation-service",
  "timestamp": "2025-10-12T11:07:00Z",
  "payload": {
    "simulation_id": "sim_abc123",
    "contribution_id": "contrib_abc",
    "anonymized": true,
    "quality_score": 8.5,
    "scenario_template": {
      "type": "bia_exercise",
      "industry": "healthcare",
      "size": "large",
      "complexity": "high"
    }
  }
}
```

**Subscribers**: Community Intelligence

### Events Subscribed

#### 1.9 workflow.*.completed
```python
async def handle_workflow_completed(event: Event):
    """Auto-create simulation case when workflow completes"""
    if event.payload.get("create_simulation_case"):
        await create_simulation_case_from_workflow(
            workflow_id=event.payload["workflow_id"],
            results=event.payload["results"]
        )
```

**Pattern**: `workflow.*.completed`
**Purpose**: Automatic Case Library integration

#### 1.10 orchestrator.decision.needed
```python
async def handle_decision_needed(event: Event):
    """Run quick simulation for decision validation"""
    if event.payload.get("decision_type") == "critical":
        simulation = await create_what_if_simulation(
            decision=event.payload["decision"],
            context=event.payload["context"]
        )
        await run_simulation(simulation.id)
```

**Pattern**: `orchestrator.decision.needed`
**Purpose**: Decision validation via simulation

#### 1.11 platform.health.check
```python
async def handle_health_check(event: Event):
    """Respond to platform health checks"""
    health_status = await get_service_health()
    await eventbus.publish(Event(
        type="simulation.health.response",
        payload=health_status
    ))
```

**Pattern**: `platform.health.check`
**Purpose**: Platform monitoring

### Implementation

**File**: `integration/eventbus_client.py`

```python
from typing import Callable, Dict, List
from infrastructure.eventbus.choreography.event import Event
from infrastructure.eventbus.choreography.eventbus_client import EventBusClient as BaseClient

class SimulationEventBusClient:
    """EventBus integration for Simulation Service"""

    def __init__(self, eventbus_url: str, redis_url: str):
        self.client = BaseClient(
            service_name="simulation-service",
            redis_url=redis_url,
            eventbus_url=eventbus_url
        )
        self.handlers: Dict[str, Callable] = {}

    async def connect(self):
        """Connect to EventBus"""
        await self.client.connect()
        await self._subscribe_to_events()

    async def disconnect(self):
        """Disconnect from EventBus"""
        await self.client.disconnect()

    # Publish methods
    async def publish_simulation_created(self, simulation: Simulation):
        """Publish simulation.created event"""
        await self.client.publish(Event(
            type="simulation.created",
            source="simulation-service",
            payload={
                "simulation_id": simulation.id,
                "specification_id": simulation.specification_id,
                "scenario_id": simulation.scenario_id,
                "engine": simulation.engine.value,
                "created_by": simulation.created_by,
                "organization_id": simulation.organization_id,
                "metadata": simulation.metadata
            }
        ))

    async def publish_progress_update(
        self,
        simulation_id: str,
        progress: int,
        step: str,
        metrics: Dict
    ):
        """Publish simulation.progress.updated event"""
        await self.client.publish(Event(
            type="simulation.progress.updated",
            source="simulation-service",
            payload={
                "simulation_id": simulation_id,
                "progress_percent": progress,
                "current_step": step,
                "metrics": metrics
            }
        ))

    # Subscribe methods
    async def _subscribe_to_events(self):
        """Subscribe to relevant events"""
        await self.client.subscribe(
            pattern="workflow.*.completed",
            handler=self._handle_workflow_completed
        )
        await self.client.subscribe(
            pattern="orchestrator.decision.needed",
            handler=self._handle_decision_needed
        )
        await self.client.subscribe(
            pattern="platform.health.check",
            handler=self._handle_health_check
        )

    async def _handle_workflow_completed(self, event: Event):
        """Handle workflow completion"""
        if event.payload.get("create_simulation_case"):
            # Auto-create case
            pass

    async def _handle_decision_needed(self, event: Event):
        """Handle decision validation request"""
        if event.payload.get("decision_type") == "critical":
            # Run what-if simulation
            pass
```

### Configuration

```python
# config/settings.py
eventbus_url: str = Field(default="http://localhost:8055", env="EVENTBUS_URL")
eventbus_redis_url: str = Field(default="redis://localhost:6379/1", env="EVENTBUS_REDIS_URL")
eventbus_enabled: bool = Field(default=True, env="EVENTBUS_ENABLED")
```

### Error Handling

```python
async def publish_with_retry(event: Event, max_retries: int = 3):
    """Publish event with retry logic"""
    for attempt in range(max_retries):
        try:
            await self.client.publish(event)
            return
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to publish event after {max_retries} attempts: {e}")
                # Store in dead letter queue
                await self._store_in_dlq(event)
            else:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### Testing

```python
# tests/integration/test_eventbus.py
async def test_simulation_created_event():
    client = SimulationEventBusClient(...)
    await client.connect()

    simulation = create_test_simulation()
    await client.publish_simulation_created(simulation)

    # Verify event published
    events = await get_published_events()
    assert len(events) == 1
    assert events[0].type == "simulation.created"
```

---

## 2️⃣ AI Orchestrator Integration (Port 8026)

**Priority**: HIGH
**Type**: Both (API + Events)
**Status**: Required

### Purpose
- Specification validation before simulation
- Autonomous decision-making during simulation
- Result analysis and pattern recognition
- Memory system integration

### API Endpoints Used

#### 2.1 Validate Specification
```http
POST /api/v1/validate/specification
Content-Type: application/json

{
  "specification": {
    "goal": "Test BIA process resilience",
    "constraints": {...},
    "context": {...}
  },
  "simulation_context": {
    "organization_type": "hospital",
    "previous_simulations": []
  }
}

Response 200 OK:
{
  "is_valid": true,
  "confidence": 0.92,
  "suggestions": [
    "Consider adding cyber incident scenario",
    "Increase participant count for better results"
  ],
  "risk_assessment": {
    "complexity": "high",
    "resource_requirements": "moderate",
    "estimated_duration": 3600
  }
}
```

**When to call**: Before creating simulation

#### 2.2 Request Decision
```http
POST /api/v1/decide
Content-Type: application/json

{
  "decision_type": "inject_timing",
  "context": {
    "simulation_id": "sim_abc123",
    "current_progress": 0.4,
    "participant_status": "engaged",
    "events_so_far": 120
  },
  "options": [
    {"inject": "cyber_attack", "timing": "now"},
    {"inject": "cyber_attack", "timing": "after_30min"},
    {"skip": true}
  ]
}

Response 200 OK:
{
  "decision": {
    "inject": "cyber_attack",
    "timing": "after_30min",
    "reason": "Participants showing good handling, escalate complexity gradually"
  },
  "confidence": 0.87,
  "alternative_considered": {...}
}
```

**When to call**: During simulation for event injection decisions

#### 2.3 Analyze Results
```http
POST /api/v1/analyze/simulation-results
Content-Type: application/json

{
  "simulation_id": "sim_abc123",
  "results": {
    "total_events": 1250,
    "incidents_handled": 12,
    "recovery_time": 180,
    "success_rate": 0.95
  },
  "specification": {...},
  "scenario": {...}
}

Response 200 OK:
{
  "analysis": {
    "strengths": [
      "Excellent incident response time",
      "Effective communication protocol"
    ],
    "weaknesses": [
      "Backup capacity insufficient",
      "Recovery procedures outdated"
    ],
    "patterns_identified": [
      "Similar to successful exercise from 2024-09",
      "Follows industry best practice pattern"
    ],
    "recommendations": [
      "Update backup strategy",
      "Schedule recovery drill"
    ]
  },
  "quality_score": 8.5,
  "contribution_worthy": true
}
```

**When to call**: After simulation completion

#### 2.4 Store Memory
```http
POST /api/v1/memory/store
Content-Type: application/json

{
  "memory_type": "simulation_pattern",
  "content": {
    "simulation_id": "sim_abc123",
    "pattern": "bia_exercise_hospital_large",
    "key_factors": [...],
    "success_indicators": [...],
    "lessons_learned": [...]
  },
  "layer": "long_term",
  "retention_policy": "permanent"
}

Response 200 OK:
{
  "memory_id": "mem_xyz789",
  "stored_at": "long_term",
  "indexed": true
}
```

**When to call**: After successful simulation for pattern storage

### Implementation

**File**: `integration/orchestrator_client.py`

```python
import httpx
from typing import Dict, List, Optional
from models.pydantic_models import TaskSpecification, SimulationResult

class OrchestratorClient:
    """AI Orchestrator integration client"""

    def __init__(self, base_url: str, enabled: bool = True):
        self.base_url = base_url
        self.enabled = enabled
        self.client = httpx.AsyncClient(timeout=30.0)

    async def validate_specification(
        self,
        spec: TaskSpecification,
        context: Optional[Dict] = None
    ) -> Dict:
        """Validate specification before simulation"""
        if not self.enabled:
            return {"is_valid": True, "confidence": 1.0}

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/validate/specification",
                json={
                    "specification": spec.dict(),
                    "simulation_context": context or {}
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Orchestrator validation failed: {e}")
            return {"is_valid": True, "confidence": 0.5}

    async def decide_inject_timing(
        self,
        simulation_id: str,
        context: Dict,
        options: List[Dict]
    ) -> Dict:
        """Get AI decision for event injection"""
        if not self.enabled:
            return options[0] if options else {}

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/decide",
                json={
                    "decision_type": "inject_timing",
                    "context": {
                        "simulation_id": simulation_id,
                        **context
                    },
                    "options": options
                }
            )
            response.raise_for_status()
            return response.json()["decision"]
        except Exception as e:
            logger.warning(f"Orchestrator decision failed: {e}")
            return options[0] if options else {}

    async def analyze_results(
        self,
        simulation_id: str,
        results: SimulationResult,
        spec: TaskSpecification
    ) -> Dict:
        """Analyze simulation results with AI"""
        if not self.enabled:
            return {"analysis": {}, "quality_score": 7.0}

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/analyze/simulation-results",
                json={
                    "simulation_id": simulation_id,
                    "results": results.dict(),
                    "specification": spec.dict()
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Orchestrator analysis failed: {e}")
            return {"analysis": {}, "quality_score": 7.0}

    async def store_simulation_pattern(
        self,
        simulation_id: str,
        pattern: Dict
    ) -> Optional[str]:
        """Store simulation pattern in Memory System"""
        if not self.enabled:
            return None

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/memory/store",
                json={
                    "memory_type": "simulation_pattern",
                    "content": {
                        "simulation_id": simulation_id,
                        **pattern
                    },
                    "layer": "long_term",
                    "retention_policy": "permanent"
                }
            )
            response.raise_for_status()
            return response.json()["memory_id"]
        except Exception as e:
            logger.warning(f"Pattern storage failed: {e}")
            return None
```

### Configuration

```python
ai_orchestrator_url: str = Field(default="http://localhost:8026", env="AI_ORCHESTRATOR_URL")
ai_orchestrator_enabled: bool = Field(default=True, env="AI_ORCHESTRATOR_ENABLED")
ai_orchestrator_timeout: int = Field(default=30, env="AI_ORCHESTRATOR_TIMEOUT")
```

---

## 3️⃣ Workflow Intelligence Integration (Port 8037)

**Priority**: HIGH
**Type**: Both (API + Events)
**Status**: Required

### Purpose
- PDCA cycle creation for simulations
- Case Library integration (Simulation cases)
- Process framework utilization
- Continuous improvement tracking

### API Endpoints Used

#### 3.1 Create PDCA Cycle
```http
POST /api/v1/pdca/cycles
Content-Type: application/json

{
  "type": "simulation_improvement",
  "plan": {
    "goal": "Improve BIA exercise effectiveness",
    "based_on_simulation": "sim_abc123",
    "metrics": ["response_time", "success_rate", "participant_engagement"]
  },
  "do": {
    "actions": [
      "Update incident response procedures",
      "Train additional staff"
    ],
    "scheduled_simulation": "pending"
  }
}

Response 201 Created:
{
  "cycle_id": "pdca_xyz789",
  "status": "plan",
  "next_phase": "do",
  "simulation_tracking": true
}
```

**When to call**: After simulation completion with improvement recommendations

#### 3.2 Create Simulation Case
```http
POST /api/v1/cases
Content-Type: application/json

{
  "case_type": "simulation",
  "source": "simulation-service",
  "source_id": "sim_abc123",
  "title": "Successful BIA Exercise - Hospital Large",
  "description": "...",
  "lessons_learned": [...],
  "best_practices": [...],
  "context": {
    "organization_type": "hospital",
    "organization_size": "large",
    "complexity": "high"
  },
  "quality_score": 8.5,
  "tags": ["bia", "exercise", "hospital", "incident_response"]
}

Response 201 Created:
{
  "case_id": "case_sim_123",
  "case_type": "simulation",
  "status": "published",
  "indexed_for_rag": true
}
```

**When to call**: After successful simulation with quality_score >= threshold

#### 3.3 Search Cases
```http
GET /api/v1/cases/search?
  query=hospital+bia+exercise&
  case_type=simulation&
  min_quality_score=7.0&
  limit=10

Response 200 OK:
{
  "cases": [
    {
      "case_id": "case_sim_456",
      "title": "Hospital BIA Exercise - Medium Complexity",
      "similarity_score": 0.89,
      "context": {...},
      "lessons_learned": [...]
    }
  ],
  "total": 15,
  "page": 1
}
```

**When to call**: Before scenario generation to find similar cases

### Implementation

**File**: `integration/workflow_client.py`

```python
class WorkflowIntelligenceClient:
    """Workflow Intelligence integration"""

    def __init__(self, base_url: str, enabled: bool = True):
        self.base_url = base_url
        self.enabled = enabled
        self.client = httpx.AsyncClient()

    async def create_pdca_cycle(
        self,
        simulation: Simulation,
        recommendations: List[str]
    ) -> Optional[str]:
        """Create PDCA cycle for continuous improvement"""
        if not self.enabled:
            return None

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/pdca/cycles",
                json={
                    "type": "simulation_improvement",
                    "plan": {
                        "goal": f"Improve {simulation.specification.goal}",
                        "based_on_simulation": simulation.id,
                        "recommendations": recommendations
                    },
                    "metadata": {
                        "simulation_id": simulation.id,
                        "quality_score": simulation.results.quality_score
                    }
                }
            )
            response.raise_for_status()
            return response.json()["cycle_id"]
        except Exception as e:
            logger.warning(f"PDCA creation failed: {e}")
            return None

    async def create_simulation_case(
        self,
        simulation: Simulation,
        results: SimulationResult,
        quality_score: float
    ) -> Optional[str]:
        """Create case in Case Library"""
        if not self.enabled or quality_score < 7.0:
            return None

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/cases",
                json={
                    "case_type": "simulation",
                    "source": "simulation-service",
                    "source_id": simulation.id,
                    "title": f"{simulation.specification.goal} - {results.status}",
                    "description": results.summary,
                    "lessons_learned": results.lessons_learned,
                    "best_practices": results.best_practices,
                    "context": simulation.specification.context,
                    "quality_score": quality_score,
                    "tags": self._generate_tags(simulation)
                }
            )
            response.raise_for_status()
            return response.json()["case_id"]
        except Exception as e:
            logger.warning(f"Case creation failed: {e}")
            return None

    async def search_similar_cases(
        self,
        query: str,
        context: Optional[Dict] = None,
        min_quality: float = 7.0
    ) -> List[Dict]:
        """Search for similar simulation cases"""
        if not self.enabled:
            return []

        try:
            params = {
                "query": query,
                "case_type": "simulation",
                "min_quality_score": min_quality,
                "limit": 10
            }
            response = await self.client.get(
                f"{self.base_url}/api/v1/cases/search",
                params=params
            )
            response.raise_for_status()
            return response.json()["cases"]
        except Exception as e:
            logger.warning(f"Case search failed: {e}")
            return []
```

---

## 4️⃣ AI Foundation Integration (Port 8025)

**Priority**: HIGH
**Type**: API
**Status**: Required

### Purpose
- RAG search for scenarios
- LLM-powered specification generation
- ML predictions for simulation outcomes
- Embedding generation for similarity search

### API Endpoints Used

#### 4.1 RAG Search
```http
POST /api/v1/rag/search
Content-Type: application/json

{
  "collection": "simulation_scenarios",
  "query": "hospital BIA exercise with cyber incident",
  "filters": {
    "organization_type": "hospital",
    "complexity": "high"
  },
  "limit": 5,
  "similarity_threshold": 0.7
}

Response 200 OK:
{
  "results": [
    {
      "id": "scenario_123",
      "content": "...",
      "similarity_score": 0.89,
      "metadata": {...}
    }
  ],
  "total": 12
}
```

#### 4.2 LLM Generation
```http
POST /api/v1/llm/generate
Content-Type: application/json

{
  "prompt": "Generate a detailed BCM simulation specification for...",
  "model": "claude-3-sonnet",
  "temperature": 0.8,
  "max_tokens": 2000,
  "context": {
    "organization_type": "hospital",
    "previous_exercises": [...]
  }
}

Response 200 OK:
{
  "generated_text": "...",
  "model_used": "claude-3-sonnet",
  "tokens_used": 1847
}
```

#### 4.3 ML Prediction
```http
POST /api/v1/ml/predict
Content-Type: application/json

{
  "model": "simulation_outcome_predictor",
  "features": {
    "organization_size": "large",
    "complexity": "high",
    "participants": 10,
    "duration_hours": 4,
    "scenario_type": "bia_exercise"
  }
}

Response 200 OK:
{
  "prediction": {
    "success_probability": 0.87,
    "estimated_duration": 3540,
    "risk_factors": ["complexity", "participant_count"],
    "recommendations": [...]
  }
}
```

### Implementation

**File**: `integration/foundation_client.py`

```python
class AIFoundationClient:
    """AI Foundation integration"""

    def __init__(self, base_url: str, enabled: bool = True):
        self.base_url = base_url
        self.enabled = enabled
        self.client = httpx.AsyncClient()

    async def rag_search(
        self,
        query: str,
        collection: str = "simulation_scenarios",
        filters: Optional[Dict] = None,
        limit: int = 5
    ) -> List[Dict]:
        """Search scenarios using RAG"""
        if not self.enabled:
            return []

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/rag/search",
                json={
                    "collection": collection,
                    "query": query,
                    "filters": filters or {},
                    "limit": limit,
                    "similarity_threshold": 0.7
                }
            )
            response.raise_for_status()
            return response.json()["results"]
        except Exception as e:
            logger.warning(f"RAG search failed: {e}")
            return []

    async def generate_specification(
        self,
        goal: str,
        context: Dict,
        model: str = "claude-3-sonnet"
    ) -> Optional[str]:
        """Generate specification using LLM"""
        if not self.enabled:
            return None

        prompt = self._build_spec_prompt(goal, context)

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/llm/generate",
                json={
                    "prompt": prompt,
                    "model": model,
                    "temperature": 0.8,
                    "max_tokens": 2000
                }
            )
            response.raise_for_status()
            return response.json()["generated_text"]
        except Exception as e:
            logger.warning(f"LLM generation failed: {e}")
            return None

    async def predict_outcome(
        self,
        specification: TaskSpecification
    ) -> Dict:
        """Predict simulation outcome"""
        if not self.enabled:
            return {}

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/ml/predict",
                json={
                    "model": "simulation_outcome_predictor",
                    "features": self._extract_features(specification)
                }
            )
            response.raise_for_status()
            return response.json()["prediction"]
        except Exception as e:
            logger.warning(f"ML prediction failed: {e}")
            return {}
```

---

## 5️⃣ Knowledge Center Integration (Port 8038)

**Priority**: MEDIUM
**Type**: Async (Events)
**Status**: Optional

### Purpose
- Store successful simulation patterns
- Store lessons learned
- Store best practices
- Enable organizational learning

### Events Consumed

#### 5.1 simulation.knowledge.stored
The Knowledge Center subscribes to this event and automatically stores knowledge.

### Implementation

```python
# Automatic via EventBus
async def store_knowledge_after_simulation(simulation: Simulation, results: SimulationResult):
    """Automatically store knowledge in Knowledge Center"""
    if results.quality_score >= 8.0:
        await eventbus.publish(Event(
            type="simulation.knowledge.stored",
            payload={
                "simulation_id": simulation.id,
                "knowledge_id": f"knowledge_{simulation.id}",
                "category": "best_practice",
                "title": f"Effective {simulation.specification.goal}",
                "content": results.lessons_learned,
                "tags": _generate_tags(simulation)
            }
        ))
```

---

## 6️⃣ Community Intelligence Integration (Port 8030)

**Priority**: MEDIUM
**Type**: Async (Events)
**Status**: Optional

### Purpose
- Share successful scenarios with community
- Get peer review and feedback
- Access community templates
- Reputation and contribution tracking

### Events Consumed

#### 6.1 simulation.community.contributed
The Community Intelligence service subscribes and processes contributions.

### Implementation

```python
async def contribute_to_community(simulation: Simulation, results: SimulationResult):
    """Contribute simulation to community"""
    if results.quality_score >= settings.auto_contribution_min_quality_score:
        # Anonymize data
        anonymized = await anonymize_simulation(simulation, results)

        await eventbus.publish(Event(
            type="simulation.community.contributed",
            payload={
                "simulation_id": simulation.id,
                "contribution_id": f"contrib_{uuid.uuid4()}",
                "anonymized": True,
                "quality_score": results.quality_score,
                "scenario_template": anonymized
            }
        ))
```

---

## 7️⃣ Predictive Journey Integration (Port 8031)

**Priority**: MEDIUM
**Type**: API
**Status**: Optional

### Purpose
- Pre-simulation outcome forecasting
- Recommendation engine
- Risk assessment

### API Endpoints Used

#### 7.1 Forecast Outcome
```http
POST /api/v1/forecast/simulation
Content-Type: application/json

{
  "specification": {...},
  "historical_data": [...],
  "context": {...}
}

Response 200 OK:
{
  "forecast": {
    "success_probability": 0.85,
    "estimated_metrics": {...},
    "risk_factors": [...],
    "recommendations": [...]
  }
}
```

---

## 8️⃣ Digital Twin Integration (Port 8096)

**Priority**: LOW
**Type**: API
**Status**: Optional

### Purpose
- Load real organization data
- Realistic simulation parameters
- Validation against actual metrics

### API Endpoints Used

#### 8.1 Get Organization Model
```http
GET /api/v1/organization/{org_id}/model

Response 200 OK:
{
  "organization": {
    "id": "org_456",
    "type": "hospital",
    "size": "large",
    "departments": [...],
    "resources": {...},
    "processes": {...}
  }
}
```

---

## 📊 Integration Health Monitoring

### Health Check Endpoints

```python
@app.get("/health/integrations")
async def integration_health():
    """Check all integration health"""
    return {
        "eventbus": await check_eventbus_health(),
        "ai_orchestrator": await check_orchestrator_health(),
        "workflow_intelligence": await check_workflow_health(),
        "ai_foundation": await check_foundation_health(),
        "knowledge_center": await check_knowledge_health(),
        "community_intelligence": await check_community_health(),
        "predictive_journey": await check_predictive_health(),
        "digital_twin": await check_digital_twin_health()
    }
```

### Graceful Degradation Matrix

| Integration | If Unavailable | Fallback Behavior |
|-------------|----------------|-------------------|
| EventBus | Service continues | Log events locally, sync later |
| AI Orchestrator | Service continues | Use rule-based decisions |
| Workflow Intelligence | Service continues | Skip PDCA, skip Case Library |
| AI Foundation | Service continues | Use local LLM or manual input |
| Knowledge Center | Service continues | Skip auto-storage |
| Community Intelligence | Service continues | Skip auto-contribution |
| Predictive Journey | Service continues | Skip forecasting |
| Digital Twin | Service continues | Use manual parameters |

---

## 🧪 Testing Integration

### Integration Test Template

```python
# tests/integration/test_orchestrator_integration.py
@pytest.mark.integration
async def test_orchestrator_validation():
    """Test AI Orchestrator specification validation"""
    client = OrchestratorClient(...)

    spec = TaskSpecification(
        goal="Test BIA process",
        constraints={},
        context={"type": "hospital"}
    )

    result = await client.validate_specification(spec)

    assert result["is_valid"] == True
    assert result["confidence"] > 0.7
    assert "suggestions" in result
```

---

**Last Updated**: 2025-10-12
**Next Review**: After Phase 1 completion
