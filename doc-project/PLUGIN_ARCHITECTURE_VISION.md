# 🔌 Plugin Architecture - Quick Vision

**Date:** 2025-10-05
**Concept:** Domain as Plugin

---

## 🎯 Main Idea

**BCM = Plugin that loads into Platform**

```
Platform (system)  +  BCM Domain (plugin)  =  BCM Platform
Platform (system)  +  HR Domain (plugin)   =  HR Platform
Platform (system)  +  [No domain]          =  Empty Platform
```

---

## 📊 3 Layers

### Layer 1: Platform Core (Domain-Agnostic System)

**Works with ANY domain:**

```
platform-core/
├── workflow/           ← Unified Workflow (works for BCM, HR, Finance)
├── learning/           ← Learning System (learns from any domain)
├── case-library/       ← Success patterns (any domain)
├── community/          ← Community intelligence
└── coordination/       ← Coordination center
```

**No BCM references!** Just workflow engine, case library, learning.

---

### Layer 2: AI Intelligence (Configures for Domain)

**Adapts to loaded domain:**

```
ai-intelligence/
├── chief/              ← ChiefExecutiveAI (routes to any domain)
├── managers/           ← 3 managers (govern, platform, domain)
└── shared/
    ├── base/           ← BaseDomain, BaseExpert, BaseTool
    ├── rag/            ← RAG pipeline (loads domain knowledge)
    ├── ml/             ← ML models
    └── learning/       ← Self-learning
```

**Platform-level AI** that configures for any domain.

---

### Layer 3: Domain Layer (Swappable Plugin)

**BCM domain plugin:**

```
domains/bcm/
├── experts/            ← 10 BCM experts
├── tools/              ← BCM tools
├── organs/             ← BCM organs
├── knowledge/          ← ISO 22301, BCI GPG
├── services/           ← bia-service, risk-service
└── domain_config.py    ← Plugin registration
```

**All BCM-specific code in one place!**

---

## 🔄 How It Works

### 1. Platform without domain (empty)

```python
from ai_intelligence import Platform

platform = Platform()

# Platform Core works:
platform.workflow_engine    # ✅ Ready
platform.learning_system    # ✅ Ready
platform.case_library       # ✅ Ready

# But no experts:
platform.domain_manager.get_experts()  # → []
```

---

### 2. Load BCM domain

```python
from domains.bcm import BCMDomain

bcm = BCMDomain()
await platform.load_domain(bcm)

# Now BCM experts registered:
platform.domain_manager.get_experts()
# → [BIASpecialist, RiskAnalyst, ...] (10 experts)

# BCM knowledge loaded:
platform.rag_pipeline.search("ISO 22301")
# → Returns ISO 22301 content
```

---

### 3. Use platform

```python
result = await platform.chief.handle_request(
    query="How to conduct BIA?",
    context={"industry": "healthcare"}
)

# Routing:
# Chief → Domain Manager → BIA Specialist
#
# BIA Specialist uses:
# - platform.workflow_engine (Platform Core)
# - platform.rag_pipeline (with BCM knowledge)
# - platform.case_library (Platform Core)
# - bcm.tools (Domain tools)
```

---

### 4. Switch domain (future)

```python
from domains.hr import HRDomain

await platform.switch_domain(HRDomain())

# Now HR experts:
platform.domain_manager.get_experts()
# → [SuccessionPlanner, TalentManager, ...]

# Same platform, different domain!
```

---

## 🎯 Key Benefits

### ✅ Separation

- Platform Core = NO BCM code
- BCM = self-contained in `domains/bcm/`
- Easy to find everything BCM-related

### ✅ Synergy without tight coupling

```python
# BCM Expert uses Platform Core
class BIASpecialist:
    def __init__(
        self,
        workflow_engine,    # Platform Core
        rag_pipeline,       # AI Intelligence
        tools              # BCM Domain
    ):
        # Expert uses platform services
        # but is BCM-specific
```

### ✅ Easy to add new domains

```bash
# Copy structure
cp -r domains/bcm domains/hr

# Modify config
vim domains/hr/domain_config.py

# Add HR experts
# Done!
```

### ✅ Platform stays functional

```python
# Platform without domain = works
platform.workflow_engine.find_similar(...)    # ✅
platform.case_library.search(...)             # ✅
platform.learning_system.learn(...)           # ✅

# Just no domain experts until loaded
```

---

## 📁 File Migration Map

### → Platform Core
```
unified-workflow/           → platform-core/workflow/
learning-system/            → platform-core/learning/
workflow_intelligence/case/ → platform-core/case-library/
```

### → AI Intelligence
```
ai_platform/chief/          → ai-intelligence/chief/
ai_platform/managers/       → ai-intelligence/managers/
ai-office/core/rag/         → ai-intelligence/shared/rag/
ai_experts/ml/              → ai-intelligence/shared/ml/
```

### → BCM Domain
```
ai_platform/experts/domain/ → domains/bcm/experts/
ai_experts/tools/           → domains/bcm/tools/
ai-office/organs/           → domains/bcm/organs/
ai_experts/knowledge/       → domains/bcm/knowledge/
platform-services/          → domains/bcm/services/
```

---

## 🚀 Quick Start

### For implementation:
1. Read: [PLUGIN_ARCHITECTURE_IMPLEMENTATION_PLAN.md](PLUGIN_ARCHITECTURE_IMPLEMENTATION_PLAN.md)
2. Read: [AGENT_ONBOARDING.md](AGENT_ONBOARDING.md) (for second agent)
3. Pick tasks from Phase 1
4. Start parallel work!

---

## ✨ Vision Summary

**Before:**
```
intelligent-core/
├── ai-office/          ← BCM + general (MIXED!)
├── ai_experts/         ← BCM + general (MIXED!)
├── ai_platform/        ← Trying to merge (CONFUSION!)
└── unified-workflow/   ← Good (domain-agnostic)
```

**After:**
```
intelligent-core/
├── platform-core/      ← Domain-agnostic (workflow, learning)
├── ai-intelligence/    ← AI infrastructure (any domain)

domains/bcm/            ← BCM plugin (all BCM code)
```

**Result:** Clean, modular, scalable! 🎉

---

**Ready to implement?** See [PLUGIN_ARCHITECTURE_IMPLEMENTATION_PLAN.md](PLUGIN_ARCHITECTURE_IMPLEMENTATION_PLAN.md)
