# BCM GitHub Integration Service

**Extracted from:** `/intelligent-core/tools/github_app/` (Oct 4, 2025)
**Status:** Production-ready
**Lines of code:** 99

## What it does
GitHub integration service that handles webhooks, authentication, and provides proxy endpoints for GitHub Copilot Extension to communicate with the AI Orchestrator. Acts as a bridge between GitHub's ecosystem and the BCM platform's AI services.

## Integration points
- **GitHub Webhooks:** Receives and processes GitHub events
- **GitHub Copilot Extension:** Token exchange and authentication
- **AI Orchestrator:** Proxies Claude AI requests to `http://ai_orchestrator:8000`
  - `/claude/analyze-changes` - Code change analysis
  - `/claude/generate-config` - Configuration generation
  - `/claude/analyze-deployment` - Deployment analysis
  - `/deployment/orchestrate` - Deployment orchestration
  - `/deployment/history` - Deployment history retrieval
- **EventBus:** No direct integration (proxies to orchestrator)
- **Database:** No direct database access

## Dependencies
- FastAPI (web framework)
- httpx (async HTTP client for proxying)
- uvicorn (ASGI server)
- Standard Python libraries

## Key Features
- GitHub webhook handling
- OAuth token exchange for Copilot Extension
- Transparent proxy to AI Orchestrator
- Async HTTP client for high performance
- Environment-based configuration

## Environment Variables
- `GITHUB_APP_ID` - GitHub App identifier
- Additional GitHub App credentials as needed

## How to run
```bash
# Build the service
docker build -t bcm-github-integration .

# Run standalone
python main.py

# Or via docker-compose
docker-compose up github-integration
```

## API Endpoints
### GitHub Integration
- `GET /` - Service status and info
- `POST /github/webhook` - GitHub webhook receiver
- `POST /auth/token-exchange` - Copilot token exchange

### Proxy Endpoints (to AI Orchestrator)
- `POST /claude/analyze-changes` - Proxy code analysis
- `POST /claude/generate-config` - Proxy config generation
- `POST /claude/analyze-deployment` - Proxy deployment analysis
- `POST /deployment/orchestrate` - Proxy deployment orchestration
- `GET /deployment/history` - Proxy deployment history
