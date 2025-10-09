# 🔄 Unified Architecture Reconciliation

**Date:** 2025-10-05
**Status:** Reconciliation Plan
**Purpose:** Объединить 3 архитектурных решения в единое целое

---

## 📊 Проблема

Есть **3 разных архитектурных документа** с пересекающимися решениями:

1. **FINAL_ARCHITECTURE_DECISION.md** - expertise-center + domains
2. **PLUGIN_ARCHITECTURE_IMPLEMENTATION_PLAN.md** - platform-core + ai-intelligence + domains
3. **Текущее состояние** - platform-core/workflow уже реализован

**Результат:** Неясно, какой структуре следовать.

---

## ✅ Решение: Гибридная Архитектура

### Объединяем лучшее из всех 3 подходов:

```
AI-Platform-ISO/
│
├── intelligent-core/
│   │
│   ├── platform-core/              # Layer 1 (РЕАЛИЗОВАНО ✅)
│   │   ├── workflow/               # ✅ unified-workflow (4040 lines)
│   │   ├── case-library/           # ← workflow_intelligence/case_library
│   │   ├── learning/               # ← learning-system
│   │   └── coordination/           # ← coordination-center
│   │
│   ├── expertise-center/           # Layer 2 (НОВОЕ - ОБЪЕДИНЕНИЕ!)
│   │   │
│   │   ├── core/                   # Chief + Managers
│   │   │   ├── chief_executive.py  # ← ai_platform/chief + ai-office/coordinator
│   │   │   ├── governance_manager.py
│   │   │   ├── platform_manager.py
│   │   │   └── domain_manager.py
│   │   │
│   │   ├── shared/                 # Shared AI Infrastructure
│   │   │   ├── base/               # Base classes
│   │   │   │   ├── base_domain.py
│   │   │   │   ├── base_expert.py
│   │   │   │   ├── base_tool.py
│   │   │   │   └── base_organ.py
│   │   │   │
│   │   │   ├── rag/                # RAG Pipeline (merge!)
│   │   │   │   ├── pipeline.py     # ← ai-office/core/rag + ai_experts/rag
│   │   │   │   ├── retrieval.py
│   │   │   │   └── embeddings.py
│   │   │   │
│   │   │   ├── ml/                 # ML Infrastructure
│   │   │   │   ├── predictive.py   # ← ai_experts/ml
│   │   │   │   └── training.py
│   │   │   │
│   │   │   └── learning/           # Self-Learning
│   │   │       ├── meta_learning.py  # ← ai-office/core/learning
│   │   │       └── pattern_extraction.py
│   │   │
│   │   ├── domains/                # Domain Plugins
│   │   │   │
│   │   │   └── bcm/                # BCM Domain
│   │   │       │
│   │   │       ├── domain_config.py  # Plugin registration
│   │   │       │
│   │   │       ├── experts/        # AI Colleagues (7)
│   │   │       │   ├── bia_specialist.py       # ← ai-office/colleagues
│   │   │       │   ├── risk_analyst.py
│   │   │       │   ├── compliance_auditor.py
│   │   │       │   ├── project_manager.py
│   │   │       │   ├── incident_expert.py
│   │   │       │   ├── exercise_designer.py
│   │   │       │   └── plan_generator.py
│   │   │       │
│   │   │       ├── organs/         # AI Organs (10)
│   │   │       │   ├── governance_brain.py     # ← ai-office/organs
│   │   │       │   ├── emergency_response.py
│   │   │       │   ├── impact_oracle.py
│   │   │       │   ├── scenario_creator.py
│   │   │       │   ├── risk_advisor.py
│   │   │       │   ├── compliance_guardian.py
│   │   │       │   ├── performance_analyst.py
│   │   │       │   ├── learning_coach.py
│   │   │       │   ├── plan_generator_organ.py
│   │   │       │   └── lifecycle_monitor.py
│   │   │       │
│   │   │       ├── tools/          # Structured Tools
│   │   │       │   ├── bia_tools.py            # ← ai_experts/tools
│   │   │       │   ├── risk_tools.py
│   │   │       │   └── compliance_tools.py
│   │   │       │
│   │   │       ├── knowledge/      # Domain Knowledge
│   │   │       │   ├── iso22301/               # ← ai_experts/knowledge
│   │   │       │   ├── bci_gpg/
│   │   │       │   └── knowledge_graph.py
│   │   │       │
│   │   │       └── services/       # REST API Services
│   │   │           ├── bia-service/            # ← platform-services
│   │   │           ├── risk-service/
│   │   │           ├── compliance-service/
│   │   │           └── document-service/       # НОВОЕ! (для портала)
│   │   │
│   │   └── api/                    # Expertise Center API
│   │       └── main.py
│   │
│   └── ai-orchestration/           # MEGA-BRAIN (не трогаем)
│
├── human-interface/                # Web Portal (существует!)
│   ├── web-app/                    # Next.js frontend ✅
│   └── api-gateway/                # BFF (backend for frontend) ✅
│
└── infrastructure/                 # Infrastructure (не меняется)
```

---

## 🎯 Ключевые Решения

### 1. Naming Convention

**Выбираем:**
- ✅ `expertise-center/` (из FINAL_ARCHITECTURE_DECISION)
  - **Почему:** более понятное имя чем "ai-intelligence"
  - Содержит: Chief, Managers, Shared AI, Domains

**НЕ используем:**
- ❌ `ai-intelligence/` (слишком generic)
- ❌ `ai_platform/` (старое название)

---

### 2. Layer Structure

**Layer 1: Platform Core** (domain-agnostic functions)
- ✅ Уже реализован: `platform-core/workflow/`
- Добавить: case-library, learning, coordination

**Layer 2: Expertise Center** (AI intelligence)
- Chief Executive (orchestrates experts)
- Shared AI (RAG, ML, Learning)
- Domain Plugins (BCM, HR future, Finance future)

**Layer 3: Infrastructure**
- Database (Supabase)
- Redis (caching)
- Event Bus
- Monitoring

---

### 3. BCM Domain Structure

**Объединяем:**
- **Experts** (7 AI colleagues) ← from ai-office/ВСМ-colleagues
- **Organs** (10 AI processors) ← from ai-office/organs
- **Tools** (structured operations) ← from ai_experts/tools
- **Knowledge** (ISO 22301, BCI GPG) ← from ai_experts/knowledge
- **Services** (REST APIs) ← from platform-services

**Все вместе** = BCM Domain Plugin

---

### 4. Separation of Concerns

**Intelligence vs Services:**

```
User Request: "How to conduct BIA for hospital?"
         ↓
expertise-center/core/chief_executive.py  (routes to expert)
         ↓
domains/bcm/experts/bia_specialist.py  (AI reasoning)
         ↓ (consults)
domains/bcm/organs/impact_oracle.py  (heavy analysis)
         ↓ (uses RAG)
expertise-center/shared/rag/pipeline.py  (retrieves knowledge)
         ↓ (calls API)
domains/bcm/services/bia-service/  (creates BIA in DB)
```

**Key Point:**
- **Experts = Intelligence** (reasoning, advice)
- **Services = CRUD** (data management)
- **Services НЕ содержат AI логику!**

---

## 📋 Migration Plan

### Phase 1: Foundation (COMPLETED ✅)
- [x] Create `platform-core/workflow/`
- [x] Move unified-workflow
- [x] Archive bpmn-workflow

### Phase 2: Expertise Center Structure (NEW)
**Duration:** 2 days

**Step 2.1:** Create expertise-center structure
```bash
mkdir -p intelligent-core/expertise-center/{core,shared,domains,api}
mkdir -p intelligent-core/expertise-center/shared/{base,rag,ml,learning}
```

**Step 2.2:** Move Chief and Managers
```bash
# Chief from ai_platform
cp -r intelligent-core/ai_platform/chief → expertise-center/core/

# Managers from ai_platform
cp -r intelligent-core/ai_platform/managers → expertise-center/core/
```

**Step 2.3:** Merge Shared AI components
```bash
# RAG - merge from 2 sources
cp -r intelligent-core/ai-office/core/rag → expertise-center/shared/rag/
cp -r intelligent-core/ai_experts/rag/* → expertise-center/shared/rag/
# Manual merge conflicts

# ML
cp -r intelligent-core/ai_experts/ml → expertise-center/shared/ml/

# Learning
cp -r intelligent-core/ai-office/core/learning → expertise-center/shared/learning/
```

**Step 2.4:** Create Base classes
```bash
# Move from ai_platform/shared/base
cp -r intelligent-core/ai_platform/shared/base → expertise-center/shared/base/

# Add new: base_domain.py, base_organ.py
```

---

### Phase 3: BCM Domain Migration (NEW)
**Duration:** 3 days

**Step 3.1:** Create BCM domain structure
```bash
mkdir -p intelligent-core/expertise-center/domains/bcm/{experts,organs,tools,knowledge,services}
```

**Step 3.2:** Move Experts (AI Colleagues)
```bash
# From ai-office/ВСМ-colleagues
cp -r intelligent-core/ai-office/ВСМ-colleagues/* → expertise-center/domains/bcm/experts/

# Rename files:
# compliance_copilot.py → compliance_auditor.py
# bia_specialist_ai.py → bia_specialist.py
```

**Step 3.3:** Move Organs
```bash
# From ai-office/organs
cp -r intelligent-core/ai-office/organs/* → expertise-center/domains/bcm/organs/
```

**Step 3.4:** Move Tools
```bash
# From ai_experts/tools
cp -r intelligent-core/ai_experts/tools/* → expertise-center/domains/bcm/tools/
```

**Step 3.5:** Move Knowledge
```bash
# From ai_experts/knowledge
cp -r intelligent-core/ai_experts/knowledge/* → expertise-center/domains/bcm/knowledge/
```

**Step 3.6:** Move Services
```bash
# From platform-services
mv platform-services/* → expertise-center/domains/bcm/services/
```

**Step 3.7:** Create BCM Domain Config
```bash
# Create domains/bcm/domain_config.py
# Implement BCMDomain class (registers all experts, tools, organs)
```

---

### Phase 4: Web Portal Integration (NEW)
**Duration:** 2 days

**Step 4.1:** Create Document Service
```bash
mkdir -p expertise-center/domains/bcm/services/document-service
```

**Features:**
- Upload documents (PDF, DOCX, TXT)
- Store in Supabase storage
- Trigger AI analysis via Chief Executive
- Return parsed results

**Step 4.2:** Update API Gateway
```python
# human-interface/api-gateway/main.py

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile):
    # 1. Save to Supabase storage
    # 2. Send to Document Expert
    # 3. Return analysis results
    pass

@app.post("/api/ai/chat")
async def chat(message: str):
    # Route to Chief Executive
    # Return expert response
    pass
```

**Step 4.3:** Update Web App
```typescript
// human-interface/web-app/src/app/documents/page.tsx

export default function Documents() {
  const handleUpload = async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch('/api/documents/upload', {
      method: 'POST',
      body: formData
    })

    const analysis = await response.json()
    // Display AI analysis results
  }

  return (
    <DocumentUploader onUpload={handleUpload} />
  )
}
```

---

### Phase 5: Testing & Validation
**Duration:** 2 days

**Tests:**
1. Platform loads with BCM domain
2. Chief Executive routes to correct expert
3. Expert uses correct organs and tools
4. RAG retrieves ISO 22301 knowledge
5. Service creates BIA in database
6. Web portal uploads document
7. Document analysis returns results

---

## 🌐 Web Portal Architecture

### Current State (EXISTS ✅)

```
human-interface/
├── web-app/              # Next.js (TypeScript + Tailwind)
│   ├── src/app/
│   │   ├── page.tsx      # Dashboard (mock data)
│   │   └── layout.tsx
│   └── package.json
│
└── api-gateway/          # FastAPI (Python)
    └── main.py           # Routes (stub)
```

### Target State (TO IMPLEMENT)

```
Web Browser
     ↓
Next.js Web App (port 3000)
     ↓ (API calls)
API Gateway (port 8000)
     ↓ (routes to)
┌─────────────────────────────────────┐
│ Expertise Center API (port 8031)    │
│   ↓ Chief Executive                 │
│   ↓ Domain Manager                  │
│   ↓ BCM Experts                     │
└─────────────────────────────────────┘
     ↓ (calls)
┌─────────────────────────────────────┐
│ BCM Services (various ports)        │
│   - BIA Service (8001)              │
│   - Risk Service (8002)             │
│   - Document Service (8003) NEW!   │
└─────────────────────────────────────┘
     ↓ (persists)
Supabase PostgreSQL
```

### Document Workflow

```
User uploads PDF document (BCM policy)
         ↓
Web App → API Gateway → Document Service
         ↓
Document Service saves to Supabase Storage
         ↓
Document Service → Chief Executive
         ↓
Chief Executive → Documentation Expert (BCM domain)
         ↓
Documentation Expert → RAG Pipeline (parse document)
         ↓
RAG Pipeline → Vector embeddings → Supabase pgvector
         ↓
Documentation Expert returns:
  - Document type (policy, procedure, plan)
  - Key sections identified
  - ISO 22301 compliance gaps
  - Recommendations
         ↓
Results displayed in Web App
```

---

## 📚 Documentation Cleanup Plan

### Keep (3 files):

1. **PLATFORM_SPECIFICATION.md** (NEW - create)
   - Current architecture diagram
   - Layer structure
   - Component descriptions
   - API endpoints
   - Database schema
   - Technology stack

2. **DEVELOPMENT_ROADMAP.md** (NEW - create)
   - What's implemented (with ✅)
   - What's missing (with ⚠️)
   - Known weaknesses
   - Future enhancements
   - Priority order

3. **QUICK_START.md** (NEW - create)
   - Installation instructions
   - Environment setup
   - Run services
   - Test queries
   - Common issues

### Archive (all others):

```bash
mkdir -p _archive/old_architecture_docs/
mv *ARCHITECTURE*.md → _archive/old_architecture_docs/
mv PLUGIN_*.md → _archive/old_architecture_docs/
mv AI_*_ARCHITECTURE*.md → _archive/old_architecture_docs/

# Keep only:
# - PLATFORM_SPECIFICATION.md
# - DEVELOPMENT_ROADMAP.md
# - QUICK_START.md
```

---

## ⚠️ Current Weaknesses & Gaps

### 1. Missing Components

**Not Implemented:**
- [ ] Document Service (для портала)
- [ ] Document Expert (AI colleague #8)
- [ ] Full RAG merge (2 sources: ai-office + ai_experts)
- [ ] Web portal → Backend integration
- [ ] Authentication (Supabase Auth)
- [ ] Multi-tenancy enforcement

### 2. Partially Implemented

**Incomplete:**
- ⚠️ Chief Executive (exists but не роутит к BCM experts)
- ⚠️ Domain Manager (exists but не загружает domains)
- ⚠️ BCM Experts (scattered: ai-office, ai_platform, ai_experts)
- ⚠️ RAG Pipeline (2 versions exist, not merged)

### 3. Technical Debt

**Issues:**
- 🔴 33+ architecture documents (confusing!)
- 🔴 No unified import structure
- 🔴 Circular dependencies possible
- 🔴 No integration tests
- 🔴 Services не используют Coordination Center

---

## 🎯 Priority Order

### P0 (Critical - Week 1)
1. Create expertise-center structure
2. Move BCM experts to domains/bcm/
3. Merge RAG pipelines
4. Create BCMDomain config
5. Clean up documentation

### P1 (High - Week 2)
1. Create Document Service
2. Implement Chief → Expert routing
3. Web portal integration
4. Authentication setup

### P2 (Medium - Week 3)
1. Integration tests
2. Multi-tenancy
3. Performance optimization

### P3 (Nice to have - Week 4+)
1. Additional domains (HR, Finance)
2. Advanced analytics
3. Mobile app

---

## ✅ Success Criteria

**Must Have:**
1. Single clear architecture (expertise-center)
2. BCM domain plugin working
3. Web portal uploads documents
4. AI analysis returns results
5. 3 documentation files only

**Should Have:**
1. All 7 experts + 10 organs in BCM domain
2. RAG pipeline merged and working
3. Chief Executive routes correctly
4. Integration tests passing

**Nice to Have:**
1. Domain switching (BCM → HR)
2. Multi-tenancy working
3. Performance benchmarks

---

## 🚀 Next Steps

1. **Review this plan** with team
2. **Get approval** on naming (expertise-center)
3. **Start Phase 2** - create structure
4. **Daily sync** - avoid conflicts
5. **Test early** - integration tests

---

**Ready to proceed?**
