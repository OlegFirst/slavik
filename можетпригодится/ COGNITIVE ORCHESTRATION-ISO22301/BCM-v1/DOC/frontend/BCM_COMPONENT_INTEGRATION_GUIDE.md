# 🧩 BCM PLATFORM - КОМПОНЕНТНАЯ ИНТЕГРАЦИЯ И ПОДКЛЮЧЕНИЯ

## 🔌 КАК ПОДКЛЮЧАТЬ НОВЫЕ МОДУЛИ

### 🎯 Пошаговая инструкция добавления BCM модуля

#### 1️⃣ Создание Odoo модуля
```bash
# 📁 Создание структуры модуля
mkdir /core/odoo-18.0/addons/bcm_new_module
cd bcm_new_module

# 📂 Базовая структура
mkdir {models,views,controllers,security,data,demo,static}
mkdir static/{src,description}
mkdir models/__pycache__
```

```python
# 📄 __manifest__.py
{
    'name': 'BCM New Module - Description',
    'version': '18.0.1.0.0',
    'category': 'Business Continuity',
    'sequence': 20,  # После bcm_core (1-10), перед сложными (50+)
    'summary': 'Brief module description',
    'depends': [
        'bcm_core',              # ВСЕГДА включать
        'bcm_intelligent_base',  # Если нужна AI интеграция
        'bcm_base',             # Если нужна интеграция с сервисами
        # + другие зависимости
    ],
    'data': [
        'security/bcm_security.xml',
        'security/ir.model.access.csv',
        'data/bcm_data.xml',
        'views/menu.xml',
        'views/bcm_model_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
```

```python
# 📄 models/__init__.py
from . import bcm_new_model

# 📄 models/bcm_new_model.py
from odoo import models, fields, api, _

class BCMNewModel(models.Model):
    _name = 'bcm.new.model'
    _description = 'New BCM Model'
    _inherit = ['bcm.base']  # ОБЯЗАТЕЛЬНО наследуем от bcm.base
    _order = 'sequence, name'

    # Стандартные поля (автоматически из bcm.base)
    # - active, company_id, iso_clause, compliance_status
    # - created_by, last_review_date, next_review_date
    # - risk_level, tag_ids

    # Специфичные поля модуля
    name = fields.Char('Name', required=True)
    description = fields.Text('Description')

    # AI интеграция (если нужна)
    _inherit_ai = ['bcm.intelligent.base']  # Добавляет AI поля

    def action_ai_analyze(self):
        """AI анализ через bcm_base сервисы"""
        ai_service = self.env['bcm.ai.service']
        result = ai_service.analyze_process_risk({
            'name': self.name,
            'description': self.description,
            'model': self._name
        })
        self.ai_recommendations = result.get('recommendations')
        return result
```

#### 2️⃣ Создание Frontend компонента

```vue
<!-- 📄 src/views/modules/BCMNewModule.vue -->
<template>
  <BCMModuleLayout
    :config="moduleConfig"
    @create="handleCreate"
    @refresh="handleRefresh"
  >
    <!-- 📊 Module-specific metrics -->
    <template #metrics>
      <BCMMetricCard
        v-for="metric in moduleMetrics"
        :key="metric.key"
        v-bind="metric"
      />
    </template>

    <!-- 📋 Main content -->
    <template #content>
      <BCMDataTable
        :data="records"
        :columns="tableColumns"
        :loading="isLoading"
        @row-click="handleRowClick"
        @edit="handleEdit"
        @delete="handleDelete"
      />
    </template>

    <!-- 🤖 AI sidebar (if enabled) -->
    <template #ai-panel v-if="hasAI">
      <AIRecommendations
        :module="moduleConfig.name"
        :context="selectedRecord"
      />
    </template>
  </BCMModuleLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useBCMModule } from '@/composables/useBCMModule'
import BCMModuleLayout from '@/components/layouts/BCMModuleLayout.vue'

// 📋 Module configuration
const moduleConfig = {
  name: 'bcm_new_module',
  title: 'New Module',
  description: 'Module description',
  entityName: 'Record',
  hasAI: true,
  permissions: {
    view: 'bcm.new_module.view',
    create: 'bcm.new_module.create',
    edit: 'bcm.new_module.edit',
    delete: 'bcm.new_module.delete'
  }
}

// 📊 Use composable for data management
const {
  records,
  isLoading,
  selectedRecord,
  loadRecords,
  createRecord,
  updateRecord,
  deleteRecord
} = useBCMModule(moduleConfig.name)

// 📊 Table configuration
const tableColumns = [
  { key: 'name', label: 'Name', sortable: true },
  { key: 'status', label: 'Status', sortable: true },
  { key: 'last_review_date', label: 'Last Review', sortable: true },
  { key: 'compliance_status', label: 'Compliance', sortable: true }
]

// 📊 Module metrics
const moduleMetrics = computed(() => [
  {
    title: 'Total Records',
    value: records.value.length,
    trend: '+12%',
    color: 'blue'
  },
  {
    title: 'Compliant',
    value: records.value.filter(r => r.compliance_status === 'compliant').length,
    trend: '+5%',
    color: 'green'
  }
  // ... more metrics
])

// Methods
function handleCreate() {
  // Navigate to create form
}

function handleEdit(record) {
  // Navigate to edit form
}

// Lifecycle
onMounted(() => {
  loadRecords()
})
</script>
```

#### 3️⃣ Регистрация в роутере

```typescript
// 📄 src/router/index.ts - добавить новый route
{
  path: '/modules/bcm-new-module',
  name: 'BCMNewModule',
  component: () => import('@/views/modules/BCMNewModule.vue'),
  meta: {
    title: 'New Module',
    requiresAuth: true,
    permissions: ['bcm.new_module.view']
  }
}
```

#### 4️⃣ Добавление в меню

```vue
<!-- 📄 components/layout/AppSidebar.vue -->
<SidebarItem
  icon="fas fa-new-icon"
  label="New Module"
  to="/modules/bcm-new-module"
  :badge="newModuleCount"
  :active="$route.path.startsWith('/modules/bcm-new-module')"
/>
```

---

## 🎨 DESIGN SYSTEM COMPONENTS

### 🧩 Базовые компоненты (создать в src/components/ui/)

```typescript
// 📄 BCMButton.vue - Базовая кнопка
interface BCMButtonProps {
  variant: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size: 'sm' | 'md' | 'lg'
  loading?: boolean
  disabled?: boolean
  icon?: string
  iconPosition?: 'left' | 'right'
}

// 📄 BCMCard.vue - Контейнер контента
interface BCMCardProps {
  title?: string
  subtitle?: string
  headerActions?: boolean
  padding?: 'sm' | 'md' | 'lg'
  shadow?: 'sm' | 'md' | 'lg'
  border?: boolean
}

// 📄 BCMTable.vue - Таблица данных
interface BCMTableProps {
  data: any[]
  columns: TableColumn[]
  loading?: boolean
  sortable?: boolean
  selectable?: boolean
  pagination?: boolean
  pageSize?: number
  emptyStateConfig?: EmptyStateConfig
}

// 📄 BCMForm.vue - Форма
interface BCMFormProps {
  model: any
  fields: FormField[]
  validation?: ValidationRules
  loading?: boolean
  readonly?: boolean
  layout?: 'vertical' | 'horizontal' | 'grid'
}

// 📄 BCMModal.vue - Модальное окно
interface BCMModalProps {
  title: string
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  persistent?: boolean
  actions?: ModalAction[]
  loading?: boolean
}
```

### 🎯 BCM специфичные компоненты

```typescript
// 📄 BCMStatusBadge.vue - Индикатор статуса
interface StatusBadgeProps {
  status: 'draft' | 'active' | 'approved' | 'outdated' | 'critical'
  showIcon?: boolean
  size?: 'sm' | 'md' | 'lg'
}

// 📄 BCMComplianceScore.vue - Индикатор соответствия
interface ComplianceScoreProps {
  score: number  // 0-100
  standard: 'iso_22301' | 'iso_27001' | 'nist'
  showDetails?: boolean
  size?: 'sm' | 'md' | 'lg'
}

// 📄 BCMRiskMatrix.vue - Матрица рисков
interface RiskMatrixProps {
  risks: Risk[]
  interactive?: boolean
  showTooltips?: boolean
  colorScheme?: 'default' | 'accessibility'
}

// 📄 BCMTimelineView.vue - Временная линия
interface TimelineProps {
  events: TimelineEvent[]
  groupBy?: 'date' | 'type' | 'severity'
  showFilters?: boolean
  realTime?: boolean
}

// 📄 BCMAIInsights.vue - AI рекомендации
interface AIInsightsProps {
  module: string
  context?: any
  showConfidence?: boolean
  interactive?: boolean
}
```

---

## 🔗 ИНТЕГРАЦИОННЫЕ ПАТТЕРНЫ

### 🤖 AI Integration Pattern

```typescript
// 📄 composables/useAIIntegration.ts
export function useAIIntegration(moduleName: string) {
  const isAIEnabled = ref(false)
  const aiRecommendations = ref([])
  const aiScore = ref(0)
  const isAnalyzing = ref(false)

  // Проверка доступности AI для модуля
  async function checkAIAvailability() {
    try {
      const response = await bcmAPI.checkAIAvailability(moduleName)
      isAIEnabled.value = response.enabled
    } catch (error) {
      console.warn('AI not available for', moduleName)
      isAIEnabled.value = false
    }
  }

  // Запуск AI анализа
  async function runAIAnalysis(data: any) {
    if (!isAIEnabled.value) return

    isAnalyzing.value = true
    try {
      const response = await bcmAPI.runAIAnalysis(moduleName, data)
      aiRecommendations.value = response.recommendations
      aiScore.value = response.score
      return response
    } catch (error) {
      console.error('AI analysis failed:', error)
      throw error
    } finally {
      isAnalyzing.value = false
    }
  }

  // Применение AI рекомендации
  async function applyRecommendation(recommendation: AIRecommendation) {
    try {
      return await bcmAPI.applyAIRecommendation(moduleName, recommendation)
    } catch (error) {
      console.error('Failed to apply recommendation:', error)
      throw error
    }
  }

  return {
    isAIEnabled,
    aiRecommendations,
    aiScore,
    isAnalyzing,
    checkAIAvailability,
    runAIAnalysis,
    applyRecommendation
  }
}
```

### 📊 Data Management Pattern

```typescript
// 📄 composables/useBCMModule.ts
export function useBCMModule(moduleName: string) {
  const records = ref([])
  const selectedRecord = ref(null)
  const isLoading = ref(false)
  const searchQuery = ref('')
  const statusFilter = ref('')
  const pagination = ref({
    page: 1,
    pageSize: 20,
    total: 0
  })

  // CRUD Operations
  async function loadRecords() {
    isLoading.value = true
    try {
      const response = await bcmAPI.getRecords(moduleName, {
        search: searchQuery.value,
        status: statusFilter.value,
        page: pagination.value.page,
        limit: pagination.value.pageSize
      })
      records.value = response.data
      pagination.value.total = response.total
    } catch (error) {
      console.error('Failed to load records:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function createRecord(data: any) {
    try {
      const response = await bcmAPI.createRecord(moduleName, data)
      records.value.unshift(response.data)
      return response
    } catch (error) {
      console.error('Failed to create record:', error)
      throw error
    }
  }

  async function updateRecord(id: string, data: any) {
    try {
      const response = await bcmAPI.updateRecord(moduleName, id, data)
      const index = records.value.findIndex(r => r.id === id)
      if (index >= 0) {
        records.value[index] = response.data
      }
      return response
    } catch (error) {
      console.error('Failed to update record:', error)
      throw error
    }
  }

  async function deleteRecord(id: string) {
    try {
      await bcmAPI.deleteRecord(moduleName, id)
      records.value = records.value.filter(r => r.id !== id)
    } catch (error) {
      console.error('Failed to delete record:', error)
      throw error
    }
  }

  // Watchers для автоматической перезагрузки
  watch([searchQuery, statusFilter], () => {
    pagination.value.page = 1
    loadRecords()
  }, { debounce: 300 })

  return {
    records,
    selectedRecord,
    isLoading,
    searchQuery,
    statusFilter,
    pagination,
    loadRecords,
    createRecord,
    updateRecord,
    deleteRecord
  }
}
```

### 🔐 Permission Integration Pattern

```typescript
// 📄 composables/usePermissions.ts
export function usePermissions(moduleName: string) {
  const authStore = useAuthStore()

  const permissions = computed(() => ({
    canView: authStore.hasPermission(moduleName, 'view'),
    canCreate: authStore.hasPermission(moduleName, 'create'),
    canEdit: authStore.hasPermission(moduleName, 'edit'),
    canDelete: authStore.hasPermission(moduleName, 'delete'),
    canAdmin: authStore.hasPermission(moduleName, 'admin')
  }))

  // Permission guards для UI
  const canAccessRecord = (record: any) => {
    // Проверка ownership для обычных пользователей
    if (!permissions.value.canAdmin) {
      return record.created_by === authStore.user?.id
    }
    return true
  }

  const canModifyRecord = (record: any) => {
    return permissions.value.canEdit && canAccessRecord(record)
  }

  return {
    permissions,
    canAccessRecord,
    canModifyRecord
  }
}
```

---

## 📱 RESPONSIVE DESIGN PATTERNS

### 📐 Grid System для всех экранов

```css
/* 📱 BCM Responsive Grid */
.bcm-grid {
  display: grid;
  gap: 1rem;

  /* 📱 Mobile: 1 column */
  grid-template-columns: 1fr;

  /* 💻 Tablet: 2 columns */
  @media (min-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }

  /* 🖥️ Desktop: 3 columns */
  @media (min-width: 1024px) {
    grid-template-columns: repeat(3, 1fr);
  }

  /* 🖥️ Large Desktop: 4 columns */
  @media (min-width: 1280px) {
    grid-template-columns: repeat(4, 1fr);

    /* Специальные варианты для разных модулей */
    &.dashboard-grid {
      grid-template-columns: 2fr 1fr;  /* Dashboard: широкий + узкий */
    }

    &.detail-grid {
      grid-template-columns: 1fr 300px;  /* Detail: контент + sidebar */
    }

    &.form-grid {
      grid-template-columns: repeat(2, 1fr);  /* Form: 2 равные колонки */
    }
  }
}

/* 📊 Responsive Card Layouts */
.metric-cards {
  display: grid;
  gap: 1rem;

  /* 📱 Mobile: Stack vertically */
  grid-template-columns: 1fr;

  /* 💻 Tablet: 2x2 grid */
  @media (min-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }

  /* 🖥️ Desktop: 4 in a row */
  @media (min-width: 1024px) {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

### 📱 Touch-Friendly Interactions

```css
/* 👆 Touch-optimized Design */
.touch-target {
  min-height: 44px;  /* Apple HIG recommendation */
  min-width: 44px;
  padding: 0.5rem 1rem;
}

.mobile-optimized {
  /* 📱 Larger tap targets on mobile */
  @media (max-width: 767px) {
    .btn {
      min-height: 48px;
      font-size: 1rem;
    }

    .table-row {
      min-height: 56px;
      padding: 1rem 0.5rem;
    }

    .form-field {
      min-height: 52px;
      font-size: 1rem;
    }

    /* Swipe gestures indicators */
    .swipeable-item {
      position: relative;

      &::after {
        content: '👆 Swipe for actions';
        position: absolute;
        right: 1rem;
        top: 50%;
        transform: translateY(-50%);
        font-size: 0.75rem;
        color: var(--bcm-gray-400);
        opacity: 0.7;
      }
    }
  }
}
```

---

## 🔄 СОСТОЯНИЯ И ПЕРЕХОДЫ UI

### 📊 Loading States для разных контекстов

```vue
<!-- 📄 components/ui/BCMLoadingStates.vue -->
<template>
  <div class="loading-container" :class="`loading-${type}`">
    <!-- 📋 Table Loading -->
    <div v-if="type === 'table'" class="table-skeleton">
      <div
        v-for="row in skeletonRows"
        :key="row"
        class="skeleton-row"
      >
        <div class="skeleton-cell" v-for="col in skeletonCols" :key="col"></div>
      </div>
    </div>

    <!-- 📊 Dashboard Loading -->
    <div v-else-if="type === 'dashboard'" class="dashboard-skeleton">
      <div class="skeleton-metrics">
        <div v-for="i in 4" :key="i" class="skeleton-metric"></div>
      </div>
      <div class="skeleton-charts">
        <div class="skeleton-chart-large"></div>
        <div class="skeleton-chart-small"></div>
      </div>
    </div>

    <!-- 📝 Form Loading -->
    <div v-else-if="type === 'form'" class="form-skeleton">
      <div v-for="field in formFields" :key="field" class="skeleton-field">
        <div class="skeleton-label"></div>
        <div class="skeleton-input"></div>
      </div>
    </div>

    <!-- 📄 Generic Loading -->
    <div v-else class="generic-loading">
      <div class="spinner"></div>
      <p class="loading-text">{{ loadingText }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  type: 'table' | 'dashboard' | 'form' | 'generic'
  skeletonRows?: number
  skeletonCols?: number
  formFields?: number
  loadingText?: string
}

const props = withDefaults(defineProps<Props>(), {
  skeletonRows: 5,
  skeletonCols: 4,
  formFields: 6,
  loadingText: 'Loading...'
})
</script>

<style scoped>
.skeleton-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.skeleton-cell {
  height: 1rem;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
  flex: 1;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
```

---

## 🎯 ФОРМАТЫ ДАННЫХ И API КОНТРАКТЫ

### 📋 Стандартные API Response форматы

```typescript
// 📄 types/api.ts
interface BCMAPIResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  errors?: string[]
  meta?: {
    total?: number
    page?: number
    pageSize?: number
    hasMore?: boolean
  }
}

interface BCMRecord {
  id: string
  name: string
  description?: string
  status: RecordStatus
  company_id: string
  created_by: string
  create_date: string
  write_date: string

  // BCM specific fields
  iso_clause?: string
  compliance_status: 'compliant' | 'partial' | 'non_compliant' | 'not_applicable'
  risk_level: 'low' | 'medium' | 'high' | 'critical'
  last_review_date?: string
  next_review_date?: string

  // AI fields (if bcm_intelligent_base inherited)
  ai_enabled?: boolean
  ai_score?: number
  ai_recommendations?: string
  ai_last_analysis?: string
}

interface BCMPlan extends BCMRecord {
  plan_type: 'recovery' | 'continuity' | 'emergency' | 'communication' | 'it_disaster'
  recovery_procedures?: string
  activation_criteria?: string
  contact_list?: string
  rto_hours?: number
  rpo_hours?: number
  estimated_cost?: number
  business_process_ids?: string[]
  incident_ids?: string[]
}

interface BCMIncident extends BCMRecord {
  severity: 'low' | 'medium' | 'high' | 'critical'
  category: 'operational' | 'technical' | 'security' | 'natural' | 'human' | 'external'
  response_checklist?: string
  ai_generated_checklist?: boolean
  resolution_notes?: string
  plan_id?: string
  assigned_user_id?: string
  reported_date: string
  resolved_date?: string
}
```

### 🔗 API Endpoint Patterns

```typescript
// 📄 services/bcmAPI.ts
class BCMModuleAPI {
  private basePath: string

  constructor(moduleName: string) {
    this.basePath = `/api/bcm/${moduleName}`
  }

  // Standard CRUD operations
  async getRecords(params?: QueryParams): Promise<BCMAPIResponse<BCMRecord[]>> {
    return this.apiClient.get(this.basePath, { params })
  }

  async getRecord(id: string): Promise<BCMAPIResponse<BCMRecord>> {
    return this.apiClient.get(`${this.basePath}/${id}`)
  }

  async createRecord(data: Partial<BCMRecord>): Promise<BCMAPIResponse<BCMRecord>> {
    return this.apiClient.post(this.basePath, data)
  }

  async updateRecord(id: string, data: Partial<BCMRecord>): Promise<BCMAPIResponse<BCMRecord>> {
    return this.apiClient.put(`${this.basePath}/${id}`, data)
  }

  async deleteRecord(id: string): Promise<BCMAPIResponse<void>> {
    return this.apiClient.delete(`${this.basePath}/${id}`)
  }

  // AI Integration
  async runAIAnalysis(id: string, analysisType: string): Promise<BCMAPIResponse<AIAnalysisResult>> {
    return this.apiClient.post(`${this.basePath}/${id}/ai-analyze`, { analysisType })
  }

  async getAIRecommendations(id: string): Promise<BCMAPIResponse<AIRecommendation[]>> {
    return this.apiClient.get(`${this.basePath}/${id}/ai-recommendations`)
  }

  // Module-specific methods can be added as needed
  async getModuleMetrics(): Promise<BCMAPIResponse<ModuleMetrics>> {
    return this.apiClient.get(`${this.basePath}/metrics`)
  }

  async exportData(format: 'csv' | 'xlsx' | 'pdf'): Promise<Blob> {
    return this.apiClient.get(`${this.basePath}/export`, {
      params: { format },
      responseType: 'blob'
    })
  }
}

// Factory для создания API клиентов модулей
export function createBCMModuleAPI(moduleName: string) {
  return new BCMModuleAPI(moduleName)
}
```

---

## ⚙️ КОНФИГУРАЦИЯ И НАСТРОЙКИ

### 🎛️ Module Configuration Schema

```typescript
// 📄 types/moduleConfig.ts
interface ModuleConfig {
  // Basic info
  name: string                    // Техническое имя модуля
  title: string                   // Отображаемое название
  description: string             // Описание
  icon: string                    // FontAwesome иконка
  color: string                   // Цвет темы модуля
  sequence: number                // Порядок в меню

  // Capabilities
  features: {
    hasAI: boolean                // Поддержка AI анализа
    hasReports: boolean           // Есть отчеты
    hasExport: boolean            // Экспорт данных
    hasImport: boolean            // Импорт данных
    hasNotifications: boolean     // Уведомления
    hasWorkflow: boolean          // Workflow/Approvals
    hasVersioning: boolean        // Версионирование
    hasAudit: boolean            // Аудит логи
  }

  // UI Configuration
  ui: {
    defaultView: 'list' | 'dashboard' | 'kanban'
    allowedViews: string[]
    showQuickActions: boolean
    showFilters: boolean
    showSearch: boolean
    showBulkActions: boolean
  }

  // Permissions
  permissions: {
    view: string                  // bcm.module.view
    create: string                // bcm.module.create
    edit: string                  // bcm.module.edit
    delete: string                // bcm.module.delete
    admin: string                 // bcm.module.admin
  }

  // API Configuration
  api: {
    endpoints: APIEndpoint[]
    rateLimit?: number
    cacheTTL?: number
  }

  // Integration points
  integrations?: {
    odoo?: OdooIntegration
    ai?: AIIntegration
    external?: ExternalIntegration[]
  }
}

// 📄 Пример конфигурации модуля
export const bcmCoreConfig: ModuleConfig = {
  name: 'bcm_core',
  title: 'BCM Core',
  description: 'Business Continuity Foundation Layer',
  icon: 'fas fa-brain',
  color: '#2563eb',
  sequence: 1,

  features: {
    hasAI: true,
    hasReports: true,
    hasExport: true,
    hasImport: false,
    hasNotifications: true,
    hasWorkflow: false,
    hasVersioning: false,
    hasAudit: true
  },

  ui: {
    defaultView: 'dashboard',
    allowedViews: ['list', 'dashboard', 'form'],
    showQuickActions: true,
    showFilters: true,
    showSearch: true,
    showBulkActions: false
  },

  permissions: {
    view: 'bcm.core.view',
    create: 'bcm.core.create',
    edit: 'bcm.core.edit',
    delete: 'bcm.core.delete',
    admin: 'bcm.core.admin'
  },

  api: {
    endpoints: [
      { path: '/plans', methods: ['GET', 'POST'] },
      { path: '/incidents', methods: ['GET', 'POST'] },
      { path: '/ai/analyze', methods: ['POST'] }
    ],
    rateLimit: 100,
    cacheTTL: 300
  },

  integrations: {
    ai: {
      services: ['ai_orchestrator', 'bia_engine'],
      autoAnalysis: true,
      confidence_threshold: 0.8
    }
  }
}
```

### 🎨 Theme Configuration

```typescript
// 📄 styles/themes.ts
export const BCMThemes = {
  default: {
    name: 'BCM Default',
    colors: {
      primary: '#2563eb',
      secondary: '#7c3aed',
      accent: '#f59e0b',
      success: '#10b981',
      warning: '#f59e0b',
      danger: '#ef4444',
      info: '#06b6d4',
      gray: {
        50: '#f9fafb',
        100: '#f3f4f6',
        200: '#e5e7eb',
        300: '#d1d5db',
        400: '#9ca3af',
        500: '#6b7280',
        600: '#4b5563',
        700: '#374151',
        800: '#1f2937',
        900: '#111827'
      }
    },
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem',
      '2xl': '3rem'
    },
    typography: {
      fontFamily: 'Inter, sans-serif',
      fontSize: {
        xs: '0.75rem',
        sm: '0.875rem',
        base: '1rem',
        lg: '1.125rem',
        xl: '1.25rem',
        '2xl': '1.5rem',
        '3xl': '2rem'
      }
    }
  },

  dark: {
    // Dark theme configuration
    name: 'BCM Dark',
    colors: {
      // Переопределение цветов для темной темы
    }
  }
}
```

**🎯 Это дает команде разработчиков:**

✅ **Точные инструкции** как добавлять новые модули
✅ **Готовые шаблоны** для компонентов и страниц
✅ **Паттерны интеграции** для AI, данных, разрешений
✅ **Responsive design** правила для всех экранов
✅ **Стандартные форматы** для API и данных
✅ **Конфигурационные схемы** для модулей

**Команда теперь может создавать новые модули по четкому template! 🚀**

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Create detailed UI/UX navigation maps", "status": "completed", "activeForm": "Creating detailed UI/UX navigation maps"}, {"content": "Design menu structure and layouts", "status": "completed", "activeForm": "Designing menu structure and layouts"}, {"content": "Create component integration guides", "status": "completed", "activeForm": "Creating component integration guides"}, {"content": "Document user interface patterns", "status": "completed", "activeForm": "Documenting user interface patterns"}]