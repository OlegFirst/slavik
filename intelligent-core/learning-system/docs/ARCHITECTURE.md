# Learning System - Architecture

**Version**: 1.0.0
**Last Updated**: 2025-10-09

## Overview

Adaptive learning system for organizational knowledge management.

**Port**: 8033

## Components

### Core Components

- **Knowledge graph construction**
- **Lesson learned capture**
- **Training recommendation engine**
- **Competency tracking**
- **Learning path optimization**

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
