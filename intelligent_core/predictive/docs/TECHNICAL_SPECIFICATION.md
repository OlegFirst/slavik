# Predictive Journey Service - Technical Specification

**Document Version**: 1.0.0
**Last Updated**: 2025-10-09
**Status**: Production

## 1. System Overview

### 1.1 Purpose

The Predictive Journey Service analyzes historical BCM journey data to forecast future milestones, timelines, and resource needs. It uses pattern matching and statistical analysis to provide confidence-scored predictions.

### 1.2 Scope

- Journey timeline prediction (90-day horizon)
- Certification date forecasting
- Expert demand forecasting
- Proactive recommendations generation
- Challenge prediction and mitigation
- Cost estimation
- Similarity-based organizational matching

### 1.3 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | FastAPI | 0.104+ |
| Runtime | Python | 3.11+ |
| Database | PostgreSQL (Supabase) | 15+ |
| Messaging | Redis | 7.0+ |
| Scheduler | APScheduler | 3.10+ |
| Metrics | Prometheus | Latest |
| Deployment | Docker | 24+ |

## 2. Architecture

### 2.1 Component Architecture

```
┌─────────────────────────────────────────────────┐
│         FastAPI Application (Port 8031)         │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────┐      ┌────────────────────┐  │
│  │   Journey   │      │   Certification    │  │
│  │  Predictor  │      │    Predictor       │  │
│  └──────┬──────┘      └──────┬─────────────┘  │
│         │                    │                 │
│  ┌──────┴────────────────────┴─────────────┐  │
│  │      Case Library Integration            │  │
│  │   (workflow_intelligence.case_library)   │  │
│  └──────────────────┬───────────────────────┘  │
│                     │                           │
│  ┌─────────────────┴───────────────────────┐  │
│  │   Similarity Matching Engine            │  │
│  │   - Industry (30%)                      │  │
│  │   - Size (25%)                          │  │
│  │   - Maturity (20%)                      │  │
│  │   - Resources (15%)                     │  │
│  │   - Geography (10%)                     │  │
│  └─────────────────────────────────────────┘  │
│                                                 │
│  ┌─────────────────────────────────────────┐  │
│  │    Proactive Recommendations Engine     │  │
│  │    - Daily Digest Scheduler             │  │
│  │    - Resource Mapping                   │  │
│  │    - Timing Optimization                │  │
│  └─────────────────────────────────────────┘  │
│                                                 │
│  ┌─────────────────────────────────────────┐  │
│  │        Demand Forecaster                │  │
│  │    - Specialty Aggregation              │  │
│  │    - Geographic Distribution            │  │
│  │    - Peak Detection                     │  │
│  └─────────────────────────────────────────┘  │
│                                                 │
│  ┌─────────────────────────────────────────┐  │
│  │         Event Handlers                  │  │
│  │    Publishers: 8+ event types           │  │
│  │    Subscribers: 5+ event types          │  │
│  └─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
           │              │              │
           ▼              ▼              ▼
     ┌──────────┐  ┌──────────┐  ┌──────────┐
     │PostgreSQL│  │  Redis   │  │Notification│
     │(Supabase)│  │(EventBus)│  │  Service  │
     └──────────┘  └──────────┘  └──────────┘
```

### 2.2 Data Flow

#### Journey Prediction Flow

```
1. API Request (GET /journey/{org_id}?horizon_days=90)
   ↓
2. Extract Organization Context
   ↓
3. Query Case Library (workflow_intelligence)
   ↓
4. Calculate Similarity Scores
   - Industry match: 30% weight
   - Size similarity: 25% weight
   - Maturity level: 20% weight
   - Resources: 15% weight
   - Geography: 10% weight
   ↓
5. Filter Similar Organizations (threshold >= 0.5)
   ↓
6. Pattern Analysis
   - Extract milestone sequences
   - Calculate frequencies
   - Compute average durations
   - Identify challenges
   ↓
7. Statistical Confidence Scoring
   confidence = frequency * (1 - variance_penalty)
   ↓
8. Generate Predictions
   - Predicted milestones
   - Start dates
   - Durations
   - Expert recommendations
   - Cost estimates
   ↓
9. Publish Event (prediction.forecast_generated)
   ↓
10. Return Response + Cache (24h TTL)
```

#### Daily Digest Flow

```
1. Cron Trigger (8:00 AM daily)
   ↓
2. Query Active Organizations
   ↓
3. For Each Organization:
   - Get cached journey prediction
   - Filter milestones within 7 days
   - Generate recommendations
   ↓
4. Batch Notifications
   - Format email content
   - Include resources
   - Add action items
   ↓
5. Send via Notification Service
   ↓
6. Log Delivery Status
   ↓
7. Update Metrics
```

### 2.3 Database Schema

#### Predictions Table

```sql
CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    prediction_type VARCHAR(50) NOT NULL, -- 'journey', 'certification', 'demand'
    predicted_data JSONB NOT NULL,
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    horizon_days INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,

    INDEX idx_org_type (organization_id, prediction_type),
    INDEX idx_created (created_at DESC),
    INDEX idx_expires (expires_at)
);
```

#### Prediction Data Structure (JSONB)

```json
{
  "prediction_type": "journey",
  "milestones": [
    {
      "milestone": "risk_assessment",
      "predicted_start_date": "2025-10-18T00:00:00Z",
      "predicted_duration_days": 34,
      "confidence": 0.87,
      "reasoning": "83% of similar orgs started risk 14±3 days after BIA",
      "expert_recommendations": [
        {
          "specialty": "risk_assessment",
          "usage_count": 47,
          "helpful_rate": 0.92
        }
      ],
      "cost_estimate": {
        "min": 6800,
        "max": 10200,
        "currency": "USD"
      },
      "challenges": [
        {
          "challenge": "Data availability",
          "probability": 0.45,
          "mitigation": "Start with available data, use templates"
        }
      ]
    }
  ],
  "based_on_organizations": 47,
  "generated_at": "2025-10-09T10:00:00Z"
}
```

## 3. Algorithms

### 3.1 Similarity Scoring Algorithm

```python
def calculate_similarity_score(org1: Organization, org2: Organization) -> float:
    """
    Multi-factor organizational similarity calculation

    Returns: float between 0.0 and 1.0
    """
    score = 0.0

    # Industry match (30% weight)
    if org1.industry == org2.industry:
        score += 0.30
    elif is_related_industry(org1.industry, org2.industry):
        score += 0.15  # Partial credit for related industries

    # Size similarity (25% weight)
    size_ratio = min(org1.employee_count, org2.employee_count) / \
                 max(org1.employee_count, org2.employee_count)
    score += 0.25 * size_ratio

    # Maturity level (20% weight)
    maturity_levels = 5  # 1-5 scale
    maturity_diff = abs(org1.maturity_level - org2.maturity_level)
    maturity_similarity = max(0, 1 - (maturity_diff / maturity_levels))
    score += 0.20 * maturity_similarity

    # Resource availability (15% weight)
    if org1.has_dedicated_team == org2.has_dedicated_team:
        score += 0.10
    if org1.budget_level == org2.budget_level:
        score += 0.05

    # Geographic region (10% weight)
    if org1.region == org2.region:
        score += 0.10
    elif org1.continent == org2.continent:
        score += 0.05

    return round(score, 2)

# Minimum threshold for "similar"
MIN_SIMILARITY = 0.5
```

### 3.2 Confidence Scoring Algorithm

```python
def calculate_prediction_confidence(
    pattern_frequency: float,
    pattern_variance: float,
    sample_size: int,
    data_recency_days: int
) -> float:
    """
    Calculate confidence score for a prediction

    Args:
        pattern_frequency: 0.0-1.0, how often pattern occurs
        pattern_variance: Standard deviation of timing
        sample_size: Number of similar organizations
        data_recency_days: Age of data in days

    Returns: float between 0.0 and 1.0
    """
    # Base confidence from frequency
    base_confidence = pattern_frequency

    # Variance penalty
    if pattern_variance > 0:
        mean_timing = get_mean_timing()  # From pattern data
        variance_penalty = min(pattern_variance / mean_timing, 0.5)
        base_confidence *= (1 - variance_penalty)

    # Sample size adjustment
    if sample_size >= 50:
        size_boost = 1.0
    elif sample_size >= 15:
        size_boost = 0.9
    elif sample_size >= 5:
        size_boost = 0.8
    else:
        size_boost = 0.6

    base_confidence *= size_boost

    # Recency adjustment
    if data_recency_days < 30:
        recency_factor = 1.0
    elif data_recency_days < 90:
        recency_factor = 0.95
    elif data_recency_days < 180:
        recency_factor = 0.90
    else:
        recency_factor = 0.85

    final_confidence = base_confidence * recency_factor

    return round(min(final_confidence, 1.0), 2)
```

### 3.3 Pattern Extraction Algorithm

```python
def extract_milestone_patterns(similar_cases: List[WorkflowCase]) -> Dict:
    """
    Extract milestone patterns from similar cases

    Returns: Pattern dictionary with frequencies and statistics
    """
    patterns = defaultdict(lambda: {
        'occurrences': [],
        'durations': [],
        'gaps_from_previous': []
    })

    for case in similar_cases:
        milestones = sorted(case.milestones, key=lambda m: m.start_date)

        for i, milestone in enumerate(milestones):
            pattern_key = milestone.type

            # Record occurrence
            patterns[pattern_key]['occurrences'].append(case.id)

            # Record duration
            if milestone.end_date:
                duration = (milestone.end_date - milestone.start_date).days
                patterns[pattern_key]['durations'].append(duration)

            # Record gap from previous milestone
            if i > 0:
                gap = (milestone.start_date - milestones[i-1].end_date).days
                patterns[pattern_key]['gaps_from_previous'].append(gap)

    # Calculate statistics
    for pattern_key, data in patterns.items():
        data['frequency'] = len(data['occurrences']) / len(similar_cases)
        data['avg_duration'] = statistics.mean(data['durations']) if data['durations'] else None
        data['std_duration'] = statistics.stdev(data['durations']) if len(data['durations']) > 1 else 0
        data['avg_gap'] = statistics.mean(data['gaps_from_previous']) if data['gaps_from_previous'] else None
        data['std_gap'] = statistics.stdev(data['gaps_from_previous']) if len(data['gaps_from_previous']) > 1 else 0

    return dict(patterns)
```

## 4. Event Integration

### 4.1 Published Events

| Event Type | Trigger | Payload |
|-----------|---------|---------|
| `prediction.forecast_generated` | Journey prediction created | `{org_id, horizon_days, milestones[], confidence}` |
| `prediction.certification_predicted` | Certification forecast | `{org_id, predicted_date, success_probability}` |
| `prediction.demand_forecast_updated` | Demand forecast generated | `{specialty, expected_projects, peak_week}` |
| `prediction.confidence_low` | Confidence < 0.7 | `{prediction_id, confidence, reason}` |
| `prediction.milestone_approaching` | Milestone within 7 days | `{org_id, milestone, days_until}` |
| `prediction.daily_digest_sent` | Daily digest delivered | `{org_id, recommendations_count}` |
| `prediction.pattern_updated` | New pattern learned | `{pattern_type, confidence_delta}` |
| `prediction.accuracy_tracked` | Prediction validated | `{predicted_date, actual_date, error_days}` |

### 4.2 Subscribed Events

| Event Type | Handler | Action |
|-----------|---------|--------|
| `workflow.completed` | `on_workflow_completed()` | Update case library, re-analyze patterns |
| `bia.completed` | `on_bia_completed()` | Trigger journey prediction |
| `risk.completed` | `on_risk_completed()` | Update milestone patterns |
| `case.approved` | `on_case_approved()` | Add to similar case pool |
| `organization.profile_updated` | `on_profile_updated()` | Re-calculate similarity matches |

## 5. Performance Specifications

### 5.1 Response Time Targets

| Endpoint | Target | Acceptable | Method |
|----------|--------|------------|--------|
| Journey prediction | <2s | <5s | Caching, indexed queries |
| Certification forecast | <1s | <3s | Pre-computed patterns |
| Similar orgs lookup | <1s | <2s | Database indexes |
| Demand forecast | <1s | <3s | Aggregation caching |
| Daily digest generation | <5s/100 users | <10s/100 users | Batch processing |

### 5.2 Scalability Targets

- **Concurrent Predictions**: 100+ simultaneous requests
- **Organizations Supported**: 10,000+
- **Predictions per Hour**: 1,000+
- **Daily Digest Capacity**: 10,000+ users
- **Case Library Size**: 100,000+ historical cases

### 5.3 Caching Strategy

```python
# Cache configuration
CACHE_CONFIG = {
    'journey_prediction': {
        'ttl': 86400,  # 24 hours
        'key_pattern': 'prediction:journey:{org_id}:{horizon}',
        'invalidation': ['workflow.completed', 'case.approved']
    },
    'certification_forecast': {
        'ttl': 604800,  # 7 days
        'key_pattern': 'prediction:cert:{org_id}',
        'invalidation': ['workflow.completed']
    },
    'similar_organizations': {
        'ttl': 86400,  # 24 hours
        'key_pattern': 'similar:{org_id}',
        'invalidation': ['organization.profile_updated']
    },
    'demand_forecast': {
        'ttl': 3600,  # 1 hour
        'key_pattern': 'demand:{specialty}:{days}',
        'invalidation': ['prediction.forecast_generated']
    }
}
```

## 6. Security

### 6.1 Authentication

- Bearer token authentication (JWT)
- Organization-scoped access control
- Service-to-service authentication for internal APIs

### 6.2 Data Privacy

```python
# Anonymization for similar case exposure
def anonymize_case_data(case: WorkflowCase) -> Dict:
    """Remove PII from case data before exposure"""
    return {
        'industry': case.industry,
        'size_range': get_size_range(case.employee_count),  # e.g., "100-500"
        'region': case.region,
        'milestones': [
            {
                'type': m.type,
                'duration_days': m.duration_days,
                'success': m.success
            }
            for m in case.milestones
        ],
        # Exclude: organization name, contact info, specific dates
    }
```

### 6.3 Rate Limiting

```python
RATE_LIMITS = {
    '/api/v1/predictions/journey': '100/hour',
    '/api/v1/predictions/certification': '100/hour',
    '/api/v1/predictions/recommendations': '1000/hour',
    '/api/v1/predictions/expert-demand': '20/hour'
}
```

## 7. Error Handling

### 7.1 Error Codes

| Code | Error | Response | Retry |
|------|-------|----------|-------|
| 404 | Organization not found | `{error: "Organization not found"}` | No |
| 422 | Insufficient data for prediction | `{error: "Need at least 3 similar orgs"}` | Yes, later |
| 500 | Case library unavailable | `{error: "Service temporarily unavailable"}` | Yes |
| 503 | Database connection failed | `{error: "Database unavailable"}` | Yes |

### 7.2 Graceful Degradation

```python
# If case library unavailable, return basic prediction
if not case_library_available():
    return {
        'prediction_type': 'basic',
        'confidence': 0.3,
        'message': 'Limited prediction based on default patterns',
        'milestones': get_default_milestone_sequence()
    }
```

## 8. Monitoring

### 8.1 Health Checks

```python
@app.get("/health")
async def health_check():
    """
    Comprehensive health check
    """
    checks = {
        'database': await check_database_connection(),
        'case_library': await check_case_library(),
        'eventbus': await check_eventbus(),
        'scheduler': check_scheduler_running()
    }

    status = 'healthy' if all(checks.values()) else 'degraded'

    return {
        'status': status,
        'checks': checks,
        'timestamp': datetime.utcnow().isoformat()
    }
```

### 8.2 Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics definitions
predictions_total = Counter(
    'predictive_predictions_total',
    'Total predictions generated',
    ['prediction_type', 'status']
)

prediction_latency = Histogram(
    'predictive_prediction_latency_seconds',
    'Prediction generation latency',
    ['prediction_type']
)

confidence_scores = Histogram(
    'predictive_confidence_scores',
    'Distribution of confidence scores',
    buckets=[0.3, 0.5, 0.7, 0.8, 0.9, 1.0]
)

similar_orgs_found = Gauge(
    'predictive_similar_orgs_count',
    'Number of similar organizations found',
    ['org_id']
)

daily_digests_sent = Counter(
    'predictive_daily_digests_sent_total',
    'Total daily digests sent'
)
```

## 9. Testing

### 9.1 Test Coverage Requirements

- Unit tests: >80% coverage
- Integration tests: All API endpoints
- Performance tests: Load testing for 100 concurrent users
- Accuracy tests: Validate predictions against historical data

### 9.2 Test Data

```python
# Test organizations with known journeys
TEST_ORGANIZATIONS = [
    {
        'id': 'test-org-1',
        'industry': 'healthcare',
        'size': 250,
        'maturity': 2,
        'completed_milestones': ['bia', 'risk'],
        'expected_next': 'planning'
    },
    # ... more test cases
]
```

## 10. Deployment

### 10.1 Environment Variables

```bash
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
REDIS_URL=redis://localhost:6379

# Optional
ENABLE_DAILY_DIGESTS=true
DAILY_DIGEST_HOUR=8
MIN_SIMILAR_ORGS=3
TARGET_SIMILAR_ORGS=50
MIN_CONFIDENCE=0.7
MIN_PATTERN_FREQUENCY=0.30
CACHE_TTL_HOURS=24
LOG_LEVEL=INFO
```

### 10.2 Resource Requirements

```yaml
# Kubernetes deployment
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"

replicas: 2
autoscaling:
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

## 11. Future Enhancements

### 11.1 Planned Features

1. **ML Model Integration**: Replace statistical heuristics with trained models
2. **Real-time WebSocket Notifications**: Live prediction updates
3. **Explainable AI**: Detailed reasoning chains for predictions
4. **Federated Learning**: Cross-tenant pattern sharing with privacy preservation
5. **Causal Inference**: Identify causal relationships beyond correlation

### 11.2 Research Areas

- LSTM networks for time series forecasting
- Transformer models for pattern recognition
- Ensemble methods for confidence boosting
- Differential privacy techniques for data sharing

---

**Document Control**
- Version: 1.0.0
- Author: AI Platform Team
- Review Date: 2025-10-09
- Next Review: 2026-01-09
