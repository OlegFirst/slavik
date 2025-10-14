# Planning Service - EventBus Quick Reference

## Published Events

### 1. planning.strategy.created
**When:** После создания новой стратегии
**Method:** `StrategyService.create_strategy()`
**Line:** 66-82 в `services/business_logic.py`

```json
{
  "strategy_id": "uuid",
  "tenant_id": "string",
  "strategy_number": "STRAT-YYYY-XXXXXX",
  "name": "string",
  "strategy_type": "backup_restore|alternate_site|...",
  "strategy_phase": "response|recovery|...",
  "status": "draft",
  "created_by": "user_id",
  "timestamp": "2025-10-03T10:30:00.000Z"
}
```

---

### 2. planning.strategy.approved
**When:** После утверждения стратегии
**Method:** `StrategyService.approve_strategy()`
**Line:** 252-270 в `services/business_logic.py`

```json
{
  "strategy_id": "uuid",
  "tenant_id": "string",
  "strategy_number": "STRAT-YYYY-XXXXXX",
  "name": "string",
  "strategy_type": "backup_restore|alternate_site|...",
  "status": "approved",
  "approved_by": "user_id",
  "approval_notes": "string",
  "approved_at": "2025-10-03T10:30:00.000Z",
  "timestamp": "2025-10-03T10:30:00.000Z"
}
```

---

### 3. planning.cost_benefit.completed
**When:** После завершения анализа затрат-выгод
**Method:** `StrategyService.calculate_cost_benefit()`
**Line:** 206-227 в `services/business_logic.py`

```json
{
  "strategy_id": "uuid",
  "tenant_id": "string",
  "strategy_number": "STRAT-YYYY-XXXXXX",
  "total_cost": 75000.0,
  "total_benefits": 180000.0,
  "cost_benefit_ratio": 2.4,
  "roi_percentage": 140.0,
  "payback_period_months": 15.0,
  "net_present_value": 95000.0,
  "recommendation": "proceed|review|reject",
  "confidence_level": "high|medium|low",
  "timestamp": "2025-10-03T10:30:00.000Z"
}
```

---

## Error Handling

Все события обрабатываются с graceful degradation:

```python
try:
    await publish_event(topic="...", data={...})
    logger.info("Published event...")
except Exception as e:
    logger.warning(f"Failed to publish event: {e}")
    # Операция продолжается, бизнес-логика НЕ прерывается
```

---

## Configuration

EventBus URL настраивается в `config.py`:

```python
EVENTBUS_URL: str = "http://localhost:8001"  # По умолчанию
```

Или через environment variables:
```bash
export EVENTBUS_URL=http://eventbus:8001
```

---

## Testing

### Unit Tests (Mock EventBus):
```bash
python test_eventbus_integration.py
```

### Integration Tests (Real EventBus):
```bash
# 1. Запустить EventBus
docker-compose up eventbus

# 2. Запустить Planning Service
uvicorn main:app --host 0.0.0.0 --port 8011

# 3. Создать стратегию через API
curl -X POST http://localhost:8011/api/v1/strategies \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"test","name":"Test Strategy",...}'

# 4. Проверить событие в EventBus
curl http://localhost:8001/events/topics
```

---

## Monitoring

### Logs to Watch:
```bash
# Успешная публикация:
INFO: Published planning.strategy.created event for strategy STRAT-2025-ABC123

# Ошибка публикации:
WARNING: Failed to publish planning.strategy.created event: Connection refused
```

### Health Check:
```bash
# Проверить доступность EventBus
curl http://localhost:8001/health
```

---

## Common Issues

### Issue 1: EventBus недоступен
**Симптомы:** WARNING в логах "Failed to publish event"
**Решение:** Проверить, что EventBus запущен и доступен по `EVENTBUS_URL`
**Влияние:** Минимальное - бизнес-логика продолжает работать

### Issue 2: Timeout при публикации
**Симптомы:** WARNING "Failed to publish event: timeout"
**Решение:** Увеличить timeout в `events/publishers.py` (по умолчанию 5 сек)
**Влияние:** Минимальное - операция завершится без события

### Issue 3: События не появляются в других сервисах
**Симптомы:** События публикуются, но подписчики не получают
**Решение:** Проверить подписки в других сервисах
**Диагностика:** `curl http://localhost:8001/events/subscriptions`

---

## Integration Points

### Upstream (Planning Service публикует):
- ✅ `planning.strategy.created`
- ✅ `planning.strategy.approved`
- ✅ `planning.cost_benefit.completed`

### Downstream (потенциальные подписчики):
- BIA Service
- Risk Service
- Audit Service
- Notification Service
- Finance Service
- Implementation Service
- Governance Service
- Dashboard Service

---

## Code Examples

### Пример 1: Добавление нового события
```python
# В services/business_logic.py

async def new_method(self, ...):
    # Бизнес-логика
    result = await self.repo.some_operation(...)

    # Публикация события
    try:
        await publish_event(
            topic="planning.new_event",
            data={
                "strategy_id": str(result.id),
                "tenant_id": result.tenant_id,
                "timestamp": datetime.now().isoformat(),
                # ... другие поля
            }
        )
        logger.info(f"Published planning.new_event for {result.id}")
    except Exception as e:
        logger.warning(f"Failed to publish planning.new_event: {e}")

    return result
```

### Пример 2: Подписка на событие (в другом сервисе)
```python
# В другом сервисе
from eventbus_client import subscribe

@subscribe(topic="planning.strategy.approved")
async def on_strategy_approved(event_data: dict):
    strategy_id = event_data["strategy_id"]
    tenant_id = event_data["tenant_id"]

    # Обработка события
    await update_related_processes(strategy_id)
```

---

## Files Modified

1. **services/business_logic.py**
   - Строка 9: Добавлен `import logging`
   - Строка 23: Добавлен `from ..events.publishers import publish_event`
   - Строка 25: Добавлен `logger = logging.getLogger(__name__)`
   - Строки 64-82: Событие в `create_strategy()`
   - Строки 206-227: Событие в `calculate_cost_benefit()`
   - Строки 251-270: Событие в `approve_strategy()`

## Files Created

1. **test_eventbus_integration.py** - тестовый скрипт
2. **EVENTBUS_INTEGRATION_REPORT.md** - полная документация
3. **EVENTBUS_QUICK_REFERENCE.md** - быстрый справочник (этот файл)

---

## Performance Impact

- **Latency:** +5-50ms на операцию (зависит от сети EventBus)
- **Timeout:** 5 секунд (настраивается)
- **Failure Mode:** Graceful degradation (логируется warning, операция продолжается)
- **Resource Usage:** Минимальное (async HTTP client)

---

## Security Notes

- События публикуются только после успешного выполнения операции
- События содержат только бизнес-данные (без credentials)
- EventBus должен быть в защищенной сети
- Рекомендуется использовать HTTPS для production

---

**Last Updated:** 2025-10-03
**Version:** 1.0
**Author:** Integration Team
