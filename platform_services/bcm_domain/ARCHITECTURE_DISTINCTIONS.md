# Architecture Distinctions: What Goes Where?

**Critical Decision Document for BCM Domain Migration**

---

## 🎯 Core Principle

**Domain-Driven Architecture with Clear Separation:**

```
WHAT stays in intelligent_core:
✅ Generic AI capabilities (RAG, LLM, ML)
✅ Platform self-management (System BCM Service)
✅ Strategic experts for the PLATFORM
✅ Framework and infrastructure

WHAT moves to bcm_domain (platform_services):
✅ BCM domain services (BIA, Risk, Compliance, etc.)
✅ BCM tactical assistants for USERS
✅ BCM domain knowledge (ISO 22301, scenarios)
✅ BCM-specific workflows
```

---

## 📊 THREE LEVELS OF BCM AI

### Level 1: META-LEVEL (Platform BCM)
**Location:** `intelligent_core/system_bcm_service/`
**Port:** 8050

**Purpose:** **THE PLATFORM APPLIES BCM TO ITSELF**

```python
# This is NOT a BCM domain service!
# This is the PLATFORM's own BCM system!

system_bcm_service:
  - Monitors platform health (self-awareness)
  - Applies BCM principles to platform itself
  - Coordinates recovery of platform services
  - Uses EventBus for platform-wide coordination
  - Delegates to existing platform components
  - "Coordinator, not executor"
```

**Key Characteristics:**
- 🏥 **Self-Healing**: Platform heals itself using BCM
- 🔄 **24-hour cycles**: Continuous PDCA for platform
- 📊 **Resource Tracking**: Platform's own RTO/RPO monitoring
- 🧠 **Learning**: Platform learns from its own incidents
- ⚡ **Survival Instinct**: Platform fights to stay alive

**Why it stays in intelligent_core:**
- It's a PLATFORM CAPABILITY, not a business service
- It's GENERIC (any platform could have this)
- It's INFRASTRUCTURE-level, not domain-level
- It ensures platform CONTINUITY (meta-BCM)

**Migration Decision:** ✅ **KEEP in intelligent_core** (NO MOVE!)

---

### Level 2: STRATEGIC EXPERTS (Program-Level)
**Location:** `intelligent_core/expertise_center/ai_experts/specialists/`

**Purpose:** **STRATEGIC BCM PROGRAM MANAGEMENT**

```python
ai_experts/specialists/:
  - bcm_advisor.py          # BCM program strategy
  - compliance_auditor.py   # ISO 22301 compliance
  - strategic_planner.py    # Long-term BCM roadmap

# These are HIGH-LEVEL strategic consultants
# They advise on the PROGRAM, not tactical tasks
```

**Strategic Experts:**

1. **BCM Advisor**
   - Role: BCM program strategy
   - Scope: Organization-wide BCM
   - Tools: BIA Analysis, Dependency Mapper, Case Search
   - Temperature: 0.3 (factual)

2. **Compliance Auditor**
   - Role: ISO 22301 compliance auditing
   - Scope: Clause-by-clause compliance
   - Tools: Compliance Check, Gap Analysis, Evidence Validator
   - Temperature: 0.2 (very factual)

3. **Strategic Planner**
   - Role: Long-term BCM roadmap
   - Scope: Multi-year planning, budgeting, maturity
   - Tools: Timeline Predictor, Resource Planner, Maturity Assessment
   - Temperature: 0.4 (strategic thinking)

**Why they stay in intelligent_core:**
- They're GENERIC experts (work across domains)
- They're STRATEGIC (program-level, not task-level)
- They're REUSABLE (security_domain, privacy_domain will use them too)
- They're FRAMEWORK (not domain-specific)

**Migration Decision:** ✅ **KEEP in intelligent_core/expertise_center** (NO MOVE!)

---

### Level 3: TACTICAL COLLEAGUES (User-Facing)
**Location:** `platform_services/bcm_domain/ai_colleagues/` ← MIGRATED!

**Purpose:** **TACTICAL BCM TASK ASSISTANCE FOR USERS**

```python
bcm_domain/ai_colleagues/:
  - bia_specialist/         # RTO/RPO determination
  - risk_analyst/           # Tactical risk analysis
  - compliance_copilot/     # Day-to-day compliance
  - exercise_designer/      # Exercise design
  - incident_advisor/       # Incident response
  - plan_generator/         # Plan creation
  - project_manager/        # BCM project tasks
  - project_intelligence/   # BCM analytics

# These are TASK-LEVEL assistants
# They help USERS do BCM work
```

**Tactical Colleagues:**

**Characteristics:**
- 🎯 **Task-focused**: Help with specific BCM tasks
- 👥 **User-facing**: Direct interaction with BCM practitioners
- 📝 **Hands-on**: Create deliverables (BIAs, plans, exercises)
- 🔧 **Tool-using**: Integrate with BCM services (8012, 8015, etc.)
- 📊 **Domain-specific**: ISO 22301 specific

**Why they moved to bcm_domain:**
- They're BCM-SPECIFIC (only relevant for ISO 22301)
- They're USER-FACING (help users do BCM work)
- They're TIGHTLY COUPLED to BCM services
- They're DOMAIN LOGIC (not generic framework)

**Migration Decision:** ✅ **MOVED to platform_services/bcm_domain/ai_colleagues/**

---

## 🏗️ Architecture Comparison

### BEFORE (Old Structure - Confusing!)

```
intelligent_core/
├── system_bcm_service/        # Platform BCM (meta-level)
├── expertise_center/
│   ├── ai_office/             # ❌ MIXED: Tactical + Infrastructure
│   │   └── ВСМ-colleagues/   # Tactical BCM assistants
│   └── ai_experts/
│       └── specialists/       # Strategic BCM experts
```

**Problem:** Tactical colleagues mixed with strategic experts!

### AFTER (New Structure - Clear!)

```
intelligent_core/
├── system_bcm_service/        # ✅ META: Platform self-BCM
└── expertise_center/
    └── ai_experts/
        └── specialists/       # ✅ STRATEGIC: Program-level

platform_services/
└── bcm_domain/
    └── ai_colleagues/         # ✅ TACTICAL: User-facing
```

**Benefit:** Clear separation by purpose and level!

---

## 📋 Decision Matrix

| Component | Level | Purpose | Location | Move? |
|-----------|-------|---------|----------|-------|
| **system_bcm_service** | Meta | Platform self-BCM | intelligent_core/ | ❌ NO |
| **ai_experts/specialists** | Strategic | Program management | intelligent_core/expertise_center/ | ❌ NO |
| **ai_office/ВСМ-colleagues** | Tactical | User task assistance | platform_services/bcm_domain/ | ✅ YES |

---

## 🎯 Key Distinctions

### System BCM Service vs BCM Domain Services

```
system_bcm_service (Port 8050):
├── Purpose: Platform applies BCM to ITSELF
├── Monitors: Platform health, platform RTO/RPO
├── Recovers: Platform services
├── Learns: From platform incidents
└── Who uses: PLATFORM (autonomous)

bcm_domain/services (Ports 80XX):
├── Purpose: Help USERS apply BCM to THEIR organization
├── Monitors: User's business processes
├── Recovers: User's critical functions
├── Learns: From user's BCM activities
└── Who uses: USERS (interactive)
```

### Strategic Experts vs Tactical Colleagues

```
ai_experts/specialists:
├── Level: Strategic, program-level
├── Scope: Organization-wide BCM program
├── Examples: "Should we adopt ISO 22301?" "What's our maturity level?"
├── Temperature: Lower (factual, strategic)
├── Tools: Assessment, planning, roadmapping
└── Reusable: Yes (across domains)

ai_colleagues:
├── Level: Tactical, task-level
├── Scope: Specific BCM deliverables
├── Examples: "Determine RTO for process X" "Create BIA for department Y"
├── Temperature: Higher (practical, creative)
├── Tools: BIA forms, risk registers, plan templates
└── Reusable: No (BCM-specific)
```

---

## 🚀 Multi-Standard Scalability

### When we add ISO 27001 (Security Domain):

```
intelligent_core/
├── system_bcm_service/        # ✅ Still generic (platform self-management)
└── expertise_center/
    └── ai_experts/
        └── specialists/       # ✅ Will add ISMS Advisor, Security Auditor
            ├── bcm_advisor.py
            ├── isms_advisor.py          # NEW for ISO 27001
            ├── security_auditor.py      # NEW for ISO 27001
            └── strategic_planner.py     # ✅ Reused across domains!

platform_services/
├── bcm_domain/
│   └── ai_colleagues/         # ✅ BCM-specific colleagues
│       ├── bia_specialist/
│       └── ...
│
└── security_domain/            # NEW!
    └── ai_colleagues/          # NEW: Security-specific colleagues
        ├── vulnerability_analyst/
        ├── threat_hunter/
        └── security_architect/
```

**Key Insight:**
- Strategic Experts are SHARED (strategic_planner works for both!)
- Tactical Colleagues are DOMAIN-SPECIFIC (each domain has its own)

---

## ✅ Final Architecture Recommendation

### ❌ DO NOT MOVE (Keep in intelligent_core):

1. **system_bcm_service/** - Platform self-BCM (meta-level)
2. **expertise_center/ai_experts/specialists/** - Strategic program experts

**Reasoning:**
- Generic capabilities
- Reusable across domains
- Infrastructure/framework level
- Not BCM-domain specific

### ✅ DO MOVE (To platform_services/bcm_domain):

1. **ai_office/ВСМ-colleagues/** → **bcm_domain/ai_colleagues/**

**Reasoning:**
- BCM-specific tactical assistants
- User-facing task helpers
- Tightly coupled to BCM services
- Domain logic, not framework

---

## 📚 Summary

**Three Levels of BCM AI:**

```
Level 1 (Meta):        intelligent_core/system_bcm_service/
                       "Platform applies BCM to itself"
                       ✅ KEEP

Level 2 (Strategic):   intelligent_core/expertise_center/ai_experts/
                       "Program-level BCM expertise"
                       ✅ KEEP

Level 3 (Tactical):    platform_services/bcm_domain/ai_colleagues/
                       "Task-level BCM assistance"
                       ✅ MOVED
```

**Result:**
- ✅ Clear separation of concerns
- ✅ Proper abstraction levels
- ✅ Ready for multi-standard scaling
- ✅ Platform self-management intact

---

**Last Updated:** 2025-10-18
**Decision:** Architectural clarity achieved!
**Status:** system_bcm_service and ai_experts/specialists stay in intelligent_core
