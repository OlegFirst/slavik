# ТЗ: Настройка GitHub для AI-Platform-ISO

**Дата создания:** 2025-10-03
**Статус:** 📋 Готово к выполнению (когда все сервисы будут созданы)

---

## 🎯 Цель

Настроить GitHub для AI-Platform-ISO в формате **monorepo** с правильной организацией, CI/CD и автоматизацией.

---

## 📦 Структура репозитория

```
AI-Platform-ISO/  (github.com/your-org/ai-platform-iso)
├── .github/
│   ├── workflows/
│   │   ├── ci-validation-service.yml
│   │   ├── ci-documents-service.yml
│   │   ├── ci-mio-manager.yml
│   │   ├── automation-toolkit.yml
│   │   └── security-scan.yml
│   ├── CODEOWNERS
│   └── pull_request_template.md
│
├── tools/                          # Automation Toolkit
│   ├── analyzers/
│   ├── generators/
│   └── README.md
│
├── intelligent-core/               # AI компоненты
│   ├── mio-manager/
│   ├── ai-orchestrator/
│   └── workflow-intelligence/
│
├── platform-services/              # Микросервисы
│   ├── validation-service/
│   ├── documents-service/
│   ├── governance-service/
│   └── ...
│
├── shared/                         # Shared библиотека
│   ├── database/
│   ├── auth/
│   └── cache/
│
├── infrastructure/                 # Инфраструктура
│   ├── docker-compose.yml
│   ├── kubernetes/
│   └── terraform/
│
├── docs/                          # Документация
│   ├── architecture/
│   ├── api/
│   └── deployment/
│
├── .gitignore
├── .dockerignore
├── README.md
├── LICENSE
└── CONTRIBUTING.md
```

---

## 📝 Файлы для создания

### 1. `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Logs
*.log
logs/
*.log.*

# Environment
.env
.env.local
.env.*.local
*.env

# Database
*.db
*.sqlite
*.sqlite3

# Testing
.coverage
.pytest_cache/
htmlcov/
.tox/
.nox/

# Reports
tools/reports/*.json
tools/reports/*.html
tools/reports/*.png
!tools/reports/.gitkeep

# Generated tests
tests/generated/*.py
tests/generated/*.yaml
!tests/generated/.gitkeep

# Temporary
*.tmp
*.temp
.cache/
```

### 2. Главный `README.md`

```markdown
# 🚀 AI-Platform-ISO

**Intelligent BCM Platform powered by AI**

## 🎯 Overview

AI-Platform-ISO - это интеллектуальная платформа для управления Business Continuity Management (BCM) в соответствии с ISO 22301.

### Ключевые компоненты:

- 🤖 **AI MIO Manager** - Управляющий центр платформы
- 🔧 **Automation Toolkit** - Инструменты автоматизации и анализа
- 🧠 **Intelligent Core** - AI-компоненты и оркестрация
- 🏗️ **Platform Services** - Микросервисы (12+)
- 🔗 **Shared Libraries** - Общие библиотеки

## 🏗️ Architecture

[Диаграмма архитектуры]

## 🚀 Quick Start

[Инструкции по запуску]

## 📚 Documentation

- [Architecture](docs/architecture/)
- [API Reference](docs/api/)
- [Deployment Guide](docs/deployment/)
```

### 3. GitHub Actions Workflows

#### `ci-validation-service.yml`

```yaml
name: CI - Validation Service

on:
  push:
    paths:
      - 'platform-services/validation-service/**'
      - 'shared/**'
  pull_request:
    paths:
      - 'platform-services/validation-service/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r platform-services/validation-service/requirements.txt
          pip install pytest pytest-asyncio

      - name: Run tests
        run: |
          cd platform-services/validation-service
          pytest tests/

      - name: Security scan
        run: |
          pip install bandit
          bandit -r platform-services/validation-service/ -ll
```

#### `automation-toolkit.yml`

```yaml
name: Automation Toolkit

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install tools
        run: |
          cd tools
          ./setup.sh

      - name: Run analysis
        run: |
          cd tools
          ./run_analysis.sh

      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: analysis-reports
          path: tools/reports/
```

#### `security-scan.yml`

```yaml
name: Security Scan

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r . -f json -o security-report.json -ll

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: security-scan
          path: security-report.json
```

### 4. `CONTRIBUTING.md`

```markdown
# Contributing to AI-Platform-ISO

## Branch Strategy

- `main` - production-ready code
- `develop` - development branch
- `feature/*` - new features
- `fix/*` - bug fixes
- `refactor/*` - refactoring

## Pull Request Process

1. Create feature branch from `develop`
2. Make changes
3. Run tests locally
4. Create PR to `develop`
5. Wait for CI/CD checks
6. Get approval from 2 reviewers
7. Merge

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, test, chore
```

### 5. `CODEOWNERS`

```
# Code owners

# Automation Toolkit
/tools/ @md-bcm-lead

# MIO Manager
/intelligent-core/mio-manager/ @md-bcm-lead

# Platform Services
/platform-services/validation-service/ @validation-team
/platform-services/documents-service/ @documents-team

# Shared Libraries
/shared/ @core-team

# Infrastructure
/infrastructure/ @devops-team
```

---

## 🔄 CI/CD Pipeline

### На каждый Push:

1. **Linting** - Pylint, Black, isort
2. **Type checking** - mypy
3. **Unit tests** - pytest
4. **Security scan** - Bandit
5. **Code coverage** - pytest-cov (>80%)

### На Pull Request:

1. Все проверки из Push
2. **Integration tests**
3. **API contract tests**
4. **Performance tests**

### На Merge в main:

1. **Build Docker images**
2. **Push to registry**
3. **Deploy to staging**
4. **E2E tests**
5. **Deploy to production** (manual approval)

---

## 📊 Automation

### Daily (2:00 AM):

- Run full Automation Toolkit analysis
- Generate reports
- Upload to artifacts

### Weekly (Sunday 3:00 AM):

- Generate synthetic tests
- Update API documentation
- Complexity analysis

### On Security Alert:

- Create GitHub issue
- Notify team
- Run detailed security scan

---

## 🚀 Deployment Strategy

### Environments:

1. **Development** - auto-deploy from `develop`
2. **Staging** - auto-deploy from `main`
3. **Production** - manual approval + deploy

### Docker Images:

```yaml
services:
  validation-service:
    image: ghcr.io/your-org/validation-service:${TAG}

  mio-manager:
    image: ghcr.io/your-org/mio-manager:${TAG}
```

---

## 📋 Checklist перед настройкой Git

- [ ] Все сервисы созданы и протестированы
- [ ] Документация обновлена
- [ ] .gitignore настроен
- [ ] GitHub Actions workflows готовы
- [ ] Secrets настроены в GitHub
- [ ] Branch protection rules настроены
- [ ] Code owners назначены
- [ ] CI/CD протестирован

---

## 🎯 Execution Plan

1. **Создать репозиторий на GitHub:**
   ```bash
   # Локально
   cd /Users/MD/AI-Platform-ISO
   git init
   git add .
   git commit -m "Initial commit: AI-Platform-ISO v1.0"

   # GitHub
   git remote add origin git@github.com:your-org/ai-platform-iso.git
   git push -u origin main
   ```

2. **Настроить GitHub:**
   - Enable branch protection (main, develop)
   - Add secrets (API keys, tokens)
   - Configure webhooks

3. **Настроить CI/CD:**
   - Verify all workflows work
   - Test deployment pipeline
   - Setup monitoring

4. **Документация:**
   - Generate API docs
   - Update README
   - Create deployment guide

---

## ✅ Success Criteria

- [ ] Repository created and pushed
- [ ] CI/CD pipelines passing
- [ ] All services deployable
- [ ] Documentation complete
- [ ] Team has access
- [ ] First production deploy successful

---

**Статус:** Готово к выполнению после завершения всех сервисов
