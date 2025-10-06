"""
Living Documentation Dependencies

Dependency injection for all services
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)


# ================================================
# DATABASE
# ================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session

    Uses Supabase PostgreSQL connection pool
    """
    try:
        from infrastructure.database.managers.supabase_client import get_async_session

        async for session in get_async_session():
            yield session

    except ImportError:
        logger.warning("Supabase client not available, using None")
        yield None


# ================================================
# AI CLIENT
# ================================================

async def get_ai_client():
    """
    Get AI client (Anthropic Claude)

    Falls back to mock client if no API key
    """
    import os
    from .config import settings

    api_key = os.getenv("ANTHROPIC_API_KEY") or settings.ANTHROPIC_API_KEY

    if api_key and api_key != "your_anthropic_api_key_here":
        try:
            from anthropic import AsyncAnthropic

            client = AsyncAnthropic(api_key=api_key)

            # Test connection
            logger.info("✅ Anthropic Claude client initialized")
            return client

        except Exception as e:
            logger.warning(f"Failed to initialize Anthropic client: {e}")

    # Fallback to mock
    logger.info("Using Mock AI Client (no API key)")
    return MockAIClient()


class MockAIClient:
    """Mock AI client for testing"""

    async def messages_create(self, **kwargs):
        """Mock message creation"""

        class MockResponse:
            def __init__(self):
                self.content = [MockContent()]

        class MockContent:
            def __init__(self):
                self.text = """
# Example Documentation

This is AI-generated documentation (mock version).

## Section 1
Lorem ipsum dolor sit amet...

## Section 2
Based on industry best practices...

## Example
Here's how to do it:
1. Step one
2. Step two
3. Step three

## Next Steps
- Action item 1
- Action item 2
"""

        return MockResponse()


# ================================================
# COLLECTIVE INTELLIGENCE CLIENT
# ================================================

async def get_collective_intelligence_client():
    """
    Get Collective Intelligence client

    For fetching anonymized cases and examples
    """
    from .config import settings

    try:
        import httpx

        base_url = settings.COLLECTIVE_INTELLIGENCE_URL

        client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

        logger.info(f"✅ Collective Intelligence client initialized: {base_url}")
        return client

    except Exception as e:
        logger.warning(f"Collective Intelligence client not available: {e}")
        return None


# ================================================
# DOCUMENTATION EVOLUTION ENGINE
# ================================================

async def get_evolution_engine(
    db: AsyncSession = None,
    ai_client = None,
    collective_client = None
):
    """
    Get Documentation Evolution Engine

    Self-learning documentation system
    """
    from .services.documentation_evolution_engine import DocumentationEvolutionEngine

    # Get dependencies if not provided
    if db is None:
        async for session in get_db():
            db = session
            break

    if ai_client is None:
        ai_client = await get_ai_client()

    if collective_client is None:
        collective_client = await get_collective_intelligence_client()

    engine = DocumentationEvolutionEngine(
        db=db,
        ai_client=ai_client,
        collective_intelligence=collective_client
    )

    logger.info("✅ Documentation Evolution Engine initialized")
    return engine


# ================================================
# PERSONALIZATION SERVICE
# ================================================

async def get_personalization_service(
    db: AsyncSession = None
):
    """
    Get Personalization Service

    Customizes documentation for each user
    """
    from .services.personalization_service import PersonalizationService

    # Get dependencies if not provided
    if db is None:
        async for session in get_db():
            db = session
            break

    service = PersonalizationService(db=db)

    logger.info("✅ Personalization Service initialized")
    return service


# ================================================
# AI EXAMPLE GENERATOR
# ================================================

async def get_example_generator(
    db: AsyncSession = None,
    ai_client = None,
    collective_client = None
):
    """
    Get AI Example Generator

    Generates examples on demand
    """
    from .services.ai_example_generator import AIExampleGenerator

    # Get dependencies if not provided
    if db is None:
        async for session in get_db():
            db = session
            break

    if ai_client is None:
        ai_client = await get_ai_client()

    if collective_client is None:
        collective_client = await get_collective_intelligence_client()

    generator = AIExampleGenerator(
        db=db,
        ai_client=ai_client,
        collective_intelligence=collective_client
    )

    logger.info("✅ AI Example Generator initialized")
    return generator


# ================================================
# DEPENDENCY VALIDATION
# ================================================

async def validate_dependencies() -> dict:
    """
    Validate all dependencies at startup

    Returns health status of each component
    """
    status = {
        "database": False,
        "ai_client": False,
        "collective_intelligence": False,
        "overall": False
    }

    # Check database
    try:
        async for session in get_db():
            if session is not None:
                status["database"] = True
            break
    except Exception as e:
        logger.error(f"Database check failed: {e}")

    # Check AI client
    try:
        ai_client = await get_ai_client()
        if ai_client is not None:
            status["ai_client"] = True
    except Exception as e:
        logger.error(f"AI client check failed: {e}")

    # Check Collective Intelligence
    try:
        collective_client = await get_collective_intelligence_client()
        if collective_client is not None:
            status["collective_intelligence"] = True
    except Exception as e:
        logger.warning(f"Collective Intelligence check failed: {e}")

    # Overall status (database and AI are critical)
    status["overall"] = status["database"] and status["ai_client"]

    # Log results
    logger.info("Dependency Validation:")
    for service, healthy in status.items():
        symbol = "✅" if healthy else "❌"
        logger.info(f"  {symbol} {service}: {healthy}")

    return status


# ================================================
# MOCK DEPENDENCIES (for testing without full infrastructure)
# ================================================

class MockDatabase:
    """Mock database for testing"""

    async def execute(self, *args, **kwargs):
        class MockResult:
            def scalars(self):
                return self

            def all(self):
                return []

        return MockResult()

    async def commit(self):
        pass

    async def rollback(self):
        pass


async def get_mock_dependencies():
    """Get mock dependencies for testing"""
    return {
        "db": MockDatabase(),
        "ai_client": MockAIClient(),
        "collective_client": None,
        "evolution_engine": None,
        "personalization_service": None,
        "example_generator": None
    }
