# Workflow Engine - Architecture

**Version**: 1.0.0
**Last Updated**: 2025-10-09

## Overview

Bcm workflow orchestration and state management.

**Port**: 8035

## Components

### Core Components

- **Workflow definition and execution**
- **State machine implementation**
- **Transition validation**
- **Progress tracking**
- **Checkpoint management**

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
