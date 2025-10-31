# BCM Platform - Comprehensive Development Guide

> **Единое руководство по разработке всех 28 BCM модулей**
> 
> Этот документ содержит полную стратегию, техническое задание и инструкции для разработки unified BCM платформы.

---

## 📑 Содержание

1. [Обзор проекта](#обзор-проекта)
2. [Текущий статус](#текущий-статус)
3. [Архитектура и стандарты](#архитектура-и-стандарты)
4. [Стратегия разработки](#стратегия-разработки)
5. [АКТИВНОЕ ТЗ: AI Control Center](#активное-тз-ai-control-center)
6. [Планы следующих модулей](#планы-следующих-модулей)
7. [Cross-module интеграция](#cross-module-интеграция)
8. [Автоматизация и инструменты](#автоматизация-и-инструменты)
9. [Quality Assurance](#quality-assurance)
10. [Timeline и milestones](#timeline-и-milestones)

---

## 🎯 Обзор проекта

### **Цель:**
Создать современную unified BCM платформу на Next.js 15 с 28 специализированными модулями, интегрированную с Odoo backend и AI-сервисами.

### **Технический стек:**
- **Frontend:** Next.js 15, React 19, TypeScript
- **Styling:** Tailwind CSS 4, shadcn/ui
- **State:** React Query + Zustand
- **Backend:** Odoo 18.0 + микросервисы
- **AI:** 10 специализированных AI органов

### **Ключевые принципы:**
1. **Модульная архитектура** - независимые, но интегрированные компоненты
2. **API-first подход** - готовность к backend интеграции
3. **Consistent UX** - единообразный пользовательский опыт
4. **Real-time интеграция** - живые данные между модулями
5. **Progressive enhancement** - от mock данных к real-time

---

## 📊 Текущий статус

### ✅ **Завершено:**
- **Platform foundation** - Next.js setup, navigation, API layer
- **Risk Management модуль** - полностью функционален
- **BIA Module** - полностью функционален
- **Development standards** - паттерны и guidelines

### 🔄 **В разработке:**
- **AI Control Center** - детальное ТЗ готово (см. раздел ниже)

### 📋 **Планы:**
- **BCM Core** - организационный контекст (следующий)
- **25 остальных модулей** - по фазам разработки

---

## 🏗️ Архитектура и стандарты

### **Структура проекта:**
```
unified-bcm-platform/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Main layout с navigation
│   ├── page.tsx           # Dashboard homepage
│   └── modules/           # Маршруты модулей
│       ├── risk-management/
│       ├── bia/
│       └── ai-control/
├── components/
│   ├── dashboard/         # Dashboard компоненты
│   ├── layout/           # Layout компоненты
│   ├── modules/          # Компоненты модулей
│   └── ui/              # Переиспользуемые UI
├── lib/
│   ├── api.ts           # API клиент
│   ├── store.ts         # Global state
│   └── utils.ts         # Утилиты
└── types/               # TypeScript типы
```

### **Стандартный паттерн модуля:**
```tsx
// components/modules/ModuleName.tsx
'use client'

import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Button } from '@/components/ui/button'

interface ModuleData {
  // TypeScript интерфейсы
}

export function ModuleNameModule() {
  const [filter, setFilter] = useState<string>('all')
  
  const { data, isLoading } = useQuery({
    queryKey: ['module-data', filter],
    queryFn: async () => {
      // API call или mock данные
    }
  })

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <ModuleHeader />
      
      {/* Metrics */}
      <MetricsGrid />
      
      {/* Filters */}
      <FilterSection />
      
      {/* Main Content */}
      <MainContent />
    </div>
  )
}
```

### **UI/UX стандарты:**

#### **Цветовая система:**
```css
/* Статусы */
.status-active { @apply bg-green-100 text-green-800; }
.status-warning { @apply bg-yellow-100 text-yellow-800; }
.status-error { @apply bg-red-100 text-red-800; }
.status-inactive { @apply bg-gray-100 text-gray-800; }

/* Категории модулей */
.category-core { @apply bg-blue-50 border-blue-200; }
.category-business { @apply bg-purple-50 border-purple-200; }
.category-analytics { @apply bg-green-50 border-green-200; }
.category-ai { @apply bg-violet-50 border-violet-200; }
```

#### **Компонентная библиотека:**
- **MetricCard** - стандартные KPI карточки
- **DataTable** - таблицы с сортировкой
- **StatusIndicator** - цветовые индикаторы
- **FilterButton** - кнопки фильтров
- **HealthBar** - полосы прогресса
- **ActionButton** - кнопки с loading состояниями

#### **Responsive breakpoints:**
- **Mobile:** < 768px - стек карточек
- **Tablet:** 768px - 1024px - адаптированная сетка
- **Desktop:** > 1024px - полная функциональность

---

## 📈 Стратегия разработки

### **ЭТАП 1: CORE MVP (4 модуля)**
**Цель:** Минимально жизнеспособная платформа

1. ✅ **Risk Management** - управление рисками (ГОТОВ)
2. ✅ **BIA Module** - анализ воздействия (ГОТОВ)
3. 🔄 **AI Control Center** - управление AI (В РАЗРАБОТКЕ)
4. ⚡ **BCM Core** - организационный контекст (СЛЕДУЮЩИЙ)

### **ЭТАП 2A: BUSINESS CRITICAL BATCH (5 модулей)**
**Подход:** Групповая разработка для эффективности

5. **Incident Management** - управление инцидентами
6. **Governance** - стратегическое управление
7. **Plans Management** - планы непрерывности
8. **Reporting** - кросс-модульная аналитика
9. **Configuration** - настройки системы

### **ЭТАП 2B: ANALYTICS BATCH (3 модуля)**
10. **KPI Management** - ключевые показатели
11. **Audit** - аудит и соответствие
12. **Context Management** - управление контекстом

### **ЭТАП 3: TRAINING ECOSYSTEM (4 модуля)**
13. **Training** - система обучения
14. **Community** - профессиональное сообщество
15. **Scenario Hub** - маркетплейс сценариев
16. **Exercise** - учения и симуляции

### **ЭТАП 4: ADVANCED FEATURES (12 модулей)**
**Подход:** Template-based + специализация

**Digital Twin группа:**
17-20. Digital Twin Core, AI Twin Orchestrator, Corporate Twin, Digital Copy Manager

**Client Services группа:**
21-23. Clients, Portal, Templates

**AI Advanced группа:**
24-28. AI Assistant, Intelligent Base, AI Consultant, Admin Website, Incident Core

---

## 🎯 АКТИВНОЕ ТЗ: AI Control Center

> **ЗАДАЧА ДЛЯ CLAUDE CODE:** Создать модуль AI Control Center согласно данной спецификации

### **Обзор модуля:**
**Название:** AI Control Center  
**Модуль:** `bcm_ai_control`  
**Приоритет:** Критический (Core Infrastructure)  
**Описание:** Центр управления Digital BCM Organism с 10 специализированными AI органами

### **Функциональные требования:**

#### **10 AI Органов для мониторинга:**
```typescript
const AI_ORGANS = [
  { 
    id: 'governance-brain', 
    name: 'Governance Brain', 
    category: 'strategic',
    description: 'Strategic decision-making and policy guidance',
    capabilities: ['strategy', 'governance', 'policy'],
    icon: 'Crown'
  },
  { 
    id: 'risk-advisor', 
    name: 'Risk Advisor', 
    category: 'analysis',
    description: 'Risk assessment and predictive analysis',
    capabilities: ['risk-analysis', 'prediction', 'monte-carlo'],
    icon: 'Shield'
  },
  { 
    id: 'incident-commander', 
    name: 'Incident Commander', 
    category: 'response',
    description: 'Emergency response coordination',
    capabilities: ['incident-response', 'coordination', 'escalation'],
    icon: 'Zap'
  },
  { 
    id: 'training-mentor', 
    name: 'Training Mentor', 
    category: 'learning',
    description: 'Learning optimization and competency development',
    capabilities: ['training', 'assessment', 'personalization'],
    icon: 'GraduationCap'
  },
  { 
    id: 'audit-inspector', 
    name: 'Audit Inspector', 
    category: 'compliance',
    description: 'Compliance monitoring and audit automation',
    capabilities: ['audit', 'compliance', 'iso-22301'],
    icon: 'CheckCircle'
  },
  { 
    id: 'recovery-planner', 
    name: 'Recovery Planner', 
    category: 'planning',
    description: 'Business recovery strategy development',
    capabilities: ['recovery-planning', 'rto-optimization', 'resource-allocation'],
    icon: 'Calendar'
  },
  { 
    id: 'communication-hub', 
    name: 'Communication Hub', 
    category: 'coordination',
    description: 'Stakeholder communication management',
    capabilities: ['communication', 'stakeholder-management', 'messaging'],
    icon: 'MessageCircle'
  },
  { 
    id: 'resource-manager', 
    name: 'Resource Manager', 
    category: 'optimization',
    description: 'Resource optimization and allocation',
    capabilities: ['resource-optimization', 'allocation', 'cost-analysis'],
    icon: 'Settings'
  },
  { 
    id: 'performance-monitor', 
    name: 'Performance Monitor', 
    category: 'analytics',
    description: 'KPI tracking and performance analysis',
    capabilities: ['kpi-tracking', 'performance-analysis', 'reporting'],
    icon: 'TrendingUp'
  },
  { 
    id: 'knowledge-keeper', 
    name: 'Knowledge Keeper', 
    category: 'documentation',
    description: 'Knowledge management and documentation',
    capabilities: ['knowledge-management', 'documentation', 'search'],
    icon: 'FileText'
  }
]
```

#### **Структура интерфейса:**

**1. Заголовок модуля:**
```tsx
<div className="flex items-center justify-between">
  <div>
    <h1 className="text-3xl font-bold text-gray-900">AI Control Center</h1>
    <p className="text-gray-600">Digital BCM Organism Management</p>
  </div>
  <div className="flex gap-3">
    <Button variant="outline">
      <RefreshCw className="h-4 w-4 mr-2" />
      Refresh All
    </Button>
    <Button variant="destructive">
      <Power className="h-4 w-4 mr-2" />
      Emergency Stop
    </Button>
    <Button>
      <Settings className="h-4 w-4 mr-2" />
      Settings
    </Button>
  </div>
</div>
```

**2. Системные метрики (4 карточки):**
```tsx
<div className="grid grid-cols-1 md:grid-cols-4 gap-6">
  <MetricCard 
    title="Active Organs"
    value={`${activeOrgans}/10`}
    icon={Brain}
    color="blue"
  />
  <MetricCard 
    title="System Health"
    value={`${averageHealth}%`}
    icon={Activity}
    color="green"
  />
  <MetricCard 
    title="Tokens Today"
    value={totalTokens}
    icon={Zap}
    color="purple"
  />
  <MetricCard 
    title="Avg Response"
    value={`${avgResponseTime}ms`}
    icon={Clock}
    color="yellow"
  />
</div>
```

**3. Сетка AI Органов (2x5):**
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
  {AI_ORGANS.map((organ) => (
    <AIOrganCard key={organ.id} organ={organ} />
  ))}
</div>
```

**4. Панель активности:**
```tsx
<div className="bg-white rounded-lg border p-6">
  <h3 className="text-lg font-semibold mb-4">AI Activity Log</h3>
  <div className="space-y-3 max-h-96 overflow-y-auto">
    {decisionLog.map((decision) => (
      <AIDecisionItem key={decision.id} decision={decision} />
    ))}
  </div>
</div>
```

### **TypeScript интерфейсы:**
```typescript
interface AIOrgan {
  id: string
  name: string
  category: 'strategic' | 'analysis' | 'response' | 'learning' | 'compliance' | 'planning' | 'coordination' | 'optimization' | 'analytics' | 'documentation'
  description: string
  status: 'active' | 'idle' | 'error' | 'maintenance' | 'initializing'
  health: number // 0-100
  lastActivity: string // ISO timestamp
  responseTime: number // milliseconds
  tokensUsed: number // today's usage
  capabilities: string[]
  configuration: {
    enabled: boolean
    maxTokensPerDay: number
    priorityLevel: number
    autoRestart: boolean
  }
}

interface AISystemMetrics {
  activeOrgans: number
  totalOrgans: number
  averageHealth: number
  totalTokensToday: number
  averageResponseTime: number
  systemLoad: number
  lastUpdate: string
}

interface AIDecisionLog {
  id: string
  organId: string
  organName: string
  timestamp: string
  decision: string
  confidence: number
  context: string
  category: string
  impact: 'low' | 'medium' | 'high' | 'critical'
  executionTime: number
}
```

### **Mock данные:**
```typescript
function generateMockAIOrgans(): AIOrgan[] {
  return AI_ORGANS.map((organ, index) => ({
    ...organ,
    status: getRandomStatus(),
    health: Math.floor(Math.random() * 30) + 70, // 70-100%
    lastActivity: new Date(Date.now() - Math.random() * 3600000).toISOString(),
    responseTime: Math.floor(Math.random() * 150) + 50, // 50-200ms
    tokensUsed: Math.floor(Math.random() * 5000) + 1000, // 1000-6000
    configuration: {
      enabled: Math.random() > 0.1,
      maxTokensPerDay: 10000,
      priorityLevel: Math.floor(Math.random() * 5) + 1,
      autoRestart: true
    }
  }))
}

function generateMockDecisionLog(): AIDecisionLog[] {
  const decisions = [
    "Risk threshold exceeded for manufacturing line",
    "BIA analysis completed for customer services", 
    "Incident escalation triggered for data center",
    "Training gap identified in crisis response",
    "Compliance deviation detected in security policy",
    "Recovery plan optimization suggested",
    "Stakeholder notification sent automatically",
    "Resource reallocation recommended",
    "KPI target adjustment needed",
    "Knowledge base updated with new procedures"
  ]
  
  return decisions.map((decision, i) => ({
    id: `decision-${i}`,
    organId: AI_ORGANS[i % AI_ORGANS.length].id,
    organName: AI_ORGANS[i % AI_ORGANS.length].name,
    timestamp: new Date(Date.now() - i * 300000).toISOString(),
    decision,
    confidence: Math.random() * 30 + 70,
    context: `Context for ${decision}`,
    category: AI_ORGANS[i % AI_ORGANS.length].category,
    impact: ['low', 'medium', 'high', 'critical'][Math.floor(Math.random() * 4)] as any,
    executionTime: Math.floor(Math.random() * 100) + 50
  }))
}
```

### **API интеграция:**
```typescript
// hooks/useAIOrgans.ts
export function useAIOrgans() {
  return useQuery({
    queryKey: ['ai-organs'],
    queryFn: async () => {
      // Real API (когда backend готов):
      // const response = await fetch('/api/ai/organs/status')
      // return response.json()
      
      // Mock для разработки:
      return generateMockAIOrgans()
    },
    refetchInterval: 10000, // 10 seconds auto-refresh
  })
}

export function useAIOrganControl() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ organId, action }: { organId: string, action: 'start' | 'stop' | 'restart' }) => {
      // Real API call:
      // const response = await fetch(`/api/ai/organs/${organId}/${action}`, { method: 'POST' })
      // return response.json()
      
      // Mock response:
      return { success: true, organId, action }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-organs'] })
    }
  })
}
```

### **Компоненты для создания:**

#### **1. Основной модуль:**
```typescript
// components/modules/AIControlCenter.tsx
export function AIControlCenter() {
  // Основная логика модуля
}
```

#### **2. AI Organ Card:**
```typescript
// components/ui/AIOrganCard.tsx
interface AIOrganCardProps {
  organ: AIOrgan
  onAction: (organId: string, action: string) => void
}

export function AIOrganCard({ organ, onAction }: AIOrganCardProps) {
  // Карточка отдельного органа
}
```

#### **3. Health Bar:**
```typescript
// components/ui/HealthBar.tsx
interface HealthBarProps {
  health: number
  size?: 'sm' | 'md' | 'lg'
  animated?: boolean
}

export function HealthBar({ health, size = 'md', animated = true }: HealthBarProps) {
  // Полоса здоровья
}
```

#### **4. Status Indicator:**
```typescript
// components/ui/StatusIndicator.tsx
interface StatusIndicatorProps {
  status: AIOrgan['status']
  pulse?: boolean
}

export function StatusIndicator({ status, pulse = false }: StatusIndicatorProps) {
  // Индикатор статуса
}
```

### **Файлы для создания:**
1. ✅ `components/modules/AIControlCenter.tsx` - основной компонент
2. ✅ `app/modules/ai-control/page.tsx` - страница модуля
3. ✅ `components/ui/AIOrganCard.tsx` - карточка органа
4. ✅ `components/ui/HealthBar.tsx` - полоса здоровья
5. ✅ `components/ui/StatusIndicator.tsx` - статус индикатор
6. ✅ `hooks/useAIOrgans.ts` - React Query hooks
7. ✅ Обновить `components/layout/Navigation.tsx` - добавить ссылку

### **Критерии приемки:**
- [ ] Все 10 AI органов отображаются корректно
- [ ] Системные метрики показывают реальные данные
- [ ] Кнопки управления работают (mock)
- [ ] Real-time обновления каждые 10 секунд
- [ ] Responsive дизайн на всех экранах
- [ ] Нет ошибок TypeScript
- [ ] Соответствует design system платформы
- [ ] Навигация в модуль работает

---

## 📋 Планы следующих модулей

### **BCM Core (следующий после AI Control Center):**
```typescript
// Организационный контекст и базовая функциональность
interface BCMCoreModule {
  organizations: Organization[]
  businessUnits: BusinessUnit[]
  criticalFunctions: CriticalFunction[]
  stakeholders: Stakeholder[]
  dependencies: Dependency[]
}

// Функциональность:
- Профиль организации
- Иерархия бизнес-единиц
- Критические функции
- Заинтересованные стороны
- Матрица зависимостей
```

### **Business Critical Batch (5 модулей):**
После завершения Core, создать batch ТЗ для:
- Incident Management
- Governance
- Plans Management
- Reporting
- Configuration

---

## 🔗 Cross-module интеграция

### **Integration Levels:**

#### **Level 1: Data Sharing**
```typescript
// Общие данные между модулями
interface SharedBCMData {
  organizations: Organization[]
  risks: Risk[]
  biaResults: BIAResult[]
  incidents: Incident[]
  plans: BCPlan[]
  aiOrgans: AIOrgan[]
}
```

#### **Level 2: State Management**
```typescript
// lib/bcm-store.ts - Zustand store
interface BCMGlobalStore {
  currentOrganization: Organization
  selectedContext: BCMContext
  
  // Module states
  riskManagement: RiskState
  biaAnalysis: BIAState
  aiControl: AIState
  
  // Cross-module actions
  linkRiskToBIA: (riskId: string, biaId: string) => void
  triggerAIAnalysis: (type: string, data: any) => void
}
```

#### **Level 3: Real-time Events**
```typescript
// Event-driven архитектура
interface BCMEvents {
  'risk:created': Risk
  'bia:completed': BIAResult
  'incident:triggered': Incident
  'ai:recommendation': AIRecommendation
}
```

#### **Level 4: UI Integration**
```typescript
// Cross-module navigation
interface NavigationIntegration {
  riskToBIA: (riskId: string) => string
  biaToRisk: (biaId: string) => string
  aiOrganToModule: (organId: string) => string
}
```

### **Интеграция AI Control Center:**
После создания модуля добавить связи:
- Клик по "Risk Advisor" → переход в Risk Management
- Клик по органу BIA → переход в BIA Module
- Preview данных из других модулей в AI панелях

---

## 🛠️ Автоматизация и инструменты

### **Module Generator (после 8-10 модулей):**
```bash
npm run generate-module --name="Audit" --category="compliance"

# Автоматически создает:
# - components/modules/Audit.tsx
# - app/modules/audit/page.tsx
# - types/audit.ts
# - hooks/useAuditData.ts
# - mocks/audit-data.ts
```

### **Component CLI:**
```bash
npm run create-component MetricCard --type=ui
npm run create-component DataTable --type=shared
npm run link-modules --from=Risk --to=BIA --type=data-flow
```

---

## ✅ Quality Assurance

### **Testing Strategy:**
```typescript
// Unit тесты для каждого модуля
describe('AIControlCenter', () => {
  test('renders AI organs correctly')
  test('handles status updates')
  test('processes control actions')
})

// Integration тесты
describe('ModuleIntegration', () => {
  test('AI organ links to correct modules')
  test('Cross-module data flow works')
})
```

### **Code Quality:**
```json
// tsconfig.json - strict TypeScript
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

---

## 📅 Timeline и milestones

### **Milestone 1: Core MVP**
**Target:** Первые 4 модуля интегрированы
- ✅ Risk Management (готов)
- ✅ BIA Module (готов)
- 🔄 AI Control Center (в разработке)
- ⚡ BCM Core (следующий)

**Success Criteria:**
- [ ] Все 4 модуля функциональны
- [ ] Cross-module navigation работает
- [ ] Shared state management настроен
- [ ] Real-time обновления работают

### **Milestone 2: Business Critical**
**Target:** 9 модулей с полной функциональностью

### **Milestone 3: Complete Platform**
**Target:** Все 28 модулей реализованы

---

## 🚀 Immediate Action Plan

### **ШАГ 1: АКТИВНАЯ ЗАДАЧА**
**Для Claude Code:**
```
Создай модуль AI Control Center согласно спецификации 
в разделе "АКТИВНОЕ ТЗ" этого документа.
```

### **ШАГ 2: Интеграция**
После создания AI Control Center:
- Настроить cross-module navigation
- Добавить preview компоненты
- Реализовать shared data flow

### **ШАГ 3: BCM Core**
Создать организационный контекст модуль

### **ШАГ 4: Batch Development**
Подготовить ТЗ для Business Critical batch

---

**🎯 ГОТОВ К РАЗРАБОТКЕ: Начинай с AI Control Center модуля!**
