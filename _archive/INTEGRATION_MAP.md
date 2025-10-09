# Integration Map - Phase 1 + Phase 2

**Date**: 2025-10-09
**Purpose**: Визуализация всех компонентов, связей и потоков данных

## Component Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SYSTEM BCM SERVICE                              │
│                     (Main Coordinator)                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                    ServiceState                              │ │
│  │  • eventbus                                                  │ │
│  │  • coordinator                                               │ │
│  │  • survival        ← Phase 1                                 │ │
│  │  • memory          ← Phase 1                                 │ │
│  │  • resource_tracker ← Phase 2 NEW                            │ │
│  │  • wishlist        ← Phase 2 NEW                             │ │
│  └──────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## Detailed Architecture Map

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                        USER / EXTERNAL SYSTEMS                               │
│                                                                              │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │ HTTP API
                                 │
┌────────────────────────────────▼─────────────────────────────────────────────┐
│                         SYSTEM BCM SERVICE                                   │
│                         Port: 8009                                           │
│                                                                              │
│  API Endpoints:                                                              │
│  • GET /health                                                               │
│  • GET /survival/health                                                      │
│  • GET /survival/stats                                                       │
│  • GET /memory/stats                                                         │
│  • GET /wishlist/items         ← NEW                                         │
│  • GET /resources/trends       ← NEW                                         │
│                                                                              │
└──────┬──────────┬──────────┬──────────┬────────────┬──────────┬─────────────┘
       │          │          │          │            │          │
       │          │          │          │            │          │
   ┌───▼───┐  ┌───▼───┐  ┌───▼───┐  ┌──▼──┐   ┌────▼────┐  ┌──▼──┐
   │Event  │  │System │  │Survi  │  │Memo │   │Resource │  │Wish │
   │Bus    │  │BCM    │  │val    │  │ry   │   │Tracker  │  │list │
   │       │  │Coord  │  │Inst.  │  │Sys. │   │         │  │Sys. │
   └───┬───┘  └───┬───┘  └───┬───┘  └──┬──┘   └────┬────┘  └──┬──┘
       │          │          │          │            │          │
       │          │          │          │            │          │
       └──────────┴──────────┴──────────┴────────────┴──────────┘
                              │
                              │
                    All communicate via
                    in-memory references
```

## Component Communication Matrix

### 1. Resource Tracker

**Receives from**:
- **psutil** (system): CPU, Memory, Disk IO, Network stats
- **File System**: Previous history on startup

**Sends to**:
- **Wishlist System**: Available resources for prioritization
- **Survival Instinct**: Resource state (deficit/normal/surplus)
- **File System**: Snapshots history (periodic save)
- **API**: Trends and stats on request

**Communication Pattern**:
```python
# PULL pattern - others ask Resource Tracker
available = resource_tracker.get_available_resources()
state = resource_tracker.detect_resource_state()
trend = resource_tracker.calculate_trend('cpu_percent')
```

**Data Flow**:
```
psutil → ResourceTracker.take_snapshot() → history (deque)
                                         → calculate_trend()
                                         → predict_deficit()
                                         → detect_resource_state()
                                         → get_available_resources()
```

### 2. Wishlist System

**Receives from**:
- **Survival Instinct**: New wishes when imbalance detected
- **Resource Tracker**: Available resources
- **File System**: Previous wishlist on startup
- **Game Loop** (future): Wish execution results

**Sends to**:
- **Executor Loop**: Prioritized wishes to execute
- **Memory System**: Execution results for learning
- **File System**: Wishlist state (periodic save)
- **API**: Wish list on request

**Communication Pattern**:
```python
# PUSH pattern - Survival creates wishes
wish = wishlist.add_wish(
    description="Optimize cache",
    need_type=NeedType.EFFICIENCY,
    urgency=0.8,
    resource_cost=ResourceCost(cpu_percent=10, time_seconds=30)
)

# PULL pattern - Executor pulls prioritized
available = resource_tracker.get_available_resources()
wishes = wishlist.get_prioritized_wishes(available, limit=5)
```

**Data Flow**:
```
Survival Instinct → wishlist.add_wish() → items (dict)
                                        → detect_conflicts()
                                        → resolve_conflicts()
Resource Tracker  → get_prioritized_wishes() → sorted by priority
                                             → return top N
```

### 3. Survival Instinct

**Receives from**:
- **Self** (internal loop): Periodic KPI checks (every 60s)
- **Memory System**: Historical patterns for corrections
- **File System**: KPI config on startup

**Sends to**:
- **Wishlist System**: Wishes when imbalance detected
- **Memory System**: Correction results for learning
- **Infrastructure** (future): Actual correction actions
- **File System**: State (if needed)
- **API**: Health status on request

**Communication Pattern**:
```python
# AUTONOMOUS - runs own loop
while is_running:
    metrics = get_my_current_metrics()
    imbalance = detect_my_imbalance(metrics)

    if imbalance:
        # Create wish
        wishlist.add_wish(...)

        # Or execute directly
        action = trigger_my_correction(imbalance)
        success = await execute_correction_action(action)

        # Learn
        memory.remember_pattern(state_sig, action_type, success)
```

**Data Flow**:
```
Timer (60s) → get_my_current_metrics() → my_kpis (dict)
                                       → detect_my_imbalance()
                                       → trigger_my_correction()
                                       → wishlist.add_wish()
                                       → memory.remember_pattern()
```

### 4. Memory System

**Receives from**:
- **Survival Instinct**: Pattern results (state + action + success)
- **Game Loop** (future): Fast action results
- **File System**: Previous patterns on startup

**Sends to**:
- **Game Loop**: Patterns for fast path
- **Wishlist System** (indirect): Success rates influence priorities
- **File System**: Patterns (periodic save)
- **API**: Memory stats on request

**Communication Pattern**:
```python
# PUSH pattern - others record patterns
memory.remember_pattern(
    state_signature="cpu_80_mem_70",
    action_type="throttle",
    success=True,
    context={'cpu': 85, 'memory': 75}
)

# PULL pattern - others query patterns
patterns = memory.find_matching_patterns(
    state_signature="cpu_80_",
    min_success_rate=0.75
)
```

**Data Flow**:
```
Survival/GameLoop → remember_pattern() → short_term (cache)
                                      → long_term (persistent)
                                      → calculate success_rate

Query             → find_matching_patterns() → similarity match
                                            → filter by success_rate
                                            → return top N
```

### 5. EventBus (Existing)

**Receives from**:
- **All components**: Events to publish
- **Redis Streams**: Events from other services

**Sends to**:
- **All components**: Subscribed events
- **Redis Streams**: Events to other services

**Communication Pattern**:
```python
# PUBLISH
await eventbus.publish(Event(
    type="platform.bcm.imbalance_detected",
    data={"kpi": "cpu", "level": "severe"},
    source="survival-instinct"
))

# SUBSCRIBE
@eventbus.subscribe("platform.bcm.*")
async def handle_bcm_event(event):
    # React to event
```

**Current Usage**: Minimal in Phase 1/2, reserved for inter-service communication.

## Data Flow Scenarios

### Scenario 1: Imbalance Detection → Wish Creation

```
┌────────────────────┐
│ Survival Instinct  │
│  (60s loop)        │
└─────────┬──────────┘
          │
          │ 1. detect_my_imbalance()
          │    → CPU > 85%
          │
          ▼
┌────────────────────┐
│  Imbalance Found   │
│  Level: SEVERE     │
└─────────┬──────────┘
          │
          │ 2. trigger_my_correction()
          │    → action_type: "throttle"
          │
          ▼
┌────────────────────┐      3. add_wish()
│ Wishlist System    │◄────────────────────┐
│                    │                     │
│ • description      │                     │
│ • urgency: 0.9     │                     │
│ • cost: 10% CPU    │                     │
└─────────┬──────────┘                     │
          │                                │
          │ Wish added to queue            │
          │ ID: wish_12345                 │
          │                                │
          ▼                                │
   [Storage: JSON]                   [Success]
```

### Scenario 2: Wish Prioritization → Execution

```
┌────────────────────┐
│ Executor Loop      │
│  (30s interval)    │
└─────────┬──────────┘
          │
          │ 1. Get available resources
          ▼
┌────────────────────┐
│ Resource Tracker   │
│                    │
│ get_available()    │
│ → CPU: 45%         │
│ → Memory: 2GB      │
└─────────┬──────────┘
          │
          │ 2. available_resources
          ▼
┌────────────────────┐
│ Wishlist System    │
│                    │
│ get_prioritized(   │
│   available,       │
│   limit=5          │
│ )                  │
└─────────┬──────────┘
          │
          │ 3. Returns top 5 wishes
          │    sorted by priority
          │
          ▼
┌────────────────────┐
│ Top Wish:          │
│ "Optimize cache"   │
│ Priority: 0.92     │
│ Can afford: YES    │
└─────────┬──────────┘
          │
          │ 4. Execute action
          ▼
┌────────────────────┐
│ Execute Logic      │
│ (optimize_cache)   │
└─────────┬──────────┘
          │
          │ 5. Success = True
          │
          ├────────────────────────┐
          │                        │
          ▼                        ▼
┌────────────────────┐    ┌────────────────────┐
│ Wishlist System    │    │ Memory System      │
│                    │    │                    │
│ complete_wish(     │    │ remember_pattern(  │
│   id, success      │    │   state, action,   │
│ )                  │    │   success          │
└────────────────────┘    │ )                  │
                          └────────────────────┘
```

### Scenario 3: Resource Deficit → Self-Actualization (Future)

```
┌────────────────────┐
│ Resource Tracker   │
│  (monitoring)      │
└─────────┬──────────┘
          │
          │ 1. detect_resource_state()
          │    → "deficit"
          │
          │ 2. predict_deficit()
          │    → CPU hits 90% in 120s
          │
          ▼
┌────────────────────┐
│ DEFICIT DETECTED   │
└─────────┬──────────┘
          │
          │ 3. Trigger self-actualization
          │
          ▼
┌────────────────────┐
│ Wishlist System    │
│                    │
│ add_wish(          │
│   "Train model",   │
│   urgency=0.95     │
│ )                  │
└─────────┬──────────┘
          │
          │ 4. High priority wish
          │
          ▼
┌────────────────────┐
│ Self-Actualization │  ← Future component
│ Engine             │
│                    │
│ • Train lightweight│
│   optimization     │
│   model            │
│ • Learn efficient  │
│   algorithms       │
│ • Reduce resource  │
│   usage            │
└────────────────────┘
```

### Scenario 4: Conflict Detection → Resolution

```
┌────────────────────┐
│ Wishlist System    │
│                    │
│ Wish A: urgent=0.9 │
│ Wish B: urgent=0.8 │
│ Wish C: urgent=0.85│
└─────────┬──────────┘
          │
          │ 1. detect_and_resolve_conflicts()
          │
          ▼
┌────────────────────┐
│ Conflict Resolver  │
│                    │
│ Check:             │
│ • Circular deps    │
│ • Resource limits  │
│ • Deadlines        │
└─────────┬──────────┘
          │
          │ 2. CONFLICT FOUND
          │    Total CPU: 150%
          │    Available: 45%
          │
          ▼
┌────────────────────┐
│ Resource Conflict  │
│                    │
│ Competing:         │
│ • Wish A (0.9)     │
│ • Wish B (0.8)     │
│ • Wish C (0.85)    │
└─────────┬──────────┘
          │
          │ 3. resolve_conflict()
          │    Strategy: Postpone lower half
          │
          ▼
┌────────────────────┐
│ RESOLVED           │
│                    │
│ Kept:              │
│ • Wish A (0.9)     │
│ • Wish C (0.85)    │
│                    │
│ Postponed:         │
│ • Wish B (0.4) ← halved urgency
└────────────────────┘
```

## Component Dependencies

### Dependency Graph

```
┌─────────────────────────────────────────────────────────────┐
│                     Level 0: Infrastructure                 │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  psutil  │  │   File   │  │  Redis   │                 │
│  │          │  │  System  │  │  Streams │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
                        │
                        │
┌─────────────────────────────────────────────────────────────┐
│                     Level 1: Core Systems                   │
│                                                             │
│  ┌──────────────┐         ┌──────────────┐                │
│  │   Memory     │         │   EventBus   │                │
│  │   System     │         │              │                │
│  └──────────────┘         └──────────────┘                │
└─────────────────────────────────────────────────────────────┘
                        │
                        │
┌─────────────────────────────────────────────────────────────┐
│                Level 2: Monitoring & Resources              │
│                                                             │
│  ┌──────────────┐                                          │
│  │   Resource   │                                          │
│  │   Tracker    │                                          │
│  └──────┬───────┘                                          │
│         │                                                   │
│         │ provides                                          │
│         │                                                   │
│  ┌──────▼───────┐                                          │
│  │   Wishlist   │                                          │
│  │   System     │                                          │
│  └──────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
                        │
                        │ uses
                        │
┌─────────────────────────────────────────────────────────────┐
│                   Level 3: Intelligence                     │
│                                                             │
│  ┌──────────────┐         ┌──────────────┐                │
│  │   Survival   │         │   Game Loop  │                │
│  │   Instinct   │         │   (future)   │                │
│  └──────────────┘         └──────────────┘                │
└─────────────────────────────────────────────────────────────┘
                        │
                        │ coordinated by
                        │
┌─────────────────────────────────────────────────────────────┐
│                Level 4: Service Orchestration               │
│                                                             │
│  ┌──────────────────────────────────────────────────┐     │
│  │          System BCM Service                      │     │
│  │          (main.py)                               │     │
│  └──────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Initialization Order

```
1. EventBus              ← First (needed by Coordinator)
2. Memory System         ← Independent, can be early
3. Resource Tracker      ← Independent, starts monitoring
4. Wishlist System       ← Depends on Resource Tracker (soft)
5. Survival Instinct     ← Uses Memory + Wishlist
6. BCM Coordinator       ← Uses EventBus
7. Background Executors  ← Last (uses all above)
```

### Shutdown Order

```
1. Background Executors  ← Stop first (no new wishes)
2. Survival Instinct     ← Stop monitoring
3. Resource Tracker      ← Stop monitoring
4. Wishlist System       ← Save state
5. Memory System         ← Save patterns
6. BCM Coordinator       ← Cleanup
7. EventBus              ← Last
```

## Integration Points

### Where Code Lives

```
/intelligent-core/
├── ai-foundation/
│   └── memory/
│       └── memory_system.py          ← Phase 1
│
├── coordination-center/
│   ├── resources/
│   │   └── resource_tracker.py       ← Phase 2 NEW
│   └── wishlist/
│       └── wishlist_system.py        ← Phase 2 NEW
│
├── orchestration/
│   └── gameloop/
│       └── operational_loop.py       ← Phase 1 (future use)
│
└── system-bcm-service/
    ├── instincts/
    │   └── survival.py               ← Phase 1
    └── main.py                       ← Integration point
```

### main.py Integration Structure

```python
# ============================================================================
# IMPORTS
# ============================================================================
from ai_foundation.memory import create_memory_system
from coordination_center.resources import create_resource_tracker
from coordination_center.wishlist import create_wishlist_system
from instincts.survival import start_survival_instinct
from eventbus import create_eventbus

# ============================================================================
# STATE
# ============================================================================
class ServiceState:
    def __init__(self):
        # Phase 0
        self.eventbus = None
        self.coordinator = None

        # Phase 1
        self.memory = None
        self.survival = None

        # Phase 2
        self.resource_tracker = None
        self.wishlist = None

        # Background tasks
        self.scheduler_task = None
        self.wishlist_executor_task = None  # NEW

# ============================================================================
# STARTUP
# ============================================================================
@app.on_event("startup")
async def startup():
    # 1. EventBus
    await setup_eventbus()

    # 2. Memory System
    state.memory = await create_memory_system(...)

    # 3. Resource Tracker
    state.resource_tracker = await create_resource_tracker(...)

    # 4. Wishlist System
    state.wishlist = await create_wishlist_system(...)

    # 5. Survival Instinct (with dependencies)
    state.survival = await start_survival_instinct(
        ...,
        memory_system=state.memory,
        wishlist_system=state.wishlist,      # NEW
        resource_tracker=state.resource_tracker  # NEW
    )

    # 6. Background executors
    state.scheduler_task = asyncio.create_task(scheduler_loop())
    state.wishlist_executor_task = asyncio.create_task(wishlist_executor_loop())  # NEW

# ============================================================================
# SHUTDOWN
# ============================================================================
@app.on_event("shutdown")
async def shutdown():
    # Stop in reverse order
    if state.wishlist_executor_task:
        state.wishlist_executor_task.cancel()

    if state.survival:
        state.survival.stop()

    if state.resource_tracker:
        state.resource_tracker.stop()

    if state.memory:
        state.memory.stop()
```

## API Surface

### Current Endpoints

```
GET  /health                 → Overall service health
GET  /status                 → Detailed status
GET  /survival/health        → Survival Instinct health  (Phase 1)
GET  /survival/stats         → Survival statistics      (Phase 1)
GET  /memory/stats           → Memory statistics        (Phase 1)
```

### New Endpoints (Phase 2)

```
GET  /wishlist/items         → Prioritized wishes       (NEW)
GET  /wishlist/stats         → Wishlist statistics     (NEW)
GET  /resources/trends       → Resource trends         (NEW)
GET  /resources/state        → Current resource state  (NEW)
POST /wishlist/add           → Manually add wish       (NEW)
POST /wishlist/complete      → Mark wish complete      (NEW)
```

## Performance Impact

### Memory Usage

```
Component          | Memory     | Growth
-------------------|------------|------------------
Memory System      | ~5MB       | +1KB per pattern
Resource Tracker   | ~500KB     | +5KB per snapshot
Wishlist System    | ~1MB       | +1KB per wish
Survival Instinct  | ~100KB     | +100B per check
-------------------|------------|------------------
TOTAL              | ~6.5MB     | Bounded by limits
```

### CPU Usage

```
Component          | CPU        | Frequency
-------------------|------------|------------------
Resource Tracker   | <1%        | Every 60s
Survival Instinct  | <1%        | Every 60s
Wishlist Executor  | <1%        | Every 30s
Memory Cleanup     | <1%        | Every 5 minutes
-------------------|------------|------------------
TOTAL              | <5%        | Background
```

### Disk I/O

```
Component          | Disk Write | Frequency
-------------------|------------|------------------
Memory System      | ~10KB      | Every pattern save
Resource Tracker   | ~10KB      | Every 60s
Wishlist System    | ~5KB       | On change
Survival Instinct  | ~5KB       | Rarely
-------------------|------------|------------------
TOTAL              | ~30KB      | Per minute
```

## Critical Paths

### Fast Path (< 100ms)

```
API Request → get_prioritized_wishes() → return from memory
API Request → get_resource_trends() → return from history
API Request → get_memory_stats() → return from cache
```

### Medium Path (< 1s)

```
Imbalance Detection → add_wish() → save to file
Resource Snapshot → calculate_trend() → save to file
Wish Execution → remember_pattern() → save to file
```

### Slow Path (> 1s)

```
Conflict Resolution → resolve_all_conflicts() → save changes
Full System Analysis → coordinator.run_bcm_cycle() → minutes
```

## Failure Modes

### What Happens If...

**Resource Tracker fails**:
- Wishlist continues with default resources
- Survival Instinct continues monitoring
- Manual execution still possible

**Wishlist fails**:
- Survival Instinct can execute directly
- No prioritization, but still functional
- Manual intervention possible

**Memory fails**:
- Survival still works (no learning)
- Game Loop falls back to default patterns
- System functional but doesn't improve

**Survival fails**:
- Manual monitoring still possible via API
- Other components unaffected
- Can restart independently

## Next Steps

### Integration Checklist

- [ ] Update Survival Instinct to use Wishlist
- [ ] Update Survival Instinct to use Resource Tracker
- [ ] Add wishlist_executor_loop to main.py
- [ ] Add new API endpoints
- [ ] Update startup/shutdown sequences
- [ ] Write integration tests
- [ ] Update monitoring dashboards

### Testing Strategy

1. **Unit Tests**: Each component in isolation
2. **Integration Tests**: Component pairs
3. **System Tests**: Full flow end-to-end
4. **Load Tests**: Under resource pressure

---

**Вопросы**:
1. Начать с интеграции или сначала unit tests?
2. Wishlist в памяти или сразу в Supabase?
3. EventBus использовать для internal communication или только external?
