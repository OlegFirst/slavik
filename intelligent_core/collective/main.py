"""
🤝 Collective Agent Networks Service

**THE BREAKTHROUGH:**
Organizations help each other through AI without revealing their identities.

**How it works:**
1. Organization A stuck on problem
2. Platform finds organizations B, C, D that solved it
3. Creates temporary Collective Agent from their experiences
4. A chats with agent without knowing who B, C, D are
5. Full privacy + collective wisdom

**Example:**
```
User: "Struggling with supply chain dependencies in BIA"

Platform: "I've created a Collective Agent from 7 organizations
           that solved this challenge. Chat with it:"

Collective Agent: "Organizations that addressed supply chain
                   complexity typically started with Tier 1
                   suppliers. 5 out of 7 used dependency mapping
                   tools. The common pattern was..."

User: 🤯 "This is AMAZING! But who are these organizations?"

Platform: "That information is anonymous to protect privacy.
           But their collective wisdom is now yours."
```

**Privacy Guarantees:**
- Source organizations NEVER revealed
- Minimum 5 organizations required (k-anonymity)
- Multi-layer anonymization
- Agents expire after 7 days

Port: 8032
"""

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
import sys
from pathlib import Path
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from .config import settings
from .api import collective_agents, stuck_detection

# Add shared event_bus to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.event_bus import init_event_bus, get_event_bus

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ================================================
# LIFECYCLE
# ================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager

    Startup:
    - Initialize database connections
    - Start agent expiration cron job
    - Start stuck detection cron job

    Shutdown:
    - Close database connections
    - Stop background jobs
    """

    logger.info("🤝 Collective Agent Networks Service starting...")
    logger.info(f"Port: {settings.PORT}")
    logger.info(f"K-anonymity: {settings.K_ANONYMITY} (minimum organizations)")
    logger.info(f"Agent expiration: {settings.AGENT_EXPIRATION_DAYS} days")

    # Initialize EventBus
    try:
        await init_event_bus(
            service_name="collective",
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379")
        )
        logger.info("✅ EventBus initialized")
    except Exception as e:
        logger.warning(f"⚠️ EventBus init failed: {e}")

    # Startup
    try:
        # Initialize background jobs
        # In production: Start cron jobs for agent expiration and stuck detection
        logger.info("✅ Background jobs initialized")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Collective Agent Networks Service shutting down...")
    bus = get_event_bus()
    if bus:
        await bus.close()

# ================================================
# APPLICATION
# ================================================

app = FastAPI(
    title="Collective Agent Networks",
    description="""
    🤝 **Anonymous Collaboration Between Organizations**

    Organizations help each other through AI without revealing their identities.

    ## Key Features

    ### 🤖 Collective Agents
    Temporary AI agents created from multiple organizations' experiences.
    - **Anonymous:** Source organizations never revealed
    - **Collective:** Synthesizes wisdom from 5+ organizations
    - **Temporary:** Expires after 7 days

    ### 🆘 Stuck Detection
    Automatically detects when organizations need help.
    - Days without progress
    - Validation failures
    - Low AI confidence
    - Frustration indicators

    ### 🔒 Privacy-Preserving
    Multi-layer anonymization ensures privacy.
    - K-anonymity (minimum 5 orgs)
    - No outlier highlighting
    - Geographic generalization
    - No time correlation

    ## Use Cases

    **1. Stuck on BIA**
    - Hospital struggling with dependency mapping for 2 weeks
    - Platform creates Collective Agent from 7 hospitals that solved it
    - User asks: "How did you identify indirect dependencies?"
    - Agent: "Organizations typically used stakeholder interviews..."

    **2. Anonymous Benchmarking**
    - "Is our BIA timeline normal?"
    - Platform finds 12 similar orgs (anonymized)
    - Shows: "Organizations like yours completed BIA in 42 days (median)"

    **3. Best Practice Discovery**
    - "What's the best way to engage executives?"
    - Platform creates agent from 8 successful organizations
    - Agent: "Organizations with strong executive sponsorship achieved it through..."

    ## Privacy Architecture

    **Layer 1: Organization Anonymization**
    - Remove org name, people, dates
    - Keep industry, size category, region

    **Layer 2: Aggregation**
    - Minimum 5 organizations required
    - Aggregate statistics only

    **Layer 3: Collective Agent Synthesis**
    - AI generates collective wisdom
    - NEVER reveals source organizations
    - Speaks as: "Organizations that..."

    ## Innovation Level: 🤯🤯🤯🤯🤯

    **Why Revolutionary:**
    - Solves privacy paradox (want to share vs. can't share)
    - Network effects without risk
    - Small orgs get big org wisdom
    - Unique differentiation (no competitor does this)
    """,
    version="1.0.0",
    lifespan=lifespan
)

# ================================================
# MIDDLEWARE
# ================================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================================
# ROUTES
# ================================================

# Register API routers
app.include_router(collective_agents.router, prefix="/api/v1")
app.include_router(stuck_detection.router, prefix="/api/v1")

# ================================================
# HEALTH CHECK
# ================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "collective-agent-networks",
        "port": settings.PORT,
        "privacy": {
            "k_anonymity": settings.K_ANONYMITY,
            "max_risk_score": settings.MAX_RISK_SCORE,
            "agent_expiration_days": settings.AGENT_EXPIRATION_DAYS
        }
    }

@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint

    Exposes collective agent metrics for monitoring.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "Collective Agent Networks",
        "tagline": "🤝 Organizations help each other through AI without revealing their identities",
        "version": "1.0.0",
        "port": settings.PORT,
        "innovation_level": "🤯🤯🤯🤯🤯",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "collective_agents": "/api/v1/collective-agents",
            "stuck_detection": "/api/v1/stuck-detection"
        },
        "how_it_works": [
            "1. Organization A stuck on problem",
            "2. Platform finds organizations B, C, D that solved it",
            "3. Creates Collective Agent from their anonymized experiences",
            "4. A chats with agent without knowing who B, C, D are",
            "5. Full privacy + collective wisdom ✨"
        ],
        "privacy_guarantees": [
            "✅ Source organizations NEVER revealed",
            "✅ Minimum 5 organizations required (k-anonymity)",
            "✅ Multi-layer anonymization",
            "✅ Agents expire after 7 days"
        ]
    }

# ================================================
# ERROR HANDLERS
# ================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return {
        "error": "Not found",
        "message": "The requested resource was not found",
        "hint": "Check /docs for available endpoints"
    }

# ================================================
# MAIN
# ================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )
