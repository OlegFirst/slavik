#!/usr/bin/env python3
"""
BCM Platform - Централизованный API Gateway

Единая точка входа для всех API сервисов платформы:
- Odoo BCM интеграция
- Микросервисы (Compliance, BIA, Document Processor, etc.)
- Authentication & Authorization
- Request routing и load balancing
- Error handling и retry logic
- Caching и rate limiting
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from functools import wraps
import hashlib

from fastapi import FastAPI, HTTPException, Depends, Header, Request, status, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import httpx
import redis
from cachetools import TTLCache
import jwt

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===========================
# КОНФИГУРАЦИЯ
# ===========================

class ServiceConfig:
    """Конфигурация микросервисов"""

    # Odoo
    ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
    ODOO_DB = os.getenv("ODOO_DB", "bcm_platform")
    ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
    ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")

    # Микросервисы
    SERVICES = {
        "compliance_checker": {
            "url": os.getenv("COMPLIANCE_CHECKER_URL", "http://localhost:8084"),
            "timeout": 30,
            "retry": 3
        },
        "bia_engine": {
            "url": os.getenv("BIA_ENGINE_URL", "http://localhost:8082"),
            "timeout": 30,
            "retry": 3
        },
        "document_processor": {
            "url": os.getenv("DOCUMENT_PROCESSOR_URL", "http://localhost:8083"),
            "timeout": 60,
            "retry": 2
        },
        "scenario_orchestrator": {
            "url": os.getenv("SCENARIO_ORCHESTRATOR_URL", "http://localhost:8085"),
            "timeout": 30,
            "retry": 3
        },
        "ai_orchestrator": {
            "url": os.getenv("AI_ORCHESTRATOR_URL", "http://localhost:8000"),
            "timeout": 45,
            "retry": 2
        },
        "notification_service": {
            "url": os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8002"),
            "timeout": 10,
            "retry": 3
        }
    }

    # Redis для кеширования
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

    # JWT Settings
    JWT_SECRET = os.getenv("JWT_SECRET", "bcm_secret_key_change_in_production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24

config = ServiceConfig()

# ===========================
# ПРИЛОЖЕНИЕ
# ===========================

app = FastAPI(
    title="BCM Platform API Gateway",
    description="Централизованный API Gateway для всей BCM платформы",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================
# КЛИЕНТЫ И КЕШИРОВАНИЕ
# ===========================

# HTTP клиент для внешних запросов
http_client = httpx.AsyncClient(timeout=30.0)

# Redis клиент
try:
    redis_client = redis.from_url(config.REDIS_URL, decode_responses=True)
    redis_available = True
    logger.info("✅ Redis подключен")
except Exception as e:
    logger.warning(f"⚠️ Redis недоступен: {e}. Используем in-memory cache")
    redis_available = False

# In-memory cache как fallback
memory_cache = TTLCache(maxsize=1000, ttl=300)  # 5 минут TTL

# Odoo session storage
odoo_sessions = {}

# ===========================
# AUTHENTICATION
# ===========================

security = HTTPBearer()

def create_jwt_token(user_data: dict) -> str:
    """Создать JWT токен"""
    payload = {
        "user": user_data,
        "exp": datetime.utcnow() + timedelta(hours=config.JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

def verify_jwt_token(token: str) -> dict:
    """Проверить JWT токен"""
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        return payload["user"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Получить текущего пользователя из токена"""
    token = credentials.credentials
    user = verify_jwt_token(token)
    return user

# ===========================
# ODOO ИНТЕГРАЦИЯ
# ===========================

class OdooClient:
    """Клиент для работы с Odoo"""

    def __init__(self):
        self.session_id = None
        self.uid = None

    async def authenticate(self) -> bool:
        """Аутентификация в Odoo"""
        try:
            # Проверяем кешированную сессию
            cache_key = f"odoo_session_{config.ODOO_USERNAME}"

            if redis_available:
                cached_session = redis_client.get(cache_key)
                if cached_session:
                    session_data = json.loads(cached_session)
                    self.session_id = session_data["session_id"]
                    self.uid = session_data["uid"]
                    return True

            # Аутентифицируемся в Odoo
            auth_url = f"{config.ODOO_URL}/web/session/authenticate"
            auth_data = {
                "jsonrpc": "2.0",
                "params": {
                    "db": config.ODOO_DB,
                    "login": config.ODOO_USERNAME,
                    "password": config.ODOO_PASSWORD
                }
            }

            response = await http_client.post(auth_url, json=auth_data)

            if response.status_code == 200:
                result = response.json()
                if result.get("result") and result["result"].get("uid"):
                    self.uid = result["result"]["uid"]
                    self.session_id = response.cookies.get("session_id")

                    # Кешируем сессию
                    session_data = {"session_id": self.session_id, "uid": self.uid}
                    if redis_available:
                        redis_client.setex(
                            cache_key,
                            3600,  # 1 час
                            json.dumps(session_data)
                        )

                    logger.info("✅ Odoo аутентификация успешна")
                    return True

            logger.error("❌ Odoo аутентификация провалена")
            return False

        except Exception as e:
            logger.error(f"❌ Ошибка Odoo аутентификации: {e}")
            return False

    async def call_kw(self, model: str, method: str, args: list, kwargs: dict = None) -> Any:
        """Вызов метода модели Odoo"""
        if not self.session_id:
            await self.authenticate()

        url = f"{config.ODOO_URL}/web/dataset/call_kw/{model}/{method}"

        data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": model,
                "method": method,
                "args": args,
                "kwargs": kwargs or {}
            },
            "id": 1
        }

        headers = {"Cookie": f"session_id={self.session_id}"}

        response = await http_client.post(url, json=data, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"]["message"])
            return result.get("result")
        else:
            raise HTTPException(status_code=response.status_code, detail="Odoo request failed")

    async def search_read(self, model: str, domain: list = None, fields: list = None,
                         limit: int = None, offset: int = 0, order: str = None) -> list:
        """Поиск и чтение записей"""
        kwargs = {
            "domain": domain or [],
            "fields": fields or [],
            "limit": limit,
            "offset": offset,
            "order": order
        }
        # Убираем None значения
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        return await self.call_kw(model, "search_read", [], kwargs)

    async def create(self, model: str, vals: dict) -> int:
        """Создание записи"""
        return await self.call_kw(model, "create", [vals])

    async def write(self, model: str, ids: list, vals: dict) -> bool:
        """Обновление записей"""
        return await self.call_kw(model, "write", [ids, vals])

    async def unlink(self, model: str, ids: list) -> bool:
        """Удаление записей"""
        return await self.call_kw(model, "unlink", [ids])

# Глобальный Odoo клиент
odoo_client = OdooClient()

# ===========================
# CACHE HELPERS
# ===========================

def cache_key(prefix: str, params: dict) -> str:
    """Генерация ключа кеша"""
    param_str = json.dumps(params, sort_keys=True)
    hash_str = hashlib.md5(param_str.encode()).hexdigest()
    return f"{prefix}:{hash_str}"

async def get_cached(key: str) -> Optional[Any]:
    """Получить из кеша"""
    if redis_available:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    else:
        return memory_cache.get(key)
    return None

async def set_cached(key: str, data: Any, ttl: int = 300):
    """Сохранить в кеш"""
    json_data = json.dumps(data)
    if redis_available:
        redis_client.setex(key, ttl, json_data)
    else:
        memory_cache[key] = data

# ===========================
# API ENDPOINTS - AUTHENTICATION
# ===========================

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Вход в систему"""
    # В реальном приложении здесь проверка в Odoo
    # Пока simplified версия
    if request.username and request.password:
        user_data = {
            "username": request.username,
            "id": 1,
            "role": "admin"
        }
        token = create_jwt_token(user_data)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user_data
        }

    raise HTTPException(status_code=401, detail="Invalid credentials")

# ===========================
# API ENDPOINTS - ODOO BCM MODULES
# ===========================

@app.get("/api/bcm/modules")
async def get_bcm_modules(user: dict = Depends(get_current_user)):
    """Получить список BCM модулей"""
    cache_key_str = cache_key("bcm_modules", {})
    cached = await get_cached(cache_key_str)
    if cached:
        return cached

    modules = await odoo_client.search_read(
        "ir.module.module",
        domain=[["name", "like", "bcm_"]],
        fields=["name", "display_name", "state", "summary", "description"]
    )

    await set_cached(cache_key_str, modules, ttl=600)
    return modules

@app.get("/api/bcm/config")
async def get_bcm_config(user: dict = Depends(get_current_user)):
    """Получить конфигурацию BCM"""
    configs = await odoo_client.search_read(
        "bcm.config",
        domain=[["is_active", "=", True]],
        fields=["name", "value", "description", "config_type"]
    )

    # Группируем по типу
    grouped = {
        "general": [],
        "security": [],
        "integrations": [],
        "notifications": []
    }

    for config in configs:
        config_type = config.get("config_type", "general")
        if config_type in grouped:
            grouped[config_type].append(config)

    return grouped

@app.post("/api/bcm/config/{config_id}")
async def update_bcm_config(
    config_id: int,
    value: str,
    user: dict = Depends(get_current_user)
):
    """Обновить конфигурацию"""
    result = await odoo_client.write("bcm.config", [config_id], {"value": value})
    return {"success": result}

# ===========================
# API ENDPOINTS - TEMPLATES
# ===========================

@app.get("/api/bcm/templates")
async def get_templates(user: dict = Depends(get_current_user)):
    """Получить шаблоны BCM"""
    templates = await odoo_client.search_read(
        "bcm.document.template",
        fields=["name", "category", "file_type", "status", "usage_count"]
    )
    return templates

# ===========================
# API ENDPOINTS - CLIENTS
# ===========================

@app.get("/api/bcm/clients")
async def get_clients(user: dict = Depends(get_current_user)):
    """Получить BCM клиентов"""
    clients = await odoo_client.search_read(
        "res.partner",
        domain=[["is_bcm_client", "=", True]],
        fields=["name", "email", "phone", "bcm_status", "bcm_risk_profile"]
    )
    return clients

# ===========================
# API ENDPOINTS - USERS
# ===========================

@app.get("/api/bcm/users")
async def get_users(user: dict = Depends(get_current_user)):
    """Получить BCM пользователей"""
    users = await odoo_client.search_read(
        "res.users",
        domain=[["bcm_user", "=", True]],
        fields=["name", "login", "email", "bcm_role", "bcm_department"]
    )
    return users

# ===========================
# PROXY TO MICROSERVICES
# ===========================

@app.api_route("/api/services/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_service(
    service: str,
    path: str,
    request: Request,
    user: dict = Depends(get_current_user)
):
    """Проксирование запросов к микросервисам"""

    if service not in config.SERVICES:
        raise HTTPException(status_code=404, detail=f"Service {service} not found")

    service_config = config.SERVICES[service]
    url = f"{service_config['url']}/{path}"

    # Пробуем с retry logic
    for attempt in range(service_config.get("retry", 1)):
        try:
            # Копируем headers
            headers = dict(request.headers)
            headers.pop("host", None)

            # Делаем запрос
            response = await http_client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=await request.body(),
                timeout=service_config.get("timeout", 30)
            )

            return JSONResponse(
                content=response.json() if response.content else {},
                status_code=response.status_code
            )

        except httpx.TimeoutException:
            if attempt == service_config.get("retry", 1) - 1:
                raise HTTPException(status_code=504, detail=f"Service {service} timeout")
            await asyncio.sleep(1)  # Ждем перед retry
        except Exception as e:
            logger.error(f"Service {service} error: {e}")
            raise HTTPException(status_code=503, detail=f"Service {service} error")

# ===========================
# HEALTH CHECK
# ===========================

@app.get("/api/health")
async def health_check():
    """Проверка здоровья API Gateway"""
    services_status = {}

    # Проверяем доступность сервисов
    for service_name, service_config in config.SERVICES.items():
        try:
            response = await http_client.get(
                f"{service_config['url']}/health",
                timeout=5
            )
            services_status[service_name] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            services_status[service_name] = "offline"

    # Проверяем Odoo
    try:
        await odoo_client.authenticate()
        services_status["odoo"] = "healthy"
    except:
        services_status["odoo"] = "offline"

    # Проверяем Redis
    services_status["redis"] = "healthy" if redis_available else "offline"

    overall_status = "healthy" if all(
        status == "healthy" for status in services_status.values()
    ) else "degraded"

    return {
        "status": overall_status,
        "services": services_status,
        "timestamp": datetime.utcnow().isoformat()
    }

# ===========================
# WEBSOCKET SUPPORT
# ===========================

try:
    from websocket_manager import connection_manager, live_data_manager, websocket_endpoint

    @app.websocket("/ws/{client_id}")
    async def websocket_route(websocket: WebSocket, client_id: str):
        """WebSocket endpoint для real-time обновлений"""
        await websocket_endpoint(websocket, client_id, connection_manager, live_data_manager)

    logger.info("✅ WebSocket support enabled")
except ImportError:
    logger.warning("⚠️ WebSocket manager not found, real-time features disabled")

# ===========================
# STARTUP & SHUTDOWN
# ===========================

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    logger.info("🚀 BCM API Gateway starting...")

    # Проверяем Odoo подключение
    if await odoo_client.authenticate():
        logger.info("✅ Odoo connection established")
    else:
        logger.warning("⚠️ Odoo connection failed - will retry on requests")

    logger.info("✅ BCM API Gateway started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при остановке"""
    await http_client.aclose()
    if redis_available:
        redis_client.close()
    logger.info("👋 BCM API Gateway stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8090,
        log_level="info",
        reload=True
    )