# EventBus Integration - Plans Service

## Overview

Plans Service теперь публикует события в EventBus при ключевых операциях с планами непрерывности бизнеса.

## Добавленные события

### 1. `plans.plan.created`

**Триггер:** Создание нового плана непрерывности бизнеса

**Payload:**
```json
{
  "plan_id": 123,
  "tenant_id": "tenant-123",
  "plan_code": "BC-001",
  "plan_name": "IT Systems Recovery Plan",
  "plan_type": "disaster_recovery",
  "priority": "critical",
  "status": "draft",
  "version": "1.0",
  "plan_owner_user_id": "user-456",
  "team_leader_user_id": "user-789",
  "rto_hours": 4,
  "rpo_hours": 1,
  "mtpd_hours": 24,
  "based_on_bia_id": 10,
  "based_on_risk_ids": [5, 7, 12],
  "created_by": "user-456"
}
```

**Использование:**
- Уведомление заинтересованных сторон о новом плане
- Инициация процесса review
- Синхронизация с внешними системами

---

### 2. `plans.plan.approved`

**Триггер:** Утверждение плана (переход из UNDER_REVIEW → APPROVED)

**Payload:**
```json
{
  "plan_id": 123,
  "tenant_id": "tenant-123",
  "plan_code": "BC-001",
  "plan_name": "IT Systems Recovery Plan",
  "plan_type": "disaster_recovery",
  "priority": "critical",
  "status": "approved",
  "version": "1.0",
  "approved_by_user_id": "user-admin",
  "approval_date": "2025-10-03T10:30:00",
  "approval_notes": "Approved with minor recommendations",
  "plan_owner_user_id": "user-456",
  "rto_hours": 4,
  "rpo_hours": 1
}
```

**Использование:**
- Уведомление владельца плана и команды
- Инициация процесса активации
- Обновление статуса в системе управления документами
- Интеграция с системой соответствия (Compliance Service)

---

### 3. `plans.plan.activated`

**Триггер:** Активация плана (переход из APPROVED → ACTIVE)

**Payload:**
```json
{
  "plan_id": 123,
  "tenant_id": "tenant-123",
  "plan_code": "BC-001",
  "plan_name": "IT Systems Recovery Plan",
  "plan_type": "disaster_recovery",
  "priority": "critical",
  "status": "active",
  "version": "1.0",
  "activated_by_user_id": "user-admin",
  "plan_owner_user_id": "user-456",
  "team_leader_user_id": "user-789",
  "rto_hours": 4,
  "rpo_hours": 1,
  "mtpd_hours": 24
}
```

**Использование:**
- Уведомление всех членов команды восстановления
- Активация процедур мониторинга
- Обновление дашбордов и метрик
- Интеграция с Incident Management системой

---

### 4. `plans.review.completed`

**Триггер:** Завершение регулярного review плана

**Payload:**
```json
{
  "review_id": 45,
  "plan_id": 123,
  "tenant_id": "tenant-123",
  "plan_code": "BC-001",
  "plan_name": "IT Systems Recovery Plan",
  "review_type": "periodic",
  "reviewed_by_user_id": "user-reviewer",
  "is_current": true,
  "is_effective": true,
  "findings": [
    "Plan is up to date",
    "All contact information verified"
  ],
  "recommendations": [
    "Update RTO based on new SLA requirements",
    "Add new cloud backup procedure"
  ],
  "action_items": [
    {
      "description": "Update RTO to 2 hours",
      "assigned_to": "user-456",
      "due_date": "2025-11-01"
    }
  ],
  "review_date": "2025-10-03T14:00:00",
  "next_review_date": "2026-01-03T14:00:00"
}
```

**Использование:**
- Создание задач из action_items
- Уведомление о необходимости обновления плана
- Отслеживание соответствия требованиям ISO 22301
- Планирование следующего review

---

## Технические детали

### EventBus Client

Plans Service использует `httpx.AsyncClient` для публикации событий:

```python
async def _publish_event(self, topic: str, data: Dict[str, Any]) -> None:
    """
    Publish event to EventBus

    Args:
        topic: Event topic (e.g., "plans.plan.created")
        data: Event data payload
    """
    try:
        client = await self._get_http_client()
        await client.post(
            f"{settings.EVENTBUS_URL}/publish",
            json={
                "topic": topic,
                "data": data,
                "source": settings.SERVICE_NAME,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        logger.info(f"Published event: {topic} for plan_id={data.get('plan_id')}")
    except Exception as e:
        # Don't fail the main operation if EventBus is unavailable
        logger.warning(f"Failed to publish event {topic}: {e}")
```

### Обработка ошибок

- Если EventBus недоступен, событие НЕ публикуется
- Основная операция (создание плана, approval и т.д.) **НЕ прерывается**
- Ошибка логируется как WARNING
- Это обеспечивает graceful degradation

### Конфигурация

EventBus URL настраивается через `.env`:

```bash
EVENTBUS_URL=http://localhost:8001
```

По умолчанию: `http://localhost:8001`

---

## Примеры использования

### Пример 1: Создание плана

```bash
curl -X POST http://localhost:8023/api/plans/plans \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant-123",
    "plan_code": "BC-001",
    "plan_name": "IT Systems Recovery Plan",
    "plan_type": "disaster_recovery",
    "priority": "critical",
    "rto_hours": 4,
    "rpo_hours": 1,
    "mtpd_hours": 24,
    "plan_owner_user_id": "user-456"
  }'
```

**EventBus событие:**
- Topic: `plans.plan.created`
- Лог: `Published event: plans.plan.created for plan_id=123`

---

### Пример 2: Утверждение плана

```bash
curl -X POST http://localhost:8023/api/plans/plans/123/approve \
  -H "Content-Type: application/json" \
  -d '{
    "approved_by": "user-admin",
    "approval_notes": "Approved with minor recommendations"
  }'
```

**EventBus событие:**
- Topic: `plans.plan.approved`
- Лог: `Published event: plans.plan.approved for plan_id=123`

---

### Пример 3: Активация плана

```bash
curl -X POST http://localhost:8023/api/plans/plans/123/activate \
  -H "Content-Type: application/json" \
  -d '{
    "activated_by": "user-admin"
  }'
```

**EventBus событие:**
- Topic: `plans.plan.activated`
- Лог: `Published event: plans.plan.activated for plan_id=123`

---

### Пример 4: Создание review

```bash
curl -X POST http://localhost:8023/api/plans/plans/123/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant-123",
    "review_type": "periodic",
    "is_current": true,
    "is_effective": true,
    "findings": ["Plan is up to date"],
    "recommendations": ["Update RTO"],
    "reviewed_by": "user-reviewer"
  }'
```

**EventBus событие:**
- Topic: `plans.review.completed`
- Лог: `Published event: plans.review.completed for plan_id=123`

---

## Мониторинг событий

### Просмотр всех событий в EventBus

```bash
curl http://localhost:8001/topics/plans.plan.created
curl http://localhost:8001/topics/plans.plan.approved
curl http://localhost:8001/topics/plans.plan.activated
curl http://localhost:8001/topics/plans.review.completed
```

### Проверка логов

```bash
# Логи Plans Service
docker logs plans_service | grep "Published event"

# Пример вывода:
# INFO: Published event: plans.plan.created for plan_id=123
# INFO: Published event: plans.plan.approved for plan_id=123
# INFO: Published event: plans.plan.activated for plan_id=123
# INFO: Published event: plans.review.completed for plan_id=123
```

---

## Интеграция с другими сервисами

### Подписка на события Plans Service

Другие сервисы могут подписываться на события:

```python
# В другом сервисе (например, Compliance Service)
async with httpx.AsyncClient() as client:
    await client.post(
        f"{EVENTBUS_URL}/subscribe",
        json={
            "service": "compliance_service",
            "topics": [
                "plans.plan.created",
                "plans.plan.approved",
                "plans.plan.activated",
                "plans.review.completed"
            ]
        }
    )
```

### Использование в Incident Management

```python
# Incident Service может активировать план при инциденте
async def handle_critical_incident(incident_id: int):
    # Активация плана
    response = await plans_client.activate_plan(
        plan_id=123,
        activated_by="incident_manager"
    )

    # EventBus автоматически уведомит все заинтересованные сервисы
    # через событие plans.plan.activated
```

---

## Изменения в коде

### Файлы изменены

1. **`services/plan_service.py`**
   - Добавлен `httpx.AsyncClient` для EventBus
   - Добавлен метод `_publish_event()`
   - Добавлен метод `_get_http_client()`
   - Добавлен метод `close()`
   - Добавлена публикация событий в 4 методах:
     - `create_plan()` → `plans.plan.created`
     - `approve_plan()` → `plans.plan.approved`
     - `activate_plan()` → `plans.plan.activated`
     - `create_review()` → `plans.review.completed`

### Зависимости

Все необходимые зависимости уже присутствуют:
- `httpx` - для HTTP клиента
- `logging` - для логирования

---

## Тестирование

### Проверка публикации событий

1. Запустите EventBus:
   ```bash
   cd /Users/MD/ISO-22301—копия/services/SERVICES/BCM/eventbus
   uvicorn main:app --port 8001
   ```

2. Запустите Plans Service:
   ```bash
   cd /Users/MD/ISO-22301—копия/services/SERVICES/BCM/plans_service
   uvicorn main:app --port 8023
   ```

3. Создайте план и проверьте событие:
   ```bash
   # Создание плана
   curl -X POST http://localhost:8023/api/plans/plans \
     -H "Content-Type: application/json" \
     -d '{"tenant_id": "test", "plan_code": "BC-001", "plan_name": "Test Plan", "plan_type": "business_continuity", "priority": "high", "rto_hours": 4, "plan_owner_user_id": "user-1"}'

   # Проверка события в EventBus
   curl http://localhost:8001/topics/plans.plan.created
   ```

---

## ISO 22301 Compliance

События соответствуют требованиям ISO 22301:2019:

- **Clause 8.4.1**: Отслеживание создания и утверждения планов
- **Clause 8.4.4**: Мониторинг активации и использования планов
- **Clause 9.1**: Обеспечение прослеживаемости review и maintenance
- **Clause 10.2**: Фиксация улучшений через review события

---

## Версия

- **Дата интеграции:** 2025-10-03
- **Версия Plans Service:** 1.0.0
- **EventBus версия:** Compatible with v1.0
