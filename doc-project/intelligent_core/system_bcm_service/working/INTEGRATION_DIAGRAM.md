# System BCM - Integration Architecture Diagram

**Generated**: 2025-10-09
**Platform Version**: 2.0.0

---

## 🎨 Visual Architecture

### Complete Platform Integration

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                        AI-Platform-ISO v2.0                               ║
║                   Business Continuity Management Platform                 ║
╚═══════════════════════════════════════════════════════════════════════════╝

┌───────────────────────────────────────────────────────────────────────────┐
│ LAYER 4: INTEGRATION LAYER                                                │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────┐   ┌────────────────────────┐   ┌─────────────────┐   │
│  │ API Gateway  │   │   EventBus (Redis)     │   │   WebSocket     │   │
│  │   Port 8000  │   │   Port 6379 + 5672     │   │   Real-time     │   │
│  └──────┬───────┘   └────────┬───────────────┘   └────────┬────────┘   │
│         │                    │                              │            │
│         └────────────────────┼──────────────────────────────┘            │
│                              │                                           │
└──────────────────────────────┼───────────────────────────────────────────┘
                               │
    ┌──────────────────────────┴──────────────────────────┐
    │                                                       │
    ▼                                                       ▼

┌───────────────────────────────────────┐   ┌───────────────────────────────┐
│ LAYER 3: PLATFORM SERVICES (12)       │   │ LAYER 2: INTELLIGENT CORE (11)│
├───────────────────────────────────────┤   ├───────────────────────────────┤
│                                       │   │                               │
│ ┌─────────────────┐  ┌─────────────┐ │   │ ┌──────────────────────────┐ │
│ │ BIA Service     │  │ Risk Service│ │   │ │  AI Foundation           │ │
│ │ Port 8001       │  │ Port 8002   │ │   │ │  (LLM Router, RAG, ML)   │ │
│ └─────────────────┘  └─────────────┘ │   │ └──────────────────────────┘ │
│                                       │   │                               │
│ ┌─────────────────┐  ┌─────────────┐ │   │ ┌──────────────────────────┐ │
│ │ Compliance      │  │ Planning    │ │   │ │  Workflow Intelligence   │ │
│ │ Port 8003       │  │ Port 8004   │ │   │ │  Port 8037               │ │
│ └─────────────────┘  └─────────────┘ │   │ └──────────────────────────┘ │
│                                       │   │                               │
│ ┌─────────────────┐  ┌─────────────┐ │   │ ┌──────────────────────────┐ │
│ │ Response        │  │ Documents   │ │   │ │  Expertise Center (14)   │ │
│ │ Port 8005       │  │ Port 8006   │ │   │ │  Port 8036               │ │
│ └─────────────────┘  └─────────────┘ │   │ └──────────────────────────┘ │
│                                       │   │                               │
│ ┌─────────────────┐  ┌─────────────┐ │   │ ┌──────────────────────────┐ │
│ │ Governance      │  │ Validation  │ │   │ │  Collective Intelligence │ │
│ │ Port 8007       │  │ Port 8008   │ │   │ │  Port 8032 (347+ cases)  │ │
│ └─────────────────┘  └─────────────┘ │   │ └──────────────────────────┘ │
│                                       │   │                               │
│ ┌─────────────────┐  ┌─────────────┐ │   │ ┌──────────────────────────┐ │
│ │ Learning        │  │ BCM Coord   │ │   │ │  Predictive Intelligence │ │
│ │ Port 8009       │  │ Port 8010   │ │   │ │  Port 8031               │ │
│ └─────────────────┘  └─────────────┘ │   │ └──────────────────────────┘ │
│                                       │   │                               │
│ ┌─────────────────┐  ┌─────────────┐ │   │ ┌──────────────────────────┐ │
│ │ Community       │  │ Monitoring  │ │   │ │  Event Intelligence      │ │
│ │ Port 8011       │  │ Port 8012   │ │   │ │  Port 8039               │ │
│ └─────────────────┘  └─────────────┘ │   │ └──────────────────────────┘ │
│                                       │   │                               │
│         ALL SERVICES                  │   │ ┌──────────────────────────┐ │
│      Subscribe to Events              │   │ │  Workflow Engine (BPMN)  │ │
│      ↓ Health, Failed, etc.           │   │ │  Port 8041               │ │
└───────┼───────────────────────────────┘   │ └──────────────────────────┘ │
        │                                   │                               │
        │                                   │ ╔══════════════════════════╗ │
        │                                   │ ║ SYSTEM BCM SERVICE       ║ │
        │                                   │ ║ Port 8050                ║ │
        │                                   │ ║ ✅ INTEGRATION POINT     ║ │
        │                                   │ ╚══════════════════════════╝ │
        │                                   └───────────────────────────────┘
        │
        └──────────────┐
                       │
                       ▼

┌───────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: INFRASTRUCTURE LAYER                                             │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────┐    │
│  │ PostgreSQL      │  │ Redis           │  │ Qdrant (Vector DB)   │    │
│  │ Port 5432       │  │ Port 6379       │  │ Port 6333            │    │
│  │ (Supabase)      │  │ (EventBus Core) │  │ (RAG Pipeline)       │    │
│  └─────────────────┘  └─────────────────┘  └──────────────────────┘    │
│                                                                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────┐    │
│  │ Prometheus      │  │ Grafana         │  │ Vault                │    │
│  │ Port 9090       │  │ Port 3000       │  │ Port 8200            │    │
│  │ (Metrics)       │  │ (Dashboards)    │  │ (Secrets)            │    │
│  └─────────────────┘  └─────────────────┘  └──────────────────────┘    │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Event Flow Architecture

### System BCM Event Subscriptions & Publications

```
┌───────────────────────────────────────────────────────────────────┐
│                    EventBus (Redis Streams)                       │
│                         Port 6379                                 │
└───────────────────────────────────────────────────────────────────┘
         │                                                    ▲
         │ SUBSCRIBES TO                         PUBLISHES TO │
         ▼                                                    │
┌─────────────────────────────────┐        ┌──────────────────────────────┐
│ Platform Events (Input)         │        │ BCM Events (Output)          │
├─────────────────────────────────┤        ├──────────────────────────────┤
│                                 │        │                              │
│ 1. platform.health.degraded     │        │ 1. platform.bcm.cycle.started│
│    ├─ service: string           │        │    ├─ cycle_id: string       │
│    ├─ metric: string            │        │    └─ timestamp: ISO8601     │
│    ├─ value: float              │        │                              │
│    └─ threshold: float          │        │ 2. platform.bcm.cycle.completed
│                                 │        │    ├─ cycle_id: string       │
│ 2. platform.service.failed      │        │    ├─ phases: []             │
│    ├─ service: string           │        │    ├─ insights: int          │
│    ├─ incident_type: string     │        │    └─ improvements: int      │
│    ├─ error_message: string     │        │                              │
│    └─ timestamp: ISO8601        │        │ 3. platform.bcm.recovery.triggered
│                                 │        │    ├─ service: string        │
│ 3. platform.resource.contention │        │    ├─ incident: string       │
│    ├─ resource: cpu|memory|disk │        │    └─ procedure: string      │
│    ├─ utilization: float        │        │                              │
│    └─ threshold: float          │        │ 4. platform.bcm.recovery.completed
│                                 │        │    ├─ service: string        │
│ 4. platform.cascade.risk        │        │    ├─ duration_sec: float    │
│    ├─ services: []              │        │    ├─ rto_met: bool          │
│    ├─ dependency_chain: []      │        │    └─ success: bool          │
│    └─ risk_level: high|critical │        │                              │
│                                 │        │ 5. platform.bcm.insight.generated
└─────────────────────────────────┘        │    ├─ type: pattern|metric   │
                                           │    ├─ description: string    │
         │                                 │    ├─ confidence: float      │
         │                                 │    └─ action: string         │
         │                                 │                              │
         ▼                                 └──────────────────────────────┘
┌─────────────────────────────────┐
│   SYSTEM BCM SERVICE             │
│   Port 8050                      │
├─────────────────────────────────┤
│                                 │
│ ┌─────────────────────────────┐ │
│ │ Event Handler               │ │
│ │ ├─ on_health_degraded()     │ │
│ │ ├─ on_service_failed()      │ │
│ │ ├─ on_resource_contention() │ │
│ │ └─ on_cascade_risk()        │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ BCM Engine                  │ │
│ │ ├─ execute_bia()            │ │
│ │ ├─ assess_risks()           │ │
│ │ ├─ setup_recovery()         │ │
│ │ └─ apply_priorities()       │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ Practice Learning           │ │
│ │ ├─ learn_from_execution()   │ │
│ │ ├─ detect_patterns()        │ │
│ │ └─ generate_insights()      │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ Auto-Recovery (7 procedures)│ │
│ │ ├─ eventbus_recovery (30s)  │ │
│ │ ├─ db_pool_recovery (2m)    │ │
│ │ ├─ service_restart (5m)     │ │
│ │ ├─ memory_mitigation (10m)  │ │
│ │ ├─ cascade_prevention (15m) │ │
│ │ ├─ connection_recovery (3m) │ │
│ │ └─ disk_recovery (10m)      │ │
│ └─────────────────────────────┘ │
│                                 │
└─────────────────────────────────┘
```

---

## 📊 Data Flow Diagram

### BCM Cycle Execution Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    24-Hour BCM Cycle Scheduler                      │
│              (First run on startup, then every 24h)                 │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 1: Business Impact Analysis (BIA)                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Input: scenarios/platform_bia.json                                 │
│                                                                     │
│ Actions:                                                            │
│ 1. Load 7 critical processes (EventBus, DB, Gateway, etc.)         │
│ 2. Analyze dependencies (12 cross-dependencies)                    │
│ 3. Validate RTO/RPO targets (30s - 6h)                             │
│ 4. Check current health vs targets                                 │
│                                                                     │
│ Output:                                                             │
│ ├─ critical_processes: []                                          │
│ ├─ dependencies_mapped: int                                        │
│ ├─ rto_targets: {}                                                 │
│ └─ rpo_targets: {}                                                 │
│                                                                     │
│ Publish: platform.bcm.bia.completed                                │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 2: Risk Assessment                                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Input: scenarios/platform_risks.json                               │
│                                                                     │
│ Actions:                                                            │
│ 1. Load 12 platform risks                                          │
│ 2. Calculate risk scores (impact × likelihood)                     │
│ 3. Identify 8 high-priority risks (score >= 6)                     │
│ 4. Check if mitigations are active                                 │
│                                                                     │
│ Output:                                                             │
│ ├─ total_risks: 12                                                 │
│ ├─ high_priority_risks: 8                                          │
│ ├─ critical_risks: 3                                               │
│ └─ mitigations_active: []                                          │
│                                                                     │
│ Publish: platform.bcm.risk_assessment.completed                    │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 3: Recovery Setup                                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Input: scenarios/recovery_procedures.json                          │
│                                                                     │
│ Actions:                                                            │
│ 1. Load 7 recovery procedures                                      │
│ 2. Register triggers (health degraded, service failed, etc.)       │
│ 3. Validate procedure steps (syntax check)                         │
│ 4. Set RTO expectations (30s - 15m)                                │
│                                                                     │
│ Output:                                                             │
│ ├─ procedures_loaded: 7                                            │
│ ├─ triggers_registered: []                                         │
│ ├─ expected_rtos: {}                                               │
│ └─ auto_recovery_enabled: bool                                     │
│                                                                     │
│ Publish: platform.bcm.recovery_setup.completed                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 4: Priority Application                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Input: scenarios/resource_priorities.json                          │
│                                                                     │
│ Actions:                                                            │
│ 1. Load 3-tier resource allocation                                 │
│    ├─ Tier 1 (Critical): 50% CPU, 60% Memory                       │
│    ├─ Tier 2 (Important): 30% CPU, 30% Memory                      │
│    └─ Tier 3 (Optional): 20% CPU, 10% Memory                       │
│ 2. Apply resource limits via Docker API                            │
│ 3. Verify allocation successful                                    │
│                                                                     │
│ Output:                                                             │
│ ├─ tier1_services: 5                                               │
│ ├─ tier2_services: 7                                               │
│ ├─ tier3_services: 12                                              │
│ └─ priorities_applied: bool                                        │
│                                                                     │
│ Publish: platform.bcm.priorities.applied                           │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 5: Practice Learning                                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Input: Execution results from Phases 1-4                           │
│                                                                     │
│ Actions:                                                            │
│ 1. Measure actual vs expected (RTO, RPO, availability)             │
│ 2. Detect behavioral patterns                                      │
│    ├─ Memory usage trends                                          │
│    ├─ Error frequency patterns                                     │
│    └─ Performance degradation signals                              │
│ 3. Generate insights                                               │
│    ├─ Confidence score (0.0-1.0)                                   │
│    ├─ Priority (critical, high, medium, low)                       │
│    └─ Recommended action                                           │
│ 4. Auto-apply improvements (if confidence >= 0.7)                  │
│                                                                     │
│ Output:                                                             │
│ ├─ insights_generated: int                                         │
│ ├─ patterns_detected: []                                           │
│ ├─ improvements_applied: int                                       │
│ └─ learning_effectiveness: float                                   │
│                                                                     │
│ Publish: platform.bcm.learning.completed                           │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   platform.bcm.cycle.completed                      │
│                                                                     │
│ {                                                                   │
│   "cycle_id": "cycle_20251009_120000",                             │
│   "timestamp": "2025-10-09T12:00:00Z",                             │
│   "phases": ["bia", "risk_assessment", "recovery_setup",           │
│              "priority_application", "practice_learning"],         │
│   "bia_results": {...},                                            │
│   "risk_results": {...},                                           │
│   "recovery_results": {...},                                       │
│   "priority_results": {...},                                       │
│   "learning_results": {                                            │
│     "insights_generated": 5,                                       │
│     "patterns_detected": 2,                                        │
│     "improvements_applied": 1                                      │
│   },                                                                │
│   "cycle_duration_seconds": 12.5,                                  │
│   "success": true                                                  │
│ }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Recovery Flow Diagram

### Auto-Recovery Trigger Flow

```
┌───────────────────────────────────────────────────────────────┐
│                   Platform Event Occurs                       │
│  (Service fails, Health degrades, Resource contention, etc.)  │
└───────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│            EventBus: platform.service.failed                  │
│                                                               │
│ {                                                             │
│   "service": "redis",                                         │
│   "incident_type": "connection_pool_exhausted",               │
│   "error": "ECONNREFUSED",                                    │
│   "timestamp": "2025-10-09T12:30:00Z"                         │
│ }                                                             │
└───────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│         System BCM: Event Handler Receives Event              │
│                                                               │
│ async def on_service_failed(event):                           │
│     service = event.data["service"]                           │
│     incident_type = event.data["incident_type"]               │
│     await trigger_emergency_recovery(service, incident_type)  │
└───────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│              Select Recovery Procedure                        │
│                                                               │
│ Match: service="redis" + incident="connection_pool_exhausted" │
│ → Procedure: "eventbus_recovery"                             │
│ → RTO Target: 30 seconds                                     │
└───────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│         Publish: platform.bcm.recovery.triggered              │
│                                                               │
│ {                                                             │
│   "service": "redis",                                         │
│   "incident_type": "connection_pool_exhausted",               │
│   "procedure": "eventbus_recovery",                           │
│   "expected_rto": 30                                          │
│ }                                                             │
└───────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│           Execute Recovery Procedure Steps                    │
│                                                               │
│ Step 1: Clear connection pool              [✅ 5s]           │
│ Step 2: Reinitialize Redis client          [✅ 8s]           │
│ Step 3: Restore stream subscriptions       [✅ 10s]          │
│ Step 4: Verify event flow                  [✅ 5s]           │
│                                                               │
│ Total Duration: 28 seconds                                    │
│ RTO Met: ✅ (28s < 30s target)                                │
└───────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│              Verify Service Health                            │
│                                                               │
│ redis.ping() → PONG ✅                                        │
│ EventBus.is_connected() → True ✅                             │
│ Event subscriptions active: 4/4 ✅                            │
└───────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│        Publish: platform.bcm.recovery.completed               │
│                                                               │
│ {                                                             │
│   "service": "redis",                                         │
│   "procedure": "eventbus_recovery",                           │
│   "duration_seconds": 28,                                     │
│   "rto_met": true,                                            │
│   "success": true,                                            │
│   "steps_executed": 4                                         │
│ }                                                             │
└───────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│              Practice Learning: Analyze Recovery              │
│                                                               │
│ Learn from:                                                   │
│ • Actual RTO: 28s vs Target: 30s                              │
│ • Success rate: 100%                                          │
│ • Pattern: Connection pool exhaustion at peak load           │
│                                                               │
│ Generate Insight:                                             │
│ {                                                             │
│   "type": "pattern_detected",                                 │
│   "description": "Redis pool exhaustion during peak (12-2pm)",│
│   "confidence": 0.85,                                         │
│   "action": "increase_pool_size",                             │
│   "priority": "high"                                          │
│ }                                                             │
│                                                               │
│ Auto-Apply: ✅ (confidence 0.85 >= threshold 0.7)             │
│ → Increase Redis pool size: 50 → 75 connections              │
└───────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│        Publish: platform.bcm.insight.generated                │
│                                                               │
│ Notify other services about learned pattern                  │
└───────────────────────────────────────────────────────────────┘
```

---

## 📈 Monitoring Integration Diagram

### Prometheus & Grafana Integration

```
┌───────────────────────────────────────────────────────────────┐
│              System BCM Service (Port 8050)                   │
│                                                               │
│ Metrics Endpoint: /metrics                                   │
└───────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP Scrape every 15s
                            ▼
┌───────────────────────────────────────────────────────────────┐
│              Prometheus (Port 9090)                           │
│                                                               │
│ Job: system-bcm                                               │
│ Scrape Interval: 15s                                          │
│ Retention: 15 days                                            │
│                                                               │
│ Metrics Collected:                                            │
│ ├─ system_bcm_running (gauge)                                │
│ ├─ system_bcm_cycle_total (counter)                          │
│ ├─ system_bcm_cycle_duration_seconds (histogram)             │
│ ├─ system_bcm_recovery_total (counter)                       │
│ ├─ system_bcm_recovery_success_total (counter)               │
│ ├─ system_bcm_insights_generated (counter)                   │
│ ├─ system_bcm_service_available (gauge per service)          │
│ └─ ... (20+ metrics total)                                   │
│                                                               │
│ Alerting Rules (alerts.yml):                                 │
│ ├─ SystemBCMServiceDown (critical, for: 1m)                  │
│ ├─ BCMCycleFailing (critical, for: 5m)                       │
│ ├─ RecoveryProcedureFailing (high, for: 3m)                  │
│ ├─ RTOTargetMissed (high, for: 1m)                           │
│ └─ ... (20+ alerts total)                                    │
└───────────────────────────────────────────────────────────────┘
                            │
                            │ PromQL queries
                            ▼
┌───────────────────────────────────────────────────────────────┐
│              Grafana (Port 3000)                              │
│                                                               │
│ Dashboard: System BCM Overview                                │
│                                                               │
│ Panels:                                                       │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ 1. Service Status                                       │  │
│ │    ├─ System BCM Running: 🟢                            │  │
│ │    ├─ EventBus Connected: 🟢                            │  │
│ │    ├─ Auto-Recovery Enabled: 🟢                         │  │
│ │    └─ Last Cycle: 2 hours ago                           │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ 2. BCM Cycle Performance                                │  │
│ │    [Line Graph: Cycle duration over time]               │  │
│ │    Current: 12.5s | Target: <30s | ✅                   │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ 3. Platform Health Matrix                               │  │
│ │    Service         | Health | RTO    | Last Check       │  │
│ │    ──────────────────────────────────────────────────    │  │
│ │    redis           | 🟢     | 30s    | 5s ago           │  │
│ │    postgresql      | 🟢     | 2m     | 10s ago          │  │
│ │    bia-service     | 🟢     | 5m     | 15s ago          │  │
│ │    risk-service    | 🟡     | 5m     | 20s ago          │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ 4. Recovery Statistics                                  │  │
│ │    ├─ Total Recoveries: 23                              │  │
│ │    ├─ Success Rate: 95.7%                               │  │
│ │    ├─ Avg Recovery Time: 3m 12s                         │  │
│ │    └─ RTO Met: 87%                                      │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ 5. Learning Insights                                    │  │
│ │    [Bar Chart: Insights by type]                        │  │
│ │    Pattern Detected: 12                                 │  │
│ │    Metric Anomaly: 5                                    │  │
│ │    Resource Optimization: 3                             │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ 6. Recent Events Timeline                               │  │
│ │    [Timeline: BCM events in last 24h]                   │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## 🌐 Network Topology

### Docker Network: platform_network

```
┌───────────────────────────────────────────────────────────────────┐
│                    platform_network (bridge)                      │
│                    Subnet: 172.18.0.0/16                          │
└───────────────────────────────────────────────────────────────────┘
    │
    ├─ 172.18.0.10  → redis (EventBus Core)
    ├─ 172.18.0.11  → postgresql (Database)
    ├─ 172.18.0.12  → rabbitmq (Message Queue)
    ├─ 172.18.0.13  → qdrant (Vector DB)
    ├─ 172.18.0.14  → prometheus (Metrics)
    ├─ 172.18.0.15  → grafana (Dashboards)
    ├─ 172.18.0.16  → vault (Secrets)
    ├─ 172.18.0.20  → gateway (API Gateway)
    │
    ├─ 172.18.0.31  → bia-service
    ├─ 172.18.0.32  → risk-service
    ├─ 172.18.0.33  → compliance-service
    ├─ 172.18.0.34  → planning-service
    ├─ 172.18.0.35  → response-service
    ├─ 172.18.0.36  → documents-service
    ├─ 172.18.0.37  → governance-service
    ├─ 172.18.0.38  → validation-service
    ├─ 172.18.0.39  → learning-service
    ├─ 172.18.0.40  → bcm-coordination-service
    ├─ 172.18.0.41  → community-service
    ├─ 172.18.0.42  → monitoring
    │
    ├─ 172.18.0.51  → predictive
    ├─ 172.18.0.52  → collective
    ├─ 172.18.0.53  → expertise-center
    ├─ 172.18.0.54  → workflow-intelligence
    ├─ 172.18.0.55  → community-intelligence
    ├─ 172.18.0.56  → event-intelligence
    ├─ 172.18.0.57  → workflow-engine
    │
    └─ 172.18.0.60  → system-bcm-service ← YOU ARE HERE
```

---

**Integration Diagram Complete! 🎨**

Use this diagram to understand:
- System BCM's position in the platform
- Event flow subscriptions and publications
- Data flow through BCM cycles
- Recovery procedure execution
- Monitoring integration
- Network topology

For detailed configuration, see [PLATFORM_INTEGRATION.md](PLATFORM_INTEGRATION.md)
