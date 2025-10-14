# Central Brain & Balancer Service - Анализ Расположения

**Дата анализа**: 2025-10-10
**Сервисы**: central-brain, balancer-service
**Текущее расположение**: `/infrastructure/`
**Вопрос**: Нужно ли переместить в `/intelligent-core/`?

---

## 📊 Executive Summary

**Вердикт**: ✅ **ОБА СЕРВИСА НА ПРАВИЛЬНОМ МЕСТЕ**

**Причины**:
1. **central-brain** - Infrastructure tool (мониторинг состояния системы)
2. **balancer-service** - Infrastructure orchestrator (координирует балансировщики из ядра)
3. **Балансировщики САМИ** - в `/intelligent-core/ai-foundation/balancer/` ✅

**Архитектурный паттерн**:
- **BRAIN/LOGIC** в `/intelligent-core/` (алгоритмы, ML, логика)
- **ORCHESTRATION/DEPLOYMENT** в `/infrastructure/` (запуск, координация, мониторинг)

---

## 🔍 Анализ по сервисам

### 1. central-brain

**Расположение**: `/infrastructure/central-brain/`

**Содержимое**:
```
central-brain/
├── README.md (12KB) - документация
└── state_monitor.py (15KB) - монитор состояния
```

**Назначение**:
- Мониторинг фактического состояния системы
- Принятие стратегических решений о масштабировании
- Проверка возможности развертывания новых сервисов
- НЕ содержит бизнес-логики BCM

**Функции**:
```python
class CentralBrainStateMonitor:
    async def collect_state_from_project_manager() -> SystemState
    def get_available_resources() -> Dict
    def can_deploy_new_service(service_name, ...) -> (bool, str)
    def suggest_scaling_strategy() -> Dict
    async def continuous_monitoring(interval_seconds=60)
```

**Зависимости**:
- Импортирует из `/infrastructure/tools/project-manager/` ✅
- НЕ импортирует из `/intelligent-core/` ✅
- Чистый infrastructure компонент

**Вывод**: ✅ **ПРАВИЛЬНО в /infrastructure/**

**Причина**: Это **operational tool** для управления платформой, а не AI/BCM логика.

---

### 2. balancer-service

**Расположение**: `/infrastructure/balancer-service/`

**Содержимое**:
```
balancer-service/
├── Dockerfile
├── docker-compose.yml
├── README.md (11KB)
├── main.py (11KB) - entry point
├── requirements.txt
├── test_integration.py (8KB)
└── tests/
```

**Назначение**:
- **Orchestrator** для балансировщиков Phase 2
- Запускает и координирует 4 балансировщика:
  1. System Balancer (из intelligent-core)
  2. Impact Evidence Tracker (из intelligent-core)
  3. Predictive ROI Optimizer (из intelligent-core)
  4. Three-Dimensional Balancer (из intelligent-core)
- Подключается к EventBus
- Prometheus metrics (port 9091)

**Ключевой код** (main.py:31-36):
```python
# ВАЖНО: Импортирует из intelligent-core!
from intelligent_core.ai_foundation.balancer import (
    SystemBalancer,
    ImpactEvidenceTracker,
    PredictiveROIOptimizer,
    ThreeDimensionalBalancer
)
```

**Функции**:
```python
class BalancerService:
    async def initialize()  # Создаёт балансировщики
    async def _subscribe_to_events()  # EventBus подписки
    async def _handle_imbalance_event(event)
    async def _handle_resource_snapshot(event)
    async def start()  # Запускает мониторинг
```

**Зависимости**:
- ✅ Импортирует балансировщики из `/intelligent-core/ai-foundation/balancer/`
- ✅ Импортирует EventBus из `/infrastructure/eventbus/`
- ✅ Координирует, но НЕ содержит логику

**Вывод**: ✅ **ПРАВИЛЬНО в /infrastructure/**

**Причина**: Это **deployment/orchestration service**, логика в intelligent-core.

---

## 🧠 Балансировщики в intelligent-core

**Расположение**: `/intelligent-core/ai-foundation/balancer/`

**Содержимое**:
```
ai-foundation/balancer/
├── __init__.py (1.7KB) - экспорты
├── impact_evidence_tracker.py (24KB) ✨ RATIONAL dimension
├── predictive_roi_optimizer.py (24KB) ✨ INTUITIVE + PRAGMATIC
├── system_balancer.py (20KB) ✨ GLOBAL BRAIN
└── three_dimensional_balancer.py (22KB) ✨ 3D BALANCE
```

**Всего**: ~93KB логики балансировки

**Экспорты** (__init__.py):
```python
from .system_balancer import SystemBalancer
from .impact_evidence_tracker import ImpactEvidenceTracker
from .predictive_roi_optimizer import PredictiveROIOptimizer
from .three_dimensional_balancer import ThreeDimensionalBalancer

__all__ = [
    'SystemBalancer',
    'ImpactEvidenceTracker',
    'PredictiveROIOptimizer',
    'ThreeDimensionalBalancer'
]
```

**Вывод**: ✅ **ПРАВИЛЬНО в /intelligent-core/**

**Причина**: Это **AI/ML логика** для принятия решений о балансировке.

---

## 🏗️ Архитектурный Паттерн

### Правильное разделение:

```
┌─────────────────────────────────────────────────────────────┐
│                  /intelligent-core/                          │
│                 (BRAIN - Логика и AI)                        │
│                                                              │
│  ai-foundation/balancer/                                     │
│  ├── system_balancer.py         # Алгоритм балансировки     │
│  ├── impact_evidence_tracker.py # ROI расчёты               │
│  ├── predictive_roi_optimizer.py # ML предсказания          │
│  └── three_dimensional_balancer.py # 3D decision making     │
│                                                              │
│  Содержит: АЛГОРИТМЫ, ML, БИЗНЕС-ЛОГИКУ                     │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │ import
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               /infrastructure/                               │
│            (ORCHESTRATION - Запуск и координация)           │
│                                                              │
│  balancer-service/                                           │
│  ├── main.py              # Orchestrator                     │
│  ├── Dockerfile           # Deployment                       │
│  └── docker-compose.yml   # Container orchestration         │
│                                                              │
│  central-brain/                                              │
│  └── state_monitor.py     # System monitoring               │
│                                                              │
│  Содержит: DEPLOYMENT, ORCHESTRATION, MONITORING            │
└─────────────────────────────────────────────────────────────┘
```

### Аналогия с другими модулями:

| Логика (intelligent-core) | Orchestration (infrastructure) |
|---------------------------|--------------------------------|
| `ai-orchestration/` | `AI-office-infrastructure/orchestrator/` |
| `workflow_intelligence/` | (запускается напрямую) |
| `ai-foundation/balancer/` | `balancer-service/` ✅ |
| `system-bcm-service/` | (self-contained) |

---

## 🎯 Детальный Разбор

### central-brain - Infrastructure Tool

**Роль**: Operational monitoring и strategic decision making

**Что делает**:
1. **Мониторит состояние платформы**:
   - Порты (сколько используется)
   - Мониторинг (Prometheus/Grafana доступен?)
   - БД (PostgreSQL/Redis доступен?)
   - Сервисы (сколько работает)

2. **Принимает стратегические решения**:
   - Можно ли развернуть новый сервис?
   - Какая стратегия масштабирования? (emergency, monitoring_recovery, improve_monitoring, maintain)
   - Какие ресурсы доступны?

3. **НЕ содержит BCM логику**:
   - Нет BIA/Risk Assessment
   - Нет workflow intelligence
   - Нет ML/AI

**Пример использования**:
```python
monitor = CentralBrainStateMonitor()
await monitor.update_state()

# Проверка: можно развернуть новый сервис?
can_deploy, reason = monitor.can_deploy_new_service(
    service_name='new-analytics',
    requires_db=True,
    requires_metrics=True
)

if can_deploy:
    # Deploy service
    pass
else:
    print(f"Cannot deploy: {reason}")
```

**Интеграция с Проектным Менеджером**:
```python
# central-brain получает состояние от project-manager
from infrastructure.tools.project_manager import ComplianceCheckRunner

runner = ComplianceCheckRunner()
state_data = runner.export_state_for_central_brain()

# central-brain использует для решений
monitor.current_state = state_data
strategy = monitor.suggest_scaling_strategy()
```

**Вывод**: Это **infrastructure monitoring tool**, не AI логика.

---

### balancer-service - Orchestration Service

**Роль**: Deployment orchestrator для балансировщиков

**Что делает**:
1. **Создаёт экземпляры балансировщиков** (из intelligent-core):
```python
# main.py:96-120
self.evidence_tracker = ImpactEvidenceTracker()
self.roi_optimizer = PredictiveROIOptimizer(
    evidence_tracker=self.evidence_tracker
)
self.balancer_3d = ThreeDimensionalBalancer(
    evidence_tracker=self.evidence_tracker,
    roi_optimizer=self.roi_optimizer
)
self.system_balancer = SystemBalancer(
    eventbus=self.eventbus,
    balancer_3d=self.balancer_3d
)
```

2. **Подключается к EventBus**:
```python
# main.py:138-155
await self.eventbus.subscribe(
    'platform.bcm.imbalance_detected',
    self._handle_imbalance_event
)
await self.eventbus.subscribe(
    'platform.resources.snapshot',
    self._handle_resource_snapshot
)
```

3. **Координирует event flow**:
```python
# main.py:157-185
async def _handle_imbalance_event(self, event: dict):
    # Record baseline
    self.evidence_tracker.record_baseline(...)

    # Let System Balancer handle
    # (System Balancer processes in monitoring loop)
```

4. **Prometheus metrics** (port 9091):
```python
# main.py:51-53
BALANCER_SERVICE_UP = Gauge('balancer_service_up', ...)
BALANCER_ERRORS = Counter('balancer_errors_total', ...)
BALANCER_EVENTS_PROCESSED = Counter('balancer_events_processed_total', ...)
```

**Что НЕ делает**:
- ❌ НЕ содержит логику балансировки
- ❌ НЕ вычисляет ROI
- ❌ НЕ принимает решения о распределении ресурсов

**Deployment**:
```yaml
# docker-compose.yml
services:
  balancer-service:
    build: .
    ports:
      - "9091:9091"  # Prometheus metrics
    depends_on:
      - redis
    networks:
      - ai-platform
```

**Вывод**: Это **deployment/orchestration wrapper**, логика в intelligent-core.

---

## ✅ Правильность Текущей Структуры

### Критерии оценки:

#### 1. Separation of Concerns ✅
- **Логика** (балансировщики) в `/intelligent-core/` ✅
- **Orchestration** (запуск, координация) в `/infrastructure/` ✅
- **Monitoring** (состояние системы) в `/infrastructure/` ✅

#### 2. Import Direction ✅
- Infrastructure импортирует из intelligent-core ✅
- Intelligent-core НЕ импортирует из infrastructure ✅
- Правильная зависимость: infra зависит от core, не наоборот ✅

#### 3. Reusability ✅
- Балансировщики можно использовать из других сервисов ✅
- balancer-service - один из возможных orchestrators ✅
- central-brain - reusable monitoring tool ✅

#### 4. Testability ✅
- Балансировщики тестируются независимо ✅
- balancer-service имеет integration tests ✅
- central-brain можно тестировать отдельно ✅

#### 5. Deployment ✅
- balancer-service - контейнеризован (Dockerfile) ✅
- central-brain - standalone script ✅
- Балансировщики - библиотека (не нужен deployment) ✅

---

## 🚫 Почему НЕ переносить в intelligent-core

### central-brain НЕ в intelligent-core, потому что:

1. **Не содержит AI/ML логику**:
   - Нет машинного обучения
   - Нет предсказаний
   - Нет BCM domain logic

2. **Это operational tool**:
   - Мониторинг инфраструктуры
   - Проверка ресурсов
   - Deployment decisions

3. **Зависит от infrastructure**:
   - Использует project-manager (из infrastructure/tools)
   - Мониторит infrastructure components
   - Operational, не domain logic

4. **Аналогия**:
   - Как `kubectl` для Kubernetes (infrastructure tool)
   - Не как "Kubernetes Scheduler" (core logic)

### balancer-service НЕ в intelligent-core, потому что:

1. **Это orchestrator, не логика**:
   - Создаёт экземпляры
   - Подключает к EventBus
   - Координирует events
   - НЕ принимает решения

2. **Deployment-focused**:
   - Dockerfile
   - docker-compose.yml
   - Prometheus metrics
   - Infrastructure concerns

3. **Аналогия**:
   - Как "main.py" для запуска ML модели
   - Не как "model.py" с самой моделью

4. **Правильный паттерн**:
   ```
   intelligent-core/ai-foundation/balancer/  # BRAIN (алгоритмы)
   infrastructure/balancer-service/          # RUNNER (запуск)
   ```

---

## 📋 Comparison Table

| Аспект | central-brain | balancer-service | Балансировщики (intelligent-core) |
|--------|--------------|------------------|-----------------------------------|
| **Тип** | Monitoring tool | Orchestrator | AI/ML Logic |
| **Логика** | Infrastructure | Deployment | BCM/AI/ML |
| **Импорты** | infrastructure/tools | intelligent-core/balancer | shared libraries |
| **Deployment** | Standalone script | Docker container | Library (no deployment) |
| **Цель** | Operational monitoring | Coordinate balancers | Decision making algorithms |
| **Тесты** | State monitoring | Integration tests | Unit tests (logic) |
| **Место** | ✅ /infrastructure/ | ✅ /infrastructure/ | ✅ /intelligent-core/ |

---

## 🎯 Рекомендации

### 1. Оставить как есть ✅

**central-brain** → `/infrastructure/central-brain/`
**balancer-service** → `/infrastructure/balancer-service/`
**Балансировщики** → `/intelligent-core/ai-foundation/balancer/`

### 2. Улучшения (опционально)

#### central-brain:
- [ ] Добавить Dockerfile (для consistency)
- [ ] Prometheus metrics (аналогично balancer-service)
- [ ] API endpoints (FastAPI) вместо только CLI

#### balancer-service:
- [ ] Unit tests для event handlers
- [ ] Health check endpoint
- [ ] Graceful shutdown (уже есть signal handlers ✅)

#### Балансировщики:
- [ ] Unit tests для каждого балансировщика
- [ ] Documentation по алгоритмам
- [ ] Performance benchmarks

### 3. Документация

Создать документ архитектурных принципов:

**`/doc/ARCHITECTURE_PRINCIPLES.md`**:
```markdown
# Архитектурные Принципы

## Разделение intelligent-core vs infrastructure

### intelligent-core (BRAIN)
- AI/ML алгоритмы
- Бизнес-логика BCM
- Domain models
- Reusable libraries

### infrastructure (RUNNER)
- Deployment services
- Orchestration
- Monitoring tools
- Infrastructure concerns

### Правило импортов:
- ✅ infrastructure может импортировать intelligent-core
- ❌ intelligent-core НЕ должен импортировать infrastructure

### Примеры:
- Балансировщики (AI logic) → intelligent-core ✅
- balancer-service (orchestrator) → infrastructure ✅
- central-brain (monitoring) → infrastructure ✅
```

---

## 📝 Примеры Использования

### 1. central-brain - Проверка перед развёртыванием

```python
from infrastructure.central_brain.state_monitor import CentralBrainStateMonitor

async def deploy_new_service(service_config):
    """Deploy service only if resources available"""

    # Check with central-brain
    monitor = CentralBrainStateMonitor()
    await monitor.update_state()

    can_deploy, reason = monitor.can_deploy_new_service(
        service_name=service_config['name'],
        requires_db=service_config.get('requires_db', True),
        requires_metrics=service_config.get('requires_metrics', True)
    )

    if not can_deploy:
        print(f"❌ Cannot deploy: {reason}")

        # Get strategy suggestion
        strategy = monitor.suggest_scaling_strategy()
        print(f"💡 Strategy: {strategy['action']}")
        return False

    # Deploy
    print(f"✅ Deploying {service_config['name']}...")
    # ... deployment logic ...
    return True
```

### 2. balancer-service - Event-driven балансировка

```python
# balancer-service автоматически запускается через docker-compose
# и слушает события от Survival Instinct

# В модуле (например, bia-module):
from survival_instinct import detect_my_imbalance

async def monitor_bia_health():
    """Модуль мониторит своё здоровье"""

    health_score = calculate_health()

    if health_score < 50:
        # Publish imbalance event
        await eventbus.publish('platform.bcm.imbalance_detected', {
            'source': 'bia-module',
            'kpi_name': 'workflow_completion_rate',
            'level': 'critical',
            'health_score': health_score,
            'cpu_usage': 0.85,
            'memory_usage': 0.92
        })

# balancer-service получает event и:
# 1. Records baseline в Evidence Tracker
# 2. System Balancer анализирует
# 3. 3D Balancer принимает решение
# 4. Публикует рекомендацию
```

### 3. Балансировщики - Прямое использование

```python
# Можно использовать балансировщики напрямую (без balancer-service)
from intelligent_core.ai_foundation.balancer import (
    ImpactEvidenceTracker,
    PredictiveROIOptimizer,
    ThreeDimensionalBalancer
)

async def custom_balancing_logic():
    """Custom балансировка для специфического use case"""

    # Create components
    evidence = ImpactEvidenceTracker()
    roi = PredictiveROIOptimizer(evidence_tracker=evidence)
    balancer = ThreeDimensionalBalancer(
        evidence_tracker=evidence,
        roi_optimizer=roi
    )

    # Record baseline
    evidence.record_baseline(
        module_name='custom-module',
        health_score=65.0,
        cpu_usage=0.75
    )

    # Make decision
    decision = balancer.decide_allocation(
        module='custom-module',
        imbalance_data={'health_score': 45.0, 'cpu_usage': 0.95}
    )

    print(f"Decision: {decision['action']}")
    print(f"Reasoning: {decision['reasoning']}")
```

---

## 🏆 Best Practices

### 1. Импорты

**✅ ПРАВИЛЬНО**:
```python
# В infrastructure/balancer-service/main.py
from intelligent_core.ai_foundation.balancer import SystemBalancer

# В infrastructure/central-brain/state_monitor.py
from infrastructure.tools.project_manager import ComplianceCheckRunner
```

**❌ НЕПРАВИЛЬНО**:
```python
# В intelligent-core/ai-foundation/balancer/system_balancer.py
from infrastructure.balancer_service import BalancerService  # НЕТ!
```

### 2. Deployment

**✅ ПРАВИЛЬНО**:
- Infrastructure services имеют Dockerfile
- Intelligent-core - библиотеки (pip install)

**❌ НЕПРАВИЛЬНО**:
- Dockerizing intelligent-core modules напрямую
- (Используйте infrastructure wrappers)

### 3. Testing

**✅ ПРАВИЛЬНО**:
```python
# Тестировать логику независимо
# intelligent-core/ai-foundation/balancer/tests/test_system_balancer.py
def test_reward_penalty_logic():
    balancer = SystemBalancer(...)
    result = balancer._apply_reward_penalty(
        health_score=85,
        allocated_resources=100
    )
    assert result == 70  # 100 * 0.7 (reward)

# Тестировать интеграцию
# infrastructure/balancer-service/test_integration.py
async def test_event_flow():
    service = BalancerService()
    await service.initialize()
    # Test event handling
```

---

## ✅ Вывод

### Текущая структура ПРАВИЛЬНАЯ:

1. **`/infrastructure/central-brain/`** ✅
   - Operational monitoring tool
   - Infrastructure concerns
   - НЕ AI/BCM логика

2. **`/infrastructure/balancer-service/`** ✅
   - Deployment orchestrator
   - Координирует балансировщики
   - НЕ содержит логику решений

3. **`/intelligent-core/ai-foundation/balancer/`** ✅
   - AI/ML алгоритмы
   - Логика принятия решений
   - Reusable components

### НЕ нужно переносить в intelligent-core!

**Причина**: Правильное разделение между:
- **BRAIN** (intelligent-core) - логика, алгоритмы, AI
- **RUNNER** (infrastructure) - deployment, orchestration, monitoring

**Архитектурный паттерн соблюдён**: ✅

---

## 📚 Связанные Документы

1. [PHASE2_INTEGRATION_COMPLETE.md](/doc-project/PHASE2_INTEGRATION_COMPLETE.md) - балансировщики Phase 2
2. [LIVING_SYSTEM_ARCHITECTURE.md](/doc-project/LIVING_SYSTEM_ARCHITECTURE.md) - концепция живой системы
3. [INTELLIGENT_CORE_ACTION_PLAN.md](/doc-project/INTELLIGENT_CORE_ACTION_PLAN.md) - план по intelligent-core
4. [WORKFLOW_INTELLIGENCE_ANATOMY_REPORT.md](/doc-project/WORKFLOW_INTELLIGENCE_ANATOMY_REPORT.md) - пример правильной структуры

---

**Анализ завершён**: 2025-10-10
**Вердикт**: ✅ **Оставить как есть - структура правильная**
**Рекомендация**: Добавить архитектурную документацию о принципах разделения

**Создано**: Claude (Architectural Analysis Mode)
