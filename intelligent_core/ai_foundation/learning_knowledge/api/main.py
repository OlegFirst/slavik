"""
 Unified Learning & Knowledge API

FastAPI application providing access to:
-  Knowledge Management (ISO/BCI/WHO standards, workflow cases, vector search)
-  Learning Engine (pattern detection, ML predictions, self-learning)
-  Training Programs (exercises, competency tracking, gamification)
- ️  Cross-Learning (pattern→article, case→lesson, virtuous cycle)

Architecture:
- Multi-tenant support via X-Tenant-ID header
- Integration with Redis cache
- Prometheus metrics
- EventBus for async operations
- Unified search across all knowledge sources

Version: 2.0 - Fully Unified System
"""

from fastapi import FastAPI, HTTPException, Header, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import logging
import os

from pydantic import BaseModel, Field
from prometheus_client import make_asgi_app
from shared.eventbus import init_eventbus, get_eventbus

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import shared database utilities
try:
    import sys
    from pathlib import Path
    shared_path = Path(__file__).parent.parent / "shared"
    if str(shared_path) not in sys.path:
        sys.path.insert(0, str(shared_path))

    from database import get_db_session, get_database_manager, get_qdrant_client
    DATABASE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Database utilities not available: {e}")
    DATABASE_AVAILABLE = False

# Import learning routers
try:
    from .learning.ml_router import router as ml_router
    from .learning.recommendation_router import router as recommendation_router
    from .learning.platform_integration_router import router as platform_integration_router
    from .learning.learning_router import router as learning_router
    from .learning.gamification_router import router as gamification_router
    from .learning.process_gap_router import router as process_gap_router
    from .learning.self_learning_router import router as self_learning_router
    from .learning.analytics_router import router as analytics_router
    from .learning.competency_router import router as competency_router
    from .learning.pattern_router import router as pattern_router
    from .learning.knowledge_router import router as knowledge_router
    LEARNING_ROUTERS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Learning routers not available: {e}")
    LEARNING_ROUTERS_AVAILABLE = False

# Create FastAPI app
app = FastAPI(
    title="Unified Learning & Knowledge API",
    description="""
    Complete Learning & Knowledge Management System

    **Features:**
    -  Knowledge Management (ISO standards, workflow cases, vector search)
    -  Learning Engine (pattern detection, ML predictions, self-learning)
    -  Training Programs (exercises, competency tracking, gamification)
    - ️  Cross-Learning (pattern→article, case→lesson, virtuous cycle)

    **Virtuous Learning Cycle:**
    1. User completes workflow → Case saved
    2. Pattern detected → Article created
    3. Users learn from article → Performance improves
    4. AI learns from outcomes → Predictions improve
    5. → Cycle repeats ️
    """,
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure based on environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class StandardMetadata(BaseModel):
    """Standard metadata response"""
    standard: str
    title: str
    version: str
    amendment: Optional[str] = None
    clauses_count: int
    guides_count: int
    last_updated: str


class CaseMetadata(BaseModel):
    """Case metadata response"""
    case_id: str
    module: str
    outcome: str
    organization_context: Dict[str, Any]
    metrics: Dict[str, Any]
    collected_at: str


class CaseSearchRequest(BaseModel):
    """Case search request"""
    module: str = Field(..., description="Module to search (bia, risk, etc)")
    industry: Optional[str] = Field(None, description="Filter by industry")
    org_size: Optional[str] = Field(None, description="Filter by organization size")
    maturity_level: Optional[str] = Field(None, description="Filter by BCM maturity")
    query_text: Optional[str] = Field(None, description="Semantic search query")
    limit: int = Field(5, ge=1, le=20, description="Number of results")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    components: Dict[str, str]


# ============================================================================
# DEPENDENCIES
# ============================================================================

async def get_tenant_id(
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID")
) -> str:
    """Extract tenant ID from header"""
    if not x_tenant_id:
        return "default"  # Default tenant for development
    return x_tenant_id


def get_standards_loader():
    """Get StandardsLoader instance"""
    import sys
    from pathlib import Path

    # Add knowledge-system to path
    ks_path = Path(__file__).parents[1]
    if str(ks_path) not in sys.path:
        sys.path.insert(0, str(ks_path))

    from loader.standards_loader import StandardsLoader
    return StandardsLoader()


def get_case_collector():
    """Get CaseCollector instance"""
    import sys
    from pathlib import Path

    ks_path = Path(__file__).parents[1]
    if str(ks_path) not in sys.path:
        sys.path.insert(0, str(ks_path))

    from loader.case_loader import CaseCollector
    return CaseCollector()


# ============================================================================
# HEALTH & STATUS
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""

    # Check components
    components = {
        "api": "healthy",
        "standards_loader": "healthy",
        "case_collector": "healthy",
    }

    # Check database connection
    if DATABASE_AVAILABLE:
        try:
            db = get_database_manager()
            # Try a simple query
            async with db.get_session() as session:
                await session.execute("SELECT 1")
            components["database"] = "healthy"
        except Exception as e:
            components["database"] = f"error: {str(e)[:50]}"
    else:
        components["database"] = "unavailable"

    # Check Qdrant vector DB
    if DATABASE_AVAILABLE:
        try:
            qdrant = get_qdrant_client()
            # Check if client is initialized
            if qdrant:
                components["vector_db"] = "healthy"
            else:
                components["vector_db"] = "unavailable"
        except Exception as e:
            components["vector_db"] = f"error: {str(e)[:50]}"
    else:
        components["vector_db"] = "unavailable"

    # Try to check data directory
    try:
        data_path = Path(__file__).parents[3] / "data"
        if data_path.exists():
            components["data_storage"] = "healthy"
        else:
            components["data_storage"] = "unavailable"
    except Exception as e:
        components["data_storage"] = f"error: {e}"

    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        components=components
    )


@app.get("/")
async def root():
    """API root - System status"""
    return {
        "service": "Unified Learning & Knowledge System",
        "version": "2.0.0",
        "status": "operational",
        "components": {
            "knowledge_management": " operational",
            "learning_engine": " operational" if LEARNING_ROUTERS_AVAILABLE else "️  limited",
            "training_programs": " operational" if LEARNING_ROUTERS_AVAILABLE else "️  limited",
            "cross_learning": " operational"
        },
        "endpoints": {
            "health": "/health",
            "documentation": "/api/docs",
            "knowledge": {
                "standards": "/standards",
                "cases": "/cases",
                "search": "/cases/search"
            },
            "learning": {
                "ml_predictions": "/api/ml",
                "patterns": "/api/patterns",
                "recommendations": "/api/recommendations",
                "self_learning": "/api/self-learning"
            },
            "training": {
                "learning_paths": "/api/learning",
                "competency": "/api/competency",
                "gamification": "/api/gamification"
            },
            "analytics": {
                "dashboards": "/api/analytics",
                "process_gaps": "/api/process-gaps"
            },
            "cross_learning": {
                "virtuous_cycle": "/api/cross-learning/virtuous-cycle"
            }
        }
    }


# ============================================================================
# STANDARDS ENDPOINTS
# ============================================================================

@app.get("/standards", response_model=List[str])
async def list_standards(
    domain: Optional[str] = Query(None, description="Filter by domain (iso, bci, who, nist)"),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    List available standards

    Returns list of standard IDs
    """
    try:
        loader = get_standards_loader()

        # Get available standards from data/knowledge/standards/
        standards_path = loader.standards_path

        standards = []

        # Scan domains
        domains_to_scan = [domain] if domain else ["iso", "bci", "who", "nist"]

        for dom in domains_to_scan:
            domain_path = standards_path / dom
            if domain_path.exists():
                for std_dir in domain_path.iterdir():
                    if std_dir.is_dir():
                        standards.append(f"{dom}/{std_dir.name}")

        return standards

    except Exception as e:
        logger.error(f"Failed to list standards: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/standards/{standard_id:path}", response_model=Dict[str, Any])
async def get_standard(
    standard_id: str,
    include_clauses: bool = Query(True, description="Include clauses"),
    include_guides: bool = Query(False, description="Include guides"),
    include_mappings: bool = Query(False, description="Include mappings"),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get standard details

    Examples:
    - /standards/iso/iso-22301
    - /standards/bci/gpg-2018
    """
    try:
        loader = get_standards_loader()

        # Parse standard_id (format: domain/standard-name)
        parts = standard_id.split("/")
        if len(parts) < 2:
            raise HTTPException(
                status_code=400,
                detail="Invalid standard_id format. Expected: domain/standard-name"
            )

        domain = parts[0]
        standard_name = "/".join(parts[1:])

        # Load standard based on domain
        if domain == "iso":
            data = await loader.load_iso_standard(standard_name)
        elif domain == "bci":
            data = await loader.load_bci_gpg(standard_name)
        elif domain == "who":
            data = await loader.load_who_framework(standard_name)
        elif domain == "nist":
            data = await loader.load_nist_framework(standard_name)
        else:
            raise HTTPException(status_code=404, detail=f"Unknown domain: {domain}")

        # Filter response based on query params
        response = {
            "standard": data["standard"],
            "version": data["version"],
            "metadata": data["metadata"]
        }

        if include_clauses:
            response["clauses"] = data.get("clauses", [])

        if include_guides:
            response["guides"] = data.get("guides", [])

        if include_mappings:
            response["mappings"] = data.get("mappings", {})

        response["loaded_at"] = data.get("loaded_at")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load standard {standard_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/standards/{standard_id:path}/metadata", response_model=StandardMetadata)
async def get_standard_metadata(
    standard_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """Get standard metadata only (fast)"""
    try:
        loader = get_standards_loader()

        parts = standard_id.split("/")
        if len(parts) < 2:
            raise HTTPException(status_code=400, detail="Invalid standard_id format")

        domain = parts[0]
        standard_name = "/".join(parts[1:])

        # Load metadata from metadata.json file
        standard_path = loader.standards_path / domain / standard_name
        metadata_file = standard_path / "metadata.json"

        if not metadata_file.exists():
            raise HTTPException(status_code=404, detail="Metadata not found")

        import json
        metadata = json.loads(metadata_file.read_text())

        # Count clauses and guides
        clauses_count = 0
        guides_count = 0

        if (standard_path / "clauses_breakdown.md").exists():
            clauses_count = len([
                line for line in (standard_path / "clauses_breakdown.md").read_text().split("\n")
                if line.strip().startswith("#")
            ])

        if "sources" in metadata and "guides" in metadata["sources"]:
            guides_count = len(metadata["sources"]["guides"])

        return StandardMetadata(
            standard=metadata["standard"],
            title=metadata["title"],
            version=metadata["version"],
            amendment=metadata.get("amendment"),
            clauses_count=clauses_count,
            guides_count=guides_count,
            last_updated=metadata.get("migrated_at", "unknown")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load metadata for {standard_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CASES ENDPOINTS
# ============================================================================

@app.get("/cases", response_model=List[CaseMetadata])
async def list_cases(
    module: Optional[str] = Query(None, description="Filter by module"),
    limit: int = Query(10, ge=1, le=100),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    List available cases

    Returns case metadata (not full case content)
    """
    try:
        collector = get_case_collector()

        # Get cases path
        cases_path = collector.workflow_cases_path

        cases = []

        # Scan modules
        if module:
            module_path = cases_path / module
            if module_path.exists():
                cases.extend(_scan_cases_in_directory(module_path, module))
        else:
            # Scan all modules
            for module_dir in cases_path.iterdir():
                if module_dir.is_dir():
                    cases.extend(_scan_cases_in_directory(module_dir, module_dir.name))

        # Sort by collected_at (newest first)
        cases.sort(key=lambda c: c.collected_at, reverse=True)

        return cases[:limit]

    except Exception as e:
        logger.error(f"Failed to list cases: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cases/{case_id}", response_model=Dict[str, Any])
async def get_case(
    case_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """Get full case details"""
    try:
        collector = get_case_collector()

        # Find case file (search all modules)
        cases_path = collector.workflow_cases_path

        case_file = None
        for module_dir in cases_path.iterdir():
            if module_dir.is_dir():
                potential_file = module_dir / f"{case_id}.json"
                if potential_file.exists():
                    case_file = potential_file
                    break

        if not case_file:
            raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")

        import json
        case_data = json.loads(case_file.read_text())

        return case_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load case {case_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cases/search", response_model=List[Dict[str, Any]])
async def search_cases(
    request: CaseSearchRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Search for similar cases

    Supports:
    - Filtering by module, industry, org size, maturity level
    - Semantic search (TODO: requires vector DB)
    """
    try:
        collector = get_case_collector()

        # For now: simple file-based filtering
        # TODO: Implement vector search with Qdrant

        cases_path = collector.workflow_cases_path / request.module

        if not cases_path.exists():
            return []

        import json
        matching_cases = []

        for case_file in cases_path.glob("*.json"):
            case_data = json.loads(case_file.read_text())

            # Apply filters
            if request.industry:
                if case_data.get("organization_context", {}).get("industry") != request.industry:
                    continue

            if request.org_size:
                if case_data.get("organization_context", {}).get("size") != request.org_size:
                    continue

            if request.maturity_level:
                if case_data.get("organization_context", {}).get("maturity_level") != request.maturity_level:
                    continue

            # TODO: Semantic search with query_text

            matching_cases.append(case_data)

            if len(matching_cases) >= request.limit:
                break

        return matching_cases

    except Exception as e:
        logger.error(f"Failed to search cases: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _scan_cases_in_directory(directory: Path, module: str) -> List[CaseMetadata]:
    """Scan cases in a directory and return metadata"""
    import json

    cases = []

    for case_file in directory.glob("*.json"):
        try:
            case_data = json.loads(case_file.read_text())

            cases.append(CaseMetadata(
                case_id=case_data["case_id"],
                module=case_data["module"],
                outcome=case_data["outcome"],
                organization_context=case_data.get("organization_context", {}),
                metrics=case_data.get("metrics", {}),
                collected_at=case_data.get("collected_at", "unknown")
            ))
        except Exception as e:
            logger.warning(f"Failed to parse case file {case_file}: {e}")
            continue

    return cases


# ============================================================================
# STARTUP / SHUTDOWN
# ============================================================================

# ============================================================================
# MOUNT LEARNING ROUTERS
# ============================================================================

if LEARNING_ROUTERS_AVAILABLE:
    logger.info(" Mounting learning routers...")

    # Learning Engine
    app.include_router(ml_router, prefix="/api/ml", tags=[" ML & Predictions"])
    app.include_router(pattern_router, prefix="/api/patterns", tags=[" Pattern Detection"])
    app.include_router(self_learning_router, prefix="/api/self-learning", tags=[" Self-Learning"])
    app.include_router(recommendation_router, prefix="/api/recommendations", tags=[" Recommendations"])

    # Training Programs
    app.include_router(learning_router, prefix="/api/learning", tags=[" Learning & Training"])
    app.include_router(competency_router, prefix="/api/competency", tags=[" Competency Tracking"])
    app.include_router(gamification_router, prefix="/api/gamification", tags=[" Gamification"])

    # Analytics & Integration
    app.include_router(analytics_router, prefix="/api/analytics", tags=[" Analytics & Dashboards"])
    app.include_router(platform_integration_router, prefix="/api/platform", tags=[" Platform Integration"])
    app.include_router(process_gap_router, prefix="/api/process-gaps", tags=["️  Process Gap Analysis"])
    app.include_router(knowledge_router, prefix="/api/knowledge-search", tags=[" Knowledge Search"])

    logger.info(" All learning routers mounted")


# ============================================================================
# CROSS-LEARNING ENDPOINTS
# ============================================================================

@app.post("/api/cross-learning/virtuous-cycle/workflow")
async def process_workflow_for_cycle(
    workflow_case: dict,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Process completed workflow through virtuous cycle

    Workflow:
    1. Save workflow case
    2. Create training lesson from successful case
    3. Make lesson available to all users

    Part of: User completes work → Others learn from it
    """
    try:
        import sys
        from pathlib import Path

        # Add creation path
        creation_path = Path(__file__).parents[1] / "creation"
        if str(creation_path) not in sys.path:
            sys.path.insert(0, str(creation_path))

        from synthesis.virtuous_cycle import VirtuousLearningCycle

        cycle = VirtuousLearningCycle()
        result = await cycle.process_workflow_completion(workflow_case, tenant_id)

        return result
    except Exception as e:
        logger.error(f"Virtuous cycle workflow processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cross-learning/virtuous-cycle/pattern")
async def process_pattern_for_cycle(
    pattern: dict,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Process detected pattern through virtuous cycle

    Workflow:
    1. Record pattern
    2. Create knowledge article from pattern
    3. Make article searchable

    Part of: AI detects pattern → Humans learn from it
    """
    try:
        import sys
        from pathlib import Path

        creation_path = Path(__file__).parents[1] / "creation"
        if str(creation_path) not in sys.path:
            sys.path.insert(0, str(creation_path))

        from synthesis.virtuous_cycle import VirtuousLearningCycle

        cycle = VirtuousLearningCycle()
        result = await cycle.process_pattern_detection(pattern, tenant_id)

        return result
    except Exception as e:
        logger.error(f"Virtuous cycle pattern processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cross-learning/virtuous-cycle/metrics")
async def get_virtuous_cycle_metrics(tenant_id: str = Depends(get_tenant_id)):
    """
    Get virtuous cycle effectiveness metrics

    Shows:
    - Cycles completed
    - Knowledge created (articles, lessons)
    - Conversion rates
    - Cycle health
    """
    try:
        import sys
        from pathlib import Path

        creation_path = Path(__file__).parents[1] / "creation"
        if str(creation_path) not in sys.path:
            sys.path.insert(0, str(creation_path))

        from synthesis.virtuous_cycle import VirtuousLearningCycle

        cycle = VirtuousLearningCycle()
        metrics = cycle.get_cycle_metrics()

        return {
            "tenant_id": tenant_id,
            **metrics
        }
    except Exception as e:
        logger.error(f"Virtuous cycle metrics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UNIFIED SEARCH ENDPOINT
# ============================================================================

@app.get("/api/search")
async def unified_search(
    query: str,
    search_type: Optional[str] = Query("all", description="all, knowledge, lessons, patterns"),
    limit: int = Query(20, ge=1, le=100),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Unified search across ALL knowledge and learning resources

    Searches:
    - Knowledge base (standards, articles, cases)
    - Training lessons
    - Detected patterns
    - Recommendations

    Args:
        query: Search query
        search_type: Type filter (all, knowledge, lessons, patterns)
        limit: Max results

    Returns:
        Unified search results across all sources
    """
    # TODO: Implement unified search using vector search (Qdrant)
    # This would query all knowledge sources and aggregate results

    return {
        "query": query,
        "search_type": search_type,
        "tenant_id": tenant_id,
        "results": {
            "knowledge_articles": [],
            "training_lessons": [],
            "detected_patterns": [],
            "recommendations": []
        },
        "total_results": 0,
        "note": "Unified search implementation pending - requires Qdrant integration"
    }


# ============================================================================
# REACTIVE LEARNING ENDPOINTS
# ============================================================================

@app.get("/api/reactive-learning/statistics")
async def get_reactive_learning_statistics(tenant_id: str = Depends(get_tenant_id)):
    """
    Get reactive learning statistics

    Shows:
    - Events processed by type
    - ML model training status
    - Learning effectiveness metrics
    """
    try:
        if not hasattr(app.state, 'learning_subscriber'):
            return {
                "status": "disabled",
                "message": "Reactive learning not active"
            }

        subscriber = app.state.learning_subscriber
        stats = subscriber.get_statistics()

        return {
            "status": "active",
            "tenant_id": tenant_id,
            **stats
        }

    except Exception as e:
        logger.error(f"Failed to get reactive learning stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reactive-learning/subscribers")
async def list_active_subscribers(tenant_id: str = Depends(get_tenant_id)):
    """
    List all active event subscribers

    Returns information about registered event handlers
    """
    return {
        "subscribers": [
            {
                "event_type": "case.approved",
                "handler": "handle_case_approved",
                "description": "Learn from approved workflow cases - update ML models, index to vector DB",
                "source": "community_intelligence"
            },
            {
                "event_type": "case.rejected",
                "handler": "handle_case_rejected",
                "description": "Analyze rejection patterns for quality improvement",
                "source": "community_intelligence"
            },
            {
                "event_type": "review.submitted",
                "handler": "handle_review_submitted",
                "description": "Learn from peer feedback and quality signals",
                "source": "community_intelligence"
            },
            {
                "event_type": "workflow.completed",
                "handler": "handle_workflow_completed",
                "description": "Extract success patterns and update prediction models",
                "source": "workflow_intelligence"
            },
            {
                "event_type": "workflow.failed",
                "handler": "handle_workflow_failed",
                "description": "Analyze failure patterns and update risk models",
                "source": "workflow_intelligence"
            },
            {
                "event_type": "workflow.milestone_reached",
                "handler": "handle_workflow_milestone_reached",
                "description": "Update user competency scores",
                "source": "workflow_intelligence"
            },
            {
                "event_type": "bia.completed",
                "handler": "handle_bia_completed",
                "description": "Extract BIA patterns and update knowledge graph",
                "source": "bia_engine"
            },
            {
                "event_type": "bia.validated",
                "handler": "handle_bia_validated",
                "description": "Mark validated BIAs as high-quality training examples",
                "source": "bia_engine"
            },
            {
                "event_type": "incident.resolved",
                "handler": "handle_incident_resolved",
                "description": "Learn from incident resolutions and build lessons database",
                "source": "incident_management"
            },
            {
                "event_type": "incident.pattern_detected",
                "handler": "handle_incident_pattern_detected",
                "description": "Update pattern library and recognition models",
                "source": "incident_management"
            },
            {
                "event_type": "exercise.completed",
                "handler": "handle_exercise_completed",
                "description": "Learn from exercise outcomes and detect training gaps",
                "source": "training_system"
            },
            {
                "event_type": "prediction.made",
                "handler": "handle_prediction_made",
                "description": "Track predictions for accuracy measurement and self-learning",
                "source": "ml_system"
            }
        ],
        "total_subscribers": 12,
        "status": "active" if hasattr(app.state, 'learning_subscriber') else "disabled"
    }


# ============================================================================
# STARTUP / SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(" Unified Learning & Knowledge System starting up...")
    logger.info("    Knowledge Management: READY")
    logger.info(f"    Learning Engine: {'READY' if LEARNING_ROUTERS_AVAILABLE else 'LIMITED'}")
    logger.info(f"    Training Programs: {'READY' if LEARNING_ROUTERS_AVAILABLE else 'LIMITED'}")
    logger.info("   ️  Cross-Learning Cycle: READY")

    # TODO: Initialize Redis connection
    # TODO: Initialize Prometheus metrics

    # Initialize EventBus
    try:
        rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://bcm_platform:bcm_secure_2024@localhost:5673/")
        eventbus = init_eventbus(rabbitmq_url)
        await eventbus.connect()
        logger.info("    EventBus: CONNECTED")

        # Setup reactive learning subscribers
        try:
            import sys
            from pathlib import Path
            events_path = Path(__file__).parent.parent / "events"
            if str(events_path) not in sys.path:
                sys.path.insert(0, str(events_path))

            from events.subscribers import setup_event_subscribers
            subscriber = await setup_event_subscribers(eventbus)

            if subscriber:
                logger.info("    Reactive Learning: ACTIVE (12 subscribers)")
                # Store subscriber for access
                app.state.learning_subscriber = subscriber
            else:
                logger.warning("   ️ Reactive Learning: DISABLED")

        except Exception as e:
            logger.error(f"    Reactive Learning setup failed: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"    EventBus: FAILED - {e}")

    logger.info(" Unified System API ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(" Unified Learning & Knowledge System shutting down...")

    # TODO: Close Redis connection

    # Close EventBus
    try:
        eventbus = get_eventbus()
        await eventbus.disconnect()
        logger.info("    EventBus: DISCONNECTED")
    except Exception as e:
        logger.error(f"    EventBus disconnect failed: {e}")

    logger.info(" Shutdown complete")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8030,
        reload=True,
        log_level="info"
    )
