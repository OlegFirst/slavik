# Balancer Service - Phase 2 MVP

**Версия**: 2.4.0
**Статус**: ✅ Ready to Run
**Дата**: 2025-10-09

---

## 🎯 Что это?

Balancer Service - это сервис, который запускает все балансировщики Phase 2:

1. **System Balancer** (МОЗГ ГЛОБАЛЬНЫЙ) - глобальная балансировка с ПООЩРЕНИЕ/НАКАЗАНИЕ
2. **Impact Evidence Tracker** (RATIONAL) - доказательная база с ROI
3. **Predictive ROI Optimizer** (INTUITIVE + PRAGMATIC) - предсказания + ROI оптимизация
4. **Three-Dimensional Balancer** (3D BALANCE) - баланс между тремя измерениями

---

## 🚀 Быстрый старт

### Вариант 1: Docker Compose (рекомендуется)

```bash
# В директории balancer-service
cd infrastructure/balancer-service

# Запустить (создаст сеть если нужно)
docker-compose up -d

# Проверить логи
docker-compose logs -f balancer-service

# Проверить метрики
curl http://localhost:9091/metrics

# Остановить
docker-compose down
```

### Вариант 2: Локальный запуск (для разработки)

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить Redis (нужен для EventBus)
docker run -d -p 6379:6379 redis:7-alpine

# Запустить сервис
python main.py
```

---

## 🧪 Тестирование

### Integration Test

```bash
# Запустить integration test
python test_integration.py
```

**Тест проверяет:**
1. ✅ EventBus connection
2. ✅ Balancer initialization
3. ✅ Imbalance event flow
4. ✅ Three-dimensional decision making

**Ожидаемый результат:**
```
====================================
Test Summary
====================================
✅ PASS - EventBus Connection
✅ PASS - Balancer Initialization
✅ PASS - Imbalance Event Flow
✅ PASS - Three-Dimensional Decision

Total: 4/4 tests passed

🎉 All tests passed!
```

---

## 📊 Мониторинг

### Prometheus Metrics

Доступны на порту **9091**:

```bash
# Проверить метрики
curl http://localhost:9091/metrics
```

**Ключевые метрики:**

```
# Service health
balancer_service_up 1

# Events processed
balancer_events_processed_total{component="imbalance"} 142
balancer_events_processed_total{component="resource_snapshot"} 1850

# Errors
balancer_errors_total{component="imbalance_handler"} 0

# System Balancer
balancer_global_imbalances_detected 12
balancer_allocations_recommended 45
balancer_rewards_given 15
balancer_penalties_given 8

# Three-Dimensional Balancer
3d_decisions_made_total 23
3d_balance_score 0.89
```

---

## 🔌 Интеграция с платформой

### Resource Tracker (уже интегрирован в mio-manager)

Resource Tracker запускается автоматически в **mio-manager** и публикует события:

```python
# События от Resource Tracker:
'platform.resources.snapshot'   # Каждые 60s
'platform.resources.deficit'    # При дефиците ресурсов
'platform.resources.surplus'    # При избытке ресурсов
```

### Survival Instinct (интеграция готова)

Survival Instinct публикует события дисбаланса:

```python
# События от Survival Instinct:
'platform.bcm.imbalance_detected'  # При обнаружении дисбаланса
```

### Wishlist Integration (интегрирован в decision-center)

Wishlist доступен через decision-center module:

```python
from infrastructure.decision_center import WishlistDecisionIntegration

wishlist = WishlistDecisionIntegration(
    decision_center=decision_center,
    resource_tracker=resource_tracker,
    eventbus=eventbus
)
await wishlist.start()
```

---

## 🎓 Как это работает?

### 1. EventBus Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Survival Instinct (в каждом модуле)                      │
│    • detect_my_imbalance()                                  │
│    • publish: platform.bcm.imbalance_detected               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. EventBus (Redis Streams)                                 │
│    • Доставка событий всем подписчикам                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Balancer Service                                         │
│    ├─ System Balancer (слушает события)                     │
│    ├─ Impact Evidence Tracker (записывает baseline)         │
│    ├─ Predictive ROI Optimizer (анализирует тренды)         │
│    └─ Three-Dimensional Balancer (принимает решения)        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. System Balancer публикует рекомендации                   │
│    • platform.bcm.allocation_recommended                    │
└─────────────────────────────────────────────────────────────┘
```

### 2. Three-Dimensional Decision Making

```
RATIONAL (Evidence-Based):
├── Baseline → Intervention → Outcome
├── ROI calculation: benefit/cost
└── Confidence: 0-1

INTUITIVE (Pattern-Based):
├── Health trends: rising/falling/stable
├── Future imbalances prediction
└── Pattern recognition

PRAGMATIC (ROI-Driven):
├── Cost/benefit analysis
├── Risk-adjusted ROI
└── Breakeven time

↓ Weighted Voting ↓

BALANCED DECISION:
├── Action type
├── Resource allocation
├── Reasoning
└── Adaptive weights (context-aware)
```

### 3. Reward/Penalty Mechanism

```python
# ПООЩРЕНИЕ (health > 80):
allocated_resources × 0.7  # Reduce priority

# НАКАЗАНИЕ (health < 50):
allocated_resources × 1.5  # Increase priority
```

---

## ⚙️ Конфигурация

### Environment Variables

```bash
# EventBus
REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR

# Intervals
RESOURCE_CHECK_INTERVAL=60  # seconds
BALANCER_CHECK_INTERVAL=10  # seconds
```

### Customize via Code

```python
# В main.py можно настроить:

# Resource Tracker interval
resource_tracker = ResourceTrackerClient(
    eventbus=eventbus,
    check_interval=30  # 30 секунд вместо 60
)

# System Balancer thresholds
system_balancer = SystemBalancer(
    eventbus=eventbus,
    check_interval=5,  # 5 секунд вместо 10
    min_health_threshold=40,  # Penalty threshold
    max_health_threshold=85   # Reward threshold
)
```

---

## 🐛 Troubleshooting

### Проблема: EventBus connection failed

```bash
# Проверить что Redis запущен
docker ps | grep redis

# Если нет - запустить
docker run -d -p 6379:6379 redis:7-alpine

# Проверить подключение
redis-cli ping
# Должно вернуть: PONG
```

### Проблема: No events received

```bash
# Проверить что Resource Tracker запущен (в mio-manager)
curl http://localhost:8046/health

# Проверить что Survival Instinct публикует события
# (нужно trigger imbalance в каком-то модуле)
```

### Проблема: Import errors

```bash
# Проверить что пути добавлены правильно
python -c "import sys; print(sys.path)"

# Должны быть:
# - /path/to/intelligent-core
# - /path/to/infrastructure
```

---

## 📈 Влияние на производительность

### Текущие измерения (нужно измерить!):

- **CPU**: Ожидается ~5-10% при работе
- **Memory**: ~200-300 MB
- **Network**: Минимальное (только EventBus)

### Рекомендации:

1. **Не запускать всё сразу** в первый раз
2. **Начать с Resource Tracker** - самый легковесный
3. **Добавить System Balancer** после проверки
4. **Мониторить метрики** Prometheus

---

## 🎯 Следующие шаги

### Phase 2.5 - Тесты и оптимизация:
- [ ] Unit тесты для каждого балансировщика
- [ ] Load тесты (сколько событий в секунду можно обработать?)
- [ ] Performance профилирование
- [ ] Оптимизация алгоритмов

### Phase 3 - Production Ready:
- [ ] Database для хранения evidence (Supabase/PostgreSQL)
- [ ] Dashboard для визуализации решений
- [ ] Alerting при критических дисбалансах
- [ ] Auto-scaling балансировщиков

---

## 📚 Документация

- [PHASE2_INTEGRATION_COMPLETE.md](../../PHASE2_INTEGRATION_COMPLETE.md) - полная документация
- [PHASE2_QUICK_REFERENCE.md](../../PHASE2_QUICK_REFERENCE.md) - примеры кода
- [docs/PHASE2_REALITY_CHECK.md](../../docs/PHASE2_REALITY_CHECK.md) - честная оценка
- [LIVING_SYSTEM_ARCHITECTURE.md](../../LIVING_SYSTEM_ARCHITECTURE.md) - концепция

---

## ✅ Checklist перед запуском

- [ ] Redis запущен (docker run redis)
- [ ] EventBus доступен (redis://localhost:6379)
- [ ] mio-manager запущен (Resource Tracker работает)
- [ ] Dependencies установлены (pip install -r requirements.txt)
- [ ] Integration test пройден (python test_integration.py)

---

**Готово к запуску!** 🚀

**Версия**: 2.4.0
**Статус**: ✅ MVP Ready
**Дата**: 2025-10-09
