# Legacy AI Services Archive

**Extracted from:** `/intelligent-core/tools/docker-ai/` and `/intelligent-core/tools/docker-ai-poc/` (Oct 4, 2025)
**Status:** Legacy / Archive (not for production)
**Total lines of code:** ~527

## What these were
Early proof-of-concept unified AI services that combined multiple AI capabilities into single monolithic containers. These were experimental Docker-based services created during the initial platform development phase.

## Contents

### 1. docker-ai/ (264 LOC)
Original unified AI service combining:
- AI Orchestrator functionality
- BIA (Business Impact Analysis) Engine
- Document Processor
- Compliance Checker

**Key files:**
- `unified_ai_service.py` - Main service implementation
- `Dockerfile` - Container configuration
- `docker-compose.ai.yml` - Docker Compose setup

### 2. docker-ai-poc/ (263 LOC)
Proof-of-concept variant with similar functionality but experimental features:
- Agent-based architecture exploration
- Alternative AI orchestration patterns
- Testing different integration approaches

**Key files:**
- `unified_ai_service.py` - POC implementation
- `Dockerfile` - Container configuration
- `docker-compose.ai.yml` - Docker Compose setup

## Why archived
These services were replaced by the modular microservices architecture:
- **Too monolithic:** Combined too many concerns
- **Hard to scale:** Single service couldn't scale independently
- **Limited flexibility:** Difficult to update individual components
- **Superseded by:** Modern AI Orchestrator + specialized services

## Modern replacements
- **AI Orchestrator** (`/intelligent-core/ai-orchestration/`) - Main AI coordination
- **Document Processor** - Specialized document handling
- **Compliance Service** - Dedicated compliance checking
- **BIA Service** - Business impact analysis

## Historical value
These services represent important architectural learning:
- Early AI integration patterns
- Docker containerization approaches
- Service discovery experiments
- Multi-AI coordination concepts

## Do NOT use for
- Production deployments
- New development
- Reference architecture
- Current best practices

## MAY use for
- Historical reference
- Understanding evolution of platform
- Learning what NOT to do
- Recovering old experimental features

## Integration points (historical)
- Redis: Event messaging
- PostgreSQL: Data storage
- FastAPI: REST API
- Docker: Containerization
- Agent discovery: Health checks

## Dependencies (frozen)
- FastAPI
- Redis client
- httpx (async HTTP)
- Pydantic
- Standard Python libraries

## Notes
Both implementations are nearly identical (264 vs 263 lines), suggesting the POC was a minor variation of the original. The differences are minimal and mainly in experimental features or configuration.

---

**Archive date:** October 4, 2025
**Archived by:** Claude Code reorganization
**Original location:** `/intelligent-core/tools/`
**Reason:** Platform modernization and architectural refactoring
