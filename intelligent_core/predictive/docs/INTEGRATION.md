# Predictive Journey Service - Integration Guide

**Document Version**: 1.0.0
**Last Updated**: 2025-10-09

## 1. Integration Overview

The Predictive Journey Service integrates with multiple platform components to deliver AI-powered forecasting capabilities. This document details all integration points, protocols, and implementation patterns.

## 2. Internal Dependencies

### 2.1 Case Library Integration (workflow_intelligence)

**Purpose**: Access historical journey data for pattern analysis

**Integration Type**: Direct Python import + Database access

**Implementation**:

```python
from workflow_intelligence.case_library.repository import CaseRepository

# Initialize
case_library = CaseRepository(
    db_client=supabase_client,
    cache_client=redis_client
)

# Find similar organizations
similar_cases = await case_library.find_similar_cases(
    organization_context={
        'industry': 'healthcare',
        'size': 250,
        'maturity_level': 2,
        'region': 'north_america'
    },
    limit=50,
    min_similarity=0.5
)

# Get benchmarks
benchmarks = await case_library.get_benchmarks(
    industry='healthcare',
    module='bia',
    min_cases=5
)
```

**Data Exchanged**:
- Organization profiles (industry, size, maturity)
- Completed workflow cases (milestones, durations, outcomes)
- Benchmark statistics (averages, medians, distributions)
- Success patterns (frequency, effectiveness)

**Error Handling**:
```python
try:
    similar_cases = await case_library.find_similar_cases(...)
except CaseLibraryUnavailable:
    # Fallback to default patterns
    return get_default_prediction_patterns()
except InsufficientData:
    # Return error with guidance
    raise HTTPException(
        status_code=422,
        detail="Insufficient historical data for prediction. Need at least 3 similar organizations."
    )
```

### 2.2 EventBus Integration (shared.event_bus)

**Purpose**: Publish prediction events and subscribe to platform events

**Integration Type**: Redis Pub/Sub via shared EventBus

**Initialization**:

```python
from shared.event_bus import init_event_bus, get_event_bus

# Startup
await init_event_bus(
    service_name="predictive",
    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379")
)

eventbus = get_event_bus()
```

**Published Events** (8 types):

```python
# 1. Journey forecast generated
await eventbus.publish('prediction.forecast_generated', {
    'organization_id': str,
    'horizon_days': int,
    'milestones_count': int,
    'avg_confidence': float,
    'certification_date': str,
    'generated_at': str
})

# 2. Certification predicted
await eventbus.publish('prediction.certification_predicted', {
    'organization_id': str,
    'predicted_date': str,
    'success_probability': float,
    'months_remaining': float,
    'based_on_orgs': int
})

# 3. Demand forecast updated
await eventbus.publish('prediction.demand_forecast_updated', {
    'specialty': str,
    'time_period': str,  # 'next_30_days'
    'expected_projects': int,
    'peak_week': str,
    'confidence': float,
    'geographic_distribution': dict
})

# 4. Low confidence warning
await eventbus.publish('prediction.confidence_low', {
    'prediction_id': str,
    'organization_id': str,
    'confidence': float,
    'reason': str,
    'similar_orgs_count': int
})

# 5. Milestone approaching
await eventbus.publish('prediction.milestone_approaching', {
    'organization_id': str,
    'milestone': str,
    'days_until': int,
    'confidence': float,
    'preparations_needed': list
})

# 6. Daily digest sent
await eventbus.publish('prediction.daily_digest_sent', {
    'organization_id': str,
    'recommendations_count': int,
    'milestones_within_7_days': int,
    'sent_at': str
})

# 7. Pattern updated
await eventbus.publish('prediction.pattern_updated', {
    'pattern_type': str,
    'milestone': str,
    'old_confidence': float,
    'new_confidence': float,
    'based_on_cases': int
})

# 8. Accuracy tracked
await eventbus.publish('prediction.accuracy_tracked', {
    'prediction_id': str,
    'predicted_date': str,
    'actual_date': str,
    'error_days': int,
    'was_accurate': bool  # within ±7 days
})
```

**Subscribed Events** (5 types):

```python
# 1. Workflow completed
@eventbus.subscribe('workflow.completed')
async def on_workflow_completed(event_data):
    """
    Update patterns when workflow completes
    """
    org_id = event_data['organization_id']
    module = event_data['module']

    # Re-generate journey prediction with new data
    await journey_predictor.update_predictions(org_id)

    # Track prediction accuracy
    await track_prediction_accuracy(org_id, module)

# 2. BIA completed
@eventbus.subscribe('bia.completed')
async def on_bia_completed(event_data):
    """
    Trigger initial journey prediction
    """
    org_id = event_data['organization_id']

    # Generate 90-day journey forecast
    prediction = await journey_predictor.predict_next_milestones(
        org_id=org_id,
        horizon_days=90
    )

    # Send welcome email with timeline
    await send_journey_welcome_email(org_id, prediction)

# 3. Risk completed
@eventbus.subscribe('risk.completed')
async def on_risk_completed(event_data):
    """
    Update milestone patterns
    """
    await update_milestone_patterns('risk_assessment', event_data)

# 4. Case approved
@eventbus.subscribe('case.approved')
async def on_case_approved(event_data):
    """
    Add to similar case pool
    """
    # Case now available for pattern matching
    await invalidate_pattern_cache()

# 5. Organization profile updated
@eventbus.subscribe('organization.profile_updated')
async def on_profile_updated(event_data):
    """
    Re-calculate similarity matches
    """
    org_id = event_data['organization_id']

    # Invalidate cached similar organizations
    await cache.delete(f'similar:{org_id}')

    # Re-generate predictions with new context
    await journey_predictor.update_predictions(org_id)
```

**Connection Health Monitoring**:

```python
async def check_eventbus_health():
    """Verify EventBus connectivity"""
    try:
        eventbus = get_event_bus()
        if not eventbus:
            return False

        # Test publish
        await eventbus.publish('health.check', {'timestamp': datetime.utcnow().isoformat()})
        return True
    except Exception as e:
        logger.error(f"EventBus health check failed: {e}")
        return False
```

### 2.3 Notification Service Integration

**Purpose**: Deliver daily digests and proactive recommendations via email

**Integration Type**: HTTP REST API

**Base URL**: `http://notification-service:8020`

**Authentication**: Service-to-service JWT token

**Implementation**:

```python
import httpx

class NotificationClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)

    async def send_daily_digest(
        self,
        user_email: str,
        organization_name: str,
        recommendations: List[Dict]
    ):
        """Send daily proactive recommendations"""
        payload = {
            'template': 'daily_digest',
            'to': user_email,
            'data': {
                'organization_name': organization_name,
                'recommendations': recommendations,
                'generated_at': datetime.utcnow().isoformat()
            }
        }

        response = await self.client.post(
            f'{self.base_url}/api/v1/notifications/email',
            json=payload,
            headers={'Authorization': f'Bearer {self.get_service_token()}'}
        )

        response.raise_for_status()
        return response.json()

    async def send_milestone_reminder(
        self,
        user_email: str,
        milestone: Dict,
        days_until: int
    ):
        """Send milestone approaching notification"""
        payload = {
            'template': 'milestone_reminder',
            'to': user_email,
            'data': {
                'milestone_name': milestone['name'],
                'days_until': days_until,
                'confidence': milestone['confidence'],
                'preparations': milestone.get('preparations', []),
                'resources': milestone.get('resources', [])
            }
        }

        response = await self.client.post(
            f'{self.base_url}/api/v1/notifications/email',
            json=payload
        )

        response.raise_for_status()
        return response.json()
```

**Error Handling**:

```python
try:
    await notification_client.send_daily_digest(...)
except httpx.HTTPStatusError as e:
    if e.response.status_code == 429:
        # Rate limited, retry with backoff
        await asyncio.sleep(60)
        await notification_client.send_daily_digest(...)
    elif e.response.status_code == 503:
        # Service unavailable, log and continue
        logger.error(f"Notification service unavailable: {e}")
    else:
        raise
except httpx.TimeoutException:
    logger.error("Notification service timeout")
```

### 2.4 Database Integration (Supabase PostgreSQL)

**Purpose**: Store predictions, track accuracy, cache patterns

**Integration Type**: PostgreSQL via Supabase client

**Tables Used**:

```sql
-- Predictions storage
CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    prediction_type VARCHAR(50) NOT NULL,
    predicted_data JSONB NOT NULL,
    confidence FLOAT NOT NULL,
    horizon_days INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,

    INDEX idx_org_type (organization_id, prediction_type),
    INDEX idx_created (created_at DESC)
);

-- Prediction accuracy tracking
CREATE TABLE prediction_accuracy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prediction_id UUID REFERENCES predictions(id),
    predicted_date DATE NOT NULL,
    actual_date DATE,
    error_days INTEGER,
    was_accurate BOOLEAN,
    tracked_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_prediction (prediction_id)
);

-- Pattern cache
CREATE TABLE pattern_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_key VARCHAR(200) UNIQUE NOT NULL,
    pattern_data JSONB NOT NULL,
    confidence FLOAT,
    sample_size INTEGER,
    last_updated TIMESTAMP DEFAULT NOW(),

    INDEX idx_key (pattern_key)
);
```

**Client Initialization**:

```python
from supabase import create_client, Client

supabase: Client = create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_KEY")
)
```

**Usage Patterns**:

```python
# Store prediction
prediction_record = {
    'organization_id': str(org_id),
    'prediction_type': 'journey',
    'predicted_data': predicted_milestones,
    'confidence': avg_confidence,
    'horizon_days': 90,
    'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
}

result = supabase.table('predictions').insert(prediction_record).execute()

# Track accuracy
accuracy_record = {
    'prediction_id': prediction_id,
    'predicted_date': predicted_date.isoformat(),
    'actual_date': actual_date.isoformat(),
    'error_days': abs((actual_date - predicted_date).days),
    'was_accurate': abs((actual_date - predicted_date).days) <= 7
}

supabase.table('prediction_accuracy').insert(accuracy_record).execute()

# Query patterns
patterns = supabase.table('pattern_cache')\
    .select('*')\
    .eq('pattern_key', f'milestone:risk_assessment')\
    .single()\
    .execute()
```

## 3. External Dependencies

### 3.1 Redis (EventBus + Caching)

**Purpose**: Message broker and prediction caching

**Connection**: `redis://localhost:6379` or `REDIS_URL` env var

**Usage**:

```python
import redis.asyncio as aioredis

# Caching
redis_client = await aioredis.from_url(
    os.getenv("REDIS_URL"),
    encoding="utf-8",
    decode_responses=True
)

# Cache journey prediction
cache_key = f'prediction:journey:{org_id}:90'
await redis_client.setex(
    cache_key,
    86400,  # 24 hours TTL
    json.dumps(prediction_data)
)

# Retrieve cached prediction
cached = await redis_client.get(cache_key)
if cached:
    return json.loads(cached)
```

**Cache Invalidation**:

```python
# Invalidate on workflow completion
await redis_client.delete(f'prediction:journey:{org_id}:*')

# Invalidate similar organizations cache
await redis_client.delete(f'similar:{org_id}')
```

### 3.2 Prometheus (Metrics)

**Purpose**: Service metrics and monitoring

**Endpoint**: `/metrics`

**Metrics Exposed**:

```python
from prometheus_client import Counter, Histogram, Gauge

# Predictions counter
predictions_total = Counter(
    'predictive_predictions_total',
    'Total predictions generated',
    ['prediction_type', 'status']
)

# Usage
predictions_total.labels(prediction_type='journey', status='success').inc()

# Confidence distribution
confidence_scores = Histogram(
    'predictive_confidence_scores',
    'Distribution of confidence scores',
    buckets=[0.3, 0.5, 0.7, 0.8, 0.9, 1.0]
)

# Usage
confidence_scores.observe(0.87)

# Similar orgs found
similar_orgs_gauge = Gauge(
    'predictive_similar_orgs_count',
    'Number of similar organizations found'
)

# Usage
similar_orgs_gauge.set(47)
```

## 4. API Integration Patterns

### 4.1 REST API Endpoints

**Base URL**: `http://predictive-service:8031/api/v1/predictions`

**Authentication**: Bearer token (JWT)

**Endpoints**:

```bash
# Journey prediction
GET /journey/{org_id}?horizon_days=90
Authorization: Bearer {token}

Response 200:
{
  "organization_id": "uuid",
  "horizon_days": 90,
  "milestones": [
    {
      "milestone": "risk_assessment",
      "predicted_start_date": "2025-10-18T00:00:00Z",
      "predicted_duration_days": 34,
      "confidence": 0.87,
      "reasoning": "83% of similar orgs started risk 14±3 days after BIA",
      "expert_recommendations": [...],
      "cost_estimate": {...},
      "challenges": [...]
    }
  ],
  "certification_timeline": {
    "predicted_date": "2026-06-15",
    "success_probability": 0.82
  },
  "based_on_organizations": 47,
  "generated_at": "2025-10-09T10:00:00Z"
}

# Certification forecast
GET /certification/{org_id}
Response: {...}

# Proactive recommendations
GET /recommendations/{org_id}?days_ahead=14
Response: {...}

# Expert demand forecast
GET /expert-demand?horizon_days=30&specialty=bia
Response: {...}

# Similar organizations
GET /similar-organizations/{org_id}?limit=10
Response: {...}
```

### 4.2 Client SDK Example

```python
class PredictiveClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            headers={'Authorization': f'Bearer {api_key}'}
        )

    async def get_journey_prediction(
        self,
        org_id: str,
        horizon_days: int = 90
    ) -> Dict:
        """Get journey timeline prediction"""
        response = await self.client.get(
            f'{self.base_url}/journey/{org_id}',
            params={'horizon_days': horizon_days}
        )
        response.raise_for_status()
        return response.json()

    async def get_recommendations(
        self,
        org_id: str,
        days_ahead: int = 14
    ) -> Dict:
        """Get proactive recommendations"""
        response = await self.client.get(
            f'{self.base_url}/recommendations/{org_id}',
            params={'days_ahead': days_ahead}
        )
        response.raise_for_status()
        return response.json()

# Usage
client = PredictiveClient(
    base_url='http://predictive-service:8031/api/v1/predictions',
    api_key=os.getenv('API_KEY')
)

prediction = await client.get_journey_prediction(
    org_id='123e4567-e89b-12d3-a456-426614174000'
)
```

## 5. Integration Testing

### 5.1 EventBus Integration Test

```python
import pytest

@pytest.mark.asyncio
async def test_eventbus_publish():
    """Test event publishing"""
    await init_event_bus(service_name="predictive_test")
    eventbus = get_event_bus()

    # Publish event
    await eventbus.publish('prediction.forecast_generated', {
        'organization_id': 'test-org-1',
        'milestones_count': 3,
        'avg_confidence': 0.85
    })

    # Verify event was published (check logs or subscriber)
    assert True

@pytest.mark.asyncio
async def test_eventbus_subscribe():
    """Test event subscription"""
    received_events = []

    async def test_handler(event_data):
        received_events.append(event_data)

    await init_event_bus(service_name="predictive_test")
    eventbus = get_event_bus()

    # Subscribe
    await eventbus.subscribe('workflow.completed', test_handler)

    # Publish test event
    await eventbus.publish('workflow.completed', {
        'organization_id': 'test-org-1',
        'module': 'bia'
    })

    # Wait for processing
    await asyncio.sleep(0.5)

    # Verify received
    assert len(received_events) == 1
    assert received_events[0]['module'] == 'bia'
```

### 5.2 Case Library Integration Test

```python
@pytest.mark.asyncio
async def test_case_library_integration():
    """Test case library access"""
    case_library = CaseRepository(db_client=test_db)

    # Find similar organizations
    similar = await case_library.find_similar_cases(
        organization_context={
            'industry': 'healthcare',
            'size': 200,
            'maturity_level': 2
        },
        limit=10
    )

    assert len(similar) > 0
    assert similar[0]['industry'] == 'healthcare'
```

### 5.3 Notification Service Integration Test

```python
@pytest.mark.asyncio
async def test_notification_integration():
    """Test notification delivery"""
    notification_client = NotificationClient(
        base_url='http://notification-service:8020'
    )

    result = await notification_client.send_daily_digest(
        user_email='test@example.com',
        organization_name='Test Org',
        recommendations=[
            {
                'milestone': 'risk_assessment',
                'days_until': 3,
                'confidence': 0.87
            }
        ]
    )

    assert result['status'] == 'sent'
```

## 6. Troubleshooting Integration Issues

### 6.1 Case Library Unavailable

**Symptom**: `CaseLibraryUnavailable` exception

**Diagnosis**:
```python
# Check case library health
try:
    await case_library.health_check()
except Exception as e:
    logger.error(f"Case library health check failed: {e}")
```

**Solution**:
- Verify workflow_intelligence service is running
- Check database connectivity
- Fallback to default patterns

### 6.2 EventBus Connection Failed

**Symptom**: Events not publishing, subscription failures

**Diagnosis**:
```python
# Check Redis connectivity
try:
    await redis_client.ping()
except Exception as e:
    logger.error(f"Redis ping failed: {e}")
```

**Solution**:
- Verify REDIS_URL environment variable
- Check Redis server status
- Restart EventBus connection

### 6.3 Notification Delivery Failure

**Symptom**: Daily digests not sending

**Diagnosis**:
```bash
# Check notification service logs
curl http://notification-service:8020/health

# Check predictive service logs
grep "Notification.*failed" logs/predictive.log
```

**Solution**:
- Verify notification service connectivity
- Check SMTP configuration
- Review rate limiting

---

**Document Control**
- Version: 1.0.0
- Author: AI Platform Team
- Review Date: 2025-10-09
- Next Review: 2026-01-09
