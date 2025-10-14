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
- `database/postgresql`
- `shared/database`

### Внешние сервисы
- `external/anthropic`

---

## 💻 Использование

### Запуск сервиса

```bash
cd living-docs
python3 main.py
```

### Пример запроса

```python
import httpx

response = httpx.get("http://localhost:8000/")
print(response.json())
```

---

## ⚙️ Конфигурация

**Конфигурационные файлы:**

- `requirements.txt`

---


---

## 📚 Дополнительные материалы

- [Архитектура платформы](../../doc-project/FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md)
- [API Reference](./API.md) ✅
- [Тесты](./tests/) ⚠️ Тесты отсутствуют

**Сгенерировано автоматически:** 2025-10-07 05:07
**Инструмент:** `tools/generators/documentation_generator.py`
