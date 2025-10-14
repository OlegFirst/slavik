# Community Intelligence Foundation

Полноценный модуль для создания саморазвивающейся платформы BCM через коллективный интеллект.

## 🎯 Основные возможности

### 1. **Case Contributions & Peer Review**
- Пользователи делятся своими workflow-кейсами
- Автоматическая анонимизация (Smart Anonymizer)
- Peer review система (3 рецензента)
- Одобренные кейсы → Case Library

### 2. **Multi-Dimensional Reputation System**
- Очки за вклад, рецензии, помощь
- 4 уровня: newcomer → contributor → expert → master
- Экспертиза по доменам (BIA, Risk, Planning)
- Бейджи и достижения

### 3. **Living Documentation**
- Эксперты добавляют интерпретации стандартов
- AI синтезирует: официальный текст + community + кейсы
- Голосование за качество интерпретаций
- Результат: практическое руководство, постоянно улучшающееся

### 4. **Predictive Timeline**
- Предсказание journey организации
- ML на основе похожих организаций
- Прогноз потребности в ресурсах
- Critical path и milestones

## 📁 Структура модуля

```
community_intelligence/
├── __init__.py              # Экспорты модуля
├── config.py                # Конфигурация
│
├── models/                  # Database models
│   ├── __init__.py
│   └── database.py          # SQLAlchemy models
│
├── services/                # Бизнес-логика
│   ├── __init__.py
│   ├── anonymizer.py        # Smart anonymization
│   ├── contribution_service.py  # Peer review workflow
│   ├── living_docs.py       # Documentation synthesis
│   └── predictive_timeline.py   # Journey prediction
│
├── api/                     # REST API
│   ├── __init__.py
│   └── routes.py            # FastAPI endpoints
│
├── tests/                   # Unit tests
│   ├── __init__.py
│   ├── test_anonymizer.py
│   └── test_contribution_service.py
│
└── README.md                # This file
```

## 🚀 Quick Start

### 1. Установка

```bash
cd intelligent-core/community_intelligence
pip install -r requirements.txt
```

### 2. Применение миграций

```bash
# Миграции в infrastructure/database/migrations_source/
# Добавьте новую миграцию для Community Intelligence таблиц

python infrastructure/database/apply_migrations_simple.py
```

### 3. Запуск API

```python
from fastapi import FastAPI
from intelligent_core.community_intelligence.api import router

app = FastAPI()
app.include_router(router)

# uvicorn main:app --reload
```

### 4. Использование сервисов

```python
from intelligent_core.community_intelligence import (
    ContributionService,
    SmartAnonymizer,
    LivingDocumentationService
)

# Smart Anonymization
anonymizer = SmartAnonymizer(k_anonymity=5)
result = await anonymizer.anonymize_case(case_data)

# Case Contribution
service = ContributionService(db, anonymizer, case_library)
contribution_id = await service.submit_case(user_id, case_data, "bia")

# Living Documentation
docs_service = LivingDocumentationService(db, kg, cases, llm)
annotation_id = await docs_service.add_annotation(
    user_id,
    "4.1",
    "Практическая интерпретация для healthcare...",
    {"industry": "healthcare"}
)
```

## 📊 Database Schema

### Основные таблицы

**case_contributions** - Community-contributed cases
```sql
- id: UUID (PK)
- contributor_id: UUID
- case_data: JSONB (anonymized)
- status: ENUM (draft, pending_review, approved, rejected)
- reviewers: UUID[] (assigned reviewers)
- module: VARCHAR (bia, risk, planning)
- tags: VARCHAR[] (searchable tags)
```

**peer_reviews** - Quality reviews
```sql
- id: UUID (PK)
- contribution_id: UUID (FK)
- reviewer_id: UUID
- approved: BOOLEAN
- quality_score: INTEGER (1-10)
- feedback: TEXT
```

**user_reputation** - Multi-dimensional reputation
```sql
- user_id: UUID (PK)
- total_points: INTEGER
- level: VARCHAR (newcomer, contributor, expert, master)
- contribution_points: INTEGER
- review_points: INTEGER
- expertise: JSONB ({bcm: 85, risk: 70})
- badges: VARCHAR[]
```

**community_annotations** - Expert interpretations
```sql
- id: UUID (PK)
- clause_id: VARCHAR (4.1, 4.2, etc)
- author_id: UUID
- interpretation: TEXT
- industry_specific: VARCHAR
- upvotes: INTEGER
- downvotes: INTEGER
```

**synthesized_guidance** - AI-unified guidance
```sql
- id: UUID (PK)
- clause_id: VARCHAR (unique)
- unified_guidance: TEXT
- practical_steps: JSONB
- common_pitfalls: JSONB
- success_patterns: JSONB
```

## 🔌 API Endpoints

### Case Contributions

```http
POST /api/v1/community/contributions
GET  /api/v1/community/contributions/{id}
GET  /api/v1/community/contributions/pending-reviews
POST /api/v1/community/contributions/{id}/review
```

### Reputation

```http
GET /api/v1/community/reputation/{user_id}
GET /api/v1/community/reputation/leaderboard
```

### Living Documentation

```http
POST /api/v1/community/annotations
GET  /api/v1/community/guidance/{clause_id}
POST /api/v1/community/annotations/{id}/vote
```

### Predictive Timeline

```http
POST /api/v1/community/timeline/predict
GET  /api/v1/community/insights/similar-orgs/{org_id}
```

## 🧪 Testing

```bash
# Run all tests
pytest intelligent-core/community_intelligence/tests/

# Run specific test file
pytest intelligent-core/community_intelligence/tests/test_anonymizer.py

# With coverage
pytest --cov=intelligent-core/community_intelligence
```

## ⚙️ Configuration

Environment variables (prefix `COMMUNITY_`):

```bash
# Peer Review
COMMUNITY_REVIEWERS_PER_CONTRIBUTION=3
COMMUNITY_REVIEW_DEADLINE_DAYS=7
COMMUNITY_MIN_REPUTATION_TO_REVIEW=100

# Reputation
COMMUNITY_POINTS_PEER_REVIEW=5
COMMUNITY_POINTS_CASE_APPROVED_BASE=50

# Anonymization
COMMUNITY_K_ANONYMITY=5
COMMUNITY_MAX_RISK_SCORE=0.7

# AI Synthesis
COMMUNITY_SYNTHESIS_TEMPERATURE=0.3
COMMUNITY_SYNTHESIS_MAX_TOKENS=2000
```

## 🔒 Security & Privacy

### Smart Anonymization

1. **Удаляет direct identifiers**: имена, email, ID
2. **Обобщает quasi-identifiers**: локации → регионы, точные даты → месяц/год
3. **Сохраняет utility**: industry, size, success patterns
4. **K-anonymity**: гарантирует ≥k похожих записей
5. **Risk scoring**: 0-1, блокирует при высоком риске

### Data Flow

```
User submits case
  → Smart Anonymizer (removes PII)
  → Peer Review (3 reviewers)
  → If approved → Case Library
  → Available for community learning
```

## 📈 Metrics & Monitoring

Ключевые метрики:

- **Contribution Rate**: cases submitted per month
- **Review Velocity**: avg time to complete review
- **Approval Rate**: % approved cases
- **Reputation Distribution**: users per level
- **Synthesis Quality**: feedback scores on guidance
- **Timeline Accuracy**: predicted vs actual completion

## 🛠️ Integration Points

### С другими модулями платформы

1. **Workflow Engine**: получает текущее состояние для predictions
2. **Case Library**: добавляет одобренные кейсы
3. **Knowledge Graph**: извлекает официальные тексты стандартов
4. **LLM Service**: синтезирует unified guidance
5. **ML Predictor**: предсказывает journey на основе похожих org

## 🚧 Roadmap

### Phase 1: Core (✅ Done)
- [x] Database schema
- [x] Smart Anonymizer
- [x] Contribution Service (peer review)
- [x] Reputation System
- [x] Living Documentation
- [x] Predictive Timeline
- [x] REST API

### Phase 2: Enhancements
- [ ] Real-time notifications (reviewers assigned, case approved)
- [ ] Advanced ML models for timeline prediction
- [ ] Gamification (achievements, challenges)
- [ ] Expert matching algorithm
- [ ] Mobile app integration

### Phase 3: Community Features
- [ ] Discussion forums per clause
- [ ] Q&A system (StackOverflow-style)
- [ ] Marketplace (consultants, auditors)
- [ ] Webinars & events
- [ ] Certification programs

## 📝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests
4. Implement feature
5. Run tests (`pytest`)
6. Commit (`git commit -m 'Add amazing feature'`)
7. Push (`git push origin feature/amazing-feature`)
8. Open Pull Request

## 📄 License

Proprietary - AI-Platform-ISO

## 🤝 Support

- Documentation: `/doc-project/community_intelligence/`
- Issues: GitHub Issues
- Email: support@ai-platform-iso.com

---

**Built with ❤️ for the BCM Community**
