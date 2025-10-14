# Process Framework Prometheus Metrics

Comprehensive Prometheus metrics for monitoring business process execution, validation, and performance.

## Location

- **Main Module**: `/intelligent-core/workflow_intelligence/metrics/process_metrics.py`
- **Package Exports**: `/intelligent-core/workflow_intelligence/metrics/__init__.py`
- **Examples**: `/intelligent-core/workflow_intelligence/example_process_metrics.py`

## Quick Start

```python
from intelligent_core.workflow_intelligence.metrics import (
    process_metrics,
    track_process_execution,
    track_step_execution
)

# Manual tracking
process_metrics.track_process_start("bia_process")
process_metrics.track_step_execution("bia_process", "collect_data", 1.5, "success")
process_metrics.track_process_completion("bia_process", "completed", 125.5)

# Or use decorators
@track_process_execution(process_id="bia_process")
async def execute_process():
    # Your process logic
    pass
```

## Available Metrics

### Counters (Monotonically Increasing)

#### 1. `process_framework_process_started_total`
Total number of process instances started.

**Labels:**
- `process_id`: Process definition identifier (e.g., "bia_process", "risk_assessment")

**Example:**
```prometheus
process_framework_process_started_total{process_id="bia_process"} 142
process_framework_process_started_total{process_id="risk_assessment"} 87
```

**Usage:**
```python
process_metrics.track_process_start("bia_process")
```

---

#### 2. `process_framework_process_completed_total`
Total number of process instances completed.

**Labels:**
- `process_id`: Process definition identifier
- `status`: Completion status (completed, cancelled, suspended, failed)

**Example:**
```prometheus
process_framework_process_completed_total{process_id="bia_process",status="completed"} 128
process_framework_process_completed_total{process_id="bia_process",status="cancelled"} 8
```

**Usage:**
```python
process_metrics.track_process_completion("bia_process", "completed", 125.5)
```

**PromQL Queries:**
```promql
# Success rate
rate(process_framework_process_completed_total{status="completed"}[5m]) /
rate(process_framework_process_started_total[5m])

# Completion rate by status
sum by (status) (rate(process_framework_process_completed_total[5m]))
```

---

#### 3. `process_framework_step_executed_total`
Total number of process steps executed.

**Labels:**
- `process_id`: Process definition identifier
- `step_id`: Step identifier (e.g., "collect_data", "approval", "analysis")
- `result`: Execution result (success, error, skipped, validation_failed)

**Example:**
```prometheus
process_framework_step_executed_total{process_id="bia_process",step_id="collect_data",result="success"} 142
process_framework_step_executed_total{process_id="bia_process",step_id="approval",result="error"} 3
```

**Usage:**
```python
process_metrics.track_step_execution(
    "bia_process",
    "collect_data",
    1.5,  # duration
    "success"  # result
)
```

**PromQL Queries:**
```promql
# Step error rate
rate(process_framework_step_executed_total{result="error"}[5m])

# Most problematic steps
topk(5, sum by (step_id) (
  rate(process_framework_step_executed_total{result="error"}[1h])
))
```

---

#### 4. `process_framework_validation_errors_total`
Total number of validation errors by field.

**Labels:**
- `process_id`: Process definition identifier
- `step_id`: Step where validation occurred
- `field_name`: Name of the field that failed validation

**Example:**
```prometheus
process_framework_validation_errors_total{process_id="bia_process",step_id="collect_data",field_name="rto_value"} 12
process_framework_validation_errors_total{process_id="bia_process",step_id="collect_data",field_name="impact_score"} 8
```

**Usage:**
```python
process_metrics.track_validation_error("bia_process", "collect_data", "rto_value")
```

**PromQL Queries:**
```promql
# Most problematic fields
topk(10, sum by (field_name) (
  rate(process_framework_validation_errors_total[1h])
))

# Validation error rate by process
sum by (process_id) (rate(process_framework_validation_errors_total[5m]))
```

**Use Case:** Identify form fields that frequently cause validation issues, helping improve UX and data quality.

---

#### 5. `process_framework_documents_generated_total`
Total number of documents generated from templates.

**Labels:**
- `template_id`: Document template identifier (e.g., "bia_report", "risk_assessment_report")
- `format`: Output format (pdf, docx, html, json)

**Example:**
```prometheus
process_framework_documents_generated_total{template_id="bia_report",format="pdf"} 95
process_framework_documents_generated_total{template_id="bia_report",format="docx"} 47
```

**Usage:**
```python
process_metrics.track_document_generation("bia_report", "pdf")
```

**PromQL Queries:**
```promql
# Document generation rate
rate(process_framework_documents_generated_total[5m])

# Most popular formats
sum by (format) (rate(process_framework_documents_generated_total[1h]))
```

---

### Histograms (Distribution of Values)

#### 6. `process_framework_step_execution_duration_seconds`
Step execution duration distribution.

**Labels:**
- `process_id`: Process definition identifier
- `step_id`: Step identifier

**Buckets:** [1ms, 5ms, 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s, 10s, 30s, 1min, 5min]

**Provides:**
- `_bucket`: Count of observations in each bucket
- `_sum`: Total sum of all observations
- `_count`: Total count of observations

**Usage:**
```python
process_metrics.track_step_execution(
    "bia_process",
    "collect_data",
    1.234,  # duration in seconds
    "success"
)
```

**PromQL Queries:**
```promql
# Average step duration
rate(process_framework_step_execution_duration_seconds_sum[5m]) /
rate(process_framework_step_execution_duration_seconds_count[5m])

# 95th percentile step duration
histogram_quantile(0.95,
  rate(process_framework_step_execution_duration_seconds_bucket[5m])
)

# 99th percentile by step
histogram_quantile(0.99, sum by (step_id, le) (
  rate(process_framework_step_execution_duration_seconds_bucket[5m])
))

# Steps taking longer than 10s
sum(process_framework_step_execution_duration_seconds_bucket{le="10"}) by (step_id)
```

---

#### 7. `process_framework_process_duration_seconds`
Complete process execution duration distribution.

**Labels:**
- `process_id`: Process definition identifier

**Buckets:** [1s, 5s, 10s, 30s, 1min, 5min, 10min, 30min, 1h, 2h, 4h, 24h]

**Usage:**
```python
process_metrics.track_process_completion("bia_process", "completed", 125.5)
```

**PromQL Queries:**
```promql
# Average process duration
rate(process_framework_process_duration_seconds_sum[1h]) /
rate(process_framework_process_duration_seconds_count[1h])

# 99th percentile (SLA monitoring)
histogram_quantile(0.99,
  rate(process_framework_process_duration_seconds_bucket[1h])
)

# Processes exceeding 1 hour
sum(process_framework_process_duration_seconds_bucket{le="3600"}) by (process_id)
```

---

### Gauges (Current State Values)

#### 8. `process_framework_active_instances`
Number of currently active process instances.

**Labels:**
- `process_id`: Process definition identifier

**Example:**
```prometheus
process_framework_active_instances{process_id="bia_process"} 14
process_framework_active_instances{process_id="risk_assessment"} 8
```

**Usage:**
```python
# Set absolute value
process_metrics.update_active_instances("bia_process", 14)

# Or increment/decrement
process_metrics.increment_active_instances("bia_process")
process_metrics.decrement_active_instances("bia_process")
```

**PromQL Queries:**
```promql
# Total active processes
sum(process_framework_active_instances)

# Active processes by type
process_framework_active_instances

# Alert on high load
process_framework_active_instances{process_id="bia_process"} > 50
```

**Alerts:**
```yaml
- alert: HighProcessLoad
  expr: process_framework_active_instances > 50
  for: 15m
  annotations:
    summary: "High number of active {{ $labels.process_id }} processes"
```

---

#### 9. `process_framework_pending_approvals`
Number of process steps waiting for approval.

**Labels:**
- `process_id`: Process definition identifier
- `step_id`: Approval step identifier

**Example:**
```prometheus
process_framework_pending_approvals{process_id="bia_process",step_id="manager_approval"} 5
process_framework_pending_approvals{process_id="risk_assessment",step_id="final_approval"} 3
```

**Usage:**
```python
# Set absolute value
process_metrics.update_pending_approvals("bia_process", "manager_approval", 5)

# Or increment/decrement
process_metrics.increment_pending_approvals("bia_process", "manager_approval")
process_metrics.decrement_pending_approvals("bia_process", "manager_approval")
```

**PromQL Queries:**
```promql
# Total pending approvals
sum(process_framework_pending_approvals)

# Approval backlog by step
sum by (step_id) (process_framework_pending_approvals)

# Long-pending approvals (rate of change)
delta(process_framework_pending_approvals[1h])
```

**Alerts:**
```yaml
- alert: ApprovalBacklog
  expr: process_framework_pending_approvals > 10
  for: 15m
  annotations:
    summary: "High number of pending approvals for {{ $labels.step_id }}"

- alert: StuckApprovals
  expr: delta(process_framework_pending_approvals[1h]) == 0 and process_framework_pending_approvals > 0
  for: 2h
  annotations:
    summary: "Approvals not being processed"
```

---

## Usage Patterns

### 1. Manual Tracking

```python
from intelligent_core.workflow_intelligence.metrics import process_metrics
import time

# Start process
process_metrics.track_process_start("bia_process")
process_metrics.increment_active_instances("bia_process")

start_time = time.time()

# Execute steps
step_start = time.time()
# ... step logic ...
process_metrics.track_step_execution(
    "bia_process",
    "collect_data",
    time.time() - step_start,
    "success"
)

# Track validation errors
process_metrics.track_validation_error(
    "bia_process",
    "collect_data",
    "rto_value"
)

# Generate documents
process_metrics.track_document_generation("bia_report", "pdf")

# Complete process
process_metrics.track_process_completion(
    "bia_process",
    "completed",
    time.time() - start_time
)
process_metrics.decrement_active_instances("bia_process")
```

### 2. Decorator-Based Tracking

```python
from intelligent_core.workflow_intelligence.metrics import (
    track_process_execution,
    track_step_execution
)

@track_process_execution(process_id="bia_process")
async def execute_bia_process():
    """Process execution automatically tracked"""
    await step1()
    await step2()
    # Metrics tracked automatically

@track_step_execution(process_id="bia_process", step_id="collect_data")
async def step1():
    """Step execution automatically tracked"""
    # Step logic here
    pass
```

### 3. Validation Tracking

```python
from intelligent_core.workflow_intelligence.metrics import track_validation

@track_validation(process_id="bia_process", step_id="collect_data")
def validate_form(data: dict) -> dict:
    """Validation errors automatically tracked"""
    errors = {}

    if not data.get('rto_value'):
        errors['rto_value'] = ['Required field']

    # Errors are automatically tracked as metrics
    return errors
```

### 4. Integration with Process Framework

```python
from intelligent_core.workflow_intelligence.process_framework import get_process_framework
from intelligent_core.workflow_intelligence.metrics import process_metrics
import time

framework = get_process_framework()

# Start process with metrics
process_metrics.track_process_start("bia_process")
process_metrics.increment_active_instances("bia_process")

instance = framework.start_process("bia_process", "user@example.com")

# Execute step with metrics
step_start = time.time()
success, error, next_step = framework.execute_step(
    instance.id,
    {"rto_value": 24},
    "user@example.com"
)

if success:
    process_metrics.track_step_execution(
        "bia_process",
        instance.current_step_id,
        time.time() - step_start,
        "success"
    )
else:
    # Track validation errors
    for field_name in error:
        process_metrics.track_validation_error(
            "bia_process",
            instance.current_step_id,
            field_name
        )
```

## Viewing Metrics

### Start Metrics Exporter

```bash
# Default port (9001)
python3 -m intelligent_core.workflow_intelligence.metrics_exporter

# Custom port
python3 -m intelligent_core.workflow_intelligence.metrics_exporter --port 9002

# Custom host and port
python3 -m intelligent_core.workflow_intelligence.metrics_exporter --host 0.0.0.0 --port 9001
```

### Access Metrics Endpoint

Visit: `http://localhost:9001/metrics`

Look for metrics starting with `process_framework_`

### Example Metrics Output

```prometheus
# HELP process_framework_process_started_total Total number of process instances started
# TYPE process_framework_process_started_total counter
process_framework_process_started_total{process_id="bia_process"} 142.0
process_framework_process_started_total{process_id="risk_assessment"} 87.0

# HELP process_framework_active_instances Number of currently active process instances
# TYPE process_framework_active_instances gauge
process_framework_active_instances{process_id="bia_process"} 14.0

# HELP process_framework_step_execution_duration_seconds Step execution duration in seconds
# TYPE process_framework_step_execution_duration_seconds histogram
process_framework_step_execution_duration_seconds_bucket{le="0.1",process_id="bia_process",step_id="collect_data"} 89.0
process_framework_step_execution_duration_seconds_bucket{le="1.0",process_id="bia_process",step_id="collect_data"} 135.0
process_framework_step_execution_duration_seconds_sum{process_id="bia_process",step_id="collect_data"} 178.5
process_framework_step_execution_duration_seconds_count{process_id="bia_process",step_id="collect_data"} 142.0
```

## Prometheus Configuration

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'workflow_intelligence'
    static_configs:
      - targets: ['localhost:9001']
    scrape_interval: 15s
    scrape_timeout: 10s
```

## Grafana Dashboards

### Example Dashboard Panels

**1. Process Throughput**
```promql
rate(process_framework_process_completed_total[5m])
```

**2. Average Process Duration**
```promql
rate(process_framework_process_duration_seconds_sum[5m]) /
rate(process_framework_process_duration_seconds_count[5m])
```

**3. Active Processes**
```promql
sum(process_framework_active_instances)
```

**4. Step Error Rate**
```promql
rate(process_framework_step_executed_total{result="error"}[5m])
```

**5. Top Validation Errors**
```promql
topk(10, sum by (field_name) (
  rate(process_framework_validation_errors_total[1h])
))
```

**6. Pending Approvals**
```promql
sum(process_framework_pending_approvals) by (process_id, step_id)
```

## Alerting Rules

```yaml
groups:
  - name: process_framework
    interval: 30s
    rules:
      # High process load
      - alert: HighProcessLoad
        expr: process_framework_active_instances > 50
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "High number of active processes"
          description: "{{ $labels.process_id }} has {{ $value }} active instances"

      # Approval backlog
      - alert: ApprovalBacklog
        expr: process_framework_pending_approvals > 10
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "High number of pending approvals"
          description: "{{ $labels.step_id }} has {{ $value }} pending approvals"

      # High error rate
      - alert: HighStepErrorRate
        expr: |
          rate(process_framework_step_executed_total{result="error"}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High step error rate"
          description: "{{ $labels.step_id }} error rate: {{ $value }}"

      # Slow processes
      - alert: SlowProcessExecution
        expr: |
          histogram_quantile(0.95,
            rate(process_framework_process_duration_seconds_bucket[15m])
          ) > 3600
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Processes taking too long"
          description: "95th percentile: {{ $value }}s"

      # Validation error spike
      - alert: ValidationErrorSpike
        expr: |
          rate(process_framework_validation_errors_total[5m]) > 0.5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High validation error rate"
          description: "{{ $labels.field_name }}: {{ $value }} errors/sec"
```

## Examples

See `example_process_metrics.py` for complete working examples:

```bash
python3 example_process_metrics.py
```

## Testing

```bash
# Test imports
python3 -c "from intelligent_core.workflow_intelligence.metrics import process_metrics; print('OK')"

# Run examples
python3 example_process_metrics.py

# View metrics
curl http://localhost:9001/metrics | grep process_framework_
```

## Best Practices

1. **Always track process start/completion pairs**
   - Use `track_process_start()` when starting
   - Use `track_process_completion()` when done
   - Keep active instance count accurate

2. **Use decorators for automatic tracking**
   - Less boilerplate code
   - Automatic error handling
   - Consistent metrics

3. **Track validation errors granularly**
   - Track per-field errors
   - Identify UX issues
   - Improve form design

4. **Monitor approval queues**
   - Set alerts on high pending counts
   - Track approval throughput
   - Identify bottlenecks

5. **Use histograms for SLA monitoring**
   - Track percentiles (p95, p99)
   - Set alerts on slow operations
   - Identify performance degradation

## Troubleshooting

**Metrics not appearing:**
- Check metrics exporter is running
- Verify Prometheus scrape config
- Check for import errors

**Incorrect metric values:**
- Ensure increment/decrement pairs match
- Check for exception handling
- Verify decorator usage

**High cardinality:**
- Limit unique label values
- Avoid user IDs in labels
- Use field name instead of values

## Related Documentation

- [Process Framework Documentation](./process_framework.py)
- [Workflow Intelligence Metrics](./monitoring/metrics.py)
- [PDCA Metrics](./metrics/pdca_metrics.py)
- [Prometheus Client Library](https://github.com/prometheus/client_python)
