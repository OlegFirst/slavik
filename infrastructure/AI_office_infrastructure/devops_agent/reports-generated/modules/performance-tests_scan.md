# Module Scan Report: performance-tests

**Дата сканирования:** 2025-10-08 15:17
**Путь:** `platform-services/performance-tests`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 4248 |
| **Python файлов** | 12 |
| **Классов** | 12 |
| **Функций** | 86 |
| **API Endpoints** | 0 |
| **Зависимостей** | 21 |

---

## 🔗 Зависимости (21)


### argparse
- `argparse`

### asyncio
- `asyncio`

### asyncpg
- `asyncpg`

### csv
- `csv`

### datetime
- `datetime`

### dotenv
- `dotenv`

### json
- `json`

### locust
- `locust`

### locust.contrib.fasthttp
- `locust.contrib.fasthttp`

### logging
- `logging`

### os
- `os`

### psutil
- `psutil`

### pytest
- `pytest`

### random
- `random`

### requests
- `requests`

### runtime
- `runtime/eventbus`

### string
- `string`

### sys
- `sys`

### time
- `time`

### typing
- `typing`

### yaml
- `yaml`

---

## 💻 Классы (12)

- **HeavyLoadUser** (16 методов) - `scenario_heavy.py`
- **MediumLoadUser** (14 методов) - `scenario_medium.py`
- **StressTestUser** (13 методов) - `scenario_stress.py`
- **MetricsCollector** (10 методов) - `metrics_collector.py`
- **LightLoadUser** (9 методов) - `scenario_light.py`
- **BIAServiceUser** (7 методов) - `locustfile.py`
- **ReportGenerator** (7 методов) - `generate_report.py`
- **PerformanceRegression** (6 методов) - `performance_regression.py`
- **ComplianceServiceUser** (6 методов) - `locustfile.py`
- **PlanningServiceUser** (5 методов) - `locustfile.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 1244 символов (73 строк)

**Превью:**
```
# performance-tests

> 📚 Library модуль платформы

## 📊 Обзор

| Метрика | Значение |
|---------|----------|
| **Строк кода** | 4,248 |
| **Python файлов** | 12 |
| **Классов** | 12 |
| **Функций** | 86 |
| **API Endpoints** | 0 |
| **Зависимостей** | 21 |

**Тип модуля:** 📚 Library
**Последнее обновление:** 2025-10-07

---

## 🏗️ Архитектура

### Ключевые классы

- **HeavyLoadUser** (16 методов) - `scenario_heavy.py`
- **MediumLoadUser** (14 методов) - `scenario_medium.py`
- **StressTestUser** (13 методов) - `scenario_stress.py`
- **MetricsCollector** (10 методов) - `metrics_collector.py`
- **LightLoadUser** (9 методов) - `scenario_light.py`

### Функции

Всего публичных функций: 86

---

## 🔗 Зависимости

### Инфраструктура
- `runtime/eventbus`

---

## 💻 Использование

### Импорт

```python
from performance_tests import ...
```

---

## ⚙️ Конфигурация

**Конфигурационные файлы:**

- `requirements.txt`

---


---

## 📚 Дополнительные материалы

- [Архитектура платформы](../../doc-pr
```

---

## ⚙️ Конфигурация

- `requirements.txt` → `platform-services/performance-tests/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 22
**Директорий:** 3
