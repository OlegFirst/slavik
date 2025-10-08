# Module Scan Report: tools

**Дата сканирования:** 2025-10-08 16:44
**Путь:** `infrastructure/tools`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 7749 |
| **Python файлов** | 22 |
| **Классов** | 23 |
| **Функций** | 18 |
| **API Endpoints** | 3 |
| **Зависимостей** | 26 |

---

## 🔗 Зависимости (26)


### argparse
- `argparse`

### ast
- `ast`

### asyncio
- `asyncio`

### collections
- `collections`

### dataclasses
- `dataclasses`

### datetime
- `datetime`

### docker
- `docker`

### docker_manager
- `docker_manager`

### external
- `external/anthropic`

### httpx
- `httpx`

### jinja2
- `jinja2`

### json
- `json`

### logging
- `logging`

### math
- `math`

### matplotlib.pyplot
- `matplotlib.pyplot`

### networkx
- `networkx`

### os
- `os`

### pathlib
- `pathlib`

### plotly.express
- `plotly.express`

### plotly.graph_objects
- `plotly.graph_objects`

### plotly.subplots
- `plotly.subplots`

### re
- `re`

### subprocess
- `subprocess`

### sys
- `sys`

### typing
- `typing`

### yaml
- `yaml`

---

## 🌐 API Endpoints (3)

- **POST** `/path` (файл: `api_mapper.py`)
- **POST** `[^)]*?` (файл: `api_mapper.py`)
- **GET** `/metrics` (файл: `metrics_discovery.py`)

---

## 💻 Классы (23)

- **DocumentationGenerator** (17 методов) - `documentation_generator.py`
- **ServiceDiscovery** (16 методов) - `discover_services.py`
- **DependencyValidator** (15 методов) - `dependency_validator.py`
- **MetricsDiscovery** (15 методов) - `metrics_discovery.py`
- **ModuleScanner** (13 методов) - `module_scanner.py`
- **DependencyMapper** (12 методов) - `dependency_mapper.py`
- **ASTAnalyzer** (12 методов) - `ast_analyzer.py`
- **APIMapper** (12 методов) - `api_mapper.py`
- **ImprovedComposeGenerator** (11 методов) - `generate_improved_compose.py`
- **EventCatalogGenerator** (10 методов) - `event_catalog_generator.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 12150 символов (518 строк)

**Превью:**
```
# AI-Platform-ISO: Automation & Analysis Toolkit

> **Полная автоматизация анализа, документирования и визуализации микросервисов**

## 📋 Содержание

- [Быстрый старт](#быстрый-старт)
- [Инструменты](#инструменты)
- [Использование](#использование)
- [Результаты](#результаты)
- [Лицензии](#лицензии)

---

## 🚀 Быстрый старт

### 1. Установка (5 минут)

```bash
cd /Users/MD/AI-Platform-ISO
chmod +x tools/setup.sh
./tools/setup.sh
```

Скрипт установит все необходимые инструменты и создаст структуру директорий.

### 2. Запуск полного анализа (5 минут)

```bash
chmod +x tools/run_analysis.sh
./tools/run_analysis.sh
```

Этот скрипт выполнит:
- ✅ AST-анализ (функции, классы, эндпоинты)
- ✅ Карту зависимостей между модулями
- ✅ Анализ сложности кода (Cyclomatic, Cognitive)
- ✅ Сканирование безопасности (Bandit OWASP)
- ✅ Анализ качества кода (Pylint)
- ✅ Интерактивные дашборды

### 3. Просмотр результатов

```bash
# Открыть главный дашборд
open tools/reports/dashboard.html

# Открыть UI blue
```

---

## ⚙️ Конфигурация

- `requirements.txt` → `infrastructure/tools/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 197
**Директорий:** 13
