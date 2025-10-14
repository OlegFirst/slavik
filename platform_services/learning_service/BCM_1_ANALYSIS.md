# 📚 BCM_1 Learning Modules Analysis

**Date:** 2025-10-01
**Purpose:** Extract useful data before archiving BCM_1 learning-related modules

---

## 📦 Modules Analyzed

### 1. `/services/BCM_1/bcm_training` (250 lines total)

**Status:** ⚠️ **EXTRACT DATA BEFORE ARCHIVING**

**Files:**
- `models/models.py` - 18 lines (too simple, skip)
- `models/ai_learning_coach.py` - 230 lines ⭐ **USEFUL**
- `data/bcm_training_data.xml` - 12 lines (1 test record, skip)

#### ✅ What to Extract:

**1. Competency Areas (from ai_learning_coach.py):**
```python
competency_areas = [
    'incident_response',
    'business_continuity',
    'risk_assessment',
    'crisis_communication'
]
```

**2. Coaching Styles:**
```python
coaching_style = [
    ('adaptive', '🎯 Adaptive - Personalized Learning'),
    ('intensive', '🔥 Intensive - Accelerated Training'),
    ('supportive', '🤝 Supportive - Guided Learning'),
    ('challenging', '💪 Challenging - Advanced Training')
]
```

**3. Learning Plan Structure:**
```python
learning_plan = {
    'competency_area': str,
    'current_level': int (0-5),
    'target_level': int (0-5),
    'learning_modules': list,
    'estimated_duration': int (hours),
    'learning_style': str,
    'priority': str (low/medium/high/critical)
}
```

**4. Learning Metrics:**
- learners_coached (int)
- competency_improvements (float %)
- learning_acceleration (float factor)

**5. AI Integration Pattern (Phase 2):**
- Endpoint: `http://ai_orchestrator:8000/nlp/query`
- Context format for learning coach
- Personalized learning path generation

#### ❌ What NOT to use:
- Odoo ORM code
- Simple models.py
- XML views
- Test data

---

### 2. `/services/BCM_1/bcm_templates` (294 lines total)

**Status:** ⚠️ **EXTRACT DATA BEFORE ARCHIVING**

**Files:**
- `models/models.py` - 292 lines ⭐ **USEFUL**
- `data/bpmn_workflow_templates.xml` - 20KB ⚠️ **SKIP (for Exercise module)**

#### ✅ What to Extract:

**1. Template Categories:**
```python
category = [
    ('document', 'Document Template'),
    ('workflow', 'BPMN Workflow Template'),  # Skip - for Exercise
    ('form', 'Form Template'),
    ('checklist', 'Checklist Template'),
    ('report', 'Report Template')
]
```

**2. Training Template Types:**
```python
# Forms for learning
template_type = [
    ('bia_form', 'BIA Assessment Form'),
    ('risk_form', 'Risk Assessment Form'),
    ('exercise_form', 'Exercise Evaluation Form'),
    ('exercise_checklist', 'Exercise Checklist'),
    ('audit_checklist', 'Audit Checklist'),
]
```

**3. Template Fields:**
- name, description, notes
- content (HTML)
- form_schema (JSON)
- iso_clause (mapping)
- usage_count, last_used
- is_ai_enhanced, ai_prompt

#### ❌ What NOT to use:
- BPMN workflow templates (for Exercise module, not Learning)
- Odoo Many2many relations
- XML views

---

### 3. `/services/BCM_1/bcm_content_training_bridge` (3020 lines total) 🔥

**Status:** ⚠️ **VERY USEFUL - EXTRACT COMPREHENSIVE DATA**

**Files:**
- `models/bcm_scenario.py` - Large
- `models/ai_scenario_creator.py` - Large
- `models/gamification_bridge.py` - Large
- `models/digital_twin_scenario.py` - Large
- `models/bcm_tag.py`, `bcm_domain.py` - Metadata

#### ✅ What to Extract:

**1. Scenario Types (for training exercises):**
- Crisis scenarios
- Exercise scenarios
- Response playbooks
- Industry-specific scenarios

**2. Content Categories:**
- Policy templates
- Procedure templates
- Assessment forms
- Communication templates
- Training materials

**3. Gamification Elements:**
- Achievement tracking
- Progress badges
- Skill levels
- Learning challenges

**4. Rating & Review System:**
- Content ratings
- User reviews
- Community feedback
- Quality metrics

**5. AI Capabilities (Phase 2):**
- Content generation
- Auto-completion
- Compliance checking
- Scenario creation

#### ❌ What NOT to use:
- Odoo gamification integration (we'll use custom)
- Website slides integration (Odoo-specific)
- Calendar integration (separate module)
- BPMN workflows

---

### 4. `/services/BCM_1/bcm_exercise` (345 lines total)

**Status:** ⚠️ **SKIP FOR NOW (different module)**

**Reason:** Exercise module is ISO 22301 Clause 8.5, not Clause 7.2-7.3 (Learning)

**Exercise Types:**
- Tabletop exercises
- Functional exercises
- Full-scale simulations
- Drill exercises
- Orientation sessions

**Note:** Will need this data when creating Exercise module later.

---

### 5. `/services/BCM_1/bcm_plans` (893 lines total)

**Status:** ⚠️ **SKIP FOR NOW (different module)**

**Reason:** Plans module is ISO 22301 Clause 8.2-8.4, not Clause 7.2-7.3

**Plan Types:**
- Business Continuity Plans (BCP)
- Disaster Recovery Plans (DRP)
- Emergency Response Plans (ERP)
- Crisis Communication Plans
- Pandemic Response Plans
- Cyber Incident Response Plans

**Note:** Will need this when creating Plans module later.

---

### 6. `/services/BCM_1/bcm_reporting` (small)

**Status:** ✅ **SKIP (separate module)**

**Reason:** Cross-module analytics, not learning-specific

---

### 7. `/services/BCM_1/knowledge-base` (TypeScript)

**Status:** ✅ **ALREADY MIGRATED**

**Location:** `/services/knowledge-base/standards/ISO_22301/`

**Content:**
- ISO 22301 standard breakdown
- Clause requirements
- Audit questions
- Evidence needed

---

### 8. `/services/BCM_1/template_library` (empty)

**Status:** ✅ **SKIP (empty)**

---

## 📊 Summary: What to Extract

### Priority 1: Extract Now ⭐

**From bcm_training:**
1. Competency areas list → `learning/database/competency_seed.sql`
2. Coaching styles → Database enum
3. Learning plan structure → Database model
4. Metrics tracking → Database fields

**From bcm_templates:**
1. Template categories → Database enum
2. Training template types → Seed data
3. Template structure (content, form_schema) → Database model

**From bcm_content_training_bridge:**
1. Scenario types → Seed data
2. Content categories → Database
3. Rating/review system → Database models
4. Tag/domain system → Metadata tables

### Priority 2: Document for Phase 2 📝

1. AI Learning Coach integration patterns
2. Gamification elements
3. AI content generation
4. Scenario creation workflows

### Priority 3: Save for Other Modules 🗂️

**bcm_exercise (345 lines):**
- Exercise types, workflows
- For future Exercise module (Clause 8.5)

**bcm_plans (893 lines):**
- Plan types, components
- For future Plans module (Clause 8.2-8.4)

---

## 🎯 Action Plan

### Step 1: Extract Data ✅
- [x] Analyze all modules
- [ ] Create `learning/database/competency_seed.sql`
- [ ] Create `learning/database/training_templates_seed.sql`
- [ ] Document AI patterns in README

### Step 2: Archive Modules 🗄️

**Can archive NOW:**
- ✅ `/services/BCM_1/bcm_training` (after extraction)
- ✅ `/services/BCM_1/bcm_templates` (after extraction)
- ✅ `/services/BCM_1/bcm_content_training_bridge` (after extraction)

**DO NOT archive (needed later):**
- ⚠️ `/services/BCM_1/bcm_exercise` → for Exercise module
- ⚠️ `/services/BCM_1/bcm_plans` → for Plans module
- ⚠️ `/services/BCM_1/bcm_context` → for Context module

**Can archive (not needed):**
- ✅ `/services/BCM_1/bcm_reporting` → separate concern
- ✅ `/services/BCM_1/template_library` → empty
- ✅ `/services/BCM_1/knowledge-base` → already migrated

---

## 📋 Archive Checklist

### Before Archiving:
- [ ] Extract competency areas
- [ ] Extract template types
- [ ] Extract scenario categories
- [ ] Extract rating system structure
- [ ] Document AI integration patterns
- [ ] Create seed SQL files

### After Extraction:
```bash
mkdir -p /Users/MD/ISO-22301—копия/services/_archived/BCM_1/

# Archive learning-related (after extraction):
mv /Users/MD/ISO-22301—копия/services/BCM_1/bcm_training /Users/MD/ISO-22301—копия/services/_archived/BCM_1/
mv /Users/MD/ISO-22301—копия/services/BCM_1/bcm_templates /Users/MD/ISO-22301—копия/services/_archived/BCM_1/
mv /Users/MD/ISO-22301—копия/services/BCM_1/bcm_content_training_bridge /Users/MD/ISO-22301—копия/services/_archived/BCM_1/

# Archive not needed:
mv /Users/MD/ISO-22301—копия/services/BCM_1/bcm_reporting /Users/MD/ISO-22301—копия/services/_archived/BCM_1/
mv /Users/MD/ISO-22301—копия/services/BCM_1/template_library /Users/MD/ISO-22301—копия/services/_archived/BCM_1/
mv /Users/MD/ISO-22301—копия/services/BCM_1/knowledge-base /Users/MD/ISO-22301—копия/services/_archived/BCM_1/

# Archive governance (already extracted):
mv /Users/MD/ISO-22301—копия/services/BCM_1/bcm_governance /Users/MD/ISO-22301—копия/services/_archived/BCM_1/
```

### Keep for Later:
- `/services/BCM_1/bcm_exercise` → Exercise module
- `/services/BCM_1/bcm_plans` → Plans module
- `/services/BCM_1/bcm_context` → Context module

---

**Next Steps:**
1. Create seed data files
2. Move to archive
3. Start building Learning module

**Status:** Ready for extraction 🚀
