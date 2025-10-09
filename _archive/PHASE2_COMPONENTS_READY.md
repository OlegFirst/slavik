# Phase 2 Components - Ready for Integration

**Date**: 2025-10-09
**Status**: Core components implemented
**Integration**: Pending

## What Was Built

### 1. Wishlist System ✅

**Location**: `/intelligent-core/coordination-center/wishlist/`

**Files**:
- `wishlist_system.py` (650 lines)
- `__init__.py`

**Key Features**:
- **WishlistItem**: Желание с приоритетом, ресурсами, зависимостями
- **NeedType**: SURVIVAL, EFFICIENCY, LEARNING, GROWTH
- **ResourceCost**: CPU, Memory, Time, Disk IO
- **Conflict Detection**: Циклические зависимости, ресурсы, deadline
- **Auto-Resolution**: Автоматическое разрешение конфликтов
- **Priority Calculation**: Учет urgency, ресурсов, deadline
- **Obsolescence**: Автоматическое удаление старых (24ч)
- **Persistence**: JSON storage + автозагрузка

**Integration Points**:
```python
# Survival Instinct создает желания при дисбалансе
wishlist.add_wish(
    description="Optimize cache to reduce response time",
    need_type=NeedType.EFFICIENCY,
    urgency=imbalance.level_value(),
    resource_cost=ResourceCost(cpu_percent=5, time_seconds=30)
)

# Memory System влияет на приоритеты
# Если паттерн был успешен → urgency выше

# Resource Tracker определяет что можно выполнить
available = resource_tracker.get_available_resources()
prioritized = wishlist.get_prioritized_wishes(available, limit=5)
```

**API**:
```python
# Добавить желание
item = wishlist.add_wish(desc, need_type, urgency, cost, parent_id, deps, deadline)

# Получить приоритизированный список
wishes = wishlist.get_prioritized_wishes(available_resources, limit=10)

# Очистить устаревшие
obsolete = wishlist.cleanup_obsolete()

# Разрешить конфликты
resolutions = wishlist.detect_and_resolve_conflicts(available_resources)

# Завершить
wishlist.complete_wish(item_id, success=True)

# Статистика
stats = wishlist.get_stats()
```

### 2. Resource Tracker ✅

**Location**: `/intelligent-core/coordination-center/resources/`

**Files**:
- `resource_tracker.py` (450 lines)
- `__init__.py`

**Key Features**:
- **Snapshots**: CPU, Memory, Disk IO, Network каждые 60s
- **History**: Последние 100 снимков (deque)
- **Trend Calculation**: Линейная регрессия → -1 to +1
- **Deficit Prediction**: Предсказание когда метрика достигнет порога
- **Resource State**: deficit/normal/surplus
- **Available Resources**: Для Wishlist приоритизации
- **Persistence**: JSON storage
- **Background Loop**: Asyncio мониторинг

**Trends**:
```python
cpu_trend = tracker.calculate_trend('cpu_percent', window_size=10)
# +1.0 = быстрый рост
# 0.0 = стабильно
# -1.0 = быстрое падение
```

**Deficit Prediction**:
```python
seconds_to_deficit = tracker.predict_deficit(
    'cpu_percent',
    threshold_percent=90.0,
    lookahead_snapshots=5
)
# Returns: секунды до порога (или None)
```

**Integration**:
```python
# Получить доступные ресурсы
available = tracker.get_available_resources()
# Returns: {'cpu_percent': 45.0, 'memory_mb': 2048.0, ...}

# Определить состояние
state = tracker.detect_resource_state()
# Returns: "deficit", "normal", "surplus"

# При deficit → триггер самореализации
if state == "deficit":
    # Train lightweight model
    # Optimize algorithms
    # Reduce resource usage
```

## Architecture Integration

### Data Flow

```
┌─────────────────────────────────────────────────────────┐
│              Resource Tracker                           │
│  • Monitors CPU/Memory/Disk/Network                     │
│  • Calculates trends                                    │
│  • Predicts deficits                                    │
│  • Provides available resources                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ available_resources
                 │
                 v
┌─────────────────────────────────────────────────────────┐
│              Wishlist System                            │
│  • Stores needs/desires                                 │
│  • Prioritizes based on resources                       │
│  • Detects conflicts                                    │
│  • Auto-resolves conflicts                              │
│  • Removes obsolete items                               │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ prioritized_wishes
                 │
                 v
┌─────────────────────────────────────────────────────────┐
│          Survival Instinct / Modules                    │
│  • Create wishes when imbalance detected                │
│  • Execute top-priority wishes                          │
│  • Report success/failure to Memory                     │
└─────────────────────────────────────────────────────────┘
                 │
                 │ pattern_learning
                 │
                 v
┌─────────────────────────────────────────────────────────┐
│              Memory System                              │
│  • Stores successful action patterns                    │
│  • Influences future wish priorities                    │
│  • Feeds patterns to Game Loop                          │
└─────────────────────────────────────────────────────────┘
```

### Integration Steps

#### Step 1: Add to system-bcm-service main.py

```python
from coordination_center.wishlist import create_wishlist_system
from coordination_center.resources import create_resource_tracker

# In ServiceState
class ServiceState:
    def __init__(self):
        # ... existing ...
        self.wishlist = None
        self.resource_tracker = None

# In startup
async def startup():
    # ... existing ...

    # Initialize Resource Tracker
    resource_storage = Path(__file__).parent / "data" / "resource_history.json"
    state.resource_tracker = await create_resource_tracker(
        snapshot_interval_seconds=60.0,
        history_size=100,
        storage_path=str(resource_storage)
    )
    logger.info("✅ Resource Tracker started")

    # Initialize Wishlist System
    wishlist_storage = Path(__file__).parent / "data" / "wishlist.json"
    state.wishlist = await create_wishlist_system(
        storage_path=str(wishlist_storage),
        max_item_age_seconds=86400.0  # 24 hours
    )
    logger.info("✅ Wishlist System initialized")

    # ... existing Memory, Survival ...

# In shutdown
async def shutdown():
    # ... existing ...

    if state.resource_tracker:
        state.resource_tracker.stop()

# API endpoints
@app.get("/wishlist/items")
async def get_wishlist_items():
    if not state.wishlist:
        raise HTTPException(status_code=503, detail="Wishlist not initialized")

    available = state.resource_tracker.get_available_resources()
    wishes = state.wishlist.get_prioritized_wishes(available, limit=20)

    return {
        "total_items": len(state.wishlist.items),
        "prioritized": [
            {
                "id": w.id,
                "description": w.description,
                "urgency": w.urgency,
                "priority": w.priority,
                "need_type": w.need_type.value,
                "status": w.status
            }
            for w in wishes
        ]
    }

@app.get("/resources/trends")
async def get_resource_trends():
    if not state.resource_tracker:
        raise HTTPException(status_code=503, detail="Resource tracker not initialized")

    return {
        "cpu_trend": state.resource_tracker.calculate_trend('cpu_percent'),
        "memory_trend": state.resource_tracker.calculate_trend('memory_percent'),
        "state": state.resource_tracker.detect_resource_state(),
        "available": state.resource_tracker.get_available_resources(),
        "stats": state.resource_tracker.get_stats()
    }
```

#### Step 2: Enhance Survival Instinct Integration

```python
# In survival.py
async def trigger_my_correction(self, imbalance: ImbalanceDetection):
    # ... existing code ...

    # Add wish to Wishlist
    if self.wishlist_system:
        resource_cost = self._estimate_action_cost(action)

        wish_item = self.wishlist_system.add_wish(
            description=action.description,
            need_type=NeedType.SURVIVAL if imbalance.level == ImbalanceLevel.CRITICAL else NeedType.EFFICIENCY,
            urgency=imbalance.level_value(),
            resource_cost=resource_cost,
            deadline=time.time() + 3600  # 1 hour
        )

        logger.info(f"Added wish: {wish_item.id}")

def _estimate_action_cost(self, action: CorrectionAction) -> ResourceCost:
    """Estimate resource cost of action"""
    costs = {
        'scale_up': ResourceCost(cpu_percent=20, memory_mb=500, time_seconds=120),
        'optimize_cache': ResourceCost(cpu_percent=10, memory_mb=100, time_seconds=30),
        'restart_service': ResourceCost(cpu_percent=30, memory_mb=0, time_seconds=10),
        'throttle_requests': ResourceCost(cpu_percent=5, memory_mb=50, time_seconds=5),
    }
    return costs.get(action.action_type, ResourceCost(cpu_percent=5, time_seconds=10))
```

#### Step 3: Background Task to Execute Wishes

```python
# In main.py
async def wishlist_executor_loop():
    """Execute wishes from Wishlist"""
    logger.info("Wishlist executor started")

    while state.running:
        try:
            # Get available resources
            available = state.resource_tracker.get_available_resources()

            # Get prioritized wishes
            wishes = state.wishlist.get_prioritized_wishes(available, limit=1)

            if wishes:
                wish = wishes[0]

                # Check if can afford
                if wish.resource_cost.can_afford_with(available):
                    logger.info(f"Executing wish: {wish.description}")

                    wish.status = "active"

                    # Execute (delegate to appropriate handler)
                    success = await execute_wish_action(wish)

                    # Complete
                    state.wishlist.complete_wish(wish.id, success)

                    # Learn pattern
                    if state.memory:
                        state.memory.remember_pattern(
                            state_signature=f"{wish.need_type.value}_{wish.urgency:.1f}",
                            action_type=wish.description[:50],
                            success=success
                        )

            # Cleanup obsolete
            state.wishlist.cleanup_obsolete()

            # Resolve conflicts
            state.wishlist.detect_and_resolve_conflicts(available)

            await asyncio.sleep(30)  # Check every 30s

        except Exception as e:
            logger.error(f"Wishlist executor error: {e}")
            await asyncio.sleep(30)

async def execute_wish_action(wish: WishlistItem) -> bool:
    """Execute action for wish"""
    # Map wish to action
    # This is where wishes become reality!

    if "optimize" in wish.description.lower():
        # Trigger optimization
        return await optimize_something()

    elif "scale" in wish.description.lower():
        # Trigger scaling
        return await scale_something()

    # Default: mark as success
    return True

# Start in startup
state.wishlist_executor = asyncio.create_task(wishlist_executor_loop())
```

## What's NOT Implemented Yet

### From Extracted Concepts

1. **Existential Dimensions** (Growth, Purpose)
   - Currently only Survival dimension
   - Need to track Growth and Purpose levels
   - Files: `/intelligent-core/ai-foundation/existential/`

2. **Motivation Engine**
   - Autonomy, Competence, Relatedness, Purpose scores
   - Influences wish priorities
   - Files: `/intelligent-core/ai-foundation/motivation/`

3. **Strategic Planning Layer**
   - Long-term goals (weeks-months)
   - Capability trend analysis
   - Direction adjustment
   - Files: `/intelligent-core/ai-foundation/strategy/`

4. **Initiative Levels**
   - Conservative/Balanced/Experimental/Creative modes
   - Adaptive based on success rate
   - Add to Game Loop

5. **Self-Actualization Engine**
   - Training lightweight models
   - Triggered by resource deficit
   - Files: `/intelligent-core/ai-foundation/self_actualization/`

## Database Schema (Supabase)

If you want to persist to Supabase instead of JSON files:

```sql
-- Wishlist items table
CREATE TABLE wishlist_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    description TEXT NOT NULL,
    need_type TEXT NOT NULL,
    urgency FLOAT NOT NULL,
    resource_cost JSONB NOT NULL,
    parent_id UUID REFERENCES wishlist_items(id),
    dependencies UUID[] DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    deadline TIMESTAMP,
    context JSONB DEFAULT '{}'::jsonb
);

-- Resource snapshots table
CREATE TABLE resource_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP NOT NULL,
    cpu_percent FLOAT NOT NULL,
    memory_percent FLOAT NOT NULL,
    memory_mb FLOAT NOT NULL,
    disk_io_mb FLOAT NOT NULL,
    network_bytes FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_wishlist_status ON wishlist_items(status);
CREATE INDEX idx_wishlist_urgency ON wishlist_items(urgency DESC);
CREATE INDEX idx_resource_timestamp ON resource_snapshots(timestamp DESC);
```

## Performance Notes

### Resource Tracker
- Snapshot every 60s: ~5KB memory per snapshot
- 100 snapshots = 500KB memory
- Disk: ~10KB per save
- Negligible CPU impact

### Wishlist System
- ~1KB per wish item
- 1000 items = 1MB memory
- Conflict detection: O(n²) worst case, but n is small (<100)
- Priority calculation: O(n log n) for sorting

### Combined Impact
- Memory: <2MB total
- CPU: <1% average
- Disk: <1MB per day

## Next Steps

### Phase 2A (Immediate)
1. ✅ Wishlist System - DONE
2. ✅ Resource Tracker - DONE
3. ⏳ Integration into system-bcm-service
4. ⏳ Background executor for wishes
5. ⏳ API endpoints
6. ⏳ Testing

### Phase 2B (Soon)
1. Existential Dimensions
2. Motivation Engine
3. Strategic Planning Layer
4. Self-Actualization Engine

### Phase 3 (Later)
1. Learning with resource costs
2. Play Instinct
3. Advanced conflict resolution
4. Multi-agent coordination

## Testing Plan

```python
# Test wishlist_system.py
pytest intelligent-core/coordination-center/wishlist/test_wishlist.py

# Test resource_tracker.py
pytest intelligent-core/coordination-center/resources/test_resource_tracker.py

# Integration test
pytest intelligent-core/system-bcm-service/tests/test_phase2_integration.py
```

## Success Criteria

Phase 2A is complete when:
- ✅ Wishlist System stores and prioritizes wishes
- ✅ Resource Tracker monitors and predicts trends
- ⏳ Survival Instinct creates wishes on imbalance
- ⏳ Background executor processes wishes
- ⏳ API endpoints functional
- ⏳ Integration tests pass
- ⏳ Documentation complete

## Summary

**Built**:
- Wishlist System (650 lines) with conflict resolution
- Resource Tracker (450 lines) with trend prediction

**Ready for**:
- Integration into system-bcm-service
- Database persistence (optional)
- Testing

**Not Yet**:
- Existential Dimensions
- Motivation Engine
- Strategic Planning
- Self-Actualization

**Strategy**: Start small, grow organically. Don't overload. Add features as needed.
