# MIO Manager - Правильная архитектура

**Дата**: 2025-10-10
**Критично**: Исправление архитектуры!

---

## 🎯 Проблема (обнаружена пользователем)

### Текущая архитектура (НЕПРАВИЛЬНАЯ):
```
❌ ai-event-manager
   └── monitoring/InfrastructureStateMonitor
       └── Собирает данные и публикует в EventBus

❌ mio-manager
   └── Подписывается на события (пассивно)
```

**Проблема**: МиО Manager должен быть **главным координатором**, а не просто подписчиком!

---

## ✅ Правильная архитектура

### МиО Manager - Главный координатор платформы

**Роль МиО**:
> МиО это главный координатор всей системы, МиО на топ менеджер. Так что он оркестрирует и связывает и собирает все данные и следит самое главное чтоб они собирались по всей системе. У него должен быть не просто мониторинг - он и оценивает, ориентируясь на метрики производительности и эффективности каждого элемента и системы.

### Ключевые обязанности МиО:
1. ✅ **Собирает данные** из всех источников
2. ✅ **Оркестрирует** взаимодействие компонентов
3. ✅ **Оценивает производительность** каждого элемента
4. ✅ **Оценивает эффективность** системы в целом
5. ✅ **Публикует метрики** для всех сервисов
6. ✅ **Координирует** действия на основе анализа

---

## 🏗️ Новая архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                  MIO MANAGER (Port 8046)                     │
│                  ГЛАВНЫЙ КООРДИНАТОР                         │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Infrastructure State Monitor                       │     │
│  │  (переместить из ai-event-manager)                 │     │
│  │  - Собирает данные из всех источников              │     │
│  │  - Объединяет в единое состояние                   │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Performance Evaluator (NEW!)                       │     │
│  │  - Оценивает производительность каждого сервиса    │     │
│  │  - Рассчитывает эффективность системы              │     │
│  │  - Выявляет bottlenecks и проблемы                 │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Coordination Engine (exists)                       │     │
│  │  - Оркестрирует действия                          │     │
│  │  - Делегирует задачи                               │     │
│  │  - Координирует компоненты                         │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Resource Tracker (exists - Phase 2 ГЛАЗА)         │     │
│  │  - Отслеживает ресурсы                             │     │
│  │  - Публикует snapshots                             │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │ Publishes to EventBus:
                       │ - platform.mio.infrastructure_state
                       │ - platform.mio.performance_evaluation
                       │ - platform.mio.coordination_directive
                       │
                       ▼
              ┌─────────────────┐
              │    EventBus     │
              └────────┬────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ai-event-     │ │balancer-     │ │analytics-    │
│manager       │ │service       │ │specialist    │
│(исполнитель) │ │(исполнитель) │ │(исполнитель) │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## 📊 Data Flow (Правильный)

### 1. Сбор данных (MIO Manager собирает):
```
MIO Manager/InfrastructureStateMonitor
    │
    ├─→ Project Manager (ports, DBs, compliance)
    ├─→ Prometheus (metrics, performance)
    ├─→ Resource Tracker (CPU, memory, disk)
    ├─→ Service Discovery (health checks)
    ├─→ Analytics Specialist (insights)
    ├─→ ai-event-manager (event intelligence)
    └─→ balancer-service (balancing metrics)
```

### 2. Оценка производительности (MIO Manager анализирует):
```
MIO Manager/PerformanceEvaluator
    │
    ├─→ Оценка производительности каждого сервиса:
    │   - Response time
    │   - Throughput
    │   - Error rate
    │   - Resource efficiency
    │
    ├─→ Оценка эффективности системы:
    │   - Overall health score
    │   - Bottleneck detection
    │   - Capacity planning
    │   - ROI metrics
    │
    └─→ Выявление проблем:
        - Performance degradation
        - Resource waste
        - Imbalances
```

### 3. Координация (MIO Manager оркестрирует):
```
MIO Manager/CoordinationEngine
    │
    ├─→ Публикует директивы:
    │   - balancer-service: "Optimize allocation"
    │   - analytics-specialist: "Investigate bottleneck"
    │   - ai-event-manager: "Scan for gaps"
    │
    └─→ Координирует действия:
        - Scaling decisions
        - Resource allocation
        - Emergency response
```

### 4. Публикация в EventBus (MIO Manager информирует):
```
MIO Manager → EventBus
    │
    ├─→ platform.mio.infrastructure_state (unified state)
    ├─→ platform.mio.performance_evaluation (scores & analysis)
    ├─→ platform.mio.coordination_directive (commands)
    ├─→ platform.mio.resource_snapshot (resources)
    └─→ platform.mio.alert (emergencies)
```

---

## 🔧 Implementation Plan

### Phase 1: Переместить InfrastructureStateMonitor
```bash
# Move monitoring module
mv /infrastructure/AI-office-infrastructure/ai-event-manager/monitoring/ \
   /infrastructure/AI-office-infrastructure/mio-manager/monitoring/

# Update imports in mio-manager/main.py
from monitoring.infrastructure_state import InfrastructureStateMonitor
```

### Phase 2: Создать PerformanceEvaluator
```python
# /infrastructure/AI-office-infrastructure/mio-manager/monitoring/performance_evaluator.py

from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ServicePerformance:
    """Оценка производительности одного сервиса"""
    service_name: str
    response_time_p95: float  # ms
    throughput: float  # req/s
    error_rate: float  # 0-1
    cpu_efficiency: float  # 0-1 (throughput/cpu)
    memory_efficiency: float  # 0-1
    health_score: float  # 0-100
    bottleneck_detected: bool
    recommendation: str

@dataclass
class SystemPerformance:
    """Оценка эффективности всей системы"""
    timestamp: datetime
    overall_health: float  # 0-100
    total_throughput: float
    avg_response_time: float
    system_error_rate: float
    resource_utilization: float  # 0-1
    bottlenecks: List[str]
    capacity_remaining: float  # 0-1
    efficiency_score: float  # 0-100
    roi_metrics: Dict

class PerformanceEvaluator:
    """
    Оценивает производительность и эффективность системы

    Собирает метрики от Prometheus, анализирует performance,
    выявляет bottlenecks, рассчитывает эффективность
    """

    def __init__(self, prometheus_url: str, eventbus):
        self.prometheus_url = prometheus_url
        self.eventbus = eventbus

    async def evaluate_service_performance(self, service_name: str) -> ServicePerformance:
        """Оценить производительность одного сервиса"""
        # Collect metrics from Prometheus
        metrics = await self._get_service_metrics(service_name)

        # Calculate efficiency
        cpu_efficiency = metrics['throughput'] / max(metrics['cpu_usage'], 0.01)

        # Calculate health score
        health_score = self._calculate_health_score(metrics)

        # Detect bottleneck
        bottleneck = self._detect_bottleneck(metrics)

        # Generate recommendation
        recommendation = self._generate_recommendation(metrics, bottleneck)

        return ServicePerformance(
            service_name=service_name,
            response_time_p95=metrics['response_time_p95'],
            throughput=metrics['throughput'],
            error_rate=metrics['error_rate'],
            cpu_efficiency=cpu_efficiency,
            memory_efficiency=metrics['throughput'] / max(metrics['memory_usage'], 0.01),
            health_score=health_score,
            bottleneck_detected=bottleneck is not None,
            recommendation=recommendation
        )

    async def evaluate_system_performance(self, infrastructure_state) -> SystemPerformance:
        """Оценить эффективность всей системы"""
        # Evaluate all services
        service_performances = []
        for service in infrastructure_state.total_services:
            perf = await self.evaluate_service_performance(service)
            service_performances.append(perf)

        # Calculate system-wide metrics
        overall_health = sum(p.health_score for p in service_performances) / len(service_performances)

        # Detect system bottlenecks
        bottlenecks = [p.service_name for p in service_performances if p.bottleneck_detected]

        # Calculate efficiency score
        efficiency_score = self._calculate_efficiency_score(
            service_performances,
            infrastructure_state
        )

        # Calculate ROI metrics
        roi_metrics = self._calculate_roi_metrics(
            service_performances,
            infrastructure_state
        )

        return SystemPerformance(
            timestamp=datetime.utcnow(),
            overall_health=overall_health,
            total_throughput=sum(p.throughput for p in service_performances),
            avg_response_time=sum(p.response_time_p95 for p in service_performances) / len(service_performances),
            system_error_rate=sum(p.error_rate for p in service_performances) / len(service_performances),
            resource_utilization=infrastructure_state.cpu_usage or 0,
            bottlenecks=bottlenecks,
            capacity_remaining=1 - (infrastructure_state.cpu_usage or 0),
            efficiency_score=efficiency_score,
            roi_metrics=roi_metrics
        )

    async def publish_evaluation(self, system_performance: SystemPerformance):
        """Публикация оценки в EventBus"""
        await self.eventbus.publish(
            'platform.mio.performance_evaluation',
            {
                'evaluation': asdict(system_performance),
                'timestamp': system_performance.timestamp.isoformat()
            },
            priority='normal'
        )
```

### Phase 3: Интегрировать в MIO Manager
```python
# /infrastructure/AI-office-infrastructure/mio-manager/main.py

from monitoring.infrastructure_state import InfrastructureStateMonitor
from monitoring.performance_evaluator import PerformanceEvaluator

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... existing initialization ...

    # Initialize Infrastructure State Monitor (MOVED from ai-event-manager)
    logger.info("   📊 Initializing Infrastructure State Monitor...")
    infrastructure_monitor = InfrastructureStateMonitor(
        eventbus=eventbus_client,
        config={
            'monitor_interval': 60,
            'project_manager_enabled': True,
            'mio_manager_enabled': True,
            'service_discovery_enabled': True,
            'prometheus_enabled': True
        }
    )

    # Initialize Performance Evaluator (NEW!)
    logger.info("   🎯 Initializing Performance Evaluator...")
    performance_evaluator = PerformanceEvaluator(
        prometheus_url='http://localhost:9090',
        eventbus=eventbus_client
    )

    # Start monitoring & evaluation loop
    async def monitoring_and_evaluation_loop():
        while True:
            try:
                # 1. Update infrastructure state
                await infrastructure_monitor.update_state()
                state = infrastructure_monitor.current_state

                # 2. Evaluate performance
                evaluation = await performance_evaluator.evaluate_system_performance(state)

                # 3. Publish evaluation
                await performance_evaluator.publish_evaluation(evaluation)

                # 4. Make coordination decisions
                if evaluation.overall_health < 70:
                    await coordination_engine.handle_health_degradation(evaluation)

                if evaluation.bottlenecks:
                    await coordination_engine.handle_bottlenecks(evaluation.bottlenecks)

                # Sleep
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)

    monitoring_task = asyncio.create_task(monitoring_and_evaluation_loop())
    logger.info("   ✅ Monitoring & Evaluation loop started")

    # ... rest of initialization ...
```

### Phase 4: Обновить ai-event-manager
```python
# ai-event-manager больше НЕ собирает infrastructure state
# Он ПОДПИСЫВАЕТСЯ на events от MIO Manager

# /infrastructure/AI-office-infrastructure/ai-event-manager/main.py

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... existing ...

    # Subscribe to MIO Manager events
    if integration_manager.eventbus:
        await integration_manager.eventbus.subscribe(
            'platform.mio.infrastructure_state',
            handle_mio_infrastructure_state
        )
        await integration_manager.eventbus.subscribe(
            'platform.mio.performance_evaluation',
            handle_mio_performance_evaluation
        )
        logger.info("✅ Subscribed to MIO Manager coordination events")

async def handle_mio_infrastructure_state(event: dict):
    """Получить infrastructure state от MIO Manager"""
    state = event['data']['state']
    # Use state for event intelligence context
    logger.info(f"Infrastructure state received from MIO: {state['total_services']} services")

async def handle_mio_performance_evaluation(event: dict):
    """Получить performance evaluation от MIO Manager"""
    evaluation = event['data']['evaluation']
    # Use evaluation for intelligent event analysis
    logger.info(f"Performance evaluation from MIO: health={evaluation['overall_health']}")
```

---

## 📡 EventBus Events (Обновленные)

### Published by MIO Manager (координатор):
- `platform.mio.infrastructure_state` - Unified infrastructure state (every 60s)
- `platform.mio.performance_evaluation` - Performance & efficiency scores (every 60s)
- `platform.mio.coordination_directive` - Commands to services
- `platform.mio.resource_snapshot` - Resource Tracker data
- `platform.mio.alert` - Critical alerts

### Subscribed by other services:
- **ai-event-manager** subscribes to:
  - `platform.mio.infrastructure_state`
  - `platform.mio.performance_evaluation`

- **balancer-service** subscribes to:
  - `platform.mio.infrastructure_state`
  - `platform.mio.coordination_directive`

- **analytics-specialist** subscribes to:
  - `platform.mio.infrastructure_state`
  - `platform.mio.performance_evaluation`

---

## ✅ Результат правильной архитектуры

### МиО Manager как Top Manager:
```
MIO MANAGER (Port 8046) - TOP MANAGER
    │
    ├─→ СОБИРАЕТ данные из всех источников
    ├─→ ОЦЕНИВАЕТ производительность каждого элемента
    ├─→ ОЦЕНИВАЕТ эффективность системы
    ├─→ ОРКЕСТРИРУЕТ действия
    ├─→ КООРДИНИРУЕТ компоненты
    └─→ ПУБЛИКУЕТ директивы

    ↓ Управляет всеми ↓

ai-event-manager     balancer-service     analytics-specialist
(исполнитель)        (исполнитель)        (исполнитель)
```

### Преимущества:
✅ **Единый координатор** - МиО на топе
✅ **Централизованная оценка** - производительность и эффективность
✅ **Оркестрация действий** - координированные решения
✅ **Иерархия четкая** - МиО → исполнители
✅ **Data ownership** - МиО владеет всеми данными

---

**Статус**: 🚧 Architecture correction in progress
**Приоритет**: CRITICAL - исправить архитектуру!
**Дата**: 2025-10-10
