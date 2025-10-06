# 🏗️ BCM Platform - Системные Сервисы и Модули

**Дата:** 2025-10-03
**Версия:** 1.0
**Статус:** План реализации

---

## 📊 Текущее Состояние

### Готово к использованию (45% инфраструктуры):
- ✅ **API Gateway** (80% - security/api-gateway/)
- ✅ **Secrets Manager** (100% - secrets-manager/)
- ✅ **WebSocket Service** (100% - realtime-websocket/)
- ✅ **Reliability Patterns** (60% - reliability/)
- ✅ **Connection Pooling** (100% - performance/connection-pooling/)
- ✅ **Load Testing** (100% - performance/load-testing/)

### Требует доработки:
- ⚠️ **Performance/Caching** (40% - нужен cache_manager.py)
- ⚠️ **Scalability** (30% - нужен load balancer config)

### Нужно создать с нуля:
- ❌ **Intelligent Gateway** (0% - intelligent-gateway/)
- ❌ **Kubernetes Manifests** (0% - kubernetes/)

---

## 🎯 Необходимые Системные Сервисы

### 1. Core Infrastructure (Критично - Week 1)

#### 1.1 API Gateway ✅ ГОТОВ
**Путь:** `/infrastructure/security/api-gateway/`
**Статус:** 80% готов, нужно деплоить
**Порт:** 8000

**Возможности:**
- JWT Authentication
- Rate Limiting (Redis)
- Audit Logging (PostgreSQL)
- Service Discovery
- Load Balancing
- Health Checks
- Circuit Breaker
- Prometheus Metrics

**Действия:**
1. [x] Код готов
2. [ ] Создать Docker image
3. [ ] Добавить в docker-compose
4. [ ] Настроить маршрутизацию для 18 сервисов
5. [ ] Протестировать

#### 1.2 Secrets Manager (Vault) ✅ ГОТОВ
**Путь:** `/infrastructure/secrets-manager/`
**Статус:** 100% готов
**Порт:** 8200 (Vault)

**Возможности:**
- KV Secrets
- Dynamic Database Credentials
- Encryption as a Service
- Token Management
- Audit Logging

**Действия:**
1. [ ] Развернуть Vault в docker-compose
2. [ ] Инициализировать и unseal
3. [ ] Мигрировать секреты из .env
4. [ ] Настроить AppRole для сервисов

#### 1.3 WebSocket Service ✅ ГОТОВ
**Путь:** `/infrastructure/realtime-websocket/`
**Статус:** 100% готов
**Порт:** 8050

**Возможности:**
- Multi-channel messaging
- User presence tracking
- Message persistence
- Redis caching
- Connection management

**Действия:**
1. [x] Код готов
2. [ ] Добавить JWT authentication
3. [ ] Интеграция с EventBus
4. [ ] Добавить в docker-compose
5. [ ] Протестировать

---

### 2. Reliability & Performance (Week 2)

#### 2.1 Reliability Patterns ✅ ГОТОВ
**Путь:** `/infrastructure/reliability/`
**Статус:** 60% готов

**Компоненты:**
- ✅ Circuit Breaker (готов)
- ✅ Retry Patterns (готов)
- ✅ Health Checks (готов)
- ✅ Graceful Shutdown (готов)
- ✅ Timeout Config (готов)

**Действия:**
1. [ ] Добавить circuit breaker во все межсервисные вызовы
2. [ ] Добавить /health endpoint во все сервисы
3. [ ] Добавить retry для EventBus операций
4. [ ] Graceful shutdown для всех сервисов

#### 2.2 Performance Optimization ⚠️ ТРЕБУЕТ ДОРАБОТКИ
**Путь:** `/infrastructure/performance/`
**Статус:** 40% готов

**Компоненты:**
- ✅ Connection Pooling (готов)
- ❌ Cache Manager (НУЖНО СОЗДАТЬ!)
- ✅ Query Analyzer (готов)
- ✅ Load Testing (готов)

**Действия:**
1. [ ] Создать `caching/cache_manager.py`
2. [ ] Создать `caching/cache_decorator.py`
3. [ ] Внедрить connection pooling во все сервисы
4. [ ] Определить стратегию кэширования для BCM

**Требуемый код:**
```python
# infrastructure/performance/caching/cache_manager.py
import redis.asyncio as redis
from functools import wraps
import json
import hashlib

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    def cache(self, ttl: int = 300, key_prefix: str = ""):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                key = f"{key_prefix}:{self._hash_args(args, kwargs)}"

                # Try cache
                cached = await self.redis.get(key)
                if cached:
                    return json.loads(cached)

                # Cache miss
                result = await func(*args, **kwargs)

                # Cache result
                await self.redis.setex(key, ttl, json.dumps(result))

                return result
            return wrapper
        return decorator

    async def invalidate(self, pattern: str):
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
```

---

### 3. Deployment & Orchestration (Week 3)

#### 3.1 Kubernetes Manifests ❌ СОЗДАТЬ
**Путь:** `/infrastructure/kubernetes/`
**Статус:** 0% (пустые директории)

**Требуемые файлы:**

**Namespaces:**
```yaml
# kubernetes/namespaces/bcm-platform.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: bcm-platform
```

**Deployments (18 сервисов):**
1. coordination-center (8004)
2. bia-service (8005)
3. workflow-intelligence (8006)
4. risk-service (8007)
5. planning-service (8008)
6. compliance-service (8009)
7. governance-service (8010)
8. response-service (8011)
9. learning-service (8012)
10. documents-service (8013)
11. community-service (8014)
12. marketplace (8015)
13. validation-service
14. auth-service (8002)
15. notification-service (8003)
16. realtime-websocket (8050)
17. api-gateway (8000)
18. intelligent-gateway (8080)

**Шаблон Deployment:**
```yaml
# kubernetes/deployments/coordination-center.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: coordination-center
  namespace: bcm-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: coordination-center
  template:
    metadata:
      labels:
        app: coordination-center
    spec:
      containers:
      - name: coordination-center
        image: bcm/coordination-center:latest
        ports:
        - containerPort: 8004
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-credentials
              key: url
        livenessProbe:
          httpGet:
            path: /health
            port: 8004
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8004
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

**Services:**
```yaml
# kubernetes/services/coordination-center.yaml
apiVersion: v1
kind: Service
metadata:
  name: coordination-center
  namespace: bcm-platform
spec:
  selector:
    app: coordination-center
  ports:
  - port: 8004
    targetPort: 8004
  type: ClusterIP
```

**Ingress:**
```yaml
# kubernetes/ingress/api-gateway.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bcm-api-gateway
  namespace: bcm-platform
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.bcm-platform.com
    secretName: bcm-tls
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
              number: 8000
```

**Действия:**
1. [ ] Создать namespace manifest
2. [ ] Создать 18 Deployment manifests
3. [ ] Создать 18 Service manifests
4. [ ] Создать Ingress для API Gateway
5. [ ] Создать ConfigMaps
6. [ ] Создать Secrets (sealed-secrets)

#### 3.2 Scalability ⚠️ ДОРАБОТАТЬ
**Путь:** `/infrastructure/scalability/`
**Статус:** 30% готов

**Компоненты:**
- ✅ HPA manifests (базовые)
- ✅ WebSocket scaling (Redis Pub/Sub)
- ⚠️ Load Balancer (требуется конфигурация)
- ❌ Service Mesh (отложить)

**Действия:**
1. [ ] HPA для критичных сервисов
2. [ ] Настроить Traefik/NGINX load balancer
3. [ ] Интегрировать WebSocket scaling
4. [ ] Service mesh - отложить до масштаба

---

### 4. Advanced Features (Week 4+)

#### 4.1 Intelligent Gateway ❌ СОЗДАТЬ
**Путь:** `/infrastructure/intelligent-gateway/`
**Статус:** 0% (только README)

**Назначение:** AI-powered API Gateway с умной маршрутизацией

**Компоненты для создания:**
1. `routing/analyzer.py` - AI request analyzer
2. `routing/router.py` - Smart router
3. `load_balancing/balancer.py` - Intelligent load balancer
4. `circuit_breaker/breaker.py` - Circuit breaker
5. `caching/smart_cache.py` - AI-powered cache

**Приоритет:** Средний (можно использовать обычный API Gateway пока)

**Действия:**
1. [ ] Отложить до завершения базовой инфраструктуры
2. [ ] Использовать security/api-gateway в качестве основного
3. [ ] Реализовать когда нужны AI features

---

## 📋 Директории и Структура

### Текущая структура (что есть):

```
infrastructure/
├── security/api-gateway/ ✅ ГОТОВ (80%)
│   ├── main.py
│   ├── middleware/
│   ├── routing/
│   └── tests/
│
├── secrets-manager/ ✅ ГОТОВ (100%)
│   └── vault_manager.py
│
├── realtime-websocket/ ✅ ГОТОВ (100%)
│   ├── main.py
│   └── README.md
│
├── reliability/ ✅ ГОТОВ (60%)
│   ├── circuit-breaker/
│   ├── retry-patterns/
│   ├── health-checks/
│   └── graceful-shutdown/
│
├── performance/ ⚠️ ДОРАБОТАТЬ (40%)
│   ├── connection-pooling/ ✅
│   ├── caching/ ❌ (пусто, нужен код!)
│   ├── database/ ✅
│   └── load-testing/ ✅
│
├── scalability/ ⚠️ ДОРАБОТАТЬ (30%)
│   ├── kubernetes-hpa/ ✅
│   ├── websocket-scaling/ ✅
│   ├── load-balancer/ ⚠️ (базовый config)
│   └── service-mesh/ (отложить)
│
├── kubernetes/ ❌ СОЗДАТЬ (0%)
│   ├── namespaces/ (пусто)
│   ├── deployments/ (пусто)
│   ├── services/ (пусто)
│   └── ingress/ (пусто)
│
└── intelligent-gateway/ ❌ СОЗДАТЬ (0%)
    ├── routing/ (пусто)
    ├── load_balancing/ (пусто)
    ├── circuit_breaker/ (пусто)
    └── caching/ (пусто)
```

### Требуемая структура (что нужно):

```
infrastructure/
├── 1_CRITICAL/ (Week 1)
│   ├── api-gateway/ ✅
│   ├── secrets-manager/ ✅
│   └── reliability/ ✅
│
├── 2_HIGH_PRIORITY/ (Week 2)
│   ├── performance/
│   │   ├── caching/ ❌ СОЗДАТЬ!
│   │   └── connection-pooling/ ✅
│   └── realtime-websocket/ ✅
│
├── 3_DEPLOYMENT/ (Week 3)
│   ├── kubernetes/
│   │   ├── namespaces/ ❌ СОЗДАТЬ!
│   │   ├── deployments/ ❌ СОЗДАТЬ (18 файлов)!
│   │   ├── services/ ❌ СОЗДАТЬ (18 файлов)!
│   │   └── ingress/ ❌ СОЗДАТЬ!
│   └── scalability/
│       ├── hpa/ ✅
│       └── load-balancer/ ⚠️ ДОРАБОТАТЬ
│
└── 4_ADVANCED/ (Week 4+)
    └── intelligent-gateway/ ❌ ОТЛОЖИТЬ
```

---

## 🎯 Action Plan

### Week 1: Core Infrastructure (КРИТИЧНО)

**Day 1-2: API Gateway**
- [ ] Создать Dockerfile для API Gateway
- [ ] Добавить в docker-compose
- [ ] Настроить маршрутизацию для 18 сервисов
- [ ] Протестировать authentication
- [ ] Протестировать rate limiting

**Day 3-4: Secrets Manager**
- [ ] Развернуть Vault в docker-compose
- [ ] Инициализировать и unseal
- [ ] Создать структуру секретов (bcm/database, bcm/api-keys, etc)
- [ ] Мигрировать секреты из .env
- [ ] Настроить AppRole authentication

**Day 5: Reliability**
- [ ] Добавить /health endpoint во все сервисы
- [ ] Интегрировать circuit breaker
- [ ] Добавить retry patterns для EventBus

---

### Week 2: Performance & Real-time

**Day 1-2: Caching**
- [ ] Создать `performance/caching/cache_manager.py`
- [ ] Создать `performance/caching/cache_decorator.py`
- [ ] Определить стратегию кэширования
- [ ] Внедрить в критичные сервисы (BIA, Risk, Compliance)

**Day 3: Connection Pooling**
- [ ] Внедрить connection pooling во все сервисы
- [ ] Настроить PostgreSQL pool settings
- [ ] Тестирование под нагрузкой

**Day 4-5: WebSocket Service**
- [ ] Добавить JWT authentication
- [ ] Интеграция с EventBus
- [ ] Добавить в docker-compose
- [ ] Протестировать multi-channel messaging

---

### Week 3: Kubernetes Deployment

**Day 1: Namespaces & ConfigMaps**
- [ ] Создать namespace manifest
- [ ] Создать ConfigMaps для конфигурации
- [ ] Создать Secrets (sealed-secrets)

**Day 2-4: Deployments & Services**
- [ ] Создать 18 Deployment manifests
- [ ] Создать 18 Service manifests
- [ ] Протестировать локально (minikube)

**Day 5: Ingress & Testing**
- [ ] Создать Ingress для API Gateway
- [ ] Протестировать routing
- [ ] Load testing

---

### Week 4: Scalability & Testing

**Day 1-2: HPA**
- [ ] HPA для coordination-center
- [ ] HPA для bia-service
- [ ] HPA для risk-service
- [ ] HPA для compliance-service

**Day 3-4: Load Balancer**
- [ ] Настроить Traefik конфигурацию
- [ ] Health-based routing
- [ ] SSL termination

**Day 5: Load Testing**
- [ ] Запустить Locust tests
- [ ] Запустить k6 tests
- [ ] Анализ bottlenecks
- [ ] Оптимизация

---

## 📁 Файлы для Создания

### Критично (Week 1-2):

```
infrastructure/
├── performance/caching/
│   ├── cache_manager.py ❌ СОЗДАТЬ (200 строк)
│   ├── cache_decorator.py ❌ СОЗДАТЬ (50 строк)
│   └── cache_invalidation.py ❌ СОЗДАТЬ (100 строк)
│
├── security/api-gateway/
│   ├── Dockerfile ❌ СОЗДАТЬ
│   └── docker-compose.yml ❌ СОЗДАТЬ
│
└── realtime-websocket/
    ├── Dockerfile ❌ СОЗДАТЬ
    └── auth_middleware.py ❌ СОЗДАТЬ (100 строк)
```

### Высокий приоритет (Week 3):

```
infrastructure/kubernetes/
├── namespaces/
│   └── bcm-platform.yaml ❌ СОЗДАТЬ
│
├── deployments/
│   ├── coordination-center.yaml ❌ СОЗДАТЬ
│   ├── bia-service.yaml ❌ СОЗДАТЬ
│   ├── workflow-intelligence.yaml ❌ СОЗДАТЬ
│   ├── risk-service.yaml ❌ СОЗДАТЬ
│   ├── planning-service.yaml ❌ СОЗДАТЬ
│   ├── compliance-service.yaml ❌ СОЗДАТЬ
│   ├── governance-service.yaml ❌ СОЗДАТЬ
│   ├── response-service.yaml ❌ СОЗДАТЬ
│   ├── learning-service.yaml ❌ СОЗДАТЬ
│   ├── documents-service.yaml ❌ СОЗДАТЬ
│   ├── community-service.yaml ❌ СОЗДАТЬ
│   ├── marketplace.yaml ❌ СОЗДАТЬ
│   ├── validation-service.yaml ❌ СОЗДАТЬ
│   ├── auth-service.yaml ❌ СОЗДАТЬ
│   ├── notification-service.yaml ❌ СОЗДАТЬ
│   ├── realtime-websocket.yaml ❌ СОЗДАТЬ
│   ├── api-gateway.yaml ❌ СОЗДАТЬ
│   └── intelligent-gateway.yaml ❌ СОЗДАТЬ (отложить)
│
├── services/
│   └── [те же 18 файлов].yaml ❌ СОЗДАТЬ
│
├── ingress/
│   └── api-gateway.yaml ❌ СОЗДАТЬ
│
└── hpa/
    ├── coordination-center-hpa.yaml ❌ СОЗДАТЬ
    ├── bia-service-hpa.yaml ❌ СОЗДАТЬ
    ├── risk-service-hpa.yaml ❌ СОЗДАТЬ
    └── compliance-service-hpa.yaml ❌ СОЗДАТЬ
```

### Средний приоритет (Week 4):

```
infrastructure/scalability/load-balancer/
├── traefik.yaml ⚠️ ДОРАБОТАТЬ
└── nginx.conf ⚠️ СОЗДАТЬ
```

---

## ✅ Checklist Ready-to-Use

### Сейчас можно использовать:

- [x] API Gateway (main.py) - нужен только Docker image
- [x] Vault Manager (vault_manager.py) - нужен только Vault instance
- [x] WebSocket Service (main.py) - нужен только Docker image
- [x] Circuit Breaker (circuit_breaker.py)
- [x] Retry Patterns (retry_decorator.py)
- [x] Health Checks (health_endpoint.py)
- [x] Connection Pooling (pooled_client.py)
- [x] Load Testing (locustfile.py, k6-script.js)

### Нужно создать:

- [ ] Cache Manager (cache_manager.py) - 2 дня
- [ ] Kubernetes Manifests (18 deployments + services + ingress) - 7 дней
- [ ] Load Balancer config (traefik/nginx) - 3 дня

---

## 🎉 Итого

**Готово к использованию:** 45% инфраструктуры
**Требует создания:** 55% (в основном K8s manifests и caching)

**Минимально необходимое для production:** 70%
**ETA до production-ready:** 3-4 недели

---

**Следующий шаг:** Применить схему Supabase и начать Week 1 (API Gateway + Vault)
