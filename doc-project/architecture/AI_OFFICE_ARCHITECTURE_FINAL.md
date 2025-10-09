# AI Office Architecture - Final Design Based on Business Logic

**Created:** 2025-10-05
**Source:**
- Analysis of existing AI Office components ([AI_OFFICE_INVENTORY_ANALYSIS.md](AI_OFFICE_INVENTORY_ANALYSIS.md))
- Business logic from previous Claude ([AI_OFFICE_BUSINESS_LOGIC.md](AI_OFFICE_BUSINESS_LOGIC.md))
- Workflow Intelligence Engine design from [ком.md](ком.md)

**Purpose:** Define FINAL architecture for AI Office based on actual business requirements

---

## 🎯 Executive Summary

Previous Claude designed **Workflow Intelligence Engine** as the cornerstone of the AI platform. This engine provides:
- **State Machine** - prevents invalid operations
- **Case Library** - learns from all workflow journeys
- **Governance System** - managed autonomy (Constitution + Checkpoints + Creative Zones)
- **AI Context Builder** - prevents hallucination by providing rich context

All components integrate through this engine according to their roles:
- **Services** use Workflow Engine for state management
- **AI Advisors** (Colleagues) use Case Library for pattern-based advice
- **AI Workers** (Organs) get Workflow Context to avoid hallucination
- **EventBus** connects everything for event-driven learning

---

## 🏗️ Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: User Interface                                     │
│ - Frontend (Next.js)                                        │
│ - Colleague Coordinator (routes to right advisor)          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: AI Advisors (Colleagues)                          │
│ - BIA Specialist                                            │
│ - Risk Analyst                                              │
│ - Compliance Copilot                                        │
│ - Project Manager                                           │
│ - Plan Strategy AI                                          │
│ - Incident Advisor                                          │
│ - Exercise Designer                                         │
│                                                             │
│ Integration: AI Context Builder                             │
│   ├→ Workflow State (current stage, data, errors)          │
│   ├→ Case Library (similar successful workflows)           │
│   ├→ Benchmarks (industry statistics)                       │
│   └→ Knowledge Graph (ISO standards)                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Intelligence Infrastructure                        │
│ - RAG Pipeline (semantic search)                            │
│ - Intent Analyzer (understand user needs)                   │
│ - Learning System (pattern extraction)                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 0: Workflow Intelligence Engine (CORNERSTONE)         │
│                                                             │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ Core Components:                                     │   │
│ │ - State Machine (prevents invalid transitions)      │   │
│ │ - Rules Engine (Constitution → Mandatory → Best)    │   │
│ │ - Checkpoints (strict validation points)            │   │
│ │ - Creative Zones (where AI is free)                 │   │
│ │ - AI Context Builder (prevents hallucination)       │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                             │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ Case Library (Self-Learning):                       │   │
│ │ - Case Collector (captures all workflow events)     │   │
│ │ - Case Repository (semantic search for patterns)    │   │
│ │ - Benchmarking (industry statistics)                │   │
│ │ - Trending Analysis (recent successful patterns)    │   │
│ └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Services & Workers                                          │
│                                                             │
│ Services (State Management):                                │
│ - BIA Service → BIAWorkflowAdapter                         │
│ - Risk Service → RiskWorkflowAdapter                       │
│ - Planning Service → PlanningWorkflowAdapter               │
│ - Response Service → ResponseWorkflowAdapter               │
│ - etc.                                                      │
│                                                             │
│ AI Workers (Organs - Execute with Context):                │
│ - Process Analyzer                                          │
│ - Risk Assessor                                             │
│ - Impact Calculator                                         │
│ - RTO Recommender                                           │
│ - Plan Document Generator                                   │
│ - etc.                                                      │
│                                                             │
│ Integration: Workflow Context API                           │
│   workflow.get_context() returns:                           │
│   - current_state                                           │
│   - available_actions                                       │
│   - validation_errors                                       │
│   - completed_actions                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Infrastructure                                              │
│ - EventBus (Redis) - nervous system                        │
│ - PostgreSQL (state, cases, data)                          │
│ - Vector DB (semantic search)                              │
│ - Cache (Redis)                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Integration Patterns

### Pattern 1: Service Executes Workflow

```python
# User starts BIA
User → BIA Service

# BIA Service uses Workflow Engine
bia_service = BIAService(db, eventbus)
workflow = await bia_service.start_bia(org_id="org_123")

# Workflow Engine:
# 1. Creates state machine for BIA
# 2. Sets initial state = 'identify_processes'
# 3. Emits event: bia.workflow.started
# 4. Returns context to service

# User adds process
await bia_service.add_process({
    'name': 'Patient Registration',
    'tier': 'tier_1'
})

# Workflow Engine:
# 1. Validates: are we in correct stage? ✅
# 2. Validates: required fields present? ✅
# 3. Validates: meets rules? ✅
# 4. Updates state data
# 5. Emits event: bia.process.added
# 6. Case Collector captures for learning

# Workflow Engine prevents invalid operations
await bia_service.set_rto(...)  # ❌ Wrong stage, blocked
```

### Pattern 2: AI Advisor Provides Guidance

```python
# User asks for help
User → Colleague Coordinator → BIA Specialist

# BIA Specialist gets rich context
context_builder = AIContextBuilder(workflow, case_repo)
context = await context_builder.build_full_context(
    org_context={'industry': 'healthcare', 'size': 'medium'}
)

# Context includes:
{
    'workflow': {
        'current_state': 'identify_processes',
        'data': {'processes': [...]},
        'validation_errors': [],
        'progress': 25.0
    },
    'similar_cases': [
        # 3 successful healthcare BIAs
        {
            'industry': 'healthcare',
            'duration_days': 21,
            'success_patterns': [
                'Started with Emergency Dept',
                'Used FMEA for impact analysis'
            ]
        }
    ],
    'benchmarks': {
        'avg_duration': 23.5,
        'top_patterns': [...]
    }
}

# BIA Specialist sends to LLM with RICH context
response = await llm.generate(
    context_builder.format_for_llm_prompt(context)
)

# Response is context-aware, not hallucinated:
"Organizations like yours (healthcare, medium) typically start BIA
by identifying Emergency Department first (seen in 87% of similar cases).
Based on successful patterns, I recommend..."
```

### Pattern 3: AI Worker Executes Safely

```python
# Service needs AI analysis
BIA Service → Process Analyzer (Organ)

# Organ MUST get workflow context first
workflow = workflow_engine.get_workflow('bia_123')
context = workflow.get_context()

# Context tells organ:
{
    'workflow_id': 'bia_123',
    'current_state': 'identify_processes',
    'data': {'processes': [...]},
    'validation_errors': [],
    'available_actions': ['add_process', 'transition_to_dependencies']
}

# Organ validates it's allowed to run
if context['current_state'] != 'identify_processes':
    raise Error("Cannot analyze processes in stage: " + context['current_state'])

# Safe to execute - has full context, won't hallucinate
result = await organ.analyze_critical_processes(context)

# Returns result to service
# Service uses result in workflow
```

### Pattern 4: EventBus Learning Loop

```python
# Every workflow action emits events
Workflow Engine → EventBus

# Case Collector subscribes to ALL workflow events
Case Collector ← EventBus

# Events collected:
- bia.workflow.started (metadata: org context)
- bia.stage.changed (from: X, to: Y)
- bia.process.added (data: process details)
- bia.challenge.encountered (what went wrong)
- bia.challenge.resolved (how fixed)
- bia.ai.intervention (AI advice given, accepted?)
- bia.checkpoint.passed (validation success)
- bia.workflow.completed (final result)

# When workflow completes:
# Case Collector compiles journey
journey = [
    {stage: 'identify_processes', duration: 8h, actions: 5, challenges: 1},
    {stage: 'analyze_dependencies', duration: 12h, actions: 8},
    ...
]

# AI extracts patterns
patterns = await ai.extract_patterns(journey, metrics)
# "✓ Starting with Emergency Dept reduced time by 30%"
# "✓ Using FMEA framework improved impact accuracy"

# Saves to Case Library
case_library.save_case({
    'org_context': {'industry': 'healthcare', 'size': 'medium'},
    'journey': journey,
    'success_patterns': patterns,
    'metrics': {'duration': 21 days, 'ai_usage': 15}
})

# FUTURE workflows benefit
# AI Advisors can now say: "Similar orgs did X and succeeded"
```

---

## 📊 Component Roles (Final Classification)

### AI Advisors (Colleagues) - 7 Components

**Role:** Provide intelligent, context-aware advice using patterns and benchmarks

| Component | Domain | Status | Integration |
|-----------|--------|--------|-------------|
| BIA Specialist | BIA processes | ✅ Production | AI Context Builder → Case Library |
| Risk Analyst | Risk assessment | ✅ Production | AI Context Builder → Case Library |
| Compliance Copilot | ISO compliance | ✅ Production | AI Context Builder → Knowledge Graph |
| Project Manager | BCM projects | ✅ Production | AI Context Builder → Project Intelligence Service |
| Plan Strategy AI | Planning | ⚠️ Minimal | Needs Case Library integration |
| Incident Advisor | Incident response | ⚠️ Minimal | Needs Case Library integration |
| Exercise Designer | Exercises | ⚠️ Minimal | Needs Case Library integration |

**Common Pattern:**
```python
class BaseAIColleague:
    def __init__(self, rag_pipeline):
        self.rag = rag_pipeline
        self.context_builder = AIContextBuilder()

    async def process_message(self, user_message, context, tenant_id):
        # 1. Build rich context from Case Library + Workflow
        full_context = await self.context_builder.build_full_context(...)

        # 2. Format for LLM
        prompt = self.context_builder.format_for_llm_prompt(full_context)

        # 3. Get advice from LLM
        response = await self.llm.generate(prompt)

        return response
```

### AI Workers (Organs) - 10 Components

**Role:** Execute domain logic with workflow context to avoid hallucination

| Organ | Purpose | Used By Service | Needs Context From |
|-------|---------|-----------------|-------------------|
| Process Analyzer | Identify critical processes | BIA Service | BIA Workflow |
| Impact Calculator | Calculate financial impact | BIA Service | BIA Workflow |
| RTO Recommender | Recommend RTO/RPO | BIA Service | BIA Workflow |
| Risk Assessor | Assess risk levels | Risk Service | Risk Workflow |
| Threat Identifier | Identify threats | Risk Service | Risk Workflow |
| Plan Document Generator | Generate plan docs | Planning Service | Planning Workflow |
| Strategy Recommender | Recommend BC strategies | Planning Service | Planning Workflow + BIA Results |
| Exercise Scenario Builder | Create exercise scenarios | Validation Service | Exercise Workflow |
| Compliance Checker | Check ISO compliance | Governance Service | All Workflows |
| Timeline Estimator | Predict completion dates | All Services | Any Workflow |

**Common Pattern:**
```python
class BaseOrgan:
    async def execute(self, workflow_id, **params):
        # 1. MUST get workflow context first
        workflow = workflow_engine.get_workflow(workflow_id)
        context = workflow.get_context()

        # 2. Validate allowed to run in current stage
        if not self._can_execute(context['current_state']):
            raise Error(f"Cannot run in stage: {context['current_state']}")

        # 3. Execute with full context (prevents hallucination)
        result = await self._execute_with_context(context, **params)

        return result

    def _can_execute(self, stage):
        # Define which stages this organ can run in
        return stage in self.allowed_stages
```

### Support Components

| Component | Role | Integration |
|-----------|------|-------------|
| RAG Pipeline | Semantic search | Used by all Colleagues |
| Intent Analyzer | Understand user intent | Used by Coordinator |
| Colleague Coordinator | Route to right advisor | Uses Intent Analyzer |
| Learning System | Extract patterns | Part of Case Library |
| MIO Manager | ❓ TBD | Need to analyze role |

---

## 🎯 Governance: Managed Autonomy

### Constitution (Unchangeable Principles)

**BIA Constitution:**
1. Never recommend RTO < 1h without explicit justification
2. Always validate financial impact with quantitative data
3. Mandatory dependency mapping for Tier 1-2 processes

**Forbidden Actions:**
- Modify user data without permission
- Create processes without user confirmation
- Override regulatory requirements
- Bypass mandatory checkpoints
- Delete audit trail

### Creative Zones (Where AI Can Innovate)

**4 Creativity Levels:**

1. **NONE** - Strictly deterministic (checkpoints)
2. **LOW** - Stay close to established patterns
3. **MEDIUM** - Balance innovation with proven approaches
4. **HIGH** - Explore novel approaches, multiple perspectives

**Example: BIA Impact Assessment (HIGH Creativity)**
```yaml
creative_zone:
  stage: assess_impact
  creativity_level: high

  allowed_approaches:
    - Multiple frameworks (quantitative + qualitative)
    - Scenario analysis
    - Cascading impact modeling
    - Analogies from similar industries

  forbidden:
    - Invent financial data
    - Override user-provided data
    - Make definitive claims without evidence

  guidance: |
    You have HIGH creative freedom:
    - Use multiple frameworks (FMEA, scenario-based)
    - Consider direct AND indirect impacts
    - Use case studies: "Hospital X lost $2M when similar process failed"

    BUT distinguish:
    - Data-driven conclusions (when you have data)
    - Educated estimates (when inferring)
    - Hypothetical scenarios (when exploring)
```

### Checkpoints (Strict Validation)

**BIA Checkpoints:**
1. **bia_cp_001** - Process Identification Complete
   - Rules: min 3 processes, at least 1 Tier 1, owners documented
   - Can skip: ❌ No
   - Escalation: ❌ No

2. **bia_cp_002** - Dependencies Mapped
   - Rules: Tier 1 needs min 2 deps (people + technology)
   - Can skip: ❌ No
   - Escalation: ✅ Yes (for Tier 1 violations)

3. **bia_cp_003** - Impact Assessment Complete
   - Rules: financial impact exists, all impact types assessed
   - Can skip: ❌ No
   - Escalation: ❌ No

4. **bia_cp_004** - RTO Determination Valid
   - Rules: no RTO <1h without justification, rationale required
   - Can skip: ❌ No
   - Escalation: ✅ Yes (for RTO violations)

5. **bia_cp_005** - Final BIA Validation
   - Rules: ALL constitution + mandatory rules
   - Can skip: ❌ No
   - Escalation: ✅ Yes (final review)

**Checkpoint Logic:**
```python
async def validate_checkpoint(checkpoint_id, context):
    # Run all rules for this checkpoint
    violations = []
    for rule_id in checkpoint.rules:
        is_valid, message = rule.validate(context)
        if not is_valid:
            violations.append(violation)

    # Check if can proceed
    critical_violations = [v for v in violations if v.severity in [CRITICAL, HIGH]]
    can_proceed = len(critical_violations) == 0

    # Escalate if needed
    if checkpoint.escalation_required and len(violations) > 0:
        await escalate_to_human(violations)

    return can_proceed, violations, next_steps
```

---

## 🔧 Implementation Roadmap

### Phase 1: Foundation (Workflow Intelligence Engine)

**Status:** Design complete in ком.md, NOT implemented

**Components to Build:**
1. State Machine Engine
   - State definitions
   - Transition validation
   - Progress tracking
   - Event emission

2. Rules Engine
   - Rule registration
   - Validation execution
   - Violation reporting
   - Escalation logic

3. Checkpoints & Creative Zones
   - Checkpoint manager
   - Creative zone configs
   - Stage mode detection

4. Case Library
   - Case Collector (subscribe to EventBus)
   - Case Repository (storage + search)
   - Benchmarking (statistics)
   - Pattern extraction (AI-powered)

5. AI Context Builder
   - Context aggregation from multiple sources
   - LLM prompt formatting
   - Rich context delivery

**Priority:** 🔴 CRITICAL - This is the cornerstone, everything depends on it

---

### Phase 2: Integrate Services

**Status:** Services exist, but NOT integrated with Workflow Engine

**Tasks:**
1. Create Workflow Adapters
   - BIAWorkflowAdapter
   - RiskWorkflowAdapter
   - PlanningWorkflowAdapter
   - ResponseWorkflowAdapter

2. Migrate Services to use Adapters
   - Replace direct DB calls with workflow.add_process()
   - Use workflow.transition_to() instead of manual state changes
   - Emit events through workflow engine

3. Define YAML Workflow Definitions
   - BIA process (6 stages)
   - Risk assessment (5 stages)
   - Planning (3 stages)
   - Response (varies)

**Priority:** 🟠 HIGH - Required for state management

---

### Phase 3: Integrate AI Advisors (Colleagues)

**Status:** 4/7 production-ready, but NOT using Case Library

**Tasks:**
1. Implement AI Context Builder
   - Query Case Library for similar workflows
   - Get benchmarks for industry
   - Fetch trending patterns
   - Format rich prompt

2. Update Existing Colleagues
   - BIA Specialist → use AI Context Builder
   - Risk Analyst → use AI Context Builder
   - Compliance Copilot → use AI Context Builder
   - Project Manager → integrate with Project Intelligence Service

3. Complete Minimal Colleagues
   - Plan Strategy AI → full implementation
   - Incident Advisor → full implementation
   - Exercise Designer → full implementation

**Priority:** 🟡 MEDIUM - Improves advice quality

---

### Phase 4: Integrate AI Workers (Organs)

**Status:** All 10 organs present, but integration pattern UNDEFINED

**Tasks:**
1. Define Workflow Context API
   ```python
   workflow.get_context() → {
       'workflow_id': str,
       'current_state': str,
       'data': dict,
       'validation_errors': list,
       'available_actions': list,
       'progress': float
   }
   ```

2. Update Each Organ
   - Add workflow context validation
   - Define allowed_stages for each organ
   - Implement _execute_with_context()

3. Service Integration
   - BIA Service → uses Process Analyzer, Impact Calculator, RTO Recommender
   - Risk Service → uses Risk Assessor, Threat Identifier
   - Planning Service → uses Plan Generator, Strategy Recommender

**Priority:** 🟡 MEDIUM - Prevents hallucination

---

### Phase 5: EventBus & Learning Loop

**Status:** Mentioned everywhere, NOT implemented

**Tasks:**
1. Implement EventBus (Redis backend)
   - Publish API
   - Subscribe API
   - Topic patterns (bia.*, risk.*, etc.)

2. Integrate with Workflow Engine
   - Emit events on all state changes
   - Emit events on validations
   - Emit events on AI interventions

3. Implement Case Collector
   - Subscribe to *.workflow.* events
   - Compile journey on completion
   - Extract patterns using AI
   - Save to Case Library

4. Learning Loop Verification
   - First workflow creates no cases
   - Second workflow learns from first
   - Benchmarks improve over time

**Priority:** 🟢 LOW - But critical for self-learning

---

## 🚧 Known Issues to Resolve

### Issue 1: Plan Generator Duplicate

**Problem:** Exists as both Colleague (53 lines) and Organ (310 lines)

**Analysis:**
- Colleague version: Minimal, probably skeleton
- Organ version: Full implementation

**Proposed Solution:**
- **Rename Colleague → "Plan Strategy AI"**
  - Role: AI Advisor that RECOMMENDS strategies
  - Uses: Case Library to suggest "what worked for similar orgs"
  - Integration: AI Context Builder → LLM

- **Keep Organ → "Plan Document Generator"**
  - Role: AI Worker that GENERATES plan documents
  - Uses: Workflow Context to know what to generate
  - Called by: Planning Service

**Decision:** Need user confirmation

---

### Issue 2: MIO Manager Role Unclear

**Location:** `/intelligent-core/ai-office/mio-manager/`

**Questions:**
- What is MIO? (Management Intelligence Officer?)
- What does it manage?
- How does it integrate with architecture?

**Action:** Need to analyze MIO Manager code

---

### Issue 3: EventBus Not Implemented

**Problem:** Mentioned in every component, but code doesn't exist

**Impact:**
- Cannot emit workflow events
- Cannot collect cases for learning
- Cannot do real-time monitoring

**Solution:** Implement EventBus as Phase 5

---

### Issue 4: Project Agent Not Related to BCM

**Location:** `/intelligent-core/ai-office/project-agent/`

**Discovery:** This is a UNIVERSAL CLI tool for code analysis, supports multiple domains (fintech, healthcare, security)

**Decision:**
- NOT part of BCM AI Office
- Should be moved to separate tools directory
- OR kept as general-purpose development tool

**Action:** Need user decision on where to place it

---

## 📈 Success Metrics

### Technical Metrics

1. **State Management**
   - ✅ Invalid transitions blocked: 100%
   - ✅ Validation rules enforced: 100%
   - ✅ Checkpoint passage rate: >90%

2. **AI Quality**
   - ✅ Hallucination rate: <5%
   - ✅ Context-aware responses: >95%
   - ✅ Pattern usage in advice: >80%

3. **Learning Loop**
   - ✅ Cases collected: 100% of completed workflows
   - ✅ Pattern extraction: >50 patterns per 100 workflows
   - ✅ Benchmark accuracy: ±10% of actual

### Business Metrics

1. **User Efficiency**
   - Workflow completion time: -30% (vs manual)
   - Rework rate: <10%
   - User satisfaction: >4.0/5.0

2. **Compliance**
   - ISO 22301 compliance: 100%
   - Mandatory fields complete: 100%
   - Audit trail: 100% captured

3. **AI Adoption**
   - AI advice usage: >60% of workflows
   - AI advice acceptance: >70%
   - User trust score: >4.0/5.0

---

## 🎓 Conclusion

The architecture is CLEAR from previous Claude's design:

1. **Workflow Intelligence Engine** is the cornerstone
   - State Machine prevents errors
   - Case Library enables learning
   - Governance ensures compliance
   - AI Context prevents hallucination

2. **All components integrate through this engine:**
   - Services → use for state management
   - AI Advisors → use for pattern-based advice
   - AI Workers → use for safe execution context
   - EventBus → enables learning loop

3. **Next Steps:**
   - Phase 1: Build Workflow Intelligence Engine (CRITICAL)
   - Phase 2: Integrate Services with Adapters (HIGH)
   - Phase 3: Integrate Colleagues with AI Context Builder (MEDIUM)
   - Phase 4: Integrate Organs with Workflow Context (MEDIUM)
   - Phase 5: Implement EventBus & Learning Loop (LOW but important)

4. **Resolve Issues:**
   - Plan Generator duplicate (rename Colleague)
   - MIO Manager role (analyze code)
   - EventBus implementation (Phase 5)
   - Project Agent placement (move to tools)

**The foundation exists in code and design. Now we execute the integration plan.**
