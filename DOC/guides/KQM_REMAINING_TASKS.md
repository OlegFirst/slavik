# KQM - Оставшиеся Задачи для Полной Реализации
## Knowledge Quality Manager - Roadmap до 100%

**Текущий статус**: 🟡 70% готово
**Дата**: 2025-10-11 03:30

---

## ✅ ЧТО УЖЕ РАБОТАЕТ (70%)

### Полностью реализовано:
- ✅ **Архитектура** - полная документация
- ✅ **База данных** - Migration 044, 11 таблиц
- ✅ **Data Models** - 12 Pydantic моделей
- ✅ **Main Service** - FastAPI на порту 8090
- ✅ **Scenario Generator** - генерация из 4 источников
- ✅ **Knowledge Monitor** - оценка покрытия и пробелов
- ✅ **Compliance Controller** - базовая валидация
- ✅ **328 сценариев загружено** - в PostgreSQL
- ✅ **24-hour cycle** - оркестрация запущена
- ✅ **Philosophy Trinity** - реализована в коде

---

## 🟡 ЧТО ОСТАЛОСЬ (30%)

### 1. RAG INTEGRATION (Критично) - 10%

**Проблема**: RAG (Qdrant) пока не подключён
```
WARNING: RAG context error: All connection attempts failed
```

**Что нужно**:
```bash
# A) Развернуть Qdrant
cd /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/rag/
python3 setup_qdrant.py

# B) Загрузить 328 сценариев в Qdrant
python3 load_scenarios_to_rag.py

# C) Обновить AI Foundation URL в settings.py
AI_FOUNDATION_URL=http://localhost:8002  # Проверить что работает
```

**Файлы для реализации**:
- `/intelligent-core/ai-foundation/rag/setup_qdrant.py` - уже есть?
- `/intelligent-core/ai-foundation/rag/load_scenarios_to_rag.py` - создан ранее

**Приоритет**: 🔴 ВЫСОКИЙ
**Время**: 30 минут
**Польза**: Semantic search для лучшей генерации

---

### 2. REDIS INTEGRATION (Желательно) - 5%

**Проблема**: Hot cache не используется

**Что нужно**:
```python
# Обновить Knowledge Monitor для использования Redis
import redis

class KnowledgeMonitor:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)

    async def _load_existing_scenarios(self):
        # Try Redis first (hot cache)
        cached = self.redis.get("kqm:scenarios:all")
        if cached:
            return json.loads(cached)

        # Load from PostgreSQL
        scenarios = await self._load_from_db()

        # Cache for 7 days
        self.redis.setex("kqm:scenarios:all", 604800, json.dumps(scenarios))

        return scenarios
```

**Приоритет**: 🟡 СРЕДНИЙ
**Время**: 20 минут
**Польза**: Быстрый доступ к частым сценариям

---

### 3. EXPERT REVIEW WORKFLOW (Важно) - 8%

**Проблема**: Экспертная оценка - заглушка

**Что нужно**:
```python
# Интеграция с Expertise Center
async def _get_domain_specialist(self, service: str):
    response = await self.http_client.get(
        f"{settings.EXPERTISE_CENTER_URL}/api/specialists/get",
        params={"domain": service}
    )
    return response.json()

async def _request_expert_review(self, scenario, specialist):
    # Реальная интеграция вместо заглушки
    response = await self.http_client.post(
        f"{settings.EXPERTISE_CENTER_URL}/api/review/request",
        json={
            "scenario_id": scenario.id,
            "specialist_id": specialist['id']
        }
    )
    return response.json()
```

**Файлы**:
- `/intelligent-core/expertise-center/api.py` - проверить endpoints
- Интегрировать Compliance Guardian (уже найден)

**Приоритет**: 🟡 СРЕДНИЙ
**Время**: 1 час
**Польза**: Качественная валидация от AI экспертов

---

### 4. DB INTELLIGENCE INTEGRATION (Оптимизация) - 3%

**Проблема**: Hot/cold storage не оптимизируется

**Что нужно**:
```python
# Интеграция с DB Intelligence для hot/cold размещения
async def _optimize_storage(self, scenario):
    response = await self.http_client.post(
        "http://localhost:8XXX/api/db-intelligence/optimize",
        json={
            "scenario_id": scenario.id,
            "usage_count": await self._get_usage_count(scenario.id),
            "last_accessed": scenario.updated_at
        }
    )

    placement = response.json()

    if placement["storage"] == "hot":
        # Store in Redis (TTL=7d)
        await self.redis.setex(f"scenario:{scenario.id}", 604800, scenario.content)
    else:
        # PostgreSQL only (cold)
        pass
```

**Файл**:
- `/infrastructure/AI-office-infrastructure/db-intelligence/main.py` - проверить API

**Приоритет**: 🟢 НИЗКИЙ
**Время**: 30 минут
**Польза**: Экономия ресурсов

---

### 5. COMMUNITY INTELLIGENCE INTEGRATION - 2%

**Проблема**: k≥5 паттерны не используются

**Что нужно**:
```python
# Интеграция для generate_from_community
async def generate_from_community(self, gap):
    response = await self.http_client.get(
        f"{settings.COMMUNITY_INTEL_URL}/api/patterns/find-similar",
        params={"description": gap.description, "k": 5}
    )

    if response.status_code == 200:
        patterns = response.json()
        # Generate scenario from k≥5 anonymized patterns
```

**Файл**:
- `/intelligent-core/community_intelligence/api.py` - проверить endpoints

**Приоритет**: 🟢 НИЗКИЙ
**Время**: 20 минут
**Польза**: Коллективное обучение

---

### 6. PREDICTIVE INTEGRATION - 2%

**Проблема**: Предсказание пробелов не работает

**Что нужно**:
```python
# Интеграция для предсказания будущих потребностей
async def detect_gaps(self):
    # Current gaps
    gaps = await self._detect_current_gaps()

    # Future gaps (predictive)
    future_needs = await self.http_client.get(
        f"{settings.PREDICTIVE_URL}/api/predict/knowledge-needs",
        params={"time_horizon": "3_months"}
    )

    if future_needs.status_code == 200:
        predicted_gaps = self._convert_to_gaps(future_needs.json())
        gaps.extend(predicted_gaps)

    return gaps
```

**Приоритет**: 🟢 НИЗКИЙ
**Время**: 30 минут
**Польза**: Проактивная генерация

---

## 📊 ROADMAP К 100%

### Phase 1: Критичное (70% → 80%) - 1-2 часа
1. ✅ Проверить что AI Foundation работает
2. ✅ Развернуть/подключить Qdrant
3. ✅ Загрузить 328 сценариев в RAG
4. ✅ Протестировать semantic search

### Phase 2: Важное (80% → 90%) - 2-3 часа
1. ✅ Интегрировать Redis для hot cache
2. ✅ Подключить Expertise Center (Compliance Guardian)
3. ✅ Реализовать expert review workflow
4. ✅ Протестировать полный цикл с экспертами

### Phase 3: Оптимизация (90% → 95%) - 1-2 часа
1. ✅ Интегрировать DB Intelligence
2. ✅ Подключить Community Intelligence
3. ✅ Добавить Predictive
4. ✅ Оптимизировать производительность

### Phase 4: Production Ready (95% → 100%) - 2-3 часа
1. ✅ Мониторинг (Prometheus/Grafana)
2. ✅ Alerts (критичные пробелы, низкий coverage)
3. ✅ Backup strategy
4. ✅ Load testing
5. ✅ Production deployment

---

## 🎯 ПРИОРИТЕТНЫЙ ПЛАН (Следующие Шаги)

### Сегодня (2-3 часа)
```bash
# 1. RAG Integration (КРИТИЧНО)
cd /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation
# Проверить/развернуть Qdrant
# Загрузить 328 сценариев

# 2. Redis Integration
# Добавить caching в Knowledge Monitor

# 3. Первый полный тест
curl -X POST http://localhost:8090/api/kqm/scenarios/generate
# Проверить: RAG context используется, Redis кэширует
```

### Завтра (2-3 часа)
```bash
# 4. Expert Review
# Интегрировать Compliance Guardian
# Протестировать expert validation

# 5. DB Intelligence
# Подключить hot/cold optimization

# 6. Community + Predictive
# Интегрировать оставшиеся компоненты
```

### Через Неделю
```bash
# 7. Production готовность
# Мониторинг, alerts, backup
# Load testing
# Deployment guide
```

---

## 📋 ДЕТАЛЬНЫЙ CHECKLIST

### RAG (10%)
- [ ] Проверить AI Foundation работает
- [ ] Qdrant развёрнут и доступен
- [ ] 328 сценариев загружены в Qdrant
- [ ] Semantic search протестирован
- [ ] ScenarioGenerator использует RAG context
- [ ] Нет WARNING "RAG context error"

### Redis (5%)
- [ ] Redis доступен по REDIS_URL
- [ ] Cache manager реализован
- [ ] Hot scenarios кэшируются (TTL=7d)
- [ ] Cache hit rate > 50%

### Expert Review (8%)
- [ ] Expertise Center доступен
- [ ] Compliance Guardian интегрирован
- [ ] Expert review workflow работает
- [ ] Quality score учитывает expert approval

### DB Intelligence (3%)
- [ ] DB Intelligence API доступен
- [ ] Hot/cold optimization работает
- [ ] Metrics показывают оптимизацию

### Community Intelligence (2%)
- [ ] API доступен
- [ ] k≥5 паттерны получаются
- [ ] generate_from_community работает

### Predictive (2%)
- [ ] Predictive API доступен
- [ ] Future gaps предсказываются
- [ ] Интегрировано в detect_gaps

---

## 🔧 ФАЙЛЫ ДЛЯ ОБНОВЛЕНИЯ

### Приоритет 1 (Критично)
1. `/intelligent-core/ai-foundation/rag/setup_qdrant.py`
2. `/intelligent-core/ai-foundation/rag/load_scenarios_to_rag.py`
3. `/platform-services/AI-services-management/tools/scenario_generator.py` (RAG integration)

### Приоритет 2 (Важно)
4. `/platform-services/AI-services-management/analytics/knowledge_monitor.py` (Redis)
5. `/platform-services/AI-services-management/validation/compliance_controller.py` (Expert review)

### Приоритет 3 (Опционально)
6. Интеграции с DB Intelligence, Community, Predictive

---

## 💡 РЕКОМЕНДАЦИИ

### Минимально для Production (80%)
- ✅ RAG Integration (обязательно)
- ✅ Redis Cache (желательно)
- ⏭️ Expert Review (можно отложить, сейчас LLM валидация работает)

### Полная реализация (100%)
- Все интеграции выше
- Мониторинг
- Alerts
- Backup

---

## 📊 ТЕКУЩИЙ ПРОГРЕСС

```
[████████████████████░░░░░░░░░░] 70%

Компоненты:
✅ Architecture        100%
✅ Database           100%
✅ Main Service       100%
✅ Data Models        100%
✅ Generator          100%
✅ Monitor            100%
✅ Validator           90% (needs expert integration)
🟡 RAG Integration      0% (КРИТИЧНО)
🟡 Redis Cache          0%
🟡 Expert Review        0%
🟡 DB Intelligence      0%
🟡 Community Intel      0%
🟡 Predictive           0%
🟡 Monitoring           0%
```

---

## 🎯 ИТОГО

**Для базовой production-ready системы** (80%):
- ⏰ Время: **2-3 часа**
- 🎯 Задачи: RAG + Redis
- 💰 ROI: Semantic search + performance

**Для полной реализации** (100%):
- ⏰ Время: **8-10 часов**
- 🎯 Задачи: Все интеграции + мониторинг
- 💰 ROI: Production-grade система

---

**Что делать сейчас?**
👉 Начать с **RAG Integration** (критично для качества генерации)
