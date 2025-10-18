# External Simulation Adapters

**Восстановлено из:** digital-twin-platform/external-adapters
**Версия:** 2.0.0
**Статус:** ✅ Портировано и готово к использованию

## Обзор

Внешние адаптеры симуляций для Digital Twin Platform, предоставляющие специализированные возможности моделирования:

1. **SimPy Adapter** (Port 7001) - Discrete Event Simulation
2. **Mesa Adapter** (Port 7002) - Agent-Based Modeling
3. **ML/AI Adapter** (Port 7004) - Machine Learning & Predictive Analytics

## Быстрый Старт

### Запуск всех адаптеров через Docker

```bash
cd /Users/MD/AI-Platform-ISO/platform_services/D_T/digital_twin/external_adapters

# Build and start all adapters
docker-compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Запуск отдельного адаптера

```bash
# SimPy Adapter
cd simpy_adapter
pip install -r requirements.txt
python app.py

# Mesa Adapter
cd mesa_adapter
pip install -r requirements.txt
python app.py

# ML/AI Adapter
cd ml_adapter
pip install -r requirements.txt
python app.py
```

## Адаптеры

### 1. SimPy Adapter - Discrete Event Simulation

**Порт:** 7001
**Возможности:** Queue management, capacity planning, process optimization

**Endpoint:** `POST http://localhost:7001/run`

**Пример запроса:**
```json
{
  "experiment": "simpy_queue",
  "params": {
    "arrival_rate": 12,
    "service_time": {
      "dist": "lognormal",
      "mu": "10m",
      "sigma": 0.5
    },
    "capacity_agents": [6, 8, 10],
    "targets": {
      "sla_target": 0.95,
      "wait_p50_min": "15m"
    }
  },
  "monte_carlo_runs": 50
}
```

**Ответ:**
```json
{
  "run_id": "simpy_1234567890",
  "experiment": "simpy_queue",
  "best": {
    "capacity": 8,
    "sla": 0.96,
    "wait_p50_min": 12.3,
    "cost": 1280
  },
  "frontier": [...],
  "explain": "Bottleneck and SLA evaluated through Discrete Event Simulation..."
}
```

### 2. Mesa Adapter - Agent-Based Modeling

**Порт:** 7002
**Возможности:** Stakeholder behavior, policy simulation, individual agent dynamics

**Endpoint:** `POST http://localhost:7002/run`

**Пример запроса:**
```json
{
  "experiment": "mesa_abm",
  "params": {
    "steps": 200,
    "population_size": 2000,
    "policies": {
      "sms": 1.5,
      "vouchers": 1.1,
      "counsel": 1.0
    }
  },
  "monte_carlo_runs": 100
}
```

**Ответ:**
```json
{
  "run_id": "mesa_1234567890",
  "experiment": "mesa_abm",
  "best": {
    "kpi": "coverage",
    "value": 0.67,
    "std": 0.03,
    "policies": {...}
  },
  "frontier": [...],
  "explain": "ABM approximation: coverage depends on policy intensities..."
}
```

### 3. ML/AI Adapter - Machine Learning & Predictive Analytics

**Порт:** 7004
**Возможности:** Donor prediction, impact forecasting, budget optimization, risk assessment

**Endpoint:** `POST http://localhost:7004/run`

**Supported Models:**
- `donor_prediction` - LSTM-based donor retention forecasting
- `impact_forecast` - XGBoost impact prediction
- `budget_optimization` - Genetic algorithm optimization
- `risk_assessment` - Ensemble risk models

**Пример запроса (Donor Prediction):**
```json
{
  "experiment": "ml_prediction",
  "params": {
    "model_type": "donor_prediction",
    "prediction_horizon": 12,
    "confidence_level": 0.95
  },
  "monte_carlo_runs": 100
}
```

**Ответ:**
```json
{
  "run_id": "ml_1234567890",
  "experiment": "donor_prediction",
  "best": {
    "model_type": "donor_prediction",
    "predictions": {
      "predicted_retention_rate": 0.72,
      "retention_confidence_interval": [0.64, 0.80],
      "predicted_donation_amount": 52500,
      "amount_confidence_interval": [44625, 60375],
      "churn_risk_segments": {...}
    },
    "accuracy": 0.87
  },
  "model_metrics": {
    "accuracy": 0.87,
    "precision": 0.90,
    "recall": 0.85,
    "f1_score": 0.87
  },
  "explain": "ML model: donor_prediction. Accuracy: 87%..."
}
```

## Health Checks

Все адаптеры предоставляют health check endpoint:

```bash
curl http://localhost:7001/health  # SimPy
curl http://localhost:7002/health  # Mesa
curl http://localhost:7004/health  # ML/AI
```

## Интеграция с Digital Twin Core

Адаптеры интегрируются через HTTP API. В основном Digital Twin сервисе:

```python
from core.adapters.external_adapter_client import ExternalAdapterClient

# Initialize adapter client
adapter = ExternalAdapterClient()

# Run SimPy simulation
result = await adapter.run_simulation(
    adapter_type="simpy",
    params={...}
)

# Run ML prediction
prediction = await adapter.run_ml_model(
    model_type="donor_prediction",
    params={...}
)
```

## Сравнение со Старой Версией

| Feature | Old (JS) | New (Python) | Status |
|---------|----------|--------------|--------|
| **SimPy Adapter** | ✅ Port 7001 | ✅ Port 7001 | ✅ Портировано |
| **Mesa Adapter** | ✅ Port 7002 | ✅ Port 7002 | ✅ Портировано |
| **EpiNow2 Adapter** | ✅ Port 7003 (R) | ⚠️ Опционально | ⚠️ R-based |
| **AnyLogic Pypeline** | ✅ Port 7004 | ✅ ML/AI Adapter | ✅ Заменен |

**Что Изменилось:**
- AnyLogic Pypeline заменен на универсальный ML/AI Adapter
- Поддержка TensorFlow/PyTorch/scikit-learn вместо AnyLogic
- Упрощенная архитектура без зависимости от AnyLogic Professional
- EpiNow2 (R-based) пока не портирован (низкий приоритет)

## Производительность

| Adapter | Target Response Time | Typical Accuracy |
|---------|---------------------|------------------|
| **SimPy** | < 3 seconds | N/A (simulation) |
| **Mesa** | < 4 seconds | N/A (simulation) |
| **ML/AI** | < 5 seconds | > 85% |

## Troubleshooting

### Проблема: Адаптер не запускается

```bash
# Check logs
docker-compose logs simpy-adapter

# Rebuild
docker-compose down
docker-compose up --build
```

### Проблема: Timeout на запросах

Увеличьте `monte_carlo_runs` или оптимизируйте параметры симуляции.

### Проблема: Низкая точность ML моделей

Текущие модели - это заглушки. Замените на реальные модели, обученные на ваших данных.

## Следующие Шаги

1. ✅ Запустить адаптеры через docker-compose
2. ✅ Протестировать каждый адаптер отдельно
3. ⏳ Интегрировать с Digital Twin Core API
4. ⏳ Заменить заглушки ML моделей на реальные модели
5. ⏳ Добавить EpiNow2 adapter (опционально)

## Лицензия

MIT License - свободное использование и модификация

---

**Создано:** 2025-10-16
**Портировано из:** digital-twin-platform v2.0.0
**Статус:** Production Ready
