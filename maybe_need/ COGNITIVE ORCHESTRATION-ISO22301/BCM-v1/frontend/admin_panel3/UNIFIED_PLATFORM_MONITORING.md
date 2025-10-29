# 📊 **UNIFIED PLATFORM MONITORING INTEGRATION**

## **🎯 ПЛАН ИНТЕГРАЦИИ МОНИТОРИНГА**

### **1️⃣ ДОБАВИТЬ В ADMIN PANEL:**

#### **SystemMonitor.tsx - расширить для Unified Platform**
```typescript
// Добавить в компонент мониторинга:
const unifiedPlatformMetrics = {
  // URL: http://localhost:3002 (Unified Platform)
  url: 'http://localhost:3002',
  name: 'Unified BCM Platform',
  status: 'active',
  
  // Метрики для отслеживания:
  sections: [
    { name: 'Risk Assessment', users: 45, uptime: '99.8%' },
    { name: 'AI Automation', users: 32, uptime: '99.9%' },
    { name: 'Analytics', users: 28, uptime: '100%' },
    { name: 'Incident Management', users: 15, uptime: '99.7%' },
    { name: 'Strategy Planning', users: 22, uptime: '99.9%' },
    { name: 'My Workspace', users: 89, uptime: '100%' }
  ],
  
  // Real-time данные:
  activeUsers: 156,
  totalSessions: 1247,
  avgResponseTime: '245ms',
  errorRate: '0.02%'
}
```

### **2️⃣ API ENDPOINTS ДЛЯ МОНИТОРИНГА:**

#### **В Unified Platform добавить API:**
```typescript
// app/api/health/route.ts - health check
export async function GET() {
  return Response.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    sections: {
      'risk-assessment': { status: 'up', users: 45 },
      'ai-automation': { status: 'up', users: 32 },
      'analytics': { status: 'up', users: 28 },
      'incident-management': { status: 'up', users: 15 },
      'strategy-planning': { status: 'up', users: 22 },
      'workspace': { status: 'up', users: 89 }
    }
  })
}

// app/api/metrics/route.ts - detailed metrics
export async function GET() {
  return Response.json({
    performance: {
      avgResponseTime: '245ms',
      errorRate: '0.02%',
      uptime: '99.9%'
    },
    usage: {
      activeUsers: 156,
      totalSessions: 1247,
      pageViews: 8945
    }
  })
}
```

### **3️⃣ ВИЗУАЛИЗАЦИЯ В ADMIN PANEL:**

#### **Dashboard Card для Unified Platform:**
```typescript
// components/UnifiedPlatformMonitor.tsx
export function UnifiedPlatformMonitor() {
  return (
    <Card className="col-span-2">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Building2 className="h-5 w-5 text-blue-600" />
          <CardTitle>Unified BCM Platform</CardTitle>
          <Badge className="bg-green-100 text-green-800">
            <Circle className="h-2 w-2 mr-1 fill-current" />
            Active
          </Badge>
        </div>
        <CardDescription>
          Main business portal - http://localhost:3002
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Real-time metrics grid */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <MetricCard 
            label="Active Users" 
            value="156" 
            trend="+12%" 
            color="blue" 
          />
          <MetricCard 
            label="Response Time" 
            value="245ms" 
            trend="-5%" 
            color="green" 
          />
          <MetricCard 
            label="Error Rate" 
            value="0.02%" 
            trend="0%" 
            color="green" 
          />
          <MetricCard 
            label="Uptime" 
            value="99.9%" 
            trend="+0.1%" 
            color="green" 
          />
        </div>
        
        {/* Sections status */}
        <div className="space-y-2">
          <h4 className="font-medium mb-3">Section Status</h4>
          {sections.map(section => (
            <div key={section.name} className="flex items-center justify-between p-2 bg-gray-50 rounded">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 bg-green-500 rounded-full" />
                <span className="text-sm">{section.name}</span>
              </div>
              <div className="text-xs text-gray-600">
                {section.users} users • {section.uptime} uptime
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
```

### **4️⃣ REAL-TIME UPDATES:**

#### **WebSocket для live данных:**
```typescript
// hooks/useUnifiedPlatformMetrics.ts
export function useUnifiedPlatformMetrics() {
  const [metrics, setMetrics] = useState(null)
  
  useEffect(() => {
    // Polling каждые 30 секунд
    const interval = setInterval(async () => {
      try {
        const response = await fetch('http://localhost:3002/api/health')
        const data = await response.json()
        setMetrics(data)
      } catch (error) {
        console.error('Failed to fetch metrics:', error)
      }
    }, 30000)
    
    return () => clearInterval(interval)
  }, [])
  
  return metrics
}
```

### **5️⃣ ALERTS И NOTIFICATIONS:**

#### **Система уведомлений:**
```typescript
// Добавить в SystemMonitor.tsx
const alertRules = [
  { 
    condition: 'errorRate > 1%', 
    severity: 'high',
    message: 'High error rate detected in Unified Platform'
  },
  { 
    condition: 'responseTime > 1000ms', 
    severity: 'medium',
    message: 'Slow response time in Unified Platform'
  },
  { 
    condition: 'activeUsers < 10', 
    severity: 'low',
    message: 'Low user activity in Unified Platform'
  }
]
```

## **🎯 РЕЗУЛЬТАТ ИНТЕГРАЦИИ:**

### **Админ панель будет показывать:**
- ✅ **Real-time статус** всех 12 разделов Unified Platform
- ✅ **User activity** по каждому разделу
- ✅ **Performance metrics** (response time, errors, uptime)
- ✅ **Health checks** с автоматическими alerts
- ✅ **Traffic analytics** (page views, sessions, users)

### **Практические benefits:**
- **Centralized monitoring** - один dashboards для всех платформ
- **Proactive alerts** - уведомления о проблемах до их критичности  
- **Usage insights** - понимание использования разделов
- **Performance tracking** - optimization opportunities
- **System health** - overall ecosystem visibility

**ГОТОВ РЕАЛИЗОВАТЬ ИНТЕГРАЦИЮ! 🚀**