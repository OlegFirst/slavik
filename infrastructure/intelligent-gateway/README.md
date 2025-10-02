# Intelligent API Gateway

## Concept

Не просто "тупой" роутер (`if path.startswith("/api/bia") → bia_service`), а **умный шлюз** с AI-powered функциями.

## Key Features

### 1. Smart Routing
- AI предсказывает оптимальный маршрут
- Учитывает текущую нагрузку на сервисы
- Adaptive routing при сбоях

### 2. Intelligent Caching
- AI решает что кешировать и на сколько
- Smart cache invalidation
- Predictive cache warming

### 3. Adaptive Load Balancing
- Не просто round-robin
- Учитывает сложность запроса (AI estimation)
- Учитывает приоритет пользователя (VIP → выделенные инстансы)
- Учитывает текущую нагрузку каждого инстанса

### 4. Circuit Breaker
- Автоматическое отключение неработающих сервисов
- Graceful degradation
- Fallback strategies

### 5. Request Analysis
- AI анализирует каждый запрос:
  - Оценивает сложность
  - Определяет приоритет
  - Предсказывает время выполнения
  - Решает нужен ли кеш

## Architecture

```
Client Request
     ↓
┌─────────────────────────────────────────┐
│  REQUEST ANALYZER (AI)                  │
│  • Complexity estimation                │
│  • Priority detection                   │
│  • Cache check                          │
└─────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────┐
│  SMART ROUTER                           │
│  • Service discovery                    │
│  • Health check                         │
│  • Load balancing decision              │
└─────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────┐
│  CIRCUIT BREAKER                        │
│  • Check service health                 │
│  • Fallback if needed                   │
└─────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────┐
│  REQUEST EXECUTOR                       │
│  • Adaptive timeout                     │
│  • Retry with backoff                   │
│  • Response validation                  │
└─────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────┐
│  RESPONSE HANDLER                       │
│  • Cache if applicable                  │
│  • Learning from execution              │
│  • Metrics collection                   │
└─────────────────────────────────────────┘
     ↓
Client Response
```

## Example Flow

### Simple GET Request

```python
GET /api/bia/processes?org_id=123

# 1. Request Analysis (AI)
analysis = {
    "complexity": "low",        # AI: Simple SELECT query
    "priority": "normal",       # Not VIP user
    "cacheable": true,          # GET request with stable data
    "estimated_time": 0.2,      # AI prediction: 200ms
    "cache_ttl": 300            # AI: Cache for 5 minutes
}

# 2. Cache Check
cache_key = "bia:processes:org_123"
if cached := redis.get(cache_key):
    return cached  # FAST PATH: Return from cache

# 3. Service Discovery
service = registry.find("bia")
instances = service.healthy_instances  # [instance1, instance2, instance3]

# 4. Load Balancing (AI)
selected = load_balancer.select(
    instances=instances,
    complexity="low",         # Low complexity → any instance OK
    priority="normal",        # Normal priority → standard pool
    current_load=[0.3, 0.5, 0.2]  # Pick instance3 (lowest load)
)

# 5. Execute with Circuit Breaker
try:
    response = await execute(
        url=f"{selected.url}/api/bia/processes",
        params={"org_id": 123},
        timeout=analysis["estimated_time"] * 1.5,  # 300ms timeout
        retry=3
    )
except ServiceUnavailable:
    # Circuit breaker: Try another instance or degraded mode
    response = fallback_handler()

# 6. Cache Result
redis.set(cache_key, response, ttl=analysis["cache_ttl"])

# 7. Learn from Execution
learning_engine.record({
    "endpoint": "/api/bia/processes",
    "predicted_time": 0.2,
    "actual_time": 0.18,
    "cache_hit": false
})

return response
```

### Complex POST Request (High Priority)

```python
POST /api/digital-twin/simulate
{
    "disruption_type": "ransomware",
    "org_id": 456
}

# User: VIP customer
# Request: Computationally expensive

# 1. Request Analysis (AI)
analysis = {
    "complexity": "high",       # AI: Heavy simulation
    "priority": "high",         # VIP customer
    "cacheable": false,         # POST with side effects
    "estimated_time": 15.0,     # AI prediction: 15 seconds
    "requires_isolation": true  # Don't block other requests
}

# 2. No cache (not cacheable)

# 3. Service Discovery
service = registry.find("intelligent-core")
instances = service.healthy_instances

# 4. Intelligent Load Balancing
selected = load_balancer.select(
    instances=instances,
    complexity="high",          # High complexity → dedicated instance
    priority="high",            # High priority → VIP pool
    current_load=[0.8, 0.3, 0.9]  # Pick instance2
)

# 5. Execute with Extended Timeout
response = await execute(
    url=f"{selected.url}/api/digital-twin/simulate",
    body={...},
    timeout=analysis["estimated_time"] * 2,  # 30s timeout for heavy task
    retry=1  # Don't retry expensive operations
)

# 6. No caching

# 7. Learn & Update Model
learning_engine.record({
    "endpoint": "/api/digital-twin/simulate",
    "predicted_time": 15.0,
    "actual_time": 12.3,
    "instance_load_before": 0.3,
    "instance_load_after": 0.7
})

return response
```

## Implementation Components

### 1. Request Analyzer (`routing/analyzer.py`)
```python
class RequestAnalyzer:
    async def analyze(self, request: Request) -> Analysis:
        """AI-powered request analysis"""

        # Extract features
        features = self.extract_features(request)

        # ML model predicts complexity
        complexity = await self.ml_model.predict_complexity(features)

        # Determine priority
        priority = self.determine_priority(request.user, request.path)

        # Check cacheability
        cacheable = self.is_cacheable(request.method, request.path)

        # Predict execution time
        estimated_time = await self.predict_execution_time(
            endpoint=request.path,
            complexity=complexity,
            historical_data=self.metrics.get_history(request.path)
        )

        return Analysis(
            complexity=complexity,
            priority=priority,
            cacheable=cacheable,
            estimated_time=estimated_time
        )
```

### 2. Smart Router (`routing/router.py`)
```python
class SmartRouter:
    async def route(self, request: Request, analysis: Analysis):
        """Find best service instance"""

        # Service discovery
        service = self.registry.find_service(request.path)

        if not service:
            raise ServiceNotFound(request.path)

        # Get healthy instances
        instances = await service.get_healthy_instances()

        if not instances:
            raise NoHealthyInstances(service.name)

        # Intelligent load balancing
        selected = await self.load_balancer.select_best_instance(
            instances=instances,
            analysis=analysis
        )

        return selected
```

### 3. Load Balancer (`load_balancing/balancer.py`)
```python
class IntelligentLoadBalancer:
    async def select_best_instance(
        self,
        instances: List[Instance],
        analysis: Analysis
    ) -> Instance:
        """AI-powered instance selection"""

        # Collect real-time metrics for each instance
        instance_metrics = []
        for instance in instances:
            metrics = await self.metrics.get_current(instance.id)
            instance_metrics.append((instance, metrics))

        # Score each instance
        scores = []
        for instance, metrics in instance_metrics:
            score = self.calculate_score(
                cpu=metrics.cpu_usage,
                memory=metrics.memory_usage,
                active_requests=metrics.active_requests,
                avg_latency=metrics.avg_latency,
                complexity=analysis.complexity,
                priority=analysis.priority
            )
            scores.append((instance, score))

        # Select instance with best score
        best = max(scores, key=lambda x: x[1])

        return best[0]

    def calculate_score(
        self,
        cpu: float,
        memory: float,
        active_requests: int,
        avg_latency: float,
        complexity: str,
        priority: str
    ) -> float:
        """Score instance for this specific request"""

        # Base score (lower load = higher score)
        base_score = (1 - cpu) * 0.4 + (1 - memory) * 0.3

        # Penalize for active requests
        request_penalty = active_requests * 0.05

        # Penalize for high latency
        latency_penalty = (avg_latency / 1000) * 0.2

        # Adjust for complexity
        if complexity == "high" and cpu > 0.7:
            base_score *= 0.5  # Don't send heavy tasks to busy instances

        # Adjust for priority
        if priority == "high":
            # VIP requests prefer less loaded instances
            base_score *= (1 - cpu)

        final_score = base_score - request_penalty - latency_penalty

        return max(0, final_score)
```

### 4. Circuit Breaker (`circuit_breaker/breaker.py`)
```python
class CircuitBreaker:
    """Prevent cascading failures"""

    states = {
        "closed": "Normal operation",
        "open": "Service failing, rejecting requests",
        "half_open": "Testing if service recovered"
    }

    async def execute(
        self,
        func: Callable,
        fallback: Optional[Callable] = None
    ):
        """Execute with circuit breaker protection"""

        if self.state == "open":
            # Circuit is open, don't try
            if fallback:
                return await fallback()
            raise CircuitBreakerOpen()

        try:
            result = await func()

            # Success: Reset failure count
            self.failure_count = 0
            if self.state == "half_open":
                self.state = "closed"

            return result

        except Exception as e:
            self.failure_count += 1

            # Too many failures: Open circuit
            if self.failure_count >= self.threshold:
                self.state = "open"
                self.opened_at = time.time()

            # Try fallback
            if fallback:
                return await fallback()

            raise
```

### 5. Intelligent Cache (`caching/smart_cache.py`)
```python
class SmartCache:
    """AI-powered caching with smart TTL and invalidation"""

    async def get_or_set(
        self,
        key: str,
        fetch_func: Callable,
        analysis: Analysis
    ):
        """Get from cache or fetch and cache"""

        # Check cache
        cached = await self.redis.get(key)
        if cached:
            return cached

        # Cache miss: Fetch
        value = await fetch_func()

        # AI decides TTL
        ttl = self.predict_ttl(
            endpoint=analysis.endpoint,
            data_volatility=self.estimate_volatility(value),
            access_pattern=self.metrics.get_access_pattern(key)
        )

        # Cache with predicted TTL
        await self.redis.set(key, value, ttl=ttl)

        return value

    def predict_ttl(
        self,
        endpoint: str,
        data_volatility: float,
        access_pattern: dict
    ) -> int:
        """AI predicts optimal cache TTL"""

        # High volatility = short TTL
        base_ttl = 300  # 5 minutes

        if data_volatility > 0.8:
            ttl = 60  # 1 minute for frequently changing data
        elif data_volatility > 0.5:
            ttl = 180  # 3 minutes
        else:
            ttl = 600  # 10 minutes for stable data

        # Adjust for access pattern
        if access_pattern["frequency"] == "high":
            ttl *= 1.5  # Cache longer if accessed frequently

        return int(ttl)
```

## Configuration

```python
# intelligent-gateway/config.py

class GatewayConfig:
    # Load Balancing
    LOAD_BALANCE_ALGORITHM = "intelligent"  # or "round_robin", "least_conn"
    INSTANCE_HEALTH_CHECK_INTERVAL = 10  # seconds

    # Circuit Breaker
    CIRCUIT_BREAKER_THRESHOLD = 5  # failures before opening
    CIRCUIT_BREAKER_TIMEOUT = 30  # seconds to wait before half-open

    # Caching
    CACHE_ENABLED = True
    CACHE_DEFAULT_TTL = 300  # seconds
    CACHE_MAX_SIZE = "1GB"

    # Request Analysis
    COMPLEXITY_MODEL_PATH = "models/complexity_predictor.pkl"
    ENABLE_AI_PREDICTIONS = True

    # Timeouts
    DEFAULT_TIMEOUT = 30  # seconds
    MAX_TIMEOUT = 300  # seconds

    # Retry
    MAX_RETRIES = 3
    RETRY_BACKOFF = [1, 2, 4]  # seconds
```

## Metrics

Gateway collects metrics for learning:

```python
{
    "timestamp": "2025-10-02T12:00:00Z",
    "endpoint": "/api/bia/processes",
    "method": "GET",
    "predicted_complexity": "low",
    "predicted_time": 0.2,
    "actual_time": 0.18,
    "cache_hit": false,
    "instance_selected": "instance-2",
    "instance_load_before": 0.3,
    "status_code": 200,
    "user_priority": "normal"
}
```

AI learns from these metrics to improve predictions.

## Implementation Plan

1. **Request Analyzer** (3-4 hours)
2. **Smart Router** (2-3 hours)
3. **Intelligent Load Balancer** (4-5 hours)
4. **Circuit Breaker** (2-3 hours)
5. **Smart Cache** (3-4 hours)

**Total:** 14-19 hours
