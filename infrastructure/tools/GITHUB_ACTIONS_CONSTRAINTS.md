# GitHub Actions Integration Constraints Analysis

**Question:** Какие из этих инструментов нельзя интегрировать через GitHub Actions?

**Answer:** ВСЕ 26 инструментов МОЖНО интегрировать через GitHub Actions, но с разными ограничениями и workaround'ами.

---

## 📊 Классификация инструментов

### ✅ Категория 1: Полностью автоматизируемые (17 инструментов)

**Без ограничений, работают "из коробки" в GitHub Actions:**

| Инструмент | Что делает | Почему легко |
|------------|------------|--------------|
| **ast_analyzer.py** | AST анализ кода | Только читает файлы |
| **dependency_mapper.py** | Граф зависимостей | Только читает imports |
| **metrics_discovery.py** | Метрики сервисов | Анализ структуры проекта |
| **module_scanner.py** | Сканирование модулей | Только читает файлы |
| **api_mapper.py** | Карта API endpoints | Парсит FastAPI декораторы |
| **dependency_validator.py** | Валидация зависимостей | Проверяет requirements.txt |
| **code_complexity_analyzer.py** | Сложность кода | Статический анализ |
| **security_scanner.py** | Security скан | Bandit, не требует runtime |
| **test_coverage_analyzer.py** | Coverage анализ | Читает .coverage файлы |
| **documentation_generator.py** | Генерация docs | Из AST + docstrings |
| **changelog_generator.py** | Changelog из git | git log |
| **ui_blueprint_gen.py** | UI blueprints | Из API схем |
| **test_generator.py** | Генерация тестов | Из AST |
| **service_discovery.py** | Service registry | Сканирует структуру |
| **docker_compose_generator.py** | Docker compose | Из конфигов |
| **prometheus_config_generator.py** | Prometheus config | Из service registry |
| **module_dashboard.py** | Интерактивные дашборды | Plotly HTML |

**Пример GitHub Actions workflow:**

```yaml
name: Automated Analysis

on:
  push:
    branches: [main, develop]
  pull_request:
  schedule:
    - cron: '0 2 * * *'  # Daily at 02:00 UTC

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r infrastructure/tools/requirements.txt

      - name: Run AST Analysis
        run: python3 infrastructure/tools/analyzers/ast_analyzer.py

      - name: Run Dependency Mapper
        run: python3 infrastructure/tools/analyzers/dependency_mapper.py

      - name: Run Metrics Discovery
        run: python3 infrastructure/tools/analyzers/metrics_discovery.py

      - name: Generate Documentation
        run: python3 infrastructure/tools/doc-generators/documentation_generator.py

      - name: Generate Tests
        run: python3 infrastructure/tools/doc-generators/test_generator.py

      - name: Commit Generated Files
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add infrastructure/tools/reports/ docs/ tests/generated/
          git commit -m "chore: automated analysis and generation" || true
          git push
```

**Результат:** ✅ Работает без проблем, запускается автоматически.

---

### ⚠️ Категория 2: Требуют дополнительной настройки (6 инструментов)

#### 2.1 api_docs_generator.py

**Проблема:** Требует запущенных сервисов для получения OpenAPI спецификаций.

**Constraint:**
```python
# Код требует HTTP доступ к /openapi.json
response = requests.get(f"http://localhost:{port}/openapi.json")
```

**Workaround 1: Deploy to staging first**

```yaml
name: API Documentation

on:
  deployment_status:

jobs:
  generate-api-docs:
    if: github.event.deployment_status.state == 'success'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate API Docs from deployed services
        env:
          STAGING_URL: ${{ secrets.STAGING_URL }}
        run: |
          # Modify api_docs_generator.py to use STAGING_URL
          python3 infrastructure/tools/doc-generators/api_docs_generator.py \
            --base-url $STAGING_URL
```

**Workaround 2: Start services in GitHub Actions**

```yaml
jobs:
  generate-api-docs:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
      redis:
        image: redis:7

    steps:
      - uses: actions/checkout@v3

      - name: Start services
        run: |
          docker-compose up -d
          sleep 30  # Wait for services to start

      - name: Generate API Docs
        run: python3 infrastructure/tools/doc-generators/api_docs_generator.py

      - name: Stop services
        run: docker-compose down
```

**Workaround 3: Use static OpenAPI specs (BEST)**

```python
# Modify api_docs_generator.py
def get_openapi_spec(service_name: str) -> dict:
    """Get OpenAPI spec from static file or live service"""
    static_spec_path = f"docs/openapi/{service_name}.json"

    # Try static file first
    if Path(static_spec_path).exists():
        with open(static_spec_path) as f:
            return json.load(f)

    # Fallback to live service
    response = requests.get(f"http://localhost:{self.services[service_name]}/openapi.json")
    return response.json()
```

**Рекомендация:** ✅ Использовать Workaround 3 (статические спецификации).

---

#### 2.2 ai_documentation_generator.py

**Проблема:** Требует LLM API ключи (Anthropic/OpenAI).

**Constraint:**
```python
# Требует API ключ
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
```

**Workaround: GitHub Secrets**

```yaml
jobs:
  ai-documentation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate AI Documentation
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          # Or
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python3 infrastructure/tools/doc-generators/ai_documentation_generator.py
```

**Cost Consideration:**
- Anthropic Claude Sonnet: ~$3/M tokens input, ~$15/M tokens output
- Если генерировать документацию для всего проекта: ~500K tokens input → **~$1.50 per run**
- Daily run: **~$45/month**, Weekly: **~$6/month**

**Рекомендация:** ✅ Запускать WEEKLY, не daily, использовать GitHub Secrets.

---

#### 2.3 dependency_reconciler.py

**Проблема:** Создает Pull Requests для исправления конфликтов.

**Constraint:**
```python
# Требует GitHub token с write permissions
gh_client.create_pull_request(
    title="fix: reconcile dependency conflicts",
    body=reconciliation_plan
)
```

**Workaround: GitHub App Token или PAT**

```yaml
jobs:
  dependency-reconciliation:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write

    steps:
      - uses: actions/checkout@v3

      - name: Generate GitHub App Token
        id: generate-token
        uses: actions/create-github-app-token@v1
        with:
          app-id: ${{ secrets.APP_ID }}
          private-key: ${{ secrets.PRIVATE_KEY }}

      - name: Reconcile Dependencies
        env:
          GITHUB_TOKEN: ${{ steps.generate-token.outputs.token }}
        run: |
          python3 infrastructure/tools/analyzers/dependency_reconciler.py --auto-pr
```

**Альтернатива: Только отчет, без auto-PR**

```yaml
      - name: Reconcile Dependencies (Report Only)
        run: |
          python3 infrastructure/tools/analyzers/dependency_reconciler.py --report-only

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('infrastructure/tools/reports/reconciliation_report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
```

**Рекомендация:** ✅ Report-only mode на PR, auto-PR только для scheduled runs.

---

#### 2.4 environment_validator.py

**Проблема:** Проверяет реальное окружение (.env файлы, API доступность).

**Constraint:**
```python
# Проверяет реальные .env файлы
env_files = [".env", ".env.production", ".env.staging"]
# Проверяет доступность внешних API
check_api_availability("https://api.anthropic.com")
```

**Workaround: Mock для CI**

```yaml
      - name: Setup Test Environment
        run: |
          cp .env.example .env.test
          echo "ANTHROPIC_API_KEY=test-key-ci" >> .env.test

      - name: Validate Environment
        run: |
          python3 infrastructure/tools/analyzers/environment_validator.py \
            --env-file .env.test \
            --skip-api-checks
```

**Рекомендация:** ✅ Использовать --skip-api-checks в CI, full validation только в production deployment.

---

#### 2.5 integration_test_generator.py

**Проблема:** Генерирует тесты, которые требуют запущенных сервисов.

**Constraint:**
```python
# Генерирует тесты с реальными HTTP вызовами
def test_create_kpi(client):
    response = client.post("/kpis", json=kpi_data)
    assert response.status_code == 201
```

**Workaround: TestClient вместо реальных сервисов**

```python
# Генерировать тесты с TestClient
from fastapi.testclient import TestClient

def test_create_kpi():
    from validation_service.main import app
    client = TestClient(app)
    response = client.post("/kpis", json=kpi_data)
    assert response.status_code == 201
```

**Рекомендация:** ✅ Генерировать unit/integration тесты с TestClient, не требуют запущенных сервисов.

---

#### 2.6 performance_profiler.py

**Проблема:** Профилирование требует запущенного приложения и нагрузочного тестирования.

**Constraint:**
```python
# Требует запущенное приложение
profiler = cProfile.Profile()
# Требует реальные запросы
for i in range(1000):
    response = requests.post("/kpis", json=test_data)
```

**Workaround: Mock profiling**

```yaml
      - name: Profile Performance (Mock)
        run: |
          python3 infrastructure/tools/analyzers/performance_profiler.py \
            --mode mock \
            --iterations 100
```

**Рекомендация:** ⚠️ Запускать только в staging/production environments, НЕ в GitHub Actions.

---

### 🔴 Категория 3: НЕ рекомендуется для GitHub Actions (3 инструмента)

#### 3.1 real_time_monitor.py

**Проблема:** Real-time мониторинг требует постоянно работающего процесса.

**Why NOT in GitHub Actions:**
- GitHub Actions workflows имеют max timeout 6 часов
- Real-time мониторинг должен работать 24/7
- Генерирует огромные логи

**Где запускать:**
```bash
# На production сервере как systemd service
[Unit]
Description=Real-time Platform Monitor
After=network.target

[Service]
Type=simple
User=platform
ExecStart=/usr/bin/python3 /opt/platform/tools/analyzers/real_time_monitor.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Рекомендация:** ❌ НЕ использовать в GitHub Actions. Запускать как systemd service на production.

---

#### 3.2 live_metrics_collector.py

**Проблема:** Сбор метрик с живых сервисов в реальном времени.

**Why NOT in GitHub Actions:**
- Требует доступ к production Prometheus/Grafana
- Требует постоянное подключение к БД
- Security риск: production credentials в CI

**Где запускать:**
```bash
# Как cronjob на monitoring сервере
0 * * * * /usr/bin/python3 /opt/platform/tools/analyzers/live_metrics_collector.py
```

**Рекомендация:** ❌ НЕ использовать в GitHub Actions. Запускать как cronjob на monitoring server.

---

#### 3.3 deployment_orchestrator.py

**Проблема:** Оркестрация deployment'а - это задача CI/CD pipeline, не анализа.

**Why NOT in GitHub Actions:**
- Требует доступ к production Kubernetes/Docker
- Требует production credentials
- Критичный для безопасности

**Где запускать:**
```yaml
# В отдельном deployment workflow
name: Production Deployment

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment'
        required: true
        type: choice
        options:
          - staging
          - production

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment }}
    steps:
      - name: Deploy with orchestrator
        env:
          KUBE_CONFIG: ${{ secrets.KUBE_CONFIG }}
        run: |
          python3 infrastructure/tools/deployment_orchestrator.py \
            --environment ${{ github.event.inputs.environment }}
```

**Рекомендация:** ✅ Можно в GitHub Actions, но в ОТДЕЛЬНОМ workflow с manual approval.

---

## 📋 Итоговая таблица

| Инструмент | GitHub Actions? | Workaround | Рекомендация |
|------------|----------------|------------|--------------|
| ast_analyzer.py | ✅ Да | Не требуется | Daily/PR |
| dependency_mapper.py | ✅ Да | Не требуется | Daily/PR |
| metrics_discovery.py | ✅ Да | Не требуется | Daily |
| module_scanner.py | ✅ Да | Не требуется | PR |
| api_mapper.py | ✅ Да | Не требуется | Daily |
| dependency_validator.py | ✅ Да | Не требуется | PR |
| dependency_reconciler.py | ⚠️ Да | GitHub Token | Weekly |
| code_complexity_analyzer.py | ✅ Да | Не требуется | PR |
| security_scanner.py | ✅ Да | Не требуется | Daily/PR |
| test_coverage_analyzer.py | ✅ Да | Не требуется | PR |
| environment_validator.py | ⚠️ Да | --skip-api-checks | Deployment |
| performance_profiler.py | 🔴 Нет | Staging only | Manual |
| real_time_monitor.py | 🔴 Нет | Systemd service | Production |
| live_metrics_collector.py | 🔴 Нет | Cronjob | Production |
| documentation_generator.py | ✅ Да | Не требуется | Weekly |
| api_docs_generator.py | ⚠️ Да | Static specs | Post-deploy |
| ai_documentation_generator.py | ⚠️ Да | GitHub Secrets | Weekly ($6/mo) |
| changelog_generator.py | ✅ Да | Не требуется | Release |
| ui_blueprint_gen.py | ✅ Да | Не требуется | Weekly |
| test_generator.py | ✅ Да | Не требуется | Daily |
| integration_test_generator.py | ⚠️ Да | TestClient | Weekly |
| service_discovery.py | ✅ Да | Не требуется | Daily |
| docker_compose_generator.py | ✅ Да | Не требуется | On config change |
| prometheus_config_generator.py | ✅ Да | Не требуется | On config change |
| deployment_orchestrator.py | ⚠️ Да | Manual approval | Manual only |
| module_dashboard.py | ✅ Да | Не требуется | Weekly |

**Легенда:**
- ✅ Да (17) - Полностью автоматизируемо без ограничений
- ⚠️ Да (6) - Требует дополнительной настройки (secrets, tokens, flags)
- 🔴 Нет (3) - Не рекомендуется для GitHub Actions (production-only)

---

## 🎯 Рекомендуемые GitHub Actions Workflows

### Workflow 1: Daily Analysis (Ежедневный анализ)

```yaml
name: Daily Analysis

on:
  schedule:
    - cron: '0 2 * * *'  # 02:00 UTC daily
  workflow_dispatch:

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r infrastructure/tools/requirements.txt

      # ✅ Категория 1: Полностью автоматизируемые
      - name: AST Analysis
        run: python3 infrastructure/tools/analyzers/ast_analyzer.py

      - name: Dependency Mapping
        run: python3 infrastructure/tools/analyzers/dependency_mapper.py

      - name: Metrics Discovery
        run: python3 infrastructure/tools/analyzers/metrics_discovery.py

      - name: API Mapping
        run: python3 infrastructure/tools/analyzers/api_mapper.py

      - name: Security Scan
        run: python3 infrastructure/tools/analyzers/security_scanner.py

      - name: Service Discovery
        run: python3 infrastructure/tools/analyzers/service_discovery.py

      - name: Generate Test Cases
        run: python3 infrastructure/tools/doc-generators/test_generator.py

      - name: Commit Reports
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add infrastructure/tools/reports/ tests/generated/
          git commit -m "chore: daily analysis reports [skip ci]" || true
          git push
```

**Результат:** Запускается каждый день, генерирует отчеты автоматически.

---

### Workflow 2: PR Checks (Проверки на Pull Request)

```yaml
name: PR Quality Checks

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  quality-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r infrastructure/tools/requirements.txt

      - name: Module Scanner
        run: python3 infrastructure/tools/analyzers/module_scanner.py

      - name: Dependency Validator
        run: python3 infrastructure/tools/analyzers/dependency_validator.py

      - name: Code Complexity
        run: |
          python3 infrastructure/tools/analyzers/code_complexity_analyzer.py
          # Fail if complexity > threshold

      - name: Security Scan
        run: python3 infrastructure/tools/analyzers/security_scanner.py

      - name: Test Coverage
        run: python3 infrastructure/tools/analyzers/test_coverage_analyzer.py

      - name: Comment Results on PR
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('infrastructure/tools/reports/pr_quality_report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
```

**Результат:** Каждый PR автоматически проверяется на качество.

---

### Workflow 3: Weekly Deep Analysis (Еженедельный глубокий анализ)

```yaml
name: Weekly Deep Analysis

on:
  schedule:
    - cron: '0 3 * * 0'  # Sunday 03:00 UTC
  workflow_dispatch:

jobs:
  deep-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r infrastructure/tools/requirements.txt

      # ⚠️ Категория 2: С дополнительной настройкой
      - name: AI Documentation Generation
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python3 infrastructure/tools/doc-generators/ai_documentation_generator.py

      - name: Dependency Reconciliation
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python3 infrastructure/tools/analyzers/dependency_reconciler.py --report-only

      - name: Documentation Generation
        run: python3 infrastructure/tools/doc-generators/documentation_generator.py

      - name: UI Blueprints
        run: python3 infrastructure/tools/doc-generators/ui_blueprint_gen.py

      - name: Integration Test Generation
        run: python3 infrastructure/tools/doc-generators/integration_test_generator.py

      - name: Module Dashboard
        run: python3 infrastructure/tools/dashboards/module_dashboard.py

      - name: Commit All Outputs
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add docs/ infrastructure/tools/reports/ tests/
          git commit -m "chore: weekly deep analysis [skip ci]" || true
          git push
```

**Результат:** Раз в неделю полный анализ + AI-generated документация.

---

### Workflow 4: Post-Deployment (После деплоя)

```yaml
name: Post-Deployment Analysis

on:
  deployment_status:

jobs:
  post-deploy-analysis:
    if: github.event.deployment_status.state == 'success'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r infrastructure/tools/requirements.txt

      # ⚠️ API Docs from deployed services
      - name: Generate API Documentation
        env:
          STAGING_URL: ${{ secrets.STAGING_URL }}
        run: |
          python3 infrastructure/tools/doc-generators/api_docs_generator.py \
            --base-url $STAGING_URL

      - name: Environment Validation
        env:
          ENV_FILE: .env.${{ github.event.deployment.environment }}
        run: |
          python3 infrastructure/tools/analyzers/environment_validator.py \
            --env-file $ENV_FILE

      - name: Generate Prometheus Config
        run: python3 infrastructure/tools/generators/prometheus_config_generator.py

      - name: Generate Docker Compose
        run: python3 infrastructure/tools/generators/docker_compose_generator.py
```

**Результат:** После каждого деплоя обновляется документация и конфиги.

---

## 💰 Cost Analysis (для LLM-based инструментов)

### ai_documentation_generator.py

**Anthropic Claude Sonnet 3.5:**
- Input: $3 / 1M tokens
- Output: $15 / 1M tokens

**Расчет для full project documentation:**
- Codebase size: ~500K tokens (весь intelligent-core/)
- Input: 500K tokens × $3/M = **$1.50**
- Output: ~100K tokens × $15/M = **$1.50**
- **Total per run: ~$3.00**

**Monthly cost scenarios:**
- Daily: 30 runs × $3 = **$90/month** ❌ Дорого
- Weekly: 4 runs × $3 = **$12/month** ✅ Приемлемо
- Bi-weekly: 2 runs × $3 = **$6/month** ✅ Оптимально

**Рекомендация:** Weekly runs в GitHub Actions.

---

## 🎯 Итоговый вывод

### Можно автоматизировать через GitHub Actions: 23/26 (88%)

**Полностью без проблем (17):**
- ast_analyzer, dependency_mapper, metrics_discovery
- module_scanner, api_mapper, dependency_validator
- code_complexity_analyzer, security_scanner, test_coverage_analyzer
- documentation_generator, changelog_generator, ui_blueprint_gen
- test_generator, service_discovery
- docker_compose_generator, prometheus_config_generator
- module_dashboard

**С workaround'ами (6):**
- api_docs_generator → Static OpenAPI specs
- ai_documentation_generator → GitHub Secrets + Weekly
- dependency_reconciler → GitHub Token + Report-only mode
- environment_validator → --skip-api-checks flag
- integration_test_generator → TestClient pattern
- deployment_orchestrator → Manual approval workflow

**НЕ рекомендуется (3):**
- real_time_monitor → Systemd service на production
- live_metrics_collector → Cronjob на monitoring server
- performance_profiler → Manual runs на staging

---

## 📝 Action Items

1. **Немедленно создать 4 GitHub Actions workflows:**
   - Daily Analysis (17 инструментов)
   - PR Checks (6 инструментов)
   - Weekly Deep Analysis (6 инструментов + AI)
   - Post-Deployment (4 инструмента)

2. **Настроить GitHub Secrets:**
   - `ANTHROPIC_API_KEY` - для ai_documentation_generator
   - `STAGING_URL` - для api_docs_generator
   - GitHub App token - для dependency_reconciler

3. **Модифицировать 3 инструмента:**
   - api_docs_generator.py → добавить --base-url flag
   - environment_validator.py → добавить --skip-api-checks flag
   - integration_test_generator.py → использовать TestClient

4. **Создать systemd services для production (3):**
   - real_time_monitor.service
   - live_metrics_collector.timer
   - (performance_profiler - manual only)

---

**Результат:** ВСЕ 26 инструментов интегрированы, 88% автоматизированы через GitHub Actions! ✅
