# Event Intelligence - Architecture

**Version**: 1.0.0
**Last Updated**: 2025-10-09

## Overview

Event pattern detection and predictive analytics.

**Port**: 8036

## Components

### Core Components

- **Event pattern learning**
- **Anomaly detection**
- **Auto-discovery of services**
- **Gap prediction**
- **Code healing**

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
