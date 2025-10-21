# BCM Platform - Centralized Architecture Guide

## 🏗️ Overview

BCM Platform использует централизованную архитектуру для обеспечения единообразного доступа ко всем сервисам, данным и функциональности. Эта архитектура основана на концепции **единой точки входа** и **event-driven communication**.

## 🔧 Core Components

### 1. 🗄️ Unified Database Gateway (Port 8888)
**Назначение**: Централизованный доступ ко всем базам данных

**Основные функции**:
- Унифицированный API для всех типов БД
- Поддержка Odoo операций (search, read, create, write)
- Аутентификация через Odoo
- Кэширование запросов

**Поддерживаемые БД**:
- PostgreSQL (основная БД Odoo)
- Redis (кэш и очереди)
- MongoDB (документы и аналитика)
- Supabase (внешние интеграции)
- RabbitMQ (сообщения)

**API Endpoints**:
```http
POST /query - Выполнение операций с БД
POST /auth/odoo - Аутентификация Odoo
GET /health - Проверка состояния
GET /databases - Список подключенных БД
```

**Пример использования**:
```typescript
const response = await fetch('http://localhost:8888/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    database: 'odoo',
    operation: 'odoo_search',
    model: 'crm.lead',
    domain: [['active', '=', true]],
    fields: ['name', 'partner_id', 'stage_id']
  })
});
```

### 2. 🌐 Unified API Gateway (Port 8777)
**Назначение**: Роутер для всех backend сервисов

**Основные функции**:
- Service Discovery и Load Balancing
- Проксирование запросов к микросервисам
- Метрики и мониторинг
- Централизованная аутентификация

**Зарегистрированные сервисы** (18+ сервисов):
- **Core**: odoo, ai_orchestrator, database_gateway, crm_bridge
- **BCM Modules**: bia_engine, document_processor, compliance_checker
- **Infrastructure**: prometheus, grafana, rabbitmq
- **Simulation**: scenario_orchestrator, exercise_simulators
- **Development**: module_validator, deployer

**API Pattern**:
```
GET /api/{service_name}/{path}
POST /api/{service_name}/{path}
PUT /api/{service_name}/{path}
DELETE /api/{service_name}/{path}
```

**Примеры**:
```typescript
// Доступ к CRM Bridge
const projects = await fetch('http://localhost:8777/api/crm_bridge/projects');

// Доступ к BIA Engine
const analysis = await fetch('http://localhost:8777/api/bia_engine/analyze', {
  method: 'POST',
  body: JSON.stringify(analysisData)
});

// Проверка состояния сервисов
const services = await fetch('http://localhost:8777/services');
```

### 3. 🔗 CRM Bridge (Port 8778)
**Назначение**: Интеграция Odoo CRM с BCM модулями

**Основные функции**:
- Связь CRM проектов с BCM workspace
- Event Bus для межмодульной коммуникации
- Автоматическое создание BCM структур
- Gamification интеграция

**Event Bus Handlers**:
- **CRM Events**: project.won, project.stage_changed, project.lost
- **Audit Events**: audit.completed, audit.finding_created
- **Incident Events**: incident.critical, incident.resolved
- **Gamification**: content.created, training.completed

**Key Endpoints**:
```http
GET /projects - Список CRM проектов
POST /projects/{id}/workspace - Создание BCM workspace
POST /eventbus/publish - Публикация событий
GET /eventbus/stats - Статистика Event Bus
POST /eventbus/project-won - Триггер события выигрыша проекта
POST /eventbus/audit-completed - Триггер завершения аудита
POST /eventbus/incident-critical - Триггер критического инцидента
```

**Event Publishing Example**:
```typescript
await fetch('http://localhost:8778/eventbus/publish', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    event_type: 'custom.event',
    source_module: 'admin_panel',
    project_id: 123,
    data: {
      message: 'Custom event from admin panel',
      priority: 'high'
    }
  })
});
```

### 4. 📊 Monitoring Service (Port 8779)
**Назначение**: Централизованное логирование и мониторинг

**Основные функции**:
- Real-time мониторинг всех сервисов
- Централизованное логирование
- Система алертов
- WebSocket dashboard

**Endpoints**:
```http
GET /status - Общее состояние системы
GET /services - Состояние всех сервисов
GET /logs - Системные логи
GET /alerts - Активные алерты
GET /dashboard - Web dashboard
WebSocket /ws/realtime - Real-time обновления
```

## 🚀 Event-Driven Architecture

### Event Flow
```
Frontend Action → API Gateway → CRM Bridge → Event Bus → BCM Modules → Database Gateway → Odoo/PostgreSQL
```

### Event Types

#### 1. Project Lifecycle Events
```typescript
// Проект выигран
{
  event_type: 'project.won',
  source_module: 'crm_project',
  project_id: 123,
  data: {
    partner_name: 'Example Corp',
    industry: 'finance',
    employee_count: 500,
    compliance_target: 'iso_22301'
  }
}
```

#### 2. Audit Events
```typescript
// Аудит завершен
{
  event_type: 'audit.completed',
  source_module: 'bcm_audit',
  project_id: 123,
  data: {
    compliance_score: 85,
    findings: [
      {
        title: 'Missing BCP documentation',
        severity: 'high',
        description: 'Business continuity plan not documented'
      }
    ]
  }
}
```

#### 3. Incident Events
```typescript
// Критический инцидент
{
  event_type: 'incident.critical',
  source_module: 'bcm_incident',
  project_id: 123,
  data: {
    title: 'Data Center Power Failure',
    severity: 'critical',
    description: 'Primary data center lost power',
    assigned_to_id: 2
  }
}
```

#### 4. Gamification Events
```typescript
// Контент создан
{
  event_type: 'content.created',
  source_module: 'bcm_content',
  project_id: 123,
  user_id: 5,
  data: {
    content_type: 'template',
    content_id: 42,
    title: 'Emergency Response Template'
  }
}
```

## 🔐 Authentication & Security

### Odoo Authentication
```typescript
// Аутентификация через Database Gateway
const authResponse = await fetch('http://localhost:8888/auth/odoo', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin',
    database: 'bcm_platform'
  })
});

const { session_id, user_id, user_context } = await authResponse.json();
```

### Session Management
- Все запросы к Odoo проходят через единую аутентификацию
- Session ID автоматически управляется gateway'ями
- Контекст пользователя передается между сервисами

## 📝 Frontend Integration

### TypeScript Client (Centralized)
```typescript
// Использование централизованного клиента
import { centralizedClient } from '@/lib/centralized-client';

// Database операции
const leads = await centralizedClient.odoo('search', 'crm.lead', {
  domain: [['stage_id.name', '=', 'Won']],
  fields: ['name', 'partner_id', 'expected_revenue']
});

// Service calls
const projects = await centralizedClient.apiGateway('/api/crm_bridge/projects');

// Event publishing
await centralizedClient.publishEvent({
  event_type: 'user.action',
  source_module: 'admin_panel',
  project_id: projectId,
  data: actionData
});
```

### React Integration
```typescript
// Хук для мониторинга сервисов
const useServiceStatus = () => {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    const fetchStatus = async () => {
      const response = await fetch('http://localhost:8779/status');
      setStatus(await response.json());
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return status;
};

// Компонент с real-time обновлениями
const SystemMonitor = () => {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8779/ws/realtime');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'log') {
        setLogs(prev => [data.data, ...prev.slice(0, 99)]);
      }
    };

    return () => ws.close();
  }, []);

  return <LogDisplay logs={logs} />;
};
```

## 🔄 Data Flow Patterns

### 1. Create BCM Workspace (Project Won)
```
1. CRM Lead marked as "Won"
2. Event: project.won published
3. CRM Handler creates:
   - bcm.context (organization setup)
   - bcm.audit (initial assessment scheduled)
   - bcm.plan (implementation plan)
   - bcm.training (awareness session scheduled)
4. Response: workspace_id returned
```

### 2. Audit Completion Flow
```
1. Audit completed in BCM module
2. Event: audit.completed published
3. Audit Handler:
   - Updates CRM with compliance score
   - Creates action items for findings
   - Triggers notifications
4. CRM updated with latest assessment
```

### 3. Critical Incident Escalation
```
1. Critical incident detected
2. Event: incident.critical published
3. Incident Handler:
   - Creates CRM activity
   - Sets project priority to "High"
   - Sends notifications to stakeholders
4. CRM reflects incident status
```

## 📊 Monitoring & Metrics

### Service Health Metrics
- **Response Time**: латентность запросов
- **Availability**: процент времени работы
- **Error Rate**: количество ошибок
- **Throughput**: количество запросов в секунду

### Event Bus Metrics
- **Queue Size**: количество событий в очереди
- **Processing Time**: время обработки событий
- **Handler Status**: состояние обработчиков
- **Event Types**: распределение типов событий

### Database Metrics
- **Connection Pool**: использование соединений
- **Query Performance**: производительность запросов
- **Cache Hit Rate**: эффективность кэширования
- **Storage Usage**: использование дискового пространства

## 🚀 Deployment

### Docker Compose Services
```yaml
services:
  unified_database_gateway:
    ports: ["8888:8888"]

  unified_api_gateway:
    ports: ["8777:8777"]

  crm_bridge:
    ports: ["8778:8778"]

  monitoring_service:
    ports: ["8779:8779"]
```

### Environment Variables
```bash
# Database connections
POSTGRES_URL=postgresql://odoo:postgres123@postgres:5432/bcm_platform
REDIS_URL=redis://redis:6379
MONGODB_URL=mongodb://mongo:27017

# Service URLs (Docker hostnames)
ODOO_API_URL=http://odoo:8069
DATABASE_GATEWAY_URL=http://unified_database_gateway:8888
API_GATEWAY_URL=http://unified_api_gateway:8777

# Monitoring
LOG_DIR=/app/logs
METRICS_RETENTION_HOURS=24
```

## 🔧 Development Guide

### Adding New Service to API Gateway
```python
# In unified_api_gateway/main.py
SERVICE_REGISTRY = {
    "your_service": {
        "url": "http://your_service:port",
        "health": "/health",
        "description": "Your Service Description"
    }
}
```

### Creating Event Handler
```python
# In crm_bridge/event_bus.py
class YourEventHandler(BcmEventHandler):
    async def handle_event(self, event: BcmEvent) -> bool:
        if event.event_type == "your.event":
            return await self._process_your_event(event)
        return True

    async def _process_your_event(self, event: BcmEvent) -> bool:
        # Your event processing logic
        pass

# Register handler
self.handlers["your_module"] = YourEventHandler(odoo_api_url, db_gateway_url)
```

### Database Operations
```python
# Using Database Gateway
query_data = {
    "database": "odoo",
    "operation": "odoo_search",
    "model": "your.model",
    "domain": [["field", "=", "value"]],
    "fields": ["field1", "field2"]
}

response = await client.post(f"{Config.DATABASE_GATEWAY_URL}/query", json=query_data)
```

## 📋 Testing

### Health Checks
```bash
# Check all services
curl http://localhost:8777/services

# Check specific service
curl http://localhost:8888/health
curl http://localhost:8778/health
curl http://localhost:8779/health

# Test Event Bus
curl -X POST http://localhost:8778/eventbus/project-won \
  -H "Content-Type: application/json" \
  -d '{"project_id": 123, "partner_name": "Test Company"}'
```

### Integration Test Script
```python
# test_integration.py - Already included in project
python3 test_integration.py
```

## 🔍 Troubleshooting

### Common Issues

1. **Service Unavailable (502/503)**
   - Check if service is running: `docker ps`
   - Check service logs: `docker logs <service_name>`
   - Verify service registry in API Gateway

2. **Database Connection Errors**
   - Verify database URLs in environment
   - Check PostgreSQL/Redis connectivity
   - Review authentication credentials

3. **Event Bus Not Processing**
   - Check Event Bus stats: `GET /eventbus/stats`
   - Verify handler registration
   - Check queue size and processing status

4. **Authentication Issues**
   - Verify Odoo session validity
   - Check database name configuration
   - Review user permissions in Odoo

### Debugging Tools
```bash
# Service logs
docker logs unified_api_gateway
docker logs crm_bridge
docker logs monitoring_service

# Database connectivity
docker exec -it postgres psql -U odoo -d bcm_platform

# Redis status
docker exec -it redis redis-cli ping
```

## 📚 API Reference

### Complete Endpoint List

#### Database Gateway (8888)
- `POST /query` - Execute database operations
- `POST /auth/odoo` - Odoo authentication
- `GET /health` - Health check
- `GET /databases` - List databases

#### API Gateway (8777)
- `GET /api/{service}/{path}` - Proxy to service
- `GET /services` - Service registry
- `GET /health` - Health check
- `GET /metrics` - Gateway metrics

#### CRM Bridge (8778)
- `GET /projects` - List CRM projects
- `POST /projects/{id}/workspace` - Create BCM workspace
- `POST /eventbus/publish` - Publish event
- `GET /eventbus/stats` - Event Bus statistics
- `POST /eventbus/project-won` - Project won event
- `POST /eventbus/audit-completed` - Audit completed event
- `POST /eventbus/incident-critical` - Critical incident event

#### Monitoring Service (8779)
- `GET /status` - System status
- `GET /services` - Services health
- `GET /logs` - System logs
- `GET /alerts` - Active alerts
- `GET /dashboard` - Web dashboard
- `WebSocket /ws/realtime` - Real-time updates

---

## 🎯 Next Steps

1. **Performance Optimization**
   - Implement caching strategies
   - Add request rate limiting
   - Optimize database queries

2. **Enhanced Security**
   - API key authentication
   - Role-based access control
   - Request encryption

3. **Advanced Monitoring**
   - Custom metrics collection
   - Alerting rules
   - Performance dashboards

4. **Documentation**
   - OpenAPI specifications
   - Integration examples
   - Video tutorials

---

**Developed for BCM Platform • Centralized Architecture v1.0**