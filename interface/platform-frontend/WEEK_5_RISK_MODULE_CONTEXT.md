# 🎯 WEEK 5 - Risk Assessment Module - Quick Context

**Created:** 2025-10-19
**Status:** Starting Round 1
**Progress:** 0% (Foundation phase)

---

## 📊 Backend Status: ✅ READY

- **Service:** Risk Management Service
- **Port:** 8040 (NOT 8023!)
- **Base URL:** `http://localhost:8040/api/v1/risk`
- **ISO Standard:** ISO 22301:2019 Clause 8.2.3
- **Endpoints:** 30+ endpoints
- **Database:** PostgreSQL schema `risk`

---

## 🎯 What We're Building

A complete Risk Assessment frontend module following the **Documents Module pattern** (Week 4 - 16,313 lines, 46 files).

### Core Features:
1. **Risk CRUD** - Create, list, view, edit, delete risks
2. **Risk Matrix** - 5x5 heat map (likelihood × impact)
3. **FAIR Analysis** - Quantitative risk analysis (Annual Loss Expectancy)
4. **Monte Carlo** - Probabilistic simulation (10k iterations, VaR/CVaR)
5. **Treatment Plans** - Mitigation strategies (avoid, mitigate, transfer, accept)
6. **Analytics** - Trends, insights, performance metrics
7. **AI Features** - Recommendations, similar cases, pattern detection

---

## 📋 Data Models (TypeScript)

### Risk (Primary Model)
```typescript
interface Risk {
  id?: string;  // UUID
  organization_id: string;

  // Identification
  risk_title: string;  // required, max 255
  risk_code?: string;  // unique identifier
  risk_category: RiskCategory;  // 7 categories
  description: string;
  threat_source?: string;
  vulnerabilities: string[];

  // Analysis (1-5 scale)
  likelihood: RiskLikelihood;  // 1=rare, 5=almost_certain
  impact: RiskImpact;  // 1=insignificant, 5=catastrophic
  inherent_risk_score: number;  // likelihood × impact (1-25)

  // Treatment
  treatment_strategy?: TreatmentStrategy;  // avoid/mitigate/transfer/accept
  residual_likelihood?: RiskLikelihood;
  residual_impact?: RiskImpact;
  residual_risk_score?: number;

  // Ownership & Review
  risk_owner_id?: string;
  status: RiskStatus;  // identified/analyzing/treated/monitoring/closed
  last_reviewed_at?: string;
  next_review_date?: string;

  // Relations
  related_processes: any[];
  related_assets: any[];

  // Metadata
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}
```

### FAIRAnalysis
```typescript
interface FAIRAnalysis {
  risk_id: string;
  threat_event_frequency: number;  // Threats/year
  vulnerability_score: number;  // 0-1 probability
  loss_event_frequency: number;  // Calculated

  // Loss (triangular distribution)
  primary_loss_min: number;  // $ USD
  primary_loss_max: number;
  primary_loss_most_likely: number;
  secondary_loss_min: number;
  secondary_loss_max: number;

  // Results
  annual_loss_expectancy: number;  // $ USD
  risk_rating: string;  // low/medium/high/critical
  confidence_interval_low: number;
  confidence_interval_high: number;

  analyzed_at?: string;
  analyzed_by?: string;
}
```

### MonteCarloSimulation
```typescript
interface MonteCarloSimulation {
  risk_id: string;
  iterations: number;  // 1000-100000, default 10000

  factors: Array<{
    name?: string;
    min: number;
    most_likely: number;
    max: number;
  }>;

  // Results
  mean_loss: number;
  median_loss: number;
  percentile_95: number;  // VaR
  percentile_99: number;  // CVaR

  distribution_data?: {
    histogram: number[];  // 50 bins
    bin_edges: number[];
    min: number;
    max: number;
    std_dev: number;
  };

  simulated_at?: string;
}
```

### RiskTreatmentPlan
```typescript
interface RiskTreatmentPlan {
  id?: string;
  risk_id: string;
  strategy: TreatmentStrategy;
  description: string;

  actions: Array<{
    action?: string;
    responsible?: string;
    deadline?: string;
    status?: string;
  }>;

  responsible_party?: string;
  start_date?: string;
  target_date?: string;
  completion_date?: string;

  estimated_cost?: number;
  actual_cost?: number;

  expected_residual_likelihood?: RiskLikelihood;
  expected_residual_impact?: RiskImpact;

  status: string;  // planned/in_progress/completed
  created_at?: string;
  updated_at?: string;
}
```

---

## 🔢 Enums

### RiskCategory
```typescript
enum RiskCategory {
  OPERATIONAL = "operational",
  FINANCIAL = "financial",
  STRATEGIC = "strategic",
  COMPLIANCE = "compliance",
  REPUTATIONAL = "reputational",
  CYBERSECURITY = "cybersecurity",
  NATURAL_DISASTER = "natural_disaster"
}
```

### RiskLikelihood (1-5 scale)
```typescript
enum RiskLikelihood {
  RARE = 1,              // < 5%
  UNLIKELY = 2,          // 5-20%
  POSSIBLE = 3,          // 20-50%
  LIKELY = 4,            // 50-80%
  ALMOST_CERTAIN = 5     // > 80%
}
```

### RiskImpact (1-5 scale)
```typescript
enum RiskImpact {
  INSIGNIFICANT = 1,
  MINOR = 2,
  MODERATE = 3,
  MAJOR = 4,
  CATASTROPHIC = 5
}
```

### TreatmentStrategy
```typescript
enum TreatmentStrategy {
  AVOID = "avoid",       // Eliminate
  MITIGATE = "mitigate", // Reduce
  TRANSFER = "transfer", // Insurance
  ACCEPT = "accept"      // Accept risk
}
```

### RiskStatus
```typescript
enum RiskStatus {
  IDENTIFIED = "identified",
  ANALYZING = "analyzing",
  TREATED = "treated",
  MONITORING = "monitoring",
  CLOSED = "closed"
}
```

---

## 🔗 Key API Endpoints

### Risk CRUD
- `POST /api/v1/risk/assessments` - Create
- `GET /api/v1/risk/assessments` - List (with filters: category, status, min_score)
- `GET /api/v1/risk/assessments/{risk_id}` - Get by ID
- `PUT /api/v1/risk/assessments/{risk_id}` - Update
- `DELETE /api/v1/risk/assessments/{risk_id}` - Soft delete

### FAIR Analysis
- `POST /api/v1/risk/assessments/{risk_id}/fair-analysis` - Perform
- `GET /api/v1/risk/assessments/{risk_id}/fair-analysis` - Get results

### Monte Carlo
- `POST /api/v1/risk/assessments/{risk_id}/monte-carlo` - Run simulation
- `GET /api/v1/risk/assessments/{risk_id}/monte-carlo` - Get results

### Treatment Plans
- `POST /api/v1/risk/assessments/{risk_id}/treatment-plans` - Create
- `GET /api/v1/risk/assessments/{risk_id}/treatment-plans` - List
- `PUT /api/v1/risk/treatment-plans/{plan_id}` - Update

### Analytics & Visualizations
- `GET /api/v1/risk/reports` - Generate report
- `GET /api/v1/risk/assessments/{risk_id}/matrix-position` - Get position
- `GET /api/v1/risk/risk-heat-map` - Get 5x5 matrix data
- `GET /api/v1/risk/risk-trends?days=90` - Get trends

### AI Features (Workflow Intelligence)
- `GET /api/v1/workflow-ai/insights?days=30` - Get insights
- `GET /api/v1/workflow-ai/recommendations?limit=5` - Get recommendations
- `GET /api/v1/workflow-ai/cases/search?query=...` - Search cases
- `GET /api/v1/workflow-ai/cases/{case_id}/similar?limit=5` - Find similar
- `GET /api/v1/workflow-ai/analytics/patterns?days=90` - Analyze patterns
- `GET /api/v1/workflow-ai/analytics/performance?days=30` - Get metrics

---

## 📐 Risk Severity Thresholds

```typescript
const RISK_SEVERITY = {
  CRITICAL: { min: 20, max: 25, color: "red" },    // score >= 20
  HIGH:     { min: 15, max: 19, color: "orange" }, // score 15-19
  MEDIUM:   { min: 8,  max: 14, color: "yellow" }, // score 8-14
  LOW:      { min: 1,  max: 7,  color: "green" }   // score < 8
};

// Risk Score = Likelihood × Impact
// Range: 1-25
```

---

## 🎨 UI Components to Create

### Badges (3 components)
1. **RiskCategoryBadge** - 7 categories with icons
2. **RiskSeverityBadge** - Critical/High/Medium/Low with colors
3. **RiskStatusBadge** - 5 statuses with colors

### Core Components (6 components)
4. **RiskCard** - List item with key metrics
5. **RiskList** - List view with filters
6. **RiskDetail** - Full risk details
7. **RiskForm** - Create/edit metadata
8. **RiskFilters** - Filter panel (category, status, severity)
9. **RiskMatrix** - 5x5 heat map visualization

### Analytics Components (3 components)
10. **FAIRAnalysisCard** - Display FAIR results
11. **MonteCarloChart** - Histogram + statistics
12. **TrendChart** - Line chart for trends

### Treatment Components (2 components)
13. **TreatmentPlanForm** - Create/edit plan
14. **TreatmentPlanList** - List with progress

---

## 📄 Pages to Create

1. **`/risk/page.tsx`** - List all risks (with filters, search)
2. **`/risk/new/page.tsx`** - Create new risk
3. **`/risk/[id]/page.tsx`** - Risk detail view
4. **`/risk/[id]/edit/page.tsx`** - Edit risk
5. **`/risk/analytics/page.tsx`** - Analytics dashboard (heat map, trends, insights)

---

## 🚀 Execution Plan (4 Rounds)

### ✅ Round 1 - Foundation (3 agents, ~1,450 lines)
**Status:** Ready to start
- Agent 1: Types & Enums (risk.ts) - 400 lines
- Agent 2: Validation Schemas (risk-validation.ts) - 250 lines
- Agent 3: API Client (risk-client.ts) - 800 lines

### ⏳ Round 2 - Data Layer (3 agents, ~2,000 lines)
- Agent 4: CRUD Hooks (useRisks, useRisk, useCreateRisk, useUpdateRisk, useDeleteRisk) - 1,000 lines
- Agent 5: Analytics Hooks (useFAIR, useMonteCarlo, useHeatMap, useTrends, useReport) - 600 lines
- Agent 6: AI Hooks (useInsights, useRecommendations, useSimilarCases, usePatterns) - 400 lines

### ⏳ Round 3 - UI Components (6 agents, ~3,000 lines)
- Agent 7: Badge Components (Category, Severity, Status) - 300 lines
- Agent 8: Card/List Components (RiskCard, RiskList) - 500 lines
- Agent 9: Form Components (RiskForm, RiskFilters) - 800 lines
- Agent 10: Risk Matrix (5x5 heat map) - 400 lines
- Agent 11: FAIR/Monte Carlo Components - 600 lines
- Agent 12: Treatment Plan Components - 400 lines

### ⏳ Round 4 - Pages (2 agents, ~1,600 lines)
- Agent 13: Main Pages (list, new, detail, edit) - 1,000 lines
- Agent 14: Analytics Dashboard - 600 lines

**Total:** ~8,050 lines, 14 agents, 4 rounds

---

## 🎨 Design Guidelines

- **Color Scheme:** Anthropic warm colors (orange/amber) + severity colors (red/orange/yellow/green)
- **Icons:** Lucide React (AlertTriangle, Shield, TrendingUp, Target, etc.)
- **Typography:** Same as Documents Module
- **Layout:** Responsive, mobile-friendly
- **Patterns:** Follow Documents Module exactly

### Risk Severity Colors:
```typescript
const SEVERITY_COLORS = {
  CRITICAL: {
    bg: "bg-red-100",
    text: "text-red-800",
    border: "border-red-300",
    badge: "bg-red-600 text-white"
  },
  HIGH: {
    bg: "bg-orange-100",
    text: "text-orange-800",
    border: "border-orange-300",
    badge: "bg-orange-600 text-white"
  },
  MEDIUM: {
    bg: "bg-yellow-100",
    text: "text-yellow-800",
    border: "border-yellow-300",
    badge: "bg-yellow-600 text-white"
  },
  LOW: {
    bg: "bg-green-100",
    text: "text-green-800",
    border: "border-green-300",
    badge: "bg-green-600 text-white"
  }
};
```

---

## 🔧 Technical Stack

- **Next.js 14** App Router
- **TypeScript** Strict Mode
- **React Query** (TanStack Query) - server state
- **Zod** - validation
- **Tailwind CSS** - styling
- **Lucide React** - icons
- **date-fns** - date formatting
- **react-hot-toast** - notifications
- **recharts** - charts (for trends, histograms)

---

## 📝 Key Files to Create

```
src/
├── types/
│   └── risk.ts                              # All types & enums
├── lib/
│   ├── validations/
│   │   └── risk-validation.ts               # Zod schemas
│   └── api/
│       └── risk-client.ts                   # API client
├── hooks/
│   └── risk/
│       ├── useRisks.ts                      # List
│       ├── useRisk.ts                       # Single
│       ├── useCreateRisk.ts                 # Create
│       ├── useUpdateRisk.ts                 # Update
│       ├── useDeleteRisk.ts                 # Delete
│       ├── useFAIRAnalysis.ts               # FAIR
│       ├── useMonteCarloSimulation.ts       # Monte Carlo
│       ├── useRiskTrends.ts                 # Trends
│       ├── useRiskHeatMap.ts                # Heat map
│       ├── useTreatmentPlans.ts             # Treatment
│       ├── useRiskInsights.ts               # AI insights
│       ├── useRiskRecommendations.ts        # AI recommendations
│       └── index.ts                         # Barrel
├── components/
│   └── risk/
│       ├── RiskCategoryBadge.tsx
│       ├── RiskSeverityBadge.tsx
│       ├── RiskStatusBadge.tsx
│       ├── RiskCard.tsx
│       ├── RiskList.tsx
│       ├── RiskDetail.tsx
│       ├── RiskForm.tsx
│       ├── RiskFilters.tsx
│       ├── RiskMatrix.tsx
│       ├── FAIRAnalysisCard.tsx
│       ├── MonteCarloChart.tsx
│       ├── TrendChart.tsx
│       ├── TreatmentPlanForm.tsx
│       ├── TreatmentPlanList.tsx
│       └── index.ts
└── app/
    └── (platform)/
        └── risk/
            ├── page.tsx                     # List
            ├── new/
            │   └── page.tsx                 # Create
            ├── [id]/
            │   ├── page.tsx                 # Detail
            │   └── edit/
            │       └── page.tsx             # Edit
            └── analytics/
                └── page.tsx                 # Dashboard
```

---

## 💡 Important Notes

1. **Port is 8040, not 8023!** Update all API calls
2. **Risk Score Calculation:** `score = likelihood × impact` (1-25)
3. **Severity Auto-Calculated:** Based on score thresholds
4. **Multi-Tenancy:** All data filtered by `organization_id` from JWT
5. **Soft Delete:** Use `is_active: false`, not hard delete
6. **Review Dates:** Auto-calculated based on severity
7. **Event Bus:** Risk service publishes events on create/update/severity change

---

## 🎯 Next Step

**Start Round 1 - Foundation:**
Launch 3 agents in parallel to create:
1. Types & Enums (risk.ts)
2. Validation Schemas (risk-validation.ts)
3. API Client (risk-client.ts)

Command: "Launch Round 1 agents"

---

**Generated:** 2025-10-19
**For:** Week 5 Risk Assessment Module
**Follows Pattern:** Week 4 Documents Module (16,313 lines, 46 files)
**Estimated Completion:** ~8,050 lines of production code
