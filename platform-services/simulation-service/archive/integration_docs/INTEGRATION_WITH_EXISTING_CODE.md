# Integration with Existing Simulation Code

## 🔍 Discovered Existing Code

### Location: `/platform-services/simulation/scenarios/`

**Найдено:**

1. ✅ **Scenario Orchestrator** (576 lines)
   - Path: `scenarios/scenario_orchestrator/main.py`
   - Status: Working FastAPI service
   - Port: 8085

2. ✅ **BCM Incident Module** (Odoo)
   - Path: `scenarios/bcm_incident/`
   - Status: Odoo module with models, views, data

---

## 📊 Analysis of Existing Code

### 1. Scenario Orchestrator (scenario_orchestrator/main.py)

**Features Found:**

✅ **AI-Powered Scenario Generation**
```python
@app.post("/scenarios/generate")
async def generate_ai_scenario(request: ScenarioGenerationRequest):
    # Uses AI Orchestrator for scenario generation
    # Generates JaamSim configs for complex scenarios
    # Saves scenarios locally or to Odoo
```

**Request Model:**
```python
class ScenarioGenerationRequest(BaseModel):
    category: str  # epidemic, blackout, cyber, supply, natural, terrorism
    complexity: int = 3  # 1-5 scale
    duration_hours: int = 4
    participants: int = 10
    affected_systems: List[str] = []
    custom_objectives: List[str] = []
    organization_context: Optional[str] = None
```

✅ **Experience Accumulation System (Phase 5)**
```python
@app.post("/learning/exercise-result")
async def collect_exercise_result(result: ExerciseResult):
    # Collects exercise results
    # Accumulates learning data
    # Generates AI-powered improvements
    # Notifies AI Orchestrator
```

✅ **Learning Dashboard**
```python
@app.get("/learning/dashboard")
async def get_learning_dashboard():
    # Platform-wide effectiveness
    # Top performing scenarios
    # Scenarios needing improvement
```

✅ **JaamSim Config Generation**
```python
def _generate_jaamsim_config(request: ScenarioGenerationRequest) -> str:
    # Generates JaamSim .cfg files
    # Configures distributions, entities, servers
    # Sets exercise duration and participants
```

**Endpoints:**
- POST `/scenarios/generate` - Generate AI scenario
- GET `/scenarios/available` - Get scenarios from Odoo
- POST `/learning/exercise-result` - Collect exercise results
- GET `/learning/scenario/{id}/insights` - Get learning insights
- GET `/learning/dashboard` - Learning dashboard
- GET `/health` - Health check

### 2. BCM Incident Module (bcm_incident/)

**Structure:**
```
bcm_incident/
├── __manifest__.py       # Odoo module manifest
├── models/               # Data models
│   ├── bcm_incident_unified.py
│   ├── bcm_incident_integration_api.py
│   └── ai_communication_models.py
├── views/                # UI views
├── data/                 # Initial data
├── security/             # Access controls
└── migration/            # DB migrations
```

**Purpose:** Odoo-based BCM incident management

---

## 🔄 Integration Strategy

### What to Use from Existing Code

#### ✅ USE - Scenario Orchestrator Endpoints

**Integrate with our Simulation Service:**

```python
# In our simulation-service, add proxy/wrapper for scenario orchestrator

class ScenarioOrchestratorClient:
    """Client for existing Scenario Orchestrator service"""

    def __init__(self, base_url: str = "http://localhost:8085"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)

    async def generate_ai_scenario(
        self,
        category: str,
        complexity: int,
        duration_hours: int,
        participants: int,
        affected_systems: List[str] = None,
        custom_objectives: List[str] = None,
        organization_context: str = None
    ) -> Dict:
        """Call existing scenario generation endpoint"""
        response = await self.client.post(
            "/scenarios/generate",
            json={
                "category": category,
                "complexity": complexity,
                "duration_hours": duration_hours,
                "participants": participants,
                "affected_systems": affected_systems or [],
                "custom_objectives": custom_objectives or [],
                "organization_context": organization_context
            }
        )
        return response.json()

    async def collect_learning(
        self,
        exercise_result: Dict
    ) -> Dict:
        """Submit exercise results to learning system"""
        response = await self.client.post(
            "/learning/exercise-result",
            json=exercise_result
        )
        return response.json()

    async def get_learning_insights(
        self,
        scenario_id: str
    ) -> Dict:
        """Get accumulated learning for scenario"""
        response = await self.client.get(
            f"/learning/scenario/{scenario_id}/insights"
        )
        return response.json()
```

#### ✅ USE - JaamSim Config Generation

**Reuse existing JaamSim config generator:**

```python
# In our engines/jaamsim_engine.py

from scenarios.scenario_orchestrator.main import _generate_jaamsim_config

class JaamSimEngine(SimulationEngine):
    async def initialize(self, config: EngineConfig) -> bool:
        # Use existing config generator
        jaamsim_config = _generate_jaamsim_config(
            complexity=config.parameters.get("complexity", 3),
            category=config.parameters.get("category", "generic"),
            duration_hours=config.parameters.get("duration_hours", 4),
            participants=config.parameters.get("participants", 10)
        )

        # Save config and initialize JaamSim
        self.config_file = self._save_config(jaamsim_config)
        return True
```

#### ✅ USE - Learning System Integration

**Connect our results to existing learning system:**

```python
# In our core/orchestrator.py

async def integrate_learning(
    self,
    simulation_id: str,
    results: SimulationResult,
    session: AsyncSession,
    tenant_id: str = "default"
) -> Dict[str, Optional[str]]:
    """Integrate learning using existing systems"""

    learning_results = {}

    # 1. Submit to existing Scenario Orchestrator learning system
    scenario_orchestrator_client = ScenarioOrchestratorClient()

    exercise_result = {
        "exercise_id": simulation_id,
        "scenario_id": results.scenario_id,
        "template_id": results.template_id,
        "exercise_type": results.engine_used,
        "duration_actual_hours": results.duration_seconds / 3600,
        "participants_count": len(results.participant_performance),
        "success_metrics": results.metrics,
        "participant_feedback": results.participant_performance,
        "lessons_learned": results.lessons_learned,
        "improvement_suggestions": results.recommendations,
        "effectiveness_score": results.quality_score
    }

    learning_response = await scenario_orchestrator_client.collect_learning(
        exercise_result
    )
    learning_results["scenario_orchestrator_learning"] = learning_response

    # 2. Also do our PDCA cycle creation
    pdca_id = await self.workflow.create_pdca_cycle(...)
    learning_results["pdca_cycle_id"] = pdca_id

    # 3. Case Library storage
    case_id = await self.workflow.create_simulation_case(...)
    learning_results["case_id"] = case_id

    # etc...

    return learning_results
```

---

## 🎯 Integration Architecture

### Proposed Architecture

```
┌─────────────────────────────────────────────────────┐
│         NEW: Simulation Service (Port 8095)         │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │        Main Orchestrator                     │  │
│  │  - Full lifecycle management                 │  │
│  │  - Integration coordination                  │  │
│  └──────────────┬───────────────────────────────┘  │
│                 │                                    │
│  ┌──────────────┴───────────────────────────────┐  │
│  │     Integration Clients                      │  │
│  │  - AI Orchestrator                           │  │
│  │  - Workflow Intelligence                     │  │
│  │  - AI Foundation                             │  │
│  │  - Knowledge Center                          │  │
│  │  - Community Intelligence                    │  │
│  │  - Scenario Orchestrator ← NEW!              │  │
│  └──────────────┬───────────────────────────────┘  │
│                 │                                    │
└─────────────────┼────────────────────────────────────┘
                  │
                  ├─────────────────────────────┐
                  │                             │
                  ▼                             ▼
┌─────────────────────────────┐  ┌─────────────────────────────┐
│  EXISTING:                  │  │  EXISTING:                  │
│  Scenario Orchestrator      │  │  BCM Incident Module        │
│  (Port 8085)                │  │  (Odoo)                     │
│                             │  │                             │
│  - AI scenario generation   │  │  - Incident management      │
│  - Learning system          │  │  - Odoo integration         │
│  - JaamSim configs          │  │  - UI views                 │
│  - Insights dashboard       │  │                             │
└─────────────────────────────┘  └─────────────────────────────┘
```

---

## 📋 Implementation Plan

### Phase 1: Create Integration Client ✅ NEXT

**File:** `simulation-service/integration/scenario_orchestrator_client.py`

```python
"""
Scenario Orchestrator Integration Client

REAL integration with existing Scenario Orchestrator service (Port 8085)
for AI-powered scenario generation and learning accumulation
"""

import logging
from typing import Dict, List, Optional, Any
import httpx

from config.settings import Settings

logger = logging.getLogger(__name__)


class ScenarioOrchestratorClient:
    """
    Existing Scenario Orchestrator integration

    Provides:
    - AI scenario generation
    - Learning accumulation
    - Insights retrieval
    - JaamSim config generation
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = settings.scenario_orchestrator_url  # http://localhost:8085
        self.enabled = settings.scenario_orchestrator_enabled
        self.timeout = 60.0  # Longer for AI generation

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    # ========================================================================
    # SCENARIO GENERATION
    # ========================================================================

    async def generate_ai_scenario(
        self,
        category: str,
        complexity: int = 3,
        duration_hours: int = 4,
        participants: int = 10,
        affected_systems: Optional[List[str]] = None,
        custom_objectives: Optional[List[str]] = None,
        organization_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-powered scenario using existing service

        Args:
            category: epidemic, blackout, cyber, supply, natural, terrorism
            complexity: 1-5 scale
            duration_hours: Exercise duration
            participants: Number of participants
            affected_systems: List of affected systems
            custom_objectives: Custom exercise objectives
            organization_context: Organization context

        Returns:
            Generated scenario data
        """
        if not self.enabled:
            logger.debug("Scenario Orchestrator disabled")
            return {}

        try:
            response = await self.client.post(
                "/scenarios/generate",
                json={
                    "category": category,
                    "complexity": complexity,
                    "duration_hours": duration_hours,
                    "participants": participants,
                    "affected_systems": affected_systems or [],
                    "custom_objectives": custom_objectives or [],
                    "organization_context": organization_context
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"Scenario generated: {result.get('scenario_id')}")
            return result

        except httpx.HTTPError as e:
            logger.error(f"Scenario generation failed: {e}")
            return {}

    # ========================================================================
    # LEARNING SYSTEM
    # ========================================================================

    async def collect_exercise_result(
        self,
        exercise_id: str,
        scenario_id: str,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit exercise results to learning system

        Args:
            exercise_id: Exercise ID
            scenario_id: Scenario ID
            results: Exercise results

        Returns:
            Learning collection response
        """
        if not self.enabled:
            return {}

        try:
            response = await self.client.post(
                "/learning/exercise-result",
                json={
                    "exercise_id": exercise_id,
                    "scenario_id": scenario_id,
                    "template_id": results.get("template_id", ""),
                    "exercise_type": results.get("engine_used", ""),
                    "duration_actual_hours": results.get("duration_seconds", 0) / 3600,
                    "participants_count": results.get("participants_count", 0),
                    "success_metrics": results.get("metrics", {}),
                    "participant_feedback": results.get("participant_feedback", []),
                    "simulation_metrics": results.get("detailed_metrics"),
                    "lessons_learned": results.get("lessons_learned", []),
                    "improvement_suggestions": results.get("recommendations", []),
                    "effectiveness_score": results.get("quality_score", 0.0)
                }
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.warning(f"Learning collection failed: {e}")
            return {}

    async def get_learning_insights(
        self,
        scenario_id: str
    ) -> Dict[str, Any]:
        """
        Get accumulated learning insights for scenario

        Args:
            scenario_id: Scenario ID

        Returns:
            Learning insights
        """
        if not self.enabled:
            return {}

        try:
            response = await self.client.get(
                f"/learning/scenario/{scenario_id}/insights"
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.warning(f"Insights retrieval failed: {e}")
            return {}

    async def get_learning_dashboard(self) -> Dict[str, Any]:
        """
        Get learning dashboard data

        Returns:
            Dashboard data with platform-wide metrics
        """
        if not self.enabled:
            return {}

        try:
            response = await self.client.get("/learning/dashboard")
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.warning(f"Dashboard retrieval failed: {e}")
            return {}

    # ========================================================================
    # HEALTH CHECK
    # ========================================================================

    async def health_check(self) -> Dict:
        """Check Scenario Orchestrator health"""
        if not self.enabled:
            return {"status": "disabled", "connected": False}

        try:
            response = await self.client.get("/health", timeout=5.0)
            response.raise_for_status()
            return {
                "status": "healthy",
                "connected": True,
                "response": response.json()
            }
        except httpx.HTTPError as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }
```

### Phase 2: Update Settings ✅

**File:** `simulation-service/config/settings.py`

Add:
```python
# Scenario Orchestrator (existing service)
scenario_orchestrator_url: str = Field(
    default="http://localhost:8085",
    env="SCENARIO_ORCHESTRATOR_URL"
)
scenario_orchestrator_enabled: bool = Field(
    default=True,
    env="SCENARIO_ORCHESTRATOR_ENABLED"
)
```

### Phase 3: Update Main Orchestrator ✅

**File:** `simulation-service/core/orchestrator.py`

Add scenario_orchestrator_client to dependencies and use it.

### Phase 4: Update Integration __init__.py ✅

**File:** `simulation-service/integration/__init__.py`

Add:
```python
from .scenario_orchestrator_client import ScenarioOrchestratorClient

__all__ = [
    ...,
    "ScenarioOrchestratorClient"
]
```

---

## 🎯 Benefits of Integration

### What We Gain

1. ✅ **AI Scenario Generation** (already working!)
2. ✅ **Learning Accumulation System** (already working!)
3. ✅ **JaamSim Config Generation** (ready to use!)
4. ✅ **Insights Dashboard** (already working!)
5. ✅ **Experience-based Improvements** (AI-powered!)

### What We Keep

1. ✅ **Our Main Orchestrator** - Full lifecycle control
2. ✅ **Our Integration Clients** - All 6 platform integrations
3. ✅ **Our Report Generator** - Professional reports
4. ✅ **Our Scenario Generator** - Universal spec builder
5. ✅ **Our Architecture** - Modular, scalable

---

## 📊 Comparison

| Feature | Our Service | Existing Scenario Orchestrator | Decision |
|---------|-------------|--------------------------------|----------|
| Full Lifecycle | ✅ Yes | ❌ No | **Keep Ours** |
| AI Generation | ⚠️ Planned | ✅ Working | **Use Existing** |
| Learning System | ⚠️ Planned | ✅ Working | **Use Existing** |
| Platform Integration | ✅ 6 services | ⚠️ AI Orchestrator only | **Keep Ours** |
| Report Generation | ✅ Professional | ❌ No | **Keep Ours** |
| JaamSim Config | ⚠️ Planned | ✅ Working | **Use Existing** |
| PDCA Cycles | ✅ Yes | ❌ No | **Keep Ours** |
| Case Library | ✅ Yes | ❌ No | **Keep Ours** |
| Memory System | ✅ Yes | ❌ No | **Keep Ours** |
| Knowledge Center | ✅ Yes | ❌ No | **Keep Ours** |

**Conclusion:**
- ✅ Use Scenario Orchestrator for: AI generation, Learning, JaamSim configs
- ✅ Keep our service for: Full lifecycle, integrations, reporting, memory

---

## 🚀 Next Steps

### Immediate Actions

1. **Create ScenarioOrchestratorClient** (30 min)
2. **Add to settings.py** (5 min)
3. **Update main orchestrator** (15 min)
4. **Test integration** (30 min)

**Total Time:** ~90 minutes

### Testing

```bash
# 1. Start Scenario Orchestrator
cd /Users/MD/AI-Platform-ISO/platform-services/simulation/scenarios/scenario_orchestrator
python main.py  # Runs on 8085

# 2. Start our Simulation Service
cd /Users/MD/AI-Platform-ISO/platform-services/simulation/simulation-service
python main.py  # Runs on 8095

# 3. Test integration
curl -X POST http://localhost:8095/api/v1/simulations/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Test cyber attack scenario",
    "category": "cyber",
    "complexity": 4
  }'
```

---

## ✅ Summary

**Найдено ценного кода:**
- ✅ Scenario Orchestrator (576 lines, working service)
- ✅ AI scenario generation
- ✅ Learning accumulation system
- ✅ JaamSim config generation
- ✅ Insights dashboard

**Решение:**
- ✅ **INTEGRATE** (not replace!)
- ✅ Add ScenarioOrchestratorClient
- ✅ Use for AI generation & learning
- ✅ Keep our full-cycle orchestrator
- ✅ Best of both worlds!

**Время на интеграцию:** ~90 минут
**Выгода:** Получаем рабочий AI generation + learning system БЕСПЛАТНО!

---

*Created: 2025-10-12*
*Integration Analysis Complete*
