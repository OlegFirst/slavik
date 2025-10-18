# BIA Module - Full Integration Plan
**Дата:** 2025-10-18
**Статус:** В процессе реализации
**Цель:** Полная интеграция всех backend сервисов и intelligent core

---

## 🎯 КОМПЛЕКСНАЯ АРХИТЕКТУРА

### Backend Services Integration

#### 1. BIA Service (port 8012) ✅ ЧАСТИЧНО РЕАЛИЗОВАНО
**Что работает:**
- ✅ CRUD операции (create, read, update, delete)
- ✅ Bulk operations (create, update, delete, validate)
- ✅ AI RTO suggestions endpoint
- ✅ Summary reports
- ✅ Filtering по criticality/status

**Что нужно добавить:**
- ⚠️ Discover dependencies endpoint
- ⚠️ Critical processes report
- ⚠️ Dependencies mapping report
- ⚠️ Compliance check endpoint
- ⚠️ Cache metrics
- ⚠️ Supply Chain BCM endpoints

#### 2. Documents Service (port 8024) ❌ НЕ ИНТЕГРИРОВАН
**Для BIA нужно:**
- 📄 Автоматическое создание BIA документа при complete
- 📄 Version control для BIA reports
- 📄 Approval workflow для critical processes
- 📄 Retention policies (7 years for BIA per ISO 22301)
- 📄 Document templates для BIA reports
- 📄 Export в PDF/DOCX
- 📄 Classification: Confidential для BIA

**Frontend компоненты нужны:**
- BIADocumentExport (PDF/DOCX export)
- BIADocumentVersion (version history)
- BIADocumentApproval (approval workflow UI)
- BIADocumentShare (sharing with stakeholders)

#### 3. Living Docs (port 8XXX) ❌ НЕ ИНТЕГРИРОВАН
**Что это даёт:**
- 🧠 AI-powered documentation evolution
- 🧠 Personalization по user journey
- 🧠 Interactive examples
- 🧠 Gap analysis
- 🧠 Documentation improvements suggestions

**Frontend компоненты нужны:**
- BIAInteractiveGuide (step-by-step с AI)
- BIAGapAnalysis (что не заполнено)
- BIAImprovementsSuggestions (AI suggestions)
- BIAJourneyTracker (progress tracking)

---

## 🧠 Intelligent Core Integration

### 1. BIA Specialist AI ❌ НЕ ИНТЕГРИРОВАН
**Локация:** `/intelligent_core/expertise_center/ai_office/ВСМ-colleagues/bia_specialist/`

**6 методов которые нужно интегрировать:**

1. **`analyze_process_criticality()`**
   - Вход: process data
   - Выход: criticality tier, RTO/RPO recommendations, impact analysis
   - Frontend: AIProcessAnalysis component

2. **`determine_rto_rpo()`**
   - Вход: process, financial impact, dependencies
   - Выход: RTO/RPO/MTPD с reasoning
   - Frontend: ✅ УЖЕ ЕСТЬ в useAISuggestion

3. **`calculate_impact_over_time()`**
   - Вход: process, timeframes
   - Выход: impact progression chart data
   - Frontend: ImpactTimeline component (НУЖЕН)

4. **`map_dependencies()`**
   - Вход: process data
   - Выход: dependency graph с criticality
   - Frontend: DependencyMapper component (НУЖЕН)

5. **`suggest_recovery_strategies()`**
   - Вход: process, RTO, resources
   - Выход: recovery strategies recommendations
   - Frontend: RecoveryStrategiesAI component (НУЖЕН)

6. **`conduct_bia()`**
   - Вход: organization data
   - Выход: complete BIA report
   - Frontend: BIAFullReport component (НУЖЕН)

### 2. Workflow Intelligence ❌ ЧАСТИЧНО ПОНЯТО
**Локация:** `/intelligent_core/workflow_intelligence/workflows/bia_workflow.py`

**7 стадий BIA Workflow:**
```python
class BIAStage:
    NOT_STARTED = "not_started"
    IDENTIFY_PROCESSES = "identify_processes"      # >= 3 processes
    ANALYZE_DEPENDENCIES = "analyze_dependencies"  # Tier 1 needs >= 2 deps
    ASSESS_IMPACT = "assess_impact"                # All impact types
    DETERMINE_RTO = "determine_rto"                # RTO/RPO/MTPD
    REVIEW_RESULTS = "review_results"              # All validators pass
    COMPLETED = "completed"
```

**Frontend компоненты нужны:**
- ✅ ProcessForm (частично покрывает IDENTIFY_PROCESSES)
- ❌ DependencyForm (для ANALYZE_DEPENDENCIES)
- ❌ ImpactAssessmentForm (для ASSESS_IMPACT)
- ❌ RTODeterminationWizard (для DETERMINE_RTO)
- ❌ BIAReviewPanel (для REVIEW_RESULTS)
- ❌ WorkflowProgress (отображение текущей стадии)

**Validators которые нужно отображать:**
```python
def _validate_processes(data) -> tuple[bool, str]
def _validate_dependencies(data) -> tuple[bool, str]
def _validate_impact(data) -> tuple[bool, str]
def _validate_rto(data) -> tuple[bool, str]
def _validate_business_rules(data) -> tuple[bool, str]
def _validate_compliance(data) -> tuple[bool, str]
def _validate_completeness(data) -> tuple[bool, str]
```

**Frontend: BIAValidationPanel** (НУЖЕН)

### 3. Scenario Intelligence ❌ НЕ ИНТЕГРИРОВАН
**Локация:** `/intelligent_core/scenario_intelligence/scenarios/level3_intersystem/ai-assisted-bia.v1.0.0.yaml`

**AI-Assisted BIA Scenario:**
```yaml
steps:
  1. create_bia_draft         # Platform Services
  2. request_ai_analysis      # AI Orchestrator
  3. wait_completion          # Async
  4. retrieve_ai_suggestions  # AI Orchestrator
  5. update_bia              # Platform Services
  6. store_ai_analysis       # Platform Services
  7. verify_audit_trail      # Cross-system
```

**Frontend: AIAssistedBIAWizard** (НУЖЕН)

### 4. System BCM Service ❌ НЕ ИНТЕГРИРОВАН
**Локация:** `/intelligent_core/system_bcm_service/`

**Что даёт для BIA:**
- Real-time platform health monitoring
- Actual RTO/RPO from incidents
- Recovery effectiveness metrics
- Pattern detection
- Auto-recovery procedures

**Frontend: PlatformHealthPanel для BIA** (НУЖЕН)

---

## 📋 НЕДОСТАЮЩИЕ КОМПОНЕНТЫ

### Критически важные (High Priority)

#### 1. DependencyMapper (React Flow)
```typescript
// frontend/src/components/bia/DependencyMapper.tsx
interface DependencyMapperProps {
  process: BIAProcess;
  onDependenciesUpdate: (deps: Dependency[]) => void;
  aiSuggestionsEnabled?: boolean; // Integrate with BIA Specialist AI
}
```
**Функции:**
- Визуальный граф зависимостей
- Drag & drop для добавления узлов
- AI suggestions для dependencies
- Criticality color coding
- Circular dependency detection

#### 2. ImpactAssessmentForm
```typescript
// frontend/src/components/bia/ImpactAssessmentForm.tsx
interface ImpactAssessmentFormProps {
  process: BIAProcess;
  onComplete: (impact: ImpactData) => void;
}
```
**Секции:**
- Financial Impact Timeline (1h, 4h, 8h, 24h, 1week, 1month)
- Operational Impact
- Reputational Impact (5 levels)
- Regulatory Impact (5 levels)
- Patient Safety Impact (healthcare, 5 levels)
- AI-powered impact calculation

#### 3. RecoveryStrategiesBuilder
```typescript
// frontend/src/components/bia/RecoveryStrategiesBuilder.tsx
```
**Функции:**
- Add/remove recovery strategies
- Link to resources
- Priority ordering
- Cost estimation
- AI suggestions integration
- Validation по RTO feasibility

#### 4. BIAWorkflowWizard
```typescript
// frontend/src/components/bia/BIAWorkflowWizard.tsx
```
**7 шагов:**
- Step 1: Identify Processes (min 3)
- Step 2: Analyze Dependencies (Tier 1 >= 2 deps)
- Step 3: Assess Impact (all types)
- Step 4: Determine RTO/RPO/MTPD
- Step 5: Define Recovery Strategies
- Step 6: Review & Validate
- Step 7: Complete & Generate Report

**Каждый шаг:**
- Progress indicator
- Validators в real-time
- AI assistance button
- Save draft
- Next/Previous navigation

### Средней важности (Medium Priority)

#### 5. BIADocumentGenerator
```typescript
// frontend/src/components/bia/BIADocumentGenerator.tsx
```
**Export форматы:**
- PDF Report (comprehensive)
- PDF Executive Summary
- DOCX Report (editable)
- CSV Data Export
- Excel Workbook (multiple sheets)

**Интеграция с Documents Service:**
- Auto-create document on complete
- Version control
- Approval workflow
- Retention policy application

#### 6. BIAComplianceChecker
```typescript
// frontend/src/components/bia/BIAComplianceChecker.tsx
```
**Проверки:**
- ISO 22301:2019 Clause 8.2.2 compliance
- WHO Essential Services tiers (healthcare)
- Business rules (RTO >= RPO, etc.)
- Completeness checks
- Gap analysis

#### 7. BIAAIAssistant (Chat Panel)
```typescript
// frontend/src/components/bia/BIAAIAssistant.tsx
```
**Функции:**
- Chat с BIA Specialist AI
- Contextual suggestions
- Ask questions about BIA
- Get examples
- Explain ISO requirements

### Низкой важности (Low Priority)

#### 8. BIABulkOperationsUI
```typescript
// frontend/src/components/bia/BIABulkOperationsUI.tsx
```
**Операции:**
- Select multiple processes
- Bulk update criticality
- Bulk assign owner
- Bulk export
- Bulk delete with confirmation

#### 9. BIASupplyChainView
```typescript
// frontend/src/components/bia/BIASupplyChainView.tsx
```
**Интеграция с Supply Chain API:**
- Critical suppliers list
- Supplier risk assessment
- Dependencies от suppliers
- Supply chain BIA

---

## 🔄 EventBus Integration

### Events которые нужно слушать:

```typescript
// frontend/src/lib/eventbus/bia-events.ts

// From BIA Service
- 'bia.process.created'
- 'bia.process.updated'
- 'bia.process.completed'
- 'bia.process.deleted'

// From AI Orchestrator
- 'ai.bia.analysis.completed'
- 'ai.bia.suggestions.ready'

// From Workflow Intelligence
- 'workflow.bia.stage.changed'
- 'workflow.bia.validation.failed'

// From Documents Service
- 'document.bia_report.published'
- 'document.bia_report.approved'
```

### Events которые нужно публиковать:

```typescript
- 'bia.process.view.requested'
- 'bia.ai.suggestion.requested'
- 'bia.document.export.requested'
```

---

## 🗄️ Database Schema Integration

### BIA Service Tables:
```sql
- bia_processes         # Main table
- bia_dependencies      # Dependencies
- bia_impacts          # Impact data
- bia_resources        # Resource requirements
- bia_strategies       # Recovery strategies
```

### Documents Service Tables (для BIA):
```sql
- documents                    # BIA reports
- document_versions           # Version history
- document_approvals          # Approval workflow
- document_retention_policies # 7 years retention
```

---

## 📦 Недостающие npm пакеты

```bash
npm install --save \
  react-flow-renderer@latest \  # Для DependencyMapper
  recharts@latest \              # Для Impact charts (УЖЕ ЕСТЬ?)
  jspdf@latest \                 # Для PDF export
  docx@latest \                  # Для DOCX export
  xlsx@latest \                  # Для Excel export
  socket.io-client@latest \      # Для EventBus WebSocket
  date-fns@latest \              # Для date handling
  @tanstack/react-table@latest   # Для advanced tables
```

---

## 🎯 ПОШАГОВЫЙ ПЛАН РЕАЛИЗАЦИИ

### Phase 1: Workflow Integration (Week 3-4) 🔜 NEXT
1. ✅ BIAWorkflowWizard shell
2. ✅ DependencyForm component
3. ✅ ImpactAssessmentForm component
4. ✅ RecoveryStrategiesBuilder component
5. ✅ BIAReviewPanel component
6. ✅ WorkflowProgress indicator
7. ✅ Stage validators integration

### Phase 2: AI Integration (Week 5)
1. ⏳ BIA Specialist AI endpoints integration
2. ⏳ AIAssistedBIAWizard
3. ⏳ BIAAIAssistant chat panel
4. ⏳ Impact calculation with AI
5. ⏳ Dependency discovery with AI
6. ⏳ Recovery strategies suggestions

### Phase 3: Documents Integration (Week 6)
1. ⏳ BIADocumentGenerator
2. ⏳ PDF/DOCX/Excel export
3. ⏳ Documents Service integration
4. ⏳ Approval workflow UI
5. ⏳ Version control UI
6. ⏳ Retention policy display

### Phase 4: Living Docs Integration (Week 7)
1. ⏳ Interactive BIA guide
2. ⏳ Gap analysis component
3. ⏳ Improvements suggestions
4. ⏳ Journey tracking
5. ⏳ Personalized learning path

### Phase 5: Advanced Features (Week 8)
1. ⏳ EventBus WebSocket integration
2. ⏳ Real-time collaboration
3. ⏳ BulkOperationsUI
4. ⏳ Supply Chain view
5. ⏳ Advanced analytics
6. ⏳ Compliance dashboard

---

## ✅ ЧТО УЖЕ РЕАЛИЗОВАНО

### Week 1-2 (COMPLETE):
- ✅ 7 React Query hooks (CRUD + AI + Summary)
- ✅ 3 Badge components
- ✅ ProcessCard component
- ✅ ProcessForm component (basic)
- ✅ ProcessModal component
- ✅ Main BIA page с grid layout
- ✅ Zod validation schemas
- ✅ API client
- ✅ TypeScript types

**Процент готовности:** ~25% от полной интеграции

---

## 🎯 ИТОГОВАЯ ЦЕЛЬ

**Создать полнофункциональный BIA модуль который:**

1. ✅ Использует все 16 endpoints BIA Service
2. ✅ Интегрирован с BIA Specialist AI (6 методов)
3. ✅ Следует BIA Workflow Engine (7 стадий)
4. ✅ Интегрирован с Documents Service (export, approval, retention)
5. ✅ Интегрирован с Living Docs (AI guide, gap analysis)
6. ✅ Использует Scenario Intelligence (AI-assisted creation)
7. ✅ Показывает данные из System BCM (real RTO/RPO)
8. ✅ Публикует/слушает EventBus events
9. ✅ Полностью ISO 22301:2019 compliant
10. ✅ NO MOCKS - только реальные данные

---

## 📊 ПРОГРЕСС

**Backend Services:**
- BIA Service: 40% интегрирован
- Documents Service: 0% интегрирован
- Living Docs: 0% интегрирован

**Intelligent Core:**
- BIA Specialist AI: 15% интегрирован (только RTO suggestions)
- Workflow Intelligence: 20% понят, 0% интегрирован
- Scenario Intelligence: 0% интегрирован
- System BCM: 0% интегрирован

**Frontend Components:**
- Основные: 30% готовы
- Workflow: 10% готовы
- AI Integration: 10% готовы
- Documents: 0% готовы
- Analytics: 0% готовы

**Общий прогресс: ~18% от полной интеграции**

---

**Следующие 6-8 недель:** Довести до 100% 🚀

**Принцип:** NO MOCKS! Только реальная интеграция! Профессиональный продукт!
