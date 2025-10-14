# Planning Service - Business Continuity Strategy

**Service:** `planning_service`
**Port:** `8011`
**ISO 22301:** Clause 8.3
**BCI Practice:** PP4 (Solutions Design)

## Overview

Planning Service manages business continuity strategy development, cost-benefit analysis, and strategy approval workflows. This service implements ISO 22301 Clause 8.3 requirements for determining and selecting business continuity strategies.

## Architecture

```
planning_service/
├── config.py                   # Configuration
├── main.py                     # FastAPI app
├── database.py                 # Database connection
├── dependencies.py             # Dependency injection
├── models/
│   ├── domain.py              # Pydantic models
│   └── database.py            # SQLAlchemy models
├── api/
│   └── routes.py              # API endpoints
├── services/
│   └── business_logic.py      # Business logic
├── repositories/
│   └── repository.py          # Data access layer
├── events/
│   └── publishers.py          # Event publishing
└── requirements.txt
```

## Features

### Strategy Management
- Create, read, update, delete strategies
- Strategy classification (recovery, resilience, prevention, etc.)
- Multi-phase support (pre-incident, during-incident, post-incident)
- Strategy lifecycle workflow (draft → review → approved → implemented)

### Cost-Benefit Analysis
- Comprehensive cost breakdown (CAPEX, OPEX, training, maintenance)
- Quantitative and qualitative benefits tracking
- ROI calculation with NPV
- Payback period analysis
- Automated recommendations

### Resource Planning
- Resource requirement identification
- Resource gap analysis
- Availability assessment
- Criticality classification

### Integration
- Links to BIA Service (bia analysis results)
- Links to Risk Service (risk assessments)
- Event publishing to EventBus
- Registration with Orchestrator

## API Endpoints

### Strategy Management

#### `POST /api/strategies`
Create new strategy

**Request:**
```json
{
  "tenant_id": "tenant-001",
  "name": "Data Center Failover Strategy",
  "description": "Automated failover to backup datacenter",
  "strategy_type": "recovery",
  "strategy_phase": "during_incident",
  "objective": "Ensure <4h RTO for critical systems",
  "scope": ["IT Systems", "Core Banking"],
  "risk_mitigation": ["Datacenter Failure", "Network Outage"]
}
```

#### `GET /api/strategies`
List strategies with filters

**Query Parameters:**
- `tenant_id` (required)
- `status` (optional): draft, review, approved, implemented
- `strategy_type` (optional)
- `skip`, `limit` (pagination)

#### `GET /api/strategies/{strategy_id}`
Get strategy details

#### `PUT /api/strategies/{strategy_id}`
Update strategy (only draft status)

#### `DELETE /api/strategies/{strategy_id}`
Archive strategy (soft delete)

### Cost-Benefit Analysis

#### `POST /api/strategies/{strategy_id}/cost-benefit`
Calculate cost-benefit analysis

**Request:**
```json
{
  "cost_breakdown": {
    "capex": 500000,
    "opex": 100000,
    "training": 50000,
    "maintenance": 75000,
    "other": 25000,
    "currency": "USD"
  },
  "expected_benefits": {
    "quantitative_benefits": {
      "downtime_savings": 2000000,
      "productivity_gains": 500000,
      "risk_reduction": 300000
    },
    "qualitative_benefits": [
      "Improved customer confidence",
      "Regulatory compliance",
      "Brand protection"
    ],
    "risk_reduction_percentage": 85.0,
    "downtime_reduction_hours": 72.0
  },
  "implementation_years": 3,
  "discount_rate": 0.1
}
```

**Response:**
```json
{
  "strategy_id": "uuid",
  "total_cost": 750000,
  "total_benefits": 2800000,
  "cost_benefit_ratio": 3.73,
  "roi_analysis": {
    "total_investment": 750000,
    "annual_savings": 933333,
    "payback_period_months": 9.64,
    "roi_percentage": 273.33,
    "net_present_value": 1578954
  },
  "recommendation": "proceed",
  "confidence_level": "high"
}
```

### Approval Workflow

#### `POST /api/strategies/{strategy_id}/submit-review`
Submit strategy for review (DRAFT → REVIEW)

#### `POST /api/strategies/{strategy_id}/approve`
Approve strategy (REVIEW → APPROVED)

## Database Schema

### Strategy Table (`planning.strategies`)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | VARCHAR(100) | Tenant identifier |
| strategy_number | VARCHAR(50) | Unique strategy number (STRAT-2025-XXXXXX) |
| name | VARCHAR(255) | Strategy name |
| description | TEXT | Strategy description |
| strategy_type | ENUM | recovery, resilience, prevention, etc. |
| strategy_phase | ENUM | pre_incident, during_incident, post_incident |
| status | ENUM | draft, review, approved, implemented, archived |
| objective | TEXT | Strategy objective |
| scope | JSON | Business units/processes covered |
| risk_mitigation | JSON | Risks addressed |
| estimated_cost | FLOAT | Total estimated cost |
| cost_breakdown | JSON | Cost breakdown details |
| expected_benefits | JSON | Benefit analysis |
| roi_analysis | JSON | ROI calculations |
| cost_benefit_ratio | FLOAT | Calculated ratio |
| resource_requirements | JSON | Required resources |
| resource_gaps | JSON | Identified gaps |
| implementation_phases | JSON | Implementation timeline |
| dependencies | JSON | Dependencies |
| success_criteria | JSON | Success metrics |
| linked_bia_ids | JSON | Links to BIA service |
| linked_risk_ids | JSON | Links to Risk service |
| submitted_for_review_at | TIMESTAMP | When submitted for review |
| reviewed_by | VARCHAR(255) | Reviewer user ID |
| reviewed_at | TIMESTAMP | Review timestamp |
| approved_by | VARCHAR(255) | Approver user ID |
| approved_at | TIMESTAMP | Approval timestamp |
| created_by | VARCHAR(255) | Creator user ID |
| created_at | TIMESTAMP | Creation timestamp |
| updated_by | VARCHAR(255) | Last updater user ID |
| updated_at | TIMESTAMP | Last update timestamp |
| active | BOOLEAN | Soft delete flag |

## Events Published

### `planning.strategy.created`
```json
{
  "strategy_id": "uuid",
  "tenant_id": "tenant-001",
  "strategy_type": "recovery",
  "created_by": "user-123"
}
```

### `planning.strategy.approved`
```json
{
  "strategy_id": "uuid",
  "tenant_id": "tenant-001",
  "approved_by": "user-456",
  "cost_benefit_ratio": 3.73
}
```

### `planning.cost_benefit.completed`
```json
{
  "strategy_id": "uuid",
  "tenant_id": "tenant-001",
  "recommendation": "proceed",
  "roi_percentage": 273.33
}
```

## Running the Service

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://bcm:bcm@localhost:5432/bcm"
export EVENTBUS_URL="http://localhost:8001"
export ORCHESTRATOR_URL="http://localhost:8002"

# Run service
python -m planning_service.main
```

### Docker

```bash
docker build -t planning_service .
docker run -p 8011:8011 planning_service
```

## Configuration

See `config.py` for all configuration options:

- `SERVICE_PORT`: Service port (default: 8011)
- `DATABASE_URL`: PostgreSQL connection string
- `EVENTBUS_URL`: EventBus service URL
- `ORCHESTRATOR_URL`: Orchestrator service URL
- `BIA_SERVICE_URL`: BIA service URL for integration
- `RISK_SERVICE_URL`: Risk service URL for integration

## ISO 22301 Compliance

### Clause 8.3 - Business Continuity Strategies

**Requirements Met:**
- ✅ Strategy identification and selection
- ✅ Cost-benefit analysis
- ✅ Resource requirement identification
- ✅ Strategy documentation
- ✅ Approval workflow
- ✅ Link to BIA results
- ✅ Link to risk assessments

**Evidence Generated:**
- Strategy documents with objectives and scope
- Cost-benefit analysis reports
- Resource requirement documentation
- Approval records with timestamps

## Integration Examples

### Creating Strategy from BIA Results

```python
import httpx

# Get BIA results
bia_response = await client.get(f"{BIA_SERVICE_URL}/analyses/{bia_id}")
bia_data = bia_response.json()

# Create strategy based on BIA
strategy_data = {
    "tenant_id": bia_data["tenant_id"],
    "name": f"Recovery Strategy for {bia_data['process_name']}",
    "strategy_type": "recovery",
    "objective": f"Meet RTO of {bia_data['rto_hours']} hours",
    "scope": [bia_data["process_name"]],
    "linked_bia_ids": [bia_id]
}

strategy_response = await client.post(
    f"{PLANNING_SERVICE_URL}/api/strategies",
    json=strategy_data,
    params={"created_by": "user-123"}
)
```

## Testing

```bash
# Run tests
pytest

# Test coverage
pytest --cov=planning_service
```

## License

Internal - Company Use Only
