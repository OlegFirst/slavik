# Decision Center (Isolated Implementation) - ARCHIVED

**Date Archived:** 2025-10-16
**Reason:** Consolidated into unified solution

---

## Why Archived?

This was the **NEW** Decision Center implementation created during Phase 1.1-1.5.
It was a complete microservice with:
- FastAPI REST API
- AI Hub integration (stub)
- PostgreSQL persistence
- Docker/K8s deployment
- Prometheus monitoring

**Problem:** It duplicated business logic from the existing `policy_engine/decision_center.py` which was already working and being used by Infrastructure Coordinator.

**Solution:** Created **unified solution**:
1. Enhanced OLD Decision Center (`policy_engine/decision_center.py`) with:
   - Optional AI Hub integration
   - Optional Prometheus metrics
   - Kept all working business logic
2. Created FastAPI wrapper (`decision_center_api/`) over enhanced OLD
3. Reused production infrastructure (Docker, K8s) from NEW

---

## What Was Archived?

From `infrastructure/decision_center/`:

### Core Business Logic (Duplicated - не нужно)
- `core/decision_engine.py` - Decision making logic (дублирует OLD)
- `core/escalation_manager.py` - Escalation management (дублирует OLD)
- `core/approval_manager.py` - Approval workflow (дублирует OLD)

### Integrations (Kept useful parts)
- ✅ `integrations/ai_hub.py` - **KEPT** (используется в unified)
- ❌ `integrations/ai_hub_v2.py` - **ARCHIVED** (не использовался)

### API (Replaced with decision_center_api)
- `api/main.py` - FastAPI app (заменен на decision_center_api/main.py)
- `api/decisions.py` - Decision endpoints
- `api/escalations.py` - Escalation endpoints

### Production Infrastructure (Reused)
- ✅ `Dockerfile` - **REUSED** in decision_center_api/
- ✅ `docker-compose.yml` - **REUSED** in decision_center_api/
- ✅ `k8s/` manifests - **REUSED** in decision_center_api/k8s/

### Models & Schemas
- `models/` - Pydantic models (заменены на decision_center_api/models.py)
- `schemas/` - Database schemas (пока не используется)

---

## Migration Path

### Before (Broken):
```
Infrastructure Coordinator
    ↓
OLD Decision Center (policy_engine/)
    (no AI, no metrics)

NEW Decision Center (decision_center/)
    (isolated, not used by anyone)
    ❌ Duplicate business logic
    ❌ Not integrated
```

### After (Unified):
```
Infrastructure Coordinator
    ↓
Enhanced OLD Decision Center (policy_engine/)
    - Proven business logic ✅
    - Optional AI Hub ✅
    - Optional Prometheus ✅
    ↓
FastAPI Wrapper (decision_center_api/)
    - REST API for external services
    - Production infrastructure (Docker/K8s)
```

---

## What to Use Instead?

### For Python Integration:
```python
from infrastructure.policy_engine import InfrastructureDecisionCenter

# With AI and metrics
decision_center = InfrastructureDecisionCenter(
    ai_hub=AIIntelligenceHub(...),
    enable_metrics=True
)
```

### For REST API:
```bash
# Use unified API
curl http://decision-center-api:8080/api/v1/decisions
```

### For Deployment:
```bash
cd infrastructure/decision_center_api/
docker-compose up -d
```

---

## Files in Archive

```
_archive/decision-center-isolated-20251016/
├── core/
│   ├── decision_engine.py (duplicate logic)
│   ├── escalation_manager.py (duplicate)
│   └── approval_manager.py (duplicate)
├── api/
│   ├── main.py (replaced)
│   ├── decisions.py
│   └── escalations.py
├── integrations/
│   └── ai_hub_v2.py (unused)
├── models/
│   └── *.py (replaced)
└── README_ARCHIVE.md (this file)
```

---

## Lessons Learned

1. **Don't duplicate working code** - OLD Decision Center was working, should have enhanced it instead of creating NEW
2. **Integration before isolation** - Should have integrated NEW features into OLD from the start
3. **Backward compatibility first** - Enhanced OLD is backward compatible, NEW was not
4. **Reuse infrastructure, not logic** - Production infrastructure (Docker/K8s) is reusable, business logic duplication is not

---

## Conclusion

This archive contains the **isolated NEW Decision Center** that was never fully integrated.

**Unified solution** combines:
- ✅ Best of OLD: Proven business logic, working integration
- ✅ Best of NEW: AI Hub architecture, production infrastructure
- ✅ Backward compatible: Existing code works
- ✅ Future ready: REST API available

**Use:** `infrastructure/decision_center_api/` instead.
