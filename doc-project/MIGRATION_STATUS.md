# Database Migration Status - Community Intelligence

## ✅ Миграция завершена!

### Supabase Connection
- **URL**: `https://tpdkhddtbhpoqzzgxfni.supabase.co`
- **Region**: EU North 1 (AWS)
- **Status**: ✅ Connected

---

## Созданные таблицы (6/6)

### 1. `case_contributions` ✅
- Хранит community-contributed workflow cases
- Поля: id, contributor_id, case_data (JSONB), status, reviewers, tags, module
- RLS: Включен (owner + reviewers видят draft, все видят approved)

### 2. `peer_reviews` ✅
- Peer review submissions для contributions
- Поля: id, contribution_id, reviewer_id, approved, quality_score, feedback
- RLS: Включен (reviewers могут создавать, видят только свои contributions)

### 3. `user_reputation` ✅
- Multi-dimensional reputation system
- Поля: user_id (PK), total_points, level, contribution_points, review_points, expertise (JSONB), badges
- Levels: newcomer (0-99), contributor (100-499), expert (500-1999), master (2000+)
- RLS: Все могут читать, только система может обновлять

### 4. `reputation_transactions` ✅
- Audit trail для reputation changes
- Поля: id, user_id, points, reason, related_contribution_id, timestamp
- RLS: User видит только свои транзакции

### 5. `community_annotations` ✅
- Expert interpretations of standard clauses
- Поля: id, clause_id, standard, author_id, interpretation, industry_specific, upvotes, downvotes
- RLS: Все читают, authenticated могут создавать, author может обновлять

### 6. `synthesized_guidance` ✅
- AI-synthesized guidance from multiple sources
- Поля: id, clause_id (unique), unified_guidance, practical_steps, common_pitfalls, success_patterns
- RLS: Все могут читать

---

## Indexes & Optimization

### Созданы индексы для:
- `case_contributions`: contributor_id, status, submitted_at, module
- `peer_reviews`: contribution_id, reviewer_id
- `user_reputation`: total_points (для leaderboard)
- `reputation_transactions`: user_id, timestamp
- `community_annotations`: clause_id, author_id

---

## Row Level Security (RLS)

✅ **Включен на всех таблицах**

### Политики безопасности:
1. **Case Contributions**: 
   - Owner видит все свои
   - Reviewers видят assigned contributions
   - Все видят approved cases

2. **Peer Reviews**:
   - Только assigned reviewers могут создавать
   - Visibility следует за contributions

3. **User Reputation**:
   - Public read (leaderboard)
   - Service-only write (через backend API)

4. **Reputation Transactions**:
   - User видит только свои

5. **Community Annotations**:
   - Public read
   - Authenticated write
   - Author-only update

6. **Synthesized Guidance**:
   - Public read (все могут использовать)

---

## Triggers

✅ **Auto-update timestamps:**
- `case_contributions.updated_at`
- `community_annotations.updated_at`
- `synthesized_guidance.updated_at`
- `user_reputation.updated_at`

---

## API Endpoints Ready

### 17 эндпоинтов готовы к использованию:

#### Case Contributions (4)
1. `POST /api/v1/community/contributions` - Submit case
2. `GET /api/v1/community/contributions/{id}` - Get details
3. `GET /api/v1/community/contributions/pending-reviews` - Assigned reviews
4. `POST /api/v1/community/contributions/{id}/review` - Submit review

#### Reputation (2)
5. `GET /api/v1/community/reputation/{user_id}` - User reputation
6. `GET /api/v1/community/reputation/leaderboard` - Top contributors

#### Living Documentation (4)
7. `POST /api/v1/community/annotations` - Add interpretation
8. `GET /api/v1/community/guidance/{clause_id}` - Get guidance
9. `POST /api/v1/community/annotations/{id}/vote` - Vote
10. `GET /api/v1/community/clauses/search` - Search clauses

#### Predictive Timeline (3)
11. `POST /api/v1/community/timeline/predict` - Generate timeline
12. `GET /api/v1/community/timeline/{org_id}/next-steps` - Next actions
13. `GET /api/v1/community/insights/similar-orgs/{org_id}` - Similar orgs

#### Marketplace (1)
14. `GET /api/v1/community/marketplace/demand-forecast` - Expert demand

#### Statistics (2)
15. `GET /api/v1/community/stats/community` - Community stats
16. `GET /api/v1/community/stats/impact` - Impact metrics

#### Health (1)
17. `GET /api/v1/community/health` - Health check

---

## Next Steps

### 1. Настроить LLM API Keys ⚠️

**Требуется:**
```bash
# В .env файле замените:
OPENAI_API_KEY=sk-your-actual-key-here
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

**Где получить:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/account/keys

### 2. Запустить Community Intelligence API

```bash
cd /Users/MD/AI-Platform-ISO
uvicorn intelligent-core.community_intelligence.api.main:app --reload --port 8100
```

### 3. Проверить работу

```bash
# Health check
curl http://localhost:8100/api/v1/community/health

# Community stats
curl http://localhost:8100/api/v1/community/stats/community

# OpenAPI docs
open http://localhost:8100/docs
```

### 4. Создать первых пользователей

Через Supabase Auth или напрямую в `user_reputation`:
```sql
INSERT INTO user_reputation (user_id, total_points, level)
VALUES ('00000000-0000-0000-0000-000000000001', 0, 'newcomer');
```

### 5. Тестирование с пилотами

- Загрузить первые 3-5 workflow cases
- Настроить peer review с 2-3 экспертами
- Создать аннотации для ISO 22301 clauses
- Проверить predictive timeline

---

## Проверка БД

### Подключиться к Supabase:
```bash
export PGPASSWORD='K@x3ta9V8GK5rnW'
psql -h aws-1-eu-north-1.pooler.supabase.com \
     -U postgres.tpdkhddtbhpoqzzgxfni \
     -d postgres \
     -p 5432
```

### Полезные запросы:
```sql
-- Проверить все таблицы
\dt

-- Посмотреть структуру
\d case_contributions

-- Проверить RLS
SELECT tablename, policyname 
FROM pg_policies 
WHERE tablename LIKE '%case%' OR tablename LIKE '%reputation%';

-- Проверить индексы
\di

-- Статистика
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Статус готовности

### Database ✅
- [x] Supabase подключение
- [x] 6 таблиц Community Intelligence
- [x] RLS policies настроены
- [x] Индексы созданы
- [x] Triggers работают

### API ✅
- [x] 17 REST эндпоинтов
- [x] Request/Response models
- [x] OpenAPI документация
- [x] Error handling

### Integration ⚠️
- [ ] LLM API keys (нужны настоящие ключи)
- [x] Database connection (работает)
- [x] Authentication (Supabase Auth ready)
- [ ] Vector DB (опционально, для semantic search)

### Testing 🔄
- [ ] Unit tests
- [ ] Integration tests
- [ ] Load testing
- [ ] Security audit

---

## Платформа готова к запуску! 🚀

**Что имеем:**
- ✅ Community Intelligence БД (6 таблиц)
- ✅ REST API (17 эндпоинтов)
- ✅ Workflow Intelligence
- ✅ Governance System
- ✅ Blue Ocean архитектура

**Что нужно:**
- ⚠️ LLM API ключи
- 🔄 Первые пользователи для тестирования

**Готово для:**
- 12 государственных структур (ваш контракт)
- NPO в healthcare
- Community launch

---

**Дата**: 2025-10-04  
**Статус**: ✅ Migration Complete  
**Таблиц**: 6/6  
**API Endpoints**: 17/17  
**RLS**: Enabled
