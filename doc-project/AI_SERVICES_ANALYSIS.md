# 🤖 AI-Services - Анализ Модулей

**Дата:** 5 октября 2025
**Местоположение:** `/intelligent-core/AI-Servises/`
**Всего:** 48 Python файлов

---

## 📊 Что Внутри

### 4 Модуля:

| Модуль | Files | Описание | Статус |
|--------|-------|----------|--------|
| **mio-manager** | ~15 | AI MIO Manager - управляющий центр | ✅ Production-ready |
| **project-agent** | ~15 | Universal CLI для анализа проектов | ✅ Production-ready |
| **agent-router** | ~8 | Intelligent routing для AI агентов | ✅ Production-ready |
| **ai-devops** | ~10 | AI DevOps engine | ⚠️ Duplicate (есть в infrastructure) |

---

## 🔍 Детальный Анализ

### 1. MIO Manager (AI Monitoring & Observability Manager)

**Port:** 8046

#### Назначение:
**Управляющий центр платформы** - координирует все AI сервисы

#### Архитектура:
```
MIO Manager
├── Automation Toolkit Manager  ← Запускает инструменты анализа
├── Orchestrator Client         ← Делегирует задачи AI Orchestrator
├── Gateway Manager             ← Управляет API Gateway
└── Automation Scheduler        ← 6 автоматических задач
```

#### Возможности:

**1. Automation Toolkit Integration:**
```python
# integrations/automation_toolkit.py
class AutomationToolkitManager:
    """Запускает инструменты из /tools"""

    async def run_ast_analyzer():
        """Auto-discovery сервисов"""

    async def run_dependency_mapper():
        """Root cause analysis"""

    async def run_security_scanner():
        """Bandit OWASP scanning"""

    async def run_complexity_analyzer():
        """Radon code quality"""

    async def run_test_generator():
        """Synthetic monitoring"""
```

**2. Orchestrator Delegation:**
```python
# integrations/orchestrator_client.py
class OrchestratorClient:
    """Делегирует задачи AI Orchestrator"""

    async def delegate_task(task: Task):
        """Service restart, config updates"""

    async def get_task_status(task_id):
        """Track task execution"""
```

**3. Gateway Management:**
```python
# integrations/gateway_manager.py
class GatewayManager:
    """Управляет API Gateway"""

    async def register_service(service_info):
        """Service registration"""

    async def update_routing():
        """Routing updates"""

    async def health_check():
        """Health monitoring"""
```

**4. Automation Scheduler (APScheduler):**

| Задача | Расписание | Действие |
|--------|-----------|----------|
| Service Discovery | Каждые 5 мин | Auto-discovery новых сервисов |
| Security Scan | Каждый час | Bandit security scan |
| Dependency Analysis | Каждые 15 мин | Root cause analysis |
| Code Complexity | Ежедневно 2:00 | Radon complexity |
| Test Generation | Воскресенье 3:00 | Synthetic tests |
| Health Check | Каждые 2 мин | Health check всех |

#### Flow:
```
1. Обнаруживает проблему (Prometheus metrics)
   ↓
2. Анализирует через Automation Toolkit
   ↓
3. Формирует задачу (Task)
   ↓
4. Выполняет действие или делегирует Orchestrator
   ↓
5. Отчитывается в Monitoring
```

---

### 2. Project Agent (Universal CLI)

**Тип:** CLI инструмент для анализа проектов

#### Назначение:
**Универсальный анализатор проектов** с auto-detection домена

#### Возможности:

**1. Domain Detection (Авто-определение):**
```python
# agent/domain_detector.py
class DomainDetector:
    """Определяет домен проекта автоматически"""

    def detect() -> str:
        # Анализирует:
        # - Код (imports, keywords)
        # - Документацию (README, docs/)
        # - Зависимости (requirements.txt, package.json)

        return domain  # ISO 22301, Security, Fintech, Healthcare, E-commerce
```

**2. Security Module:**
```python
# agent/modules/security.py
class SecurityModule:
    def find_secrets():
        """API keys, passwords, tokens"""

    def find_vulnerabilities():
        """eval, pickle, SQL injection, XSS"""

    def analyze_dependencies():
        """Safety, npm audit integration"""
```

**3. Testing Module:**
```python
# agent/modules/testing.py
class TestingModule:
    def analyze_coverage():
        """pytest, jest, go test"""

    def check_threshold():
        """Coverage requirements"""
```

**4. Quality Module:**
```python
# agent/modules/quality.py
class QualityModule:
    def cyclomatic_complexity():
        """Code complexity"""

    def find_duplicates():
        """Code duplication"""

    def find_technical_debt():
        """TODO, FIXME, HACK, XXX"""
```

**5. Compliance Module:**
```python
# agent/modules/compliance.py
class ComplianceModule:
    def check_iso_22301():
        """BCM compliance"""

    def check_iso_27001():
        """InfoSec compliance"""

    def check_pci_dss():
        """Payment card compliance"""
```

**6. Reporting:**
```bash
# Markdown/HTML/JSON отчеты
project-agent report --format markdown --audience dev
project-agent report --format html --audience business
project-agent report --format json --audience security
```

#### CLI Commands:
```bash
# Инициализация (авто-определит домен)
project-agent init

# Статус
project-agent status

# Полное сканирование
project-agent scan

# Выборочное сканирование
project-agent scan --module security
project-agent scan --module quality --module testing
```

---

### 3. Agent Router (Intelligent Routing)

**Назначение:**
**Роутер для AI агентов** - направляет запросы к нужным сервисам

#### Архитектура:

**Agent Roles:**
1. **ORCHESTRATOR** - Main coordination (PDCA, Workflow, Decision)
2. **PROCESSOR** - Multi-service (BIA, Documents, Compliance)
3. **ASSISTANT** - Context-aware (PDCA Assistant)
4. **SPECIALIST** - Domain expert (Document AI)
5. **BRIDGE** - External integration (GitHub App)
6. **REGISTRY** - Service discovery

#### Возможности:
```python
from agent_router import AIAgentRouter, AgentCapability

router = AIAgentRouter(redis_url="redis://localhost:6379/0")

# Route request
result = await router.route_request(
    capability=AgentCapability.BIA_ANALYSIS,
    request_data={"organization": "Acme Corp"},
    context={"user_id": "123", "priority": "high"}
)

# Health check
health = await router.health_check_all_agents()

# Analytics
analytics = router.get_agent_analytics()
```

#### Features:
- ✅ Load balancing across AI agents
- ✅ Health monitoring + failover
- ✅ Request tracking (Redis)
- ✅ Analytics

---

### 4. AI DevOps (Duplicate)

**Статус:** ⚠️ Дублируется

**Уже есть в:**
- `/infrastructure/deployment-service/` (новая версия)
- `/intelligent-core/ai-devops/` (извлечено ранее)

**Рекомендация:** Архивировать

---

## 🎯 Связь с Основной Архитектурой

### Как Эти Модули Вписываются?

```
Platform Architecture
│
├── platform-services/          ← BCM сервисы
│   ├── bia-service
│   ├── compliance-service
│   └── ...
│
├── intelligent-core/
│   ├── ai_experts/             ← AI консультанты
│   ├── ai-orchestration/       ← AI Orchestrator
│   └── AI-Servises/            ← ЭТИ МОДУЛИ
│       ├── mio-manager         ← Управляющий центр
│       ├── project-agent       ← CLI для анализа
│       └── agent-router        ← Роутинг AI агентов
│
└── infrastructure/
    ├── eventbus/
    ├── database/
    └── ...
```

### Integration Points:

**1. MIO Manager ↔ Platform:**
```
MIO Manager (Port 8046)
    ↓ управляет
API Gateway
    ↓ роутит
Platform Services (BIA, Risk, Compliance, etc.)
    ↓ отчитываются
Prometheus/Grafana
    ↓ алерты
MIO Manager (обнаруживает проблемы)
```

**2. Project Agent ↔ Development:**
```bash
# Анализ кода платформы
cd /Users/MD/AI-Platform-ISO
project-agent init  # → определит: ISO 22301 (BCM)

project-agent scan --module compliance
# → Проверит соответствие ISO 22301

project-agent scan --module security
# → Найдет уязвимости, секреты
```

**3. Agent Router ↔ AI Services:**
```
User Request
    ↓
Agent Router
    ↓ определяет capability
    ├─→ BIA_ANALYSIS → bia-service
    ├─→ COMPLIANCE → compliance-service
    ├─→ ORCHESTRATION → ai-orchestration
    └─→ PDCA_GUIDANCE → ai_experts/colleagues
```

---

## 💡 Ключевые Находки

### 1. MIO Manager = Platform Control Center ⭐

**Это управляющий центр!**
- Координирует все сервисы
- Автоматические проверки (security, complexity, tests)
- Делегирует задачи AI Orchestrator
- Управляет API Gateway

**Очень важный модуль для production!**

### 2. Project Agent = DevOps CLI ⭐

**Универсальный анализатор проектов:**
- Auto-detection домена (ISO 22301, Security, etc.)
- Security scanning
- Compliance checking
- Code quality analysis

**Полезен для CI/CD и мониторинга качества!**

### 3. Agent Router = Service Mesh для AI

**Intelligent routing:**
- Знает capability каждого агента
- Load balancing
- Health monitoring
- Analytics

**Упрощает работу с multiple AI services!**

---

## 🔗 Интеграция с AI Modules

### Вопрос: Как Связать с ai_experts/colleagues?

**Вариант 1: Agent Router знает о Colleagues**
```python
# agent-router/router.py

from ai_experts.colleagues import (
    BIASpecialistAI,
    ComplianceCopilot,
    RiskAnalystAI
)

class AIAgentRouter:
    def __init__(self):
        self.colleagues = {
            'bia_specialist': BIASpecialistAI(...),
            'compliance_copilot': ComplianceCopilot(...),
            'risk_analyst': RiskAnalystAI(...)
        }

    async def route_request(self, capability, request_data):
        if capability == AgentCapability.BIA_ANALYSIS:
            # Использовать BIA Specialist
            return await self.colleagues['bia_specialist'].chat(
                user_message=request_data['query'],
                pdca_phase=request_data.get('pdca_phase', 'plan'),
                ui_context='bia'
            )
```

**Вариант 2: MIO Manager использует Colleagues для recommendations**
```python
# mio-manager/integrations/ai_advisor.py

from ai_experts.colleagues import ComplianceCopilot

class AIAdvisor:
    """AI советник для MIO Manager"""

    def __init__(self):
        self.copilot = ComplianceCopilot(...)

    async def get_remediation_advice(self, security_issues):
        """Получить советы по устранению проблем"""

        advice = await self.copilot.chat(
            user_message=f"Найдены проблемы безопасности: {security_issues}. Как исправить?",
            pdca_phase='act',
            ui_context='governance'
        )

        return advice
```

---

## 🎯 Рекомендации

### 1. MIO Manager - ОСТАВИТЬ ✅

**Место:** `/infrastructure/mio-manager/`

**Почему:**
- Управляющий центр платформы
- Автоматические проверки
- Integration с Orchestrator и Gateway
- Production-ready

**Интеграция:**
- Добавить AI Advisor (использует colleagues)
- Интеграция с EventBus (publish events)
- Prometheus metrics

---

### 2. Project Agent - ОСТАВИТЬ ✅

**Место:** `/tools/project-agent/` (dev tools)

**Почему:**
- Полезен для CI/CD
- Compliance checking
- Security scanning
- Code quality

**Использование:**
```bash
# В CI/CD pipeline
project-agent scan --module compliance
project-agent scan --module security
```

---

### 3. Agent Router - ИНТЕГРИРОВАТЬ ✅

**Место:** `/infrastructure/agent-router/`

**Почему:**
- Нужен для роутинга между AI сервисами
- Load balancing
- Health monitoring

**Интеграция:**
- Добавить роутинг к colleagues
- Интеграция с AI Expert Service (если создадим)

---

### 4. AI DevOps - АРХИВИРОВАТЬ ❌

**Уже есть в:**
- `/infrastructure/deployment-service/`

---

## 📊 Финальная Структура

```
AI-Platform-ISO/
│
├── infrastructure/
│   ├── mio-manager/           ← Управляющий центр
│   ├── agent-router/          ← AI routing
│   ├── eventbus/
│   └── database/
│
├── intelligent-core/
│   ├── ai_experts/
│   │   ├── colleagues/        ← AI коллеги
│   │   ├── tools/
│   │   │   └── organs/        ← AI движки
│   │   └── shared/ai_core/    ← RAG, LLM
│   │
│   └── ai-orchestration/      ← AI Orchestrator
│
├── platform-services/         ← BCM сервисы
│
└── tools/
    └── project-agent/         ← CLI для анализа
```

---

## ❓ Вопрос к тебе

**Что делать с AI-Services:**

1. **MIO Manager** → перенести в `/infrastructure/mio-manager/`? ✅
2. **Project Agent** → перенести в `/tools/project-agent/`? ✅
3. **Agent Router** → перенести в `/infrastructure/agent-router/`? ✅
4. **AI DevOps** → архивировать в `_archive/`? ✅

**Начинаем перенос?**
