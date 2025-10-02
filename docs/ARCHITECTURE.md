# Архитектура AI-Powered BCM Platform

## Обзор

Платформа построена на AI-first архитектуре с тремя функциональными слоями:

```
┌─────────────────────────────────┐
│     INTELLIGENT CORE            │  ← AI мозг
│  • AI Orchestration Engine      │
│  • Knowledge System             │
│  • Digital Twin Simulator       │
└─────────────────────────────────┘
            ↓
┌─────────────────────────────────┐
│     EXECUTION ENGINE            │  ← BCM workflows
│  • PLAN Workflow                │
│  • DO Workflow                  │
│  • CHECK Workflow               │
│  • ACT Workflow                 │
│  • 9 BCM Capabilities           │
└─────────────────────────────────┘
            ↓
┌─────────────────────────────────┐
│     HUMAN INTERFACE             │  ← Пользовательский интерфейс
│  • Web Application              │
│  • API Gateway                  │
│  • AI Chat                      │
└─────────────────────────────────┘
```

## Принципы архитектуры

### 1. AI-First, Not AI-Added
AI не дополнение, а фундамент. Все решения проходят через Intelligent Core.

### 2. Workflows Over Services
Вместо 10 независимых микросервисов - 4 workflow по ISO 22301 PDCA:
- **PLAN**: Context → Risk → BIA → Strategy → Plans
- **DO**: Incident → Activation → Response → Recovery
- **CHECK**: Exercise → Measure → Audit → Review
- **ACT**: Gaps → CAPA → Implement → Verify

### 3. Digital Twin для симуляции
Уникальная возможность тестировать сбои до того, как они произойдут.

### 4. Healthcare-специализация
WHO Tier 1-4 framework, patient safety, HIPAA compliance.

### 5. Предиктивность
Предсказываем и готовимся, а не только реагируем.

## Технический стек

### Backend
- **Python 3.11** + FastAPI + SQLAlchemy (async)
- **PostgreSQL 15** (multi-tenant с RLS)
- **Redis 7** (кэш, real-time state)

### AI/ML
- **OpenAI GPT-4** / **Anthropic Claude** / **Llama**
- **LangChain** для AI orchestration
- **Neo4j** для knowledge graph
- **Qdrant** для vector store

### Frontend
- **React 18** + **Next.js 14** (App Router)
- **TailwindCSS** для стилей
- **WebSocket** для real-time

### Infrastructure
- **Docker** + **docker-compose** (development)
- **Kubernetes** (production)
- **Prometheus** + **Grafana** (monitoring)

## Компоненты

### Intelligent Core (порт 9000)

**AI Orchestration Engine:**
- Decision Engine - принятие решений
- Pattern Recognition - обучение на истории
- Predictive Models - прогнозирование
- Optimization Engine - выбор оптимальных стратегий

**Knowledge System:**
- BCM Domain Knowledge (ISO 22301, BCI)
- Organization Context
- Historical Data
- Threat Intelligence

**Digital Twin:**
- Process Model
- Dependency Graph
- Resource Model
- Disruption Simulator

**API Endpoints:**
- `POST /api/v1/decisions/make` - AI принимает решение
- `POST /api/v1/digital-twin/simulate` - симуляция сбоя
- `GET /api/v1/knowledge/bcm/{topic}` - BCM знания
- `POST /api/v1/optimization/recommend-strategy` - рекомендация стратегии
- `POST /api/v1/chat` - conversational interface

### Execution Engine (порт 8000)

**Workflows:**
- PLAN Workflow (ISO Clause 4-7)
- DO Workflow (ISO Clause 8)
- CHECK Workflow (ISO Clause 9)
- ACT Workflow (ISO Clause 10)

**Capabilities (9 BCM модулей):**
1. **Governance** - политики, контекст, stakeholders
2. **Analysis** - BIA + Risk Assessment
3. **Strategy** - стратегии восстановления
4. **Planning** - BC планы
5. **Response** - управление инцидентами
6. **Learning** - обучение персонала
7. **Validation** - учения и тесты
8. **Compliance** - аудит ISO 22301, CAPA
9. **Documents** - управление документами

**API Endpoints:**
- `POST /api/v1/workflows/{workflow}/execute`
- `GET/POST /api/v1/capabilities/bia/processes`
- `GET/POST /api/v1/capabilities/risk/assessments`
- `POST /api/v1/capabilities/risk/{id}/fair-analysis`
- `GET/POST /api/v1/capabilities/planning/plans`
- `GET/POST /api/v1/capabilities/response/incidents`
- `GET /api/v1/capabilities/compliance/iso22301/audit`

### API Gateway (порт 3001)

**Функции:**
- Единая точка входа для всех API
- Маршрутизация на Intelligent Core / Execution Engine
- JWT аутентификация
- Rate limiting
- WebSocket для real-time

**Routes:**
- `/api/v1/ai/*` → Intelligent Core
- `/api/v1/bcm/*` → Execution Engine
- `/api/v1/dashboard/overview` - aggregated data
- `/ws` - WebSocket endpoint

### Web Application (порт 3000)

**Next.js 14 App Router:**
- `/` - Dashboard
- `/bia` - Business Impact Analysis
- `/risk` - Risk Assessment
- `/plans` - BC Plans
- `/incidents` - Incident Command Center
- `/compliance` - ISO 22301 Compliance
- `/ai-chat` - AI Conversational Interface

## Уникальные возможности

### 1. Digital Twin Simulation (UNIQUE)
Симуляция сбоев с предсказанием каскадных эффектов:
```python
POST /api/v1/digital-twin/simulate
{
  "disruption_type": "ransomware",
  "affected_assets": ["Primary Data Center"],
  "recovery_strategy": {...}
}

Response:
{
  "timeline": [hour 0, 1, 2, 4...],
  "total_financial_loss": 475000,
  "rto_achieved": false,
  "recommendations": [...]
}
```

### 2. FAIR + Monte Carlo (RARE)
Количественный анализ рисков:
```python
POST /api/v1/capabilities/risk/{id}/fair-analysis

Response:
{
  "loss_event_frequency": 1.875/year,
  "loss_magnitude": 750000,
  "annual_loss_expectancy": 1406250,
  "confidence_interval": [850000, 2100000]
}
```

### 3. AI Scenario Generation (UNIQUE)
AI генерирует реалистичные сценарии для учений на основе:
- Истории инцидентов организации
- Threat intelligence feeds
- Индустриальных best practices

### 4. Automated ISO 22301 Audit (RARE)
Автоматическая проверка соответствия каждому clause:
```python
GET /api/v1/capabilities/compliance/iso22301/audit

Response:
{
  "overall_compliance": "87%",
  "clauses": [...],
  "gaps": [...]
}
```

### 5. Healthcare Specialization (NICHE)
- WHO Tier 1-4 essential services встроены
- Patient safety impact в BIA
- HIPAA compliance checks
- EHR-specific recovery procedures

## Deployment

### Development (Docker Compose)
```bash
docker-compose up -d
```

Сервисы:
- PostgreSQL (5432)
- Redis (6379)
- Intelligent Core (9000)
- Execution Engine (8000)
- API Gateway (3001)
- Web App (3000)

### Production (Kubernetes)
```bash
kubectl apply -f infrastructure/kubernetes/
```

## Security

- **Multi-tenancy**: PostgreSQL Row-Level Security (RLS)
- **Authentication**: JWT tokens
- **Authorization**: Role-based access control (RBAC)
- **Encryption**: TLS/SSL для всех коммуникаций
- **Secrets**: Kubernetes secrets / HashiCorp Vault

## Monitoring

- **Metrics**: Prometheus
- **Dashboards**: Grafana
- **Logs**: Loki
- **Tracing**: Jaeger (опционально)

## Next Steps

1. Добавить real database integration (PostgreSQL)
2. Реализовать AI capabilities с real LLM
3. Создать Digital Twin engine
4. Построить полноценный frontend
5. Добавить authentication/authorization
6. Настроить CI/CD pipeline

## Соответствие ISO 22301

| Clause | Requirement | Implementation |
|--------|-------------|----------------|
| 4 | Context | Governance module |
| 5 | Leadership | Governance module |
| 6 | Planning | PLAN workflow |
| 7 | Support | All modules |
| 8 | Operation | DO workflow |
| 9 | Performance | CHECK workflow |
| 10 | Improvement | ACT workflow |

---

**Status**: MVP готов к development
**Next**: Database integration + AI implementation
