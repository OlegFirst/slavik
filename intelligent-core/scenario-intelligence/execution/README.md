# Scenario Execution Engine

The Scenario Execution Engine executes scenarios (L1-L4), validates results, and generates comprehensive reports.

## 🎯 Overview

The execution engine consists of four main components:

1. **ScenarioExecutor** - Executes individual scenarios and steps
2. **ExecutionValidator** - Validates execution results against expected outcomes
3. **ExecutionReporter** - Generates reports (JSON, HTML)
4. **ExecutionEngine** - Main orchestrator that coordinates everything

## 📁 File Structure

```
execution/
├── __init__.py                 # Package exports
├── executor.py                 # ScenarioExecutor implementation
├── validator.py                # ExecutionValidator implementation
├── reporter.py                 # ExecutionReporter implementation
├── execution_engine.py         # ExecutionEngine orchestrator
├── test_execution.py          # Comprehensive tests
└── README.md                   # This file
```

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
from execution.execution_engine import ExecutionEngine

async def main():
    # Create engine (without database)
    engine = ExecutionEngine(storage=None, save_to_db=False)

    # Execute a scenario
    scenario = {
        'meta': {'id': 'my-scenario', 'level': 1, 'type': 'functional'},
        'execution': {
            'steps': [
                {'id': 'step1', 'action': 'mock_action', 'params': {'test': True}}
            ]
        }
    }

    report = await engine.execute_scenario_direct(scenario)
    print(f"Status: {report.summary['overall_status']}")
    print(f"Success Rate: {report.summary['success_rate']:.1%}")

asyncio.run(main())
```

### With Database Integration

```python
from execution.execution_engine import ExecutionEngine
from storage.postgres_storage import PostgresScenarioStorage

async def main():
    # Initialize storage
    storage = PostgresScenarioStorage(connection_string="postgresql://...")
    await storage.initialize()

    # Create engine with database
    engine = ExecutionEngine(storage=storage, save_to_db=True)

    # Execute scenario by ID
    report = await engine.execute_scenario('l1-service-vault')

    # View execution history
    history = await engine.get_execution_history('l1-service-vault')
    print(f"Previous executions: {len(history)}")

    await storage.close()
```

## 📦 Components

### 1. ScenarioExecutor

Executes individual scenarios and their steps.

**Features:**
- Sequential step execution
- HTTP request support (GET, POST, PUT, DELETE)
- Mock actions for testing
- Variable substitution (`{{variable}}`)
- Timing measurements
- Error handling

**Example:**

```python
from execution.executor import ScenarioExecutor

async with ScenarioExecutor() as executor:
    result = await executor.execute(scenario)

    print(f"Status: {result.status}")
    print(f"Duration: {result.duration_seconds}s")
    print(f"Steps: {len(result.steps)}")
```

**Supported Actions:**
- `http_request` - Make HTTP requests
- `check_availability` - Health check endpoints
- `mock_action` - Simulated actions for testing
- Any HTTP method: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`

### 2. ExecutionValidator

Validates execution results against expected outcomes.

**Validation Checks:**
- Overall execution status
- Individual step results
- Timing requirements
- Compliance requirements
- Custom validation rules

**Example:**

```python
from execution.validator import ExecutionValidator

validator = ExecutionValidator()
validation_report = validator.validate_result(execution_result, scenario)

print(f"Valid: {validation_report.is_valid}")
print(f"Status: {validation_report.validation_status}")
print(f"Issues: {len(validation_report.issues)}")
```

**Validation Levels:**
- `error` - Critical failures
- `warning` - Issues that don't prevent execution
- `info` - Informational messages

### 3. ExecutionReporter

Generates comprehensive reports from execution results.

**Report Formats:**
- JSON (programmatic access)
- HTML (human-readable)

**Example:**

```python
from execution.reporter import ExecutionReporter

reporter = ExecutionReporter()
report = reporter.generate_report(results=[execution_result])

# Export to JSON
json_str = reporter.export_to_json(report)

# Export to HTML
html_str = reporter.export_to_html(report)

# Save to file
reporter.save_report(report, 'report.html', format='html')
```

**Report Contents:**
- Execution summary (success rate, timing, steps)
- Individual execution details
- Validation results
- Issue tracking
- Statistics and metrics

### 4. ExecutionEngine

Main orchestrator that coordinates all components.

**Features:**
- Single scenario execution
- Batch execution (multiple scenarios)
- Workflow execution (L4 scenarios)
- Database persistence
- Execution history
- Statistics

**Example:**

```python
from execution.execution_engine import ExecutionEngine

engine = ExecutionEngine(
    storage=storage,
    save_to_db=True,
    validate_results=True
)

# Execute single scenario
report = await engine.execute_scenario('scenario-id')

# Execute batch
report = await engine.execute_batch(['id1', 'id2', 'id3'])

# Execute workflow
report = await engine.execute_workflow(l4_workflow_scenario)
```

## 🧪 Testing

Run comprehensive tests:

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence

# Run all tests
python3 execution/test_execution.py

# Tests include:
# 1. Simple mock scenario execution
# 2. HTTP request scenario
# 3. Database integration
# 4. Batch execution
# 5. Real L1 scenario
# 6. Report export (JSON/HTML)
```

## 📊 Execution Flow

```
1. Load Scenario (from database or direct)
   ↓
2. ScenarioExecutor.execute()
   - Parse steps
   - Execute each step sequentially
   - Measure timing
   - Collect results
   ↓
3. ExecutionValidator.validate_result()
   - Check status
   - Validate steps
   - Check timing
   - Check compliance
   ↓
4. ExecutionReporter.generate_report()
   - Aggregate results
   - Generate summary
   - Create report
   ↓
5. Save to Database (optional)
   - Store execution history
   - Update statistics
   ↓
6. Return ExecutionReport
```

## 🎯 Use Cases

### 1. Execute L1 Service Scenario

```python
# Health check for a service
engine = ExecutionEngine(storage=storage)
report = await engine.execute_scenario('l1-service-vault')

if report.summary['overall_status'] == 'success':
    print("✅ Service is healthy")
else:
    print("❌ Service has issues")
```

### 2. Batch Testing

```python
# Test all L1 services
storage = PostgresScenarioStorage(DATABASE_URL)
await storage.initialize()

# Find all L1 scenarios
scenarios = await storage.find_scenarios(level=1, type='service')
scenario_ids = [s['meta']['id'] for s in scenarios]

# Execute batch
engine = ExecutionEngine(storage=storage)
report = await engine.execute_batch(scenario_ids)

print(f"Success Rate: {report.summary['success_rate']:.1%}")
print(f"Passed: {report.summary['successful']}/{report.summary['total_executions']}")
```

### 3. CI/CD Integration

```python
async def run_scenario_tests():
    """Run scenarios as part of CI/CD pipeline"""
    engine = ExecutionEngine(storage=storage, save_to_db=True)

    # Execute critical scenarios
    critical_scenarios = ['l1-service-vault', 'l1-service-auth', 'l1-service-api-gateway']
    report = await engine.execute_batch(critical_scenarios)

    # Fail build if any critical scenario fails
    if report.summary['failed'] > 0:
        print("❌ Critical scenarios failed")
        sys.exit(1)

    print("✅ All critical scenarios passed")
    return True
```

### 4. Generate Reports

```python
engine = ExecutionEngine(storage=storage)
report = await engine.execute_scenario('my-scenario')

reporter = ExecutionReporter()

# Save HTML report for human review
reporter.save_report(report, '/reports/execution_report.html', format='html')

# Save JSON for programmatic access
reporter.save_report(report, '/reports/execution_report.json', format='json')
```

## 📈 Database Schema

The execution engine uses the `scenario_intelligence.scenario_executions` table:

```sql
CREATE TABLE scenario_intelligence.scenario_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL, -- 'running', 'success', 'failed', 'timeout'
    result JSONB,
    error_message TEXT,
    organization_id UUID
);
```

**Note:** If the table doesn't exist in your database, the engine will still work but won't save execution history. To enable persistence, apply the migration:

```bash
# Apply the schema migration
psql $DATABASE_URL -f /infrastructure/database/postgresql/migrations_source/050_scenario_intelligence_schema.sql
```

## 🔧 Configuration

### Environment Variables

```bash
# Database connection (optional)
export DATABASE_URL="postgresql://user:pass@host:port/db"

# HTTP timeout for requests (default: 30s)
export EXECUTION_HTTP_TIMEOUT=60
```

### ExecutionEngine Options

```python
ExecutionEngine(
    storage=storage,              # PostgresScenarioStorage instance
    temporal_client=None,         # Temporal client (future feature)
    save_to_db=True,             # Save execution history
    validate_results=True         # Validate results after execution
)
```

## 📝 Step Configuration

### HTTP Request Step

```yaml
steps:
  - id: health_check
    action: http_request
    method: GET
    endpoint: http://localhost:8000/health
    expect:
      http_status: 200
      response_time_max: 2s
```

### Mock Action Step

```yaml
steps:
  - id: test_step
    action: mock_action
    params:
      test: true
      value: 42
    expect:
      status: 200
```

### Variable Substitution

```yaml
steps:
  - id: step1
    action: create_user
    params:
      name: "Test User"

  - id: step2
    action: get_user
    params:
      user_id: "{{steps.step1.user_id}}"  # Use result from step1
```

## 🎨 Report Examples

### JSON Report Structure

```json
{
  "report_id": "report-20251014-123456",
  "report_type": "single",
  "generated_at": "2025-10-14T12:34:56",
  "executions": [{
    "scenario_id": "l1-service-vault",
    "status": "success",
    "duration_seconds": 2.5,
    "steps": [...],
    "summary": {
      "total_steps": 5,
      "successful_steps": 5,
      "failed_steps": 0
    }
  }],
  "validations": [{
    "is_valid": true,
    "validation_status": "passed",
    "issues": []
  }],
  "summary": {
    "total_executions": 1,
    "successful": 1,
    "failed": 0,
    "success_rate": 1.0,
    "timing": {
      "avg_duration": 2.5
    }
  }
}
```

### HTML Report

The HTML report includes:
- Visual status badges (success/failed/partial)
- Summary metrics dashboard
- Detailed execution table
- Validation issues
- Timing charts
- Responsive design

View example: `/tmp/test_report.html` (generated by tests)

## ⚡ Performance

### Typical Execution Times

- Mock scenario (2 steps): ~0.2s
- HTTP health check: ~0.5-2s
- L1 service scenario: ~2-5s
- Batch execution (10 scenarios): ~15-30s

### Optimization Tips

1. **Parallel Execution**: Use `asyncio.gather()` for independent scenarios
2. **Caching**: Cache scenario definitions to avoid repeated DB queries
3. **Timeout Configuration**: Adjust HTTP timeout based on service characteristics
4. **Database Pooling**: Reuse connection pools for better performance

## 🐛 Troubleshooting

### Issue: "relation scenario_intelligence.scenario_executions does not exist"

**Solution:** Apply the database migration:
```bash
psql $DATABASE_URL -f infrastructure/database/postgresql/migrations_source/050_scenario_intelligence_schema.sql
```

Or disable database persistence:
```python
engine = ExecutionEngine(storage=None, save_to_db=False)
```

### Issue: HTTP Request Timeout

**Solution:** Increase timeout or check service availability:
```python
executor = ScenarioExecutor(http_timeout=60)  # 60 seconds
```

### Issue: Validation Failures

**Solution:** Check expectations in scenario definition:
```yaml
expect:
  http_status: 200  # Must match actual response
  response_time_max: 3s  # Increase if service is slow
```

## 🚀 Future Enhancements

### MVP (Current Implementation)
- ✅ Basic scenario execution
- ✅ HTTP request support
- ✅ Result validation
- ✅ JSON/HTML reports
- ✅ Database persistence
- ✅ Batch execution

### Future Features (Post-MVP)
- ⏳ Temporal workflow integration
- ⏳ Parallel step execution
- ⏳ Advanced retry logic
- ⏳ Real-time progress updates
- ⏳ Grafana dashboard integration
- ⏳ EventBus notifications
- ⏳ Metrics collection (Prometheus)

## 📚 API Reference

### ExecutionEngine

```python
class ExecutionEngine:
    async def execute_scenario(scenario_id: str, context: Dict = None) -> ExecutionReport
    async def execute_scenario_direct(scenario: Dict, context: Dict = None) -> ExecutionReport
    async def execute_batch(scenario_ids: List[str], context: Dict = None) -> ExecutionReport
    async def execute_workflow(workflow_scenario: Dict, context: Dict = None) -> ExecutionReport
    async def get_execution_history(scenario_id: str, limit: int = 10) -> List[Dict]
    async def get_statistics() -> Dict
```

### ScenarioExecutor

```python
class ScenarioExecutor:
    async def execute(scenario: Dict, context: Dict = None) -> ExecutionResult
    async def execute_step(step: Dict, context: Dict) -> StepResult
```

### ExecutionValidator

```python
class ExecutionValidator:
    def validate_result(result: ExecutionResult, scenario: Dict) -> ValidationReport
    def validate_step(step_result: StepResult, expected: Dict) -> bool
```

### ExecutionReporter

```python
class ExecutionReporter:
    def generate_report(results: List[ExecutionResult], ...) -> ExecutionReport
    def export_to_json(report: ExecutionReport, pretty: bool = True) -> str
    def export_to_html(report: ExecutionReport) -> str
    def save_report(report: ExecutionReport, filepath: str, format: str = 'json')
```

## 📞 Support

For issues or questions:
1. Check this README
2. Review test cases in `test_execution.py`
3. See parent directory documentation: `../README.md`
4. Check scenario generation docs: `../GENERATORS_COMPLETE.md`

---

**Status:** ✅ MVP Complete
**Version:** 1.0.0
**Last Updated:** 2025-10-14
