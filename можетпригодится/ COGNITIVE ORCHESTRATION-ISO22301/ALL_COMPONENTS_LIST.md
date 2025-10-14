# 🎯 ВСЕ КОМПОНЕНТЫ - КУБИКИ КОНСТРУКТОРА

## Вываливаем все компоненты из BCM-v1 и platform-framework:

### Backend компоненты:
```
BCM-v1/backend/eventbus                  # Event Bus - нервная система
BCM-v1/backend/orchestrator              # AI Orchestrator
BCM-v1/backend/orchestrator_service      # Platform Orchestrator
BCM-v1/backend/bpmn_service              # Workflow Engine
BCM-v1/backend/auth_service              # Authentication
BCM-v1/backend/notification_service      # Notifications
BCM-v1/backend/document_processor        # Document Processing
BCM-v1/backend/thehive_adapter           # TheHive Integration
BCM-v1/backend/lms_adapter               # LMS Integration
BCM-v1/backend/grafana_adapter           # Grafana Integration
BCM-v1/backend/service_registry          # Service Registry
```

### Services компоненты:
```
BCM-v1/services/ai_orchestrator          # AI Orchestration
BCM-v1/services/ai_workflow_optimizer    # AI Workflow Optimization
BCM-v1/services/process_mining_service   # Process Mining
BCM-v1/services/monitoring_service       # Monitoring
BCM-v1/services/notification_service     # Notifications (duplicate)
BCM-v1/services/unified_api_gateway      # Unified API Gateway
BCM-v1/services/unified_control_center   # Control Center
BCM-v1/services/unified_database_gateway # Database Gateway
BCM-v1/services/realtime_websocket       # WebSocket Service
BCM-v1/services/deployer                 # Deployment Service
BCM-v1/services/integration_hub          # Integration Hub
```

### Integrations компоненты:
```
BCM-v1/integrations/gateway              # API Gateway
BCM-v1/integrations/nginx                # Load Balancer
BCM-v1/integrations/thehive              # TheHive
BCM-v1/integrations/lms                  # Learning Management
BCM-v1/integrations/governance           # GRC Integration
BCM-v1/integrations/opengrc_oscal        # OSCAL Standard
BCM-v1/integrations/exercise_simulators  # Exercise Simulations
BCM-v1/integrations/simulation           # Simulations
BCM-v1/integrations/mcp-server           # MCP Server
```

### Platform-framework компоненты:
```
platform-framework/event-bus             # Event Bus (новый)
platform-framework/service-registry      # Service Registry (новый)
platform-framework/orchestrator          # Cognitive Orchestrator (новый)
platform-framework/api-gateway           # API Gateway (новый)
platform-framework/auth-service          # Auth Service (новый)
platform-framework/config-service        # Config Service
platform-framework/monitoring            # Monitoring Stack
platform-framework/notification-service  # Notifications
platform-framework/document-processor    # Document Processor
platform-framework/services/bpmn_service # BPMN Service
```

### Golden modules (Odoo BCM):
```
golden-pr-modules/bcm_ai_bridge          # AI Bridge для Odoo
golden-pr-modules/bcm_microservices_bridge # Microservices Bridge
golden-pr-modules/bcm_project_management # Project Management
golden-pr-modules/core/odoo-18.0/addons/bcm_* # Все BCM модули
```

## 🏗️ ТЕПЕРЬ СТРОИМ ПО СЛОЯМ:

### 🧠 **1_BRAIN** (Мозг - думает и решает):
```
ОБЪЕДИНЯЕМ:
- backend/orchestrator
- backend/orchestrator_service
- services/ai_orchestrator
- platform-framework/orchestrator
→ В ЕДИНЫЙ: orchestrator/

- services/ai_workflow_optimizer
→ ai-optimizer/

- services/unified_control_center
→ control-center/

- golden-pr-modules/bcm_ai_bridge
→ ai-bridge/
```

### ⚡ **2_NERVOUS_SYSTEM** (Нервы - передача сигналов):
```
ОБЪЕДИНЯЕМ:
- backend/eventbus
- platform-framework/event-bus
→ В ЕДИНЫЙ: event-bus/

- backend/service_registry
- platform-framework/service-registry
→ service-registry/

- backend/bpmn_service
- platform-framework/services/bpmn_service
→ workflow-engine/

- services/process_mining_service
→ process-mining/
```

### 👁️ **3_SENSORS** (Сенсоры - наблюдают):
```
- services/monitoring_service
- platform-framework/monitoring
→ monitoring/

- backend/grafana_adapter
→ grafana-connector/

Добавить:
→ alerting/
→ telemetry/
→ analytics/
```

### 🔌 **4_CONNECTORS** (Коннекторы - связь с миром):
```
ОБЪЕДИНЯЕМ:
- integrations/gateway
- services/unified_api_gateway
- platform-framework/api-gateway
→ В ЕДИНЫЙ: api-gateway/

- integrations/nginx
→ load-balancer/

- backend/auth_service
- platform-framework/auth-service
→ auth-service/

- services/realtime_websocket
→ websocket-gateway/

- backend/notification_service
- services/notification_service
- platform-framework/notification-service
→ В ЕДИНЫЙ: notifications/
```

### 🔗 **5_INTEGRATORS** (Интеграторы - подключения):
```
ОБЪЕДИНЯЕМ:
- services/unified_database_gateway
→ database-gateway/

- integrations/thehive
- backend/thehive_adapter
→ thehive-connector/

- integrations/lms
- backend/lms_adapter
→ lms-connector/

- integrations/governance
- integrations/opengrc_oscal
→ governance-connector/

- services/integration_hub
→ integration-hub/

- golden-pr-modules/bcm_microservices_bridge
→ microservices-bridge/
```

### 🛠️ **6_TOOLS** (Инструменты - универсальные):
```
- backend/document_processor
- platform-framework/document-processor
→ document-processor/

- services/deployer
→ deployment-manager/

- integrations/exercise_simulators
- integrations/simulation
→ simulators/

- integrations/mcp-server
→ mcp-server/

- platform-framework/config-service
→ config-manager/
```

### 📦 **7_BCM_MODULES** (BCM специфичные модули):
```
Все из golden-pr-modules/core/odoo-18.0/addons/:
- bcm_base
- bcm_core
- bcm_risk_management
- bcm_incident_management
- bcm_audit
- bcm_training
- bcm_bia
- bcm_governance
- bcm_plans
- bcm_exercise
- bcm_reporting
- bcm_kpi
... и другие bcm_*
```

### 🏢 **8_PLATFORM** (Платформа - скелет):
```
- golden-pr-modules/core/odoo-18.0/
→ odoo-core/

- Инфраструктура (PostgreSQL, Redis, RabbitMQ)
→ infrastructure/
```

## 🔄 ДУБЛИКАТЫ И ОБЪЕДИНЕНИЯ:

1. **EventBus**: 3 версии → объединить в одну
2. **Orchestrator**: 4 версии → объединить в один Cognitive Orchestrator
3. **API Gateway**: 3 версии → объединить
4. **Notification Service**: 3 версии → объединить
5. **TheHive**: adapter + integration → объединить
6. **LMS**: adapter + integration → объединить
7. **Auth Service**: 2 версии → объединить
8. **Document Processor**: 2 версии → объединить
9. **Monitoring**: 2 версии → объединить

Теперь у нас есть полная карта всех компонентов и как их правильно распределить по слоям организма!