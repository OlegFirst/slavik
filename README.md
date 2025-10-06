# 🏗️ AI-Powered BCM Platform

**AI-Powered Business Continuity Management Platform** - Production-ready платформа для управления непрерывностью бизнеса с AI intelligence.

**Version:** 8.2 Final
**Status:** Production Architecture ✅
**Date:** 2025-10-06

---

## 🚀 Quick Start

**✅ Temporal Cloud Setup Complete!**

**Status:**
- [x] Python 3.11.13 installed
- [x] Temporal CLI 1.4.1 installed
- [x] Temporal Cloud connected
- [x] Sample project tested
- [ ] **Next:** Start Phase 2 - Workflow Intelligence Engine (8-12 дней)

**Start Here:**

1. **[intelligent-core/workflow_intelligence/README.md](intelligent-core/workflow_intelligence/README.md)** ⭐⭐⭐ - **Workflow Intelligence Engine**
   - Temporal Cloud setup complete
   - Ready to start Phase 2 development
   - Core Workflow Engine + Case Library + Governance

2. **[doc-project/CORRECT_SETUP_WITH_TEMPORAL.md](doc-project/CORRECT_SETUP_WITH_TEMPORAL.md)** - Full deployment guide
   - Основано на `арх2.md`
   - 5 фаз deployment (20-30 дней)

3. **[infrastructure/README.md](infrastructure/README.md)** - Infrastructure overview
4. **[infrastructure/TECHNICAL_GUIDE.md](infrastructure/TECHNICAL_GUIDE.md)** - Technical guide
5. **[infrastructure/OVERVIEW.md](infrastructure/OVERVIEW.md)** - Architecture overview

---

## 📋 О проекте

### Что это?

AI-Powered BCM Platform - это **полнофункциональная платформа** для управления непрерывностью бизнеса (Business Continuity Management) с встроенным искусственным интеллектом.

**Основные возможности:**

1. **12 BCM модулей:**
   - Business Impact Analysis (BIA)
   - Risk Management
   - Compliance Management
   - Document Management
   - Incident Response
   - Validation & Testing
   - Governance
   - Planning
   - Learning & Training
   - Community

2. **AI Intelligence:**
   - Workflow automation
   - Predictive analytics
   - AI experts (domain knowledge)
   - Learning system
   - Recommendation engine

3. **Production Infrastructure:**
   - Microservices architecture
   - Event-driven messaging
   - Vector database (RAG)
   - Real-time WebSocket
   - Monitoring & observability

---

## 🏗️ Архитектура

### Layered Architecture (5 слоев)

```
┌─────────────────────────────────────────────────────┐
│  Layer 5: Human Interface                           │
│           (Web App + API Gateway)                    │
├─────────────────────────────────────────────────────┤
│  Layer 4: Platform Services                         │
│           (12 BCM Microservices)                     │
├─────────────────────────────────────────────────────┤
│  Layer 3: Intelligent Core                          │
│           (AI + Workflow Intelligence)               │
├─────────────────────────────────────────────────────┤
│  Layer 2: Shared Libraries                          │
│           (Auth, DB, Cache, EventBus)                │
├─────────────────────────────────────────────────────┤
│  Layer 1: Infrastructure                            │
│           (Database, Redis, Qdrant, EventBus)        │
└─────────────────────────────────────────────────────┘
```

**Deployment Order:** Layer 1 → Layer 2 → Layer 3 → Layer 4 → Layer 5

**Подробнее:** [infrastructure/OVERVIEW.md](infrastructure/OVERVIEW.md)

---

## 📁 Структура проекта

```
AI-Platform-ISO/
│
├── infrastructure/          # Layer 1: Infrastructure services
│   ├── database/           # PostgreSQL + Supabase (43 migrations)
│   ├── eventbus/           # Event-driven messaging (Redis Streams)
│   ├── vector-db/          # Qdrant Cloud (RAG + semantic search)
│   ├── monitoring/         # Prometheus + Grafana
│   ├── security/           # API Gateway + Auth
│   └── ...                 # 20+ infrastructure services
│
├── shared/                 # Layer 2: Shared libraries (11,248 LOC)
│   ├── auth/              # JWT + RBAC
│   ├── database/          # Async DB + connection pooling
│   ├── cache/             # Redis cache
│   ├── eventbus/          # EventBus client
│   ├── integrations/      # RAG, Knowledge, ML Platform
│   └── ...
│
├── intelligent-core/       # Layer 3: AI Intelligence
│   ├── workflow_intelligence/   # Workflow Engine (THE BRAIN)
│   ├── ai_experts/             # Domain knowledge experts
│   ├── coordination-center/    # AI → Tools orchestration
│   ├── learning-system/        # Learning from outcomes
│   ├── predictive/             # Predictive analytics
│   └── ...
│
├── platform-services/      # Layer 4: Business services (12)
│   ├── bia-service/        # Business Impact Analysis (3,405 LOC)
│   ├── risk-service/       # Risk Management (2,156 LOC)
│   ├── compliance-service/ # Compliance (1,789 LOC)
│   └── ...                 # +8 more services
│
├── human-interface/        # Layer 5: User interfaces
│   ├── api-gateway/       # GraphQL/REST API
│   └── web-app/           # React/Vue Web App
│
├── tools/                 # Development tools
├── tests/                 # Testing infrastructure
├── ISO-22301-Library/     # BCM knowledge base
│
├── .env.example           # Environment variables template
├── docker-compose.yml     # Docker Compose config
├── SETUP_ALGORITHM.md     # ⭐ Setup guide
└── README.md              # This file
```

---

## 🚀 Deployment

### Prerequisites

```bash
# System requirements
Docker >= 24.0
Docker Compose >= 2.20
Python >= 3.11
PostgreSQL >= 14
Redis >= 7.0
Node.js >= 18 (for web app)

# Resources
Min 8GB RAM
Min 4 CPU cores
Min 50GB disk space
```

### Quick Setup (для нетерпеливых)

```bash
# 1. Clone
git clone <repo-url>
cd AI-Platform-ISO

# 2. Configure
cp .env.example .env
nano .env  # Fill in credentials

# 3. Start foundation
docker-compose up -d postgres redis

# 4. Apply migrations
cd infrastructure/database
python apply_migrations_simple.py

# 5. Initialize Qdrant
cd ../vector-db
pip install -r requirements.txt
python qdrant/init_collections.py

# 6. Start infrastructure
cd ../eventbus && python -m eventbus.main &
cd ../security/api-gateway && uvicorn main:app --port 3001 &

# 7. Start platform services
./infrastructure/scripts/start_platform_services.sh

# 8. Health check
./infrastructure/scripts/health_check_all.sh
```

### Proper Setup (рекомендуется)

**Следуй пошаговому алгоритму:**

📖 **[SETUP_ALGORITHM.md](SETUP_ALGORITHM.md)** ⭐

- 7 фаз deployment
- 40-54 часа (1-2 недели)
- Validation на каждом шаге
- Production-ready конфигурация

---

## 📚 Документация

### Основная документация

| Документ | Описание |
|----------|----------|
| **[SETUP_ALGORITHM.md](SETUP_ALGORITHM.md)** ⭐ | Пошаговый алгоритм настройки |
| [infrastructure/DEPLOYMENT_ROADMAP.md](infrastructure/DEPLOYMENT_ROADMAP.md) | Детальный deployment roadmap |
| [infrastructure/OVERVIEW.md](infrastructure/OVERVIEW.md) | Обзор архитектуры |
| [infrastructure/TECHNICAL_GUIDE.md](infrastructure/TECHNICAL_GUIDE.md) | Техническое руководство |
| [infrastructure/QUICK_REFERENCE.md](infrastructure/QUICK_REFERENCE.md) | Быстрая справка |
| [infrastructure/INDEX.md](infrastructure/INDEX.md) | Полный индекс документации |

### По компонентам

| Компонент | Документация |
|-----------|--------------|
| **EventBus** | [eventbus/QUICKSTART.md](infrastructure/eventbus/QUICKSTART.md) |
| **Vector DB** | [vector-db/QUICKSTART.md](infrastructure/vector-db/QUICKSTART.md) |
| **Notifications** | [notification-service/QUICK_START.md](infrastructure/notification-service/QUICK_START.md) |
| **Database** | [database/README.md](infrastructure/database/README.md) |
| **Monitoring** | [monitoring/README.md](infrastructure/monitoring/README.md) |

### Архитектурная документация

- [doc-project/FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md](doc-project/FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md) - Полная спецификация архитектуры V8.2

---

## 🔧 Development

### Start Development Environment

```bash
# Terminal 1: Infrastructure
docker-compose up -d

# Terminal 2: EventBus
cd infrastructure/eventbus
python -m eventbus.main

# Terminal 3: API Gateway
cd infrastructure/security/api-gateway
uvicorn main:app --port 3001 --reload

# Terminal 4: Platform Services
./infrastructure/scripts/start_platform_services.sh

# Terminal 5: Web App
cd human-interface/web-app
npm run dev
```

### Run Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# E2E tests
pytest tests/e2e/ -v

# Health check
./infrastructure/scripts/health_check_all.sh
```

### Code Quality

```bash
# Linting
ruff check .

# Type checking
mypy .

# Format
black .
ruff format .
```

---

## 🌟 Key Features

### 1. AI-Powered Workflows
- Automatic workflow generation
- Context-aware recommendations
- Learning from outcomes
- Predictive risk assessment

### 2. Semantic Search (RAG)
- Knowledge base search (ISO standards, BCI guidelines)
- Case library search (workflow patterns)
- Document search
- Powered by Qdrant Vector DB

### 3. Real-time Collaboration
- WebSocket for live updates
- Event-driven notifications
- Multi-user workflows
- Activity streams

### 4. Compliance Automation
- ISO 22301 compliance tracking
- Automated compliance checks
- Audit trail
- Evidence collection

### 5. Production-Ready Infrastructure
- Microservices architecture
- Event-driven messaging
- Horizontal scaling
- Monitoring & observability
- Automated backups
- Security hardening

---

## 📊 Statistics

**Code Base:**
- **Infrastructure:** 20+ services
- **Platform Services:** 12 microservices (~18,000 LOC)
- **Shared Library:** 11,248 LOC, 57 files
- **Intelligent Core:** AI + Workflow + Domain expertise
- **Database Migrations:** 43 migrations (006-041)
- **Total:** ~50,000+ LOC

**Technologies:**
- **Backend:** Python 3.11, FastAPI, PostgreSQL, Redis
- **AI:** OpenAI, Anthropic Claude, RAG (Qdrant)
- **Frontend:** React/Vue, Next.js
- **Infrastructure:** Docker, Docker Compose, Kubernetes-ready
- **Monitoring:** Prometheus, Grafana
- **Auth:** JWT, Supabase Auth, Keycloak (SSO)

---

## 🤝 Contributing

**Setup для разработчиков:**

1. Прочитай [SETUP_ALGORITHM.md](SETUP_ALGORITHM.md)
2. Настрой development environment
3. Изучи [infrastructure/TECHNICAL_GUIDE.md](infrastructure/TECHNICAL_GUIDE.md)
4. Проверь service-specific README

**Code style:**
- Follow PEP 8 (Python)
- Use type hints
- Write tests
- Document changes

---

## 📄 License

[Specify your license here]

---

## 📞 Support

**Questions?**
- Check [SETUP_ALGORITHM.md](SETUP_ALGORITHM.md)
- Review [infrastructure/TECHNICAL_GUIDE.md](infrastructure/TECHNICAL_GUIDE.md)
- Check [infrastructure/INDEX.md](infrastructure/INDEX.md) for full docs index

**Found a bug?**
- Check logs
- Review troubleshooting guide
- Document the issue

---

## 🗺️ Roadmap

### Completed ✅
- ✅ Infrastructure foundation (Database, Redis, Qdrant)
- ✅ EventBus (event-driven messaging)
- ✅ API Gateway + Auth
- ✅ 12 Platform services
- ✅ AI Intelligence layer
- ✅ Vector DB (RAG)
- ✅ Monitoring stack

### In Progress ⏳
- ⏳ Notification service configuration
- ⏳ WebSocket real-time updates
- ⏳ Message queue setup

### Planned 📋
- 📋 Kubernetes deployment
- 📋 Advanced ML models
- 📋 Multi-tenant support
- 📋 Mobile app
- 📋 Advanced analytics dashboards

---

## 🎯 Quick Links

- **Setup Guide:** [SETUP_ALGORITHM.md](SETUP_ALGORITHM.md) ⭐
- **Architecture:** [infrastructure/OVERVIEW.md](infrastructure/OVERVIEW.md)
- **Technical Guide:** [infrastructure/TECHNICAL_GUIDE.md](infrastructure/TECHNICAL_GUIDE.md)
- **Full Docs Index:** [infrastructure/INDEX.md](infrastructure/INDEX.md)
- **Architecture Spec:** [doc-project/FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md](doc-project/FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md)

---

**Built with ❤️ using AI + Modern Software Architecture**

**Last Updated:** 2025-10-06
**Version:** 8.2 Final
**Status:** Production Ready ✅
