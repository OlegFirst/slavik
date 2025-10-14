# Workflow Intelligence Metrics Instrumentation
## Quick Start Guide

This directory contains comprehensive metrics instrumentation for the Workflow Intelligence module.

---

## 📚 Documentation Index

### For Quick Overview
- **START HERE**: [`INSTRUMENTATION_EXECUTIVE_SUMMARY.md`](./INSTRUMENTATION_EXECUTIVE_SUMMARY.md)
  - High-level overview of what was done
  - Business value and impact
  - Statistics and progress
  - **Best for**: Managers, stakeholders, quick overview

### For Implementation Details
- **DETAILED REPORT**: [`INSTRUMENTATION_DETAILED_REPORT.md`](./INSTRUMENTATION_DETAILED_REPORT.md)
  - Line-by-line changes with exact line numbers
  - Every context manager documented
  - Performance benchmarks
  - **Best for**: Code review, debugging, understanding exact changes

### For Implementation Guide
- **COMPLETE GUIDE**: [`INSTRUMENTATION_COMPLETE_GUIDE.md`](./INSTRUMENTATION_COMPLETE_GUIDE.md)
  - How to instrument remaining files
  - Patterns and best practices
  - Testing strategies
  - Grafana dashboard recommendations
  - **Best for**: Developers adding new instrumentation

### For Original Report
- **INITIAL REPORT**: [`INSTRUMENTATION_REPORT.md`](./INSTRUMENTATION_REPORT.md)
  - Original instrumentation plan
  - Metrics overview
  - File-by-file breakdown
  - **Best for**: Understanding the original scope

---

## 🚀 Quick Start

### View Current Metrics
```bash
# Start the service (if not running)
cd /Users/MD/AI-Platform-ISO/intelligent-core/workflow_intelligence
python -m workflow_intelligence.main

# View metrics endpoint
curl http://localhost:8000/metrics | grep workflow_intelligence

# Or visit in browser
open http://localhost:8000/metrics
```

### Add Metrics to Your Code
```python
from workflow_intelligence.monitoring import (
    track_workflow_action_async,
    track_db_query_async,
    track_eventbus_operation_async
)

async def my_function(self):
    async with track_workflow_action_async(module="my_module", action="my_action"):
        # Your business logic here

        async with track_db_query_async(operation="select", table="my_table"):
            data = await self.db.query()

        async with track_eventbus_operation_async(operation="publish", event_type="my.event"):
            await self.eventbus.publish(event)
```

---

## 📊 Metrics Available

### Workflow Actions
```prometheus
workflow_intelligence_actions_total{module, action, status}
workflow_intelligence_action_duration_seconds{module, action}
```

### Database Operations
```prometheus
workflow_intelligence_db_queries_total{operation, table, status}
workflow_intelligence_db_query_duration_seconds{operation, table}
```

### EventBus Operations
```prometheus
workflow_intelligence_eventbus_operations_total{operation, event_type, status}
workflow_intelligence_eventbus_operation_duration_seconds{operation, event_type}
```

### Error Tracking
```prometheus
workflow_intelligence_errors_total{error_type, module, operation}
```

---

## 📁 Files Modified

| File | Status | Purpose |
|------|--------|---------|
| `monitoring/metrics.py` | ✅ Complete | Context managers and metrics definitions |
| `monitoring/__init__.py` | ✅ Complete | Export tracking functions |
| `core/workflow_engine.py` | ✅ Complete | Core workflow tracking |
| `storage/postgres_adapter.py` | 🔄 Partial | Database operation tracking |

---

## 📈 Current Coverage

- **Infrastructure**: 100% ✅
- **Core Workflows**: 100% ✅
- **Storage Layer**: 18% 🔄
- **Overall**: ~18% (Phase 1 complete)

---

## 🎯 Next Steps

1. **Immediate**: Complete `storage/postgres_adapter.py` instrumentation
2. **Short-term**: Instrument `case_library/` and `integration/` modules
3. **Medium-term**: Add Grafana dashboards and alerting

See [`INSTRUMENTATION_COMPLETE_GUIDE.md`](./INSTRUMENTATION_COMPLETE_GUIDE.md) for detailed next steps.

---

## 🔧 Context Managers Available

### Async Context Managers (Primary)
- `track_workflow_action_async(module, action)` - Track business operations
- `track_db_query_async(operation, table)` - Track database queries
- `track_eventbus_operation_async(operation, event_type)` - Track event bus

### Sync Context Managers (Legacy Support)
- `track_workflow_action_context(module, action)`
- `track_db_query_context(operation, table)`
- `track_eventbus_operation_context(operation, event_type)`

### Decorators
- `@track_workflow_action(module, action)` - Method decorator
- `@track_ai_advice(module)` - AI advice tracking
- `@track_ml_prediction(prediction_type, module)` - ML prediction tracking
- `@track_case_collection(module)` - Case collection tracking

---

## 📝 Example Queries

### Prometheus Queries

```promql
# Request rate per module
sum(rate(workflow_intelligence_actions_total[5m])) by (module)

# Error rate
rate(workflow_intelligence_errors_total[5m])

# Slow operations (P95 latency)
histogram_quantile(0.95,
  rate(workflow_intelligence_action_duration_seconds_bucket[5m])
)

# Database query performance by table
histogram_quantile(0.95,
  rate(workflow_intelligence_db_query_duration_seconds_bucket[5m])
) by (table)

# EventBus throughput
sum(rate(workflow_intelligence_eventbus_operations_total[5m])) by (event_type)
```

---

## 🎨 Grafana Dashboard Ideas

### Panel 1: Workflow Performance
- Metric: `workflow_intelligence_action_duration_seconds`
- Visualization: Heatmap or Graph
- Group by: `module`, `action`

### Panel 2: Database Performance
- Metric: `workflow_intelligence_db_query_duration_seconds`
- Visualization: Graph with P50, P95, P99
- Group by: `table`

### Panel 3: Error Rate
- Metric: `workflow_intelligence_errors_total`
- Visualization: Graph
- Alert threshold: > 5 errors/min

### Panel 4: Throughput
- Metric: `workflow_intelligence_actions_total`
- Visualization: Counter + Graph
- Aggregation: `rate()` over 5m

---

## 🚨 Alerting Examples

```yaml
groups:
  - name: workflow_intelligence
    rules:
      - alert: HighErrorRate
        expr: rate(workflow_intelligence_errors_total[5m]) > 5
        for: 2m
        annotations:
          summary: "High error rate in workflow intelligence"
          description: "Error rate is {{ $value }} errors/min"

      - alert: SlowWorkflows
        expr: histogram_quantile(0.95, rate(workflow_intelligence_action_duration_seconds_bucket[5m])) > 10
        for: 5m
        annotations:
          summary: "Workflows are running slow"
          description: "P95 latency is {{ $value }}s"

      - alert: DatabaseSlowQueries
        expr: histogram_quantile(0.95, rate(workflow_intelligence_db_query_duration_seconds_bucket[5m])) > 1
        for: 3m
        annotations:
          summary: "Database queries are slow"
          description: "P95 query time is {{ $value }}s"
```

---

## 🧪 Testing

### Unit Test Example
```python
import pytest
from prometheus_client import REGISTRY

async def test_workflow_tracking():
    # Execute workflow
    await workflow_engine.start("test-workflow", {})

    # Verify metrics exist
    metrics = REGISTRY.get_sample_value(
        'workflow_intelligence_actions_total',
        {'module': 'test', 'action': 'start_workflow', 'status': 'success'}
    )
    assert metrics >= 1
```

### Integration Test Example
```python
async def test_end_to_end_instrumentation():
    # Complete full workflow
    workflow_id = await create_and_complete_workflow()

    # Verify all expected metrics
    assert_metric_exists('workflow_intelligence_actions_total')
    assert_metric_exists('workflow_intelligence_db_queries_total')
    assert_metric_exists('workflow_intelligence_eventbus_operations_total')
```

---

## 📞 Support

### Questions?
- See [`INSTRUMENTATION_COMPLETE_GUIDE.md`](./INSTRUMENTATION_COMPLETE_GUIDE.md) for implementation help
- See [`INSTRUMENTATION_DETAILED_REPORT.md`](./INSTRUMENTATION_DETAILED_REPORT.md) for code details
- See [`INSTRUMENTATION_EXECUTIVE_SUMMARY.md`](./INSTRUMENTATION_EXECUTIVE_SUMMARY.md) for overview

### Issues?
- Check import paths: `from ..monitoring import ...`
- Verify context manager nesting
- Review error logs for tracking failures
- Check Prometheus is scraping the endpoint

---

## 📊 Performance Impact

**Overhead**: <5% on typical operations
**Memory**: ~100KB per 10,000 unique metrics
**Recommendation**: Safe for production use

See performance benchmarks in [`INSTRUMENTATION_DETAILED_REPORT.md`](./INSTRUMENTATION_DETAILED_REPORT.md)

---

## 🎯 Quick Reference Card

| Want to track... | Use this... | Example |
|-----------------|-------------|---------|
| Workflow action | `track_workflow_action_async()` | `async with track_workflow_action_async("bcm", "create_bia"):` |
| Database query | `track_db_query_async()` | `async with track_db_query_async("insert", "workflows"):` |
| EventBus publish | `track_eventbus_operation_async()` | `async with track_eventbus_operation_async("publish", "bia.created"):` |
| AI advice | `@track_ai_advice()` | `@track_ai_advice(module="advisor")` |
| ML prediction | `@track_ml_prediction()` | `@track_ml_prediction("success", "ml")` |

---

## 📅 Version History

- **v1.0** (2025-10-07): Initial instrumentation
  - Core infrastructure complete
  - Workflow engine fully instrumented
  - Storage layer partially instrumented
  - Documentation complete

---

**Last Updated**: 2025-10-07
**Status**: Phase 1 Complete, Phase 2 In Progress
**Coverage**: 18% (4/22 priority files)
