# Predictive Journey Service

**Type**: Core Module
**Domain**: Intelligent-Core
**Status**: Active
**Version**: 1.0.0
**Port**: 8031

## Overview

The Predictive Journey Service provides AI-powered forecasting capabilities for business continuity management journeys. It analyzes historical organizational data to predict future milestones, certification timelines, expert demands, and potential challenges. The service leverages pattern matching, statistical analysis, and machine learning to deliver proactive recommendations with confidence scoring.

## Architecture

### Core Components

- **Journey Predictor**: Forecasts BCM milestone timelines using similarity-based pattern matching
- **Certification Predictor**: Estimates ISO 22301 certification achievement dates
- **Demand Forecaster**: Predicts expert marketplace demand across specialties and regions
- **Proactive Recommendations Engine**: Generates daily personalized guidance and reminders
- **Challenge Predictor**: Identifies likely obstacles with mitigation strategies
- **Event Handlers**: Publishes 8+ event types and subscribes to 5+ platform events

### Technology Stack

- FastAPI (REST API framework)
- APScheduler (daily digest scheduling)
- PostgreSQL (predictions storage via Supabase)
- Redis (EventBus messaging)
- Prometheus (metrics)

## Features

- **90-Day Journey Timeline**: Predicts next 3-6 milestones with confidence scores
- **Certification Date Forecasting**: Success probability and key success factors
- **Daily Proactive Digests**: Personalized recommendations via email (8:00 AM schedule)
- **Expert Demand Forecasting**: Aggregate demand predictions by specialty and geography
- **Challenge Prediction**: Historical pattern-based obstacle identification
- **Cost Estimation**: Size-adjusted internal staff time estimates
- **Similarity Matching**: Multi-factor organizational matching algorithm
- **Confidence Scoring**: Transparent frequency and variance-based confidence

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL (Supabase)
- Redis 7.0+
- Access to Case Library (workflow_intelligence module)

### Setup

```bash
cd intelligent-core/predictive

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env with:
# - SUPABASE_URL
# - SUPABASE_KEY
# - REDIS_URL
# - NOTIFICATION_SERVICE_URL

# Run service
python main.py
```

Service starts on http://localhost:8031

API documentation: http://localhost:8031/docs

## API Reference

See [docs/API.md](docs/API.md) for complete API documentation.

### Primary Endpoints

- `GET /api/v1/predictions/journey/{org_id}` - Journey timeline prediction
- `GET /api/v1/predictions/certification/{org_id}` - Certification forecast
- `GET /api/v1/predictions/recommendations/{org_id}` - Proactive recommendations
- `GET /api/v1/predictions/expert-demand` - Marketplace demand forecast
- `GET /api/v1/predictions/similar-organizations/{org_id}` - Similar case lookup
- `GET /health` - Service health check
- `GET /metrics` - Prometheus metrics

## Dependencies

### Internal Dependencies

- `shared.event_bus` - Event publishing and subscription
- `shared.database` - Supabase client and connection pooling
- `workflow_intelligence.case_library` - Historical journey data
- `infrastructure.notification-service` - Email digest delivery

### External Dependencies

- Supabase PostgreSQL - Predictions storage
- Redis - EventBus messaging
- Prometheus - Metrics collection
- SMTP Server - Email delivery

## Standards Compliance

### ISO 22301:2019

- **8.2.2 Business Impact Analysis**: Supports BIA timeline prediction
- **8.2.3 Risk Assessment**: Risk milestone forecasting
- **8.3 Business Continuity Strategy**: Planning timeline prediction
- **8.4 Business Continuity Plans**: Plan development forecasting
- **9.1 Monitoring and Review**: Continuous pattern learning and accuracy tracking

### Data Privacy

- Anonymizes organizational data in similarity matching
- No PII exposure in demand forecasts
- Tenant isolation in predictions storage

## Configuration

### Environment Variables

```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Messaging
REDIS_URL=redis://localhost:6379

# Integrations
NOTIFICATION_SERVICE_URL=http://localhost:8020
CASE_LIBRARY_ENABLED=true

# Scheduler
ENABLE_DAILY_DIGESTS=true
DAILY_DIGEST_HOUR=8

# Prediction Thresholds
MIN_SIMILAR_ORGS=3
TARGET_SIMILAR_ORGS=50
MIN_CONFIDENCE=0.7
MIN_PATTERN_FREQUENCY=0.30
```

## Development

### Running Tests

```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests/integration/

# Coverage
pytest --cov=services --cov-report=html
```

### Adding New Predictions

1. Create predictor in `services/`
2. Add API endpoint in `api/predictions.py`
3. Publish events in `event_handlers.py`
4. Update docs and tests

## Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment guide.

### Docker Deployment

```bash
docker build -t predictive-journey:latest .
docker run -p 8031:8031 --env-file .env predictive-journey:latest
```

### Health Checks

- Readiness: `GET /health`
- Metrics: `GET /metrics`
- EventBus: Check `stats/eventbus` endpoint

## Monitoring

### Prometheus Metrics

- `predictive_predictions_total` - Total predictions generated
- `predictive_confidence_avg` - Average confidence scores
- `predictive_similar_orgs_count` - Similar organizations found
- `predictive_daily_digests_sent` - Daily digest deliveries
- `predictive_event_publications` - EventBus publications

### Logging

- Structured JSON logging
- Log levels: INFO (default), DEBUG, ERROR
- Correlation IDs for request tracing

## Troubleshooting

### Common Issues

**Issue**: Low prediction confidence
**Solution**: Verify MIN_SIMILAR_ORGS threshold and case library population

**Issue**: Daily digests not sending
**Solution**: Check ENABLE_DAILY_DIGESTS=true and notification service connectivity

**Issue**: EventBus integration failing
**Solution**: Verify REDIS_URL and EventBus initialization in logs

## Performance

### Benchmarks

- Journey prediction: <2 seconds (50 similar orgs)
- Certification forecast: <1 second
- Similar organization search: <1 second
- Daily digest batch: <5 seconds per 100 users

### Scalability

- Supports 10,000+ organizations
- Handles 1,000+ predictions/hour
- Caches frequent queries (24-hour TTL)

## License

Proprietary - AI-Platform-ISO

---

**Last Updated**: 2025-10-09
**Maintainer**: AI Platform Team
**Documentation**: See docs/ folder for detailed specifications
