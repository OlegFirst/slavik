# Архивировано: 2025-10-11

**Причина**: Функции перенесены в DevOps Agent

---

## Что было

`/infrastructure/tools/project-manager/` - Platform compliance checker (CLI script)

**Compliance checks (6 priorities)**:
1. ✅ Priority 1: Port conflicts
2. ✅ Priority 2: Metrics integration (Prometheus/Grafana)
3. ✅ Priority 3: Database connections (PostgreSQL/Redis)
4. ✅ Priority 4: KPI registration
5. ✅ Priority 5: EventBus events
6. ✅ Priority 6: Orchestrator control

---

## Куда переехало

**Compliance checks** теперь в DevOps Agent:

```
/infrastructure/AI-office-infrastructure/devops-agent/
├── tools/
│   ├── compliance-checks/          # ⭐ Все 6 приоритетов
│   │   ├── priority_1_port_conflicts.py
│   │   ├── priority_2_metrics_integration.py
│   │   ├── priority_3_database_connections.py
│   │   ├── priority_4_kpi_registration.py
│   │   ├── priority_5_eventbus_events.py
│   │   └── priority_6_orchestrator_control.py
│   │
│   ├── compliance_runner.py         # Unified interface
│   └── __init__.py
│
└── agent.py                          # DevOps Agent (интегрирует toolkit)
    └── async def run_compliance_checks()
```

---

## Как использовать

**Раньше:**
```bash
python /infrastructure/tools/project-manager/run_compliance_checks.py
```

**Теперь:**
```python
from devops_agent.agent import DevOpsAgent

agent = DevOpsAgent(project_root="/Users/MD/AI-Platform-ISO")
await agent.initialize()

# Run compliance checks
results = await agent.run_compliance_checks()

# Or full infrastructure scan (includes compliance)
results = await agent.scan_infrastructure(scan_type="full")
```

---

## MIO Manager Integration

**Раньше:**
```python
# mio-manager/monitoring/infrastructure_state.py
from run_compliance_checks import ComplianceCheckRunner
runner = ComplianceCheckRunner()
state = runner.export_state_for_central_brain()
```

**Теперь:**
```python
# mio-manager/monitoring/infrastructure_state.py
from devops_agent.tools import ComplianceRunner
runner = ComplianceRunner()
state = runner.export_state_for_mio_manager()
```

---

## Преимущества нового подхода

1. ✅ **Unified DevOps Agent**: Все infrastructure checks в одном месте
2. ✅ **AI-powered**: DevOps Agent добавляет AI analysis к compliance checks
3. ✅ **EventBus Integration**: Real-time publishing результатов
4. ✅ **Auto-remediation**: DevOps Agent может исправлять проблемы
5. ✅ **Минимизация элементов**: Один сервис вместо двух инструментов

---

## Восстановление

Если нужно восстановить старую версию:

```bash
cp -r /Users/MD/AI-Platform-ISO/_archive/tools-cleanup-2025-10-11/project-manager \
      /Users/MD/AI-Platform-ISO/infrastructure/tools/
```

**НО**: Рекомендуется использовать DevOps Agent вместо этого.

---

**Архивировано**: 2025-10-11
**Безопасно удалить после**: 2025-11-10 (через 30 дней)
**Статус**: Функционал полностью перенесен в DevOps Agent ✅
