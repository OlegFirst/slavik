# Database Integration Progress

## Цель
Интеграция Community Level и Passive Learning с PostgreSQL базой данных.

## Текущий Статус: 60% Complete

### ✅ Выполнено (15 октября 2025)

#### 1. Database Migrations ✅
**Файл:** `/platform_services/D_T/digital_twin/alembic/versions/b7c8d9e0f1a2_add_community_and_learning_tables.py`

Создана Alembic миграция для всех необходимых таблиц:

**Community Level Tables:**
- `community_learnings` - Хранилище анонимизированных знаний
- `learning_feedback` - Обратная связь по применению знаний
- `user_networking_profiles` - Профили профессионалов для people matching
- `community_privacy_settings` - Настройки приватности

**Passive Learning Tables:**
- `learning_events` - Лог событий обучения (JSONB для insights)
- `learning_insights` - Накопленные инсайты (один инсайт на twin+type)
- `organization_contexts` - Кэш организационных контекстов

**Особенности:**
- Использование PostgreSQL ARRAY для списков (tags, skills, languages)
- JSONB для гибких данных (insights, patterns, trends)
- Индексы на все ключевые поля (industry, size, maturity, source, created_at)
- Foreign keys с cascade delete
- Unique constraint на (twin_id, insight_type)

#### 2. SQLAlchemy Models ✅
**Файл:** `/platform_services/D_T/digital_twin/storage/models.py`

Добавлены SQLAlchemy ORM модели:

- `CommunityLearningModel` - с relationship к feedback
- `LearningFeedbackModel`
- `UserNetworkingProfileModel`
- `CommunityPrivacySettingsModel`
- `LearningEventModel`
- `LearningInsightModel` - с unique constraint
- `OrganizationContextModel`

**Особенности:**
- Использование SQLAlchemy 2.0 синтаксиса (`Mapped[]`, `mapped_column()`)
- Правильная типизация (Optional, List, Dict)
- Relationships между моделями
- Автоматические timestamps (created_at, updated_at)
- Индексы для производительности

#### 3. Repository Layer ✅

**Файл 1:** `/platform_services/D_T/digital_twin/storage/community_repository.py`

**CommunityRepository** - Полный CRUD для Community Level:

**Knowledge Exchange:**
- `create_learning()` - Создать learning
- `get_learning()` - Получить по ID
- `query_learnings()` - Поиск с фильтрами (industry, size, maturity, tags, min_effectiveness)
- `get_top_learnings()` - Топ по usage и effectiveness
- `update_learning_metrics()` - Обновить метрики (times_used, success_rate)
- `get_community_statistics()` - Статистика Knowledge Exchange

**Learning Feedback:**
- `submit_feedback()` - Отправить feedback
- `get_learning_feedback()` - Получить feedback для learning

**People Matching:**
- `create_profile()` - Создать профиль
- `get_profile()` - Получить профиль
- `update_profile()` - Обновить профиль
- `delete_profile()` - Удалить профиль
- `search_profiles()` - Поиск профилей (role, experience, expertise, languages, mentoring)
- `get_network_statistics()` - Статистика People Matching

**Privacy:**
- `create_privacy_settings()` - Создать настройки
- `get_privacy_settings()` - Получить настройки
- `update_privacy_settings()` - Обновить настройки

**Файл 2:** `/platform_services/D_T/digital_twin/storage/learning_repository.py`

**LearningRepository** - Полный CRUD для Passive Learning:

**Learning Events:**
- `create_event()` - Создать event
- `get_event()` - Получить event по ID
- `get_events_for_twin()` - Получить события twin (с фильтрами source, since)
- `get_event_count()` - Количество событий
- `get_event_sources()` - Уникальные источники событий

**Learning Insights:**
- `upsert_insight()` - PostgreSQL UPSERT (INSERT ... ON CONFLICT UPDATE)
- `get_insight()` - Получить конкретный инсайт
- `get_all_insights()` - Все инсайты twin
- `get_insights_dict()` - Инсайты как словарь
- `delete_insight()` - Удалить инсайт

**Organization Contexts:**
- `upsert_context()` - PostgreSQL UPSERT для контекста
- `get_context()` - Получить контекст
- `delete_context()` - Удалить контекст
- `get_stale_contexts()` - Найти устаревшие контексты
- `get_similar_contexts()` - Найти похожие контексты

**Statistics:**
- `get_statistics()` - Глобальная или twin-specific статистика

**Особенности:**
- Использование PostgreSQL-specific фичей (ARRAY.overlap, INSERT...ON CONFLICT)
- Правильная работа с async sessions
- Логирование всех операций
- Оптимизированные запросы с индексами

### 🔄 В процессе

#### 4. Service Layer Updates (In Progress)

Необходимо обновить существующие сервисы для использования PostgreSQL вместо in-memory storage.

**Следующие файлы для обновления:**

1. `/platform_services/D_T/digital_twin/core/community/knowledge_exchange.py`
   - Заменить `self._learnings: Dict` на `CommunityRepository`
   - Использовать `repository.create_learning()`, `repository.query_learnings()`

2. `/platform_services/D_T/digital_twin/core/community/people_matching.py`
   - Заменить `self._profiles: Dict` на `CommunityRepository`
   - Использовать `repository.create_profile()`, `repository.search_profiles()`

3. `/platform_services/D_T/digital_twin/core/learning/passive_learning_engine.py`
   - Заменить `self._events: Dict` и `self._insights: Dict` на `LearningRepository`
   - Использовать `repository.create_event()`, `repository.upsert_insight()`

4. `/platform_services/D_T/digital_twin/core/learning/context_builder.py`
   - Заменить обращения к in-memory на `LearningRepository`
   - Использовать `repository.get_context()`, `repository.upsert_context()`

### 📋 Осталось сделать

#### 5. Service Layer Integration (Pending)
- [ ] Внедрить dependency injection для repositories в сервисах
- [ ] Обновить API routers для передачи database session
- [ ] Добавить transaction management

#### 6. Testing (Pending)
- [ ] Unit tests для repositories
- [ ] Integration tests для сервисов
- [ ] API endpoint tests
- [ ] Performance tests

#### 7. Database Setup (Pending)
- [ ] Запустить миграцию: `alembic upgrade head`
- [ ] Проверить создание всех таблиц
- [ ] Проверить индексы и constraints

## Архитектурные Решения

### 1. Repository Pattern
Используем Repository Pattern для изоляции database logic:
- **Repository Layer** - CRUD операции с базой данных
- **Service Layer** - Бизнес-логика, использует repositories
- **API Layer** - FastAPI endpoints, использует services

### 2. PostgreSQL-Specific Features

**ARRAY Types:**
```sql
tags TEXT[]
expertise_areas TEXT[]
languages TEXT[]
```
Используем SQLAlchemy ARRAY.overlap для фильтрации.

**JSONB Types:**
```sql
insights JSONB
patterns JSONB
trends JSONB
```
Гибкая схема для динамических данных.

**UPSERT:**
```python
INSERT INTO learning_insights (...)
VALUES (...)
ON CONFLICT (twin_id, insight_type)
DO UPDATE SET ...
```

### 3. Session Management

Repositories принимают `AsyncSession` в конструктор:
```python
repo = CommunityRepository(session)
```

Services будут использовать dependency injection:
```python
async def get_repository(session: AsyncSession = Depends(get_db_session)):
    return CommunityRepository(session)
```

### 4. Performance Optimizations

**Индексы:**
- Композитные индексы на часто используемых фильтрах
- UNIQUE constraints для upsert логики
- Index на foreign keys

**Кэширование:**
- `organization_contexts` - pre-built cache таблица
- Избегаем пересборки контекстов при каждом запросе

**Пагинация:**
- Все list методы имеют `limit` параметр
- Используем `.limit()` и `.offset()` для pagination

## Timeline

**15 октября 2025:**
- ✅ Миграции созданы
- ✅ Models созданы
- ✅ Repositories созданы

**Следующие шаги (1-2 дня):**
- 🔄 Обновить сервисы (Knowledge Exchange, People Matching)
- 🔄 Обновить сервисы (Passive Learning, Context Builder)
- 🔄 Обновить API routers

**Затем (2-3 дня):**
- ⏳ Тестирование
- ⏳ Запуск миграций
- ⏳ Performance tuning

## Примеры Использования

### Community Repository

```python
# Knowledge Exchange
async with session() as db:
    repo = CommunityRepository(db)

    # Create learning
    learning = await repo.create_learning({
        'learning_id': str(uuid4()),
        'tenant_id': tenant_id,
        'title': 'Anonymized Title',
        'challenge': '...',
        'solution': '...',
        'outcome': '...',
        'industry': 'finance',
        'size_category': 'medium',
        'maturity_level': 'level_3',
        'effectiveness_score': 0.85,
        'times_used': 0,
        'success_rate': 0.0,
        'anonymization_level': 'standard',
        'contributor_twin_id': twin_id,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    })

    # Query learnings
    learnings = await repo.query_learnings(
        industry='finance',
        size_category='medium',
        min_effectiveness=0.7,
        limit=10
    )
```

### Learning Repository

```python
# Passive Learning
async with session() as db:
    repo = LearningRepository(db)

    # Create event
    event = await repo.create_event({
        'event_id': str(uuid4()),
        'twin_id': twin_id,
        'tenant_id': tenant_id,
        'source': 'bia',
        'insights': {
            'risk_tolerance': 'medium',
            'decision_speed': 'fast',
            'critical_functions': ['payment_processing', 'customer_support']
        },
        'confidence': 0.8,
        'created_at': datetime.utcnow()
    })

    # Upsert insight (PostgreSQL UPSERT)
    insight = await repo.upsert_insight({
        'id': str(uuid4()),
        'twin_id': twin_id,
        'tenant_id': tenant_id,
        'insight_type': 'risk_tolerance',
        'insight_value': {'value': 'medium', 'source': 'bia'},
        'confidence': 0.8,
        'source_event_count': 1,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    })

    # Get all insights as dict
    insights_dict = await repo.get_insights_dict(twin_id)
    # {'risk_tolerance': {'value': 'medium', ...}, 'decision_speed': {...}}

    # Upsert context
    context = await repo.upsert_context({
        'twin_id': twin_id,
        'tenant_id': tenant_id,
        'risk_tolerance': 'medium',
        'decision_speed': 'fast',
        'critical_functions': ['payment_processing'],
        'total_events': 15,
        'confidence_score': 0.75,
        'created_at': datetime.utcnow(),
        'last_updated': datetime.utcnow()
    })
```

## Статус
**60% Complete** - Database layer готов, нужна интеграция с сервисами.
