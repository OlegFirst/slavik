# Community Intelligence - Architecture

**Version**: 1.0.0
**Last Updated**: 2025-10-09

## Overview

Community-driven knowledge creation through peer review and reputation.

**Port**: 8030

## Components

### Core Components

- **Auto-contribution from workflow completions**
- **Peer review system with quality scoring**
- **Reputation economy with gamification**
- **Case library with semantic search**
- **Smart anonymization**

## Technology Stack

- Python 3.11+
- FastAPI (if service)
- PostgreSQL (Supabase)
- Redis (EventBus)

## Integration Points

### Internal Dependencies

- `shared.database` - Database client
- `shared.eventbus` - Event messaging
- `ai_foundation` - AI capabilities

### External Dependencies

- Supabase PostgreSQL
- Redis
- Prometheus (metrics)

## Data Flow

```
Request → API Layer → Business Logic → Data Layer → Response
           ↓
      Event Publishing
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions.

---

**Document Control**
- Version: 1.0.0
- Author: AI Platform Team
- Review Date: 2025-10-09
