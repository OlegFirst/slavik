# 🧪 Testing Specification - AI-Powered BCM Platform

**Version**: 1.0
**Date**: 2025-10-07
**Status**: Production Ready
**Type**: Technical Specification

---

## 📋 Document Overview

### Purpose
This document provides the complete technical specification for testing the AI-Powered BCM Platform, covering all 9 intelligent-core modules with automated testing strategies, coverage targets, and implementation guidelines.

### Scope
- **9 Intelligent-Core Modules**: Complete test coverage strategy
- **Testing Infrastructure**: pytest, fixtures, CI/CD integration
- **Automation**: Continuous testing pipeline
- **Quality Targets**: 80%+ code coverage, 95%+ critical path coverage

### Related Documents
- [Architecture Specification](architecture/FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md)
- [API Documentation](api/)
- [Deployment Guide](deployment/)

---

## 📊 Executive Summary

### Current State
- **Total Python Files**: 1,868
- **Existing Tests**: ~35 files (1.9% coverage)
- **Coverage Gaps**: 7 modules with 0-10% coverage
- **Risk Level**: 🔴 **HIGH** - Production system with minimal test coverage

### Target State (14 weeks)
- **Test Coverage**: 80%+ overall, 95%+ critical paths
- **Total Tests**: 1000+ test cases
- **Test Categories**: Unit (60%), Integration (30%), E2E (10%)
- **Automation**: Full CI/CD integration with GitHub Actions
- **Metrics**: Real-time coverage dashboard

### Investment
- **Initial Setup**: 1-2 weeks
- **Module Coverage**: 12 weeks (phased approach)
- **Ongoing**: ~20% of development time

---

## 🏗️ Modules Overview

### All 9 Intelligent-Core Modules

| # | Module | Python Files | Existing Tests | Coverage | Priority | Complexity |
|---|--------|--------------|----------------|----------|----------|------------|
| 1 | **workflow_intelligence** | ~100 | 9 | 5% | 🔴 Critical | HIGH |
| 2 | **ai-foundation** | ~50 | 2 | 2% | 🔴 Critical | HIGH |
| 3 | **orchestration** | ~80 | 6 | 10% | 🔴 Critical | VERY HIGH |
| 4 | **expertise-center** | ~150 | 0 | 0% | 🟡 High | MEDIUM-HIGH |
| 5 | **collective** | ~20 | 0 | 0% | 🔴 Critical (Privacy) | MEDIUM |
| 6 | **community_intelligence** | ~40 | 2 | 3% | 🟡 High | MEDIUM-HIGH |
| 7 | **predictive** | ~15 | 0 | 0% | 🟢 Medium | MEDIUM |
| 8 | **workflow-engine** | 22 | 1 | 1% | 🔴 Critical | HIGH |
| 9 | **ai_workflow_optimizer** | 1 (946 LOC) | 0 | 0% | 🔴 Critical | VERY HIGH |

**Total**: ~580 Python files, ~35 existing tests

---

## 🎯 Testing Strategy by Module

### Module 1: workflow_intelligence
**Role**: Core workflow engine (THE BRAIN)
**Target**: 120+ tests, 85% coverage

#### Components
- WorkflowEngine - State machine orchestration
- PostgresStorageAdapter - RLS-enabled database
- CaseCollector - Learn from completed workflows
- AIContextBuilder - Context for AI decisions
- Temporal Workflows - BIA, Risk, Planning workflows

#### Test Breakdown
- **Unit Tests** (70): State machine, storage, case collection
- **Integration Tests** (30): Temporal, EventBus, RLS security
- **E2E Tests** (15): Complete workflow cycles
- **Performance Tests** (5): Throughput, latency

#### Critical Test Scenarios
```python
# RLS Security (10 tests)
test_rls_tenant_isolation_enforced()
test_rls_prevents_cross_tenant_access()
test_rls_admin_override_scenarios()

# State Transitions (15 tests)
test_valid_state_transitions()
test_invalid_transitions_blocked()
test_concurrent_state_updates()

# Temporal Integration (15 tests)
test_bia_workflow_completion()
test_workflow_failure_recovery()
test_temporal_timeout_handling()
```

---

### Module 2: ai-foundation
**Role**: AI infrastructure (RAG, ML, LLM)
**Target**: 150+ tests, 80% coverage

#### Components
- RAGPipeline - Document retrieval and ranking
- EmbeddingGenerator - Voyage/OpenAI embeddings
- QdrantVectorStore - Vector search
- PredictiveModel - ML predictions
- LLMRouter - Multi-provider routing

#### Test Breakdown
- **Unit Tests** (90): RAG, embeddings, ML models
- **Integration Tests** (40): Qdrant, LLM APIs
- **Performance Tests** (20): Embedding speed, search latency

#### Critical Test Scenarios
```python
# RAG Pipeline (30 tests)
test_rag_document_ingestion()
test_rag_hybrid_retrieval()
test_rag_reranking_accuracy()

# ML Models (25 tests)
test_predictive_model_accuracy()
test_anomaly_detection_thresholds()
test_model_retraining_improves_accuracy()

# LLM Integration (20 tests)
test_llm_fallback_chain()
test_llm_rate_limit_handling()
@pytest.mark.vcr  # Record/replay
test_llm_response_parsing()
```

---

### Module 3: orchestration
**Role**: AI autonomous decision-making
**Target**: 100+ tests, 85% coverage

#### Components
- AIOrchestrator - Core decision loop
- ContextAggregator - Platform-wide context
- DelegationManager - Route to specialists
- DistributedMemory - 4-layer memory system
- SafetyMonitor - Safety validation

#### Test Breakdown
- **Unit Tests** (60): Decision-making, memory, safety
- **Integration Tests** (30): Full orchestration cycle
- **Chaos Tests** (10): Resilience testing

#### Critical Test Scenarios
```python
# Decision Making (20 tests)
test_orchestrator_context_aggregation()
test_orchestrator_priority_calculation()
test_orchestrator_delegation_routing()

# Safety (15 tests)
test_safety_monitor_prevents_hallucinations()
test_safety_monitor_detects_loops()
test_safety_override_scenarios()

# Memory System (25 tests)
test_working_memory_updates()
test_long_term_pattern_retrieval()
test_memory_persistence()
```

---

### Module 4: expertise-center
**Role**: 26 AI agents (analyzers, specialists, assistants)
**Target**: 180+ tests, 75% coverage

#### Components
- BaseAnalyzer - 10 analyzers (Impact, Risk, Compliance, etc.)
- BaseSpecialist - 3 strategic specialists
- BaseTacticalAssistant - 13 conversational assistants

#### Test Breakdown
- **Unit Tests** (120): Base classes + individual agents
- **Integration Tests** (40): AI foundation integration
- **Conversational Tests** (20): Multi-turn dialogues

#### Critical Test Scenarios
```python
# Base Classes (30 tests)
test_base_analyzer_ai_foundation_integration()
test_base_specialist_abstract_methods()
test_base_tactical_assistant_conversation_flow()

# Individual Agents (150 tests - 6 per agent)
@pytest.mark.parametrize("analyzer_class", ALL_ANALYZERS)
test_analyzer_initialization()
test_analyzer_domain_logic()
test_analyzer_error_handling()
```

---

### Module 5: collective
**Role**: Privacy-preserving collective intelligence
**Target**: 70+ tests, 90% coverage (privacy-critical!)

#### Components
- CollectiveAgentService - Create agents from ≥5 orgs
- Anonymizer - PII removal
- K-AnonymityValidator - Privacy enforcement
- StuckDetectionService - Detect stuck workflows

#### Test Breakdown
- **Unit Tests** (40): Anonymization, k-anonymity
- **Integration Tests** (20): Case library integration
- **Security Tests** (10): Privacy guarantees

#### Critical Test Scenarios
```python
# Privacy (20 tests)
test_anonymizer_removes_all_pii()
test_k_anonymity_minimum_5_orgs_enforced()
test_no_reverse_engineering_possible()
test_gdpr_compliance()

# Collective Agents (20 tests)
test_collective_agent_creation_from_cases()
test_collective_agent_chat_handling()
test_collective_agent_expiration()
```

---

### Module 6: community_intelligence
**Role**: Community-driven knowledge creation
**Target**: 90+ tests, 80% coverage

#### Components
- ContributionService - Submit/review contributions
- PeerReviewService - Multi-reviewer workflow
- ReputationEngine - Gamification
- WorkflowCompletionHandler - EventBus integration

#### Test Breakdown
- **Unit Tests** (50): Services, reputation
- **Integration Tests** (30): EventBus, case library
- **E2E Tests** (10): Full contribution workflow

---

### Module 7: predictive
**Role**: Journey prediction and recommendations
**Target**: 60+ tests, 75% coverage

#### Components
- JourneyPredictor - Predict next steps
- ProactiveRecommendations - Generate recommendations
- DailyDigestScheduler - Scheduled jobs

#### Test Breakdown
- **Unit Tests** (40): Prediction, recommendations
- **Integration Tests** (15): Case library
- **Scheduler Tests** (5): Cron job execution

---

### Module 8: workflow-engine
**Role**: BPMN 2.0 orchestration
**Target**: 90+ tests, 80% coverage

#### Components
- UnifiedWorkflowEngine - BPMN + Workflow Intelligence
- BPMNEngine - BPMN execution
- BPMNParser - XML parsing
- GatewayEvaluator - Gateway logic

#### Test Breakdown
- **Unit Tests** (60): Parser, engine, gateways
- **Integration Tests** (20): PostgreSQL, workflow_intelligence
- **E2E Tests** (10): Complete BPMN workflows

#### Critical Test Scenarios
```python
# BPMN Parsing (15 tests)
test_parser_parse_valid_bpmn_xml()
test_parser_exclusive_gateway()
test_parser_parallel_gateway()

# Gateway Evaluation (10 tests)
test_gateway_exclusive_one_path()
test_gateway_parallel_all_paths()
test_gateway_condition_evaluation()
```

---

### Module 9: ai_workflow_optimizer
**Role**: Platform self-evolution (ML-powered)
**Target**: 140+ tests, 85% coverage

#### Components
- WorkflowOptimizerService - ML analysis
- PerformancePredictor - RandomForest
- BottleneckDetector - Classifier
- AnomalyDetector - Isolation Forest

#### Test Breakdown
- **Unit Tests** (80): ML models, predictions
- **Integration Tests** (30): Database, models
- **ML Validation Tests** (20): Accuracy, precision
- **E2E Tests** (10): Self-evolution cycle

#### Critical Test Scenarios
```python
# ML Models (30 tests)
test_performance_predictor_training()
test_performance_predictor_accuracy_threshold()
test_bottleneck_detector_precision_recall()
test_anomaly_detector_false_positive_rate()

# Predictions (30 tests)
test_predict_performance_returns_valid_result()
test_detect_bottlenecks_identifies_issues()
test_optimize_resources_calculates_improvements()

# Evolution Cycle (10 tests)
test_platform_detects_optimization_need()
test_generates_technical_specification()
# Future: test_lab_implements_specification()
```

---

## 🛠️ Testing Infrastructure

### Technology Stack

#### Core Framework
```python
pytest==7.4.4                  # Main framework
pytest-asyncio==0.23.3         # Async support
pytest-cov==4.1.0              # Coverage
pytest-mock==3.11.0            # Mocking
pytest-xdist==3.5.0            # Parallel execution
```

#### Database Testing
```python
pytest-postgresql==5.0.0       # PostgreSQL fixtures
fakeredis==2.21.0              # Redis mocking
factory-boy==3.3.0             # Test data generation
```

#### API Testing
```python
httpx==0.26.0                  # Async HTTP client
respx==0.20.2                  # HTTP mocking
aioresponses==0.7.6            # Async response mocking
```

#### AI/ML Mocking
```python
vcrpy==5.1.0                   # Record/replay LLM calls
faker==22.0.0                  # Fake data
hypothesis==6.98.0             # Property-based testing
```

### Global Fixtures (25+)

Located in `tests/conftest.py`:

```python
# Database
@pytest.fixture
async def db_session() -> AsyncSession

@pytest.fixture
def redis_client() -> FakeRedis

# AI Foundation
@pytest.fixture
def mock_llm_client() -> Mock

@pytest.fixture
def mock_rag_pipeline() -> Mock

@pytest.fixture
def mock_ml_predictor() -> Mock

# EventBus
@pytest.fixture
def mock_eventbus() -> Mock

# Sample Data
@pytest.fixture
def sample_workflow_context() -> Dict

@pytest.fixture
def sample_organization() -> Dict

# Security
@pytest.fixture
def sql_injection_patterns() -> List[str]
```

### Configuration

**pytest.ini**:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
asyncio_mode = auto

addopts =
    -v
    --cov=intelligent-core
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --durations=10

markers =
    slow: slow tests
    integration: integration tests
    e2e: end-to-end tests
    security: security tests
    performance: performance tests
```

---

## 🔄 CI/CD Integration

### GitHub Actions Workflow

**Stages**:
1. **Unit Tests** (on every push)
   - Fast execution (< 5 min)
   - 60% of test suite
   - Fail fast on errors

2. **Integration Tests** (on PR)
   - Requires services (PostgreSQL, Redis, Qdrant)
   - 30% of test suite
   - Full environment

3. **Security Tests** (on PR)
   - SQL injection prevention
   - RLS isolation
   - Privacy validation

4. **E2E Tests** (on merge to main)
   - Complete workflow cycles
   - 10% of test suite
   - Production-like environment

5. **Nightly Tests**
   - Performance benchmarks
   - Chaos engineering
   - ML model validation

### Coverage Requirements

**Merge Criteria**:
- ✅ Unit tests pass (100%)
- ✅ Integration tests pass (100%)
- ✅ Security tests pass (100%)
- ✅ Code coverage ≥ 80% (overall)
- ✅ Critical path coverage ≥ 95%

---

## 📈 Testing Metrics

### Coverage Targets by Module

| Module | Target Coverage | Critical Paths |
|--------|----------------|----------------|
| workflow_intelligence | 85% | 95% |
| ai-foundation | 80% | 90% |
| orchestration | 85% | 95% |
| expertise-center | 75% | 85% |
| collective | 90% | 100% (privacy!) |
| community_intelligence | 80% | 90% |
| predictive | 75% | 85% |
| workflow-engine | 80% | 90% |
| ai_workflow_optimizer | 85% | 95% |

### Quality Metrics

**Test Quality**:
- Pass Rate: > 99%
- Flaky Test Rate: < 1%
- Test Execution Time: < 30 min (full suite)
- Test Maintenance Time: < 20% of dev time

**Code Quality**:
- Cyclomatic Complexity: < 10 per function
- Code Duplication: < 3%
- Static Analysis: 0 critical issues
- Security Vulnerabilities: 0 (safety check)

---

## 🚀 Implementation Timeline

### Phase 1: Critical Infrastructure (Weeks 1-4)
**Goal**: 40% overall coverage

**Week 1-2**: workflow_intelligence
- 120+ tests
- RLS security validation
- Temporal integration

**Week 3-4**: ai-foundation
- 150+ tests
- RAG pipeline testing
- ML model validation

### Phase 2: Self-Evolution (Weeks 5-7)
**Goal**: 55% overall coverage

**Week 5-6**: workflow-engine
- 90+ tests
- BPMN compliance
- Gateway evaluation

**Week 7**: ai_workflow_optimizer
- 140+ tests
- ML accuracy validation
- Evolution cycle testing

### Phase 3: Orchestration (Weeks 8-9)
**Goal**: 65% overall coverage

**Week 8-9**: orchestration
- 100+ tests
- Decision-making validation
- Safety monitoring

### Phase 4: Domain Logic (Weeks 10-12)
**Goal**: 75% overall coverage

**Week 10-11**: expertise-center
- 180+ tests
- 26 agent validation

**Week 12**: collective
- 70+ tests
- Privacy verification

### Phase 5: Community Features (Weeks 13-14)
**Goal**: 80%+ overall coverage

**Week 13**: community_intelligence
- 90+ tests
- Peer review workflow

**Week 14**: predictive
- 60+ tests
- Journey prediction

---

## 🎓 Best Practices

### Test Design Principles

1. **AAA Pattern** (Arrange-Act-Assert)
```python
def test_workflow_engine_start():
    # ARRANGE
    engine = WorkflowEngine(storage=mock_storage)

    # ACT
    workflow_id = await engine.start("planning", "tenant-1")

    # ASSERT
    assert workflow_id.startswith("wf-")
```

2. **Descriptive Names**
```python
def test_workflow_engine_start_valid_workflow_creates_context()
def test_workflow_engine_execute_invalid_action_raises_error()
```

3. **Single Responsibility**
- One test = one behavior
- Clear failure messages
- Independent tests

4. **Mock External Dependencies**
```python
@pytest.fixture
def mock_llm_client():
    client = Mock()
    client.generate.return_value = {"content": "test"}
    return client
```

5. **Use Fixtures for DRY**
```python
@pytest.fixture
def workflow_context():
    return {
        "workflow_id": "test-001",
        "module": "planning",
        "tenant_id": "tenant-1"
    }
```

### Security Testing

**SQL Injection Prevention**:
```python
@pytest.mark.security
@pytest.mark.parametrize("malicious_input", [
    "'; DROP TABLE users; --",
    "' OR '1'='1",
])
async def test_sql_injection_prevented(storage, malicious_input):
    with pytest.raises(ValueError):
        await storage.create_workflow(tenant_id=malicious_input)
```

**RLS Isolation**:
```python
@pytest.mark.security
async def test_rls_tenant_isolation():
    # Create workflow for tenant-1
    wf_id = await storage.create_workflow(tenant_id="tenant-1")

    # Try to access from tenant-2 (should fail)
    with pytest.raises(PermissionError):
        await storage.get_workflow(wf_id, tenant_id="tenant-2")
```

### Performance Testing

**Benchmark Tests**:
```python
@pytest.mark.performance
def test_rag_retrieval_under_100ms(benchmark, rag_pipeline):
    result = benchmark(rag_pipeline.retrieve, "ISO 22301")
    assert result.execution_time_ms < 100
```

**Load Testing**:
```python
@pytest.mark.performance
async def test_workflow_throughput_100_per_second():
    engine = WorkflowEngine(storage=test_storage)

    start = time.time()
    tasks = [engine.start(f"wf-{i}") for i in range(1000)]
    await asyncio.gather(*tasks)
    duration = time.time() - start

    throughput = 1000 / duration
    assert throughput >= 100
```

---

## 📚 Quick Reference

### Running Tests

```bash
# All tests
pytest

# Specific module
pytest tests/unit/workflow_intelligence/

# With coverage
pytest --cov=intelligent-core --cov-report=html

# Fast tests only
pytest -m "not slow"

# Specific test
pytest tests/unit/workflow_intelligence/test_engine.py::test_start

# Debug mode
pytest --pdb

# Parallel execution
pytest -n auto
```

### Coverage Reports

```bash
# Generate HTML report
pytest --cov=intelligent-core --cov-report=html
open htmlcov/index.html

# Terminal report
pytest --cov=intelligent-core --cov-report=term-missing

# XML report (for CI)
pytest --cov=intelligent-core --cov-report=xml
```

### Continuous Testing

```bash
# Watch mode (requires pytest-watch)
ptw

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

---

## 🔗 Additional Resources

### Documentation
- [Testing Quick Start](/TESTING_QUICK_START.md)
- [Comprehensive Strategy](/doc-project/COMPREHENSIVE_TESTING_STRATEGY.md)
- [Modules 8-9 Analysis](/doc-project/TESTING_STRATEGY_MODULES_8_9.md)
- [Test Examples](/tests/README.md)

### Tools
- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [VCR.py](https://vcrpy.readthedocs.io/) - Record/replay HTTP

### Internal
- Architecture: `/docs/architecture/`
- API Docs: `/docs/api/`
- Deployment: `/docs/deployment/`

---

## 📞 Support

### Testing Issues
- Check fixtures: `tests/conftest.py`
- Review examples: `tests/unit/*/`
- Read [tests/README.md](../tests/README.md)

### Coverage Questions
- Dashboard: `open htmlcov/index.html`
- CI Reports: GitHub Actions artifacts
- Metrics: Prometheus/Grafana

---

**Document Version**: 1.0
**Last Updated**: 2025-10-07
**Next Review**: 2025-11-07
**Owner**: Testing & QA Team
