# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
# BIA MODULE - Business Impact Analysis

**Версия**: 1.0
**Дата**: 2025-10-09
**Статус**: Draft
**Автор**: MD + AI Assistant

---

## 1. INTRODUCTION

### 1.1 Purpose
Этот документ описывает функциональные и нефункциональные требования к модулю **Business Impact Analysis (BIA)** платформы AI-Platform-ISO.

### 1.2 Scope
BIA модуль позволяет пользователям (BCM менеджерам):
- Идентифицировать критичные бизнес-процессы
- Определить зависимости между процессами
- Рассчитать RTO (Recovery Time Objective) и RPO (Recovery Point Objective)
- Оценить финансовое воздействие простоев
- Сгенерировать BIA отчёт

### 1.3 Definitions
- **BIA** - Business Impact Analysis
- **RTO** - Recovery Time Objective (целевое время восстановления)
- **RPO** - Recovery Point Objective (допустимая потеря данных)
- **MTPD** - Maximum Tolerable Period of Disruption
- **AI Engine** - Claude API (Anthropic) для генерации и анализа

### 1.4 User Roles
- **BCM Manager** - Основной пользователь, проводит BIA
- **Admin** - Настраивает шаблоны, интеграции
- **Viewer** - Просмотр отчётов (директор, аудитор)

---

## 2. OVERALL DESCRIPTION

### 2.1 Product Perspective
BIA модуль - часть платформы AI-Platform-ISO, интегрируется с:
- Gap Analysis модулем (использует org profile)
- BCP Generator (передаёт результаты BIA)
- Knowledge Base (347+ кейсов)
- External systems (ERP, HR)

### 2.2 Product Functions
1. **Data Collection** - сбор данных о процессах (3 метода)
2. **Process Mapping** - построение графа зависимостей (AI)
3. **Impact Analysis** - расчёт RTO/RPO, финансового воздействия
4. **Report Generation** - создание BIA отчёта (PDF/Excel)
5. **Continuous Monitoring** - обновление при изменениях

### 2.3 User Characteristics
**Primary User: Мария, BCM Менеджер**
- Возраст: 32
- Опыт в BCM: 6 месяцев
- Tech-savvy: Средний уровень
- Боли: 84 часа на BIA вручную, неуверенность в правильности

### 2.4 Operating Environment
- **Frontend**: Web browser (Chrome, Firefox, Safari)
- **Backend**: Supabase (PostgreSQL), Claude API
- **Deployment**: Cloud (Vercel frontend, Supabase backend)

### 2.5 Constraints
- Claude API rate limits (100K tokens/min)
- Supabase storage (50GB в бесплатном плане)
- Время обработки документов: <10 минут для 100 файлов
- Поддержка языков: EN, RU, UK (на старте)

---

## 3. FUNCTIONAL REQUIREMENTS

### 3.1 BIA Setup & Initialization

#### FR-BIA-001: Start BIA Wizard
**Description**: Пользователь может начать новый BIA анализ.

**Preconditions**:
- Пользователь аутентифицирован
- Организация создана (Gap Analysis завершён)

**Inputs**:
- Organization ID (UUID)
- BIA Name (string, optional)

**Processing**:
1. Создать запись в таблице `bia_analyses` (status: 'draft')
2. Загрузить org profile
3. Инициализировать wizard (step 1 of 5)

**Outputs**:
- BIA Analysis object (id, status, created_at)
- Redirect на первый шаг wizard

**Acceptance Criteria**:
```gherkin
GIVEN user is logged in
  AND organization exists
WHEN user clicks "Start BIA"
THEN system creates BIA record in <2 seconds
  AND displays Step 1: "Data Collection Method"
  AND saves BIA ID in session
```

**Priority**: P0 (Must Have)
**Complexity**: Low
**Dependencies**: Auth, Organizations table

---

#### FR-BIA-002: Select Data Collection Method
**Description**: Пользователь выбирает метод сбора данных.

**Inputs**:
- BIA ID
- Method selection (radio):
  - Interactive Questionnaire
  - Document Upload
  - ERP Integration
  - Combination (multiple)

**Processing**:
1. Сохранить выбор в `bia_analyses.collection_method`
2. Настроить wizard steps в зависимости от метода
3. Переход на соответствующий шаг

**Outputs**:
- Updated BIA record
- Next wizard step

**Acceptance Criteria**:
```gherkin
GIVEN BIA is created
WHEN user selects "Interactive Questionnaire"
THEN system saves selection
  AND displays questionnaire step
  AND shows progress: Step 2/5

WHEN user selects "Combination"
THEN system shows all 3 method steps
  AND updates progress: Step 2/7
```

**Priority**: P0 (Must Have)
**Complexity**: Low

---

### 3.2 Data Collection Methods

#### FR-BIA-101: Interactive Questionnaire
**Description**: AI генерирует персонализированную анкету для сбора данных о процессах.

**Inputs**:
- BIA ID
- Organization profile (industry, size)

**Processing**:
1. Вызвать Claude API с промптом:
   ```
   Generate BIA questionnaire for:
   - Industry: Healthcare
   - Size: 450 employees
   - Based on 347 similar cases
   Output: 20 questions (JSON)
   ```
2. AI генерирует вопросы
3. Предзаполнить вероятные ответы (из Knowledge Base)
4. Сохранить в `bia_questions`

**Outputs**:
- Array of questions (20 items)
- Pre-filled answers (where available)
- Estimated completion time (10-15 min)

**Acceptance Criteria**:
```gherkin
GIVEN org profile is Healthcare, 450 employees
WHEN user starts questionnaire
THEN AI generates 18-22 questions in <30 seconds
  AND ≥50% questions have pre-filled suggestions
  AND questions are industry-specific
  AND user can modify/override suggestions

WHEN user completes questionnaire
THEN system saves answers
  AND extracts structured data:
    - Process names
    - Dependencies
    - Estimated RTO/RPO
```

**Priority**: P0 (Must Have)
**Complexity**: High
**Dependencies**: Claude API, Knowledge Base

---

#### FR-BIA-102: Document Upload & OCR
**Description**: Пользователь загружает документы, AI извлекает данные через OCR + NLP.

**Inputs**:
- Files: PDF, Word, Excel, PowerPoint, Images
- Max file size: 50MB per file
- Max total: 200 files

**Processing**:
1. Upload files to Supabase Storage
2. Queue для обработки (background job)
3. Для каждого файла:
   - OCR (Tesseract для images/PDF)
   - NLP extraction (Claude API):
     ```
     Extract from document:
     - Process names
     - People (name, role, contact)
     - Metrics (RTO, RPO, revenue)
     - Dependencies
     Output: JSON
     ```
4. Дедупликация (объединить дубликаты)
5. Сохранить в `bia_processes`, `bia_dependencies`

**Outputs**:
- Extracted processes (array)
- Extracted dependencies (array)
- Processing status per file

**Acceptance Criteria**:
```gherkin
GIVEN user uploads 10 PDF files (total 20MB)
WHEN processing starts
THEN all files processed in <5 minutes
  AND ≥85% data extraction accuracy
  AND duplicates are merged
  AND user sees progress bar (real-time)

WHEN file has poor quality scan
THEN system shows warning: "Low confidence extraction"
  AND allows manual review/correction
```

**Priority**: P1 (Should Have)
**Complexity**: High
**Dependencies**: Supabase Storage, Claude API, OCR service

---

#### FR-BIA-103: ERP Integration (Odoo)
**Description**: Прямое подключение к Odoo ERP для автоматического сбора данных.

**Inputs**:
- Odoo instance URL
- API key (user provides)
- Permissions: Read-only access to:
  - Business processes (models)
  - Organization structure
  - Financial data (optional)

**Processing**:
1. Validate credentials (test connection)
2. Scan Odoo models via API:
   ```python
   GET /api/v2/models
   GET /api/v2/process_flow
   GET /api/v2/org_chart
   ```
3. AI mapping:
   ```
   Map Odoo models to BIA processes
   Example: "sale.order" → "Sales Order Processing"
   ```
4. Extract dependencies (model relationships)
5. Calculate financial impact (revenue per process)

**Outputs**:
- Processes (from ERP)
- Dependencies (model relationships)
- Financial data (revenue, costs)

**Acceptance Criteria**:
```gherkin
GIVEN user provides valid Odoo credentials
WHEN system scans ERP
THEN connection succeeds in <10 seconds
  AND discovers 50-100 processes
  AND maps them to BIA structure
  AND shows financial impact per process

WHEN credentials are invalid
THEN system shows error: "Cannot connect to Odoo"
  AND suggests troubleshooting steps
```

**Priority**: P2 (Could Have)
**Complexity**: High
**Dependencies**: Odoo API client, AI mapping

---

### 3.3 Data Processing & Analysis

#### FR-BIA-201: AI Process Mapping
**Description**: AI строит граф зависимостей между процессами.

**Inputs**:
- Processes (from collection methods)
- Dependencies (from collection methods)

**Processing**:
1. Объединить данные из всех методов (merge + dedup)
2. AI построение графа:
   ```
   Claude prompt:
   Given processes and dependencies, create dependency graph.
   Identify:
   - Critical path
   - Single points of failure
   - Circular dependencies (warn user)
   ```
3. Визуализация (Vis.js network graph)
4. Validation (AI checks consistency):
   ```
   If "Emergency Surgery" is critical
     BUT "Oxygen Supply" not in dependencies
   → AI warns: "Possible missing dependency"
   ```

**Outputs**:
- Dependency graph (JSON)
- Visualization data (nodes, edges)
- Warnings/suggestions

**Acceptance Criteria**:
```gherkin
GIVEN 47 processes with dependencies collected
WHEN AI builds graph
THEN graph is generated in <2 minutes
  AND shows all 47 nodes
  AND shows dependency edges
  AND identifies critical path
  AND detects 0 circular dependencies (or warns)
  AND suggests missing dependencies

WHEN user reviews graph
THEN user can:
  - Drag nodes (rearrange)
  - Add manual dependencies
  - Remove AI suggestions
  - Save modifications
```

**Priority**: P0 (Must Have)
**Complexity**: High
**Dependencies**: Claude API, Vis.js library

---

#### FR-BIA-202: RTO/RPO Calculation
**Description**: AI рассчитывает RTO и RPO для каждого процесса.

**Inputs**:
- Process criticality (from data collection)
- Industry benchmarks (from Knowledge Base)
- Org constraints (from profile)

**Processing**:
1. Для каждого процесса:
   ```
   AI calculates:
   - RTO (based on criticality + industry norms)
   - RPO (based on data sensitivity)
   - MTPD (Maximum Tolerable Period)
   ```
2. Примеры (Healthcare):
   ```
   Emergency Surgery:
     RTO: 4 hours (industry: 2-6 hours)
     RPO: 0 (patient data loss unacceptable)
     MTPD: 24 hours

   Billing:
     RTO: 48 hours (industry: 24-72 hours)
     RPO: 24 hours (daily backup acceptable)
     MTPD: 1 week
   ```
3. Пользователь может override AI suggestions

**Outputs**:
- RTO per process (hours)
- RPO per process (hours)
- MTPD per process (hours/days)
- Benchmark comparison

**Acceptance Criteria**:
```gherkin
GIVEN 47 processes identified
WHEN AI calculates RTO/RPO
THEN each process has RTO/RPO in <1 minute
  AND values are within industry norms ±20%
  AND user can see benchmark comparison
  AND user can override (with justification required)

WHEN user overrides RTO from 4h to 1h
THEN system requires justification
  AND recalculates dependencies
  AND warns if unrealistic
```

**Priority**: P0 (Must Have)
**Complexity**: Medium
**Dependencies**: Claude API, Knowledge Base

---

#### FR-BIA-203: Financial Impact Analysis
**Description**: Расчёт финансовых потерь при простое процесса.

**Inputs**:
- Process revenue/cost data (from ERP or manual)
- Downtime duration (RTO)
- Organization financial data

**Processing**:
1. Для каждого процесса:
   ```
   Financial Impact = (Revenue per hour) × (RTO hours)

   Example: Emergency Surgery
     Revenue: €500/hour (операции)
     RTO: 4 hours
     Impact: €2,000 per incident

   Example: Entire Hospital
     Revenue: €12,000/hour (450 patients × €200 avg)
     RTO: 24 hours (total shutdown)
     Impact: €288,000 per day
   ```
2. Monte Carlo simulation (10K iterations):
   - Best case (быстрое восстановление)
   - Likely case (RTO achieved)
   - Worst case (RTO breach)
3. Cascading impact (зависимые процессы):
   ```
   If "IT Systems" down → 23 processes affected
   Total impact = Sum of all 23 processes
   ```

**Outputs**:
- Financial impact per process (€)
- Cascading impact (€)
- Monte Carlo distribution (chart)
- Total organizational risk (€)

**Acceptance Criteria**:
```gherkin
GIVEN process has revenue data
WHEN AI calculates financial impact
THEN shows:
  - Direct impact: €2,000
  - Cascading impact: €15,000
  - Total: €17,000
  - Monte Carlo range: €12K-€23K (90% confidence)

WHEN revenue data missing
THEN AI estimates from industry benchmarks
  AND shows: "Estimated (not actual data)"
```

**Priority**: P1 (Should Have)
**Complexity**: High
**Dependencies**: Financial data, Monte Carlo engine

---

### 3.4 Validation & Review

#### FR-BIA-301: AI Validation Engine
**Description**: AI проверяет полноту и корректность BIA.

**Inputs**:
- Complete BIA data (processes, dependencies, RTO/RPO, impact)

**Processing**:
1. **Completeness check**:
   ```
   ✓ All critical processes have RTO/RPO?
   ✓ Dependencies defined?
   ✓ Financial impact calculated?
   ```
2. **Consistency check**:
   ```
   If "Emergency Surgery" RTO = 4h
     AND "Oxygen Supply" RTO = 24h
   → Warning: Dependency has longer RTO than dependent
   ```
3. **Best practice check**:
   ```
   If RTO > industry norm by >50%
   → Suggestion: "Your RTO is 2x industry average"
   ```
4. ISO 22301 compliance check:
   ```
   ✓ All clauses covered?
   ✓ Evidence sufficient?
   ```

**Outputs**:
- Validation report:
  - Completeness: 95%
  - Consistency: 3 warnings
  - Best practices: 5 suggestions
  - ISO compliance: 87%

**Acceptance Criteria**:
```gherkin
GIVEN BIA data complete
WHEN user runs validation
THEN AI finds all gaps in <30 seconds
  AND categorizes: Critical / Warning / Info
  AND provides fix suggestions
  AND shows ISO compliance score

WHEN user fixes all criticals
THEN compliance score → 100%
  AND BIA is marked "Ready for Review"
```

**Priority**: P0 (Must Have)
**Complexity**: High
**Dependencies**: Claude API, ISO 22301 Knowledge

---

#### FR-BIA-302: Manual Review & Corrections
**Description**: Пользователь может просмотреть и исправить данные.

**Inputs**:
- BIA ID
- Validation report

**UI Flow**:
```
┌─────────────────────────────────────┐
│ BIA Review: 47 Processes            │
├─────────────────────────────────────┤
│ ⚠️  3 Critical Issues               │
│ ⚠️  5 Warnings                      │
│ ℹ️  12 Suggestions                  │
│                                     │
│ CRITICAL:                           │
│ 1. Process "IT Systems" missing RTO │
│    [Fix Now]                        │
│                                     │
│ 2. Circular dependency detected     │
│    A → B → C → A                    │
│    [View Graph] [Break Loop]        │
│                                     │
│ 3. Emergency Surgery: Oxygen not    │
│    in dependencies (AI suggestion)  │
│    [Add Dependency] [Ignore]        │
│                                     │
│ [Export Issues] [Continue Review]   │
└─────────────────────────────────────┘
```

**Outputs**:
- Updated BIA data
- Corrections logged (audit trail)

**Acceptance Criteria**:
```gherkin
GIVEN validation finds 3 critical issues
WHEN user reviews
THEN user sees all issues categorized
  AND can fix each with 1-2 clicks
  AND changes are auto-saved
  AND re-validation runs automatically

WHEN all issues fixed
THEN system marks BIA "Approved"
  AND unlocks Report Generation
```

**Priority**: P0 (Must Have)
**Complexity**: Medium

---

### 3.5 Report Generation

#### FR-BIA-401: Generate BIA Report (PDF)
**Description**: AI генерирует полный BIA отчёт.

**Inputs**:
- BIA ID (approved status)
- Report template (ISO 22301 compliant)

**Processing**:
1. AI генерация контента:
   ```
   Claude prompt:
   Generate BIA report sections:
   1. Executive Summary
   2. Methodology
   3. Process Inventory (47 processes)
   4. Dependency Analysis
   5. RTO/RPO Summary
   6. Financial Impact Assessment
   7. Recommendations
   8. Appendices (raw data)
   ```
2. Форматирование (Markdown → PDF)
3. Визуализации:
   - Process dependency graph (PNG export)
   - Financial impact charts (Chart.js → PNG)
   - RTO distribution (histogram)

**Outputs**:
- PDF report (30-50 pages)
- Executive summary (2 pages)
- Data appendix (Excel file)

**Acceptance Criteria**:
```gherkin
GIVEN BIA is approved
WHEN user clicks "Generate Report"
THEN PDF is generated in <2 minutes
  AND contains all sections
  AND includes visualizations
  AND is ISO 22301 compliant
  AND file size <10MB

WHEN user downloads
THEN file name: BIA_Report_Hospital_2025-10-09.pdf
  AND opens in any PDF reader
```

**Priority**: P0 (Must Have)
**Complexity**: Medium
**Dependencies**: Claude API, PDF library, Chart.js

---

#### FR-BIA-402: Generate Executive Summary (PowerPoint)
**Description**: AI создаёт презентацию для руководства.

**Inputs**:
- BIA summary data
- Template (PowerPoint)

**Processing**:
1. AI генерация слайдов:
   ```
   Slide 1: Title
   Slide 2: Key Findings (3 bullets)
   Slide 3: Critical Processes (top 10)
   Slide 4: Financial Impact (chart)
   Slide 5: Risk Heat Map
   Slide 6: Recommendations (5 priorities)
   Slide 7: Next Steps
   ```
2. Визуализации embedded
3. Export PPTX

**Outputs**:
- PowerPoint file (7 slides)
- Presenter notes (AI-generated)

**Acceptance Criteria**:
```gherkin
GIVEN BIA complete
WHEN user generates Executive Summary
THEN PPTX created in <1 minute
  AND contains 7 slides
  AND includes charts/graphs
  AND has presenter notes
  AND ready to present to CEO

WHEN user customizes template
THEN AI adapts content to template structure
```

**Priority**: P1 (Should Have)
**Complexity**: Medium

---

#### FR-BIA-403: Export Data (Excel)
**Description**: Экспорт сырых данных в Excel для анализа.

**Inputs**:
- BIA ID

**Processing**:
1. Создать Excel workbook:
   - Sheet 1: Process Inventory
   - Sheet 2: Dependencies Matrix
   - Sheet 3: RTO/RPO Summary
   - Sheet 4: Financial Impact
   - Sheet 5: Validation Results
2. Форматирование (conditional formatting, charts)

**Outputs**:
- Excel file (.xlsx)

**Acceptance Criteria**:
```gherkin
GIVEN BIA complete
WHEN user exports to Excel
THEN file contains all data
  AND is properly formatted
  AND has conditional formatting (red/yellow/green)
  AND includes pivot tables
  AND user can manipulate data
```

**Priority**: P1 (Should Have)
**Complexity**: Low

---

### 3.6 Continuous Monitoring & Updates

#### FR-BIA-501: Real-time Change Detection
**Description**: Система мониторит изменения в организации и обновляет BIA.

**Inputs**:
- Webhooks from integrated systems (HR, ERP)
- User manual updates

**Processing**:
1. Webhook listener:
   ```
   Event: employee.terminated
   Data: { employee_id: 1245, name: "Смирнов Пётр" }

   Action:
   1. Find affected BIA (where Смирнов is key person)
   2. Flag as "Needs Update"
   3. Notify BCM manager
   4. Suggest replacement (AI)
   ```
2. Periodic scan (daily):
   ```
   - Check ERP for new processes
   - Check HR for org structure changes
   - Detect stale data (>6 months old)
   ```

**Outputs**:
- Update notifications
- Suggested changes (AI)
- BIA status flag

**Acceptance Criteria**:
```gherkin
GIVEN HR integration active
WHEN key person leaves organization
THEN system detects in <5 minutes
  AND flags BIA "Needs Update"
  AND notifies BCM manager
  AND suggests replacement from org chart

WHEN BCM manager reviews
THEN can approve/reject suggestion
  AND BIA is updated
  AND version history logged
```

**Priority**: P2 (Could Have)
**Complexity**: High
**Dependencies**: Webhooks, Integration APIs

---

#### FR-BIA-502: Version Control
**Description**: Отслеживание изменений BIA со временем.

**Inputs**:
- BIA updates (any change)

**Processing**:
1. Каждое изменение → новая версия
2. Diff между версиями (что изменилось)
3. Changelog (auto-generated)

**Outputs**:
- Version history (v1.0, v1.1, v2.0, ...)
- Diff view (side-by-side)
- Changelog (Markdown)

**Acceptance Criteria**:
```gherkin
GIVEN BIA v1.0 exists
WHEN user updates process RTO
THEN new version v1.1 created
  AND changelog shows: "RTO updated: 4h → 2h"
  AND user can revert to v1.0

WHEN auditor requests history
THEN user can export all versions
  AND show what changed when
```

**Priority**: P2 (Could Have)
**Complexity**: Medium

---

## 4. NON-FUNCTIONAL REQUIREMENTS

### 4.1 Performance

#### NFR-BIA-001: Response Time
- **Requirement**: Page load <2 seconds (p95)
- **API calls**: <500ms (p95)
- **AI generation**: <5 seconds for questionnaire, <2 minutes for full report
- **File upload**: Support 50MB files, process in <5 minutes

#### NFR-BIA-002: Scalability
- **Concurrent users**: Support 1,000 simultaneous BIA sessions
- **Data volume**: Handle 10,000 processes per BIA
- **File processing**: Queue system for >100 files

#### NFR-BIA-003: Availability
- **Uptime**: 99.9% (max 8.76 hours downtime/year)
- **Backup**: Daily automated backups (Supabase)
- **Recovery**: RTO 4 hours, RPO 24 hours

### 4.2 Security

#### NFR-BIA-101: Data Encryption
- **In transit**: TLS 1.3
- **At rest**: AES-256 encryption (Supabase default)
- **API keys**: Stored in environment variables (never in code)

#### NFR-BIA-102: Access Control
- **Authentication**: Supabase Auth (email/password, OAuth)
- **Authorization**: Row-level security (RLS)
  ```sql
  -- User can only access their org's BIA
  CREATE POLICY bia_access ON bia_analyses
  FOR SELECT USING (
    organization_id IN (
      SELECT id FROM organizations
      WHERE user_id = auth.uid()
    )
  );
  ```
- **Audit log**: Track all data access/changes

#### NFR-BIA-103: Compliance
- **GDPR**: User data deletion on request
- **ISO 27001**: Security controls documented
- **SOC 2**: Compliance via Supabase

### 4.3 Usability

#### NFR-BIA-201: User Experience
- **Wizard completion**: 80% users complete BIA in <1 hour
- **Error rate**: <5% user errors (form validation prevents)
- **Help availability**: Contextual AI help on every step
- **Mobile responsive**: Works on tablets (iPad+)

#### NFR-BIA-202: Accessibility
- **WCAG 2.1 Level AA** compliance
- **Keyboard navigation**: All functions accessible without mouse
- **Screen readers**: ARIA labels for all interactive elements
- **Color contrast**: Minimum 4.5:1 ratio

### 4.4 Maintainability

#### NFR-BIA-301: Code Quality
- **Test coverage**: >80% unit tests
- **Documentation**: All functions have JSDoc/TSDoc
- **Linting**: ESLint + Prettier (enforced)
- **Type safety**: TypeScript strict mode

#### NFR-BIA-302: Monitoring
- **Error tracking**: Sentry integration
- **Performance**: Vercel Analytics
- **Logging**: Structured JSON logs (Pino)
- **Alerting**: Critical errors → Slack notification

---

## 5. USE CASES

### UC-BIA-001: Complete BIA in 1 Hour

**Actor**: Maria (BCM Manager)

**Precondition**: Organization profile exists

**Main Flow**:
1. Maria starts BIA wizard
2. Selects "Interactive Questionnaire"
3. AI generates 20 questions (30 sec)
4. Maria answers questions (10 min)
5. AI builds process graph (2 min)
6. Maria reviews graph, adds 2 manual dependencies (5 min)
7. AI calculates RTO/RPO (1 min)
8. Maria reviews, overrides 3 values (10 min)
9. AI calculates financial impact (1 min)
10. AI validates BIA (30 sec)
11. Maria fixes 2 warnings (5 min)
12. AI generates PDF report (2 min)
13. Maria downloads report

**Postcondition**: BIA complete, report ready

**Alternative Flows**:
- 4a. Maria uploads documents instead → FR-BIA-102
- 7a. RTO data missing → AI estimates from benchmarks
- 10a. Critical validation errors → Must fix before proceeding

**Time**: 50 minutes (vs 84 hours manual)

---

### UC-BIA-002: Update BIA When Employee Leaves

**Actor**: System (automated) + Maria

**Precondition**: HR integration active, BIA v1.0 exists

**Main Flow**:
1. Employee "Smirnov" leaves (HR system event)
2. Webhook triggers in our system (5 min delay)
3. AI scans BIA, finds Smirnov in 3 processes
4. System flags BIA "Needs Update"
5. Email notification → Maria
6. Maria opens BIA, sees suggested changes
7. AI suggests replacement: "Ivanov (same role)"
8. Maria approves suggestion
9. BIA updated → v1.1
10. Changelog logged

**Postcondition**: BIA reflects current org structure

**Alternative Flows**:
- 7a. No suitable replacement → Maria assigns manually
- 8a. Maria rejects → Keeps old data with warning flag

---

## 6. ACCEPTANCE CRITERIA (Overall)

### 6.1 Functional Acceptance

**GIVEN** user is BCM Manager
**WHEN** conducting BIA
**THEN** system SHALL:

✅ Collect data via 3 methods (questionnaire, upload, ERP)
✅ Generate process dependency graph with AI
✅ Calculate RTO/RPO with 85%+ accuracy vs benchmarks
✅ Calculate financial impact (Monte Carlo simulation)
✅ Validate BIA for completeness & ISO compliance
✅ Generate PDF report in <2 minutes
✅ Export data to Excel
✅ Monitor changes and notify when updates needed
✅ Support version control (track changes)

### 6.2 Non-Functional Acceptance

**Performance**:
✅ Complete BIA in <1 hour (80% of users)
✅ Page load <2 sec, API <500ms
✅ AI response <5 sec (questionnaire), <2 min (report)

**Security**:
✅ Data encrypted (TLS 1.3 + AES-256)
✅ RLS policies enforce access control
✅ Audit log tracks all changes

**Usability**:
✅ WCAG 2.1 AA compliant
✅ Mobile responsive (tablet+)
✅ Contextual help on every step

---

## 7. DEPENDENCIES

### Internal Dependencies
- **Gap Analysis module**: Provides org profile
- **Knowledge Base**: 347+ cases for AI training
- **Auth service**: User authentication
- **BCP Generator**: Consumes BIA results

### External Dependencies
- **Claude API** (Anthropic): AI generation, analysis
- **Supabase**: Database, auth, storage
- **Vis.js**: Graph visualization
- **Chart.js**: Financial impact charts
- **Tesseract OCR**: Document text extraction
- **OpenAI** (optional): Backup AI for non-Claude tasks

### Integration Dependencies (Optional)
- **Odoo API**: ERP integration
- **BambooHR API**: HR integration
- **Google Calendar API**: Scheduling
- **Slack API**: Notifications

---

## 8. RISKS & MITIGATIONS

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Claude API rate limits | High | Medium | Implement queue, fallback to OpenAI |
| Poor OCR accuracy | Medium | Medium | Manual review step, user corrections |
| ERP integration fails | Medium | Low | Fallback to manual input |
| User abandons wizard | High | Medium | Auto-save every 30 sec, resume capability |
| AI generates wrong RTO | High | Low | Always show benchmarks, require user confirmation |
| Data loss | Critical | Low | Daily backups, version control |

---

## 9. FUTURE ENHANCEMENTS (Out of Scope v1.0)

- Multi-site BIA (separate analysis per location)
- Advanced analytics (trend analysis over time)
- Integration with Digital Twin module
- Real-time collaboration (multiple users editing)
- AI-powered predictive maintenance (predict BIA staleness)
- Voice input (dictate answers instead of typing)
- Offline mode (Progressive Web App)

---

## 10. GLOSSARY

| Term | Definition |
|------|------------|
| **BIA** | Business Impact Analysis - process to identify critical business functions and their dependencies |
| **RTO** | Recovery Time Objective - target time to restore function after disruption |
| **RPO** | Recovery Point Objective - maximum acceptable data loss measured in time |
| **MTPD** | Maximum Tolerable Period of Disruption - absolute maximum time a process can be down |
| **Cascading Impact** | Secondary impact when dependency fails (e.g., IT down → 23 processes affected) |
| **Knowledge Base** | Collection of 347+ real BIA cases used for AI training |
| **Process Dependency Graph** | Visual representation of how processes depend on each other |

---

## APPROVAL

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | MD | _________ | _____ |
| Tech Lead | _________ | _________ | _____ |
| QA Lead | _________ | _________ | _____ |

---

**Document Version History**:
- v1.0 (2025-10-09): Initial draft
