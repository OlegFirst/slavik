# SDLC ROADMAP: Что делать дальше по стандартам разработки

**Дата**: 2025-10-09
**Цель**: Определить следующие шаги согласно Software Development Life Cycle

---

## 📍 ГДЕ МЫ СЕЙЧАС

### Текущий статус проекта

```
✅ ЧТО УЖЕ ЕСТЬ:

1. VISION & CONCEPT
   ✅ LIVING_SYSTEM_ARCHITECTURE.md - философия и архитектура
   ✅ Концепция "живой системы"
   ✅ 7 базовых инстинктов
   ✅ Общая идея платформы

2. ARCHITECTURE (Высокоуровневая)
   ✅ Модульная структура (intelligent-core, platform-services, infrastructure)
   ✅ EventBus для интеграции
   ✅ Базовые сервисы (BIA, Risk, Planning и т.д.)
   ✅ Каталоги с кодом (Python/TypeScript)

3. BUSINESS FLOWS (в /interface/)
   ✅ USER JOURNEYS - описания персон и путей
   ✅ BUSINESS FLOWS - бизнес-процессы
   ✅ UI/UX спецификации (частично)

4. BACKEND CODE (частично реализован)
   ✅ Некоторые сервисы написаны
   ✅ EventBus есть
   ✅ База данных (Supabase)

❌ ЧЕГО НЕТ (критично для разработки):

1. FUNCTIONAL REQUIREMENTS (SRS - Software Requirements Specification)
   ❌ Четкие функциональные требования
   ❌ Use Cases в формальном виде
   ❌ Acceptance Criteria для каждой фичи
   ❌ Приоритизация требований (MoSCoW)

2. TECHNICAL DESIGN DOCUMENTS
   ❌ Detailed Design (компоненты, классы, методы)
   ❌ API Specification (OpenAPI/Swagger)
   ❌ Database Schema (DDL, ER-диаграммы)
   ❌ Interface Design (UI components, states)

3. PROJECT MANAGEMENT
   ❌ Backlog (список задач)
   ❌ Sprint planning
   ❌ Definition of Done
   ❌ Testing strategy
```

---

## 🎯 ЧТО НУЖНО СДЕЛАТЬ СЕЙЧАС (по стандарту)

### Стандартный SDLC Process:

```
1. Requirements Gathering ← ВЫ ЗДЕСЬ СЕЙЧАС
2. Requirements Analysis
3. System Design
4. Implementation
5. Testing
6. Deployment
7. Maintenance
```

### Следующий шаг: REQUIREMENTS SPECIFICATION

---

## 📋 ПЛАН ДЕЙСТВИЙ (практический)

### Этап 1: SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

**Что это:**
Формальный документ с **ЧЕТКИМИ требованиями** к системе.

**Что должно быть:**

```markdown
# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## 1. INTRODUCTION
   1.1 Purpose
   1.2 Scope
   1.3 Definitions
   1.4 References

## 2. OVERALL DESCRIPTION
   2.1 Product Perspective
   2.2 Product Functions
   2.3 User Classes and Characteristics
   2.4 Operating Environment
   2.5 Constraints

## 3. FUNCTIONAL REQUIREMENTS
   3.1 User Management
       FR-001: User Registration
       FR-002: User Login
       FR-003: Password Recovery
       ...

   3.2 Gap Analysis Module
       FR-101: Questionnaire Generation
       FR-102: Answer Collection
       FR-103: Compliance Calculation
       FR-104: Report Generation
       ...

   3.3 BIA Module
       FR-201: Process Identification
       FR-202: Dependency Mapping
       FR-203: RTO/RPO Calculation
       ...

## 4. NON-FUNCTIONAL REQUIREMENTS
   NFR-001: Performance (response time <2 sec)
   NFR-002: Scalability (support 10K concurrent users)
   NFR-003: Security (data encryption, GDPR)
   NFR-004: Availability (99.9% uptime)
   ...

## 5. USE CASES
   UC-001: User completes Gap Analysis
   UC-002: User generates BIA report
   UC-003: Auditor analyzes documents
   ...

## 6. ACCEPTANCE CRITERIA
   For each FR: Given/When/Then scenarios
```

**Формат каждого требования:**

```
FR-101: AI Questionnaire Generation

Description:
System SHALL generate personalized questionnaire based on organization profile.

Inputs:
- Organization type (e.g., Hospital)
- Size (number of employees)
- Industry

Processing:
1. Load Knowledge Base (347+ cases)
2. Find similar organizations
3. Generate 15 adaptive questions
4. Pre-fill likely answers

Outputs:
- Questionnaire object (15 questions)
- Estimated completion time

Acceptance Criteria:
GIVEN user completes org profile
WHEN user starts Gap Analysis
THEN system generates questionnaire in <30 seconds
AND questionnaire contains 12-18 questions
AND questions are relevant to industry
AND AI pre-fills ≥50% of answers

Priority: MUST (P0)
Complexity: Medium
Dependencies: Knowledge Base, AI Engine
```

---

### Этап 2: SYSTEM DESIGN SPECIFICATION (SDS)

**Что это:**
Техническое описание КАК реализовать требования.

**Что должно быть:**

```markdown
# SYSTEM DESIGN SPECIFICATION (SDS)

## 1. ARCHITECTURE DESIGN
   1.1 High-Level Architecture (C4 diagrams)
   1.2 Component Diagram
   1.3 Deployment Diagram
   1.4 Technology Stack

## 2. DATABASE DESIGN
   2.1 ER Diagram
   2.2 Schema (DDL)
   2.3 Indexes
   2.4 Migrations

## 3. API DESIGN
   3.1 REST API Endpoints (OpenAPI)
   3.2 GraphQL Schema
   3.3 WebSocket Events
   3.4 Authentication/Authorization

## 4. UI/UX DESIGN
   4.1 Wireframes
   4.2 User Flows
   4.3 Component Library
   4.4 Design System (colors, typography)

## 5. AI INTEGRATION
   5.1 Claude API usage
   5.2 Prompt engineering
   5.3 Context management
   5.4 Fallback strategies

## 6. INFRASTRUCTURE
   6.1 Supabase configuration
   6.2 Deployment pipeline
   6.3 Monitoring & logging
   6.4 Backup & recovery
```

---

### Этап 3: BACKLOG & SPRINT PLANNING

**Что это:**
Разбить требования на задачи для разработки.

**Формат:**

```
EPIC: Gap Analysis Module

User Story 1: As a BCM Manager, I want to complete org profile,
              so that AI can generate personalized questionnaire

Tasks:
├─ TASK-001: Design org profile form (UI)
├─ TASK-002: Create Supabase table `organizations`
├─ TASK-003: Implement POST /api/organizations endpoint
├─ TASK-004: Add form validation (frontend)
├─ TASK-005: Write integration tests
└─ TASK-006: Deploy to staging

Acceptance Criteria:
- User can fill org profile in <2 minutes
- Data is saved to database
- Validation prevents invalid inputs
- All tests pass

Story Points: 5
Priority: P0 (Must Have)
Sprint: Sprint 1
```

---

## 🚀 ПРАКТИЧЕСКИЙ ПЛАН (ближайшие шаги)

### ШАГ 1: Выбрать ОДИН модуль для старта (2 часа)

**Рекомендация**: Начните с **Gap Analysis** (самый простой и важный).

**Что делать:**
```
1. Открыть существующие USER JOURNEYS
2. Взять сценарий "Gap Analysis"
3. Выписать ВСЕ функциональные требования
4. Для каждого требования написать:
   - ID (FR-001, FR-002, ...)
   - Description
   - Inputs/Outputs
   - Acceptance Criteria
   - Priority (P0/P1/P2)
```

**Пример выхода:**
```
FR-001: Organization Profile Creation
FR-002: Industry Selection
FR-003: Size Input Validation
FR-004: AI Questionnaire Generation
FR-005: Adaptive Question Flow
FR-006: Answer Auto-Save
FR-007: Compliance Score Calculation
FR-008: Gap Report Generation
FR-009: PDF Export
FR-010: Roadmap Visualization
```

---

### ШАГ 2: Database Schema для этого модуля (2 часа)

**Что делать:**
```sql
-- Создать DDL для Gap Analysis

CREATE TABLE organizations (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  industry VARCHAR(100),
  size INTEGER,
  country VARCHAR(2),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE gap_analyses (
  id UUID PRIMARY KEY,
  organization_id UUID REFERENCES organizations(id),
  status VARCHAR(50), -- 'in_progress', 'completed'
  compliance_score INTEGER, -- 0-100
  created_at TIMESTAMP,
  completed_at TIMESTAMP
);

CREATE TABLE gap_answers (
  id UUID PRIMARY KEY,
  gap_analysis_id UUID REFERENCES gap_analyses(id),
  question_id VARCHAR(50),
  answer TEXT,
  answered_at TIMESTAMP
);

CREATE TABLE gap_findings (
  id UUID PRIMARY KEY,
  gap_analysis_id UUID REFERENCES gap_analyses(id),
  clause VARCHAR(10), -- e.g., "4.1", "5.2"
  status VARCHAR(50), -- 'compliant', 'gap', 'partial'
  description TEXT,
  priority VARCHAR(10) -- 'critical', 'high', 'medium', 'low'
);
```

---

### ШАГ 3: API Specification (OpenAPI) (2 часа)

**Что делать:**
```yaml
# openapi.yaml

openapi: 3.0.0
info:
  title: AI-Platform-ISO API
  version: 1.0.0

paths:
  /api/organizations:
    post:
      summary: Create organization profile
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                  example: "City Hospital"
                industry:
                  type: string
                  enum: [healthcare, finance, it, manufacturing]
                size:
                  type: integer
                  minimum: 1
                  example: 450
      responses:
        201:
          description: Organization created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Organization'

  /api/gap-analysis:
    post:
      summary: Start Gap Analysis
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                organization_id:
                  type: string
                  format: uuid
      responses:
        201:
          description: Gap Analysis started
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GapAnalysis'

  /api/gap-analysis/{id}/questionnaire:
    get:
      summary: Get AI-generated questionnaire
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        200:
          description: Questionnaire generated
          content:
            application/json:
              schema:
                type: object
                properties:
                  questions:
                    type: array
                    items:
                      $ref: '#/components/schemas/Question'
```

---

### ШАГ 4: UI Wireframes (1 день)

**Что делать:**
Нарисовать простые макеты (можно в Excalidraw, Figma, или даже ASCII):

```
┌─────────────────────────────────────────┐
│ Gap Analysis - Organization Profile    │
├─────────────────────────────────────────┤
│                                         │
│ Organization Name:                      │
│ [_____________________________]         │
│                                         │
│ Industry:                               │
│ [v Healthcare          ▼]               │
│                                         │
│ Number of Employees:                    │
│ [_____]                                 │
│                                         │
│ Country:                                │
│ [v Ukraine             ▼]               │
│                                         │
│               [Next →]                  │
│                                         │
└─────────────────────────────────────────┘

↓ (user clicks Next)

┌─────────────────────────────────────────┐
│ Gap Analysis - Question 1 of 15        │
├─────────────────────────────────────────┤
│ Progress: [███░░░░░░░░░░░] 7%          │
│                                         │
│ Question 1: Organizational Context      │
│                                         │
│ Do you have a designated BCM Manager?   │
│                                         │
│ ○ Yes, full-time BCM role               │
│ ● Yes, combined with other duties       │
│ ○ Yes, another person                   │
│ ○ No, not yet assigned                  │
│                                         │
│ 💡 AI Tip: 78% of similar hospitals     │
│    combine BCM with quality/risk roles  │
│                                         │
│ [← Back]  [Skip]  [Next →]             │
└─────────────────────────────────────────┘
```

---

### ШАГ 5: Implementation Backlog (1 день)

**Что делать:**
Создать список задач в любом трекере (GitHub Issues, Linear, Jira, или просто Markdown):

```markdown
# Gap Analysis Module - Implementation Backlog

## Sprint 1: Foundation (Week 1)

### Backend
- [ ] TASK-001: Setup Supabase tables (organizations, gap_analyses, etc.)
- [ ] TASK-002: Create API endpoint POST /api/organizations
- [ ] TASK-003: Create API endpoint POST /api/gap-analysis
- [ ] TASK-004: Implement Claude API integration for questionnaire generation
- [ ] TASK-005: Write unit tests for API endpoints

### Frontend
- [ ] TASK-006: Create Organization Profile form (React component)
- [ ] TASK-007: Implement form validation
- [ ] TASK-008: Create Gap Analysis Wizard component
- [ ] TASK-009: Implement question navigation (Next/Back)
- [ ] TASK-010: Add auto-save functionality

### Integration
- [ ] TASK-011: Connect frontend to backend API
- [ ] TASK-012: Test end-to-end flow
- [ ] TASK-013: Deploy to staging environment

## Sprint 2: AI Enhancement (Week 2)

### Backend
- [ ] TASK-014: Implement adaptive question logic
- [ ] TASK-015: Add Knowledge Base integration
- [ ] TASK-016: Implement compliance score calculation
- [ ] TASK-017: Generate Gap Analysis report (JSON)

### Frontend
- [ ] TASK-018: Display AI tips/suggestions
- [ ] TASK-019: Show progress bar
- [ ] TASK-020: Create results page (compliance score)
- [ ] TASK-021: Visualize gaps (chart/table)

### Testing
- [ ] TASK-022: Integration tests
- [ ] TASK-023: User acceptance testing
- [ ] TASK-024: Performance testing (AI response time)
```

---

## 📚 РЕКОМЕНДУЕМЫЙ ФОРМАТ ДОКУМЕНТОВ

### Создайте структуру:

```
/docs/
├── requirements/
│   ├── SRS_GapAnalysis.md       ← Функциональные требования
│   ├── SRS_BIA.md
│   ├── SRS_BCP.md
│   └── NFR.md                    ← Нефункциональные требования
│
├── design/
│   ├── API_Specification.yaml   ← OpenAPI
│   ├── Database_Schema.sql      ← DDL
│   ├── Architecture.md          ← C4 diagrams
│   └── UI_Wireframes/           ← Figma/Excalidraw
│
├── backlog/
│   ├── Epics.md
│   ├── UserStories.md
│   └── Tasks.md
│
└── testing/
    ├── TestPlan.md
    ├── TestCases.md
    └── AcceptanceCriteria.md
```

---

## ✅ КОНКРЕТНЫЙ NEXT STEP (прямо сейчас)

**Рекомендация**: Начните с самого простого - **SRS для Gap Analysis**.

**Задание на 2-3 часа:**

1. Откройте `/Users/MD/AI-Platform-ISO/interface/BCM_SPECIALIST_COMPLETE_JOURNEY.md`
2. Найдите раздел про Gap Analysis
3. Выпишите ВСЕ функции (что система должна делать)
4. Для каждой функции создайте требование в формате:

```
FR-001: [Название]
Description: [Что делает]
Inputs: [Что на входе]
Outputs: [Что на выходе]
Acceptance Criteria: [Как проверить что работает]
Priority: P0/P1/P2
```

**Хотите чтобы я создал ПРИМЕР SRS для Gap Analysis модуля?**

Или вы хотите сами начать, а я помогу?