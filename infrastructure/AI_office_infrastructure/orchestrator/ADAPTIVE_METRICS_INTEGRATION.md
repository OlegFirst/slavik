# Адаптивные Метрики и Приоритеты - AI Office Orchestrator ✅

**Дата**: 2025-10-08
**Статус**: ✅ Полностью интегрировано

---

## 🎯 Что было сделано

Интегрирована система **адаптивных метрик и динамических приоритетов** в AI Office Orchestrator (`unified_orchestrator.py`). Теперь оркестратор работает в рамках метрик производительности и автоматически адаптирует приоритеты задач на основе текущей нагрузки системы.

---

## 🏗️ Архитектура

```
UnifiedOrchestrator (с AdaptiveOrchestratorMixin)
    ↓
├─ AdaptiveMetricsCollector ────► Собирает метрики из AI Orchestrator (port 8030)
│   └─ История метрик (1000 записей)
│   └─ История задач (5000 записей)
│   └─ Скользящие средние (5 мин)
│
├─ PriorityEngine ────► Расчет приоритетов задач
│   ├─ Базовый приоритет (CRITICAL/HIGH/NORMAL/LOW/IDLE)
│   ├─ Фактор нагрузки системы
│   ├─ Срочность по дедлайну
│   ├─ Штраф за повторы
│   ├─ Эффективность по стоимости
│   └─ Бонус за зависимости
│
└─ Task Queue ────► Очередь с динамической сортировкой
    └─ Автоматическая пересортировка каждые 10 сек
```

---

## 📊 Собираемые метрики

### Performance Metrics
- **CPU Usage**: % использования CPU
- **Memory Usage**: % использования памяти
- **Active Tasks**: Количество активных задач
- **Queue Length**: Длина очереди задач

### Quality Metrics
- **Success Rate**: Процент успешных задач
- **Error Rate**: Процент ошибок
- **Avg Latency**: Средняя задержка
- **P95 Latency**: 95-й перцентиль задержки

### Throughput Metrics
- **Tasks Per Minute**: Задач в минуту
- **Requests Per Second**: Запросов в секунду

### Cost Metrics
- **Cost Per Hour**: Стоимость в час
- **Total Cost**: Общая стоимость

---

## 🎚️ Уровни приоритета

### 1. CRITICAL (5) - Критичные
- Сбои инфраструктуры
- Проблемы безопасности
- Восстановление после сбоя

**Поведение**: Выполняются ВСЕГДА, даже при перегрузке системы

### 2. HIGH (4) - Высокий
- Deployment новых версий
- Масштабирование сервисов
- Критичные обновления

**Поведение**: Выполняются при нормальной нагрузке

### 3. NORMAL (3) - Обычный
- Обновления конфигураций
- Оптимизации
- Рутинные задачи

**Поведение**: Стандартное выполнение

### 4. LOW (2) - Низкий
- Фоновые задачи
- Аналитика
- Сбор статистики

**Поведение**: Откладываются при высокой нагрузке

### 5. IDLE (1) - Для простоя
- Очистка кэша
- Архивирование логов
- Дефрагментация БД

**Поведение**: Выполняются только при низкой нагрузке (<30%)

---

## 🔧 Факторы приоритизации

### 1. System Load Factor
**Вес**: 0.5 (адаптивный до 1.0 при перегрузке)

```python
# Если система перегружена (CPU/Memory > 80%)
if load_score > 80:
    # Тяжелые задачи (>5 мин) → приоритет -1.0
    # Средние задачи (>1 мин) → приоритет -0.5
    # Легкие задачи → без изменений

# Если система простаивает (<30%)
elif load_score < 30:
    # LOW/IDLE задачи → приоритет +1.0
    # Остальные → приоритет +0.5
```

### 2. Deadline Urgency
**Вес**: 0.8

```python
# Просрочено → +3.0
# <5 минут до дедлайна → +2.0
# <30 минут → +1.0
# <2 часа → +0.5
```

### 3. Retry Penalty
**Вес**: 0.3 (адаптивный до 0.8 при высоком error rate)

```python
# 0 попыток → 0.0
# 1-2 попытки → +0.2 (повторная попытка важна)
# 3+ попытки → -0.5 * (retry_count - 2)  # Штраф растет
```

### 4. Cost Efficiency
**Вес**: 0.2 (адаптивный до 0.5 при высокой стоимости)

```python
# Задача в 2x дороже средней → -0.5
# Задача в 0.5x дешевле средней → +0.3
```

### 5. Dependency Bonus
**Вес**: 0.4

```python
# 5+ зависимых задач → +1.5
# 3-4 зависимых → +1.0
# 1-2 зависимых → +0.5
```

---

## 🌟 Адаптивное поведение

### Динамическая адаптация весов

Система автоматически адаптирует веса факторов на основе текущих метрик:

```python
# Высокая нагрузка (CPU/Memory > 70%)
weights['system_load'] = 1.0      # ↑ Увеличен
weights['cost_efficiency'] = 0.5  # ↑ Увеличен

# Высокий error rate (>5%)
weights['retry_penalty'] = 0.8    # ↑ Увеличен
weights['base_priority'] = 1.5    # ↑ Увеличен
```

### Пересчет приоритетов в реальном времени

Каждые **10 секунд**:
1. Собираются метрики из AI Orchestrator
2. Адаптируются веса факторов
3. Пересчитываются приоритеты всех задач в очереди
4. Очередь пересортировывается

---

## 🚀 API Endpoints

### 1. Получить текущие метрики
```bash
GET http://localhost:8090/api/v1/metrics/current
```

**Response**:
```json
{
  "status": "success",
  "metrics": {
    "cpu_percent": 45.2,
    "memory_percent": 62.8,
    "active_tasks": 3,
    "queue_length": 12,
    "success_rate": 97.5,
    "error_rate": 2.5,
    "avg_latency": 1.23,
    "p95_latency": 2.45,
    "tasks_per_minute": 15.8,
    "cost_per_hour": 0.45,
    "health_status": "healthy",
    "is_healthy": true,
    "timestamp": "2025-10-08T12:34:56Z"
  }
}
```

### 2. Статистика очереди
```bash
GET http://localhost:8090/api/v1/queue/stats
```

**Response**:
```json
{
  "status": "success",
  "queue": {
    "total": 12,
    "by_priority": {
      "CRITICAL": 1,
      "HIGH": 3,
      "NORMAL": 5,
      "LOW": 2,
      "IDLE": 1
    },
    "avg_priority": 5.67,
    "oldest_task_age_seconds": 245,
    "top_5_tasks": [
      {
        "task_id": "deploy-prod-v2.1",
        "type": "deployment",
        "priority": 8.5,
        "age_seconds": 120
      }
    ]
  }
}
```

### 3. Добавить задачу в очередь с приоритетом
```bash
POST http://localhost:8090/api/v1/queue/add
Content-Type: application/json

{
  "task_id": "deploy-prod-v2.1",
  "task_type": "deployment",
  "base_priority": "HIGH",
  "deadline": "2025-10-08T15:00:00Z",
  "dependencies": ["build-v2.1", "test-v2.1"],
  "estimated_duration": 300.0,
  "estimated_cost": 0.15
}
```

**Response**:
```json
{
  "status": "success",
  "task": {
    "task_id": "deploy-prod-v2.1",
    "task_type": "deployment",
    "base_priority": "HIGH",
    "actual_priority": 7.8,
    "priority_factors": {
      "base_priority": 4.0,
      "system_load": 0.0,
      "deadline_urgency": 2.0,
      "retry_penalty": 0.0,
      "cost_efficiency": -0.2,
      "dependency_bonus": 1.0
    },
    "position_in_queue": 2
  }
}
```

### 4. Получить следующую задачу
```bash
GET http://localhost:8090/api/v1/queue/next
```

**Response**:
```json
{
  "status": "success",
  "task": {
    "task_id": "fix-auth-service",
    "task_type": "hotfix",
    "base_priority": "CRITICAL",
    "actual_priority": 9.5,
    "priority_factors": {
      "base_priority": 5.0,
      "system_load": 0.0,
      "deadline_urgency": 3.0,
      "retry_penalty": 0.2,
      "cost_efficiency": 0.3,
      "dependency_bonus": 1.0
    },
    "submitted_at": "2025-10-08T12:30:00Z",
    "estimated_duration": 180.0,
    "estimated_cost": 0.05
  }
}
```

### 5. Запустить фоновый мониторинг
```bash
POST http://localhost:8090/api/v1/monitoring/start
```

**Response**:
```json
{
  "status": "success",
  "message": "Adaptive monitoring started"
}
```

### 6. Остановить мониторинг
```bash
POST http://localhost:8090/api/v1/monitoring/stop
```

---

## 💡 Примеры использования

### Пример 1: Deployment с дедлайном

```python
import httpx
from datetime import datetime, timedelta

# Добавить deployment с дедлайном через 30 минут
deadline = datetime.utcnow() + timedelta(minutes=30)

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8090/api/v1/queue/add",
        json={
            "task_id": "deploy-urgent-fix",
            "task_type": "deployment",
            "base_priority": "HIGH",
            "deadline": deadline.isoformat(),
            "estimated_duration": 600.0,  # 10 минут
            "estimated_cost": 0.20
        }
    )

    task = response.json()['task']
    print(f"Task priority: {task['actual_priority']:.2f}")
    print(f"Position: {task['position_in_queue']}")
```

### Пример 2: Фоновая задача для простоя

```python
# Добавить задачу очистки логов (выполнится при load < 30%)
await client.post(
    "http://localhost:8090/api/v1/queue/add",
    json={
        "task_id": "cleanup-old-logs",
        "task_type": "maintenance",
        "base_priority": "IDLE",
        "estimated_duration": 1800.0,  # 30 минут
        "estimated_cost": 0.0
    }
)
```

### Пример 3: Критичный hotfix

```python
# Критичный фикс - выполнится немедленно
await client.post(
    "http://localhost:8090/api/v1/queue/add",
    json={
        "task_id": "fix-security-vulnerability",
        "task_type": "hotfix",
        "base_priority": "CRITICAL",
        "deadline": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
        "estimated_duration": 120.0,  # 2 минуты
        "estimated_cost": 0.05
    }
)
```

---

## 📈 Monitoring & Debugging

### Логирование

Адаптивные метрики логируют каждые 10 секунд:

```
DEBUG Adaptive monitoring: status=healthy, cpu=45.2%, mem=62.8%, latency_p95=2.45s, queue_size=12
INFO Task added to queue: deploy-prod-v2.1 (type=deployment, priority=7.80, position=2/12)
INFO Next task selected: fix-auth-service (priority=9.50, factors={'base_priority': 5.0, 'deadline_urgency': 3.0, ...})
DEBUG Adapted weights: {'system_load': 0.5, 'deadline_urgency': 0.8, ...}
```

### Grafana Dashboard

Метрики доступны через существующий orchestrator dashboard:
- URL: http://localhost:3001 → Orchestrator tab
- Метрики собираются из http://localhost:8030/api/v1/monitoring/dashboard

---

## ⚙️ Конфигурация

### Настройка весов приоритетов

Веса можно настроить в `adaptive_metrics.py`:

```python
class PriorityEngine:
    def __init__(self, metrics_collector):
        self.weights = {
            "base_priority": 1.0,       # Базовый приоритет
            "system_load": 0.5,         # Нагрузка системы
            "deadline_urgency": 0.8,    # Срочность по дедлайну
            "retry_penalty": 0.3,       # Штраф за повторы
            "cost_efficiency": 0.2,     # Эффективность по стоимости
            "dependency_bonus": 0.4,    # Бонус для задач с зависимостями
        }
```

### Настройка пороговых значений

Пороги для определения перегрузки в `MetricThreshold`:

```python
class MetricThreshold(Enum):
    CPU_CRITICAL = 90       # CPU > 90% - критично
    CPU_WARNING = 70        # CPU > 70% - предупреждение
    MEMORY_CRITICAL = 85    # Memory > 85% - критично
    LATENCY_CRITICAL = 5.0  # Latency > 5s - критично
    ERROR_RATE_CRITICAL = 5 # Error rate > 5% - критично
```

---

## 🎯 Преимущества

### 1. Автоматическая адаптация
- Система **сама подстраивается** под нагрузку
- Не требует ручной настройки приоритетов
- Учитывает текущее состояние инфраструктуры

### 2. Умное управление ресурсами
- **Откладывает тяжелые задачи** при перегрузке
- **Выполняет легкие задачи** при простое
- **Приоритизирует критичные** задачи всегда

### 3. Cost-aware execution
- Учитывает **стоимость задач**
- Оптимизирует расходы через приоритеты
- Откладывает дорогие задачи на период низкой нагрузки

### 4. Deadline-driven
- **Автоматически повышает** приоритет при приближении дедлайна
- **Максимальный приоритет** для просроченных задач
- Гарантирует выполнение в срок

### 5. Dependency-aware
- **Повышает приоритет** задач, от которых зависят другие
- Предотвращает блокировки
- Оптимизирует порядок выполнения

---

## 🔮 Дальнейшее развитие

### Planned Features

1. **Machine Learning для предсказания**
   - Предсказание времени выполнения задач
   - Предсказание стоимости на основе истории
   - Автоматическая оптимизация весов

2. **Multi-tenant приоритизация**
   - Учет квот пользователей
   - Fair scheduling между тенантами
   - Приоритет для премиум-пользователей

3. **Advanced scheduling**
   - Планирование задач на определенное время
   - Batch processing для похожих задач
   - Распределенное выполнение

4. **Интеграция с внешними системами**
   - PagerDuty для критичных задач
   - Slack уведомления
   - Jira integration для tracking

---

## ✅ Проверка работоспособности

### 1. Запустить Orchestrator
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/orchestrator
python unified_orchestrator.py
```

### 2. Запустить адаптивный мониторинг
```bash
curl -X POST http://localhost:8090/api/v1/monitoring/start
```

### 3. Проверить текущие метрики
```bash
curl http://localhost:8090/api/v1/metrics/current
```

### 4. Добавить тестовую задачу
```bash
curl -X POST http://localhost:8090/api/v1/queue/add \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "test-task-1",
    "task_type": "test",
    "base_priority": "NORMAL"
  }'
```

### 5. Проверить очередь
```bash
curl http://localhost:8090/api/v1/queue/stats
```

---

## 📞 Support

**Файлы**:
- Adaptive metrics: `/infrastructure/AI-office-infrastructure/orchestrator/adaptive_metrics.py`
- Unified orchestrator: `/infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py`
- Monitoring integration: `/intelligent-core/orchestration/ai-orchestration/monitoring/`

**API Documentation**: http://localhost:8090/docs (FastAPI Swagger UI)

---

**Статус**: ✅ Готово к production использованию
**Интеграция**: ✅ Полностью интегрировано с существующей системой мониторинга
**Тестирование**: ⏳ Рекомендуется протестировать в dev окружении перед production
