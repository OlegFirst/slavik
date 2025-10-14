# Центральный Мозг - Монитор Состояния

**Central Brain State Monitor**

## Концепция

Центральный Мозг получает ТОЛЬКО **фактическое состояние** системы и использует его для принятия **стратегических решений**.

### Что Центральный Мозг НЕ делает

❌ НЕ проводит проверки соответствия
❌ НЕ знает, как "должно быть"
❌ НЕ сравнивает с ожидаемой конфигурацией
❌ НЕ выдает рекомендации по исправлению

**Это задача Проектного Менеджера.**

### Что Центральный Мозг делает

✅ Получает фактическое состояние системы
✅ Оценивает доступные ресурсы
✅ Принимает стратегические решения
✅ Предлагает стратегию масштабирования
✅ Определяет, можно ли развернуть новый сервис

## Архитектура

```
┌──────────────────────────────────────────────────────────────┐
│                    ПРОЕКТНЫЙ МЕНЕДЖЕР                         │
│                 (Проверки Соответствия)                       │
│                                                               │
│  • Конфликты портов                                          │
│  • Интеграция с метриками                                    │
│  • Подключение к БД                                          │
│  • KPI регистрация                                           │
│  • EventBus события                                          │
│  • Контроль оркестратором                                    │
│                                                               │
│  Знает: КАК ДОЛЖНО БЫТЬ                                      │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        │ Фактическое состояние
                        │ (ТОЛЬКО факты)
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                    ЦЕНТРАЛЬНЫЙ МОЗГ                           │
│                 (Стратегические Решения)                      │
│                                                               │
│  • Оценка ресурсов                                           │
│  • Стратегия масштабирования                                 │
│  • Принятие решений о развертывании                          │
│  • Распределение ресурсов                                    │
│                                                               │
│  Знает: ЧТО ЕСТЬ                                             │
└──────────────────────────────────────────────────────────────┘
```

## Использование

### Однократный Сбор Состояния

```python
from infrastructure.central_brain.state_monitor import CentralBrainStateMonitor

monitor = CentralBrainStateMonitor()

# Собрать текущее состояние
await monitor.update_state()

# Получить доступные ресурсы
resources = monitor.get_available_resources()

print(f"Сервисов: {resources['total_services']}")
print(f"Мониторинг: {resources['monitoring_coverage'] * 100:.0f}%")
print(f"БД: {resources['database_coverage'] * 100:.0f}%")
```

### Проверка Возможности Развертывания

```python
# Можно ли развернуть новый сервис?
can_deploy, reason = monitor.can_deploy_new_service(
    service_name='new-service',
    requires_db=True,
    requires_metrics=True
)

if can_deploy:
    print(f"✅ Можно развернуть: {reason}")
    # Разверните сервис
else:
    print(f"❌ Нельзя развернуть: {reason}")
    # Подождите или освободите ресурсы
```

### Стратегия Масштабирования

```python
# Получить рекомендации по масштабированию
strategy = monitor.suggest_scaling_strategy()

print(f"Стратегия: {strategy['strategy']}")
print(f"Приоритет: {strategy['priority']}")
print(f"Действие: {strategy['action']}")
print(f"Причина: {strategy['reason']}")

# Примеры стратегий:
# - 'emergency' - критичная ситуация, БД упали
# - 'monitoring_recovery' - восстановить мониторинг
# - 'improve_monitoring' - улучшить покрытие мониторинга
# - 'maintain' - все в порядке, поддерживать состояние
```

### Непрерывный Мониторинг

```python
# Запустить непрерывный мониторинг (обновление каждые 60с)
await monitor.continuous_monitoring(interval_seconds=60)

# Будет непрерывно:
# 1. Собирать состояние
# 2. Оценивать ресурсы
# 3. Предлагать стратегию
# 4. Логировать результаты
```

### Запуск из Командной Строки

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/central-brain

# Однократный сбор состояния
python state_monitor.py
```

## Пример Вывода

```
================================================================================
ФАКТИЧЕСКОЕ СОСТОЯНИЕ СИСТЕМЫ (для Центрального Мозга)
================================================================================
✅ Система работает
   Сервисов: 24
   Мониторинг: 75% покрытие
   БД: 83% подключено
   Здоровье: ✅ Здорова

СТРАТЕГИЯ:
  IMPROVE_MONITORING (приоритет: medium)
  Действие: Подключить больше сервисов к Prometheus
  Причина: Только 75% сервисов мониторятся
================================================================================
```

## Типы Стратегий

### EMERGENCY (приоритет: critical)
**Когда**: Критичные БД (PostgreSQL/Redis) недоступны
**Действие**: Восстановить БД немедленно
**Пример**:
```python
{
    'strategy': 'emergency',
    'priority': 'critical',
    'action': 'Восстановить критичные БД немедленно',
    'reason': 'PostgreSQL недоступен'
}
```

### MONITORING_RECOVERY (приоритет: high)
**Когда**: Prometheus недоступен
**Действие**: Восстановить мониторинг
**Пример**:
```python
{
    'strategy': 'monitoring_recovery',
    'priority': 'high',
    'action': 'Восстановить Prometheus для мониторинга',
    'reason': 'Мониторинг недоступен - система работает вслепую'
}
```

### IMPROVE_MONITORING (приоритет: medium)
**Когда**: Менее 50% сервисов мониторятся
**Действие**: Подключить больше сервисов к Prometheus
**Пример**:
```python
{
    'strategy': 'improve_monitoring',
    'priority': 'medium',
    'action': 'Подключить больше сервисов к Prometheus',
    'reason': 'Только 40% сервисов мониторятся'
}
```

### MAINTAIN (приоритет: low)
**Когда**: Все работает нормально
**Действие**: Поддерживать текущее состояние
**Пример**:
```python
{
    'strategy': 'maintain',
    'priority': 'low',
    'action': 'Поддерживать текущее состояние',
    'reason': 'Система работает в штатном режиме'
}
```

## Интеграция с Проектным Менеджером

Центральный Мозг получает состояние от Проектного Менеджера:

```python
# Проектный Менеджер собирает ФАКТИЧЕСКОЕ состояние
from infrastructure.tools.project_manager import ComplianceCheckRunner

runner = ComplianceCheckRunner()
state_data = runner.export_state_for_central_brain()

# state_data содержит ТОЛЬКО факты:
{
  "timestamp": "2025-10-09T14:30:00",
  "ports": {
    "total_ports_listening": 15,
    "ports": [...]
  },
  "metrics": {
    "prometheus_available": true,
    "services_with_metrics": 18
  },
  "databases": {
    "postgres_available": true,
    "services_connected": 20
  }
}

# Центральный Мозг использует это для решений
monitor = CentralBrainStateMonitor()
state = await monitor.collect_state_from_project_manager()

# Принимает стратегические решения
strategy = monitor.suggest_scaling_strategy()
```

## API

### SystemState
```python
@dataclass
class SystemState:
    timestamp: datetime
    ports_available: int
    ports_used: int
    prometheus_available: bool
    grafana_available: bool
    services_with_metrics: int
    postgres_available: bool
    redis_available: bool
    services_with_db: int
    total_services: int
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
```

### get_available_resources()
```python
{
    'available': True,
    'timestamp': '2025-10-09T14:30:00',
    'can_allocate_port': True,
    'monitoring_available': True,
    'monitoring_coverage': 0.75,
    'databases_available': True,
    'database_coverage': 0.83,
    'total_services': 24,
    'system_healthy': True
}
```

### can_deploy_new_service(service_name, requires_db, requires_metrics)
```python
# Возвращает: (can_deploy: bool, reason: str)
(True, "Все необходимые ресурсы доступны")
# или
(False, "PostgreSQL недоступен")
```

### suggest_scaling_strategy()
```python
{
    'strategy': 'maintain',
    'priority': 'low',
    'action': 'Поддерживать текущее состояние',
    'reason': 'Система работает в штатном режиме'
}
```

## Различие с Проектным Менеджером

| Аспект | Центральный Мозг | Проектный Менеджер |
|--------|------------------|-------------------|
| **Входные данные** | Фактическое состояние | Требования + факты |
| **Выходные данные** | Стратегические решения | Отчеты о соответствии |
| **Проверки** | Нет | Да (6 приоритетов) |
| **Знание** | Что ЕСТЬ | Как ДОЛЖНО быть |
| **Цель** | Оптимальная работа | Соответствие требованиям |
| **Принятие решений** | Стратегические | Тактические |

## Файлы

```
infrastructure/central-brain/
├── README.md           # Этот файл
└── state_monitor.py    # Монитор состояния
```

---

**Created**: 2025-10-09
**Author**: Центральный Мозг
**Status**: ✅ Базовая версия реализована
