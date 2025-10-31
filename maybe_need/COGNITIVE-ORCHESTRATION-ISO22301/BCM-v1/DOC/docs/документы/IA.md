# Information Architecture - BCM Web Portal

## Navigation Structure (5 Sections)

### 1. Overview Dashboard
**Purpose**: Real-time system status and KPI monitoring
**Route**: `/overview` or `/` (default)

**Components Required**:
- `OverviewDashboard.vue` (main layout)
- `KPIMetricsCard.vue` (BIA coverage, plans up-to-date, CAPA on-time)
- `CriticalProcessesWidget.vue` (processes with RTO < 4 hours)
- `IncidentStatusWidget.vue` (open incidents counter)
- `ComplianceScoreWidget.vue` (ISO 22301 compliance level)
- `RecentActivitiesWidget.vue` (latest events feed)

**Data Sources**:
- KPI API: `/bcm/kpi` (Odoo endpoint)
- EventBus SSE: `/api/events/stream?tenant_id=xxx`
- Vuex store: processes, incidents, complianceData

### 2. Events Monitor
**Purpose**: Real-time event stream and system activity
**Route**: `/events`

**Components Required**:
- `EventMonitor.vue` (main component with SSE connection)
- `EventStreamViewer.vue` (scrolling event feed)
- `EventFilters.vue` (filter by type, tenant, date range)
- `EventDetailsModal.vue` (event payload inspector)
- `EventStatistics.vue` (event count by type)

**Key Features**:
- Real-time SSE connection to EventBus
- Event filtering and search
- Event correlation tracking
- Payload inspection with JSON viewer
- Export event history to CSV/JSON

### 3. AI Orchestrator
**Purpose**: AI decision management and workflow automation
**Route**: `/orchestrator`

**Components Required**:
- `AIOrchestrator.vue` (main AI dashboard)
- `PendingDecisions.vue` (decisions awaiting approval)
- `DecisionCard.vue` (individual decision with approve/reject)
- `WorkflowStatus.vue` (PDCA cycle progress)
- `AIRecommendations.vue` (context-aware suggestions)
- `DecisionHistory.vue` (completed decisions log)

**API Integration**:
- Orchestrator: `/api/ai/decisions/pending`
- Decision actions: `/api/ai/decisions/{id}/approve|reject`
- Workflow triggers: `/api/v1/orchestrator/workflows/*/start`

### 4. Documents & Context
**Purpose**: Document analysis, context management, evidence upload
**Route**: `/documents`

**Components Required**:
- `DocumentCenter.vue` (main document hub)
- `ContextImporter.vue` (organizational context upload)
- `EvidenceUploader.vue` (audit evidence management)
- `DocumentAnalyzer.vue` (AI document analysis)
- `ComplianceDocuments.vue` (ISO 22301 templates)
- `AuditTrail.vue` (document version history)

**Integration Points**:
- Odoo portal: `/portal/bcm/upload-evidence`
- AI analysis: Orchestrator `/api/recommendations`
- File storage: bcm.client.vault model

### 5. Admin & Configuration
**Purpose**: System configuration, user management, settings
**Route**: `/admin`

**Components Required**:
- `AdminDashboard.vue` (admin overview)
- `ServiceConfiguration.vue` (EventBus, Orchestrator, BIA Engine URLs)
- `TenantManagement.vue` (multi-tenant client management)
- `UserPermissions.vue` (BCM roles and access control)
- `SystemHealth.vue` (service status monitoring)
- `APIKeyManager.vue` (client API keys management)

**Admin Features**:
- BCM service health checks
- Configuration testing (connection validation)
- Tenant isolation verification
- Event bus statistics and monitoring
- System logs and error tracking

## Cross-Component Services

### 1. EventBusService
```javascript
// services/eventbus.js
class EventBusService {
  async connect(tenantId)
  async publish(eventData)
  subscribe(eventType, callback)
  disconnect()
}
```

### 2. OrchestratorService
```javascript
// services/orchestrator.js  
class OrchestratorService {
  async getPendingDecisions(tenantId)
  async approveDecision(decisionId)
  async rejectDecision(decisionId)
  async getRecommendations(context)
}
```

### 3. KPIService
```javascript
// services/kpi.js
class KPIService {
  async getCurrentKPIs(tenantId)
  async calculateKPIs(tenantId)
  async getKPIHistory(period)
}
```

## Vuex Store Enhancement

### Additional State
```javascript
state: {
  // Existing state...
  events: [],
  pendingDecisions: [],
  kpiMetrics: null,
  systemHealth: {},
  currentTenant: 'demo_hospital'
}
```

### Additional Actions
```javascript
actions: {
  // Event management
  async connectEventBus({ commit, state })
  async publishEvent({ commit }, eventData)
  
  // AI decisions
  async fetchPendingDecisions({ commit })
  async approveDecision({ commit }, decisionId)
  async rejectDecision({ commit }, decisionId)
  
  // KPI management  
  async fetchKPIMetrics({ commit })
  async calculateKPIs({ commit })
  
  // System health
  async checkSystemHealth({ commit })
}
```

## Router Configuration

```javascript
// router/index.js
const routes = [
  { path: '/', redirect: '/overview' },
  { path: '/overview', component: () => import('@/views/OverviewDashboard.vue') },
  { path: '/events', component: () => import('@/views/EventMonitor.vue') },
  { path: '/orchestrator', component: () => import('@/views/AIOrchestrator.vue') },
  { path: '/documents', component: () => import('@/views/DocumentCenter.vue') },
  { path: '/admin', component: () => import('@/views/AdminDashboard.vue'), meta: { requiresAdmin: true } }
]
```

## Authentication & Authorization

### User Roles
- `bcm_portal` - Portal users (sections 1-4)
- `bcm_internal` - Internal BCM users (all sections)  
- `bcm_manager` - BCM managers (admin access)

### Route Guards
```javascript
router.beforeEach((to, from, next) => {
  const userRole = store.state.user?.role
  if (to.meta.requiresAdmin && userRole !== 'bcm_manager') {
    next('/overview')
  } else {
    next()
  }
})
```

## Responsive Design Considerations

### Desktop Layout (≥1024px)
- Full navigation sidebar
- Multi-column dashboards
- Expandable event details
- Side-by-side decision approval

### Tablet Layout (768-1023px)  
- Collapsible navigation
- Stacked widgets
- Modal event details
- Single-column forms

### Mobile Layout (<768px)
- Bottom navigation tabs
- Single-column layout
- Swipe gestures for events
- Full-screen modals

## Performance Optimizations

1. **Lazy Loading**: Route-based code splitting
2. **SSE Connection Management**: Auto-reconnect with backoff
3. **Event Throttling**: Batch updates for high-frequency events
4. **Caching**: KPI metrics cached for 5 minutes
5. **Virtual Scrolling**: Event lists with 1000+ items

## Security Considerations

1. **Tenant Isolation**: All API calls include tenant_id
2. **CORS Configuration**: Restricted to known origins
3. **API Authentication**: JWT tokens for Odoo integration
4. **Event Validation**: Schema validation on publish
5. **XSS Prevention**: Sanitized event payload display
