# BCM Domain Migration Guide

**Migration from scattered structure to consolidated bcm_domain**

---

## 🎯 Migration Strategy

**Approach:** Gradual migration with zero breaking changes

**Key Principle:** Symlinks maintain backward compatibility until migration complete

---

## 📋 What's Being Migrated

### ✅ MOVED TO bcm_domain

```
intelligent_core/expertise_center/ai_office/ВСМ-colleagues/  → TACTICAL AI Colleagues
platform_services/bia_service/                             → BIA Service
platform_services/risk_service/                            → Risk Service
platform_services/compliance_service/                      → Compliance Service
platform_services/planning_service/                        → Planning Service
platform_services/governance_center/                       → Governance Service
platform_services/plans_service/                           → Plans Service
platform_services/response_service/                        → Response Service
platform_services/documents_service/                       → Documents Service
platform_services/validation_service/                      → Validation Service
platform_services/learning_service/                        → Learning Service
platform_services/community_service/                       → Community Service
platform_services/simulation_service/                      → Simulation Service
platform_services/AI_services_management/                  → Knowledge Quality Manager
```

### ❌ NOT MOVED (Stay in intelligent_core)

**IMPORTANT:** These components are NOT BCM domain-specific!

```
intelligent_core/system_bcm_service/                       → ❌ NO MOVE
  Purpose: Platform self-BCM (meta-level)
  Reason: Platform applies BCM to ITSELF (not a business service)

intelligent_core/expertise_center/ai_experts/specialists/  → ❌ NO MOVE
  Purpose: Strategic BCM program experts
  Reason: Generic framework, reusable across domains
```

**See:** `ARCHITECTURE_DISTINCTIONS.md` for detailed explanation

### Destination (NEW)
```
platform_services/bcm_domain/
├── ai_colleagues/              ← Tactical AI Colleagues (MOVED)
├── services/                   ← All 12 BCM services (MOVED)
└── knowledge_quality_manager/  ← KQM (RENAMED)
```

---

## 🔄 Migration Phases

### Phase 1: Structure Creation ✅ DONE
- [x] Create bcm_domain/ directory
- [x] Create subdirectories (services, ai_colleagues, knowledge, workflows)
- [x] Create __init__.py files
- [x] Create README.md

### Phase 2: Symlink Creation (In Progress)
- [ ] Create symlinks for backward compatibility
- [ ] Test old imports still work
- [ ] Document symlink mappings

### Phase 3: AI Colleagues Migration
- [ ] Copy ВСМ-colleagues/* to ai_colleagues/
- [ ] Update imports in colleagues
- [ ] Test colleague functionality
- [ ] Update coordinator

### Phase 4: Services Migration
- [ ] Move 12 BCM services to services/
- [ ] Update service imports
- [ ] Update SERVICE_CATALOG_DETAILED.yaml
- [ ] Test service discovery

### Phase 5: KQM Migration
- [ ] Rename AI_services_management to knowledge_quality_manager
- [ ] Update imports
- [ ] Test Port 8090
- [ ] Create KQM README

### Phase 6: Cleanup
- [ ] Remove symlinks
- [ ] Update all documentation
- [ ] Run integration tests
- [ ] Update GitHub Pages

---

## 🔗 Symlink Mappings

```bash
# AI Colleagues backward compatibility
ln -s /Users/MD/AI-Platform-ISO/platform_services/bcm_domain/ai_colleagues \
      /Users/MD/AI-Platform-ISO/intelligent_core/expertise_center/ai_office

# Services (if needed during transition)
# No symlinks needed - services accessed via ports, not direct imports
```

---

## 📝 Import Migration Examples

### AI Colleagues

**OLD:**
```python
from intelligent_core.expertise_center.ai_office.colleagues import BIASpecialistAI
from intelligent_core.expertise_center.ai_office.coordinator import ColleagueCoordinator
```

**NEW:**
```python
from platform_services.bcm_domain.ai_colleagues import BIASpecialistAI
from platform_services.bcm_domain.ai_colleagues import ColleagueCoordinator
```

### Services

Services are accessed via HTTP/ports, so no direct import changes needed.

**Service URLs remain the same:**
- BIA Service: http://localhost:8012
- Risk Service: http://localhost:8015
- etc.

---

## ✅ Testing Checklist

After each migration phase:

- [ ] Run unit tests: `pytest platform_services/bcm_domain/`
- [ ] Test imports: `python -c "from platform_services.bcm_domain.ai_colleagues import BIASpecialistAI"`
- [ ] Test services: `curl http://localhost:8012/health`
- [ ] Test integrations: Check EventBus, Decision Center
- [ ] Test documentation: Build docs and verify links

---

## 🚨 Breaking Changes

**None during Phases 1-5!**

Symlinks ensure all old code continues working.

**Phase 6 (Cleanup) will introduce breaking changes:**
- Symlinks removed
- Old import paths will break
- Services moved to new directory structure

**Timeline for Phase 6:** After all components updated

---

## 📞 Support During Migration

**If you encounter issues:**

1. **Imports not working?**
   - Check symlinks exist: `ls -la intelligent_core/expertise_center/ai_office`
   - Should show symlink to bcm_domain/ai_colleagues

2. **Services not found?**
   - Check ports: `netstat -an | grep 8012`
   - Service discovery unchanged

3. **Tests failing?**
   - Update PYTHONPATH: `export PYTHONPATH=/Users/MD/AI-Platform-ISO:$PYTHONPATH`
   - Run from project root

---

## 📊 Migration Progress Tracking

```
Phase 1: Structure       ████████████████████ 100% ✅
Phase 2: Symlinks        ░░░░░░░░░░░░░░░░░░░░   0%
Phase 3: AI Colleagues   ░░░░░░░░░░░░░░░░░░░░   0%
Phase 4: Services        ░░░░░░░░░░░░░░░░░░░░   0%
Phase 5: KQM            ░░░░░░░░░░░░░░░░░░░░   0%
Phase 6: Cleanup         ░░░░░░░░░░░░░░░░░░░░   0%

Overall:                 ███░░░░░░░░░░░░░░░░░  17%
```

---

**Last Updated:** 2025-10-18
**Status:** Phase 1 Complete, Phase 2 In Progress
