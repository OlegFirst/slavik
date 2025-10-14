# РЕАЛЬНАЯ АРХИТЕКТУРА ПЛАТФОРМЫ - Полная Интеграционная Карта

**Дата создания**: 2025-10-12
**Версия**: 1.0.0
**Статус**: ✅ Полный анализ всех 3 директорий

---

## 🎯 КРИТИЧЕСКАЯ НАХОДКА

Я моделировал сценарии **НЕПОЛНО** потому что не видел полную картину платформы!

### Что я упустил:

1. **AI Office Infrastructure** (`/infrastructure/AI-office-infrastructure/`) - 8 агентов
2. **Platform Services** (`/platform-services/`) - 18 бизнес-сервисов
3. **Infrastructure Runtime** (`/infrastructure/runtime/`) - EventBus, Service Discovery, WebSocket
4. **Observability Stack** (`/infrastructure/observability/`) - MiO Manager, Prometheus, Grafana
5. **Governance System** (`/intelligent-core/workflow_intelligence/governance/`) - Goals + Rules Engine

---

## 📊 ПОЛНАЯ АРХИТЕКТУРА ПЛАТФОРМЫ

### Layer 0: Infrastructure Foundation

```
/infrastructure/
├── database/                        # Хранилище данных
│   ├── postgresql/                  # PostgreSQL + миграции (026 файлов)
│   ├── redis/                       # Кэширование + сессии
│   └── vector-db/                   # Qdrant (RAG)
│
├── runtime/                         # Runtime сервисы
│   ├── eventbus/                    # 🔥 EventBus (Redis) - главная шина событий
│   ├── message-queue/               # RabbitMQ очереди
│   ├── realtime-websocket/          # WebSocket real-time связь
│   └── service-discovery/           # 🔥 Consul (Port 8500) - service registry
│
├── observability/                   # Мониторинг
│   ├── monitoring-backend/          # MiO Manager (Port 8095)
│   ├── prometheus/                  # 🔥 Prometheus (Port 9090) - metrics collection
│   ├── grafana/                     # 🔥 Grafana (Port 3000) - 18 dashboards
│   ├── notification-service/        # Уведомления
│   └── logs/                        # Логирование
│
├── gateway/                         # 🔥 API Gateway (Port 8000)
│   └── api-gateway/                 # Auth, rate limiting, load balancing, circuit breaker
│
├── security/                        # Безопасность
│   ├── auth/                        # JWT аутентификация
│   ├── secrets-manager/             # Vault интеграция
│   └── secrets-management/          # Secret management
│
├── policy-engine/                   # Политики (Phase 1)
└── balancer-service/                # 🔥 Load balancing (round-robin, least-connections)
```

### Layer 1: AI Office Infrastructure (Agents)

```
/infrastructure/AI-office-infrastructure/
├── mio-manager/                     # 🔥 MiO Manager (Port 8095)
│   ├── monitoring/                  # Мониторинг компонентов
│   ├── intelligence/                # Анализ метрик
│   ├── reaction/                    # Реакции на события
│   ├── scheduler/                   # Scheduled jobs
│   └── integrations/                # EventBus, Temporal
│
├── orchestrator/                    # 🔥 AI Orchestrator (Port 8092)
│   # Управление AI агентами
│
├── agent-router/                    # Agent Router (Port 8093)
│   # Маршрутизация между агентами
│
├── analytics-specialist/            # Analytics Agent (Port 8094)
│   # Аналитика данных
│
├── project-agent/                   # Project Agent (Port 8096)
│   # Управление проектами
│
├── devops-agent/                    # DevOps Agent (Port 8097)
│   # DevOps операции
│
├── db-intelligence/                 # DB Intelligence (Port 8051)
│   # Оптимизация БД
│
└── ai-event-manager/                # AI Event Manager (Port 8098)
    # Управление событиями AI
```

### Layer 2: Intelligent Core (Brain)

```
/intelligent-core/
├── workflow_intelligence/           # 🧠 МОЗГ (Port 8037)
│   ├── governance/                  # 🔥 Goals + Rules Engine
│   │   ├── goals.yaml               # 16+ целей (User/System/Component/Platform)
│   │   ├── goals_engine.py          # Goals tracking
│   │   ├── rules_engine_v2.py       # 5-level rules hierarchy
│   │   └── governance_orchestrator.py  # Unified decision making
│   ├── core/                        # Workflow engine
│   ├── case_library/                # Case library (learning from history)
│   └── process_framework.py         # Business процессы (BIA, Risk)
│
├── orchestration/ai-orchestration/  # 🔥 AI Orchestration (Port 8030)
│   ├── decision_center/             # Priority engine, delegation
│   ├── memory/                      # 4-layer memory
│   ├── safety/                      # Safety monitors
│   └── evolution/                   # Self-evolution
│
├── scenario-intelligence/           # 🔥 Scenario Intelligence (Port 8090)
│   ├── engines/                     # 5 engines (Scenario, Call, Event, Chaos, Compliance)
│   ├── scenarios/                   # 4-level scenarios (Module/Subsystem/Inter-system/User)
│   ├── storage/                     # Registry (in-memory)
│   └── learning/                    # Scenario learner
│
├── ai-foundation/                   # 🔥 AI Foundation (Port 8040)
│   ├── rag/                         # RAG Pipeline (Qdrant)
│   ├── ml/                          # ML models
│   ├── llm/                         # LLM Router (Claude, GPT)
│   ├── learning/                    # Self-learning engine
│   └── utils/                       # ResourceTracker 🆕
│
├── predictive/                      # 🔥 Predictive (Port 8031)
│   ├── services/                    # Journey predictor, demand forecaster
│   ├── scheduler/                   # Daily digests (8:00 AM)
│   └── integrations/                # Event intelligence learning
│
├── expertise-center/                # 🔥 Expertise Center (Port 8035)
│   ├── domains/bcm/                 # BCM domain experts
│   │   └── tactical_assistants/    # BIA, Compliance, Risk assistants
│   ├── ai-office/                   # AI Office colleagues
│   └── ai_experts/                  # Strategic analyzers
│
├── workflow-engine/                 # 🔥 Workflow Engine (Port 8036)
│   ├── workflow/bpmn/               # BPMN 2.0 engine
│   ├── workflow/persistence/        # PostgreSQL persistence
│   └── workflow/api/                # FastAPI
│
├── ai_workflow_optimizer/           # 🔥 AI Optimizer (Port 8038)
│   # ML-powered workflow optimization
│
├── event_intelligence/              # Event Intelligence (Port 8039)
│   # Event pattern learning, auto-discovery
│
├── community_intelligence/          # Community Intelligence (Port 8030)
│   # Peer review, case curation
│
├── collective/                      # Collective Intelligence (Port 8032)
│   # Anonymous collaboration (K-anonymity)
│
├── coordination-center/             # 🔴 PLANNED Q1 2026 (NOT IMPLEMENTED)
│   # Multi-agent coordination (FUTURE)
│
└── shared/                          # Shared utilities
    ├── event_bus/                   # EventBus client
    └── database/                    # DB clients
```

### Layer 3: Platform Services (Business Logic)

```
/platform-services/
├── bia-service/                     # 🔥 BIA Service
│   ├── api/                         # REST API
│   ├── services/                    # Business logic
│   ├── repositories/                # Data access
│   └── workflow_integration.py      # Integration with workflow-engine
│
├── risk-service/                    # Risk Assessment
├── compliance-service/              # ISO 22301 compliance
├── plans_service/                   # BC Plans
├── planning_service/                # Planning
├── response-service/                # Incident response
├── learning-service/                # Training & awareness
├── governance-service/              # Governance
├── documents-service/               # Document generation
├── validation-service/              # Validation
├── community-service/               # Community
│   ├── marketplace/                 # Expert marketplace
│   └── portal/                      # Community portal
│
├── digital-twin/                    # Digital Twin
│   ├── collectors/                  # Data collection
│   ├── processors/                  # Data processing
│   └── bridges/                     # Integration bridges
│
├── living-docs/                     # Living documentation
├── simulation/                      # Simulation services
│   ├── scenarios/                   # Simulation scenarios
│   └── simulation-service/          # Simulation engine
│
├── business-monitoring/             # Business monitoring
│   ├── compliance-monitoring/       # Compliance tracking
│   └── process-analytics/           # Process analytics
│
└── AI-services-management/          # AI services management
```

---

## 🔄 РЕАЛЬНЫЙ ПОТОК СИСТЕМНОГО СЦЕНАРИЯ

### Сценарий: DB Overload Detection & Auto-Recovery

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 0: ENTRY POINT (External Request → API Gateway)           │
└─────────────────────────────────────────────────────────────────┘

0. External Request (User or System)
   ↓ HTTP POST /api/v1/bia/start
   ↓
   ↓ Request triggers DB load (BIA Service)

1. API Gateway (Port 8000)
   ↓ infrastructure/gateway/api-gateway/
   ↓
   ↓ 1. JWT Validation:
   ↓    → Calls Auth Service (Port 8001)
   ↓    → Validates token signature
   ↓    → Extracts user context (user_id, tenant_id, roles)
   ↓    ✅ Token valid
   ↓
   ↓ 2. Rate Limiting:
   ↓    → Checks Redis (token bucket algorithm)
   ↓    → Current: 150 requests/min (limit: 10,000/min)
   ↓    ✅ Within limits
   ↓
   ↓ 3. Service Discovery Lookup:
   ↓    → Queries Service Discovery (Port 8500)
   ↓    → GET /v1/catalog/service/bia-service
   ↓    → Response: {
   ↓         "ServiceName": "bia-service",
   ↓         "ServiceAddress": "10.0.1.20",
   ↓         "ServicePort": 8008,
   ↓         "ServiceMeta": {
   ↓           "version": "2.0.0",
   ↓           "health": "passing"
   ↓         }
   ↓       }
   ↓
   ↓ 4. Load Balancing:
   ↓    → Strategy: round-robin
   ↓    → Available instances: 3
   ↓    → Selected: 10.0.1.20:8008
   ↓
   ↓ 5. Circuit Breaker Check:
   ↓    → State: CLOSED (healthy)
   ↓    → Error rate: 0.5% (threshold: 50%)
   ↓    ✅ Pass through
   ↓
   ↓ 6. Route Request:
   ↓    → Forward to bia-service:8008
   ↓    → Add headers:
   ↓      X-Request-ID: req_xxx
   ↓      X-User-ID: user_123
   ↓      X-Tenant-ID: tenant_1
   ↓
   ↓ 7. Audit Log:
   ↓    → Log to PostgreSQL audit table
   ↓    → {
   ↓        "request_id": "req_xxx",
   ↓        "user_id": "user_123",
   ↓        "endpoint": "/api/v1/bia/start",
   ↓        "method": "POST",
   ↓        "timestamp": "2025-10-12T14:30:00Z",
   ↓        "source_ip": "192.168.1.100"
   ↓      }

2. BIA Service (Port 8008)
   ↓ Processes request
   ↓ Executes N+1 queries (БАГ!)
   ↓ SELECT * FROM processes WHERE id = ? (выполняется 100 раз!)
   ↓
   ↓ Это создает нагрузку на DB...

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: DETECTION (MiO Manager + Digital Twin)                 │
└─────────────────────────────────────────────────────────────────┘

3. Digital Twin / collectors/
   ↓ Собирает метрики из PostgreSQL каждые 10 секунд
   ↓ • Active connections: 95/100
   ↓ • Query latency: 5000ms (P95)
   ↓ • CPU: 85%
   ↓ • Memory: 90%

2. Digital Twin / processors/
   ↓ Обрабатывает метрики, вычисляет тренды
   ↓ Trend: +5 connections/minute
   ↓ Prediction: 100 connections in 1 minute

5. MiO Manager (Port 8095)
   ↓ intelligence/ анализирует метрики
   ↓ ALERT: "DB overload imminent"
   ↓ KPI Violation: query_latency > 2000ms (target: <2000ms)

6. EventBus (infrastructure/runtime/eventbus/)
   ↓ Публикует событие:
   ↓ Event: "monitoring.kpi.violation"
   ↓ {
   ↓   "component": "postgresql",
   ↓   "metric": "query_latency",
   ↓   "current": 5000,
   ↓   "target": 2000,
   ↓   "severity": "high"
   ↓ }

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: PREDICTION (Predictive Intelligence + AI Foundation)   │
└─────────────────────────────────────────────────────────────────┘

7. Predictive Service (Port 8031)
   ↓ Подписан на EventBus: "monitoring.kpi.violation"
   ↓ services/ai_foundation_integration.py
   ↓
   ↓ Calls AI Foundation (Port 8040):
   ↓ • ml/anomaly_detection.py → Обнаруживает аномалию
   ↓ • ml/predictive_models.py → Предсказывает через 15 мин 100% overload
   ↓
   ↓ Queries Case Library (workflow_intelligence/case_library/):
   ↓ • Находит 5 похожих случаев
   ↓ • Похожий паттерн: N+1 queries в BIA Service
   ↓ • Решение из Case #47: "Add JOIN to eliminate N+1"
   ↓ • Success rate: 85%

8. Predictive Service → EventBus
   ↓ Публикует:
   ↓ Event: "prediction.resource_exhaustion"
   ↓ {
   ↓   "component": "postgresql",
   ↓   "time_to_exhaustion_minutes": 15,
   ↓   "confidence": 0.85,
   ↓   "suggested_solution": "optimize_n_plus_one_queries",
   ↓   "historical_case_id": "case_047"
   ↓ }

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: GOVERNANCE (Workflow Intelligence - Goals + Rules)     │
└─────────────────────────────────────────────────────────────────┘

9. Workflow Intelligence (Port 8037)
   ↓ Подписан на EventBus: "prediction.resource_exhaustion"
   ↓
   ↓ governance/governance_orchestrator.py
   ↓ → validate_system_health(system_metrics)
   ↓
   ↓ governance/goals_engine.py:
   ↓ • Goal 2.3: "Maintain 99.9% Uptime" → AT RISK
   ↓ • Goal 2.2: "Zero Data Loss" → AT RISK
   ↓ • Goal 2.1: "PDCA Continuous Improvement" → ACTIVE
   ↓
   ↓ governance/rules_engine_v2.py:
   ↓ • Constitution Rule: "No data loss" (Priority: CRITICAL)
   ↓ • Compliance Rule: "ISO 22301 - 8.4 Response" (Priority: HIGH)
   ↓ • Organization Rule: "Performance SLA <2s" (Priority: MEDIUM)
   ↓
   ↓ Decision:
   ↓ {
   ↓   "decision_type": "allow_with_urgency",
   ↓   "rationale": "2 critical goals at risk, constitution rule applies",
   ↓   "priority": "critical",
   ↓   "actions_to_take": [
   ↓     "create_recovery_scenario",
   ↓     "escalate_to_devops",
   ↓     "enable_circuit_breaker"
   ↓   ]
   ↓ }

10. Workflow Intelligence → EventBus
   ↓ Публикует:
   ↓ Event: "governance.decision_made"
   ↓ {
   ↓   "decision_id": "dec_xxx",
   ↓   "decision_type": "allow_with_urgency",
   ↓   "priority": "critical",
   ↓   "scenario_to_execute": "db_overload_recovery"
   ↓ }

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: ORCHESTRATION (AI Orchestration + Decision Center)     │
└─────────────────────────────────────────────────────────────────┘

11. AI Orchestration (Port 8030)
   ↓ Подписан на EventBus: "governance.decision_made"
   ↓
   ↓ decision_center/priority_engine.py:
   ↓ • Анализирует priority: "critical"
   ↓ • Назначает приоритет: 100 (highest)
   ↓
   ↓ decision_center/delegation_manager.py:
   ↓ • Создает команды для агентов:
   ↓   1. DB Intelligence Agent → diagnose root cause
   ↓   2. DevOps Agent → prepare rollback plan
   ↓   3. Scenario Intelligence → execute recovery scenario
   ↓
   ↓ decision_center/strategy_selector.py:
   ↓ • Выбирает стратегию: "immediate_recovery + parallel_diagnostics"
   ↓
   ↓ memory/short_term_memory.py:
   ↓ • Сохраняет контекст в Redis (TTL: 1 hour)

12. AI Orchestration → Service Discovery + EventBus
    ↓
    ↓ Service Discovery (Port 8500):
    ↓ AI Orchestration запрашивает адреса агентов:
    ↓
    ↓ Query 1: GET /v1/catalog/service/db-intelligence
    ↓ Response: {
    ↓   "ServiceName": "db-intelligence",
    ↓   "ServiceAddress": "10.0.1.15",
    ↓   "ServicePort": 8051,
    ↓   "ServiceMeta": {
    ↓     "version": "1.0.0",
    ↓     "health": "passing",
    ↓     "last_check": "2025-10-12T14:30:45Z"
    ↓   }
    ↓ }
    ↓
    ↓ Query 2: GET /v1/catalog/service/devops-agent
    ↓ Response: {
    ↓   "ServiceName": "devops-agent",
    ↓   "ServiceAddress": "10.0.1.18",
    ↓   "ServicePort": 8097,
    ↓   "ServiceMeta": {
    ↓     "version": "1.0.0",
    ↓     "health": "passing"
    ↓   }
    ↓ }
    ↓
    ↓ Query 3: GET /v1/catalog/service/scenario-intelligence
    ↓ Response: {
    ↓   "ServiceName": "scenario-intelligence",
    ↓   "ServiceAddress": "10.0.1.25",
    ↓   "ServicePort": 8090,
    ↓   "ServiceMeta": {
    ↓     "version": "1.0.0",
    ↓     "health": "passing"
    ↓   }
    ↓ }
    ↓
    ↓ EventBus публикует 3 события:
    ↓ Публикует 3 события:
    ↓ Event: "ai.task.delegated"
    ↓ {
    ↓   "agent": "db_intelligence",
    ↓   "task": "diagnose_root_cause",
    ↓   "priority": "critical",
    ↓   "context": {...}
    ↓ }
    ↓ + 2 других события для DevOps Agent и Scenario Intelligence

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 5: EXPERT ANALYSIS (DB Intelligence + Expertise Center)   │
└─────────────────────────────────────────────────────────────────┘

13. DB Intelligence Agent (Port 8051)
    ↓ Подписан на EventBus: "ai.task.delegated" (agent=db_intelligence)
    ↓
    ↓ Анализирует:
    ↓ • pg_stat_statements → Находит top 10 slow queries
    ↓ • EXPLAIN ANALYZE → Обнаруживает Seq Scan вместо Index Scan
    ↓ • Source: BIA Service, process_framework.py:245
    ↓ • Root cause: N+1 query pattern
    ↓
    ↓ Diagnosis:
    ↓ {
    ↓   "root_cause": "n_plus_one_queries",
    ↓   "source_service": "bia-service",
    ↓   "source_file": "process_framework.py:245",
    ↓   "query_pattern": "SELECT * FROM processes WHERE id = ?",
    ↓   "executions_per_request": 100,
    ↓   "recommendation": "Use JOIN or batch SELECT with IN clause"
    ↓ }

14. Expertise Center (Port 8035)
    ↓ DB Intelligence вызывает:
    ↓ domains/bcm/tactical_assistants/performance_assistant.py
    ↓
    ↓ Использует AI Foundation (Port 8040):
    ↓ • rag/rag_pipeline.py → Ищет в knowledge base
    ↓ • Находит: "PostgreSQL N+1 Query Optimization"
    ↓ • llm/llm_router.py → Claude 3.5 Sonnet
    ↓ • Генерирует SQL fix:
    ↓
    ↓   # Before (N+1):
    ↓   for process in processes:
    ↓       steps = db.query("SELECT * FROM steps WHERE process_id = ?", process.id)
    ↓
    ↓   # After (JOIN):
    ↓   SELECT processes.*, steps.*
    ↓   FROM processes
    ↓   LEFT JOIN steps ON steps.process_id = processes.id
    ↓   WHERE processes.workflow_id = ?
    ↓
    ↓ Code fix generated with confidence: 95%

15. DB Intelligence + Expertise Center → EventBus
    ↓ Публикует:
    ↓ Event: "expert.diagnosis.completed"
    ↓ {
    ↓   "diagnosis": {...},
    ↓   "fix": {...},
    ↓   "confidence": 0.95,
    ↓   "estimated_improvement": "80% latency reduction"
    ↓ }

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 6: SCENARIO EXECUTION (Scenario Intelligence)             │
└─────────────────────────────────────────────────────────────────┘

16. Scenario Intelligence (Port 8090)
    ↓ Подписан на EventBus: "ai.task.delegated" (agent=scenario_intelligence)
    ↓
    ↓ engines/scenario_engine.py
    ↓ → Загружает сценарий: "db_overload_recovery.v1.0.0.yaml"
    ↓
    ↓ Сценарий (4-level hierarchy):
    ↓ Level 3 (Inter-system): db_overload_recovery
    ↓ ├── Step 1: Scale DB connection pool (immediate)
    ↓ │   └── Call: infrastructure/database/postgresql/scale_pool.sh
    ↓ ├── Step 2: Enable query cache (Redis)
    ↓ │   └── Call: infrastructure/redis/enable_cache.sh
    ↓ ├── Step 3: Apply SQL optimization
    ↓ │   └── Call Level 1: bia_service_apply_fix (wait for expert fix)
    ↓ ├── Step 4: Monitor recovery
    ↓ │   └── Call: mio-manager/api/check_metrics
    ↓ └── Step 5: Rollback if failed
    ↓     └── Chaos Engine: rollback_plan

17. Scenario Intelligence executes steps:

    ↓ Step 1: Scale DB pool (5 → 20 connections)
    ↓ $ infrastructure/database/postgresql/scale_pool.sh --connections 20
    ↓ ✅ Success: Pool scaled

    ↓ Step 2: Enable Redis cache
    ↓ $ infrastructure/redis/enable_cache.sh --ttl 300
    ↓ ✅ Success: Cache enabled

    ↓ Step 3: Wait for expert fix from EventBus
    ↓ Ожидает: "expert.diagnosis.completed"
    ↓ Получено! Применяет fix:
    ↓ $ git apply /tmp/fix_n_plus_one.patch
    ↓ $ systemctl restart bia-service
    ↓ ✅ Success: BIA Service restarted

    ↓ Step 4: Monitor recovery
    ↓ $ curl http://mio-manager:8095/api/metrics/postgresql
    ↓ Response: {
    ↓   "connections": 45/20,  # Уменьшилось!
    ↓   "query_latency": 800ms,  # Улучшилось с 5000ms!
    ↓   "cpu": 45%
    ↓ }
    ↓ ✅ Success: Metrics improved

    ↓ Step 5: Rollback (NOT needed, recovery successful)

18. Scenario Intelligence → EventBus
    ↓ Публикует:
    ↓ Event: "scenario.execution.completed"
    ↓ {
    ↓   "scenario_id": "db_overload_recovery",
    ↓   "result": "success",
    ↓   "duration_seconds": 45,
    ↓   "steps_executed": 4,
    ↓   "steps_failed": 0,
    ↓   "metrics_improvement": {
    ↓     "query_latency": "-84%",  # 5000ms → 800ms
    ↓     "connections": "-55%"
    ↓   }
    ↓ }

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 7: WORKFLOW ORCHESTRATION (Workflow Engine - Long Running)│
└─────────────────────────────────────────────────────────────────┘

19. Workflow Engine (Port 8036)
    ↓ Для ДОЛГИХ процессов (days/weeks), создает BPMN workflow:
    ↓
    ↓ workflow/bpmn/engine_persistent.py
    ↓ → Создает процесс: "Post-Incident Review"
    ↓
    ↓ BPMN Workflow (ISO 22301 - 10.2 Nonconformity and corrective action):
    ↓
    ↓ <bpmn:process id="post_incident_review">
    ↓   <bpmn:startEvent id="start"/>
    ↓
    ↓   <bpmn:serviceTask id="collect_evidence"
    ↓                     name="Collect Incident Evidence">
    ↓     <bpmn:script>
    ↓       evidence = {
    ↓         "incident_id": "inc_xxx",
    ↓         "duration": "45 seconds",
    ↓         "root_cause": "N+1 queries",
    ↓         "fix_applied": "SQL JOIN optimization"
    ↓       }
    ↓     </bpmn:script>
    ↓   </bpmn:serviceTask>
    ↓
    ↓   <bpmn:userTask id="team_review"
    ↓                  name="Team Review (Human)">
    ↓     <bpmn:documentation>
    ↓       DevOps team reviews incident and approves lessons learned
    ↓     </bpmn:documentation>
    ↓   </bpmn:userTask>
    ↓
    ↓   <bpmn:serviceTask id="update_case_library"
    ↓                     name="Update Case Library">
    ↓     <bpmn:script>
    ↓       POST /workflow_intelligence/case_library/add
    ↓       {
    ↓         "title": "PostgreSQL N+1 Query in BIA Service",
    ↓         "root_cause": "N+1 queries",
    ↓         "solution": "SQL JOIN optimization",
    ↓         "success_rate": 1.0,
    ↓         "duration": 45
    ↓       }
    ↓     </bpmn:script>
    ↓   </bpmn:serviceTask>
    ↓
    ↓   <bpmn:endEvent id="end"/>
    ↓ </bpmn:process>
    ↓
    ↓ Workflow persisted to PostgreSQL:
    ↓ • workflow_instances (id, status, start_time)
    ↓ • workflow_states (current_step, context)
    ↓ • Survives restarts/crashes

20. Workflow Engine → EventBus
    ↓ Публикует:
    ↓ Event: "workflow.bpmn.started"
    ↓ {
    ↓   "workflow_id": "wf_post_incident_review_xxx",
    ↓   "process_definition_id": "post_incident_review",
    ↓   "current_step": "collect_evidence"
    ↓ }

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 8: OPTIMIZATION (AI Workflow Optimizer + Learning)        │
└─────────────────────────────────────────────────────────────────┘

21. AI Workflow Optimizer (Port 8038)
    ↓ Подписан на EventBus: "scenario.execution.completed"
    ↓
    ↓ Анализирует выполненный сценарий:
    ↓ • Total duration: 45 seconds
    ↓ • Bottlenecks:
    ↓   - Step 3 (Apply fix): 30 seconds (67% времени!)
    ↓   - Причина: Restart BIA Service (systemctl takes time)
    ↓
    ↓ ML model (trained on historical scenarios):
    ↓ • Recommendation: "Use rolling restart instead of full restart"
    ↓ • Estimated improvement: 30s → 5s (83% reduction)
    ↓ • Confidence: 0.88
    ↓
    ↓ Generates optimization suggestion:
    ↓ {
    ↓   "scenario_id": "db_overload_recovery",
    ↓   "optimization": "rolling_restart",
    ↓   "estimated_improvement_seconds": 25,
    ↓   "confidence": 0.88,
    ↓   "applies_to_step": "apply_sql_fix"
    ↓ }

22. AI Workflow Optimizer → EventBus
    ↓ Публикует:
    ↓ Event: "workflow.optimization.suggested"
    ↓ {
    ↓   "scenario_id": "db_overload_recovery",
    ↓   "optimization": {...},
    ↓   "approval_required": true  # Требует human approval
    ↓ }

23. Workflow Intelligence (Port 8037)
    ↓ Подписан на EventBus: "workflow.optimization.suggested"
    ↓
    ↓ governance/governance_orchestrator.py
    ↓ → validate_optimization_suggestion()
    ↓
    ↓ governance/rules_engine_v2.py:
    ↓ • Best Practice Rule: "ML recommendations require approval if confidence < 0.90"
    ↓ • Confidence: 0.88 → ⚠️ Requires approval
    ↓
    ↓ Decision:
    ↓ {
    ↓   "decision_type": "approve_with_review",
    ↓   "rationale": "Optimization suggestion confidence 0.88 requires human review",
    ↓   "actions_to_take": [
    ↓     "send_notification_to_devops_team",
    ↓     "create_approval_workflow"
    ↓   ]
    ↓ }

24. Notification Service (infrastructure/observability/notification-service/)
    ↓ Отправляет уведомление:
    ↓ To: devops-team@company.com
    ↓ Subject: "Scenario Optimization Approval Required"
    ↓ Body: "AI Workflow Optimizer suggests rolling restart for db_overload_recovery..."
    ↓ Link: http://admin-panel/approvals/opt_xxx

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 9: LEARNING (AI Foundation + Predictive + Case Library)   │
└─────────────────────────────────────────────────────────────────┘

25. AI Foundation (Port 8040)
    ↓ learning/self_learning_engine.py
    ↓ Подписан на EventBus: "scenario.execution.completed"
    ↓
    ↓ Извлекает паттерн:
    ↓ Pattern: {
    ↓   "trigger": "monitoring.kpi.violation (query_latency)",
    ↓   "root_cause": "n_plus_one_queries",
    ↓   "solution": "sql_join_optimization",
    ↓   "success_rate": 1.0,
    ↓   "duration": 45,
    ↓   "correlation": 0.95
    ↓ }
    ↓
    ↓ Обновляет ML модель:
    ↓ • Anomaly detector → Learns "N+1 query pattern"
    ↓ • Predictive model → Updates "time_to_exhaustion" accuracy
    ↓
    ↓ learning/pattern_extractor.py:
    ↓ • Extracts rule: "IF query_latency > 2000ms AND seq_scan_count > 100
    ↓                    THEN likely N+1 queries"

26. Predictive Service (Port 8031)
    ↓ Обновляет модель прогнозирования:
    ↓
    ↓ services/journey_predictor.py:
    ↓ • Записывает результат в историю
    ↓ • Prediction accuracy: 85% → 90% (улучшилось!)
    ↓ • Next time: Предскажет на 10 минут раньше
    ↓
    ↓ integrations/event_intelligence_learning.py:
    ↓ • Обучает event correlation:
    ↓   "monitoring.kpi.violation" → 15 мин → "resource.exhaustion" (confidence: 0.95)

27. Workflow Intelligence (Port 8037)
    ↓ case_library/ (historical learning):
    ↓
    ↓ Добавляет новый кейс:
    ↓ POST /case_library/add
    ↓ {
    ↓   "case_id": "case_189",
    ↓   "title": "PostgreSQL N+1 Query Recovery",
    ↓   "domain": "bcm",
    ↓   "category": "performance",
    ↓   "root_cause": "n_plus_one_queries",
    ↓   "solution": "sql_join_optimization",
    ↓   "success_rate": 1.0,
    ↓   "duration_seconds": 45,
    ↓   "organization_type": "healthcare",
    ↓   "tags": ["postgresql", "bia-service", "n+1", "optimization"],
    ↓   "evidence": {
    ↓     "metrics_before": {"query_latency": 5000, "connections": 95},
    ↓     "metrics_after": {"query_latency": 800, "connections": 45},
    ↓     "improvement": "-84%"
    ↓   }
    ↓ }
    ↓
    ↓ governance/goals_engine.py:
    ↓ • Goal 2.1: "PDCA Continuous Improvement" → ✅ ACHIEVED
    ↓ • Records PDCA cycle:
    ↓   - Plan: Prevent future N+1 queries
    ↓   - Do: Applied SQL JOIN optimization
    ↓   - Check: Verified 84% improvement
    ↓   - Act: Updated Case Library + ML models

28. Community Intelligence (Port 8030)
    ↓ Синхронизирует в community case library:
    ↓ • Anonymizes organization data
    ↓ • Shares with other healthcare orgs (K-anonymity)
    ↓ • Contribution reputation: +10 points

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 10: VALIDATION (MiO Manager + Digital Twin)               │
└─────────────────────────────────────────────────────────────────┘

29. MiO Manager (Port 8095)
    ↓ Продолжает мониторинг (60 секунд спустя):
    ↓
    ↓ monitoring/ checks metrics:
    ↓ • Query latency: 800ms ✅ (target: <2000ms)
    ↓ • Connections: 45 ✅ (max: 100)
    ↓ • CPU: 45% ✅ (threshold: <80%)
    ↓
    ↓ intelligence/ validates:
    ↓ • KPI restored: ✅
    ↓ • Alert closed: ✅
    ↓ • Incident duration: 45 seconds
    ↓
    ↓ reaction/alert_manager.py:
    ↓ • Sends resolution notification
    ↓ • Updates incident status: "resolved"

30. Prometheus (Port 9090)
    ↓ infrastructure/observability/prometheus/
    ↓
    ↓ Scrapes /metrics from ALL services every 15 seconds:
    ↓
    ↓ Scrape targets:
    ↓ • postgresql:5432/metrics →
    ↓     - postgresql_connections: 45 (was 95)
    ↓     - postgresql_query_duration_p95: 800ms (was 5000ms)
    ↓ • bia-service:8008/metrics →
    ↓     - http_requests_total: 150/min
    ↓     - http_request_duration_p95: 1200ms (was 6000ms)
    ↓ • api-gateway:8000/metrics →
    ↓     - gateway_requests_total: 150/min
    ↓     - gateway_rate_limit_exceeded: 0
    ↓ • mio-manager:8095/metrics →
    ↓     - mio_services_healthy: 30/30
    ↓     - mio_alerts_active: 0 (was 1)
    ↓
    ↓ Stores time-series data:
    ↓ • Retention: 15 days
    ↓ • Storage: /prometheus/data
    ↓
    ↓ Alerting rules:
    ↓ • Rule: "DB Overload" (FIRING → RESOLVED)
    ↓   - Query: postgresql_query_duration_p95 > 2000ms
    ↓   - Duration: 45 seconds
    ↓   - Resolution: 14:31:00Z
    ↓
    ↓ Sends alert to Alertmanager:
    ↓ {
    ↓   "status": "resolved",
    ↓   "labels": {
    ↓     "alertname": "DB Overload",
    ↓     "severity": "critical",
    ↓     "service": "postgresql"
    ↓   },
    ↓   "annotations": {
    ↓     "summary": "DB query latency restored to normal",
    ↓     "description": "P95 latency: 800ms (target: <2000ms)",
    ↓     "recovery_time": "45 seconds"
    ↓   }
    ↓ }

31. Grafana (Port 3000)
    ↓ infrastructure/observability/grafana/
    ↓
    ↓ Queries Prometheus data:
    ↓ • Dashboard: "Intelligent Core Overview"
    ↓ • Time range: Last 1 hour
    ↓
    ↓ Displays real-time metrics:
    ↓
    ↓ Panel 1: "Service Health"
    ↓ ┌─────────────────────────────────────┐
    ↓ │ ✅ All Services: 30/30 healthy      │
    ↓ │ ✅ API Gateway: passing             │
    ↓ │ ✅ PostgreSQL: passing              │
    ↓ │ ✅ BIA Service: passing             │
    ↓ └─────────────────────────────────────┘
    ↓
    ↓ Panel 2: "DB Query Latency"
    ↓ ┌─────────────────────────────────────┐
    ↓ │ 📉 P95 Latency                      │
    ↓ │ 14:30:00 | █████████ 5000ms ❌      │
    ↓ │ 14:30:15 | ██████ 3500ms            │
    ↓ │ 14:30:30 | ███ 1500ms               │
    ↓ │ 14:30:45 | ██ 800ms ✅ (target)     │
    ↓ │ Target: 2000ms (green line)         │
    ↓ └─────────────────────────────────────┘
    ↓
    ↓ Panel 3: "EventBus Throughput"
    ↓ ┌─────────────────────────────────────┐
    ↓ │ 📊 Events Published                 │
    ↓ │ Last 1 min: 35 events               │
    ↓ │ • monitoring.kpi.violation: 1       │
    ↓ │ • prediction.generated: 1           │
    ↓ │ • governance.decision_made: 1       │
    ↓ │ • ai.task.delegated: 3              │
    ↓ │ • scenario.execution.completed: 1   │
    ↓ │ • workflow.bpmn.started: 1          │
    ↓ │ • ... (28 total in scenario)        │
    ↓ └─────────────────────────────────────┘
    ↓
    ↓ Panel 4: "Resource Usage"
    ↓ ┌─────────────────────────────────────┐
    ↓ │ 💾 PostgreSQL Connections           │
    ↓ │ Active: 45/100 ✅                   │
    ↓ │ 🧠 Memory Usage                     │
    ↓ │ Redis: 128MB/512MB ✅               │
    ↓ │ ⚡ CPU Usage                         │
    ↓ │ Platform: 45% ✅                    │
    ↓ └─────────────────────────────────────┘
    ↓
    ↓ Alert Notifications:
    ↓ • Alert "DB Overload" resolved at 14:31:00Z
    ↓ • Recovery time: 45 seconds ✅
    ↓ • Slack notification sent to #platform-alerts
    ↓
    ↓ 18 Pre-configured Dashboards:
    ↓ 1. Intelligent Core Overview
    ↓ 2. Database Performance
    ↓ 3. API Gateway Metrics
    ↓ 4. AI Services Health
    ↓ 5. EventBus Flow
    ↓ 6. Workflow Execution
    ↓ 7. Platform Services
    ↓ 8. Security Audit
    ↓ 9. Resource Usage
    ↓ 10. Error Rates
    ↓ 11. User Activity
    ↓ 12. BCM Compliance
    ↓ 13. Predictive Analytics
    ↓ 14. AI Office Agents
    ↓ 15. Scenario Intelligence
    ↓ 16. Community Intelligence
    ↓ 17. System BCM
    ↓ 18. Custom Metrics

32. Digital Twin (platform-services/digital-twin/)
    ↓ Обновляет состояние системы:
    ↓
    ↓ storage/ records:
    ↓ • System state: "healthy"
    ↓ • Last incident: "inc_xxx" (resolved)
    ↓ • Recovery time: 45 seconds ✅ (target: <15 min MTTR)
    ↓
    ↓ bridges/ синхронизирует:
    ↓ • Prometheus metrics updated
    ↓ • Grafana dashboard shows green
    ↓ • Living Docs автоматически обновлен

┌─────────────────────────────────────────────────────────────────┐
│ FINAL RESULT: Complete Recovery + Learning                      │
└─────────────────────────────────────────────────────────────────┘

✅ УСПЕХ:
• Duration: 45 seconds
• Improvement: 84% latency reduction (5000ms → 800ms)
• Root cause: Identified (N+1 queries) and fixed (SQL JOIN)
• Learning: Case added to library, ML models updated
• Governance: PDCA cycle completed
• Compliance: ISO 22301 - 10.2 evidence generated
• Next time: Will predict 10 minutes earlier with 95% accuracy
• Total events: 35+ EventBus events (28 scenario + 7 monitoring)

📊 УЧАСТВОВАЛИ (ALL 5 MODULES + 8 MORE!):

Layer 0 (Infrastructure): ✅ 9 КОМПОНЕНТОВ
  ✅ API Gateway - entry point, auth, rate limiting, load balancing
  ✅ Service Discovery (Consul) - service address lookup (3 queries)
  ✅ PostgreSQL - affected component
  ✅ Redis - cache enablement + rate limiting
  ✅ EventBus - coordination (35+ events published!)
  ✅ Prometheus - metrics collection (scraping every 15s from 30 services)
  ✅ Grafana - visualization (18 dashboards, real-time updates)
  ✅ MiO Manager - detection + validation
  ✅ Balancer Service - load distribution

Layer 1 (AI Office): ✅ 4 АГЕНТА
  ✅ Orchestrator - agent coordination
  ✅ DB Intelligence Agent - root cause analysis
  ✅ DevOps Agent - rollback plan preparation
  ✅ Agent Router - routing between agents

Layer 2 (Intelligent Core): ✅ 10 МОДУЛЕЙ
  ✅ Workflow Intelligence - governance decision (Goals + Rules)
  ✅ AI Orchestration - priority + delegation + Service Discovery lookup
  ✅ Scenario Intelligence - scenario execution (4-level)
  ✅ AI Foundation - ML detection + RAG search + self-learning
  ✅ Predictive - forecasting + learning + accuracy improvement
  ✅ Expertise Center - expert recommendations (DB Specialist)
  ✅ Workflow Engine - BPMN post-incident review (long-running)
  ✅ AI Workflow Optimizer - optimization suggestions (rolling restart)
  ✅ Event Intelligence - event correlation learning
  ✅ Community Intelligence - case sharing (anonymized)

Layer 3 (Platform Services): ✅ 3 СЕРВИСА
  ✅ BIA Service - affected service (N+1 query bug fixed)
  ✅ Digital Twin - state management (collectors + processors)
  ✅ Living Docs - auto-documentation update
```

---

## 🔥 КРИТИЧЕСКИЕ ВЫВОДЫ

### 1. API Gateway - Входная точка

**API Gateway** (`/infrastructure/gateway/api-gateway/`) - это ЕДИНАЯ точка входа!

Все внешние запросы проходят через Gateway:
- JWT authentication (<100ms)
- Rate limiting (10,000 req/min)
- Load balancing (round-robin, least-connections)
- Circuit breaker pattern
- Audit logging (100% requests)
- Service Discovery integration

### 2. Service Discovery - Телефонная книга

**Service Discovery** (`/infrastructure/runtime/service-discovery/`, Consul) - как сервисы находят друг друга!

Динамическое обнаружение сервисов:
- Service registration (автоматическая)
- Health checks (каждые 10 секунд)
- Service lookup (<50ms)
- Load balancing metadata
- Version tracking

### 3. EventBus - Сердце Платформы

**EventBus** (`/infrastructure/runtime/eventbus/`) - это ГЛАВНЫЙ координатор!

Все модули общаются через EventBus:
- 35+ событий опубликовано в одном сценарии (28 scenario + 7 monitoring)
- Асинхронная координация
- Decoupled architecture
- Redis Streams backend

### 4. Prometheus + Grafana - Глаза И Мозг Мониторинга

**Prometheus** (`/infrastructure/observability/prometheus/`) - сбор метрик!

Метрики со ВСЕХ сервисов:
- Scraping /metrics every 15 seconds
- 30+ services monitored
- Time-series storage (15 days retention)
- Alerting rules engine
- PromQL query language

**Grafana** (`/infrastructure/observability/grafana/`) - визуализация!

18 pre-configured dashboards:
- Intelligent Core Overview
- Database Performance
- API Gateway Metrics
- EventBus Flow
- Real-time updates
- Alert notifications (Slack, Email)

### 5. MiO Manager - Детектор Проблем

**MiO Manager** (`/infrastructure/AI-office-infrastructure/mio-manager/`) - это детектор проблем!

Не просто мониторинг:
- Intelligence layer - анализ паттернов
- Reaction layer - автоматические реакции
- Scheduler - periodic checks
- Integrations - EventBus, Temporal workflows

### 6. Governance System - Совесть Платформы

**Workflow Intelligence Governance** - это мозг принятия решений!

Goals + Rules на 4 уровнях:
- USER - пользовательские workflows
- SYSTEM - самопроверка (каждые 60 сек)
- COMPONENT - валидация компонентов
- PLATFORM - платформенные цели

### 7. AI Office Infrastructure - Исполнители

**8 агентов** в `/infrastructure/AI-office-infrastructure/`:
- Orchestrator - координация
- Agent Router - маршрутизация
- Analytics Specialist - аналитика
- DB Intelligence - БД оптимизация
- DevOps Agent - DevOps операции
- Project Agent - управление проектами
- AI Event Manager - события AI
- MiO Manager - мониторинг

### 8. Platform Services - Бизнес Логика

**18 сервисов** в `/platform-services/`:
- BIA Service, Risk Service, Compliance Service (BCM core)
- Digital Twin - состояние системы
- Living Docs - живая документация
- Community Service - marketplace + portal
- Simulation - тестирование сценариев

---

## 📈 ЧТО Я УПУСТИЛ В МОИХ СЦЕНАРИЯХ

### ❌ Упустил Layer 0 (Infrastructure):
- ~~EventBus как главный координатор~~ ✅ Исправлено
- ~~MiO Manager как detector~~ ✅ Исправлено
- ~~Service Discovery для health checks~~ ✅ **ДОБАВЛЕНО В PHASE 4**
- ~~Digital Twin для state management~~ ✅ Исправлено
- **API Gateway как entry point** ✅ **ДОБАВЛЕНО В PHASE 0**
- **Prometheus + Grafana observability** ✅ **ДОБАВЛЕНО В PHASE 10**
- **Balancer Service** ✅ Упомянут

### ❌ Упустил Layer 1 (AI Office):
- 8 агентов для исполнения задач
- Agent Router для маршрутизации
- Orchestrator для координации агентов

### ❌ Упустил Governance System:
- Goals Engine (16+ целей)
- Rules Engine V2 (5-level hierarchy)
- Governance Orchestrator (unified decisions)
- Self-monitoring (каждые 60 сек)

### ❌ Упустил Platform Services:
- Digital Twin collectors/processors
- Living Docs auto-update
- Community Intelligence case sharing
- Simulation для тестирования

### ❌ Упустил Event Flow:
- 28 событий в одном сценарии!
- Async coordination через EventBus
- Event Intelligence correlation learning

---

## ✅ ПРАВИЛЬНАЯ МОДЕЛЬ

```
СИСТЕМНЫЙ СЦЕНАРИЙ =

  Layer 0: Entry Point (API Gateway)
     ↓ Auth, Rate Limiting, Load Balancing
     ↓ Service Discovery lookup
     ↓ Route to service

  Layer 0: Detection (MiO Manager + Digital Twin)
     ↓ EventBus

  Layer 2: Prediction (Predictive + AI Foundation ML)
     ↓ EventBus

  Layer 2: Governance (Workflow Intelligence Goals + Rules)
     ↓ EventBus

  Layer 2: Orchestration (AI Orchestration Decision Center)
     ↓ Service Discovery (3 agent lookups)
     ↓ EventBus (3 события для агентов)

  Layer 1: Agents (DB Intelligence, DevOps, etc.)
     ↓ EventBus

  Layer 2: Expert Analysis (Expertise Center + AI Foundation RAG)
     ↓ EventBus

  Layer 2: Execution (Scenario Intelligence)
     ↓ EventBus

  Layer 2: Long Workflows (Workflow Engine BPMN)
     ↓ EventBus

  Layer 2: Optimization (AI Workflow Optimizer)
     ↓ EventBus

  Layer 2: Learning (AI Foundation + Predictive + Case Library)
     ↓ EventBus

  Layer 0: Validation (MiO Manager + Digital Twin)
     ↓ Metrics published

  Layer 0: Observability (Prometheus + Grafana)
     ↓ Scrapes metrics every 15s
     ↓ Visualizes 18 dashboards
     ↓ Sends alerts
```

**Ключи:**
1. **API Gateway** - единая точка входа
2. **Service Discovery** - динамическое обнаружение сервисов
3. **EventBus** - асинхронная координация
4. **Prometheus + Grafana** - observability

---

## 🎯 ОТВЕТ НА ВОПРОС ПОЛЬЗОВАТЕЛЯ

> "почему эти не участвуют: predictive, expertise-center, ai-foundation, workflow-engine, ai_workflow_optimizer"

**ТЕПЕРЬ Я ПОНИМАЮ!**

Они ВСЕ участвуют, но я не показал:

1. **Predictive** - предсказывает проблемы ДО их возникновения (Phase 2)
2. **Expertise Center** - дает expert recommendations (Phase 5)
3. **AI Foundation** - базовый слой для ML/RAG/LLM во ВСЕХ фазах
4. **Workflow Engine** - для долгих BPMN workflows (Phase 7)
5. **AI Workflow Optimizer** - оптимизирует сценарии после выполнения (Phase 8)

ПЛЮС я упустил в первой версии (ТЕПЕРЬ ИСПРАВЛЕНО ✅):
- ~~**EventBus** - главный координатор~~ ✅
- ~~**MiO Manager** - detector~~ ✅
- ~~**Governance System** - decision maker~~ ✅
- ~~**AI Office Agents** - executors~~ ✅
- ~~**Digital Twin** - state manager~~ ✅
- ~~**Platform Services** - business logic~~ ✅
- **API Gateway** - entry point ✅ **ДОБАВЛЕНО**
- **Service Discovery** - service lookup ✅ **ДОБАВЛЕНО**
- **Prometheus** - metrics collection ✅ **ДОБАВЛЕНО**
- **Grafana** - dashboards ✅ **ДОБАВЛЕНО**

---

**Версия:** 2.0.0 ✅ **ОБНОВЛЕНО**
**Дата:** 2025-10-12
**Статус:** ✅ Complete Real Architecture Analysis + Missing Components Added

**Обновления в v2.0.0:**
- ✅ **PHASE 0 добавлен**: API Gateway entry point (7 шагов)
- ✅ **PHASE 4 расширен**: Service Discovery lookup (3 запроса)
- ✅ **PHASE 10 расширен**: Prometheus scraping + Grafana dashboards (2 компонента)
- ✅ **Layer 0 дополнен**: Все 9 infrastructure компонентов
- ✅ **Статистика обновлена**: 35+ событий (было 28), 26 компонентов (было 22)

**Источник истины:** `/catalogs/` (services, subsystems, systems)

**Следующий шаг:** Использовать эту архитектуру для моделирования других сценариев!
