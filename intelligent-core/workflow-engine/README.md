# Platform Core - Layer 1

**Purpose:** Domain-agnostic system functions
**Version:** 1.0.0
**Created:** 2025-10-05

---

## 🎯 What is Platform Core?

**Platform Core** contains foundational system services that work independently of business domain.

These modules can be used for **ANY domain** - not just BCM (Business Continuity Management).

---

## 📦 Modules

### 1. workflow/
**Unified Workflow Engine** - BPMN orchestration + AI recommendations

- BPMN 2.0 visual modeling
- PostgreSQL persistence
- AI-powered recommendations
- Event-driven architecture
- Multi-tenancy support

**Status:** ✅ Production-ready (v2.0)

**Location:** `platform-core/workflow/` (formerly `unified-workflow/`)

**Documentation:** See `workflow/PHASE_2_COMPLETE.md`

---

### 2. coordination/ (Future)
**Coordination Center** - Multi-agent coordination

---

### 3. learning/ (Future)
**Learning Systems** - Platform-wide learning

---

### 4. community/ (Future)
**Community Intelligence** - Collective intelligence

---

## 🏗️ Architecture Principle

**Layer 1 (Platform Core):** Domain-agnostic
- No BCM-specific logic
- Reusable across domains
- System-level functions

**Layer 2 (AI Intelligence):** Configurable for domains
- AI agents
- RAG pipelines
- ML models

**Layer 3 (Domain Layer):** Business domain logic
- BCM specialists (BIA, Risk, Compliance)
- Domain tools
- Domain knowledge

---

## 📖 Usage

```python
# Import from platform-core
from platform_core.workflow import UnifiedWorkflowEngine

# Use in ANY domain
engine = await UnifiedWorkflowEngine.create(
    tenant_id="acme-corp",
    module="bia"  # or "hr", "finance", "legal", etc.
)
```

---

## 🔗 Related

- **Workflow Intelligence:** `/intelligent-core/workflow_intelligence/`
- **AI Intelligence:** `/intelligent-core/ai-intelligence/` (Layer 2)
- **Domain Plugins:** `/domains/bcm/` (Layer 3)

---

**Version:** 1.0.0
**Last Updated:** 2025-10-05
