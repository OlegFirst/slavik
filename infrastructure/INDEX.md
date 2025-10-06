# Infrastructure Documentation Index

**Обновлено:** 2025-10-06

---

## 📚 Основная документация

### 1. [README.md](README.md)
**Назначение:** Главная страница infrastructure
- Обзор всех сервисов
- Статус (работающие/требующие настройки/to be created)
- Приоритеты развития
- Архивированные компоненты

### 2. [OVERVIEW.md](OVERVIEW.md) ⭐ NEW
**Назначение:** Полный обзор архитектуры и сервисов
- Детальное описание каждого сервиса
- Архитектурные диаграммы
- Интеграции с shared library и platform-services
- Производительность и best practices

### 3. [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md) ⭐ NEW
**Назначение:** Техническая документация для разработчиков
- Quick Start
- Environment Setup (полный .env guide)
- Service Configuration (для каждого сервиса)
- Development Workflow
- Production Deployment
- Troubleshooting

---

## 🔧 Сервисы (Production-ready)

### Database
- [database/README.md](database/README.md) - PostgreSQL + Redis managers
- [database/migrations_source/README.md](database/migrations_source/README.md) - Migration guide

### EventBus
- [eventbus/README.md](eventbus/README.md) - Main documentation
- [eventbus/ARCHITECTURE.md](eventbus/ARCHITECTURE.md) - Architecture deep dive
- [eventbus/QUICKSTART.md](eventbus/QUICKSTART.md) - Quick start guide
- [eventbus/SUMMARY.md](eventbus/SUMMARY.md) - Executive summary

### Security
- [security/README.md](security/README.md) - Security overview
- [security/SECURITY_ROADMAP.md](security/SECURITY_ROADMAP.md) - Security roadmap

### Vector DB (Qdrant Cloud)
- [vector-db/README.md](vector-db/README.md) - Full documentation
- [vector-db/QUICKSTART.md](vector-db/QUICKSTART.md) - Quick start ⭐
- [vector-db/SETUP_COMPLETE.md](vector-db/SETUP_COMPLETE.md) - Setup summary

### Monitoring
- [monitoring/README.md](monitoring/README.md) - Prometheus + Grafana
- [monitoring/MIGRATION_CHECKLIST.md](monitoring/MIGRATION_CHECKLIST.md) - Migration guide

### Service Discovery
- [service-discovery/README.md](service-discovery/README.md) - Service registry + health checks

---

## ⚙️ Сервисы (Needs Configuration)

### Notification Service
- [notification-service/README.md](notification-service/README.md) - Email, Slack, Telegram
- [notification-service/QUICK_START.md](notification-service/QUICK_START.md) - Quick start
- [notification-service/INTEGRATION_COMPLETE.md](notification-service/INTEGRATION_COMPLETE.md) - Integration guide

### Realtime WebSocket
- [realtime-websocket/README.md](realtime-websocket/README.md) - WebSocket server
- [realtime-websocket/MIGRATION_CHECKLIST.md](realtime-websocket/MIGRATION_CHECKLIST.md) - Setup checklist

### Message Queue
- [message-queue/README.md](message-queue/README.md) - RabbitMQ integration

### Intelligent Gateway
- [intelligent-gateway/README.md](intelligent-gateway/README.md) - AI-powered gateway (495 строк!)

### Secrets Manager
- [secrets-manager/README.md](secrets-manager/README.md) - HashiCorp Vault

### Deployment Service
- [deployment-service/README.md](deployment-service/README.md) - Deployment automation
- [deployment-service/IMPROVEMENTS.md](deployment-service/IMPROVEMENTS.md) - Improvement ideas

### GitHub Integration
- [github-integration/README.md](github-integration/README.md) - GitHub webhooks
- [github-integration/IMPROVEMENTS.md](github-integration/IMPROVEMENTS.md) - Enhancement ideas

### Observability
- [observability/README.md](observability/README.md) - Distributed tracing
- [observability/MIGRATION_COMPLETE.md](observability/MIGRATION_COMPLETE.md) - Migration status
- [observability/monitoring-README.md](observability/monitoring-README.md) - Monitoring guide

---

## 🗂️ Дополнительные сервисы

### Docker Management
- [docker-management/README.md](docker-management/README.md) - Docker orchestration

### MCP Server
- [mcp-server/README.md](mcp-server/README.md) - MCP protocol для collective agents

### Process Mining Service
- [process_mining_service/README.md](process_mining_service/README.md) - Process analytics
- [process_mining_service/IMPROVEMENTS.md](process_mining_service/IMPROVEMENTS.md) - Improvement ideas

### Partisia Contracts
- [partisia-contracts/README.md](partisia-contracts/README.md) - Blockchain integration

---

## 💾 Data Storage

### Compliance Data
- [data/compliance/README.md](data/compliance/README.md) - ISO 22301 compliance data storage
  - `alerts/` - Compliance alerts
  - `nonconformities/` - Nonconformity records
  - `audits/` - Audit tracking
  - `metrics/` - BC metrics (RTO/RPO/MTPD)
  - `backups/` - Daily snapshots
  - `automation/` - Automation results

---

## 📦 Архив

### архив/
Историческая документация (устаревшая):
- [архив/INDEX.md](архив/INDEX.md) - Index архива
- `INFRASTRUCTURE_ANALYSIS.md` - Old analysis
- `ARCHITECTURE_ASSESSMENT.md` - Old assessment
- `SERVICES_INVENTORY.md` - Old inventory
- `PERFORMANCE_IMPACT_ANALYSIS.md` - Performance study
- `SHARED_LIBRARY_IMPACT.md` - Shared library analysis
- И другие старые документы

**⚠️ Не использовать для актуальной информации!**
Только для исторического контекста.

---

## 🚀 С чего начать?

### Для новых разработчиков:
1. **Читай:** [OVERVIEW.md](OVERVIEW.md) - архитектура и обзор
2. **Настраивай:** [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md) - setup окружения
3. **Изучай:** Документацию конкретных сервисов

### Для DevOps:
1. **Deployment:** [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md) - Production Deployment section
2. **Monitoring:** [monitoring/README.md](monitoring/README.md)
3. **Secrets:** [secrets-manager/README.md](secrets-manager/README.md)

### Для архитекторов:
1. **Архитектура:** [OVERVIEW.md](OVERVIEW.md)
2. **EventBus:** [eventbus/ARCHITECTURE.md](eventbus/ARCHITECTURE.md)
3. **Security:** [security/SECURITY_ROADMAP.md](security/SECURITY_ROADMAP.md)

---

## 📊 Статус документации

### ✅ Актуальная (2025-10-06):
- README.md
- OVERVIEW.md (NEW!)
- TECHNICAL_GUIDE.md (NEW!)
- vector-db/* (NEW!)
- eventbus/*
- database/*
- security/*
- monitoring/*
- notification-service/*
- realtime-websocket/*

### ⚠️ Требует обновления:
- message-queue/
- intelligent-gateway/ (архитектура готова, нужна реализация)
- secrets-manager/
- observability/

### 📦 Архивная:
- архив/* - всё устаревшее

---

## 🔗 Связанные документы

### Root Documentation
- [/README.md](../README.md) - Main project README
- [/.env.example](../.env.example) - Environment variables template
- [/ARCHITECTURE_VISION.md](../ARCHITECTURE_VISION.md) - Overall vision

### Shared Library
- [/shared/](../shared/) - Common code
  - database, auth, cache, eventbus clients
  - integrations (RAG, Knowledge, ML Platform)

### Platform Services
- [/platform-services/](../platform-services/) - Business services
  - BIA, Risk, Planning, Response, etc.

### Intelligent Core
- [/intelligent-core/](../intelligent-core/) - AI components
  - AI Experts, Workflow Intelligence, Learning, etc.

---

## 📝 Conventions

### Naming:
- `README.md` - Main documentation для сервиса
- `QUICKSTART.md` - Quick start guide
- `ARCHITECTURE.md` - Architecture deep dive
- `MIGRATION_*.md` - Migration guides
- `IMPROVEMENTS.md` - Enhancement ideas
- `*_COMPLETE.md` - Completion/status reports

### Structure:
```
service-name/
├── README.md              # Main docs
├── QUICKSTART.md          # Quick start (optional)
├── requirements.txt       # Dependencies
├── docker-compose.yml     # Docker setup (if applicable)
└── src/                   # Source code
```

---

## 🆘 Help

**Вопросы?**
1. Проверь соответствующий README
2. Проверь [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md) - Troubleshooting section
3. Проверь [архив/](архив/) - может быть исторический контекст

**Нашел ошибку в документации?**
- Обнови соответствующий файл
- Добавь дату обновления
- Commit с понятным сообщением

---

**Last Updated:** 2025-10-06
**Maintainers:** BCM Platform Team
