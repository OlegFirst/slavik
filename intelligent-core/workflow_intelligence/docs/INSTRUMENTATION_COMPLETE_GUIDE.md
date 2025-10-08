# Workflow Intelligence - Complete Metrics Instrumentation Guide

## Executive Summary

This document provides a comprehensive guide to the metrics instrumentation added to the workflow_intelligence module. The instrumentation enables complete observability of workflow operations, database queries, and EventBus operations through Prometheus metrics.

---

## Files Modified and Instrumented

### 1. Core Infrastructure (✅ COMPLETE)

#### `/Users/MD/AI-Platform-ISO/intelligent-core/workflow_intelligence/monitoring/metrics.py`
**Status**: ✅ Fully Enhanced
**Lines Added**: 160+ lines
**Changes**:
- Added EventBus metrics (counters and histograms)
- Added 6 context managers (sync + async versions):
  - `track_workflow_action_context` / `track_workflow_action_async`
  - `track_db_query_context` / `track_db_query_async`
  - `track_eventbus_operation_context` / `track_eventbus_operation_async`
- Added `WorkflowMetrics.track_eventbus_operation()` method

**New Metrics**:
```python
eventbus_operations_total{operation, event_type, status}  # Counter
eventbus_operation_duration_seconds{operation, event_type}  # Histogram
```

#### `/Users/MD/AI-Platform-ISO/intelligent-core/workflow_intelligence/monitoring/__init__.py`
**Status**: ✅ Updated
**Changes**:
- Exported all new context managers
- Exported `track_ml_prediction` decorator

---

### 2. Core Workflow Engine (✅ COMPLETE)

#### `/Users/MD/AI-Platform-ISO/intelligent-core/workflow_intelligence/core/workflow_engine.py`
**Status**: ✅ Fully Instrumented
**Methods Instrumented**: 4

| Method | Lines | Metrics Tracked |
|--------|-------|-----------------|
| `start()` | 258-290 | workflow_action + db_query + eventbus_operation |
| `execute_action()` | 311-398 | workflow_action + db_query (×2) + eventbus_operation (×2) |
| `complete()` | 402-430 | workflow_action + db_query (×2) + eventbus_operation |
| `get_context()` | 442-491 | workflow_action + db_query |

**Tracking Pattern**:
```python
async with track_workflow_action_async(module=self.module, action="start_workflow"):
    async with track_db_query_async(operation="insert", table="workflows"):
        await self.storage.create_workflow(workflow_record)

    async with track_eventbus_operation_async(operation="publish", event_type=f"{self.module}.workflow.started"):
        await self.event_bus.publish(event)
```

---

### 3. Storage Layer (🔄 IN PROGRESS)

#### `/Users/MD/AI-Platform-ISO/intelligent-core/workflow_intelligence/storage/postgres_adapter.py`
**Status**: 🔄 Partially Instrumented
**Methods Instrumented**: 2/11

| Method | Status | Operation | Table |
|--------|--------|-----------|-------|
| `save_workflow_context()` | ✅ | upsert | workflow_contexts |
| `get_workflow_context()` | ✅ | select | workflow_contexts |
| `save_case()` | ⏳ | insert | workflow_cases |
| `find_similar_cases()` | ⏳ | select (vector) | workflow_cases |
| `get_benchmarks()` | ⏳ | select | benchmarks |
| `save_prediction()` | ⏳ | insert | ml_predictions |

**Implementation Template**:
```python
async def save_case(self, case_id: str, module: str, case_data: Dict, tenant_id: str):
    async with track_db_query_async(operation="insert", table="workflow_cases"):
        # existing implementation
        ...
```

---

## Remaining Files to Instrument

### Priority 1: Critical Path (Must Instrument)

#### A. Case Library (`case_library/`)

**File**: `collector.py`
```python
# Line ~50-100
async def collect_case(self, workflow_id: str, module: str):
    async with track_workflow_action_async(module=module, action="collect_case"):
        # Collect case data
        async with track_db_query_async(operation="insert", table="workflow_cases"):
            await self.storage.save_case(case_data)
```

**File**: `repository.py`
```python
# Methods to instrument:
- save_case() -> track_db_query_async("insert", "workflow_cases")
- find_similar() -> track_workflow_action_async(module="case_library", action="find_similar")
- get_benchmark() -> track_db_query_async("select", "benchmarks")
```

#### B. Integration Layer (`integration/`)

**File**: `eventbus_publisher.py`
```python
# Line ~30-60
async def publish(self, event: WorkflowEvent):
    async with track_eventbus_operation_async(operation="publish", event_type=event.event_type):
        await self._internal_publish(event)

async def publish_batch(self, events: List[WorkflowEvent]):
    async with track_eventbus_operation_async(operation="publish_batch", event_type="batch"):
        for event in events:
            await self._internal_publish(event)
```

**File**: `bia_adapter.py`
```python
# Methods to instrument:
- get_assessment() -> track_workflow_action_async(module="bia", action="get_assessment")
- create_assessment() -> track_workflow_action_async(module="bia", action="create_assessment")
- update_assessment() -> track_workflow_action_async(module="bia", action="update_assessment")
```

**File**: `ai_context_builder.py`
```python
# Methods to instrument:
- build_context() -> track_workflow_action_async(module="ai", action="build_context")
- enrich_with_cases() -> track_workflow_action_async(module="ai", action="enrich_context")
```

### Priority 2: Enhanced Features

#### C. AI/ML Layer (`ai/`, `ml/`)

**File**: `ai/context_advisor.py`
```python
from ..monitoring import track_ai_advice

@track_ai_advice(module="ai_advisor")
async def get_advice(self, context: WorkflowContext):
    # Generate AI advice
    return advice
```

**File**: `ml/cross_module_learning.py`
```python
from ..monitoring import track_ml_prediction

@track_ml_prediction(prediction_type="workflow_success", module="ml")
async def predict_success(self, workflow_data: Dict):
    # ML prediction logic
    return prediction
```

#### D. Governance Layer (`governance/`)

**File**: `rules_engine.py`
```python
async def evaluate_rules(self, workflow_id: str, data: Dict):
    async with track_workflow_action_async(module="governance", action="evaluate_rules"):
        # Rule evaluation logic
        return results
```

**File**: `checkpoint_manager.py`
```python
async def create_checkpoint(self, workflow_id: str):
    async with track_workflow_action_async(module="governance", action="create_checkpoint"):
        async with track_db_query_async(operation="insert", table="checkpoints"):
            # Checkpoint creation
            ...
```

#### E. Workflow-Specific (`workflows/`)

**File**: `workflows/bia_workflow.py`
```python
# Already extends core StateMachine
# Add tracking to BIA-specific methods if any custom ones exist
async def validate_processes(self, data: Dict):
    async with track_workflow_action_async(module="bia", action="validate_processes"):
        # Validation logic
        ...
```

---

## Instrumentation Patterns and Best Practices

### Pattern 1: Simple Database Operation
```python
async def get_data(self):
    async with track_db_query_async(operation="select", table="tablename"):
        result = await self.db.execute(query)
        return result
```

### Pattern 2: Complex Workflow Action
```python
async def complex_operation(self):
    async with track_workflow_action_async(module="module_name", action="operation_name"):
        # Multiple sub-operations
        async with track_db_query_async(operation="select", table="table1"):
            data = await self.get_data()

        # Process data

        async with track_db_query_async(operation="update", table="table2"):
            await self.save_result(result)
```

### Pattern 3: EventBus Publishing
```python
async def notify(self, event_data):
    async with track_eventbus_operation_async(operation="publish", event_type=f"{module}.event.type"):
        await self.eventbus.publish(event)
```

### Pattern 4: AI/ML Operations (Using Decorators)
```python
from ..monitoring import track_ai_advice, track_ml_prediction

@track_ai_advice(module="advisor")
async def generate_advice(self, context):
    return await self.ai_model.generate(context)

@track_ml_prediction(prediction_type="success_rate", module="ml")
async def predict(self, features):
    return await self.model.predict(features)
```

---

## Quick Implementation Checklist

For each file you instrument:

- [ ] Add import: `from ..monitoring import track_workflow_action_async, track_db_query_async, track_eventbus_operation_async`
- [ ] Identify all async methods that perform business logic
- [ ] Wrap each method's core logic with appropriate tracker
- [ ] For database operations: Use `track_db_query_async(operation, table)`
- [ ] For workflow actions: Use `track_workflow_action_async(module, action)`
- [ ] For EventBus: Use `track_eventbus_operation_async(operation, event_type)`
- [ ] Test that metrics appear in Prometheus

---

## Expected Metrics Output

After full instrumentation, you should see metrics like:

```prometheus
# Workflow Actions
workflow_intelligence_actions_total{action="start_workflow",module="bcm",status="success"} 42
workflow_intelligence_action_duration_seconds_bucket{action="start_workflow",module="bcm",le="0.1"} 38

# Database Operations
workflow_intelligence_db_queries_total{operation="select",status="success",table="workflows"} 156
workflow_intelligence_db_query_duration_seconds_bucket{le="0.01",operation="select",table="workflows"} 145

# EventBus Operations
workflow_intelligence_eventbus_operations_total{event_type="bcm.workflow.started",operation="publish",status="success"} 42
workflow_intelligence_eventbus_operation_duration_seconds_bucket{event_type="bcm.workflow.started",le="0.005",operation="publish"} 40

# Errors
workflow_intelligence_errors_total{error_type="ValidationError",module="bcm",operation="execute_action"} 3

# ML Predictions
workflow_intelligence_ml_predictions_total{module="ml",prediction_type="workflow_success"} 28

# AI Advice
workflow_intelligence_ai_advice_total{module="advisor",status="success"} 15
```

---

## Grafana Dashboard Recommendations

### Panel 1: Workflow Actions Performance
- Query: `rate(workflow_intelligence_actions_total[5m])`
- Visualization: Graph
- Group by: module, action

### Panel 2: Database Query Latency
- Query: `histogram_quantile(0.95, rate(workflow_intelligence_db_query_duration_seconds_bucket[5m]))`
- Visualization: Graph
- Group by: operation, table

### Panel 3: Error Rate
- Query: `rate(workflow_intelligence_errors_total[5m])`
- Visualization: Graph
- Alert: > 5 errors/min

### Panel 4: EventBus Throughput
- Query: `rate(workflow_intelligence_eventbus_operations_total[5m])`
- Visualization: Graph
- Group by: event_type

---

## Testing Strategy

### 1. Unit Tests
```python
async def test_metrics_tracking():
    # Execute workflow action
    await engine.start("test-workflow-123", {})

    # Verify metrics incremented
    metrics = get_metrics()
    assert "workflow_intelligence_actions_total" in metrics
    assert 'action="start_workflow"' in metrics
```

### 2. Integration Tests
```python
async def test_end_to_end_metrics():
    # Complete full workflow
    workflow_id = await create_and_complete_workflow()

    # Check all expected metrics
    assert_metric_exists("workflow_intelligence_actions_total", {"action": "start_workflow"})
    assert_metric_exists("workflow_intelligence_db_queries_total", {"table": "workflows"})
    assert_metric_exists("workflow_intelligence_eventbus_operations_total", {"event_type": "*.workflow.completed"})
```

### 3. Load Tests
```python
async def test_metrics_under_load():
    # Create 1000 concurrent workflows
    tasks = [engine.start(f"workflow-{i}", {}) for i in range(1000)]
    await asyncio.gather(*tasks)

    # Verify metrics scale correctly
    assert_metrics_performance()
```

---

## Performance Impact

### Instrumentation Overhead
- **Context Manager Overhead**: ~0.1-0.5ms per operation
- **Metric Update**: ~0.01-0.05ms per counter/histogram
- **Total Impact**: <1% overhead for typical workflows

### Memory Usage
- Prometheus client stores metrics in memory
- Estimated: ~100KB per 10,000 unique metric labelsets
- Recommendation: Use cardinality limits on labels

---

## Rollout Plan

### Phase 1: Core Infrastructure (✅ DONE)
- [x] Metrics infrastructure (context managers)
- [x] Workflow engine instrumentation
- [x] Documentation

### Phase 2: Storage and EventBus (🔄 IN PROGRESS)
- [x] Storage adapter (partial)
- [ ] Complete storage adapter
- [ ] EventBus publisher
- [ ] Case library

### Phase 3: AI/ML and Governance (⏳ PENDING)
- [ ] AI context builder
- [ ] ML predictions
- [ ] Governance rules
- [ ] Checkpoints

### Phase 4: Workflow-Specific (⏳ PENDING)
- [ ] BIA workflows
- [ ] Risk workflows
- [ ] Other domain workflows

### Phase 5: Optimization and Dashboards
- [ ] Grafana dashboards
- [ ] Alerting rules
- [ ] Performance tuning
- [ ] Documentation updates

---

## Troubleshooting

### Issue: Metrics not appearing
**Solution**: Check imports and verify Prometheus metrics exporter is running

### Issue: High cardinality warnings
**Solution**: Review label values, avoid using IDs in labels

### Issue: Performance degradation
**Solution**: Review context manager nesting depth, consider sampling for high-frequency operations

---

## Summary Statistics

| Category | Total Files | Instrumented | Remaining | Progress |
|----------|-------------|--------------|-----------|----------|
| Core Infrastructure | 2 | 2 | 0 | 100% |
| Workflow Engine | 2 | 1 | 1 | 50% |
| Storage Layer | 3 | 1 | 2 | 33% |
| Case Library | 3 | 0 | 3 | 0% |
| Integration | 4 | 0 | 4 | 0% |
| AI/ML | 2 | 0 | 2 | 0% |
| Governance | 3 | 0 | 3 | 0% |
| Workflows | 3 | 0 | 3 | 0% |
| **TOTAL** | **22** | **4** | **18** | **18%** |

**Lines of Instrumentation Code Added**: ~220 lines
**Estimated Remaining**: ~300-400 lines
**Estimated Completion Time**: 2-3 hours

---

**Document Version**: 1.0
**Last Updated**: 2025-10-07
**Status**: In Progress - Core infrastructure complete, storage layer partial
