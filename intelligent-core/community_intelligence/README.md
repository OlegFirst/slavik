# Community Intelligence Service

**Type**: Core Module
**Domain**: Intelligent-Core
**Status**: Production Ready
**Version**: 1.0.0
**Port**: 8030

## Overview

The Community Intelligence Service transforms passive case collection into active community-driven knowledge creation. It enables peer-reviewed knowledge sharing through automated workflow integration, expert validation, reputation systems, and a searchable case library of BCM best practices.

## Architecture

### Core Components

- **Contribution Manager**: Auto-captures workflow completions as shareable cases
- **Peer Review System**: Smart reviewer matching and quality scoring
- **Reputation Engine**: Gamification and incentive mechanisms
- **Case Library**: Searchable knowledge base with anonymization
- **Event Integration**: Workflow completion triggers and EventBus publishing

### Technology Stack

- FastAPI (REST API framework)
- PostgreSQL (Supabase) - contributions, reviews, reputation
- Redis (EventBus messaging)
- AI Foundation (anonymization, reviewer matching)

## Features

- **Auto-Contribution**: Workflow completion triggers contribution offers
- **Smart Anonymization**: AI-powered PII removal with preview
- **Peer Review**: 3-reviewer consensus with quality scoring (1-10)
- **Reputation Economy**: Points, badges, and leaderboards
- **Case Search**: Full-text and semantic similarity search
- **Reviewer Matching**: Expertise, industry, and workload-based matching
- **Quality Assurance**: 2/3 approval threshold for publication

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL (Supabase)
- Redis 7.0+

### Setup

```bash
cd intelligent-core/community_intelligence

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env with SUPABASE_URL, SUPABASE_KEY, REDIS_URL

# Apply database migration
psql $DATABASE_URL -f ../../infrastructure/database/migrations_source/040_community_intelligence.sql

# Run service
python main.py
```

Service starts on http://localhost:8030

API documentation: http://localhost:8030/docs

## API Reference

See [API.md](API.md) for complete API documentation.

### Primary Endpoints

- `POST /api/v1/community/contributions` - Create contribution
- `POST /api/v1/community/contributions/from-workflow/{id}` - Auto-contribution from workflow
- `GET /api/v1/community/contributions/my` - User's contributions
- `POST /api/v1/community/reviews` - Submit review
- `GET /api/v1/community/reputation/leaderboard` - Top contributors
- `GET /api/v1/community/cases/search` - Search case library

## Dependencies

### Internal Dependencies

- `shared.database` - Supabase client
- `shared.eventbus` - Event publishing/subscription
- `ai_foundation` - Anonymization and matching

### External Dependencies

- PostgreSQL (Supabase) - Data persistence
- Redis - EventBus messaging

## Standards Compliance

### ISO 22301:2019

- **9.1 Monitoring and Review**: Knowledge management and lessons learned
- **10.2 Nonconformity and Corrective Action**: Peer review and quality assurance
- **A.17 Knowledge Management**: Community-driven knowledge base

### Data Privacy

- Automated PII anonymization
- Opt-in contribution model
- Reviewer anonymity
- Tenant isolation

## Configuration

### Environment Variables

```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Messaging
REDIS_URL=redis://localhost:6379

# Service
PORT=8030
CORS_ORIGINS=["*"]

# AI Foundation
ANTHROPIC_API_KEY=sk-ant-...
```

## Development

### Running Tests

```bash
pytest tests/
pytest --cov=services
```

### Adding Features

1. Create service in `services/`
2. Add API endpoint in `api/`
3. Update event handlers in `events/`
4. Add tests in `tests/`

## Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment.

### Docker

```bash
docker build -t community-intelligence:latest .
docker run -p 8030:8030 --env-file .env community-intelligence:latest
```

## Monitoring

### Health Checks

- Readiness: `GET /health`
- Metrics: `GET /metrics`

### Key Metrics

- `community_contributions_total` - Total contributions
- `community_reviews_total` - Total reviews
- `community_reputation_points` - Reputation distribution
- `community_cases_published` - Published cases

## License

Proprietary - AI-Platform-ISO

---

**Last Updated**: 2025-10-09
**Maintainer**: AI Platform Team
**Documentation**: See docs/ folder for detailed specifications
