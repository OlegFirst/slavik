# Quick Start Guide — Project Agent

## Установка (5 минут)

```bash
# 1. Перейдите в директорию с Project Agent
cd /Users/maksymdemchenko/Downloads/project-agent

# 2. Создайте виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Установите Project Agent
pip install -e .
```

## Первый запуск (2 минуты)

### Тест на демо-проекте

```bash
# Перейдите в тестовый проект
cd test-project

# Запустите полное сканирование
export REPO_PATH=$(pwd)
project-agent init
project-agent scan

# Смотрите результаты
ls -la docs/reports/
cat docs/reports/security_report.md
cat docs/reports/quality_report.md
```

### Использование на вашем проекте

```bash
# Перейдите в ваш проект
cd /path/to/your/project

# Инициализация
export REPO_PATH=$(pwd)
project-agent init  # авто-определит домен

# Сканирование
project-agent scan

# Смотрите отчеты
open docs/reports/security_report.md  # или просто `cat`
```

## Основные команды

```bash
# Статус и конфигурация
project-agent status

# Сканирование по модулям
project-agent scan --module security     # только безопасность
project-agent scan --module quality      # только качество кода
project-agent scan --module testing      # только тесты

# Дополнительные отчеты
project-agent report --weekly           # weekly summary для бизнеса
project-agent iso                       # ISO 22301 compliance
project-agent changelog --days 7        # changelog за неделю
```

## Конфигурация

Файл `.project-agent.yml` создается автоматически при `init`. Вы можете редактировать его:

```yaml
domain: iso22301  # Ваш домен

modules:
  security:
    enabled: true
    checks: [secrets, vulnerabilities, dependencies]

  testing:
    enabled: true
    coverage_threshold: 70  # Минимальный % покрытия

  quality:
    enabled: true
    checks: [complexity, duplication, tech-debt]
```

## Интеграция в CI/CD

### GitHub Actions

```yaml
name: Project Agent Scan

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Project Agent
        run: |
          pip install project-agent

      - name: Run Security Scan
        run: |
          export REPO_PATH=$(pwd)
          project-agent scan --module security

      - name: Check Results
        run: |
          if grep -q "FAIL" docs/reports/security_report.md; then
            echo "Security issues found!"
            exit 1
          fi
```

### GitLab CI

```yaml
project-agent-scan:
  image: python:3.10
  script:
    - pip install project-agent
    - export REPO_PATH=$(pwd)
    - project-agent scan --module security --module quality
  artifacts:
    paths:
      - docs/reports/
```

## Troubleshooting

### "Command not found: project-agent"

```bash
# Убедитесь что виртуальное окружение активно
source .venv/bin/activate

# Переустановите
pip install -e .
```

### "No module named 'agent'"

```bash
# Убедитесь что вы в правильной директории
cd /Users/maksymdemchenko/Downloads/project-agent
pip install -e .
```

### Тесты не запускаются / Coverage 0%

```bash
# Установите pytest для Python coverage
pip install pytest pytest-cov

# Для JavaScript
npm install --save-dev jest
```

## Что дальше?

- 📖 Полная документация: [README.md](README.md)
- 🧪 Попробуйте на тестовом проекте: `cd test-project && project-agent scan`
- ⚙️ Настройте под свой проект: редактируйте `.project-agent.yml`
- 🔄 Интегрируйте в CI/CD
- 📊 Смотрите отчеты в `docs/reports/`

Готово! Project Agent настроен и работает 🚀
