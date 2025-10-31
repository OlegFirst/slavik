# 🔍 BIA MODULE - ПОЛНЫЙ АУДИТ И ПЛАН РЕАЛИЗАЦИИ

**Дата аудита**: 17 сентября 2025
**Модуль**: Business Impact Analysis (BIA)
**Статус**: 🟡 **65% готовности**
**Критичность**: ⚠️ **ВЫСОКАЯ** - ключевой модуль ISO 22301

## 📊 ТЕКУЩЕЕ СОСТОЯНИЕ

### ✅ ЧТО УЖЕ РЕАЛИЗОВАНО (35%)

1. **Базовая структура данных**:
   - ✅ Интерфейс `BIAResult` с полными полями
   - ✅ RTO/RPO/MTPD показатели
   - ✅ Уровни критичности (low/medium/high/critical)
   - ✅ Отслеживание зависимостей (dependencies)

2. **UI компоненты**:
   - ✅ Таблица результатов BIA
   - ✅ Метрики карточки (4 основных показателя)
   - ✅ Фильтрация по департаментам
   - ✅ ML Recommendations панель (статичная)

3. **Базовые вычисления**:
   - ✅ Расчет финансового воздействия
   - ✅ Суммарные метрики (totalFunctions, criticalFunctions)

### 🔴 КРИТИЧЕСКИЕ ПРОПУСКИ (65%)

#### 1. **BIA QUESTIONNAIRE INTERFACE** ❌
```typescript
// ОТСУТСТВУЕТ: Интерфейс для проведения BIA опросов
interface BIAQuestionnaire {
  id: string
  sections: QuestionSection[]
  respondent: User
  status: 'draft' | 'in_progress' | 'completed'
  completionPercentage: number
}

// Нужны формы для:
- Идентификация критических процессов
- Оценка воздействия на репутацию
- Финансовые потери по временным периодам
- Определение минимальных ресурсов
- Взаимозависимости процессов
```

#### 2. **DEPENDENCY MAPPING VISUALIZATION** ❌
```typescript
// Данные есть, но НЕТ визуализации
dependencies: ['Payment Gateway', 'Inventory System', 'CRM']

// Нужно:
- Интерактивная карта зависимостей (D3.js/Recharts)
- Граф связей между функциями
- Cascading failure analysis
- Critical path highlighting
```

#### 3. **IMPACT TIMELINE CHARTS** ❌
```typescript
// ОТСУТСТВУЕТ: Временная шкала воздействия
interface ImpactTimeline {
  function: string
  impactOverTime: {
    hour1: number
    hour4: number
    hour8: number
    hour24: number
    day3: number
    week1: number
  }
  recoveryMilestones: Milestone[]
}
```

#### 4. **CRITICAL PATH ANALYSIS** ❌
```typescript
// НЕТ анализа критических путей восстановления
interface CriticalPath {
  pathId: string
  steps: RecoveryStep[]
  totalDuration: number
  bottlenecks: Bottleneck[]
  alternativePaths: Path[]
}
```

#### 5. **ML OPTIMIZATION ENGINE** ❌
```typescript
// Заявлена "AI-powered BIA Engine v2.0", но НЕТ:
- Автоматического определения RTO на основе исторических данных
- Предиктивного анализа воздействия
- Оптимизации ресурсов восстановления
- Динамической приоритизации
```

#### 6. **AUTOMATED BIA REPORTS** ❌
```typescript
// ОТСУТСТВУЕТ генерация отчетов
interface BIAReport {
  executive_summary: string
  critical_functions: Function[]
  recovery_priorities: Priority[]
  resource_requirements: Resources
  recommendations: string[]
  export_formats: ['PDF', 'Excel', 'Word']
}
```

#### 7. **WHAT-IF SCENARIOS** ❌
```typescript
// НЕТ сценарного моделирования
interface ScenarioModeling {
  scenario: string // "Data center failure", "Pandemic", etc.
  affected_functions: string[]
  impact_simulation: SimulationResult
  recovery_strategies: Strategy[]
}
```

#### 8. **RECOVERY PRIORITIZATION** ❌
```typescript
// ОТСУТСТВУЮТ инструменты приоритизации
interface RecoveryPriority {
  function: string
  priority_score: number
  recovery_sequence: number
  required_resources: Resource[]
  dependencies_resolved: boolean
}
```

### 🔴 MOCK ДАННЫЕ (100% MOCK!)

```typescript
// ВСЕ данные в модуле - это MOCK
function getMockBIAResults(): BIAResult[] {
  return [
    {
      id: '1',
      businessFunction: 'Customer Order Processing',
      // ... все hardcoded
    }
  ]
}

// Метрики тоже mock:
queryFn: async () => ({
  totalFunctions: 45,  // Hardcoded!
  criticalFunctions: 12, // Hardcoded!
  avgRTO: 4.2, // Hardcoded!
  totalFinancialRisk: 2500000 // Hardcoded!
})
```

## 🎯 ПЛАН РЕАЛИЗАЦИИ

### ЭТАП 1: API ИНТЕГРАЦИЯ (Убрать Mock)

```typescript
// 1. Создать BIA API Service
// services/bia-api.ts

import { BCMAPIClient } from '@/lib/api-client'

export interface BIAResult {
  id: string
  businessFunction: string
  department: string
  rto: number
  rpo: number
  mtpd: number
  financialImpactPerHour: number
  criticalityLevel: 'low' | 'medium' | 'high' | 'critical'
  dependencies: string[]
  lastAssessed: string
  // Новые поля:
  impactCategories: {
    reputation: number
    regulatory: number
    operational: number
    financial: number
  }
  resourceRequirements: {
    staff: number
    systems: string[]
    facilities: string[]
  }
}

class BIAApiService {
  private api: BCMAPIClient

  async getBIAResults(department?: string): Promise<BIAResult[]> {
    const endpoint = '/api/v1/bcm/bia/results'
    const params = department ? `?department=${department}` : ''

    const response = await this.api.request<BIAResult[]>(
      `${endpoint}${params}`,
      { method: 'GET' }
    )

    return response.data
  }

  async createBIAAssessment(data: Partial<BIAResult>): Promise<BIAResult> {
    return await this.api.request('/api/v1/bcm/bia/assessments', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async runBIAAnalysis(functionId: string): Promise<BIAResult> {
    return await this.api.request(`/api/v1/bcm/bia/analyze/${functionId}`, {
      method: 'POST'
    })
  }
}

export const biaAPI = new BIAApiService()
```

### ЭТАП 2: BIA QUESTIONNAIRE WIZARD

```typescript
// components/modules/bia/BIAQuestionnaire.tsx

export function BIAQuestionnaire() {
  const [currentStep, setCurrentStep] = useState(0)
  const [answers, setAnswers] = useState<Record<string, any>>({})

  const steps = [
    {
      title: 'Function Identification',
      questions: [
        {
          id: 'function_name',
          type: 'text',
          label: 'Business Function Name',
          required: true
        },
        {
          id: 'department',
          type: 'select',
          label: 'Department',
          options: ['IT', 'Finance', 'Operations', 'Sales', 'HR']
        },
        {
          id: 'criticality_self_assessment',
          type: 'slider',
          label: 'How critical is this function? (1-10)',
          min: 1,
          max: 10
        }
      ]
    },
    {
      title: 'Impact Assessment',
      questions: [
        {
          id: 'financial_impact_1h',
          type: 'currency',
          label: 'Financial impact after 1 hour outage'
        },
        {
          id: 'financial_impact_4h',
          type: 'currency',
          label: 'Financial impact after 4 hours'
        },
        {
          id: 'reputation_impact',
          type: 'scale',
          label: 'Reputation impact (1-5 scale)'
        }
      ]
    },
    {
      title: 'Recovery Requirements',
      questions: [
        {
          id: 'rto_hours',
          type: 'number',
          label: 'Recovery Time Objective (hours)'
        },
        {
          id: 'rpo_hours',
          type: 'number',
          label: 'Recovery Point Objective (hours)'
        },
        {
          id: 'min_staff_required',
          type: 'number',
          label: 'Minimum staff required'
        }
      ]
    },
    {
      title: 'Dependencies',
      questions: [
        {
          id: 'it_systems',
          type: 'multiselect',
          label: 'Required IT Systems',
          options: dynamicSystemsList
        },
        {
          id: 'upstream_dependencies',
          type: 'multiselect',
          label: 'Upstream Dependencies'
        },
        {
          id: 'downstream_impacts',
          type: 'multiselect',
          label: 'Downstream Impacts'
        }
      ]
    }
  ]

  return (
    <Dialog>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Business Impact Analysis Questionnaire</DialogTitle>
          <Progress value={(currentStep / steps.length) * 100} />
        </DialogHeader>

        <div className="py-6">
          <h3 className="text-lg font-medium mb-4">
            {steps[currentStep].title}
          </h3>

          <div className="space-y-4">
            {steps[currentStep].questions.map(question => (
              <QuestionField
                key={question.id}
                question={question}
                value={answers[question.id]}
                onChange={(value) => setAnswers({
                  ...answers,
                  [question.id]: value
                })}
              />
            ))}
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => setCurrentStep(currentStep - 1)}
            disabled={currentStep === 0}
          >
            Previous
          </Button>

          {currentStep < steps.length - 1 ? (
            <Button onClick={() => setCurrentStep(currentStep + 1)}>
              Next
            </Button>
          ) : (
            <Button onClick={submitBIAAssessment}>
              Complete Assessment
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

### ЭТАП 3: DEPENDENCY VISUALIZATION

```typescript
// components/modules/bia/DependencyMap.tsx

import { ForceGraph2D } from 'react-force-graph'

export function DependencyMap({ functions }: { functions: BIAResult[] }) {
  const graphData = {
    nodes: functions.map(f => ({
      id: f.id,
      name: f.businessFunction,
      criticality: f.criticalityLevel,
      val: f.criticalityLevel === 'critical' ? 20 : 10
    })),
    links: functions.flatMap(f =>
      f.dependencies.map(dep => ({
        source: f.id,
        target: dep,
        value: 1
      }))
    )
  }

  return (
    <div className="bg-white rounded-lg border p-6">
      <h3 className="text-lg font-semibold mb-4">Dependency Network</h3>

      <ForceGraph2D
        graphData={graphData}
        nodeLabel="name"
        nodeColor={node =>
          node.criticality === 'critical' ? '#EF4444' :
          node.criticality === 'high' ? '#F97316' :
          node.criticality === 'medium' ? '#EAB308' :
          '#10B981'
        }
        linkDirectionalArrowLength={6}
        linkDirectionalArrowRelPos={1}
        width={800}
        height={400}
        onNodeClick={(node) => {
          // Show details panel
          showFunctionDetails(node.id)
        }}
      />

      {/* Legend */}
      <div className="flex gap-4 mt-4">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-500 rounded-full" />
          <span className="text-sm">Critical</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-orange-500 rounded-full" />
          <span className="text-sm">High</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-yellow-500 rounded-full" />
          <span className="text-sm">Medium</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded-full" />
          <span className="text-sm">Low</span>
        </div>
      </div>
    </div>
  )
}
```

### ЭТАП 4: IMPACT TIMELINE VISUALIZATION

```typescript
// components/modules/bia/ImpactTimeline.tsx

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'

export function ImpactTimeline({ function }: { function: BIAResult }) {
  const timelineData = [
    { time: '0h', financial: 0, reputation: 0, operational: 0 },
    { time: '1h', financial: 50000, reputation: 1, operational: 2 },
    { time: '4h', financial: 200000, reputation: 2, operational: 3 },
    { time: '8h', financial: 500000, reputation: 3, operational: 4 },
    { time: '24h', financial: 1500000, reputation: 4, operational: 5 },
    { time: '3d', financial: 5000000, reputation: 5, operational: 5 },
    { time: '1w', financial: 10000000, reputation: 5, operational: 5 }
  ]

  return (
    <div className="bg-white rounded-lg border p-6">
      <h3 className="text-lg font-semibold mb-4">
        Impact Timeline: {function.businessFunction}
      </h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Financial Impact Chart */}
        <div>
          <h4 className="text-sm font-medium text-gray-600 mb-2">
            Financial Impact Over Time
          </h4>
          <LineChart width={400} height={250} data={timelineData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis tickFormatter={(value) => `$${(value/1000000).toFixed(1)}M`} />
            <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
            <Line
              type="monotone"
              dataKey="financial"
              stroke="#EF4444"
              strokeWidth={2}
            />
            {/* RTO Marker */}
            <ReferenceLine
              x={`${function.rto}h`}
              stroke="#10B981"
              label="RTO"
              strokeDasharray="5 5"
            />
            {/* MTPD Marker */}
            <ReferenceLine
              x={`${function.mtpd}h`}
              stroke="#EF4444"
              label="MTPD"
              strokeDasharray="5 5"
            />
          </LineChart>
        </div>

        {/* Multi-Impact Chart */}
        <div>
          <h4 className="text-sm font-medium text-gray-600 mb-2">
            Combined Impact Assessment
          </h4>
          <RadarChart width={400} height={250} data={impactCategories}>
            <PolarGrid />
            <PolarAngleAxis dataKey="category" />
            <PolarRadiusAxis angle={90} domain={[0, 5]} />
            <Radar
              name="Current State"
              dataKey="current"
              stroke="#3B82F6"
              fill="#3B82F6"
              fillOpacity={0.6}
            />
            <Radar
              name="After MTPD"
              dataKey="afterMTPD"
              stroke="#EF4444"
              fill="#EF4444"
              fillOpacity={0.6}
            />
            <Legend />
          </RadarChart>
        </div>
      </div>

      {/* Recovery Milestones */}
      <div className="mt-6">
        <h4 className="text-sm font-medium text-gray-600 mb-2">
          Recovery Milestones
        </h4>
        <div className="relative">
          <div className="absolute left-0 top-3 w-full h-0.5 bg-gray-200" />
          <div className="relative flex justify-between">
            {recoveryMilestones.map((milestone, index) => (
              <div key={index} className="flex flex-col items-center">
                <div className={cn(
                  "w-6 h-6 rounded-full border-2 bg-white z-10",
                  milestone.achieved ? "border-green-500" : "border-gray-300"
                )}>
                  {milestone.achieved && (
                    <CheckIcon className="w-4 h-4 text-green-500" />
                  )}
                </div>
                <div className="text-xs mt-1">{milestone.time}</div>
                <div className="text-xs text-gray-500">{milestone.action}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
```

### ЭТАП 5: ML OPTIMIZATION INTEGRATION

```typescript
// services/bia-ml-engine.ts

export class BIAMLEngine {
  async optimizeRTO(historicalData: HistoricalIncident[]): Promise<RTORecommendation> {
    // Анализ исторических данных инцидентов
    const patterns = this.analyzeRecoveryPatterns(historicalData)

    // ML модель для предсказания оптимального RTO
    const prediction = await this.predictOptimalRTO({
      function_type: patterns.functionType,
      historical_recovery_times: patterns.recoveryTimes,
      resource_availability: patterns.resources,
      cost_constraints: patterns.costs
    })

    return {
      recommended_rto: prediction.rto,
      confidence: prediction.confidence,
      cost_impact: prediction.costImpact,
      risk_reduction: prediction.riskReduction,
      justification: prediction.reasoning
    }
  }

  async prioritizeRecovery(functions: BIAResult[]): Promise<RecoverySequence> {
    // Граф зависимостей
    const dependencyGraph = this.buildDependencyGraph(functions)

    // Критический путь
    const criticalPath = this.findCriticalPath(dependencyGraph)

    // Оптимизация последовательности с учетом:
    // - Dependencies
    // - Resource constraints
    // - Financial impact
    // - Regulatory requirements

    return {
      sequence: optimizedSequence,
      parallel_tracks: parallelRecoveryTracks,
      resource_allocation: resourcePlan,
      estimated_total_recovery: totalTime
    }
  }

  async simulateScenario(scenario: DisruptionScenario): Promise<ImpactSimulation> {
    // Monte Carlo симуляция воздействия
    const simulations = await this.runMonteCarloSimulation({
      scenario_type: scenario.type,
      affected_functions: scenario.affectedFunctions,
      duration_distribution: scenario.durationEstimates,
      iterations: 10000
    })

    return {
      expected_impact: simulations.mean,
      worst_case: simulations.p95,
      best_case: simulations.p5,
      probability_distribution: simulations.distribution,
      key_vulnerabilities: simulations.weakPoints,
      mitigation_strategies: this.generateMitigations(simulations)
    }
  }
}
```

## 📋 IMPLEMENTATION CHECKLIST

### Immediate Actions (Sprint 1)
- [ ] Create `services/bia-api.ts` with full CRUD operations
- [ ] Replace all mock data with API calls
- [ ] Add loading states and error handling
- [ ] Implement BIA creation form

### Sprint 2
- [ ] Build BIA Questionnaire Wizard
- [ ] Add validation rules for RTO/RPO/MTPD
- [ ] Implement auto-save for questionnaire progress
- [ ] Create draft/publish workflow

### Sprint 3
- [ ] Implement Dependency Visualization (D3.js/Force Graph)
- [ ] Add interactive node details
- [ ] Build cascading failure analysis
- [ ] Create dependency editor interface

### Sprint 4
- [ ] Add Impact Timeline Charts
- [ ] Implement recovery milestone tracking
- [ ] Build what-if scenario simulator
- [ ] Create comparative analysis views

### Sprint 5
- [ ] Integrate ML optimization engine
- [ ] Add automated RTO recommendations
- [ ] Build recovery prioritization algorithm
- [ ] Implement cost-benefit analysis

### Sprint 6
- [ ] Create automated report generation
- [ ] Add export to PDF/Excel/Word
- [ ] Build executive dashboard
- [ ] Implement ISO 22301 compliance checks

## 🔄 INTEGRATION POINTS

### With Risk Management
```typescript
// Link risks to business functions
interface RiskToBIAMapping {
  riskId: string
  affectedFunctions: string[]
  impactMultiplier: number
}
```

### With Incident Management
```typescript
// Real-time BIA updates during incidents
interface IncidentBIAUpdate {
  incidentId: string
  affectedFunctions: string[]
  actualDowntime: number
  actualImpact: FinancialImpact
}
```

### With Plans Management
```typescript
// BIA drives plan priorities
interface BIAToPlanLink {
  functionId: string
  requiredPlans: string[]
  activationThreshold: number
}
```

## 📊 SUCCESS METRICS

1. **Functional Completeness**: From 65% to 100%
2. **Mock Data Elimination**: From 100% mock to 0% mock
3. **User Engagement**: BIA questionnaire completion rate > 80%
4. **Accuracy**: RTO predictions within 10% of actual
5. **Compliance**: 100% ISO 22301 clause coverage

## 🚀 EXPECTED OUTCOMES

После реализации всех компонентов:

1. **Полноценный BIA процесс** от опросов до отчетов
2. **Визуальная аналитика** зависимостей и воздействий
3. **ML-оптимизация** RTO/RPO на основе данных
4. **Автоматизация** приоритизации восстановления
5. **Интеграция** с другими модулями BCM платформы
6. **ISO 22301 соответствие** для BIA процессов

---

**Следующий шаг**: Начать с создания `bia-api.ts` сервиса и замены всех mock данных на реальные API вызовы.