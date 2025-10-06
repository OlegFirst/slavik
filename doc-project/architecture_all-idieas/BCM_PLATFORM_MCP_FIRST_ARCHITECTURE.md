# BCM Platform: MCP-First Architecture

**Версия:** 1.0
**Дата:** 2025-10-03
**Статус:** Концепция

---

## 🎯 Общая Концепция

### Принцип разделения ответственности

**BCM Platform** = Бизнес-логика + Визуализация + Данные
**MCP Servers** = AI-анализ + Генерация + Валидация + Q&A

### Почему MCP-First?

1. **Separation of Concerns**: Платформа фокусируется на domain expertise (BCM процессы, ISO стандарты), AI — это подключаемые инструменты
2. **Standard Interface**: Пользователи работают в привычных AI интерфейсах (Claude Desktop, ChatGPT), нет необходимости изобретать свой chat UI
3. **Flexibility**: MCP servers можно менять/обновлять независимо от платформы
4. **Vendor Independence**: Не привязаны к конкретному LLM provider

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                    BCM PLATFORM (Web App)                       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  CORE UI LAYER                                           │  │
│  │  • BIA Canvas (ReactFlow - visual dependencies)          │  │
│  │  • Risk Matrix (interactive heatmap)                     │  │
│  │  • Document Editor (Tiptap - collaborative)              │  │
│  │  • Simulation Studio (scenario runner)                   │  │
│  │  • Compliance Dashboard (progress tracking)              │  │
│  │  • Gantt/Timeline (implementation roadmap)               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  EMBEDDED AI ASSISTANT (для работы в платформе)         │  │
│  │  • Sidebar chat (всегда доступен)                        │  │
│  │  • Context-aware (знает что пользователь сейчас делает)  │  │
│  │  • Quick actions ("Generate this section", "Audit doc")  │  │
│  │  • Uses same MCP backend (consistency)                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  BUSINESS LOGIC ENGINE                                   │  │
│  │  • Workflows (BIA → Strategy → Plans → Testing)          │  │
│  │  • Validation rules (RTO logic, compliance checks)       │  │
│  │  • Calculations (risk scores, timelines)                 │  │
│  │  • Notifications (deadlines, gaps, issues)               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  DATA LAYER                                              │  │
│  │  PostgreSQL: orgs, processes, risks, plans, exercises    │  │
│  │  MinIO/S3: documents, reports, audit trails              │  │
│  │  Redis: sessions, cache, real-time collaboration         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ REST API + WebSocket
                         │
           ┌─────────────┴──────────────┐
           │                            │
   ┌───────▼────────┐          ┌────────▼──────────┐
   │  MCP SERVERS   │          │  External Users   │
   │  (AI Experts)  │◄─────────┤  (Claude Desktop, │
   │                │  MCP     │   ChatGPT, etc)   │
   └────────────────┘          └───────────────────┘
```

---

## 📦 Компоненты Платформы

### 1. Core UI Layer

**Назначение:** Визуализация и интерактивное взаимодействие с BCM данными

**Компоненты:**

#### BIA Canvas (ReactFlow)
- Visual mapping бизнес-процессов
- Drag-and-drop процессов
- Автоматическое рисование dependencies (стрелки)
- Цветовая индикация (зеленый = OK, красный = gap в RTO)
- Click на процесс → детальный анализ

**Технологии:** React, ReactFlow, TailwindCSS

#### Risk Matrix (Interactive Heatmap)
- 5x5 matrix (likelihood × impact)
- Drag-and-drop рисков
- Автоматический расчет risk score
- Filters (by category, owner, status)
- Export to PDF/Excel

**Технологии:** React, D3.js или Recharts

#### Document Editor (Collaborative)
- Real-time collaboration (как Google Docs)
- Version control
- Comments и review workflow
- Templates (BC Plans, Policies, Procedures)
- Export to Word/PDF

**Технологии:** Tiptap, Y.js (CRDT), WebSocket

#### Simulation Studio
- Scenario selection (ransomware, flood, power outage...)
- Interactive timeline (что происходило по минутам)
- Decision points (пользователь выбирает действие)
- Results dashboard (RTO achieved?, issues found, recommendations)

**Технологии:** React, Custom state machine

#### Compliance Dashboard
- Progress tracking по ISO 22301 clauses
- Traffic lights (red/yellow/green)
- Gap analysis
- Action items with owners and deadlines

**Технологии:** React, Chart.js

#### Gantt/Timeline
- Implementation roadmap
- Milestones
- Dependencies between tasks
- Resource allocation

**Технологии:** React, dhtmlx-gantt или frappe-gantt

---

### 2. Embedded AI Assistant

**Назначение:** AI помощник для пользователей, работающих в платформе

**Функции:**

1. **Context-Aware Chat**
   - Знает на какой странице пользователь
   - Знает с каким документом/процессом работает
   - Проактивные подсказки

2. **Quick Actions**
   - "Recommend RTO" (для текущего процесса)
   - "Validate Document" (compliance check)
   - "Generate Missing Section" (в редакторе документов)
   - "Show Examples" (похожие кейсы)

3. **Smart Suggestions**
   - Замечает gaps (например, не определен RTO)
   - Предлагает improvements
   - Напоминает о deadlines

**Реализация:**
- Sidebar component (всегда видим)
- WebSocket connection для real-time
- Использует те же MCP endpoints что и external AI

---

### 3. Business Logic Engine

**Назначение:** Бизнес-правила и workflows (БЕЗ AI)

**Функции:**

#### Workflows
```
BIA → Risk Assessment → BC Strategy → BC Plans → Testing → Audit
```
- State machine для каждого workflow
- Validation rules на каждом шаге
- Notifications о следующих действиях

#### Validation Rules
- RTO logic: `RTO_downstream <= RTO_upstream`
- Plan completeness: required sections present?
- Compliance checks: ISO 22301 requirements met?

#### Calculations
- Risk score: `likelihood × impact`
- Timeline estimates: based on organization size
- Resource requirements: based on number of critical processes

#### Notifications
- Deadlines approaching (7 days, 3 days, 1 day)
- Gaps detected (RTO misalignment, missing documents)
- Issues requiring attention (non-conformities, failed tests)

**Технологии:** Python (FastAPI), Business rules engine

---

### 4. Data Layer

**Назначение:** Постоянное хранение всех данных

#### PostgreSQL Schema

**Tables:**

```sql
-- Organizations
organizations (
  id, name, industry, size, risk_appetite,
  created_at, updated_at
)

-- Business Processes
business_processes (
  id, org_id, name, type, criticality,
  rto, rpo, mtpd,
  dependencies JSONB,
  created_at, updated_at
)

-- Risks
risks (
  id, org_id, title, description, category,
  likelihood, impact, risk_score,
  owner_id, status, mitigation_plan,
  created_at, updated_at
)

-- BC Plans
bc_plans (
  id, org_id, process_id, version,
  content JSONB,
  status, approved_by, approved_at,
  created_at, updated_at
)

-- Exercises
exercises (
  id, org_id, type, scenario,
  scheduled_date, conducted_date,
  results JSONB, issues JSONB,
  created_at, updated_at
)

-- Audits
audits (
  id, org_id, type, standard, auditor,
  audit_date, findings JSONB,
  compliance_score,
  created_at, updated_at
)

-- Documents
documents (
  id, org_id, type, title, version,
  storage_path, mime_type,
  created_by, approved_by,
  created_at, updated_at
)

-- Users
users (
  id, org_id, email, role,
  permissions JSONB,
  created_at, updated_at
)
```

#### MinIO/S3
- PDF documents
- Word/Excel files
- Audit reports
- Exercise recordings
- Evidence files

#### Redis
- User sessions
- Real-time collaboration state (Y.js CRDT)
- Cache (frequently accessed data)
- Rate limiting

---

## 🤖 MCP Servers

### Архитектура MCP Integration

```
User (Claude Desktop / ChatGPT / Platform UI)
         ↓
    MCP Protocol
         ↓
┌────────────────────────────────┐
│     MCP Server Gateway         │
│  (routes to specific servers)  │
└────────────────────────────────┘
         ↓
    ┌────┴────┬──────────┬────────────┐
    ↓         ↓          ↓            ↓
┌────────┐ ┌──────┐ ┌────────┐ ┌──────────┐
│ BCM AI │ │Compli│ │Knowledge│ │Slack Bot │
│ Expert │ │ance  │ │ Graph   │ │(Claude)  │
└────────┘ └──────┘ └────────┘ └──────────┘
    ↓         ↓          ↓            ↓
    └─────────┴──────────┴────────────┘
                  ↓
        BCM Platform REST API
                  ↓
         PostgreSQL / MinIO
```

---

### MCP Server #1: BCM AI Expert

**Назначение:** AI эксперт по Business Continuity Management

**Tools:**

#### `recommend_rto`
```python
@server.tool("recommend_rto")
async def recommend_rto(
    org_id: str,
    process_name: str
) -> dict:
    """
    Рекомендует RTO для процесса

    Учитывает:
    - Тип процесса (critical, important, normal)
    - Финансовый impact
    - Регуляторные требования
    - Dependencies
    - Risk appetite организации

    Returns:
    - recommended_rto: int (hours)
    - rationale: str
    - alternatives: list
    - risks_if_not_met: list
    """
```

#### `generate_bc_plan`
```python
@server.tool("generate_bc_plan")
async def generate_bc_plan(
    org_id: str,
    process_name: str,
    strategy: str
) -> dict:
    """
    Генерирует Business Continuity Plan

    Использует:
    - Templates из ISO 22301
    - Best practices из BCI GPG
    - Case studies из knowledge base

    Returns:
    - plan_id: str
    - content: markdown
    - compliance_score: float
    - view_url: str (ссылка в платформу)
    """
```

#### `assess_risk`
```python
@server.tool("assess_risk")
async def assess_risk(
    org_id: str,
    threat: str,
    assets: list
) -> dict:
    """
    Проводит risk assessment

    Методология: FAIR + ISO 31000

    Returns:
    - likelihood: int (1-5)
    - impact: int (1-5)
    - risk_score: int
    - mitigation_options: list
    """
```

#### `simulate_incident`
```python
@server.tool("simulate_incident")
async def simulate_incident(
    org_id: str,
    scenario: dict,
    bc_plans: list
) -> dict:
    """
    Симулирует инцидент

    Проверяет:
    - Эффективность BC plans
    - RTO achievement
    - Decision points

    Returns:
    - timeline: list (events по минутам)
    - rto_achieved: bool
    - issues: list
    - recommendations: list
    """
```

---

### MCP Server #2: Compliance Auditor

**Назначение:** Проверка соответствия стандартам

**Tools:**

#### `audit_documents`
```python
@server.tool("audit_documents")
async def audit_documents(
    org_id: str,
    standard: str,  # "ISO22301", "ISO27001"
    audit_type: str  # "gap_analysis", "pre_certification"
) -> dict:
    """
    Audit всех документов организации

    Returns:
    - overall_compliance: float (%)
    - major_nc: list (major non-conformities)
    - minor_nc: list (minor non-conformities)
    - observations: list
    - certification_readiness: str
    """
```

#### `check_clause_compliance`
```python
@server.tool("check_clause_compliance")
async def check_clause_compliance(
    org_id: str,
    clause: str  # "8.2.2" (BIA)
) -> dict:
    """
    Проверка compliance с конкретным clause

    Returns:
    - compliant: bool
    - satisfied_requirements: list
    - missing_requirements: list
    - suggested_actions: list
    """
```

---

### MCP Server #3: Knowledge Graph Navigator

**Назначение:** Навигация по связям между стандартами

**Tools:**

#### `find_related_standards`
```python
@server.tool("find_related_standards")
async def find_related_standards(
    current_standards: list,
    organization_goals: list
) -> dict:
    """
    Находит связанные стандарты

    Returns:
    - related_standards: list
    - overlap_percentage: dict
    - integration_opportunities: list
    - estimated_savings: float
    """
```

#### `map_requirements`
```python
@server.tool("map_requirements")
async def map_requirements(
    standard_a: str,
    standard_b: str
) -> dict:
    """
    Mapping requirements между стандартами

    Пример: ISO 22301:6.1 = ISO 27001:6.1.2

    Returns:
    - shared_requirements: list
    - unique_to_a: list
    - unique_to_b: list
    """
```

---

### MCP Server #4: Slack Bot (Claude Integration)

**Назначение:** AI-powered BCM assistant в Slack

**Интеграция с Claude + Slack:**

#### Возможности
1. **Incident Management**
   ```
   @Claude incident start "Database failure in validation-service"
   → Создает incident channel, приглашает DRI, запускает runbook
   ```

2. **Compliance Q&A**
   ```
   @Claude what's our RTO for critical services?
   → Запрашивает из Platform API, показывает actual vs target
   ```

3. **Smart Alerts**
   ```
   Critical alert в Prometheus
   → @Claude автоматически постит в #bcm-critical-alerts:
     "🚨 Service down: validation-service
      Impact: ISO 8.4 compliance at risk
      Suggested action: [runbook link]"
   ```

4. **Documentation Helper**
   ```
   @Claude document this incident
   → Собирает timeline из треда, создает draft Incident Report
   ```

5. **Team Collaboration**
   ```
   @Claude who's responsible for backup recovery?
   → Находит в org chart, показывает contact info
   ```

#### Slack Workflows
- **Incident Response Workflow**
- **Compliance Alert Workflow**
- **Audit Request Workflow**
- **Emergency Notification Workflow**

---

## 🔄 Два Режима Работы

### Режим 1: Встроенный AI Assistant (для работы в платформе)

**Для кого:** Пользователи, которые не доверяют внешним AI или предпочитают работать только в платформе

**Как работает:**
1. Пользователь открывает BIA Canvas в платформе
2. AI Assistant в sidebar видит контекст (какой процесс выбран)
3. AI проактивно предлагает: "Не определен RTO. Хотите рекомендацию?"
4. Пользователь кликает "Да" → AI вызывает backend → результат в платформе

**Технологии:**
- React component (sidebar chat)
- WebSocket (real-time updates)
- Backend вызывает те же MCP tools

---

### Режим 2: External AI через MCP (Claude Desktop / ChatGPT)

**Для кого:** Power users, которые уже используют AI ежедневно

**Как работает:**
1. Пользователь открывает Claude Desktop
2. У него подключен MCP server от BCM Platform
3. Спрашивает: "Помоги с BIA для Emergency Department"
4. Claude через MCP запрашивает данные из платформы → анализирует → сохраняет результат в платформу

**Преимущества:**
- Работа без открытия браузера
- Интеграция BCM в AI workflow
- Доступ ко всем tools Claude (code, docs, web search...)

---

## 💾 Data Flow

### Пример: Рекомендация RTO

```
┌──────────────────────────────────────────────────────────────┐
│ Шаг 1: Пользователь запрашивает                             │
└──────────────────────────────────────────────────────────────┘
   User (в платформе или Claude Desktop)
     ↓
   "Recommend RTO for Emergency Department"

┌──────────────────────────────────────────────────────────────┐
│ Шаг 2: Запрос идет в backend                                │
└──────────────────────────────────────────────────────────────┘
   Platform Backend (FastAPI)
     ↓
   GET /api/organizations/{org_id}/context
   GET /api/processes/emergency-department
   GET /api/organizations/{org_id}/bia

┌──────────────────────────────────────────────────────────────┐
│ Шаг 3: Backend вызывает MCP tool                            │
└──────────────────────────────────────────────────────────────┘
   MCP Server: BCM AI Expert
     ↓
   Tool: recommend_rto(
     org_id="hospital_city",
     process_name="Emergency Department"
   )
     ↓
   AI Analysis (RAG + LLM):
   - Retrieve: ISO 22301, BCI GPG, healthcare standards
   - Analyze: process criticality, financial impact, regulations
   - Generate: recommendation with rationale

┌──────────────────────────────────────────────────────────────┐
│ Шаг 4: Результат сохраняется в БД                           │
└──────────────────────────────────────────────────────────────┘
   Platform Backend
     ↓
   POST /api/organizations/{org_id}/bia
   {
     "process_id": "emergency-department",
     "rto": 0,  // hours
     "rationale": "...",
     "timestamp": "2025-10-03T10:30:00Z"
   }
     ↓
   PostgreSQL (business_processes table updated)

┌──────────────────────────────────────────────────────────────┐
│ Шаг 5: Результат возвращается пользователю                  │
└──────────────────────────────────────────────────────────────┘
   User видит:
   - RTO = 0 hours (immediate)
   - Rationale: "ED is Tier 1 critical..."
   - Dependencies gaps highlighted
   - Link to view in platform
```

**Ключевой момент:** Независимо от интерфейса (встроенный AI или MCP), данные всегда сохраняются в платформе = single source of truth.

---

## 🎨 User Experience Scenarios

### Сценарий 1: Менеджер BCM проводит BIA

**Режим: Embedded AI в платформе**

1. Открывает BIA Canvas
2. Добавляет процесс "Emergency Department"
3. AI в sidebar предлагает: "Рекомендовать RTO?"
4. Кликает "Да"
5. AI показывает:
   - RTO = 0 hours
   - Rationale
   - Dependencies gaps (визуально подсвечены на canvas)
6. Принимает рекомендацию → данные сохранены
7. Переходит к следующему процессу

**Время:** 2-3 минуты на процесс (vs 15-20 минут вручную)

---

### Сценарий 2: Консультант готовит BC Plan

**Режим: Claude Desktop (external MCP)**

1. Открывает Claude Desktop
2. Говорит: "Generate BC plan for Emergency Department at City Medical Hospital"
3. Claude через MCP:
   - Запрашивает org context из платформы
   - Запрашивает BIA results
   - Генерирует план по ISO 22301 template
   - Сохраняет в платформу
4. Claude отвечает:
   ```
   ✅ BC Plan создан и сохранен в платформе

   Compliance score: 87%

   Missing sections:
   - Contact list (emergency contacts)
   - Communication plan (stakeholders)

   View in platform: https://bcm-platform.com/plans/12345
   ```
5. Консультант открывает ссылку → дорабатывает в document editor

**Время:** 5 минут для draft (vs 2-3 часа вручную)

---

### Сценарий 3: Аудитор проверяет compliance

**Режим: Embedded AI в платформе**

1. Открывает Compliance Dashboard
2. Выбирает "Pre-Certification Audit"
3. AI запускает audit всех документов
4. Показывает результаты:
   - Overall compliance: 78%
   - 2 major non-conformities
   - 5 minor non-conformities
   - 12 observations
5. Кликает на major NC → AI объясняет что не хватает
6. Создает action items с owners и deadlines

**Время:** 10 минут для полного audit (vs 2-3 дня вручную)

---

### Сценарий 4: BCM Team реагирует на инцидент в Slack

**Режим: Slack Bot с Claude**

**Timeline:**

```
09:03 - Prometheus alert → #bcm-critical-alerts
@Claude автоматически:
"🚨 CRITICAL: validation-service DOWN
Status: unavailable (2 min)
Impact: ISO 8.4 compliance at risk
RTO target: 15 minutes
Runbook: [link]
DRI: @john_smith"

09:04 - John clicks "Start Incident Response"
@Claude создает:
- #incident-2025-10-03-001 channel
- Приглашает: DRI, oncall, manager
- Запускает incident timer

09:05 - Team в канале
@Claude постит checklist из runbook:
☐ Check database connection
☐ Verify backup system
☐ Contact vendor if needed

09:10 - John: "database connection restored"
@Claude обновляет:
✅ Check database connection
☐ Verify backup system

09:12 - Service восстановлен
@Claude:
"✅ Service UP
RTO achieved: 9 minutes (target: 15 min)
Ready to document incident? [Yes] [Later]"

09:15 - Team clicks "Yes"
@Claude генерирует draft Incident Report:
- Timeline events
- Root cause (database timeout)
- Actions taken
- RTO performance
- Recommendations (increase timeout setting)

→ Saved to BCM Platform
```

**Результат:**
- Incident resolved в 9 минут (vs 15 min target)
- Документация создана автоматически
- Lessons learned captured

---

## 🔐 Security & Permissions

### Role-Based Access Control (RBAC)

**Roles:**
- **Super Admin** (platform owner)
- **Organization Admin** (hospital CEO)
- **BCM Manager** (day-to-day management)
- **Process Owner** (owns specific processes)
- **Auditor** (read-only + compliance checks)
- **Consultant** (temporary access to specific orgs)

### Permissions Matrix

| Resource | Super Admin | Org Admin | BCM Manager | Process Owner | Auditor | Consultant |
|----------|-------------|-----------|-------------|---------------|---------|------------|
| Organizations | CRUD | RU | R | R | R | R |
| Processes | CRUD | CRUD | CRUD | U (own only) | R | R |
| BC Plans | CRUD | CRUD | CRUD | U (own only) | R | CRU |
| Risks | CRUD | CRUD | CRUD | U (own only) | R | CRU |
| Exercises | CRUD | CRUD | CRUD | R | R | CRU |
| Audits | CRUD | RU | R | R | CRUD | CRUD |
| Documents | CRUD | CRUD | CRU | U (own only) | R | CRU |

### Data Privacy

- **Encryption at rest:** PostgreSQL TDE, MinIO encryption
- **Encryption in transit:** TLS 1.3
- **Audit logs:** All changes tracked (who, what, when)
- **Data retention:** Configurable per org (GDPR compliance)
- **Anonymization:** PII can be anonymized for demos

---

## 📊 Monitoring & Analytics

### Platform Metrics (Prometheus)

```
# User activity
platform_active_users{org_id}
platform_page_views{page}
platform_session_duration_seconds

# AI usage
ai_requests_total{tool, status}
ai_request_duration_seconds{tool}
ai_cost_usd{tool, model}

# Business metrics
processes_analyzed_total{org_id}
bc_plans_generated_total{org_id}
compliance_score{org_id, standard}
exercises_conducted_total{org_id}
```

### User Analytics

**Track:**
- Most used features
- AI acceptance rate (recommendations accepted/rejected)
- Time saved (before AI vs after AI)
- Compliance score improvement over time

**Dashboard:**
- Admin sees: platform-wide stats
- Org sees: their org stats
- User sees: their personal stats

---

## 💰 Monetization Strategy

### Pricing Tiers

**Tier 1: Starter** ($99/month)
- 1 organization
- Up to 50 processes
- Embedded AI assistant (limited)
- Community support

**Tier 2: Professional** ($299/month)
- 1 organization
- Unlimited processes
- Full AI assistant
- MCP server access
- Email support
- Compliance dashboards

**Tier 3: Enterprise** ($999/month)
- Multiple organizations
- Unlimited everything
- Dedicated MCP server instance
- Slack bot integration
- White-label option
- Priority support
- Custom AI training (on their data)

### Add-ons

- **Consultant Access:** $49/month per consultant
- **Audit Package:** $199 per audit (AI-powered full audit)
- **Training:** $999 per organization (onboarding + certification)

### MCP Server

**Free tier:**
- Public MCP server
- Rate limited (10 requests/hour)
- Shared resources

**Paid tier (included in Professional+):**
- Dedicated instance
- No rate limits
- Priority queue
- Custom fine-tuning

---

## 🚀 MVP Roadmap

### Phase 1: Platform Core (3 months)

**Deliverables:**
- [ ] Database schema (PostgreSQL)
- [ ] REST API (FastAPI)
- [ ] Authentication (JWT + RBAC)
- [ ] BIA Canvas (ReactFlow)
- [ ] Risk Matrix (interactive)
- [ ] Document Editor (Tiptap)
- [ ] Basic workflows (BIA → Plans)

**Team:** 2 backend + 2 frontend developers

---

### Phase 2: MCP Integration (1 month)

**Deliverables:**
- [ ] MCP Server: BCM AI Expert
  - [ ] `recommend_rto` tool
  - [ ] `assess_risk` tool
  - [ ] `generate_bc_plan` tool
- [ ] Platform API endpoints for MCP
- [ ] Testing with Claude Desktop

**Team:** 1 AI engineer + 1 backend developer

---

### Phase 3: Embedded AI (1 month)

**Deliverables:**
- [ ] AI Assistant sidebar component
- [ ] Context-aware suggestions
- [ ] Quick actions integration
- [ ] Real-time chat (WebSocket)

**Team:** 1 frontend + 1 AI engineer

---

### Phase 4: Advanced Features (2 months)

**Deliverables:**
- [ ] Simulation Studio
- [ ] Compliance Dashboard
- [ ] Gantt/Timeline
- [ ] MCP Server: Compliance Auditor
- [ ] MCP Server: Knowledge Graph

**Team:** Full team (6 people)

---

### Phase 5: Slack Integration (1 month)

**Deliverables:**
- [ ] Slack Bot with Claude
- [ ] Incident response workflow
- [ ] Alert notifications
- [ ] Document generation in Slack

**Team:** 1 developer + 1 AI engineer

---

## 📝 Technical Stack

### Frontend
- **Framework:** Next.js 14 (App Router)
- **UI Library:** React 18
- **Styling:** TailwindCSS
- **Components:** shadcn/ui
- **Charts:** Recharts / D3.js
- **Diagrams:** ReactFlow
- **Editor:** Tiptap
- **State:** Zustand
- **Real-time:** WebSocket (Socket.io)
- **Collaboration:** Y.js (CRDT)

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **ORM:** SQLAlchemy 2.0
- **Validation:** Pydantic v2
- **Auth:** JWT (python-jose)
- **Tasks:** Celery + Redis
- **API Docs:** OpenAPI 3.1

### Database
- **Primary:** PostgreSQL 15
- **Cache:** Redis 7
- **Object Storage:** MinIO (S3-compatible)
- **Search:** PostgreSQL Full-Text Search

### AI/ML
- **MCP Framework:** @modelcontextprotocol/sdk
- **LLM:** Claude 3.5 Sonnet (primary), GPT-4 Turbo (fallback)
- **Embeddings:** text-embedding-3-large
- **Vector DB:** pgvector (PostgreSQL extension)
- **RAG Framework:** LangChain / LlamaIndex

### Infrastructure
- **Container:** Docker + Docker Compose
- **Orchestration:** Kubernetes (production)
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus + Grafana
- **Logging:** Loki
- **Tracing:** Jaeger

### Deployment
- **Frontend:** Vercel (или self-hosted)
- **Backend:** AWS ECS / GCP Cloud Run
- **Database:** Supabase (managed PostgreSQL)
- **Object Storage:** AWS S3 / MinIO
- **CDN:** Cloudflare

---

## 🎓 Key Principles

1. **Platform = Business Logic, MCP = AI Logic**
   - Clear separation of concerns
   - Easy to update AI without touching platform

2. **Data Always in Platform**
   - Single source of truth
   - Vendor lock-in (good for business)

3. **Two UI Modes**
   - Embedded AI (for non-AI-users)
   - External MCP (for power users)

4. **API-First Design**
   - Everything through REST API
   - Easy to integrate with 3rd party tools

5. **Standards-Based**
   - ISO 22301, ISO 27001, GDPR
   - BCI Good Practice Guidelines
   - NIST frameworks

---

## 📧 Contact & Next Steps

**Prepared by:** Claude (Anthropic)
**Date:** 2025-10-03
**Version:** 1.0

**Next Steps:**
1. Review and validate architecture
2. Set up infrastructure (PostgreSQL, Redis, MinIO)
3. Start Phase 1 development (Platform Core)

**Questions?**
- Architecture questions → Review with technical lead
- Business questions → Review with product owner
- Implementation questions → Reference this document

---

**End of Document**
