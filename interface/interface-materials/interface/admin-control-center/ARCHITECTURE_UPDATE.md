# BCM Admin Panel - Architecture Update

## 🆕 What's New: Centralized Architecture Monitor

Добавлен новый раздел **Centralized Architecture Monitor** (`/architecture`) для полного контроля над централизованной архитектурой BCM Platform.

## 🚀 New Features

### 1. Real-time System Monitoring
- **Service Health**: Мониторинг всех 18+ сервисов в реальном времени
- **Response Times**: Отслеживание производительности каждого сервиса
- **Status Indicators**: Визуальные индикаторы состояния (healthy/degraded/unhealthy)

### 2. Event Bus Control Center
- **Live Statistics**: Размер очереди, количество handlers, статус
- **Event Testing**: Кнопки для тестирования различных типов событий
- **Handler Monitoring**: Отслеживание активных обработчиков событий

### 3. Architecture Overview
- **Visual Diagram**: Схема всей централизованной архитектуры
- **Service Breakdown**: Разбивка по слоям (Frontend, API, Core, Infrastructure)
- **Key Features**: Список реализованных возможностей

### 4. Complete API Documentation
- **Endpoint Reference**: Полный список API всех сервисов
- **Code Examples**: Примеры интеграции для разработчиков
- **Integration Guide**: Пошаговые инструкции

## 🔧 How to Access

### Via Navigation
1. Запустите admin panel: `npm run dev`
2. Откройте браузер: `http://localhost:3001`
3. Перейдите на `/architecture`

### Direct URL
```
http://localhost:3001/architecture
```

## 📊 Dashboard Sections

### Services Tab
- Grid view всех сервисов
- Real-time status updates каждые 30 секунд
- Response time metrics
- Last updated timestamps

### Event Bus Tab
- **Status Panel**: Общая информация о Event Bus
- **Test Controls**: Кнопки для тестирования событий:
  - `project-won` - Триггер выигрыша проекта
  - `audit-completed` - Завершение аудита
  - `incident-critical` - Критический инцидент

### Architecture Tab
- **Service Architecture**: Визуальная схема по слоям
- **Key Features**: Список реализованных возможностей
- **Benefits**: Преимущества централизованной архитектуры

### Documentation Tab
- **API Reference**: Документация всех endpoints
- **Integration Examples**: Примеры кода для TypeScript
- **Implementation Guide**: Инструкции по использованию

## 🔌 Integration with Centralized Services

### Automatic Fallbacks
Компонент автоматически определяет доступность сервисов:

1. **Primary**: Использует Monitoring Service (8779) если доступен
2. **Fallback**: Проверяет сервисы напрямую если monitoring недоступен
3. **Graceful Degradation**: Показывает базовую информацию при любых условиях

### Service Discovery
```typescript
// Автоматическая проверка core сервисов
const coreServices = {
  'database_gateway': 'http://localhost:8888/health',
  'api_gateway': 'http://localhost:8777/health',
  'crm_bridge': 'http://localhost:8778/health',
  'monitoring_service': 'http://localhost:8779/health'
};
```

## 📝 Event Testing Features

### Available Test Events

#### 1. Project Won Event
```typescript
// Симулирует выигрыш проекта в CRM
{
  project_id: 999,
  partner_name: "Test Organization",
  industry: "finance",
  employee_count: 500,
  compliance_target: "iso_22301"
}
```

#### 2. Audit Completed Event
```typescript
// Симулирует завершение аудита
{
  project_id: 999,
  audit_id: 456,
  compliance_score: 85,
  findings: [...]
}
```

#### 3. Critical Incident Event
```typescript
// Симулирует критический инцидент
{
  project_id: 999,
  incident_id: 789,
  title: "Test Event from Admin Panel",
  severity: "critical"
}
```

### Real-time Feedback
- ✅ Успешные события показывают confirmation
- ❌ Ошибки отображают error messages
- 🔄 Event Bus статистика обновляется автоматически

## 🔍 Monitoring Capabilities

### System-wide Health Check
```typescript
const systemStatus = {
  overall_status: 'healthy',
  services_count: 4,
  healthy_services: 4,
  degraded_services: 0,
  unhealthy_services: 0,
  active_alerts: 0
};
```

### Service-specific Metrics
```typescript
const serviceStatus = {
  name: 'database_gateway',
  status: 'healthy',
  response_time_ms: 45.2,
  last_updated: '2025-09-18T17:15:30Z',
  port: 8888
};
```

## 🎨 UI Components Used

### Shadcn/ui Components
- `Card`, `CardContent`, `CardHeader` - Layout structure
- `Badge` - Status indicators
- `Button` - Interactive controls
- `Tabs` - Section organization
- `Progress` - Loading states
- `Alert` - System notifications

### Lucide Icons
- `Server`, `Database`, `Network` - Infrastructure icons
- `CheckCircle`, `XCircle`, `AlertTriangle` - Status icons
- `Activity`, `BarChart3`, `MessageSquare` - Feature icons
- `Shield`, `Zap` - Action icons

## 🔧 Developer Integration

### Adding to Navigation
```typescript
// In BCMUnifiedWorkspace.tsx or main navigation
<Link to="/architecture">
  <Server className="h-4 w-4" />
  Architecture Monitor
</Link>
```

### Custom Service Integration
```typescript
// Extend service monitoring
const customServices = {
  'your_service': {
    url: 'http://localhost:XXXX/health',
    description: 'Your Service Name',
    port: XXXX
  }
};
```

## 📋 Configuration Options

### Refresh Intervals
```typescript
// Настраиваемые интервалы обновления
const REFRESH_INTERVALS = {
  status: 30000,    // 30 seconds
  services: 30000,  // 30 seconds
  eventBus: 15000,  // 15 seconds
  logs: 60000       // 1 minute
};
```

### Service Ports Reference
```typescript
const SERVICE_PORTS = {
  unified_database_gateway: 8888,
  unified_api_gateway: 8777,
  crm_bridge: 8778,
  monitoring_service: 8779,
  odoo: 8069,
  admin_panel: 3001
};
```

## 🎯 Next Steps

### Planned Enhancements
1. **WebSocket Integration**: Real-time log streaming
2. **Custom Alerts**: User-configurable alert rules
3. **Performance Charts**: Historical metrics visualization
4. **Export Functions**: Status reports and logs export

### Contributing
1. Добавьте новые service checks в `fetchServices()`
2. Расширьте Event Bus тестирование в `triggerTestEvent()`
3. Обновите документацию в Documentation tab
4. Добавьте новые метрики в Monitoring service

---

**🚀 Ready to Monitor Your Centralized BCM Architecture!**

Новый раздел Architecture Monitor предоставляет complete visibility и control над всей централизованной инфраструктурой BCM Platform. Используйте его для:

- 📊 **Real-time monitoring** всех сервисов
- 🔧 **Event testing** и debugging
- 📚 **API documentation** reference
- 🏗️ **Architecture understanding**

Access: `http://localhost:3001/architecture`