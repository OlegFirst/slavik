# Security Infrastructure - Integration Architecture

**Дата:** 2025-10-07
**Статус:** 🔴 НЕ ИНТЕГРИРОВАНО (сервисы изолированы)

---

## 🎯 Цель интеграции

Создать **единую защищённую экосистему**, где:
- Все запросы идут **через API Gateway**
- Все сервисы используют **Auth Service для проверки JWT**
- Все секреты хранятся в **Vault**
- Все действия логируются в **Audit Log**

---

## 📊 Архитектура интеграции

```
┌──────────────────────────────────────────────────────────────┐
│                  CLIENT (Browser/Mobile/CLI)                  │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             │ 1. Request with JWT
                             ↓
┌──────────────────────────────────────────────────────────────┐
│                   API GATEWAY (port 8000)                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Middleware Stack:                                      │  │
│  │ 1. Auth Middleware → Verify JWT via Auth Service      │  │
│  │ 2. Rate Limit → Check Redis                           │  │
│  │ 3. Audit → Log to PostgreSQL                          │  │
│  │ 4. Circuit Breaker → Check service health             │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ↓                 ↓                 ↓
┌──────────────────┐  ┌─────────────┐  ┌──────────────────┐
│  Auth Service    │  │   Vault     │  │  Redis/PostgreSQL│
│  (port 8001)     │  │ (port 8200) │  │                  │
│                  │  │             │  │                  │
│  - Login/Signup  │  │ - Secrets   │  │ - Rate limiting  │
│  - JWT verify    │  │ - API Keys  │  │ - Audit logs     │
│  - User info     │  │ - DB creds  │  │ - Sessions       │
└──────────────────┘  └─────────────┘  └──────────────────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │
                             │ 2. Route to backend
                             ↓
┌──────────────────────────────────────────────────────────────┐
│              PLATFORM SERVICES (12 microservices)             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ BIA Service  │  │ Risk Service │  │ Compliance   │  ...  │
│  │ (port 8012)  │  │ (port 8013)  │  │ (port 8014)  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                               │
│  ⚠️  IMPORTANT: Services should NOT be accessible directly!  │
│      Only through API Gateway (port 8000)                    │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flow (Детально)

### Пример: User запрашивает список BIA процессов

#### **Шаг 1: Login (получить JWT)**

```bash
# Client → Auth Service
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",  # ← JWT token
  "refresh_token": "session_abc123",
  "user": {...}
}
```

#### **Шаг 2: API Request через Gateway**

```bash
# Client → API Gateway
curl http://localhost:8000/api/v1/bia/processes \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**Что происходит в Gateway:**

```python
# gateway/api-gateway/main.py

@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    # 1. AUTH MIDDLEWARE
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return JSONResponse({"error": "Missing auth"}, 401)

    # 2. VERIFY JWT via Auth Service
    async with httpx.AsyncClient() as client:
        auth_response = await client.get(
            "http://localhost:8001/auth/me",
            headers={"Authorization": auth_header}
        )

    if auth_response.status_code != 200:
        return JSONResponse({"error": "Invalid token"}, 401)

    user = auth_response.json()
    request.state.user = user  # ← Attach user to request

    # 3. RATE LIMITING (Redis)
    user_id = user['id']
    rate_limit_key = f"rate_limit:{user_id}"

    redis = await get_redis_client()
    count = await redis.incr(rate_limit_key)
    if count == 1:
        await redis.expire(rate_limit_key, 60)  # 60 seconds window

    if count > 100:  # 100 requests per minute
        return JSONResponse({"error": "Rate limit exceeded"}, 429)

    # 4. AUDIT LOG (PostgreSQL)
    await audit_logger.log({
        "user_id": user_id,
        "method": request.method,
        "path": request.url.path,
        "timestamp": datetime.now()
    })

    # 5. ROUTE TO BACKEND
    # /api/v1/bia/* → http://localhost:8012
    if request.url.path.startswith("/api/v1/bia"):
        backend_url = "http://localhost:8012" + request.url.path

        # Circuit breaker check
        if is_circuit_open("bia-service"):
            return JSONResponse({"error": "Service unavailable"}, 503)

        # Proxy request
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=backend_url,
                headers={"X-User-Id": user_id},  # ← Pass user context
                content=await request.body()
            )

        return Response(
            content=response.content,
            status_code=response.status_code
        )
```

#### **Шаг 3: Backend Service обрабатывает запрос**

```python
# platform-services/bia-service/main.py

@app.get("/api/v1/bia/processes")
async def list_bia_processes(
    request: Request,
    user_id: str = Header(None, alias="X-User-Id")  # ← From Gateway
):
    # ✅ User already authenticated by Gateway!
    # ✅ Rate limit already checked by Gateway!
    # ✅ Audit already logged by Gateway!

    # Just do business logic
    processes = await db.fetch(
        "SELECT * FROM bia_processes WHERE organization_id = %s",
        (user_id,)
    )

    return processes
```

---

## 🔧 Что нужно интегрировать

### 1. API Gateway ↔ Auth Service

**Файл:** `infrastructure/gateway/api-gateway/middleware/auth.py`

```python
# CURRENT (placeholder):
async def auth_middleware(request: Request, call_next):
    # TODO: Verify JWT
    return await call_next(request)

# NEED TO CHANGE TO:
async def auth_middleware(request: Request, call_next):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse({"error": "Missing Authorization header"}, 401)

    token = auth_header.split(" ")[1]

    # Call Auth Service to verify token
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://localhost:8001/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code != 200:
                return JSONResponse({"error": "Invalid token"}, 401)

            user = response.json()
            request.state.user = user  # Attach user to request

        except Exception as e:
            logger.error(f"Auth Service error: {e}")
            return JSONResponse({"error": "Auth service unavailable"}, 503)

    return await call_next(request)
```

**Статус:** ❌ НЕ РЕАЛИЗОВАНО

---

### 2. API Gateway ↔ Platform Services (Routing)

**Файл:** `infrastructure/gateway/api-gateway/routing/router.py`

```python
# CURRENT (empty):
class ServiceRouter:
    def __init__(self):
        self.services = {}

    async def route_request(self, request: Request):
        # TODO: Implement routing
        pass

# NEED TO CHANGE TO:
class ServiceRouter:
    def __init__(self):
        self.services = {
            "/api/v1/bia": "http://localhost:8012",
            "/api/v1/risk": "http://localhost:8013",
            "/api/v1/compliance": "http://localhost:8014",
            "/api/v1/documents": "http://localhost:8015",
            "/api/v1/response": "http://localhost:8016",
            "/api/v1/validation": "http://localhost:8017",
            "/api/v1/governance": "http://localhost:8018",
            "/api/v1/planning": "http://localhost:8019",
            "/api/v1/plans": "http://localhost:8020",
            "/api/v1/learning": "http://localhost:8021",
            "/api/v1/community": "http://localhost:8022",
        }

    async def route_request(self, request: Request) -> Response:
        # Find matching service
        for prefix, backend_url in self.services.items():
            if request.url.path.startswith(prefix):
                # Proxy to backend
                async with httpx.AsyncClient() as client:
                    response = await client.request(
                        method=request.method,
                        url=backend_url + request.url.path,
                        headers={
                            "X-User-Id": request.state.user['id'],
                            "X-User-Email": request.state.user['email'],
                            "X-Organization-Id": request.state.user.get('organization_id'),
                        },
                        content=await request.body()
                    )

                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )

        return JSONResponse({"error": "Service not found"}, 404)
```

**Статус:** ❌ НЕ РЕАЛИЗОВАНО

---

### 3. Platform Services ↔ Vault (Secrets)

**Пример для BIA Service:**

**Файл:** `platform-services/bia-service/config.py`

```python
# CURRENT:
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # ❌ Hardcoded in .env
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# NEED TO CHANGE TO:
import os
import sys
sys.path.insert(0, "/Users/MD/AI-Platform-ISO/infrastructure/security/secrets-manager")
from vault_manager import get_vault_manager

class Settings:
    def __init__(self):
        if os.getenv("VAULT_ENABLED", "false") == "true":
            # ✅ Get secrets from Vault
            vault = get_vault_manager(
                url=os.getenv("VAULT_ADDR", "http://localhost:8200"),
                token=os.getenv("VAULT_TOKEN", "bcm-root-token")
            )

            self.openai_api_key = vault.read_secret("api/openai")["key"]
            self.supabase_key = vault.read_secret("database/supabase")["service_key"]
        else:
            # Fallback to env
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

settings = Settings()
```

**Статус:** ❌ НЕ РЕАЛИЗОВАНО (во всех 12 сервисах)

---

### 4. Platform Services → Удалить прямой доступ

**ВАЖНО:** Сервисы должны быть доступны **ТОЛЬКО через Gateway**, не напрямую!

**Текущая проблема:**
```bash
# ❌ BAD - Direct access (bypasses auth, rate limit, audit)
curl http://localhost:8012/api/v1/bia/processes
# → Returns data without any security checks!

# ✅ GOOD - Through Gateway
curl http://localhost:8000/api/v1/bia/processes \
  -H "Authorization: Bearer <token>"
# → Auth checked, rate limited, audited, then routed to 8012
```

**Решение:**

1. **Bind services to localhost only** (не 0.0.0.0):
   ```python
   # platform-services/bia-service/main.py
   if __name__ == "__main__":
       uvicorn.run(
           app,
           host="127.0.0.1",  # ← Only localhost (not 0.0.0.0)
           port=8012
       )
   ```

2. **Or use firewall** to block external access to 8012-8022.

**Статус:** ❌ НЕ РЕАЛИЗОВАНО

---

## 🚀 План интеграции

### Phase 1: Gateway ↔ Auth Service (2-3 часа)

```bash
# 1. Обновить auth middleware
# File: infrastructure/gateway/api-gateway/middleware/auth.py
# Add: Real JWT verification via Auth Service

# 2. Тест
curl http://localhost:8000/api/v1/bia/processes
# Expected: 401 Unauthorized (no token)

TOKEN=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl http://localhost:8000/api/v1/bia/processes \
  -H "Authorization: Bearer $TOKEN"
# Expected: Routed to BIA service (if running)
```

### Phase 2: Gateway ↔ Platform Services (2-3 часа)

```bash
# 1. Обновить service router
# File: infrastructure/gateway/api-gateway/routing/router.py
# Add: Route /api/v1/bia → http://localhost:8012, etc.

# 2. Запустить все platform services
cd /Users/MD/AI-Platform-ISO/platform-services
./start_all_services.sh  # Need to create this script

# 3. Тест роутинга
curl http://localhost:8000/api/v1/bia/processes -H "Authorization: Bearer $TOKEN"
curl http://localhost:8000/api/v1/risk/assessments -H "Authorization: Bearer $TOKEN"
curl http://localhost:8000/api/v1/compliance/audits -H "Authorization: Bearer $TOKEN"
```

### Phase 3: Services → Vault (3-4 часа)

```bash
# 1. Сохранить секреты в Vault
vault kv put secret/api/openai key=sk-proj-xxx
vault kv put secret/database/supabase service_key=eyJ...

# 2. Обновить каждый сервис (12 сервисов)
# Add: Vault integration in config.py

# 3. Удалить .env файлы с секретами
# Keep only: VAULT_ADDR, VAULT_TOKEN
```

### Phase 4: Security Hardening (2-3 часа)

```bash
# 1. Bind services to localhost only
# 2. Add firewall rules
# 3. Enable HTTPS (production)
# 4. Add MFA (production)
# 5. Migrate to RS256 JWT (production)
```

**TOTAL TIME:** 9-13 часов

---

## ✅ Критерии успешной интеграции

1. **Auth Flow:**
   - [ ] Login через Auth Service возвращает JWT
   - [ ] Gateway проверяет JWT перед роутингом
   - [ ] Невалидный JWT → 401 Unauthorized

2. **Routing:**
   - [ ] Все запросы идут через Gateway (port 8000)
   - [ ] Gateway роутит на правильные backend services
   - [ ] Backend services НЕ доступны напрямую

3. **Rate Limiting:**
   - [ ] 100+ запросов в минуту → 429 Rate Limit Exceeded
   - [ ] Счётчик в Redis обнуляется каждую минуту

4. **Audit Logging:**
   - [ ] Все запросы логируются в PostgreSQL
   - [ ] Логи содержат: user_id, method, path, timestamp, status

5. **Secrets:**
   - [ ] Все API keys в Vault
   - [ ] Никаких секретов в .env файлах
   - [ ] Сервисы читают секреты из Vault при старте

---

## 🔧 Быстрый тест интеграции

```bash
#!/bin/bash
# test_integration.sh

# 1. Login
echo "1. Testing login..."
TOKEN=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))")

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed!"
    exit 1
fi
echo "✅ Login successful, token: ${TOKEN:0:20}..."

# 2. Test Gateway auth
echo "2. Testing Gateway without token..."
curl -s http://localhost:8000/api/v1/bia/processes | grep -q "401\|Unauthorized"
if [ $? -eq 0 ]; then
    echo "✅ Gateway blocks requests without token"
else
    echo "❌ Gateway allows unauthenticated requests!"
fi

# 3. Test Gateway with token
echo "3. Testing Gateway with valid token..."
RESPONSE=$(curl -s http://localhost:8000/api/v1/bia/processes \
  -H "Authorization: Bearer $TOKEN")

if echo "$RESPONSE" | grep -q "error"; then
    echo "❌ Gateway routing failed: $RESPONSE"
else
    echo "✅ Gateway routing works"
fi

# 4. Test direct access (should fail in production)
echo "4. Testing direct backend access..."
curl -s http://localhost:8012/api/v1/bia/processes >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "⚠️  Backend accessible directly (should fix in production)"
else
    echo "✅ Backend not accessible directly"
fi

echo "Done!"
```

---

## 📚 Документы для изучения

1. **Gateway Implementation:**
   - [api-gateway/middleware/auth.py](../gateway/api-gateway/middleware/auth.py) - Нужно дописать
   - [api-gateway/routing/router.py](../gateway/api-gateway/routing/router.py) - Нужно дописать

2. **Auth Service:**
   - [auth/auth_service.py](auth/auth_service.py) - Уже работает ✅

3. **Vault Integration:**
   - [secrets-manager/vault_manager.py](secrets-manager/vault_manager.py) - Готов к использованию ✅

---

## 🆘 Помощь

Начать интеграцию с Phase 1 (Gateway ↔ Auth)?

Я могу:
1. Дописать `middleware/auth.py` в Gateway
2. Дописать `routing/router.py` в Gateway
3. Создать `start_all_services.sh` для запуска всех platform services
4. Создать `test_integration.sh` для проверки

Делать?
