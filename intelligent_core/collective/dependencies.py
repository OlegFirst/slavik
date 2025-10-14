"""
FastAPI Dependencies for Collective Agent Networks

Dependency injection for services and authentication.

UPDATED: Now uses real service implementations!
- Database connection from Supabase
- Authentication (placeholder - to be connected)
- Case Library integration
- Analytics Client integration
- LLM Client integration
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import os
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

# ================================================
# DATABASE
# ================================================

async def get_db() -> AsyncSession:
    """
    Get database session from Supabase connection pool

    Uses existing infrastructure database manager
    """
    try:
        # Import from existing infrastructure
        from infrastructure.database.managers.supabase_client import get_async_session

        async for session in get_async_session():
            yield session

    except ImportError as e:
        logger.error(f"Failed to import database manager: {e}")
        logger.warning("Falling back to placeholder database session")
        # Fallback: Will cause errors but allows service to start
        yield None

# ================================================
# AUTHENTICATION
# ================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token

    TODO: Connect to real authentication service
    Currently returns placeholder user

    Returns:
        {
            'user_id': 'uuid',
            'org_id': 'uuid',
            'email': 'user@example.com',
            'role': 'user'
        }
    """

    # TODO: Integrate with platform's JWT validation
    # try:
    #     from infrastructure.auth.jwt_validator import validate_token
    #     user = await validate_token(credentials.credentials)
    #     return user
    # except ImportError:
    #     logger.warning("Auth service not available")

    # Placeholder for development
    logger.debug("Using placeholder authentication")
    return {
        'user_id': 'user-dev-001',
        'org_id': 'org-dev-001',
        'email': 'dev@example.com',
        'role': 'user'
    }

# ================================================
# SERVICE DEPENDENCIES
# ================================================

async def get_case_library(
    db: AsyncSession = Depends(get_db)
):
    """
    Get Case Library instance

    Queries community intelligence case contributions
    """
    from .services.case_library import CaseLibrary

    if db is None:
        logger.error("Database session is None - case library will not work")
        return None

    return CaseLibrary(db=db)


async def get_analytics_client(
    db: AsyncSession = Depends(get_db)
):
    """
    Get Analytics Client instance

    Queries activity logs and workflow events
    """
    from .services.analytics_client import AnalyticsClient

    if db is None:
        logger.error("Database session is None - analytics will not work")
        return None

    return AnalyticsClient(db=db)


async def get_llm_client():
    """
    Get LLM Client instance

    Uses Anthropic Claude API
    Falls back to mock client if no API key
    """
    from .services.llm_client import CollectiveLLMClient, MockLLMClient

    api_key = os.getenv('ANTHROPIC_API_KEY')

    if api_key:
        logger.info("Using real Anthropic LLM client")
        return CollectiveLLMClient(api_key=api_key)
    else:
        logger.warning("ANTHROPIC_API_KEY not set - using mock LLM client")
        return MockLLMClient()


async def get_anonymizer():
    """
    Get Anonymizer Service instance

    No dependencies - stateless service
    """
    from .services.anonymizer_service import AnonymizerService
    return AnonymizerService()

# ================================================
# COMPOSITE SERVICES
# ================================================

async def get_collective_service(
    db: AsyncSession = Depends(get_db),
    case_library = Depends(get_case_library),
    llm_client = Depends(get_llm_client),
    anonymizer = Depends(get_anonymizer)
):
    """
    Get Collective Agent Service instance

    Fully initialized with all dependencies
    """
    from .services.collective_agent_service import CollectiveAgentService

    if db is None:
        logger.error("Cannot create collective service: database session is None")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )

    service = CollectiveAgentService(
        db=db,
        anonymizer=anonymizer,
        case_library=case_library,
        llm_client=llm_client
    )

    logger.debug("Created CollectiveAgentService instance")

    return service


async def get_stuck_detector(
    db: AsyncSession = Depends(get_db),
    analytics_client = Depends(get_analytics_client),
    collective_service = Depends(get_collective_service)
):
    """
    Get Stuck Detector Service instance

    Fully initialized with all dependencies
    """
    from .services.stuck_detector_service import StuckDetectorService

    if db is None:
        logger.error("Cannot create stuck detector: database session is None")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )

    service = StuckDetectorService(
        db=db,
        analytics_client=analytics_client,
        collective_agent_service=collective_service
    )

    logger.debug("Created StuckDetectorService instance")

    return service

# ================================================
# OPTIONAL: MCP + PARTISIA INTEGRATION
# ================================================

async def get_mcp_partisia_service():
    """
    Get MCP + Partisia integration service

    Optional advanced feature - uses simulated responses for now
    """
    from .services.mcp_partisia_integration import MCPPartisiaService

    # Always use simulated for MVP
    # Real blockchain integration is Phase 2
    return MCPPartisiaService(use_real_blockchain=False)

# ================================================
# DEPENDENCY VALIDATION
# ================================================

async def validate_dependencies():
    """
    Validate all dependencies are working

    Call this at startup to check configuration

    Returns:
        Dict with status of each dependency
    """
    status_dict = {
        'database': False,
        'case_library': False,
        'analytics': False,
        'llm': False,
        'overall': False
    }

    try:
        # Check database
        async for db in get_db():
            if db is not None:
                status_dict['database'] = True
            break

        # Check case library
        case_lib = await get_case_library(db)
        if case_lib is not None:
            status_dict['case_library'] = True

        # Check analytics
        analytics = await get_analytics_client(db)
        if analytics is not None:
            status_dict['analytics'] = True

        # Check LLM
        llm = await get_llm_client()
        if llm is not None:
            # Test connection
            connection_ok = await llm.test_connection()
            status_dict['llm'] = connection_ok

        # Overall status
        status_dict['overall'] = all([
            status_dict['database'],
            status_dict['case_library'],
            status_dict['analytics'],
            status_dict['llm']
        ])

        logger.info(f"Dependency validation: {status_dict}")

    except Exception as e:
        logger.error(f"Dependency validation failed: {e}", exc_info=True)

    return status_dict
