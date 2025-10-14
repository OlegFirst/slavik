# Migration Strategy - Old → New Architecture

**Date:** 2025-10-02
**Goal:** Migrate and improve existing INTELLIGENCE + PLATFORM services into new AI-First architecture

---

## 📊 Current State Analysis

### OLD INTELLIGENCE Platform
**Location:** `/Users/MD/ISO-22301—копия/services/SERVICES/INTELLIGENCE/`

**Services:**
1. **AI Intelligence (8032)** - 10 AI Organs
   - Governance Brain, Emergency Response, Impact Oracle, Scenario Creator
   - Risk Advisor, Compliance Guardian, Performance Analyst, Learning Coach
   - Plan Generator, Lifecycle Monitor

2. **Project Intelligence** - Unified workflows
   - BCM workflow orchestration
   - Integration with Digital Twin

3. **AI-All/orchestrator_обьединенный** - Unified orchestrator
   - Consolidation of 8 scattered orchestrators
   - Platform, AI, Scenario orchestrators
   - Master controller

### OLD PLATFORM Services
**Location:** `/Users/MD/ISO-22301—копия/services/SERVICES/PLATFORM/`

**Services:**
1. **Orchestration (8002)** - AI-powered orchestration
   - Multi-model AI routing (GPT-4, Claude)
   - Risk analysis, incident classification
   - NLP queries, BIA automation

2. **Coordination (8003)** - BPMN workflow engine
   - Workflow orchestration (BIA, Risk, Incident, Plan approval)
   - State management, parallel execution
   - Error handling, compensation logic

3. **EventBus (8001)** - Event system
   - Redis pub/sub + HTTP webhooks
   - Event persistence, replay capability

### NEW AI-Platform Architecture
**Location:** `/Users/MD/AI-Platform-ISO/`

**Services:**
1. **Coordination Center (8004)** ✅ - NEW посредник
   - Intent parser, Command translator
   - Tool Registry, Execution Tracker
   - Security Layer (permissions, rate limiting, audit)

2. **Intelligent Gateway** (pending) - AI-powered routing
3. **3-level Database** - System/Platform/Business

---

## 🎯 Migration Strategy

### Принципы:
1. **NO direct migration** - не копируем код 1:1
2. **Extract & Improve** - берем лучшее, улучшаем
3. **Consolidate** - объединяем дублирующиеся функции
4. **AI-First** - все через Coordination Center

### Phase 2.5: Consolidation (текущая фаза)

#### Step 1: Unified AI Orchestration Module ✅
**Объединить:**
- `AI-All/orchestrator_обьединенный` (unified orchestrator)
- `PLATFORM/orchestration` (AI-powered orchestration)
- `project-intelligence` (unified workflows)

**Создать:**
`/Users/MD/AI-Platform-ISO/infrastructure/intelligent-orchestration/`

**Функции:**
- Multi-model AI routing (GPT-4, Claude, Llama)
- Rule-based automation (event → action)
- Intelligence engine (BCM business logic)
- DevOps engine (AI-powered deployment)
- Decision tracking with approval

**Integration:**
- Coordination Center → Intelligent Orchestration → AI models
- EventBus integration для pub/sub

---

#### Step 2: AI Organs Integration ✅
**Взять из:**
- `ai-intelligence/organs/` (10 AI organs)

**Интегрировать в:**
- Coordination Center Tool Registry как AI tools

**Новая структура:**
```python
# Tool Registry добавить AI Organs
organs_tools = [
    ToolDefinition(
        tool_id="governance_brain",
        name="Governance Brain",
        category=ToolCategory.AI_ORGAN,
        base_url="http://localhost:8032",
        supported_actions=["analyze_governance", "policy_guidance"],
        endpoints={
            "analyze_governance": "/api/ai/organs/governance-brain"
        }
    ),
    # ... 9 other organs
]
```

**AI может вызывать органы:**
```
AI Intent: "Analyze governance for hospital_001"
  ↓
Coordination Center: Parse intent → Find Governance Brain organ
  ↓
Tool Registry: governance_brain tool
  ↓
Execute: POST http://localhost:8032/api/ai/organs/governance-brain
  ↓
Result: Governance analysis + recommendations
```

---

#### Step 3: BPMN Workflow Migration ✅
**Взять из:**
- `PLATFORM/coordination` (BPMN engine)

**Создать:**
`/Users/MD/AI-Platform-ISO/infrastructure/workflow-engine/`

**Функции:**
- BPMN process execution (SpiffWorkflow or Camunda)
- State management (FSM)
- Parallel task execution
- Error handling + retry
- Compensation logic (rollback)

**Integration:**
- Coordination Center → Workflow Engine → Execute BPMN
- Workflows хранятся в Platform DB
- EventBus публикует workflow events

**Workflows:**
- BIA Analysis Workflow
- Risk Assessment Workflow
- Incident Response Workflow
- Plan Approval Workflow
- Exercise Workflow

---

#### Step 4: EventBus Consolidation ✅
**Взять из:**
- `PLATFORM/eventbus` (Redis + HTTP)

**Улучшить:**
1. **Event Types:**
   - `coordination.execution.started`
   - `coordination.execution.completed`
   - `workflow.step.completed`
   - `ai.decision.pending_approval`
   - `ai.organ.analysis.completed`

2. **Event Persistence:**
   - Store in Platform DB (`events` schema)
   - Event replay capability
   - Event sourcing support

3. **Subscriptions:**
   - Services subscribe to event types
   - WebSocket для real-time updates
   - SSE (Server-Sent Events) для UI

---

## 📦 New Architecture Structure

```
/Users/MD/AI-Platform-ISO/infrastructure/

├── coordination-center/           ✅ (Phase 2 Complete)
│   ├── Intent parser
│   ├── Command translator
│   ├── Tool Registry
│   ├── Execution Tracker
│   └── Security Layer
│
├── intelligent-orchestration/     🔄 (Phase 2.5 - NEW)
│   ├── ai_router.py              # Multi-model routing
│   ├── rule_engine.py            # Event → Action rules
│   ├── intelligence_engine.py    # BCM business logic
│   ├── devops_engine.py          # AI deployment
│   └── decision_tracker.py       # Track AI decisions
│
├── ai-organs/                     🔄 (Phase 2.5 - NEW)
│   ├── base_organ.py
│   ├── governance_brain.py
│   ├── emergency_response.py
│   ├── impact_oracle.py
│   ├── scenario_creator.py
│   ├── risk_advisor.py
│   ├── compliance_guardian.py
│   ├── performance_analyst.py
│   ├── learning_coach.py
│   ├── plan_generator.py
│   └── lifecycle_monitor.py
│
├── workflow-engine/               🔄 (Phase 2.5 - NEW)
│   ├── bpmn_executor.py          # BPMN process execution
│   ├── state_manager.py          # FSM
│   ├── workflows/
│   │   ├── bia_workflow.bpmn
│   │   ├── risk_workflow.bpmn
│   │   └── incident_workflow.bpmn
│   └── compensation.py           # Rollback logic
│
├── event-system/                  🔄 (Phase 2.5 - NEW)
│   ├── eventbus.py               # Redis pub/sub
│   ├── event_persistence.py      # DB storage
│   ├── event_replay.py           # Replay capability
│   └── subscriptions.py          # Subscription management
│
└── intelligent-gateway/           ⏸️ (Phase 3)
    └── AI-powered routing
```

---

## 🔄 Integration Flow

### OLD Flow (разрозненно):
```
User Request → Gateway (8000) → Orchestration (8002) → BCM Service
                              → Coordination (8003) → BPMN → BCM Service
                              → AI Intelligence (8032) → AI Organ
```

### NEW Flow (unified):
```
User/AI Request
  ↓
Intelligent Gateway (Phase 3)
  ↓
Coordination Center (8004) - посредник
  ↓
  ├─→ Intelligent Orchestration → AI Router → GPT-4/Claude
  ├─→ AI Organs → Governance Brain, Impact Oracle, etc.
  ├─→ Workflow Engine → BPMN Executor → BCM Services
  └─→ Event System → Publish events → Subscribers
```

**Преимущества:**
1. ✅ Единая точка входа (Coordination Center)
2. ✅ AI Intent-based API (не нужно знать endpoints)
3. ✅ Audit trail для всех действий
4. ✅ Security layer (permissions, rate limiting)
5. ✅ Rollback capability
6. ✅ Human-in-the-loop для критичных операций

---

## 🚀 Implementation Plan

### Phase 2.5 Tasks:

#### Task 1: Intelligent Orchestration (4-6 hours)
- [ ] Create `/infrastructure/intelligent-orchestration/`
- [ ] AI Router (GPT-4, Claude, Llama)
- [ ] Rule Engine (event → action mapping)
- [ ] Intelligence Engine (BCM logic)
- [ ] Decision Tracker
- [ ] Integration with Coordination Center

#### Task 2: AI Organs Integration (3-4 hours)
- [ ] Copy 10 organs from `ai-intelligence/organs/`
- [ ] Create `/infrastructure/ai-organs/`
- [ ] Register organs in Tool Registry
- [ ] Update Command Interpreter для AI organ intents
- [ ] Test: AI creates intent → Coordination → Organ execution

#### Task 3: Workflow Engine (5-6 hours)
- [ ] Create `/infrastructure/workflow-engine/`
- [ ] BPMN executor (SpiffWorkflow)
- [ ] Migrate 5 workflows (BIA, Risk, Incident, Plan, Exercise)
- [ ] State management (FSM)
- [ ] Compensation logic
- [ ] Integration with Coordination Center

#### Task 4: Event System (3-4 hours)
- [ ] Create `/infrastructure/event-system/`
- [ ] Redis pub/sub client
- [ ] Event persistence (Platform DB)
- [ ] Event replay capability
- [ ] WebSocket support для real-time
- [ ] Integration with all modules

#### Task 5: Integration Testing (2-3 hours)
- [ ] E2E test: AI intent → Coordination → Orchestration → AI model
- [ ] E2E test: AI intent → Coordination → AI Organ → Analysis
- [ ] E2E test: Workflow execution → BPMN → BCM services
- [ ] E2E test: Event publishing → Subscribers receive

**Total Time:** 17-23 hours (3-4 days)

---

## 📊 Success Metrics

✅ **Phase 2.5 Complete when:**
- Coordination Center интегрирован с Intelligent Orchestration
- 10 AI Organs доступны через Tool Registry
- BPMN Workflow Engine работает
- Event System публикует события
- E2E тесты проходят
- Старые сервисы можно выключить (не нужны)

---

## 🎯 Next Steps (After Phase 2.5)

### Phase 3: Intelligent Gateway
- Request Analyzer (ML predictions)
- Smart Router (service discovery)
- Intelligent Load Balancer
- Circuit Breaker
- Smart Cache (AI-powered TTL)

### Phase 4: First Services
- Participants Service
- BIA Service v2
- Integration с Business DB

---

**Current Focus:** Phase 2.5 - Consolidation & Migration
**Goal:** Unified AI-First architecture с лучшими наработками из старой платформы

---

**Партнер, начинаем Phase 2.5?** 🚀

Предлагаю начать с Task 1 (Intelligent Orchestration), так как это ключевой компонент для AI routing.
