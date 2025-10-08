# BCM Platform Event Flow Diagrams

Visual representation of event-driven architecture and integration gaps.

---

## 1. BIA Workflow Event Flow

### Current State (BROKEN) ❌
```
┌─────────────┐
│ BIA Service │
└──────┬──────┘
       │ publishes: bcm.bia.completed
       │
       ▼
    ( EventBus )
       │
       │ ❌ NO SUBSCRIBERS!
       ▼
    ∅ (dropped)
```

### Target State (FIXED) ✅
```
┌─────────────┐
│ BIA Service │
└──────┬──────┘
       │ publishes: bcm.bia.completed
       │
       ▼
    ( EventBus )
       │
       ├────────────────────────────────────┐
       │                                    │
       ▼                                    ▼
┌──────────────┐                    ┌────────────────┐
│  Predictive  │                    │ AI-Orchestrator│
│   Service    │                    │                │
│              │                    │ Triggers:      │
│ • Learn from │                    │ Risk Assessment│
│   BIA data   │                    │ phase          │
│ • Update     │                    └────────────────┘
│   models     │
└──────────────┘
       │
       ▼
┌──────────────────┐
│ Community Intel  │
│                  │
│ • Offer case     │
│   contribution   │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ Governance       │
│                  │
│ • Update         │
│   compliance     │
│   status         │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ Event            │
│ Intelligence     │
│                  │
│ • Detect         │
│   patterns       │
└──────────────────┘
```

---

## 2. Exercise Workflow Event Flow

### Current State (NAMING MISMATCH) ❌
```
┌──────────────────┐
│ Simulation       │
│ Service          │
└────────┬─────────┘
         │ publishes: bcm.exercise.completed
         │
         ▼
      ( EventBus )
         │
         │ ❌ NAMING MISMATCH!
         │
         ▼
┌──────────────────┐
│ Governance       │
│ Service          │
│                  │
│ subscribes to:   │
│ exercise.        │  ❌ WRONG NAME!
│ completed        │
└──────────────────┘
```

### Target State (FIXED) ✅
```
┌──────────────────┐
│ Simulation       │
│ Service          │
└────────┬─────────┘
         │ publishes: bcm.exercise.completed
         │
         ▼
      ( EventBus )
         │
         ├─────────────────────────────┐
         │                             │
         ▼                             ▼
┌──────────────────┐          ┌──────────────────┐
│ Governance       │          │ AI-Foundation    │
│ Service          │          │ Learning         │
│                  │          │                  │
│ • Track          │          │ • Learn from     │
│   compliance     │          │   outcomes       │
│ • Identify gaps  │          │ • Update models  │
└──────────────────┘          └──────────────────┘
         │                             │
         ▼                             ▼
┌──────────────────┐          ┌──────────────────┐
│ Validation       │          │ Predictive       │
│ Service          │          │ Service          │
│                  │          │                  │
│ • Validate       │          │ • Adjust         │
│   effectiveness  │          │   readiness      │
└──────────────────┘          └──────────────────┘
         │
         ▼
┌──────────────────┐
│ Community Intel  │
│                  │
│ • Capture        │
│   lessons        │
└──────────────────┘
```

---

## 3. Incident Response Event Flow

### Current State (NAMING MISMATCH) ❌
```
┌──────────────────┐
│ Response         │
│ Service          │
└────────┬─────────┘
         │ publishes: response.incident.resolved
         │
         ▼
      ( EventBus )
         │
         │ ❌ NAMING MISMATCH!
         │
         ▼
┌──────────────────┐
│ Governance       │
│ Service          │
│                  │
│ subscribes to:   │
│ incident.        │  ❌ WRONG NAME!
│ resolved         │
└──────────────────┘
```

### Target State (FIXED) ✅
```
┌──────────────────┐
│ Response         │
│ Service          │
└────────┬─────────┘
         │ publishes: response.incident.resolved
         │
         ▼
      ( EventBus )
         │
         ├───────────────────────────────────┐
         │                                   │
         ▼                                   ▼
┌──────────────────┐              ┌──────────────────┐
│ AI-Foundation    │              │ Predictive       │
│ Learning         │              │ Service          │
│                  │              │                  │
│ • Extract        │              │ • Update RTO     │
│   resolution     │              │   predictions    │
│   patterns       │              │ • Compare actual │
│ • Update         │              │   vs predicted   │
│   playbooks      │              └──────────────────┘
└──────────────────┘
         │
         ▼
┌──────────────────┐
│ Event            │
│ Intelligence     │
│                  │
│ • Detect         │
│   incident       │
│   patterns       │
│ • Identify       │
│   recurring      │
└──────────────────┘
         │
         ▼
┌──────────────────┐
│ Community Intel  │
│                  │
│ • Capture case   │
│   study          │
└──────────────────┘
         │
         ▼
┌──────────────────┐
│ Governance       │
│                  │
│ • Track metrics  │
└──────────────────┘
```

---

## 4. Workflow Engine Event Flow

### Current State (NO SUBSCRIBERS) ❌
```
┌──────────────────┐
│ Workflow Engine  │
│ (BPMN)           │
└────────┬─────────┘
         │ publishes: bpmn.instance.completed
         │
         ▼
      ( EventBus )
         │
         │ ❌ NO SUBSCRIBERS!
         ▼
      ∅ (dropped)
```

### Target State (FIXED) ✅
```
┌──────────────────┐
│ Workflow Engine  │
│ (BPMN)           │
└────────┬─────────┘
         │ publishes: bpmn.instance.completed
         │           workflow.completed
         │
         ▼
      ( EventBus )
         │
         ├─────────────────────────────────────┐
         │                                     │
         ▼                                     ▼
┌──────────────────┐                  ┌──────────────────┐
│ Coordination     │                  │ Event            │
│ Center           │                  │ Intelligence     │
│                  │                  │                  │
│ • Track all      │                  │ • Detect         │
│   executions     │                  │   workflow       │
│ • Audit trail    │                  │   patterns       │
└──────────────────┘                  │ • Identify       │
         │                            │   bottlenecks    │
         ▼                            └──────────────────┘
┌──────────────────┐
│ AI-Orchestrator  │
│                  │
│ • Coordinate     │
│   multi-step     │
│   workflows      │
│ • Trigger        │
│   dependent      │
│   workflows      │
└──────────────────┘
         │
         ▼
┌──────────────────┐
│ Predictive       │
│ Service          │
│                  │
│ • Learn from     │
│   durations      │
│ • Improve        │
│   predictions    │
└──────────────────┘
```

---

## 5. Governance Event Flow (Competence Gaps)

### Current State (NO SUBSCRIBERS) ❌
```
┌──────────────────┐
│ Governance       │
│ Service          │
└────────┬─────────┘
         │ publishes: governance.competence.gap_identified
         │
         ▼
      ( EventBus )
         │
         │ ❌ NO SUBSCRIBERS!
         ▼
      ∅ (dropped)

❌ Result: Competence gaps identified but NO ACTION TAKEN!
```

### Target State (FIXED) ✅
```
┌──────────────────┐
│ Governance       │
│ Service          │
│                  │
│ Detects:         │
│ • User lacks     │
│   "Risk          │
│   Assessment"    │
│   competence     │
└────────┬─────────┘
         │ publishes: governance.competence.gap_identified
         │
         ▼
      ( EventBus )
         │
         ├─────────────────────────────┐
         │                             │
         ▼                             ▼
┌──────────────────┐          ┌──────────────────┐
│ Learning         │          │ Community        │
│ Service          │          │ Marketplace      │
│                  │          │                  │
│ AUTO ACTION:     │          │ AUTO ACTION:     │
│ • Find/create    │          │ • Match org with │
│   Risk           │          │   Risk Assessment│
│   Assessment     │          │   specialists    │
│   training       │          │ • Send           │
│ • Enroll user    │          │   recommendations│
│ • Send           │          │                  │
│   notification   │          └──────────────────┘
└──────────────────┘
         │
         ▼
┌──────────────────┐
│ Event            │
│ Intelligence     │
│                  │
│ • Track systemic │
│   competence     │
│   gaps           │
│ • Identify       │
│   industry       │
│   trends         │
└──────────────────┘

✅ Result: Competence gaps AUTOMATICALLY addressed!
```

---

## 6. Community Contribution Flow

### Current State (PARTIALLY WORKING) ⚠️
```
┌──────────────────┐
│ Community        │
│ Intelligence     │
└────────┬─────────┘
         │ publishes: case.approved
         │
         ▼
      ( EventBus )
         │
         │ ⚠️ ONLY AI-Foundation subscribes
         ▼
┌──────────────────┐
│ AI-Foundation    │
│ Learning         │
│                  │
│ • Add to ML      │
│   training data  │
└──────────────────┘

❌ Missing: Governance doesn't award competence points!
❌ Missing: Portal doesn't notify user!
```

### Target State (IMPROVED) ✅
```
┌──────────────────┐
│ Community        │
│ Intelligence     │
└────────┬─────────┘
         │ publishes: case.approved
         │           reputation.points_awarded
         │           reputation.level_up
         │
         ▼
      ( EventBus )
         │
         ├───────────────────────────────┐
         │                               │
         ▼                               ▼
┌──────────────────┐            ┌──────────────────┐
│ AI-Foundation    │            │ Governance       │
│ Learning         │            │ Service          │
│                  │            │                  │
│ • Add to ML      │            │ NEW:             │
│   training       │            │ • Award          │
│ • Update models  │            │   competence     │
└──────────────────┘            │   points         │
         │                      │ • Track          │
         ▼                      │   contributions  │
┌──────────────────┐            └──────────────────┘
│ Event            │                     │
│ Intelligence     │                     ▼
│                  │            ┌──────────────────┐
│ • Detect high-   │            │ Community        │
│   quality case   │            │ Portal           │
│   patterns       │            │                  │
└──────────────────┘            │ NEW:             │
                                │ • Send           │
                                │   notification   │
                                │ • Update         │
                                │   dashboard      │
                                └──────────────────┘
```

---

## 7. Predictive Service Learning Loop

### Current State (NO INPUT) ❌
```
┌──────────────────┐
│ Predictive       │
│ Service          │
│                  │
│ Makes            │
│ predictions      │
│ based on...      │
│ ❌ Static data!  │
│                  │
│ Never learns     │
│ from actual      │
│ outcomes         │
└──────────────────┘

❌ Predictions never improve!
```

### Target State (LEARNING LOOP) ✅
```
                    ┌─────────────────┐
                    │  Platform       │
                    │  Activity       │
                    │                 │
                    │ • BIA completed │
                    │ • Exercise done │
                    │ • Incident      │
                    │   resolved      │
                    └────────┬────────┘
                             │
                             │ publishes events
                             ▼
                       ( EventBus )
                             │
                             ▼
                    ┌─────────────────┐
                    │  Predictive     │
                    │  Service        │
                    │                 │
                    │ 1. Receives     │
                    │    actual data  │
                    │ 2. Compares to  │
                    │    predictions  │
                    │ 3. Updates ML   │
                    │    models       │
                    └────────┬────────┘
                             │
                             │ improved models
                             ▼
                    ┌─────────────────┐
                    │  Future         │
                    │  Predictions    │
                    │                 │
                    │ ✅ More         │
                    │    accurate!    │
                    └─────────────────┘

✅ Continuous learning loop!
```

---

## 8. Full Platform Event Architecture (Target State)

```
                              ┌────────────────────────────────┐
                              │      EventBus (RabbitMQ)       │
                              │                                │
                              │  Topic Exchanges:              │
                              │  • bcm.*                       │
                              │  • workflow.*                  │
                              │  • governance.*                │
                              │  • community.*                 │
                              │  • coordination.*              │
                              └─────┬──────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
        │ Event            │ │ AI-Foundation│ │ Predictive       │
        │ Intelligence     │ │ Learning     │ │ Service          │
        │                  │ │              │ │                  │
        │ Subscribes to:   │ │ Subscribes   │ │ Subscribes to:   │
        │ • ALL events     │ │ to:          │ │ • bcm.bia.*      │
        │   (wildcards)    │ │ • case.*     │ │ • bcm.exercise.* │
        │                  │ │ • review.*   │ │ • response.*     │
        │ Detects:         │ │ • workflow.* │ │ • workflow.*     │
        │ • Patterns       │ │ • bia.*      │ │                  │
        │ • Anomalies      │ │ • incident.* │ │ Updates:         │
        │ • Trends         │ │              │ │ • Journey models │
        │                  │ │ Updates:     │ │ • RTO models     │
        │ Publishes:       │ │ • ML models  │ │ • Demand models  │
        │ • ai.pattern.*   │ │ • Knowledge  │ │                  │
        └──────────────────┘ │   base       │ │ Publishes:       │
                             └──────────────┘ │ • prediction.*   │
                                              └──────────────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
        ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
        │ AI-Orchestrator  │ │ Coordination │ │ Community Intel  │
        │                  │ │ Center       │ │                  │
        │ Subscribes to:   │ │              │ │ Subscribes to:   │
        │ • bcm.bia.*      │ │ Subscribes   │ │ • bcm.*.*        │
        │ • coordination.* │ │ to:          │ │   (completions)  │
        │ • workflow.*     │ │ • All coord. │ │ • marketplace.*  │
        │                  │ │   events     │ │                  │
        │ Coordinates:     │ │              │ │ Offers:          │
        │ • Multi-step     │ │ Tracks:      │ │ • Case           │
        │   workflows      │ │ • AI actions │ │   contributions  │
        │ • Service chains │ │ • Audit      │ │                  │
        │                  │ │   trail      │ │ Publishes:       │
        │ Publishes:       │ │              │ │ • case.*         │
        │ • orchestration.*│ │ Publishes:   │ │ • reputation.*   │
        └──────────────────┘ │ • audit.*    │ └──────────────────┘
                             └──────────────┘
                    │               │                │
                    └───────────────┼────────────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
        ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
        │ Governance       │ │ Learning     │ │ Validation       │
        │ Service          │ │ Service      │ │ Service          │
        │                  │ │              │ │                  │
        │ Subscribes to:   │ │ Subscribes   │ │ Subscribes to:   │
        │ • bcm.exercise.* │ │ to:          │ │ • bcm.exercise.* │
        │ • response.*     │ │ • governance │ │ • plan.*         │
        │ • learning.*     │ │   .gap.*     │ │ • document.*     │
        │ • case.approved  │ │ • bcm.*      │ │                  │
        │                  │ │   completions│ │ Detects:         │
        │ Tracks:          │ │              │ │ • Non-compliance │
        │ • Compliance     │ │ Creates:     │ │ • Gaps           │
        │ • Competence     │ │ • Training   │ │                  │
        │ • KPIs           │ │   programs   │ │ Publishes:       │
        │                  │ │              │ │ • validation.*   │
        │ Publishes:       │ │ Publishes:   │ └──────────────────┘
        │ • governance.*   │ │ • learning.* │
        └──────────────────┘ └──────────────┘
```

**Legend:**
- ✅ Working integration
- ⚠️ Partial integration
- ❌ Broken/missing integration

---

## Event Naming Convention

### Standard Pattern
```
{domain}.{entity}.{action}
```

### Examples
```
✅ GOOD:
- bcm.bia.completed
- governance.policy.approved
- response.incident.resolved
- community.case.approved
- coordination.execution.completed

❌ BAD:
- bia.completed (no domain)
- process_added (underscore, no domain)
- incident.resolved (ambiguous domain)
```

---

## Integration Health Metrics

### Before Fixes
```
┌─────────────────────────────────────┐
│ Event Integration Health: 7.1%      │
├─────────────────────────────────────┤
│                                     │
│ ▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│                                     │
│ Connected:   9 events (7.1%)        │
│ Orphaned:   93 events (73.8%)       │
│ Broken:     24 events (19.0%)       │
│                                     │
└─────────────────────────────────────┘
```

### After Phase 1 (Quick Fixes)
```
┌─────────────────────────────────────┐
│ Event Integration Health: 17.5%     │
├─────────────────────────────────────┤
│                                     │
│ ▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│                                     │
│ Connected:  22 events (17.5%)       │
│ Orphaned:   80 events (63.5%)       │
│ Broken:     11 events (8.7%)        │
│                                     │
└─────────────────────────────────────┘
```

### After Phase 2 (Add Subscribers)
```
┌─────────────────────────────────────┐
│ Event Integration Health: 41.3%     │
├─────────────────────────────────────┤
│                                     │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░  │
│                                     │
│ Connected:  52 events (41.3%)       │
│ Orphaned:   50 events (39.7%)       │
│ Broken:     11 events (8.7%)        │
│                                     │
└─────────────────────────────────────┘
```

### Target State (Phase 3+)
```
┌─────────────────────────────────────┐
│ Event Integration Health: 80%+      │
├─────────────────────────────────────┤
│                                     │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░  │
│                                     │
│ Connected: 100 events (79.4%)       │
│ Orphaned:   13 events (10.3%)       │
│ Broken:      0 events (0.0%)        │
│                                     │
└─────────────────────────────────────┘
```

---

## See Also

- **event_system_gap_analysis.json** - Complete detailed analysis
- **EVENT_SYSTEM_ANALYSIS_SUMMARY.md** - Executive summary
- **EVENT_INTEGRATION_QUICK_FIXES.md** - Implementation guide
