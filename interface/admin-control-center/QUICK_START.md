# 🚀 Quick Start - AI Platform Admin Dashboard

## ✅ Current Status: RUNNING

**URL:** http://localhost:3001
**Status:** ✅ Development server active
**Port:** 3001

---

## 🎯 What's Working

### ✅ Infrastructure Complete
- [x] React 18 + TypeScript + Vite
- [x] 497 npm packages installed
- [x] Development server running
- [x] Tailwind CSS + Shadcn/ui configured
- [x] React Router with 7 routes

### ✅ API Service Layer Created
File: `src/services/platform.ts`

Provides TypeScript clients for:
- AI Orchestrator (port 8000)
- Workflow Intelligence (port 8003)
- Community Intelligence (port 8004)
- Predictive Service (port 8005)
- Analytics Specialist (port 8051)
- Event Bus (port 8001)
- API Gateway (port 8777)

### ✅ Vite Proxy Configured
All API calls proxied through Vite:
- `/api/orchestrator/*` → http://localhost:8000
- `/api/workflow/*` → http://localhost:8003
- `/api/community/*` → http://localhost:8004
- `/api/predictive/*` → http://localhost:8005
- `/api/analytics/*` → http://localhost:8051
- `/api/eventbus/*` → http://localhost:8001
- `/api/gateway/*` → http://localhost:8777
- `/prometheus/*` → http://localhost:9090
- `/grafana/*` → http://localhost:3000

---

## 📍 Available Routes

Visit these URLs in your browser:

1. **Main Dashboard** - http://localhost:3001/
   - Component: RealDataDashboard
   - Shows platform overview

2. **Architecture Monitor** - http://localhost:3001/architecture
   - Component: CentralizedArchitectureMonitor
   - Service health & architecture

3. **Services** - http://localhost:3001/services
   - Same as architecture (alias)

4. **System Monitoring** - http://localhost:3001/monitoring
   - Component: SystemMonitor
   - Resources, alerts, logs

5. **Configuration** - http://localhost:3001/config
   - Component: SystemConfigManager
   - Platform settings

6. **Users** - http://localhost:3001/users
   - Component: UserManager
   - User administration

7. **Metrics** - http://localhost:3001/metrics
   - Same as monitoring (alias)

---

## 🔧 Development Commands

```bash
# In /Users/MD/AI-Platform-ISO/infrastructure/web-ui-react/

# Start dev server (already running)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint

# Type checking
npm run type-check
```

---

## 📝 Next Steps

### Priority 1: API Integration
Connect components to real AI Platform services:

**Example - Get Platform Health:**
```typescript
import { getPlatformHealth } from '@/services/platform';

const health = await getPlatformHealth();
console.log(`${health.healthy}/${health.total_services} services healthy`);
```

**Example - Get Insights from Analytics:**
```typescript
import { analyticsAPI } from '@/services/platform';

const insights = await analyticsAPI.getInsights();
insights.forEach(insight => {
  console.log(`[${insight.severity}] ${insight.message}`);
});
```

### Priority 2: Update Components
Replace mock data in:
1. RealDataDashboard - Connect to analytics API
2. CentralizedArchitectureMonitor - Use getPlatformHealth()
3. SystemMonitor - Integrate Prometheus metrics

### Priority 3: Add New Features
Create new dashboards:
- AI Services Dashboard
- Workflow Visualization
- Community Insights
- Predictive Analytics

---

## 🎨 UI Component Usage

### Import Components
```typescript
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Settings, BarChart, Users } from 'lucide-react';
```

### Build Layouts
```tsx
<Card className="w-full">
  <CardHeader>
    <CardTitle className="flex items-center gap-2">
      <BarChart className="w-5 h-5" />
      Platform Metrics
    </CardTitle>
  </CardHeader>
  <CardContent>
    {/* Your content */}
  </CardContent>
</Card>
```

---

## 📊 Service Integration Example

**Real implementation example:**

```typescript
// src/hooks/usePlatformHealth.ts
import { useQuery } from '@tanstack/react-query';
import { getPlatformHealth } from '@/services/platform';

export const usePlatformHealth = () => {
  return useQuery({
    queryKey: ['platform-health'],
    queryFn: getPlatformHealth,
    refetchInterval: 30000, // Refetch every 30s
    retry: 2,
  });
};

// In component:
import { usePlatformHealth } from '@/hooks/usePlatformHealth';

function Dashboard() {
  const { data, isLoading, error } = usePlatformHealth();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading health data</div>;

  return (
    <div>
      <h2>{data.healthy}/{data.total_services} Services Healthy</h2>
      {data.services.map(service => (
        <ServiceCard key={service.service} {...service} />
      ))}
    </div>
  );
}
```

---

## 🔍 File Locations

**Key files you'll work with:**

```
infrastructure/web-ui-react/
├── src/
│   ├── App.tsx                    # Router configuration
│   ├── services/
│   │   └── platform.ts           # ✨ API service layer
│   ├── components/
│   │   ├── RealDataDashboard.tsx
│   │   └── ...
│   └── hooks/
│       └── (create custom hooks here)
├── vite.config.ts                # Vite configuration
├── package.json                  # Dependencies
├── README.md                     # Full documentation
├── MIGRATION_COMPLETE.md         # Migration report
└── QUICK_START.md                # This file
```

---

## 🌐 Browser Access

1. **Open browser:** http://localhost:3001
2. **Navigate routes** using the sidebar/menu (if implemented)
3. **Check browser console** for any errors
4. **Open DevTools Network tab** to see API calls

---

## ⚠️ Troubleshooting

**Issue: Blank page**
- Check browser console for errors
- Verify all services are running (ports 8000, 8003, etc.)
- Check terminal for Vite errors

**Issue: API errors**
- Ensure backend services are running:
  ```bash
  # Check if services are up
  curl http://localhost:8000/health
  curl http://localhost:8051/health
  ```

**Issue: Port 3001 in use**
```bash
# Find process
lsof -i :3001

# Kill it
kill -9 <PID>

# Or change port in vite.config.ts
```

---

## 📚 Documentation

- **Full README:** [README.md](./README.md)
- **Migration Report:** [MIGRATION_COMPLETE.md](./MIGRATION_COMPLETE.md)
- **Platform Analysis:** [../tools/analyzers/reports/PLATFORM_ANALYSIS_FOR_ADMIN_PANEL.md](../tools/analyzers/reports/PLATFORM_ANALYSIS_FOR_ADMIN_PANEL.md)

---

## ✨ What Makes This Special

1. **Professional Enterprise Stack** - React 18, TypeScript, Tailwind, Shadcn/ui
2. **Complete API Layer** - TypeScript clients for all 7 AI services
3. **Optimized Build** - Code splitting, tree shaking, lazy loading
4. **Real-time Ready** - WebSocket integration prepared
5. **Type Safety** - Full TypeScript coverage
6. **Modern Tooling** - Vite for instant HMR, Tanstack Query for data

---

**🎉 You're ready to start building!**

Open http://localhost:3001 and start connecting components to the AI Platform services.
