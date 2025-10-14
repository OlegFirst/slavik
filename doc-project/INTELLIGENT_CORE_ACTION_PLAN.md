# Intelligent Core - Action Plan
**Created**: 2025-10-10
**Priority**: HIGH
**Status**: Ready for Execution

---

## 🎯 Executive Summary

Based on comprehensive analysis of `/intelligent-core/`, here's the prioritized action plan to make the system production-ready.

**Key Findings:**
- ✅ **10 modules production-ready** - Can launch immediately
- ⚠️ **1.5MB duplicate code** in ai-foundation/learning-knowledge
- ⚠️ **Memory architecture fragmented** - 2 independent systems
- ⚠️ **3 case libraries** operating independently
- ✅ **No architectural blockers** - System can operate fully

---

## 🚀 Week 1: Critical Cleanup (Days 1-5)

### Day 1: Archive Duplicate Code (2 hours) - HIGHEST PRIORITY

**Problem**: `ai-foundation/learning-knowledge/` is 1.5MB duplicate of `learning-system/`

**Actions:**
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation
mkdir -p _archive-duplicates/
mv learning-knowledge/ _archive-duplicates/learning-knowledge-2025-10-10/
```

**Verify:**
- Check no imports reference `ai-foundation.learning_knowledge`
- Run tests to confirm nothing breaks
- Document in ai-foundation/README.md

**Expected Result**: -1.5MB, cleaner codebase

---

### Day 2: Clean Root Directory (30 minutes)

**Problem**: 14 files in `/intelligent-core/` root need organization

**Actions:**
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core

# Create directories
mkdir -p docs/
mkdir -p _archive-scripts/

# Move documentation
mv *.md docs/
mv *.txt docs/

# Move old scripts
mv *.py _archive-scripts/  # Only if old/unused
mv *.sh _archive-scripts/  # Only if old/unused

# Keep in root: README.md, __init__.py, setup.py (if exists)
mv docs/README.md ./
```

**Expected Result**: Clean root with only essential files

---

### Days 3-5: Memory Architecture Analysis (Planning Phase)

**Problem**: Memory fragmented across:
- `ai-orchestration/memory/` - 4 files, Redis backend
- `ai-foundation/memory/` - 7 files, PostgreSQL backend
- 3 separate case libraries (workflow, community, collective)
- 3 Qdrant implementations with different embedding models

**Day 3 Actions:**
1. Map all memory read/write operations across codebase
2. Identify which systems are actively used
3. Document current memory flow diagram
4. List all embedding models in use

**Day 4 Actions:**
1. Design unified memory architecture
2. Choose primary backend (recommend: PostgreSQL + Redis hybrid)
3. Plan migration strategy for case libraries
4. Standardize on single Qdrant instance

**Day 5 Actions:**
1. Create migration plan document
2. Estimate effort (2-3 weeks for full migration)
3. Identify rollback points
4. Get stakeholder approval before proceeding

**Expected Result**: Clear roadmap for memory consolidation

---

## 📋 Week 2: Module Integration Check (Days 6-10)

### Day 6: Coordination-Center Decision

**Current State**: Only 2 utility files (ResourceTracker, WishlistSystem), no service

**Options:**

**Option A: Keep as Library** (Recommended, 0 hours)
- Leave as utility modules
- Import where needed
- Document usage in README

**Option B: Convert to Full Service** (1-2 weeks)
- Add main.py, API endpoints
- Integrate with EventBus
- Add to service registry
- Assign port (8059?)

**Action**: Choose option and document decision

---

### Day 7: Verify Production-Ready Modules

**Test these 10 modules:**
1. ai-orchestration (Port 8043)
2. workflow_intelligence (Port 8044)
3. system-bcm-service (Port 8050)
4. expertise-center (Port 8052)
5. ai-foundation (Port 8053)
6. knowledge-system (Port 8054)
7. intelligent-router (Port 8055)
8. learning-system (Port 8057)
9. collective-intelligence (Port 8058)
10. decision-support (Port unassigned)

**Verification Checklist** for each:
- [ ] Service starts without errors
- [ ] `/health` endpoint responds
- [ ] `/metrics` endpoint works
- [ ] Registers with orchestrator
- [ ] Database connections work
- [ ] Redis/EventBus connects
- [ ] Tests pass
- [ ] Logs show no critical errors

**Action**: Create test results spreadsheet

---

### Days 8-10: Integration Testing

**Test inter-service communication:**
- ai-orchestration → workflow_intelligence
- expertise-center → knowledge-system
- learning-system → collective-intelligence
- All services → EventBus

**Create integration tests:**
```python
# test_intelligent_core_integration.py
async def test_orchestrator_to_workflow():
    # Test full request flow
    pass

async def test_knowledge_retrieval():
    # Test expertise-center → knowledge-system
    pass

async def test_learning_feedback_loop():
    # Test learning-system → collective-intelligence
    pass
```

**Expected Result**: All services communicate correctly

---

## 🔧 Weeks 3-4: Memory Consolidation (Optional but Recommended)

### Week 3: Backend Consolidation

**Actions:**
1. Implement unified memory interface
2. Migrate ai-orchestration/memory to new interface
3. Migrate ai-foundation/memory to new interface
4. Add compatibility layer for gradual migration
5. Run parallel systems for 1 week

### Week 4: Case Library Unification

**Actions:**
1. Create unified case storage schema
2. Migrate workflow cases
3. Migrate community cases
4. Migrate collective intelligence cases
5. Implement cross-case search
6. Add case synchronization

**Expected Result**: Single, coherent memory system

---

## 📊 Success Metrics

### Immediate (Week 1)
- [ ] Duplicate code archived (-1.5MB)
- [ ] Root directory cleaned (≤5 files)
- [ ] Memory consolidation plan documented

### Short-term (Week 2)
- [ ] All 10 production modules tested
- [ ] Integration tests pass
- [ ] coordination-center decision made

### Medium-term (Weeks 3-4)
- [ ] Memory architecture unified
- [ ] Case libraries consolidated
- [ ] Single Qdrant instance operational

---

## 🎯 Decision Points

### Critical Decisions Needed:

1. **Coordination-Center**: Keep as library or convert to service?
   - **Recommendation**: Keep as library (lower effort, sufficient for current needs)

2. **Memory Consolidation**: Do now or defer?
   - **Recommendation**: Plan now (Week 1), execute in Weeks 3-4
   - **Alternative**: Defer if immediate launch is priority

3. **Case Libraries**: Unify or keep separate?
   - **Recommendation**: Unify (improves cross-learning)
   - **Timeline**: Week 4

---

## 📝 Documentation Updates Needed

After cleanup:
1. Update `/intelligent-core/README.md` - Reflect new structure
2. Create `/intelligent-core/docs/MEMORY_ARCHITECTURE.md` - Document unified design
3. Create `/intelligent-core/docs/MODULE_DEPENDENCIES.md` - Service dependency map
4. Update each module's README with integration status

---

## 🚦 Current Status: Ready to Begin

**Blockers**: None
**Prerequisites Met**: All
**Estimated Total Effort**:
- Critical cleanup: 1 week
- Integration testing: 1 week
- Memory consolidation: 2 weeks (optional)

**Total**: 2-4 weeks depending on scope

---

## 🎬 Next Steps

**Immediate action (now):**
```bash
# 1. Archive duplicate code
cd /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation
mkdir -p _archive-duplicates
mv learning-knowledge/ _archive-duplicates/learning-knowledge-2025-10-10/
git add -A
git commit -m "refactor: Archive duplicate learning-knowledge code from ai-foundation"

# 2. Clean root
cd /Users/MD/AI-Platform-ISO/intelligent-core
mkdir -p docs/ _archive-scripts/
# (Review files before moving)

# 3. Start services one by one
cd ai-orchestration
python main.py  # Should start on port 8043
```

**Then proceed with Week 1 Day 3 planning.**

---

**Created by**: Claude (Intelligent Core Analysis Session)
**Based on**: 4 agent reports + 3 module deep-dives + comprehensive catalog
**Review**: `/doc-project/INTELLIGENT_CORE_ANALYSIS_2025-10-10.md` for full details
