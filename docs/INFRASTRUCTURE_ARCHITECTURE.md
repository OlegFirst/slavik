# Infrastructure Architecture - AI-First BCM Platform

**Дата:** 2025-10-02
**Версия:** 2.0
**Философия:** Intelligence-driven, orchestrated infrastructure

---

## Ключевые архитектурные решения

### 1. Трехуровневая база данных
### 2. Coordination Center (руки мозгов)
### 3. Intelligent Orchestration
### 4. Event-Driven Communication

---

## 1. Трехуровневая архитектура баз данных

### Проблема с монолитной БД:
- Смешивание системных, платформенных и пользовательских данных
- Риски безопасности (AI имеет доступ ко всему)
- Сложность обслуживания и backup
- Нет изоляции для критичных операций

### Решение: 3 отдельных базы данных

```
┌─────────────────────────────────────────────────────────┐
│  LEVEL 1: SYSTEM DATABASE (Brain & Intelligence)       │
│  ┌───────────────────────────────────────────────────┐  │
│  │ • AI decision logs                                │  │
│  │ • Knowledge graph (Neo4j)                         │  │
│  │ • Vector embeddings (Qdrant)                      │  │
│  │ • Pattern recognition data                        │  │
│  │ • Model training data                             │  │
│  │ • System-level metrics                            │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  Access: ТОЛЬКО Intelligent Core                         │
│  Backup: Ежечасно                                        │
│  Security: Encrypted at rest + in transit                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  LEVEL 2: PLATFORM DATABASE (Infrastructure & Coord)    │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Schemas:                                          │  │
│  │ • auth           - Users, roles, permissions      │  │
│  │ • platform       - Tenants, subscriptions         │  │
│  │ • coordination   - Task queue, workflows          │  │
│  │ • events         - Event bus, domain events       │  │
│  │ • audit          - Platform audit logs            │  │
│  │ • integrations   - External system configs        │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  Access: Platform services + Coordination Center         │
│  Backup: Каждые 6 часов                                  │
│  Security: RLS enabled, multi-tenant isolation           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  LEVEL 3: BUSINESS DATABASE (User/BCM Data)             │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Schemas:                                          │  │
│  │ • public         - Organizations, users           │  │
│  │ • community      - Specialists, marketplace       │  │
│  │ • bia            - Business impact analysis       │  │
│  │ • risk           - Risk assessments               │  │
│  │ • governance     - Policies, objectives           │  │
│  │ • response       - Incidents, crisis mgmt         │  │
│  │ • validation     - Exercises, audits, CAPA        │  │
│  │ • documents      - Document management            │  │
│  │ • intelligence   - Digital twins, simulations     │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  Access: Execution Engine + Coordination Center          │
│  Backup: Каждые 4 часа                                   │
│  Security: RLS per tenant, row-level encryption          │
└─────────────────────────────────────────────────────────┘
```

### Преимущества разделения:

**Безопасность:**
- AI не имеет прямого доступа к пользовательским данным
- Можно дать AI read-only к Level 3 через Coordination Center
- Утечка одной БД не компрометирует всю систему

**Производительность:**
- Level 1 оптимизирована под векторные операции и граф
- Level 2 оптимизирована под частые read/write (координация)
- Level 3 оптимизирована под OLTP (транзакции пользователей)

**Масштабирование:**
- Каждый уровень можно масштабировать независимо
- Level 1 можно вынести на специализированное железо (GPU)
- Level 3 можно шардировать по tenant_id

**Обслуживание:**
- Разные политики backup (Level 1 - ежечасно, Level 3 - каждые 4 часа)
- Разные retention политики
- Можно делать maintenance Level 2 без влияния на пользователей

**Соответствие регуляциям:**
- Level 3 можно разместить в регионе клиента (GDPR, data residency)
- Level 1 и 2 в любом регионе
- Easier compliance audits

---

## 2. Coordination Center - Руки для мозгов

### Проблема:
В текущей архитектуре **Intelligent Core** (мозги) напрямую вызывает **Execution Engine** (инструменты). Это создает:
- Tight coupling между AI и бизнес-логикой
- AI должен знать все API endpoints
- Сложность тестирования и отладки
- Невозможность отменить/откатить решения AI

### Решение: Coordination Center как посредник

```
┌──────────────────────────────────────────────────────────┐
│              INTELLIGENT CORE (Мозги)                     │
│  • Принимает решения                                     │
│  • Анализирует ситуацию                                  │
│  • Генерирует план действий                              │
│  • НЕ выполняет напрямую                                 │
└──────────────────────────────────────────────────────────┘
                          ↓ (Intent/Command)
┌──────────────────────────────────────────────────────────┐
│           COORDINATION CENTER (Руки)                      │
│  ┌────────────────────────────────────────────────────┐  │
│  │  COMMAND INTERPRETER                               │  │
│  │  • Получает Intent от Intelligent Core            │  │
│  │  │  Example: {                                     │  │
│  │  │    "intent": "create_bia",                      │  │
│  │  │    "params": {"org_id": 123, "scope": "IT"}    │  │
│  │  │  }                                              │  │
│  │  │                                                 │  │
│  │  • Транслирует в конкретные API calls             │  │
│  │  • Добавляет контекст (auth, tenant_id)           │  │
│  │  • Валидирует параметры                           │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │  WORKFLOW ORCHESTRATOR                             │  │
│  │  • Разбивает команду на шаги                      │  │
│  │  • Управляет последовательностью вызовов          │  │
│  │  • Обрабатывает ошибки и retry                    │  │
│  │  • Логирует каждый шаг                            │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │  TOOL REGISTRY                                     │  │
│  │  • Каталог всех доступных инструментов            │  │
│  │  • Intelligent Core не знает API напрямую         │  │
│  │  • Tools:                                          │  │
│  │    - create_bia_process()                         │  │
│  │    - assess_risk()                                │  │
│  │    - activate_plan()                              │  │
│  │    - send_notification()                          │  │
│  │    - generate_report()                            │  │
│  │    - etc...                                       │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │  EXECUTION TRACKER                                 │  │
│  │  • Отслеживает статус выполнения                  │  │
│  │  • Сохраняет результаты                           │  │
│  │  • Позволяет отменить/откатить                    │  │
│  │  • Real-time прогресс для UI                      │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │  SECURITY LAYER                                    │  │
│  │  • Проверяет права AI на действие                │  │
│  │  • Требует human approval для критичных операций  │  │
│  │  • Rate limiting для AI                           │  │
│  │  • Audit log всех AI действий                     │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                          ↓ (API Calls)
┌──────────────────────────────────────────────────────────┐
│            EXECUTION ENGINE (Инструменты)                 │
│  • BIA Service                                           │
│  • Risk Service                                          │
│  • Planning Service                                      │
│  • Response Service                                      │
│  • etc...                                                │
└──────────────────────────────────────────────────────────┘
```

### Пример работы:

**1. Intelligent Core принимает решение:**
```python
# AI видит: Risk score стал HIGH
decision = {
    "intent": "mitigate_high_risk",
    "reasoning": "Risk R-123 escalated to HIGH. Need immediate BIA.",
    "actions": [
        {
            "tool": "create_bia_process",
            "params": {
                "org_id": 123,
                "risk_id": "R-123",
                "scope": "IT Infrastructure",
                "priority": "urgent"
            }
        },
        {
            "tool": "notify_stakeholders",
            "params": {
                "org_id": 123,
                "recipients": ["bcm_manager", "cto"],
                "template": "high_risk_alert"
            }
        }
    ],
    "requires_approval": False  # AI может выполнить автономно
}

# AI НЕ вызывает API напрямую! Отправляет команду в Coordination Center
coordination_center.execute_intent(decision)
```

**2. Coordination Center обрабатывает:**
```python
class CoordinationCenter:
    async def execute_intent(self, intent: Intent):
        # 1. Валидация
        if not self.validate_intent(intent):
            return {"status": "rejected", "reason": "Invalid parameters"}

        # 2. Security check
        if intent.requires_approval and not await self.get_human_approval(intent):
            return {"status": "pending_approval"}

        # 3. Создать execution record
        execution_id = await self.tracker.create_execution(intent)

        # 4. Выполнить каждый action
        results = []
        for action in intent.actions:
            try:
                # Найти tool в registry
                tool = self.tools.get(action.tool)

                # Добавить контекст (auth, tenant, etc.)
                enriched_params = self.enrich_params(action.params)

                # Вызвать инструмент
                result = await tool.execute(**enriched_params)

                # Сохранить результат
                await self.tracker.log_step(execution_id, action.tool, result)
                results.append(result)

            except Exception as e:
                # Обработать ошибку
                await self.tracker.log_error(execution_id, action.tool, e)

                # Откатить предыдущие действия если нужно
                if intent.transactional:
                    await self.rollback(execution_id, results)

                return {"status": "failed", "error": str(e)}

        # 5. Вернуть результаты в Intelligent Core
        return {
            "status": "completed",
            "execution_id": execution_id,
            "results": results
        }
```

**3. Результат возвращается в AI:**
```python
# Intelligent Core получает результат
result = await coordination_center.execute_intent(decision)

# AI анализирует результат и учится
if result["status"] == "completed":
    self.learning_engine.record_success(decision, result)
else:
    self.learning_engine.record_failure(decision, result)
    # AI может принять новое решение
```

### Преимущества Coordination Center:

**Decoupling:**
- AI не знает про API endpoints
- Можно менять Execution Engine без изменения AI
- Легче тестировать и отлаживать

**Security:**
- Все AI действия проходят через единую точку контроля
- Можно добавить human-in-the-loop для критичных операций
- Audit trail всех AI решений

**Observability:**
- Видно что AI пытался сделать
- Видно что реально выполнилось
- Можно откатить действия AI

**Transactional integrity:**
- Можно сделать группу действий транзакционной
- Rollback если что-то пошло не так

**Rate limiting & Cost control:**
- Можно лимитировать частоту AI действий
- Контроль стоимости (API calls, DB queries)

---

## 3. Intelligent Orchestration - Умное управление

### Проблема статической архитектуры:
- API Gateway тупо маршрутизирует (if path.startswith("/api/bia") → bia_service)
- Нет адаптации под нагрузку
- Нет приоритизации запросов
- Нет оптимизации маршрутов

### Решение: Intelligent API Gateway

```python
class IntelligentGateway:
    """
    API Gateway с AI-powered routing, caching, load balancing
    """

    async def route_request(self, request: Request):
        # 1. Analyze request
        analysis = await self.analyze_request(request)
        # {
        #   "endpoint": "/api/bia/processes",
        #   "method": "POST",
        #   "user_id": "user-123",
        #   "tenant_id": "org-456",
        #   "estimated_complexity": "medium",  # AI оценка
        #   "priority": "high",  # Из контекста
        #   "cacheable": False
        # }

        # 2. Check cache (intelligent caching)
        if analysis["cacheable"]:
            cache_key = self.generate_smart_cache_key(request, analysis)
            cached = await self.redis.get(cache_key)
            if cached:
                return cached

        # 3. Find target service
        target_service = self.service_registry.find(analysis["endpoint"])

        # 4. Intelligent load balancing
        # Не просто round-robin, а с учетом:
        # - Текущей нагрузки на инстансы
        # - Сложности запроса (AI estimation)
        # - Приоритета пользователя
        instance = await self.intelligent_load_balancer.select_instance(
            service=target_service,
            complexity=analysis["estimated_complexity"],
            priority=analysis["priority"]
        )

        # 5. Adaptive timeout
        # AI предсказывает сколько времени займет запрос
        timeout = await self.predict_timeout(analysis)

        # 6. Execute with circuit breaker
        try:
            response = await self.execute_with_retry(
                instance,
                request,
                timeout=timeout,
                max_retries=3
            )
        except ServiceUnavailable:
            # Fallback to alternative instance or degraded mode
            response = await self.fallback_handler(request, analysis)

        # 7. Cache if applicable
        if analysis["cacheable"]:
            await self.redis.set(cache_key, response, ttl=self.predict_cache_ttl(analysis))

        # 8. Learn from execution
        await self.learning_engine.record_execution(analysis, response)

        return response


    async def predict_timeout(self, analysis: Dict) -> int:
        """
        AI предсказывает timeout на основе:
        - Исторических данных по этому endpoint
        - Сложности запроса
        - Текущей нагрузки
        """
        historical_p95 = await self.metrics.get_p95_latency(
            endpoint=analysis["endpoint"],
            window="15m"
        )

        complexity_multiplier = {
            "low": 1.0,
            "medium": 1.5,
            "high": 2.0
        }[analysis["estimated_complexity"]]

        load_multiplier = await self.get_load_multiplier()

        predicted_timeout = historical_p95 * complexity_multiplier * load_multiplier

        # Add safety margin
        return int(predicted_timeout * 1.5)


    async def intelligent_load_balancer.select_instance(
        self,
        service: str,
        complexity: str,
        priority: str
    ) -> Instance:
        """
        Умный выбор инстанса с учетом:
        - Current load на каждом инстансе
        - Request complexity (не посылать heavy на занятый инстанс)
        - Priority (VIP клиенты на выделенные инстансы)
        """
        instances = self.service_registry.get_healthy_instances(service)

        # Собрать метрики по каждому инстансу
        instance_scores = []
        for instance in instances:
            metrics = await self.metrics.get_instance_metrics(instance.id)

            score = self.calculate_instance_score(
                cpu_usage=metrics["cpu"],
                memory_usage=metrics["memory"],
                active_requests=metrics["active_requests"],
                avg_response_time=metrics["avg_response_time"],
                complexity=complexity,
                priority=priority
            )

            instance_scores.append((instance, score))

        # Выбрать инстанс с лучшим score
        best_instance = max(instance_scores, key=lambda x: x[1])[0]

        return best_instance
```

### Intelligent Database Connection Pool

```python
class IntelligentConnectionPool:
    """
    Умный connection pool с AI-powered:
    - Prefetching (предсказывает нужные соединения)
    - Adaptive sizing (меняет размер пула под нагрузку)
    - Query optimization hints
    """

    async def get_connection(self, context: RequestContext):
        # 1. Predict query pattern
        predicted_queries = await self.ai.predict_queries(context)
        # AI смотрит: "Пользователь открыл BIA module → вероятно запросит processes"

        # 2. Prefetch connection for predicted DB
        if predicted_queries:
            await self.prefetch_connections(predicted_queries)

        # 3. Get connection from pool
        conn = await self.pool.acquire()

        # 4. Set RLS context
        await conn.set_rls_context(
            user_id=context.user_id,
            tenant_id=context.tenant_id
        )

        # 5. Apply query hints (если AI предсказал тяжелый запрос)
        if context.estimated_complexity == "high":
            await conn.execute("SET statement_timeout = '30s'")
            await conn.execute("SET work_mem = '256MB'")

        return conn


    async def adaptive_pool_sizing(self):
        """
        Автоматически меняет размер пула под нагрузку
        """
        while True:
            await asyncio.sleep(60)  # Каждую минуту

            metrics = await self.get_pool_metrics()
            # {
            #   "utilization": 0.85,  # 85% connections in use
            #   "wait_time_p95": 0.2,  # 200ms wait time
            #   "active_connections": 17,
            #   "max_connections": 20
            # }

            # AI решает нужно ли менять размер пула
            decision = await self.ai.decide_pool_size(metrics)

            if decision["action"] == "increase":
                await self.pool.resize(decision["new_size"])
                logger.info(f"Pool resized: {metrics['max_connections']} → {decision['new_size']}")

            elif decision["action"] == "decrease":
                await self.pool.resize(decision["new_size"])
```

---

## 4. Event-Driven Architecture - Асинхронная координация

### Проблема синхронных вызовов:
- Intelligent Core → Coordination Center → Execution Engine (sync chain)
- Если Execution Engine медленный → блокирует AI
- Нет возможности параллельного выполнения
- Сложность retry и error handling

### Решение: Event Bus

```
┌─────────────────────────────────────────────────────────┐
│                    EVENT BUS (Redis Streams)             │
│  ┌─────────────────────────────────────────────────────┐│
│  │  Channels:                                          ││
│  │  • ai.decisions      - AI принял решение           ││
│  │  • coordination.commands - Команды для выполнения  ││
│  │  • execution.results - Результаты выполнения       ││
│  │  • domain.events     - Бизнес события              ││
│  │  • system.alerts     - Системные алерты            ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
         ↑ publish          ↓ subscribe
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Intelligent  │   │ Coordination │   │  Execution   │
│    Core      │   │   Center     │   │   Engine     │
└──────────────┘   └──────────────┘   └──────────────┘
```

### Пример async workflow:

```python
# 1. AI принимает решение и публикует event
await event_bus.publish("ai.decisions", {
    "decision_id": "dec-123",
    "intent": "create_bia",
    "params": {...},
    "priority": "high",
    "timestamp": "2025-10-02T12:00:00Z"
})

# 2. Coordination Center слушает канал ai.decisions
@event_bus.subscribe("ai.decisions")
async def handle_ai_decision(event):
    decision = event.data

    # Транслировать в команды
    commands = coordination_center.translate_to_commands(decision)

    for cmd in commands:
        await event_bus.publish("coordination.commands", cmd)

# 3. Execution Engine слушает coordination.commands
@event_bus.subscribe("coordination.commands")
async def handle_command(event):
    command = event.data

    # Выполнить команду
    result = await execution_engine.execute(command)

    # Опубликовать результат
    await event_bus.publish("execution.results", {
        "command_id": command["id"],
        "decision_id": command["decision_id"],
        "status": "completed",
        "result": result
    })

# 4. AI слушает execution.results и учится
@event_bus.subscribe("execution.results")
async def handle_execution_result(event):
    result = event.data

    # Найти оригинальное решение
    decision = await intelligent_core.get_decision(result["decision_id"])

    # Обновить learning model
    await intelligent_core.learning_engine.record_outcome(decision, result)
```

---

## 5. Итоговая архитектура инфраструктуры

```
┌───────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                          │
│  Supabase, OpenAI, Anthropic, Resend, Upstash, etc.          │
└───────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                          │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  INTELLIGENT API GATEWAY                                 ││
│  │  • Smart routing                                         ││
│  │  • Intelligent caching                                   ││
│  │  • Adaptive load balancing                               ││
│  │  • Circuit breaker                                       ││
│  │  • Rate limiting                                         ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  EVENT BUS (Redis Streams)                               ││
│  │  • ai.decisions                                          ││
│  │  • coordination.commands                                 ││
│  │  • execution.results                                     ││
│  │  • domain.events                                         ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  DATABASE LAYER (3 levels)                               ││
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        ││
│  │  │  System    │  │ Platform   │  │  Business  │        ││
│  │  │  Database  │  │ Database   │  │  Database  │        ││
│  │  └────────────┘  └────────────┘  └────────────┘        ││
│  │                                                          ││
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        ││
│  │  │  Neo4j     │  │  Qdrant    │  │ TimescaleDB│        ││
│  │  │  (Graph)   │  │  (Vector)  │  │ (Metrics)  │        ││
│  │  └────────────┘  └────────────┘  └────────────┘        ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  CACHING & SESSION (Redis/Upstash)                       ││
│  │  • API response cache                                    ││
│  │  • Session storage                                       ││
│  │  • Rate limiting counters                                ││
│  │  • Real-time data                                        ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  AUTH & SECURITY                                         ││
│  │  • Supabase Auth (JWT)                                   ││
│  │  • RLS enforcement                                       ││
│  │  • Encryption (at rest & in transit)                     ││
│  │  • Secrets management (GitHub Secrets)                   ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  OBSERVABILITY                                           ││
│  │  • Metrics (Prometheus)                                  ││
│  │  • Logs (Structured JSON logs)                           ││
│  │  • Traces (OpenTelemetry)                                ││
│  │  • Alerts (Custom alerting system)                       ││
│  └──────────────────────────────────────────────────────────┘│
└───────────────────────────────────────────────────────────────┘
```

---

## 6. Технологический стек инфраструктуры

### Базы данных:
- **PostgreSQL (Supabase)** - 3 instances для 3 уровней
- **Redis (Upstash)** - Кэш, очереди, pub/sub
- **Neo4j (Neo4j Aura)** - Knowledge graph
- **Qdrant (Cloud)** - Vector embeddings
- **TimescaleDB (расширение PostgreSQL)** - Time-series метрики

### API & Gateway:
- **FastAPI** - Core framework
- **HTTPX** - Async HTTP client
- **WebSocket** - Real-time communication

### Auth & Security:
- **Supabase Auth** - JWT-based authentication
- **PostgreSQL RLS** - Row-level security
- **GitHub Secrets** - Secrets management

### Orchestration:
- **Python asyncio** - Async orchestration
- **Redis Streams** - Event bus
- **Celery (optional)** - Background jobs

### Monitoring:
- **Prometheus** - Metrics
- **Grafana** - Dashboards
- **Sentry** - Error tracking
- **Structured logging** - JSON logs

### Deployment:
- **Docker** - Containerization
- **docker-compose** - Local development
- **Kubernetes (future)** - Production orchestration
- **GitHub Actions** - CI/CD

---

## 7. Следующие шаги

### Этап 1: Настройка баз данных (сейчас)
1. Создать 3 Supabase проекта (System, Platform, Business)
2. Применить миграции к каждой БД
3. Настроить RLS policies
4. Создать connection managers для каждой БД

### Этап 2: Coordination Center (следующий)
1. Реализовать Command Interpreter
2. Реализовать Tool Registry
3. Реализовать Execution Tracker
4. Реализовать Security Layer

### Этап 3: Intelligent Gateway
1. Smart routing
2. Intelligent caching
3. Adaptive load balancing
4. Circuit breaker pattern

### Этап 4: Event Bus
1. Redis Streams setup
2. Publisher/Subscriber pattern
3. Event schemas
4. Dead letter queue

---

**Готово к реализации.**
