# BCM Tactical Assistants (AI Digital Colleagues)

**Total:** 12 Tactical Assistants
**Coverage:** 100% of platform-services
**Status:** ✅ Complete

---

## 📋 Overview

Tactical Assistants are AI Digital Colleagues that provide expert assistance for specific BCM modules. Each assistant is specialized in a particular domain and integrated with corresponding platform services.

---

## 🎯 Complete List

| # | Assistant | Platform Service | Integration | Status |
|---|-----------|-----------------|-------------|--------|
| 1 | **BIA Specialist** | bia-service | ✅ Direct | ✅ Complete |
| 2 | **Risk Analyst** | risk-service | ✅ Direct | ✅ Complete |
| 3 | **Compliance Copilot** | compliance-service | ✅ Direct | ✅ Complete |
| 4 | **Incident Advisor** | response-service | ✅ Direct | ✅ Complete |
| 5 | **Plan Generator** | plans_service, planning_service | ✅ Direct | ✅ Complete |
| 6 | **Project Manager** | General | ✅ Cross-module | ✅ Complete |
| 7 | **Exercise Designer** | validation-service | ✅ Direct | ✅ Complete |
| 8 | **Documents Specialist** | documents-service | ✅ + living-docs (8034) | ✅ NEW |
| 9 | **Governance Specialist** | governance-service | ✅ Direct | ✅ NEW |
| 10 | **Validation Specialist** | validation-service | ✅ Direct | ✅ NEW |
| 11 | **Community Specialist** | community-service | ✅ + community_intelligence (8030) + collective (8032) | ✅ NEW |
| 12 | **Learning Specialist** | learning-service | ✅ + learning-system (8033) | ✅ NEW |

---

## 🆕 Newly Created Assistants

### 1. Documents Specialist AI

**File:** `documents_specialist.py`
**Platform Service:** documents-service
**Special Integration:** living-docs service (port 8034)

**Specializes in:**
- Document lifecycle management
- Version control and approval workflows
- ISO 22301 documentation requirements
- Living Documentation (self-evolving docs)
- Document search and retrieval
- Templates and standardization

**Special Methods:**
```python
# Living Docs integration
await assistant.search_living_docs(query, user_id)
await assistant.get_living_doc(page_id, user_id, personalize=True)
await assistant.generate_example(topic, context)
```

**Configuration:**
```python
config = {
    "living_docs_url": "http://localhost:8034",
    "living_docs_enabled": True
}
```

---

### 2. Governance Specialist AI

**File:** `governance_specialist.py`
**Platform Service:** governance-service

**Specializes in:**
- BCMS governance framework design
- Roles and responsibilities (RACI matrices)
- BCM Policy development
- Stakeholder management
- Performance measurement and KPIs
- Management review

**Key Features:**
- ISO 22301 clause 5 (Leadership) expert
- RACI matrix generation
- KPI framework design
- Management review facilitation

---

### 3. Validation Specialist AI

**File:** `validation_specialist.py`
**Platform Service:** validation-service

**Specializes in:**
- BC plan validation and verification
- Exercise design (tabletop, simulation, full-scale)
- Test scenarios and success criteria
- After-action reviews
- Quality metrics and audit readiness

**Key Features:**
- ISO 22301 clause 8.5 (Testing) expert
- Exercise type recommendations
- SMART success criteria
- AAR (After-Action Review) structure

---

### 4. Community Specialist AI

**File:** `community_specialist.py`
**Platform Service:** community-service
**Special Integration:**
- community_intelligence (port 8030)
- collective (port 8032)

**Specializes in:**
- Community-driven knowledge creation
- Peer review coordination
- Reputation and gamification
- Case library management
- Collective intelligence facilitation

**Special Methods:**
```python
# Community Intelligence integration
await assistant.search_case_library(problem_type, context)
await assistant.request_collective_help(problem, org_context)
```

**Configuration:**
```python
config = {
    "community_intelligence_url": "http://localhost:8030",
    "collective_url": "http://localhost:8032"
}
```

---

### 5. Learning Specialist AI

**File:** `learning_specialist.py`
**Platform Service:** learning-service
**Special Integration:** learning-system (port 8033)

**Specializes in:**
- Training program design
- Competency tracking and assessment
- Learning analytics
- Gamification
- Knowledge gap analysis
- ML-powered predictions

**Special Methods:**
```python
# Learning System integration
await assistant.get_competency_profile(user_id)
await assistant.recommend_training(user_id, gap_analysis)
await assistant.predict_exercise_success(team_id, scenario_type)
```

**Configuration:**
```python
config = {
    "learning_system_url": "http://localhost:8033"
}
```

---

## 🔗 Service Integration Map

```
Tactical Assistants → Platform Services → AI Services

documents_specialist → documents-service → living-docs (8034)
governance_specialist → governance-service
validation_specialist → validation-service
community_specialist → community-service → community_intelligence (8030)
                                         → collective (8032)
learning_specialist → learning-service → learning-system (8033)
```

---

## 📖 Usage Example

```python
from expertise_center.domains.bcm.tactical_assistants import DocumentsSpecialistAI

# Initialize with RAG and config
assistant = DocumentsSpecialistAI(
    rag_pipeline=rag,
    config={
        "living_docs_url": "http://localhost:8034",
        "living_docs_enabled": True
    }
)

# Get assistance
response = await assistant.assist(
    query="How should I structure our BC Policy document?",
    context={
        "step": "policy_development",
        "description": "Developing first BCM policy for ISO 22301 certification"
    }
)

# Use living-docs integration
search_results = await assistant.search_living_docs(
    query="BC Policy examples",
    user_id="user-123"
)

# Generate AI example
example = await assistant.generate_example(
    topic="bc_policy_structure",
    context={
        "industry": "healthcare",
        "org_type": "hospital",
        "size": "medium"
    }
)
```

---

## 🚀 Deployment

### 1. Ensure Platform Services are Running

```bash
# Check platform services
docker-compose -f platform-services/docker-compose.yml ps

# Should see:
# - documents-service (running)
# - governance-service (running)
# - validation-service (running)
# - community-service (running)
# - learning-service (running)
```

### 2. Ensure AI Services are Running

```bash
# Check AI services
cd intelligent-core
docker-compose ps

# Should see:
# - living-docs (port 8034)
# - community_intelligence (port 8030)
# - collective (port 8032)
# - learning-system (port 8033)
```

### 3. Configuration

All assistants are configured through the expertise-center domain loader with service URLs:

```python
# expertise-center/config.py
TACTICAL_ASSISTANTS_CONFIG = {
    "living_docs_url": os.getenv("LIVING_DOCS_URL", "http://localhost:8034"),
    "community_intelligence_url": os.getenv("COMMUNITY_URL", "http://localhost:8030"),
    "collective_url": os.getenv("COLLECTIVE_URL", "http://localhost:8032"),
    "learning_system_url": os.getenv("LEARNING_URL", "http://localhost:8033"),
}
```

---

## 📊 Coverage Statistics

```
Platform Services: 12
Tactical Assistants: 12
Coverage: 100%

With AI Service Integration:
- living-docs: ✅ documents_specialist
- community_intelligence: ✅ community_specialist
- collective: ✅ community_specialist
- learning-system: ✅ learning_specialist
```

---

## 🎯 Next Steps

1. ✅ All 12 assistants created
2. ✅ Service integrations implemented
3. ⏳ Update expertise-center config with service URLs
4. ⏳ Add integration tests
5. ⏳ Deploy and verify connectivity

---

**Status:** ✅ Ready for Integration Testing

**Date:** 2025-10-06
