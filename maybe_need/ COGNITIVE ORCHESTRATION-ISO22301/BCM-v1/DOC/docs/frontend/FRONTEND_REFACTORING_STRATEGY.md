# 🚀 Frontend Refactoring Strategy
*Стратегия рефакторинга frontend с переходом на архитектуру из BCM_PORTAL_DETAILED_SECTIONS_AND_CONTROLS*

---

## 📊 **Текущее состояние проекта**

### ❌ **Проблемы:**
1. **29 файлов с заглушками** - много TODO/FIXME
2. **Дублирующиеся компоненты** - Admin.vue и AdminOld.vue, множество BCM*.vue
3. **Технический дашборд** - показывает статусы сервисов вместо бизнес-метрик
4. **Избыточная структура** - 65 компонентов в modules для 8 основных страниц
5. **Нет ролевой персонализации** - один интерфейс для всех

### ✅ **Что можно сохранить:**
1. **UI компоненты** - Card, Button, LoadingSpinner, ErrorBoundary
2. **Layout компоненты** - AppHeader, AppSidebar (с доработкой)
3. **Auth flow** - Login, ForgotPassword, stores/auth
4. **AssistantPanel** - AI assistant интеграция
5. **Scenario components** - готовые компоненты для сценариев

---

## 🎯 **План рефакторинга**

### **ФАЗА 1: Очистка и подготовка**
```bash
# 1. Создать резервную копию
cp -r /Users/MD/ISO-22301/frontend/web_portal-2 /Users/MD/ISO-22301/frontend/web_portal-2_backup

# 2. Создать новую структуру
mkdir -p src/views/pages
mkdir -p src/components/shared
mkdir -p src/components/business
mkdir -p src/components/dashboards
```

### **ФАЗА 2: Новая структура страниц**

```
src/
├── views/
│   └── pages/                    # 8 основных страниц
│       ├── MainDashboard.vue     # Персонализированный главный дашборд
│       ├── RiskAnalysisHub.vue   # Risk + BIA анализ
│       ├── CrisisCommandCenter.vue # Кризисное управление
│       ├── PlansWorkspace.vue    # Планы и процедуры
│       ├── TrainingHub.vue       # Обучение и учения
│       ├── AnalyticsSuite.vue    # Аналитика и отчеты
│       ├── KnowledgePortal.vue   # База знаний и коллаборация
│       └── SystemAdmin.vue       # Администрирование
│
├── components/
│   ├── dashboards/               # Ролевые дашборды
│   │   ├── BCMManagerDashboard.vue
│   │   ├── RiskAnalystDashboard.vue
│   │   ├── CrisisManagerDashboard.vue
│   │   ├── ProcessOwnerDashboard.vue
│   │   └── ITManagerDashboard.vue
│   │
│   ├── business/                 # Бизнес-компоненты
│   │   ├── risk/
│   │   │   ├── RiskHeatMap.vue
│   │   │   ├── RiskDetailsPanel.vue
│   │   │   ├── ImpactCalculator.vue
│   │   │   └── AIRiskAdvisor.vue
│   │   ├── crisis/
│   │   │   ├── SituationMap.vue
│   │   │   ├── ResponseTeamsPanel.vue
│   │   │   ├── DecisionLog.vue
│   │   │   └── CrisisStatusBar.vue
│   │   ├── plans/
│   │   │   ├── PlanLibrary.vue
│   │   │   ├── PlanEditor.vue
│   │   │   ├── ApprovalWorkflow.vue
│   │   │   └── PlanTesting.vue
│   │   ├── training/
│   │   │   ├── ExerciseBuilder.vue
│   │   │   ├── LearningCenter.vue
│   │   │   ├── CompetencyTracker.vue
│   │   │   └── AILearningCoach.vue
│   │   └── analytics/
│   │       ├── ReportBuilder.vue
│   │       ├── InteractiveDashboards.vue
│   │       ├── PredictiveAnalytics.vue
│   │       └── AIInsightsPanel.vue
│   │
│   └── shared/                   # Переиспользуемые компоненты
│       ├── ui/                   # Сохраняем существующие
│       ├── layout/               # Доработка существующих
│       └── common/              # Новые общие компоненты
│           ├── KPICard.vue
│           ├── StatusCard.vue
│           ├── ActivityFeed.vue
│           └── PriorityAlerts.vue
```

### **ФАЗА 3: Реализация новых страниц**

#### **1. MainDashboard.vue - Персонализированный hub**
```vue
<template>
  <div class="main-dashboard">
    <!-- Header с ролевым селектором -->
    <DashboardHeader
      :user="currentUser"
      :role="selectedRole"
      @roleChange="handleRoleChange"
    />

    <!-- KPI Overview - адаптивные метрики по роли -->
    <KPIOverview :metrics="roleSpecificKPIs" />

    <!-- Status Cards Grid -->
    <div class="status-grid">
      <StatusCard
        v-for="card in roleSpecificCards"
        :key="card.id"
        :data="card"
        @action="handleCardAction"
      />
    </div>

    <!-- Activity Feed с фильтрацией -->
    <ActivityFeed
      :filters="activityFilters"
      :items="recentActivities"
    />

    <!-- Priority Alerts Panel -->
    <PriorityAlerts
      :alerts="priorityAlerts"
      @action="handleAlertAction"
    />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useDashboardStore } from '@/stores/dashboard'
import { useRoleAdapter } from '@/composables/useRoleAdapter'

const authStore = useAuthStore()
const dashboardStore = useDashboardStore()
const { roleSpecificKPIs, roleSpecificCards } = useRoleAdapter()

// Динамическая адаптация под роль пользователя
const currentUser = computed(() => authStore.user)
const selectedRole = computed(() => authStore.selectedRole)

const handleRoleChange = (newRole) => {
  authStore.setSelectedRole(newRole)
  dashboardStore.loadRoleDashboard(newRole)
}
</script>
```

#### **2. RiskAnalysisHub.vue - Объединенный анализ**
```vue
<template>
  <div class="risk-analysis-hub">
    <!-- Analysis Control Panel -->
    <AnalysisControlPanel
      v-model:mode="analysisMode"
      :aiEnabled="aiAssistantActive"
      @aiToggle="toggleAIAssistant"
    />

    <div class="analysis-layout">
      <!-- Left: Visual Analysis -->
      <div class="visual-column">
        <RiskHeatMap
          v-if="analysisMode === 'risk'"
          :data="riskData"
          @cellClick="handleRiskSelection"
        />
        <BIAProcessMap
          v-else-if="analysisMode === 'bia'"
          :processes="biaProcesses"
          @processClick="handleProcessSelection"
        />
        <DependencyGraph
          v-else
          :nodes="dependencies"
        />
      </div>

      <!-- Right: Details & AI -->
      <div class="details-column">
        <RiskDetailsPanel
          v-if="selectedRisk"
          :risk="selectedRisk"
          @action="handleRiskAction"
        />
        <ImpactCalculator
          v-if="analysisMode === 'bia'"
          :process="selectedProcess"
          @calculate="runBIAEngine"
        />
        <AIRecommendations
          :context="analysisContext"
          :recommendations="aiRecommendations"
        />
      </div>
    </div>

    <!-- Integration Panel -->
    <IntegrationPanel>
      <ThreatIntelFeed />
      <IndustryBenchmarks />
      <RegulatoryUpdates />
    </IntegrationPanel>
  </div>
</template>
```

### **ФАЗА 4: Маппинг старых компонентов**

| Старый компонент | Новое расположение | Действие |
|-----------------|-------------------|----------|
| BCMPortal.vue | MainDashboard.vue | Рефакторинг |
| BCMGovernance.vue | SystemAdmin.vue (часть) | Merge |
| BCMRiskManagement.vue | RiskAnalysisHub.vue | Интеграция |
| BCMBIA.vue | RiskAnalysisHub.vue | Интеграция |
| BCMIncident.vue | CrisisCommandCenter.vue | Merge |
| BCMPlans.vue | PlansWorkspace.vue | Рефакторинг |
| BCMExercise.vue | TrainingHub.vue | Merge |
| BCMTraining.vue | TrainingHub.vue | Merge |
| BCMReporting.vue | AnalyticsSuite.vue | Рефакторинг |
| AIAssistant.vue | Shared component | Сохранить |

### **ФАЗА 5: Новый роутинг**

```typescript
// router/index.ts
const routes = [
  {
    path: '/',
    component: AuthenticatedLayout,
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/pages/MainDashboard.vue'),
        meta: {
          requiresAuth: true,
          adaptsToRole: true
        }
      },
      {
        path: 'risk-analysis',
        name: 'RiskAnalysis',
        component: () => import('@/views/pages/RiskAnalysisHub.vue'),
        meta: {
          requiresAuth: true,
          permissions: ['risk.view', 'bia.view']
        }
      },
      {
        path: 'crisis-center',
        name: 'CrisisCenter',
        component: () => import('@/views/pages/CrisisCommandCenter.vue'),
        meta: {
          requiresAuth: true,
          permissions: ['crisis.manage']
        }
      },
      {
        path: 'plans',
        name: 'PlansWorkspace',
        component: () => import('@/views/pages/PlansWorkspace.vue'),
        meta: {
          requiresAuth: true,
          permissions: ['plans.view']
        }
      },
      {
        path: 'training',
        name: 'TrainingHub',
        component: () => import('@/views/pages/TrainingHub.vue'),
        meta: {
          requiresAuth: true,
          permissions: ['training.view']
        }
      },
      {
        path: 'analytics',
        name: 'Analytics',
        component: () => import('@/views/pages/AnalyticsSuite.vue'),
        meta: {
          requiresAuth: true,
          permissions: ['analytics.view']
        }
      },
      {
        path: 'knowledge',
        name: 'KnowledgePortal',
        component: () => import('@/views/pages/KnowledgePortal.vue'),
        meta: {
          requiresAuth: true
        }
      },
      {
        path: 'admin',
        name: 'SystemAdmin',
        component: () => import('@/views/pages/SystemAdmin.vue'),
        meta: {
          requiresAuth: true,
          permissions: ['system.admin']
        }
      }
    ]
  }
]
```

### **ФАЗА 6: Stores рефакторинг**

```typescript
// stores/dashboard.ts
export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    currentRole: null,
    roleSpecificData: {},
    kpis: [],
    alerts: [],
    activities: []
  }),

  actions: {
    async loadRoleDashboard(role: string) {
      // Загрузка данных специфичных для роли
      const config = getRoleConfiguration(role)

      // Parallel loading
      const [kpis, alerts, activities] = await Promise.all([
        fetchRoleKPIs(role, config.kpiTypes),
        fetchRoleAlerts(role, config.alertTypes),
        fetchRoleActivities(role, config.activityTypes)
      ])

      this.roleSpecificData = { kpis, alerts, activities }
    }
  }
})
```

---

## 🚀 **Порядок выполнения рефакторинга**

### **Неделя 1: Подготовка и базовая структура**
1. Backup текущего проекта
2. Создание новой структуры папок
3. Миграция shared компонентов
4. Настройка нового роутинга

### **Неделя 2: Основные страницы**
1. MainDashboard с ролевой адаптацией
2. RiskAnalysisHub с AI интеграцией
3. CrisisCommandCenter
4. PlansWorkspace

### **Неделя 3: Дополнительные страницы**
1. TrainingHub
2. AnalyticsSuite
3. KnowledgePortal
4. SystemAdmin

### **Неделя 4: Интеграция и тестирование**
1. API интеграция
2. Ролевое тестирование
3. Performance оптимизация
4. Mobile адаптация

---

## ✅ **Преимущества рефакторинга**

1. **Чистая архитектура** - 8 страниц вместо 65 компонентов
2. **Ролевая персонализация** - адаптивный интерфейс
3. **Лучшая производительность** - code splitting и lazy loading
4. **Maintainable код** - четкая структура и логика
5. **Готовность к масштабированию** - модульная архитектура

---

## 🎯 **Метрики успеха**

- ✅ Сокращение кода на 40-50%
- ✅ Улучшение Time to Interactive на 30%
- ✅ 100% покрытие бизнес-требований
- ✅ Поддержка всех 7 ролей пользователей
- ✅ Mobile-ready интерфейс

**Рефакторинг позволит создать современный, эффективный и масштабируемый frontend!**