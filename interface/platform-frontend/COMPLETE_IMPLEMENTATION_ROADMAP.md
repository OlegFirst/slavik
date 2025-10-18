# Complete Platform Frontend Implementation Roadmap 🗺️

**Дата:** 2025-10-17
**Цель:** Полная реализация единого интерфейса для всей платформы (46 сервисов)
**Основа:** Сценарии из `/catalogs/scenarios/` + архитектура из `SERVICE_CATALOG`

---

## 📊 Масштаб реализации

### Всего к реализации:
- **46 сервисов** → 46+ модулей UI
- **19 функциональных систем** (L3)
- **11 подсистем** (L2)
- **76+ сценариев** (L1-L4)

### Приоритизация (по сценариям из catalogs):

**Уровень 1: Production Ready (31 сервис) - Приоритет HIGH**
- ✅ Auth, EventBus, Gateway - уже интегрированы
- 🎯 BIA, Planning, Learning, Validation - Core BCM
- 🎯 Digital Twin - Integration Dashboard
- 🎯 AI Foundation, Workflow Intelligence - AI Core

**Уровень 2: Development (15 сервисов) - Приоритет MEDIUM**
- Compliance, Documents, Governance
- Risk, Response, Plans
- AI Orchestration, Collective Intelligence

**Уровень 3: Future (Infrastructure) - Приоритет LOW**
- Monitoring, Observability - Admin only
- Internal infrastructure services

---

## 🎯 Implementation Strategy

### Принципы (на основе сценариев):

1. **Scenario-Driven Development**
   - Каждый модуль реализуется по сценариям из `/catalogs/scenarios/`
   - L1 scenarios = Service UI
   - L2 scenarios = Subsystem integration UI
   - L3 scenarios = System workflows UI
   - L4 scenarios = User journeys UI

2. **4-Layer Architecture** (из scenario generation system):
   ```
   L4 (User Workflows)    → Complete user journeys
   L3 (Systems)           → Cross-subsystem integration
   L2 (Subsystems)        → Inter-service communication
   L1 (Services)          → Individual service UI
   ```

3. **API-First**
   - OpenAPI code generation
   - TypeScript types from schemas
   - React Query for server state

4. **Component-Driven**
   - Shared components library
   - Module-specific components
   - Story-driven development (Storybook)

---

## 📅 12-Week Implementation Plan

### **Phase 1: Foundation** ✅ COMPLETE (Week 1-2)
- [x] Project setup & architecture
- [x] Navigation & layout
- [x] Service configuration (46 services)
- [x] Base components (Sidebar, Header, Breadcrumbs)
- [x] Placeholder pages

---

### **Phase 2: Core BCM Modules** (Week 3-6) 🎯 NEXT

#### Week 3-4: BIA Module (Business Impact Analysis)
**Scenario Source**: `/catalogs/scenarios/comprehensive-platform-docs/BUSINESS_PROCESS_SCENARIOS_COMPLETE.md`

**Features to implement:**
- [ ] BIA List & Create
- [ ] BIA Wizard (5-step процесс)
- [ ] Process Management
- [ ] Criticality Analysis
- [ ] RTO/RPO Calculator (AI-powered)
- [ ] Dependencies Graph (React Flow)
- [ ] Questionnaire Generator
- [ ] Results & Reports

**Pages:**
```
/bia
  ├── page.tsx                 # BIA List
  ├── create/page.tsx          # Create BIA Wizard
  ├── [id]/
  │   ├── page.tsx            # BIA Overview
  │   ├── processes/page.tsx   # Process Management
  │   ├── analysis/page.tsx    # Impact Analysis
  │   ├── questionnaire/page.tsx # Questionnaire
  │   └── reports/page.tsx     # Reports
```

**Components:**
```typescript
// BIA-specific components
src/components/bia/
├── BIAWizard.tsx              # 5-step wizard
├── ProcessCard.tsx            # Process display
├── CriticalityMatrix.tsx      # Criticality visualization
├── RTOCalculator.tsx          # RTO/RPO calculator
├── DependencyGraph.tsx        # Dependencies (React Flow)
├── QuestionnaireBuilder.tsx   # Questionnaire creator
└── ImpactReport.tsx           # Report generator
```

**API Integration:**
```typescript
// src/lib/api/generated/bia-service.ts
// Auto-generated from http://localhost:8012/openapi.json

export class BIAClient {
  async listBIA(): Promise<BIA[]>
  async createBIA(data: CreateBIARequest): Promise<BIA>
  async getBIA(id: string): Promise<BIA>
  async addProcess(biaId: string, process: Process): Promise<void>
  async calculateRTO(processId: string): Promise<RTOResult>
  async generateQuestionnaire(biaId: string): Promise<Questionnaire>
  async submitAnswers(questionnaireId: string, answers: Answer[]): Promise<void>
}
```

---

#### Week 3-4: Planning Module
**Scenario Source**: Planning service scenarios

**Features:**
- [ ] BC Strategy Management
- [ ] Objectives (SMART goals)
- [ ] Recovery Plans
- [ ] Strategy Templates
- [ ] AI Plan Generator

**Pages:**
```
/planning
  ├── page.tsx                 # Planning Dashboard
  ├── strategies/
  │   ├── page.tsx            # Strategies List
  │   └── [id]/page.tsx       # Strategy Details
  ├── objectives/
  │   ├── page.tsx            # Objectives List
  │   └── [id]/page.tsx       # Objective Details
  └── recovery-plans/
      ├── page.tsx            # Plans List
      └── [id]/page.tsx       # Plan Details
```

---

#### Week 5-6: Learning & Validation Modules

**Learning Module:**
- [ ] Courses Management
- [ ] Competence Tracking
- [ ] Training Programs
- [ ] Certifications
- [ ] Progress Analytics

**Validation Module:**
- [ ] Exercises Management
- [ ] Exercise Execution
- [ ] Audits & Reviews
- [ ] CAPA (Corrective Actions)
- [ ] Validation Reports

---

### **Phase 3: Digital Twin Module** (Week 7-8) ⭐

**Scenario Source**: `/catalogs/platform-services/digital-twin.yaml`

#### Week 7: Platform Topology & System Clone

**Features:**
- [ ] Platform Topology Visualization (React Flow)
- [ ] Service Discovery Dashboard
- [ ] Health Monitoring
- [ ] System Clone Management
- [ ] Mirror Creation Wizard
- [ ] Mirror Comparison View

**Pages:**
```
/digital-twin
  ├── page.tsx                    # DT Dashboard
  ├── topology/
  │   ├── page.tsx               # Platform Topology (React Flow)
  │   ├── [service]/page.tsx     # Service Details
  │   └── health/page.tsx        # Health Dashboard
  ├── clone/
  │   ├── page.tsx               # Clones List
  │   ├── create/page.tsx        # Create Mirror Wizard
  │   ├── [id]/page.tsx          # Clone Details
  │   └── compare/page.tsx       # Compare Clones
  ├── simulations/
  │   ├── page.tsx               # Simulations List
  │   ├── create/page.tsx        # Create Simulation
  │   └── [id]/page.tsx          # Simulation Results
  └── collection/
      ├── page.tsx               # Collection Sessions
      ├── create/page.tsx        # Collection Wizard
      └── [id]/page.tsx          # Session Details
```

**Components:**
```typescript
// Digital Twin components
src/components/digital-twin/
├── TopologyGraph.tsx          # Platform topology (React Flow)
├── ServiceCard.tsx            # Service info card
├── HealthIndicator.tsx        # Service health
├── MirrorWizard.tsx          # Clone creation wizard
├── MirrorComparison.tsx      # Side-by-side comparison
├── SimulationForm.tsx        # Simulation setup
├── SimulationResults.tsx     # Results visualization
├── DataCollectionWizard.tsx  # 8 methods, 10 categories
└── CollectionProgress.tsx    # Session progress
```

**Topology Visualization (React Flow):**
```typescript
// src/components/digital-twin/TopologyGraph.tsx
import ReactFlow, { Node, Edge } from 'reactflow';

interface ServiceNode extends Node {
  data: {
    name: string;
    port: number;
    status: 'running' | 'stopped' | 'degraded';
    health: number;
    dependencies: string[];
  }
}

export function TopologyGraph({ services }: { services: Service[] }) {
  const nodes: ServiceNode[] = services.map(service => ({
    id: service.name,
    type: 'custom',
    position: calculatePosition(service), // Auto-layout
    data: service
  }));

  const edges: Edge[] = calculateDependencies(services);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={{ custom: ServiceNode }}
    />
  );
}
```

---

#### Week 8: Simulations & Data Collection

**Simulations:**
- [ ] 7 Simulation Engines Access
- [ ] Monte Carlo Simulations
- [ ] What-If Scenarios
- [ ] Scenario Generator (AI)
- [ ] Results Visualization (Recharts)

**Data Collection:**
- [ ] 8 Collection Methods UI
- [ ] 10 Data Categories Workflow
- [ ] Collection Session Management
- [ ] Quality Scoring
- [ ] Data Export

---

### **Phase 4: Intelligence Layer** (Week 9-10)

#### Week 9: AI Services Dashboard

**Scenario Source**: `/catalogs/scenarios/comprehensive-platform-docs/AI_FOUNDATION_CAPABILITIES.md`

**Features:**
- [ ] AI Foundation Dashboard
- [ ] Model Management
- [ ] Prompt Library
- [ ] AI Execution History
- [ ] Token Usage Analytics

**Pages:**
```
/ai
  ├── page.tsx                # AI Dashboard
  ├── foundation/
  │   ├── page.tsx           # AI Foundation
  │   ├── models/page.tsx     # Model Management
  │   └── prompts/page.tsx    # Prompt Library
  ├── orchestration/
  │   ├── page.tsx           # AI Orchestration
  │   └── workflows/page.tsx  # AI Workflows
  └── agents/
      ├── page.tsx           # AI Agents
      └── [id]/page.tsx      # Agent Details
```

---

#### Week 10: Community & Analytics

**Community Intelligence:**
- [ ] Peer Knowledge Sharing
- [ ] Discussion Forums
- [ ] Best Practices Library
- [ ] Case Studies
- [ ] Community Insights

**Analytics:**
- [ ] Platform KPI Dashboard
- [ ] Service Metrics (Recharts)
- [ ] Trend Analysis
- [ ] Custom Reports
- [ ] Data Export

---

### **Phase 5: Governance & Compliance** (Week 11-12)

#### Compliance Module
- [ ] Requirements Management
- [ ] Evidence Collection
- [ ] Compliance Reports
- [ ] Audit Trail
- [ ] Gap Analysis

#### Governance Module
- [ ] Policies Management
- [ ] Committee Management
- [ ] Decision Tracking
- [ ] Governance Reports

#### Risk Module
- [ ] Risk Register
- [ ] Risk Assessment
- [ ] Treatment Plans
- [ ] Risk Monitoring

#### Response Module
- [ ] Incident Management
- [ ] Playbooks
- [ ] Response Activation
- [ ] Recovery Tracking

---

### **Phase 6: Integration & Polish** (Week 13-14)

**Features:**
- [ ] WebSocket real-time updates
- [ ] Notification Center
- [ ] Advanced Search (Algolia/Meilisearch)
- [ ] Dark Mode
- [ ] Mobile Responsive
- [ ] Accessibility (WCAG AA)
- [ ] Performance Optimization
- [ ] E2E Tests (Playwright)

---

## 🔌 API Generation Strategy

### OpenAPI Client Generation

```bash
#!/bin/bash
# scripts/generate-all-api-clients.sh

# Production services (31)
services=(
  "auth-service:8001"
  "bia-service:8012"
  "planning-service:8011"
  "learning-service:8021"
  "validation-service:8022"
  "digital-twin:8096"
  "ai-foundation:8040"
  "system-bcm:8050"
  "workflow-intelligence:8037"
  "community:8030"
  # ... add all 46 services
)

for service in "${services[@]}"; do
  IFS=':' read -r name port <<< "$service"

  echo "🔄 Generating $name..."

  # Download OpenAPI spec
  curl -s "http://localhost:$port/openapi.json" > "temp/$name-openapi.json"

  # Generate TypeScript client
  npx openapi-typescript "temp/$name-openapi.json" \
    --output "src/lib/api/generated/${name}.ts"

  echo "✅ $name done"
done

echo "🎉 All API clients generated!"
```

---

## 🎨 Component Library Structure

### Shared Components (All Modules)

```
src/components/
├── ui/                          # shadcn/ui base
│   ├── button.tsx
│   ├── card.tsx
│   ├── dialog.tsx
│   ├── form.tsx
│   ├── input.tsx
│   ├── select.tsx
│   ├── table.tsx
│   └── ...
│
├── layout/                      # Layout components
│   ├── Sidebar.tsx
│   ├── Header.tsx
│   ├── Breadcrumbs.tsx
│   ├── PageHeader.tsx
│   └── Footer.tsx
│
├── data-display/                # Data visualization
│   ├── DataTable.tsx           # Universal table
│   ├── MetricCard.tsx          # KPI cards
│   ├── StatusBadge.tsx         # Status indicators
│   ├── HealthIndicator.tsx     # Health status
│   ├── Timeline.tsx            # Event timeline
│   └── ProgressBar.tsx         # Progress indicators
│
├── visualizations/              # Advanced viz
│   ├── TopologyGraph.tsx       # React Flow graphs
│   ├── DependencyTree.tsx      # Tree visualization
│   ├── MetricsChart.tsx        # Recharts wrapper
│   ├── HeatMap.tsx             # Heatmap
│   └── NetworkDiagram.tsx      # D3.js networks
│
├── forms/                       # Form components
│   ├── FormBuilder.tsx         # Dynamic forms
│   ├── WizardStep.tsx          # Multi-step wizards
│   ├── DateRangePicker.tsx     # Date selection
│   └── FileUpload.tsx          # File uploads
│
└── [module-name]/               # Module-specific
    ├── bia/
    ├── digital-twin/
    ├── planning/
    └── ...
```

---

## 📊 State Management Strategy

### Global State (Zustand)

```typescript
// src/store/platform.ts

interface PlatformState {
  // Services
  services: Service[];
  serviceStatus: Record<string, ServiceStatus>;

  // Platform health
  platformHealth: number;
  activeServices: number;
  totalServices: number;

  // Real-time updates
  events: PlatformEvent[];

  // Actions
  fetchServices: () => Promise<void>;
  updateServiceStatus: (name: string, status: ServiceStatus) => void;
  subscribeToEvents: () => void;
}

export const usePlatformStore = create<PlatformState>((set, get) => ({
  services: [],
  serviceStatus: {},
  platformHealth: 0,
  activeServices: 0,
  totalServices: 46,
  events: [],

  fetchServices: async () => {
    const services = await api.discovery.getServices();
    set({ services });
  },

  updateServiceStatus: (name, status) => {
    set(state => ({
      serviceStatus: {
        ...state.serviceStatus,
        [name]: status
      }
    }));
  },

  subscribeToEvents: () => {
    // WebSocket connection to EventBus
    const ws = new WebSocket('ws://localhost:8056');

    ws.onmessage = (event) => {
      const platformEvent = JSON.parse(event.data);
      set(state => ({
        events: [platformEvent, ...state.events].slice(0, 100)
      }));
    };
  }
}));
```

### Module State (React Query)

```typescript
// src/lib/api/hooks/useBIA.ts

export function useBIAList(orgId: string) {
  return useQuery({
    queryKey: ['bia', 'list', orgId],
    queryFn: () => api.bia.list(orgId),
  });
}

export function useCreateBIA() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateBIARequest) => api.bia.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bia'] });
    },
  });
}
```

---

## 🧪 Testing Strategy

### Unit Tests (Jest + Testing Library)

```typescript
// src/components/bia/__tests__/BIAWizard.test.tsx

describe('BIAWizard', () => {
  it('renders all 5 steps', () => {
    render(<BIAWizard />);
    expect(screen.getByText('Step 1: Basic Information')).toBeInTheDocument();
  });

  it('validates form before next step', async () => {
    render(<BIAWizard />);

    const nextButton = screen.getByRole('button', { name: /next/i });
    fireEvent.click(nextButton);

    expect(await screen.findByText(/name is required/i)).toBeInTheDocument();
  });
});
```

### Integration Tests (Playwright)

```typescript
// e2e/bia-workflow.spec.ts

test('complete BIA creation workflow', async ({ page }) => {
  await page.goto('/bia/create');

  // Step 1: Basic info
  await page.fill('[name="name"]', 'Test BIA');
  await page.click('button:has-text("Next")');

  // Step 2: Add processes
  await page.click('button:has-text("Add Process")');
  await page.fill('[name="processName"]', 'Critical Process');
  await page.selectOption('[name="criticality"]', 'high');
  await page.click('button:has-text("Save")');

  // Step 3: Calculate RTO
  await page.click('button:has-text("Calculate RTO")');
  await page.waitForResponse(response =>
    response.url().includes('/calculate-rto')
  );

  // Step 4: Generate questionnaire
  await page.click('button:has-text("Generate Questionnaire")');

  // Step 5: Review & Submit
  await page.click('button:has-text("Submit BIA")');

  await expect(page).toHaveURL(/\/bia\/[^/]+$/);
  await expect(page.getByText('BIA created successfully')).toBeVisible();
});
```

---

## 📈 Performance Targets

### Core Web Vitals
- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1

### Application Performance
- **Initial Load**: < 3s
- **Route Navigation**: < 500ms
- **API Calls**: < 1s (p95)
- **Bundle Size**: < 500KB (initial), < 200KB (route chunks)

### Optimization Techniques
- Code splitting (Next.js automatic)
- Image optimization (next/image)
- API response caching (React Query)
- Virtual scrolling (large lists)
- Lazy loading (components, images)

---

## 🎯 Success Criteria

### Phase 2 (Core BCM) Success Metrics:
- [ ] BIA Module: 100% feature parity with backend API
- [ ] Planning Module: All CRUD operations working
- [ ] Learning Module: Course management complete
- [ ] Validation Module: Exercise workflow complete
- [ ] < 3s page load time
- [ ] 95% test coverage

### Phase 3 (Digital Twin) Success Metrics:
- [ ] Platform Topology: 46 services visualized
- [ ] System Clone: Mirror creation & comparison working
- [ ] Simulations: 7 engines accessible
- [ ] Data Collection: 8 methods × 10 categories implemented
- [ ] Real-time updates (WebSocket)

### Overall Platform Success Metrics:
- [ ] All 46 services accessible via UI
- [ ] Unified navigation (18 items)
- [ ] Single sign-on (JWT)
- [ ] Responsive (mobile, tablet, desktop)
- [ ] Accessible (WCAG AA)
- [ ] Production deployment

---

## 🚀 Next Immediate Steps

### Week 3 (NOW):

1. **Generate API clients for production services**
   ```bash
   npm run generate-api-clients
   ```

2. **Start BIA Module implementation**
   - Create BIA pages structure
   - Build BIA Wizard component
   - Implement Process Management
   - Add RTO Calculator

3. **Implement Digital Twin Topology page**
   - Setup React Flow
   - Create service discovery UI
   - Add health indicators

---

**Ready to begin Phase 2! 🎯**

Хочешь начать с:
1. **Digital Twin (Week 7-8)** - твой модуль полностью
2. **BIA (Week 3-4)** - core BCM первым
3. **API Generation** - сначала сгенерировать все клиенты

Что предпочитаешь?
