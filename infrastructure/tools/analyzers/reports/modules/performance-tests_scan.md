# Module Scan Report: performance-tests

**Дата сканирования:** 2025-10-06 21:10
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
**Размер:** 12840 символов (501 строк)

**Превью:**
```
# BCM Platform Performance Testing Suite

Comprehensive performance testing and benchmarking suite for the BCM (Business Continuity Management) Platform, compliant with ISO 22301:2019 requirements.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Running Tests](#running-tests)
- [Test Scenarios](#test-scenarios)
- [Interpreting Results](#interpreting-results)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This performance testing suite provides:

- **Load Testing**: Locust-based load tests for realistic production scenarios
- **Benchmarking**: pytest-benchmark tests for API, database, and cache operations
- **Metrics Collection**: Comprehensive system and application metrics
- **Automated Reporting**: HTML reports with visualizations and recommendations
- **Regression Detection**: Automatic detection of performance degradation
- **CI/CD Integr
```

---

## ⚙️ Конфигурация

- `requirements.txt` → `platform-services/performance-tests/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 22
**Директорий:** 3
