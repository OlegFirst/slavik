# Portal Service

**Port:** 8031
**Цель:** Knowledge Hub + Scenario Marketplace + Community Forum + Client Dashboard

---

## 🎯 Обзор

Portal Service - это микросервис платформы BCM, предоставляющий:

1. **Knowledge Hub** - База знаний по Business Continuity Management
2. **Scenario Marketplace** - Каталог готовых сценариев учений
3. **Community Forum** - Форум с обсуждениями, модерацией и геймификацией
4. **Client Dashboard** - Панель клиента с аналитикой

### Ключевые возможности

✅ **Реализовано (MVP):**

**Knowledge Hub:**
- Knowledge articles с Markdown/HTML
- Full-text search (PostgreSQL)
- Voting система (upvote/downvote)
- Bookmarks для статей
- AI генерация статей из учений
- Expert verification для AI контента

**Scenario Marketplace:**
- Scenario catalog с фильтрацией
- One-click deployment сценариев в учения
- Scenario reviews и ratings

**Community Forum:**
- Categories и Topics с вложенностью
- Posts с nested replies
- Voting на topics и posts
- Moderation система (flags, queue)
- Reputation & Gamification (badges, leaderboard)
- Integration с Knowledge Hub (обсуждения статей)

**Platform:**
- Multi-tenancy с Row Level Security
- JWT authentication через Clients service

🔜 **Phase 2:**
- Elasticsearch для advanced search
- Real-time уведомления
- Content recommendations
- Analytics dashboard

---

## 📊 Архитектура

### Компоненты

```
portal/
├── database/           # SQLAlchemy модели + миграции
├── api/               # FastAPI endpoints
├── services/          # Business logic
├── schemas/           # Pydantic schemas
├── integrations/      # HTTP clients для других сервисов
├── tests/             # Unit & integration tests
└── main.py            # FastAPI app
```

### Интеграции

**Зависимости:**
- **Clients Service (8030)** - Аутентификация, user profiles
- **Validation Module (8022)** - Exercise integration, AI article generation source
- **AI Orchestrator** - AI content generation

**База данных:**
- PostgreSQL schema: `portal.*`
- Async SQLAlchemy 2.0 + asyncpg
- Row Level Security для multi-tenancy

---

## 🗄️ База Данных

### Схема: `portal.*`

**Таблицы:**

1. **knowledge_articles** - Статьи базы знаний
   - Content (Markdown + cached HTML)
   - Categorization (category, tags, ISO clause)
   - AI generation metadata
   - Verification workflow
   - Engagement metrics (views, votes, usefulness score)

2. **article_bookmarks** - Закладки пользователей
3. **article_votes** - Голосование за статьи
4. **scenarios** - Каталог сценариев учений
5. **scenario_reviews** - Отзывы на сценарии

### Миграции

Запуск SQL миграций:

```bash
# Подключиться к PostgreSQL
psql -U bcm_user -d bcm_platform

# Выполнить миграции
\i database/migrations/001_initial_portal_schema.sql
\i database/migrations/002_add_scenarios.sql
```

### Индексы

**Performance optimization:**
- GIN индекс для full-text search
- JSONB индексы для tags
- Composite индексы для фильтрации (tenant_id, published, category)
- Index на usefulness_score для ранжирования

---

## 🚀 Quick Start

### Локальный запуск

```bash
# 1. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Настроить .env
cp .env.example .env
# Отредактировать DATABASE_URL и service URLs

# 4. Запустить миграции БД
psql -U bcm_user -d bcm_platform -f database/migrations/001_initial_portal_schema.sql
psql -U bcm_user -d bcm_platform -f database/migrations/002_add_scenarios.sql

# 5. Запустить сервис
uvicorn main:app --host 0.0.0.0 --port 8031 --reload
```

### Docker запуск

```bash
# Запустить с docker-compose
docker-compose up -d

# Проверить логи
docker-compose logs -f portal

# Остановить
docker-compose down
```

### Проверка работы

```bash
# Health check
curl http://localhost:8031/health

# API документация
open http://localhost:8031/docs
```

---

## 📚 API Endpoints

### Knowledge Hub

**Articles:**
- `POST /api/portal/knowledge/articles` - Создать статью
- `GET /api/portal/knowledge/articles` - Список статей (с фильтрацией)
- `GET /api/portal/knowledge/articles/{id}` - Получить статью
- `PATCH /api/portal/knowledge/articles/{id}` - Обновить статью

**Search:**
- `GET /api/portal/knowledge/search?query=RTO` - Full-text search

**Voting:**
- `POST /api/portal/knowledge/articles/{id}/vote` - Проголосовать
- `DELETE /api/portal/knowledge/articles/{id}/vote` - Удалить голос

**Bookmarks:**
- `POST /api/portal/knowledge/articles/{id}/bookmark` - Добавить в закладки
- `DELETE /api/portal/knowledge/articles/{id}/bookmark` - Удалить закладку
- `GET /api/portal/knowledge/bookmarks` - Мои закладки

**AI Generation:**
- `POST /api/portal/knowledge/ai-generate` - Генерация статьи из учения

**Verification (Specialist/Admin only):**
- `POST /api/portal/knowledge/articles/{id}/verify` - Верифицировать статью

### Scenario Marketplace

**Scenarios:**
- `GET /api/portal/scenarios` - Каталог сценариев
- `GET /api/portal/scenarios/{id}` - Детали сценария

**Deployment:**
- `POST /api/portal/scenarios/{id}/deploy` - Развернуть как учение

**Reviews:**
- `POST /api/portal/scenarios/{id}/reviews` - Оставить отзыв
- `GET /api/portal/scenarios/{id}/reviews` - Получить отзывы

**Featured:**
- `GET /api/portal/scenarios/featured/popular` - Популярные сценарии

### Community Forum

**Categories & Topics:**
- `GET /api/portal/forum/categories` - Список категорий
- `GET /api/portal/forum/topics` - Список тем (с фильтрами)
- `POST /api/portal/forum/topics` - Создать тему
- `GET /api/portal/forum/topics/{id}` - Получить тему
- `PATCH /api/portal/forum/topics/{id}` - Обновить тему

**Posts:**
- `GET /api/portal/forum/topics/{id}/posts` - Посты в теме
- `POST /api/portal/forum/topics/{id}/posts` - Создать пост
- `PATCH /api/portal/forum/posts/{id}` - Обновить пост

**Voting:**
- `POST /api/portal/forum/topics/{id}/vote` - Голосовать за тему
- `POST /api/portal/forum/posts/{id}/vote` - Голосовать за пост
- `POST /api/portal/forum/posts/{id}/mark-solution` - Отметить как решение

**Moderation:**
- `POST /api/portal/forum/topics/{id}/flag` - Пожаловаться на тему
- `POST /api/portal/forum/posts/{id}/flag` - Пожаловаться на пост
- `GET /api/portal/forum/moderation/queue` - Очередь модерации (Specialist)
- `POST /api/portal/forum/moderation/flags/{id}/resolve` - Обработать жалобу

**Gamification:**
- `GET /api/portal/forum/reputation/{user_id}` - Репутация пользователя
- `GET /api/portal/forum/leaderboard` - Лидерборд
- `GET /api/portal/forum/badges` - Все бейджи
- `GET /api/portal/forum/users/{user_id}/badges` - Бейджи пользователя
- `GET /api/portal/forum/stats` - Статистика форума

**Integration:**
- `POST /api/portal/knowledge/articles/{id}/discuss` - Создать обсуждение статьи
- `GET /api/portal/knowledge/articles/{id}/discussion` - Получить обсуждение

---

## 🔐 Аутентификация

Все защищённые endpoints требуют JWT token от Clients service:

```bash
curl -H "Authorization: Bearer <jwt_token>" \
  http://localhost:8031/api/portal/knowledge/articles
```

### Получение токена

```bash
# Логин через Clients service
curl -X POST http://localhost:8030/api/clients/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password"}'

# Ответ:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

---

## 💡 Примеры использования

### 1. Создать статью

```bash
curl -X POST http://localhost:8031/api/portal/knowledge/articles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "How to conduct effective BIA",
    "summary": "Best practices for Business Impact Analysis in financial sector",
    "content": "# Introduction\n\nBusiness Impact Analysis (BIA) is...",
    "category": "BIA",
    "tags": ["BIA", "ISO 22301", "Financial"],
    "iso_clause": "8.2"
  }'
```

### 2. Поиск статей

```bash
curl "http://localhost:8031/api/portal/knowledge/search?query=RTO%20RPO&category=BIA&verified_only=true"
```

### 3. Проголосовать за статью

```bash
# Upvote
curl -X POST http://localhost:8031/api/portal/knowledge/articles/1/vote \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"vote": 1}'

# Downvote
curl -X POST http://localhost:8031/api/portal/knowledge/articles/1/vote \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"vote": -1}'
```

### 4. AI генерация статьи из учения

```bash
curl -X POST http://localhost:8031/api/portal/knowledge/ai-generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exercise_id": 123,
    "category": "Lessons Learned",
    "tags": ["Ransomware", "Incident Response"]
  }'
```

### 5. Развернуть сценарий как учение

```bash
curl -X POST http://localhost:8031/api/portal/scenarios/1/deploy \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "org-123",
    "exercise_name_override": "Q1 2024 Ransomware Drill"
  }'
```

---

## 🧪 Тестирование

### Unit Tests

```bash
# Запустить все тесты
pytest

# С покрытием
pytest --cov=. --cov-report=html

# Конкретный тест
pytest tests/test_knowledge_service.py::test_create_article
```

### Integration Tests

```bash
# Требует запущенную БД
pytest tests/integration/

# С выводом логов
pytest tests/integration/ -v -s
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# Service URLs
CLIENTS_SERVICE_URL=http://localhost:8030
VALIDATION_SERVICE_URL=http://localhost:8022
AI_ORCHESTRATOR_URL=http://localhost:8000

# Server
PORT=8031
DEBUG=true

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Logging
LOG_LEVEL=INFO
```

---

## 📊 Business Logic

### Usefulness Score

Формула ранжирования статей:

```python
usefulness_score = (upvotes * 2 - downvotes) + (view_count / 100)
```

**Примеры:**
- Статья с 50 upvotes, 5 downvotes, 1000 views: `(50*2 - 5) + (1000/100) = 95 + 10 = 105`
- Статья с 10 upvotes, 0 downvotes, 500 views: `(10*2 - 0) + (500/100) = 20 + 5 = 25`

### Verification Workflow

1. **AI генерация** → статус `pending`, `ai_generated=true`
2. **Specialist review** → статус `verified` или `rejected`
3. **Publishing** → только verified статьи можно публиковать

### Full-Text Search

**PostgreSQL ts_rank:**

```sql
SELECT id, title,
       ts_rank(to_tsvector('english', title || ' ' || content),
               plainto_tsquery('english', 'RTO RPO')) AS relevance
FROM portal.knowledge_articles
WHERE to_tsvector('english', title || ' ' || content)
      @@ plainto_tsquery('english', 'RTO RPO')
ORDER BY relevance DESC;
```

---

## 🚧 Roadmap

### ✅ MVP (Реализовано)

- Knowledge articles CRUD
- PostgreSQL full-text search
- Voting & bookmarks
- AI generation from exercises
- Scenario catalog & deployment
- Reviews & ratings

### 🔜 Phase 2

- [ ] Elasticsearch integration
- [ ] Real-time notifications (WebSocket)
- [ ] Content recommendations engine
- [ ] Analytics dashboard
- [ ] Article versioning
- [ ] Comments/discussions on articles
- [ ] Author reputation system

### 🌟 Phase 3

- [ ] Multi-language support
- [ ] PDF export
- [ ] Advanced analytics (read time, engagement)
- [ ] Knowledge graphs
- [ ] Integration with Learning module

---

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Проверить доступность PostgreSQL
pg_isready -h localhost -p 5432

# Проверить пользователя
psql -U bcm_user -d bcm_platform -c "SELECT version();"

# Проверить схему
psql -U bcm_user -d bcm_platform -c "\dn portal"
```

### Миграции не применились

```bash
# Проверить текущее состояние
psql -U bcm_user -d bcm_platform -c "\dt portal.*"

# Применить вручную
psql -U bcm_user -d bcm_platform < database/migrations/001_initial_portal_schema.sql
```

### Service Integration Errors

```bash
# Проверить доступность Clients service
curl http://localhost:8030/health

# Проверить доступность Validation
curl http://localhost:8022/health
```

---

## 📖 Документация

- **API Docs:** http://localhost:8031/docs (Swagger UI)
- **ReDoc:** http://localhost:8031/redoc
- **Спецификация:** `PORTAL_SERVICE_SPEC.md`
- **Стратегия:** `IMPLEMENTATION_STRATEGY.md`

---

## 🤝 Contributing

При добавлении нового функционала:

1. Обновить database models
2. Создать SQL миграцию
3. Добавить Pydantic schemas
4. Реализовать business logic в services/
5. Добавить API endpoints
6. Написать tests
7. Обновить README

---

---

## 🎮 Forum Gamification

### Reputation System

**Как заработать репутацию:**
- Создать тему: +2 очка
- Создать пост: +1 очко
- Пост проголосовали вверх: +5 очков
- Пост проголосовали вниз: -2 очка
- Тему проголосовали вверх: +3 очка
- Пост отмечен как решение: +15 очков
- Получить бейдж: +10-50 очков (зависит от бейджа)

**Уровни репутации:**
- 🆕 Newbie: 0-99
- 👤 Contributor: 100-499
- ⭐ Expert: 500-999
- 🏆 Guru: 1000-2499
- 👑 Legend: 2500+

### Badges (Бейджи)

**Certification (Gold):**
- 🥇 ISO 22301 Lead Implementer
- 🥇 ISO 22301 Lead Auditor
- 🥇 BCI Certified Professional

**Achievement:**
- 🥉 First Post (Bronze) - Первый пост
- 🥈 Helpful (Silver) - 50+ upvotes
- 🥇 Expert Contributor (Gold) - 100+ постов
- 🥇 Problem Solver (Gold) - 10 решений

**Reputation:**
- 🥉 Rising Star - 100 очков
- 🥈 Community Leader - 1000 очков
- 🥇 BCM Guru - 2500 очков

### Leaderboard

```bash
# Получить топ пользователей
curl http://localhost:8031/api/portal/forum/leaderboard?period=all_time&limit=50
```

---

**Разработано:** Claude Code
**Дата:** 2025-10-02
**Статус:** ✅ Full MVP Реализован (Knowledge Hub + Scenarios + Forum + Platform Integration)

---

## 🔗 Platform Integration

Portal Service полностью интегрирован с BCM Platform:

✅ **Gateway Registration** - Доступен через API Gateway (Port 8000)
✅ **EventBus Integration** - Эмитит события для всех активностей
✅ **Docker Orchestration** - Часть Platform docker-compose stack
✅ **Service Discovery** - Зарегистрирован в service registry

**Документация:**
- 📖 [Platform Integration Guide](./PLATFORM_INTEGRATION.md)
- 🚀 [Deployment Guide](./DEPLOYMENT.md)

**Запуск всей платформы:**
```bash
cd /Users/MD/ISO-22301—копия/services/SERVICES/PLATFORM
docker-compose -f docker-compose.platform.yml up -d
```
