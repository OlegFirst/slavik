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

## Roadmap

- [ ] GitHub App version
- [ ] PDF reports для аудиторов
- [ ] Интеграция с GitHub Issues для tech debt tracking
- [ ] Поддержка Rust, Ruby, PHP
- [ ] Real-time dashboard
- [ ] Slack/Teams notifications
