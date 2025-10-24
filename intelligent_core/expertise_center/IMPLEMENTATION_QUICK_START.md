# 🚀 LIVING ARCHITECTURE - Quick Start Implementation

**Цель:** За 1 день запустить базовую живую архитектуру Expertise Center
**Статус:** 🟢 READY TO IMPLEMENT

---

## 📋 IMPLEMENTATION CHECKLIST

### Day 1: Core Foundation (6-8 hours)

#### Step 1: Create Directory Structure (30 min)

```bash
cd /Users/MD/AI-Platform-ISO/intelligent_core/expertise_center

# Create new directories
mkdir -p core flows integration orchestration

# Directory structure:
# expertise_center/
# ├── core/               # Core components
# │   ├── expertise_hub.py
# │   ├── knowledge_graph.py
# │   ├── specialists_pool.py
# │   └── action_tracker.py
# ├── flows/              # Living flows
# │   ├── __init__.py
# │   ├── sensing_flow.py
# │   ├── learning_flow.py
# │   ├── thinking_flow.py
# │   ├── acting_flow.py
# │   └── evolution_flow.py
# ├── integration/        # Ecosystem integration
# │   ├── __init__.py
# │   ├── ecosystem_integration.py
# │   ├── workflow_intel_bridge.py
# │   ├── event_intel_bridge.py
# │   └── services_bridge.py
# └── orchestration/      # Coordination
#     ├── __init__.py
#     └── living_orchestrator.py
```

#### Step 2: Implement Core Hub (2 hours)

Используй существующие компоненты как foundation:
- ✅ `infrastructure_consultation.py` - уже есть консультации
- ✅ `metrics_exporter.py` - уже есть метрики
- ✅ `shared/` - уже есть base classes
- ✅ `ai_experts/` - уже есть эксперты

**Extend, not replace!**

#### Step 3: Implement Key Flows (3 hours)

**Priority order:**
1. ✅ **Sensing Flow** - начни здесь (базовое восприятие)
2. ✅ **Learning Flow** - подключи к case library
3. ✅ **Acting Flow** - используй существующую consultation API

**Skip for MVP:**
- ⏸️ Thinking Flow (can use simplified version)
- ⏸️ Evolution Flow (add in Phase 2)

#### Step 4: Basic Integration (2 hours)

**Connect to:**
1. ✅ Workflow Intelligence (case library)
2. ✅ Event Intelligence (patterns)
3. ✅ AI Foundation (RAG, LLM)

**Skip for MVP:**
- ⏸️ Community Intelligence
- ⏸️ Collective
- ⏸️ 12 Services (add gradually)

#### Step 5: Test & Verify (1 hour)

```python
# Simple test
from expertise_center.core.expertise_hub import ExpertiseHub

hub = ExpertiseHub()
await hub.start()

# Test consultation
result = await hub.consult(
    question="Should we restart the database service?",
    context={"memory_percent": 95, "recovery_attempts": 1}
)

print(result)  # Should get smart recommendation
```

---

## 🎯 MVP ARCHITECTURE (Simplified for Day 1)

```
┌─────────────────────────────────────┐
│     Expertise Hub (Core)            │
│  - Coordinates all flows            │
│  - Manages knowledge                │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    ↓                     ↓
┌─────────┐         ┌──────────┐
│ Sensing │         │ Acting   │
│ Flow    │────────→│ Flow     │
└────┬────┘         └────┬─────┘
     │                   │
     ↓                   ↓
┌─────────────┐    ┌──────────┐
│ Learning    │    │ Existing │
│ Flow        │    │ Consult  │
└─────────────┘    │ API      │
                   └──────────┘
```

**Core Loop:**
1. **Sense** events from workflow intelligence
2. **Learn** from cases
3. **Act** through consultation API
4. **Repeat** continuously

---

## 💻 CODE SNIPPETS (Copy-Paste Ready)

### 1. Minimal Expertise Hub

```python
# /core/expertise_hub.py (Minimal MVP)

import asyncio
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ExpertiseHub:
    """Minimal MVP - Living Expertise Center Core"""

    def __init__(self):
        # Will connect to existing components
        self._workflow_client = None
        self._event_client = None
        self._ai_foundation = None

        # Simple knowledge store (MVP)
        self._knowledge = []
        self._cases = []

        # Track consultations for learning
        self._consultations = []

        logger.info("🧠 Expertise Hub initialized (MVP)")

    async def start(self):
        """Start the living system"""
        logger.info("🌱 Starting Living Expertise System...")

        # Start sensing (simple version)
        asyncio.create_task(self._sense_continuously())

        # Start learning (simple version)
        asyncio.create_task(self._learn_continuously())

        logger.info("✅ Living system started!")

    async def _sense_continuously(self):
        """MVP Sensing - just log for now"""
        while True:
            # TODO: Connect to workflow intelligence
            # TODO: Connect to event intelligence
            logger.debug("👁️ Sensing... (MVP mode)")
            await asyncio.sleep(30)

    async def _learn_continuously(self):
        """MVP Learning - from consultations"""
        while True:
            if len(self._consultations) > 10:
                # Simple learning: find patterns
                logger.info(f"📚 Learning from {len(self._consultations)} consultations...")
                # TODO: Implement pattern detection
            await asyncio.sleep(60)

    async def consult(
        self,
        question: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Main consultation API"""

        # Use existing infrastructure_consultation
        from intelligent_core.expertise_center.infrastructure_consultation import (
            InfrastructureConsultationAPI
        )

        api = InfrastructureConsultationAPI()

        # Extract service and action from question
        service, action = self._parse_question(question)

        # Get consultation
        result = await api.consult(
            service=service,
            action=action,
            reason=question,
            context=context
        )

        # Track for learning
        self._consultations.append({
            'question': question,
            'context': context,
            'result': result
        })

        return result

    def _parse_question(self, question: str) -> tuple:
        """Simple question parsing (MVP)"""
        # TODO: Use NLP for better parsing
        if "database" in question.lower():
            service = "database"
        elif "redis" in question.lower():
            service = "redis"
        else:
            service = "unknown"

        if "restart" in question.lower():
            action = "restart"
        elif "scale" in question.lower():
            action = "scale_up"
        else:
            action = "investigate"

        return service, action
```

### 2. Simple Sensing Flow

```python
# /flows/sensing_flow.py (MVP)

import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SensingFlow:
    """MVP Sensing Flow - Basic version"""

    def __init__(self, expertise_hub):
        self.hub = expertise_hub
        self._signals = []

    async def sense_continuously(self):
        """Continuous sensing (simplified)"""
        while True:
            # Collect signals
            signals = await self._collect_signals()

            # Send to hub for processing
            if signals:
                await self.hub.process_signals(signals)

            await asyncio.sleep(10)  # Sense every 10 seconds

    async def _collect_signals(self) -> Dict[str, Any]:
        """Collect signals from environment"""
        # MVP: Just return placeholder
        # TODO: Connect to real sources
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'sources': ['workflow', 'events', 'services'],
            'signals': []
        }
```

### 3. Integration Bridge (Workflow Intelligence)

```python
# /integration/workflow_intel_bridge.py

from typing import Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)

class WorkflowIntelligenceBridge:
    """Bridge to Workflow Intelligence"""

    def __init__(self, workflow_intel_url: str = "http://localhost:8037"):
        self.base_url = workflow_intel_url
        self._callbacks = []

    async def subscribe_to_cases(self, callback: Callable):
        """Subscribe to workflow case updates"""
        self._callbacks.append(callback)
        logger.info("✅ Subscribed to workflow cases")

        # TODO: Implement actual subscription via EventBus
        # For MVP: poll periodically
        asyncio.create_task(self._poll_cases())

    async def _poll_cases(self):
        """MVP: Poll for new cases"""
        while True:
            try:
                # TODO: Fetch new cases from workflow intelligence
                # For now, just placeholder
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Error polling cases: {e}")
                await asyncio.sleep(60)

    async def get_case_library(self) -> list:
        """Get cases from library"""
        # TODO: Implement actual API call
        return []

    async def add_expertise_to_workflow(
        self,
        workflow_id: str,
        expertise: Dict[str, Any]
    ):
        """Add expertise to a workflow"""
        # TODO: Implement
        logger.info(f"Added expertise to workflow {workflow_id}")
```

---

## 🏃 RUNNING IT

### Option A: Standalone (Quick Test)

```python
# test_living_system.py

import asyncio
from expertise_center.core.expertise_hub import ExpertiseHub

async def main():
    # Create hub
    hub = ExpertiseHub()

    # Start living system
    await hub.start()

    # Test consultation
    result = await hub.consult(
        question="Should we restart the database due to high memory?",
        context={
            "service": "database",
            "memory_percent": 95,
            "cpu_percent": 80,
            "recovery_attempts": 1
        }
    )

    print("Consultation Result:")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Reasoning: {result['reasoning']}")

    # Keep running
    await asyncio.sleep(3600)  # Run for 1 hour

if __name__ == "__main__":
    asyncio.run(main())
```

### Option B: As Service (Production)

```python
# main.py (update existing)

from fastapi import FastAPI
from expertise_center.core.expertise_hub import ExpertiseHub

app = FastAPI(title="Living Expertise Center")

# Global hub instance
hub = None

@app.on_event("startup")
async def startup():
    global hub
    hub = ExpertiseHub()
    await hub.start()
    logger.info("🌱 Living Expertise Center started!")

@app.post("/api/v1/consult")
async def consult(request: ConsultRequest):
    """Consultation endpoint"""
    result = await hub.consult(
        question=request.question,
        context=request.context
    )
    return result

@app.get("/api/v1/knowledge/stats")
async def knowledge_stats():
    """Get knowledge base statistics"""
    return {
        "cases_learned": len(hub._cases),
        "consultations_performed": len(hub._consultations),
        "knowledge_items": len(hub._knowledge)
    }

@app.get("/health")
async def health():
    return {
        "status": "alive" if hub else "dead",
        "system": "living",
        "capabilities": ["sensing", "learning", "acting"]
    }
```

---

## 📊 MONITORING (Day 1)

### Basic Metrics

```python
# metrics.py (add to existing metrics_exporter.py)

from prometheus_client import Counter, Gauge, Histogram

# Living system metrics
expertise_consultations = Counter(
    'expertise_center_consultations_total',
    'Total consultations performed'
)

expertise_learning_events = Counter(
    'expertise_center_learning_events_total',
    'Total learning events processed'
)

expertise_knowledge_items = Gauge(
    'expertise_center_knowledge_items',
    'Current number of knowledge items'
)

expertise_consultation_duration = Histogram(
    'expertise_center_consultation_duration_seconds',
    'Consultation duration'
)
```

### Simple Dashboard

```python
# dashboard.py

@app.get("/dashboard")
async def dashboard():
    """Simple HTML dashboard"""
    return """
    <html>
    <head><title>Living Expertise Center</title></head>
    <body>
        <h1>🧠 Living Expertise Center</h1>
        <h2>Status: 🟢 ALIVE</h2>

        <h3>Metrics</h3>
        <ul>
            <li>Consultations: <span id="consultations">0</span></li>
            <li>Cases Learned: <span id="cases">0</span></li>
            <li>Knowledge Items: <span id="knowledge">0</span></li>
        </ul>

        <h3>Recent Activity</h3>
        <div id="activity"></div>

        <script>
        setInterval(async () => {
            const stats = await fetch('/api/v1/knowledge/stats').then(r => r.json());
            document.getElementById('consultations').textContent = stats.consultations_performed;
            document.getElementById('cases').textContent = stats.cases_learned;
            document.getElementById('knowledge').textContent = stats.knowledge_items;
        }, 5000);
        </script>
    </body>
    </html>
    """
```

---

## ✅ SUCCESS CRITERIA (Day 1)

After Day 1, you should have:

✅ Expertise Hub running
✅ Basic sensing (even if just logging)
✅ Consultation API working
✅ Learning from consultations (basic tracking)
✅ Health endpoint responding
✅ Metrics being collected
✅ Simple dashboard showing activity

**Test command:**
```bash
curl http://localhost:PORT/api/v1/consult \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Should we restart database?",
    "context": {"memory_percent": 95}
  }'
```

---

## 🚀 NEXT STEPS (Day 2+)

### Day 2: Real Integration
- ✅ Connect to Workflow Intelligence Case Library
- ✅ Connect to Event Intelligence
- ✅ Connect to AI Foundation (RAG, LLM)

### Day 3: Enhanced Learning
- ✅ Implement pattern detection
- ✅ Build knowledge graph
- ✅ Add feedback loops

### Day 4: Evolution
- ✅ Auto-tuning
- ✅ Performance tracking
- ✅ Continuous improvement

---

## 💡 TIPS

1. **Start Simple** - Get MVP running first
2. **Use Existing Code** - Extend `infrastructure_consultation.py`, don't rewrite
3. **Test Incrementally** - Test each component as you build
4. **Log Everything** - Use logging liberally for debugging
5. **Monitor Metrics** - Watch metrics to see system come alive

---

## 🆘 TROUBLESHOOTING

### Issue: Hub won't start
**Solution:** Check dependencies, ensure asyncio is used correctly

### Issue: No signals detected
**Solution:** Start with mock signals, add real ones incrementally

### Issue: Consultations not learning
**Solution:** Check that consultations are being tracked in `_consultations` list

---

**Ready to start?** 🚀

```bash
cd /Users/MD/AI-Platform-ISO/intelligent_core/expertise_center
# Follow Step 1: Create directories
# Then copy code snippets into files
# Run: python test_living_system.py
```

**You'll see:** 🌱 → 🌿 → 🌳 (system growing!)
