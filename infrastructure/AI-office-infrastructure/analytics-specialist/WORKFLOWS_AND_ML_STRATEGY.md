# 🔄 Workflows & ML Models Strategy for Analytics Specialist

**Date:** 2025-10-08
**Status:** Strategic Enhancement Plan
**Purpose:** Закрепление бизнес-процессов в workflow + легкие ML модели

---

## 📋 Вопрос пользователя

> "нужно чтобы они были закреплены в воркфлоу все бизнес процессы. как должностные инструкции и автоматизированы. есть ли у него легкие модели в помощь."

**Ответ:** ✅ **ДА!** Analytics Specialist уже имеет workflow-based архитектуру, но можно существенно усилить:

1. ✅ **Workflows уже есть** - daily_health_check, incident_investigation, continuous_improvement
2. ⚠️ **Нужно расширить** - добавить workflow для КАЖДОГО бизнес-процесса BCM
3. ❌ **ML моделей пока нет** - сейчас только rule-based логика
4. 🎯 **План улучшения** - добавить легкие ML модели для предсказаний

---

## 🏗️ Текущая Архитектура Workflows

### Existing Workflows (Already Implemented)

**Location:** `analytics-specialist/workflows/`

#### 1. Daily Health Check (`daily_health_check.py`)
```python
async def daily_health_check() -> Dict[str, Any]:
    """
    Ежедневная проверка здоровья платформы

    Schedule: Every 24 hours (86400 seconds)
    Автоматизация: ✅ Запускается автоматически через lifespan

    Процесс:
    1. Анализ всех process-analytics метрик
    2. Проверка metrics coverage
    3. Анализ dependencies (если middle+)
    4. Расчет health_score (0-100)
    5. Отправка отчета в MIO Manager
    6. Если critical issues → делегирование задач Orchestrator
    """
```

**Закреплено:** ✅ Автоматический запуск каждые 24 часа
**Должностная инструкция:** "Ежедневно в 00:00 проверять здоровье платформы и докладывать МиО"

#### 2. Continuous Improvement (`continuous_improvement.py`)
```python
async def continuous_improvement_scan() -> Dict[str, Any]:
    """
    Непрерывное улучшение процессов

    Schedule: Every 1 hour (3600 seconds)
    Автоматизация: ✅ Запускается автоматически

    Процесс:
    1. Анализ metrics coverage gaps
    2. Dependency conflicts detection
    3. API health monitoring
    4. Code quality improvements
    5. Recommendations to MIO Manager
    """
```

**Закреплено:** ✅ Автоматический запуск каждый час
**Должностная инструкция:** "Каждый час сканировать платформу на возможности улучшения"

#### 3. Incident Investigation (`incident_investigation.py`)
```python
async def investigate_incident(
    incident_id: str,
    incident_details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Расследование инцидентов

    Schedule: On-demand (triggered by API call or MIO Manager)
    Автоматизация: ⚠️ Manual trigger / Event-driven

    Процесс:
    1. Анализ процесса где произошел инцидент
    2. Root cause analysis
    3. Impact assessment
    4. Prevention plan generation
    5. Report to MIO Manager
    """
```

**Закреплено:** ✅ API endpoint + Event listener
**Должностная инструкция:** "При получении инцидента - немедленно расследовать причину"

---

## 🎯 Расширение: BCM Business Processes как Workflows

### Нужно добавить workflows для ВСЕХ BCM процессов

**Стандарт:** Каждый бизнес-процесс BCM = отдельный workflow с должностной инструкцией

### 📊 Plan: 10 Core BCM Workflows

#### **Workflow 1: BIA Analysis Workflow**
```python
# File: workflows/bia_analysis_workflow.py

async def bia_analysis_workflow(bia_id: str) -> Dict[str, Any]:
    """
    Business Impact Analysis - Workflow

    Должностная инструкция:
    "При запуске BIA анализа - отслеживать выполнение, выявлять bottlenecks,
    рассчитывать качество данных, докладывать о завершении"

    Процесс:
    1. Monitor BIA execution через process-analytics
    2. Detect bottlenecks в опросах/анализе
    3. Check data quality (completeness, accuracy)
    4. Calculate BIA health score
    5. Report to MIO Manager
    6. Если проблемы → delegate to Orchestrator
    """
    core = AnalyticsCore()

    # Monitor BIA process
    bia_metrics = await core.pa_client.comprehensive_analysis("bia_workflow")

    # Analyze data quality
    insights = []
    if bia_metrics["health_score"] < 70:
        insights.append({
            "severity": "high",
            "title": "BIA процесс имеет проблемы",
            "description": f"Health score: {bia_metrics['health_score']}"
        })

    # Report to MIO
    await core.report_to_mio(...)

    return {"status": "complete", "insights": insights}
```

**Schedule:** Event-driven (когда BIA запущен) + Daily monitoring
**Автоматизация:** ✅ Event listener + Scheduled check

---

#### **Workflow 2: Risk Assessment Workflow**
```python
# File: workflows/risk_assessment_workflow.py

async def risk_assessment_workflow(risk_id: str) -> Dict[str, Any]:
    """
    Risk Assessment - Workflow

    Должностная инструкция:
    "Отслеживать процесс risk assessment, выявлять паттерны рисков,
    проверять соответствие ISO 22301, докладывать о критических рисках"

    Процесс:
    1. Monitor risk assessment execution
    2. Detect patterns в identified risks
    3. Check compliance with ISO 22301 (clauses 6.1, 8.2.3)
    4. Identify critical risks requiring immediate action
    5. Report to MIO Manager
    6. Auto-trigger mitigation planning для critical risks
    """
    # Implementation similar to BIA
```

**Schedule:** Event-driven + Weekly monitoring
**Автоматизация:** ✅

---

#### **Workflow 3: Incident Response Workflow**
```python
# File: workflows/incident_response_workflow.py

async def incident_response_workflow(incident_id: str) -> Dict[str, Any]:
    """
    Incident Response Monitoring - Workflow

    Должностная инструкция:
    "При инциденте - отслеживать response time, эффективность команды,
    собирать metrics для post-mortem, проверять compliance с планами"

    Процесс:
    1. Track incident response timeline
    2. Monitor team performance (response time, resolution time)
    3. Detect deviations from incident response plan
    4. Collect metrics for post-mortem analysis
    5. Real-time reporting to MIO Manager
    6. Trigger learning system updates after resolution
    """
```

**Schedule:** Real-time (triggered on incident creation)
**Автоматизация:** ✅ Event-driven

---

#### **Workflow 4: Compliance Audit Workflow**
```python
# File: workflows/compliance_audit_workflow.py

async def compliance_audit_workflow(audit_id: str) -> Dict[str, Any]:
    """
    Compliance Audit Monitoring - Workflow

    Должностная инструкция:
    "Отслеживать compliance audit, проверять coverage ISO 22301 clauses,
    выявлять gaps, докладывать о non-conformities"

    Процесс:
    1. Monitor audit execution
    2. Check ISO 22301 clause coverage
    3. Detect compliance gaps
    4. Track non-conformities
    5. Report to MIO Manager + Compliance Guardian
    6. Generate remediation recommendations
    """
```

**Schedule:** Event-driven + Monthly monitoring
**Автоматизация:** ✅

---

#### **Workflow 5: Plan Generation Workflow**
```python
# File: workflows/plan_generation_workflow.py

async def plan_generation_workflow(plan_id: str) -> Dict[str, Any]:
    """
    BCM Plan Generation Monitoring - Workflow

    Должностная инструкция:
    "Отслеживать генерацию планов, проверять quality, completeness,
    alignment с ISO 22301, докладывать о готовности"

    Процесс:
    1. Monitor plan generation process
    2. Check plan quality metrics
    3. Verify completeness (all required sections)
    4. Validate alignment with ISO 22301
    5. Report to MIO Manager + Plan Generator
    6. Trigger review workflow if issues found
    """
```

**Schedule:** Event-driven
**Автоматизация:** ✅

---

#### **Workflow 6: Exercise Design & Execution Workflow**
```python
# File: workflows/exercise_workflow.py

async def exercise_workflow(exercise_id: str) -> Dict[str, Any]:
    """
    BCM Exercise Monitoring - Workflow

    Должностная инструкция:
    "Отслеживать execution табletop/simulation exercises, собирать metrics,
    анализировать team performance, генерировать improvement recommendations"

    Процесс:
    1. Monitor exercise execution
    2. Track team performance metrics
    3. Detect gaps in response procedures
    4. Collect lessons learned
    5. Report to MIO Manager + Exercise Designer
    6. Trigger learning system updates
    """
```

**Schedule:** Event-driven
**Автоматизация:** ✅

---

#### **Workflow 7: Governance Review Workflow**
```python
# File: workflows/governance_review_workflow.py

async def governance_review_workflow() -> Dict[str, Any]:
    """
    Governance Review - Workflow

    Должностная инструкция:
    "Ежеквартально проверять governance processes, policy compliance,
    stakeholder engagement, management review effectiveness"

    Процесс:
    1. Analyze governance metrics (quarterly)
    2. Check policy compliance across organization
    3. Review stakeholder engagement metrics
    4. Assess management review effectiveness
    5. Report to MIO Manager + Governance Brain
    6. Generate governance improvement recommendations
    """
```

**Schedule:** Quarterly (every 90 days)
**Автоматизация:** ✅ Scheduled

---

#### **Workflow 8: Learning & Training Workflow**
```python
# File: workflows/learning_workflow.py

async def learning_workflow() -> Dict[str, Any]:
    """
    Learning & Training Monitoring - Workflow

    Должностная инструкция:
    "Отслеживать training completion, competency development,
    knowledge retention, докладывать о learning gaps"

    Процесс:
    1. Monitor training completion rates
    2. Track competency development
    3. Assess knowledge retention
    4. Identify learning gaps
    5. Report to MIO Manager + Learning Coach
    6. Generate personalized training recommendations
    """
```

**Schedule:** Weekly + Event-driven
**Автоматизация:** ✅

---

#### **Workflow 9: Supply Chain Continuity Workflow**
```python
# File: workflows/supply_chain_workflow.py

async def supply_chain_workflow() -> Dict[str, Any]:
    """
    Supply Chain Continuity Monitoring - Workflow

    Должностная инструкция:
    "Отслеживать supplier assessments, dependency risks,
    alternative supplier availability, докладывать о supply chain risks"

    Процесс:
    1. Monitor supplier health metrics
    2. Analyze supply chain dependencies
    3. Detect single points of failure
    4. Track alternative supplier readiness
    5. Report to MIO Manager
    6. Trigger risk mitigation if critical dependency found
    """
```

**Schedule:** Weekly
**Автоматизация:** ✅

---

#### **Workflow 10: Platform Health Meta-Workflow**
```python
# File: workflows/platform_health_meta_workflow.py

async def platform_health_meta_workflow() -> Dict[str, Any]:
    """
    Platform-Wide Health Meta-Analysis - Workflow

    Должностная инструкция:
    "Ежедневно агрегировать результаты всех workflows,
    строить platform-wide insights, докладывать executive summary"

    Процесс:
    1. Aggregate results from all 9 BCM workflows
    2. Calculate platform-wide health score
    3. Identify cross-cutting issues
    4. Generate executive summary
    5. Report to MIO Manager
    6. Trigger strategic planning if major issues found
    """
```

**Schedule:** Daily (after all workflows complete)
**Автоматизация:** ✅

---

## 🤖 Легкие ML Модели: Integration Strategy

### Почему легкие ML модели?

**Текущая проблема:**
- Analytics Specialist сейчас использует только **rule-based логику**
- Пример: `if health_score < 50: severity = "critical"`
- Не учитывает исторические паттерны, не предсказывает будущее

**Решение:**
- Добавить **легкие ML модели** для:
  - Предсказание bottlenecks
  - Anomaly detection
  - Pattern recognition
  - Proactive recommendations

**Требования:**
- ✅ Легкие (< 100MB)
- ✅ Быстрые (< 100ms inference time)
- ✅ Не требуют GPU
- ✅ Можно тренировать локально

---

### 🎯 ML Models Roadmap

#### **Model 1: Bottleneck Predictor** (Priority: HIGH)

**Purpose:** Предсказывать bottlenecks в процессах до их появления

**Algorithm:** Gradient Boosting (LightGBM / XGBoost)

**Features:**
```python
# Input features
features = {
    "process_id": str,              # one-hot encoded
    "avg_duration_last_7d": float,  # historical average
    "execution_count_last_24h": int,
    "time_of_day": int,             # 0-23
    "day_of_week": int,             # 0-6
    "active_users": int,
    "system_load": float,
    "dependency_health": float
}

# Output
output = {
    "bottleneck_probability": float,  # 0-1
    "predicted_step": str,            # which step will bottleneck
    "severity": str                   # low/medium/high
}
```

**Training Data Source:**
- `process_analytics.executions` table (historical data)
- `process_analytics.bottlenecks` table (labels)

**Model Size:** ~10MB (LightGBM)
**Inference Time:** ~5ms

**Implementation:**
```python
# File: ml/models/bottleneck_predictor.py

import lightgbm as lgb
import joblib
from typing import Dict, Any

class BottleneckPredictor:
    """
    Легкая ML модель для предсказания bottlenecks

    Competency Required: Middle (unlocks at middle level)
    """

    def __init__(self, model_path: str = "models/bottleneck_predictor.pkl"):
        self.model = joblib.load(model_path)

    async def predict(self, process_id: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """Предсказать вероятность bottleneck"""
        # Prepare features
        X = self._prepare_features(process_id, features)

        # Predict
        probability = self.model.predict_proba(X)[0][1]  # P(bottleneck=1)

        # Determine severity
        if probability > 0.7:
            severity = "high"
        elif probability > 0.4:
            severity = "medium"
        else:
            severity = "low"

        return {
            "bottleneck_probability": probability,
            "severity": severity,
            "predicted_at": datetime.now().isoformat()
        }

    async def train(self, training_data: pd.DataFrame):
        """Дообучение модели на новых данных"""
        # Incremental training
        pass
```

**Integration:**
```python
# In analytics_core.py

async def _analyze_processes(self) -> Dict[str, Any]:
    insights = []

    # Existing rule-based analysis
    bottlenecks = await self.pa_client.detect_bottlenecks(process_id)

    # NEW: ML-based prediction (if middle+)
    if "bottleneck_predictor" in self.ml_models:
        prediction = await self.ml_models["bottleneck_predictor"].predict(
            process_id=process_id,
            features={...}
        )

        if prediction["bottleneck_probability"] > 0.7:
            insights.append({
                "severity": "high",
                "category": "predictive",
                "title": "Bottleneck predicted in next 24h",
                "description": f"ML model predicts {prediction['bottleneck_probability']:.1%} chance",
                "recommendation": "Proactively scale resources"
            })

    return {"insights": insights}
```

---

#### **Model 2: Anomaly Detector** (Priority: HIGH)

**Purpose:** Детектировать anomalies в метриках платформы

**Algorithm:** Isolation Forest / LSTM Autoencoder (for time series)

**Features:**
```python
# Time series features
features = {
    "metric_name": str,
    "values_last_24h": List[float],  # 24 hourly values
    "day_of_week": int,
    "is_weekend": bool
}

# Output
output = {
    "is_anomaly": bool,
    "anomaly_score": float,  # 0-1 (higher = more anomalous)
    "expected_range": Tuple[float, float]
}
```

**Model Size:** ~15MB
**Inference Time:** ~10ms

**Implementation:**
```python
# File: ml/models/anomaly_detector.py

from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    """
    Легкая ML модель для anomaly detection

    Competency Required: Middle
    """

    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)

    async def detect(self, metric_name: str, values: List[float]) -> Dict[str, Any]:
        """Детектировать anomalies в метриках"""
        # Prepare features
        X = np.array(values).reshape(-1, 1)

        # Predict
        predictions = self.model.predict(X)
        scores = self.model.score_samples(X)

        # Identify anomalies
        anomalies = np.where(predictions == -1)[0]

        return {
            "is_anomaly": len(anomalies) > 0,
            "anomaly_count": len(anomalies),
            "anomaly_score": abs(scores.min()),
            "anomaly_indices": anomalies.tolist()
        }
```

---

#### **Model 3: Health Score Predictor** (Priority: MEDIUM)

**Purpose:** Предсказывать health score на 7 дней вперед

**Algorithm:** LSTM / Prophet (time series forecasting)

**Features:**
```python
# Input
features = {
    "historical_health_scores": List[float],  # last 30 days
    "upcoming_events": List[Dict],            # planned exercises, audits
    "seasonal_factors": Dict[str, float]
}

# Output
output = {
    "predicted_scores_7d": List[float],  # 7 daily predictions
    "confidence_interval": List[Tuple[float, float]],
    "trend": str  # "improving" / "stable" / "declining"
}
```

**Model Size:** ~20MB
**Inference Time:** ~50ms

---

#### **Model 4: Recommendation Ranker** (Priority: LOW)

**Purpose:** Ранжировать recommendations по приоритету/эффективности

**Algorithm:** Gradient Boosting Ranker

**Features:**
```python
# Input
features = {
    "recommendation_type": str,
    "affected_components": List[str],
    "estimated_impact": float,
    "implementation_cost": str,  # low/medium/high
    "historical_effectiveness": float
}

# Output
output = {
    "priority_score": float,  # 0-100
    "expected_roi": float
}
```

---

### 📦 ML Models Integration Architecture

```python
# File: ml/__init__.py

from typing import Dict, Any, Optional
from .models.bottleneck_predictor import BottleneckPredictor
from .models.anomaly_detector import AnomalyDetector
from .models.health_score_predictor import HealthScorePredictor
from .models.recommendation_ranker import RecommendationRanker


class MLModelsManager:
    """
    Manager для всех ML моделей Analytics Specialist

    Competency-based model loading:
    - Junior: None (rule-based only)
    - Middle: Bottleneck Predictor + Anomaly Detector
    - Senior: + Health Score Predictor
    - Expert: + Recommendation Ranker + Custom models
    """

    def __init__(self, competency_level: str):
        self.competency = competency_level
        self.models = self._load_models()

    def _load_models(self) -> Dict[str, Any]:
        """Load models based on competency level"""
        models = {}

        # Middle+ models
        if self.competency in ["middle", "senior", "expert"]:
            models["bottleneck_predictor"] = BottleneckPredictor()
            models["anomaly_detector"] = AnomalyDetector()

        # Senior+ models
        if self.competency in ["senior", "expert"]:
            models["health_score_predictor"] = HealthScorePredictor()

        # Expert models
        if self.competency == "expert":
            models["recommendation_ranker"] = RecommendationRanker()

        return models

    async def predict_bottleneck(self, process_id: str, features: Dict) -> Optional[Dict]:
        """Wrapper for bottleneck prediction"""
        if "bottleneck_predictor" not in self.models:
            return None
        return await self.models["bottleneck_predictor"].predict(process_id, features)

    async def detect_anomalies(self, metric_name: str, values: List[float]) -> Optional[Dict]:
        """Wrapper for anomaly detection"""
        if "anomaly_detector" not in self.models:
            return None
        return await self.models["anomaly_detector"].detect(metric_name, values)
```

**Integration in AnalyticsCore:**

```python
# File: core/analytics_core.py

from ..ml import MLModelsManager

class AnalyticsCore:
    def __init__(self):
        # ... existing code ...

        # NEW: ML Models
        self.ml_models = MLModelsManager(competency_level=settings.COMPETENCY_LEVEL)

    async def analyze_platform_health(self) -> AnalyticsReport:
        insights = []

        # Rule-based analysis (always)
        rule_based_insights = await self._analyze_processes()
        insights.extend(rule_based_insights["insights"])

        # ML-based predictions (if middle+)
        if self.ml_models.models:
            ml_insights = await self._ml_predict_issues()
            insights.extend(ml_insights)

        # ... rest of analysis ...

    async def _ml_predict_issues(self) -> List[AnalyticsInsight]:
        """Use ML models to predict future issues"""
        insights = []

        # Bottleneck prediction
        processes = await self.pa_client.get_all_processes()
        for process_id in processes:
            prediction = await self.ml_models.predict_bottleneck(
                process_id=process_id,
                features={...}
            )

            if prediction and prediction["bottleneck_probability"] > 0.6:
                insights.append(AnalyticsInsight(
                    id=f"ml_bottleneck_{process_id}",
                    category=InsightCategory.PERFORMANCE,
                    severity=SeverityLevel.HIGH,
                    title=f"Predicted bottleneck in {process_id}",
                    description=f"ML model predicts {prediction['bottleneck_probability']:.1%} chance",
                    affected_components=[process_id],
                    impact="Process may slow down in next 24h",
                    evidence={"ml_prediction": prediction}
                ))

        return insights
```

---

### 🔧 ML Models Training Pipeline

```python
# File: ml/training/trainer.py

class ModelTrainer:
    """
    Automated ML model training pipeline

    Schedule: Weekly (retrain models on new data)
    """

    async def train_all_models(self):
        """Train all ML models with latest data"""
        logger.info("Starting ML model training pipeline")

        # 1. Extract training data from Supabase
        training_data = await self._extract_training_data()

        # 2. Train bottleneck predictor
        bottleneck_model = await self._train_bottleneck_predictor(
            training_data["executions"],
            training_data["bottlenecks"]
        )

        # 3. Train anomaly detector
        anomaly_model = await self._train_anomaly_detector(
            training_data["metrics_history"]
        )

        # 4. Validate models
        metrics = await self._validate_models(bottleneck_model, anomaly_model)

        # 5. Deploy if better than current
        if metrics["bottleneck_accuracy"] > 0.8:
            await self._deploy_model(bottleneck_model, "bottleneck_predictor")

        logger.info(f"Training complete. Metrics: {metrics}")

        return metrics

    async def _extract_training_data(self) -> Dict[str, pd.DataFrame]:
        """Extract training data from Supabase"""
        # Query process_analytics tables
        query = """
        SELECT
            e.process_id,
            e.execution_id,
            e.start_time,
            e.end_time,
            e.status,
            b.step_name,
            b.avg_duration_minutes
        FROM process_analytics.executions e
        LEFT JOIN process_analytics.bottlenecks b
            ON e.process_id = b.process_id
        WHERE e.start_time > NOW() - INTERVAL '90 days'
        """

        # ... execute query, return DataFrames
```

**Deployment:**

```yaml
# File: workflows/ml_model_training_workflow.py

async def ml_model_training_workflow():
    """
    Weekly ML Model Training Workflow

    Schedule: Every Sunday at 02:00
    Должностная инструкция: "Еженедельно переобучать ML модели на новых данных"

    Процесс:
    1. Extract last 90 days of data from Supabase
    2. Train all ML models
    3. Validate models (accuracy, precision, recall)
    4. Deploy if better than current models
    5. Report training metrics to MIO Manager
    """
    trainer = ModelTrainer()

    # Train models
    metrics = await trainer.train_all_models()

    # Report to MIO
    await report_ml_training(
        mio_client=MIOManagerClient(),
        metrics=metrics
    )

    return {"status": "complete", "metrics": metrics}
```

---

## 📊 Summary: Complete Integration

### ✅ Workflows (Закреплены как должностные инструкции)

| Workflow | Schedule | Автоматизация | Status |
|----------|----------|---------------|--------|
| Daily Health Check | Every 24h | ✅ Auto | **Implemented** |
| Continuous Improvement | Every 1h | ✅ Auto | **Implemented** |
| Incident Investigation | Event-driven | ✅ Auto | **Implemented** |
| BIA Analysis | Event + Daily | ⚠️ TODO | **Plan Ready** |
| Risk Assessment | Event + Weekly | ⚠️ TODO | **Plan Ready** |
| Incident Response | Real-time | ⚠️ TODO | **Plan Ready** |
| Compliance Audit | Event + Monthly | ⚠️ TODO | **Plan Ready** |
| Plan Generation | Event-driven | ⚠️ TODO | **Plan Ready** |
| Exercise Execution | Event-driven | ⚠️ TODO | **Plan Ready** |
| Governance Review | Quarterly | ⚠️ TODO | **Plan Ready** |
| Learning & Training | Weekly + Event | ⚠️ TODO | **Plan Ready** |
| Supply Chain | Weekly | ⚠️ TODO | **Plan Ready** |
| Platform Meta-Analysis | Daily | ⚠️ TODO | **Plan Ready** |

**Total:** 13 workflows (3 implemented, 10 planned)

---

### 🤖 ML Models (Легкие модели в помощь)

| Model | Algorithm | Size | Competency | Status |
|-------|-----------|------|------------|--------|
| Bottleneck Predictor | LightGBM | ~10MB | Middle+ | ⚠️ TODO |
| Anomaly Detector | Isolation Forest | ~15MB | Middle+ | ⚠️ TODO |
| Health Score Predictor | LSTM/Prophet | ~20MB | Senior+ | ⚠️ TODO |
| Recommendation Ranker | Gradient Boosting | ~15MB | Expert | ⚠️ TODO |

**Total:** 4 models (0 implemented, 4 planned)

---

### 🎯 Implementation Priority

#### **Phase 1: Workflows Foundation (Week 1-2)**
1. ✅ Fix ProcessAnalyticsClient (DONE!)
2. ⚠️ Add BIA Analysis Workflow
3. ⚠️ Add Risk Assessment Workflow
4. ⚠️ Add Incident Response Workflow

#### **Phase 2: ML Models Foundation (Week 3-4)**
1. ⚠️ Implement Bottleneck Predictor
2. ⚠️ Implement Anomaly Detector
3. ⚠️ Setup training pipeline
4. ⚠️ Integrate with AnalyticsCore

#### **Phase 3: Remaining Workflows (Week 5-6)**
1. ⚠️ Add Compliance Audit Workflow
2. ⚠️ Add Plan Generation Workflow
3. ⚠️ Add Exercise Workflow
4. ⚠️ Add Governance Review Workflow

#### **Phase 4: Advanced ML (Week 7-8)**
1. ⚠️ Implement Health Score Predictor
2. ⚠️ Implement Recommendation Ranker
3. ⚠️ Add automated retraining workflow

---

## ✅ Conclusion

**Ответ на вопрос:**

### 1. Закреплены ли бизнес-процессы в workflow как должностные инструкции?

**Частично:** ✅ 3 из 13 workflows уже реализованы и автоматизированы
**План:** ⚠️ Добавить оставшиеся 10 workflows (2-3 недели работы)

### 2. Есть ли легкие ML модели в помощь?

**Сейчас:** ❌ Нет, только rule-based логика
**План:** ⚠️ Добавить 4 легкие ML модели (2-3 недели работы)

### 3. Что нужно сделать?

**Immediate Next Steps:**
1. ✅ ProcessAnalyticsClient исправлен (DONE!)
2. ⚠️ Реализовать BIA + Risk + Incident workflows (Week 1-2)
3. ⚠️ Добавить Bottleneck Predictor + Anomaly Detector (Week 3-4)
4. ⚠️ Постепенно добавлять оставшиеся workflows

**Estimated Timeline:** 6-8 weeks для полной реализации всех workflows + ML моделей

---

**Status:** 🎯 **Стратегия готова! Начинаем реализацию?**

**KPI для успеха:**
- ✅ 13/13 workflows реализованы и автоматизированы
- ✅ 4/4 ML модели обучены и deployed
- ✅ Accuracy моделей > 80%
- ✅ Все workflows имеют должностные инструкции
- ✅ Полная интеграция с MIO Manager

---

**Generated:** 2025-10-08
**By:** Analytics Specialist AI - Architecture Team
