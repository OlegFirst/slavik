# Unified Frontend Strategy 🎯

**Дата:** 2025-10-17
**Статус:** STRATEGIC PLAN
**Приоритет:** ВЫСОКИЙ - избежать дублирования UI

---

## 🎯 Проблема: Фрагментированный UI

### Текущая ситуация (что есть сейчас)

```
❌ ПЛОХО: UI разбросан по сервисам

/platform_services/
├── digital_twin/
│   ├── frontend_twin/          ← Digital Twin UI (Next.js)
│   └── web/                    ← Старый web UI
├── bia_service/
│   └── web_ui/                 ← BIA UI (?)
└── другие сервисы...

/intelligent_core/
├── system_bcm_service/
│   ├── frontend/               ← BCM UI
│   └── frontend_full/          ← BCM Full UI
└── ...

/interface/
├── mvp-platform/
│   └── frontend/              ← MVP UI (Next.js 14 ✅)
├── web-app/                   ← Web app (?)
└── админ/                     ← Admin UI (?)
```

**Проблемы:**
1. ❌ Дублирование кода (auth, layouts, components)
2. ❌ Разные UI frameworks (Next.js, React, Vanilla JS)
3. ❌ Несогласованный UX
4. ❌ Сложно поддерживать
5. ❌ Пользователь переходит между разными интерфейсами

---

## ✅ Решение: UNIFIED FRONTEND

### Концепция: Один UI для всей платформы

```
✅ ХОРОШО: Единый фронтенд

/interface/unified-frontend/         ← ЕДИНСТВЕННЫЙ UI
├── src/
│   ├── app/                        # Next.js 14 App Router
│   │   ├── (auth)/                # Auth pages
│   │   │   ├── login/
│   │   │   └── register/
│   │   │
│   │   ├── (platform)/           # Main platform
│   │   │   ├── layout.tsx        # Unified layout + sidebar
│   │   │   │
│   │   │   ├── dashboard/        # Main dashboard
│   │   │   │
│   │   │   ├── organizations/    # Organizations module
│   │   │   │   ├── [id]/
│   │   │   │   └── create/
│   │   │   │
│   │   │   ├── bia/             # BIA module (from mvp-platform)
│   │   │   │   ├── [id]/
│   │   │   │   └── create/
│   │   │   │
│   │   │   ├── digital-twin/    # Digital Twin module
│   │   │   │   ├── topology/
│   │   │   │   ├── clone/
│   │   │   │   ├── simulations/
│   │   │   │   └── collection/
│   │   │   │
│   │   │   ├── bcm/             # BCM Management module
│   │   │   │   ├── cycles/
│   │   │   │   ├── recovery/
│   │   │   │   └── continuity/
│   │   │   │
│   │   │   ├── risk/            # Risk Assessment module
│   │   │   ├── compliance/      # Compliance module
│   │   │   ├── plans/           # Plans module
│   │   │   └── analytics/       # Analytics module
│   │   │
│   │   └── (admin)/             # Admin panel
│   │       └── ...
│   │
│   ├── components/              # Shared components
│   │   ├── ui/                 # shadcn/ui base components
│   │   ├── layout/             # Layout components
│   │   │   ├── navbar.tsx
│   │   │   ├── sidebar.tsx
│   │   │   └── org-switcher.tsx
│   │   ├── bia/                # BIA-specific components
│   │   ├── digital-twin/       # Digital Twin components
│   │   ├── bcm/                # BCM components
│   │   └── shared/             # Cross-module components
│   │
│   ├── lib/
│   │   ├── api/                # API clients for ALL services
│   │   │   ├── bia.ts          # BIA Service (8012)
│   │   │   ├── digital-twin.ts  # Digital Twin (8096)
│   │   │   ├── bcm.ts          # BCM Service (8050)
│   │   │   ├── simulation.ts    # Simulation (8095)
│   │   │   └── ...
│   │   │
│   │   ├── auth/               # Shared auth logic
│   │   └── utils/
│   │
│   ├── hooks/                  # Shared React hooks
│   └── types/                  # Shared TypeScript types
│
└── package.json
```

---

## 🏗️ Архитектура

### 1. Unified Layout

```typescript
// app/(platform)/layout.tsx

export default function PlatformLayout({ children }) {
  return (
    <div className="flex h-screen">
      {/* Единый sidebar для всей платформы */}
      <Sidebar modules={[
        { name: "Dashboard", icon: Home, href: "/dashboard" },
        { name: "Organizations", icon: Building, href: "/organizations" },
        { name: "BIA", icon: FileCheck, href: "/bia" },
        { name: "Digital Twin", icon: Network, href: "/digital-twin" },
        { name: "BCM", icon: Shield, href: "/bcm" },
        { name: "Risk", icon: AlertTriangle, href: "/risk" },
        { name: "Compliance", icon: CheckSquare, href: "/compliance" },
        { name: "Plans", icon: FileText, href: "/plans" },
        { name: "Analytics", icon: BarChart, href: "/analytics" },
      ]} />

      <main className="flex-1 overflow-y-auto">
        {/* Единый navbar */}
        <Navbar />

        {/* Module content */}
        <div className="container mx-auto p-6">
          {children}
        </div>
      </main>
    </div>
  );
}
```

### 2. Module-based Organization

Каждый модуль = отдельный раздел UI, но **ВНУТРИ** единого приложения:

```typescript
// Модуль BIA
/bia/
  ├── page.tsx              // Список BIA
  ├── create/page.tsx       // Создать BIA
  └── [id]/
      ├── page.tsx          // BIA Details
      ├── processes/        // Процессы
      ├── questionnaire/    // Анкета
      └── results/          // Результаты

// Модуль Digital Twin
/digital-twin/
  ├── page.tsx              // DT Overview
  ├── topology/             // Platform Topology
  ├── clone/                // System Clone
  ├── simulations/          // Simulations
  └── collection/           // Data Collection

// И т.д.
```

### 3. Shared API Layer

```typescript
// lib/api/index.ts - ЕДИНЫЙ API клиент

import { BIAClient } from './bia';
import { DigitalTwinClient } from './digital-twin';
import { BCMClient } from './bcm';

export const api = {
  bia: new BIAClient('http://localhost:8012'),
  digitalTwin: new DigitalTwinClient('http://localhost:8096'),
  bcm: new BCMClient('http://localhost:8050'),
  simulation: new SimulationClient('http://localhost:8095'),
  // ... other services
};

// Usage in components
const { data } = useQuery({
  queryKey: ['bia', id],
  queryFn: () => api.bia.getById(id)
});
```

---

## 📋 Migration Plan

### Phase 1: Foundation (Неделя 1) ✅ ЧАСТИЧНО ГОТОВО

**База уже есть:** `/interface/platform-frontend/frontend/`

```bash
✅ Next.js 14 + TypeScript
✅ Tailwind CSS
✅ Zustand state management
✅ Auth flow (login/register)
✅ Organizations module
✅ BIA module
```

**Что добавить:**
- [ ] Unified sidebar component
- [ ] Organization switcher (multi-tenant)
- [ ] Shared components library (shadcn/ui)

### Phase 2: Digital Twin Integration (Неделя 2-3)

**Добавить модуль Digital Twin:**
```bash
cd /interface/platform-frontend/frontend

# Add Digital Twin routes
mkdir -p src/app/(platform)/digital-twin/{topology,clone,simulations,collection}

# Create API client for Digital Twin
# lib/api/digital-twin.ts - generated from OpenAPI

# Add Digital Twin components
mkdir -p src/components/digital-twin
```

**Что интегрировать:**
- [ ] Platform Topology page
- [ ] System Clone management
- [ ] Simulations UI
- [ ] Data Collection wizard

### Phase 3: BCM Integration (Неделя 4)

**Добавить BCM модуль:**
```bash
# Add BCM routes
mkdir -p src/app/(platform)/bcm/{cycles,recovery,continuity}

# BCM API client
# lib/api/bcm.ts

# BCM components
mkdir -p src/components/bcm
```

### Phase 4: Other Modules (Неделя 5-6)

- [ ] Risk Assessment
- [ ] Compliance
- [ ] Plans Management
- [ ] Analytics Dashboard

---

## 🎨 Design System (Unified)

### Single source of truth для дизайна

```typescript
// Design tokens
const theme = {
  colors: {
    primary: '#764ba2',      // Purple (from old Digital Twin UI)
    secondary: '#667eea',
    // ... unified color palette
  },

  components: {
    // Все компоненты используют одинаковый стиль
  }
};
```

### Shared Components

```
components/
├── ui/                     # Base UI (shadcn/ui)
│   ├── button.tsx
│   ├── card.tsx
│   ├── dialog.tsx
│   ├── input.tsx
│   └── ...
│
├── layout/                 # Layout components
│   ├── navbar.tsx         # Единый navbar для всей платформы
│   ├── sidebar.tsx        # Единый sidebar с модулями
│   ├── breadcrumbs.tsx
│   └── page-header.tsx
│
├── data-display/           # Data display components
│   ├── data-table.tsx     # Универсальная таблица
│   ├── metric-card.tsx    # Metric cards
│   ├── status-badge.tsx
│   └── ...
│
└── forms/                  # Form components
    ├── form-builder.tsx
    ├── wizard-step.tsx
    └── ...
```

---

## 🔗 API Integration Strategy

### Centralized API Management

```typescript
// lib/api/config.ts
export const API_ENDPOINTS = {
  AUTH: 'http://localhost:8001',
  BIA: 'http://localhost:8012',
  DIGITAL_TWIN: 'http://localhost:8096',
  BCM: 'http://localhost:8050',
  SIMULATION: 'http://localhost:8095',
  PLANNING: 'http://localhost:8011',
  RISK: 'http://localhost:8006',
  // ... all services
};

// lib/api/client.ts - Base API client
export class BaseAPIClient {
  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Authorization': `Bearer ${getToken()}`,
      }
    });
  }
}

// lib/api/digital-twin.ts
export class DigitalTwinClient extends BaseAPIClient {
  constructor() {
    super(API_ENDPOINTS.DIGITAL_TWIN);
  }

  async getTopology() {
    return this.client.get('/api/v1/topology');
  }

  async createMirror(serviceName: string) {
    return this.client.post('/api/v1/system-clone/create', {
      service_name: serviceName
    });
  }

  // ... all Digital Twin API methods
}
```

### OpenAPI Code Generation

```bash
# Generate TypeScript clients from OpenAPI specs

# Digital Twin
curl http://localhost:8096/openapi.json > openapi/digital-twin.json
npx openapi-typescript openapi/digital-twin.json --output types/digital-twin-api.ts

# BIA Service
curl http://localhost:8012/openapi.json > openapi/bia.json
npx openapi-typescript openapi/bia.json --output types/bia-api.ts

# etc.
```

---

## 📊 Module Mapping

### Как модули сопоставляются с сервисами

| UI Module | Backend Services | Ports |
|-----------|-----------------|-------|
| **Organizations** | organizations API | 8000 |
| **BIA** | bia_service | 8012 |
| **Digital Twin** | digital_twin | 8096 |
| → Topology | digital_twin `/topology` | 8096 |
| → System Clone | digital_twin `/system-clone` | 8096 |
| → Simulations | simulation_service (via bridge) | 8095 |
| → Data Collection | digital_twin `/data-collection` | 8096 |
| **BCM** | system_bcm_service | 8050 |
| **Risk** | risk_service | 8006 |
| **Planning** | planning_service | 8011 |
| **Compliance** | compliance_service | 8014 |
| **Plans** | plans_service | 8023 |

---

## ✅ Benefits of Unified Frontend

### 1. Consistency

```
✅ Единый UX across всех модулей
✅ Одинаковые UI components
✅ Consistent navigation
✅ Same design language
```

### 2. Code Reuse

```
✅ Shared components library
✅ Single auth implementation
✅ Common API layer
✅ Shared utilities
```

### 3. Better DX

```
✅ Один проект для разработки
✅ Single build process
✅ Unified testing
✅ Easier debugging
```

### 4. Better UX

```
✅ Пользователь НЕ переключается между приложениями
✅ Single sign-on
✅ Unified navigation
✅ Consistent mental model
```

### 5. Maintainability

```
✅ Одно место для updates
✅ Easier to add new modules
✅ Less code duplication
✅ Single deployment
```

---

## 🚀 Implementation Steps

### Step 1: ✅ DONE - Renamed to platform-frontend

```bash
cd /Users/MD/AI-Platform-ISO/interface/platform-frontend/frontend

# Update package.json
{
  "name": "ai-platform-unified-frontend",
  "version": "2.0.0"
}
```

### Step 2: Реструктурировать для модулей

```bash
cd src/app

# Create module structure
mkdir -p (platform)/{bia,digital-twin,bcm,risk,compliance,plans,analytics}

# Move existing pages
mv dashboard (platform)/dashboard
```

### Step 3: Создать unified sidebar

```typescript
// components/layout/sidebar.tsx

const modules = [
  {
    group: "Core",
    items: [
      { name: "Dashboard", href: "/dashboard", icon: Home },
      { name: "Organizations", href: "/organizations", icon: Building },
    ]
  },
  {
    group: "Analysis",
    items: [
      { name: "BIA", href: "/bia", icon: FileCheck },
      { name: "Risk", href: "/risk", icon: AlertTriangle },
    ]
  },
  {
    group: "Platform",
    items: [
      { name: "Digital Twin", href: "/digital-twin", icon: Network },
      { name: "BCM", href: "/bcm", icon: Shield },
    ]
  },
  // ...
];
```

### Step 4: Добавить Digital Twin модуль

```bash
# Generate API client
curl http://localhost:8096/openapi.json > openapi/digital-twin.json

# Create module pages
# src/app/(platform)/digital-twin/...

# Create components
# src/components/digital-twin/...
```

### Step 5: Интегрировать остальные модули

По аналогии с Digital Twin.

---

## 📁 Final Structure

```
/interface/unified-frontend/
├── frontend/                      # ЕДИНЫЙ UI
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/           # Auth pages
│   │   │   ├── (platform)/       # All modules
│   │   │   │   ├── dashboard/
│   │   │   │   ├── organizations/
│   │   │   │   ├── bia/
│   │   │   │   ├── digital-twin/
│   │   │   │   ├── bcm/
│   │   │   │   ├── risk/
│   │   │   │   └── ...
│   │   │   └── (admin)/
│   │   │
│   │   ├── components/          # Shared components
│   │   ├── lib/                 # Shared logic
│   │   │   └── api/            # API clients for ALL services
│   │   ├── hooks/              # Shared hooks
│   │   └── types/              # Shared types
│   │
│   └── package.json
│
├── backend/                     # Backend proxy (optional)
└── docker-compose.yml

/platform_services/
├── digital_twin/                # Backend service (NO UI)
├── bia_service/                 # Backend service (NO UI)
└── ...                          # All backend services (NO UI)

/intelligent_core/
├── system_bcm_service/          # Backend service (NO UI)
└── ...                          # All intelligent services (NO UI)
```

---

## 🎯 Summary

### ❌ До (сейчас):
- Фрагментированный UI
- Дублирование кода
- Разные фреймворки
- Плохой UX (переключение между приложениями)

### ✅ После (unified):
- **ОДИН** Next.js frontend
- Shared components
- Unified UX
- Модульная архитектура
- Легко добавлять новые модули

---

## 🔥 Next Action

**Что делать СЕЙЧАС:**

1. ✅ Переименовать `/interface/mvp-platform/` → `/interface/unified-frontend/`
2. ✅ Добавить Digital Twin module в этот frontend
3. ✅ Создать unified sidebar
4. ✅ НЕ создавать отдельный UI для Digital Twin

**Хочешь чтобы я:**
1. Переименовал mvp-platform в unified-frontend?
2. Добавил Digital Twin routes в существующий frontend?
3. Создал unified sidebar?

**Скажи да, и я начну! 🚀**
