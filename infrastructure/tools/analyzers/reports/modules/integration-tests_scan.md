# Module Scan Report: integration-tests

**Дата сканирования:** 2025-10-06 21:10
**Путь:** `platform-services/integration-tests`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 4441 |
| **Python файлов** | 10 |
| **Классов** | 1 |
| **Функций** | 12 |
| **API Endpoints** | 0 |
| **Зависимостей** | 9 |

---

## 🔗 Зависимости (9)


### asyncio
- `asyncio`

### datetime
- `datetime`

### dotenv
- `dotenv`

### httpx
- `httpx`

### jwt
- `jwt`

### os
- `os`

### pytest
- `pytest`

### time
- `time`

### typing
- `typing`

---

## 💻 Классы (1)

- **EventBusHelper** (1 методов) - `conftest.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 9341 символов (376 строк)

**Превью:**
```
# BCM Platform Integration Tests

Comprehensive integration tests for inter-service communication in the BCM platform.

## Overview

This directory contains end-to-end integration tests that verify:
- Cross-service workflows (BIA → Planning → Plans → Compliance)
- API integration and data flow
- EventBus event publishing and consumption
- Authentication and authorization across services
- Data consistency and referential integrity
- Performance benchmarks
- Error handling and resilience

## Directory Structure

```
integration-tests/
├── README.md                           # This file
├── pytest.ini                          # Pytest configuration
├── requirements.txt                    # Test dependencies
├── conftest.py                         # Shared fixtures
├── .env.test                           # Test environment variables
├── docker-compose.test.yml             # Test service configuration
├── run_integration_tests.sh            # Main test runner script
├── wait-for-services.s
```

---

## ⚙️ Конфигурация

- `requirements.txt` → `platform-services/integration-tests/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 19
**Директорий:** 1
