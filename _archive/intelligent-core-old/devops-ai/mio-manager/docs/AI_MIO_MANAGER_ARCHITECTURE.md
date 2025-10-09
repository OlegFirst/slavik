# 🧠 AI Monitoring & Observability (MIO) Manager - Architecture Specification

**Version:** 1.0.0
**Date:** 2025-10-03
**Status:** 🔥 READY FOR DISCUSSION
**Author:** Claude & MD

---

## 🎯 Executive Summary

**AI MIO Manager** - это **интеллектуальная система управления мониторингом и наблюдаемостью**, которая превращает **пассивный сбор метрик** в **проактивное AI-управление** платформой BCM.

### Ключевые Возможности:

1. 🔍 **Auto-Discovery** - Автоматическое обнаружение новых сервисов
2. 🧠 **AI Analysis** - Интеллектуальный анализ метрик в реальном времени
3. 🎯 **Predictive Alerts** - Предсказание проблем ДО их возникновения
4. 🔗 **AI Coordination** - Координация с Workflow Intelligence и AI Orchestration
5. 🛠️ **Self-Healing** - Автоматическое исправление проблем
6. 📊 **Coverage Management** - Полный контроль покрытия системы мониторингом

### Отличие от Традиционного Мониторинга:

| Традиционный Подход | AI MIO Manager |
|---------------------|----------------|
| ❌ Вручную добавлять сервисы в Prometheus | ✅ Auto-discovery новых сервисов |
| ❌ Реагировать на проблемы ПОСЛЕ падения | ✅ Предсказывать проблемы ЗАРАНЕЕ |
| ❌ Вручную анализировать метрики в Grafana | ✅ AI автоматически находит аномалии |
| ❌ Изолированный мониторинг | ✅ Координация с Workflow Intelligence |
| ❌ Статические правила алертов | ✅ Самообучающиеся динамические модели |

---

## 🏗️ Architectural Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                   AI MIO MANAGER (Port 8046)                         │
│           Intelligent Monitoring & Observability Orchestrator        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  1. SERVICE DISCOVERY AGENT                                 │    │
│  │  ────────────────────────────────────────────────────────  │    │
│  │  🔍 Auto-Discovery:                                        │    │
│  │  - Сканирует Docker/K8s для новых сервисов                │    │
│  │  - Проверяет /health, /metrics endpoints                   │    │
│  │  - Валидирует Prometheus config                            │    │
│  │  - Auto-генерация scrape configs                           │    │
│  │                                                             │    │
│  │  📊 Coverage Manager:                                       │    │
│  │  - Tracking: 12/12 services monitored                      │    │
│  │  - Гарантирует 100% coverage                               │    │
│  │  - Алерты при добавлении неотслеживаемых сервисов          │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  2. METRICS INTELLIGENCE ENGINE                             │    │
│  │  ────────────────────────────────────────────────────────  │    │
│  │  🧠 AI-Powered Analysis:                                   │    │
│  │  - Real-time metric analysis (PromQL → AI models)          │    │
│  │  - Anomaly detection (Isolation Forest, LSTM)              │    │
│  │  - Pattern recognition (Time Series analysis)              │    │
│  │  - Correlation discovery (Pearson, Spearman)               │    │
│  │  - Root cause analysis (Causality graphs)                  │    │
│  │                                                             │    │
│  │  🔮 Predictive Analytics:                                  │    │
│  │  - Forecasting (Prophet, ARIMA)                            │    │
│  │  - Trend detection (Mann-Kendall test)                     │    │
│  │  - Capacity planning (Resource exhaustion predictions)     │    │
│  │  - Failure prediction (ML classification models)           │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  3. WORKFLOW INTELLIGENCE INTEGRATION HUB                   │    │
│  │  ────────────────────────────────────────────────────────  │    │
│  │  🔗 Bi-directional Integration:                            │    │
│  │  MIO → Workflow Intelligence:                               │    │
│  │    - Метрики производительности workflows                  │    │
│  │    - Проблемные workflow patterns                          │    │
│  │    - Resource utilization по модулям                       │    │
│  │                                                             │    │
│  │  Workflow Intelligence → MIO:                               │    │
│  │    - Workflow execution context (какой workflow выполняется)│    │
│  │    - Case similarity analysis (похожие проблемы в прошлом) │    │
│  │    - Benchmark comparisons (норма vs текущее)              │    │
│  │    - AI recommendations (что делать)                        │    │
│  │                                                             │    │
│  │  📈 Combined Intelligence:                                  │    │
│  │    MIO обнаруживает: "governance-service latency spike"     │    │
│  │    → запрашивает Workflow Intelligence                      │    │
│  │    → получает: "Policy creation workflow anomaly detected"  │    │
│  │    → Root cause: массовое создание политик за 1 минуту     │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  4. AI RECOMMENDATION ENGINE                                │    │
│  │  ────────────────────────────────────────────────────────  │    │
│  │  💡 LLM-Powered Recommendations:                           │    │
│  │  - GPT-4 analysis of complex issues                        │    │
│  │  - RAG (Retrieval-Augmented Generation)                    │    │
│  │  - Best practices knowledge base                           │    │
│  │  - Context-aware solutions                                 │    │
│  │                                                             │    │
│  │  🎯 Recommendation Output:                                 │    │
│  │  - Problem description (что случилось)                     │    │
│  │  - Root cause (почему)                                     │    │
│  │  - Impact analysis (кого затронет)                         │    │
│  │  - Action plan (что делать)                                │    │
│  │  - Priority (CRITICAL/HIGH/MEDIUM/LOW)                     │    │
│  │  - Estimated time to resolution                            │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  5. AI ORCHESTRATION COORDINATOR                            │    │
│  │  ────────────────────────────────────────────────────────  │    │
│  │  🎭 Multi-AI System Coordination:                          │    │
│  │  - MIO Manager (monitoring intelligence)                   │    │
│  │  - Workflow Intelligence (process intelligence)            │    │
│  │  - AI Orchestration (action execution)                     │    │
│  │                                                             │    │
│  │  Coordination Flow:                                         │    │
│  │  1. MIO обнаруживает проблему                              │    │
│  │  2. Workflow Intelligence анализирует контекст              │    │
│  │  3. Recommendation Engine вырабатывает решение             │    │
│  │  4. AI Orchestration выполняет действия                    │    │
│  │  5. MIO верифицирует результат                             │    │
│  │                                                             │    │
│  │  📡 EventBus Integration:                                   │    │
│  │  - Публикует: monitoring.anomaly.detected                  │    │
│  │  - Публикует: monitoring.prediction.warning                │    │
│  │  - Подписан: *.workflow.failed, *.error, *.degraded        │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  6. SELF-HEALING ORCHESTRATOR                               │    │
│  │  ────────────────────────────────────────────────────────  │    │
│  │  🛠️ Automated Remediation:                                 │    │
│  │  - Service restart (при memory leaks, deadlocks)           │    │
│  │  - Auto-scaling (при high load)                            │    │
│  │  - Circuit breaker activation (при cascading failures)     │    │
│  │  - Rate limiting (при traffic spikes)                      │    │
│  │  - Rollback deployment (при errors после deploy)           │    │
│  │                                                             │    │
│  │  🔒 Safety Mechanisms:                                      │    │
│  │  - Dry-run mode (симуляция действий)                      │    │
│  │  - Approval workflows (для critical actions)               │    │
│  │  - Blast radius analysis (оценка влияния)                 │    │
│  │  - Rollback capability (откат изменений)                   │    │
│  │  - Audit trail (лог всех действий)                         │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  7. LEARNING & ADAPTATION ENGINE                            │    │
│  │  ────────────────────────────────────────────────────────  │    │
│  │  🎓 Continuous Learning:                                   │    │
│  │  - Запоминает успешные решения                             │    │
│  │  - Обучается на исторических данных                        │    │
│  │  - Улучшает модели предсказаний                            │    │
│  │  - Адаптирует пороги алертов                               │    │
│  │                                                             │    │
│  │  📚 Knowledge Base:                                         │    │
│  │  - Incident history (проблемы + решения)                   │    │
│  │  - Pattern library (известные аномалии)                    │    │
│  │  - Best practices (рекомендации)                           │    │
│  │  - Service profiles (нормальное поведение)                 │    │
│  └────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴────────────────┐
                │                              │
                ▼                              ▼
┌───────────────────────────┐    ┌───────────────────────────┐
│   DATA SOURCES            │    │   ACTION TARGETS          │
├───────────────────────────┤    ├───────────────────────────┤
│ • Prometheus (metrics)    │    │ • AI Orchestration        │
│ • Loki (logs)             │    │ • Workflow Intelligence   │
│ • Tempo (traces)          │    │ • Kubernetes API          │
│ • EventBus (events)       │    │ • Docker API              │
│ • Service /health         │    │ • Service Registry        │
│ • Workflow Intelligence   │    │ • EventBus                │
│ • Service Registry        │    │ • Alertmanager            │
└───────────────────────────┘    └───────────────────────────┘
```

---

## 📋 Component Specifications

### 1. Service Discovery Agent

**Purpose:** Автоматическое обнаружение и регистрация сервисов в системе мониторинга

**Architecture:**

```python
# /intelligent-core/mio-manager/agents/service_discovery.py

class ServiceDiscoveryAgent:
    """
    Сканирует инфраструктуру для обнаружения сервисов
    """

    def __init__(self, prometheus_config_path: str, service_registry_url: str):
        self.prometheus_config = prometheus_config_path
        self.service_registry = service_registry_url
        self.discovered_services = {}

    async def scan_infrastructure(self):
        """
        Сканирует Docker/K8s/Service Registry для поиска сервисов
        """
        # 1. Docker API scan
        docker_services = await self._scan_docker()

        # 2. Kubernetes API scan (if available)
        k8s_services = await self._scan_kubernetes()

        # 3. Service Registry check
        registry_services = await self._scan_service_registry()

        # Merge discovered services
        all_services = self._merge_services(
            docker_services, k8s_services, registry_services
        )

        return all_services

    async def validate_service(self, service: Service):
        """
        Проверяет что сервис имеет необходимые endpoints
        """
        validations = {
            "health_endpoint": await self._check_health(service),
            "metrics_endpoint": await self._check_metrics(service),
            "prometheus_format": await self._validate_metrics_format(service),
            "port_available": await self._check_port(service.port),
        }

        service.validation_status = validations
        return validations

    async def auto_register_service(self, service: Service):
        """
        Автоматически добавляет сервис в Prometheus config
        """
        # 1. Generate Prometheus scrape config
        scrape_config = self._generate_prometheus_config(service)

        # 2. Update prometheus.yml
        await self._update_prometheus_config(scrape_config)

        # 3. Reload Prometheus (HTTP POST /-/reload)
        await self._reload_prometheus()

        # 4. Publish event
        await self.eventbus.publish({
            "type": "monitoring.service.registered",
            "service": service.name,
            "port": service.port,
            "metrics_path": service.metrics_path
        })

        logger.info(f"✅ Auto-registered service: {service.name}:{service.port}")

    def _generate_prometheus_config(self, service: Service) -> dict:
        """
        Генерирует Prometheus scrape config на основе метаданных сервиса
        """
        return {
            "job_name": service.name,
            "scrape_interval": "10s",
            "scrape_timeout": "5s",
            "metrics_path": service.metrics_path or "/metrics",
            "static_configs": [{
                "targets": [f"{service.host}:{service.port}"],
                "labels": {
                    "service": service.name,
                    "iso_clause": service.iso_clause if hasattr(service, 'iso_clause') else "unknown",
                    "component": service.component or "bcm"
                }
            }],
            "relabel_configs": [{
                "source_labels": ["__address__"],
                "target_label": "instance",
                "replacement": service.name
            }]
        }
```

**Key Features:**
- Periodic scanning (every 5 minutes)
- Deduplication (avoid re-registering existing services)
- Validation before registration
- Automatic Prometheus reload
- EventBus notifications

**Data Flow:**
```
Infrastructure → Discovery Agent → Validation → Auto-Registration → Prometheus Updated
```

---

### 2. Metrics Intelligence Engine

**Purpose:** AI-анализ метрик для обнаружения аномалий, трендов и предсказаний

**Architecture:**

```python
# /intelligent-core/mio-manager/intelligence/metrics_analyzer.py

class MetricsIntelligenceEngine:
    """
    AI-powered анализ метрик из Prometheus
    """

    def __init__(self, prometheus_url: str, model_registry_path: str):
        self.prometheus = PrometheusClient(prometheus_url)
        self.models = self._load_ml_models(model_registry_path)
        self.anomaly_detector = IsolationForest()
        self.time_series_model = Prophet()  # Facebook Prophet

    async def analyze_real_time(self, service: str, metric: str):
        """
        Real-time анализ метрики
        """
        # 1. Fetch metric from Prometheus (last 1 hour)
        query = f'{metric}{{service="{service}"}}'
        data = await self.prometheus.query_range(
            query=query,
            start="-1h",
            step="15s"
        )

        # 2. Anomaly detection
        anomalies = await self._detect_anomalies(data)

        # 3. Trend analysis
        trend = await self._analyze_trend(data)

        # 4. Correlation check (with other metrics)
        correlations = await self._find_correlations(service, metric, data)

        return {
            "anomalies": anomalies,
            "trend": trend,
            "correlations": correlations,
            "timestamp": datetime.utcnow()
        }

    async def _detect_anomalies(self, data: TimeSeriesData):
        """
        Isolation Forest для обнаружения аномалий
        """
        # Extract values
        values = np.array([point.value for point in data.points])

        # Reshape for sklearn
        X = values.reshape(-1, 1)

        # Predict (-1 = anomaly, 1 = normal)
        predictions = self.anomaly_detector.fit_predict(X)

        # Find anomaly points
        anomaly_indices = np.where(predictions == -1)[0]
        anomalies = [
            {
                "timestamp": data.points[i].timestamp,
                "value": data.points[i].value,
                "severity": self._calculate_severity(data.points[i].value, values)
            }
            for i in anomaly_indices
        ]

        return anomalies

    async def predict_future(self, service: str, metric: str, horizon: str = "1d"):
        """
        Предсказание значений метрики на будущее
        """
        # 1. Fetch historical data (last 30 days)
        query = f'{metric}{{service="{service}"}}'
        historical = await self.prometheus.query_range(
            query=query,
            start="-30d",
            step="5m"
        )

        # 2. Prepare data for Prophet
        df = pd.DataFrame({
            'ds': [p.timestamp for p in historical.points],
            'y': [p.value for p in historical.points]
        })

        # 3. Fit model
        model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            changepoint_prior_scale=0.05
        )
        model.fit(df)

        # 4. Make future predictions
        future_periods = self._parse_horizon(horizon)  # "1d" → 288 periods (5min intervals)
        future = model.make_future_dataframe(periods=future_periods, freq='5min')
        forecast = model.predict(future)

        # 5. Extract predictions
        predictions = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(future_periods)

        return {
            "predictions": predictions.to_dict('records'),
            "trend": "increasing" if predictions['yhat'].iloc[-1] > predictions['yhat'].iloc[0] else "decreasing",
            "confidence_interval": (predictions['yhat_lower'].mean(), predictions['yhat_upper'].mean())
        }

    async def root_cause_analysis(self, anomaly: Anomaly):
        """
        Поиск root cause аномалии через корреляции
        """
        # 1. Build causality graph
        service = anomaly.service
        timestamp = anomaly.timestamp

        # 2. Fetch all metrics for service at that time
        all_metrics = await self._fetch_all_service_metrics(service, timestamp)

        # 3. Calculate correlations
        correlations = []
        for metric_name, metric_data in all_metrics.items():
            correlation = self._calculate_correlation(
                anomaly.metric_data,
                metric_data
            )
            if abs(correlation) > 0.7:  # Strong correlation
                correlations.append({
                    "metric": metric_name,
                    "correlation": correlation,
                    "lag": self._calculate_lag(anomaly.metric_data, metric_data)
                })

        # 4. Sort by correlation strength
        correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)

        # 5. Find leading indicators (metrics that changed BEFORE anomaly)
        root_causes = [
            c for c in correlations
            if c['lag'] < 0  # Changed before anomaly
        ]

        return {
            "primary_cause": root_causes[0] if root_causes else None,
            "contributing_factors": root_causes[1:3] if len(root_causes) > 1 else [],
            "correlation_graph": correlations
        }
```

**ML Models Used:**
1. **Isolation Forest** - Anomaly detection
2. **Prophet** - Time series forecasting
3. **ARIMA** - Seasonal decomposition
4. **LSTM** - Deep learning for complex patterns
5. **Pearson/Spearman** - Correlation analysis

**Output Example:**
```json
{
  "anomaly_detected": true,
  "service": "learning-service",
  "metric": "http_request_duration_seconds",
  "current_value": 5.2,
  "expected_range": [0.1, 0.5],
  "severity": "HIGH",
  "root_cause": {
    "primary_metric": "database_connections_active",
    "correlation": 0.92,
    "lag": -30,  // Changed 30 seconds before latency spike
    "explanation": "Database connection pool exhaustion led to increased latency"
  },
  "prediction": {
    "next_1h": [5.5, 6.0, 6.8],  // Will get worse
    "trend": "increasing",
    "recommendation": "Immediate action required"
  }
}
```

---

### 3. Workflow Intelligence Integration Hub

**Purpose:** Би-директиональная интеграция с Workflow Intelligence для контекстного анализа

**Architecture:**

```python
# /intelligent-core/mio-manager/integrations/workflow_intelligence_hub.py

class WorkflowIntelligenceHub:
    """
    Координирует MIO Manager с Workflow Intelligence
    """

    def __init__(self, workflow_intelligence_url: str):
        self.workflow_api = WorkflowIntelligenceClient(workflow_intelligence_url)
        self.context_cache = {}

    async def enrich_anomaly_with_workflow_context(self, anomaly: Anomaly):
        """
        Обогащает аномалию контекстом из Workflow Intelligence
        """
        service = anomaly.service
        timestamp = anomaly.timestamp

        # 1. Get active workflows at time of anomaly
        active_workflows = await self.workflow_api.get_active_workflows(
            service=service,
            timestamp=timestamp,
            window="5m"  # 5 minutes before/after
        )

        # 2. Get workflow performance metrics
        workflow_metrics = []
        for workflow in active_workflows:
            metrics = await self.workflow_api.get_workflow_metrics(
                workflow_id=workflow.id,
                module=workflow.module
            )
            workflow_metrics.append(metrics)

        # 3. Search for similar cases in Case Library
        similar_cases = await self.workflow_api.search_similar_cases(
            query={
                "service": service,
                "anomaly_type": anomaly.type,
                "metric": anomaly.metric
            },
            limit=5
        )

        # 4. Get benchmark statistics
        benchmarks = await self.workflow_api.get_benchmarks(
            module=service.split('-')[0],  # "learning-service" → "learning"
            industry="bcm",
            metric=anomaly.metric
        )

        # 5. Combine all context
        return {
            "anomaly": anomaly,
            "workflow_context": {
                "active_workflows": active_workflows,
                "workflow_metrics": workflow_metrics,
                "abnormal_patterns": self._detect_workflow_anomalies(workflow_metrics, benchmarks)
            },
            "historical_context": {
                "similar_cases": similar_cases,
                "success_rate": self._calculate_success_rate(similar_cases),
                "avg_resolution_time": self._calculate_avg_resolution(similar_cases)
            },
            "benchmark_context": {
                "industry_benchmark": benchmarks,
                "deviation": self._calculate_deviation(workflow_metrics, benchmarks)
            }
        }

    async def get_ai_recommendation_from_workflow(self, enriched_anomaly):
        """
        Запрашивает AI recommendation от Workflow Intelligence ContextAdvisor
        """
        # Use Workflow Intelligence's ContextAdvisor
        recommendation = await self.workflow_api.get_ai_advice(
            context={
                "current_state": enriched_anomaly["anomaly"].current_state,
                "workflow_metrics": enriched_anomaly["workflow_context"]["workflow_metrics"],
                "similar_cases": enriched_anomaly["historical_context"]["similar_cases"]
            }
        )

        return recommendation

    async def report_resolution_to_workflow(self, anomaly, resolution):
        """
        Отправляет успешное решение в Workflow Intelligence Case Library
        """
        # Create case for future learning
        case = {
            "module": anomaly.service.split('-')[0],
            "workflow_type": anomaly.workflow_type if hasattr(anomaly, 'workflow_type') else "general",
            "context": {
                "anomaly_type": anomaly.type,
                "metric": anomaly.metric,
                "service": anomaly.service,
                "timestamp": anomaly.timestamp
            },
            "metrics": {
                "resolution_time": resolution.duration,
                "success": resolution.success,
                "automated": resolution.automated
            },
            "outcome": "resolved",
            "metadata": {
                "root_cause": resolution.root_cause,
                "action_taken": resolution.action,
                "blast_radius": resolution.affected_services
            }
        }

        await self.workflow_api.submit_case(case)
        logger.info(f"✅ Submitted resolution case to Workflow Intelligence: {anomaly.id}")
```

**Integration Flow:**

```
┌──────────────────┐
│  MIO Manager     │
│  Detects Anomaly │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────┐
│ Workflow Intelligence Hub     │
│ ──────────────────────────   │
│ 1. Get active workflows       │
│ 2. Search similar cases       │
│ 3. Get benchmarks             │
│ 4. Request AI recommendation  │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Workflow Intelligence         │
│ (ContextAdvisor)              │
│ ──────────────────────────   │
│ - Analyzes context            │
│ - Retrieves similar cases     │
│ - Generates recommendation    │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────┐
│ MIO Manager      │
│ Executes Action  │
└──────────────────┘
```

---

### 4. AI Recommendation Engine

**Purpose:** LLM-powered генерация рекомендаций по устранению проблем

**Architecture:**

```python
# /intelligent-core/mio-manager/intelligence/recommendation_engine.py

class AIRecommendationEngine:
    """
    Генерирует рекомендации используя GPT-4 + RAG
    """

    def __init__(self, openai_api_key: str, knowledge_base_path: str):
        self.llm = OpenAI(api_key=openai_api_key, model="gpt-4-turbo")
        self.vectorstore = ChromaDB(persist_directory=knowledge_base_path)
        self.embeddings = OpenAIEmbeddings()

    async def generate_recommendation(self, enriched_anomaly):
        """
        Генерирует comprehensive recommendation
        """
        # 1. Retrieve relevant best practices from knowledge base (RAG)
        relevant_docs = await self._retrieve_knowledge(enriched_anomaly)

        # 2. Build context for LLM
        context = self._build_llm_context(enriched_anomaly, relevant_docs)

        # 3. Generate recommendation via GPT-4
        prompt = f"""
        You are an expert BCM platform operations engineer analyzing a monitoring anomaly.

        ANOMALY DETAILS:
        Service: {enriched_anomaly['anomaly'].service}
        Metric: {enriched_anomaly['anomaly'].metric}
        Current Value: {enriched_anomaly['anomaly'].current_value}
        Expected Range: {enriched_anomaly['anomaly'].expected_range}
        Severity: {enriched_anomaly['anomaly'].severity}

        ROOT CAUSE ANALYSIS:
        {json.dumps(enriched_anomaly['anomaly'].root_cause, indent=2)}

        WORKFLOW CONTEXT:
        {json.dumps(enriched_anomaly['workflow_context'], indent=2)}

        HISTORICAL SIMILAR CASES:
        {json.dumps(enriched_anomaly['historical_context']['similar_cases'], indent=2)}

        RELEVANT BEST PRACTICES:
        {relevant_docs}

        TASK:
        1. Analyze the root cause and contributing factors
        2. Assess the blast radius (which services/users are affected)
        3. Provide step-by-step resolution plan
        4. Estimate time to resolution
        5. Suggest preventive measures

        Respond in JSON format:
        {{
            "problem_summary": "Brief description",
            "root_cause": "Detailed root cause explanation",
            "blast_radius": {{
                "affected_services": [...],
                "affected_users": "estimated count",
                "business_impact": "HIGH/MEDIUM/LOW"
            }},
            "resolution_plan": {{
                "immediate_actions": [
                    {{"step": 1, "action": "...", "estimated_time": "..."}},
                    ...
                ],
                "short_term_fixes": [...],
                "long_term_solutions": [...]
            }},
            "estimated_total_resolution_time": "30 minutes",
            "priority": "CRITICAL/HIGH/MEDIUM/LOW",
            "automated_remediation_available": true/false,
            "preventive_measures": [...]
        }}
        """

        response = await self.llm.generate(prompt)
        recommendation = json.loads(response.content)

        # 4. Validate and enrich recommendation
        recommendation = await self._validate_recommendation(recommendation)
        recommendation["generated_at"] = datetime.utcnow()
        recommendation["confidence_score"] = await self._calculate_confidence(recommendation, enriched_anomaly)

        return recommendation

    async def _retrieve_knowledge(self, enriched_anomaly):
        """
        RAG: Retrieval-Augmented Generation from knowledge base
        """
        # Build search query
        query = f"""
        {enriched_anomaly['anomaly'].type} in {enriched_anomaly['anomaly'].service}
        {enriched_anomaly['anomaly'].metric} anomaly resolution
        """

        # Embed query
        query_embedding = await self.embeddings.embed_query(query)

        # Search vector database
        similar_docs = self.vectorstore.similarity_search(
            query_embedding,
            k=5  # Top 5 relevant documents
        )

        return similar_docs

    async def _calculate_confidence(self, recommendation, enriched_anomaly):
        """
        Рассчитывает confidence score рекомендации
        """
        factors = {
            "similar_cases_found": len(enriched_anomaly['historical_context']['similar_cases']) > 0,
            "root_cause_identified": enriched_anomaly['anomaly'].root_cause is not None,
            "workflow_context_available": len(enriched_anomaly['workflow_context']['active_workflows']) > 0,
            "benchmark_deviation": enriched_anomaly['benchmark_context']['deviation'] < 0.5,
            "automated_remediation": recommendation['automated_remediation_available']
        }

        # Weighted score
        weights = {
            "similar_cases_found": 0.3,
            "root_cause_identified": 0.3,
            "workflow_context_available": 0.2,
            "benchmark_deviation": 0.1,
            "automated_remediation": 0.1
        }

        score = sum(
            weights[factor] if factors[factor] else 0
            for factor in factors
        )

        return score
```

**Example Recommendation Output:**

```json
{
  "problem_summary": "Learning Service experiencing high latency (5.2s vs expected 0.1-0.5s) due to database connection pool exhaustion",
  "root_cause": "Sudden spike in policy creation workflows (50 requests in 1 minute vs normal 5/min) caused database connection pool to exhaust. Learning Service shares connection pool with Governance Service, leading to cascading latency.",
  "blast_radius": {
    "affected_services": ["learning-service", "governance-service", "community-portal"],
    "affected_users": "~150 active users",
    "business_impact": "HIGH - Training enrollments and policy management blocked"
  },
  "resolution_plan": {
    "immediate_actions": [
      {
        "step": 1,
        "action": "Enable rate limiting on Governance API (max 10 req/min per user)",
        "estimated_time": "30 seconds",
        "automated": true
      },
      {
        "step": 2,
        "action": "Restart Learning Service to release stuck connections",
        "estimated_time": "1 minute",
        "automated": true
      }
    ],
    "short_term_fixes": [
      {
        "step": 3,
        "action": "Increase connection pool size from 20 to 50",
        "estimated_time": "5 minutes",
        "automated": false,
        "requires_approval": true
      }
    ],
    "long_term_solutions": [
      {
        "action": "Separate connection pools for Learning and Governance services",
        "estimated_time": "1 day",
        "priority": "HIGH"
      },
      {
        "action": "Implement connection pool monitoring and auto-scaling",
        "estimated_time": "2 days",
        "priority": "MEDIUM"
      }
    ]
  },
  "estimated_total_resolution_time": "15 minutes",
  "priority": "HIGH",
  "automated_remediation_available": true,
  "confidence_score": 0.85,
  "preventive_measures": [
    "Add connection pool usage metrics to dashboard",
    "Set alert threshold at 80% pool utilization",
    "Review API rate limits across all services",
    "Implement circuit breaker for Governance API"
  ],
  "generated_at": "2025-10-03T12:30:45Z"
}
```

---

### 5. Self-Healing Orchestrator

**Purpose:** Автоматическое исправление проблем на основе рекомендаций

**Architecture:**

```python
# /intelligent-core/mio-manager/automation/self_healing.py

class SelfHealingOrchestrator:
    """
    Автоматическое устранение проблем
    """

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.action_history = []
        self.approval_workflows = ApprovalWorkflowManager()

    async def execute_remediation(self, recommendation: dict):
        """
        Выполняет plan по устранению проблемы
        """
        # 1. Check if automated remediation is safe
        safety_check = await self._safety_check(recommendation)
        if not safety_check["safe"]:
            logger.warning(f"⚠️ Automated remediation blocked: {safety_check['reason']}")
            await self._request_manual_approval(recommendation)
            return

        # 2. Execute immediate actions
        immediate_results = []
        for action in recommendation['resolution_plan']['immediate_actions']:
            if action.get('automated', False):
                result = await self._execute_action(action)
                immediate_results.append(result)

        # 3. Verify remediation success
        verification = await self._verify_remediation(recommendation)

        if verification["success"]:
            logger.info(f"✅ Self-healing successful: {recommendation['problem_summary']}")

            # Report to Workflow Intelligence
            await self._report_success(recommendation, immediate_results)
        else:
            logger.error(f"❌ Self-healing failed: {verification['error']}")
            await self._escalate_to_human(recommendation, verification)

        return {
            "success": verification["success"],
            "actions_taken": immediate_results,
            "verification": verification
        }

    async def _execute_action(self, action: dict):
        """
        Выполняет конкретное действие
        """
        action_type = action.get('action_type', self._infer_action_type(action['action']))

        if self.dry_run:
            logger.info(f"[DRY-RUN] Would execute: {action['action']}")
            return {"status": "dry_run", "action": action}

        # Route to appropriate executor
        if action_type == "restart_service":
            return await self._restart_service(action)
        elif action_type == "scale_service":
            return await self._scale_service(action)
        elif action_type == "enable_rate_limit":
            return await self._enable_rate_limit(action)
        elif action_type == "circuit_breaker":
            return await self._activate_circuit_breaker(action)
        elif action_type == "rollback_deployment":
            return await self._rollback_deployment(action)
        else:
            logger.error(f"Unknown action type: {action_type}")
            return {"status": "error", "error": f"Unknown action type: {action_type}"}

    async def _restart_service(self, action: dict):
        """
        Перезапускает сервис через Docker/K8s API
        """
        service_name = action.get('service')

        # 1. Check if service is managed by Docker
        if await self._is_docker_service(service_name):
            # Restart via Docker API
            await docker_client.containers.get(service_name).restart()
            logger.info(f"🔄 Restarted Docker container: {service_name}")

        # 2. Check if service is in Kubernetes
        elif await self._is_k8s_service(service_name):
            # Restart via K8s API (delete pod, let deployment recreate)
            await k8s_client.delete_pod(service_name)
            logger.info(f"🔄 Restarted K8s pod: {service_name}")

        return {
            "status": "success",
            "action": "restart_service",
            "service": service_name,
            "timestamp": datetime.utcnow()
        }

    async def _safety_check(self, recommendation: dict):
        """
        Проверяет безопасность автоматического устранения
        """
        checks = {
            "blast_radius": recommendation['blast_radius']['business_impact'] != "CRITICAL",
            "confidence": recommendation['confidence_score'] > 0.7,
            "automated_available": recommendation['automated_remediation_available'],
            "not_production_hours": not await self._is_peak_hours(),
            "no_recent_failures": await self._check_recent_action_failures() == 0
        }

        # All checks must pass
        safe = all(checks.values())

        return {
            "safe": safe,
            "checks": checks,
            "reason": self._explain_safety_check(checks) if not safe else None
        }
```

**Supported Actions:**

1. **Service Restart**
   - Docker container restart
   - Kubernetes pod restart
   - Graceful shutdown + restart

2. **Auto-Scaling**
   - Horizontal Pod Autoscaler (HPA) adjustment
   - Docker Swarm service scaling
   - Manual replica count increase

3. **Rate Limiting**
   - API Gateway rate limit rules
   - Service-level throttling
   - Per-user/per-IP limits

4. **Circuit Breaker**
   - Activate circuit breaker for failing dependencies
   - Fallback to degraded mode
   - Retry policies adjustment

5. **Rollback Deployment**
   - K8s rollout undo
   - Docker image tag revert
   - Configuration rollback

**Safety Mechanisms:**

- ✅ **Dry-run mode** - Simulate actions first
- ✅ **Blast radius analysis** - Don't auto-fix if impact is CRITICAL
- ✅ **Approval workflows** - Human approval for risky actions
- ✅ **Rollback capability** - Undo failed actions
- ✅ **Rate limiting** - Max 3 auto-remediations per hour
- ✅ **Audit trail** - Log all actions with timestamps

---

## 🔗 Integration Points

### Integration with Existing Systems:

```yaml
# Event Flow

EventBus Events (Consumed by MIO Manager):
  - "*.workflow.failed"          # Workflow failures
  - "*.error"                    # Error events from all services
  - "*.degraded"                 # Performance degradation
  - "service.deployed"           # New deployments
  - "database.connection.failed" # Infrastructure issues

EventBus Events (Published by MIO Manager):
  - "monitoring.anomaly.detected"       # Anomaly found
  - "monitoring.prediction.warning"     # Predictive alert
  - "monitoring.service.registered"     # New service added
  - "monitoring.remediation.started"    # Self-healing initiated
  - "monitoring.remediation.completed"  # Self-healing success/failure

Workflow Intelligence Integration:
  API Calls (MIO → Workflow Intelligence):
    - GET /api/workflows/active          # Get active workflows
    - GET /api/workflows/{id}/metrics    # Get workflow performance
    - POST /api/cases/search             # Find similar cases
    - GET /api/benchmarks                # Get industry benchmarks
    - POST /api/advice                   # Request AI recommendation
    - POST /api/cases                    # Submit resolved case

  API Calls (Workflow Intelligence → MIO):
    - GET /api/mio/services              # Get monitored services
    - GET /api/mio/metrics/{service}     # Get service metrics
    - GET /api/mio/anomalies             # Get recent anomalies

AI Orchestration Integration:
  - POST /api/orchestrate/action       # Execute coordinated action
  - GET /api/orchestrate/status        # Check action status

Prometheus Integration:
  - Query API: http://prometheus:9090/api/v1/query
  - Query Range: http://prometheus:9090/api/v1/query_range
  - Reload: POST http://prometheus:9090/-/reload

Grafana Integration:
  - Create dashboards via API
  - Update alert rules
  - Annotate anomalies on graphs
```

---

## 📊 Data Models

```python
# /intelligent-core/mio-manager/models.py

from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional

class Service(BaseModel):
    """Discovered service"""
    name: str
    host: str
    port: int
    health_endpoint: str = "/health"
    metrics_endpoint: str = "/metrics"
    iso_clause: Optional[str] = None
    component: str = "bcm"
    discovered_at: datetime
    validation_status: Dict[str, bool]

class Anomaly(BaseModel):
    """Detected anomaly"""
    id: str
    service: str
    metric: str
    current_value: float
    expected_range: tuple[float, float]
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    detected_at: datetime
    root_cause: Optional[Dict] = None
    workflow_context: Optional[Dict] = None

class Recommendation(BaseModel):
    """AI-generated recommendation"""
    problem_summary: str
    root_cause: str
    blast_radius: Dict
    resolution_plan: Dict
    estimated_resolution_time: str
    priority: str
    confidence_score: float
    automated_remediation_available: bool
    preventive_measures: List[str]
    generated_at: datetime

class RemediationAction(BaseModel):
    """Action taken for remediation"""
    action_id: str
    anomaly_id: str
    action_type: str  # restart, scale, rollback, etc
    action_details: Dict
    executed_at: datetime
    success: bool
    result: Dict
```

---

## 🚀 Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- ✅ Set up MIO Manager service structure
- ✅ Service Discovery Agent (basic Docker scan)
- ✅ Coverage Manager dashboard
- ✅ Prometheus config auto-generation
- ✅ EventBus integration

### Phase 2: Intelligence (Week 3-4)
- 🧠 Metrics Intelligence Engine
- 🧠 Anomaly detection (Isolation Forest)
- 🧠 Basic time series forecasting
- 🧠 Correlation analysis

### Phase 3: AI Integration (Week 5-6)
- 🤖 Workflow Intelligence Hub
- 🤖 AI Recommendation Engine (GPT-4 + RAG)
- 🤖 Knowledge base setup
- 🤖 LLM prompt engineering

### Phase 4: Automation (Week 7-8)
- 🛠️ Self-Healing Orchestrator (dry-run mode)
- 🛠️ Action executors (restart, scale)
- 🛠️ Safety mechanisms
- 🛠️ Approval workflows

### Phase 5: Production (Week 9-10)
- 📈 Advanced ML models (LSTM, Prophet)
- 📈 Learning & Adaptation Engine
- 📈 Production deployment
- 📈 Monitoring of the monitor (meta-monitoring!)

---

## 💡 Discussion Points

**Questions for Review:**

1. **Scope**: Все 7 компонентов нужны или начать с подмножества?
2. **ML Models**: Какие модели наиболее критичны? (Isolation Forest, Prophet, LSTM?)
3. **LLM**: Использовать GPT-4 API или локальную LLM (Llama, Mistral)?
4. **Safety**: Dry-run режим по умолчанию? Когда разрешить полную автоматизацию?
5. **Integration Priority**: С чего начать - Workflow Intelligence или Self-Healing?
6. **Data Retention**: Сколько хранить аномалии, рекомендации, действия?

**Key Decisions Needed:**

- [ ] Port allocation (предлагаю 8046 для MIO Manager)
- [ ] Database (PostgreSQL для истории аномалий?)
- [ ] Message queue (Redis Streams для event processing?)
- [ ] ML model hosting (локально или cloud?)
- [ ] LLM provider (OpenAI vs self-hosted?)

---

## ✅ Success Metrics

После внедрения AI MIO Manager мы должны увидеть:

1. **Coverage**: 100% сервисов в мониторинге (12/12)
2. **MTTR**: Mean Time To Resolution < 15 minutes (сейчас ~2 hours)
3. **Prediction Accuracy**: >80% проблем предсказаны до падения
4. **Auto-Remediation Rate**: >60% проблем решены автоматически
5. **False Positive Rate**: <5% ложных алертов
6. **Context Enrichment**: 100% аномалий обогащены Workflow Intelligence context

---

**Готов к обсуждению!** 🚀

Что думаешь об этой архитектуре? Какие компоненты наиболее приоритетны для первой реализации?
