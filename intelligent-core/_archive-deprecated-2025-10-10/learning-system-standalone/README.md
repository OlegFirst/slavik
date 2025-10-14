# Learning System Service

## Обзор

Learning System Service - интеллектуальная система обучения для платформы BCM (Business Continuity Management), которая автоматически учится на результатах упражнений, обнаруживает паттерны, отслеживает компетенции и предоставляет персонализированные рекомендации по обучению.

**Порт**: 8033
**Версия**: 2.0.0
**Статус**: ✅ Production Ready

## Основные Возможности

### 🎯 Core Features (Phase 1)
- **Pattern Detection** - автоматическое обнаружение паттернов успеха и провала
- **Performance Analysis** - анализ трендов производительности
- **AI Model Improvement** - рекомендации по улучшению AI моделей
- **Predictive Scoring** - предсказание успеха упражнений
- **Continuous Learning** - непрерывный цикл обучения

### 📊 Enhancement Features (Phase 2)
- **Competency Tracking** - отслеживание индивидуальных и командных компетенций
- **Process Gap Analysis** - анализ покрытия процессов обучением
- **Gamification** - система достижений, бейджей и лидерборда
- **Knowledge Integration** - интеграция с базой знаний
- **ML Predictions** - ML-powered предсказания сложности и успеха
- **Analytics Dashboard** - продвинутая аналитика

### 🔄 Self-Learning Features (Phase 3)
- **Automated Needs Collection** - автоматический сбор потребностей в обучении из 6 источников
- **Self-Improving ML Models** - ML модели, которые автоматически переобучаются
- **Auto-Knowledge Creation** - автоматическое создание статей из паттернов (≥5 occurrences)
- **External Knowledge Sync** - синхронизация ISO standards, threat feeds

### 🔗 Platform Integration (Phase 4)
- **RAG Integration** - семантический поиск по единой базе знаний платформы
- **ML Platform Integration** - общие ML модели для всех сервисов
- **Knowledge Base Integration** - структурированное управление знаниями
- **Cross-Service Learning** - модели учатся от всех сервисов платформы

## 📚 Документация

Вся документация находится в папке [`docs/`](docs/):
- **[Техническая спецификация](docs/TECHNICAL_SPECIFICATION.md)** - детальная архитектура, API, алгоритмы
- **[Руководство пользователя](docs/USER_GUIDE.md)** - практические примеры использования
- **[План развития](docs/DEVELOPMENT_ROADMAP.md)** - roadmap Q4 2025 - Q2 2026
- **[Интеграция с платформой](docs/PLATFORM_INTEGRATION_ARCHITECTURE.md)** - RAG, ML Platform, KB

## Архитектура

### Высокоуровневая Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                   LEARNING SYSTEM SERVICE                    │
│                        (Port 8033)                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  API Layer                                                   │
│  ├── Pattern Detection API                                   │
│  ├── Competency Tracking API                                 │
│  ├── Gamification API                                        │
│  ├── ML Predictions API                                      │
│  ├── Self-Learning API                                       │
│  └── Platform Integration API                                │
│                                                              │
│  Engine Layer                                                │
│  ├── Pattern Detector                                        │
│  ├── Competency Tracker                                      │
│  ├── Gamification Engine                                     │
│  ├── ML Predictor (Integrated)                               │
│  ├── Knowledge Connector (Integrated)                        │
│  ├── Learning Needs Collector                                │
│  └── Self-Learning Engine                                    │
│                                                              │
│  Data Layer                                                  │
│  ├── PostgreSQL (via Supabase)                               │
│  ├── Redis Cache                                             │
│  └── Event Bus                                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                          ↓ использует
┌─────────────────────────────────────────────────────────────┐
│               SHARED PLATFORM SERVICES                       │
│                                                              │
│  ├── RAG Service (Port 8050) - Semantic Search              │
│  ├── ML Platform (Port 8060) - Predictions & Learning       │
│  └── Knowledge Base (Port 8040) - Structured Knowledge      │
└─────────────────────────────────────────────────────────────┘
```

### Структура Проекта

```
learning-system/
├── README.md                          # Этот файл
├── docs/                              # 📚 Вся документация
│   ├── TECHNICAL_SPECIFICATION.md
│   ├── USER_GUIDE.md
│   ├── DEVELOPMENT_ROADMAP.md
│   └── PLATFORM_INTEGRATION_ARCHITECTURE.md
│
├── main.py                            # Точка входа (FastAPI app)
├── requirements.txt                   # Python зависимости
│
├── api/                               # API роутеры
│   ├── pattern_router.py              # Обнаружение паттернов
│   ├── learning_router.py             # Основное обучение
│   ├── recommendation_router.py       # Рекомендации
│   ├── competency_router.py           # Отслеживание компетенций
│   ├── process_gap_router.py          # Анализ пробелов
│   ├── gamification_router.py         # Геймификация
│   ├── knowledge_router.py            # Интеграция знаний
│   ├── ml_router.py                   # ML предсказания
│   ├── analytics_router.py            # Аналитика
│   ├── self_learning_router.py        # Самообучение
│   └── platform_integration_router.py # Интеграция с платформой
│
├── engines/                           # Бизнес-логика
│   ├── pattern_detector.py            # Детектор паттернов
│   ├── learning_analyzer.py           # Анализатор обучения
│   ├── competency_tracker.py          # Трекер компетенций
│   ├── process_gap_analyzer.py        # Анализатор пробелов
│   ├── gamification_engine.py         # Движок геймификации
│   ├── knowledge_integrator.py        # Интегратор знаний (legacy)
│   ├── ml_predictor.py                # ML предиктор (legacy)
│   ├── learning_needs_collector.py    # Сборщик потребностей
│   ├── self_learning_engine.py        # Движок самообучения
│   ├── knowledge_base_connector_integrated.py  # KB connector (integrated)
│   └── ml_predictor_integrated.py     # ML predictor (integrated)
│
├── models/                            # Data models
│   └── learning_models.py             # Pydantic/SQLAlchemy модели
│
├── examples/                          # Примеры использования
│   └── platform_integration_example.py
│
└── docs/                              # Документация
    ├── PLATFORM_INTEGRATION_COMPLETE.md
    ├── INTEGRATION_ARCHITECTURE_DIAGRAM.md
    ├── PHASE_2A_IMPLEMENTATION_COMPLETE.md
    ├── MISSING_COMPONENTS_DESIGN.md
    ├── FULL_LEARNING_CYCLE.md
    └── WHATS_NEXT.md
```

## Технический Стек

### Backend
- **FastAPI** 0.104+ - современный async web framework
- **Python** 3.11+ - основной язык
- **Pydantic** 2.0+ - валидация данных
- **SQLAlchemy** 2.0+ - ORM

### Database
- **PostgreSQL** 14+ (через Supabase)
- **Redis** 7+ - кеширование и session store

### ML/AI
- **scikit-learn** - базовые ML модели
- **pandas** / **numpy** - обработка данных
- **Platform ML Service** - shared predictions (интеграция)

### Integration
- **httpx** - async HTTP клиент для platform services
- **RAG Service** - семантический поиск
- **ML Platform** - общие ML модели
- **Knowledge Base** - структурированные знания

### Infrastructure
- **Docker** / **Docker Compose**
- **Kubernetes** (production)
- **Supabase** - managed PostgreSQL
- **Redis Cloud** / local Redis

## База Данных

### Основные Таблицы (Schemas)

**learning schema** - основные данные обучения:
- `exercise_results` - результаты упражнений
- `learning_patterns` - обнаруженные паттерны
- `user_progress` - прогресс пользователей
- `recommendations` - рекомендации

**Enhancement tables** (Phase 2):
- `user_competencies` - компетенции пользователей
- `team_competencies` - командные компетенции
- `process_coverage_matrix` - матрица покрытия процессов
- `gamification_profiles` - геймификация профили
- `badge_definitions` - определения бейджей
- `user_badges` - заработанные бейджи
- `leaderboard` - лидерборд
- `learning_paths` - пути обучения
- `smart_goals` - SMART цели
- `alerts` - алерты

**Self-Learning tables** (Phase 3):
- Встроены в движки самообучения
- Планируется миграция для персистентности

### Миграции

Миграции расположены в: `/infrastructure/database/migrations_source/`

Ключевые миграции:
- `043_learning_system_enhancements.sql` - Phase 2 enhancements
- Будущие: `044_learning_phase3_tables.sql` - Phase 3 persistence

## API Endpoints

### Core API (`/api/learning/`)

**Pattern Detection**:
```
POST   /patterns/detect          - Обнаружение паттернов
GET    /patterns                 - Получение паттернов
GET    /patterns/{pattern_id}    - Детали паттерна
```

**Learning & Recommendations**:
```
POST   /analyze                  - Анализ результатов
GET    /progress/{user_id}       - Прогресс пользователя
GET    /recommendations/{user_id} - Рекомендации
```

### Competency API (`/api/learning/competency/`)

```
POST   /calculate                - Расчёт компетенций
GET    /user/{user_id}           - Компетенции пользователя
GET    /team/{team_name}         - Анализ команды
POST   /team/coverage            - Покрытие команды
GET    /role-gaps/{role}         - Пробелы роли
POST   /track-decay              - Отслеживание деградации
```

### Gamification API (`/api/learning/gamification/`)

```
POST   /profile                  - Расчёт профиля геймификации
GET    /badges                   - Список бейджей
POST   /check-badges             - Проверка заработанных бейджей
GET    /leaderboard              - Лидерборд
POST   /activity                 - Запись активности
```

### ML Predictions API (`/api/learning/ml/`)

```
POST   /predict/success          - Предсказание успеха
POST   /predict/difficulty       - Предсказание сложности
POST   /recommend/difficulty     - Рекомендация сложности
POST   /time-estimate            - Оценка времени
```

### Self-Learning API (`/api/learning/auto/`)

```
POST   /needs/collect            - Сбор потребностей в обучении
POST   /needs/prioritize         - Приоритизация потребностей
POST   /kb/search                - Поиск в KB
POST   /kb/create-learning-path  - Создание learning path
POST   /kb/auto-create-from-patterns - Авто-создание знаний
POST   /self-learn/record-prediction - Запись предсказания
POST   /self-learn/record-outcome    - Запись результата
GET    /self-learn/effectiveness     - Эффективность обучения
POST   /workflow/full-cycle      - Полный цикл обучения
```

### Platform Integration API (`/api/learning/platform/`)

**RAG Integration**:
```
POST   /rag/search               - Семантический поиск
POST   /rag/add-knowledge        - Добавление знаний
```

**ML Platform Integration**:
```
POST   /ml/predict-success       - Предсказание через ML Platform
POST   /ml/submit-feedback       - Feedback для обучения моделей
GET    /ml/performance           - Производительность моделей
GET    /ml/feature-importance    - Важность фич
```

**Knowledge Base Integration**:
```
POST   /kb/create-learning-path  - Создание learning path из KB
POST   /kb/auto-create-from-pattern - Авто-создание статей
POST   /kb/sync-external         - Синхронизация внешних источников
```

**Unified Workflows**:
```
POST   /unified/predict-and-recommend - Предсказание + рекомендации
GET    /status                   - Статус интеграции с платформой
```

## Быстрый Старт

### Установка

```bash
cd intelligent-core/learning-system

# Создать virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt
```

### Конфигурация

Создать `.env` файл:

```env
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Platform Services (optional)
RAG_SERVICE_URL=http://localhost:8050
ML_PLATFORM_URL=http://localhost:8060
KB_SERVICE_URL=http://localhost:8040

# Service
PORT=8033
LOG_LEVEL=INFO
```

### Запуск

```bash
# Development
python main.py

# Production (через uvicorn)
uvicorn main:app --host 0.0.0.0 --port 8033 --workers 4

# Docker
docker build -t learning-system .
docker run -p 8033:8033 --env-file .env learning-system
```

### Проверка

```bash
# Health check
curl http://localhost:8033/

# API docs
open http://localhost:8033/docs

# Примеры
python examples/platform_integration_example.py
```

## Использование

См. подробное руководство: [USER_GUIDE.md](USER_GUIDE.md)

### Быстрый Пример

```python
import httpx

# 1. Обнаружение паттернов
response = await httpx.post(
    "http://localhost:8033/api/learning/patterns/detect",
    json={
        "exercise_results": [
            {
                "exercise_id": "ex_123",
                "overall_score": 85,
                "scenario_type": "cyber_incident",
                # ...
            }
        ],
        "min_confidence": 0.7
    }
)
patterns = response.json()

# 2. Расчёт компетенций
response = await httpx.post(
    "http://localhost:8033/api/learning/competency/calculate",
    json={
        "user_id": "user_123",
        "exercise_results": [...]
    }
)
competencies = response.json()

# 3. ML предсказание через Platform Integration
response = await httpx.post(
    "http://localhost:8033/api/learning/platform/ml/predict-success",
    json={
        "scenario_type": "cyber_incident",
        "team_size": 12,
        "avg_competency": 0.75
    }
)
prediction = response.json()
```

## Разработка

### Добавление Нового Endpoint

1. Создать роутер в `api/`:
```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/my-endpoint")
async def my_endpoint(request: MyRequest):
    # логика
    return {"result": "success"}
```

2. Добавить в `main.py`:
```python
from api import my_router
app.include_router(my_router.router, prefix="/api/learning/my", tags=["My Feature"])
```

### Добавление Нового Engine

1. Создать engine в `engines/`:
```python
class MyEngine:
    def __init__(self):
        pass

    async def process(self, data):
        # логика
        return result
```

2. Использовать в роутере:
```python
from engines.my_engine import MyEngine

engine = MyEngine()

@router.post("/process")
async def process(data):
    result = await engine.process(data)
    return result
```

### Тестирование

```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests/integration/

# Coverage
pytest --cov=. tests/
```

## Мониторинг и Логи

### Логирование

Логи пишутся в stdout в формате JSON:

```json
{
  "timestamp": "2025-10-05T10:30:00Z",
  "level": "INFO",
  "service": "learning-system",
  "message": "Pattern detected",
  "pattern_type": "success_pattern",
  "confidence": 0.85
}
```

### Метрики

Метрики экспортируются в Prometheus формате на `/metrics`:

- `learning_patterns_detected_total` - счётчик обнаруженных паттернов
- `learning_predictions_total` - счётчик предсказаний
- `learning_api_requests_total` - счётчик API запросов
- `learning_api_request_duration_seconds` - длительность запросов

### Health Checks

```bash
# Liveness probe
curl http://localhost:8033/health/live

# Readiness probe
curl http://localhost:8033/health/ready
```

## Производительность

### Рекомендуемые Ресурсы

**Development**:
- CPU: 2 cores
- RAM: 2GB
- Disk: 10GB

**Production**:
- CPU: 4+ cores
- RAM: 8GB+
- Disk: 50GB+

### Масштабирование

Learning System поддерживает горизонтальное масштабирование:

```yaml
# Kubernetes deployment
replicas: 3

resources:
  requests:
    cpu: 1000m
    memory: 2Gi
  limits:
    cpu: 2000m
    memory: 4Gi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

## Безопасность

### Аутентификация

Используется JWT токены через shared auth middleware:

```python
from shared.auth.dependencies import require_user

@router.get("/protected")
async def protected_route(user = Depends(require_user)):
    return {"user_id": user.id}
```

### Авторизация

Row-Level Security (RLS) на уровне базы данных:

```sql
-- Пользователи видят только свои данные
CREATE POLICY user_isolation ON learning.user_competencies
    FOR ALL TO authenticated
    USING (user_id = auth.uid());
```

### Rate Limiting

```python
from shared.middleware.rate_limiter import rate_limit

@router.post("/expensive-operation")
@rate_limit(requests=10, window=60)  # 10 req/min
async def expensive_operation():
    pass
```

## Troubleshooting

### Частые Проблемы

**1. База данных недоступна**
```bash
# Проверить подключение
psql $SUPABASE_URL

# Проверить миграции
python scripts/check_migrations.py
```

**2. Redis недоступен**
```bash
# Проверить Redis
redis-cli ping

# Проверить подключение
python -c "import redis; r=redis.Redis(); print(r.ping())"
```

**3. Platform Services недоступны**
```bash
# Проверить статус
curl http://localhost:8033/api/learning/platform/status

# Services работают в fallback режиме, если недоступны
```

## Contributing

См. [CONTRIBUTING.md](../../CONTRIBUTING.md) в корне проекта.

## Лицензия

Proprietary - All Rights Reserved

## Контакты

- **Команда**: AI Platform Team
- **Email**: support@ai-platform.com
- **Документация**: https://docs.ai-platform.com

## См. Также

- [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md) - Техническая спецификация
- [USER_GUIDE.md](USER_GUIDE.md) - Руководство пользователя
- [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) - План развития
- [PLATFORM_INTEGRATION_COMPLETE.md](docs/PLATFORM_INTEGRATION_COMPLETE.md) - Интеграция с платформой
