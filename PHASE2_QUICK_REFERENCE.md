# Phase 2 Quick Reference 🚀

**Версия**: 2.3.0 (Рационально-Интуитивно-Прагматичная система)
**Дата**: 2025-10-09

---

## 🎯 Быстрый старт

### Импорт компонентов

```python
# 1. ГЛАЗА - Resource Tracker
from infrastructure.mio_manager.integrations.resource_tracker_client import (
    ResourceTrackerClient, ResourceSnapshot, ResourceState
)

# 2. МОЗГ ТАКТИЧЕСКИЙ - Wishlist Integration
from infrastructure.decision_center.wishlist_integration import (
    WishlistDecisionIntegration
)

# 3. БАЛАНСИРОВЩИКИ
from intelligent_core.ai_foundation.balancer import (
    # System Balancer (МОЗГ ГЛОБАЛЬНЫЙ)
    SystemBalancer, BalanceState, GlobalImbalance,
    
    # RATIONAL dimension
    ImpactEvidenceTracker, ImpactEvidence, ImpactLevel,
    
    # INTUITIVE + PRAGMATIC dimensions
    PredictiveROIOptimizer, HealthTrend, ROIProjection,
    
    # 3D Balance
    ThreeDimensionalBalancer, BalancedDecision
)
```

---

## 🔄 Примеры использования

### 1. Resource Tracker (ГЛАЗА)

```python
# Создать и запустить мониторинг ресурсов
tracker = ResourceTrackerClient(
    eventbus=eventbus,
    check_interval=60  # каждые 60 секунд
)

await tracker.start()

# Получить текущий snapshot
snapshot = tracker.get_latest_snapshot()
print(f"CPU: {snapshot.cpu_percent}%")
print(f"Memory: {snapshot.memory_percent}%")

# Получить доступные ресурсы для Wishlist
available = tracker.get_available_resources()
print(f"Available CPU: {available['cpu']}%")
```

### 2. Wishlist Integration (МОЗГ ТАКТИЧЕСКИЙ)

```python
# Интеграция Wishlist в DecisionCenter
wishlist_integration = WishlistDecisionIntegration(
    decision_center=decision_center,
    resource_tracker=resource_tracker,
    eventbus=eventbus
)

await wishlist_integration.start()

# Отложить решение если нет ресурсов
wish = await wishlist_integration.postpone_decision_to_wishlist(
    decision=decision,
    resource_cost={'cpu': 20, 'memory': 512},
    urgency=0.8,
    deadline_seconds=300
)

# Background executor автоматически обработает когда ресурсы появятся
```

### 3. System Balancer (МОЗГ ГЛОБАЛЬНЫЙ)

```python
# Создать System Balancer
balancer = SystemBalancer(eventbus=eventbus)

# Подписаться на события дисбаланса
await balancer.subscribe_to_events()

# Обнаружить глобальный дисбаланс
imbalance = balancer.detect_global_imbalance(modules_health)
if imbalance:
    print(f"Дисбаланс: {imbalance.severity}")
    print(f"Причина: {imbalance.reason}")

# Балансировка приоритетов (ПООЩРЕНИЕ/НАКАЗАНИЕ)
available_resources = {'cpu': 400, 'memory': 8192, 'disk': 100}
allocation = await balancer.balance_priorities(imbalance, available_resources)

# ПООЩРЕНИЕ: health > 80 → ресурсы × 0.7
# НАКАЗАНИЕ: health < 50 → ресурсы × 1.5
```

### 4. Impact Evidence Tracker (RATIONAL)

```python
# Создать трекер доказательств
evidence_tracker = ImpactEvidenceTracker()

# 1. Зафиксировать baseline (ДО вмешательства)
evidence_tracker.record_baseline(
    module_name="workflow-intelligence",
    health_score=45.0,
    cpu_usage=80.0,
    memory_usage=85.0
)

# 2. Зафиксировать вмешательство
intervention_id = evidence_tracker.record_intervention(
    intervention_id="int_001",
    module_name="workflow-intelligence",
    intervention_type="scale_up",
    allocated_cpu=40.0,
    allocated_memory=1024,
    reasoning="Health < 50, scaling up"
)

# 3. Зафиксировать outcome (ПОСЛЕ вмешательства)
evidence_tracker.record_outcome(
    intervention_id=intervention_id,
    health_score=75.0,  # +30 improvement!
    cpu_usage=60.0,
    memory_usage=65.0
)

# 4. Вычислить impact и ROI
evidence = evidence_tracker.calculate_impact(intervention_id)
print(f"Health improvement: {evidence.health_delta}")
print(f"ROI: {evidence.roi}")
print(f"Confidence: {evidence.confidence}")

# 5. Рационализация: стоило ли?
rationale = evidence_tracker.rationalize_decision(intervention_id)
print(f"Justified: {rationale['justified']}")
print(f"Recommendations: {rationale['recommendations']}")
```

### 5. Predictive ROI Optimizer (INTUITIVE + PRAGMATIC)

```python
# Создать предиктивный оптимизатор
roi_optimizer = PredictiveROIOptimizer(
    evidence_tracker=evidence_tracker
)

# ИНТУИЦИЯ: Предсказать тренд здоровья
trend = roi_optimizer.predict_health_trend(
    module_name="workflow-intelligence",
    horizon=PredictionHorizon.MEDIUM  # 5-30 минут
)
print(f"Direction: {trend.direction}")  # rising/falling/stable
print(f"Predicted in 5min: {trend.predicted_5min}")
print(f"Predicted in 30min: {trend.predicted_30min}")

# ИНТУИЦИЯ: Предсказать будущие дисбалансы
future_imbalances = roi_optimizer.predict_future_imbalances(
    modules=all_modules,
    horizon_minutes=30
)
for imb in future_imbalances:
    print(f"Module {imb.module_name} будет в дисбалансе через {imb.minutes_ahead} минут")

# ПРАГМАТИКА: Рассчитать ROI проекцию
roi_projection = roi_optimizer.calculate_roi_projection(
    module_name="workflow-intelligence",
    intervention_type="scale_up",
    allocated_cpu=40.0,
    allocated_memory=1024,
    predicted_health_improvement=30.0
)
print(f"Projected ROI: {roi_projection.projected_roi}")
print(f"Risk-adjusted ROI: {roi_projection.risk_adjusted_roi}")
print(f"Worth doing: {roi_projection.worth_doing}")

# Оптимизировать вмешательства по ROI
optimized = roi_optimizer.optimize_interventions(
    possible_interventions=[intervention1, intervention2, intervention3],
    max_interventions=2
)
# Вернёт top-2 по ROI
```

### 6. Three-Dimensional Balancer (БАЛАНС)

```python
# Создать трёхмерный балансировщик
balancer_3d = ThreeDimensionalBalancer(
    evidence_tracker=evidence_tracker,
    roi_optimizer=roi_optimizer
)

# Принять сбалансированное решение (RATIONAL + INTUITIVE + PRAGMATIC)
context = {
    'current_health': 45.0,
    'available_resources': 30.0,  # Low resources!
    'data_quality': 0.8,
    'in_crisis': True  # health < 50
}

decision = balancer_3d.make_balanced_decision(
    module_name="workflow-intelligence",
    context=context
)

print(f"Action: {decision.action_type}")
print(f"Resources: CPU={decision.cpu_allocation}, Memory={decision.memory_allocation}")
print(f"Reasoning: {decision.reasoning}")

# Адаптивные веса
print(f"Rational weight: {decision.weights.rational_weight}")
print(f"Intuitive weight: {decision.weights.intuitive_weight}")
print(f"Pragmatic weight: {decision.weights.pragmatic_weight}")
print(f"Balance score: {decision.balance_score}")  # 1.0 = идеальный баланс
```

---

## 📊 Метрики для мониторинга

### Ключевые метрики по компонентам:

```python
# Resource Tracker
resource_tracker.stats['snapshots_taken']
resource_tracker.stats['deficit_detections']
resource_tracker.stats['surplus_detections']

# System Balancer
system_balancer.stats['global_imbalances_detected']
system_balancer.stats['rewards_given']  # health > 80
system_balancer.stats['penalties_given']  # health < 50
system_balancer.stats['balance_score']  # 0-1

# Impact Evidence Tracker
evidence_tracker.stats['interventions_tracked']
evidence_tracker.stats['roi_calculated']
evidence_tracker.stats['justified_decisions']

# Predictive ROI Optimizer
roi_optimizer.stats['trends_predicted']
roi_optimizer.stats['future_imbalances_detected']
roi_optimizer.stats['roi_projections_calculated']

# Three-Dimensional Balancer
balancer_3d.stats['decisions_made']
balancer_3d.stats['balance_score']
balancer_3d.stats['weight_adaptations']
```

---

## 🔍 События EventBus

### Публикуемые события:

```python
# Resource Tracker
'platform.resources.snapshot'           # каждые 60s
'platform.resources.deficit'            # при дефиците
'platform.resources.surplus'            # при избытке

# Survival Instinct
'platform.bcm.imbalance_detected'       # при дисбалансе KPI

# System Balancer
'platform.bcm.balance_state_changed'    # изменение состояния баланса
'platform.bcm.stabilization_triggered'  # критический дисбаланс
'platform.bcm.allocation_recommended'   # рекомендация по ресурсам
```

---

## 🎓 Принципы работы

### ПООЩРЕНИЕ/НАКАЗАНИЕ (System Balancer):

```
IF health_score > 80:
    allocated_resources × 0.7  # REWARD: good health → reduce priority
    
IF health_score < 50:
    allocated_resources × 1.5  # PENALTY: poor health → increase priority
```

### Три измерения (Three-Dimensional Balancer):

```
RATIONAL (Evidence-Based):
- Что мы ЗНАЕМ точно?
- Baseline → Intervention → Outcome
- ROI calculation, confidence metrics

INTUITIVE (Pattern-Based):
- Что мы ПРЕДЧУВСТВУЕМ?
- Health trends, future imbalances
- Pattern recognition

PRAGMATIC (ROI-Driven):
- Что ВЫГОДНО делать?
- Cost/benefit analysis
- Risk-adjusted ROI, breakeven time
```

### Адаптивные веса:

```
Context-aware weight adaptation:
- High confidence dimension → weight × 1.3
- Low resources (< 30%) → pragmatic_weight × 1.5
- In crisis (health < 30) → balance towards 0.33/0.33/0.33
- High data quality → rational_weight × 1.3

Learning rate α = 0.3 для постепенной конвергенции
```

---

## 🚦 Состояния и пороги

### Resource States:
- **DEFICIT**: CPU > 70% OR Memory > 80% OR Disk I/O > 50 MB/s
- **NORMAL**: В норме
- **SURPLUS**: CPU < 30% AND Memory < 40%

### Health States:
- **CRITICAL**: health < 30
- **POOR**: 30 <= health < 50
- **FAIR**: 50 <= health < 70
- **GOOD**: 70 <= health < 80
- **EXCELLENT**: health >= 80

### ROI Thresholds:
- **min_roi**: 1.5 (default) - минимальный ROI для оправдания действия
- **min_confidence**: 0.7 (default) - минимальная уверенность в доказательствах

---

## 📁 Файлы

```
intelligent-core/ai-foundation/balancer/
├── __init__.py                          # Экспорт всех балансировщиков
├── system_balancer.py                   # МОЗГ ГЛОБАЛЬНЫЙ + ПООЩРЕНИЕ/НАКАЗАНИЕ
├── impact_evidence_tracker.py           # RATIONAL dimension
├── predictive_roi_optimizer.py          # INTUITIVE + PRAGMATIC dimensions
└── three_dimensional_balancer.py        # 3D BALANCE

infrastructure/AI-office-infrastructure/mio-manager/integrations/
└── resource_tracker_client.py           # ГЛАЗА

infrastructure/decision-center/
└── wishlist_integration.py              # МОЗГ ТАКТИЧЕСКИЙ

intelligent-core/system-bcm-service/instincts/
└── survival.py                          # ВЫЖИТЬ + EventBus
```

---

## 🎯 Когда что использовать?

### Resource Tracker:
- Нужно знать доступные ресурсы
- Wishlist decision making
- Real-time resource monitoring

### System Balancer:
- Глобальная балансировка между модулями
- Автоматическая стабилизация
- ПООЩРЕНИЕ/НАКАЗАНИЕ механизм

### Impact Evidence Tracker:
- Нужны доказательства эффективности
- ROI calculation для стейкхолдеров
- Learning insights (что работает?)

### Predictive ROI Optimizer:
- Предсказание будущих дисбалансов
- ROI проекции для планирования
- Оптимизация вмешательств

### Three-Dimensional Balancer:
- Сложные решения требующие баланса
- Context-aware decision making
- Адаптация к изменяющимся условиям

---

**Дата**: 2025-10-09
**Автор**: MD + Claude (Партнёры)
**Версия**: 2.3.0
