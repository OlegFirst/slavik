# Quick Guide: Complete Authentication for Remaining Routers

## Overview

Core authentication is **COMPLETE** for BIA and Evidence modules. The remaining compliance routers need the same simple pattern applied.

**Time Estimate**: 90 minutes total for all remaining work

---

## Pattern to Apply

### Step 1: Add Imports (Top of File)

```python
from shared.auth import get_current_user, Permission, require_permission
```

### Step 2: Add Tenant Helper (After router definition)

```python
def verify_tenant_access(current_user: dict, tenant_id: str) -> None:
    """Verify user has access to tenant"""
    if current_user.get("tenant_id") != tenant_id:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: User tenant '{current_user.get('tenant_id')}' does not match resource tenant '{tenant_id}'"
        )
```

### Step 3: Update Each Endpoint

**Before**:
```python
@router.get("/example")
async def get_example(
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
):
    # ... endpoint logic
```

**After**:
```python
@router.get("/example")
@require_permission(Permission.XXX_VIEW)  # <-- ADD THIS
async def get_example(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # <-- ADD THIS
):
    verify_tenant_access(current_user, tenant_id)  # <-- ADD THIS
    # ... endpoint logic
```

---

## Router-Specific Checklist

### 1. assessments.py (6 endpoints remaining) - 15 min

**File**: `/Users/MD/AI-Platform-ISO/services/bcm/compliance/api/assessments.py`

Already has imports and helper ✓

| Endpoint | Decorator | Status |
|----------|-----------|--------|
| `create_assessment` | `@require_permission(Permission.ASSESSMENT_CREATE)` | ✅ DONE |
| `list_assessments` | `@require_permission(Permission.ASSESSMENT_VIEW)` | ⏳ TODO |
| `get_assessment` | `@require_permission(Permission.ASSESSMENT_VIEW)` | ⏳ TODO |
| `run_assessment` | `@require_permission(Permission.ASSESSMENT_RUN)` | ⏳ TODO |
| `get_assessment_results` | `@require_permission(Permission.ASSESSMENT_VIEW)` | ⏳ TODO |
| `delete_assessment` | `@require_permission(Permission.ASSESSMENT_DELETE)` | ⏳ TODO |
| `batch_ai_assessment` | `@require_permission(Permission.ASSESSMENT_RUN)` | ⏳ TODO |

**Quick Script**:
```bash
# Lines to update in assessments.py
# Line ~98: @router.get("/")
# Line ~138: @router.get("/{assessment_id}")
# Line ~176: @router.post("/{assessment_id}/run")
# Line ~281: @router.get("/{assessment_id}/results")
# Line ~362: @router.delete("/{assessment_id}")
# Line ~412: @router.post("/batch-ai-scan")
```

---

### 2. gaps.py (13 endpoints) - 30 min

**File**: `/Users/MD/AI-Platform-ISO/services/bcm/compliance/api/gaps.py`

| Endpoint | Decorator | Line |
|----------|-----------|------|
| `list_gaps` | `@require_permission(Permission.GAP_VIEW)` | ~49 |
| `get_gap` | `@require_permission(Permission.GAP_VIEW)` | ~98 |
| `update_gap` | `@require_permission(Permission.GAP_UPDATE)` | ~136 |
| `start_remediation` | `@require_permission(Permission.GAP_REMEDIATE)` | ~183 |
| `update_remediation_progress` | `@require_permission(Permission.GAP_REMEDIATE)` | ~251 |
| `resolve_gap` | `@require_permission(Permission.GAP_REMEDIATE)` | ~319 |
| `verify_gap_resolution` | `@require_permission(Permission.GAP_VERIFY)` | ~385 |
| `reopen_gap` | `@require_permission(Permission.GAP_UPDATE)` | ~454 |
| `get_gaps_by_severity` | `@require_permission(Permission.GAP_VIEW)` | ~520 |
| `create_root_cause_analysis` | `@require_permission(Permission.GAP_UPDATE)` | ~573 |
| `get_root_cause_analyses` | `@require_permission(Permission.GAP_VIEW)` | ~658 |
| `create_effectiveness_review` | `@require_permission(Permission.GAP_VERIFY)` | ~717 |
| `get_effectiveness_reviews` | `@require_permission(Permission.GAP_VIEW)` | ~817 |

**Needs**: Imports + Helper + 13 endpoint updates

---

### 3. audit.py (11 endpoints) - 25 min

**File**: `/Users/MD/AI-Platform-ISO/services/bcm/compliance/api/audit.py`

| Endpoint | Decorator | Line |
|----------|-----------|------|
| `create_audit_program` | `@require_permission(Permission.AUDIT_CREATE)` | ~59 |
| `list_audit_programs` | `@require_permission(Permission.AUDIT_VIEW)` | ~113 |
| `schedule_audit` | `@require_permission(Permission.AUDIT_CREATE)` | ~159 |
| `list_audits` | `@require_permission(Permission.AUDIT_VIEW)` | ~232 |
| `get_audit_checklist` | `@require_permission(Permission.AUDIT_VIEW)` | ~269 |
| `create_audit_finding` | `@require_permission(Permission.AUDIT_CONDUCT)` | ~353 |
| `list_audit_findings` | `@require_permission(Permission.AUDIT_VIEW)` | ~425 |
| `start_audit` | `@require_permission(Permission.AUDIT_CONDUCT)` | ~473 |
| `complete_audit` | `@require_permission(Permission.AUDIT_CLOSE)` | ~512 |
| `get_audit_report` | `@require_permission(Permission.AUDIT_VIEW)` | ~551 |

**Needs**: Imports + Helper + 11 endpoint updates

---

### 4. dashboard.py (4 endpoints) - 10 min

**File**: `/Users/MD/AI-Platform-ISO/services/bcm/compliance/api/dashboard.py`

All endpoints use `Permission.ASSESSMENT_VIEW`:

| Endpoint | Line |
|----------|------|
| `get_compliance_overview` | ~48 |
| `get_requirements_matrix` | ~168 |
| `get_compliance_roadmap` | ~289 |
| `get_analytics_dashboard` | ~404 |

**Simplest router** - all same permission

---

### 5. management_review.py (8 endpoints) - 20 min

**File**: `/Users/MD/AI-Platform-ISO/services/bcm/compliance/api/management_review.py`

| Endpoint | Decorator | Line |
|----------|-----------|------|
| `create_management_review` | `@require_permission(Permission.REVIEW_CREATE)` | ~58 |
| `list_management_reviews` | `@require_permission(Permission.REVIEW_VIEW)` | ~112 |
| `get_management_review` | `@require_permission(Permission.REVIEW_VIEW)` | ~158 |
| `get_review_inputs` | `@require_permission(Permission.REVIEW_VIEW)` | ~203 |
| `start_review` | `@require_permission(Permission.REVIEW_UPDATE)` | ~356 |
| `record_decisions` | `@require_permission(Permission.REVIEW_UPDATE)` | ~418 |
| `complete_review` | `@require_permission(Permission.REVIEW_UPDATE)` | ~493 |
| `get_review_report` | `@require_permission(Permission.REVIEW_VIEW)` | ~573 |

**Needs**: Imports + Helper + 8 endpoint updates

---

## Automation Option

To speed up the process, you could use a Python script:

```python
#!/usr/bin/env python3
"""
Add authentication to compliance routers
"""

import re
from pathlib import Path

ROUTERS = {
    "assessments.py": {
        "list_assessments": ("Permission.ASSESSMENT_VIEW", 98),
        "get_assessment": ("Permission.ASSESSMENT_VIEW", 138),
        "run_assessment": ("Permission.ASSESSMENT_RUN", 176),
        "get_assessment_results": ("Permission.ASSESSMENT_VIEW", 281),
        "delete_assessment": ("Permission.ASSESSMENT_DELETE", 362),
        "batch_ai_assessment": ("Permission.ASSESSMENT_RUN", 412),
    },
    # ... add others
}

def add_decorator(filepath: Path, endpoint_name: str, permission: str, line_num: int):
    """Add @require_permission decorator before @router decorator"""
    content = filepath.read_text()
    lines = content.split("\n")

    # Find @router line
    for i in range(line_num - 5, line_num + 5):
        if "@router." in lines[i]:
            # Insert decorator before @router
            decorator = f"@require_permission({permission})"
            if decorator not in lines[i-1]:
                lines.insert(i, decorator)
            break

    filepath.write_text("\n".join(lines))

# Run for each router...
```

---

## Verification

After updating each router, verify:

```bash
# Syntax check
python3 -m py_compile /path/to/router.py

# Import check
python3 -c "from compliance.api.gaps import router; print('OK')"
```

---

## Testing

Once complete, test with:

```bash
# Create test token
python3 << 'EOF'
from shared.auth import init_jwt
jwt_manager = init_jwt("dev-secret-CHANGE-IN-PRODUCTION-12345")
token = jwt_manager.create_token("user1", "tenant1", "bcm_manager", 24)
print(f"Token: {token}")
EOF

# Test endpoint
curl -X GET \
  http://localhost:8014/api/gaps?tenant_id=tenant1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Completion Checklist

- [ ] assessments.py (6 endpoints)
- [ ] gaps.py (13 endpoints)
- [ ] audit.py (11 endpoints)
- [ ] dashboard.py (4 endpoints)
- [ ] management_review.py (8 endpoints)
- [ ] Run syntax validation on all files
- [ ] Test authentication with sample tokens
- [ ] Test permission enforcement
- [ ] Test tenant isolation
- [ ] Update AUTH_IMPLEMENTATION_REPORT.md with final status

**Total**: 42 endpoints to protect

---

## Quick Reference: Permission by Operation

| Operation | Permission |
|-----------|-----------|
| List/Get (READ) | XXX_VIEW |
| Create (POST new resource) | XXX_CREATE |
| Update/Patch (MODIFY) | XXX_UPDATE |
| Delete | XXX_DELETE |
| Special actions (run, complete, etc.) | Specific permission |

---

**Ready to continue?** Start with **assessments.py** (6 endpoints, 15 min) - it already has the imports and helper function, so you only need to update the 6 endpoints.
