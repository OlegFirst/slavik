# Project Agent — Universal CLI for Project Analysis

Универсальный CLI-агент для анализа проектов любого домена с автоматическим определением тематики.

## Возможности

### 🔍 Domain Detection (Авто-определение тематики)
- Анализирует код, документацию, зависимости
- Определяет домен: ISO 22301, Security, Fintech, Healthcare, E-commerce
- Автоматически настраивает конфигурацию под домен

### 🛡️ Security Module
- Поиск секретов (API keys, passwords, tokens)
- Обнаружение уязвимостей (eval, pickle, SQL injection, XSS)
- Анализ зависимостей (интеграция с Safety, npm audit)

### 🧪 Testing Module
- Анализ тестового покрытия (pytest, jest, go test)
- **Автоматическая генерация тестов** для Python модулей
- Поиск тестовых файлов
- Проверка соответствия coverage threshold

### 📊 Quality Module
- Cyclomatic complexity анализ
- Обнаружение дублирования кода
- Поиск технического долга (TODO, FIXME, HACK, XXX)

### ✅ Compliance Module
- ISO 22301 (Business Continuity Management)
- ISO 27001 (Information Security)
- PCI-DSS, HIPAA, GDPR (настраиваемо)

### 📈 Reporting
- Markdown/HTML/JSON отчеты
- Отчеты для разных аудиторий: dev, business, security, audit
- Daily и Weekly reports

## Установка

```bash
# Клонируйте репозиторий
cd /Users/maksymdemchenko/Downloads/project-agent

# Установите зависимости
pip install -r requirements.txt

# Установите агент
pip install -e .
```

## Быстрый старт

```bash
# 1. Перейдите в ваш проект
cd /path/to/your/project

# 2. Инициализация (авто-определит домен)
export REPO_PATH=$(pwd)
project-agent init

# 3. Проверка статуса
project-agent status

# 4. Полное сканирование
project-agent scan

# 5. Выборочное сканирование модулей
project-agent scan --module security
project-agent scan --module quality --module testing
```

## Команды

### `project-agent init`
Инициализирует конфигурацию с автоматическим определением домена проекта.

```bash
project-agent init                    # авто-определение
project-agent init --domain security  # явное указание домена
project-agent init --force            # перезаписать существующий конфиг
```

### `project-agent scan`
Запускает анализ проекта по всем включенным модулям.

```bash
project-agent scan                          # все включенные модули
project-agent scan --module security        # только security
project-agent scan --module quality --module testing
```

### `project-agent status`
Показывает текущий статус и конфигурацию агента.

```bash
project-agent status
```

### `project-agent generate-tests` ✨ NEW!
Автоматически генерирует pytest тесты для Python модулей.

```bash
# Генерация для всех модулей intelligent-core
project-agent generate-tests

# Генерация для конкретного модуля
project-agent generate-tests --module workflow_intelligence

# С ограничением количества файлов
project-agent generate-tests --module ai-foundation --max-files 5
```

**Что генерируется:**
- Unit тесты для функций и классов
- AAA pattern (Arrange-Act-Assert)
- Поддержка async/await
- Шаблоны для edge cases и error handling
- Готовые TODO комментарии для доработки

### Дополнительные команды

```bash
project-agent index          # Индексация кода
project-agent iso            # ISO 22301 compliance check
project-agent processmap     # BPMN/YAML process mapping
project-agent consistency    # Проверка синхронности доков и кода
project-agent changelog      # Генерация changelog
project-agent report         # Генерация отчетов
project-agent report --weekly  # Weekly summary для доноров/аудиторов
```

## Конфигурация

После `project-agent init` создается файл `.project-agent.yml`:

```yaml
domain: iso22301  # auto-detected

modules:
  security:
    enabled: true
    checks:
      - secrets
      - vulnerabilities
      - dependencies

  testing:
    enabled: true
    coverage_threshold: 70
    frameworks:
      - pytest
      - jest
      - go-test

  quality:
    enabled: true
    checks:
      - complexity
      - duplication
      - tech-debt

  compliance:
    enabled: true
    standards:
      - ISO22301
      - ISO27001

reports:
  formats:
    - markdown
    - html
  audiences:
    - dev
    - business
    - audit

integrations:
  thehive:
    enabled: false
    url: ""
    api_key: ""

  m365:
    enabled: false
    tenant_id: ""
    client_id: ""
    client_secret: ""
```

## Отчеты

Все отчеты сохраняются в `docs/reports/`:

```
docs/reports/
├── security_report.md         # Security findings
├── security_report.json
├── quality_report.md          # Code quality metrics
├── quality_report.json
├── testing_report.md          # Test coverage
├── testing_report.json
├── iso_coverage.json          # ISO compliance
├── daily_report.md            # Daily summary (technical)
├── donor_summary.md           # Weekly summary (business)
└── dashboard.html             # Interactive dashboard
```

## Поддерживаемые языки

- **Python** (полная поддержка)
- **JavaScript/TypeScript** (полная поддержка)
- **Go** (базовая поддержка)
- **Java** (базовая поддержка)

## Поддерживаемые домены

| Домен | Описание | Рекомендуемые модули |
|-------|----------|---------------------|
| **iso22301** | Business Continuity Management | security, testing, quality, compliance |
| **security** | Security-focused projects | security (strict), quality, testing |
| **fintech** | Financial technology | security (strict), compliance, testing (90%), quality |
| **healthcare** | Healthcare/Medical | security (strict), compliance (HIPAA), testing |
| **ecommerce** | E-commerce projects | security, testing, quality |

## Примеры использования

### Для ISO 22301 проекта

```bash
cd /path/to/bcm-project
export REPO_PATH=$(pwd)
project-agent init  # автоматически определит iso22301
project-agent scan
project-agent report --weekly  # для аудиторов
```

### Для Security audit

```bash
cd /path/to/webapp
export REPO_PATH=$(pwd)
project-agent init --domain security
project-agent scan --module security  # только security checks
```

### Для CI/CD интеграции

```bash
# В вашем CI pipeline
export REPO_PATH=$(pwd)
project-agent scan --module security
if grep -q "FAIL" docs/reports/security_report.md; then
  exit 1
fi
```

## Тестовый проект

В комплекте идет готовый `test-project/` для проверки функционала:

```bash
cd test-project
export REPO_PATH=$(pwd)
project-agent scan
```

Результаты на test-project:
- ✅ Security: 3 secrets, 2 vulnerabilities found
- ✅ Quality: 1 high complexity function, 11 duplicate blocks, 9 tech debt items
- ✅ Testing: coverage 23.53%
- ✅ Compliance: ISO checks passed

## Требования

- Python 3.8+
- Git (для changelog)
- Опционально: pytest, jest, go (для test coverage)

## Лицензия

MIT

## 🤖 Automation (NEW!)

Project Agent теперь полностью автоматизирован! Больше не нужно запускать вручную — все работает автоматически.

### 🚀 Quick Setup

```bash
# 1. Запустите установку автоматизации
cd infrastructure/tools/project-agent
./setup_automation.sh

# 2. Запустите code watcher (опционально)
./start_watcher.sh
```

### Что включено в автоматизацию?

#### 1️⃣ **GitHub Actions Workflow**
Автоматические проверки при каждом коммите и PR:

- ✅ **Auto Test Generation** — генерация тестов для новых/измененных файлов
- ✅ **Security Scan** — проверка безопасности кода
- ✅ **Quality Analysis** — анализ качества кода
- ✅ **Architecture Validation** — проверка архитектуры
- ✅ **Coverage Analysis** — анализ тестового покрытия
- ✅ **Comprehensive Reports** — полные отчеты по всем метрикам

**Запуск:**
- Автоматически при push/PR в ветки `main`, `develop`
- Ежедневно в полночь UTC (comprehensive scan)
- Еженедельно в воскресенье в 2:00 UTC (deep analysis)
- Вручную через GitHub Actions UI

**Конфигурация:** `.github/workflows/project-agent-automation.yml`

#### 2️⃣ **Code Watcher Service**
Мониторинг изменений кода в реальном времени:

```bash
# Запуск watcher
./start_watcher.sh

# Или через LaunchAgent (macOS)
launchctl load ~/Library/LaunchAgents/com.ai-platform.project-agent-watcher.plist

# Остановка
./stop_watcher.sh
```

**Возможности:**
- 👁️ Отслеживает изменения в `intelligent-core/`, `platform-services/`, `infrastructure/`
- 🧪 Автогенерация тестов для новых файлов (debounce 5 сек)
- 🔒 Автоматический security scan
- 📊 Опциональный quality check
- 📝 Логирование в `code_watcher.log`

**Конфигурация:** `watcher_config.json`

```json
{
  "debounce_seconds": 5,
  "auto_generate_tests": true,
  "auto_run_security": true,
  "auto_run_quality": false
}
```

#### 3️⃣ **Pre-commit Hooks**
Автоматические проверки перед каждым коммитом:

```bash
# Hooks устанавливаются автоматически через setup_automation.sh
# Проверить:
pre-commit run --all-files
```

**Что проверяется:**
- ✅ Test generation для измененных файлов
- ✅ Security checks (secrets, vulnerabilities)
- ✅ Code formatting (Black, isort)
- ✅ Linting (Flake8, MyPy)
- ✅ YAML/JSON syntax
- ✅ Large files detection
- ✅ Secrets detection

**Конфигурация:** `.pre-commit-config.yaml`

### 📊 Automated Reports

Все отчеты генерируются автоматически и доступны в GitHub Actions Artifacts:

- **Security Report** — уязвимости, секреты, зависимости
- **Quality Report** — complexity, code smells, maintainability
- **Coverage Report** — тестовое покрытие
- **Architecture Report** — архитектурные нарушения
- **Comprehensive Report** — сводный отчет по всем метрикам

### 🔔 Notifications

**Статус проверок:**
- ❌ Critical security vulnerabilities → workflow fails
- ⚠️ Quality gates failed → workflow fails
- ✅ All checks passed → workflow succeeds

**Где смотреть результаты:**
1. GitHub Actions → Workflows → Project Agent - Automated Testing & Analysis
2. Pull Request comments (автоматические комментарии с отчетами)
3. Artifacts в GitHub Actions runs

### ⚙️ Configuration Files

```
infrastructure/tools/project-agent/
├── code_watcher.py              # Real-time code monitoring
├── watcher_config.json          # Watcher configuration
├── setup_automation.sh          # Setup script
├── start_watcher.sh             # Start watcher
├── stop_watcher.sh              # Stop watcher
└── generate_tests.sh            # Manual test generation

.github/workflows/
└── project-agent-automation.yml # GitHub Actions workflow

.pre-commit-config.yaml          # Pre-commit hooks
```

### 🎯 Automation Triggers

| Trigger | What Runs | When |
|---------|-----------|------|
| **Push to main/develop** | Test generation, Security, Quality, Coverage | On code changes |
| **Pull Request** | Full analysis + PR comment with report | On PR creation/update |
| **Daily Schedule** | Comprehensive scan of all code | 00:00 UTC daily |
| **Weekly Schedule** | Deep analysis + architecture validation | Sunday 02:00 UTC |
| **Manual Dispatch** | Customizable scan (full/tests-only/security-only) | On demand |
| **File Change (watcher)** | Test generation + security check | Real-time (debounced) |
| **Git Commit (pre-commit)** | Format, lint, security, test generation | Before commit |

### 📈 Quality Gates

Workflow **FAILS** если:
- ❌ Critical security vulnerabilities detected
- ❌ Maintainability index < 7.0
- ❌ Average complexity > 15
- ❌ Test coverage < 70%
- ❌ Architecture violations detected

### 🛠️ Troubleshooting

**Watcher не запускается:**
```bash
# Проверьте логи
tail -f infrastructure/tools/project-agent/code_watcher.log

# Проверьте зависимости
pip install watchdog
```

**Pre-commit hooks не работают:**
```bash
# Переустановите
pre-commit uninstall
pre-commit install

# Тест
pre-commit run --all-files
```

**GitHub Actions fails:**
```bash
# Проверьте секреты в GitHub:
# Settings → Secrets → Actions
# Должен быть GITHUB_TOKEN (автоматически)
```

### 🎉 Результат

После setup у вас будет:
1. ✅ Автоматическая генерация тестов для каждого нового файла
2. ✅ Security checks на каждом коммите и PR
3. ✅ Quality gates для всех изменений
4. ✅ Real-time monitoring изменений кода
5. ✅ Ежедневные и еженедельные comprehensive reports
6. ✅ Автоматические комментарии в Pull Requests

**Вы больше не забудете:**
- Написать тесты
- Проверить безопасность
- Проверить качество кода
- Обновить документацию

## Roadmap

- [x] ✅ GitHub Actions automation
- [x] ✅ Real-time code watcher
- [x] ✅ Pre-commit hooks
- [x] ✅ Automated test generation
- [ ] GitHub App version
- [ ] PDF reports для аудиторов
- [ ] Интеграция с GitHub Issues для tech debt tracking
- [ ] Поддержка Rust, Ruby, PHP
- [ ] Real-time dashboard
- [ ] Slack/Teams notifications

### `project-agent analyze-architecture` ✨ NEW!
Комплексный архитектурный анализ проекта с использованием существующих инструментов.

```bash
# Полный архитектурный анализ
project-agent analyze-architecture

# Анализ конкретного модуля
project-agent analyze-architecture --module workflow_intelligence

# Выбор формата отчета
project-agent analyze-architecture --output-format json
```

**Что анализируется:**
- Сканирование модулей (module_scanner.py)
- Валидация зависимостей (dependency_validator.py)
- Карта зависимостей (dependency_mapper.py)
- API endpoints (api_mapper.py)
- Бизнес-логика (business_logic_mapper.py)
- Архитектурные проблемы (circular deps, conflicts)
- Health score проекта
