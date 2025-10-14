# 📋 **ТЕХНИЧЕСКОЕ ЗАДАНИЕ**
# **UNIFIED BCM PLATFORM - Frontend Implementation**

---

## 📄 **ДОКУМЕНТ ИНФОРМАЦИЯ**

| Параметр | Значение |
|----------|----------|
| **Проект** | Unified Business Continuity Management Platform |
| **Компонент** | Frontend Web Application |
| **Архитектура** | Next.js 14 + TypeScript + Tailwind CSS |
| **Версия ТЗ** | 3.0 |
| **Дата обновления** | 2025-01-17 |
| **Статус** | Обновлено с критическими UX требованиями |

---

## 🎯 **1. ОБЩЕЕ ОПИСАНИЕ ПРОЕКТА**

### **1.1 Назначение системы**
Unified BCM Platform - это веб-приложение для Business Continuity Management профессионалов (аудиторов, консультантов, менеджеров BCM), обеспечивающее полный цикл управления непрерывностью бизнеса клиентов.

### **1.2 Целевая аудитория**
- **Основные пользователи:** BCM аудиторы, консультанты, менеджеры
- **Вторичные пользователи:** Конечные клиенты организаций (ограниченный доступ)
- **Бизнес-модель:** "Uber для BCM профессионалов"

### **1.3 Ключевые особенности**
- **Multi-tenant архитектура** - каждый аудитор работает с множественными клиентами
- **Digital Twin Organization** - цифровые модели клиентских организаций  
- **AI-powered функциональность** - интеллектуальные рекомендации и автоматизация
- **Интеграция с экосистемой** - 60+ backend сервисов и модулей

---

## 🏗️ **2. ТЕХНИЧЕСКАЯ АРХИТЕКТУРА**

### **2.1 Technology Stack**

| Компонент | Технология | Версия |
|-----------|------------|--------|
| **Frontend Framework** | Next.js | 14.x |
| **Language** | TypeScript | 5.x |
| **Styling** | Tailwind CSS | 3.x |
| **UI Components** | shadcn/ui + Radix UI | Latest |
| **State Management** | Zustand / React Query | Latest |
| **Charts & Visualization** | Recharts / D3.js | Latest |
| **3D Visualization** | Three.js | r128 |
| **Form Management** | React Hook Form | Latest |
| **Date Management** | date-fns | Latest |
| **PWA Support** | @serwist/next | Latest |
| **Accessibility** | @radix-ui/react-a11y | Latest |
| **Touch Gestures** | @use-gesture/react | Latest |
| **Offline Storage** | Dexie.js | Latest |
| **Screen Reader** | @testing-library/jest-dom | Latest |

### **2.2 Структура проекта**
```
/frontend/unified-bcm-platform/
├── app/                            # Next.js App Router
│   ├── (dashboard)/               # Dashboard layout группа
│   │   ├── page.tsx              # Central Hub (/)
│   │   ├── digital-twin/         # Digital Organization Twin
│   │   ├── risk-assessment/      # Risk & Impact Assessment
│   │   ├── strategy-planning/    # Strategy & Planning
│   │   ├── incident-management/  # Incident & Crisis Management
│   │   ├── workflow-management/  # Workflow & Process Management
│   │   ├── learning-community/   # Learning & Community
│   │   ├── client-management/    # Client & Project Management
│   │   ├── ai-automation/        # AI & Automation
│   │   ├── analytics/            # Analytics & Intelligence ✅ ЕСТЬ
│   │   └── workspace/            # My Workspace & Settings
│   ├── layout.tsx                # Root layout
│   ├── globals.css               # Global styles
│   └── loading.tsx               # Global loading UI
├── components/                    # React Components
│   ├── sections/                 # Компоненты страниц-разделов
│   │   ├── CentralHub/
│   │   ├── DigitalTwin/
│   │   ├── RiskAssessment/       # ✅ ЧАСТИЧНО ЕСТЬ
│   │   ├── StrategyPlanning/
│   │   ├── IncidentManagement/   # ✅ ЕСТЬ
│   │   ├── WorkflowManagement/
│   │   ├── LearningCommunity/
│   │   ├── ClientManagement/
│   │   ├── AIAutomation/
│   │   ├── Analytics/            # ✅ ЕСТЬ
│   │   └── Workspace/
│   ├── shared/                   # Переиспользуемые компоненты
│   │   ├── Navigation/
│   │   ├── Layout/
│   │   ├── Forms/
│   │   ├── Charts/
│   │   └── Tables/
│   ├── ui/                       # UI Kit компоненты ✅ ЕСТЬ
│   └── providers/                # Context providers
├── lib/                          # Утилиты и конфигурация
│   ├── api/                      # API клиенты
│   │   ├── odoo/                 # Odoo API интеграция
│   │   ├── services/             # Backend services API
│   │   └── integrations/         # External integrations API
│   ├── stores/                   # State management
│   ├── utils/                    # Утилитные функции ✅ ЕСТЬ
│   ├── types/                    # TypeScript типы
│   └── constants/                # Константы
├── services/                     # ✅ УЖЕ ЕСТЬ (включая monte-carlo-simulation.ts)
├── public/                       # Статические файлы
└── docs/                         # Документация
```

### **2.3 Backend Integration - ОБНОВЛЕННАЯ АРХИТЕКТУРА**

#### **2.3.1 Odoo Backend (24 модуля после консолидации)**

**✅ ОБЪЕДИНЕННЫЕ МОДУЛИ (было 28 → стало 24):**

| **Было (28 модулей)** | **Стало (22 модуля)** | **Результат** |
|----------------------|----------------------|---------------|
| `bcm_incident` + `bcm_incident_management` | `bcm_incident_unified` | ✅ Объединено |
| `bcm_base` + `bcm_config` + `bcm_context` | `bcm_foundation` | ✅ Объединено |
| `bcm_portal` + `bcm_admin_website` | `bcm_web_portal` | ✅ Объединено |
| `bcm_templates` + `bcm_scenario_hub` | `bcm_content_library` | ✅ Объединено |

**Новая архитектура модулей:**

```typescript
// ✅ ОБНОВЛЕННЫЙ СПИСОК МОДУЛЕЙ
const odooModules = {
  // ===== CORE INFRASTRUCTURE =====
  core: {
    'bcm_core': 'Ядро BCM системы',
    'bcm_foundation': 'Объединенная инфраструктура (base+config+context)', // ✅ НОВЫЙ
  },
  
  // ===== BUSINESS PROCESSES =====
  business: {
    'bcm_bia': 'Business Impact Analysis',
    'bcm_risk_management': 'Risk Management',
    'bcm_governance': 'Governance & Compliance',
    'bcm_plans': 'Business Continuity Plans',
  },
  
  // ===== INCIDENT & CRISIS MANAGEMENT =====
  incident: {
    'bcm_incident_unified': 'Unified Incident Management (incident+management)', // ✅ НОВЫЙ
    'bcm_exercise': 'Exercises & Simulations',
  },
  
  // ===== DIGITAL TWIN ECOSYSTEM =====
  digitalTwin: {
    'bcm_digital_twin_core': 'Digital Twin Core',
    'bcm_corporate_twin': 'Corporate Digital Twin',
    'bcm_digital_copy_manager': 'Digital Copy Manager',
  },
  
  // ===== AI ECOSYSTEM =====
  ai: {
    'bcm_ai_consultant': 'AI Consultant',
    'bcm_ai_control': 'AI Control Center',
    'bcm_ai_twin_orchestrator': 'AI Twin Orchestrator',
    'bcm_intelligent_base': 'Intelligent Base',
  },
  
  // ===== CLIENT & PORTAL =====
  client: {
    'bcm_clients': 'Client Management',
    'bcm_web_portal': 'Unified Web Portal (portal+admin)', // ✅ НОВЫЙ
  },
  
  // ===== CONTENT & LEARNING =====
  content: {
    'bcm_content_library': 'Content Library (templates+scenarios)', // ✅ НОВЫЙ
    'bcm_training': 'Training & Learning',
    'bcm_community': 'Professional Community',
  },
  
  // ===== ANALYTICS & REPORTING =====
  analytics: {
    'bcm_kpi': 'KPI Management',
    'bcm_reporting': 'Analytics & Reporting',
    'bcm_audit': 'Audit & Compliance',
  }
}
```

#### **2.3.2 Микросервисы (9 сервисов)**
- **auth_service** (8005) - JWT аутентификация
- **eventbus** (8001) - Event-driven архитектура  
- **bpmn_service** (8005) - BPMN Workflow Engine
- **orchestrator_service** (8002) - AI оркестрация
- **notification_service** (8004) - Уведомления
- **document_processor** (8003) - Обработка документов
- **grafana_adapter** (8008) - Grafana интеграция
- **thehive_adapter** (8007) - TheHive интеграция  
- **lms_adapter** (8006) - Multi-LMS интеграция

#### **2.3.3 Специализированные сервисы (15+ сервисов)**
- AI сервисы: `ai-consultant`, `ai_orchestrator`, `digital-twin-engine`
- Data processing: `bia_engine`, `compliance_checker`, `scenario_orchestrator`
- Platform services: `unified_control_center`, `knowledge-base`

---

## 📱 **3. ФУНКЦИОНАЛЬНЫЕ ТРЕБОВАНИЯ**

### **3.1 Архитектура навигации**

#### **3.1.1 Главное меню**
```typescript
const mainNavigation = [
  { name: 'Central Hub', href: '/', icon: Home },
  { name: 'Digital Twin', href: '/digital-twin', icon: Building },
  { name: 'Risk Assessment', href: '/risk-assessment', icon: Shield },
  { name: 'Strategy & Planning', href: '/strategy-planning', icon: FileText },
  { name: 'Incident Management', href: '/incident-management', icon: AlertTriangle },
  { name: 'Workflow Management', href: '/workflow-management', icon: Workflow },
  { name: 'Learning & Community', href: '/learning-community', icon: GraduationCap },
  { name: 'Client Management', href: '/client-management', icon: Users },
  { name: 'AI & Automation', href: '/ai-automation', icon: Bot },
  { name: 'Analytics & Intelligence', href: '/analytics', icon: BarChart },
  { name: 'My Workspace', href: '/workspace', icon: User },
]
```

#### **3.1.2 Layout структура**
- **Sidebar Navigation** - главное меню слева
- **Header** - breadcrumbs, user menu, notifications
- **Main Content Area** - контент страницы
- **Footer** - системная информация

### **3.2 User Experience Requirements**

#### **3.2.1 User Onboarding & Help System**

**Обязательные компоненты:**
```typescript
// КРИТИЧЕСКИЙ ПРИОРИТЕТ
components/onboarding/
├── OnboardingWizard.tsx          // Wizard первоначальной настройки
├── FeatureTour.tsx               // Interactive guided tours  
├── ContextualHelp.tsx            // Context-sensitive help overlay
├── TutorialModal.tsx             // Step-by-step tutorials
└── ProgressTracker.tsx           // User progress tracking

lib/onboarding/
├── onboarding-steps.ts           // Конфигурация onboarding
├── help-content.ts               // База knowledge для помощи
└── tutorial-scenarios.ts         // BCM-specific learning scenarios
```

**Функциональные требования:**
- ✅ Wizard setup для новых пользователей (организация, роль, preferences)
- ✅ Interactive tours для каждого модуля (BIA, Risk, Incident, etc.)
- ✅ Context-sensitive help в каждом интерфейсе
- ✅ Progress tracking освоения функций
- ✅ Role-based onboarding paths (Auditor vs Client vs Admin)

#### **3.2.2 Mobile & Emergency Access**

**Обязательные компоненты:**
```typescript
// КРИТИЧЕСКИЙ ПРИОРИТЕТ - BCM требует мобильного доступа
components/mobile/
├── MobileNavigation.tsx          // Touch-optimized navigation
├── EmergencyAccess.tsx           // Emergency incident reporting
├── TouchOptimizedControls.tsx    // Touch UI для всех форм
├── OfflineIndicator.tsx          // Offline mode индикатор
└── PWAInstallPrompt.tsx          // Progressive Web App

lib/mobile/
├── touch-handlers.ts             // Touch gesture support
├── offline-storage.ts            // Critical data offline storage
├── pwa-config.ts                 // PWA manifest & service worker
└── emergency-protocols.ts        // Emergency access protocols
```

**Функциональные требования:**
- ✅ **PWA Support** - установка как мобильное приложение
- ✅ **Emergency Incident Reporting** - быстрая подача инцидентов
- ✅ **Offline Critical Access** - базовый функционал без интернета
- ✅ **Touch-optimized Forms** - все формы адаптированы для touch
- ✅ **GPS Location Integration** - для emergency response

#### **3.2.3 Accessibility & Compliance**

**Обязательные компоненты:**
```typescript
// ЮРИДИЧЕСКОЕ ТРЕБОВАНИЕ - ADA/WCAG 2.1 AA
components/accessibility/
├── ScreenReaderAnnouncer.tsx     // ARIA live regions
├── KeyboardNavigation.tsx        // Full keyboard navigation
├── HighContrastTheme.tsx         // High contrast themes
├── FontSizeController.tsx        // Text scaling 125%-200%
└── AccessibilitySettings.tsx     // User accessibility preferences

lib/accessibility/
├── aria-helpers.ts               // ARIA attributes utilities
├── keyboard-shortcuts.ts         // Global keyboard shortcuts
├── screen-reader.ts              // Screen reader optimization
└── wcag-compliance.ts            // WCAG 2.1 AA compliance checker
```

**Функциональные требования:**
- ✅ **WCAG 2.1 AA Compliance** - полное соответствие
- ✅ **Screen Reader Support** - NVDA, JAWS, VoiceOver
- ✅ **Keyboard Navigation** - полная работа без мыши
- ✅ **High Contrast Themes** - для слабовидящих
- ✅ **Text Scaling** - 125%, 150%, 200% масштабирование

#### **3.2.4 Cross-Module Integration**

**Обязательные компоненты:**
```typescript
// КРИТИЧЕСКИЙ UX ПРОПУСК - модули работают изолированно
components/integration/
├── CrossModuleWorkflows.tsx      // Связанные workflow между модулями
├── RiskToPlanIntegration.tsx     // Risk Assessment → BCP Plans
├── IncidentToBIACorrelation.tsx  // Incidents → BIA Impact Analysis
├── UnifiedDashboard.tsx          // Интегрированный cross-module dashboard
└── ModuleNavigationBridge.tsx    // Навигация между связанными модулями

lib/integration/
├── cross-module-api.ts           // API для межмодульной интеграции
├── workflow-orchestrator.ts     // Автоматические workflow между модулями
└── data-correlation.ts          // Автокорреляция данных между модулями
```

**Функциональные требования:**
- ✅ **Risk-to-Plan Workflows** - риски автоматически создают планы
- ✅ **Incident-to-BIA Correlation** - инциденты влияют на BIA анализ
- ✅ **Training-to-Competency** - обучение связано с компетенциями
- ✅ **Unified Cross-Module Dashboard** - общий overview всех модулей

#### **3.2.5 External System Integration UI**

**Обязательные компоненты:**
```typescript
// БИЗНЕС ТРЕБОВАНИЕ - интеграция с external systems
components/integrations/
├── SIEMConnector.tsx             // SIEM system integration UI
├── EmergencyServicesAPI.tsx      // Emergency services integration
├── HRSystemIntegration.tsx       // HR system connectors
├── FinancialSystemConnector.tsx  // ERP/Financial system integration
└── ExternalAPIManager.tsx        // Central external API management

lib/integrations/
├── siem-adapters.ts             // SIEM system adapters
├── emergency-api.ts             // Emergency services API
├── hr-connectors.ts             // HR system connectors
└── financial-api.ts             // Financial/ERP API
```

**Функциональные требования:**
- ✅ **SIEM Integration** - security incident correlation
- ✅ **Emergency Services API** - автовызов служб при критических инцидентах
- ✅ **HR System Integration** - employee data, org chart, contacts
- ✅ **Financial/ERP Integration** - cost impact, budget tracking

#### **3.2.6 ISO 22301:2019 Complete Compliance**

**Обязательные компоненты:**
```typescript
// REGULATORY REQUIREMENT - полное соответствие ISO 22301:2019
components/compliance/iso22301/
├── StakeholderAnalysis.tsx       // Clause 4.2 - Stakeholder needs
├── ContextMonitoring.tsx         // Clause 4.1 - Organization context
├── PolicyDeployment.tsx          // Clause 5.2 - Policy deployment
├── ManagementReview.tsx          // Clause 9.3 - Management review
├── InternalAuditManager.tsx      // Clause 9.2 - Internal audit
└── PerformanceMonitoring.tsx     // Clause 9.1 - Monitoring & measurement

lib/compliance/
├── iso22301-requirements.ts     // Complete ISO 22301:2019 mapping
├── compliance-checker.ts        // Automated compliance verification
└── audit-workflows.ts           // Internal audit workflows
```

**Функциональные требования:**
- ✅ **Clause 4 Complete** - Context of Organization (stakeholder analysis, external/internal context)
- ✅ **Clause 5 Complete** - Leadership (policy deployment, responsibility assignment)
- ✅ **Clause 9 Complete** - Performance Evaluation (monitoring, measurement, management review)
- ✅ **Automated Compliance Checking** - real-time ISO compliance status
- ✅ **Internal Audit Management** - complete audit lifecycle

### **3.3 Performance & Accessibility Requirements**
- **WCAG 2.1 AA Compliance** - mandatory
- **Mobile Performance** - < 3s load time on 3G
- **PWA Capability** - installable, offline-capable
- **Keyboard Navigation** - 100% mouse-free operation
- **Screen Reader** - full compatibility

---

## 📄 **4. ДЕТАЛЬНЫЕ СПЕЦИФИКАЦИИ СТРАНИЦ**

### **🏠 4.1 СТРАНИЦА 1: Central Hub & Dashboard**

#### **4.1.1 Общая информация**
| Параметр | Значение |
|----------|----------|
| **URL** | `/` |
| **Layout** | Dashboard |
| **Доступ** | Все авторизованные пользователи |
| **Статус** | 🔄 К реализации |

#### **4.1.2 Назначение**
Стартовая страница после авторизации. Предоставляет общий обзор всех клиентов, проектов и ключевых метрик аудитора/консультанта.

#### **4.1.3 Backend интеграция**
| Сервис/Модуль | Endpoint | Назначение |
|---------------|----------|------------|
| `unified_control_center` | `/api/overview` | Общий обзор |
| `auth_service` | `/api/auth/me` | Информация о пользователе |
| `eventbus` | `/api/events/recent` | Последние события |
| `kpi` API | `/api/kpi/summary` | Общие метрики |
| `bcm_clients` | `/api/clients` | Список клиентов |
| `bcm_core` | `/api/projects/active` | Активные проекты |

#### **4.1.4 UI Компоненты**
```typescript
interface CentralHubComponents {
  MultiClientOverview: {
    purpose: "Обзор всех клиентов аудитора"
    data: "Client[], ClientMetrics"
    features: ["Client switching", "Health status", "Quick actions"]
  }
  
  ActiveProjectsDashboard: {
    purpose: "Активные проекты по всем клиентам"  
    data: "Project[], ProjectStatus"
    features: ["Project timeline", "Progress tracking", "Priority alerts"]
  }
  
  QuickActionsPanel: {
    purpose: "Быстрые действия и shortcuts"
    features: ["New BIA", "Create incident", "Generate report", "Schedule exercise"]
  }
  
  RecentActivityFeed: {
    purpose: "Лента последних событий"
    data: "Event[], Notification[]"
    features: ["Real-time updates", "Filter by client", "Action buttons"]
  }
  
  KeyMetricsSummary: {
    purpose: "Ключевые метрики всех проектов"
    data: "AggregatedKPIs"
    features: ["Visual charts", "Trend indicators", "Drill-down capability"]
  }
}
```

---

### **🏢 4.2 СТРАНИЦА 2: Digital Organization Twin**

#### **4.2.1 Общая информация**
| Параметр | Значение |
|----------|----------|
| **URL** | `/digital-twin` |
| **Layout** | Dashboard |
| **Доступ** | Все авторизованные пользователи |
| **Статус** | 🔄 К реализации |

#### **4.2.2 Назначение**
Цифровая модель организации клиента. Центральный хаб для понимания структуры, процессов, зависимостей и текущего состояния организации.

#### **4.2.3 Backend интеграция - ОБНОВЛЕНО**
| Сервис/Модуль | Endpoint | Назначение |
|---------------|----------|------------|
| `bcm_digital_twin_core` | `/api/digital-twin` | Ядро цифрового двойника |
| `bcm_corporate_twin` | `/api/corporate-twin` | Корпоративный двойник |
| `bcm_digital_copy_manager` | `/api/digital-copies` | Управление копиями |
| `bcm_foundation` | `/api/context` | Организационный контекст ✅ ОБНОВЛЕНО |
| `digital-twin-engine` | `/api/twin-engine` | Движок цифровых двойников |
| `digital-twin-platform` | `/api/twin-platform` | Платформа двойников |

---

### **📊 4.3 СТРАНИЦА 3: Risk & Impact Assessment**

#### **4.3.1 Общая информация**
| Параметр | Значение |
|----------|----------|
| **URL** | `/risk-assessment` |
| **Layout** | Dashboard |
| **Статус** | 🔄 К доработке (частично есть) |

#### **4.3.2 Backend интеграция - ОБНОВЛЕНО**
| Сервис/Модуль | Endpoint | Назначение |
|---------------|----------|------------|
| `bcm_bia` | `/api/bia` | Business Impact Analysis |
| `bcm_risk_management` | `/api/risks` | Управление рисками |
| `bcm_foundation` | `/api/context` | Организационный контекст ✅ ОБНОВЛЕНО |
| `bia_engine` | `/api/bia-engine` | BIA движок |
| `compliance_checker` | `/api/compliance` | Проверка соответствия |
| `scenario_orchestrator` | `/api/scenarios` | Оркестратор сценариев |
| `monte-carlo-simulation` | Local service | Monte Carlo анализ ✅ ЕСТЬ |

---

### **📋 4.4 СТРАНИЦА 4: Strategy & Planning**

#### **4.4.1 Backend интеграция - ОБНОВЛЕНО**
| Сервис/Модуль | Endpoint | Назначение |
|---------------|----------|------------|
| `bcm_plans` | `/api/plans` | Планы восстановления |
| `bcm_governance` | `/api/governance` | Политики и процедуры |
| `bcm_content_library` | `/api/content` | Объединенная библиотека контента ✅ НОВЫЙ |
| `bcm_content_library` | `/api/templates` | Шаблоны документов ✅ НОВЫЙ |
| `bcm_content_library` | `/api/scenarios` | Маркетплейс сценариев ✅ НОВЫЙ |
| `knowledge-base` | `/api/knowledge` | База знаний |
| `document_processor` | `/api/documents` | Обработка документов |
| `opengrc_oscal` | `/api/grc` | OpenGRC интеграция |

#### **4.4.2 UI Компоненты - ОБНОВЛЕНО**
```typescript
interface StrategyPlanningComponents {
  PlanBuilder: {
    purpose: "Конструктор планов непрерывности бизнеса"
    features: ["Template-based creation", "AI assistance", "Workflow integration"]
  }
  
  PolicyManager: {
    purpose: "Управление политиками и процедурами"
    features: ["Version control", "Approval workflows", "Distribution tracking"]
  }
  
  UnifiedContentLibrary: { // ✅ НОВЫЙ КОМПОНЕНТ
    purpose: "Объединенная библиотека шаблонов и сценариев"
    api: "bcm_content_library"
    features: ["Template catalog", "Scenario marketplace", "Custom content", "Content sharing"]
  }
  
  DocumentProcessor: {
    purpose: "Обработка и анализ документов"
    features: ["Document upload", "NLP analysis", "Compliance checking"]
  }
  
  GovernanceFramework: {
    purpose: "Фреймворк управления BCM"
    features: ["Framework selection", "Compliance mapping", "Gap analysis"]
  }
}
```

#### **4.4.3 Tabs/разделы - ОБНОВЛЕНО**
```typescript
const strategyPlanningTabs = [
  {
    id: "bcp-plans",
    name: "Business Continuity Plans",
    component: "PlanBuilder"
  },
  {
    id: "policies",
    name: "Policies & Procedures", 
    component: "PolicyManager"
  },
  {
    id: "content-library", // ✅ ОБНОВЛЕНО
    name: "Content Library", 
    component: "UnifiedContentLibrary" // templates + scenarios в одном
  },
  {
    id: "governance",
    name: "Governance Framework",
    component: "GovernanceFramework" 
  },
  {
    id: "knowledge",
    name: "Knowledge Base",
    component: "KnowledgeBase"
  }
]
```

---

### **🚨 4.5 СТРАНИЦА 5: Incident & Crisis Management**

#### **4.5.1 Общая информация**
| Параметр | Значение |
|----------|----------|
| **URL** | `/incident-management` |
| **Layout** | Dashboard |
| **Статус** | ✅ В основном готово + ТРЕБУЕТ ОБНОВЛЕНИЯ |

#### **4.5.2 Backend интеграция - КРИТИЧЕСКОЕ ОБНОВЛЕНИЕ**
| Сервис/Модуль | Endpoint | Назначение |
|---------------|----------|------------|
| `bcm_incident_unified` | `/api/incidents` | ✅ НОВЫЙ ОБЪЕДИНЕННЫЙ МОДУЛЬ |
| `bcm_exercise` | `/api/exercises` | Учения и тренировки |
| `notification_service` | `/api/notifications` | Уведомления |
| `thehive` | `/api/thehive` | Security incidents |
| `exercise_simulators` | `/api/simulators` | Симуляторы учений |
| `thehive_adapter` | `/api/security` | TheHive интеграция |

#### **🚨 КРИТИЧЕСКОЕ ОБНОВЛЕНИЕ API ИНТЕГРАЦИИ**

Поскольку `bcm_incident` и `bcm_incident_management` объединены в `bcm_incident_unified`, необходимо обновить:

```typescript
// ❌ СТАРАЯ интеграция (требует замены):
const OLD_API_ENDPOINTS = [
  {
    module: 'bcm_incident',
    model: 'bcm.incident',
    endpoint: '/api/v1/bcm/incidents',
  },
  {
    module: 'bcm_incident_management',
    model: 'bcm.incident.response',
    endpoint: '/api/v1/bcm/incident-responses',
  }
]

// ✅ НОВАЯ интеграция (обновить в платформе):
const NEW_API_ENDPOINTS = [
  {
    module: 'bcm_incident_unified',
    model: 'bcm.incident',
    endpoint: '/api/v1/bcm/incidents',
    features: [
      'basic-incident-management',
      'ai-commander',
      'response-teams', 
      'crisis-communication',
      'mobile-response',
      'gps-tracking',
      'escalation-rules',
      'similarity-analysis'
    ]
  }
]
```

#### **4.5.3 UI Компоненты - ОБНОВЛЕНО**
```typescript
interface IncidentManagementComponents {
  // ✅ СУЩЕСТВУЮЩИЕ компоненты (обновить API)
  IncidentBoard: "Основная доска инцидентов с расширенной функциональностью"
  IncidentTimeline: "Timeline событий с AI insights"
  CrisisCommunication: "Интегрированные коммуникации из unified модуля"
  ResponseTeamCoordination: "Расширенная координация команд"
  
  // ✅ НОВЫЕ возможности из unified модуля
  AICommanderDashboard: {
    purpose: "AI Commander с интеллектуальным анализом"
    api: "bcm_incident_unified"
    features: ["AI classification", "Escalation prediction", "Response recommendations", "Similar incidents"]
  }
  
  MobileResponseInterface: {
    purpose: "Мобильный интерфейс для полевых команд"
    api: "bcm_incident_unified" 
    features: ["GPS tracking", "Field updates", "Real-time communication", "Offline support"]
  }
  
  CrisisLevelManagement: {
    purpose: "Управление уровнями кризиса (0-5)"
    api: "bcm_incident_unified"
    features: ["Crisis escalation", "Executive notifications", "Resource allocation"]
  }
  
  IntegratedAnalytics: {
    purpose: "Объединенная аналитика инцидентов"
    api: "bcm_incident_unified"
    features: ["RTO/RPO metrics", "AI performance", "Team efficiency", "Lessons learned"]
  }
}
```

#### **4.5.4 Tabs/разделы - ОБНОВЛЕНО**
```typescript
const incidentManagementTabs = [
  {
    id: "active-incidents",
    name: "Active Incidents",
    component: "IncidentBoard" // ✅ ОБНОВИТЬ API НА unified
  },
  {
    id: "ai-commander", // ✅ НОВЫЙ ТАБ
    name: "AI Commander",
    component: "AICommanderDashboard"
  },
  {
    id: "mobile-response", // ✅ НОВЫЙ ТАБ  
    name: "Mobile Response",
    component: "MobileResponseInterface"
  },
  {
    id: "exercises",
    name: "Exercise & Simulations",
    component: "ExerciseCalendar"
  },
  {
    id: "communication",
    name: "Crisis Communication",
    component: "CrisisCommunication" // ✅ ОБНОВИТЬ НА unified API
  },
  {
    id: "analytics", // ✅ РАСШИРЕННЫЙ ТАБ
    name: "Incident Analytics",
    component: "IntegratedAnalytics"
  }
]
```

---

### **⚙️ 4.6 СТРАНИЦА 6: Workflow & Process Management**

#### **4.6.1 Backend интеграция - ОБНОВЛЕНО**
| Сервис/Модуль | Endpoint | Назначение |
|---------------|----------|------------|
| `bpmn_service` | `/api/bpmn` | BPMN Workflow Engine |
| `bcm_core` | `/api/processes` | Базовые процессы |
| `bcm_foundation` | `/api/config` | Конфигурация workflow ✅ ОБНОВЛЕНО |

---

### **🎓 4.7 СТРАНИЦА 7: Learning & Community**

#### **4.7.1 Backend интеграция - БЕЗ ИЗМЕНЕНИЙ**
| Сервис/Модуль | Endpoint | Назначение |
|---------------|----------|------------|
| `bcm_training` | `/api/training` | Обучение и тренинги |
| `bcm_community` | `/api/community` | Профессиональное сообщество |
| `lms` | `/api/lms` | LMS интеграции |
| `moodle` | `/api/moodle` | Moodle интеграция |
| `lms_adapter` | `/api/lms-adapter` | Multi-LMS поддержка |

---

### **👥 4.8 СТРАНИЦА 8: Client & Project Management**

#### **4.8.1 Backend интеграция - ОБНОВЛЕНО**
| Сервис/Модуль | Endpoint | Назначение |
|---------------|----------|------------|
| `bcm_clients` | `/api/clients` | Управление клиентами |
| `bcm_kpi` | `/api/kpi` | KPI управление |
| `bcm_web_portal` | `/api/portal` | Объединенный портал ✅ ОБНОВЛЕНО |

---

### **🔗 4.9 СТРАНИЦА 9: AI & Automation**

#### **4.9.1 Backend интеграция - БЕЗ ИЗМЕНЕНИЙ**
| Сервис/Модуль | Endpoint | Назначение |
|---------------|----------|------------|
| `bcm_ai_consultant` | `/api/ai-consultant` | AI консультант |
| `ai-consultant` | `/api/ai/consultant` | AI консультант сервис |
| `ai_orchestrator` | `/api/ai/orchestrator` | AI оркестратор |
| `digital-twin-engine` | `/api/digital-twin/ai` | AI для цифровых двойников |
| `orchestrator_service` | `/api/orchestrator` | AI оркестрация |

---

### **📈 4.10 СТРАНИЦА 10: Analytics & Intelligence**

#### **4.10.1 Общая информация**
| Параметр | Значение |
|----------|----------|
| **URL** | `/analytics` |
| **Layout** | Dashboard |
| **Статус** | ✅ УЖЕ РЕАЛИЗОВАНА |

---

### **👤 4.11 СТРАНИЦА 11: My Workspace & Settings**

#### **4.11.1 Backend интеграция - ОБНОВЛЕНО**
| Сервис/Модуль | Endpoint | Назначение |
|---------------|----------|------------|
| `bcm_web_portal` | `/api/portal/personal` | Объединенный портал ✅ ОБНОВЛЕНО |
| `bcm_audit` | `/api/audit/personal` | Аудит (личные логи) |
| `auth_service` | `/api/auth/profile` | Профиль пользователя |

---

## 🔄 **5. КРИТИЧЕСКИЕ ОБНОВЛЕНИЯ ИНТЕГРАЦИИ**

### **5.1 Обновления API mapping для объединенных модулей**

#### **lib/odoo-api-mapper.ts - ТРЕБУЕТ ОБНОВЛЕНИЯ:**

```typescript
// ✅ ОБНОВЛЕННЫЕ ENDPOINTS после консолидации
export const ODOO_ENDPOINTS = [
  // === INFRASTRUCTURE ===
  {
    module: 'bcm_core',
    endpoint: '/api/v1/bcm/core',
    status: 'active'
  },
  {
    module: 'bcm_foundation', // ✅ НОВЫЙ (base+config+context)
    endpoint: '/api/v1/bcm/foundation',
    status: 'active'
  },
  
  // === INCIDENT MANAGEMENT ===
  {
    module: 'bcm_incident_unified', // ✅ НОВЫЙ (incident+management)
    model: 'bcm.incident',
    endpoint: '/api/v1/bcm/incidents',
    features: ['ai-commander', 'mobile-response', 'crisis-management'],
    status: 'active'
  },
  
  // === CONTENT & PORTAL ===
  {
    module: 'bcm_content_library', // ✅ НОВЫЙ (templates+scenarios)
    endpoint: '/api/v1/bcm/content',
    features: ['templates', 'scenarios', 'marketplace'],
    status: 'active'
  },
  {
    module: 'bcm_web_portal', // ✅ НОВЫЙ (portal+admin)
    endpoint: '/api/v1/bcm/portal',
    features: ['client-portal', 'admin-interface'],
    status: 'active'
  },
  
  // === ОСТАЛЬНЫЕ МОДУЛИ (без изменений) ===
  // ... all other existing modules
]
```

#### **lib/api-client.ts - ДОБАВИТЬ МЕТОДЫ:**

```typescript
// ✅ НОВЫЕ методы для unified модулей
class BCMApiClient {
  
  // Incident Unified API
  async getIncidentWithAI(incidentId: string) {
    return this.request(`/api/v1/bcm/incidents/${incidentId}?include=ai_data`);
  }
  
  async triggerAIAnalysis(incidentId: string) {
    return this.request(`/api/v1/bcm/incidents/${incidentId}/ai-analyze`, { method: 'POST' });
  }
  
  async getMobileFieldUpdates(incidentId: string) {
    return this.request(`/api/v1/bcm/incidents/${incidentId}/field-updates`);
  }
  
  // Content Library Unified API
  async getUnifiedContent(type: 'templates' | 'scenarios' | 'all') {
    return this.request(`/api/v1/bcm/content?type=${type}`);
  }
  
  async searchContentLibrary(query: string) {
    return this.request(`/api/v1/bcm/content/search?q=${query}`);
  }
  
  // Foundation API
  async getOrganizationContext(clientId: string) {
    return this.request(`/api/v1/bcm/foundation/context/${clientId}`);
  }
  
  async updateFoundationConfig(config: any) {
    return this.request('/api/v1/bcm/foundation/config', { 
      method: 'PUT', 
      body: config 
    });
  }
  
  // Web Portal Unified API
  async getPortalDashboard(userId: string) {
    return this.request(`/api/v1/bcm/portal/dashboard/${userId}`);
  }
}
```

### **5.2 Обновление State Management**

#### **lib/stores/incident-store.ts - КРИТИЧЕСКОЕ ОБНОВЛЕНИЕ:**

```typescript
// ✅ ОБНОВИТЬ store для unified incident module
interface IncidentStore {
  // Расширенные поля из unified модуля
  incidents: IncidentUnified[]
  
  // AI Commander state
  aiRecommendations: Record<string, AIRecommendation[]>
  aiRiskScores: Record<string, number>
  similarIncidents: Record<string, string[]>
  
  // Mobile Response state  
  fieldUpdates: Record<string, FieldUpdate[]>
  gpsTracking: Record<string, GPSLocation[]>
  
  // Crisis Management state
  crisisLevels: Record<string, number>
  responseTeams: ResponseTeam[]
  
  // Actions - ОБНОВИТЬ для unified API
  fetchIncidentWithAI: (id: string) => Promise<void>
  triggerAIAnalysis: (id: string) => Promise<void>
  updateMobileLocation: (incidentId: string, location: GPSLocation) => Promise<void>
  escalateCrisisLevel: (incidentId: string) => Promise<void>
}
```

### **5.3 Обновление TypeScript типов**

#### **lib/types/incidents.ts - ДОБАВИТЬ:**

```typescript
// ✅ НОВЫЕ типы для unified incident module
interface IncidentUnified {
  // Базовые поля (из bcm_incident)
  id: string
  incident_number: string
  title: string
  description: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  status: 'draft' | 'detected' | 'assessing' | 'responding' | 'recovering' | 'resolved' | 'closed'
  
  // AI Commander поля (из bcm_incident_management)
  ai_risk_score?: number
  ai_recommendations?: string
  ai_similar_incidents?: string[]
  ai_escalation_prediction?: boolean
  ai_classification_confidence?: number
  
  // Mobile Response поля
  mobile_reporting_enabled?: boolean
  gps_tracking_enabled?: boolean
  field_updates?: FieldUpdate[]
  
  // Crisis Management поля
  crisis_level?: number
  business_impact_level?: string
  response_team_activated?: boolean
  response_team_members?: ResponseTeamMember[]
  incident_commander?: string
  
  // Escalation поля
  escalation_level?: number
  escalation_deadline?: string
  auto_escalate?: boolean
  escalation_history?: string
}

interface AIRecommendation {
  type: 'immediate' | 'assessment' | 'containment' | 'recovery'
  priority: 'high' | 'medium' | 'low'
  action: string
  confidence: number
}

interface FieldUpdate {
  id: string
  incident_id: string
  reporter_id: string
  update_text: string
  gps_location?: string
  timestamp: string
}

interface ResponseTeamMember {
  id: string
  name: string
  role: string
  mobile_phone?: string
  email?: string
}
```

---

## 🚨 **6. ПЛАН МИГРАЦИИ И ОБНОВЛЕНИЯ**

### **6.1 Критические задачи (ВЫСОКИЙ ПРИОРИТЕТ)**

#### **Неделя 1: API Integration Updates**
- ✅ **Обновить odoo-api-mapper.ts** с новыми endpoints
- ✅ **Обновить api-client.ts** с методами unified модулей  
- ✅ **Обновить TypeScript типы** для расширенных моделей
- ✅ **Тестировать API compatibility** с новыми модулями

#### **Неделя 2: Incident Management Upgrade**
- ✅ **Обновить IncidentManagement.tsx** для unified API
- ✅ **Добавить AI Commander компоненты**
- ✅ **Добавить Mobile Response интерфейс**
- ✅ **Интегрировать Crisis Level management**

### **6.2 Средний приоритет**

#### **Неделя 3: Content Library Integration**
- ✅ **Объединить Template и Scenario компоненты**
- ✅ **Создать UnifiedContentLibrary компонент**
- ✅ **Обновить Strategy Planning страницу**

#### **Неделя 4: Portal Consolidation**
- ✅ **Обновить Client Management интеграцию**
- ✅ **Объединить Portal компоненты**
- ✅ **Обновить Workspace страницу**

### **6.3 Тестирование и валидация**

#### **Неделя 5: Integration Testing**
- ✅ **E2E тестирование updated workflows**
- ✅ **API compatibility tests**
- ✅ **Performance regression tests**
- ✅ **User acceptance testing**

---

## ✅ **7. КРИТЕРИИ ПРИЕМКИ - ОБНОВЛЕНО**

### **7.1 Функциональные критерии**
- ✅ Все 11 страниц работают с обновленными модулями
- ✅ **Incident Management** полностью интегрирован с `bcm_incident_unified`
- ✅ **Strategy Planning** использует `bcm_content_library`
- ✅ **Client Management** работает с `bcm_web_portal`
- ✅ Cross-module навигация функционирует

### **7.2 Технические критерии**
- ✅ **API совместимость** с 22 обновленными модулями подтверждена
- ✅ **No breaking changes** в существующей функциональности
- ✅ **Performance improvements** от консолидации модулей
- ✅ **Enhanced functionality** доступна через новые unified модули

### **7.3 Новые функциональные критерии**
- ✅ **AI Commander** функционирует в Incident Management
- ✅ **Mobile Response** интерфейс работает с GPS
- ✅ **Crisis Level Management** интегрирован
- ✅ **Unified Content Library** объединяет templates и scenarios
- ✅ **Foundation API** обеспечивает централизованную конфигурацию

### **7.4 UX & Accessibility Criteria**
- ✅ **WCAG 2.1 AA audit passed** (независимый аудит)
- ✅ **PWA installable and functional offline**
- ✅ **Complete keyboard navigation working**
- ✅ **Screen reader compatibility** (NVDA, JAWS, VoiceOver)
- ✅ **Mobile emergency access** < 10 seconds to incident report
- ✅ **Cross-module workflows** seamlessly connected
- ✅ **ISO 22301:2019** 100% compliance UI coverage

---

## 📚 **8. ОБНОВЛЕННЫЕ ПРИЛОЖЕНИЯ**

### **8.1 Consolidated Module Map**
Карта соответствия старых и новых модулей для разработчиков

### **8.2 Enhanced API Documentation**
Обновленная документация для 4 новых unified модулей

### **8.3 Migration Scripts**
Скрипты для обновления существующих API calls

### **8.4 Testing Scenarios**
Сценарии тестирования новой функциональности

---

**ОБНОВЛЕННОЕ ТЕХНИЧЕСКОЕ ЗАДАНИЕ**

*Документ обновлен:* AI Assistant  
*Дата обновления:* 2025-01-17  
*Версия:* 3.0  
*Статус:* Обновлено с критическими UX требованиями ✅

**Ключевые изменения v3.0:**
- ✅ **ДОБАВЛЕН РАЗДЕЛ 3.2** - User Experience Requirements
- ✅ **User Onboarding & Help System** - обязательные компоненты
- ✅ **Mobile & Emergency Access** - PWA и offline поддержка
- ✅ **Accessibility & WCAG 2.1 AA** - юридические требования
- ✅ **Cross-Module Integration** - решение изоляции модулей
- ✅ **External System Integration UI** - SIEM, Emergency Services, HR, ERP
- ✅ **ISO 22301:2019 Complete Compliance** - полная реализация стандарта
- ✅ **Обновлены критерии приемки** - добавлен раздел 7.4 UX & Accessibility

**Предыдущие изменения v2.0:**
- ✅ 28 → 22 модуля после консолидации
- ✅ Новые unified endpoints и API
- ✅ Расширенная функциональность Incident Management
- ✅ Объединенная Content Library
- ✅ Критические обновления интеграции