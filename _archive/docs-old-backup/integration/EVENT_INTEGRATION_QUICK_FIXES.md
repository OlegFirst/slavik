# Event Integration Quick Fixes

**Priority: CRITICAL** 🔴
**Time to Fix: 1-2 weeks**
**Impact: Unbreak 13+ integrations immediately**

---

## Quick Fix #1: BIA Integration (15 minutes)

**Problem:** workflow_intelligence subscribes to events that don't exist

**File:** `/Users/MD/AI-Platform-ISO/intelligent-core/workflow_intelligence/integration/bia_adapter.py`

**Current Code (BROKEN):**
```python
# Currently subscribes to:
await eventbus.subscribe('process_added', handler)
await eventbus.subscribe('dependency_added', handler)
await eventbus.subscribe('impact_assessed', handler)
await eventbus.subscribe('rto_set', handler)
await eventbus.subscribe('state_changed', handler)
await eventbus.subscribe('stage_completed', handler)
await eventbus.subscribe('milestone_reached', handler)
```

**Fixed Code:**
```python
# Subscribe to actual BIA events that exist:
await eventbus.subscribe('bcm.bia.started', self.handle_bia_started)
await eventbus.subscribe('bcm.bia.completed', self.handle_bia_completed)
await eventbus.subscribe('bcm.bia.critical_process_identified', self.handle_critical_process)

# Add handlers:
async def handle_bia_started(self, event_data, tenant_id):
    """Handle BIA workflow started"""
    logger.info(f"BIA started: {event_data}")
    # Extract workflow context

async def handle_bia_completed(self, event_data, tenant_id):
    """Handle BIA workflow completed"""
    logger.info(f"BIA completed: {event_data}")
    # Trigger next phase, capture case

async def handle_critical_process(self, event_data, tenant_id):
    """Handle critical process identified"""
    logger.info(f"Critical process identified: {event_data}")
    # Update risk predictions
```

**Test:**
```bash
# Run BIA workflow and check logs
cd /Users/MD/AI-Platform-ISO/intelligent-core/workflow_intelligence
pytest tests/test_bia_adapter.py -v
```

---

## Quick Fix #2: Exercise Integration (10 minutes)

**Problem:** governance-service subscribes to wrong event name

**File:** `/Users/MD/AI-Platform-ISO/platform-services/governance-service/events/subscribers.py`

**Current Code (BROKEN):**
```python
# governance-service subscribes to:
await eventbus.subscribe('exercise.completed', handle_exercise_completed)
await eventbus.subscribe('exercise.gap_identified', handle_gap_identified)
```

**Fixed Code:**
```python
# Change to actual event names:
await eventbus.subscribe('bcm.exercise.completed', handle_exercise_completed)
await eventbus.subscribe('bcm.exercise.gap_identified', handle_gap_identified)  # if exists

# Or if gap_identified doesn't exist, handle it in completed:
async def handle_exercise_completed(event_data: Dict[str, Any]):
    """Handle exercise completion"""
    exercise_id = event_data.get('data', {}).get('exercise_id')
    results = event_data.get('data', {}).get('results', {})
    gaps = results.get('gaps', [])

    # Track completion for compliance
    logger.info(f"Exercise {exercise_id} completed with {len(gaps)} gaps")

    # Update ISO 22301 clause 8.5 status
    # Award competence points
    # If gaps found, create improvement actions
```

**Test:**
```bash
# Verify subscription
cd /Users/MD/AI-Platform-ISO/platform-services/governance-service
python -c "from events.subscribers import setup_event_subscribers; print('OK')"
```

---

## Quick Fix #3: Incident Integration (10 minutes)

**Problem:** governance-service subscribes to wrong event name

**File:** `/Users/MD/AI-Platform-ISO/platform-services/governance-service/events/subscribers.py`

**Current Code (BROKEN):**
```python
# governance-service subscribes to:
await eventbus.subscribe('incident.declared', handle_incident_declared)
await eventbus.subscribe('incident.resolved', handle_incident_resolved)
await eventbus.subscribe('risk.identified', handle_risk_identified)
```

**Fixed Code:**
```python
# Change to actual event names:
await eventbus.subscribe('response.incident.created', handle_incident_created)
await eventbus.subscribe('response.incident.resolved', handle_incident_resolved)
await eventbus.subscribe('response.incident.escalated', handle_incident_escalated)

# risk.identified might not exist yet - check if risk-service publishes events
# If not, subscribe to bcm.bia.critical_process_identified as proxy

async def handle_incident_resolved(event_data: Dict[str, Any]):
    """Handle incident resolution"""
    incident_id = event_data.get('data', {}).get('incident_id')
    resolution_time = event_data.get('data', {}).get('resolution_time_hours')

    logger.info(f"Incident {incident_id} resolved in {resolution_time}h")

    # Track for compliance metrics
    # Update KPIs
    # Award competence points to responders
```

**Test:**
```bash
# Check event names in response-service
grep -r "response.incident" /Users/MD/AI-Platform-ISO/platform-services/response-service/
```

---

## Quick Fix #4: Add workflow.completed Publisher (20 minutes)

**Problem:** orchestrator subscribes to `workflow.*` but workflow-engine only publishes `bpmn.*`

**File:** `/Users/MD/AI-Platform-ISO/intelligent-core/workflow-engine/workflow/bpmn/engine.py`

**Current Code:**
```python
# Only publishes BPMN events:
await self.eventbus.publish('bpmn.instance.completed', {...})
```

**Fixed Code:**
```python
# Publish BOTH bpmn.* and workflow.* events:
async def _complete_instance(self, instance_id):
    """Complete workflow instance"""
    # ... existing code ...

    event_data = {
        'instance_id': instance_id,
        'workflow_id': workflow_id,
        'completed_at': datetime.utcnow().isoformat(),
        'duration_seconds': duration,
        'status': 'completed'
    }

    # Publish BPMN-specific event
    await self.eventbus.publish('bpmn.instance.completed', event_data)

    # ALSO publish generic workflow event for orchestrator
    await self.eventbus.publish('workflow.completed', {
        **event_data,
        'workflow_type': 'bpmn',
        'module': self._get_workflow_module(workflow_id)  # bia, risk, planning, etc.
    })
```

**Similar changes needed for:**
- `bpmn.instance.started` → also publish `workflow.started`
- `bpmn.task.completed` → also publish `workflow.task_completed`

---

## Quick Fix #5: Add Predictive Subscribers (30 minutes)

**Problem:** predictive service has event handlers but they're not subscribed!

**File:** `/Users/MD/AI-Platform-ISO/intelligent-core/predictive/main.py`

**Current Code:**
```python
# Predictive service publishes events but doesn't subscribe to platform events
```

**Fixed Code:**
```python
# In startup function:
@app.on_event("startup")
async def startup():
    """Startup event handler"""
    logger.info("Starting Predictive Service...")

    # Initialize EventBus
    eventbus = get_eventbus()

    # Initialize event handlers
    app.state.event_handlers = PredictiveEventHandlers(
        eventbus=eventbus,
        journey_predictor=journey_predictor,
        demand_forecaster=demand_forecaster
    )

    # NEW: Subscribe to platform events for learning
    await app.state.event_handlers.subscribe_to_platform_events()

    logger.info("✅ Predictive Service ready and listening to events")
```

**File:** `/Users/MD/AI-Platform-ISO/intelligent-core/predictive/event_handlers.py`

**Check this method exists and is correct:**
```python
async def subscribe_to_platform_events(self):
    """Subscribe to all platform events that improve predictions"""

    # BIA events
    await self.eventbus.subscribe('bcm.bia.completed', self.handle_bia_completed)

    # Exercise events
    await self.eventbus.subscribe('bcm.exercise.completed', self.handle_exercise_completed)

    # Incident events
    await self.eventbus.subscribe('response.incident.resolved', self.handle_incident_resolved)

    # Workflow events
    await self.eventbus.subscribe('workflow.completed', self.handle_workflow_completed)
    await self.eventbus.subscribe('bpmn.instance.completed', self.handle_workflow_completed)  # redundant but safe

    # Community events
    await self.eventbus.subscribe('case.approved', self.handle_case_approved)

    # Risk events (if they exist)
    await self.eventbus.subscribe('risk.score_changed', self.handle_risk_score_changed)

    logger.info("✅ Subscribed to 7+ platform events for learning")
```

**Test:**
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/predictive
# Check if subscriptions are registered
python -c "
from event_handlers import PredictiveEventHandlers
from shared.eventbus import get_eventbus
import asyncio

async def test():
    eventbus = get_eventbus()
    handlers = PredictiveEventHandlers(eventbus, None, None)
    await handlers.subscribe_to_platform_events()
    print('Subscriptions registered')

asyncio.run(test())
"
```

---

## Quick Fix #6: Add Event Intelligence Wildcards (15 minutes)

**Problem:** event_intelligence should listen to ALL events but doesn't subscribe

**File:** `/Users/MD/AI-Platform-ISO/intelligent-core/event_intelligence/main.py`

**Add startup subscription:**
```python
@app.on_event("startup")
async def startup():
    """Startup event handler"""
    logger.info("Starting Event Intelligence Service...")

    # Initialize EventBus
    eventbus = get_eventbus()

    # NEW: Subscribe to ALL platform events for pattern detection
    await setup_event_subscribers(eventbus)

    logger.info("✅ Event Intelligence listening to all platform events")
```

**File:** `/Users/MD/AI-Platform-ISO/intelligent-core/event_intelligence/events/subscribers.py` (CREATE THIS FILE)

```python
"""
Event Intelligence Subscribers
Listen to ALL platform events for pattern detection and anomaly detection
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def setup_event_subscribers(eventbus):
    """
    Subscribe to all platform events using wildcards

    Event Intelligence is the "universal listener" that detects patterns
    across all platform activity.
    """

    # Subscribe to all BCM events
    await eventbus.subscribe('bcm.*', handle_bcm_event)

    # Subscribe to all workflow events
    await eventbus.subscribe('workflow.*', handle_workflow_event)
    await eventbus.subscribe('bpmn.*', handle_workflow_event)

    # Subscribe to all coordination events
    await eventbus.subscribe('coordination.*', handle_coordination_event)

    # Subscribe to all governance events
    await eventbus.subscribe('governance.*', handle_governance_event)

    # Subscribe to all community events
    await eventbus.subscribe('community.*', handle_community_event)
    await eventbus.subscribe('case.*', handle_community_event)
    await eventbus.subscribe('review.*', handle_community_event)
    await eventbus.subscribe('reputation.*', handle_community_event)

    # Subscribe to all learning events
    await eventbus.subscribe('learning.*', handle_learning_event)
    await eventbus.subscribe('training.*', handle_learning_event)

    # Subscribe to all marketplace events
    await eventbus.subscribe('marketplace.*', handle_marketplace_event)

    # Subscribe to all response/incident events
    await eventbus.subscribe('response.*', handle_response_event)

    # Subscribe to all prediction events
    await eventbus.subscribe('prediction.*', handle_prediction_event)

    logger.info("✅ Event Intelligence subscribed to ALL platform events")


async def handle_bcm_event(event_data: Dict[str, Any], tenant_id: str):
    """Handle BCM events (bia, exercise, incident, etc.)"""
    event_type = event_data.get('event_type', 'unknown')
    logger.info(f"[BCM Event] {event_type}")
    # TODO: Pattern detection, anomaly detection, metrics


async def handle_workflow_event(event_data: Dict[str, Any], tenant_id: str):
    """Handle workflow events"""
    event_type = event_data.get('event_type', 'unknown')
    logger.info(f"[Workflow Event] {event_type}")
    # TODO: Workflow pattern detection


async def handle_coordination_event(event_data: Dict[str, Any], tenant_id: str):
    """Handle coordination events"""
    event_type = event_data.get('event_type', 'unknown')
    logger.info(f"[Coordination Event] {event_type}")
    # TODO: AI action tracking


async def handle_governance_event(event_data: Dict[str, Any], tenant_id: str):
    """Handle governance events"""
    event_type = event_data.get('event_type', 'unknown')
    logger.info(f"[Governance Event] {event_type}")
    # TODO: Governance pattern detection


async def handle_community_event(event_data: Dict[str, Any], tenant_id: str):
    """Handle community events"""
    event_type = event_data.get('event_type', 'unknown')
    logger.info(f"[Community Event] {event_type}")
    # TODO: Community engagement patterns


async def handle_learning_event(event_data: Dict[str, Any], tenant_id: str):
    """Handle learning events"""
    event_type = event_data.get('event_type', 'unknown')
    logger.info(f"[Learning Event] {event_type}")
    # TODO: Learning effectiveness patterns


async def handle_marketplace_event(event_data: Dict[str, Any], tenant_id: str):
    """Handle marketplace events"""
    event_type = event_data.get('event_type', 'unknown')
    logger.info(f"[Marketplace Event] {event_type}")
    # TODO: Marketplace demand patterns


async def handle_response_event(event_data: Dict[str, Any], tenant_id: str):
    """Handle response/incident events"""
    event_type = event_data.get('event_type', 'unknown')
    logger.info(f"[Response Event] {event_type}")
    # TODO: Incident pattern detection


async def handle_prediction_event(event_data: Dict[str, Any], tenant_id: str):
    """Handle prediction events"""
    event_type = event_data.get('event_type', 'unknown')
    logger.info(f"[Prediction Event] {event_type}")
    # TODO: Track prediction accuracy
```

---

## Quick Fix #7: Add Community Intelligence Subscribers (20 minutes)

**File:** `/Users/MD/AI-Platform-ISO/intelligent-core/community_intelligence/events/subscribers.py`

**Current Code:**
```python
# Only subscribes to 3 events:
# - workflow.*.completed
# - case.contribution.submitted
# - case.approved
```

**Add These Subscriptions:**
```python
async def setup_event_subscribers(eventbus: EventBusClient):
    """Setup all event subscribers"""

    # Existing subscriptions...

    # NEW: Subscribe to BCM completion events to offer case contribution
    await eventbus.subscribe(
        topics=['bcm.bia.completed'],
        handler=on_bia_completed
    )

    await eventbus.subscribe(
        topics=['bcm.exercise.completed'],
        handler=on_exercise_completed
    )

    await eventbus.subscribe(
        topics=['response.incident.resolved'],
        handler=on_incident_resolved
    )

    await eventbus.subscribe(
        topics=['marketplace.project.completed'],
        handler=on_project_completed
    )

    logger.info("✅ Community Intelligence subscribed to completion events")


async def on_bia_completed(event: Dict[str, Any]):
    """Handle BIA completion - offer to contribute case"""
    bia_id = event.get('data', {}).get('bia_id')
    org_id = event.get('data', {}).get('org_id')
    user_id = event.get('data', {}).get('user_id')

    logger.info(f"BIA {bia_id} completed - offering case contribution")

    # Check if user has opted-in to case contributions
    # If yes: auto-submit
    # If no: send contribution offer notification


async def on_exercise_completed(event: Dict[str, Any]):
    """Handle exercise completion - offer to share lessons learned"""
    # Similar to on_bia_completed


async def on_incident_resolved(event: Dict[str, Any]):
    """Handle incident resolution - offer to share response case"""
    # Similar to on_bia_completed


async def on_project_completed(event: Dict[str, Any]):
    """Handle marketplace project completion - offer case study"""
    # Similar to on_bia_completed
```

---

## Verification Checklist

After applying fixes, verify:

### 1. Event Subscription Check
```bash
# Check if subscriptions are registered
cd /Users/MD/AI-Platform-ISO
python3 -c "
import json
with open('infrastructure/eventbus/events/events_catalog.json') as f:
    catalog = json.load(f)

# Re-scan after fixes
print('Run event scanner again to verify fixes')
"
```

### 2. Integration Test
Create simple test:
```python
# test_event_integration.py
import asyncio
from shared.eventbus import get_eventbus

async def test_integration():
    eventbus = get_eventbus()

    # Track received events
    received = []

    async def handler(event_data, tenant_id):
        received.append(event_data.get('event_type'))

    # Subscribe
    await eventbus.subscribe('bcm.bia.completed', handler)

    # Publish test event
    await eventbus.publish('bcm.bia.completed', {
        'event_type': 'bcm.bia.completed',
        'bia_id': 'test-123',
        'org_id': 'test-org'
    })

    # Wait for delivery
    await asyncio.sleep(0.5)

    # Verify
    assert 'bcm.bia.completed' in received, "Event not delivered!"
    print("✅ Integration test passed")

asyncio.run(test_integration())
```

### 3. Monitor Logs
```bash
# Start services and watch for subscription logs
cd /Users/MD/AI-Platform-ISO

# Check predictive service
tail -f intelligent-core/predictive/logs/app.log | grep "Subscribed to"

# Check event intelligence
tail -f intelligent-core/event_intelligence/logs/app.log | grep "Subscribed to"

# Check community intelligence
tail -f intelligent-core/community_intelligence/logs/app.log | grep "Subscribed to"
```

---

## Expected Results After Fixes

### Before Fixes:
- 93 orphaned events
- 24 broken events
- 9 connected events (7.1%)

### After Fixes (Phase 1):
- 80 orphaned events (↓13)
- 11 broken events (↓13)
- 22 connected events (17.5%) (↑13)

### After Phase 2 (Add Subscribers):
- 50 orphaned events (↓30)
- 11 broken events
- 52 connected events (41.3%) (↑30)

---

## Common Issues

### Issue: EventBus not initialized
```python
# Error: eventbus is None

# Fix: Initialize in startup
from shared.eventbus import get_eventbus, init_eventbus

@app.on_event("startup")
async def startup():
    init_eventbus(settings.RABBITMQ_URL)
    eventbus = get_eventbus()
    # ... subscribe
```

### Issue: Handler not async
```python
# Error: Handler must be async

# Wrong:
def handle_event(event_data, tenant_id):
    pass

# Correct:
async def handle_event(event_data, tenant_id):
    pass
```

### Issue: Wildcard not matching
```python
# Wrong: 'workflow.*' doesn't match 'bpmn.instance.completed'

# Fix: Subscribe to both
await eventbus.subscribe('workflow.*', handler)
await eventbus.subscribe('bpmn.*', handler)
```

---

## Next Steps

1. ✅ Apply Quick Fixes #1-3 (broken integrations)
2. ✅ Apply Quick Fixes #4-5 (add publishers/subscribers)
3. ✅ Run verification tests
4. ✅ Re-scan event catalog
5. ✅ Move to Phase 2 (add more subscribers)

---

**Questions?** Check the full analysis in `event_system_gap_analysis.json`
