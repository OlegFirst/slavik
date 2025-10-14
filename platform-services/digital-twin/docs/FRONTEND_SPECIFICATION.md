# 📱 Digital Twin - Frontend Technical Specification (ТЗ)

**Дата:** 2025-10-01
**Версия:** 1.0
**Статус:** ✅ Ready for Implementation

---

## 🎯 Цель проекта

Создать современный веб-интерфейс для **Digital Twin Universal Service** - платформы Business Continuity Management (BCM) с возможностями AI-анализа, симуляций и математического моделирования.

---

## 🏗️ Архитектура

### Backend (уже готов):
- **API:** FastAPI на Python 3.11
- **База данных:** PostgreSQL 16
- **Кеш:** Redis 7
- **Аутентификация:** JWT tokens
- **API URL:** `http://localhost:8000`
- **Swagger UI:** `http://localhost:8000/docs`

### Frontend (требуется создать):
- **Framework:** React 18+ или Next.js 14+ (рекомендуется Next.js для SSR)
- **TypeScript:** Обязательно (типы уже подготовлены)
- **State Management:** Zustand или Redux Toolkit
- **UI Library:** Material-UI v5 или shadcn/ui + TailwindCSS
- **Charts:** recharts или chart.js
- **API Client:** axios или fetch с React Query
- **Real-time:** WebSocket для live updates (опционально)

---

## 🔐 Аутентификация

### JWT Flow:

#### 1. Login
```typescript
POST /api/v1/auth/login
Content-Type: application/json

Request:
{
  "username": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user123",
    "username": "user@example.com",
    "tenant_id": "tenant123",
    "is_active": true
  }
}
```

#### 2. Использование токена
```typescript
// Все последующие запросы:
headers: {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 3. Logout
```typescript
POST /api/v1/auth/logout
Authorization: Bearer {token}

Response: 204 No Content
```

### TypeScript типы:
```typescript
interface LoginRequest {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  user: User;
}

interface User {
  id: string;
  username: string;
  tenant_id: string;
  is_active: boolean;
  created_at: string;
}
```

---

## 📊 Основные модули

### 1. Organizations (Организации)

#### Features:
- Список организаций
- Создание/редактирование организации
- **AI Insights Dashboard** ⭐ (главная фича)
- Health Score visualization
- Risk Landscape display

#### API Endpoints:

**1.1 Получить список организаций**
```typescript
GET /api/v1/organizations/
Authorization: Bearer {token}

Query params:
- skip: number = 0
- limit: number = 100

Response: Organization[]

interface Organization {
  id: string;
  name: string;
  industry: string;
  size: string;
  country: string;
  maturity_level: number; // 1-5
  twin_health_score?: number; // 0-100
  risk_landscape?: RiskLandscape;
  compliance_status?: ComplianceStatus;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}
```

**1.2 Создать организацию**
```typescript
POST /api/v1/organizations/
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "name": "ACME Corporation",
  "industry": "Technology",
  "size": "large",
  "country": "USA",
  "maturity_level": 3
}

Response: Organization (201 Created)
```

**1.3 Получить AI Insights** ⭐⭐⭐
```typescript
GET /api/v1/organizations/{org_id}/insights
Authorization: Bearer {token}

Response:
{
  "organization_id": "org123",
  "organization_name": "ACME Corp",
  "insights_count": 7,
  "insights": TwinInsight[],
  "summary": {
    "critical_count": 2,
    "high_count": 3,
    "medium_count": 2,
    "low_count": 0
  },
  "generated_at": "2025-10-01T12:00:00Z"
}

interface TwinInsight {
  id: string;
  type: "risk" | "opportunity" | "warning" | "recommendation" | "compliance" | "trend" | "anomaly";
  title: string;
  description: string;
  confidence: number; // 0-100
  impact: "low" | "medium" | "high" | "critical";
  source: string; // "bia_analysis", "simulation", "ai_prediction"
  actionable: boolean;
  suggested_actions: string[];
  metadata?: Record<string, any>;
  created_at: string;
}
```

**UI рекомендации для AI Insights:**
- **Dashboard cards** - каждый insight в отдельной карточке
- **Color coding:**
  - Critical (red): #EF4444
  - High (orange): #F97316
  - Medium (yellow): #EAB308
  - Low (green): #22C55E
- **Icon mapping:**
  - risk: ⚠️
  - opportunity: 💡
  - warning: 🚨
  - recommendation: ✅
  - compliance: 📋
  - trend: 📈
  - anomaly: 🔍
- **Action buttons** - для каждого suggested_action
- **Confidence meter** - progress bar (0-100%)

---

### 2. Personal Digital Twin (Персональное рабочее пространство)

#### Features:
- Персональный дашборд пользователя
- Workspace configuration
- Personal metrics
- Activity patterns
- Health score

#### API Endpoints:

**2.1 Получить Personal Digital Twin**
```typescript
GET /api/v1/personal-twin/me
Authorization: Bearer {token}

Response:
{
  "id": "pdt123",
  "user_id": "user123",
  "display_name": "John's Digital Twin",
  "workspace_config": {
    "theme": "dark",
    "dashboard_layout": ["insights", "tasks", "simulations"],
    "notifications_enabled": true
  },
  "personal_metrics": {
    "exercises_completed": 15,
    "simulations_run": 42,
    "average_response_time_hours": 2.5
  },
  "activity_patterns": {
    "most_active_hours": [9, 10, 14, 15],
    "preferred_scenario_types": ["cyber_attack", "data_breach"]
  },
  "twin_health_score": 87.5,
  "sync_status": "active",
  "last_sync_at": "2025-10-01T12:00:00Z"
}
```

**2.2 Обновить Workspace Config**
```typescript
PATCH /api/v1/personal-twin/me/config
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "workspace_config": {
    "theme": "light",
    "dashboard_layout": ["tasks", "insights"]
  }
}

Response: PersonalDigitalTwin
```

---

### 3. BIA (Business Impact Analysis)

#### Features:
- **Queue Theory BIA** ⭐⭐⭐ (математический анализ)
- Список BIA анализов
- Визуализация результатов

#### API Endpoints:

**3.1 Запустить Queue Theory BIA** ⭐⭐⭐
```typescript
POST /api/v1/bia/queue-theory
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "name": "Order Processing System",
  "description": "Customer order processing pipeline",
  "arrival_rate": 10.0,        // заявок в час (λ)
  "service_rate": 12.0,         // обработок в час (μ)
  "num_servers": 2,             // количество серверов (c)
  "simulation_hours": 168,      // 1 неделя
  "revenue_per_hour": 50000.0,
  "cost_per_hour_downtime": 75000.0,
  "max_acceptable_wait": 0.5,   // часов
  "max_data_loss_hours": 2.0
}

Response:
{
  "bia_id": "bia123",
  "name": "Order Processing System",
  "queue_metrics": {
    "average_wait_time": 0.15,      // часов
    "average_queue_length": 1.5,    // заявок
    "server_utilization": 0.83,     // 83%
    "probability_wait": 0.45        // 45% chance
  },
  "business_impact": {
    "potential_revenue_loss_per_hour": 62500.0,
    "estimated_annual_risk": 547500000.0,
    "mtd": 720.0,                   // Maximum Tolerable Downtime (hours)
    "impact_category": "critical"
  },
  "rto_rpo_recommendations": {
    "recommended_rto_hours": 0.25,  // 15 минут
    "recommended_rpo_hours": 0.5,   // 30 минут
    "rationale": "Based on M/M/c queue theory and Erlang C formula..."
  },
  "recovery_strategies": [
    {
      "name": "Hot Standby",
      "estimated_cost_annual": 120000.0,
      "expected_rto_hours": 0.1,
      "risk_reduction_percentage": 95.0
    }
  ],
  "simulation_details": {
    "total_customers_served": 16800,
    "total_simulation_time": 168.0,
    "confidence_level": 0.95
  },
  "created_at": "2025-10-01T12:00:00Z"
}
```

**UI рекомендации для Queue Theory BIA:**

**Шаг 1: Input Form**
```tsx
// Разделить на секции:
1. Business Process Info
   - name, description

2. Queue Parameters (с подсказками!)
   - arrival_rate (λ) - "How many requests/customers arrive per hour?"
   - service_rate (μ) - "How many can be processed per hour per server?"
   - num_servers (c) - "How many parallel servers/workers?"

3. Financial Impact
   - revenue_per_hour
   - cost_per_hour_downtime

4. Tolerances
   - max_acceptable_wait (часов)
   - max_data_loss_hours (RPO max)

5. Simulation Settings
   - simulation_hours (default: 168 = 1 week)
```

**Шаг 2: Results Visualization**
```tsx
// Дашборд с карточками:

[Card 1: Queue Metrics]
- Average Wait Time: 0.15 hours (9 minutes) ✅
- Queue Length: 1.5 customers
- Server Utilization: 83% ⚠️ (high but OK)
- Probability of Wait: 45%

[Card 2: Business Impact]
- Potential Loss/Hour: $62,500 🔴
- Annual Risk: $547.5M 🚨
- MTD: 720 hours (30 days)
- Impact: CRITICAL

[Card 3: RTO/RPO Recommendations] ⭐
- Recommended RTO: 15 minutes
- Recommended RPO: 30 minutes
- Rationale: [показать полный текст]

[Card 4: Recovery Strategies]
Table с стратегиями:
| Strategy | Cost/Year | RTO | Risk Reduction |
|----------|-----------|-----|----------------|
| Hot Standby | $120k | 6 min | 95% |
| ... | ... | ... | ... |

[Card 5: Simulation Stats]
- Customers Served: 16,800
- Simulation Time: 168 hours
- Confidence: 95%
```

**Графики:**
1. **Wait Time Distribution** (histogram)
2. **Queue Length over Time** (line chart)
3. **Server Utilization** (gauge chart)
4. **Cost-Benefit Analysis** (bar chart comparing strategies)

**3.2 Получить список BIA**
```typescript
GET /api/v1/bia/
Authorization: Bearer {token}

Query params:
- organization_id?: string
- skip: number = 0
- limit: number = 100

Response: BIA[] (упрощенная версия без детальных metrics)
```

---

### 4. Scenarios (Сценарии)

#### Features:
- Список шаблонов сценариев
- **AI-генерация сценариев** ⭐⭐⭐ (Advanced AI)
- **Learning Loop** ⭐ (AI учится на результатах)
- Создание/редактирование вручную

#### API Endpoints:

**4.1 Получить список сценариев**
```typescript
GET /api/v1/scenarios/
Authorization: Bearer {token}

Query params:
- organization_id?: string
- category?: string
- difficulty?: string
- skip: number = 0
- limit: number = 100

Response:
{
  "items": ScenarioTemplate[],
  "total": 42,
  "skip": 0,
  "limit": 100
}

interface ScenarioTemplate {
  id: string;
  name: string;
  description: string;
  category: "cyber" | "natural_disaster" | "pandemic" | "supply_chain" | "technology_failure" | "human_error" | "custom";
  difficulty: "beginner" | "intermediate" | "advanced" | "expert";
  estimated_duration_minutes: number;
  objectives: string[];
  injects: Inject[];
  success_criteria: Record<string, any>;
  ai_generated: boolean;
  metadata?: Record<string, any>;
  created_at: string;
}

interface Inject {
  id: string;
  time_offset_minutes: number;
  title: string;
  description: string;
  inject_type: "information" | "question" | "decision" | "action";
  expected_actions: string[];
  severity: "low" | "medium" | "high" | "critical";
}
```

**4.2 Создать сценарий (вручную)**
```typescript
POST /api/v1/scenarios/
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "name": "Ransomware Attack on Critical Systems",
  "description": "Simulated ransomware infection...",
  "category": "cyber",
  "difficulty": "advanced",
  "estimated_duration_minutes": 120,
  "objectives": [
    "Contain the ransomware spread",
    "Assess data integrity",
    "Activate backup recovery"
  ],
  "injects": [
    {
      "time_offset_minutes": 0,
      "title": "Initial Detection",
      "description": "IT team reports encrypted files...",
      "inject_type": "information",
      "expected_actions": ["Isolate affected systems", "Alert CISO"],
      "severity": "critical"
    }
  ]
}

Response: ScenarioTemplate (201 Created)
```

**4.3 AI-генерация сценария** ⭐⭐⭐
```typescript
POST /api/v1/scenarios/ai-generate-advanced
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "organization_id": "org123",
  "base_category": "cyber",
  "difficulty": "advanced",
  "focus_areas": ["ransomware", "data_breach", "incident_response"],
  "duration_minutes": 120,
  "include_historical_context": true,  // использовать прошлые упражнения
  "complexity_level": 8                // 1-10
}

Response:
{
  "id": "scenario123",
  "name": "Advanced Persistent Threat: Supply Chain Attack",
  "description": "A sophisticated APT group has compromised...",
  "category": "cyber",
  "difficulty": "advanced",
  "estimated_duration_minutes": 120,
  "objectives": [
    "Identify the initial compromise vector",
    "Assess the scope of the breach",
    "Contain lateral movement",
    "Preserve evidence for forensics"
  ],
  "injects": [
    {
      "id": "inject1",
      "time_offset_minutes": 0,
      "title": "Anomalous Network Traffic Detected",
      "description": "SIEM alerts show unusual outbound connections from your supply chain management system to an IP in Eastern Europe...",
      "inject_type": "information",
      "expected_actions": [
        "Isolate affected systems",
        "Capture network traffic",
        "Alert incident response team"
      ],
      "severity": "high"
    },
    {
      "id": "inject2",
      "time_offset_minutes": 15,
      "title": "C-Level Pressure",
      "description": "CEO calls demanding to know if customer data is safe...",
      "inject_type": "decision",
      "expected_actions": [
        "Provide status update",
        "Assess data exposure"
      ],
      "severity": "medium"
    }
    // ... more injects
  ],
  "success_criteria": {
    "time_to_detection": 10,
    "time_to_containment": 30,
    "required_actions_completed": 0.8
  },
  "ai_generated": true,
  "metadata": {
    "ai_model": "gemma-2b",
    "generation_method": "advanced_with_context",
    "historical_scenarios_used": 5,
    "confidence_score": 0.92
  },
  "created_at": "2025-10-01T12:00:00Z"
}
```

**UI рекомендации для AI Generation:**

**Форма:**
```tsx
<Form>
  <Select label="Organization" />
  <Select label="Category" options={["cyber", "natural_disaster", ...]} />
  <Select label="Difficulty" options={["beginner", "intermediate", "advanced", "expert"]} />

  <MultiSelect
    label="Focus Areas"
    placeholder="e.g., ransomware, phishing, DDoS"
  />

  <Slider
    label="Duration (minutes)"
    min={30}
    max={480}
    step={30}
    default={120}
  />

  <Slider
    label="Complexity"
    min={1}
    max={10}
    step={1}
    default={5}
    description="1=Simple, 10=Extremely Complex"
  />

  <Checkbox
    label="Use Historical Context"
    description="AI will learn from past exercises"
    default={true}
  />

  <Button type="submit" loading={isGenerating}>
    🤖 Generate AI Scenario
  </Button>
</Form>
```

**Results Display:**
- Показать сгенерированный сценарий
- **Highlight AI-generated content** (badge "🤖 AI Generated")
- Confidence score (92%)
- Кнопки: "Save", "Edit", "Regenerate"

**4.4 Learning Loop** ⭐
```typescript
POST /api/v1/scenarios/learn-from-exercise
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "scenario_id": "scenario123",
  "exercise_id": "exercise456",
  "outcomes": {
    "success": true,
    "time_to_detection_minutes": 12,
    "time_to_containment_minutes": 35,
    "actions_completed": 0.85,
    "participant_feedback": "Too many injects at once",
    "areas_of_difficulty": ["forensics", "communication"],
    "effectiveness_score": 8.5
  },
  "improvements_needed": [
    "Spread injects more evenly",
    "Add more forensics guidance",
    "Simplify communication templates"
  ]
}

Response:
{
  "learning_recorded": true,
  "scenario_id": "scenario123",
  "ai_will_adapt": true,
  "message": "AI will incorporate this feedback into future scenario generations"
}
```

**UI:**
- Post-exercise feedback form
- Автоматически вызывается после завершения упражнения

---

### 5. Simulations (Симуляции)

#### Features:
- **Monte Carlo симуляции** (уже встроен в backend)
- Визуализация результатов
- Сравнение сценариев

#### API Endpoints:

**5.1 Запустить Monte Carlo симуляцию**
```typescript
POST /api/v1/simulations/monte-carlo
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "name": "Ransomware Impact Analysis",
  "base_scenario_id": "scenario123",
  "num_iterations": 10000,
  "parameters": {
    "initial_impact": {
      "mean": 500000,
      "std_dev": 100000,
      "distribution": "normal"
    },
    "recovery_time_hours": {
      "min": 24,
      "max": 168,
      "distribution": "uniform"
    },
    "data_loss_percentage": {
      "min": 0,
      "max": 0.15,
      "distribution": "beta",
      "alpha": 2,
      "beta": 5
    }
  }
}

Response:
{
  "simulation_id": "sim123",
  "name": "Ransomware Impact Analysis",
  "num_iterations": 10000,
  "results": {
    "financial_impact": {
      "mean": 487320.50,
      "median": 495000.00,
      "std_dev": 98450.25,
      "min": 245000.00,
      "max": 875000.00,
      "percentile_5": 325000.00,
      "percentile_95": 655000.00
    },
    "recovery_time": {
      "mean": 96.5,
      "median": 95.0,
      "percentile_90": 145.0
    }
  },
  "risk_metrics": {
    "var_95": 655000.00,        // Value at Risk (95%)
    "cvar_95": 720000.00,       // Conditional VaR
    "probability_exceed_budget": 0.23  // 23% chance > budget
  },
  "created_at": "2025-10-01T12:00:00Z"
}
```

**UI рекомендации:**
1. **Histogram** - distribution of financial impact
2. **Box plot** - quartiles и outliers
3. **CDF curve** - cumulative distribution
4. **Risk metrics cards** - VaR, CVaR, probabilities

**5.2 Получить результаты симуляции**
```typescript
GET /api/v1/simulations/{simulation_id}
Authorization: Bearer {token}

Response: Simulation (полные детали)
```

---

### 6. Exercises (Упражнения)

#### Features:
- Создание упражнения из сценария
- Live execution (с инджектами по времени)
- Participant tracking
- Scoring и оценка

#### API Endpoints:

**6.1 Создать упражнение**
```typescript
POST /api/v1/exercises/
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "name": "Q4 2025 Cyber Drill",
  "scenario_id": "scenario123",
  "scheduled_start": "2025-12-15T10:00:00Z",
  "participants": ["user1", "user2", "user3"],
  "facilitators": ["user4"]
}

Response: Exercise (201 Created)
```

**6.2 Запустить упражнение**
```typescript
POST /api/v1/exercises/{exercise_id}/start
Authorization: Bearer {token}

Response:
{
  "exercise_id": "exercise123",
  "status": "in_progress",
  "started_at": "2025-10-01T12:00:00Z",
  "current_inject": 0,
  "next_inject_in_seconds": 0
}
```

**6.3 WebSocket для live updates** (рекомендуется!)
```typescript
// Connect to WebSocket
ws://localhost:8000/ws/exercises/{exercise_id}?token={jwt_token}

// Messages от сервера:
{
  "type": "inject",
  "inject": {
    "id": "inject1",
    "title": "New Development",
    "description": "...",
    "severity": "high"
  },
  "timestamp": "2025-10-01T12:15:00Z"
}

{
  "type": "status_update",
  "status": "in_progress",
  "elapsed_minutes": 15,
  "remaining_minutes": 105
}

{
  "type": "completion",
  "final_score": 85.5,
  "summary": "..."
}
```

**UI:**
- **Live Exercise Dashboard** с таймером
- **Inject feed** (новые инджекты появляются в реальном времени)
- **Action log** (что делали участники)
- **Chat/Communication** между участниками
- **Facilitator controls** (pause, inject manually, end early)

---

### 7. Predictions (Прогнозы)

#### Features:
- AI прогнозы рисков
- Trend analysis
- Recommendations

#### API Endpoints:

**7.1 Получить прогнозы**
```typescript
GET /api/v1/predictions/
Authorization: Bearer {token}

Query params:
- organization_id?: string
- prediction_type?: string
- skip: number = 0
- limit: number = 100

Response: Prediction[]
```

**7.2 Создать прогноз**
```typescript
POST /api/v1/predictions/
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "organization_id": "org123",
  "prediction_type": "risk_forecast",
  "time_horizon_days": 90,
  "parameters": {
    "include_external_threats": true,
    "include_historical_patterns": true
  }
}

Response: Prediction (201 Created)
```

---

## 🎨 UI/UX Рекомендации

### Design System:

**Colors:**
```css
/* Primary */
--primary: #3B82F6;        /* Blue */
--primary-dark: #1E40AF;
--primary-light: #93C5FD;

/* Semantic */
--success: #22C55E;        /* Green */
--warning: #EAB308;        /* Yellow */
--error: #EF4444;          /* Red */
--info: #06B6D4;           /* Cyan */

/* Impact Levels */
--impact-low: #22C55E;     /* Green */
--impact-medium: #EAB308;  /* Yellow */
--impact-high: #F97316;    /* Orange */
--impact-critical: #EF4444;/* Red */

/* Neutrals */
--gray-50: #F9FAFB;
--gray-100: #F3F4F6;
--gray-900: #111827;
```

**Typography:**
```css
/* Headings */
h1: 32px, 700
h2: 24px, 600
h3: 20px, 600
h4: 16px, 600

/* Body */
body: 14px, 400
small: 12px, 400
```

**Spacing:**
```
4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px
```

### Layout:

```
┌──────────────────────────────────────────┐
│  Header: Logo, Org Selector, User Menu  │
├──────┬───────────────────────────────────┤
│      │                                   │
│  S   │                                   │
│  I   │          Main Content             │
│  D   │                                   │
│  E   │                                   │
│  B   │                                   │
│  A   │                                   │
│  R   │                                   │
│      │                                   │
└──────┴───────────────────────────────────┘

Sidebar menu:
- 🏢 Organizations
- 👤 Personal Twin
- 📊 BIA Analysis
- 📋 Scenarios
- 🎮 Simulations
- 🏃 Exercises
- 🔮 Predictions
- ⚙️ Settings
```

### Key Screens:

#### 1. Dashboard (Home)
```
┌─────────────────────────────────────────┐
│  AI Insights for {Organization}         │
├─────────────────────────────────────────┤
│                                         │
│  [Critical Insight Card] 🔴            │
│  [High Insight Card]     🟠            │
│  [Medium Insight Card]   🟡            │
│                                         │
├─────────────────────────────────────────┤
│  Quick Stats                            │
│  ┌──────┬──────┬──────┬──────┐        │
│  │Health│ Risk │Exer. │Scen. │        │
│  │ 87.5 │ Med  │  15  │  42  │        │
│  └──────┴──────┴──────┴──────┘        │
└─────────────────────────────────────────┘
```

#### 2. Queue Theory BIA
```
┌─────────────────────────────────────────┐
│  ← Back to BIA List                     │
├─────────────────────────────────────────┤
│                                         │
│  Queue Theory BIA Analysis              │
│                                         │
│  [Input Form]                           │
│   Business Process: [_______________]   │
│   Arrival Rate (λ): [____] req/hour    │
│   Service Rate (μ): [____] req/hour    │
│   Servers (c):      [__]                │
│   ...                                   │
│                                         │
│   [Run Analysis] button                 │
│                                         │
├─────────────────────────────────────────┤
│  Results (after running):               │
│                                         │
│  ┌─────────────────────────────────┐  │
│  │ Queue Metrics                    │  │
│  │ Wait Time: 9 min ✅             │  │
│  │ Utilization: 83% ⚠️             │  │
│  └─────────────────────────────────┘  │
│                                         │
│  [Charts: Distribution, Timeline]       │
│                                         │
│  ┌─────────────────────────────────┐  │
│  │ RTO/RPO Recommendations ⭐      │  │
│  │ RTO: 15 min | RPO: 30 min      │  │
│  └─────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

#### 3. AI Scenario Generator
```
┌─────────────────────────────────────────┐
│  Generate AI Scenario 🤖                │
├─────────────────────────────────────────┤
│                                         │
│  Organization: [Select v]               │
│  Category:     [Cyber v]                │
│  Difficulty:   [Advanced v]             │
│                                         │
│  Focus Areas (multi-select):            │
│  [x] Ransomware                         │
│  [x] Data Breach                        │
│  [ ] DDoS                               │
│                                         │
│  Duration: [====|====] 120 min          │
│  Complexity: [======|==] 8/10           │
│                                         │
│  [x] Use Historical Context             │
│                                         │
│  [🤖 Generate Scenario]                 │
│                                         │
├─────────────────────────────────────────┤
│  Generated Scenario (after):            │
│                                         │
│  📋 "Advanced Persistent Threat..."     │
│  🤖 AI Generated (Confidence: 92%)      │
│                                         │
│  Description: [...]                     │
│  Objectives: [...]                      │
│  Injects (15): [expand/collapse]        │
│                                         │
│  [Save] [Edit] [Regenerate]             │
└─────────────────────────────────────────┘
```

#### 4. Live Exercise Dashboard
```
┌─────────────────────────────────────────┐
│  Q4 2025 Cyber Drill  [In Progress]     │
│  ⏱️ Elapsed: 15 min | Remaining: 105 min│
├─────────────────────────────────────────┤
│                                         │
│  Current Inject:                        │
│  ┌─────────────────────────────────┐  │
│  │ 🔴 Anomalous Network Traffic     │  │
│  │ SIEM alerts show unusual...      │  │
│  │                                  │  │
│  │ Expected Actions:                │  │
│  │ [x] Isolate systems              │  │
│  │ [x] Capture traffic              │  │
│  │ [ ] Alert IR team                │  │
│  └─────────────────────────────────┘  │
│                                         │
│  Inject Timeline:                       │
│  • 0 min:  Initial Detection ✅         │
│  • 15 min: C-Level Pressure ⬅️ NOW     │
│  • 30 min: Media Inquiry (upcoming)     │
│                                         │
│  Participants: 👤👤👤 (3 online)        │
│                                         │
│  [Chat/Notes] [End Exercise]            │
└─────────────────────────────────────────┘
```

---

## 🔌 API Integration Patterns

### 1. Axios Setup
```typescript
// api/client.ts
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (add auth token)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor (handle errors)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### 2. React Query Setup
```typescript
// api/queries.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';

// Organizations
export const useOrganizations = () => {
  return useQuery({
    queryKey: ['organizations'],
    queryFn: async () => {
      const { data } = await apiClient.get('/api/v1/organizations/');
      return data as Organization[];
    },
  });
};

export const useOrganizationInsights = (orgId: string) => {
  return useQuery({
    queryKey: ['organizations', orgId, 'insights'],
    queryFn: async () => {
      const { data } = await apiClient.get(`/api/v1/organizations/${orgId}/insights`);
      return data;
    },
    enabled: !!orgId,
    refetchInterval: 60000, // Refetch every minute
  });
};

// Queue Theory BIA
export const useQueueTheoryBIA = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: QueueTheoryRequest) => {
      const { data } = await apiClient.post('/api/v1/bia/queue-theory', request);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bia'] });
    },
  });
};

// AI Scenario Generation
export const useAIScenarioGeneration = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: AdvancedAIRequest) => {
      const { data } = await apiClient.post('/api/v1/scenarios/ai-generate-advanced', request);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scenarios'] });
    },
  });
};
```

### 3. WebSocket Setup
```typescript
// api/websocket.ts
export class ExerciseWebSocket {
  private ws: WebSocket | null = null;

  connect(exerciseId: string, token: string) {
    const wsUrl = `ws://localhost:8000/ws/exercises/${exerciseId}?token=${token}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
    };
  }

  private handleMessage(message: any) {
    switch (message.type) {
      case 'inject':
        // Handle new inject
        break;
      case 'status_update':
        // Handle status update
        break;
      case 'completion':
        // Handle exercise completion
        break;
    }
  }

  disconnect() {
    this.ws?.close();
  }
}
```

---

## 📦 Recommended Tech Stack

### Core:
- **Next.js 14+** (App Router)
- **TypeScript 5+**
- **React 18+**

### State Management:
- **Zustand** (simple, lightweight) или
- **Redux Toolkit** (if complex state)

### UI:
- **shadcn/ui** + **TailwindCSS** (рекомендуется!) или
- **Material-UI v5**

### Data Fetching:
- **TanStack Query (React Query)** ⭐ обязательно!

### Charts:
- **recharts** (простые графики) или
- **chart.js** + **react-chartjs-2** (сложные)

### Forms:
- **react-hook-form** + **zod** (validation)

### API:
- **axios** (HTTP client)

### Real-time:
- **native WebSocket API** (для live exercises)

### Date/Time:
- **date-fns** или **dayjs**

### Testing:
- **Vitest** (unit tests)
- **Playwright** (e2e tests)

---

## 🚀 Development Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Project setup (Next.js, TypeScript, TailwindCSS)
- [ ] Authentication flow (login, logout, token management)
- [ ] API client setup (axios + React Query)
- [ ] Layout & navigation (sidebar, header)
- [ ] Design system (colors, typography, components)

### Phase 2: Core Features (Week 3-4)
- [ ] Organizations CRUD
- [ ] AI Insights Dashboard ⭐
- [ ] Personal Digital Twin page
- [ ] BIA list page

### Phase 3: Queue Theory BIA (Week 5)
- [ ] Queue Theory BIA form ⭐⭐⭐
- [ ] Results visualization (charts, cards)
- [ ] Export/Print functionality

### Phase 4: AI Scenarios (Week 6-7)
- [ ] Scenarios list
- [ ] Manual scenario creation
- [ ] **AI Scenario Generator** ⭐⭐⭐
- [ ] Learning Loop feedback form

### Phase 5: Simulations (Week 8)
- [ ] Monte Carlo simulation form
- [ ] Results visualization (histograms, CDF)
- [ ] Compare scenarios

### Phase 6: Exercises (Week 9-10)
- [ ] Create exercise from scenario
- [ ] **Live Exercise Dashboard** with WebSocket ⭐
- [ ] Participant view
- [ ] Facilitator controls
- [ ] Post-exercise scoring

### Phase 7: Polish (Week 11-12)
- [ ] Responsive design (mobile/tablet)
- [ ] Dark mode
- [ ] Accessibility (WCAG 2.1 AA)
- [ ] Performance optimization
- [ ] E2E tests
- [ ] Documentation

---

## 📝 Example Code Snippets

### Organizations Insights Component:
```tsx
// components/OrganizationInsights.tsx
import { useOrganizationInsights } from '@/api/queries';
import { TwinInsight } from '@/types';

interface Props {
  organizationId: string;
}

export function OrganizationInsights({ organizationId }: Props) {
  const { data, isLoading, error } = useOrganizationInsights(organizationId);

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  if (!data) return null;

  const { insights, summary } = data;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">AI Insights</h2>
        <InsightsSummary summary={summary} />
      </div>

      <div className="grid gap-4">
        {insights.map((insight: TwinInsight) => (
          <InsightCard key={insight.id} insight={insight} />
        ))}
      </div>
    </div>
  );
}

function InsightCard({ insight }: { insight: TwinInsight }) {
  const impactColor = {
    low: 'bg-green-100 border-green-500',
    medium: 'bg-yellow-100 border-yellow-500',
    high: 'bg-orange-100 border-orange-500',
    critical: 'bg-red-100 border-red-500',
  }[insight.impact];

  return (
    <div className={`p-4 rounded-lg border-l-4 ${impactColor}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <InsightIcon type={insight.type} />
            <h3 className="font-semibold">{insight.title}</h3>
            <Badge variant={insight.impact}>{insight.impact}</Badge>
          </div>

          <p className="text-sm text-gray-700 mb-3">{insight.description}</p>

          <div className="flex items-center gap-4 text-xs text-gray-600">
            <span>Confidence: {insight.confidence}%</span>
            <span>Source: {insight.source}</span>
          </div>

          {insight.actionable && insight.suggested_actions.length > 0 && (
            <div className="mt-3">
              <p className="text-xs font-medium text-gray-700 mb-1">Suggested Actions:</p>
              <ul className="space-y-1">
                {insight.suggested_actions.map((action, i) => (
                  <li key={i} className="text-xs text-gray-600 flex items-start gap-2">
                    <span className="text-blue-500">→</span>
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <ConfidenceMeter value={insight.confidence} />
      </div>
    </div>
  );
}
```

### Queue Theory BIA Form:
```tsx
// components/QueueTheoryBIAForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useQueueTheoryBIA } from '@/api/queries';

const schema = z.object({
  name: z.string().min(3),
  description: z.string().optional(),
  arrival_rate: z.number().positive(),
  service_rate: z.number().positive(),
  num_servers: z.number().int().positive(),
  simulation_hours: z.number().positive().default(168),
  revenue_per_hour: z.number().nonnegative(),
  cost_per_hour_downtime: z.number().nonnegative(),
  max_acceptable_wait: z.number().positive(),
  max_data_loss_hours: z.number().nonnegative(),
});

type FormData = z.infer<typeof schema>;

export function QueueTheoryBIAForm() {
  const { mutate, isLoading, data } = useQueueTheoryBIA();

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      simulation_hours: 168,
      num_servers: 1,
    },
  });

  const onSubmit = (formData: FormData) => {
    mutate(formData);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Section title="Business Process Information">
          <Input
            label="Process Name"
            {...register('name')}
            error={errors.name?.message}
            placeholder="e.g., Order Processing System"
          />
          <Textarea
            label="Description"
            {...register('description')}
            error={errors.description?.message}
            placeholder="Brief description of the business process"
          />
        </Section>

        <Section title="Queue Parameters">
          <div className="grid grid-cols-3 gap-4">
            <Input
              label="Arrival Rate (λ)"
              type="number"
              step="0.1"
              {...register('arrival_rate', { valueAsNumber: true })}
              error={errors.arrival_rate?.message}
              helpText="Requests arriving per hour"
            />
            <Input
              label="Service Rate (μ)"
              type="number"
              step="0.1"
              {...register('service_rate', { valueAsNumber: true })}
              error={errors.service_rate?.message}
              helpText="Requests processed per hour (per server)"
            />
            <Input
              label="Servers (c)"
              type="number"
              {...register('num_servers', { valueAsNumber: true })}
              error={errors.num_servers?.message}
              helpText="Number of parallel servers"
            />
          </div>
        </Section>

        <Section title="Financial Impact">
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Revenue per Hour"
              type="number"
              step="100"
              {...register('revenue_per_hour', { valueAsNumber: true })}
              error={errors.revenue_per_hour?.message}
              prefix="$"
            />
            <Input
              label="Downtime Cost per Hour"
              type="number"
              step="100"
              {...register('cost_per_hour_downtime', { valueAsNumber: true })}
              error={errors.cost_per_hour_downtime?.message}
              prefix="$"
            />
          </div>
        </Section>

        <Section title="Tolerances">
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Max Acceptable Wait (hours)"
              type="number"
              step="0.1"
              {...register('max_acceptable_wait', { valueAsNumber: true })}
              error={errors.max_acceptable_wait?.message}
              helpText="How long can customers wait?"
            />
            <Input
              label="Max Data Loss (hours)"
              type="number"
              step="0.5"
              {...register('max_data_loss_hours', { valueAsNumber: true })}
              error={errors.max_data_loss_hours?.message}
              helpText="RPO tolerance"
            />
          </div>
        </Section>

        <Section title="Simulation Settings">
          <Input
            label="Simulation Duration (hours)"
            type="number"
            {...register('simulation_hours', { valueAsNumber: true })}
            error={errors.simulation_hours?.message}
            helpText="Default: 168 hours (1 week)"
          />
        </Section>

        <Button type="submit" loading={isLoading} size="lg" className="w-full">
          🔬 Run Queue Theory Analysis
        </Button>
      </form>

      {data && <QueueTheoryResults results={data} />}
    </div>
  );
}
```

---

## ✅ Checklist для разработчика

### Setup:
- [ ] Next.js 14+ project created
- [ ] TypeScript configured
- [ ] TailwindCSS setup
- [ ] ESLint + Prettier configured
- [ ] Environment variables (.env.local)
- [ ] API client setup (axios)
- [ ] React Query setup

### Authentication:
- [ ] Login page
- [ ] Token storage (localStorage)
- [ ] Protected routes (middleware)
- [ ] Auto-refresh tokens (optional)

### Core Features:
- [ ] Organizations list + CRUD
- [ ] AI Insights Dashboard ⭐
- [ ] Personal Digital Twin
- [ ] Queue Theory BIA ⭐⭐⭐
- [ ] AI Scenario Generator ⭐⭐⭐
- [ ] Simulations (Monte Carlo)
- [ ] Exercises (Live Dashboard)

### UI/UX:
- [ ] Responsive design (mobile-first)
- [ ] Dark mode support
- [ ] Loading states
- [ ] Error handling (toasts/alerts)
- [ ] Empty states
- [ ] Accessibility (keyboard navigation, ARIA)

### Testing:
- [ ] Unit tests (Vitest)
- [ ] E2E tests (Playwright)
- [ ] API integration tests

### Documentation:
- [ ] README.md
- [ ] Component Storybook (optional)
- [ ] API integration guide

---

## 🎉 Готово!

**Этот документ содержит:**
- ✅ Полное описание всех API endpoints
- ✅ TypeScript типы для всех моделей
- ✅ UI/UX рекомендации
- ✅ Code snippets и примеры
- ✅ Roadmap разработки
- ✅ Tech stack рекомендации

**Backend готов к интеграции:**
- 🔥 8 simulation engines встроены
- 🔥 Queue Theory BIA работает
- 🔥 Advanced AI Generator работает
- 🔥 150+ тестов покрывают всё
- 🔥 Docker готов к деплою

**Можно начинать фронтенд разработку!** 🚀

---

**Вопросы?** Swagger UI: http://localhost:8000/docs
