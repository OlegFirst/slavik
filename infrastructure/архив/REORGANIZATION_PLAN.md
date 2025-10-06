# План реорганизации Infrastructure

**Дата:** 6 октября 2025
**Проблема:** Есть папки с паттернами (security, reliability, performance, scalability, kubernetes), которые содержат переиспользуемый код, но структура не очевидна

---

## ЧТО У НАС ЕСТЬ СЕЙЧАС

### 1. `/infrastructure/security/` - ИСПОЛЬЗУЕТСЯ ✅

```
security/
├── api-gateway/                       ✅ РАБОТАЕТ (FastAPI gateway)
│   ├── main.py                        - API Gateway service
│   ├── middleware/
│   │   ├── auth.py                    - JWT authentication
│   │   ├── rate_limit.py              - Rate limiting
│   │   ├── audit.py                   - Audit logging
│   │   └── authorization.py           - Authorization
│   ├── routing/
│   │   ├── router.py                  - Request routing
│   │   ├── load_balancer.py           - Load balancing
│   │   └── health_checker.py          - Health checks
│   ├── utils/
│   │   ├── jwt_handler.py             - JWT utilities
│   │   └── redis_client.py            - Redis client
│   └── tests/                         - Tests
│
├── persistent-security/               ✅ ИСПОЛЬЗУЕТСЯ
│   ├── audit_logger.py                - Persistent audit logs
│   └── rate_limiter_redis.py          - Redis rate limiter
│
└── security-headers/                  ✅ ИСПОЛЬЗУЕТСЯ
    ├── middleware.py                  - Security headers middleware
    └── config.py                      - Headers config
```

**Статус:** ✅ **ОСТАВИТЬ КАК ЕСТЬ** - это **работающие сервисы**, не паттерны!

---

### 2. `/infrastructure/reliability/` - ПАТТЕРНЫ ✅

```
reliability/
├── circuit-breaker/                   ✅ ПАТТЕРН
│   ├── circuit_breaker.py             - Circuit breaker implementation
│   ├── decorators.py                  - @circuit_breaker decorator
│   └── tests/
│
├── retry-patterns/                    ✅ ПАТТЕРН
│   ├── retry_decorator.py             - @retry decorator
│   └── examples/
│       ├── eventbus_retry.py          - EventBus retry example
│       └── http_retry.py              - HTTP retry example
│
├── health-checks/                     ✅ ПАТТЕРН
│   └── health_endpoint.py             - Health check endpoint
│
├── graceful-shutdown/                 ✅ ПАТТЕРН
│   └── shutdown_handler.py            - Graceful shutdown handler
│
└── timeouts/                          ✅ ПАТТЕРН
    └── timeout_config.py              - Timeout configuration
```

**Статус:** ✅ **ОСТАВИТЬ** - это **библиотека паттернов** для переиспользования

**Назначение:** Shared patterns, которые используют другие сервисы

---

### 3. `/infrastructure/performance/` - ПАТТЕРНЫ ✅

```
performance/
├── caching/                           ✅ ПАТТЕРН
│   ├── cache_decorator.py             - @cache decorator
│   ├── cache_manager.py               - Cache manager
│   └── invalidation.py                - Cache invalidation
│
├── connection-pooling/                ✅ ПАТТЕРН
│   ├── pooled_client.py               - Connection pool client
│   └── benchmarks.py                  - Performance benchmarks
│
├── database/                          ✅ ПАТТЕРН
│   └── query_analyzer.py              - SQL query analyzer
│
├── load-testing/                      ✅ ИНСТРУМЕНТЫ
│   └── locustfile.py                  - Load testing with Locust
│
└── persistent-storage/                ⚠️ УСТАРЕЛО?
    └── scripts/
        ├── migrate_metrics.py         - Migrate metrics to DB
        └── migrate_logs.py            - Migrate logs to DB
```

**Статус:** ✅ **ОСТАВИТЬ** - это **библиотека паттернов** для переиспользования

**Назначение:** Shared patterns для оптимизации производительности

---

### 4. `/infrastructure/scalability/` - ПАТТЕРНЫ + DOCS ✅

```
scalability/
├── README.md                          ✅ ДОКУМЕНТАЦИЯ
├── SCALABILITY_GUIDE.md               ⚠️ ПУСТО
│
├── websocket-scaling/                 ✅ ИСПОЛЬЗУЕТСЯ
│   └── connection_manager.py          - WebSocket connection manager
│
├── kubernetes-hpa/                    ⚠️ ПАТТЕРН
│   └── hpa_config.yaml                - Horizontal Pod Autoscaler
│
├── load-balancer/                     ⚠️ ПАТТЕРН
│   └── nginx_config.conf              - Nginx load balancer config
│
└── service-mesh/                      ⚠️ ПАТТЕРН
    └── istio_config.yaml              - Istio service mesh config
```

**Статус:** ✅ **ОСТАВИТЬ** - это **библиотека паттернов** + рабочий код (websocket-scaling)

**Назначение:** Scalability patterns и конфигурации

---

### 5. `/infrastructure/kubernetes/` - ПУСТЫЕ ПАПКИ ⚠️

```
kubernetes/
├── deployments/                       ❌ ПУСТО
├── ingress/                           ❌ ПУСТО
├── namespaces/                        ❌ ПУСТО
└── services/                          ❌ ПУСТО
```

**Статус:** ⚠️ **ЗАПОЛНИТЬ или ПЕРЕМЕСТИТЬ**

**Проблема:** Пустые папки, но должны быть K8s манифесты

---

## РЕШЕНИЕ: ЧТО ДЕЛАТЬ?

### Вариант A: ОСТАВИТЬ КАК ЕСТЬ ⭐ (рекомендую)

**Логика:**
```
infrastructure/
│
├── СЕРВИСЫ (запускаемые)
│   ├── database/
│   ├── eventbus/
│   ├── monitoring/
│   ├── deployment-service/
│   ├── github-integration/
│   └── security/api-gateway/        ← это СЕРВИС!
│
├── БИБЛИОТЕКИ ПАТТЕРНОВ (переиспользуемый код)
│   ├── reliability/                 ← паттерны
│   ├── performance/                 ← паттерны
│   ├── scalability/                 ← паттерны + код
│   └── security/                    ← сервис + паттерны
│
└── КОНФИГУРАЦИИ (deployment configs)
    └── kubernetes/                  ← манифесты
```

**Плюсы:**
- Логично разделено: сервисы vs паттерны
- `reliability/`, `performance/`, `scalability/` - это **shared libraries**
- Ничего не ломаем
- Все импорты работают

**Минусы:**
- Не сразу понятно что паттерны, что сервисы

---

### Вариант B: РЕОРГАНИЗОВАТЬ

```
infrastructure/
│
├── services/                        ← все запускаемые сервисы
│   ├── database/
│   ├── eventbus/
│   ├── api-gateway/                 (из security/)
│   ├── monitoring/
│   ├── deployment-service/
│   └── github-integration/
│
├── shared/                          ← переиспользуемые паттерны
│   ├── reliability/
│   ├── performance/
│   ├── scalability/
│   └── security-patterns/           (из security/)
│
└── deployment/                      ← deployment configs
    ├── kubernetes/
    ├── docker-compose/
    └── terraform/
```

**Плюсы:**
- Четкая структура
- Понятно что где

**Минусы:**
- Нужно переименовывать папки
- Ломаются все импорты
- Много работы (6-8 часов)

---

### Вариант C: ГИБРИД (добавить README) ⭐⭐

**Оставить структуру, добавить документацию:**

```
infrastructure/
│
├── README.md                        ← СОЗДАТЬ (объяснить структуру)
│
├── SERVICES (запускаемые сервисы)
│   ├── database/
│   ├── eventbus/
│   ├── monitoring/
│   ├── deployment-service/
│   ├── github-integration/
│   └── security/api-gateway/
│
├── PATTERNS (библиотеки паттернов для переиспользования)
│   ├── reliability/
│   ├── performance/
│   ├── scalability/
│   └── security/                    (+ api-gateway сервис)
│
└── DEPLOYMENT (конфигурации)
    └── kubernetes/
```

**Действия:**
1. Создать `/infrastructure/README.md` с объяснением структуры
2. Добавить пометки в папках:
   - `reliability/README.md` - "Shared patterns library"
   - `performance/README.md` - "Shared patterns library"
   - `scalability/README.md` - "Shared patterns library"
3. Заполнить `kubernetes/` манифестами

**Плюсы:**
- Ничего не ломаем
- Добавляем ясность через документацию
- Быстро (1-2 часа)

**Минусы:**
- Структура остается "странной"

---

## РЕКОМЕНДАЦИЯ: ВАРИАНТ C (Гибрид)

### Шаг 1: Создать `/infrastructure/README.md`

```markdown
# Infrastructure

## Структура

### 🚀 Services (запускаемые сервисы)
- `database/` - PostgreSQL + Redis + managers
- `eventbus/` - Event-driven messaging (Memory + Redis Streams)
- `monitoring/` - Prometheus + Grafana
- `security/api-gateway/` - API Gateway с auth, rate limiting
- `deployment-service/` - Deployment automation
- `github-integration/` - GitHub webhooks, Copilot integration

### 📚 Shared Patterns (библиотеки для переиспользования)
- `reliability/` - Circuit breaker, retry patterns, health checks
- `performance/` - Caching, connection pooling, query optimization
- `scalability/` - WebSocket scaling, load balancing, service mesh
- `security/` - Security patterns (+ API Gateway service)

### 🎯 Deployment (конфигурации развертывания)
- `kubernetes/` - K8s manifests (deployments, services, ingress)

## Как использовать паттерны

```python
# Circuit breaker
from infrastructure.reliability.circuit_breaker import CircuitBreaker

# Caching
from infrastructure.performance.caching import cache_decorator

# WebSocket scaling
from infrastructure.scalability.websocket_scaling import ConnectionManager
```
```

---

### Шаг 2: Добавить README в папки с паттернами

**`/infrastructure/reliability/README.md`:**
```markdown
# Reliability Patterns

Библиотека паттернов для надежности сервисов.

## Компоненты

- **Circuit Breaker** - предотвращение каскадных сбоев
- **Retry Patterns** - автоматические повторы запросов
- **Health Checks** - проверки здоровья сервисов
- **Graceful Shutdown** - корректное завершение
- **Timeouts** - настройка таймаутов

## Использование

```python
from infrastructure.reliability.circuit_breaker import CircuitBreaker

breaker = CircuitBreaker(threshold=5, timeout=60)

@breaker.protect
async def call_external_service():
    ...
```
```

**`/infrastructure/performance/README.md`:**
```markdown
# Performance Patterns

Библиотека паттернов для оптимизации производительности.

## Компоненты

- **Caching** - декораторы кэширования
- **Connection Pooling** - пулы соединений
- **Query Analyzer** - анализ SQL запросов
- **Load Testing** - нагрузочное тестирование

## Использование

```python
from infrastructure.performance.caching import cache_decorator

@cache_decorator(ttl=300)
async def expensive_operation():
    ...
```
```

**`/infrastructure/scalability/README.md`:**
```markdown
# Scalability Patterns

Библиотека паттернов для масштабирования.

## Компоненты

- **WebSocket Scaling** - масштабирование WebSocket соединений
- **Kubernetes HPA** - Horizontal Pod Autoscaler configs
- **Load Balancer** - конфигурации Nginx
- **Service Mesh** - конфигурации Istio

## Использование

```python
from infrastructure.scalability.websocket_scaling import ConnectionManager

manager = ConnectionManager()
await manager.connect(websocket, room_id)
```
```

---

### Шаг 3: Заполнить `/infrastructure/kubernetes/`

**Создать базовые манифесты:**

**`kubernetes/namespaces/bcm-platform.yaml`:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: bcm-platform
  labels:
    name: bcm-platform
```

**`kubernetes/deployments/api-gateway.yaml`:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: bcm-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: bcm-platform/api-gateway:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          value: "redis://redis:6379"
```

**`kubernetes/services/api-gateway-service.yaml`:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: bcm-platform
spec:
  selector:
    app: api-gateway
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

**`kubernetes/ingress/main-ingress.yaml`:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bcm-platform-ingress
  namespace: bcm-platform
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: api.bcm-platform.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 80
```

---

## ИТОГОВАЯ СТРУКТУРА (после реорганизации)

```
infrastructure/
│
├── README.md                          ✅ СОЗДАТЬ
│
├── 🚀 SERVICES (запускаемые)
│   ├── database/                      ✅
│   ├── eventbus/                      ✅
│   ├── auth/                          ✅
│   ├── monitoring/                    ✅
│   ├── service-discovery/             ✅
│   ├── deployment-service/            ✅
│   ├── github-integration/            ✅
│   ├── notification-service/          ⚠️
│   ├── realtime-websocket/            ⚠️
│   ├── message-queue/                 ⚠️
│   ├── process_mining_service/        ⚠️
│   ├── secrets-manager/               ⚠️
│   ├── docker-management/             ⚠️
│   ├── mcp-server/                    ⚠️
│   └── intelligent-gateway/           ⚠️
│
├── 📚 SHARED PATTERNS (библиотеки)
│   ├── security/                      ✅
│   │   ├── api-gateway/               ← сервис + паттерны
│   │   ├── persistent-security/       ← паттерны
│   │   └── security-headers/          ← паттерны
│   ├── reliability/                   ✅
│   │   ├── README.md                  ✅ СОЗДАТЬ
│   │   ├── circuit-breaker/
│   │   ├── retry-patterns/
│   │   ├── health-checks/
│   │   ├── graceful-shutdown/
│   │   └── timeouts/
│   ├── performance/                   ✅
│   │   ├── README.md                  ✅ СОЗДАТЬ
│   │   ├── caching/
│   │   ├── connection-pooling/
│   │   ├── database/
│   │   └── load-testing/
│   └── scalability/                   ✅
│       ├── README.md                  ✅ СОЗДАТЬ
│       ├── websocket-scaling/
│       ├── kubernetes-hpa/
│       ├── load-balancer/
│       └── service-mesh/
│
└── 🎯 DEPLOYMENT (конфигурации)
    ├── kubernetes/                    ⚠️ ЗАПОЛНИТЬ
    │   ├── namespaces/
    │   │   └── bcm-platform.yaml      ✅ СОЗДАТЬ
    │   ├── deployments/
    │   │   └── api-gateway.yaml       ✅ СОЗДАТЬ
    │   ├── services/
    │   │   └── api-gateway-service.yaml ✅ СОЗДАТЬ
    │   └── ingress/
    │       └── main-ingress.yaml      ✅ СОЗДАТЬ
    └── observability/                 ❌ (будущее)
```

---

## ПЛАН ДЕЙСТВИЙ

### Сейчас (1-2 часа):

1. ✅ Создать `/infrastructure/README.md`
2. ✅ Создать README в `reliability/`, `performance/`, `scalability/`
3. ✅ Создать базовые K8s манифесты

### Потом (опционально):

4. Заполнить `kubernetes/` полными манифестами для всех сервисов
5. Добавить Helm charts (если нужно)

---

## ВЫВОДЫ

**Рекомендую: Вариант C (Гибрид)**

**Почему:**
- Ничего не ломаем (все импорты работают)
- Добавляем ясность через документацию
- Быстро (1-2 часа)
- Логично: сервисы + паттерны + deployment

**Что делать:**
1. Создать README файлы (объяснить структуру)
2. Заполнить kubernetes/ базовыми манифестами
3. Всё остальное оставить как есть

**Результат:**
- Понятная структура
- Рабочий код
- Готово к использованию

Делаем?
