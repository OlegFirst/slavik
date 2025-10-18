# Community Service

Платформенный сервис для управления сообществом BCM-специалистов.

## Структура

```
community-service/
├── portal/                 # Community Portal (форум, база знаний, новости)
│   ├── api/               # REST API endpoints
│   ├── services/          # Business logic
│   ├── database/          # Models and migrations
│   ├── integrations/      # EventBus, Marketplace clients
│   └── main.py           # FastAPI application
│
├── marketplace/           # Professional Marketplace (Uber для BCM консультантов)
│   ├── api/              # REST API endpoints
│   ├── services/         # Business logic
│   ├── database/         # Models and migrations
│   ├── integrations/     # EventBus, Portal clients
│   └── main.py          # FastAPI application
│
├── shared/               # Shared code
│   ├── database/         # Supabase connection manager
│   ├── auth/            # Authentication utilities
│   └── events/          # EventBus integration
│
└── migrations/          # Database migrations для community schemas
```

## Запуск

### Portal Service

```bash
cd portal
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8031 --reload
```

**Endpoints:**
- Health: http://localhost:8031/health
- API Docs: http://localhost:8031/docs
- 38 endpoints total

### Marketplace Service

```bash
cd marketplace
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8032 --reload
```

**Endpoints:**
- Health: http://localhost:8032/health
- API Docs: http://localhost:8032/docs
- 46 endpoints total

## База данных

**Supabase (Platform Level):**
- Connection через `shared/database/connection.py`
- Schemas: `portal`, `marketplace`
- Multi-tenant с Row Level Security
- Session pooler для IPv4 compatibility

**Environment Variables:**
```bash
DATABASE_URL=postgresql://postgres.xxx:xxx@aws-1-eu-north-1.pooler.supabase.com:5432/postgres
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJxxx...
```

## Интеграция

**EventBus:**
- Portal: 15 event types
- Marketplace: 11 event types
- Асинхронная межсервисная коммуникация

**Cross-service:**
- Portal ↔ Marketplace API clients
- Marketplace specialists в Portal articles
- Portal knowledge в Marketplace projects

## Архитектурное решение

**Почему отдельные сервисы?**
- Portal = Community (public content)
- Marketplace = Commerce (transactions, payments)
- Разная безопасность и scaling
- Следует industry best practices (LinkedIn, Stack Overflow)

См. `marketplace/ARCHITECTURE_DECISION.md` для деталей.

## Документация

- [Portal README](portal/README.md)
- [Marketplace README](marketplace/README.md)
- [Integration Guide](marketplace/CROSS_SERVICE_INTEGRATION.md)
- [Migration Guide](migrations/README.md)

## Статус

- ✅ Portal Service: 100% MVP Ready (38 endpoints)
- ✅ Marketplace Service: 100% MVP Ready (46 endpoints)
- ✅ EventBus Integration: Complete
- ✅ Cross-service Integration: Complete
- ⏳ Supabase Migration: In Progress
