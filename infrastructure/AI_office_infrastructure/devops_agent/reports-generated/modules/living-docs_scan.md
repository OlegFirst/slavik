# Module Scan Report: living-docs

**Дата сканирования:** 2025-10-08 15:17
**Путь:** `platform-services/living-docs`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 3262 |
| **Python файлов** | 12 |
| **Классов** | 24 |
| **Функций** | 0 |
| **API Endpoints** | 10 |
| **Зависимостей** | 26 |

---

## 🔗 Зависимости (26)


### api
- `api`

### asyncio
- `asyncio`

### collections
- `collections`

### config
- `config`

### contextlib
- `contextlib`

### database
- `database/postgresql`

### datetime
- `datetime`

### external
- `external/anthropic`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### hashlib
- `hashlib`

### httpx
- `httpx`

### json
- `json`

### logging
- `logging`

### os
- `os`

### pathlib
- `pathlib`

### pydantic
- `pydantic`

### pydantic_settings
- `pydantic_settings`

### services.ai_example_generator
- `services.ai_example_generator`

### services.documentation_evolution_engine
- `services.documentation_evolution_engine`

### services.personalization_service
- `services.personalization_service`

### shared
- `shared/database`

### sys
- `sys`

### typing
- `typing`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

---

## 🌐 API Endpoints (10)

- **GET** `/` (файл: `main.py`)
- **GET** `/health` (файл: `main.py`)
- **GET** `/stats` (файл: `main.py`)
- **GET** `/{page_id}` (файл: `documentation.py`)
- **POST** `/examples/generate` (файл: `documentation.py`)
- **POST** `/feedback` (файл: `documentation.py`)
- **GET** `/search` (файл: `documentation.py`)
- **GET** `/journey/{goal}` (файл: `documentation.py`)
- **GET** `/gaps` (файл: `documentation.py`)
- **GET** `/improvements` (файл: `documentation.py`)

---

## 💻 Классы (24)

- **AIExampleGenerator** (8 методов) - `ai_example_generator.py`
- **DocumentationEvolutionEngine** (6 методов) - `documentation_evolution_engine.py`
- **InteractiveExampleRunner** (3 методов) - `ai_example_generator.py`
- **MockResult** (2 методов) - `dependencies.py`
- **PersonalizationService** (2 методов) - `personalization_service.py`
- **UserJourneyPersonalizer** (2 методов) - `personalization_service.py`
- **MockResponse** (1 методов) - `dependencies.py`
- **MockContent** (1 методов) - `dependencies.py`
- **ExampleLibrary** (1 методов) - `ai_example_generator.py`
- **LivingDocsConfig** (0 методов) - `config.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 1673 символов (105 строк)

**Превью:**
```
# living-docs

> 🌐 API Service модуль платформы

## 📊 Обзор

| Метрика | Значение |
|---------|----------|
| **Строк кода** | 3,255 |
| **Python файлов** | 9 |
| **Классов** | 24 |
| **Функций** | 0 |
| **API Endpoints** | 10 |
| **Зависимостей** | 24 |

**Тип модуля:** 🌐 API Service
**Последнее обновление:** 2025-10-07

---

## 🌐 API Endpoints

### GET (8)

- `/`
- `/gaps`
- `/health`
- `/improvements`
- `/journey/{goal}`

### POST (2)

- `/examples/generate`
- `/feedback`

[→ Полная документация API](./API.md)

---

## 🏗️ Архитектура

### Ключевые классы

- **AIExampleGenerator** (8 методов) - `ai_example_generator.py`
- **DocumentationEvolutionEngine** (6 методов) - `documentation_evolution_engine.py`
- **InteractiveExampleRunner** (3 методов) - `ai_example_generator.py`
- **MockResult** (2 методов) - `dependencies.py`
- **PersonalizationService** (2 методов) - `personalization_service.py`

---

## 🔗 Зависимости

### Внутренние
- `shared/database`

### Инфраструктура
- `database/pos
```

---

## ⚙️ Конфигурация

- `.env.example` → `platform-services/living-docs/.env.example`
- `requirements.txt` → `platform-services/living-docs/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 23
**Директорий:** 5
