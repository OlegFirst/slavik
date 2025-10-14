# ResourceTracker Integration - System BCM

**Дата**: 2025-10-11
**Статус**: ✅ ИНТЕГРИРОВАН

---

## 📊 Что такое ResourceTracker?

**ResourceTracker** - это система мониторинга ресурсов платформы с предсказанием дефицитов.

### Философия

```
- Ресурсы = жизненная энергия системы
- Тренды ресурсов предсказывают будущее
- Дефицит ресурсов → триггер самореализации
- Избыток ресурсов → возможность для роста
```

### Возможности

✅ **Мониторинг ресурсов**:
- CPU usage (percent)
- Memory usage (percent & MB)
- Disk I/O (MB)
- Network traffic (bytes)

✅ **Анализ трендов**:
- Расчет тренда (растет/падает/стабильно)
- Линейная регрессия по окну снимков
- Нормализация в диапазон -1.0 to +1.0

✅ **Предсказание дефицитов**:
- Когда CPU достигнет порога (90%)
- Когда Memory достигнет порога (90%)
- Предсказание в секундах до события

✅ **Определение состояния**:
- `"deficit"` - дефицит ресурсов
- `"normal"` - нормальное состояние
- `"surplus"` - избыток ресурсов

---

## 🔌 Интеграция в System BCM

### Архитектура

```
┌─────────────────────────────────────────────────────┐
│           System BCM Service (main.py)              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────┐    ┌─────────────────────┐  │
│  │ ResourceTracker  │───▶│ BCM Coordinator     │  │
│  │ (ai-foundation)  │    │ (BIA Phase)         │  │
│  └──────────────────┘    └─────────────────────┘  │
│           │                        │               │
│           │                        ▼               │
│           │              ┌─────────────────────┐  │
│           │              │ EventBus Publisher  │  │
│           │              │ (resource events)   │  │
│           │              └─────────────────────┘  │
│           ▼                                        │
│  ┌──────────────────┐                             │
│  │ Prometheus       │                             │
│  │ Metrics          │                             │
│  └──────────────────┘                             │
└─────────────────────────────────────────────────────┘
```

### Компоненты

#### 1. ResourceTracker (Shared Utility)

**Локация**: `/intelligent-core/ai-foundation/utils/resource_tracker.py`

**Инициализация** (main.py:681-688):
```python
resource_history_path = Path(__file__).parent / "data" / "resource_history.json"
state.resource_tracker = await create_resource_tracker(
    snapshot_interval_seconds=60.0,  # Снимок каждые 60 секунд
    history_size=100,                 # Хранить 100 снимков
    storage_path=str(resource_history_path)
)
logger.info("✅ Resource Tracker activated (60s snapshots)")
```

#### 2. BCM Coordinator Integration

**Локация**: `system_bcm_coordinator.py:49-61`

```python
def __init__(self, resource_tracker=None):
    # ...
    # ResourceTracker (NEW!)
    self.resource_tracker = resource_tracker
    # ...
```

**Использование в BIA фазе** (system_bcm_coordinator.py:272-353):
```python
async def _execute_bia_phase(self, resource_tracker=None) -> Dict[str, Any]:
    # ... existing service health checks ...

    # ResourceTracker данные (NEW!)
    resource_monitoring = None
    if resource_tracker:
        available = resource_tracker.get_available_resources()
        resource_state = resource_tracker.detect_resource_state()
        cpu_deficit = resource_tracker.predict_deficit('cpu_percent', 90.0)
        mem_deficit = resource_tracker.predict_deficit('memory_percent', 90.0)

        resource_monitoring = {
            "state": resource_state,
            "available": available,
            "predictions": {
                "cpu_deficit_seconds": cpu_deficit,
                "memory_deficit_seconds": mem_deficit
            },
            "stats": resource_tracker.get_stats()
        }

        # Publish event if deficit detected
        if resource_state == "deficit":
            logger.warning(f"⚠️  Resource deficit detected!")
            await self._publish_event("resources.contention", {
                "type": "predicted_shortage",
                "available": available,
                "cpu_deficit_seconds": cpu_deficit,
                "memory_deficit_seconds": mem_deficit
            })
```

---

## 📡 API Endpoints

### GET /resources/status

**Получить статус ResourceTracker**

**Response**:
```json
{
  "available": {
    "cpu_percent": 65.3,
    "memory_mb": 2048.5,
    "time_seconds": 60.0,
    "disk_io_mb": 100.0
  },
  "state": "normal",
  "stats": {
    "total_snapshots": 150,
    "deficit_events": 2,
    "surplus_events": 5,
    "history_size": 100,
    "resource_state": "normal",
    "cpu_trend": 0.15,
    "memory_trend": -0.05
  },
  "predictions": {
    "cpu_deficit_seconds": null,
    "memory_deficit_seconds": 450.2
  }
}
```

**Коды состояния**:
- `200` - OK
- `503` - ResourceTracker не инициализирован

---

## 📊 Prometheus Metrics

### Новые метрики (добавлены в /metrics)

```prometheus
# Resource snapshots
system_bcm_resource_snapshots_total 150

# Resource events
system_bcm_resource_deficit_events 2
system_bcm_resource_surplus_events 5

# Current resource state (deficit=2, normal=1, surplus=0)
system_bcm_resource_state 1

# Available resources
system_bcm_cpu_available_percent 65.3
system_bcm_memory_available_mb 2048.5
```

---

## 🎯 EventBus Events

### Published Events

#### 1. platform.bcm.resources.contention

**Когда**: Обнаружен дефицит ресурсов (state == "deficit")

**Payload**:
```json
{
  "type": "predicted_shortage",
  "available": {
    "cpu_percent": 15.2,
    "memory_mb": 256.8,
    "time_seconds": 60.0,
    "disk_io_mb": 100.0
  },
  "cpu_deficit_seconds": 120.5,
  "memory_deficit_seconds": 85.3
}
```

**Кто слушает**:
- System BCM (apply_resource_priorities)
- Survival Instinct (может реагировать на дефицит)
- Другие сервисы для graceful degradation

---

## 📈 Использование данных в BCM цикле

### Phase 1: BIA (Business Impact Analysis)

**Что добавляется** в BIA результаты:

```json
{
  "services": [...],
  "health_score": 85.5,
  "dependencies": {...},
  "classification": {...},
  "rto_recommendations": {...},

  // NEW: Resource monitoring
  "resource_monitoring": {
    "state": "normal",
    "available": {
      "cpu_percent": 65.3,
      "memory_mb": 2048.5,
      "time_seconds": 60.0,
      "disk_io_mb": 100.0
    },
    "predictions": {
      "cpu_deficit_seconds": null,
      "memory_deficit_seconds": 450.2
    },
    "stats": {
      "total_snapshots": 150,
      "deficit_events": 2,
      "surplus_events": 5,
      "cpu_trend": 0.15,
      "memory_trend": -0.05
    }
  }
}
```

### Использование в других фазах

**Phase 2: Risk Assessment**
- Expertise Center получает resource_monitoring данные
- Учитывает предсказанные дефициты в оценке рисков

**Phase 3: Pattern Detection**
- learning-knowledge анализирует тренды ресурсов
- Находит паттерны дефицитов

**Phase 4: AI Analysis**
- RAG поиск решений для resource contention
- LLM генерирует рекомендации по оптимизации

---

## 🔧 Конфигурация

### Параметры ResourceTracker

```python
snapshot_interval_seconds = 60.0   # Интервал снимков (секунды)
history_size = 100                  # Размер истории снимков
storage_path = "data/resource_history.json"  # Путь к файлу хранения
```

### Пороги дефицита

```python
cpu_threshold_percent = 90.0       # CPU порог для предсказания дефицита
memory_threshold_percent = 90.0    # Memory порог
lookahead_snapshots = 5            # На сколько снимков вперед смотреть
```

### Триггеры событий

```python
deficit_trigger = {
    "cpu_percent": > 80,           # Дефицит если CPU > 80%
    "memory_percent": > 80         # или Memory > 80%
}

surplus_trigger = {
    "cpu_percent": < 30,           # Избыток если CPU < 30%
    "memory_percent": < 50         # и Memory < 50%
}
```

---

## 🚀 Использование

### Программный доступ

```python
# В любом месте, где есть доступ к state.resource_tracker

# 1. Получить доступные ресурсы
available = state.resource_tracker.get_available_resources()
# {
#   "cpu_percent": 65.3,
#   "memory_mb": 2048.5,
#   "time_seconds": 60.0,
#   "disk_io_mb": 100.0
# }

# 2. Определить состояние
resource_state = state.resource_tracker.detect_resource_state()
# "deficit" | "normal" | "surplus"

# 3. Предсказать дефицит
cpu_deficit_seconds = state.resource_tracker.predict_deficit(
    metric_name='cpu_percent',
    threshold_percent=90.0
)
# 120.5 секунд до достижения 90% CPU
# или None если не достигнет

# 4. Рассчитать тренд
cpu_trend = state.resource_tracker.calculate_trend(
    metric_name='cpu_percent',
    window_size=10
)
# 0.15 = медленный рост
# 0.0 = стабильно
# -0.15 = медленное падение

# 5. Получить статистику
stats = state.resource_tracker.get_stats()
# {
#   "total_snapshots": 150,
#   "deficit_events": 2,
#   "surplus_events": 5,
#   "history_size": 100,
#   "resource_state": "normal",
#   "cpu_trend": 0.15,
#   "memory_trend": -0.05
# }
```

### HTTP API

```bash
# Получить статус ресурсов
curl http://localhost:8050/resources/status

# Получить метрики (включая ResourceTracker)
curl http://localhost:8050/metrics
```

---

## 📁 Файлы

### Создано/изменено

1. **ResourceTracker (shared utility)**:
   - `/intelligent-core/ai-foundation/utils/resource_tracker.py` (415 строк)
   - `/intelligent-core/ai-foundation/utils/__init__.py` (expose для импорта)

2. **System BCM Integration**:
   - `main.py:52-53` - Import
   - `main.py:82` - State field
   - `main.py:681-688` - Startup initialization
   - `main.py:728-729` - Shutdown cleanup
   - `main.py:647-661` - API endpoint (/resources/status)
   - `main.py:615-630` - Prometheus metrics

3. **BCM Coordinator**:
   - `system_bcm_coordinator.py:49-61` - Constructor parameter
   - `system_bcm_coordinator.py:131` - Pass to BIA phase
   - `system_bcm_coordinator.py:272-353` - BIA phase resource monitoring

4. **Documentation**:
   - `/docs/RESOURCE_TRACKER_INTEGRATION.md` (этот файл)

### Удалено

- `/intelligent-core/coordination-center/resources/resource_tracker.py` (перемещено в ai-foundation)

---

## 🎯 Результат

### ✅ Что работает

1. **Мониторинг**: Снимки каждые 60 секунд (CPU, Memory, Disk I/O, Network)
2. **Тренды**: Расчет направления изменения ресурсов
3. **Предсказание**: Когда ресурсы достигнут порога
4. **Состояние**: deficit / normal / surplus detection
5. **События**: Публикация platform.bcm.resources.contention при дефиците
6. **Интеграция с BIA**: Данные включены в Phase 1 анализа
7. **API endpoint**: GET /resources/status
8. **Prometheus**: 6+ метрик для мониторинга
9. **Persistence**: Сохранение истории в JSON

### 📊 Метрики

- **Мониторинг**: 4 типа ресурсов
- **История**: 100 снимков (configurable)
- **Интервал**: 60 секунд
- **Предсказание**: до 5 снимков вперед (5 минут)
- **Persistence**: последние 50 снимков сохраняются на диск

### 🔗 Интеграции

- ✅ System BCM Service (main.py)
- ✅ BCM Coordinator (BIA phase)
- ✅ EventBus (resource.contention events)
- ✅ Prometheus (metrics)
- ✅ Shared utility (ai-foundation/utils)

---

## 🔮 Будущее развитие

### Planned enhancements:

1. **AI-powered prediction**:
   - Использовать ML модели для более точного предсказания
   - Seasonal patterns detection

2. **Auto-scaling integration**:
   - Триггеры для Docker/K8s auto-scaling
   - Resource quotas management

3. **Cross-service correlation**:
   - Связь потребления ресурсов с сервисами
   - Service-level resource attribution

4. **Advanced alerting**:
   - Multi-level thresholds
   - Smart notifications

---

**Дата**: 2025-10-11
**Автор**: Claude Code
**Статус**: ✅ Production Ready
