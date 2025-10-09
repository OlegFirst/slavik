# Event Intelligence System - Complete Implementation

## 📋 Summary

**Создана полноценная unified event-driven архитектура** для AI Platform ISO с автоматическим обнаружением сервисов, изучением паттернов и предсказанием событий.

**Статус:** ✅ **READY FOR PRODUCTION**
**Дата:** 2025-10-08

---

## 🎯 Что создано

### 1. Shared Event Bus Library
**Локация:** `intelligent-core/shared/event_bus/`

**Компоненты:**
- ✅ `core.py` - EventBus с Redis Streams backend
- ✅ `outbox.py` - Outbox pattern для гарантированной доставки
- ✅ `INTEGRATION_GUIDE.md` - Полное руководство

**Возможности:**
- Auto-discovery сервисов через decorators
- Pattern matching с wildcards (`workflow.*`)
- Consumer groups для load balancing
- Transactional event publishing
- Correlation tracking

### 2. Event Intelligence Brain
**Локация:** `intelligent-core/event_intelligence/`

**Компоненты:**
- ✅ `auto_discovery.py` - ServiceRegistry, PatternLearner, Auto-discovery engine
- ✅ `main.py` - Updated с EventBus integration + API endpoints

**Возможности:**
- Автоматическое обнаружение всех сервисов
- Изучение паттернов событий (A → B с confidence)
- Предсказание следующего события
- Построение event flow graph
- Real-time статистика

**API Endpoints:**
```
GET /discovery/services          # Все сервисы
GET /discovery/patterns          # Изученные паттерны
GET /discovery/predict/{type}    # Предсказание
GET /discovery/stats             # Статистика
GET /discovery/graph             # Граф для viz
```

### 3. Database Schema
**Локация:** `infrastructure/database/migrations_source/044_outbox_events.sql`

**Outbox Events Table:**
- Transactional event publishing
- Automatic retry с exponential backoff
- Cleanup старых событий (30 days)
- RLS для multi-tenancy

### 4. Documentation
**Созданные файлы:**
```
intelligent-core/
├── event_intelligence/
│   ├── ARCHITECTURE.md                    ✅ Полная архитектура
│   ├── README.md                          ✅ Quick start
│   └── IMPLEMENTATION_COMPLETE.md         ✅ Детальный отчёт
│
└── shared/event_bus/
    └── INTEGRATION_GUIDE.md               ✅ Integration guide

EVENT_INTELLIGENCE_SYSTEM.md               ✅ Этот файл
```

---

## 🚀 Quick Start

### 1. Deploy Infrastructure

```bash
# Start Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Apply DB migration
psql $DATABASE_URL < infrastructure/database/migrations_source/044_outbox_events.sql
```

### 2. Start Event Intelligence

```bash
export REDIS_URL=redis://localhost:6379
./intelligent-core/wrappers/run_event_intelligence.sh

# Verify
curl http://localhost:8039/health
```

### 3. Integrate Your Service

В вашем `main.py`:

```python
from shared.event_bus import init_event_bus, get_event_bus, publish_event, subscribe_to

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_event_bus(service_name="your-service")
    yield
    await get_event_bus().close()

# Publish events
await publish_event(
    event_type="workflow.completed",
    data={"workflow_id": "123"}
)

# Subscribe to events
@subscribe_to("workflow.*")
async def on_workflow(event: Event):
    print(f"Got: {event.type}")
```

**Всё!** Event Intelligence автоматически:
- Обнаружит ваш сервис
- Зарегистрирует подписки
- Начнёт изучать паттерны

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              EVENT INTELLIGENCE BRAIN                        │
│  • Auto-discovery  • Pattern Learning  • Prediction         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           SHARED EVENT BUS (Redis Streams)                   │
│  • Pub/Sub  • Outbox Pattern  • Consumer Groups             │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ All Services │  │ Auto-connect │  │ Unified API  │
│ intelligent- │  │ via shared/  │  │ publish_     │
│ core/*       │  │ event_bus    │  │ event()      │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 🎯 Key Benefits

### For Developers
- ✅ **Unified API** - один способ для всех событий
- ✅ **Auto-discovery** - не нужно manually регистрировать
- ✅ **Decorators** - `@subscribe_to("pattern")` = всё
- ✅ **Guaranteed delivery** - outbox pattern

### For Operations
- ✅ **Observability** - все события видны в Event Intelligence
- ✅ **Pattern analysis** - автоматическое обнаружение проблем
- ✅ **Prediction** - предвидение следующих шагов
- ✅ **Monitoring** - Prometheus metrics

### For Business
- ✅ **Process visibility** - граф всех workflow
- ✅ **Bottleneck detection** - медленные переходы
- ✅ **Compliance** - полная история событий
- ✅ **Analytics** - data-driven decisions

---

## 📋 Integration Checklist

### Phase 1: Infrastructure (Done ✅)
- [x] Shared Event Bus library
- [x] Event Intelligence service
- [x] Database migration
- [x] Documentation

### Phase 2: Service Integration (Next)

Для каждого сервиса в `intelligent-core/`:

- [ ] **workflow_intelligence**
  - [ ] Import `shared.event_bus`
  - [ ] `init_event_bus()` в lifespan
  - [ ] Replace direct EventBus calls → `publish_event()`
  - [ ] Add `@subscribe_to` decorators

- [ ] **expertise-center**
  - [ ] Same steps

- [ ] **community_intelligence**
  - [ ] Same steps

- [ ] **predictive**
  - [ ] Same steps

- [ ] **collective**
  - [ ] Same steps

**Template:**
```python
# main.py

# 1. Import
from shared.event_bus import init_event_bus, get_event_bus, publish_event, subscribe_to

# 2. Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_event_bus(service_name="service-name")
    yield
    await get_event_bus().close()

# 3. Publish
await publish_event(event_type="domain.entity.action", data={...})

# 4. Subscribe
@subscribe_to("pattern.*")
async def handler(event: Event):
    pass
```

---

## 🧪 Testing

### Verify Discovery

```bash
# Start Event Intelligence
curl http://localhost:8039/health

# Start another service
./wrappers/run_workflow_intelligence.sh

# Check discovery
curl http://localhost:8039/discovery/services
# Should show both services
```

### Verify Pattern Learning

```bash
# Generate events (через API вашего сервиса)
# ...after some time...

curl http://localhost:8039/discovery/patterns
# Should show learned patterns
```

### Verify Prediction

```bash
curl http://localhost:8039/discovery/predict/workflow.started
# Should return predicted next event
```

---

## 📊 Monitoring

### Prometheus Metrics

```bash
curl http://localhost:8039/metrics | grep event_intelligence
```

**Key Metrics:**
- `event_intelligence_services_discovered`
- `event_intelligence_patterns_learned`
- `event_intelligence_predictions_made`
- `eventbus_published_total`
- `outbox_events_pending`

### Health Checks

```bash
curl http://localhost:8039/health
curl http://localhost:8039/discovery/stats
```

---

## 📚 Documentation

### For Integration
👉 **START HERE:** [`intelligent-core/shared/event_bus/INTEGRATION_GUIDE.md`](intelligent-core/shared/event_bus/INTEGRATION_GUIDE.md)

### For Architecture
👉 **Full Details:** [`intelligent-core/event_intelligence/ARCHITECTURE.md`](intelligent-core/event_intelligence/ARCHITECTURE.md)

### For Quick Start
👉 **Quick Reference:** [`intelligent-core/event_intelligence/README.md`](intelligent-core/event_intelligence/README.md)

### For Implementation Details
👉 **Complete Report:** [`intelligent-core/event_intelligence/IMPLEMENTATION_COMPLETE.md`](intelligent-core/event_intelligence/IMPLEMENTATION_COMPLETE.md)

---

## 🚨 Troubleshooting

### Events не публикуются

```bash
# 1. Check Redis
redis-cli PING

# 2. Check logs
tail -f /tmp/event-intelligence.log

# 3. Check EventBus connection
curl http://localhost:8039/discovery/stats
```

### Paterns не изучаются

Убедитесь что события имеют `correlation_id`:
```python
await publish_event(
    event_type="workflow.started",
    data={...},
    correlation_id="unique-id"  # ✅ Важно!
)
```

### Outbox события stuck

```sql
-- Check errors
SELECT event_type, error FROM outbox_events WHERE status = 'failed';

-- Cleanup old
SELECT cleanup_outbox_events();
```

---

## 🎓 Event Naming Convention

**Format:** `<domain>.<entity>.<action>`

**Examples:**
```
workflow.process.started
workflow.process.completed
bia.risk.identified
bia.mitigation.planned
incident.alert.detected
incident.response.activated
compliance.audit.scheduled
governance.policy.updated
```

**Rules:**
- Use past tense for completed actions
- Use dots for hierarchy
- Keep domain-specific
- Be consistent

---

## 🔒 Security

- ✅ All events include `tenant_id`
- ✅ RLS на `outbox_events` table
- ✅ Redis password support
- ✅ Event validation
- ✅ Consumer group isolation

---

## ✅ Success Criteria (All Met!)

- [x] ✅ Shared event bus library работает
- [x] ✅ Redis Streams integration
- [x] ✅ Outbox pattern с retry
- [x] ✅ Auto-discovery сервисов
- [x] ✅ Pattern learning с prediction
- [x] ✅ Event graph для visualization
- [x] ✅ Database migration
- [x] ✅ Complete documentation
- [x] ✅ API endpoints functional

---

## 🎉 Next Steps

### Week 1
1. Deploy Event Intelligence service
2. Apply database migration
3. Integrate 2-3 core services
4. Monitor pattern learning

### Month 1
1. Integrate all intelligent-core services
2. Setup Grafana dashboards
3. Configure alerting
4. Performance tuning

### Quarter 1
1. ML-based prediction (beyond patterns)
2. Anomaly detection
3. AI Event Managers integration
4. Automated workflow healing

---

## 🤝 Contributing

При добавлении событий:

1. Следуйте naming convention
2. Всегда включайте `correlation_id`
3. Делайте handlers идемпотентными
4. Документируйте новые event types
5. Добавляйте tests

---

## 📞 Support

Вопросы? → Читайте [INTEGRATION_GUIDE.md](intelligent-core/shared/event_bus/INTEGRATION_GUIDE.md)

Проблемы? → Создавайте issue с:
- Логами
- Шагами для воспроизведения
- Ожидаемое vs фактическое поведение

---

**Event Intelligence System** - foundation для event-driven AI Platform! 🧠✨

**Status:** ✅ **PRODUCTION READY**
**Date:** 2025-10-08
