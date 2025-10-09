# AI Office Business Logic - How Components Work Together

**Created:** 2025-10-05
**Source:** Analysis of `/Users/MD/AI-Platform-ISO/ком.md` (Previous Claude's Workflow Intelligence Engine design)
**Purpose:** Define BUSINESS LOGIC of how AI components integrate based on actual requirements, not assumptions

---

## 🎯 Critical Discovery: Architecture Pattern from Previous Claude

Previous Claude (who designed Workflow Intelligence Engine) had a CLEAR vision of how components integrate:

```
Services (BIA, Risk, Planning) → Use Workflow Engine (State Machine)
AI Advisors (Colleagues?)      → Use Case Library (Pattern Learning)
AI Workers                     → Get Context from Workflow State Machine
```

**Key Quote from ком.md line 7:**
> "AI workers будут галлюцинировать" (AI workers will hallucinate)

**Insight:** AI workers NEED context from state machine to avoid hallucination. This is why Workflow Intelligence Engine was designed as cornerstone.

---

## 📊 Business Logic Patterns Discovered

### Pattern 1: Services Use Workflow Engine

**From ком.md lines 14-16:**
```
BIA service → использует workflow engine
Risk service → использует workflow engine
AI advisors → используют case library
```

**What This Means:**
- Services (BIA, Risk, Planning, etc.) integrate with **Workflow Engine** for state management
- Workflow Engine provides:
  - State machine (prevents invalid transitions)
  - Validation rules (ensures data completeness)
  - Event emission (tracks journey for learning)
  - Context for AI (prevents hallucination)

**Integration Pattern:**
```python
# BIA Service uses Workflow Engine
from workflow_intelligence.integration import BIAWorkflowAdapter

class BIAService:
    def __init__(self, db, eventbus):
        self.workflow_adapter = BIAWorkflowAdapter(db, eventbus)

    async def start_bia(self, org_id):
        # Workflow engine manages state
        return await self.workflow_adapter.start_bia(
            bia_id=f"bia_{org_id}",
            org_context=await self.get_org_context(org_id)
        )
```

### Pattern 2: AI Advisors Use Case Library

**From ком.md line 16:**
> "AI advisors → используют case library"

**What This Means:**
- AI Advisors (likely = AI Colleagues in our architecture)
- Use **Case Library** to:
  - Find similar successful workflows
  - Get industry benchmarks
  - Learn from patterns (what worked for similar organizations)
  - Provide context-aware advice

**Integration Pattern:**
```python
# AI Advisor (Colleague) uses Case Library
from workflow_intelligence.integration import AIContextBuilder

class BIASpecialist(BaseAIColleague):
    async def analyze_bia_progress(self, bia_id, org_context):
        # Build context from Case Library
        context_builder = AIContextBuilder(
            workflow_engine=workflow,
            case_repository=case_repo
        )

        full_context = await context_builder.build_full_context(
            org_context=org_context,
            user_message="How is my BIA progressing?"
        )

        # full_context contains:
        # - Current workflow state
        # - Similar successful cases
        # - Industry benchmarks
        # - Trending patterns

        # Send to LLM with rich context
        return await self.process_with_llm(full_context)
```

### Pattern 3: AI Workers Get Context from State Machine

**From ком.md lines 7, 387:**
> "AI workers будут галлюцинировать" (without context)
> "Получить полный контекст для AI Advisor" from workflow state

**What This Means:**
- AI Workers (likely = AI Organs in our architecture)
- Get **Context from Workflow State Machine** to avoid hallucination
- State machine provides:
  - Current state (where are we in the process?)
  - Available actions (what can be done now?)
  - Validation errors (what's missing?)
  - Completed actions (what's already done?)

**Integration Pattern:**
```python
# AI Worker (Organ) gets context from Workflow
class ProcessAnalyzer(BaseOrgan):
    async def analyze_process(self, bia_id):
        # Get workflow context
        workflow = workflow_engine.get_workflow(bia_id)
        context = workflow.get_context()

        # context contains:
        # {
        #   'workflow_id': 'bia_123',
        #   'current_state': 'identify_processes',
        #   'data': {...},
        #   'validation_errors': [...],
        #   'available_actions': [...],
        #   'progress': 25.0
        # }

        # Use context to avoid hallucination
        if context['current_state'] != 'identify_processes':
            raise ValueError("Wrong stage for process analysis")

        # Safe to execute within known boundaries
        return await self._analyze_with_context(context)
```

---

## 🏗️ Architecture Layers (Based on Business Logic)

### Layer 0: Workflow Intelligence Engine (Foundation)
**Role:** State management, validation, event emission, learning
**Components:**
- State Machine (core)
- Case Library (learning)
- Rules Engine (governance)
- AI Context Builder (context provider)

**Who Uses It:**
- ✅ All Services (BIA, Risk, Planning, Response, etc.)
- ✅ AI Advisors (for Case Library)
- ✅ AI Workers (for Context)

### Layer 1: Services & Workers
**Role:** Execute domain logic with workflow context
**Components:**
- Services: BIA Service, Risk Service, Planning Service, etc.
- AI Workers (Organs): Process Analyzer, Risk Assessor, Plan Generator, etc.

**Integration:**
- Services → Workflow Engine (state management)
- AI Workers → Workflow Engine (get context to avoid hallucination)

### Layer 2: AI Advisors (Colleagues)
**Role:** Provide intelligent advice using patterns and benchmarks
**Components:**
- BIA Specialist
- Risk Analyst
- Compliance Copilot
- Project Manager
- etc.

**Integration:**
- AI Advisors → Case Library (learn from patterns)
- AI Advisors → Workflow Engine (get current state)
- AI Advisors → RAG Pipeline (semantic search)

### Layer 3: Coordination
**Role:** Route requests to right advisor
**Components:**
- Colleague Coordinator

**Integration:**
- Coordinator → Intent Analyzer
- Coordinator → AI Advisors (delegates)

---

## 🔄 Integration Patterns Summary

### Pattern A: Service ↔ Workflow Engine
```
User Request
    ↓
Service (BIA/Risk/Planning)
    ↓
Workflow Engine (manages state, validates, emits events)
    ↓
Database (persists state)
    ↓
EventBus (publishes events)
    ↓
Case Collector (learns from journey)
```

### Pattern B: AI Advisor ↔ Case Library
```
User Question
    ↓
AI Advisor (Colleague)
    ↓
AI Context Builder
    ├→ Workflow Engine (current state)
    ├→ Case Repository (similar cases)
    └→ Benchmarks (industry stats)
    ↓
LLM (Claude/GPT) with rich context
    ↓
Advice with specific examples
```

### Pattern C: AI Worker ↔ Workflow Context
```
Service needs AI work
    ↓
AI Worker (Organ)
    ↓
Workflow Engine (get context)
    ↓
Validate: am I allowed to run now?
    ↓
Execute within safe boundaries
    ↓
Return result
```

---

## 🚫 What AI Organs Are NOT

Based on business logic, AI Organs are **NOT**:
- ❌ Standalone tools used randomly
- ❌ Independent services called via HTTP
- ❌ Free-form AI that can hallucinate

**They ARE:**
- ✅ Context-aware workers
- ✅ Execute within workflow boundaries
- ✅ Get state from Workflow Engine to avoid hallucination
- ✅ Safe executors within defined stages

---

## 📋 Concrete Example: BIA Workflow Journey

### Step 1: User Starts BIA
```python
# User → BIA Service → Workflow Engine
await bia_service.start_bia(org_id="org_123")

# Workflow Engine:
# - Creates state machine
# - Sets state = 'identify_processes'
# - Emits event: 'bia.workflow.started'
```

### Step 2: User Asks AI for Help
```python
# User → AI Advisor → Case Library + Workflow
await bia_specialist.get_advice(
    message="I don't know where to start with BIA"
)

# BIA Specialist:
# 1. Gets workflow state from Workflow Engine
# 2. Queries Case Library for similar healthcare orgs
# 3. Finds 5 successful BIA cases
# 4. Builds rich prompt with examples
# 5. Returns: "Organizations like yours typically start by..."
```

### Step 3: User Adds Process
```python
# User → BIA Service → Workflow Engine
await bia_service.add_process({
    'name': 'Patient Registration',
    'tier': 'tier_1',
    'owner': 'John Doe'
})

# Workflow Engine:
# - Validates: are we in 'identify_processes' stage? ✅
# - Validates: does process have required fields? ✅
# - Adds to state data
# - Emits event: 'bia.process.added'
# - Case Collector captures for learning
```

### Step 4: User Tries to Set RTO Too Early
```python
# User → BIA Service → Workflow Engine
await bia_service.set_rto(process_id='proc_1', rto=4)

# Workflow Engine:
# - Validates: are we in 'determine_rto' stage? ❌
# - Current state: 'identify_processes'
# - Returns error: "Cannot set RTO in current stage"
# - Prevents invalid transition (state machine protection)
```

### Step 5: AI Worker Analyzes Process (Safe)
```python
# BIA Service → AI Worker (Organ) → Workflow Context
await process_analyzer.analyze_critical_processes(bia_id='bia_123')

# Process Analyzer:
# 1. Gets workflow context
context = workflow.get_context()
# {
#   'current_state': 'identify_processes',
#   'data': {'processes': [...]},
#   'validation_errors': []
# }

# 2. Validates it's allowed to run
if context['current_state'] != 'identify_processes':
    raise Error("Wrong stage")

# 3. Executes within safe boundaries
# 4. Doesn't hallucinate because has full context
```

### Step 6: Workflow Completes → Case Library Learns
```python
# User → BIA Service → Workflow Engine
await bia_service.complete_bia(bia_id='bia_123')

# Workflow Engine:
# - Validates all stages complete ✅
# - Transitions to 'completed'
# - Emits: 'bia.workflow.completed'

# Case Collector (listening to events):
# - Compiles all journey events
# - Extracts success patterns using AI
# - Saves to Case Library
# - Future BIA specialists can learn from this
```

---

## 🎯 Answer to User's Question

**User asked:** "кто их кк может использовать если мы это еще не орпеделили???" (Who can use them [Organs] if we haven't defined this yet?)

**Answer from Business Logic:**

AI Organs are used by **Services** within **Workflow Engine context**:

1. **BIA Service** calls Process Analyzer Organ
   - Organ gets context from Workflow Engine
   - Validates it's in correct stage
   - Executes safely

2. **Risk Service** calls Risk Assessor Organ
   - Organ gets risk workflow context
   - Validates stage
   - Executes

3. **Planning Service** calls Plan Generator Organ
   - Organ gets planning workflow context
   - Validates stage
   - Generates plan

**Key Insight:**
Organs are NOT called directly by Colleagues (AI Advisors). They're called by **Services** within **Workflow boundaries**.

```
User
  ↓
Service (BIA/Risk/Planning)
  ↓
Workflow Engine (provides context)
  ↓
AI Organ (executes with context)
```

This prevents hallucination because Organ always knows:
- What stage are we in?
- What data exists?
- What actions are valid?
- What's the expected output?

---

## 🔧 Implementation Plan Based on Business Logic

### Phase 1: Integrate Services with Workflow Engine ✅ (Design exists in ком.md)
```
BIA Service → BIAWorkflowAdapter
Risk Service → RiskWorkflowAdapter
Planning Service → PlanningWorkflowAdapter
```

### Phase 2: Integrate AI Advisors with Case Library ⚠️ (Need to implement)
```
BIA Specialist → AIContextBuilder → Case Repository
Risk Analyst → AIContextBuilder → Case Repository
```

### Phase 3: Integrate AI Organs with Workflow Context ⚠️ (Need to define)
```
Process Analyzer → Workflow.get_context()
Risk Assessor → Workflow.get_context()
Plan Generator → Workflow.get_context()
```

### Phase 4: EventBus Integration ⚠️ (Mentioned but not implemented)
```
All components → EventBus (publish events)
Case Collector → EventBus (subscribe to *.workflow.*)
```

---

## 📊 Complete Workflow Definition Pattern (from YAML)

### BIA Workflow - 6 Stages

1. **identify_processes** (Creative Zone - Medium)
   - AI can suggest typical processes for industry
   - Checkpoint validation: min 3 processes, at least 1 Tier 1
   - Creative guidance: "Base on real industry patterns, explain WHY, allow accept/reject"

2. **analyze_dependencies** (Creative Zone - High)
   - AI helps discover hidden dependencies
   - Checkpoint validation: Tier 1 needs min 2 deps (people + technology)
   - Creative guidance: "Be a detective - ask probing questions, suggest typical deps"

3. **assess_impact** (Creative Zone - High)
   - AI analyzes using multiple frameworks
   - Checkpoint validation: financial impact required, all impact types assessed
   - Creative guidance: "Use FMEA, scenarios, cascading effects, case studies"

4. **determine_rto** (Creative Zone - Medium)
   - AI recommends RTO with reasoning
   - Checkpoint validation: no RTO <1h without justification, rationale required
   - Creative guidance: "Balance creativity with data, explain reasoning, present alternatives"

5. **review_results** (Checkpoint - No Creativity)
   - Final validation against ALL constitution + mandatory rules
   - No AI creativity - strict validation only

6. **completed** (Final State)
   - Triggers: Create case for Case Library, trigger risk assessment, update compliance

### AI Advisor Configuration (from YAML)

```yaml
ai_advisor:
  enabled: true
  proactive: true  # Can offer unsolicited advice

  triggers:
    - stage_entered → provide_stage_guidance
    - validation_failed → suggest_remediation
    - time_in_stage_exceeded (48h) → check_if_stuck
    - user_inactive (24h) → send_reminder

  context_sources:
    - workflow_state      # Current stage, data, validation errors
    - case_library        # Similar successful workflows
    - benchmarks          # Industry statistics
    - knowledge_graph     # ISO standards, best practices
    - trending_patterns   # Recent successful patterns
```

**This confirms:** AI Advisors (Colleagues) get context from:
1. Workflow Engine (state)
2. Case Library (patterns)
3. Benchmarks (statistics)
4. Knowledge Graph (standards)

**NOT from Organs!**

---

## 🎯 Governance: Managed Autonomy Pattern

### Constitution (Level 1 - Unchangeable)

**BIA Constitution:**
- Never RTO < 1h without justification
- Always validate financial impact quantitatively
- Mandatory dependency mapping for Tier 1-2

**Forbidden Actions:**
- Modify user data without permission
- Create processes without confirmation
- Override regulatory requirements
- Bypass mandatory checkpoints
- Delete audit trail

### Creative Zones (Where AI is Free)

**4 Creativity Levels:**
- `NONE` - Strictly deterministic
- `LOW` - Minimal freedom, stay close to patterns
- `MEDIUM` - Balance innovation with proven approaches
- `HIGH` - Explore novel approaches, multiple perspectives
- `UNRESTRICTED` - Full freedom

**Example: Impact Assessment (Creativity = HIGH)**
```
Allowed:
- Multiple frameworks (quantitative + qualitative)
- Scenario analysis
- Cascading impact modeling
- Analogies from similar industries

Forbidden:
- Invent financial data
- Override user-provided data
- Make definitive claims without evidence

Guidance:
- Distinguish data-driven vs educated estimates vs hypothetical
- Use case studies: "Hospital X lost $2M when similar process failed"
```

### Checkpoints (No Creativity - Strict Validation)

**5 BIA Checkpoints:**
1. Process Identification Complete (bia_cp_001)
2. Dependencies Mapped (bia_cp_002) - escalation required
3. Impact Assessment Complete (bia_cp_003)
4. RTO Determination Valid (bia_cp_004) - escalation required
5. Final BIA Validation (bia_cp_005) - escalation required

**Checkpoint Logic:**
- Must pass before proceeding (can_skip: false)
- Critical violations → escalate to human
- Generates next_steps for remediation

---

## 🔗 Integration Points (from YAML)

### EventBus Integration
```yaml
integrations:
  eventbus:
    publish_all_events: true
    subscribe_to:
      - governance.organization.created
      - governance.org_context.updated
```

**Events Published:**
- workflow.started
- stage.changed
- action.taken
- challenge.encountered/resolved
- ai.intervention
- checkpoint.failed/passed
- workflow.completed

### Case Library Integration
```yaml
case_library:
  collect_events: true
  anonymize: true

  events_to_collect:
    - All workflow events above

  success_criteria:
    - all_checkpoints_passed: true
    - stakeholder_approval: true
    - within_time_budget: max 45 days
```

**Pattern:** Case Collector listens to ALL workflow events, compiles journey when workflow.completed, extracts patterns using AI, saves to Case Library.

### AI Advisor Integration
```yaml
ai_advisor:
  context_sources:
    - workflow_state       # From Workflow Engine
    - case_library         # Similar cases
    - benchmarks           # Industry stats
    - knowledge_graph      # Standards
    - trending_patterns    # Recent wins
```

**Pattern:** AI Context Builder fetches from all sources, builds rich prompt, sends to LLM.

---

## 📝 Next Steps

1. ✅ **COMPLETED:** Extracted complete business logic from ком.md
2. ✅ **COMPLETED:** Understanding of Governance (Rules, Creative Zones, Checkpoints)
3. ✅ **COMPLETED:** YAML workflow definition patterns

**NOW READY FOR:**

### Phase 1: Map Existing Components to Business Logic
- Classify AI Colleagues as AI Advisors
- Classify AI Organs as Workers (which service uses which organ?)
- Understand MIO Manager role in architecture
- Resolve duplicates based on actual roles

### Phase 2: Define Integration Architecture
- Services → Workflow Engine (state management)
- AI Advisors → Case Library + Workflow State (for context)
- AI Workers → Workflow Context (to avoid hallucination)
- EventBus → Case Collector (learning loop)

### Phase 3: Implementation Roadmap
- Implement EventBus (mentioned but not done)
- Integrate Services with Workflow Engine
- Integrate Colleagues with AI Context Builder
- Integrate Organs with Workflow Context pattern
- Setup Case Collector

---

## 🎓 Key Takeaways

**User was RIGHT to stop me!**

I was assuming "Colleagues use Organs" without understanding the ACTUAL architecture from previous Claude's design:

**The Truth:**
1. **Services** (BIA, Risk, Planning) → Use **Workflow Engine** for state management
2. **AI Advisors** (Colleagues) → Use **Case Library + Workflow State** for context
3. **AI Workers** (Organs) → Called by **Services** with **Workflow Context** to prevent hallucination
4. **Case Library** → Learns from **ALL workflow events** via EventBus

**Key Architectural Principles:**
- ✅ **State Machine** prevents invalid operations
- ✅ **Case Library** enables learning from patterns
- ✅ **AI Context** prevents hallucination
- ✅ **Governance** (Constitution + Checkpoints + Creative Zones) = Managed Autonomy
- ✅ **EventBus** is the nervous system (all events flow through it)

**The Pattern:**
```
User Request
    ↓
Service (BIA/Risk/Planning)
    ↓
Workflow Engine (state machine + validation + events)
    ├→ AI Worker (Organ) gets context to execute safely
    ├→ EventBus publishes all events
    └→ Case Collector learns from journey

User Question
    ↓
AI Advisor (Colleague)
    ↓
AI Context Builder
    ├→ Workflow Engine (current state)
    ├→ Case Library (similar cases)
    ├→ Benchmarks (industry stats)
    └→ Knowledge Graph (standards)
    ↓
LLM with RICH context → Quality advice
```

Now we can properly classify and integrate all existing components based on ACTUAL business logic, not assumptions!
