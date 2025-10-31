# Vue.js Component Cleanup Analysis

## Information Architecture Requirements vs Existing Components

### Section 1: Overview Dashboard (`/overview`)

**Required Components:**
- ✅ `OverviewDashboard.vue` (could use `PDCADashboard.vue` or `Dashboard.vue`)
- ❌ `KPIMetricsCard.vue` (missing)
- ❌ `CriticalProcessesWidget.vue` (missing)
- ❌ `IncidentStatusWidget.vue` (missing)
- ❌ `ComplianceScoreWidget.vue` (missing)
- ❌ `RecentActivitiesWidget.vue` (missing)

### Section 2: Events Monitor (`/events`)

**Required Components:**
- ✅ `EventMonitor.vue` (exists)
- ❌ `EventStreamViewer.vue` (missing)
- ❌ `EventFilters.vue` (missing)
- ❌ `EventDetailsModal.vue` (missing)
- ❌ `EventStatistics.vue` (missing)

### Section 3: AI Orchestrator (`/orchestrator`)

**Required Components:**
- ✅ `AIOrchestrator.vue` (exists)
- ❌ `PendingDecisions.vue` (missing)
- ❌ `DecisionCard.vue` (missing)
- ❌ `WorkflowStatus.vue` (could repurpose `WorkflowModal.vue`)
- ❌ `AIRecommendations.vue` (missing)
- ❌ `DecisionHistory.vue` (missing)

### Section 4: Documents & Context (`/documents`)

**Required Components:**
- ❌ `DocumentCenter.vue` (missing)
- ❌ `ContextImporter.vue` (missing)
- ❌ `EvidenceUploader.vue` (missing)
- ❌ `DocumentAnalyzer.vue` (missing)
- ❌ `ComplianceDocuments.vue` (missing)
- ❌ `AuditTrail.vue` (missing)

### Section 5: Admin & Configuration (`/admin`)

**Required Components:**
- ❌ `AdminDashboard.vue` (missing)
- ❌ `ServiceConfiguration.vue` (missing)
- ❌ `TenantManagement.vue` (missing)
- ❌ `UserPermissions.vue` (missing)
- ❌ `SystemHealth.vue` (missing)
- ❌ `APIKeyManager.vue` (missing)

## Existing Components Analysis

### Components to Keep (7)
1. ✅ **AIOrchestrator.vue** - Core component for AI decision management
2. ✅ **EventMonitor.vue** - Core component for event streaming
3. ✅ **NotificationSystem.vue** - Cross-app notification system
4. ❓ **WorkflowModal.vue** - Could be repurposed for workflow status
5. ❓ **PhaseDetailsModal.vue** - Could be repurposed for decision details
6. ❓ **AIChatAssistant.vue** - Could be kept for chat functionality
7. ❓ **OdooView.vue** - Integration component (evaluate usage)

### Views to Consolidate/Remove

#### Views to Keep and Repurpose (4)
1. ✅ **PDCADashboard.vue** → Rename to `OverviewDashboard.vue`
2. ✅ **Dashboard.vue** → Could be admin dashboard
3. ❓ **KPIDashboard.vue** → Integrate into overview
4. ❓ **Incidents.vue** vs **IncidentList.vue** → Consolidate

#### Views to Remove (8)
1. ❌ **Demo.vue** - Demo purposes only
2. ❌ **SimpleDashboard.vue** - Redundant with PDCADashboard
3. ❌ **Compliance.vue** - Should be integrated into overview
4. ❌ **RiskManagement.vue** - Should be integrated into overview
5. ❌ **Plans.vue** vs **PlanManager.vue** - Consolidate
6. ❌ **Processes.vue** - CRUD stays in Odoo
7. ❌ **Reports.vue** - CRUD stays in Odoo
8. ❌ **Training.vue** - CRUD stays in Odoo

## Cleanup Actions

### Files to Delete (10)
```bash
rm frontend/web_portal/src/views/Demo.vue
rm frontend/web_portal/src/views/SimpleDashboard.vue
rm frontend/web_portal/src/views/Compliance.vue
rm frontend/web_portal/src/views/RiskManagement.vue
rm frontend/web_portal/src/views/Plans.vue
rm frontend/web_portal/src/views/Processes.vue
rm frontend/web_portal/src/views/Reports.vue
rm frontend/web_portal/src/views/Training.vue
```

### Files to Rename/Repurpose (3)
```bash
mv frontend/web_portal/src/views/PDCADashboard.vue frontend/web_portal/src/views/OverviewDashboard.vue
mv frontend/web_portal/src/views/Dashboard.vue frontend/web_portal/src/views/AdminDashboard.vue
```

### Files to Consolidate (2)
- Merge `IncidentList.vue` functionality into `Incidents.vue`
- Merge `KPIDashboard.vue` functionality into `OverviewDashboard.vue`

### New Components Needed (20)

#### Overview Section (5)
- `KPIMetricsCard.vue`
- `CriticalProcessesWidget.vue`
- `IncidentStatusWidget.vue`
- `ComplianceScoreWidget.vue`
- `RecentActivitiesWidget.vue`

#### Events Section (4)
- `EventStreamViewer.vue`
- `EventFilters.vue`
- `EventDetailsModal.vue`
- `EventStatistics.vue`

#### AI Orchestrator Section (4)
- `PendingDecisions.vue`
- `DecisionCard.vue`
- `AIRecommendations.vue`
- `DecisionHistory.vue`

#### Documents Section (5)
- `DocumentCenter.vue`
- `ContextImporter.vue`
- `EvidenceUploader.vue`
- `DocumentAnalyzer.vue`
- `ComplianceDocuments.vue`

#### Admin Section (2)
- `ServiceConfiguration.vue`
- `SystemHealth.vue`

## Router Updates Required

### Remove Routes (8)
- `/demo`
- `/simple-dashboard`
- `/compliance` (standalone)
- `/risk-management` (standalone)
- `/plans` (CRUD in Odoo)
- `/processes` (CRUD in Odoo)
- `/reports` (CRUD in Odoo)
- `/training` (CRUD in Odoo)

### Add Routes (5)
- `/overview` (default route)
- `/events`
- `/orchestrator`
- `/documents`
- `/admin`

### Keep Routes (2)
- `/incidents` (consolidated)
- `/kpi` (integrated into overview)

## Component Dependencies

### Services Required
- `EventBusService` (SSE connections)
- `OrchestratorService` (API calls)
- `KPIService` (metrics)
- `DocumentService` (file handling)

### Vuex Store Updates
- Add events state management
- Add AI decisions state management
- Add system health monitoring
- Add document management

## Summary
- **Delete**: 8 view files, 0 component files
- **Rename**: 2 view files
- **Create**: 20 new component files
- **Update**: Router configuration, store management
- **Final Structure**: 5 main sections, ~25 total components
