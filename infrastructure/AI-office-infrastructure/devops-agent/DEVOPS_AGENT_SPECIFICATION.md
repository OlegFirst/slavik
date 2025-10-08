# DevOps Agent - AI Digital Colleague 🤖

## Должностная инструкция

### Роль и Ответственность
**DevOps Agent** - автономный AI-коллега, отвечающий за:
- 🔍 **Continuous Code Analysis** - непрерывный анализ кодовой базы
- 🛠️ **Auto-Remediation** - автоматическое исправление проблем
- 📦 **Container Management** - генерация и управление Docker контейнерами
- 🚀 **Deployment Monitoring** - мониторинг развертываний
- 📊 **Infrastructure as Code** - автогенерация IaC конфигураций
- 🔗 **Service Integration** - интеграция с платформенными сервисами

---

## Специализация

### 1. Event-Driven Architecture Analysis
- Сканирование кода на наличие событий (publish/subscribe)
- Сравнение с AsyncAPI схемой
- Обнаружение пробелов (gaps) в покрытии
- Предложение новых событий на основе code patterns
- Генерация отчётов и метрик

### 2. Auto-Remediation Engine
- Генерация кода для недостающих publishers
- Создание шаблонов subscribers
- Dry-run режим для безопасного preview
- Отчётность об исправлениях

### 3. Container & Deployment Management
- **Dockerfile Generation** - автогенерация Dockerfile для сервисов
- **Docker Compose** - управление multi-container приложениями
- **Deployment Tracking** - мониторинг статуса развертываний
- **Rollback Automation** - автоматический откат при проблемах

### 4. Infrastructure as Code
- **Service Discovery** - автообнаружение сервисов
- **Port Management** - управление портами и конфликтами
- **Health Checks** - генерация health check endpoints
- **Prometheus Metrics** - автодобавление метрик

---

## Бизнес-процессы

### Цикл 1: Continuous Monitoring (каждый час)
```
1. Scan codebase for events
2. Compare with AsyncAPI schema
3. Detect gaps and issues
4. Generate recommendations
5. Export metrics to Prometheus
6. Report to Workflow Intelligence (мозг)
```

### Цикл 2: Weekly Deep Analysis (понедельник 03:00)
```
1. Full codebase scan
2. Dockerfile generation for new services
3. Port conflict detection
4. Deployment health check
5. Infrastructure drift detection
6. Comprehensive report to мозг
```

### Цикл 3: On-Demand Operations
```
1. Manual trigger via API
2. Fix specific issues (via auto-fixer)
3. Generate missing Dockerfiles
4. Update service configurations
5. Validate deployments
```

---

## Архитектура интеграции

### Коммуникация с мозгом (Workflow Intelligence)
```python
# DevOps Agent → Workflow Intelligence
{
    "agent_id": "devops-agent",
    "report_type": "infrastructure_analysis",
    "timestamp": "2025-10-08T03:00:00Z",
    "findings": {
        "event_gaps": 121,
        "critical_issues": 4,
        "missing_dockerfiles": 3,
        "port_conflicts": 1
    },
    "recommendations": [
        {
            "priority": "high",
            "category": "event_architecture",
            "action": "implement_missing_publishers",
            "affected_services": ["bia-service", "risk-service"]
        }
    ]
}
```

### Инструменты доступные DevOps Agent
1. **RAG System** (from ai-foundation) - поиск в knowledge base
2. **LLM Router** (from ai-foundation) - AI анализ и принятие решений
3. **EventBus** - публикация событий о проблемах
4. **Temporal Workflows** - оркестрация длительных операций
5. **Prometheus** - экспорт метрик

---

## Автоматизация

### CI/CD Integration (GitHub Actions)
```yaml
# .github/workflows/devops_agent_ci.yml
name: DevOps Agent - Continuous Analysis

on:
  push:
    branches: [main, develop]
  pull_request:
  schedule:
    - cron: '0 3 * * 1'  # Понедельник 03:00

jobs:
  infrastructure_analysis:
    runs-on: ubuntu-latest
    steps:
      - name: Run DevOps Agent Scan
        run: python3 tools/devops-agent/agent.py --full-scan

      - name: Check Critical Issues
        run: python3 tools/devops-agent/agent.py --validate --fail-on-critical

      - name: Generate Infrastructure Report
        run: python3 tools/devops-agent/agent.py --report
```

### Temporal Workflow
```python
# intelligent-core/workflow_intelligence/temporal_workflows/devops_agent_workflow.py

@workflow.defn
class DevOpsAgentWorkflow:
    @workflow.run
    async def run(self, config: Dict) -> Dict:
        # 1. Scan infrastructure
        scan_result = await workflow.execute_activity(
            scan_infrastructure,
            start_to_close_timeout=timedelta(minutes=10)
        )

        # 2. Analyze with AI
        analysis = await workflow.execute_activity(
            ai_analysis,
            scan_result,
            start_to_close_timeout=timedelta(minutes=5)
        )

        # 3. Auto-fix if approved
        if analysis['auto_fix_approved']:
            fix_result = await workflow.execute_activity(
                apply_fixes,
                analysis['recommendations'],
                start_to_close_timeout=timedelta(minutes=15)
            )

        # 4. Report to мозг
        await workflow.execute_activity(
            report_to_brain,
            analysis,
            start_to_close_timeout=timedelta(minutes=2)
        )

        return {"status": "completed", "analysis": analysis}
```

---

## Новый функционал

### 1. Dockerfile Generator
```python
class DockerfileGenerator:
    """Автогенерация Dockerfile для сервисов"""

    def analyze_service(self, service_path: str) -> ServiceMetadata:
        """Анализ сервиса и определение технологий"""
        # Python? Node? Go?
        # FastAPI? Flask? Express?
        # Requirements? Dependencies?

    def generate_dockerfile(self, metadata: ServiceMetadata) -> str:
        """Генерация оптимального Dockerfile"""
        # Multi-stage build
        # Layer caching optimization
        # Security best practices
        # Health checks

    def generate_docker_compose(self, services: List[ServiceMetadata]) -> str:
        """Генерация docker-compose.yml для платформы"""
```

### 2. Deployment Monitor
```python
class DeploymentMonitor:
    """Мониторинг развертываний и автоматический rollback"""

    def monitor_deployment(self, service_name: str):
        """Мониторинг процесса развертывания"""
        # Health check after deploy
        # Error rate monitoring
        # Response time tracking

    def auto_rollback(self, service_name: str, reason: str):
        """Автоматический откат при проблемах"""
        # Revert to previous version
        # Notify team
        # Report to мозг
```

### 3. Port Manager
```python
class PortManager:
    """Управление портами и разрешение конфликтов"""

    def scan_ports(self) -> Dict[int, str]:
        """Сканирование используемых портов"""

    def detect_conflicts(self) -> List[PortConflict]:
        """Обнаружение конфликтов портов"""

    def suggest_ports(self, service_name: str) -> int:
        """Предложение свободного порта"""
```

---

## Метрики и мониторинг

### Prometheus Metrics
```prometheus
# DevOps Agent Metrics
devops_agent_scans_total                    # Количество сканирований
devops_agent_issues_detected                # Обнаруженные проблемы
devops_agent_auto_fixes_applied             # Автоматические исправления
devops_agent_dockerfiles_generated          # Сгенерированные Dockerfile
devops_agent_deployments_monitored          # Отслеживаемые развертывания
devops_agent_port_conflicts_detected        # Конфликты портов
devops_agent_service_health_score           # Health score сервисов
```

### Grafana Dashboard
- Infrastructure Health Overview
- Event Architecture Coverage
- Deployment Success Rate
- Auto-Fix Statistics
- Port Usage Map

---

## Интеграция с платформой

### 1. Workflow Intelligence (мозг)
```python
# Регулярная отчётность
await brain.publish_report(
    report_type='infrastructure_health',
    report_data=devops_analysis
)

# Получение решений
decision = await brain.get_decision({
    'context': 'deployment_failure',
    'service': 'bia-service',
    'error_rate': 0.25
})
```

### 2. MIO Manager (оператор мониторинга)
```python
# DevOps Agent → MIO Manager
await mio.notify_issue(
    severity='high',
    category='port_conflict',
    details={
        'service1': 'ai-event-manager',
        'service2': 'workflow_intelligence',
        'port': 8050
    }
)
```

### 3. AI Event Manager
```python
# Совместная работа по событийной архитектуре
event_analysis = await ai_event_manager.analyze_event(
    event_name='bcm.bia.completed',
    publishers=found_publishers,
    subscribers=found_subscribers
)
```

---

## Файловая структура

```
tools/devops-agent/
├── DEVOPS_AGENT_SPECIFICATION.md      # Эта спецификация
├── README.md                          # Документация для разработчиков
├── agent.py                           # Главный orchestrator
├── analyzers/
│   ├── event_analyzer.py             # Event architecture analysis (старый event_intelligence_system.py)
│   ├── dockerfile_analyzer.py        # Dockerfile generation
│   ├── deployment_analyzer.py        # Deployment monitoring
│   └── port_analyzer.py              # Port conflict detection
├── auto_remediation/
│   ├── event_fixer.py                # Auto-fix events (старый auto_fixer.py)
│   ├── dockerfile_generator.py       # Generate Dockerfiles
│   └── deployment_healer.py          # Auto-rollback & healing
├── monitoring/
│   ├── continuous_monitor.py         # Continuous monitoring (старый)
│   ├── deployment_monitor.py         # Deployment tracking
│   └── metrics_exporter.py           # Prometheus metrics
├── integrations/
│   ├── workflow_intelligence.py      # Интеграция с мозгом
│   ├── mio_manager.py                # Интеграция с MIO
│   └── ai_event_manager.py           # Интеграция с Event Manager
└── workflows/
    ├── scan_workflow.py              # Temporal workflow: сканирование
    ├── fix_workflow.py               # Temporal workflow: исправление
    └── deploy_workflow.py            # Temporal workflow: развертывание
```

---

## Roadmap

### Phase 1: Foundation (✅ Complete)
- [x] Event Intelligence System
- [x] Auto-Fixer
- [x] Continuous Monitor
- [x] CI/CD Integration

### Phase 2: DevOps Expansion (🚧 Current)
- [ ] Dockerfile Generator
- [ ] Deployment Monitor
- [ ] Port Manager
- [ ] Service Discovery
- [ ] Integration with Workflow Intelligence

### Phase 3: Advanced Automation (📅 Planned)
- [ ] AI-powered infrastructure optimization
- [ ] Predictive deployment failure detection
- [ ] Auto-scaling recommendations
- [ ] Security vulnerability scanning
- [ ] Cost optimization analysis

---

## Принципы работы

1. **Autonomous but Supervised** - работает автономно, но критические решения согласовывает с мозгом
2. **Safety First** - всегда dry-run перед применением изменений
3. **Continuous Learning** - учится на feedback и улучшает рекомендации
4. **Platform Integration** - тесная интеграция со всеми компонентами платформы
5. **Developer-Friendly** - генерирует понятные отчёты и предложения

---

**Built with ❤️ for self-evolving platforms**
