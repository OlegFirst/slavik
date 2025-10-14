# Event Intelligence

## Overview
Event Intelligence is an AI-powered layer that provides intelligent analysis, learning, and prediction capabilities for event-driven architecture. It analyzes event patterns, learns from historical data, predicts future gaps, and accumulates knowledge to continuously improve the event-based system.

## Features
- **Event Analysis**: Deep analysis of events and patterns with importance scoring
- **ML-Powered Learning**: Learns from historical event data and developer feedback
- **Gap Prediction**: Predicts missing event handlers and publishers using machine learning
- **Knowledge Base**: Accumulates and retrieves event-related knowledge
- **Pattern Detection**: Identifies common event patterns and anti-patterns
- **AI-Powered Recommendations**: Generates actionable insights based on event analysis
- **Real-time Feedback Loop**: Records developer decisions and outcomes for continuous improvement

## Architecture

### Key Components

#### EventAnalyzer (`analyzer.py`)
- Analyzes individual events and entire domains
- Calculates importance scores (0-1 scale)
- Determines usage patterns (critical, frequent, rare, unused)
- Generates AI-powered recommendations
- Provides insights based on event characteristics

#### EventLearner (`learner.py`)
- Records AI suggestions and tracks outcomes
- Learns from developer feedback (approved/rejected/postponed)
- Generates learning reports and statistics
- Implements feedback loop for model improvement

#### EventPredictor (`predictor.py`)
- Predicts missing event handlers and publishers
- Uses ML models to identify potential gaps
- Provides confidence scores for predictions
- Integrates with ai-foundation ML models

#### EventKnowledgeBase (`knowledge_base.py`)
- Stores event analysis results
- Retrieves similar events
- Identifies relevant patterns
- Maintains learning statistics

## API Endpoints

### Health Check
```http
GET /event-intelligence/health
```
Returns health status of all Event Intelligence components.

### Event Analysis
```http
POST /event-intelligence/analyze
Content-Type: application/json

{
  "event_name": "user.registered",
  "publishers": ["auth-service", "user-service"],
  "subscribers": ["email-service", "analytics-service"],
  "historical_data": {}
}
```

Returns importance score, usage pattern, recommendations, and AI insights.

### Domain Analysis
```http
POST /event-intelligence/analyze/domain?domain=authentication
Content-Type: application/json

[
  {"event_name": "user.login", "publishers": [...], "subscribers": [...]},
  {"event_name": "user.logout", "publishers": [...], "subscribers": [...]}
]
```

Returns aggregated statistics and health metrics for all events in domain.

### Learning Endpoints

#### Record Suggestion
```http
POST /event-intelligence/learning/suggest
Content-Type: application/json

{
  "event_name": "order.created",
  "suggested_action": "implement",
  "confidence": 0.85
}
```

Records a suggestion for tracking and learning.

#### Record Feedback
```http
POST /event-intelligence/learning/feedback
Content-Type: application/json

{
  "suggestion_id": "uuid",
  "developer_decision": "approved",
  "outcome": "success"
}
```

Records developer feedback on suggestions.

#### Get Learning Statistics
```http
GET /event-intelligence/learning/stats
```

Returns learning statistics and metrics.

#### Export Learning Report
```http
GET /event-intelligence/learning/report
```

Exports comprehensive learning report.

### Prediction Endpoints

#### Predict Event Gaps
```http
POST /event-intelligence/predict/gaps
Content-Type: application/json

{
  "current_events": {
    "user.registered": {
      "publishers": ["auth-service"],
      "subscribers": ["email-service"]
    }
  },
  "context": {}
}
```

Predicts missing event handlers and publishers.

### Knowledge Base Endpoints

#### Find Similar Events
```http
GET /event-intelligence/knowledge/similar/user.registered?limit=5
```

Returns similar events from knowledge base.

#### Get Relevant Patterns
```http
GET /event-intelligence/knowledge/patterns/user.registered?limit=3
```

Returns relevant patterns for specified event.

#### Knowledge Statistics
```http
GET /event-intelligence/knowledge/stats
```

Returns knowledge base statistics.

## Configuration

```python
# No dedicated config file - integrates with main service config
# Uses:
# - tools/event_intelligence (for event scanning)
# - ai-foundation (for ML models)
# - Other AI services integration

# Dependencies
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")  # For AI insights
DATABASE_URL = os.getenv("DATABASE_URL")  # For persistence
REDIS_URL = os.getenv("REDIS_URL")  # For caching
```

## Quick Start

### Standalone Testing
```bash
# Set PYTHONPATH
export PYTHONPATH=/Users/MD/AI-Platform-ISO

# Import and use
python3 -c "
from intelligent_core.event_intelligence import EventAnalyzer
analyzer = EventAnalyzer()
print('Event Intelligence Ready')
"
```

### Integration with Main Service
Event Intelligence is typically integrated into the main intelligent-core service:

```python
from intelligent_core.event_intelligence.api import router, initialize_event_intelligence

# In FastAPI app
app.include_router(router, prefix="/api/v1")

# On startup
@app.on_event("startup")
async def startup():
    await initialize_event_intelligence()
```

## Dependencies

### Core Dependencies
- FastAPI (API framework)
- Pydantic (data validation)
- Python 3.9+ (async support)

### AI/ML Dependencies
- anthropic (AI insights)
- scikit-learn (ML models via ai-foundation)
- numpy (numerical operations)

### Integration Dependencies
- ai-foundation (ML models and embeddings)
- tools/event_intelligence (event scanning)
- Database (PostgreSQL/Supabase)
- Redis (caching)

## Testing

```bash
# Unit tests (when available)
pytest intelligent-core/event_intelligence/tests/

# Integration tests
pytest tests/integration/test_event_intelligence.py

# Manual API testing
curl http://localhost:8000/api/v1/event-intelligence/health
```

## Integration

### From Other Services

#### Python Services
```python
import httpx

async def analyze_event(event_name: str, publishers: list, subscribers: list):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/event-intelligence/analyze",
            json={
                "event_name": event_name,
                "publishers": publishers,
                "subscribers": subscribers
            }
        )
        return response.json()
```

#### Event-Based Integration
Event Intelligence automatically analyzes events published through the platform's event bus and provides proactive recommendations.

### Direct Python Import
```python
from intelligent_core.event_intelligence import (
    EventAnalyzer,
    EventLearner,
    EventPredictor,
    EventKnowledgeBase
)

# Initialize components
analyzer = EventAnalyzer()
learner = EventLearner()
predictor = EventPredictor()
knowledge_base = EventKnowledgeBase()

# Use directly
analysis = await analyzer.analyze_event(
    event_name="user.registered",
    publishers=["auth-service"],
    subscribers=["email-service", "analytics-service"]
)
```

## Workflow

1. **Event Scanning**: Tools scan codebase for events
2. **Analysis**: EventAnalyzer analyzes patterns and importance
3. **Learning**: EventLearner records suggestions and feedback
4. **Prediction**: EventPredictor identifies gaps
5. **Knowledge**: Results stored in knowledge base
6. **Recommendations**: AI generates actionable insights
7. **Feedback Loop**: Developer decisions improve future predictions

## Status

**Current Implementation: 90%**

### Completed ✅
- Event analysis with importance scoring
- Learning from feedback loop
- Gap prediction framework
- Knowledge base foundation
- API endpoints structure
- Integration with ai-foundation

### In Progress 🚧
- Advanced ML model training
- Historical data analysis
- Pattern library expansion

### Planned 📋
- Real-time event monitoring dashboard
- Automated event documentation
- Cross-domain pattern detection
- Multi-language event scanning
