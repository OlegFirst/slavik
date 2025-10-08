# Unified Orchestrator

**Универсальный исполнитель задач для AI Office Team**

Port: `8090`

---

## Что это?

Unified Orchestrator - центральный исполнитель для AI Office. Получает задачи от **МиО Manager** и выполняет их через специализированные **Executors**.

### Роль в AI Office Team

```
МиО Manager (Координатор)
    ↓ формулирует задачи
Unified Orchestrator (Исполнитель)
    ↓ выполняет через
Executors (Инструменты)
```

---

## Возможности

### ✅ Infrastructure Tasks
- Deploy services (docker-compose)
- Restart services
- Stop services
- Health checks

### ✅ Event Tasks
- Fix event gaps
- Add publishers to code
- Add subscribers to code
- Create PRs with changes
- Rollback changes

### ⏳ Code Tasks (Future)
- Refactoring
- Code fixes

### ⏳ Database Tasks (Future)
- Migrations
- Rollbacks

---

## Quick Start

### 1. Start Orchestrator

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/orchestrator
uvicorn unified_orchestrator:app --host 0.0.0.0 --port 8090 --reload
```

### 2. Check Health

```bash
curl http://localhost:8090/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "unified_orchestrator",
  "version": "1.0.0"
}
```

### 3. Check Status

```bash
curl http://localhost:8090/api/v1/status
```

---

## API Reference

### Unified Task Execution

#### Execute Any Task
```
POST /api/v1/tasks/execute
```

**Body:**
```json
{
  "task_type": "infrastructure" | "event" | "code" | "database",
  "action": "...",
  "parameters": {...}
}
```

**Example - Event Fix:**
```bash
curl -X POST http://localhost:8090/api/v1/tasks/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "event",
    "action": "fix_gap",
    "parameters": {
      "event_name": "bcm.bia.started",
      "gap_type": "missing_subscriber",
      "severity": "critical",
      "service": "audit-service",
      "file_path": "platform-services/audit-service/main.py",
      "recommendation": "Add subscriber"
    }
  }'
```

**Example - Infrastructure Deploy:**
```bash
curl -X POST http://localhost:8090/api/v1/tasks/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "infrastructure",
    "action": "deploy",
    "parameters": {
      "layer": "full",
      "use_ai": true
    }
  }'
```

---

### Event Endpoints

#### Fix Single Event Gap
```
POST /api/v1/events/fix-gap
```

**Body:**
```json
{
  "event_name": "bcm.bia.started",
  "gap_type": "missing_subscriber",
  "severity": "critical",
  "service": "audit-service",
  "file_path": "platform-services/audit-service/main.py",
  "recommendation": "Add subscriber"
}
```

#### Fix Multiple Gaps
```
POST /api/v1/events/fix-gaps
```

**Body:** Array of gap objects

#### Add Publisher
```
POST /api/v1/events/add-publisher?service=...&event=...&file_path=...&method_name=...
```

#### Add Subscriber
```
POST /api/v1/events/add-subscriber?service=...&event=...&file_path=...
```

#### Create PR
```
POST /api/v1/events/create-pr?branch_name=...
```

#### Rollback Changes
```
POST /api/v1/events/rollback
```

---

### Infrastructure Endpoints

#### Deploy
```
POST /api/v1/deploy
```

**Body:**
```json
{
  "layer": "full",
  "use_ai_orchestration": true,
  "force_rebuild": false
}
```

#### Discover Services
```
POST /api/v1/discover
```

#### Generate Configs
```
POST /api/v1/generate
```

#### Build and Deploy
```
POST /api/v1/build-and-deploy
```

---

## Integration with МиО Manager

### Install Client

```python
from infrastructure.AI_office_infrastructure.mio_manager.integrations.orchestrator_client import OrchestratorClient

orchestrator = OrchestratorClient("http://localhost:8090")
```

### Fix Event Gap

```python
gap = {
    'event_name': 'bcm.bia.started',
    'gap_type': 'missing_subscriber',
    'severity': 'critical',
    'service': 'audit-service',
    'file_path': 'platform-services/audit-service/main.py',
    'recommendation': 'Add subscriber for audit logging'
}

result = await orchestrator.fix_event_gap(gap)
```

### Deploy Infrastructure

```python
result = await orchestrator.deploy_service(layer="full", use_ai=True)
```

### Unified Task Execution

```python
task = {
    'task_type': 'event',
    'action': 'fix_gap',
    'parameters': gap
}

result = await orchestrator.execute_task(task)
```

---

## Architecture

```
unified_orchestrator.py
    │
    ├─ execute_task()
    │   └─ Routes to appropriate executor
    │
    └─ Executors:
        ├─ InfrastructureExecutor ✅
        │   ├─ deploy()
        │   ├─ restart_service()
        │   └─ stop_service()
        │
        ├─ EventExecutor ✅
        │   ├─ add_publisher()
        │   ├─ add_subscriber()
        │   ├─ fix_event_gap()
        │   └─ create_pr()
        │
        ├─ CodeExecutor ⏳
        └─ DatabaseExecutor ⏳
```

---

## Executors

### InfrastructureExecutor

**File:** `executors/infrastructure_executor.py`

**Functions:**
- `deploy(layer, use_ai)` - Deploy via docker-compose
- `restart_service(service)` - Restart service
- `stop_service(service)` - Stop service
- `health_check(service)` - Check health

### EventExecutor

**File:** `executors/event_executor.py`

**Functions:**
- `add_publisher(service, event, file_path, method_name)` - Add publisher to code
- `add_subscriber(service, event, file_path)` - Add subscriber and handler
- `fix_event_gap(gap)` - Auto-fix gap
- `create_pr(branch_name)` - Create PR with changes
- `rollback_changes()` - Rollback changes

**Technologies:**
- Python AST for code parsing
- Code generation
- Git integration

---

## Examples

### Example 1: Fix Missing Subscriber

```python
from executors import EventExecutor

executor = EventExecutor("/Users/MD/AI-Platform-ISO")

gap = EventGap(
    event_name="bcm.bia.started",
    gap_type="missing_subscriber",
    severity="critical",
    service="audit-service",
    file_path="platform-services/audit-service/main.py",
    recommendation="Add subscriber"
)

result = await executor.fix_event_gap(gap)
# Result: {'success': True, 'handler_name': 'handle_bcm_bia_started', ...}
```

### Example 2: Add Publisher

```python
result = await executor.add_publisher(
    service="bia-service",
    event="bcm.bia.started",
    file_path="platform-services/bia-service/main.py",
    method_name="execute_bia",
    position="end"
)

# Adds to code:
# await self.eventbus.publish(
#     'bcm.bia.started',
#     {'timestamp': datetime.utcnow().isoformat(), ...},
#     tenant_id=tenant_id
# )
```

### Example 3: Create PR

```python
# After making changes
pr_result = await executor.create_pr("fix/event-gaps-20251007")
# Result: {'success': True, 'pr_url': '...', ...}
```

---

## Documentation

### Complete Documentation
- [UNIFIED_ARCHITECTURE_COMPLETE.md](./UNIFIED_ARCHITECTURE_COMPLETE.md) - Полная техническая документация

### Project Documentation
- [AI_OFFICE_ROLES_ANALYSIS.md](../../../doc-project/AI_OFFICE_ROLES_ANALYSIS.md) - Анализ ролей
- [UNIFIED_ORCHESTRATOR_SUMMARY.md](../../../doc-project/UNIFIED_ORCHESTRATOR_SUMMARY.md) - Краткое резюме
- [ARCHITECTURE_VISUAL.md](../../../doc-project/ARCHITECTURE_VISUAL.md) - Визуальные диаграммы

### Root Documentation
- [UNIFIED_ORCHESTRATOR_IMPLEMENTATION.md](../../../UNIFIED_ORCHESTRATOR_IMPLEMENTATION.md) - Итоговая реализация
- [CHANGES_SUMMARY_2025-10-07.md](../../../CHANGES_SUMMARY_2025-10-07.md) - Изменения

---

## Development

### Adding New Executor

1. Create `executors/my_executor.py`:
```python
class MyExecutor:
    async def do_something(self, params):
        # Implementation
        pass
```

2. Add to `executors/__init__.py`:
```python
from .my_executor import MyExecutor
```

3. Add to `unified_orchestrator.py`:
```python
self.my_executor = MyExecutor(str(project_root))

async def _execute_my_task(self, action, parameters):
    if action == 'do_something':
        return await self.my_executor.do_something(parameters)
```

4. Update `execute_task()`:
```python
elif task_type == 'my_type':
    return await self._execute_my_task(action, parameters)
```

---

## Testing

### Unit Tests
```bash
pytest executors/test_event_executor.py
pytest executors/test_infrastructure_executor.py
```

### Integration Tests
```bash
pytest tests/test_orchestrator_integration.py
```

### Manual Testing
```bash
# Start orchestrator
uvicorn unified_orchestrator:app --reload

# Test in another terminal
curl -X POST http://localhost:8090/api/v1/events/fix-gap \
  -H "Content-Type: application/json" \
  -d @test_gap.json
```

---

## Troubleshooting

### Issue: Orchestrator не запускается
**Solution:** Проверьте зависимости:
```bash
pip install fastapi uvicorn httpx pydantic
```

### Issue: EventExecutor не находит файлы
**Solution:** Проверьте workspace_root:
```python
EventExecutor("/Users/MD/AI-Platform-ISO")  # Absolute path
```

### Issue: МиО Manager не может подключиться
**Solution:** Проверьте URL и порт:
```python
OrchestratorClient("http://localhost:8090")  # Correct port
```

---

## FAQ

### Q: Чем отличается от старого Orchestrator?
**A:** Unified Orchestrator поддерживает множество типов задач (infrastructure, events, code, database), не только deploy.

### Q: Как добавить новый тип задач?
**A:** Создайте новый Executor в `executors/` и добавьте routing в `execute_task()`.

### Q: Можно ли использовать без МиО Manager?
**A:** Да, можно вызывать API напрямую через curl или Python requests.

### Q: Что делать если PR creation не работает?
**A:** Реализуйте GitHub integration в `event_executor.py` методах `_create_commit()` и `_create_github_pr()`.

---

## Status

- ✅ Infrastructure Executor
- ✅ Event Executor
- ✅ Unified API
- ✅ МиО Manager integration
- ⏳ Code Executor (TODO)
- ⏳ Database Executor (TODO)

---

## License

Internal AI Platform ISO

## Contact

See project documentation for details.
