# INTELLIGENT CORE - INTEGRATION MAP

**Version:** 2.0.0 | **Updated:** 2025-10-08

---

## 🗺️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INTELLIGENT CORE                                 │
│                    (The Brain of AI-Platform-ISO)                        │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────── LAYER 1: FOUNDATION ────────────────────────┐
│                                                                           │
│  ┌─────────────────────┐              ┌─────────────────────┐          │
│  │   ai-foundation     │◄─────────────┤     shared          │          │
│  │   (Port 8040)       │              │  (utilities)        │          │
│  │                     │              │                     │          │
│  │  • LLM Router       │              │  • Platform Client  │          │
│  │  • RAG Pipeline     │              │  • EventBus Core    │          │
│  │  • Embeddings       │              │  • Outbox Pattern   │          │
│  │  • ML Predictor     │              │                     │          │
│  └─────────────────────┘              └─────────────────────┘          │
│           │ ▲                                    │ ▲                     │
│           │ │                                    │ │                     │
│           │ │                                    │ │                     │
└───────────┼─┼────────────────────────────────────┼─┼─────────────────────┘
            │ │                                    │ │
┌───────────▼─┴────────────────────────────────────▼─┴─────────────────────┐
│              LAYER 2: INTELLIGENCE & ORCHESTRATION                        │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │            workflow_intelligence (THE BRAIN)                 │        │
│  │                    (Port 8037)                               │        │
│  │                                                              │        │
│  │  • BPMN Engine        • State Machines    • Case Library   │        │
│  │  • 7 Workflow Types   • Rules Engine      • ML Analysis    │        │
│  └───────┬──────────────────────┬──────────────────┬──────────┘        │
│          │                      │                  │                     │
│          │                      │                  │                     │
│  ┌───────▼──────┐      ┌───────▼──────┐   ┌──────▼──────────┐         │
│  │  ai_workflow │      │    event      │   │   workflow-     │         │
│  │  _optimizer  │      │ _intelligence │   │    engine       │         │
│  │  (Port 8038) │      │  (Port 8039)  │   │  (Port 8036)    │         │
│  │              │      │               │   │                 │         │
│  │ • ML Optimizer│     │ • Event       │   │ • BPMN 2.0     │         │
│  │ • Bottleneck │      │   Analysis    │   │ • Persistent   │         │
│  │ • Anomaly    │      │ • Pattern     │   │   State        │         │
│  └──────────────┘      │   Learning    │   └─────────────────┘         │
│                        │ • Auto-       │                                │
│                        │   Discovery   │                                │
│                        └───────────────┘                                │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │                ai-orchestration (Port 8030)                  │        │
│  │                    Main Decision Engine                      │        │
│  │                                                              │        │
│  │  • 4-Layer Memory    • Safety Monitor   • Self-Evolution   │        │
│  │  • Decision Center   • AI Agents        • Service Control  │        │
│  └───────┬──────────────────────────────────────────┬──────────┘        │
│          │                                          │                     │
│          │        ┌─────────────────────────┐      │                     │
│          └────────►  coordination-center    ├──────┘                     │
│                   │     (Port 8034)         │                            │
│                   │                         │                            │
│                   │  • Intent Translation   │                            │
│                   │  • Security Layer       │                            │
│                   │  • Execution Tracking   │                            │
│                   └─────────────────────────┘                            │
└───────────────────────────────────────────────────────────────────────────┘

┌────────────────── LAYER 3: DOMAIN EXPERTISE & COLLABORATION ─────────────┐
│                                                                           │
│  ┌─────────────────────┐         ┌─────────────────────┐               │
│  │  expertise-center   │         │    community_       │               │
│  │    (Port 8035)      │         │   intelligence      │               │
│  │                     │         │    (Port 8030)      │               │
│  │  • 12 Tactical      │         │                     │               │
│  │    Assistants       │◄────────┤  • Peer Review     │               │
│  │  • 10 Strategic     │         │  • Reputation       │               │
│  │    Analyzers        │         │  • Case Curation   │               │
│  └─────────────────────┘         │  • AI Synthesis     │               │
│                                   └────────┬────────────┘               │
│                                            │                             │
│                                            │                             │
│                                   ┌────────▼────────────┐               │
│                                   │    collective       │               │
│                                   │   (Port 8032)       │               │
│                                   │                     │               │
│                                   │  • Anonymous        │               │
│                                   │    Collaboration    │               │
│                                   │  • Collective       │               │
│                                   │    Agents           │               │
│                                   │  • K-Anonymity      │               │
│                                   └─────────────────────┘               │
└───────────────────────────────────────────────────────────────────────────┘

┌──────────────────────── LAYER 4: PREDICTIVE ─────────────────────────────┐
│                                                                           │
│                     ┌─────────────────────────┐                          │
│                     │      predictive         │                          │
│                     │     (Port 8031)         │                          │
│                     │                         │                          │
│                     │  • Journey Prediction   │                          │
│                     │  • Proactive Recs       │                          │
│                     │  • Daily Digests        │                          │
│                     │  • Expert Demand        │                          │
│                     └─────────────────────────┘                          │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Patterns

### Pattern 1: Workflow Execution (Full Stack)

```
┌──────────────┐
│     User     │
└──────┬───────┘
       │ 1. Create workflow request
       │
       ▼
┌──────────────────────────────┐
│    ai-orchestration          │
│      (Port 8030)             │
│  • Receives request          │
│  • Aggregates context        │
│  • Makes decision            │
│  • Assesses priority         │
└──────────────┬───────────────┘
               │ 2. Decision: Create workflow
               │    Intent: {"type": "start_bia", ...}
               │
               ▼
┌──────────────────────────────┐
│   coordination-center        │
│      (Port 8034)             │
│  • Validates intent          │
│  • Checks permissions        │
│  • Translates to API calls   │
│  • Creates execution tracker │
└──────────────┬───────────────┘
               │ 3. API Call: POST /api/v1/workflow/start
               │
               ▼
┌──────────────────────────────┐
│   workflow_intelligence      │
│       (Port 8037)            │
│  • Starts BPMN workflow      │
│  • Initializes state machine │
│  • Stores in case library    │
└──────────────┬───────────────┘
               │ 4. EventBus: workflow.bia.started
               │
      ┌────────┴────────┬─────────────────┐
      │                 │                 │
      ▼                 ▼                 ▼
┌──────────┐   ┌─────────────┐   ┌────────────┐
│ ai_      │   │ expertise-  │   │ predictive │
│ workflow_│   │ center      │   │            │
│ optimizer│   │             │   │            │
│ (8038)   │   │ (8035)      │   │ (8031)     │
│          │   │             │   │            │
│ Optimize │   │ Provide     │   │ Update     │
│ execution│   │ expert      │   │ journey    │
│          │   │ guidance    │   │ prediction │
└──────┬───┘   └──────┬──────┘   └──────┬─────┘
       │              │                 │
       │ 5. Recommendations             │
       │              │                 │
       └──────────────┴─────────────────┘
                      │
                      ▼
               ┌──────────────┐
               │ workflow_    │
               │ intelligence │
               │              │
               │ • Applies    │
               │   guidance   │
               │ • Continues  │
               │   execution  │
               └──────┬───────┘
                      │ 6. EventBus: workflow.bia.completed
                      │
      ┌───────────────┼───────────────┐
      │               │               │
      ▼               ▼               ▼
┌──────────┐   ┌─────────────┐  ┌──────────┐
│community_│   │ predictive  │  │ ai_      │
│intelli-  │   │             │  │ workflow_│
│gence     │   │ Update      │  │ optimizer│
│          │   │ predictions │  │          │
│ Sync to  │   │ Generate    │  │ Learn    │
│ case     │   │ digest      │  │ from     │
│ library  │   │             │  │ success  │
└──────────┘   └─────────────┘  └──────────┘
```

---

### Pattern 2: AI-Powered Analysis

```
┌──────────────┐
│     User     │
│  Question    │
└──────┬───────┘
       │ "Analyze this BIA process"
       │
       ▼
┌──────────────────────────────┐
│   ai-foundation              │
│      (Port 8040)             │
│  • LLM Router                │
│  • RAG Query (Qdrant)        │
│  • Retrieve context          │
└──────────────┬───────────────┘
               │ Context + embeddings
               │
               ▼
┌──────────────────────────────┐
│   expertise-center           │
│      (Port 8035)             │
│  • BIA Specialist invoked    │
│  • Uses ai-foundation base   │
│  • Applies domain knowledge  │
└──────────────┬───────────────┘
               │ Expert analysis
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
┌──────────┐   ┌─────────────┐
│ workflow_│   │ community_  │
│ intelli- │   │ intelligence│
│ gence    │   │             │
│          │   │ Search      │
│ Search   │   │ similar     │
│ case     │   │ community   │
│ library  │   │ cases       │
└──────┬───┘   └──────┬──────┘
       │              │
       └──────┬───────┘
              │ Combined insights
              │
              ▼
       ┌──────────────┐
       │     User     │
       │   Response   │
       └──────────────┘
```

---

### Pattern 3: Predictive Intelligence Flow

```
┌─────────────────────────────────────────┐
│      Platform Events                    │
│  • workflow.completed                   │
│  • milestone.achieved                   │
│  • user.activity                        │
└──────────────┬──────────────────────────┘
               │ EventBus subscriptions
               │
               ▼
┌──────────────────────────────┐
│        predictive            │
│        (Port 8031)           │
│  • Collects events           │
│  • Analyzes patterns         │
└──────────────┬───────────────┘
               │ Query for patterns
               │
      ┌────────┴────────┬─────────────────┐
      │                 │                 │
      ▼                 ▼                 ▼
┌──────────┐   ┌─────────────┐   ┌────────────┐
│workflow_ │   │ community_  │   │ collective │
│intelli-  │   │ intelligence│   │            │
│gence     │   │             │   │            │
│          │   │ Similar org │   │ Anonymous  │
│ Case     │   │ timelines   │   │ patterns   │
│ patterns │   │             │   │            │
└──────┬───┘   └──────┬──────┘   └──────┬─────┘
       │              │                 │
       └──────────────┴─────────────────┘
                      │ Aggregated data
                      │
                      ▼
               ┌──────────────┐
               │  predictive  │
               │              │
               │ • ML model   │
               │   prediction │
               │ • Generate   │
               │   proactive  │
               │   recs       │
               └──────┬───────┘
                      │ EventBus: prediction.generated
                      │
                      ▼
               ┌──────────────┐
               │notification- │
               │  service     │
               │              │
               │ Send daily   │
               │ digest       │
               └──────────────┘
```

---

### Pattern 4: Collective Intelligence (Anonymous Collaboration)

```
┌──────────────┐
│Organization A│
│  (Stuck on   │
│   BIA)       │
└──────┬───────┘
       │ No progress for 7+ days
       │
       ▼
┌──────────────────────────────┐
│       collective             │
│       (Port 8032)            │
│  • Stuck detection (score≥4) │
│  • Validation failures: 5+   │
│  • Low confidence: <0.6      │
└──────────────┬───────────────┘
               │ Find similar orgs
               │
               ▼
┌──────────────────────────────┐
│   community_intelligence     │
│       (Port 8030)            │
│  • Query case library        │
│  • Filter by industry, size  │
│  • Find 5+ successful orgs   │
└──────────────┬───────────────┘
               │ 7 organizations found
               │
               ▼
┌──────────────────────────────┐
│       collective             │
│  • Anonymize experiences     │
│    - Remove org names        │
│    - Generalize geography    │
│    - Aggregate (k=5)         │
│  • Create Collective Agent   │
│    - Expiration: 7 days      │
│    - Min risk: 0.7           │
└──────────────┬───────────────┘
               │ Agent created
               │
               ▼
┌──────────────────────────────┐
│    ai-foundation             │
│       (Port 8040)            │
│  • LLM for agent personality │
│  • Temperature: 0.3          │
│  • Max tokens: 2000          │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│     Collective Agent         │
│  "Organizations that solved  │
│   this challenge typically   │
│   started with Tier 1        │
│   suppliers. 5/7 used        │
│   dependency mapping tools." │
└──────────────┬───────────────┘
               │
               ▼
       ┌──────────────┐
       │Organization A│
       │ Gets wisdom  │
       │ (anonymous)  │
       └──────────────┘
```

---

### Pattern 5: Event Intelligence (Auto-Discovery)

```
┌─────────────────────────────────────────┐
│      ALL Platform Events                │
│  (auto-subscribed)                      │
└──────────────┬──────────────────────────┘
               │ EventBus: *.*
               │
               ▼
┌──────────────────────────────┐
│    event_intelligence        │
│       (Port 8039)            │
│  • Auto-Discovery Engine     │
│  • Pattern Learner           │
│  • Event Correlator          │
└──────────────┬───────────────┘
               │
               │ Learns patterns over time
               │
      ┌────────┴────────┬─────────────────┐
      │                 │                 │
      ▼                 ▼                 ▼
┌──────────┐   ┌─────────────┐   ┌────────────┐
│ Service  │   │   Event     │   │  Predict   │
│ Registry │   │  Patterns   │   │  Next      │
│          │   │             │   │  Event     │
│ Discover │   │ workflow.   │   │            │
│ services │   │ started     │   │ If X,      │
│ automat- │   │   ↓         │   │ then Y     │
│ ically   │   │ workflow.   │   │ likely     │
│          │   │ completed   │   │            │
└──────────┘   │ (confidence)│   └────────────┘
               │             │
               │ Store       │
               │ patterns    │
               └─────────────┘
                      │
                      │ EventBus: event.pattern_detected
                      │
                      ▼
               ┌──────────────┐
               │ ai-          │
               │ orchestration│
               │              │
               │ Use patterns │
               │ for proactive│
               │ decisions    │
               └──────────────┘
```

---

## 🔗 Service Dependency Graph

### Direct Dependencies (A → B means A depends on B)

```
Foundation Layer (No dependencies):
  • ai-foundation: None
  • shared: None

Intelligence & Orchestration Layer:
  • workflow_intelligence → ai-foundation
  • ai_workflow_optimizer → ai-foundation, workflow_intelligence, expertise-center
  • event_intelligence → ai-foundation
  • ai-orchestration → ALL services (orchestrates)
  • coordination-center → ai-orchestration, workflow_intelligence
  • workflow-engine → workflow_intelligence

Domain Expertise Layer:
  • expertise-center → ai-foundation
  • community_intelligence → ai-foundation, workflow_intelligence
  • collective → ai-foundation, community_intelligence

Predictive Layer:
  • predictive → workflow_intelligence, community_intelligence
```

### Reverse Dependencies (B is used by A)

```
• ai-foundation ← ALL (foundation for all AI capabilities)
• workflow_intelligence ← ai_workflow_optimizer, community_intelligence, predictive
• expertise-center ← ai_workflow_optimizer, orchestration
• community_intelligence ← collective, predictive
• shared ← ALL (utilities for all)
```

---

## 📡 EventBus Integration Map

### Event Publishers (40+ events)

```
ai-foundation (8040):
  ✓ ai.llm.routed
  ✓ ai.rag.queried
  ✓ ai.learning.feedback_received

workflow_intelligence (8037):
  ✓ workflow.*.started
  ✓ workflow.*.completed
  ✓ workflow.*.failed
  ✓ workflow.state_changed

ai_workflow_optimizer (8038):
  ✓ workflow.optimization.completed
  ✓ ml.model.trained

event_intelligence (8039):
  ✓ event.analyzed
  ✓ event.pattern_detected
  ✓ event.anomaly_detected

ai-orchestration (8030):
  ✓ orchestration.decision_made
  ✓ orchestration.service.*
  ✓ ai.decision.*
  ✓ (10+ events)

coordination-center (8034):
  ✓ coordination.execution.*
  ✓ coordination.approval_required

expertise-center (8035):
  ✓ expert.analysis.completed
  ✓ expert.recommendation.*

community_intelligence (8030):
  ✓ community.case.approved
  ✓ community.contribution.*
  ✓ community.review.*

collective (8032):
  ✓ collective.agent.created
  ✓ collective.org.stuck_detected

predictive (8031):
  ✓ prediction.journey.generated
  ✓ prediction.certification.estimated
  ✓ prediction.recommendation.generated
  ✓ (8+ events)
```

### Event Subscribers (25+ patterns)

```
ai-orchestration (8030):
  ✓ ALL events (*.*) for context aggregation

event_intelligence (8039):
  ✓ ALL events (*.*) for auto-discovery

coordination-center (8034):
  ✓ orchestration.decision_made
  ✓ workflow.action_required
  ✓ ai.recommendation

expertise-center (8035):
  ✓ workflow.*.started
  ✓ user.question

community_intelligence (8030):
  ✓ workflow.stuck
  ✓ user.inactive

collective (8032):
  ✓ workflow.no_progress
  ✓ validation.failure

predictive (8031):
  ✓ workflow.*.completed
  ✓ organization.milestone.achieved
  ✓ user.activity.logged
  ✓ community.case.approved
  ✓ validation.kpi.updated

ai_workflow_optimizer (8038):
  ✓ workflow.execution.completed
```

---

## 🗄️ Database Integration

### Shared Data Stores

```
PostgreSQL Databases:
┌────────────────────────────────────────┐
│  bcm_platform (main database)          │
│  ├── workflow_instances                │
│  ├── workflow_states                   │
│  ├── case_library (SHARED)             │
│  ├── contributions                     │
│  ├── peer_reviews                      │
│  ├── reputation_scores                 │
│  ├── collective_agents                 │
│  ├── predictions                       │
│  ├── process_executions                │
│  ├── ml_models                         │
│  └── ... (30+ tables)                  │
└────────────────────────────────────────┘

Redis Cache:
┌────────────────────────────────────────┐
│  redis://localhost:6379                │
│  ├── working_memory (orchestration)    │
│  ├── workflow_state_cache              │
│  ├── session_cache                     │
│  └── rate_limit_counters               │
└────────────────────────────────────────┘

Qdrant Vector DB:
┌────────────────────────────────────────┐
│  qdrant://localhost:6333               │
│  ├── knowledge_base_embeddings         │
│  ├── case_library_vectors              │
│  ├── domain_knowledge_vectors          │
│  └── (RAG pipeline storage)            │
└────────────────────────────────────────┘
```

### Case Library Sync

```
┌──────────────────────────────┐
│  community_intelligence      │
│  • Case approved by peers    │
└──────────────┬───────────────┘
               │ POST /cases/add
               │
               ▼
┌──────────────────────────────┐
│  workflow_intelligence       │
│  • Add to case library       │
│  • Index for search          │
│  • Generate embeddings       │
└──────────────┬───────────────┘
               │ Shared access
               │
      ┌────────┴────────┬─────────────────┐
      │                 │                 │
      ▼                 ▼                 ▼
┌──────────┐   ┌─────────────┐   ┌────────────┐
│ ai_      │   │ predictive  │   │ expertise- │
│ workflow_│   │             │   │ center     │
│ optimizer│   │ Pattern     │   │            │
│          │   │ matching    │   │ Domain     │
│ Learn    │   │             │   │ context    │
└──────────┘   └─────────────┘   └────────────┘
```

---

## 🔐 Security & Authorization Flow

```
┌──────────────┐
│     User     │
│   Request    │
└──────┬───────┘
       │ JWT Token
       │
       ▼
┌──────────────────────────────┐
│   API Gateway                │
│  • Validate token            │
│  • Extract user context      │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│   ai-orchestration           │
│  • Check AI permissions      │
│  • Rate limiting             │
└──────────────┬───────────────┘
               │ Intent with context
               │
               ▼
┌──────────────────────────────┐
│   coordination-center        │
│  • Security Layer            │
│  • Validate intent           │
│  • Check permissions         │
│  • Human-in-loop (if needed) │
│  • Audit log                 │
└──────────────┬───────────────┘
               │ Approved intent
               │
               ▼
┌──────────────────────────────┐
│   Target Service             │
│  (workflow_intelligence, etc)│
└──────────────────────────────┘
```

---

## 🚀 Deployment Architecture

### Local Development

```
Docker Compose:
┌────────────────────────────────────────┐
│  Infrastructure Services               │
│  ├── postgres:5432                     │
│  ├── redis:6379                        │
│  ├── rabbitmq:5672,15672               │
│  ├── qdrant:6333                       │
│  └── temporal:7233                     │
└────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────┐
│  Intelligent Core Services             │
│  ├── ai-foundation:8040                │
│  ├── workflow_intelligence:8037        │
│  ├── ai-orchestration:8030             │
│  ├── expertise-center:8035             │
│  ├── predictive:8031                   │
│  ├── collective:8032                   │
│  ├── coordination-center:8034          │
│  ├── workflow-engine:8036              │
│  ├── ai_workflow_optimizer:8038        │
│  ├── event_intelligence:8039           │
│  └── community_intelligence:8030       │
└────────────────────────────────────────┘
```

### Production (Kubernetes)

```
┌────────────────────────────────────────┐
│  Namespace: intelligent-core           │
│                                        │
│  StatefulSets:                         │
│  ├── postgres-cluster (3 replicas)    │
│  ├── redis-cluster (3 replicas)       │
│  └── qdrant-cluster (3 replicas)      │
│                                        │
│  Deployments:                          │
│  ├── ai-foundation (2 replicas)       │
│  ├── workflow-intelligence (3 reps)   │
│  ├── ai-orchestration (2 replicas)    │
│  ├── expertise-center (2 replicas)    │
│  └── ... (all services)                │
│                                        │
│  Services (ClusterIP):                 │
│  ├── ai-foundation-svc:8040           │
│  ├── workflow-intelligence-svc:8037   │
│  └── ... (all services)                │
│                                        │
│  Ingress:                              │
│  └── intelligent-core-ingress         │
│      ├── /api/v1/ai/* → ai-foundation│
│      ├── /api/v1/workflow/* → wf-int │
│      └── ... (all endpoints)          │
└────────────────────────────────────────┘
```

---

## 📊 Monitoring & Observability

### Metrics Collection

```
┌────────────────────────────────────────┐
│  All Services expose /metrics          │
│  (Prometheus format)                   │
└──────────────┬─────────────────────────┘
               │ Scrape every 15s
               │
               ▼
┌────────────────────────────────────────┐
│  Prometheus                            │
│  • Scrape configs for all services     │
│  • Store time-series data              │
│  • Alerting rules                      │
└──────────────┬─────────────────────────┘
               │ Query
               │
               ▼
┌────────────────────────────────────────┐
│  Grafana Dashboards                    │
│  ├── Intelligent Core Overview        │
│  ├── Workflow Intelligence Dashboard   │
│  ├── AI Orchestration Dashboard       │
│  ├── ML Models Performance             │
│  └── EventBus Flow Visualization       │
└────────────────────────────────────────┘
```

---

## 🔍 Troubleshooting Integration Issues

### Issue: Service Can't Connect to ai-foundation

```
Check:
1. Is ai-foundation running?
   → curl http://localhost:8040/health

2. Is the service using correct URL?
   → Check AI_FOUNDATION_URL env var
   → Should be: http://localhost:8040

3. Is network accessible?
   → ping localhost
   → telnet localhost 8040

Fix:
  • Start ai-foundation: cd ai-foundation && python main.py
  • Update env var: export AI_FOUNDATION_URL=http://localhost:8040
  • Check Docker network: docker network inspect intelligent-core
```

### Issue: EventBus Events Not Received

```
Check:
1. Is RabbitMQ running?
   → curl http://localhost:15672 (management UI)

2. Are subscriptions registered?
   → Check service startup logs for "✅ Event subscriptions configured"

3. Is RABBITMQ_URL correct?
   → Should be: amqp://user:pass@localhost:5672/

Fix:
  • Start RabbitMQ: docker-compose up -d rabbitmq
  • Check credentials in .env file
  • Verify exchange and queue creation in RabbitMQ UI
```

### Issue: Case Library Not Syncing

```
Check:
1. Is workflow_intelligence running on 8037?
   → curl http://localhost:8037/health

2. Is community_intelligence configured correctly?
   → WORKFLOW_INTELLIGENCE_URL=http://localhost:8037

3. Check sync endpoint:
   → curl http://localhost:8037/cases/add (should return 405 or 400, not 404)

Fix:
  • Update community_intelligence config.py
  • Restart community_intelligence service
  • Check logs for sync success: "📚 Case added to library"
```

---

## 📞 Integration Support

**Team:** AI Platform Team
**Updated:** 2025-10-08
**Review:** Quarterly

For integration questions:
1. Check module README: `/intelligent-core/{module}/README.md`
2. Review API docs: `http://localhost:{port}/docs`
3. Check this integration map
4. Check main catalog: `INTELLIGENT_CORE_COMPLETE_CATALOG.md`
5. Contact platform team

---

**Document Version:** 1.0.0
**Generated:** 2025-10-08
