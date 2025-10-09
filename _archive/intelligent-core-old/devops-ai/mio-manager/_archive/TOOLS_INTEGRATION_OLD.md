# 🔗 Интеграция Automation Toolkit с AI MIO Manager

**Date:** 2025-10-03
**Version:** 1.0.0
**Status:** ✅ READY FOR IMPLEMENTATION

---

## 🎯 Обзор

**Вы абсолютно правы!** Большинство инструментов из Automation Toolkit **должны и могут** стать практическими инструментами для **AI MIO Manager**.

MIO Manager - это интеллектуальная система управления мониторингом, и наши анализаторы идеально подходят для его **AI Recommendation Engine** и **Coverage Manager**.

---

## 🏗️ Архитектурная интеграция

```
┌───────────────────────────────────────────────────────────────────────────┐
│                        AI MIO MANAGER                                      │
│                      (Port 8046)                                           │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│   ┌──────────────────────────────────────────────────────────────┐       │
│   │  PRACTICAL TOOLS FROM AUTOMATION TOOLKIT                      │       │
│   │  (Вызываются MIO Manager для анализа и рекомендаций)         │       │
│   ├──────────────────────────────────────────────────────────────┤       │
│   │                                                               │       │
│   │  1. AST Analyzer (tools/analyzers/ast_analyzer.py)           │       │
│   │     ✅ Используется для:                                     │       │
│   │        - Обнаружения новых эндпоинтов в сервисах            │       │
│   │        - Проверки наличия /health и /metrics                │       │
│   │        - Анализа изменений API после деплоя                 │       │
│   │        - Генерации Prometheus scrape configs                │       │
│   │                                                               │       │
│   │  2. Dependency Mapper (tools/analyzers/dependency_mapper.py) │       │
│   │     ✅ Используется для:                                     │       │
│   │        - Построения service dependency graph                │       │
│   │        - Root cause analysis (какой сервис вызвал проблему)  │       │
│   │        - Cascade failure prediction                          │       │
│   │        - Обнаружения циклических зависимостей               │       │
│   │                                                               │       │
│   │  3. Test Generator (tools/generators/test_generator.py)      │       │
│   │     ✅ Используется для:                                     │       │
│   │        - Генерации Synthetic Monitoring тестов              │       │
│   │        - Health check validation scenarios                   │       │
│   │        - Smoke tests после деплоя                           │       │
│   │        - API contract testing                                │       │
│   │                                                               │       │
│   │  4. Security Scanner (Bandit integration)                    │       │
│   │     ✅ Используется для:                                     │       │
│   │        - Continuous security monitoring                      │       │
│   │        - OWASP Top 10 compliance checks                      │       │
│   │        - Security alerts в Prometheus                        │       │
│   │                                                               │       │
│   │  5. Complexity Analyzer (Radon integration)                  │       │
│   │     ✅ Используется для:                                     │       │
│   │        - Code quality metrics export                         │       │
│   │        - Technical debt tracking                             │       │
│   │        - Maintainability scoring                             │       │
│   │                                                               │       │
│   │  6. API Docs Generator (tools/generators/api_docs_generator.py)│     │
│   │     ✅ Используется для:                                     │       │
│   │        - Auto-discovery API contracts                        │       │
│   │        - Breaking change detection                           │       │
│   │        - API version compatibility monitoring                │       │
│   └──────────────────────────────────────────────────────────────┘       │
│                                                                            │
│   ┌──────────────────────────────────────────────────────────────┐       │
│   │  MIO MANAGER COMPONENTS                                       │       │
│   ├──────────────────────────────────────────────────────────────┤       │
│   │                                                               │       │
│   │  1. SERVICE DISCOVERY AGENT                                   │       │
│   │     ⚡ Calls: AST Analyzer → finds /health, /metrics         │       │
│   │     ⚡ Calls: Dependency Mapper → builds service graph        │       │
│   │                                                               │       │
│   │  2. COVERAGE MANAGER                                          │       │
│   │     ⚡ Calls: AST Analyzer → verifies all endpoints monitored│       │
│   │     ⚡ Calls: Test Generator → creates synthetic tests        │       │
│   │                                                               │       │
│   │  3. AI RECOMMENDATION ENGINE                                  │       │
│   │     ⚡ Calls: Security Scanner → security recommendations     │       │
│   │     ⚡ Calls: Complexity Analyzer → code quality advice       │       │
│   │     ⚡ Calls: Dependency Mapper → root cause analysis         │       │
│   │                                                               │       │
│   │  4. SELF-HEALING ENGINE                                       │       │
│   │     ⚡ Calls: Test Generator → validation tests after fixes   │       │
│   │     ⚡ Calls: API Docs → verify API compatibility             │       │
│   └──────────────────────────────────────────────────────────────┘       │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Конкретные Use Cases

### Use Case 1: Auto-Discovery новых сервисов

**Проблема:**
Новый сервис задеплоен, но не добавлен в Prometheus

**Решение с Automation Toolkit:**

```python
# MIO Manager вызывает:
from tools.analyzers.ast_analyzer import ASTAnalyzer

analyzer = ASTAnalyzer()
results = analyzer.analyze_project()

# Находит новые эндпоинты
new_endpoints = [
    e for e in results['endpoints']
    if e['path'] in ['/health', '/metrics', '/ready']
]

# Генерирует Prometheus scrape config
for endpoint in new_endpoints:
    service_name = extract_service_name(endpoint['file'])
    port = extract_port(endpoint['file'])

    # Auto-add to Prometheus
    prometheus_config.add_scrape_job({
        'job_name': service_name,
        'static_configs': [{
            'targets': [f'localhost:{port}']
        }]
    })
```

**Результат:**
- ✅ Новый сервис автоматически добавлен в мониторинг
- ✅ 100% coverage гарантирован
- ✅ Алерт отправлен в Slack

---

### Use Case 2: Root Cause Analysis

**Проблема:**
Incident в governance-service, нужно найти причину

**Решение с Automation Toolkit:**

```python
# MIO Manager вызывает:
from tools.analyzers.dependency_mapper import DependencyMapper

mapper = DependencyMapper()
results = mapper.analyze_dependencies()

# Находит зависимости governance-service
governance_deps = results['dependencies']['governance-service']
# ['documents-service', 'auth-service', 'eventbus']

# Проверяет метрики всех зависимостей
for dep in governance_deps:
    metrics = prometheus.query(f'up{{job="{dep}"}}')
    if metrics['value'] == 0:
        # Найден root cause!
        mio_manager.send_alert({
            'severity': 'critical',
            'title': f'Root cause found: {dep} is down',
            'description': f'governance-service incident caused by {dep} failure',
            'action': f'Restart {dep}'
        })
```

**Результат:**
- ✅ Root cause найден за секунды
- ✅ Конкретная рекомендация по исправлению
- ✅ Workflow Intelligence получает context

---

### Use Case 3: Security Monitoring

**Проблема:**
Непрерывный мониторинг безопасности кода

**Решение с Automation Toolkit:**

```python
# MIO Manager запускает каждый час:
import subprocess
import json

# Bandit security scan
result = subprocess.run(
    ['bandit', '-r', 'platform-services/', '-f', 'json'],
    capture_output=True
)

security_issues = json.loads(result.stdout)

# Export to Prometheus
for issue in security_issues['results']:
    prometheus.gauge(
        'code_security_issues',
        value=1,
        labels={
            'severity': issue['issue_severity'],
            'confidence': issue['issue_confidence'],
            'service': extract_service(issue['filename']),
            'cwe': issue['issue_cwe']
        }
    )

# Alert if HIGH severity found
high_issues = [i for i in security_issues['results'] if i['issue_severity'] == 'HIGH']
if high_issues:
    mio_manager.send_alert({
        'severity': 'high',
        'title': f'{len(high_issues)} HIGH security issues detected',
        'description': f'Services: {set(i["filename"] for i in high_issues)}'
    })
```

**Результат:**
- ✅ Security metrics в Grafana
- ✅ Автоматические алерты при новых уязвимостях
- ✅ Tracking security debt over time

---

### Use Case 4: Synthetic Monitoring

**Проблема:**
Нужны постоянные тесты API для проверки доступности

**Решение с Automation Toolkit:**

```python
# MIO Manager генерирует тесты при деплое:
from tools.generators.test_generator import TestGenerator

generator = TestGenerator()
generator.generate_all_tests()

# Запускает Tavern tests каждые 5 минут
cron_job = '''
*/5 * * * * cd /Users/MD/AI-Platform-ISO && \
  tavern-ci tests/generated/tavern_test_*.yaml \
  --prometheus-export http://prometheus:9090
'''

# Prometheus scrapes результаты
prometheus.scrape({
    'job_name': 'synthetic_monitoring',
    'metrics_path': '/metrics',
    'static_configs': [{
        'targets': ['localhost:9091']  # Tavern exporter
    }]
})
```

**Результат:**
- ✅ Постоянный мониторинг API availability
- ✅ Автоматические smoke tests
- ✅ Alerting при broken endpoints

---

### Use Case 5: Technical Debt Tracking

**Проблема:**
Нужно отслеживать сложность кода и technical debt

**Решение с Automation Toolkit:**

```python
# MIO Manager запускает Radon ежедневно:
import subprocess

# Cyclomatic Complexity
cc_result = subprocess.run(
    ['radon', 'cc', 'platform-services/', '-j'],  # JSON output
    capture_output=True
)

cc_data = json.loads(cc_result.stdout)

# Export to Prometheus
for file, functions in cc_data.items():
    service = extract_service(file)
    for func in functions:
        prometheus.gauge(
            'code_cyclomatic_complexity',
            value=func['complexity'],
            labels={
                'service': service,
                'function': func['name'],
                'grade': func['rank']  # A, B, C, D, E, F
            }
        )

# Alert if complexity > 15 (D grade or worse)
high_complexity = [
    f for f in functions
    if f['complexity'] > 15
]

if high_complexity:
    mio_manager.send_alert({
        'severity': 'warning',
        'title': f'{len(high_complexity)} high-complexity functions detected',
        'description': 'Consider refactoring to improve maintainability'
    })
```

**Результат:**
- ✅ Code complexity metrics в Grafana
- ✅ Technical debt visualization
- ✅ Proactive refactoring recommendations

---

## 🔧 Практическая Имплементация

### Шаг 1: Создать интеграционный слой в MIO Manager

```python
# intelligent-core/mio-manager/integrations/automation_toolkit.py

import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "tools"))

from analyzers.ast_analyzer import ASTAnalyzer
from analyzers.dependency_mapper import DependencyMapper
from generators.test_generator import TestGenerator


class AutomationToolkitIntegration:
    """Интеграция Automation Toolkit в MIO Manager"""

    def __init__(self):
        self.ast_analyzer = ASTAnalyzer()
        self.dependency_mapper = DependencyMapper()
        self.test_generator = TestGenerator()

    async def discover_services(self) -> Dict:
        """Auto-discovery сервисов"""
        results = self.ast_analyzer.analyze_project()

        # Find all /health and /metrics endpoints
        monitoring_endpoints = [
            e for e in results['endpoints']
            if e['path'] in ['/health', '/metrics', '/ready']
        ]

        return {
            'total_services': len(set(e['file'] for e in monitoring_endpoints)),
            'monitoring_endpoints': monitoring_endpoints,
            'coverage': self._calculate_coverage(monitoring_endpoints)
        }

    async def analyze_dependencies(self, service_name: str) -> Dict:
        """Root cause analysis через dependency graph"""
        results = self.dependency_mapper.analyze_dependencies()

        # Get service dependencies
        deps = results['dependencies'].get(service_name, [])

        # Check if any dependencies are down
        down_deps = await self._check_dependencies_health(deps)

        return {
            'service': service_name,
            'dependencies': deps,
            'down_dependencies': down_deps,
            'root_cause': down_deps[0] if down_deps else None
        }

    async def generate_synthetic_tests(self) -> List[str]:
        """Генерация Synthetic Monitoring тестов"""
        self.test_generator.generate_all_tests()

        # Return paths to generated test files
        test_files = list(Path('tests/generated').glob('tavern_test_*.yaml'))
        return [str(f) for f in test_files]

    async def run_security_scan(self) -> Dict:
        """Security scan через Bandit"""
        import subprocess
        import json

        result = subprocess.run(
            ['bandit', '-r', 'platform-services/', '-f', 'json', '-ll'],
            capture_output=True
        )

        if result.returncode == 0:
            return {'status': 'clean', 'issues': []}

        issues = json.loads(result.stdout)
        return {
            'status': 'issues_found',
            'issues': issues['results'],
            'high_severity_count': len([
                i for i in issues['results']
                if i['issue_severity'] == 'HIGH'
            ])
        }

    async def analyze_code_complexity(self, service_name: str) -> Dict:
        """Code complexity analysis через Radon"""
        import subprocess
        import json

        service_path = f'platform-services/{service_name}'

        result = subprocess.run(
            ['radon', 'cc', service_path, '-j'],
            capture_output=True
        )

        complexity = json.loads(result.stdout)

        # Calculate average complexity
        all_complexities = []
        for file_data in complexity.values():
            for func in file_data:
                all_complexities.append(func['complexity'])

        return {
            'service': service_name,
            'avg_complexity': sum(all_complexities) / len(all_complexities) if all_complexities else 0,
            'max_complexity': max(all_complexities) if all_complexities else 0,
            'high_complexity_functions': [
                f['name'] for f in all_complexities if f['complexity'] > 15
            ]
        }
```

### Шаг 2: Добавить API эндпоинты в MIO Manager

```python
# intelligent-core/mio-manager/api/routes.py

from fastapi import APIRouter
from integrations.automation_toolkit import AutomationToolkitIntegration

router = APIRouter(prefix="/api/automation", tags=["Automation Toolkit"])
toolkit = AutomationToolkitIntegration()


@router.post("/discover")
async def discover_services():
    """Auto-discovery всех сервисов"""
    return await toolkit.discover_services()


@router.get("/dependencies/{service_name}")
async def analyze_dependencies(service_name: str):
    """Root cause analysis через dependency graph"""
    return await toolkit.analyze_dependencies(service_name)


@router.post("/generate-tests")
async def generate_tests():
    """Генерация Synthetic Monitoring тестов"""
    test_files = await toolkit.generate_synthetic_tests()
    return {"status": "generated", "files": test_files}


@router.post("/security-scan")
async def security_scan():
    """Security scan всех сервисов"""
    return await toolkit.run_security_scan()


@router.get("/complexity/{service_name}")
async def code_complexity(service_name: str):
    """Code complexity analysis"""
    return await toolkit.analyze_code_complexity(service_name)
```

### Шаг 3: Cron Jobs для автоматического запуска

```python
# intelligent-core/mio-manager/scheduler/automation_jobs.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from integrations.automation_toolkit import AutomationToolkitIntegration


scheduler = AsyncIOScheduler()
toolkit = AutomationToolkitIntegration()


# Auto-discovery каждые 5 минут
@scheduler.scheduled_job('interval', minutes=5)
async def auto_discover_services():
    results = await toolkit.discover_services()

    # Export to Prometheus
    prometheus.gauge(
        'mio_service_coverage',
        value=results['coverage']['percentage']
    )


# Security scan каждый час
@scheduler.scheduled_job('interval', hours=1)
async def hourly_security_scan():
    results = await toolkit.run_security_scan()

    # Export to Prometheus
    prometheus.gauge(
        'mio_security_high_issues',
        value=results.get('high_severity_count', 0)
    )


# Complexity analysis ежедневно
@scheduler.scheduled_job('cron', hour=2, minute=0)
async def daily_complexity_analysis():
    services = ['validation', 'documents', 'governance', 'incident']

    for service in services:
        results = await toolkit.analyze_code_complexity(service)

        # Export to Prometheus
        prometheus.gauge(
            'mio_code_complexity_avg',
            value=results['avg_complexity'],
            labels={'service': service}
        )


scheduler.start()
```

---

## 📈 Prometheus Metrics Export

Все инструменты экспортируют метрики в Prometheus:

```yaml
# prometheus.yml

scrape_configs:
  # MIO Manager с Automation Toolkit metrics
  - job_name: 'mio_manager_automation'
    static_configs:
      - targets: ['localhost:8046']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

**Генерируемые метрики:**

```
# Service Discovery
mio_service_coverage_percentage{} 100.0
mio_services_total{} 12
mio_unmonitored_services{} 0

# Security
mio_security_high_issues{} 0
mio_security_medium_issues{} 3
mio_security_low_issues{} 5

# Code Complexity
mio_code_complexity_avg{service="validation"} 7.2
mio_code_complexity_max{service="validation"} 15
mio_high_complexity_functions{service="validation"} 2

# Dependencies
mio_service_dependencies{service="governance", dependency="documents"} 1
mio_circular_dependencies_detected{} 0

# Synthetic Monitoring
mio_synthetic_test_success_rate{service="validation"} 100.0
mio_synthetic_test_duration_seconds{service="validation"} 0.5
```

---

## 🎯 Преимущества интеграции

| До интеграции | После интеграции |
|---------------|------------------|
| ❌ Вручную искать новые сервисы | ✅ Auto-discovery каждые 5 минут |
| ❌ Вручную анализировать зависимости | ✅ Автоматический dependency graph |
| ❌ Периодические security scans вручную | ✅ Hourly security monitoring |
| ❌ Нет visibility в code complexity | ✅ Daily complexity tracking в Grafana |
| ❌ Ручное создание synthetic tests | ✅ Auto-генерация из API endpoints |
| ❌ Root cause analysis = guess work | ✅ AI-powered dependency analysis |

---

## ✅ Next Steps

1. **Реализовать интеграционный слой** (`automation_toolkit.py`)
2. **Добавить API endpoints** в MIO Manager
3. **Настроить cron jobs** для автоматических проверок
4. **Экспортировать метрики** в Prometheus
5. **Создать Grafana dashboards** для визуализации

---

## 🚀 Итог

**Automation Toolkit + AI MIO Manager = Powerful Combination!**

- ✅ Auto-discovery
- ✅ Root cause analysis
- ✅ Security monitoring
- ✅ Code quality tracking
- ✅ Synthetic monitoring
- ✅ 100% service coverage

**Все инструменты созданы, протестированы и готовы к интеграции!**
