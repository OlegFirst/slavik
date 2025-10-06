# ⚠️ ARCHIVED MODULE - bpmn-workflow

**Archive Date:** 2025-10-05
**Reason:** Replaced by unified-workflow (v2.0)

---

## Why Archived?

This module was an **initial prototype** for BPMN workflow orchestration (created Oct 2, 2025).

**Issues:**
- ❌ In-memory storage only (data lost on restart)
- ❌ No database persistence
- ❌ No AI integration
- ❌ No multi-tenancy
- ❌ Limited to 443 lines single file
- ❌ FastAPI monolith (hard to reuse)

**Replacement:** `intelligent-core/platform-core/workflow/` (unified-workflow v2.0)

---

## What Was Migrated?

✅ **Concepts** taken from this module:
- BPMN Process, Instance, Task models
- BPMN XML parsing approach
- Event publishing pattern
- Process orchestration logic

✅ **Replaced with** in unified-workflow:
- PostgreSQL persistence (Supabase)
- Repository pattern
- AI recommendations
- Workflow Intelligence integration
- Multi-tenancy (RLS)
- 5,500+ lines production code

---

## Reference

This code is kept for **reference purposes only**.

**Main files:**
- `main.py` (443 lines) - BPMN engine FastAPI app
- `mock_data.py` - Mock data for testing
- `README.md` - Original documentation

**Do NOT use this code in production.**

For current BPMN/workflow functionality, use:
- `intelligent-core/platform-core/workflow/` (unified-workflow v2.0)

---

## Migration Guide

If you were using bpmn-workflow, migrate to unified-workflow:

**Old (bpmn-workflow):**
```python
# POST /api/workflows/start
POST http://localhost:8003/api/workflows/start
{
    "process_id": "proc_123",
    "tenant_id": "acme",
    "variables": {...}
}
```

**New (unified-workflow):**
```python
from platform_core.workflow import UnifiedWorkflowEngine

engine = await UnifiedWorkflowEngine.create(
    tenant_id="acme",
    module="bia"
)

instance_id = await engine.start_process_from_bpmn(
    bpmn_xml=bpmn_content,
    initial_variables={...}
)
```

---

**Questions?** See:
- `/intelligent-core/platform-core/workflow/PHASE_2_COMPLETE.md`
- `/UNIFIED_WORKFLOW_PHASE_2_SUMMARY.md`
- `/BPMN_MODULES_COMPARISON.md`
