# Process Mining Service - Advanced Process Analytics

**Original location:** `/infrastructure/process_mining_service/` (Sep 28, 2025)
**Duplicate found in:** `/intelligent-core/tools/process_mining_service/` (identical)
**Status:** Production-ready
**Lines of code:** 1087

## Duplication Resolution
During reorganization on Oct 4, 2025, discovered identical copy in `/intelligent-core/tools/process_mining_service/`. Both files are byte-for-byte identical (same 1087 lines). The infrastructure copy is the canonical version and was created first. The tools copy has been left in place for archival with the rest of the tools directory.

## What it does
Advanced process mining and analytics service that analyzes real process execution logs to discover patterns, bottlenecks, deviations, and optimization opportunities. Provides comprehensive process intelligence for BCM platform workflows.

## Integration points
- **Database:** PostgreSQL (`bcm_db`) for process event storage
  - Process instances and events tracking
  - Performance metrics storage
  - Pattern and bottleneck analysis results
- **EventBus:** Can be integrated for real-time event streaming
- **AI Orchestrator:** Process insights for AI-driven optimization
- **FastAPI:** RESTful API for analytics queries

## Dependencies
- FastAPI (web framework)
- SQLAlchemy (ORM and database)
- Pandas (data analysis)
- NumPy (numerical computations)
- PostgreSQL (database backend)

## Key Features
- Process discovery from event logs
- Bottleneck detection and analysis
- Process variant analysis
- Performance metrics computation
- Deviation detection
- Pattern mining
- Real-time process monitoring
- Event log upload and processing

## Database Schema
Creates tables for:
- `process_instances` - Process execution instances
- `process_events` - Individual process events
- `process_metrics` - Computed performance metrics
- `process_patterns` - Discovered patterns and insights

## How to run
```bash
# Build the service
docker build -t bcm-process-mining .

# Run standalone
python main.py

# Or via docker-compose
docker-compose up process-mining
```

## API Endpoints
- `GET /health` - Service health check
- `POST /upload` - Upload process event logs
- `GET /processes` - List all processes
- `GET /processes/{id}/analysis` - Get process analysis
- `GET /bottlenecks` - Identify process bottlenecks
- `GET /patterns` - Discover process patterns
- `GET /metrics/{process_id}` - Process performance metrics
