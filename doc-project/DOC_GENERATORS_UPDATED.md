# 📚 Инструменты документации - ОБНОВЛЁННЫЙ АНАЛИЗ

**Дата**: 2025-10-08
**Обновление**: Найден Project Agent - основной оркестратор!

---

## ✅ КЛЮЧЕВАЯ НАХОДКА: Project Agent

### 📍 Местоположение:
```
/infrastructure/AI-office-infrastructure/project-agent/
```

**Project Agent** - это **универсальный CLI-агент** который **ОРКЕСТРИРУЕТ** все инструменты анализа и генерации!

---

## 🎯 Project Agent - Главный оркестратор

### Что это:
**Универсальный CLI для анализа проектов** с автоматическим определением тематики (ISO 22301, Security, Fintech, Healthcare, E-commerce).

### Основные возможности:

#### 1️⃣ **Domain Detection** - Авто-определение тематики
```python
# /infrastructure/AI-office-infrastructure/project-agent/agent/domain_detector.py
detect_domain(repo_path)
# → Определяет: iso22301, security, fintech, healthcare, ecommerce
```

#### 2️⃣ **Security Module** - Безопасность
- Поиск секретов (API keys, passwords, tokens)
- Обнаружение уязвимостей (eval, pickle, SQL injection, XSS)
- Анализ зависимостей (интеграция с Safety, npm audit)

#### 3️⃣ **Testing Module** - Тестирование
- Анализ тестового покрытия (pytest, jest, go test)
- **✨ Автоматическая генерация тестов** для Python модулей
- Проверка coverage threshold

#### 4️⃣ **Quality Module** - Качество
- Cyclomatic complexity анализ
- Обнаружение дублирования кода
- Поиск технического долга (TODO, FIXME, HACK, XXX)

#### 5️⃣ **Architecture Module** ⭐ НОВОЕ!
**ИНТЕГРИРУЕТ ИНСТРУМЕНТЫ ИЗ `/infrastructure/tools/`**

```python
# /infrastructure/AI-office-infrastructure/project-agent/agent/modules/architecture.py

def _scan_modules(repo_path, target_module):
    """Вызывает /tools/analyzers/module_scanner.py"""
    scanner_path = repo_path / "tools" / "analyzers" / "module_scanner.py"
    subprocess.run([sys.executable, str(scanner_path)])

def _analyze_dependencies(repo_path, target_module):
    """Вызывает /tools/analyzers/dependency_validator.py"""
    validator_path = repo_path / "tools" / "analyzers" / "dependency_validator.py"

def _map_api_endpoints(repo_path, target_module):
    """Вызывает /tools/analyzers/api_mapper.py"""
    mapper_path = repo_path / "tools" / "analyzers" / "api_mapper.py"

def _extract_business_logic(repo_path, target_module):
    """Вызывает /tools/analyzers/business_logic_mapper.py"""
```

#### 6️⃣ **Test Generator Module** ⭐ НОВОЕ!
**Автоматическая генерация pytest тестов**

```python
# /infrastructure/AI-office-infrastructure/project-agent/agent/modules/test_generator.py

class CodeAnalyzer(ast.NodeVisitor):
    """Analyzes Python AST to extract testable components"""

def run_test_generation(config, target_module=None, max_files=None):
    """Generate pytest tests for Python modules"""
    # AST анализ
    # Генерация тестов (AAA pattern)
    # Поддержка async/await
```

---

## 🔗 Интеграция Project Agent с инструментами

### Архитектура интеграции:

```mermaid
graph TD
    A[Project Agent CLI] --> B[Architecture Module]
    A --> C[Test Generator Module]
    A --> D[Security Module]
    A --> E[Quality Module]

    B --> F[/tools/analyzers/module_scanner.py]
    B --> G[/tools/analyzers/dependency_validator.py]
    B --> H[/tools/analyzers/api_mapper.py]
    B --> I[/tools/analyzers/business_logic_mapper.py]

    C --> J[AST Analyzer]
    C --> K[Test Template Generator]

    F --> L[Module Reports]
    G --> M[Dependency Reports]
    H --> N[API Map]
    I --> O[Business Logic Map]

    C --> P[Generated Tests]
    D --> Q[Security Reports]
    E --> R[Quality Reports]
```

---

## 📦 Связь с `/infrastructure/tools/doc-generators/`

### Обнаруженная связь:

| Doc Generator | Project Agent Module | Связь |
|--------------|---------------------|-------|
| ❌ `ai_documentation_generator.py` | - | **НЕ ИНТЕГРИРОВАН** |
| ❌ `documentation_generator.py` | - | **НЕ ИНТЕГРИРОВАН** |
| ❌ `event_catalog_generator.py` | - | **НЕ ИНТЕГРИРОВАН** |
| ❌ `api_docs_generator.py` | - | **НЕ ИНТЕГРИРОВАН** |
| ❌ `prometheus_config_generator.py` | - | **НЕ ИНТЕГРИРОВАН** |
| ✅ **test_generator.py** | `test_generator` module | **ПОХОЖАЯ ФУНКЦИЯ** |
| ❌ `ui_blueprint_gen.py` | - | **НЕ ИНТЕГРИРОВАН** |

### ⚠️ Важно:
**Project Agent** использует **свой собственный test generator** (`/project-agent/agent/modules/test_generator.py`), а НЕ `/infrastructure/tools/doc-generators/test_generator.py`.

Это **два разных инструмента** с похожей функцией!

---

## 🚀 Project Agent - Команды

### Основные команды:

```bash
# Инициализация (авто-определение домена)
project-agent init

# Полное сканирование
project-agent scan

# Выборочное сканирование
project-agent scan --module security
project-agent scan --module quality --module testing

# Генерация тестов ✨ NEW!
project-agent generate-tests
project-agent generate-tests --module workflow_intelligence

# Архитектурный анализ ✨ NEW!
project-agent analyze-architecture
project-agent analyze-architecture --module ai-foundation

# Статус
project-agent status

# Дополнительные
project-agent index              # Индексация кода
project-agent iso                # ISO 22301 compliance
project-agent processmap         # BPMN/YAML process mapping
project-agent consistency        # Проверка синхронности доков и кода
project-agent changelog          # Генерация changelog
project-agent report             # Генерация отчетов
project-agent report --weekly    # Weekly summary
```

---

## 🤖 Автоматизация Project Agent

### ✅ Уже автоматизировано!

#### 1️⃣ **GitHub Actions Workflow**
**Файл**: `.github/workflows/project-agent-automation.yml`

**Запуск**:
- Автоматически при push/PR в ветки `main`, `develop`
- Ежедневно в полночь UTC (comprehensive scan)
- Еженедельно в воскресенье в 2:00 UTC (deep analysis)
- Вручную через GitHub Actions UI

**Что выполняется**:
- ✅ Auto Test Generation
- ✅ Security Scan
- ✅ Quality Analysis
- ✅ Architecture Validation
- ✅ Coverage Analysis
- ✅ Comprehensive Reports

#### 2️⃣ **Code Watcher Service**
**Файл**: `/project-agent/code_watcher.py`

**Возможности**:
- 👁️ Отслеживает изменения в `intelligent-core/`, `platform-services/`, `infrastructure/`
- 🧪 Автогенерация тестов для новых файлов (debounce 5 сек)
- 🔒 Автоматический security scan
- 📊 Опциональный quality check

**Запуск**:
```bash
cd /infrastructure/AI-office-infrastructure/project-agent
./start_watcher.sh
```

#### 3️⃣ **Pre-commit Hooks**
**Файл**: `.pre-commit-config.yaml`

**Что проверяется**:
- ✅ Test generation для измененных файлов
- ✅ Security checks (secrets, vulnerabilities)
- ✅ Code formatting (Black, isort)
- ✅ Linting (Flake8, MyPy)

---

## 📊 Связь Project Agent с AI коллегами

### Текущий статус: ⚠️ **ЧАСТИЧНО ИНТЕГРИРОВАН**

| AI Коллега | Может вызывать | Статус |
|-----------|---------------|--------|
| **Living Docs Service** | ❌ Нет прямой интеграции | 🔴 НЕ ИНТЕГРИРОВАН |
| **Documents Specialist** | ❌ Нет прямой интеграции | 🔴 НЕ ИНТЕГРИРОВАН |
| **MIO Manager** | ⚠️ Возможна интеграция | 🟡 ПОТЕНЦИАЛЬНО |
| **Project Agent сам** | ✅ Автоматизирован | 🟢 ИНТЕГРИРОВАН |

### Рекомендации по интеграции:

#### 1. Documents Specialist → Project Agent
```python
# /expertise-center/domains/bcm/tactical_assistants/documents_specialist.py

class DocumentsSpecialist:
    async def handle_user_request(self, request: str):
        if "генерируй тесты" in request:
            # Вызвать Project Agent
            subprocess.run([
                "project-agent", "generate-tests",
                "--module", module_name
            ])

        elif "анализ архитектуры" in request:
            subprocess.run([
                "project-agent", "analyze-architecture",
                "--module", module_name
            ])
```

#### 2. Living Docs → Project Agent
```python
# /intelligent-core/living-docs/services/documentation_evolution_engine.py

class DocumentationEvolutionEngine:
    async def auto_update_documentation(self):
        # 1. Project Agent для анализа
        subprocess.run(["project-agent", "analyze-architecture"])

        # 2. Затем doc generators
        subprocess.run([
            "python3",
            "infrastructure/tools/doc-generators/ai_documentation_generator.py",
            "--full", "--ai"
        ])
```

---

## 💡 Итоговая картина

### Найденные инструменты:

1. **`/infrastructure/tools/doc-generators/`** (7 инструментов)
   - ❌ НЕ автоматизированы
   - ❌ НЕ интегрированы с AI коллегами
   - ❌ НЕ интегрированы с Project Agent

2. **`/infrastructure/AI-office-infrastructure/project-agent/`** (ГЛАВНЫЙ)
   - ✅ Автоматизирован (GitHub Actions + Code Watcher + Pre-commit)
   - ⚠️ ЧАСТИЧНО интегрирован с `/tools/analyzers/` (НЕ `/tools/doc-generators/`)
   - ❌ НЕ интегрирован с AI коллегами напрямую

### Архитектура:

```
Project Agent (оркестратор)
├── Автоматизация
│   ├── GitHub Actions ✅
│   ├── Code Watcher ✅
│   └── Pre-commit Hooks ✅
│
├── Модули
│   ├── Security Module ✅
│   ├── Testing Module ✅
│   ├── Quality Module ✅
│   ├── Test Generator Module ✅
│   └── Architecture Module ✅
│       ├── → /tools/analyzers/module_scanner.py ✅
│       ├── → /tools/analyzers/dependency_validator.py ✅
│       ├── → /tools/analyzers/api_mapper.py ✅
│       └── → /tools/analyzers/business_logic_mapper.py ✅
│
└── НЕ интегрированы:
    └── /tools/doc-generators/ ❌
        ├── ai_documentation_generator.py
        ├── documentation_generator.py
        ├── event_catalog_generator.py
        ├── api_docs_generator.py
        ├── prometheus_config_generator.py
        ├── test_generator.py (дубликат!)
        └── ui_blueprint_gen.py
```

---

## 🔨 Рекомендации

### Приоритет 1: **Интегрировать doc-generators в Project Agent**

```python
# /project-agent/agent/modules/documentation.py (NEW!)

def run_documentation_generation(config, use_ai=True):
    """Генерация документации через doc-generators"""

    # 1. AI Documentation
    subprocess.run([
        "python3",
        "infrastructure/tools/doc-generators/ai_documentation_generator.py",
        "--full",
        "--ai" if use_ai else ""
    ])

    # 2. Event Catalog
    subprocess.run([
        "python3",
        "infrastructure/tools/doc-generators/event_catalog_generator.py"
    ])

    # 3. Prometheus Config
    subprocess.run([
        "python3",
        "infrastructure/tools/doc-generators/prometheus_config_generator.py"
    ])
```

Добавить команду:
```bash
project-agent generate-docs
project-agent generate-docs --ai
project-agent generate-docs --module ai-foundation
```

### Приоритет 2: **Удалить дубликат test_generator**

Есть **два test_generator**:
- `/infrastructure/tools/doc-generators/test_generator.py`
- `/infrastructure/AI-office-infrastructure/project-agent/agent/modules/test_generator.py`

**Решение**: Оставить Project Agent версию (более полный функционал), удалить дубликат из doc-generators.

### Приоритет 3: **Интегрировать с AI коллегами**

Documents Specialist + Living Docs должны вызывать:
```bash
project-agent generate-docs --ai
project-agent generate-tests --module {module}
project-agent analyze-architecture --module {module}
```

---

## 📁 Обновлённые документы

1. **[DOC_GENERATORS_UPDATED.md](DOC_GENERATORS_UPDATED.md)** - Этот файл
2. **[ИНСТРУМЕНТЫ_ДОКУМЕНТАЦИИ_АНАЛИЗ.md](ИНСТРУМЕНТЫ_ДОКУМЕНТАЦИИ_АНАЛИЗ.md)** - Предыдущий анализ (устарел частично)
3. **[DOC_GENERATORS_SUMMARY.md](DOC_GENERATORS_SUMMARY.md)** - Краткая сводка (устарела частично)

---

**Версия**: 2.0
**Дата**: 2025-10-08
**Статус**: ✅ PROJECT AGENT FOUND & ANALYZED
**Автор**: AI Assistant
