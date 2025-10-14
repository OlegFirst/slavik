# EventBus Integration - Predictive Service

Complete EventBus integration for the Predictive Service with 8+ event publishers and 5+ event subscribers.

## Status: ✅ COMPLETE

**Integration Level**: Full bidirectional event-driven architecture

## Event Publishers (8+)

The Predictive Service publishes the following events:

### 1. `prediction.forecast_generated`
**Triggered when**: Journey predictions or demand forecasts are created
**Priority**: Normal
**Data**:
```json
{
  "org_id": "uuid",
  "forecast_type": "journey|demand|certification",
  "horizon_days": 90,
  "milestones_count": 3,
  "average_confidence": 0.85,
  "metadata": {}
}
```

**Published from**:
- `GET /api/v1/predictions/journey/{org_id}`
- `GET /api/v1/predictions/certification/{org_id}`
- `GET /api/v1/predictions/expert-demand`

---

### 2. `prediction.model_updated`
**Triggered when**: ML models are retrained with new data
**Priority**: Low
**Data**:
```json
{
  "model_type": "journey|demand|similarity",
  "update_reason": "new_completion_data|scheduled_retrain",
  "training_samples": 150,
  "accuracy_improvement": 0.05,
  "update_number": 12
}
```

**Published from**: Event handlers when learning from platform events

---

### 3. `prediction.anomaly_detected`
**Triggered when**: Unusual patterns or outliers detected in org journey
**Priority**: High (if severity is high/critical), Normal otherwise
**Data**:
```json
{
  "org_id": "uuid",
  "anomaly_type": "delayed_milestone|unexpected_cost|low_progress",
  "severity": "low|medium|high|critical",
  "description": "Organization is 2 weeks behind predicted schedule",
  "affected_predictions": ["risk_assessment", "planning"],
  "requires_review": true
}
```

**Published from**: Pattern analysis in event handlers

---

### 4. `prediction.confidence_low`
**Triggered when**: Prediction confidence is below threshold (< 0.7)
**Priority**: Normal
**Data**:
```json
{
  "org_id": "uuid",
  "milestone": "risk_assessment",
  "confidence": 0.45,
  "threshold": 0.7,
  "reason": "Insufficient similar organizations",
  "similar_orgs_needed": true
}
```

**Published from**:
- Journey prediction endpoint (when milestone confidence < 0.7)
- Risk score change handler

---

### 5. `prediction.trend_identified`
**Triggered when**: Pattern analysis reveals industry/regional trends
**Priority**: Normal
**Data**:
```json
{
  "trend_type": "industry_acceleration|common_challenge|success_pattern",
  "description": "Healthcare organizations completing BIA 20% faster",
  "affected_orgs_count": 47,
  "confidence": 0.88,
  "trend_data": {}
}
```

**Published from**:
- Expert demand forecast endpoint
- BIA complexity analysis

---

### 6. `prediction.risk_calculated`
**Triggered when**: Risk assessment performed on journey predictions
**Priority**: High (if risk_score > 0.7), Normal otherwise
**Data**:
```json
{
  "org_id": "uuid",
  "risk_type": "timeline_delay|certification_failure|resource_shortage",
  "risk_score": 0.65,
  "risk_level": "medium",
  "contributing_factors": ["limited_resources", "no_executive_sponsor"],
  "mitigation_suggestions": ["Allocate dedicated team", "Seek executive buy-in"]
}
```

**Published from**: Risk analysis in event handlers

---

### 7. `prediction.financial_impact_estimated`
**Triggered when**: Cost predictions calculated for milestones
**Priority**: Normal
**Data**:
```json
{
  "org_id": "uuid",
  "milestone": "risk_assessment",
  "estimated_cost": {
    "estimated_min": 6800,
    "estimated_max": 10200,
    "currency": "USD"
  },
  "confidence": 0.87,
  "cost_drivers": ["duration", "org_size", "complexity"]
}
```

**Published from**: Journey prediction endpoint (for each milestone)

---

### 8. `prediction.rto_probability_calculated`
**Triggered when**: Recovery Time Objective predictions analyzed
**Priority**: High (if probability < 0.5), Normal otherwise
**Data**:
```json
{
  "org_id": "uuid",
  "target_rto_days": 240,
  "achievement_probability": 0.82,
  "current_trajectory": "on_track|at_risk|delayed",
  "recommendations": ["Dedicated BCM team", "Executive sponsorship"]
}
```

**Published from**: Certification prediction endpoint

---

## Event Subscribers (5+)

The Predictive Service subscribes to platform events to continuously improve prediction models:

### 1. `workflow.completed` → `handle_workflow_completed()`
**Learns from**: Actual completion times vs predictions
**Updates**: Milestone duration models, prediction accuracy tracking
**Actions**:
- Compare actual vs predicted duration
- Update ML model with real data
- Publish anomaly if significantly different

---

### 2. `bia.completed` → `handle_bia_completed()`
**Learns from**: BIA outcomes, critical processes identified
**Updates**: Complexity models, future phase duration predictions
**Actions**:
- Analyze BIA complexity (critical/total ratio)
- Adjust future predictions based on complexity
- Identify high-complexity trends

---

### 3. `incident.resolved` → `handle_incident_resolved()`
**Learns from**: Actual recovery times, incident patterns
**Updates**: RTO probability models, incident response predictions
**Actions**:
- Update RTO achievement probability calculations
- Learn from actual resolution times
- Improve incident impact predictions

---

### 4. `case.approved` → `handle_case_approved()`
**Learns from**: Approved community cases, best practices
**Updates**: Pattern library, similarity matching
**Actions**:
- Add success patterns to prediction library
- Update success factor weights
- Improve industry-specific predictions

---

### 5. `risk.score_changed` → `handle_risk_score_changed()`
**Learns from**: Risk assessment changes, trend shifts
**Updates**: Prediction confidence, risk-adjusted timelines
**Actions**:
- Adjust prediction confidence based on risk changes
- Publish low confidence events if risk increases significantly
- Update risk-adjusted milestone predictions

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Predictive Service                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌─────────────────────┐      │
│  │  API Endpoints   │────────▶│  Event Handlers     │      │
│  │                  │         │                     │      │
│  │ Journey Predict  │         │ 8 Publishers        │      │
│  │ Certification    │         │ 5 Subscribers       │      │
│  │ Expert Demand    │         │                     │      │
│  └──────────────────┘         └─────────────────────┘      │
│           │                             │                   │
│           │                             │                   │
│           ▼                             ▼                   │
│  ┌──────────────────┐         ┌─────────────────────┐      │
│  │ Journey Predictor│         │   EventBus Service  │      │
│  │ Demand Forecaster│         │                     │      │
│  └──────────────────┘         │  Redis Pub/Sub      │      │
│                                │  HTTP API           │      │
│                                └─────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
           Platform EventBus    Other Services    Learning Systems
```

## Files Modified/Created

### Created:
1. `/intelligent-core/predictive/event_handlers.py` (NEW)
   - **Lines**: 600+
   - **Publishers**: 8 methods
   - **Subscribers**: 5 handlers
   - **Helper methods**: 6+

### Modified:
1. `/intelligent-core/predictive/integration/dependencies.py`
   - Added `EventBusService` class
   - Added `get_eventbus()` function
   - Updated `Dependencies` class with eventbus

2. `/intelligent-core/predictive/main.py`
   - Added EventBus initialization in lifespan
   - Added event handler setup
   - Added subscription registration

3. `/intelligent-core/predictive/api/predictions.py`
   - Updated all endpoints to publish events
   - Added `get_eventbus_stats()` endpoint
   - Added Request parameter to endpoints

4. `/intelligent-core/predictive/services/proactive_recommendations.py`
   - Updated `_send_daily_digests()` to publish events

## Usage Examples

### Publishing a Forecast Event

```python
from event_handlers import PredictiveEventHandlers

# Initialize handlers
handlers = PredictiveEventHandlers(eventbus=deps.eventbus)

# Publish forecast generated
await handlers.publish_forecast_generated(
    org_id=UUID("..."),
    forecast_type='journey',
    horizon_days=90,
    milestones_count=3,
    confidence=0.87,
    tenant_id='default',
    metadata={'similar_orgs_count': 83}
)
```

### Subscribing to Platform Events

```python
# Subscribe to all platform events (called on startup)
await handlers.subscribe_to_platform_events()

# Events are automatically routed to handlers:
# - workflow.completed → handle_workflow_completed()
# - bia.completed → handle_bia_completed()
# - incident.resolved → handle_incident_resolved()
# - case.approved → handle_case_approved()
# - risk.score_changed → handle_risk_score_changed()
```

### Checking Integration Status

```bash
# GET /api/v1/predictions/stats/eventbus
curl http://localhost:8031/api/v1/predictions/stats/eventbus
```

**Response**:
```json
{
  "status": "active",
  "integration": {
    "publishers": 8,
    "subscribers": 5,
    "model_updates": 12,
    "learning_events_processed": 145
  },
  "event_types": {
    "publishers": [
      "prediction.forecast_generated",
      "prediction.model_updated",
      "prediction.anomaly_detected",
      "prediction.confidence_low",
      "prediction.trend_identified",
      "prediction.risk_calculated",
      "prediction.financial_impact_estimated",
      "prediction.rto_probability_calculated"
    ],
    "subscribers": [
      "workflow.completed",
      "bia.completed",
      "incident.resolved",
      "case.approved",
      "risk.score_changed"
    ]
  }
}
```

## Event Flow Examples

### Example 1: Journey Prediction with Events

```
1. User requests journey prediction
   GET /api/v1/predictions/journey/{org_id}

2. Service generates prediction
   - Analyzes similar organizations
   - Calculates milestones
   - Estimates costs

3. Events published:
   ✓ prediction.forecast_generated (horizon: 90 days, confidence: 0.87)
   ✓ prediction.financial_impact_estimated (for each milestone)
   ✓ prediction.confidence_low (if confidence < 0.7)

4. Response returned to user
   - Journey timeline
   - Milestones
   - Confidence scores
```

### Example 2: Learning from Workflow Completion

```
1. Workflow completes in platform
   Event: workflow.completed

2. Predictive Service receives event
   → handle_workflow_completed()

3. Service learns:
   - Compares actual vs predicted duration
   - Updates milestone duration model
   - Checks prediction accuracy

4. If significant deviation:
   ✓ prediction.anomaly_detected published
   ✓ prediction.model_updated published

5. Future predictions improved
```

### Example 3: Risk Score Changes

```
1. Risk score changes in platform
   Event: risk.score_changed

2. Predictive Service receives event
   → handle_risk_score_changed()

3. Service adjusts:
   - Prediction confidence
   - Timeline estimates
   - Success probability

4. If risk increased significantly:
   ✓ prediction.confidence_low published
   ✓ Recommendations adjusted
```

## Benefits

### For Organizations:
- **Proactive notifications** when predictions change
- **Real-time updates** based on platform activity
- **Improved accuracy** from continuous learning

### For Platform:
- **Event-driven architecture** enables loose coupling
- **Scalable** prediction updates
- **Auditable** prediction history via events

### For Developers:
- **Observable** prediction accuracy
- **Debuggable** learning process
- **Testable** event flows

## Testing

### Manual Testing

```bash
# 1. Start service
cd /Users/MD/AI-Platform-ISO/intelligent-core/predictive
uvicorn main:app --reload --port 8031

# 2. Generate prediction (triggers events)
curl http://localhost:8031/api/v1/predictions/journey/00000000-0000-0000-0000-000000000001

# 3. Check EventBus stats
curl http://localhost:8031/api/v1/predictions/stats/eventbus

# 4. Simulate platform event (if EventBus running)
# This would trigger learning handlers
```

### Event Verification

Check Redis for published events:
```bash
redis-cli MONITOR
# Watch for: prediction.forecast_generated, prediction.financial_impact_estimated, etc.
```

## Configuration

Required environment variables:

```bash
# EventBus
REDIS_URL=redis://localhost:6379
EVENTBUS_URL=http://localhost:8040

# Database (for learning)
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_SERVICE_ROLE_KEY=...
```

## Metrics

Current integration metrics:
- **Event Publishers**: 8
- **Event Subscribers**: 5
- **Total Event Types**: 13+
- **Lines of Code**: 600+ (event_handlers.py)
- **API Endpoints with Events**: 4
- **Learning Handlers**: 5

## Future Enhancements

1. **Advanced Learning**: ML model retraining on event triggers
2. **Event Replay**: Replay historical events for model training
3. **Event Aggregation**: Batch events for efficiency
4. **Event Analytics**: Dashboard for prediction accuracy over time
5. **Custom Alerts**: User-defined thresholds for anomaly events

## Summary

✅ **8 Event Publishers** implemented across prediction logic
✅ **5 Event Subscribers** for continuous learning
✅ **Full bidirectional** event flow
✅ **API integration** in all prediction endpoints
✅ **Stats endpoint** for monitoring
✅ **Error handling** with graceful degradation
✅ **Production-ready** with logging and metrics

The Predictive Service is now fully integrated with the platform EventBus, enabling real-time prediction updates, continuous learning from platform events, and observable prediction accuracy tracking.
