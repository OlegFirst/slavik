# BCM Platform Development Instructions for Claude

## Project Overview
We are building a unified BCM (Business Continuity Management) platform frontend that integrates with a comprehensive Odoo-based backend containing 28 specialized BCM modules. The platform uses Next.js 15, React 19, TypeScript, and Tailwind CSS.

## Project Structure
```
unified-bcm-platform/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Main layout with sidebar navigation
│   ├── page.tsx                 # Dashboard homepage
│   ├── providers.tsx            # React Query & Toaster providers
│   └── modules/                 # Individual module routes
│       ├── risk-management/     # Example: Risk Management module
│       └── bia/                 # Example: BIA module
├── components/
│   ├── dashboard/               # Dashboard components
│   │   └── MainDashboard.tsx   # Main dashboard with KPIs and AI organs
│   ├── layout/                  # Layout components
│   │   └── Navigation.tsx      # Sidebar navigation with module categories
│   ├── modules/                 # Individual module components
│   │   ├── RiskManagement.tsx  # Example: Risk Management interface
│   │   └── BIAModule.tsx       # Example: BIA interface
│   └── ui/                     # Reusable UI components
│       └── button.tsx          # Shadcn/ui style components
├── lib/
│   ├── api.ts                  # API client for Odoo integration
│   └── utils.ts                # Utility functions
└── .env.local                  # Environment configuration
```

## Backend Architecture
The platform connects to a microservices architecture:
- **Odoo BCM Core** (port 8069) - Main business logic with 28 modules
- **AI Orchestrator** (port 8000) - Coordination of 10 AI organs
- **BIA Engine** (port 8082) - Business Impact Analysis with ML
- **Document Processor** (port 8083) - AI document processing
- **PostgreSQL** (port 5432) - Primary database
- **Redis** (port 6379) - Caching and sessions

## 28 BCM Modules to Implement

### Core Infrastructure (Priority 1)
1. **bcm_core** - Organization context and base functionality
2. **bcm_base** - AI foundation and document processing
3. **bcm_ai_control** - AI Control Center for 10 AI organs
4. **bcm_digital_twin_core** - Digital twin integration
5. **bcm_context** - Organizational context management  
6. **bcm_config** - System configuration

### Business Process (Priority 2)
7. **bcm_bia** - Business Impact Analysis ✅ DONE
8. **bcm_risk_management** - Risk assessment and management ✅ DONE
9. **bcm_incident_management** - Incident response coordination
10. **bcm_incident** - Core incident handling
11. **bcm_governance** - Strategic BCM governance
12. **bcm_plans** - Business continuity plans

### Training & Community (Priority 3)
13. **bcm_training** - Learning management with AI coach
14. **bcm_community** - Professional community platform
15. **bcm_scenario_hub** - Scenario marketplace
16. **bcm_exercise** - Training exercises and simulations

### Analytics & Reporting (Priority 4)
17. **bcm_reporting** - Cross-module analytics
18. **bcm_kpi** - Performance measurement
19. **bcm_audit** - Audit management and compliance

### Client & Portal (Priority 5)
20. **bcm_clients** - Multi-tenant client management
21. **bcm_portal** - Self-service client portal
22. **bcm_templates** - Document templates library

### AI & Advanced (Priority 6)
23. **bcm_ai_consultant** - AI assistant integration
24. **bcm_ai_twin_orchestrator** - AI twins coordination
25. **bcm_intelligent_base** - Shared AI services
26. **bcm_corporate_twin** - Corporate digital twin
27. **bcm_digital_copy_manager** - Digital copy management
28. **bcm_admin_website** - Web-based administration

## Development Guidelines

### 1. Module Creation Pattern
For each new BCM module, follow this exact pattern:

#### Step 1: Create Module Component
File: `components/modules/ModuleName.tsx`
```tsx
'use client'

import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { 
  // Import relevant Lucide icons
} from 'lucide-react'

// Define TypeScript interfaces for data
interface ModuleData {
  id: string
  // Add relevant fields
}

interface ModuleMetrics {
  // Add metric fields
}

export function ModuleNameModule() {
  const [selectedFilter, setSelectedFilter] = useState<string>('all')
  
  // Data fetching with React Query
  const { data: moduleData, isLoading } = useQuery<ModuleData[]>({
    queryKey: ['module-data', selectedFilter],
    queryFn: async () => {
      // Real API call (implement when backend is ready):
      // const response = await fetch('/api/odoo/bcm_module_name/data')
      // return response.json()
      
      // Mock data for development:
      return getMockData()
    }
  })

  const { data: metrics } = useQuery<ModuleMetrics>({
    queryKey: ['module-metrics'],
    queryFn: async () => getMockMetrics()
  })

  if (isLoading) {
    return <LoadingState />
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <ModuleHeader />
      
      {/* Metrics Cards */}
      <MetricsGrid metrics={metrics} />
      
      {/* Filters */}
      <FiltersSection />
      
      {/* Main Content */}
      <MainContent data={moduleData} />
      
      {/* Additional Panels */}
      <AdditionalPanels />
    </div>
  )
}

// Helper components and mock data functions
function getMockData(): ModuleData[] {
  // Return relevant mock data
}
```

#### Step 2: Create Route Page
File: `app/modules/module-name/page.tsx`
```tsx
import { ModuleNameModule } from '@/components/modules/ModuleName'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Module Name - BCM Platform',
  description: 'Description of module functionality',
}

export default function ModuleNamePage() {
  return <ModuleNameModule />
}
```

#### Step 3: Add to Navigation
Update `components/layout/Navigation.tsx` by adding the module to the appropriate category in `BCM_MODULES` array.

### 2. Design Patterns

#### Layout Structure
Every module should follow this layout:
```tsx
<div className="p-6 space-y-6">
  {/* Header with title and action buttons */}
  <div className="flex items-center justify-between">
    <div>
      <h1 className="text-3xl font-bold text-gray-900">Module Title</h1>
      <p className="text-gray-600">Module description</p>
    </div>
    <div className="flex gap-3">
      {/* Action buttons */}
    </div>
  </div>

  {/* KPI/Metrics cards */}
  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
    {/* Metric cards */}
  </div>

  {/* Filters */}
  <div className="flex gap-4 items-center">
    {/* Filter buttons */}
  </div>

  {/* Main content area */}
  <div className="bg-white rounded-lg border shadow-sm">
    {/* Tables, charts, forms */}
  </div>

  {/* Additional panels */}
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
    {/* Side panels */}
  </div>
</div>
```

#### Color Coding System
Use consistent colors for different types of content:
- **Blue**: Primary actions, core functionality
- **Red**: Risks, critical alerts, errors
- **Yellow**: Warnings, medium priority
- **Green**: Success, completed, healthy status
- **Purple**: AI-related features
- **Gray**: Secondary information, disabled states

#### Icon Usage
Use Lucide React icons consistently:
- `Shield` - Security, protection, BCM
- `AlertTriangle` - Risks, warnings, incidents
- `TrendingUp` - Analytics, improvements, BIA
- `Brain` - AI features
- `Users` - People, training, community
- `FileText` - Documents, plans, templates
- `BarChart3` - Reporting, metrics
- `Settings` - Configuration, admin

### 3. API Integration Guidelines

#### Mock Data Strategy
During development, use mock data that mirrors real API structure:
```tsx
// Always provide realistic mock data
function getMockData() {
  return [
    {
      id: '1',
      // Use realistic field names and values
      // that match expected Odoo model structure
    }
  ]
}
```

#### Real API Integration
When backend is ready, replace mock calls with real API:
```tsx
// Real API pattern
const { data } = useQuery({
  queryKey: ['module-data'],
  queryFn: async () => {
    const response = await fetch('/api/odoo/bcm_module_name/data', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        // Add authentication headers when needed
      }
    })
    if (!response.ok) throw new Error('API call failed')
    return response.json()
  }
})
```

### 4. State Management

#### React Query for Server State
Use React Query for all server data:
- Automatic caching and background updates
- Loading and error states
- Optimistic updates for mutations

#### Local State with useState
Use useState for UI state:
- Filters, selected items, form data
- Modal visibility, panel toggles

#### No Global State Library Needed
The current architecture doesn't require Zustand or Redux. React Query handles server state, useState handles local state.

### 5. Responsive Design

#### Mobile-First Approach
Always implement responsive layouts:
```tsx
// Grid example
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

// Flex example  
<div className="flex flex-col md:flex-row gap-4">

// Hide on small screens
<div className="hidden md:block">
```

#### Breakpoint System
- `sm:` - 640px and up
- `md:` - 768px and up  
- `lg:` - 1024px and up
- `xl:` - 1280px and up

### 6. Performance Guidelines

#### Code Splitting
Each module is automatically code-split by Next.js App Router.

#### Image Optimization
Use Next.js Image component for any images:
```tsx
import Image from 'next/image'
```

#### Bundle Size
Keep individual module components under 100KB to maintain fast loading.

## AI Integration Patterns

### 10 AI Organs to Display
The platform manages these AI organisms:
1. **Governance Brain** - Strategic decision-making
2. **Risk Advisor** - Risk assessment and prediction
3. **Incident Commander** - Emergency response coordination  
4. **Training Mentor** - Learning and development
5. **Audit Inspector** - Compliance monitoring
6. **Recovery Planner** - Business recovery strategies
7. **Communication Hub** - Stakeholder messaging
8. **Resource Manager** - Asset optimization
9. **Performance Monitor** - KPI tracking
10. **Knowledge Keeper** - Documentation management

### AI Status Display Pattern
```tsx
// AI organ status component
function AIOrganStatus({ organ }: { organ: AIOrgan }) {
  return (
    <div className="p-4 border rounded-lg">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-medium">{organ.name}</h3>
        <StatusIndicator status={organ.status} />
      </div>
      <div className="text-xs text-gray-500">
        Health: {organ.health}% • {organ.responseTime}ms
      </div>
      <HealthBar health={organ.health} />
    </div>
  )
}
```

## Testing Strategy

### Development Testing
- Test with mock data first
- Verify responsive design on different screen sizes
- Check loading and error states
- Validate form inputs and user interactions

### Integration Testing
- Test API integration when backend is available
- Verify real-time data updates
- Check error handling for failed API calls

## Deployment Preparation

### Environment Variables
Always use environment variables for API endpoints:
```env
NEXT_PUBLIC_API_URL=http://localhost:8069
NEXT_PUBLIC_AI_URL=http://localhost:8000
NEXT_PUBLIC_BIA_URL=http://localhost:8082
```

### Build Optimization
Before deployment:
```bash
npm run build
npm run type-check
npm run lint
```

## Priority Implementation Order

### Phase 1: Core Foundation (Week 1)
1. bcm_core - Organization management
2. bcm_ai_control - AI Control Center  
3. bcm_context - Context management

### Phase 2: Business Process (Week 2)
4. bcm_incident_management - Critical for operations
5. bcm_governance - Strategic management
6. bcm_plans - Core BCM functionality

### Phase 3: Analytics & Training (Week 3)  
7. bcm_reporting - Cross-module analytics
8. bcm_training - Learning management
9. bcm_exercise - Simulation exercises

### Phase 4: Advanced Features (Week 4)
10. Remaining 19 modules based on business priority

## Common Patterns Reference

### Table Component Pattern
```tsx
<div className="overflow-x-auto">
  <table className="w-full">
    <thead>
      <tr className="border-b">
        <th className="text-left py-3 px-2 font-medium text-gray-500">Column</th>
      </tr>
    </thead>
    <tbody>
      {data.map(item => (
        <tr key={item.id} className="border-b hover:bg-gray-50">
          <td className="py-3 px-2">{item.value}</td>
        </tr>
      ))}
    </tbody>
  </table>
</div>
```

### Metric Card Pattern
```tsx
function MetricCard({ title, value, icon: Icon, color }) {
  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between">
        <div className={cn("w-12 h-12 rounded-lg flex items-center justify-center", colorClasses)}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
      <div className="mt-4">
        <div className="text-2xl font-bold text-gray-900">{value}</div>
        <div className="text-sm text-gray-500">{title}</div>
      </div>
    </div>
  )
}
```

### Filter Button Pattern
```tsx
<div className="flex gap-2">
  {categories.map(category => (
    <Button
      key={category}
      variant={selected === category ? "default" : "outline"}
      size="sm"
      onClick={() => setSelected(category)}
    >
      {category}
    </Button>
  ))}
</div>
```

## Final Notes

- **Consistency is key** - Follow these patterns exactly for all modules
- **Start with mock data** - Don't wait for backend API completion
- **Focus on user experience** - Every module should be intuitive and responsive  
- **Document as you go** - Add comments for complex logic
- **Test incrementally** - Verify each module works before moving to the next

Remember: The goal is to create a unified, professional BCM platform that showcases all 28 modules with modern UI/UX while maintaining integration capability with the comprehensive Odoo backend.
