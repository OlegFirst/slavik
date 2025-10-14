# Scenario Execution Engine - Quick Start

## 🚀 5-Minute Guide

### 1. Basic Execution (No Database)

```python
import asyncio
from execution.execution_engine import ExecutionEngine

async def main():
    # Create engine
    engine = ExecutionEngine(storage=None, save_to_db=False)

    # Define scenario
    scenario = {
        'meta': {'id': 'my-test', 'level': 1, 'type': 'functional'},
        'execution': {
            'steps': [
                {
                    'id': 'step1',
                    'action': 'http_request',
                    'method': 'GET',
                    'endpoint': 'https://httpbin.org/status/200',
                    'expect': {'http_status': 200}
                }
            ]
        }
    }

    # Execute
    report = await engine.execute_scenario_direct(scenario)

    # View results
    print(f"Status: {report.summary['overall_status']}")
    print(f"Success Rate: {report.summary['success_rate']:.1%}")

asyncio.run(main())
```

### 2. With Database

```python
import asyncio
from execution.execution_engine import ExecutionEngine
from storage.postgres_storage import PostgresScenarioStorage

async def main():
    # Setup storage
    storage = PostgresScenarioStorage("postgresql://user:pass@host/db")
    await storage.initialize()

    # Create engine
    engine = ExecutionEngine(storage=storage, save_to_db=True)

    # Execute by ID
    report = await engine.execute_scenario('l1-service-vault')

    print(f"Status: {report.summary['overall_status']}")

    await storage.close()

asyncio.run(main())
```

### 3. Batch Execution

```python
async def batch():
    engine = ExecutionEngine(storage=storage)

    # Execute multiple scenarios
    report = await engine.execute_batch([
        'l1-service-vault',
        'l1-service-auth',
        'l1-service-gateway'
    ])

    print(f"Tested: {report.summary['total_executions']}")
    print(f"Success: {report.summary['successful']}")
    print(f"Failed: {report.summary['failed']}")
```

### 4. Generate HTML Report

```python
from execution.reporter import ExecutionReporter

reporter = ExecutionReporter()
html = reporter.export_to_html(report)

with open('report.html', 'w') as f:
    f.write(html)

print("Report saved to report.html")
```

## 📋 Common Scenarios

### Health Check

```yaml
steps:
  - id: health
    action: http_request
    method: GET
    endpoint: http://localhost:8000/health
    expect:
      http_status: 200
      response_time_max: 2s
```

### API Test

```yaml
steps:
  - id: create_user
    action: http_request
    method: POST
    endpoint: http://api/users
    params:
      body:
        name: "Test User"
        email: "test@example.com"
    expect:
      http_status: 201

  - id: get_user
    action: http_request
    method: GET
    endpoint: http://api/users/{{steps.create_user.id}}
    expect:
      http_status: 200
```

## 🧪 Run Tests

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence
python3 execution/test_execution.py
```

## 📚 More Info

- **Full Guide:** [README.md](./README.md)
- **Implementation:** [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
- **Tests:** [test_execution.py](./test_execution.py)

---

**Ready to execute!** 🎉
