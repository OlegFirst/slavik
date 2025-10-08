# 🤖 GitHub Actions - Automated Quality & Security

**Надёжные инструменты без AI-зависимостей**

> ✅ Бесплатно | ⚡ Быстро | 🔒 Детерминированно

---

## 📋 Workflows Overview

### 1. **ruff-lint.yml** - Code Quality & Linting

**Triggers:**
- ✅ Push to `main`/`develop`
- ✅ Pull requests
- ✅ Manual dispatch

**What it does:**
```bash
✨ Ruff linter - Проверяет стиль кода
✨ Ruff formatter - Проверяет форматирование
📊 Генерирует отчёт по проблемам
📈 Статистика по кодовой базе
```

**Tools used:**
- **Ruff** - Быстрый Python linter (замена Flake8 + Black)

**Output:**
- JSON report в artifacts
- Summary в GitHub UI
- Top 5 самых частых проблем

**Когда запускается:**
- При изменении `.py` файлов в:
  - `intelligent-core/`
  - `platform-services/`
  - `infrastructure/`

---

### 2. **pytest-tests.yml** - Automated Testing & Coverage

**Triggers:**
- ✅ Push to `main`/`develop`
- ✅ Pull requests
- ✅ Daily at 2 AM UTC
- ✅ Manual dispatch

**What it does:**
```bash
🧪 Запускает все тесты pytest
📊 Собирает code coverage
📈 Генерирует отчёты по модулям
✅ Проверяет quality gates
```

**Services tested:**
- **Intelligent-Core** (11 services):
  - ai-foundation, expertise-center, workflow_intelligence
  - community_intelligence, collective, predictive
  - ai-orchestration, coordination-center
  - ai_workflow_optimizer, event_intelligence

- **Platform-Services** (9+ services):
  - bia-service, risk-service, compliance-service
  - governance-service, documents-service, validation-service
  - learning-service, response-service, plans_service

**Tools used:**
- **pytest** - Test framework
- **pytest-cov** - Coverage reporting
- **pytest-asyncio** - Async test support
- **pytest-timeout** - Timeout protection

**Output:**
- JUnit XML reports
- Coverage reports (XML, HTML, JSON)
- Coverage summary в GitHub UI
- Coverage badge data

---

### 3. **bandit-security.yml** - Security Scanning

**Triggers:**
- ✅ Push to `main`/`develop`
- ✅ Pull requests
- ✅ Weekly on Sundays at 3 AM UTC
- ✅ Manual dispatch

**What it does:**
```bash
🔒 Bandit - Сканирует код на security issues
🛡️ Safety - Проверяет vulnerable dependencies
📊 Генерирует consolidated security report
⚠️ Предупреждает о HIGH severity issues
```

**Security checks:**

#### Bandit (Code Security):
- SQL injection vulnerabilities
- Hardcoded passwords/secrets
- Insecure random usage
- Unsafe YAML loading
- Command injection risks

#### Safety (Dependencies):
- Known CVEs in packages
- Vulnerable package versions
- Security advisories

**Tools used:**
- **Bandit** - Python security linter
- **Safety** - Dependency vulnerability scanner

**Output:**
- JSON reports по каждому модулю
- Combined security report
- Top security issues
- Files with most issues
- Warning annotations в GitHub

---

### 4. **dependency-check.yml** - Dependency Health

**Triggers:**
- ✅ Push изменений в `requirements.txt`
- ✅ Pull requests с dependency changes
- ✅ Weekly on Mondays at 8 AM UTC
- ✅ Manual dispatch

**What it does:**
```bash
🔐 pip-audit - Security vulnerabilities
📦 pip-tools - Outdated packages check
📜 pip-licenses - License compliance
📊 Consolidated dependency report
```

**Checks performed:**

#### pip-audit (Security):
- CVE vulnerabilities
- Security advisories
- Severity levels (CRITICAL, HIGH, MEDIUM, LOW)

#### Version Check (Updates):
- Outdated packages
- Available updates
- Current vs latest versions

#### License Compliance:
- Package licenses
- License types distribution
- Compliance verification

**Tools used:**
- **pip-audit** - Official PyPA security tool
- **pip-tools** - Dependency management
- **pip-licenses** - License checker

**Output:**
- Vulnerability reports (JSON + Markdown)
- Outdated packages list
- License reports
- Consolidated summary

---

## 🚀 Quick Start

### Просмотр результатов:

```bash
# 1. Открыть GitHub Actions
https://github.com/YOUR_ORG/AI-Platform-ISO/actions

# 2. Выбрать workflow:
# - Ruff - Code Linting
# - Pytest - Automated Testing
# - Bandit - Security Scanning
# - Dependency Health Check

# 3. Посмотреть Summary и Artifacts
```

### Ручной запуск:

```bash
# GitHub UI:
Actions → Select Workflow → Run workflow

# Или через GitHub CLI:
gh workflow run ruff-lint.yml
gh workflow run pytest-tests.yml
gh workflow run bandit-security.yml
gh workflow run dependency-check.yml
```

### Просмотр отчётов:

```bash
# Скачать artifacts:
gh run download <RUN_ID>

# Или в GitHub UI:
Actions → Run → Artifacts → Download
```

---

## 📊 Что проверяется

### Code Quality (Ruff):
- ✅ PEP 8 compliance
- ✅ Code formatting
- ✅ Import ordering
- ✅ Unused imports
- ✅ Line length
- ✅ Complexity

### Testing (pytest):
- ✅ Unit tests
- ✅ Integration tests
- ✅ Async tests
- ✅ Code coverage
- ✅ Test performance

### Security (Bandit):
- ✅ SQL injection
- ✅ Hardcoded secrets
- ✅ Insecure functions
- ✅ Command injection
- ✅ XML vulnerabilities
- ✅ Crypto issues

### Dependencies:
- ✅ CVE vulnerabilities
- ✅ Outdated packages
- ✅ License compliance
- ✅ Version conflicts

---

## 🎯 Quality Gates

### Ruff:
- ❌ Fail if critical issues found
- ⚠️ Warn on formatting issues

### Pytest:
- ❌ Fail if coverage < 70%
- ❌ Fail if tests timeout (300s)
- ⚠️ Warn on slow tests

### Bandit:
- ⚠️ Warn on HIGH severity (не блокирует build)
- ❌ Fail на CRITICAL (если настроено)

### Dependencies:
- ⚠️ Warn on vulnerabilities
- 📊 Report на outdated packages
- ✅ License compliance check

---

## 📈 Metrics & Reports

### Доступные метрики:

**Code Quality:**
- Total issues found
- Issues by type
- Top 5 most common issues
- Code statistics (files, lines)

**Testing:**
- Total tests executed
- Test success rate
- Coverage percentage
- Coverage by module

**Security:**
- Vulnerabilities by severity
- Top security issues
- Files with most issues
- Vulnerable packages

**Dependencies:**
- Total packages
- Vulnerable packages
- Outdated packages
- License types

---

## 🔧 Configuration

### Настройка quality gates:

Отредактировать соответствующий `.yml` файл:

```yaml
# pytest-tests.yml - изменить minimum coverage
- name: Coverage gate
  run: coverage report --fail-under=80  # Изменить с 70 на 80

# bandit-security.yml - изменить severity level
bandit -r . --severity-level high  # Вместо medium
```

### Добавление новых сервисов:

```yaml
# pytest-tests.yml
strategy:
  matrix:
    service:
      - existing-service
      - new-service  # Добавить сюда
```

### Исключение путей:

```yaml
# ruff-lint.yml
on:
  push:
    paths:
      - 'intelligent-core/**/*.py'
      - '!intelligent-core/_archive/**'  # Исключить
```

---

## 🔒 Secrets Required

### Для работы workflows:

**GITHUB_TOKEN:**
- ✅ Автоматически предоставляется GitHub
- Используется для:
  - Checkout кода
  - Upload artifacts
  - Создание comments

**Опциональные (для расширенной функциональности):**

```bash
# Settings → Secrets and variables → Actions

# Для уведомлений:
SLACK_WEBHOOK_URL - Slack notifications
DISCORD_WEBHOOK_URL - Discord notifications

# Для публикации coverage:
CODECOV_TOKEN - Codecov integration
```

---

## 📅 Schedule

### Когда workflows запускаются автоматически:

```
┌─────────────────────┬──────────────────────┐
│ Workflow            │ Schedule             │
├─────────────────────┼──────────────────────┤
│ Ruff Lint           │ On push/PR           │
│ Pytest Tests        │ Daily at 2 AM UTC    │
│ Bandit Security     │ Weekly Sun 3 AM UTC  │
│ Dependency Check    │ Weekly Mon 8 AM UTC  │
└─────────────────────┴──────────────────────┘
```

### Изменение расписания:

```yaml
schedule:
  - cron: '0 2 * * *'  # Каждый день в 2 AM UTC

# Формат: minute hour day month weekday
# Примеры:
# '0 0 * * *'     - Каждый день в полночь
# '0 */6 * * *'   - Каждые 6 часов
# '0 9 * * 1-5'   - Пн-Пт в 9 AM
```

---

## 💰 Cost Analysis

### GitHub Actions:

```
FREE tier:
- 2,000 минут/месяц для private repos
- Unlimited для public repos

Наши workflows:
- Ruff: ~2 минуты
- Pytest: ~10 минут (зависит от тестов)
- Bandit: ~3 минуты
- Dependency: ~5 минут

Итого: ~20 минут на полный цикл

Месячный лимит:
2000 минут / 20 минут = 100 полных циклов/месяц
```

**Вывод:** Для нашего проекта - **БЕСПЛАТНО** ✅

---

## 🆚 Comparison: AI vs GitHub Actions

| Метрика | AI Tools | GitHub Actions |
|---------|----------|----------------|
| **Стоимость** | $120/мес | **$0** ✅ |
| **Скорость** | 30-60 сек | 5-10 сек ✅ |
| **Надёжность** | ⚠️ Зависит от API | 99.9% uptime ✅ |
| **Предсказуемость** | ❌ Разные результаты | Детерминировано ✅ |
| **Настройка** | 😰 API keys | Zero config ✅ |
| **Видимость** | ❌ Логи в сервисе | GitHub UI ✅ |

---

## 🎯 Best Practices

### 1. **Используйте caching:**

```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'
    cache: 'pip'  # ← Кеш для pip
```

### 2. **Fail fast для быстрой обратной связи:**

```yaml
strategy:
  fail-fast: true  # Остановить при первой ошибке
```

### 3. **Continue-on-error для не-критичных проверок:**

```yaml
- name: Optional check
  continue-on-error: true  # Не блокировать build
```

### 4. **Artifacts для долгосрочного хранения:**

```yaml
retention-days: 90  # Хранить отчёты 90 дней
```

### 5. **Summary для быстрого просмотра:**

```yaml
echo "## Summary" >> $GITHUB_STEP_SUMMARY
echo "- Status: ✅" >> $GITHUB_STEP_SUMMARY
```

---

## 🚨 Troubleshooting

### Workflow не запускается:

```bash
# 1. Проверить что paths корректны
# 2. Проверить branch в on.push.branches
# 3. Проверить права в Settings → Actions → General
```

### Тесты падают локально но проходят в CI:

```bash
# 1. Проверить Python version
python --version

# 2. Проверить зависимости
pip list

# 3. Запустить в той же среде что и CI
docker run -it python:3.11 bash
```

### Artifact не загружается:

```bash
# 1. Проверить что путь существует
ls -la coverage-report.json

# 2. Проверить permissions
chmod 644 coverage-report.json

# 3. Проверить размер (< 2GB limit)
du -h coverage-report.json
```

---

## 📚 Additional Resources

### Documentation:
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest Documentation](https://docs.pytest.org/)
- [Bandit Documentation](https://bandit.readthedocs.io/)

### Workflow Examples:
- [GitHub Actions Examples](https://github.com/actions/starter-workflows)
- [Python CI/CD Examples](https://github.com/actions/starter-workflows/tree/main/ci)

### Tools:
- [act](https://github.com/nektos/act) - Run GitHub Actions locally
- [actionlint](https://github.com/rhysd/actionlint) - Lint workflow files

---

## ✅ Next Steps

### 1. Проверить workflows работают:

```bash
git add .github/workflows/
git commit -m "feat: Add GitHub Actions workflows"
git push

# Проверить в GitHub → Actions
```

### 2. Настроить branch protection:

```bash
# Settings → Branches → Branch protection rules
# Добавить required checks:
# - Ruff - Code Linting
# - Pytest - Automated Testing
# - Bandit - Security Scanning
```

### 3. Добавить badges в README:

```markdown
![Ruff](https://github.com/YOUR_ORG/AI-Platform-ISO/workflows/Ruff%20-%20Code%20Linting/badge.svg)
![Tests](https://github.com/YOUR_ORG/AI-Platform-ISO/workflows/Pytest%20-%20Automated%20Testing/badge.svg)
![Security](https://github.com/YOUR_ORG/AI-Platform-ISO/workflows/Bandit%20-%20Security%20Scanning/badge.svg)
```

---

**Создано:** 2025-10-08
**Статус:** ✅ Production Ready
**AI Dependency:** ❌ ZERO (полностью без AI)
