# BCM REST API Examples

Этот документ содержит примеры использования созданных REST API эндпоинтов для всех BCM модулей в Odoo.

## Базовая информация

- **Базовый URL**: `http://localhost:8069`
- **Формат ответа**: JSON с структурой `{"success": true/false, "data": [...], "total": N, "message": "..."}`
- **Аутентификация**: `auth='user'` - требуется аутентификация пользователя
- **CORS**: поддерживается (`cors='*'`)

## Эндпоинты API

### 1. BCM Modules API

#### Получить все BCM модули
```bash
curl -X POST "http://localhost:8069/api/bcm/modules" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "limit": 50,
      "offset": 0,
      "state": "installed"
    },
    "id": 1
  }'
```

**Параметры:**
- `state`: фильтр по состоянию (`installed`, `to upgrade`, etc.)
- `limit`: лимит записей (по умолчанию 50)
- `offset`: смещение для пагинации

**Пример ответа:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "bcm_core",
      "display_name": "BCM Core",
      "shortdesc": "Business Continuity Management Core",
      "state": "installed",
      "category": "Business Continuity",
      "version": "1.0.0",
      "author": "BCM Team"
    }
  ],
  "total": 22
}
```

### 2. Clients API

#### Получить всех клиентов
```bash
curl -X POST "http://localhost:8069/api/clients" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "limit": 25,
      "offset": 0
    },
    "id": 1
  }'
```

#### Фильтрация клиентов
```bash
curl -X POST "http://localhost:8069/api/clients" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "sector": "hospital",
      "status": "active",
      "region": "Europe",
      "search": "Medical Center"
    },
    "id": 1
  }'
```

**Параметры:**
- `sector`: фильтр по сектору (`hospital`, `public`, `lab`, `private`, etc.)
- `status`: фильтр по статусу (`active`, `suspended`, `archived`, `onboarding`)
- `region`: фильтр по региону
- `search`: поиск по названию
- `limit`, `offset`: пагинация

#### Получить детали клиента
```bash
curl -X POST "http://localhost:8069/api/clients/1" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {},
    "id": 1
  }'
```

**Пример ответа:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Regional Medical Center",
    "sector": "hospital",
    "status": "active",
    "contacts": [
      {
        "id": 1,
        "name": "Dr. Smith",
        "email": "smith@medical.com",
        "role": "BCM Coordinator"
      }
    ],
    "metrics": {
      "contact_count": 5,
      "plan_count": 12,
      "incident_count": 3,
      "bia_coverage": 85.5
    }
  }
}
```

### 3. Scenarios API

#### Получить все сценарии
```bash
curl -X POST "http://localhost:8069/api/scenarios" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "limit": 20,
      "offset": 0
    },
    "id": 1
  }'
```

#### Фильтрация сценариев
```bash
curl -X POST "http://localhost:8069/api/scenarios" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "category": "cyber",
      "level": "tabletop",
      "status": "published",
      "search": "ransomware",
      "rating_min": 4.0,
      "tags": "security,incident"
    },
    "id": 1
  }'
```

**Параметры:**
- `category`: категория (`epidemic`, `blackout`, `cyber`, `supply`, `natural`, etc.)
- `level`: уровень (`tabletop`, `full`)
- `status`: статус (`draft`, `pending_review`, `published`, `rejected`)
- `visibility`: видимость (`public`, `private`, `client_only`)
- `search`: поиск по названию и контенту
- `tags`: фильтр по тегам (через запятую)
- `rating_min`: минимальный рейтинг

#### Получить детали сценария
```bash
curl -X POST "http://localhost:8069/api/scenarios/1" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {},
    "id": 1
  }'
```

### 4. Dashboard API

#### Общий дашборд
```bash
curl -X POST "http://localhost:8069/api/dashboard/overview" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {},
    "id": 1
  }'
```

#### Дашборд инцидентов
```bash
curl -X POST "http://localhost:8069/api/dashboard/incidents" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {},
    "id": 1
  }'
```

**Доступные типы дашбордов:**
- `overview`: общий обзор BCM
- `incidents`: дашборд инцидентов
- `risk`: дашборд рисков
- `plans`: дашборд планов
- `kpi`: дашборд KPI
- `clients`: дашборд клиентов

**Пример ответа (overview):**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_clients": 15,
      "total_incidents": 8,
      "active_incidents": 2,
      "total_plans": 45,
      "total_scenarios": 23
    },
    "recent_activity": [
      {
        "type": "incident",
        "title": "New incident: Server Outage",
        "date": "2024-09-15T10:30:00Z",
        "severity": "high"
      }
    ],
    "alerts": [
      {
        "type": "warning",
        "title": "2 active incident(s)",
        "message": "There are active incidents requiring attention"
      }
    ]
  }
}
```

### 5. Notifications API

#### Получить уведомления
```bash
curl -X POST "http://localhost:8069/api/notifications" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "unread_only": "true",
      "limit": 10
    },
    "id": 1
  }'
```

**Параметры:**
- `unread_only`: показать только непрочитанные (`"true"`/`"false"`)
- `limit`, `offset`: пагинация

### 6. KPI API

#### Получить KPI данные
```bash
curl -X POST "http://localhost:8069/api/kpi" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "category": "incidents",
      "period": "month"
    },
    "id": 1
  }'
```

**Параметры:**
- `category`: категория KPI
- `period`: период (`day`, `week`, `month`, `year`)
- `from_date`, `to_date`: диапазон дат

**Пример ответа:**
```json
{
  "success": true,
  "data": {
    "incidents": {
      "total_incidents": 15,
      "active_incidents": 3,
      "resolved_incidents": 12,
      "high_severity_incidents": 2
    },
    "plans": {
      "total_plans": 45,
      "active_plans": 42,
      "outdated_plans": 3,
      "plan_coverage": 85.5
    },
    "clients": {
      "total_clients": 12,
      "active_clients": 10,
      "onboarding_clients": 2,
      "avg_bia_coverage": 78.3
    }
  }
}
```

### 7. Utility APIs

#### Health Check
```bash
curl -X POST "http://localhost:8069/api/bcm/health" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {},
    "id": 1
  }'
```

#### BCM Statistics
```bash
curl -X POST "http://localhost:8069/api/bcm/stats" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {},
    "id": 1
  }'
```

## Тестирование API

### Использование Python скрипта
```bash
# Запустить все тесты
python scripts/test_bcm_api_examples.py

# Запустить конкретный тест
python scripts/test_bcm_api_examples.py --test modules
python scripts/test_bcm_api_examples.py --test clients
python scripts/test_bcm_api_examples.py --test scenarios

# Настроить подключение
python scripts/test_bcm_api_examples.py \
  --url http://localhost:8069 \
  --database bcm_db \
  --username admin \
  --password admin
```

### Использование Postman

1. Создайте новую коллекцию "BCM API"
2. Добавьте переменные:
   - `baseUrl`: http://localhost:8069
   - `database`: bcm_db
3. Сначала выполните аутентификацию:
   ```
   POST {{baseUrl}}/web/session/authenticate
   {
     "jsonrpc": "2.0",
     "method": "call",
     "params": {
       "db": "{{database}}",
       "login": "admin",
       "password": "admin"
     },
     "id": 1
   }
   ```
4. Затем используйте любые API эндпоинты

## Коды ошибок

- `200`: Успешный запрос
- `400`: Неверные параметры запроса
- `401`: Ошибка аутентификации
- `403`: Нет доступа к ресурсу
- `404`: Ресурс не найден
- `500`: Внутренняя ошибка сервера

## Формат ошибок

```json
{
  "success": false,
  "data": [],
  "total": 0,
  "message": "Описание ошибки"
}
```

## Интеграция с Frontend

Для интеграции с Vue.js frontend используйте созданный API сервис:

```javascript
// src/services/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8069',
  headers: {
    'Content-Type': 'application/json'
  }
})

export const bcmAPI = {
  // Modules
  getModules: (params = {}) =>
    api.post('/api/bcm/modules', { jsonrpc: '2.0', method: 'call', params, id: 1 }),

  // Clients
  getClients: (params = {}) =>
    api.post('/api/clients', { jsonrpc: '2.0', method: 'call', params, id: 1 }),

  getClient: (id) =>
    api.post(`/api/clients/${id}`, { jsonrpc: '2.0', method: 'call', params: {}, id: 1 }),

  // Scenarios
  getScenarios: (params = {}) =>
    api.post('/api/scenarios', { jsonrpc: '2.0', method: 'call', params, id: 1 }),

  getScenario: (id) =>
    api.post(`/api/scenarios/${id}`, { jsonrpc: '2.0', method: 'call', params: {}, id: 1 }),

  // Dashboard
  getDashboard: (type, params = {}) =>
    api.post(`/api/dashboard/${type}`, { jsonrpc: '2.0', method: 'call', params, id: 1 }),

  // KPI
  getKPI: (params = {}) =>
    api.post('/api/kpi', { jsonrpc: '2.0', method: 'call', params, id: 1 }),

  // Notifications
  getNotifications: (params = {}) =>
    api.post('/api/notifications', { jsonrpc: '2.0', method: 'call', params, id: 1 })
}
```

## Заключение

Созданные REST API эндпоинты обеспечивают полный доступ к функциональности BCM модулей через HTTP API. Все эндпоинты:

- ✅ Поддерживают аутентификацию пользователей
- ✅ Включают CORS для cross-origin запросов
- ✅ Возвращают данные в стандартном формате
- ✅ Интегрируются с существующими Odoo моделями
- ✅ Поддерживают фильтрацию и пагинацию
- ✅ Включают обработку ошибок и логирование

API готов для использования frontend приложениями и внешними интеграциями.