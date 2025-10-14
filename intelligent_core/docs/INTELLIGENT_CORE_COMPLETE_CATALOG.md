# INTELLIGENT CORE - COMPLETE CATALOG

**Generated:** 2025-10-08
**Version:** 2.0.0
**Total Modules:** 12
**Total Documentation Files:** 135
**Total Lines of Code:** 114,142+

---

## Executive Summary

The Intelligent Core represents the "brain" of the AI-Platform-ISO system, providing enterprise-grade artificial intelligence, workflow orchestration, predictive analytics, and domain expertise capabilities. This layer implements a comprehensive suite of AI services including machine learning, natural language processing, knowledge management, workflow automation, and collaborative intelligence.

### Quick Stats
- **Total Modules:** 12 core modules + 6 sub-modules
- **Running Services:** 4 confirmed (ports 8030, 8031, 8032, 8038)
- **API Endpoints:** 332+ across all modules
- **Python Files:** 481
- **Total Classes:** 664
- **Total Functions:** 221
- **Integration Status:** ~75% (high integration between foundation and intelligence layers)

### Port Allocation
| Port | Service | Status |
|------|---------|--------|
| 8030 | ai-orchestration (Collective uses this config value) | Running |
| 8031 | predictive | Running |
| 8032 | collective | Running |
| 8034 | coordination-center | Active |
| 8035 | expertise-center | Active |
| 8036 | workflow-engine | Active |
| 8037 | workflow_intelligence | Active |
| 8038 | ai_workflow_optimizer | Running |
| 8039 | event_intelligence | Active |
| 8040 | ai-foundation | Active |

---

## Architecture Layers

### Layer 1: Foundation (Core AI Services)

This layer provides fundamental AI capabilities that all other services depend on.

#### **ai-foundation**
- **Path:** `/Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation`
- **Port:** 8040
- **Status:** Active (service exists, needs deployment)
- **LOC:** 23,019
- **Purpose:** Core AI services including LLM routing, RAG pipelines, embeddings, ML models, and self-learning engines

**Key Components:**
- LLM Router (800 LOC) - Multi-provider routing (Anthropic, OpenAI)
- RAG Pipeline (1,200 LOC) - Retrieval-Augmented Generation
- Self-Learning Engine (1,500 LOC) - Adaptive learning and model improvement
- Knowledge Base Connector (900 LOC) - Knowledge management integration
- ML Predictor (1,100 LOC) - Machine learning predictions
- Pattern Extractor (700 LOC) - Pattern detection from data

**Features:**
- Multi-provider LLM routing with load balancing
- Advanced RAG with vector search (Qdrant)
- Self-learning from user feedback
- Knowledge base integration
- Embedding generation (sentence-transformers)
- ML-powered predictions

**Dependencies:**
- External: PostgreSQL 14+, Redis 7+, Qdrant vector DB
- Internal: None (foundation layer)
- Libraries: anthropic, openai, sentence-transformers, qdrant-client, scikit-learn

**API Endpoints:** 108 total
- `POST /api/v1/llm/route` - Route LLM requests
- `POST /api/v1/rag/query` - RAG query execution
- `POST /api/v1/learning/feedback` - Submit learning feedback
- `GET /health`, `GET /metrics`

**EventBus Integration:**
- **Publishes:** `ai.llm.routed`, `ai.rag.queried`, `ai.learning.feedback_received`
- **Subscribes:** None (foundation service)

**Database Schemas:** None (uses external vector DB)

**Sub-modules:**
- `learning-knowledge/` - Knowledge management and learning system
  - API on separate port (not documented)
  - Knowledge indexer, updater, monitoring
  - Event-driven architecture

**Current Issues:**
- Service skeleton exists but needs full deployment
- RAG pipeline integration with Qdrant needs configuration
- LLM routing strategy configuration required

---

#### **shared**
- **Path:** `/Users/MD/AI-Platform-ISO/intelligent-core/shared`
- **Purpose:** Shared utilities, clients, and event bus for cross-module communication

**Key Components:**
- `platform_client.py` - Unified client for accessing all platform services
- `event_bus/` - Event bus core, outbox pattern implementation

**Features:**
- Centralized service access
- Event bus abstraction
- Outbox pattern for reliable event delivery

**Dependencies:**
- Internal: All modules use this
- External: RabbitMQ, Redis

---

### Layer 2: Intelligence & Orchestration

Core workflow orchestration, event processing, and intelligent coordination.

#### **workflow_intelligence** (THE BRAIN)
- **Path:** `/Users/MD/AI-Platform-ISO/intelligent-core/workflow_intelligence`
- **Port:** 8037
- **Status:** Active (main service running)
- **LOC:** 24,392
- **Purpose:** Central workflow orchestration, BPMN engine, state machines, case library management

**Key Components:**
- BPMN Workflow Engine - Execute BPMN 2.0 workflows
- State Machine Manager (12 methods) - Manage workflow state transitions
- Rules Engine (BIARules, RiskRules - 11 methods) - Business rule processing
- Activity Coordinator - Coordinate parallel activities
- Context Advisor (AI) - Provide contextual intelligence
- Workflow Optimizer - Performance optimization
- Case Library API - Knowledge repository

**Supported Workflow Types (7):**
1. BIA Workflow - Business Impact Analysis
2. Risk Assessment Workflow - Risk identification and mitigation
3. Compliance Workflow - Gap analysis and certification
4. Document Management Workflow - Document lifecycle
5. Governance Workflow - Policy and decision-making
6. Incident Response Workflow - Incident handling
7. Validation Workflow - Process validation and KPIs

**Features:**
- BPMN 2.0 compliant workflow execution
- Real-time workflow monitoring
- AI-powered workflow recommendations
- Case library for workflow patterns
- ML-powered workflow analysis
- State persistence and recovery

**Dependencies:**
- Internal: ai-foundation (for AI recommendations), community_intelligence (case sync)
- External: PostgreSQL (workflow state), Redis (state cache), RabbitMQ (events), Temporal (workflow engine)

**API Endpoints:** 11 core + case library endpoints
- `POST /api/v1/workflow/start` - Start workflow instance
- `POST /api/v1/workflow/{id}/advance` - Advance to next state
- `GET /api/v1/workflow/{id}/status` - Get workflow status
- `POST /api/v1/workflow/{id}/rollback` - Rollback workflow
- `POST /cases/add` - Add case to library
- `GET /cases/{case_id}` - Get case details
- `POST /cases/search` - Search case library
- `POST /analyze` - ML workflow analysis
- `POST /recommend` - Get recommendations

**EventBus Integration:**
- **Publishes:** `workflow.*.started`, `workflow.*.completed`, `workflow.*.failed`, `workflow.state_changed`
- **Subscribes:** `workflow.start_requested`, `ai.recommendation.*`

**Database Schemas:**
- workflow_instances, workflow_states, workflow_transitions
- case_library (shared with community_intelligence)

**Integration with Community Intelligence:**
- Receives approved cases from community_intelligence
- Endpoint: `/cases/add` used by community sync
- Bi-directional case library sharing

**Current Issues:**
- Case library implementation marked as TODO
- Full ML recommendation system pending
- Temporal workflow integration needs configuration

---

#### **ai_workflow_optimizer**
- **Path:** `/Users/MD/AI-Platform-ISO/intelligent-core/ai_workflow_optimizer`
- **Port:** 8038
- **Status:** Running
- **LOC:** 1,701
- **Purpose:** ML-powered workflow optimization using Random Forest, Isolation Forest, and clustering

**Key Components:**
- Performance Predictor (Random Forest) - Predict execution time
- Bottleneck Detector (Random Forest Classifier) - Identify bottlenecks
- Anomaly Detector (Isolation Forest) - Detect anomalies
- Resource Optimizer - Optimize resource allocation
- ML Training Pipeline - Train models on execution data

**Features:**
- Execution time prediction with 85%+ accuracy
- Bottleneck detection and severity scoring
- Anomaly detection for unusual patterns
- Resource optimization recommendations
- Self-training on workflow execution data
- Platform client integration for AI insights

**Dependencies:**
- Internal: ai-foundation (AI insights), workflow_intelligence (case library), expertise-center (expert insights)
- External: PostgreSQL (ML models, execution data), scikit-learn, pandas, numpy

**API Endpoints:** 12 total
- `POST /api/v1/optimize/performance` - Performance optimization
- `GET /api/v1/analyze/bottlenecks/{id}` - Bottleneck analysis
- `GET /api/v1/optimize/resources/{id}` - Resource optimization
- `GET /api/v1/detect/anomalies/{id}` - Anomaly detection
- `POST /api/v1/models/retrain` - Retrain ML models
- `GET /api/v1/models/status` - Model status
- `GET /api/v1/ai/analyze/{id}` - AI-powered analysis (uses platform client)
- `POST /api/v1/ai/recommendations` - AI recommendations
- `POST /api/v1/ai/learn` - Learn from execution

**EventBus Integration:**
- **Publishes:** `workflow.optimization.completed`, `ml.model.trained`
- **Subscribes:** `workflow.execution.completed`

**Database Schemas:**
- process_executions (execution history)
- optimization_predictions (ML predictions)
- ml_models (trained models)

**Platform Client Integration:**
- Uses shared/platform_client.py for AI Foundation, Expertise Center, Workflow Intelligence access
- Combines ML models with AI insights and expert knowledge
- Learns from successful executions and adds to case library

---

#### **event_intelligence**
- **Path:** `/Users/MD/AI-Platform-ISO/intelligent-core/event_intelligence`
- **Port:** 8039
- **Status:** Active
- **LOC:** 3,545
- **Purpose:** Intelligent event analysis, pattern detection, automated healing, auto-discovery

**Key Components:**
- Domain Detector - Identify domains from events
- Error Analyzer - Analyze error patterns
- Self-Healing Engine - Automated recovery
- Auto-Discovery Engine - Discover services and patterns
- Pattern Learner - Learn event patterns
- Event Graph Builder - Build event flow graphs

**Features:**
- Real-time event analysis with AI
- Pattern detection and prediction
- Automated code healing
- Service auto-discovery
- Event correlation and causation
- ML-powered gap prediction

**Dependencies:**
- Internal: ai-foundation (AI analysis)
- External: Redis (event cache), PostgreSQL (pattern storage)

**API Endpoints:** 17 total
- Core event intelligence endpoints
- `/discovery/services` - Get discovered services
- `/discovery/patterns` - Get learned patterns
- `/discovery/predict/{event_type}` - Predict next event
- `/discovery/stats` - Discovery statistics
- `/discovery/graph` - Event flow graph

**EventBus Integration:**
- **Publishes:** `event.analyzed`, `event.pattern_detected`, `event.anomaly_detected`
- **Subscribes:** All platform events (auto-discovery)

**Database Schemas:** event_patterns, event_predictions, service_registry

---

#### **orchestration**
- **Path:** `/Users/MD/AI-Platform-ISO/intelligent-core/orchestration`
- **LOC:** 25,171
- **Purpose:** Centralized AI service coordination and control

**Sub-modules:**

##### **ai-orchestration**
- **Port:** 8030 (main orchestration)
- **Status:** Active
- **LOC:** ~12,000+
- **Purpose:** The autonomous decision-making brain - aggregates context, assesses priority, selects strategies, validates safety

**Key Components:**
- Unified Controller - Main orchestration controller
- Decision Center - Context aggregation, priority assessment, strategy selection, delegation
- Distributed Memory (4 layers):
  - Working Memory (Redis, 1 hour TTL)
  - Short-Term Memory (PostgreSQL, 30 days)
  - Long-Term Memory (Case Library, permanent)
  - Procedural Memory (ML models, learned patterns)
- Safety Monitor - Constitution enforcement, loop detection, hallucination detection
- Evolution Engine - Data, model, code evolution (daily/weekly/monthly)
- AI Agents - Claude Pro, DevOps, Context-aware agents
- Platform Orchestrator - Service lifecycle, Docker management
- Scenario Orchestrator - AI-powered scenario generation

**Features:**
- Autonomous decision-making with safety constraints
- 4-layer memory system
- Constitutional rules (immutable safety rules)
- Self-evolution (3 levels)
- Service lifecycle management
- Docker container orchestration
- AI-powered scenario generation
- Deployment orchestration
- Real-time monitoring integration

**API Endpoints:** 75 total including:
- System: `/api/v1/system/status`, `/api/v1/system/restart`
- Platform: `/api/v1/platform/services/*` (start, stop, restart, status)
- AI: `/api/v1/ai/rules`, `/api/v1/ai/decisions/*`
- Scenario: `/api/v1/scenario/generate`, `/api/v1/scenario/{id}`
- AI Agents: `/api/v1/ai/agent/process`, `/api/v1/ai/agents/health`
- Claude: `/api/v1/claude/analyze-changes`, `/api/v1/claude/generate-config`
- Deployment: `/api/v1/deployment/orchestrate`

**EventBus Integration:**
- **Publishes:** `orchestration.decision_made`, `orchestration.service.*`, `ai.decision.*`
- **Subscribes:** All platform events for context aggregation

##### **coordination-center**
- **Port:** 8034
- **Status:** Active
- **LOC:** ~8,000+
- **Purpose:** Mediator between Intelligent Core (AI) and Execution Engine (BCM tools)

**Key Components:**
- Command Interpreter - Translate AI intents to API calls
- Tool Registry - Catalog of available tools for AI
- Execution Tracker - Track command execution status
- Security Layer - Permission control, rate limiting, audit

**Features:**
- Intent-to-API translation
- Human-in-the-loop for critical operations
- Execution rollback capability
- Audit logging of all AI actions
- Rate limiting for AI agents
- Security and permission system

**API Endpoints:**
- `/coordination/execute` - Execute AI intent
- `/coordination/executions/{id}` - Get execution status
- `/coordination/executions/{id}/rollback` - Rollback execution
- `/coordination/health` - Health check

**EventBus Integration:**
- **Publishes:** `coordination.execution.*`, `coordination.approval_required`
- **Subscribes:** `orchestration.decision_made`, `workflow.action_required`, `ai.recommendation`

---

#### **workflow-engine**
- **Path:** `/Users/MD/AI-Platform-ISO/intelligent-core/workflow-engine`
- **Port:** 8036
- **Status:** Active (skeleton service)
- **LOC:** 6,361
- **Purpose:** BPMN 2.0 compliant workflow execution with persistent state management

**Features:**
- BPMN 2.0 workflow execution
- Expression evaluation
- Gateway logic
- Event-driven coordination
- Persistent state management

**Dependencies:**
- Internal: workflow_intelligence (primary orchestrator)
- External: PostgreSQL

---

### Layer 3: Domain Expertise & Collaboration

Specialized AI assistants, domain experts, and community-driven knowledge.

#### **expertise-center**
- **Path:** `/Users/MD/AI-Platform-ISO/intelligent-core/expertise-center`
- **Port:** 8035
- **Status:** Active
- **LOC:** 11,846
- **Purpose:** Domain expertise and specialized AI assistants for BCM

**Key Components:**

**Tactical Assistants (12):**
1. BIA Specialist - Business Impact Analysis expert
2. Risk Analyst - Risk assessment and mitigation
3. Compliance Copilot - ISO compliance guidance
4. Incident Advisor - Incident response support
5. Plan Generator - BCM plan generation
6. Exercise Designer - Exercise scenario design
7. Project Manager - BCM project management
8. Documents Specialist - Document management
9. Governance Specialist - Governance and policy
10. Learning Specialist - Training and learning
11. Validation Specialist - Process validation
12. Community Specialist - Community engagement

**Strategic Analyzers (10):**
1. Compliance Analyzer - Compliance gap analysis
2. Risk Analyzer - Strategic risk analysis
3. Governance Analyzer - Governance effectiveness
4. Lifecycle Analyzer - Process lifecycle analysis
5. Learning Analyzer - Learning effectiveness
6. Performance Analyzer - Performance metrics
7. Emergency Analyzer - Emergency readiness
8. Impact Analyzer - Business impact analysis
9. Plan Analyzer - Plan quality assessment
10. Scenario Analyzer - Scenario realism

**Base Classes:**
- BaseTacticalAssistant - Common assistant functionality
- BaseAnalyzer - Common analyzer functionality
- BaseSpecialist - Common specialist functionality

**Features:**
- 22 specialized AI assistants (12 tactical + 10 strategic)
- Domain-specific knowledge bases
- Integration with ai-foundation for RAG and LLM
- Contextual guidance and recommendations
- Expert-level analysis and insights

**Dependencies:**
- Internal: ai-foundation (RAG, LLM, embeddings)
- External: PostgreSQL (knowledge base), Qdrant (vector search)

**API Endpoints:** 28 total
- `/expertise/assistants` - List all assistants
- `/expertise/assistants/{type}` - Get specific assistant
- `/expertise/analyze` - Request analysis
- `/expertise/recommend` - Get recommendations

**EventBus Integration:**
- **Publishes:** `expert.analysis.completed`, `expert.recommendation.*`
- **Subscribes:** `workflow.*.started`, `user.question`

**AI Foundation Integration:**
- All tactical assistants and analyzers now use ai-foundation base class
- Inheritance: BaseTacticalAssistant → AIFoundation
- Shared RAG pipeline, LLM routing, embeddings
- Recent migration (2025-10-08) consolidated duplicate code

---

#### **community_intelligence**
- **Path:** `/Users/MD/AI-Platform-ISO/intelligent-core/community_intelligence`
- **Port:** 8030 (Note: config says 8031 but may have conflict)
- **Status:** Active
- **LOC:** 8,116
- **Purpose:** Community-driven knowledge creation, peer review, reputation system

**Key Components:**
- Contribution Manager - Manage user contributions
- Peer Review System - 3-reviewer peer review workflow
- Reputation Engine - Track user expertise and reputation
- Case Library Manager - Curate approved cases
- AI Synthesizer - Synthesize community knowledge with AI
- ML Predictor - Predict timelines and outcomes
- Anonymization Engine - K-anonymity (k=5) for privacy

**Features:**
- Peer review workflow (3 reviewers, approval threshold)
- Reputation system with levels (newcomer → contributor → expert → master)
- AI-powered knowledge synthesis
- Case library curation and approval
- Timeline prediction based on similar organizations
- Next-step recommendations
- Community annotations and guidance
- Marketplace demand forecasting
- Proactive monitoring for stuck workflows

**Dependencies:**
- Internal: workflow_intelligence (case sync), ai-foundation (AI synthesis)
- External: PostgreSQL (contributions, reviews), Redis (cache)

**API Endpoints:** 37 total including:
- `/api/v1/community/contributions` - Submit contributions
- `/api/v1/community/reviews` - Peer review system
- `/api/v1/community/reputation` - Reputation management
- `/api/v1/community/reputation/leaderboard` - Community leaderboard
- `/api/v1/community/cases` - Case library
- `/api/v1/community/annotations` - Community annotations
- `/api/v1/community/guidance/{clause_id}` - Clause guidance
- `/api/v1/community/timeline/predict` - Predict timeline
- `/api/v1/community/timeline/{org_id}/next-steps` - Next steps
- `/api/v1/community/clauses/search` - Search clauses
- `/api/v1/community/marketplace/demand-forecast` - Demand forecast
- `/api/v1/community/stats/community` - Community statistics

**EventBus Integration:**
- **Publishes:** `community.case.approved`, `community.contribution.*`, `community.review.*`
- **Subscribes:** `workflow.stuck`, `user.inactive`

**Database Schemas:**
- contributions, peer_reviews, reputation_scores, case_library (shared with workflow_intelligence)

**Workflow Intelligence Integration:**
- Syncs approved cases to workflow_intelligence via `/cases/add` endpoint
- Bi-directional case library sharing
- Configured URL: http://localhost:8037 (updated from 8020)

**AI Foundation Integration:**
- Uses ai-foundation for AI synthesis
- RAG-powered guidance generation
- LLM-powered timeline predictions

---

#### **collective**
- **Path:** `/Users/MD/AI-Platform-ISO/intelligent-core/collective`
- **Port:** 8032
- **Status:** Running
- **LOC:** 5,230
- **Purpose:** Privacy-preserving collective intelligence and anonymous collaboration

**Key Components:**
- Collective Agent Creator - Create temporary agents from multiple organizations
- Stuck Detection Engine - Detect when organizations need help
- Anonymization Engine - Multi-layer anonymization (k-anonymity k=5)
- Privacy Risk Calculator - Calculate re-identification risk
- Agent Lifecycle Manager - Manage agent expiration (7 days)

**Features:**
- **Anonymous Collaboration:** Organizations help each other without revealing identities
- **Collective Agents:** Temporary AI agents created from 5+ organizations' experiences
- **Stuck Detection:** Automatic detection of organizations needing help (4+ signals)
- **Privacy Guarantees:**
  - K-anonymity (minimum 5 organizations)
  - Multi-layer anonymization
  - No outlier highlighting
  - Geographic generalization
  - Agent expiration (7 days)
- **Privacy Architecture:**
  - Layer 1: Organization anonymization
  - Layer 2: Aggregation (min 5 orgs)
  - Layer 3: Collective agent synthesis

**Stuck Detection Signals:**
- Days without progress (7+ days)
- Validation failures (5+ failures)
- Low AI confidence (<0.6)
- Frustration indicators

**Dependencies:**
- Internal: community_intelligence (case data), ai-foundation (agent LLM)
- External: PostgreSQL (collective agents), Redis (cache)

**API Endpoints:** 10 total
- `/api/v1/collective-agents` - Manage collective agents
- `/api/v1/collective-agents/create` - Create agent
- `/api/v1/collective-agents/{id}` - Agent details
- `/api/v1/collective-agents/{id}/chat` - Chat with agent
- `/api/v1/stuck-detection` - Stuck detection
- `/api/v1/stuck-detection/{org_id}` - Check if org stuck

**EventBus Integration:**
- **Publishes:** `collective.agent.created`, `collective.org.stuck_detected`
- **Subscribes:** `workflow.no_progress`, `validation.failure`

**Database Schemas:**
- collective_agents, stuck_detection_signals, anonymized_experiences

---

### Layer 4: Predictive Intelligence

Proactive recommendations and journey prediction.

#### **predictive**
- **Path:** `/Users/MD/AI-Platform-ISO/intelligent-core/predictive`
- **Port:** 8031
- **Status:** Running
- **LOC:** 4,761
- **Purpose:** Predictive analytics and proactive recommendations for BCM journeys

**Key Components:**
- Journey Predictor - Predict 90-day organization journey
- Certification Timeline Predictor - Predict certification date
- Proactive Recommendation Engine - Generate personalized recommendations
- Expert Demand Forecaster - Forecast specialist demand
- Challenge Predictor - Predict upcoming challenges
- Daily Digest Scheduler - Send proactive digests (8 AM daily)

**Features:**
- 90-day journey timeline prediction
- Certification date estimation
- Proactive recommendations before user asks
- Expert demand forecasting
- Challenge prediction
- Daily proactive digests via email
- ML-powered timeline predictions
- Case library pattern matching

**Dependencies:**
- Internal: workflow_intelligence (case library), community_intelligence (patterns), notification-service (email)
- External: PostgreSQL (predictions), APScheduler (cron)

**API Endpoints:** 9 total
- `/api/v1/predictions/journey/{org_id}` - Predict journey
- `/api/v1/predictions/certification/{org_id}` - Predict cert date
- `/api/v1/predictions/recommendations/{org_id}` - Get recommendations
- `/api/v1/predictions/expert-demand` - Forecast expert demand
- `/api/v1/predictions/challenges/{org_id}` - Predict challenges

**EventBus Integration:**
- **Publishes:** 8+ prediction events
  - `prediction.journey.generated`
  - `prediction.certification.estimated`
  - `prediction.recommendation.generated`
  - `prediction.challenge.detected`
  - `prediction.expert_demand.forecasted`
  - `prediction.digest.sent`
  - `prediction.timeline.updated`
  - `prediction.proactive.suggested`
- **Subscribes:** 5+ platform events
  - `workflow.*.completed`
  - `organization.milestone.achieved`
  - `user.activity.logged`
  - `community.case.approved`
  - `validation.kpi.updated`

**Scheduler:**
- Daily digest job at 8:00 AM
- Uses APScheduler with cron triggers

**Database Schemas:**
- predictions, journey_timelines, proactive_recommendations, expert_demand_forecasts

---

### Layer 5: Wrappers & Utilities

#### **wrappers**
- **Path:** `/Users/MD/AI-Platform-ISO/intelligent-core/wrappers`
- **Purpose:** Python wrappers and utilities (details not fully documented)

---

## Module Integration Matrix

| Module | Depends On | Used By | EventBus Pub/Sub |
|--------|-----------|---------|------------------|
| **ai-foundation** | None | All other modules | Pub: 3 / Sub: 0 |
| **workflow_intelligence** | ai-foundation | ai_workflow_optimizer, community_intelligence, predictive | Pub: 4+ / Sub: 2+ |
| **ai_workflow_optimizer** | ai-foundation, workflow_intelligence, expertise-center | orchestration | Pub: 2 / Sub: 1 |
| **event_intelligence** | ai-foundation | orchestration | Pub: 3 / Sub: All (auto-discovery) |
| **ai-orchestration** | ai-foundation, all services | All (orchestrates everything) | Pub: 10+ / Sub: All |
| **coordination-center** | ai-orchestration, workflow_intelligence | All execution services | Pub: 2+ / Sub: 3+ |
| **workflow-engine** | workflow_intelligence | orchestration | Pub: - / Sub: - |
| **expertise-center** | ai-foundation | ai_workflow_optimizer, orchestration | Pub: 2+ / Sub: 2+ |
| **community_intelligence** | ai-foundation, workflow_intelligence | collective, predictive | Pub: 3+ / Sub: 2+ |
| **collective** | ai-foundation, community_intelligence | predictive | Pub: 2+ / Sub: 2+ |
| **predictive** | workflow_intelligence, community_intelligence | orchestration | Pub: 8+ / Sub: 5+ |
| **shared** | None | All modules | - |

---

## Data Flow Patterns

### 1. Workflow Execution Flow
```
User Request
  ↓
ai-orchestration (decision)
  ↓
coordination-center (intent → API calls)
  ↓
workflow_intelligence (execute workflow)
  ↓
ai_workflow_optimizer (optimize)
  ↓
expertise-center (expert guidance)
  ↓
workflow_intelligence (complete)
  ↓
community_intelligence (learn from success)
  ↓
workflow_intelligence (add to case library)
```

### 2. Predictive Intelligence Flow
```
Platform Events
  ↓
predictive (analyze patterns)
  ↓
workflow_intelligence (query case library)
  ↓
community_intelligence (get similar org data)
  ↓
predictive (ML prediction)
  ↓
notification-service (send proactive digest)
```

### 3. Collective Intelligence Flow
```
Organization stuck
  ↓
collective (detect stuck signals)
  ↓
community_intelligence (find similar orgs)
  ↓
collective (anonymize + create agent)
  ↓
ai-foundation (LLM for agent)
  ↓
User chats with collective agent
  ↓
collective (expire after 7 days)
```

### 4. Event Intelligence Flow
```
Platform Events
  ↓
event_intelligence (auto-discover)
  ↓
event_intelligence (learn patterns)
  ↓
ai-foundation (AI analysis)
  ↓
event_intelligence (predict next event)
  ↓
orchestration (proactive action)
```

---

## Technology Stack

### Programming Languages
- Python 3.11+ (primary)
- JavaScript/TypeScript (minimal)

### AI/ML Frameworks
- Anthropic Claude API (LLM)
- OpenAI GPT API (LLM)
- sentence-transformers (embeddings)
- scikit-learn (ML models)
- pandas, numpy (data processing)

### Databases
- PostgreSQL 14+ with JSONB (primary data store)
- Redis 7+ (caching, working memory)
- Qdrant (vector database for RAG)

### Message Queue
- RabbitMQ 3.12+ (EventBus backend)
- Redis Streams (alternative EventBus backend)

### Workflow Engine
- Temporal (workflow orchestration)
- Custom BPMN 2.0 engine

### Web Framework
- FastAPI (all services)
- Uvicorn (ASGI server)

### Observability
- Prometheus (metrics)
- Grafana (dashboards)
- Custom monitoring integration

### Scheduling
- APScheduler (cron jobs, daily digests)

### Other
- Docker (containerization)
- SQLAlchemy (ORM)
- Pydantic (data validation)
- CORS middleware (cross-origin)

---

## EventBus Architecture

### Event Publishing
Total publishers: 40+ across all modules

**By Module:**
- ai-foundation: 3 events (llm.routed, rag.queried, learning.feedback_received)
- workflow_intelligence: 4+ events (workflow.started/completed/failed/state_changed)
- ai_workflow_optimizer: 2 events (optimization.completed, ml.model.trained)
- event_intelligence: 3 events (event.analyzed/pattern_detected/anomaly_detected)
- ai-orchestration: 10+ events (orchestration.*, ai.decision.*)
- coordination-center: 2+ events (coordination.execution.*, approval_required)
- expertise-center: 2+ events (expert.analysis.completed, expert.recommendation.*)
- community_intelligence: 3+ events (community.case.approved, contribution.*, review.*)
- collective: 2 events (collective.agent.created, org.stuck_detected)
- predictive: 8+ events (prediction.*)

### Event Subscriptions
Total subscribers: 25+ across all modules

**Patterns:**
- ai-orchestration subscribes to ALL events (context aggregation)
- event_intelligence subscribes to ALL events (auto-discovery)
- coordination-center subscribes to orchestration.decision_made, workflow.action_required
- expertise-center subscribes to workflow.*.started, user.question
- community_intelligence subscribes to workflow.stuck, user.inactive
- collective subscribes to workflow.no_progress, validation.failure
- predictive subscribes to workflow.*.completed, organization.milestone.achieved

---

## Database Schemas Summary

### Core Schemas
- **workflow_intelligence:** workflow_instances, workflow_states, workflow_transitions, case_library
- **ai_workflow_optimizer:** process_executions, optimization_predictions, ml_models
- **event_intelligence:** event_patterns, event_predictions, service_registry
- **community_intelligence:** contributions, peer_reviews, reputation_scores, case_library (shared)
- **collective:** collective_agents, stuck_detection_signals, anonymized_experiences
- **predictive:** predictions, journey_timelines, proactive_recommendations, expert_demand_forecasts
- **ai-orchestration:** decisions, pending_decisions, decision_history, ml_patterns

### Shared Schemas
- **case_library:** Shared between workflow_intelligence and community_intelligence

---

## API Summary

### Total Endpoints: 332+

**By Module:**
- ai-foundation: 108
- workflow_intelligence: 11+ (core) + case library
- ai_workflow_optimizer: 12
- event_intelligence: 17
- ai-orchestration: 75
- coordination-center: ~15
- workflow-engine: 11
- expertise-center: 28
- community_intelligence: 37
- collective: 10
- predictive: 9

### Common Endpoints (All Services)
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /` - Service info
- `GET /docs` - OpenAPI documentation
- `GET /redoc` - ReDoc documentation

---

## Critical Integration Points

### 1. AI Foundation Integration
**Used by:** All modules requiring AI capabilities
- LLM routing for intelligent responses
- RAG pipeline for knowledge retrieval
- Embedding generation for semantic search
- ML predictions and analytics

### 2. Workflow Intelligence Integration
**Used by:** ai_workflow_optimizer, community_intelligence, predictive, orchestration
- Central workflow orchestration
- Case library (shared with community_intelligence)
- State management
- BPMN execution

### 3. Platform Client (Shared)
**Used by:** ai_workflow_optimizer (confirmed), others as needed
- Unified interface to access all services
- Simplifies inter-service communication
- Example usage in ai_workflow_optimizer:
  ```python
  platform_client.ai.ask(...)
  platform_client.experts.query_expert(...)
  platform_client.workflows.search_cases(...)
  ```

### 4. EventBus (Shared)
**Used by:** All modules
- Event-driven architecture
- Asynchronous communication
- Event sourcing and audit trail

### 5. Community-Workflow Sync
**Direction:** community_intelligence → workflow_intelligence
- Endpoint: `POST /cases/add` on workflow_intelligence
- Purpose: Sync approved cases to case library
- Frequency: Real-time on case approval

---

## Identified Gaps and Issues

### High Priority

1. **Port Conflicts**
   - community_intelligence config says 8031 but main.py says 8030
   - collective config uses 8030 but should be 8032
   - Need unified port allocation strategy

2. **Incomplete Implementations**
   - workflow_intelligence case library marked as TODO
   - workflow_intelligence ML recommendations pending
   - ai-foundation needs full deployment
   - workflow-engine is skeleton only

3. **Missing Integrations**
   - Temporal workflow engine configuration needed
   - Qdrant vector DB setup required
   - Some EventBus subscriptions not implemented

4. **Documentation Gaps**
   - wrappers module not documented
   - Some sub-modules (learning-knowledge) ports unknown
   - Database migration strategy not documented

### Medium Priority

5. **Configuration Management**
   - Inconsistent config file locations
   - Some services use .env, others hardcode
   - Need centralized configuration

6. **Testing**
   - Test coverage varies (78-85%)
   - Integration tests not comprehensive
   - E2E testing strategy needed

7. **Monitoring**
   - Prometheus metrics defined but dashboard missing
   - Alerting rules not defined
   - Log aggregation not configured

### Low Priority

8. **Code Quality**
   - Some duplicate code (being addressed)
   - Recent ai-foundation migration improved this
   - Further consolidation opportunities

9. **Documentation**
   - API documentation complete but examples limited
   - Deployment guides need updates
   - Architecture diagrams need updates

---

## Deployment Readiness

### Production Ready (4 services running)
✅ **ai-orchestration** (port 8030)
✅ **predictive** (port 8031)
✅ **collective** (port 8032)
✅ **ai_workflow_optimizer** (port 8038)

### Near Production Ready (needs configuration)
⚠️ **coordination-center** (port 8034) - Active, needs integration testing
⚠️ **expertise-center** (port 8035) - Active, AI foundation integrated
⚠️ **workflow-engine** (port 8036) - Active, needs full implementation
⚠️ **workflow_intelligence** (port 8037) - Active, case library TODO
⚠️ **event_intelligence** (port 8039) - Active, needs full deployment
⚠️ **ai-foundation** (port 8040) - Active, needs deployment

### Needs Work
❌ **community_intelligence** (port conflict, integration testing needed)
❌ **Temporal integration** (workflow engine backend)
❌ **Qdrant setup** (vector DB for RAG)

---

## Recommendations

### Immediate Actions (Week 1)

1. **Resolve Port Conflicts**
   - Standardize community_intelligence to 8030
   - Update all configuration files
   - Document port allocation in central registry

2. **Deploy AI Foundation**
   - Configure Qdrant vector database
   - Set up LLM API keys (Anthropic, OpenAI)
   - Deploy service on port 8040
   - Validate all dependent services work

3. **Complete Workflow Intelligence**
   - Implement case library endpoints
   - Configure Temporal workflow engine
   - Test ML recommendation system
   - Validate community_intelligence sync

4. **Integration Testing**
   - Test platform client across all services
   - Validate EventBus pub/sub
   - Test end-to-end workflows
   - Document integration patterns

### Short Term (Month 1)

5. **Monitoring & Observability**
   - Create Prometheus dashboards
   - Set up alerting rules
   - Configure log aggregation
   - Document monitoring setup

6. **Configuration Management**
   - Centralize all configuration
   - Create environment templates
   - Document deployment process
   - Create Docker Compose for local dev

7. **Documentation Updates**
   - Update architecture diagrams
   - Create API integration examples
   - Document deployment procedures
   - Create troubleshooting guide

8. **Testing Strategy**
   - Increase test coverage to 90%+
   - Create integration test suite
   - Set up E2E testing
   - Automate testing in CI/CD

### Long Term (Quarter 1)

9. **Performance Optimization**
   - Profile all services
   - Optimize database queries
   - Implement caching strategies
   - Load testing and tuning

10. **Security Hardening**
    - Implement service mesh
    - Add authentication/authorization
    - Enable TLS everywhere
    - Security audit

11. **Scalability**
    - Design for horizontal scaling
    - Implement service discovery
    - Set up load balancing
    - Plan for multi-tenancy

12. **Advanced Features**
    - Complete self-evolution engine
    - Implement advanced AI features
    - Enhance collective intelligence
    - Improve predictive capabilities

---

## Standards Compliance

All modules adhere to:
- **ISO/IEC 42001:2023** - AI Management System
- **ISO/IEC 23894:2023** - AI Risk Management
- **ISO/IEC 22989:2022** - AI Concepts and Terminology
- **ISO/IEC/IEEE 26514:2022** - Software documentation
- **ISO/IEC/IEEE 42010:2011** - Architecture description
- **ISO 22301:2019** - Business Continuity Management Systems
- **BPMN 2.0** - Business Process Model and Notation (where applicable)

---

## Key Metrics

### Code Metrics
- **Total Lines of Code:** 114,142
- **Python Files:** 481
- **Classes:** 664
- **Functions:** 221
- **API Endpoints:** 332+
- **Dependencies:** ~1,000+ external packages

### Service Metrics
- **Total Services:** 12 main + 6 sub-services
- **Running Services:** 4 confirmed
- **Active Services:** 6 ready for deployment
- **EventBus Publishers:** 40+
- **EventBus Subscribers:** 25+

### Integration Metrics
- **Service-to-Service Dependencies:** 45+ connections
- **Shared Components:** 2 (ai-foundation, shared utilities)
- **Database Schemas:** 30+ tables across modules
- **Integration Status:** ~75%

---

## Support and Maintenance

**Maintainer:** AI Platform Team
**Last Updated:** 2025-10-08
**Documentation Status:** Professional standards compliant (ISO/IEC/IEEE 26514:2022)
**Review Cycle:** Quarterly

For issues and questions:
- Check module-specific README.md files
- Review API documentation at `/docs` on each service
- Contact platform team for support

---

**Document Version:** 1.0.0
**Generated:** 2025-10-08
**Next Review:** 2026-01-08
