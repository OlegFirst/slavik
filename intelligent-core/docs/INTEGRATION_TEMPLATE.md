# 🔧 Integration Template - Автоматизация настройки сервисов

**Проблема:** Каждый сервис должен автоматически подключаться к ключевым "мозгам" платформы.

**Решение:** Базовый клиент + автоконфигурация

---

## 🧠 3 Ключевых "Мозга" Платформы

### 1. AI Foundation (порт 8040)
**Что даёт:**
- RAG Pipeline (поиск знаний)
- LLM Router (AI обработка)
- Context Builder (контекст)
- Embeddings (векторы)

**Кто должен использовать:** ВСЕ сервисы

---

### 2. Expertise Center (порт 8035)
**Что даёт:**
- 12 Tactical Assistants (BCM эксперты)
- 10 Analyzers (анализаторы)
- Domain Knowledge (доменные знания)

**Кто должен использовать:**
- orchestration
- workflow-engine
- community_intelligence
- predictive

---

### 3. Workflow Intelligence (порт 8037)
**Что даёт:**
- Case Library (библиотека кейсов)
- Workflow Analysis (анализ процессов)
- ML Recommendations (рекомендации)

**Кто должен использовать:**
- community_intelligence
- workflow-engine
- ai_workflow_optimizer

---

## 🚀 Автоматизация: Platform Client

### Базовый клиент для ВСЕХ сервисов:

```python
# intelligent-core/shared/platform_client.py

"""
Platform Client - автоматическое подключение к ключевым сервисам

Использование в любом сервисе:
    from shared.platform_client import get_platform_client

    platform = get_platform_client()

    # Автоматически доступны:
    result = await platform.ai.ask("вопрос")
    expert = await platform.experts.query("bia_specialist", "задача")
    case = await platform.workflows.add_case(data)
"""

import httpx
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PlatformConfig:
    """Конфигурация платформы - автоопределение"""

    # AI Foundation
    ai_foundation_url: str = "http://localhost:8040"

    # Expertise Center
    expertise_center_url: str = "http://localhost:8035"

    # Workflow Intelligence
    workflow_intelligence_url: str = "http://localhost:8037"

    # EventBus
    eventbus_url: str = "http://localhost:8001"

    # Database
    database_url: str = "postgresql://..."

    # Redis
    redis_url: str = "redis://localhost:6379"


class AIFoundationClient:
    """Клиент для AI Foundation"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def ask(self, query: str, context: Dict[str, Any] = None) -> str:
        """Спросить AI через LLM Router"""
        response = await self.client.post(
            f"{self.base_url}/llm/query",
            json={"query": query, "context": context or {}}
        )
        return response.json()["response"]

    async def search_knowledge(self, query: str, limit: int = 5) -> list:
        """Поиск через RAG"""
        response = await self.client.post(
            f"{self.base_url}/rag/search",
            json={"query": query, "limit": limit}
        )
        return response.json()["results"]

    async def get_embeddings(self, text: str) -> list:
        """Получить embeddings"""
        response = await self.client.post(
            f"{self.base_url}/embeddings/generate",
            json={"text": text}
        )
        return response.json()["embeddings"]


class ExpertiseCenterClient:
    """Клиент для Expertise Center"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)

    async def query_expert(
        self,
        expert_type: str,
        query: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Запросить любого эксперта"""
        response = await self.client.post(
            f"{self.base_url}/expertise/query",
            json={
                "expert_type": expert_type,
                "query": query,
                "context": context or {}
            }
        )
        return response.json()

    async def bia_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """BIA анализ"""
        response = await self.client.post(
            f"{self.base_url}/expertise/tactical/bia/analyze",
            json=data
        )
        return response.json()

    async def risk_assessment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Risk анализ"""
        response = await self.client.post(
            f"{self.base_url}/expertise/tactical/risk/assess",
            json=data
        )
        return response.json()

    async def compliance_check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compliance проверка"""
        response = await self.client.post(
            f"{self.base_url}/expertise/tactical/compliance/check",
            json=data
        )
        return response.json()


class WorkflowIntelligenceClient:
    """Клиент для Workflow Intelligence"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def add_case(self, case_data: Dict[str, Any]) -> str:
        """Добавить кейс в библиотеку"""
        response = await self.client.post(
            f"{self.base_url}/cases/add",
            json=case_data
        )
        return response.json()["case_id"]

    async def get_case(self, case_id: str) -> Dict[str, Any]:
        """Получить кейс"""
        response = await self.client.get(
            f"{self.base_url}/cases/{case_id}"
        )
        return response.json()

    async def analyze_workflow(
        self,
        workflow_id: str,
        workflow_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Анализ workflow"""
        response = await self.client.post(
            f"{self.base_url}/analyze",
            json={
                "workflow_id": workflow_id,
                "workflow_data": workflow_data
            }
        )
        return response.json()


class PlatformClient:
    """
    Unified Platform Client

    Автоматически подключается ко всем ключевым сервисам.
    Использовать в любом сервисе для доступа к "мозгам" платформы.
    """

    def __init__(self, config: PlatformConfig = None):
        self.config = config or PlatformConfig()

        # Initialize clients
        self.ai = AIFoundationClient(self.config.ai_foundation_url)
        self.experts = ExpertiseCenterClient(self.config.expertise_center_url)
        self.workflows = WorkflowIntelligenceClient(self.config.workflow_intelligence_url)

        logger.info("✅ Platform Client initialized")
        logger.info(f"  - AI Foundation: {self.config.ai_foundation_url}")
        logger.info(f"  - Expertise Center: {self.config.expertise_center_url}")
        logger.info(f"  - Workflow Intelligence: {self.config.workflow_intelligence_url}")

    async def health_check(self) -> Dict[str, bool]:
        """Проверить доступность всех сервисов"""
        results = {}

        # Check AI Foundation
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.config.ai_foundation_url}/health", timeout=5.0)
                results["ai_foundation"] = response.status_code == 200
        except:
            results["ai_foundation"] = False

        # Check Expertise Center
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.config.expertise_center_url}/health", timeout=5.0)
                results["expertise_center"] = response.status_code == 200
        except:
            results["expertise_center"] = False

        # Check Workflow Intelligence
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.config.workflow_intelligence_url}/health", timeout=5.0)
                results["workflow_intelligence"] = response.status_code == 200
        except:
            results["workflow_intelligence"] = False

        return results


# Singleton instance
_platform_client = None

def get_platform_client(config: PlatformConfig = None) -> PlatformClient:
    """Get or create platform client singleton"""
    global _platform_client
    if _platform_client is None:
        _platform_client = PlatformClient(config)
    return _platform_client
```

---

## 📝 Использование в сервисах

### Пример 1: В любом новом сервисе

```python
# my_new_service/main.py

from shared.platform_client import get_platform_client

# Получить клиент
platform = get_platform_client()

# Использовать AI
async def process_request(user_query: str):
    # 1. Поиск знаний через RAG
    knowledge = await platform.ai.search_knowledge(user_query)

    # 2. Спросить эксперта
    expert_response = await platform.experts.query_expert(
        expert_type="bia_specialist",
        query=user_query,
        context={"knowledge": knowledge}
    )

    # 3. Добавить кейс в библиотеку
    case_id = await platform.workflows.add_case({
        "query": user_query,
        "response": expert_response,
        "module": "bia"
    })

    return expert_response
```

### Пример 2: В orchestration

```python
# orchestration/ai-orchestration/orchestrator.py

from shared.platform_client import get_platform_client

class Orchestrator:
    def __init__(self):
        self.platform = get_platform_client()

    async def delegate_task(self, task: str, context: dict):
        # Определить тип задачи через AI
        analysis = await self.platform.ai.ask(
            f"Какой эксперт нужен для: {task}?"
        )

        # Делегировать нужному эксперту
        if "bia" in analysis.lower():
            return await self.platform.experts.bia_analysis({
                "task": task,
                "context": context
            })
        elif "risk" in analysis.lower():
            return await self.platform.experts.risk_assessment({
                "task": task,
                "context": context
            })
```

---

## 🔧 Автоматизация при создании нового сервиса

### Шаблон структуры:

```
new_service/
├── __init__.py
├── main.py              # Использует get_platform_client()
├── config.py            # Наследует PlatformConfig
├── api/
│   └── routes.py        # API endpoints
├── models/
│   └── schemas.py       # Pydantic models
└── tests/
    └── test_integration.py  # Тест с platform client
```

### Шаблон main.py:

```python
from fastapi import FastAPI
from shared.platform_client import get_platform_client

app = FastAPI(title="My Service")

# Initialize platform integration
platform = get_platform_client()

@app.on_event("startup")
async def startup():
    # Проверить доступность платформы
    health = await platform.health_check()

    if not all(health.values()):
        logger.warning(f"Some platform services unavailable: {health}")
    else:
        logger.info("✅ All platform services connected!")

@app.get("/")
async def root():
    return {
        "service": "my_service",
        "platform_integration": await platform.health_check()
    }
```

---

## 🎯 Процесс разработки нового сервиса

### 1. Создать структуру:
```bash
cd intelligent-core
mkdir -p new_service/{api,models,tests}
touch new_service/{__init__.py,main.py,config.py}
```

### 2. Скопировать template:
```bash
cp INTEGRATION_TEMPLATE.md new_service/
```

### 3. Использовать platform_client:
```python
from shared.platform_client import get_platform_client
platform = get_platform_client()
```

### 4. Тестировать integration:
```python
# tests/test_integration.py
async def test_platform_integration():
    platform = get_platform_client()
    health = await platform.health_check()
    assert all(health.values()), "Platform services not available"
```

---

## ✅ Преимущества этого подхода:

1. **Автоматическая интеграция:**
   - Один импорт: `get_platform_client()`
   - Все "мозги" доступны сразу

2. **Единая точка конфигурации:**
   - `PlatformConfig` - одно место для всех URL
   - Env variables или defaults

3. **Типизация и автодополнение:**
   - `platform.ai.ask()` - IDE знает методы
   - `platform.experts.query_expert()` - подсказки

4. **Health checks встроены:**
   - `await platform.health_check()` - проверка сразу всех

5. **Graceful degradation:**
   - Если сервис недоступен - не падает, логирует warning

---

## 🚀 Следующий шаг:

**Создать `/intelligent-core/shared/platform_client.py` и использовать ВЕЗДЕ!**

Это будет базовый контракт для всех сервисов:
- "Если ты сервис в intelligent-core, ты ДОЛЖЕН использовать platform_client"
- Автоматическая интеграция с 3 мозгами
- Стандартный API для всех

---

**Создано:** 2025-10-08
**Автор:** Main Claude + MD
**Статус:** ✅ ГОТОВО к реализации
