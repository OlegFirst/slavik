# C4 Model - Level 3: Component Diagram
## AI-Platform-ISO - Компоненты внутри ключевых сервисов

**Auto-generated from real codebase**
**Last updated:** 2025-10-06

---

## Что это?

Level 3 показывает **КАК** устроены ключевые сервисы изнутри:
- Какие классы/модули внутри каждого сервиса?
- Как они взаимодействуют?
- Какие паттерны используются?

---

## 1. Workflow Intelligence (THE BRAIN)

**Location:** `intelligent-core/workflow_intelligence/`
**Port:** 8001
**LOC:** 1360 lines

### Архитектура компонентов

```mermaid
graph TB
    subgraph "API Layer"
        API[FastAPI App<br/>main.py]
        ROUTES[API Routes<br/>/api/v1/*]
    end

    subgraph "Core Logic"
        WF_MANAGER[Workflow Manager<br/>workflow_manager.py<br/>━━━━━━━━━━━<br/>• Start workflows<br/>• Query status<br/>• Handle signals]

        TEMPORAL_CLIENT[Temporal Client<br/>temporal_client.py<br/>━━━━━━━━━━━<br/>• Connect to cloud<br/>• Execute activities<br/>• Handle failures]

        AI_RECOMMENDER[AI Recommender<br/>ai_recommender.py<br/>━━━━━━━━━━━<br/>• Analyze context<br/>• Generate suggestions<br/>• Optimize paths]
    end

    subgraph "Activities"
        BIA_ACT[BIA Activity<br/>Execute BIA analysis]
        RISK_ACT[Risk Activity<br/>Assess risks]
        PLAN_ACT[Planning Activity<br/>Generate plans]
        NOTIFY_ACT[Notification Activity<br/>Send alerts]
    end

    subgraph "Data Access"
        DB_REPO[Database Repository<br/>db_repository.py<br/>━━━━━━━━━━━<br/>• Workflow state<br/>• Execution history]

        VECTOR_REPO[Vector Repository<br/>vector_repository.py<br/>━━━━━━━━━━━<br/>• Semantic search<br/>• Similar workflows]
    end

    subgraph "External Integrations"
        TEMPORAL[(Temporal Cloud)]
        POSTGRES[(PostgreSQL)]
        QDRANT[(Qdrant)]
        EVENTBUS[EventBus]
    end

    API --> ROUTES
    ROUTES --> WF_MANAGER
    WF_MANAGER --> TEMPORAL_CLIENT
    WF_MANAGER --> AI_RECOMMENDER
    WF_MANAGER --> DB_REPO

    TEMPORAL_CLIENT --> BIA_ACT
    TEMPORAL_CLIENT --> RISK_ACT
    TEMPORAL_CLIENT --> PLAN_ACT
    TEMPORAL_CLIENT --> NOTIFY_ACT

    AI_RECOMMENDER --> VECTOR_REPO

    DB_REPO --> POSTGRES
    VECTOR_REPO --> QDRANT
    TEMPORAL_CLIENT --> TEMPORAL
    WF_MANAGER --> EVENTBUS

    style WF_MANAGER fill:#f3e5f5,stroke:#9c27b0,stroke-width:3px
    style AI_RECOMMENDER fill:#fff3e0
    style TEMPORAL_CLIENT fill:#e1f5fe
```

### Ключевые классы

```python
# workflow_manager.py
class WorkflowManager:
    """Управление жизненным циклом workflow"""

    def __init__(self, temporal_client, db_repo, ai_recommender):
        self.temporal = temporal_client
        self.db = db_repo
        self.ai = ai_recommender

    async def start_workflow(self, workflow_type: str, input_data: dict):
        """Запустить workflow с AI-рекомендациями"""
        # 1. Получить AI рекомендации
        recommendations = await self.ai.recommend_workflow(workflow_type, input_data)

        # 2. Запустить Temporal workflow
        handle = await self.temporal.start_workflow(
            workflow_type,
            input_data,
            recommendations=recommendations
        )

        # 3. Сохранить состояние в БД
        await self.db.save_workflow_state(handle.id, input_data)

        return handle

    async def query_status(self, workflow_id: str):
        """Запросить статус workflow"""
        return await self.temporal.query_workflow(workflow_id)
```

---

## 2. API Gateway

**Location:** `infrastructure/gateway/api-gateway/`
**Port:** 8000

### Архитектура компонентов

```mermaid
graph TB
    subgraph "Entry Point"
        MAIN[FastAPI App<br/>main.py]
    end

    subgraph "Middleware Stack"
        CORS[CORS Middleware<br/>Cross-origin requests]
        AUTH[Auth Middleware<br/>JWT validation]
        RATE[Rate Limiter<br/>Token bucket algorithm]
        LOGGING[Logging Middleware<br/>Request/response logs]
    end

    subgraph "Core Components"
        ROUTER[API Router<br/>router.py<br/>━━━━━━━━━━━<br/>• Service discovery<br/>• Load balancing<br/>• Circuit breaker]

        JWT[JWT Manager<br/>jwt_manager.py<br/>━━━━━━━━━━━<br/>• Token generation<br/>• Token validation<br/>• Refresh tokens]

        LIMITER[Rate Limiter<br/>rate_limiter.py<br/>━━━━━━━━━━━<br/>• Per-user limits<br/>• Per-endpoint limits<br/>• Redis-backed]
    end

    subgraph "Downstream Services"
        WFI[Workflow Intelligence<br/>:8001]
        BIA[BIA Service<br/>:8010]
        RISK[Risk Service<br/>:8011]
    end

    subgraph "External"
        REDIS[(Redis<br/>Rate limits)]
        POSTGRES[(PostgreSQL<br/>Users, tokens)]
    end

    MAIN --> CORS
    CORS --> AUTH
    AUTH --> RATE
    RATE --> LOGGING
    LOGGING --> ROUTER

    ROUTER --> JWT
    ROUTER --> LIMITER

    ROUTER --> WFI
    ROUTER --> BIA
    ROUTER --> RISK

    JWT --> POSTGRES
    LIMITER --> REDIS

    style ROUTER fill:#fff3e0,stroke:#ff9800,stroke-width:3px
    style JWT fill:#ffebee
    style LIMITER fill:#e8f5e9
```

### Ключевые паттерны

**1. Circuit Breaker Pattern:**
```python
# router.py
class CircuitBreaker:
    """Защита от каскадных сбоев"""

    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure < self.timeout:
                raise CircuitBreakerOpen("Service unavailable")
            else:
                self.state = "HALF_OPEN"

        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                self.last_failure = time.time()
            raise
```

**2. Rate Limiting:**
```python
# rate_limiter.py
class RateLimiter:
    """Token Bucket алгоритм"""

    async def check_rate_limit(self, user_id: str, endpoint: str):
        key = f"rate:{user_id}:{endpoint}"
        current = await redis.get(key)

        if current and int(current) >= LIMIT:
            raise RateLimitExceeded("Too many requests")

        await redis.incr(key)
        await redis.expire(key, WINDOW_SECONDS)
```

---

## 3. BIA Service (Business Impact Analysis)

**Location:** `platform-services/bia-service/`

### Архитектура компонентов

```mermaid
graph TB
    subgraph "API Layer"
        API[FastAPI App]
        ROUTES[Routes<br/>/api/v1/bia/*]
    end

    subgraph "Business Logic"
        BIA_MANAGER[BIA Manager<br/>bia_manager.py<br/>━━━━━━━━━━━<br/>• Create BIA<br/>• Calculate impact<br/>• Generate reports]

        IMPACT_CALC[Impact Calculator<br/>impact_calculator.py<br/>━━━━━━━━━━━<br/>• Financial impact<br/>• Operational impact<br/>• Reputational impact]

        RECOVERY_CALC[Recovery Calculator<br/>recovery_calculator.py<br/>━━━━━━━━━━━<br/>• RTO calculation<br/>• RPO calculation<br/>• MTD calculation]
    end

    subgraph "Data Layer"
        BIA_REPO[BIA Repository<br/>PostgreSQL]
        CACHE[Cache Layer<br/>Redis]
    end

    subgraph "External Services"
        WFI[Workflow Intelligence<br/>AI recommendations]
        EVENTBUS[EventBus<br/>Publish events]
    end

    API --> ROUTES
    ROUTES --> BIA_MANAGER
    BIA_MANAGER --> IMPACT_CALC
    BIA_MANAGER --> RECOVERY_CALC
    BIA_MANAGER --> BIA_REPO
    BIA_MANAGER --> CACHE
    BIA_MANAGER --> WFI
    BIA_MANAGER --> EVENTBUS

    style BIA_MANAGER fill:#e8f5e9,stroke:#4caf50,stroke-width:3px
```

### Бизнес-логика

```python
# bia_manager.py
class BIAManager:
    """Управление BIA анализами"""

    async def create_bia(self, business_process: dict):
        """Создать BIA с AI помощью"""

        # 1. Запросить AI рекомендации
        ai_suggestions = await self.workflow_intelligence.get_bia_suggestions(
            business_process
        )

        # 2. Рассчитать финансовое воздействие
        financial_impact = await self.impact_calculator.calculate_financial(
            business_process,
            ai_suggestions
        )

        # 3. Рассчитать RTO/RPO
        recovery_metrics = await self.recovery_calculator.calculate_metrics(
            business_process,
            financial_impact
        )

        # 4. Сохранить BIA
        bia = await self.repository.create_bia({
            "business_process": business_process,
            "financial_impact": financial_impact,
            "recovery_metrics": recovery_metrics,
            "ai_suggestions": ai_suggestions
        })

        # 5. Опубликовать событие
        await self.eventbus.publish("bia.created", bia)

        return bia
```

---

## 4. AI Workflow Optimizer

**Location:** `intelligent-core/ai_workflow_optimizer/`
**Port:** 8006
**LOC:** 946 lines

### Архитектура компонентов

```mermaid
graph TB
    subgraph "API Layer"
        API[FastAPI App<br/>main.py]
    end

    subgraph "ML Pipeline"
        FEATURE_ENG[Feature Engineering<br/>feature_engineering.py<br/>━━━━━━━━━━━<br/>• Extract features<br/>• Normalize data<br/>• Handle missing values]

        MODEL_TRAINER[Model Trainer<br/>model_trainer.py<br/>━━━━━━━━━━━<br/>• Train RandomForest<br/>• Train IsolationForest<br/>• Cross-validation]

        PREDICTOR[Predictor<br/>predictor.py<br/>━━━━━━━━━━━<br/>• Predict performance<br/>• Detect anomalies<br/>• Generate recommendations]
    end

    subgraph "Data Layer"
        TRAINING_DATA[(Training Data<br/>PostgreSQL)]
        MODEL_STORAGE[(Model Storage<br/>Disk/S3)]
    end

    API --> FEATURE_ENG
    FEATURE_ENG --> MODEL_TRAINER
    MODEL_TRAINER --> PREDICTOR
    PREDICTOR --> API

    MODEL_TRAINER --> TRAINING_DATA
    MODEL_TRAINER --> MODEL_STORAGE
    PREDICTOR --> MODEL_STORAGE

    style PREDICTOR fill:#fff3e0,stroke:#ff9800,stroke-width:3px
```

### ML Models

```python
# model_trainer.py
class ModelTrainer:
    """Обучение ML моделей для оптимизации workflow"""

    def train_performance_predictor(self):
        """RandomForest для предсказания производительности"""

        features = [
            'workflow_complexity',  # Количество шагов
            'data_volume',          # Объем данных
            'concurrent_executions', # Параллельные выполнения
            'historical_duration'   # Исторические данные
        ]

        X = self.feature_engineering.extract_features(features)
        y = self.training_data['execution_time']

        model = RandomForestRegressor(n_estimators=100, max_depth=10)
        model.fit(X, y)

        # Cross-validation
        scores = cross_val_score(model, X, y, cv=5)
        print(f"CV Score: {scores.mean():.3f}")

        return model

    def train_anomaly_detector(self):
        """IsolationForest для детекции аномалий"""

        features = self.feature_engineering.extract_features()

        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(features)

        return model
```

---

## 5. EventBus (Message Infrastructure)

**Location:** `infrastructure/runtime/eventbus/`

### Архитектура компонентов

```mermaid
graph TB
    subgraph "Core Components"
        PRODUCER[Event Producer<br/>producer.py<br/>━━━━━━━━━━━<br/>• Publish events<br/>• Serialize data<br/>• Handle retries]

        CONSUMER[Event Consumer<br/>consumer.py<br/>━━━━━━━━━━━<br/>• Subscribe to topics<br/>• Deserialize data<br/>• Acknowledge messages]

        ROUTER[Event Router<br/>router.py<br/>━━━━━━━━━━━<br/>• Topic routing<br/>• Pattern matching<br/>• Dead letter queue]
    end

    subgraph "Backend"
        REDIS_STREAMS[(Redis Streams<br/>Persistent log)]
    end

    subgraph "Subscribers"
        SUB1[Risk Service<br/>Subscribe: bia.*]
        SUB2[Notification Service<br/>Subscribe: *.completed]
        SUB3[Audit Logger<br/>Subscribe: *]
    end

    PRODUCER --> ROUTER
    ROUTER --> REDIS_STREAMS
    REDIS_STREAMS --> CONSUMER
    CONSUMER --> SUB1
    CONSUMER --> SUB2
    CONSUMER --> SUB3

    style ROUTER fill:#fce4ec,stroke:#e91e63,stroke-width:3px
```

### Event Flow Pattern

```python
# producer.py
class EventProducer:
    """Публикация событий в EventBus"""

    async def publish(self, event_type: str, payload: dict):
        """
        Publish event with retry logic

        Args:
            event_type: "bia.created", "risk.assessed", etc.
            payload: Event data
        """

        event = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "source": self.service_name,
                "version": "1.0"
            }
        }

        # Publish to Redis Stream
        await self.redis.xadd(
            f"stream:{event_type}",
            {"data": json.dumps(event)},
            maxlen=10000  # Retain last 10k events
        )

# consumer.py
class EventConsumer:
    """Подписка на события из EventBus"""

    async def subscribe(self, pattern: str, handler: Callable):
        """
        Subscribe to events matching pattern

        Args:
            pattern: "bia.*", "*.completed", etc.
            handler: Async function to handle event
        """

        while True:
            # Read from stream
            events = await self.redis.xread(
                {f"stream:{pattern}": "$"},
                count=100,
                block=1000
            )

            for stream, messages in events:
                for msg_id, msg_data in messages:
                    event = json.loads(msg_data[b'data'])

                    try:
                        await handler(event)
                        await self.redis.xack(stream, self.consumer_group, msg_id)
                    except Exception as e:
                        # Dead letter queue
                        await self.handle_failure(event, e)
```

---

## 6. Common Patterns

### 6.1 Repository Pattern (Data Access)

```python
# repository_base.py
class RepositoryBase:
    """Базовый класс для всех репозиториев"""

    def __init__(self, db_session):
        self.db = db_session

    async def create(self, entity: dict):
        # Insert into DB
        pass

    async def get_by_id(self, id: str):
        # Select from DB
        pass

    async def update(self, id: str, updates: dict):
        # Update in DB
        pass

    async def delete(self, id: str):
        # Soft delete
        pass

    async def find(self, filters: dict):
        # Query with filters
        pass
```

### 6.2 Service Layer Pattern

```python
# service_base.py
class ServiceBase:
    """Базовый класс для бизнес-логики"""

    def __init__(self, repository, eventbus, cache):
        self.repo = repository
        self.eventbus = eventbus
        self.cache = cache

    async def execute_with_events(self, operation, event_type):
        """Execute operation and publish event"""

        # 1. Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        # 2. Execute business logic
        result = await operation()

        # 3. Save to DB
        await self.repo.create(result)

        # 4. Publish event
        await self.eventbus.publish(event_type, result)

        # 5. Cache result
        await self.cache.set(cache_key, result, ttl=300)

        return result
```

### 6.3 Factory Pattern (Service Creation)

```python
# service_factory.py
class ServiceFactory:
    """Создание сервисов с зависимостями"""

    @staticmethod
    def create_bia_service():
        db = DatabaseConnection()
        redis = RedisConnection()
        eventbus = EventBus(redis)
        cache = CacheManager(redis)

        repository = BIARepository(db)
        workflow_intelligence = WorkflowIntelligenceClient()

        return BIAService(
            repository=repository,
            eventbus=eventbus,
            cache=cache,
            workflow_intelligence=workflow_intelligence
        )
```

---

## Summary

**Ключевые паттерны:**
- ✅ **Layered Architecture** (API → Business Logic → Data Access)
- ✅ **Repository Pattern** (абстракция доступа к данным)
- ✅ **Service Layer** (бизнес-логика)
- ✅ **Factory Pattern** (создание объектов с зависимостями)
- ✅ **Circuit Breaker** (защита от каскадных сбоев)
- ✅ **Event-Driven** (асинхронная коммуникация)

**Технологии:**
- FastAPI (REST APIs)
- SQLAlchemy (ORM)
- Redis (Cache + Streams)
- Temporal SDK (Workflows)
- scikit-learn (ML)

---

**Generated:** 2025-10-06
**Source:** Real codebase analysis
**Previous:** [C4 Level 2 - Containers](C4_LEVEL2_CONTAINERS.md)
**Next:** [C4 Level 4 - Code](C4_LEVEL4_CODE.md) (optional)
