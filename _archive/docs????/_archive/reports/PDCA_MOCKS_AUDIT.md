# 🔍 PDCA MOCKS AUDIT - Полный список заглушек

**Date**: 2025-10-09
**Audited**: intelligent-core/workflow_intelligence/core/pdca_rules.py

---

## 📊 SUMMARY

**Total Mocks Found**: 8
**Lines with Fallbacks**: 6
**Hardcoded Values**: 4
**Missing Integrations**: 3

---

## 🔴 CRITICAL MOCKS (Must Fix)

### 1. **Case Library - Optional Fallback** (Lines 250-273)

```python
# MOCK:
if self.case_library:
    # Real implementation
    cases = await self.case_library.find_cases(...)
else:
    # FALLBACK: Ищем в completed cycles (in-memory)
    similar = [
        {
            "plan_data": c.plan_data,
            "lessons": c.lessons_learned,
            "success": len(c.deviations or []) < 3  # HARDCODED THRESHOLD
        }
        for c in self.completed_cycles[-50:]  # LAST 50 ONLY
        if c.module == module
    ]
```

**Problem**:
- Case Library is optional (should be required!)
- Fallback uses in-memory cycles (max 50, lost on restart)
- Success threshold hardcoded (3 deviations)
- No k-anonymity check

**Fix**: Make Case Library required, connect to PostgreSQL

---

### 2. **Knowledge Base - Optional** (Lines 467-484)

```python
# MOCK:
if not self.knowledge_base:
    return  # SILENT FAIL!

# No fallback - lessons just lost!
```

**Problem**:
- Knowledge Base optional - lessons lost if not connected
- No error, no warning, just silent return
- Platform doesn't learn!

**Fix**: Make Knowledge Base required

---

### 3. **Pattern Detector - Optional** (Lines 391-400)

```python
# MOCK:
if self.pattern_detector:
    # Real ML pattern detection
    detected = await self.pattern_detector.detect_patterns(...)
else:
    # NOTHING - no pattern detection!
    pass

# Простые эвристики (fallback)
if cycle.deviations:
    lessons.append(f"Issue found: {deviation}")  # BASIC!
```

**Problem**:
- Pattern Detector optional - no ML insights
- Falls back to simple string formatting
- No anomaly detection, no trend analysis

**Fix**: Make Pattern Detector required

---

### 4. **Quality Score - Hardcoded Logic** (Lines 126-130)

```python
# MOCK:
quality_score = 8.0  # Placeholder - all approved cases are high quality
```

**Problem**:
- ALL cases get score 8.0
- No real peer review integration
- No quality variation

**Fix**: Query real peer_reviews table

---

## 🟡 MEDIUM MOCKS (Should Fix)

### 5. **Outcome Prediction - Simple Average** (Lines 291-308)

```python
# MOCK:
# Простое усреднение (можно улучшить ML моделью)
outcomes = {}
durations = [c.get("do_duration") for c in similar_cases if c.get("do_duration")]
if durations:
    outcomes["expected_duration_seconds"] = sum(durations) / len(durations)
```

**Problem**:
- Simple average, no ML model
- No confidence intervals
- No context weighting (recent cases should matter more)

**Fix**: Use Predictive Engine ML model

---

### 6. **Recommendation Parsing - Simple Text** (Lines 373-389)

```python
# MOCK:
# Simplified parsing - real implementation would use JSON parsing
recommendations = []
if "recommendation" in response_text.lower():
    lines = response_text.split('\n')
    for line in lines:
        if any(keyword in line.lower() for keyword in ['prepare', 'review', ...]):
            recommendations.append({
                'action': line.strip(),
                'priority': 'medium',  # ALWAYS MEDIUM!
                'type': 'proactive'
            })
```

**Problem**:
- Text parsing instead of structured JSON
- Priority always "medium"
- No validation

**Fix**: LLM should return structured JSON, parse properly

---

### 7. **Prerequisite Check - Always True** (Lines 313-320)

```python
# MOCK:
async def _check_prerequisites(self, action, tenant_id) -> bool:
    if not action.prerequisites:
        return True

    # Simplified prerequisite checking
    # In production, this would check actual system state
    return True  # ALWAYS TRUE!
```

**Problem**:
- Prerequisites never checked
- Always returns True
- No actual state validation

**Fix**: Check real system state (DB, workflow state, permissions)

---

## 🟢 MINOR MOCKS (Nice to Fix)

### 8. **Benchmarks - In-Memory Only** (Lines 346-365)

```python
# MOCK:
# Простой расчет из completed cycles (in-memory)
module_cycles = [c for c in self.completed_cycles if c.module == module]

if not module_cycles:
    return {}  # NO BENCHMARKS!

durations = [c.do_duration for c in module_cycles if c.do_duration]

return {
    "avg_duration": sum(durations) / len(durations) if durations else 0,
    "min_duration": min(durations) if durations else 0,
    "max_duration": max(durations) if durations else 0
}
```

**Problem**:
- Only from in-memory cycles (lost on restart)
- No historical data from PostgreSQL
- Limited to recent cycles

**Fix**: Query PostgreSQL pdca_cycles table

---

## 📊 MOCK COUNT BY TYPE

```
Optional Dependencies (silent fail):  3
├── Case Library
├── Knowledge Base
└── Pattern Detector

Hardcoded Values:                     4
├── Quality score = 8.0
├── Priority = "medium"
├── Success threshold = 3 deviations
└── Prerequisites = always True

Simplified Algorithms:                3
├── Simple average (no ML)
├── Text parsing (no JSON)
└── In-memory benchmarks

TOTAL MOCKS:                          8
```

---

## ✅ WHAT'S NEEDED

### 1. **Required Dependencies**

```python
class PDCARulesEngine:
    def __init__(
        self,
        case_library: CaseLibrary,        # REQUIRED!
        knowledge_base: KnowledgeBase,    # REQUIRED!
        pattern_detector: PatternDetector, # REQUIRED!
        db_session: AsyncSession           # REQUIRED!
    ):
        # Validate all required
        if not all([case_library, knowledge_base, pattern_detector, db_session]):
            raise ValueError("All dependencies required!")

        self.case_library = case_library
        self.knowledge_base = knowledge_base
        self.pattern_detector = pattern_detector
        self.db = db_session
```

---

### 2. **PostgreSQL Storage**

```sql
-- pdca_cycles table
CREATE TABLE workflow_intelligence.pdca_cycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id VARCHAR NOT NULL,
    module VARCHAR NOT NULL,
    tenant_id UUID NOT NULL,

    -- Timing
    cycle_started_at TIMESTAMPTZ NOT NULL,
    cycle_completed_at TIMESTAMPTZ,
    do_duration FLOAT,

    -- PLAN phase
    plan_data JSONB NOT NULL,
    plan_recommendations TEXT[],
    expected_outcomes JSONB,
    estimated_duration FLOAT,

    -- DO phase
    do_data JSONB,

    -- CHECK phase
    check_data JSONB,
    deviations TEXT[],
    benchmarks JSONB,
    quality_score FLOAT,

    -- ACT phase
    lessons_learned TEXT[],
    patterns_detected TEXT[],
    improvements TEXT[],

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Indexes
    CONSTRAINT fk_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

CREATE INDEX idx_pdca_cycles_workflow ON pdca_cycles(workflow_id);
CREATE INDEX idx_pdca_cycles_module ON pdca_cycles(module);
CREATE INDEX idx_pdca_cycles_tenant ON pdca_cycles(tenant_id);
CREATE INDEX idx_pdca_cycles_completed ON pdca_cycles(cycle_completed_at) WHERE cycle_completed_at IS NOT NULL;

-- RLS policies
ALTER TABLE pdca_cycles ENABLE ROW LEVEL SECURITY;

CREATE POLICY pdca_cycles_tenant_isolation ON pdca_cycles
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);
```

---

### 3. **Real Quality Scores**

```python
async def _get_case_quality_score(self, case_id: str) -> float:
    """Get real quality score from peer reviews"""

    result = await self.db.execute(
        text("""
            SELECT AVG(quality_score) as avg_score
            FROM community_intelligence.peer_reviews
            WHERE case_id = :case_id
            AND status = 'approved'
        """),
        {"case_id": case_id}
    )

    score = result.scalar()
    return score if score else 7.0  # Default if no reviews
```

---

### 4. **Real Benchmarks from PostgreSQL**

```python
async def _get_benchmarks(self, module: str, final_data: Dict) -> Dict[str, float]:
    """Get benchmarks from PostgreSQL history"""

    result = await self.db.execute(
        text("""
            SELECT
                AVG(do_duration) as avg_duration,
                MIN(do_duration) as min_duration,
                MAX(do_duration) as max_duration,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY do_duration) as median_duration,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY do_duration) as p95_duration
            FROM workflow_intelligence.pdca_cycles
            WHERE module = :module
            AND cycle_completed_at IS NOT NULL
            AND cycle_completed_at > NOW() - INTERVAL '90 days'  -- Last 90 days
            AND tenant_id = :tenant_id
        """),
        {"module": module, "tenant_id": current_tenant_id}
    )

    row = result.fetchone()

    return {
        "avg_duration": row.avg_duration or 0,
        "min_duration": row.min_duration or 0,
        "max_duration": row.max_duration or 0,
        "median_duration": row.median_duration or 0,
        "p95_duration": row.p95_duration or 0,
        "sample_size": row.count or 0
    }
```

---

### 5. **Save to PostgreSQL**

```python
async def _save_cycle_to_db(self, cycle: PDCACycleData):
    """Save completed cycle to PostgreSQL"""

    await self.db.execute(
        text("""
            INSERT INTO workflow_intelligence.pdca_cycles (
                workflow_id, module, tenant_id,
                cycle_started_at, cycle_completed_at, do_duration,
                plan_data, plan_recommendations, expected_outcomes, estimated_duration,
                do_data,
                check_data, deviations, benchmarks, quality_score,
                lessons_learned, patterns_detected, improvements
            ) VALUES (
                :workflow_id, :module, :tenant_id,
                :cycle_started_at, :cycle_completed_at, :do_duration,
                :plan_data, :plan_recommendations, :expected_outcomes, :estimated_duration,
                :do_data,
                :check_data, :deviations, :benchmarks, :quality_score,
                :lessons_learned, :patterns_detected, :improvements
            )
        """),
        {
            "workflow_id": cycle.workflow_id,
            "module": cycle.module,
            "tenant_id": current_tenant_id,
            "cycle_started_at": cycle.cycle_started_at,
            "cycle_completed_at": cycle.cycle_completed_at,
            "do_duration": cycle.do_duration,
            "plan_data": json.dumps(cycle.plan_data),
            "plan_recommendations": cycle.plan_recommendations,
            "expected_outcomes": json.dumps(cycle.plan_data.get("expected_outcomes")),
            "estimated_duration": cycle.plan_data.get("estimated_duration"),
            "do_data": json.dumps(cycle.do_data),
            "check_data": json.dumps(cycle.check_data),
            "deviations": cycle.deviations,
            "benchmarks": json.dumps(cycle.benchmarks),
            "quality_score": cycle.check_data.get("score") if cycle.check_data else None,
            "lessons_learned": cycle.lessons_learned,
            "patterns_detected": cycle.patterns_detected,
            "improvements": cycle.improvements
        }
    )

    await self.db.commit()
```

---

## 📋 PRIORITY FIX LIST

### Phase 1: Critical (Must Have)
1. ✅ Make Case Library required (remove optional check)
2. ✅ Make Knowledge Base required
3. ✅ Make Pattern Detector required
4. ✅ Create PostgreSQL schema (pdca_cycles table)
5. ✅ Save cycles to PostgreSQL
6. ✅ Load benchmarks from PostgreSQL

### Phase 2: Important (Should Have)
7. ✅ Real quality scores from peer_reviews
8. ✅ Prerequisite checking with real state
9. ✅ Use Predictive Engine for outcome prediction
10. ✅ Structured JSON from LLM recommendations

### Phase 3: Nice to Have
11. ✅ ML-based prediction (not just average)
12. ✅ Confidence intervals
13. ✅ Context-weighted recommendations
14. ✅ Advanced pattern detection

---

## 🎯 CONCLUSION

**Current State**:
- 8 mocks/fallbacks
- 3 optional dependencies (should be required)
- No persistence (in-memory only)
- Simplified algorithms

**Target State**:
- 0 mocks
- All dependencies required
- PostgreSQL persistence
- Real ML algorithms

**Effort**: ~8-12 hours to fix all mocks properly
