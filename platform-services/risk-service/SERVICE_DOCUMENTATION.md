# Risk Management Service - Documentation

## Service Overview

**Service Name:** Risk Management Service
**ISO 22301 Clause:** 8.2.3 - Risk Assessment
**Port:** 8040
**Technology Stack:** FastAPI, SQLAlchemy, PostgreSQL, Workflow Intelligence

## Business Purpose

Implements ISO 22301:2019 Clause 8.2.3 requirements for comprehensive risk assessment and treatment:
- Identify and assess business continuity risks
- Perform qualitative risk analysis (5×5 risk matrix)
- Conduct quantitative risk analysis (FAIR methodology)
- Run Monte Carlo simulations for probability distributions
- Develop risk treatment plans
- Generate risk heat maps and reports

## Business Logic

### Core Capabilities

#### 1. Risk Assessment Matrix (5×5)
**Likelihood Scale (1-5):**
- 1 = RARE (< 5% probability)
- 2 = UNLIKELY (5-20% probability)
- 3 = POSSIBLE (20-50% probability)
- 4 = LIKELY (50-80% probability)
- 5 = ALMOST_CERTAIN (> 80% probability)

**Impact Scale (1-5):**
- 1 = INSIGNIFICANT (Minimal impact)
- 2 = MINOR (Minor impact)
- 3 = MODERATE (Moderate impact)
- 4 = MAJOR (Major impact)
- 5 = CATASTROPHIC (Catastrophic impact)

**Risk Score:** Likelihood × Impact (1-25)

**Severity Levels:**
- CRITICAL: Score ≥ 20
- HIGH: Score 15-19
- MEDIUM: Score 8-14
- LOW: Score < 8

#### 2. Risk Categories
- **Operational:** Process failures, system outages
- **Financial:** Revenue loss, cost overruns
- **Strategic:** Market shifts, competitive threats
- **Compliance:** Regulatory violations
- **Reputational:** Brand damage, customer trust
- **Cybersecurity:** Data breaches, ransomware
- **Natural Disaster:** Earthquakes, floods, pandemics

#### 3. FAIR Quantitative Analysis
**FAIR Methodology (Factor Analysis of Information Risk):**

```
Loss Event Frequency (LEF) = Threat Event Frequency × Vulnerability Score

Annual Loss Expectancy (ALE) = LEF × Average Loss Magnitude

Risk Rating = f(ALE) → low/medium/high/critical
```

**Inputs:**
- Threat Event Frequency: Events per year
- Vulnerability Score: 0-1 probability
- Primary Loss Range: Min, Max, Most Likely ($)
- Secondary Loss Range: Min, Max ($)

**Outputs:**
- Annual Loss Expectancy (ALE)
- Risk Rating (low/medium/high/critical)
- Confidence Intervals (95%, 99%)

#### 4. Monte Carlo Simulation
- Iterations: 1,000 to 100,000 (default 10,000)
- Probability Distribution Analysis
- Results:
  - Mean Loss
  - Median Loss
  - 95th Percentile Loss
  - 99th Percentile Loss (Value at Risk)

#### 5. Risk Treatment Strategies
- **AVOID:** Eliminate the risk (e.g., discontinue risky process)
- **MITIGATE:** Reduce likelihood/impact (controls, safeguards)
- **TRANSFER:** Shift to third party (insurance, outsourcing)
- **ACCEPT:** Accept residual risk with management approval

#### 6. Residual Risk Tracking
- Pre-Treatment: Inherent Risk Score
- Post-Treatment: Residual Risk Score
- Track risk reduction effectiveness
- Continuous monitoring

### Business Workflows

#### Risk Management Lifecycle
1. **IDENTIFIED:** Risk discovered and documented
2. **ANALYZING:** FAIR/Monte Carlo analysis in progress
3. **TREATED:** Treatment plan implemented
4. **MONITORING:** Ongoing tracking of residual risk
5. **CLOSED:** Risk no longer applicable

## API Endpoints (14 total)

### Risk CRUD (5 endpoints)
1. **POST /api/v1/risk/assessments** - Create Risk Assessment
2. **GET /api/v1/risk/assessments** - List Risks (filters: category, status, min_score)
3. **GET /api/v1/risk/assessments/{id}** - Get Risk Details
4. **PUT /api/v1/risk/assessments/{id}** - Update Risk
5. **DELETE /api/v1/risk/assessments/{id}** - Soft Delete Risk

### Risk Analysis (4 endpoints)
6. **POST /api/v1/risk/assessments/{id}/fair-analysis** - Perform FAIR Analysis
7. **GET /api/v1/risk/assessments/{id}/fair-analysis** - Get FAIR Results
8. **POST /api/v1/risk/assessments/{id}/monte-carlo** - Run Monte Carlo Simulation
9. **GET /api/v1/risk/assessments/{id}/monte-carlo** - Get Simulation Results

### Risk Treatment (2 endpoints)
10. **POST /api/v1/risk/assessments/{id}/treatment** - Create Treatment Plan
11. **GET /api/v1/risk/assessments/{id}/treatment** - Get Treatment Plan

### Reporting (3 endpoints)
12. **GET /api/v1/risk/reports/heat-map** - Risk Heat Map Data
13. **GET /api/v1/risk/reports/summary** - Risk Summary Report
14. **GET /api/v1/risk/reports/by-category** - Risks Grouped by Category

## Data Models

### Core: Risk
```python
{
  "id": UUID,
  "organization_id": UUID,
  "risk_title": str,
  "risk_code": str,
  "risk_category": "operational|financial|strategic|compliance|reputational|cybersecurity|natural_disaster",
  "description": str,
  "threat_source": str,
  "vulnerabilities": [str],

  # Analysis
  "likelihood": 1-5,
  "impact": 1-5,
  "inherent_risk_score": 1-25,

  # Treatment
  "treatment_strategy": "avoid|mitigate|transfer|accept",
  "residual_likelihood": 1-5,
  "residual_impact": 1-5,
  "residual_risk_score": 1-25,

  # Ownership
  "risk_owner_id": UUID,
  "related_processes": [...],
  "related_assets": [...],

  # Status
  "status": "identified|analyzing|treated|monitoring|closed",
  "last_reviewed_at": datetime,
  "next_review_date": datetime,

  "is_active": bool,
  "created_at": datetime,
  "updated_at": datetime
}
```

### FAIRAnalysis
```python
{
  "risk_id": UUID,
  "threat_event_frequency": float,  # Events/year
  "vulnerability_score": 0-1,
  "loss_event_frequency": float,  # TEF × VS

  "primary_loss_min": float,
  "primary_loss_max": float,
  "primary_loss_most_likely": float,
  "secondary_loss_min": float,
  "secondary_loss_max": float,

  "annual_loss_expectancy": float,  # ALE
  "risk_rating": "low|medium|high|critical",
  "confidence_interval_low": float,
  "confidence_interval_high": float,

  "analyzed_at": datetime,
  "analyzed_by": UUID
}
```

### MonteCarloSimulation
```python
{
  "risk_id": UUID,
  "iterations": 10000,  # 1K-100K
  "factors": [{factor_name, distribution, params}],

  "mean_loss": float,
  "median_loss": float,
  "percentile_95": float,  # VaR 95%
  "percentile_99": float,  # VaR 99%

  "simulated_at": datetime
}
```

### RiskTreatmentPlan
```python
{
  "risk_id": UUID,
  "treatment_strategy": "avoid|mitigate|transfer|accept",
  "controls": [...],  # Control measures
  "cost_estimate": float,
  "implementation_timeline": str,
  "target_residual_score": int,
  "status": "planned|in_progress|completed",
  "owner_id": UUID
}
```

## Dependencies

### From intelligent-core
- **workflow-intelligence:** PostgreSQL storage, workflow engine, audit logger, ISO compliance checker
- **shared/auth:** JWT authentication
- **shared/database:** Database connection management

### From infrastructure
- **Database:** PostgreSQL
- **Message Queue:** RabbitMQ (optional)
- **Monitoring:** Prometheus metrics

### Integration Points
- **BIA Service (8012):** Links risks to critical processes
- **Compliance Service (8013):** Maps risks to compliance requirements
- **Response Service:** Triggers incident response for realized risks

## Configuration

### Environment Variables
```bash
SERVICE_NAME=risk-management
PORT=8040
SERVICE_VERSION=1.0.0

DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/bcm_platform
JWT_SECRET=your-secret-key

CORS_ORIGINS=http://localhost:3000,http://localhost:5173
DEBUG=false
```

## Testing

**Test Files:**
- test_api.py - API endpoint tests
- test_business_logic.py - Business logic tests
- test_repository.py - Database tests
- test_auth.py - Authentication tests

**Coverage:** Moderate (pytest, pytest-asyncio)

## Security

### Authentication
- JWT Bearer Token required for all endpoints
- Organization isolation via organization_id from JWT

### Authorization
- Users can only access risks for their organization
- Risk owners have enhanced permissions

## Monitoring

### Prometheus Metrics
- Available at /metrics
- Workflow Intelligence metrics included

### Health Checks
- GET /health - Service health
- GET /api/compliance/check - ISO 22301 Clause 8.2.3 compliance

## Known Issues/TODO

1. **FAIR Analysis:** Requires manual input of loss ranges (could integrate with financial data)
2. **Monte Carlo:** Factor definitions need standardization
3. **Risk Heat Map:** Visualization logic exists but frontend integration needed
4. **Automated Risk Detection:** Could integrate with monitoring tools for automatic risk identification

## Contact

**Service Owner:** Risk Management Team
**Documentation:** /docs (Swagger UI)
**Source Code:** `/platform-services/risk-service/`
