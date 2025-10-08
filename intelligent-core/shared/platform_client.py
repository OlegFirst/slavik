"""
Platform Client - автоматическое подключение к ключевым сервисам платформы

Использование в любом сервисе:
    from shared.platform_client import get_platform_client

    platform = get_platform_client()

    # Автоматически доступны:
    result = await platform.ai.ask("вопрос")
    expert = await platform.experts.query("bia_specialist", "задача")
    case = await platform.workflows.add_case(data)

Обеспечивает автоматическую интеграцию с 3 "мозгами" платформы:
1. AI Foundation (RAG, LLM, Embeddings)
2. Expertise Center (12 экспертов + 10 анализаторов)
3. Workflow Intelligence (Case Library + ML анализ)
"""

import httpx
import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PlatformConfig:
    """
    Конфигурация платформы - автоопределение из env или defaults

    Можно переопределить через env variables:
        export AI_FOUNDATION_URL=http://custom:8040
        export EXPERTISE_CENTER_URL=http://custom:8035
        export WORKFLOW_INTELLIGENCE_URL=http://custom:8037
    """

    # AI Foundation
    ai_foundation_url: str = os.getenv("AI_FOUNDATION_URL", "http://localhost:8040")

    # Expertise Center
    expertise_center_url: str = os.getenv("EXPERTISE_CENTER_URL", "http://localhost:8035")

    # Workflow Intelligence
    workflow_intelligence_url: str = os.getenv("WORKFLOW_INTELLIGENCE_URL", "http://localhost:8037")

    # Event Intelligence
    event_intelligence_url: str = os.getenv("EVENT_INTELLIGENCE_URL", "http://localhost:8039")

    # EventBus
    eventbus_url: str = os.getenv("EVENTBUS_URL", "http://localhost:8001")

    # Database
    database_url: str = os.getenv("DATABASE_URL", "")

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Timeouts
    default_timeout: float = 30.0
    ai_timeout: float = 60.0


class AIFoundationClient:
    """
    Клиент для AI Foundation (порт 8040)

    Предоставляет:
    - LLM Router (AI обработка)
    - RAG Pipeline (поиск знаний)
    - Embeddings (векторизация)
    - Context Builder (контекст)
    """

    def __init__(self, base_url: str, timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def ask(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Спросить AI через LLM Router

        Args:
            query: Вопрос
            context: Дополнительный контекст

        Returns:
            Ответ от AI
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/llm/query",
                    json={"query": query, "context": context or {}}
                )
                response.raise_for_status()
                return response.json().get("response", "")
        except Exception as e:
            logger.error(f"AI Foundation ask failed: {e}")
            return f"Error: {str(e)}"

    async def search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Поиск через RAG Pipeline

        Args:
            query: Поисковый запрос
            limit: Максимум результатов

        Returns:
            Список найденных документов
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/rag/search",
                    json={"query": query, "limit": limit}
                )
                response.raise_for_status()
                return response.json().get("results", [])
        except Exception as e:
            logger.error(f"Knowledge search failed: {e}")
            return []

    async def get_embeddings(self, text: str) -> List[float]:
        """
        Получить embeddings для текста

        Args:
            text: Текст для векторизации

        Returns:
            Вектор embeddings
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/embeddings/generate",
                    json={"text": text}
                )
                response.raise_for_status()
                return response.json().get("embeddings", [])
        except Exception as e:
            logger.error(f"Embeddings generation failed: {e}")
            return []

    async def health(self) -> bool:
        """Проверка доступности"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except:
            return False


class ExpertiseCenterClient:
    """
    Клиент для Expertise Center (порт 8035)

    Предоставляет:
    - 12 Tactical Assistants (BCM эксперты)
    - 10 Analyzers (анализаторы)
    - Domain Knowledge
    """

    def __init__(self, base_url: str, timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def query_expert(
        self,
        expert_type: str,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Запросить любого эксперта

        Args:
            expert_type: Тип эксперта (bia_specialist, risk_analyst, etc.)
            query: Запрос
            context: Контекст
            organization_id: ID организации

        Returns:
            Ответ эксперта
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/expertise/query",
                    json={
                        "expert_type": expert_type,
                        "query": query,
                        "context": context or {},
                        "organization_id": organization_id
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Expert query failed: {e}")
            return {"error": str(e)}

    async def bia_analysis(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """BIA анализ через BIA Specialist"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/expertise/tactical/bia/analyze",
                    json=request
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"BIA analysis failed: {e}")
            return {"error": str(e)}

    async def risk_assessment(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Risk анализ через Risk Analyst"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/expertise/tactical/risk/assess",
                    json=request
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return {"error": str(e)}

    async def compliance_check(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Compliance проверка через Compliance Copilot"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/expertise/tactical/compliance/check",
                    json=request
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return {"error": str(e)}

    async def get_info(self) -> Dict[str, Any]:
        """Получить список всех экспертов"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/expertise/info")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Get info failed: {e}")
            return {}

    async def health(self) -> bool:
        """Проверка доступности"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except:
            return False


class WorkflowIntelligenceClient:
    """
    Клиент для Workflow Intelligence (порт 8037)

    Предоставляет:
    - Case Library API
    - Workflow Analysis
    - ML Recommendations
    """

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def add_case(
        self,
        case_data: Dict[str, Any],
        module: str,
        source: str = "platform",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Добавить кейс в библиотеку

        Args:
            case_data: Данные кейса
            module: Модуль (bia, risk, etc.)
            source: Источник (platform, community, etc.)
            metadata: Дополнительные метаданные

        Returns:
            ID созданного кейса или None при ошибке
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cases/add",
                    json={
                        "case_data": case_data,
                        "module": module,
                        "source": source,
                        "metadata": metadata or {}
                    }
                )
                response.raise_for_status()
                return response.json().get("case_id")
        except Exception as e:
            logger.error(f"Add case failed: {e}")
            return None

    async def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Получить кейс по ID"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/cases/{case_id}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Get case failed: {e}")
            return None

    async def search_cases(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Поиск кейсов"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cases/search",
                    json=query
                )
                response.raise_for_status()
                return response.json().get("results", [])
        except Exception as e:
            logger.error(f"Search cases failed: {e}")
            return []

    async def analyze_workflow(
        self,
        workflow_id: str,
        workflow_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Анализ workflow с ML

        Args:
            workflow_id: ID workflow
            workflow_data: Данные workflow
            context: Контекст

        Returns:
            Результат анализа
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/analyze",
                    json={
                        "workflow_id": workflow_id,
                        "workflow_data": workflow_data,
                        "context": context or {}
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Workflow analysis failed: {e}")
            return None

    async def get_recommendations(self, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить ML рекомендации"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/recommend",
                    json=workflow_data
                )
                response.raise_for_status()
                return response.json().get("recommendations", [])
        except Exception as e:
            logger.error(f"Get recommendations failed: {e}")
            return []

    async def health(self) -> bool:
        """Проверка доступности"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except:
            return False


class EventIntelligenceClient:
    """
    Клиент для Event Intelligence (порт 8039)

    Предоставляет:
    - Event Analysis (анализ событий с importance scoring)
    - Pattern Detection (обнаружение паттернов)
    - Gap Prediction (предсказание пропущенных handlers)
    - ML Learning (обучение на фидбеке)
    - Knowledge Base (база знаний событий)
    """

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def analyze_event(
        self,
        event_name: str,
        publishers: List[str],
        subscribers: List[str],
        historical_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Анализ события

        Args:
            event_name: Имя события (например, 'user.registered')
            publishers: Список сервисов-издателей
            subscribers: Список сервисов-подписчиков
            historical_data: Исторические данные для ML анализа

        Returns:
            Результат анализа с importance_score, usage_pattern, recommendations
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/event-intelligence/analyze",
                    json={
                        "event_name": event_name,
                        "publishers": publishers,
                        "subscribers": subscribers,
                        "historical_data": historical_data
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Event analysis failed: {e}")
            return None

    async def analyze_domain(
        self,
        domain: str,
        events: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Анализ всех событий в домене

        Args:
            domain: Имя домена (например, 'authentication')
            events: Список событий в домене

        Returns:
            Агрегированная статистика и health метрики
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/event-intelligence/analyze/domain",
                    json={"domain": domain, "events": events}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Domain analysis failed: {e}")
            return None

    async def predict_gaps(
        self,
        current_events: Dict[str, Dict[str, List[str]]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Предсказать пропущенные event handlers

        Args:
            current_events: Текущая архитектура событий
            context: Дополнительный контекст

        Returns:
            Список предсказанных gaps с confidence scores
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/event-intelligence/predict/gaps",
                    json={
                        "current_events": current_events,
                        "context": context
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result.get("predicted_gaps", [])
        except Exception as e:
            logger.error(f"Gap prediction failed: {e}")
            return []

    async def record_suggestion(
        self,
        event_name: str,
        suggested_action: str,
        confidence: float
    ) -> Optional[str]:
        """
        Записать AI suggestion для learning

        Args:
            event_name: Имя события
            suggested_action: 'implement', 'postpone', 'reject'
            confidence: Уверенность (0-1)

        Returns:
            suggestion_id для отслеживания feedback
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/event-intelligence/learning/suggest",
                    json={
                        "event_name": event_name,
                        "suggested_action": suggested_action,
                        "confidence": confidence
                    }
                )
                response.raise_for_status()
                return response.json().get("suggestion_id")
        except Exception as e:
            logger.error(f"Record suggestion failed: {e}")
            return None

    async def record_feedback(
        self,
        suggestion_id: str,
        developer_decision: str,
        outcome: Optional[str] = None
    ) -> bool:
        """
        Записать developer feedback

        Args:
            suggestion_id: ID suggestion
            developer_decision: 'approved', 'rejected', 'postponed'
            outcome: 'success', 'failure', 'neutral'

        Returns:
            True если успешно
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/event-intelligence/learning/feedback",
                    json={
                        "suggestion_id": suggestion_id,
                        "developer_decision": developer_decision,
                        "outcome": outcome
                    }
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Record feedback failed: {e}")
            return False

    async def get_similar_events(self, event_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Найти похожие события в knowledge base"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/event-intelligence/knowledge/similar/{event_name}",
                    params={"limit": limit}
                )
                response.raise_for_status()
                return response.json().get("similar_events", [])
        except Exception as e:
            logger.error(f"Get similar events failed: {e}")
            return []

    async def get_learning_stats(self) -> Optional[Dict[str, Any]]:
        """Получить статистику обучения"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/event-intelligence/learning/stats"
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Get learning stats failed: {e}")
            return None

    async def health(self) -> bool:
        """Проверка доступности"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except:
            return False


class PlatformClient:
    """
    Unified Platform Client

    Автоматически подключается ко всем ключевым сервисам платформы.
    Использовать в любом сервисе для доступа к "мозгам" платформы.

    Usage:
        from shared.platform_client import get_platform_client

        platform = get_platform_client()

        # AI
        answer = await platform.ai.ask("Что такое BIA?")

        # Experts
        result = await platform.experts.query_expert("bia_specialist", "Анализ процесса")

        # Workflows
        case_id = await platform.workflows.add_case(data, "bia")
    """

    def __init__(self, config: Optional[PlatformConfig] = None):
        self.config = config or PlatformConfig()

        # Initialize clients
        self.ai = AIFoundationClient(
            self.config.ai_foundation_url,
            self.config.ai_timeout
        )

        self.experts = ExpertiseCenterClient(
            self.config.expertise_center_url,
            self.config.default_timeout
        )

        self.workflows = WorkflowIntelligenceClient(
            self.config.workflow_intelligence_url,
            self.config.default_timeout
        )

        self.events = EventIntelligenceClient(
            self.config.event_intelligence_url,
            self.config.default_timeout
        )

        logger.info("✅ Platform Client initialized")
        logger.info(f"  - AI Foundation: {self.config.ai_foundation_url}")
        logger.info(f"  - Expertise Center: {self.config.expertise_center_url}")
        logger.info(f"  - Workflow Intelligence: {self.config.workflow_intelligence_url}")
        logger.info(f"  - Event Intelligence: {self.config.event_intelligence_url}")

    async def health_check(self) -> Dict[str, bool]:
        """
        Проверить доступность всех ключевых сервисов

        Returns:
            Dict с результатами проверки каждого сервиса
        """
        return {
            "ai_foundation": await self.ai.health(),
            "expertise_center": await self.experts.health(),
            "workflow_intelligence": await self.workflows.health(),
            "event_intelligence": await self.events.health()
        }

    async def is_ready(self) -> bool:
        """
        Проверить готовность платформы (все сервисы доступны)

        Returns:
            True если все сервисы работают
        """
        health = await self.health_check()
        return all(health.values())


# ==================== Singleton ====================

_platform_client: Optional[PlatformClient] = None


def get_platform_client(config: Optional[PlatformConfig] = None) -> PlatformClient:
    """
    Получить или создать Platform Client (singleton)

    Args:
        config: Опциональная конфигурация (используется только при первом вызове)

    Returns:
        PlatformClient instance

    Usage:
        from shared.platform_client import get_platform_client

        platform = get_platform_client()

        # Use it
        result = await platform.ai.ask("Question")
    """
    global _platform_client

    if _platform_client is None:
        _platform_client = PlatformClient(config)

    return _platform_client


def reset_platform_client():
    """
    Сбросить singleton (полезно для тестов)
    """
    global _platform_client
    _platform_client = None
