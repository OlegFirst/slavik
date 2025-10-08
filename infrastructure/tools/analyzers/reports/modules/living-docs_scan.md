# Module Scan Report: living-docs

**Дата сканирования:** 2025-10-06 21:10
**Путь:** `platform-services/living-docs`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 3255 |
| **Python файлов** | 9 |
| **Классов** | 24 |
| **Функций** | 0 |
| **API Endpoints** | 10 |
| **Зависимостей** | 24 |

---

## 🔗 Зависимости (24)


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
**Размер:** 15423 символов (689 строк)

**Превью:**
```
# 📚 Living Documentation

**Innovation Level:** 🤯🤯🤯🤯🤯
**Port:** 8034
**Purpose:** Documentation that Lives, Learns, and Evolves

## 📚 Documentation

Вся документация находится в папке [`docs/`](docs/):
- **[Архитектура](docs/ARCHITECTURE.md)** - детальная архитектура системы
- **[Интеграция](docs/INTEGRATION_COMPLETE.md)** - интеграция с платформой
- **[Анализ и улучшения](docs/ANALYSIS_AND_IMPROVEMENTS.md)** - ⚠️ критичные проблемы и план реализации

---

## 🎯 THE BREAKTHROUGH

**Problem with Traditional Documentation:**
```
❌ Static - Written once, becomes outdated
❌ Generic - Same for everyone
❌ Boring - Text walls, no interactivity
❌ Disconnected - Separate from real usage
❌ Manual - Requires constant updates
```

**Living Documentation Solution:**
```
✅ Dynamic - Updates itself from usage
✅ Personalized - Adapts to each user
✅ Interactive - AI Q&A, examples on demand
✅ Connected - Learns from every interaction
✅ Autonomous - Self-evolving knowledge base
```

**Think:** Netflix rec
```

---

## ⚙️ Конфигурация

- `requirements.txt` → `platform-services/living-docs/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 16
**Директорий:** 5
