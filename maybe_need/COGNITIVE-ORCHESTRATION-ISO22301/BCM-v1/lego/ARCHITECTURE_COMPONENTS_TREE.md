# 🏗️ ДЕТАЛЬНАЯ АРХИТЕКТУРА КОМПОНЕНТОВ

## 📁 ВСЕ СОЗДАННЫЕ КОМПОНЕНТЫ:

```
lego/
│
├── 🎯 ORCHESTRATORS/
│   ├── base-orchestrator.js (450 строк)
│   │   ├── defineRequiredServices()
│   │   ├── loadServices()
│   │   ├── handle(request)
│   │   ├── subscribe(otherOrchestrator)
│   │   ├── healthCheck()
│   │   └── shutdown()
│   │
│   └── system-orchestrator.js (500 строк)
│       ├── handleEvent()
│       ├── handleWorkflow()
│       ├── handleData()
│       ├── handleAI()
│       └── optimizeSystem()
│
├── ⚙️ SYSTEM_COMPONENTS/
│   ├── 1_ORCHESTRATION/
│   │   ├── service-registry/
│   │   │   └── index.js
│   │   │       ├── registerService()
│   │   │       ├── discoverServices()
│   │   │       ├── resolveService()
│   │   │       ├── loadBalancing()
│   │   │       └── healthMonitoring()
│   │   │
│   │   ├── cognitive-orchestrator/
│   │   │   └── scenarios/*.json (6 AI сценариев)
│   │   │
│   │   └── scenario_orchestrator/
│   │       └── generated_scenarios/*.json
│   │
│   ├── 2_EVENTS/
│   │   └── message-queue/
│   │       └── index.js
│   │           ├── RabbitMQProvider
│   │           ├── RedisProvider
│   │           ├── publish()
│   │           ├── subscribe()
│   │           └── deadLetterQueue()
│   │
│   ├── 3_PROCESSING/
│   │   └── task-scheduler/
│   │       └── index.js
│   │           ├── scheduleTask()
│   │           ├── executeTask()
│   │           ├── retryLogic()
│   │           ├── priorityQueue
│   │           └── cronJobs()
│   │
│   ├── 4_STORAGE/
│   │   └── cache-layer/
│   │       └── index.js
│   │           ├── RedisCache
│   │           ├── MemoryCache
│   │           ├── get/set/delete()
│   │           ├── TTL management
│   │           └── cacheWarming()
│   │
│   ├── 5_INTELLIGENCE/
│   │   └── prediction-engine/
│   │       └── index.js
│   │           ├── loadModel()
│   │           ├── predict()
│   │           ├── trainModel()
│   │           ├── evaluateModel()
│   │           └── ensemblePredictions()
│   │
│   └── 6_TOOLS/ [ОКАЗЫВАЕТСЯ ЕСТЬ!]
│       ├── gateways/
│       │   └── platform-api-gateway/
│       │       ├── main/socketio_server.js
│       │       └── package.json
│       │
│       ├── monitoring/
│       │   └── platform-monitoring/
│       │       ├── grafana-*.json (6 дашбордов)
│       │       └── config/grafana/dashboards/
│       │
│       ├── vscode-extension/
│       │   ├── extension.js
│       │   └── package.json
│       │
│       └── mcp-server/
│           └── server.yaml
│
├── 🌉 BRIDGE_LAYER/
│   ├── ai-bridge-manager/
│   │   └── index.js (600 строк)
│   │       ├── registerModule()
│   │       ├── translateRequest()
│   │       ├── adaptResponse()
│   │       ├── learnFromInteraction()
│   │       └── optimizeRouting()
│   │
│   ├── operational-brain/
│   │   └── index.js (550 строк)
│   │       ├── buildContext()
│   │       ├── analyzeRequest()
│   │       ├── makeDecision()
│   │       ├── predictConsequences()
│   │       └── generateInsights()
│   │
│   ├── security-analyzer/
│   │   └── index.js (400 строк)
│   │       ├── analyzeThreats()
│   │       ├── detectAnomalies()
│   │       ├── enforcePolicy()
│   │       └── auditLog()
│   │
│   ├── coordinators/
│   │   └── dependency-coordinator.js (500 строк)
│   │       ├── buildDependencyGraph()
│   │       ├── resolveDependencies()
│   │       ├── detectCircular()
│   │       └── fallbackRoutes()
│   │
│   ├── module-wrapper/
│   │   └── index.js
│   │       └── wrapModule()
│   │
│   ├── auth-bridge/
│   │   └── index.js
│   │       ├── authenticateRequest()
│   │       └── authorizeAction()
│   │
│   ├── config-bridge/
│   │   └── index.js
│   │       └── syncConfiguration()
│   │
│   └── bcm_content_training_bridge/
│       └── service_config.json
│
├── 📦 PROGRAM_COMPONENTS_NEW/
│   ├── DOMAIN_REGISTRY/
│   │   └── bcm/
│   │       ├── manifest.yaml (139 строк)
│   │       │   ├── capabilities[]
│   │       │   ├── data_models[]
│   │       │   ├── workflows[]
│   │       │   └── integrations[]
│   │       │
│   │       └── core/bcm_core/ [копия Odoo модуля]
│   │
│   ├── MODULE_LIBRARY/
│   │   ├── business-impact-analysis/
│   │   │   ├── index.js (300 строк)
│   │   │   │   ├── assessBusinessImpact()
│   │   │   │   ├── mapProcessDependencies()
│   │   │   │   ├── calculateRtoRpo()
│   │   │   │   └── generateBiaReports()
│   │   │   │
│   │   │   ├── metadata.yaml
│   │   │   └── odoo-source/bcm_bia/ [копия]
│   │   │
│   │   ├── risk-assessment/
│   │   │   └── index.js (360 строк)
│   │   │       ├── assess()
│   │   │       ├── bulkAssess()
│   │   │       ├── calculateRiskScore()
│   │   │       └── simulate()
│   │   │
│   │   └── [другие модули-обертки]
│   │
│   ├── INTEGRATION_LAYER/
│   │   └── platform-adapters/
│   │       └── odoo-adapter/
│   │           ├── index.js (350 строк)
│   │           │   ├── registerOdooModule()
│   │           │   ├── executeSystemRequest()
│   │           │   ├── transformSystemToOdoo()
│   │           │   ├── transformOdooToSystem()
│   │           │   └── registerAllBcmModules()
│   │           │
│   │           ├── bcm-modules-config.js (300 строк)
│   │           │   ├── bcmModulesConfig{}
│   │           │   ├── transformationRules{}
│   │           │   └── monitoringConfig{}
│   │           │
│   │           └── test-adapter.js (200 строк)
│   │
│   └── USER_CONTEXT/
│       └── index.js (350 строк)
│           ├── createUserProfile()
│           ├── personalizeResults()
│           ├── trackPreferences()
│           └── adaptInterface()
│
├── 🛡️ CLIENT_INFRASTRUCTURE/
│   ├── index.js (400 строк)
│   │   ├── initializeSecurity()
│   │   ├── initializeAuth()
│   │   ├── initializeDatabases()
│   │   ├── initializeMonitoring()
│   │   ├── initializeAPIGateway()
│   │   └── handleClientRequest()
│   │
│   └── security/
│       └── security-gateway.js (700 строк)
│           ├── loadWAFRules()
│           ├── validate()
│           ├── checkDDoS()
│           ├── checkRateLimit()
│           ├── encrypt/decrypt()
│           └── blacklistIP()
│
├── 🧪 SANDBOX/
│   └── evolution-agent/
│       ├── index.js
│       │   ├── evolve()
│       │   └── optimize()
│       └── package.json
│
└── 📄 PROGRAM_COMPONENTS/ [старые Odoo модули]
    └── addons26/
        ├── bcm_core/
        ├── bcm_bia/
        ├── bcm_incident/
        └── ... (26 BCM модулей)
```

## 📊 СТАТИСТИКА КОМПОНЕНТОВ:

### По типам файлов:
- **JavaScript (.js):** 25+ файлов
- **YAML (.yaml):** 3 файла
- **JSON (.json):** 20+ файлов (в основном Grafana dashboards)

### По функциональности:
```
Оркестрация:        5 компонентов
Обработка событий:  3 компонента
AI/ML:              4 компонента
Безопасность:       3 компонента
Мониторинг:         6 dashboards
Адаптеры:           3 типа
Модули-обертки:     9 модулей
```

### Основные классы и функции:
```javascript
// Всего ~50+ основных методов, например:

BaseOrchestrator {
  - initialize()
  - loadServices()
  - handle()
  - subscribe()
  - healthCheck()
}

AiBridgeManager {
  - registerModule()
  - translateRequest()
  - adaptResponse()
  - learnFromInteraction()
}

OperationalBrain {
  - buildContext()
  - analyzeRequest()
  - makeDecision()
  - predictConsequences()
}

OdooAdapter {
  - registerOdooModule()
  - executeSystemRequest()
  - transformData()
  - monitorHealth()
}

SecurityGateway {
  - validateRequest()
  - checkDDoS()
  - rateLimit()
  - encrypt()
}
```

## 🎯 ВЗАИМОСВЯЗИ:

```
Orchestrators → управляют → Services
    ↓
Services → используют → Bridge Components
    ↓
Bridge → транслирует → Program Modules
    ↓
Modules → вызывают → External Services (Odoo)
    ↓
Security → защищает → все уровни
    ↓
Monitoring → отслеживает → все компоненты
```