# 🏗️ PLATFORM FRAMEWORK - Каркас платформы

## Компоненты из BCM-v1 для переноса:

### CORE PLATFORM SERVICES (Ядро платформы)
```
platform-framework/
├── event-bus/                 # Из /backend/eventbus
│   └── Центральная нервная система
│
├── service-registry/          # Новый + из /api/unified_api_gateway
│   └── Динамический реестр всех сервисов
│
├── api-gateway/              # Из /api + /services/unified_api_gateway
│   ├── main-gateway/         # /api/bcm_api_gateway.py
│   ├── events-api/           # /api/events
│   └── odoo-api/            # /api/odoo
│
├── auth-service/             # Из /backend/auth_service + Keycloak
│   └── Единая аутентификация
│
├── notification-service/     # Из /backend/notification_service
│   └── Все виды уведомлений
│
├── orchestrator/             # Из /backend/orchestrator
│   ├── workflow/            # /backend/orchestrator_service
│   └── process-engine/
│
├── monitoring/               # Из /services/monitoring_service
│   └── health-check/        # Объединенные health checks
│
└── config-service/           # НОВЫЙ - критически важен!
    └── Централизованные конфигурации
```

### ADAPTERS & INTEGRATIONS (Адаптеры и интеграции)
```
platform-framework/
└── integrations/
    ├── thehive/              # Из /adapters/thehive + /backend/thehive_adapter + /integrations/thehive
    │   └── Объединенный TheHive адаптер
    │
    ├── moodle/               # Из /integrations/moodle
    │   └── LMS интеграция
    │
    └── opengrc-oscal/        # Из /integrations/opengrc_oscal
        └── Compliance интеграция
```

## Текущее расположение компонентов в BCM-v1:

| Компонент | Где сейчас | Куда переносим |
|-----------|------------|----------------|
| Event Bus | `/backend/eventbus` | `→ /platform-framework/event-bus/` |
| Events API | `/api/events` | `→ /platform-framework/api-gateway/events-api/` |
| Odoo API | `/api/odoo` | `→ /platform-framework/api-gateway/odoo-api/` |
| Main Gateway | `/api/bcm_api_gateway.py` | `→ /platform-framework/api-gateway/main/` |
| Auth Service | `/backend/auth_service` | `→ /platform-framework/auth-service/` |
| Notification | `/backend/notification_service` | `→ /platform-framework/notification-service/` |
| Orchestrator | `/backend/orchestrator` | `→ /platform-framework/orchestrator/core/` |
| Orchestrator Service | `/backend/orchestrator_service` | `→ /platform-framework/orchestrator/service/` |
| TheHive (3 места!) | `/adapters/thehive`, `/backend/thehive_adapter`, `/integrations/thehive` | `→ /platform-framework/integrations/thehive/` |
| Moodle | `/integrations/moodle` | `→ /platform-framework/integrations/moodle/` |
| OpenGRC | `/integrations/opengrc_oscal` | `→ /platform-framework/integrations/opengrc/` |
| Services | `/services/*` | `→ Анализировать каждый` |

## Проблемы для решения:

### 1. ДУБЛИРОВАНИЕ
- **TheHive** - в 3 местах! (adapters, backend, integrations)
- **Event Bus** - в 4+ местах
- **API** - разбросано

### 2. ОТСУТСТВУЕТ
- **Config Service** - критично!
- **Dynamic Service Registry** - сейчас статический
- **General Rate Limiter** - только для WebSocket

### 3. ТРЕБУЕТ ОБЪЕДИНЕНИЯ
- **Auth** - 3 системы (backend, Keycloak, Odoo)
- **Health Checks** - разрозненные

## План миграции:

### PHASE 1: Базовый каркас (Week 1)
1. **Event Bus** - взять `/backend/eventbus/main.py` как основу
2. **Service Registry** - создать динамический на базе `/services/unified_api_gateway/`
3. **Config Service** - создать новый

### PHASE 2: Сервисы платформы (Week 2)
1. **API Gateway** - объединить все API в один
2. **Auth Service** - унифицировать через Keycloak
3. **Notification Service** - готов, просто перенести

### PHASE 3: Интеграции (Week 3)
1. **TheHive** - объединить 3 реализации в одну
2. **Moodle** - перенести как есть
3. **OpenGRC** - перенести как есть

## Архитектура взаимодействия:

```
    Service Registry (знает всех)
            ↓
    Config Service (настройки для всех)
            ↓
       Event Bus (связывает всех)
            ↓
      API Gateway (единая точка входа)
            ↓
    [Auth] → [Services] → [Monitoring]
            ↓
       Integrations (внешний мир)
```

## Команды для переноса:

```bash
# Создать структуру
mkdir -p platform-framework/{event-bus,service-registry,api-gateway,auth-service,notification-service,orchestrator,monitoring,config-service,integrations}

# Скопировать компоненты
cp -r BCM-v1/backend/eventbus/* platform-framework/event-bus/
cp -r BCM-v1/backend/auth_service/* platform-framework/auth-service/
cp -r BCM-v1/backend/notification_service/* platform-framework/notification-service/
cp -r BCM-v1/backend/orchestrator/* platform-framework/orchestrator/core/
cp -r BCM-v1/backend/orchestrator_service/* platform-framework/orchestrator/service/

# Объединить TheHive
mkdir platform-framework/integrations/thehive
cp -r BCM-v1/adapters/thehive/* platform-framework/integrations/thehive/
cp -r BCM-v1/backend/thehive_adapter/* platform-framework/integrations/thehive/
cp -r BCM-v1/integrations/thehive/* platform-framework/integrations/thehive/

# API Gateway
mkdir platform-framework/api-gateway/{main,events-api,odoo-api}
cp BCM-v1/api/bcm_api_gateway.py platform-framework/api-gateway/main/
cp -r BCM-v1/api/events/* platform-framework/api-gateway/events-api/
cp -r BCM-v1/api/odoo/* platform-framework/api-gateway/odoo-api/
```

## Результат:

Все компоненты платформы-каркаса будут:
1. ✅ В одном месте
2. ✅ Без дублирования
3. ✅ С единым Config Service
4. ✅ С динамическим Service Registry
5. ✅ Готовы к масштабированию