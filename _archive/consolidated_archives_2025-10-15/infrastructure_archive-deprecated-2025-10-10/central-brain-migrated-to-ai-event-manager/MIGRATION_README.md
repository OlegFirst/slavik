# Central Brain - MIGRATED ✅

**Дата миграции**: 2025-10-10
**Причина**: Интеграция в единую систему мониторинга

## Новое расположение

**Модуль**: `/infrastructure/AI-office-infrastructure/ai-event-manager/monitoring/infrastructure_state.py`

## Что изменилось

### До миграции:
- **central-brain** был standalone CLI tool
- Использовал simple if-else rules (не AI!)
- НЕ координировался с системой
- НЕ публиковал в EventBus
- Работал изолированно

### После миграции:
- **InfrastructureStateMonitor** интегрирован в **ai-event-manager**
- Публикует состояние в EventBus каждые 60 секунд
- Координируется с:
  - balancer-service (infrastructure-aware balancing)
  - mio-manager (resource tracking)
  - orchestrator (deployment decisions)
  - все остальные сервисы через EventBus

## Архитектура

### Старая архитектура:
```
central-brain (standalone)
     │
     ▼
  (никуда)
```

### Новая архитектура:
```
┌────────────────────────────────────┐
│   ai-event-manager (HUB)           │
│   ├── Infrastructure Monitor ✨    │
│   │   ├── Project Manager ✅       │
│   │   ├── MIO Manager ✅           │
│   │   ├── Service Discovery ✅     │
│   │   └── Prometheus ✅            │
│   └── EventBus Publishing ✅       │
└─────────────┬──────────────────────┘
              │
              │ Events:
              │ - platform.infrastructure.state_updated
              │ - platform.infrastructure.emergency
              │ - platform.infrastructure.strategy_recommended
              ▼
       ┌─────────────┐
       │  EventBus   │
       └──────┬──────┘
              │
      ┌───────┴───────┐
      │               │
      ▼               ▼
┌────────────┐  ┌────────────┐
│balancer-   │  │mio-        │
│service ✅  │  │manager ✅  │
└────────────┘  └────────────┘
```

## EventBus Events (NEW!)

### Published:
- `platform.infrastructure.state_updated` - Every 60s
- `platform.infrastructure.emergency` - Critical issues
- `platform.infrastructure.strategy_recommended` - Scaling strategy
- `platform.infrastructure.resource_deficit` - Low resources

### State Schema:
```python
{
  "timestamp": "2025-10-10T12:00:00",
  "ports_available": 50,
  "ports_used": 30,
  "prometheus_available": true,
  "grafana_available": true,
  "postgres_available": true,
  "redis_available": true,
  "services_with_metrics": 18,
  "services_with_db": 20,
  "total_services": 24,
  "healthy_services": 22,
  "unhealthy_services": 2,
  "cpu_usage": 0.45,
  "memory_usage": 0.62,
  "disk_usage": 0.35,
  "monitoring_coverage": 0.75,
  "database_coverage": 0.83,
  "health_check_coverage": 0.92
}
```

## API Endpoints (NEW!)

В **ai-event-manager** (http://localhost:8055):

- `GET /infrastructure/state` - Current infrastructure state
- `GET /infrastructure/resources` - Available resources
- `GET /infrastructure/strategy` - Scaling strategy recommendation
- `POST /infrastructure/deployment-check` - Can deploy service?
- `GET /infrastructure/history` - State history

## Восстановление (если нужно)

Если нужно восстановить старый standalone central-brain:

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/_archive-deprecated-2025-10-10
cp -r central-brain-migrated-to-ai-event-manager/ ../central-brain
```

Но **рекомендуется** использовать новую интеграцию через ai-event-manager!

## Документация

См. также:
- `/doc-project/SESSION_STATE_INTEGRATION_CENTRAL_BRAIN.md` - Детальный план интеграции
- `/doc-project/INTEGRATION_PLAN_CENTRAL_BRAIN_BALANCER.md` - Полный план
- `/doc-project/CENTRAL_BRAIN_BALANCER_ANALYSIS.md` - Первичный анализ
- `/infrastructure/AI-office-infrastructure/ai-event-manager/README.md` - Обновленная документация

## Преимущества миграции

✅ **Единая система мониторинга** - все данные в одном месте
✅ **EventBus coordination** - все сервисы получают infrastructure state
✅ **Infrastructure-aware balancing** - balancer-service учитывает capacity
✅ **Strategic decisions централизованы** - ai-event-manager = единый мозг
✅ **API endpoints** - легкий доступ к состоянию инфраструктуры
✅ **Исторические данные** - state history для анализа трендов

---

**Статус**: ✅ Миграция завершена успешно
**Дата**: 2025-10-10
**Автор**: Claude (Integration Session)
