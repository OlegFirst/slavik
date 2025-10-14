# Техническое задание для Claude Code

## 🎯 ЗАДАЧА: Создать модуль AI Control Center

**Модуль:** `bcm_ai_control` - Центр управления Digital BCM Organism  
**Приоритет:** Критический (Core Infrastructure, Фаза 1)  
**Статус:** К разработке  

---

## 📋 ТРЕБОВАНИЯ К РЕАЛИЗАЦИИ

### 1. Создать основной компонент
**Файл:** `components/modules/AIControlCenter.tsx`

### 2. Функциональные требования

#### **2.1 Мониторинг 10 AI Органов:**
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

#### **2.2 Основные блоки интерфейса:**

**Заголовок:**
- Название: "AI Control Center"
- Подзаголовок: "Digital BCM Organism Management"
- Кнопки: "Refresh All", "Emergency Stop", "Settings"

**Системные метрики (4 карточки):**
- Активные органы (X/10)
- Общий Health Score (средний %)
- Токены за сегодня (количество)
- Среднее время ответа (мс)

**Сетка AI Органов (2x5):**
- Карточка для каждого органа
- Статус индикатор (цветная точка)
- Health bar (0-100%)
- Последняя активность
- Время ответа
- Потребление токенов
- Кнопки управления (Start/Stop/Restart/Configure)

**Панель активности:**
- Лог последних 15 AI решений
- Real-time события
- Системные уведомления
- Фильтр по органам

**Конфигурация:**
- Настройки API ключей (скрытые)
- Лимиты токенов по органам
- Интервалы мониторинга
- Пороговые значения алертов

#### **2.3 TypeScript интерфейсы:**
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

interface AIAlert {
  id: string
  organId: string
  type: 'performance' | 'error' | 'capacity' | 'security'
  severity: 'info' | 'warning' | 'error' | 'critical'
  message: string
  timestamp: string
  resolved: boolean
}
```

### 3. UI/UX Спецификации

#### **3.1 Цветовая схема:**
```css
/* AI Organ статусы */
.status-active { @apply bg-green-100 text-green-800 border-green-200; }
.status-idle { @apply bg-yellow-100 text-yellow-800 border-yellow-200; }
.status-error { @apply bg-red-100 text-red-800 border-red-200; }
.status-maintenance { @apply bg-gray-100 text-gray-800 border-gray-200; }
.status-initializing { @apply bg-blue-100 text-blue-800 border-blue-200; }

/* AI категории */
.category-strategic { @apply bg-purple-50 border-purple-200; }
.category-analysis { @apply bg-blue-50 border-blue-200; }
.category-response { @apply bg-red-50 border-red-200; }
.category-learning { @apply bg-green-50 border-green-200; }
.category-compliance { @apply bg-yellow-50 border-yellow-200; }
```

#### **3.2 Health Bar компонент:**
```tsx
interface HealthBarProps {
  health: number
  size?: 'sm' | 'md' | 'lg'
  showPercentage?: boolean
  animated?: boolean
}
```

#### **3.3 Status Indicator:**
```tsx
interface StatusIndicatorProps {
  status: AIOrgan['status']
  pulse?: boolean
  size?: 'sm' | 'md' | 'lg'
}
```

#### **3.4 Иконки для категорий:**
- Strategic: `Crown` (Lucide)
- Analysis: `BarChart3`
- Response: `Zap`
- Learning: `GraduationCap` 
- Compliance: `CheckCircle`
- Planning: `Calendar`
- Coordination: `MessageCircle`
- Optimization: `Settings`
- Analytics: `TrendingUp`
- Documentation: `FileText`

### 4. Mock данные

#### **4.1 Реалистичные значения:**
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

### 5. API интеграция

#### **5.1 React Query hooks:**
```typescript
// hooks/useAIOrgans.ts
export function useAIOrgans() {
  return useQuery({
    queryKey: ['ai-organs'],
    queryFn: async () => {
      // Real API call:
      // const response = await fetch('/api/ai/organs/status')
      // return response.json()
      
      // Mock for now:
      return generateMockAIOrgans()
    },
    refetchInterval: 10000, // 10 seconds
  })
}

export function useAISystemMetrics() {
  return useQuery({
    queryKey: ['ai-system-metrics'],
    queryFn: async () => {
      // Real API call:
      // const response = await fetch('/api/ai/system/metrics')
      // return response.json()
      
      // Mock for now:
      return generateMockSystemMetrics()
    },
    refetchInterval: 5000, // 5 seconds
  })
}
```

#### **5.2 Mutations для управления:**
```typescript
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

### 6. Responsive дизайн

#### **6.1 Breakpoints:**
- **Mobile (< 768px)**: Стек карточек, скрытие деталей
- **Tablet (768px - 1024px)**: 2x5 сетка → 2x3 + scroll
- **Desktop (> 1024px)**: Полная 2x5 сетка + боковая панель

#### **6.2 Mobile оптимизации:**
```tsx
// Mobile-first responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
  {/* AI Organ cards */}
</div>

// Collapsible details on mobile
<div className="md:hidden">
  <CollapsibleDetails organ={organ} />
</div>
```

### 7. Анимации и интерактивность

#### **7.1 Micro-interactions:**
- Health bar анимация при загрузке
- Pulse анимация для активных органов
- Hover эффекты на карточках
- Loading состояния для action кнопок

#### **7.2 Real-time обновления:**
- Smooth transitions при изменении статуса
- Toast уведомления для событий
- Auto-scroll в логе активности

### 8. Deliverables

#### **8.1 Основные файлы:**
1. ✅ `components/modules/AIControlCenter.tsx`
2. ✅ `app/modules/ai-control/page.tsx`
3. ✅ `hooks/useAIOrgans.ts`
4. ✅ `components/ui/HealthBar.tsx`
5. ✅ `components/ui/StatusIndicator.tsx`

#### **8.2 Обновления существующих файлов:**
1. ✅ `components/layout/Navigation.tsx` - добавить ссылку
2. ✅ `lib/api.ts` - добавить AI endpoints

### 9. Критерии приемки

- [ ] **Визуальное соответствие:** Все 10 AI органов отображаются корректно
- [ ] **Функциональность:** Кнопки управления работают (mock)
- [ ] **Responsive:** Интерфейс адаптируется под все экраны
- [ ] **Real-time:** Данные автоматически обновляются
- [ ] **Performance:** Нет лагов при взаимодействии
- [ ] **TypeScript:** Нет ошибок типизации
- [ ] **Consistency:** Соответствует design system платформы

### 10. Интеграция с другими модулями

#### **10.1 Cross-module связи:**
```typescript
// В AI Control Center добавить:
interface AIOrganIntegration {
  riskAdvisor: {
    linkedRisks: number
    lastRiskAnalysis: string
    criticalRisksDetected: number
  }
  biaAnalyst: {
    completedBIAs: number
    criticalFunctionsAnalyzed: number
    averageRTOCalculated: number
  }
}
```

#### **10.2 Навигационные связи:**
- Клик по "Risk Advisor" → переход на `/modules/risk-management`
- Клик по "BIA Analyst" → переход на `/modules/bia`
- Preview данных из связанных модулей в hover states

---

## 🚀 НАЧИНАТЬ РАЗРАБОТКУ

**Порядок создания:**
1. Основной компонент `AIControlCenter.tsx`
2. UI компоненты (`HealthBar`, `StatusIndicator`)
3. Hooks для данных (`useAIOrgans`, `useAIMetrics`)
4. Страница модуля `page.tsx`
5. Обновление навигации
6. Тестирование и отладка

**После завершения AI Control Center переходить к интеграции с Risk Management и BIA модулями.**
