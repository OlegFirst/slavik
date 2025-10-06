# 📦 Project Agent — Package Info

## Местоположение

```
/Users/maksymdemchenko/Downloads/project-agent/
```

## Структура пакета

```
bv/
├── 📄 README.md              # Полная документация
├── 📄 QUICKSTART.md          # Быстрый старт (5 минут)
├── 📄 PACKAGE_INFO.md        # Этот файл
├── 📄 LICENSE                # MIT License
├── 🔧 requirements.txt       # Зависимости
├── 🔧 setup.py               # Установка
├── 🔧 setup.cfg              # Конфигурация пакета
├── 🔧 MANIFEST.in            # Манифест для сборки
├── 🔧 .gitignore             # Git ignore rules
├── 🚀 install.sh             # Скрипт быстрой установки
│
├── 📁 agent/                 # ОСНОВНОЙ КОД АГЕНТА
│   ├── cli.py                   # CLI (init, scan, status)
│   ├── domain_detector.py       # Domain Detection (авто-определение)
│   ├── config.py                # Система конфигурации
│   │
│   ├── modules/                 # Модули анализа
│   │   ├── security.py             # Security checks
│   │   ├── testing.py              # Testing analysis
│   │   └── quality.py              # Code quality
│   │
│   ├── compliance.py            # ISO 22301/27001
│   ├── bpmn_yaml.py             # BPMN/YAML парсинг
│   ├── indexer.py               # Индексация кода
│   ├── doc_sync.py              # Синхронизация доков
│   ├── changelog.py             # Генерация changelog
│   ├── report.py                # Отчеты
│   │
│   ├── parsers/                 # Парсеры языков (future)
│   ├── adapters/                # Внешние интеграции (future)
│   └── compliance/              # Compliance модули (future)
│
├── 📁 test-project/          # ТЕСТОВЫЙ ПРОЕКТ
│   ├── src/                     # Код с намеренными проблемами
│   ├── tests/                   # Тесты
│   ├── docs/                    # Документация
│   └── .project-agent.yml       # Конфиг агента
│
└── 📁 project-agent-sprint*/  # Старые версии (архив)
```

## Установка

### Вариант 1: Быстрая установка (рекомендуется)

```bash
cd /Users/maksymdemchenko/Downloads/project-agent
./install.sh
```

### Вариант 2: Ручная установка

```bash
cd /Users/maksymdemchenko/Downloads/project-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Проверка установки

```bash
# Должна быть активна виртуальная среда
source .venv/bin/activate

# Проверка
project-agent --help
```

## Тест на demo-проекте

```bash
cd /Users/maksymdemchenko/Downloads/project-agent/test-project
export REPO_PATH=$(pwd)
project-agent init
project-agent scan

# Смотрим результаты
cat docs/reports/security_report.md
cat docs/reports/quality_report.md
```

## Использование на вашем проекте

```bash
# 1. Перейдите в ваш проект
cd /path/to/your/project

# 2. Инициализация (авто-определит домен)
export REPO_PATH=$(pwd)
project-agent init

# 3. Сканирование
project-agent scan

# 4. Результаты
ls docs/reports/
```

## Основные команды

| Команда | Описание |
|---------|----------|
| `project-agent init` | Инициализация + domain detection |
| `project-agent scan` | Полное сканирование |
| `project-agent scan --module security` | Только security |
| `project-agent status` | Статус и конфигурация |
| `project-agent iso` | ISO 22301 compliance |
| `project-agent report --weekly` | Weekly summary |

## Возможности агента

### 🔍 Domain Detection
- ✅ Автоматическое определение домена проекта
- ✅ Поддержка: ISO 22301, Security, Fintech, Healthcare, E-commerce
- ✅ Адаптивная конфигурация под домен

### 🛡️ Security Module
- ✅ Поиск секретов (API keys, passwords, tokens)
- ✅ Обнаружение уязвимостей (eval, pickle, SQL injection)
- ✅ Анализ зависимостей (Safety, npm audit)

### 🧪 Testing Module
- ✅ Coverage анализ (pytest, jest, go test)
- ✅ Поиск тестовых файлов
- ✅ Проверка threshold

### 📊 Quality Module
- ✅ Cyclomatic complexity
- ✅ Code duplication detection
- ✅ Tech debt tracking (TODO, FIXME, HACK)

### ✅ Compliance Module
- ✅ ISO 22301 (Business Continuity)
- ✅ ISO 27001 (Information Security)
- ✅ PCI-DSS, HIPAA, GDPR (настраиваемо)

## Результаты на test-project

```
✅ Security: FAIL (как и должно быть)
   - 3 secrets found
   - 2 vulnerabilities found

✅ Quality: OK
   - 1 high complexity function
   - 11 duplicate blocks
   - 9 tech debt items

✅ Testing: BELOW_THRESHOLD
   - Coverage: 23.53%

✅ Compliance: OK
   - ISO checks passed
```

## Интеграция

### CI/CD
См. примеры в README.md для GitHub Actions и GitLab CI

### Git Hook (pre-commit)
```bash
#!/bin/bash
export REPO_PATH=$(pwd)
project-agent scan --module security
if grep -q "FAIL" docs/reports/security_report.md; then
  echo "❌ Security check failed!"
  exit 1
fi
```

## Кастомизация

Редактируйте `.project-agent.yml` в вашем проекте:

```yaml
domain: iso22301

modules:
  security:
    enabled: true
    checks: [secrets, vulnerabilities, dependencies]

  testing:
    enabled: true
    coverage_threshold: 80  # Ваш threshold

  quality:
    enabled: true
    checks: [complexity, duplication, tech-debt]
```

## Отчеты

Все отчеты сохраняются в `docs/reports/`:

```
docs/reports/
├── security_report.md/json     # Security findings
├── quality_report.md/json      # Code quality
├── testing_report.md/json      # Test coverage
├── iso_coverage.json           # ISO compliance
├── daily_report.md             # Daily summary (tech)
└── donor_summary.md            # Weekly summary (business)
```

## Поддержка

- 📖 Полная документация: [README.md](README.md)
- 🚀 Быстрый старт: [QUICKSTART.md](QUICKSTART.md)
- 🧪 Тестовый проект: [test-project/](test-project/)

## Версия

**v1.0.0** — Stable Release

## Roadmap

- [ ] GitHub App version
- [ ] PDF reports
- [ ] GitHub Issues integration for tech debt
- [ ] Support for Rust, Ruby, PHP
- [ ] Real-time dashboard
- [ ] Slack/Teams notifications

---

**Project Agent** готов к использованию! 🚀

Начните с быстрого теста:
```bash
cd test-project && export REPO_PATH=$(pwd) && project-agent scan
```
