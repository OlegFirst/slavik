# AI-Powered BCM Platform (ISO 22301)

Интеллектуальная платформа для управления непрерывностью бизнеса с AI-first архитектурой и Digital Twin симуляцией.

## Уникальные возможности

🧠 **AI Command Center** - Искусственный интеллект для принятия решений, прогнозирования и оптимизации
🔮 **Digital Twin** - Симуляция сбоев и тестирование стратегий восстановления
📊 **Quantitative Risk** - FAIR методология + Монте-Карло анализ
🏥 **Healthcare-Specialized** - WHO Tier 1-4 framework встроен
✅ **ISO 22301 Compliant** - Автоматический аудит соответствия стандарту

## Архитектура

```
┌─────────────────────────────────┐
│     INTELLIGENT CORE            │
│  • AI Orchestration Engine      │
│  • Knowledge System             │
│  • Digital Twin Simulator       │
└─────────────────────────────────┘
            ↓
┌─────────────────────────────────┐
│     EXECUTION ENGINE            │
│  • PLAN Workflow (ISO Clause 4-7)
│  • DO Workflow (ISO Clause 8)   │
│  • CHECK Workflow (ISO Clause 9)│
│  • ACT Workflow (ISO Clause 10) │
└─────────────────────────────────┘
            ↓
┌─────────────────────────────────┐
│     HUMAN INTERFACE             │
│  • Web Application              │
│  • API Gateway                  │
│  • AI Chat                      │
└─────────────────────────────────┘
```

## Быстрый старт

### Требования

- Docker 20.10+
- Docker Compose 2.0+
- Node.js 18+ (для frontend разработки)
- Python 3.11+ (для backend разработки)

### Запуск

```bash
# Клонировать репозиторий
git clone https://github.com/yourusername/AI-Platform-ISO.git
cd AI-Platform-ISO

# Создать .env файл
cp .env.example .env
# Отредактировать .env (добавить API ключи)

# Запустить все сервисы
docker-compose up -d

# Проверить статус
docker-compose ps
```

Приложение будет доступно:
- **Web UI**: http://localhost:3000
- **API Gateway**: http://localhost:3001
- **API Docs**: http://localhost:3001/docs

## Структура проекта

```
AI-Platform-ISO/
├── intelligent-core/       # AI мозг платформы
│   ├── orchestrator/       # Принятие решений, оптимизация
│   ├── knowledge/          # База знаний BCM
│   ├── digital_twin/       # Симулятор сбоев
│   └── ai_capabilities/    # AI функции (Risk Advisor, Scenario Gen)
│
├── execution-engine/       # Выполнение BCM процессов
│   ├── workflows/          # PLAN, DO, CHECK, ACT
│   └── capabilities/       # 9 BCM модулей (BIA, Risk, Plans...)
│
├── human-interface/        # UI и API
│   ├── api-gateway/        # API шлюз
│   └── web-app/            # React/Next.js frontend
│
├── platform-services/      # Поддерживающие сервисы
│   ├── auth-service/       # Аутентификация
│   ├── notification-service/
│   └── file-service/
│
└── infrastructure/         # Деплой и мониторинг
    ├── database/
    ├── observability/
    └── kubernetes/
```

## Разработка

### Backend (Python/FastAPI)

```bash
cd execution-engine
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend (Next.js)

```bash
cd human-interface/web-app
npm install
npm run dev
```

### Тесты

```bash
# Unit тесты
pytest tests/unit

# Integration тесты
pytest tests/integration

# E2E тесты
pytest tests/e2e

# Все тесты
pytest
```

## Документация

- [Архитектура платформы](docs/ARCHITECTURE.md)
- [Руководство пользователя](docs/USER_GUIDE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Деплой](docs/DEPLOYMENT.md)
- [Соответствие ISO 22301](docs/ISO_22301_MAPPING.md)

## Технологии

**Backend:**
- Python 3.11, FastAPI, SQLAlchemy (async)
- PostgreSQL 15 (multi-tenant, RLS)
- Redis 7 (cache, real-time state)

**AI/ML:**
- OpenAI GPT-4 / Claude / Llama
- LangChain, AutoGen
- Neo4j (knowledge graph)
- Qdrant (vector store)

**Frontend:**
- React 18, Next.js 14 (App Router)
- TailwindCSS, shadcn/ui
- WebSocket (real-time)

**Infrastructure:**
- Docker, Kubernetes
- Prometheus, Grafana, Loki
- GitHub Actions (CI/CD)

## Roadmap

### Phase 1: MVP (Q1 2025)
- ✅ Intelligent Core (decision engine, digital twin)
- ✅ BIA + Risk workflows
- ✅ Web UI + AI chat

### Phase 2: Production (Q2 2025)
- Incident Response module
- Exercise & Validation
- ISO 22301 audit automation

### Phase 3: Scale (Q3 2025)
- Multi-region deployment
- Mobile app (React Native)
- Advanced analytics

## Лицензия

MIT License - см. [LICENSE](LICENSE)

## Контакты

- Email: support@bcm-platform.com
- Docs: https://docs.bcm-platform.com
- Issues: https://github.com/yourusername/AI-Platform-ISO/issues

---

🚀 Built with AI-First Architecture | 🏥 Healthcare-Specialized | ✅ ISO 22301 Compliant
