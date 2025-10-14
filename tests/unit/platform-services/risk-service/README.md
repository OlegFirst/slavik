# Risk Management Module - Test Suite

Comprehensive unit tests for the Risk Management module covering all layers of the application.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared fixtures and test configuration
├── test_repository.py          # Repository layer tests (database operations)
├── test_business_logic.py      # Business logic layer tests
├── test_api.py                 # API endpoint tests
├── test_auth.py                # JWT authentication tests
└── README.md                   # This file
```

## Test Statistics

- **Total Test Files**: 6
- **Total Test Cases**: 121
  - Repository Tests: 29
  - Business Logic Tests: 36
  - API Tests: 25
  - Authentication Tests: 31
- **Test Classes**: 26
- **Total Lines of Code**: ~3,000 lines

## Test Coverage Areas

### 1. Repository Layer (`test_repository.py`)
Tests all database operations with both real and mocked database interactions.

**Coverage:**
- Risk CRUD operations (create, read, update, delete)
- FAIR analysis persistence
- Monte Carlo simulation storage
- Treatment plan management
- Analytics and statistics queries
- Risk history and trends data retrieval
- Filtering and pagination
- Edge cases (non-existent records, soft deletes)

**Key Test Classes:**
- `TestRiskCRUD` - Risk database operations
- `TestFAIRAnalysis` - FAIR analysis storage
- `TestMonteCarloSimulation` - Monte Carlo data persistence
- `TestTreatmentPlans` - Treatment plan operations
- `TestAnalytics` - Analytics queries

### 2. Business Logic Layer (`test_business_logic.py`)
Tests all business methods including risk calculations and trend analysis.

**Coverage:**
- Risk service CRUD operations
- FAIR analysis calculations and validations
- Monte Carlo simulation execution and statistics
- Treatment plan lifecycle management
- Risk trend analysis (`get_risk_trends()` with various scenarios)
- Risk report generation
- Risk heat map creation
- Utility functions (severity calculations)

**Key Test Classes:**
- `TestRiskServiceCRUD` - Risk business logic
- `TestFAIRAnalysis` - FAIR calculations and validations
- `TestMonteCarloSimulation` - Monte Carlo simulations
- `TestTreatmentPlanService` - Treatment plans
- `TestRiskTrends` - Risk trends (NEW - comprehensive coverage)
- `TestRiskReports` - Report generation
- `TestUtilities` - Utility functions

**Special Focus Areas:**
- `get_risk_trends()` tested with:
  - Empty data scenarios
  - Single day data
  - Multiple days data
  - Different time periods (7, 30, 90, 365 days)
- FAIR analysis validation:
  - Invalid threat frequencies
  - Invalid vulnerability scores
  - Invalid loss distributions
  - Risk rating calculations
- Monte Carlo validation:
  - Invalid iterations
  - No factors
  - Invalid distributions

### 3. API Routes (`test_api.py`)
Tests all HTTP endpoints with authentication and authorization.

**Coverage:**
- Risk CRUD endpoints
- FAIR analysis endpoints
- Monte Carlo simulation endpoints
- Treatment plan endpoints
- Risk report endpoints
- Risk heat map endpoint
- Risk trends endpoint (with query parameters)
- Authentication enforcement
- Organization isolation
- Error handling (404s, validation errors)

**Key Test Classes:**
- `TestRiskAPI` - Risk CRUD endpoints
- `TestFAIRAnalysisAPI` - FAIR endpoints
- `TestMonteCarloAPI` - Monte Carlo endpoints
- `TestTreatmentPlanAPI` - Treatment plan endpoints
- `TestRiskReportsAPI` - Report endpoints
- `TestAuthorization` - Access control
- `TestErrorHandling` - Error cases

### 4. Authentication (`test_auth.py`)
Tests JWT token handling and user extraction.

**Coverage:**
- JWT token verification
- Token decoding (with/without verification)
- User creation from token payload
- Authentication dependencies (`get_current_user`, `get_optional_user`)
- Role-based authorization
- Token edge cases (expired, invalid, missing claims)
- Auth disabled scenarios

**Key Test Classes:**
- `TestJWTVerification` - Token verification
- `TestJWTDecoding` - Token decoding
- `TestUserCreation` - User extraction from tokens
- `TestGetCurrentUser` - Required authentication
- `TestGetOptionalUser` - Optional authentication
- `TestRoleBasedAuth` - Role checking
- `TestTokenEdgeCases` - Edge cases

## Prerequisites

Install required dependencies:

```bash
pip install pytest pytest-asyncio pytest-cov httpx
pip install sqlalchemy aiosqlite
pip install fastapi python-jose
pip install numpy  # For Monte Carlo simulations
```

Or install all dependencies at once:

```bash
pip install -r requirements.txt
```

## Running Tests

### Run All Tests
```bash
cd /Users/MD/AI-Platform-ISO/execution-engine/capabilities/analysis/risk
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_repository.py
pytest tests/test_business_logic.py
pytest tests/test_api.py
pytest tests/test_auth.py
```

### Run Specific Test Class
```bash
pytest tests/test_repository.py::TestRiskCRUD
pytest tests/test_business_logic.py::TestRiskTrends
```

### Run Specific Test Function
```bash
pytest tests/test_business_logic.py::TestRiskTrends::test_get_risk_trends_empty_data
```

### Run with Verbose Output
```bash
pytest tests/ -v
```

### Run with Coverage Report
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run Only Failed Tests
```bash
pytest tests/ --lf
```

### Run Tests in Parallel
```bash
pip install pytest-xdist
pytest tests/ -n auto
```

## Test Fixtures

Common fixtures are defined in `conftest.py`:

**Database Fixtures:**
- `test_db_engine` - In-memory SQLite database
- `db_session` - Async database session
- `mock_db_session` - Mocked database session

**User Fixtures:**
- `test_user` - Standard test user
- `admin_user` - Admin test user

**Domain Model Fixtures:**
- `sample_risk` - Sample risk model
- `sample_fair_analysis` - Sample FAIR analysis
- `sample_monte_carlo` - Sample Monte Carlo simulation
- `sample_treatment_plan` - Sample treatment plan

**Database Model Fixtures:**
- `sample_risk_db` - Sample risk database model
- `sample_fair_db` - Sample FAIR database model
- `sample_monte_carlo_db` - Sample Monte Carlo database model
- `sample_treatment_plan_db` - Sample treatment plan database model

**JWT Fixtures:**
- `valid_jwt_payload` - Valid JWT token payload
- `expired_jwt_payload` - Expired JWT token payload
- `jwt_secret_key` - Test JWT secret

## Test Patterns

### Async Tests
All async functions use the `@pytest.mark.asyncio` decorator:

```python
@pytest.mark.asyncio
async def test_create_risk(db_session, sample_risk):
    service = RiskService(db_session)
    result = await service.create_risk(sample_risk)
    assert result is not None
```

### Mocking
Tests use `unittest.mock` for mocking dependencies:

```python
with patch.object(RiskService, 'create_risk') as mock_create:
    mock_create.return_value = sample_risk
    # Test code here
```

### Exception Testing
Exception handling is tested using pytest's `raises`:

```python
with pytest.raises(ValueError, match="Invalid vulnerability score"):
    await service.perform_fair_analysis(risk_id, invalid_data)
```

## CI/CD Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Environment Variables

Some tests may require environment variables:

```bash
export DATABASE_URL="sqlite+aiosqlite:///:memory:"
export JWT_AUTH_ENABLED="false"  # Disable JWT auth for testing
export JWT_SECRET_KEY="test-secret-key"
```

## Known Issues

None currently identified.

## Contributing

When adding new tests:

1. Place them in the appropriate test file based on the layer being tested
2. Use descriptive test names that explain what is being tested
3. Include docstrings explaining the test purpose
4. Use fixtures from `conftest.py` where applicable
5. Follow the existing test patterns
6. Ensure all async operations use `@pytest.mark.asyncio`

## Contact

For questions or issues with tests, contact the development team.
