# Advanced Analytics Dashboard - Implementation Guide

## 🎯 Обзор

Данный документ описывает реализацию продвинутой панели аналитики для BCM платформы с real-time мониторингом, включая архитектуру, технические детали и инструкции по развертыванию.

## 🏗️ Архитектура системы

### Компоненты архитектуры:

```
┌─────────────────────────────────────────────────────────────┐
│                      BCM Analytics Platform                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Real-time     │
│   (React 18)    │◄──►│   (FastAPI)     │◄──►│   (Socket.io)   │
│   Port: 3003    │    │   Port: 8888    │    │   Port: 8889    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ • Recharts      │    │ • Rate Limiting │    │ • Broadcasting  │
│ • Real-time UI  │    │ • Analytics API │    │ • Live Metrics  │
│ • RBAC          │    │ • Validation    │    │ • Notifications │
│ • Responsive    │    │ • CORS          │    │ • Health Checks │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📊 Frontend Implementation

### Технологический стек:
- **React 18** с TypeScript
- **Vite** для быстрой разработки
- **Recharts** для интерактивных графиков
- **Tailwind CSS** для стилизации
- **shadcn/ui** компоненты
- **Socket.io-client** для real-time подключения

### Ключевые компоненты:

#### 1. Analytics Dashboard (`src/pages/Analytics.tsx`)
```typescript
export const Analytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState('24h');
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData>({...});
  const { metrics, isConnected } = useRealtime();

  // Real-time updates
  useEffect(() => {
    if (metrics) {
      setAnalyticsData(prev => ({
        ...prev,
        performance: [...prev.performance.slice(-29), newMetric]
      }));
    }
  }, [metrics]);

  return (
    <Tabs defaultValue="performance">
      <TabsContent value="performance">
        <ResponsiveContainer width="100%" height={350}>
          <AreaChart data={analyticsData.performance}>
            <Area type="monotone" dataKey="value" />
          </AreaChart>
        </ResponsiveContainer>
      </TabsContent>
    </Tabs>
  );
};
```

#### 2. Real-time Hook (`src/hooks/useRealtime.ts`)
```typescript
export const useRealtime = (): UseRealtimeReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const [metrics, setMetrics] = useState<MetricsData | null>(null);

  useEffect(() => {
    realtimeService.connect();

    realtimeService.onMetrics((data: MetricsData) => {
      setMetrics(data);
    });

    return () => realtimeService.disconnect();
  }, []);

  return { isConnected, metrics, organisms, notifications };
};
```

#### 3. Authentication Context (`src/contexts/AuthContext.tsx`)
```typescript
export enum UserRole {
  ADMIN = 'admin',
  MANAGER = 'manager',
  ANALYST = 'analyst',
  VIEWER = 'viewer'
}

export const AuthProvider: React.FC = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const hasRole = (role: UserRole | UserRole[]): boolean => {
    if (!user) return false;
    const roles = Array.isArray(role) ? role : [role];
    return roles.includes(user.role);
  };

  return (
    <AuthContext.Provider value={{ user, hasRole, checkPermission }}>
      {children}
    </AuthContext.Provider>
  );
};
```

#### 4. Protected Routes (`src/components/ProtectedRoute.tsx`)
```typescript
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
  requiredPermission
}) => {
  const { isAuthenticated, hasRole, checkPermission } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  if (requiredRole && !hasRole(requiredRole)) {
    return <AccessDenied />;
  }

  return <>{children}</>;
};
```

### Конфигурация Vite:

#### Code Splitting (`vite.config.ts`)
```typescript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          if (id.includes('recharts')) return 'charts';
          if (id.includes('socket.io-client')) return 'realtime';
          if (id.includes('react')) return 'react-vendor';
          return 'vendor';
        }
      }
    },
    optimizeDeps: {
      include: ['react', 'react-dom', 'socket.io-client']
    }
  }
});
```

## 🔌 API Gateway Implementation

### Технологический стек:
- **FastAPI** с асинхронной поддержкой
- **Rate Limiting** middleware
- **CORS** для cross-origin запросов
- **Pydantic** для валидации данных

### Ключевые эндпоинты:

#### 1. Analytics Data API
```python
@app.get("/analytics/data")
async def get_analytics_data(time_range: str = "24h"):
    """Get analytics data for specified time range"""
    # Generate time series data based on range
    points = 30
    if time_range == "1h":
        time_delta = timedelta(minutes=2)
    elif time_range == "24h":
        time_delta = timedelta(hours=0.8)

    return {
        "performance": generate_series(65, 25),
        "incidents": [...],
        "compliance": generate_series(85, 10),
        "risks": [...],
        "training": generate_series(75, 15)
    }
```

#### 2. Rate Limiting Middleware
```python
class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > now - self.window_seconds
        ]

        if len(self.requests[client_id]) >= self.max_requests:
            return False

        self.requests[client_id].append(now)
        return True

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_id = request.client.host

    if not rate_limiter.is_allowed(client_id):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"},
            headers={"Retry-After": "60"}
        )

    return await call_next(request)
```

## 📡 Real-time Server Implementation

### Socket.io Server (`socketio_server.js`)
```javascript
const io = new Server(server, {
  cors: {
    origin: ["http://localhost:3000", "http://localhost:3003"],
    methods: ["GET", "POST"]
  }
});

function broadcast(topic, event, data) {
  io.to(topic).emit(event, {
    ...data,
    timestamp: new Date().toISOString(),
    topic: topic
  });
}

// Broadcast metrics every 5 seconds
setInterval(() => {
  const metrics = generateMetrics();
  broadcast('metrics', 'metrics:update', metrics);
}, 5000);

// Broadcast AI organisms status every 10 seconds
setInterval(() => {
  const organisms = generateOrganismsData();
  broadcast('organisms', 'organisms:update', organisms);
}, 10000);
```

### Real-time Service (`src/services/realtime.ts`)
```typescript
class RealtimeService {
  private socket: Socket | null = null;

  connect() {
    this.socket = io(SOCKET_URL);

    this.socket.on('connect', () => {
      console.log('Connected to real-time server');
    });
  }

  onMetrics(callback: (data: MetricsData) => void) {
    this.socket?.on('metrics:update', callback);
  }

  subscribe(topic: string) {
    this.socket?.emit('subscribe', { topic });
  }

  disconnect() {
    this.socket?.disconnect();
  }
}

export const realtimeService = new RealtimeService();
```

## 🔐 Security Implementation

### 1. Zod Validation Schemas (`src/lib/validations.ts`)
```typescript
export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Must contain uppercase letter')
    .regex(/[0-9]/, 'Must contain number')
});

export const userSchema = z.object({
  id: z.string().uuid().optional(),
  email: z.string().email(),
  role: z.enum(['admin', 'manager', 'analyst', 'viewer']),
  permissions: z.array(z.string()).default([])
});

export function validateData<T>(schema: z.ZodSchema<T>, data: unknown): T {
  return schema.parse(data);
}
```

### 2. Role-Based Access Control
```typescript
// Permission definitions
export const PERMISSIONS = {
  VIEW_ANALYTICS: 'analytics:view',
  EXPORT_DATA: 'analytics:export',
  MANAGE_USERS: 'users:manage',
  SYSTEM_CONTROL: 'system:control'
} as const;

// Role permissions mapping
export const ROLE_PERMISSIONS = {
  [UserRole.ADMIN]: Object.values(PERMISSIONS),
  [UserRole.MANAGER]: [
    PERMISSIONS.VIEW_ANALYTICS,
    PERMISSIONS.EXPORT_DATA
  ],
  [UserRole.ANALYST]: [
    PERMISSIONS.VIEW_ANALYTICS
  ],
  [UserRole.VIEWER]: []
};
```

## 🚀 Performance Optimization

### 1. Code Splitting Strategy
```typescript
// Dynamic imports for heavy components
const AdvancedCharts = lazy(() => import('@/components/AdvancedCharts'));
const DataExporter = lazy(() => import('@/components/DataExporter'));

// Chunk optimization
const manualChunks = {
  'react-vendor': ['react', 'react-dom'],
  'charts': ['recharts'],
  'realtime': ['socket.io-client'],
  'ui-vendor': ['@radix-ui', 'class-variance-authority']
};
```

### 2. Мемоизация и оптимизация
```typescript
// Мемоизация дорогих вычислений
const systemHealth = useMemo(() => {
  if (!metrics) return 0;
  return calculateSystemHealth(metrics);
}, [metrics]);

// Debounced search
const debouncedSearch = useDebounce(searchQuery, 300);

// Virtual scrolling для больших списков
const VirtualizedList = memo(({ items }: { items: any[] }) => {
  return (
    <FixedSizeList
      height={400}
      itemCount={items.length}
      itemSize={50}
    >
      {({ index, style }) => (
        <div style={style}>
          {items[index]}
        </div>
      )}
    </FixedSizeList>
  );
});
```

## 📦 Deployment Guide

### Развертывание в production:

#### 1. Build Frontend
```bash
cd frontend/admin_panel
npm run build
# Статические файлы в dist/
```

#### 2. API Gateway Setup
```bash
cd api
pip install -r requirements.txt
python3 simple_gateway.py
# Или через Docker
docker build -t bcm-gateway .
docker run -p 8888:8888 bcm-gateway
```

#### 3. Socket.io Server Setup
```bash
cd api
npm install
node socketio_server.js
# Или через PM2
pm2 start socketio_server.js --name="bcm-realtime"
```

#### 4. Nginx Configuration
```nginx
server {
    listen 80;
    server_name analytics.bcm.local;

    location / {
        root /var/www/analytics/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8888/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /socket.io/ {
        proxy_pass http://localhost:8889/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 🔧 Environment Variables

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8888
VITE_SOCKETIO_URL=http://localhost:8889
VITE_APP_TITLE=BCM Analytics Dashboard
VITE_ENABLE_REAL_TIME=true
VITE_DEBUG_MODE=false
```

### API Gateway (.env)
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:3003
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
DATABASE_URL=postgresql://user:pass@localhost/bcm
REDIS_URL=redis://localhost:6379
```

## 📈 Monitoring & Logging

### Application Metrics
```typescript
// Frontend performance monitoring
const performanceObserver = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.entryType === 'navigation') {
      analytics.track('page_load_time', {
        duration: entry.duration,
        page: window.location.pathname
      });
    }
  }
});

performanceObserver.observe({ entryTypes: ['navigation', 'resource'] });
```

### API Gateway Logging
```python
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api_gateway.log'),
        logging.StreamHandler()
    ]
)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} - "
        f"{response.status_code} - {process_time:.3f}s"
    )

    return response
```

## 🧪 Testing Strategy

### Frontend Testing
```typescript
// Component tests with React Testing Library
import { render, screen, waitFor } from '@testing-library/react';
import { Analytics } from '@/pages/Analytics';

test('renders analytics dashboard', async () => {
  render(<Analytics />);

  expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();

  await waitFor(() => {
    expect(screen.getByText('System Health')).toBeInTheDocument();
  });
});

// Real-time functionality tests
test('updates metrics in real-time', async () => {
  const mockSocket = new MockSocket();
  render(<Analytics />);

  mockSocket.emit('metrics:update', { cpu: 75, memory: 60 });

  await waitFor(() => {
    expect(screen.getByText('75%')).toBeInTheDocument();
  });
});
```

### API Testing
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_analytics_endpoint():
    response = client.get("/analytics/data?time_range=24h")
    assert response.status_code == 200
    data = response.json()
    assert "performance" in data
    assert "incidents" in data
    assert len(data["performance"]) == 30

def test_rate_limiting():
    # Make 101 requests quickly
    for i in range(101):
        response = client.get("/analytics/data")
        if i < 100:
            assert response.status_code == 200
        else:
            assert response.status_code == 429
```

## 🔄 Future Enhancements

### Планируемые улучшения:
1. **Machine Learning Analytics** - предиктивная аналитика
2. **Custom Dashboards** - пользовательские панели
3. **Advanced Filtering** - сложные фильтры данных
4. **Mobile App** - мобильное приложение
5. **Report Generation** - автоматическая генерация отчетов
6. **Integration APIs** - интеграция с внешними системами

---

**Документ обновлен**: Сентябрь 2025
**Версия**: 1.0
**Автор**: BCM Development Team