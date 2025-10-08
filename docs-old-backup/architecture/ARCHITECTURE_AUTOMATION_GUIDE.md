# Architecture Automation Guide
## Полное руководство по автоматизации архитектурной документации

**Создано:** 2025-10-06

---

## 📋 Содержание

1. [Обзор инструментов](#обзор-инструментов)
2. [Quick Start](#quick-start)
3. [Детальное использование](#детальное-использование)
4. [CI/CD интеграция](#cicd-интеграция)
5. [Troubleshooting](#troubleshooting)

---

## 🛠 Обзор инструментов

### 1. dependency_validator.py
**Что делает:** Сканирует реальный код и сравнивает с документацией

**Когда использовать:**
- После добавления новых сервисов
- Перед коммитом изменений
- При code review

**Результат:**
- ✅ Точность документации (%)
- ❌ Список недокументированных зависимостей
- ⚠️ Устаревшие зависимости
- 📊 JSON отчет

---

### 2. dependency_reconciler.py
**Что делает:** Автоматически исправляет SERVICE_CATALOG.yaml

**Когда использовать:**
- После валидации (если найдены ошибки)
- При реорганизации кода
- Для bulk updates

**Результат:**
- 🆕 Добавлены недостающие сервисы
- 📌 Обновлены зависимости
- 💾 Создан backup (.yaml.backup)
- 📝 Markdown отчет

---

### 3. C4 Model Diagrams
**Что делает:** Визуализация архитектуры на 3 уровнях

**Файлы:**
- `C4_LEVEL1_SYSTEM_CONTEXT_COMPLETE.md` - Взаимодействие с внешним миром
- `C4_LEVEL2_CONTAINERS.md` - Все сервисы, порты, зависимости
- `C4_LEVEL3_COMPONENTS.md` - Внутренняя структура ключевых сервисов

**Просмотр:**
```bash
# VS Code: Cmd+Shift+V для preview
# GitHub: автоматический рендеринг Mermaid
```

---

### 4. CI/CD Pipeline
**Что делает:** Автоматическая валидация при каждом коммите

**Триггеры:**
- Push в main/develop
- Pull Request
- Ежедневно в 2:00 UTC

**Действия:**
- ✅ Запускает dependency_validator.py
- ❌ Блокирует PR при critical errors
- 🤖 Создает auto-fix PR (опционально)

---

## 🚀 Quick Start

### Шаг 1: Проверить текущее состояние

```bash
# Запустить валидацию
python3 tools/analyzers/dependency_validator.py

# Результат:
# ✅ Services documented: 21
# ✅ Services in code: 40
# 📊 Documentation accuracy: 0.0%
# ❌ Critical errors: 6
# ❌ High errors: 39
```

### Шаг 2: Исправить автоматически

```bash
# Dry run (без изменений)
python3 tools/analyzers/dependency_reconciler.py --dry-run

# Применить изменения
python3 tools/analyzers/dependency_reconciler.py --auto-fix

# Результат:
# ✅ Backup saved: docs/architecture/SERVICE_CATALOG.yaml.backup
# ✅ Updated: docs/architecture/SERVICE_CATALOG.yaml
# ✅ CHANGES APPLIED:
#   • Added 22 services
#   • Updated dependencies for 36 services
```

### Шаг 3: Проверить C4 диаграммы

```bash
# Открыть в VS Code
code docs/architecture/C4_LEVEL1_SYSTEM_CONTEXT_COMPLETE.md

# Нажать Cmd+Shift+V для preview
```

### Шаг 4: Commit & Push

```bash
git add docs/architecture/SERVICE_CATALOG.yaml
git commit -m "🤖 Update architecture documentation"
git push

# CI/CD автоматически запустит валидацию
```

---

## 📖 Детальное использование

### dependency_validator.py

**Полный синтаксис:**
```bash
python3 tools/analyzers/dependency_validator.py
```

**Что сканируется:**
- `intelligent-core/*/` - все AI сервисы
- `platform-services/*/` - все бизнес-сервисы
- `infrastructure/*/` - все инфраструктурные сервисы

**Как работает:**
1. Парсит Python AST для всех `.py` файлов
2. Извлекает import statements
3. Классифицирует зависимости (database/postgresql, runtime/eventbus, etc.)
4. Сравнивает с `SERVICE_CATALOG.yaml`
5. Генерирует отчет в `tools/reports/dependency_validation.json`

**Классификация зависимостей:**
```python
# Примеры автоматической классификации
import psycopg2          → database/postgresql
import qdrant_client     → database/vector-db
from eventbus import *   → runtime/eventbus
import temporal          → external/temporal-cloud
from shared.database import * → shared/database
```

**Результаты:**
```json
{
  "stats": {
    "total_services_documented": 21,
    "total_services_in_code": 40,
    "total_errors": 45,
    "total_warnings": 29,
    "critical_errors": 6,
    "high_errors": 39,
    "accuracy": 0.0
  },
  "errors": [
    {
      "type": "undocumented_dependency",
      "service": "workflow-engine",
      "missing_dependencies": [
        "shared/database",
        "database/postgresql"
      ],
      "severity": "HIGH",
      "message": "workflow-engine has undocumented dependencies: ..."
    }
  ]
}
```

**Exit codes:**
- `0` - Success (no critical errors)
- `1` - Failure (critical errors or > 5 high errors)

---

### dependency_reconciler.py

**Полный синтаксис:**
```bash
# Dry run (просмотр без изменений)
python3 tools/analyzers/dependency_reconciler.py --dry-run

# Auto fix (применить изменения)
python3 tools/analyzers/dependency_reconciler.py --auto-fix
```

**Что делает:**

**1. Анализ расхождений:**
```python
{
  "missing_services": [
    "orchestration",      # Есть в коде, нет в catalog
    "expertise-center",
    ...
  ],
  "missing_dependencies": {
    "workflow-engine": [  # Зависимости не задокументированы
      "shared/database",
      "database/postgresql"
    ]
  },
  "obsolete_dependencies": {
    "living_docs": [      # Задокументированы, но не используются
      "database/vector-db"
    ]
  }
}
```

**2. Автоматические исправления:**

- **Добавление сервисов:**
```yaml
# Автоматически создается:
ai_foundation:
  orchestration:
    type: service
    location: intelligent-core/orchestration
    technology: [Python 3.11, FastAPI]
    dependencies:
      infrastructure: [database/postgresql, runtime/eventbus]
      external: [external/temporal-cloud]
    status: discovered
    auto_generated: true
```

- **Обновление зависимостей:**
```yaml
# До:
workflow-engine:
  dependencies:
    infrastructure: [database/postgresql]

# После:
workflow-engine:
  dependencies:
    infrastructure: [database/postgresql, runtime/eventbus]
    internal: [shared/database, ai_foundation/workflow_intelligence]
```

**3. Backup:**
```bash
# Автоматически создается backup
docs/architecture/SERVICE_CATALOG.yaml.backup

# Восстановление:
mv SERVICE_CATALOG.yaml.backup SERVICE_CATALOG.yaml
```

**4. Отчет:**
```markdown
# tools/reports/dependency_reconciliation.md

============================================================
📊 DEPENDENCY RECONCILIATION REPORT
============================================================

🆕 MISSING SERVICES (22):
  • orchestration
  • expertise-center
  ...

📌 MISSING DEPENDENCIES (36 services):
  • workflow-engine: shared/database, database/postgresql
  ...

✅ CHANGES APPLIED:
  • Added 22 services
  • Updated dependencies for 36 services
```

---

### C4 Model Diagrams

#### Level 1: System Context

**Файл:** `C4_LEVEL1_SYSTEM_CONTEXT_COMPLETE.md`

**Что показывает:**
- 👤 Все роли пользователей (BCM Manager, Compliance Officer, etc.)
- 🤖 AI-Platform-ISO как единая система
- ☁️ Внешние системы (Temporal, Supabase, Qdrant, Redis, etc.)
- 🔄 Основные взаимодействия

**Когда использовать:**
- Презентации для стейкхолдеров
- Онбординг новых разработчиков
- Документация для бизнеса

#### Level 2: Containers

**Файл:** `C4_LEVEL2_CONTAINERS.md`

**Что показывает:**
- 📦 Все 48 сервисов (11 AI + 11 Platform + 23 Infrastructure + 3 External)
- 🔌 Реальные порты (:8000, :8001, etc.)
- 🔗 Все зависимости между сервисами
- 🔥 SPOF анализ (Single Point of Failure)
- 📊 Database schemas
- 🛡️ Security boundaries

**Когда использовать:**
- Архитектурные ревью
- Планирование деплоймента
- Troubleshooting performance issues
- Capacity planning

#### Level 3: Components

**Файл:** `C4_LEVEL3_COMPONENTS.md`

**Что показывает:**
- 🧩 Внутренняя структура ключевых сервисов:
  - Workflow Intelligence (THE BRAIN)
  - API Gateway
  - BIA Service
  - AI Workflow Optimizer
  - EventBus
- 📝 Классы и модули
- 🔄 Паттерны (Repository, Service Layer, Factory, Circuit Breaker)
- 💻 Примеры кода

**Когда использовать:**
- Code review
- Рефакторинг
- Добавление новых фич
- Debugging

---

## 🔄 CI/CD Интеграция

### GitHub Actions Workflow

**Файл:** `.github/workflows/architecture-validation.yml`

### Job 1: validate-architecture

**Триггеры:**
- Push в main/develop
- Pull Request
- Schedule: ежедневно в 2:00 UTC

**Шаги:**
1. Checkout code
2. Setup Python 3.11
3. Install dependencies (pyyaml)
4. **Run dependency_validator.py**
5. Upload validation report (artifact)
6. **Check results:**
   - CRITICAL_ERRORS > 0 → ❌ FAIL
   - HIGH_ERRORS > 10 → ⚠️ FAIL
   - Иначе → ✅ PASS

**При failure:**
- Комментирует PR с деталями ошибок
- Предлагает команду для исправления

### Job 2: auto-reconcile (optional)

**Условия:**
- Запускается только при failure
- Только на main/develop (НЕ на PR)

**Шаги:**
1. Run `dependency_reconciler.py --auto-fix`
2. Если есть изменения:
   - Создает новую ветку `auto-reconcile-architecture`
   - Создает PR с изменениями
   - Помечает PR как "automated"

### Job 3: validate-c4-diagrams

**Проверяет:**
- Наличие всех C4 файлов
- Файлы не пустые
- (TODO) Валидация Mermaid синтаксиса

---

## 🔧 Troubleshooting

### Проблема: "YAML format error"

**Ошибка:**
```
yaml.composer.ComposerError: expected a single document in the stream
```

**Решение:**
```bash
# Проверить наличие лишних '---' разделителей
grep -n "^---$" docs/architecture/SERVICE_CATALOG.yaml

# Удалить лишние разделители
sed -i '' '7d' docs/architecture/SERVICE_CATALOG.yaml
```

---

### Проблема: "Set is not JSON serializable"

**Ошибка:**
```
TypeError: Object of type set is not JSON serializable
```

**Решение:**
Уже исправлено в dependency_validator.py:
```python
# Преобразование sets → lists
'documented_dependencies': {k: list(v) for k, v in self.documented_dependencies.items()}
```

---

### Проблема: "Service location not found"

**Ошибка:**
```
[CRITICAL] workflow_intelligence location does not exist: intelligent-core/workflow_intelligence
```

**Решение:**
1. Проверить реальный путь:
```bash
ls -la intelligent-core/workflow_intelligence
```

2. Обновить `_find_service_location()` в reconciler:
```python
path_mapping = {
    'workflow_intelligence': 'intelligent-core/workflow_intelligence',  # Correct path
    ...
}
```

---

### Проблема: "Accuracy 0%"

**Причина:**
- Большинство сервисов не задокументированы
- SERVICE_CATALOG.yaml сильно устарел

**Решение:**
```bash
# Автоматическое исправление
python3 tools/analyzers/dependency_reconciler.py --auto-fix

# Проверить результат
python3 tools/analyzers/dependency_validator.py

# Должна вырасти точность до ~80-90%
```

---

## 📊 Метрики качества

### Целевые показатели:

| Метрика | Target | Critical |
|---------|--------|----------|
| **Documentation Accuracy** | > 90% | < 50% |
| **Critical Errors** | 0 | > 0 |
| **High Errors** | < 5 | > 10 |
| **Total Warnings** | < 20 | > 50 |
| **Services Documented** | 100% (40/40) | < 70% |

---

## 🎯 Best Practices

### 1. Регулярная валидация
```bash
# Перед каждым коммитом
python3 tools/analyzers/dependency_validator.py

# Если ошибки:
python3 tools/analyzers/dependency_reconciler.py --auto-fix
git add docs/architecture/SERVICE_CATALOG.yaml
git commit -m "🤖 Update architecture docs"
```

### 2. Code Review
- Проверять C4 диаграммы при добавлении новых сервисов
- Обновлять SERVICE_CATALOG.yaml вручную для важных изменений
- Использовать auto-fix только для bulk updates

### 3. Documentation First
- При создании нового сервиса:
  1. Добавить в SERVICE_CATALOG.yaml
  2. Обновить C4 Level 2
  3. Написать код
  4. Запустить валидацию

### 4. CI/CD Trust
- Не игнорировать failing checks
- Разбираться в причинах ошибок
- Не коммитить с `--no-verify`

---

## 📚 Дополнительные ресурсы

### C4 Model:
- https://c4model.com/
- https://github.com/structurizr/dsl

### Architecture as Code:
- https://github.com/structurizr/python
- https://github.com/ArchUnit/ArchUnit

### Dependency Management:
- https://github.com/Netflix/atlas
- https://github.com/airbnb/knowledge-repo

---

## 🤝 Contributing

При добавлении новых инструментов:

1. Обновить этот README
2. Добавить тесты в `tests/`
3. Обновить CI/CD pipeline
4. Создать PR с описанием

---

**Создано:** 2025-10-06
**Автор:** AI Architecture Team
**Лицензия:** Internal Use Only
