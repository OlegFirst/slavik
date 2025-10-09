# Expertise Center - Architecture

**Version**: 1.0.0
**Last Updated**: 2025-10-09

## Overview

Domain expertise and specialized ai assistants for bcm.

**Port**: 8029

## Components

### Core Components

- **BCM domain knowledge base**
- **ISO 22301 compliance guidance**
- **Industry-specific templates**
- **Expert AI assistants**
- **Best practice recommendations**

## Technology Stack

- Python 3.11+
- FastAPI (if service)
- PostgreSQL (Supabase)
- Redis (EventBus)

## Integration Points

### Internal Dependencies

- `shared.database` - Database client
- `shared.eventbus` - Event messaging

### External Dependencies

- Supabase PostgreSQL
- Redis
- AI APIs (Anthropic, OpenAI)

---

**Document Control**
- Version: 1.0.0
- Author: AI Platform Team
- Review Date: 2025-10-09
