# Learning System Service - Техническая Спецификация

**Версия**: 2.0.0
**Дата**: 2025-10-05
**Статус**: Production Ready

## Содержание

1. [Общая Информация](#общая-информация)
2. [Архитектура Системы](#архитектура-системы)
3. [Компоненты](#компоненты)
4. [API Спецификация](#api-спецификация)
5. [Модели Данных](#модели-данных)
6. [Алгоритмы и Логика](#алгоритмы-и-логика)
7. [Интеграции](#интеграции)
8. [Безопасность](#безопасность)
9. [Производительность](#производительность)
10. [Развёртывание](#развёртывание)

## Общая Информация

### Назначение

Learning System Service - микросервис платформы AI-Platform-ISO, отвечающий за:
- Автоматическое обучение на результатах упражнений BCM
- Обнаружение паттернов успеха и провала
- Отслеживание компетенций пользователей и команд
- Персонализированные рекомендации по обучению
- Интеграция с платформенными сервисами (RAG, ML Platform, KB)

### Scope

**В Scope**:
- Анализ результатов упражнений
- Обнаружение паттернов и аномалий
- Компетенции (individual, team, role-based)
- Геймификация (badges, points, leaderboard)
- ML predictions (success, difficulty, time estimates)
- Автоматический сбор потребностей в обучении
- Самообучающиеся ML модели
- Интеграция с RAG/ML Platform/KB

**Out of Scope**:
- Выполнение самих упражнений (это Scenario Execution Service)
- Управление пользователями (это User Service)
- Создание учебных материалов (это Content Management)
- Business continuity planning (это Planning Service)

### Технологический Стек

| Категория | Технология | Версия | Назначение |
|-----------|-----------|--------|------------|
| **Runtime** | Python | 3.11+ | Основной язык |
| **Web Framework** | FastAPI | 0.104+ | REST API |
| **Validation** | Pydantic | 2.0+ | Data validation |
| **ORM** | SQLAlchemy | 2.0+ | Database ORM |
| **Database** | PostgreSQL | 14+ | Основная БД |
| **Cache** | Redis | 7+ | Кеш и session store |
| **ML** | scikit-learn | 1.3+ | ML модели |
| **Data** | pandas, numpy | - | Data processing |
| **HTTP Client** | httpx | 0.24+ | Async HTTP |
| **Testing** | pytest | 7+ | Unit/Integration tests |
| **Container** | Docker | 20+ | Контейнеризация |
| **Orchestration** | Kubernetes | 1.27+ | Production deployment |

## Архитектура Системы

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  FastAPI Routers, Request/Response Models, OpenAPI Docs     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  Business Logic Engines, Workflow Orchestration             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                              │
│  Domain Models, Value Objects, Business Rules               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                      │
│  Database Access, External Services, Caching                │
└─────────────────────────────────────────────────────────────┘
```

### Component Diagram

```
┌───────────────────────────────────────────────────────────────┐
│                    LEARNING SYSTEM SERVICE                     │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  API ROUTERS (11 routers)                               │ │
│  │  - pattern_router                                       │ │
│  │  - competency_router                                    │ │
│  │  - gamification_router                                  │ │
│  │  - ml_router                                            │ │
│  │  - self_learning_router                                 │ │
│  │  - platform_integration_router                          │ │
│  │  - ...                                                  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  ENGINES (10 engines)                                   │ │
│  │                                                         │ │
│  │  Core:                    Integrated:                  │ │
│  │  - PatternDetector        - IntegratedKnowledgeConn    │ │
│  │  - CompetencyTracker      - IntegratedMLPredictor      │ │
│  │  - GamificationEngine                                  │ │
│  │  - LearningNeedsCollector                              │ │
│  │  - SelfLearningEngine                                  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  DATA ACCESS                                            │ │
│  │  - PostgreSQL (Supabase)                                │ │
│  │  - Redis Cache                                          │ │
│  │  - Shared Integrations (RAG, ML, KB)                    │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

### Sequence Diagram: Pattern Detection

```
User → API → PatternDetector → Database
  │      │          │              │
  │──────┼─POST────→│              │
  │      │ /patterns/detect        │
  │      │          │              │
  │      │          │──Fetch──────→│
  │      │          │  exercises   │
  │      │          │←─Results────┤
  │      │          │              │
  │      │          │──Analyze────→│
  │      │          │  patterns    │
  │      │          │              │
  │      │          │──Save────────→│
  │      │          │  patterns    │
  │      │          │←─Saved──────┤
  │      │          │              │
  │      │←─Patterns┤              │
  │←─────┼─Response─┤              │
  │ 200  │          │              │
```

### Sequence Diagram: Platform Integration Workflow

```
User → API → MLPredictor → MLPlatform → KBConnector → RAG
  │      │        │            │            │           │
  │──────┼────────┼───POST────→│            │           │
  │      │ /unified/predict-recommend      │           │
  │      │        │            │            │           │
  │      │        │──predict──→│            │           │
  │      │        │←─prediction┤            │           │
  │      │        │            │            │           │
  │      │ if risk=medium/high             │           │
  │      │        │            │            │           │
  │      │        │            │──search───────────────→│
  │      │        │            │  resources │           │
  │      │        │            │←─resources────────────┤
  │      │        │            │            │           │
  │      │        │            │──create────→│           │
  │      │        │            │  path      │           │
  │      │        │            │←─path─────┤           │
  │      │        │            │            │           │
  │←─────┼────────┼────────────┼────────────┼───────────┤
  │      │ {prediction, resources, path}               │
```

## Компоненты

### 1. Pattern Detector Engine

**Файл**: `engines/pattern_detector.py`

**Назначение**: Обнаружение повторяющихся паттернов в результатах упражнений

**Ключевые Методы**:
```python
class PatternDetector:
    def detect_patterns(
        self,
        exercise_results: List[ExerciseResult],
        min_confidence: float = 0.7
    ) -> List[Pattern]:
        """
        Обнаруживает паттерны в результатах упражнений

        Алгоритм:
        1. Группировка результатов по scenario_type
        2. Анализ success patterns (score >= 70)
        3. Анализ failure patterns (score < 70)
        4. Анализ improvement trends
        5. Расчёт confidence scores

        Returns: List[Pattern] с confidence >= min_confidence
        """
```

**Типы Паттернов**:
- `success_pattern` - паттерны успешных упражнений
- `failure_pattern` - паттерны провалов
- `improvement_pattern` - паттерны улучшения
- `decline_pattern` - паттерны деградации

**Confidence Calculation**:
```python
confidence = (
    0.4 * frequency_score +      # Частота появления
    0.3 * consistency_score +    # Консистентность
    0.2 * significance_score +   # Статистическая значимость
    0.1 * recency_score          # Актуальность
)
```

### 2. Competency Tracker Engine

**Файл**: `engines/competency_tracker.py`

**Назначение**: Отслеживание индивидуальных и командных компетенций BCM

**Компетенции BCM**:
```python
BCM_COMPETENCIES = [
    'incident_detection',      # Обнаружение инцидентов
    'escalation',              # Эскалация
    'communication',           # Коммуникация
    'technical_response',      # Технический ответ
    'decision_making',         # Принятие решений
    'coordination',            # Координация
    'documentation',           # Документирование
    'recovery',                # Восстановление
    'assessment'               # Оценка
]
```

**Расчёт Компетенций**:
```python
def calculate_competency_score(exercises: List) -> CompetencyProfile:
    """
    Формула расчёта:

    base_score = weighted_average(exercise_scores)
    trend_factor = calculate_trend(recent_vs_old)
    decay_factor = calculate_decay(days_since_last)

    final_score = base_score * trend_factor * decay_factor

    Где:
    - base_score: средневзвешенный score по упражнениям
    - trend_factor: 0.9-1.1 (улучшение/ухудшение)
    - decay_factor: 0.8-1.0 (деградация навыков)
    """
```

**Skills Decay Model**:
```python
# Навыки деградируют со временем без практики
def calculate_decay_risk(days_since_last: int) -> str:
    if days_since_last > 180:
        return 'critical'  # 6+ месяцев без практики
    elif days_since_last > 90:
        return 'high'      # 3-6 месяцев
    elif days_since_last > 30:
        return 'medium'    # 1-3 месяца
    else:
        return 'low'       # < 1 месяца
```

### 3. Gamification Engine

**Файл**: `engines/gamification_engine.py`

**Назначение**: Мотивация через игровые механики

**Game Mechanics**:

**Points System**:
```python
POINTS_CONFIG = {
    'exercise_completion': 10,
    'high_score_bonus': 20,      # score >= 90
    'improvement_bonus': 15,     # улучшение на 10+%
    'streak_bonus': 5,           # за каждый день в streak
    'team_participation': 5,
    'pattern_discovery': 25,
}
```

**Level System**:
```python
LEVELS = {
    'Novice': 0,          # 0-99 points
    'Learner': 100,       # 100-299
    'Practitioner': 300,  # 300-699
    'Expert': 700,        # 700-1499
    'Champion': 1500      # 1500+
}
```

**Badge System** (15 бейджей в 6 категориях):

```python
BADGES = {
    # Frequency badges
    'First Steps': {'criteria': 'exercises >= 1'},
    'Regular': {'criteria': 'exercises >= 10'},
    'Veteran': {'criteria': 'exercises >= 50'},

    # Performance badges
    'High Achiever': {'criteria': 'avg_score >= 80'},
    'Perfect Score': {'criteria': 'score == 100'},

    # Improvement badges
    'Fast Learner': {'criteria': 'improvement >= 20%'},

    # Specialty badges (по scenario_type)
    'Cyber Expert': {'criteria': 'cyber_exercises >= 20, avg >= 80'},
    'Disaster Master': {'criteria': 'disaster_exercises >= 20, avg >= 80'},

    # Team badges
    'Team Player': {'criteria': 'team_exercises >= 15'},

    # Streak badges
    'Consistent': {'criteria': 'streak_days >= 7'},
    'Marathon': {'criteria': 'streak_days >= 30'},
}
```

### 4. ML Predictor (Integrated)

**Файл**: `engines/ml_predictor_integrated.py`

**Назначение**: ML предсказания через shared ML Platform

**Models**:

```python
MODELS = {
    'exercise_success_predictor': {
        'type': 'RandomForest',
        'target': 'overall_score',
        'features': [
            'scenario_type',
            'team_size',
            'avg_competency',
            'days_since_last',
            'historical_avg',
            'trend'
        ]
    },

    'exercise_difficulty_scorer': {
        'type': 'XGBoost',
        'target': 'difficulty_score',
        'features': [
            'scenario_complexity',
            'objectives_count',
            'team_avg_competency',
            'team_experience'
        ]
    },

    'exercise_time_estimator': {
        'type': 'LinearRegression',
        'target': 'duration_minutes',
        'features': [
            'scenario_type',
            'team_size',
            'complexity'
        ]
    }
}
```

**Feature Engineering**:
```python
class FeatureBuilder:
    """
    Построитель фич для консистентности

    Типы фич:
    - Numeric: прямые числовые значения
    - Categorical: one-hot encoding
    - Boolean: 0/1
    - Timestamp: hour, day_of_week, is_weekend
    - List Aggregates: mean, min, max, std
    """
```

### 5. Self-Learning Engine

**Файл**: `engines/self_learning_engine.py`

**Назначение**: Автоматическое улучшение ML моделей через feedback loop

**Feedback Loop**:

```
1. Prediction:
   predict(features) → {prediction_id, prediction, confidence}

2. Actual Outcome:
   record_actual(prediction_id, actual_value)

3. Error Calculation:
   error = abs(prediction - actual)

4. Accumulation:
   training_buffer.append({features, actual})

5. Retraining:
   if len(buffer) >= threshold:
       new_model = train(buffer)
       if new_model.performance > current_model.performance:
           deploy(new_model, version++)
```

**Model Versioning**:
```python
MODEL_VERSIONS = {
    'exercise_success_predictor_v1': {'mae': 15.2, 'deployed': '2025-01-15'},
    'exercise_success_predictor_v2': {'mae': 12.8, 'deployed': '2025-02-10'},
    'exercise_success_predictor_v3': {'mae': 10.5, 'deployed': '2025-03-05'},
}
```

### 6. Knowledge Base Connector (Integrated)

**Файл**: `engines/knowledge_base_connector_integrated.py`

**Назначение**: Интеграция с RAG и Knowledge Base для поиска и создания знаний

**Key Features**:

**Semantic Search**:
```python
async def search_resources_for_gap(
    gap_keyword: str,
    user_id: Optional[str],
    competency_level: Optional[str]
) -> List[Resource]:
    """
    Поиск learning resources через RAG

    1. Построение RAG query с контекстом
    2. Фильтрация по типу (training_material, procedure, guideline)
    3. Фильтрация по тегам
    4. Semantic search
    5. Сортировка по relevance
    """
```

**Auto-Knowledge Creation**:
```python
async def auto_create_knowledge_from_pattern(
    pattern: Dict,
    threshold: int = 5
) -> Optional[str]:
    """
    Автоматическое создание статьи из паттерна

    Условия:
    - pattern.occurrences >= threshold (5)
    - Статья ещё не создана

    Процесс:
    1. Проверка threshold
    2. Проверка дубликатов
    3. Генерация markdown content
    4. Создание в KB Service
    5. Добавление в RAG Service

    Returns: article_id
    """
```

**External Sync**:
```python
class ExternalKnowledgeSyncManager:
    """
    Синхронизация внешних источников:
    - ISO 22301:2019 standards updates
    - Threat intelligence feeds (MISP, STIX/TAXII)
    - Industry best practices
    """
```

## API Спецификация

### REST API Standards

**Base URL**: `http://localhost:8033`

**Content-Type**: `application/json`

**Authentication**: JWT Bearer Token
```
Authorization: Bearer <token>
```

**Response Format**:
```json
{
  "status": "success" | "error",
  "data": {},
  "message": "Optional message",
  "timestamp": "2025-10-05T10:30:00Z"
}
```

**Error Format**:
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": {}
  }
}
```

**HTTP Status Codes**:
- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing/invalid auth
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Key Endpoints

#### Pattern Detection

```yaml
POST /api/learning/patterns/detect:
  summary: Обнаружение паттернов в результатах упражнений
  requestBody:
    content:
      application/json:
        schema:
          type: object
          properties:
            exercise_results:
              type: array
              items:
                $ref: '#/components/schemas/ExerciseResult'
            min_confidence:
              type: number
              minimum: 0
              maximum: 1
              default: 0.7
  responses:
    '200':
      description: Паттерны обнаружены
      content:
        application/json:
          schema:
            type: object
            properties:
              patterns:
                type: array
                items:
                  $ref: '#/components/schemas/Pattern'
```

#### Competency Calculation

```yaml
POST /api/learning/competency/calculate:
  summary: Расчёт компетенций пользователя
  requestBody:
    content:
      application/json:
        schema:
          type: object
          required:
            - user_id
            - exercise_results
          properties:
            user_id:
              type: string
            exercise_results:
              type: array
              items:
                $ref: '#/components/schemas/ExerciseResult'
  responses:
    '200':
      description: Компетенции рассчитаны
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/CompetencyProfile'
```

#### ML Prediction (Platform Integration)

```yaml
POST /api/learning/platform/ml/predict-success:
  summary: Предсказание успеха упражнения через ML Platform
  requestBody:
    content:
      application/json:
        schema:
          type: object
          required:
            - scenario_type
            - team_size
            - avg_competency
          properties:
            scenario_type:
              type: string
              enum: [cyber_incident, natural_disaster, supply_chain]
            team_size:
              type: integer
              minimum: 1
            avg_competency:
              type: number
              minimum: 0
              maximum: 1
            days_since_last_exercise:
              type: integer
              minimum: 0
              default: 0
            historical_scores:
              type: array
              items:
                type: number
  responses:
    '200':
      description: Предсказание получено
      content:
        application/json:
          schema:
            type: object
            properties:
              prediction_id:
                type: string
              predicted_score:
                type: number
              confidence:
                type: number
              success_probability:
                type: number
              risk_level:
                type: string
                enum: [low, medium, high]
              recommendations:
                type: array
                items:
                  type: string
```

## Модели Данных

### Database Schema

#### learning.exercise_results

```sql
CREATE TABLE learning.exercise_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exercise_id TEXT NOT NULL,
    user_id UUID NOT NULL,
    scenario_type TEXT NOT NULL,
    overall_score INTEGER CHECK (overall_score >= 0 AND overall_score <= 100),
    subscores JSONB,  -- детальные scores по компонентам
    conducted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER,
    team_size INTEGER,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_exercise_results_user ON learning.exercise_results(user_id);
CREATE INDEX idx_exercise_results_scenario ON learning.exercise_results(scenario_type);
CREATE INDEX idx_exercise_results_conducted ON learning.exercise_results(conducted_at);
```

#### learning.user_competencies

```sql
CREATE TABLE learning.user_competencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    competency_name TEXT NOT NULL,
    score DECIMAL(5,2) CHECK (score >= 0 AND score <= 100),
    level TEXT CHECK (level IN ('beginner', 'intermediate', 'advanced', 'expert')),
    trend TEXT CHECK (trend IN ('improving', 'stable', 'declining')),
    last_practiced_at TIMESTAMP WITH TIME ZONE,
    decay_risk TEXT CHECK (decay_risk IN ('low', 'medium', 'high', 'critical')),
    exercises_count INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, competency_name)
);
```

#### learning.gamification_profiles

```sql
CREATE TABLE learning.gamification_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL,
    total_points INTEGER DEFAULT 0,
    level TEXT DEFAULT 'Novice',
    streak_days INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    exercises_completed INTEGER DEFAULT 0,
    badges_earned INTEGER DEFAULT 0,
    rank INTEGER,  -- leaderboard rank
    last_activity_date DATE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Pydantic Models

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ScenarioType(str, Enum):
    CYBER_INCIDENT = "cyber_incident"
    NATURAL_DISASTER = "natural_disaster"
    SUPPLY_CHAIN = "supply_chain"
    PANDEMIC = "pandemic"

class ExerciseResult(BaseModel):
    exercise_id: str
    user_id: str
    scenario_type: ScenarioType
    overall_score: int = Field(ge=0, le=100)
    subscores: Dict[str, float] = {}
    conducted_at: datetime
    duration_minutes: Optional[int] = None
    team_size: Optional[int] = None
    metadata: Dict[str, Any] = {}

class CompetencyProfile(BaseModel):
    user_id: str
    competencies: List[Competency]
    overall_avg: float
    strongest_competencies: List[str]
    weakest_competencies: List[str]
    competencies_at_risk: List[str]

class Pattern(BaseModel):
    pattern_id: str
    pattern_type: str  # success, failure, improvement, decline
    pattern_name: str
    description: str
    confidence: float = Field(ge=0, le=1)
    occurrence_count: int
    affected_scenarios: List[str]
    affected_users: List[str]
    recommendations: List[str]
    evidence: Dict[str, Any]
```

## Алгоритмы и Логика

### Pattern Detection Algorithm

```python
def detect_patterns(results: List[ExerciseResult]) -> List[Pattern]:
    """
    Алгоритм обнаружения паттернов

    1. Группировка по scenario_type
    2. Для каждой группы:
       a. Success patterns (score >= 70)
       b. Failure patterns (score < 70)
       c. Trend analysis
    3. Расчёт confidence
    4. Фильтрация по min_confidence
    """

    patterns = []

    # Группировка
    grouped = group_by(results, 'scenario_type')

    for scenario, exercises in grouped.items():
        # Success patterns
        successes = [e for e in exercises if e.overall_score >= 70]
        if len(successes) >= 3:
            pattern = analyze_success_pattern(successes)
            if pattern.confidence >= 0.7:
                patterns.append(pattern)

        # Failure patterns
        failures = [e for e in exercises if e.overall_score < 70]
        if len(failures) >= 3:
            pattern = analyze_failure_pattern(failures)
            if pattern.confidence >= 0.7:
                patterns.append(pattern)

    return patterns
```

### Competency Scoring Algorithm

```python
def calculate_competency_score(
    exercises: List[ExerciseResult],
    competency: str
) -> float:
    """
    Формула расчёта компетенций:

    final_score = (
        weighted_average(scores) *
        trend_factor *
        decay_factor
    )

    Где:
    - weighted_average: более свежие упражнения весят больше
    - trend_factor: 0.9-1.1 на основе тренда
    - decay_factor: 0.8-1.0 на основе days_since_last
    """

    # Extract scores for competency
    scores = [e.subscores.get(competency, 0) for e in exercises]

    # Weighted average (более свежие = больший вес)
    weights = calculate_recency_weights(exercises)
    base_score = np.average(scores, weights=weights)

    # Trend factor
    trend = calculate_trend(scores)
    if trend == 'improving':
        trend_factor = 1.1
    elif trend == 'declining':
        trend_factor = 0.9
    else:
        trend_factor = 1.0

    # Decay factor
    days_since = (datetime.now() - max(e.conducted_at)).days
    decay_factor = calculate_decay_factor(days_since)

    # Final score
    final_score = base_score * trend_factor * decay_factor

    return min(100, max(0, final_score))
```

### Learning Path Generation

```python
def create_learning_path(
    user_id: str,
    competency_gap: str,
    resources: List[Resource]
) -> LearningPath:
    """
    Создание персонализированного learning path

    1. Сортировка resources:
       - По relevance score (RAG)
       - По difficulty (beginner → advanced)
    2. Структурирование в phases
    3. Оценка времени
    4. SMART goals
    """

    # Сортировка
    sorted_resources = sorted(
        resources,
        key=lambda r: (
            r.relevance_score,  # сначала по релевантности
            difficulty_order[r.difficulty]  # потом по сложности
        ),
        reverse=True
    )

    # Структура path
    path_phases = []
    for i, resource in enumerate(sorted_resources[:6]):  # max 6
        phase = {
            'order': i + 1,
            'resource_id': resource.id,
            'title': resource.title,
            'type': resource.type,
            'difficulty': resource.difficulty,
            'duration_hours': resource.duration_hours
        }
        path_phases.append(phase)

    total_hours = sum(p['duration_hours'] for p in path_phases)

    return LearningPath(
        user_id=user_id,
        gap=competency_gap,
        phases=path_phases,
        estimated_hours=total_hours,
        created_at=datetime.now()
    )
```

## Интеграции

### Shared Platform Services

#### RAG Service Integration

```python
from shared.integrations.rag_connector import RAGConnector

rag = RAGConnector(rag_service_url="http://localhost:8050")

# Semantic search
results = await rag.search_knowledge(
    query="cyber incident communication procedures",
    context={'user_id': 'user123', 'domain': 'BCM'},
    filters={'type': ['procedure', 'guideline']},
    limit=10
)

# Add knowledge back
knowledge_id = await rag.add_knowledge(
    content="Pattern detected: Communication delays...",
    metadata={'pattern_type': 'failure', 'severity': 'high'},
    knowledge_type='pattern',
    source='learning_system'
)
```

#### ML Platform Integration

```python
from shared.integrations.ml_platform_client import MLPlatformClient, FeatureBuilder

ml_client = MLPlatformClient(ml_service_url="http://localhost:8060")

# Build features
features = FeatureBuilder()
features.add_categorical('scenario_type', 'cyber_incident')
features.add_numeric('team_size', 12)
features.add_numeric('avg_competency', 0.75)

# Predict
prediction = await ml_client.predict(
    model_name='exercise_success_predictor',
    features=features.build(),
    context={'user_id': 'user123'}
)

# Submit feedback (после упражнения)
await ml_client.submit_feedback(
    prediction_id=prediction['prediction_id'],
    actual_outcome=82.0,
    metadata={'exercise_id': 'ex_123'}
)
```

#### Knowledge Base Integration

```python
from shared.integrations.knowledge_client import KnowledgeClient, KnowledgeType

kb_client = KnowledgeClient(kb_service_url="http://localhost:8040")

# Search structured knowledge
articles = await kb_client.search(
    query="communication procedures",
    filters={'category': 'procedures', 'tags': ['communication']},
    limit=10
)

# Create article
article_id = await kb_client.create_article(
    title="Communication Best Practices",
    content="## Overview\n\n...",
    category="best_practices",
    knowledge_type=KnowledgeType.BEST_PRACTICE,
    tags=['communication', 'incident'],
    metadata={'iso_reference': 'ISO 22301:2019 8.4'}
)
```

### Event Bus Integration

```python
from shared.eventbus.publisher import EventPublisher

event_publisher = EventPublisher()

# Publish pattern detected event
await event_publisher.publish(
    topic='learning.pattern_detected',
    event={
        'pattern_id': 'pat_123',
        'pattern_type': 'failure',
        'confidence': 0.85,
        'affected_scenarios': ['cyber_incident'],
        'timestamp': datetime.now().isoformat()
    }
)
```

## Безопасность

### Authentication & Authorization

**JWT Token Validation**:
```python
from shared.auth.dependencies import require_user

@router.get("/protected")
async def protected_route(user = Depends(require_user)):
    # user.id, user.roles доступны
    return {"user_id": user.id}
```

**Row-Level Security (RLS)**:
```sql
-- Users can only see their own data
CREATE POLICY user_data_isolation ON learning.user_competencies
    FOR ALL TO authenticated
    USING (user_id = auth.uid());

-- Admins can see all
CREATE POLICY admin_full_access ON learning.user_competencies
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM auth.users
            WHERE id = auth.uid()
            AND role = 'admin'
        )
    );
```

### Rate Limiting

```python
from shared.middleware.rate_limiter import rate_limit

@router.post("/expensive")
@rate_limit(requests=10, window=60)  # 10 req/min
async def expensive_operation():
    pass
```

### Data Validation

```python
from pydantic import BaseModel, Field, validator

class CompetencyRequest(BaseModel):
    user_id: str = Field(..., regex=r'^[a-f0-9-]{36}$')
    exercise_results: List[ExerciseResult] = Field(..., min_items=1, max_items=100)

    @validator('exercise_results')
    def validate_results(cls, v):
        if len(v) == 0:
            raise ValueError('At least one result required')
        return v
```

## Производительность

### Caching Strategy

```python
from shared.cache.redis_cache import RedisCache

cache = RedisCache()

# Cache competency calculations (expensive)
@cache.cached(ttl=3600)  # 1 hour
async def get_user_competencies(user_id: str):
    # Expensive calculation
    return competencies

# Invalidate on update
await cache.delete(f"competencies:{user_id}")
```

### Database Optimization

**Indexes**:
```sql
-- Frequently queried fields
CREATE INDEX idx_exercise_results_user ON learning.exercise_results(user_id);
CREATE INDEX idx_exercise_results_scenario ON learning.exercise_results(scenario_type);
CREATE INDEX idx_exercise_results_conducted ON learning.exercise_results(conducted_at DESC);

-- Composite indexes for common queries
CREATE INDEX idx_user_scenario ON learning.exercise_results(user_id, scenario_type);
```

**Query Optimization**:
```python
# BAD: N+1 queries
for user_id in user_ids:
    user = await db.get(user_id)

# GOOD: Batch query
users = await db.get_many(user_ids)
```

### Async Operations

```python
import asyncio

# Parallel execution
results = await asyncio.gather(
    rag.search_knowledge(...),
    ml_client.predict(...),
    kb_client.search(...)
)
```

## Развёртывание

### Docker

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8033

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8033"]
```

### Kubernetes

**Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: learning-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: learning-system
  template:
    metadata:
      labels:
        app: learning-system
    spec:
      containers:
      - name: learning-system
        image: learning-system:2.0.0
        ports:
        - containerPort: 8033
        env:
        - name: SUPABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            cpu: 1000m
            memory: 2Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8033
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8033
          initialDelaySeconds: 10
          periodSeconds: 5
```

### Monitoring

**Prometheus Metrics**:
```python
from prometheus_client import Counter, Histogram

# Counters
patterns_detected = Counter(
    'learning_patterns_detected_total',
    'Total patterns detected',
    ['pattern_type']
)

# Histograms
api_latency = Histogram(
    'learning_api_request_duration_seconds',
    'API request latency',
    ['endpoint', 'method']
)
```

**Logging**:
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "pattern_detected",
    pattern_type="failure",
    confidence=0.85,
    scenario_type="cyber_incident"
)
```

---

**Версия**: 2.0.0
**Последнее Обновление**: 2025-10-05
**Авторы**: AI Platform Team
