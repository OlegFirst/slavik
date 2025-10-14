# Knowledge Quality Manager (KQM) - Architecture

**Date**: 2025-10-11
**Status**: 🏗️ Design & Implementation
**Location**: `/platform-services/AI-services-management/`

---

## 🎯 Mission

**Knowledge Quality Manager** - интеллектуальный сервис для:
1. ✅ Генерации необходимых сценариев (теория → практика)
2. ✅ Мониторинга уровня знаний платформы
3. ✅ Контроля соответствия стандартам (ISO 22301, NIST, WHO)
4. ✅ Анализа запросов пользователей (gaps detection)
5. ✅ Автоматического повышения компетенций

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         KNOWLEDGE QUALITY MANAGER (Orchestrator)             │
│         Location: /platform-services/AI-services-management  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  SCENARIO        │  │  KNOWLEDGE       │  │  COMPLIANCE      │
│  GENERATOR       │  │  MONITOR         │  │  CONTROLLER      │
│  (Tools)         │  │  (Analytics)     │  │  (Validator)     │
└──────────────────┘  └──────────────────┘  └──────────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  INTELLIGENT CORE (Processing)               │
├─────────────────────────────────────────────────────────────┤
│  ├─ AI Foundation (RAG, LLM, Embeddings)                    │
│  ├─ Expertise Center (Domain Specialists)                   │
│  ├─ Community Intelligence (k=5, Patterns)                  │
│  ├─ Predictive (What knowledge is needed)                   │
│  └─ Workflow Intelligence (Usage patterns)                  │
└─────────────────────────────────────────────────────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│              INFRASTRUCTURE (Storage & Control)              │
├─────────────────────────────────────────────────────────────┤
│  ├─ Database (PostgreSQL - persistent)                      │
│  ├─ Redis (cache, working memory)                           │
│  └─ DB Intelligence (placement, optimization)               │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                   OUTPUT (Knowledge Base)                    │
├─────────────────────────────────────────────────────────────┤
│  ├─ Scenarios (parsed + generated)                          │
│  ├─ Standards (ISO, NIST, WHO)                              │
│  ├─ Workflows (execution patterns)                          │
│  └─ Metrics (quality, coverage, gaps)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Component Breakdown

### 1. Knowledge Quality Manager (Main Service)

**Location**: `/platform-services/AI-services-management/`

**Role**: Orchestrator & Controller

```python
class KnowledgeQualityManager:
    """
    Main orchestrator for knowledge management

    Responsibilities:
    1. Monitor knowledge coverage
    2. Detect gaps (missing scenarios/standards)
    3. Prioritize generation needs
    4. Coordinate components
    5. Ensure quality standards
    """

    def __init__(self):
        self.scenario_generator = ScenarioGenerator()
        self.knowledge_monitor = KnowledgeMonitor()
        self.compliance_controller = ComplianceController()
        self.predictive = PredictiveEngine()

    async def run_continuous_cycle(self):
        """Main 24-hour cycle"""

        while True:
            # 1. MONITOR current state
            knowledge_state = await self.knowledge_monitor.assess()

            # 2. DETECT gaps
            gaps = await self.detect_gaps(knowledge_state)

            # 3. PREDICT needs
            future_needs = await self.predictive.predict_knowledge_needs()

            # 4. PRIORITIZE
            priorities = self.prioritize_gaps(gaps, future_needs)

            # 5. GENERATE
            new_scenarios = await self.scenario_generator.generate(priorities)

            # 6. VALIDATE
            validated = await self.compliance_controller.validate(new_scenarios)

            # 7. STORE
            await self.store_knowledge(validated)

            # 8. REPORT
            await self.report_metrics()

            await asyncio.sleep(86400)  # 24 hours
```

**Endpoints**:
```python
# Health & Status
GET  /api/kqm/health
GET  /api/kqm/status
GET  /api/kqm/metrics

# Knowledge Monitoring
GET  /api/kqm/knowledge/coverage
GET  /api/kqm/knowledge/gaps
GET  /api/kqm/knowledge/quality

# Scenario Management
POST /api/kqm/scenarios/generate
GET  /api/kqm/scenarios/pending
POST /api/kqm/scenarios/approve/{id}

# Compliance
GET  /api/kqm/compliance/status
GET  /api/kqm/compliance/gaps/{standard}
POST /api/kqm/compliance/validate

# Analytics
GET  /api/kqm/analytics/user-requests
GET  /api/kqm/analytics/knowledge-usage
GET  /api/kqm/analytics/competency-levels
```

---

### 2. Scenario Generator (Tools)

**Location**: `/platform-services/AI-services-management/tools/scenario_generator.py`

**Role**: Auto-generate scenarios based on needs

```python
class ScenarioGenerator:
    """
    Generates scenarios automatically

    Sources:
    1. Standards (ISO/NIST/WHO) - theoretical base
    2. Platform capabilities - what we can do
    3. User requests - what they need
    4. Community patterns - what others use
    5. Predictive - what will be needed
    """

    async def generate(self, priorities: List[KnowledgeGap]):
        """Generate scenarios for identified gaps"""

        scenarios = []

        for gap in priorities:
            # 1. Determine type
            if gap.type == "standard_requirement":
                # Generate from ISO/NIST/WHO
                scenario = await self.generate_from_standard(gap)

            elif gap.type == "platform_capability":
                # Generate from existing services
                scenario = await self.generate_from_capability(gap)

            elif gap.type == "user_request":
                # Generate from user needs
                scenario = await self.generate_from_request(gap)

            elif gap.type == "community_pattern":
                # Generate from community intelligence
                scenario = await self.generate_from_pattern(gap)

            scenarios.append(scenario)

        return scenarios

    async def generate_from_standard(self, gap: KnowledgeGap):
        """Generate scenario from ISO/NIST/WHO requirement"""

        # 1. Load standard text
        standard_text = await self.load_standard(gap.standard, gap.clause)

        # 2. Find platform mapping
        mapping = await self.find_platform_mapping(gap.clause)

        # 3. Get examples from community
        examples = await community_intelligence.find_similar(gap.clause, k=5)

        # 4. Generate with LLM
        prompt = f"""
        Generate a detailed scenario for implementing:

        Standard: {gap.standard} Clause {gap.clause}
        Requirement: {standard_text}

        Platform Services: {mapping.services}
        Real Examples: {examples}

        Create:
        1. Business Context
        2. Implementation Steps
        3. API calls needed
        4. Validation criteria
        5. Compliance proof
        """

        scenario = await llm.generate(prompt, model="claude-opus")

        return {
            'type': 'standard_implementation',
            'standard': gap.standard,
            'clause': gap.clause,
            'content': scenario,
            'services': mapping.services,
            'validation': 'iso_compliance'
        }

    async def generate_from_capability(self, gap: KnowledgeGap):
        """Generate scenario from platform capability"""

        # Platform has feature but no documented scenario
        capability = gap.capability
        service = gap.service

        # 1. Analyze service endpoints
        endpoints = await self.analyze_service_endpoints(service)

        # 2. Find usage patterns
        patterns = await workflow_intelligence.get_patterns(service)

        # 3. Generate documentation
        scenario = await self.generate_capability_docs(
            capability, endpoints, patterns
        )

        return scenario

    async def generate_from_request(self, gap: KnowledgeGap):
        """Generate from user request/question"""

        # User asked question, no answer found
        question = gap.user_question

        # 1. Search existing knowledge
        existing = await rag.search(question, top_k=10)

        # 2. Find related platform features
        features = await self.find_related_features(question)

        # 3. Generate new scenario
        scenario = await llm.generate(f"""
        User asked: {question}

        Existing knowledge: {existing}
        Platform features: {features}

        Create a comprehensive scenario that answers this question.
        """)

        return scenario
```

---

### 3. Knowledge Monitor (Analytics)

**Location**: `/platform-services/AI-services-management/knowledge_monitor.py`

**Role**: Track knowledge coverage and quality

```python
class KnowledgeMonitor:
    """
    Monitors knowledge base health

    Metrics:
    1. Coverage (% of standards documented)
    2. Quality (validation pass rate)
    3. Usage (scenario utilization rate)
    4. Gaps (missing knowledge areas)
    5. Freshness (last update time)
    """

    async def assess(self) -> KnowledgeState:
        """Assess current knowledge state"""

        # 1. Coverage Assessment
        coverage = await self.assess_coverage()

        # 2. Quality Assessment
        quality = await self.assess_quality()

        # 3. Usage Assessment
        usage = await self.assess_usage()

        # 4. Gaps Detection
        gaps = await self.detect_gaps()

        return KnowledgeState(
            coverage=coverage,
            quality=quality,
            usage=usage,
            gaps=gaps,
            timestamp=datetime.now()
        )

    async def assess_coverage(self) -> CoverageReport:
        """Check knowledge coverage"""

        # ISO 22301 coverage
        iso_clauses = await self.get_iso_clauses()
        iso_documented = await self.count_documented_scenarios(
            standard="ISO22301"
        )
        iso_coverage = iso_documented / len(iso_clauses)

        # Platform capabilities coverage
        services = await self.get_all_services()
        endpoints = await self.get_all_endpoints()
        documented_endpoints = await self.count_documented_endpoints()
        platform_coverage = documented_endpoints / len(endpoints)

        # User needs coverage
        user_questions = await self.get_unanswered_questions()
        coverage_gaps = len(user_questions)

        return CoverageReport(
            iso_coverage=iso_coverage,
            platform_coverage=platform_coverage,
            user_gaps=coverage_gaps,
            total_scenarios=await self.count_total_scenarios()
        )

    async def assess_quality(self) -> QualityReport:
        """Check knowledge quality"""

        # Validation metrics
        total = await self.count_total_scenarios()
        validated = await self.count_validated_scenarios()
        expert_approved = await self.count_expert_approved()

        # Usage metrics
        used = await self.count_used_scenarios()

        # Freshness
        stale = await self.count_stale_scenarios(days=90)

        return QualityReport(
            validation_rate=validated / total,
            expert_approval_rate=expert_approved / total,
            usage_rate=used / total,
            stale_count=stale,
            avg_confidence=await self.calculate_avg_confidence()
        )
```

---

### 4. Compliance Controller (Validator)

**Location**: `/platform-services/AI-services-management/compliance_controller.py`

**Role**: Ensure standards compliance

```python
class ComplianceController:
    """
    Controls compliance with standards

    Standards:
    1. ISO 22301 (BCM)
    2. NIST SP 800-34 (IT Contingency)
    3. WHO Emergency Response
    """

    async def validate(self, scenarios: List[Scenario]) -> List[ValidatedScenario]:
        """Validate scenarios for compliance"""

        validated = []

        for scenario in scenarios:
            # 1. ISO Compliance Check
            iso_check = await self.check_iso_compliance(scenario)

            # 2. Technical Validation
            tech_check = await self.check_technical_validity(scenario)

            # 3. Expert Review
            expert_check = await self.get_expert_review(scenario)

            # 4. Quality Score
            quality_score = self.calculate_quality(
                iso_check, tech_check, expert_check
            )

            validated.append(ValidatedScenario(
                scenario=scenario,
                iso_compliant=iso_check.passed,
                technically_valid=tech_check.passed,
                expert_approved=expert_check.approved,
                quality_score=quality_score,
                status='approved' if quality_score > 0.8 else 'needs_review'
            ))

        return validated

    async def check_iso_compliance(self, scenario: Scenario):
        """Check ISO 22301 compliance"""

        if not scenario.iso_clause:
            return ComplianceCheck(passed=True, note="Not ISO-related")

        # Load ISO requirements
        requirements = await self.load_iso_requirements(scenario.iso_clause)

        # Check coverage
        checks = []
        for req in requirements:
            covered = self.check_requirement_coverage(scenario, req)
            checks.append(covered)

        return ComplianceCheck(
            passed=all(checks),
            clause=scenario.iso_clause,
            requirements_met=sum(checks),
            requirements_total=len(requirements),
            gaps=[req for req, covered in zip(requirements, checks) if not covered]
        )
```

---

## 🔄 Data Flow

### 1. Knowledge Ingestion

```python
# Standards → Knowledge Base
async def ingest_standards():
    """Load ISO/NIST/WHO standards"""

    # 1. Load from files
    iso_text = load_standard("ISO22301")
    nist_text = load_standard("NIST-SP-800-34")
    who_text = load_standard("WHO-Emergency")

    # 2. Parse into clauses
    iso_clauses = parse_clauses(iso_text)

    # 3. Create embeddings
    embeddings = await embed_documents(iso_clauses)

    # 4. Store in RAG
    await rag.upsert(
        collection="bcm_knowledge",
        documents=iso_clauses,
        embeddings=embeddings
    )
```

### 2. Scenario Generation → Storage

```
User Request → Gap Detection → Priority → Generation
    ↓
LLM (Claude Opus) → Validation → Expert Review
    ↓
Approved Scenarios
    ↓
    ├─→ File System (/docs/business-scenarios/generated/)
    ├─→ RAG (Qdrant: generated_scenarios)
    ├─→ Expertise Center (domain learning)
    └─→ Redis (working memory, TTL=7d)
```

### 3. Knowledge Retrieval

```python
# User asks question
async def answer_question(question: str):

    # 1. Search all sources in parallel
    tasks = [
        rag.search(question, collection="business_scenarios"),  # Existing
        rag.search(question, collection="bcm_knowledge"),       # Standards
        rag.search(question, collection="generated_scenarios"), # Auto-gen
        community_intelligence.search(question, k=5),           # Community
    ]

    results = await asyncio.gather(*tasks)

    # 2. Rerank by relevance
    ranked = rerank_results(results)

    # 3. Build context
    context = build_context(ranked[:5])

    # 4. Generate answer
    answer = await llm.generate(
        prompt=f"Question: {question}\nContext: {context}",
        model="claude-sonnet"
    )

    # 5. Track usage (for quality monitoring)
    await track_scenario_usage(ranked[0].scenario_id)

    return answer
```

---

## 🗄️ Infrastructure Integration

### Database Layer (`/infrastructure/database/`)

**PostgreSQL Schema**:
```sql
-- Knowledge Base Tables
CREATE TABLE scenarios (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    type VARCHAR(50),  -- 'existing', 'generated', 'standard'
    source VARCHAR(100),
    confidence FLOAT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE knowledge_gaps (
    id SERIAL PRIMARY KEY,
    gap_type VARCHAR(50),  -- 'standard', 'capability', 'user_request'
    description TEXT,
    priority INT,
    status VARCHAR(20),  -- 'detected', 'in_progress', 'resolved'
    detected_at TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE TABLE scenario_validation (
    scenario_id INT REFERENCES scenarios(id),
    validator_type VARCHAR(50),  -- 'iso', 'expert', 'technical'
    validation_result JSONB,
    validated_at TIMESTAMP
);

CREATE TABLE knowledge_metrics (
    metric_name VARCHAR(100),
    metric_value FLOAT,
    metadata JSONB,
    measured_at TIMESTAMP
);
```

**Redis Schema** (`/infrastructure/database/redis_knowledge.py`):
```python
# Working Memory (TTL = 7 days)
class KnowledgeRedisCache:

    # Hot scenarios (frequently accessed)
    async def cache_hot_scenario(self, scenario_id: str, scenario: dict):
        await redis.setex(
            f"scenario:hot:{scenario_id}",
            ttl=604800,  # 7 days
            value=json.dumps(scenario)
        )

    # Gap detection results (temporary)
    async def cache_gaps(self, gaps: List[KnowledgeGap]):
        await redis.setex(
            "knowledge:gaps:current",
            ttl=86400,  # 1 day
            value=json.dumps([g.dict() for g in gaps])
        )

    # Generation queue
    async def queue_generation(self, gap: KnowledgeGap):
        await redis.lpush("queue:scenario_generation", gap.json())

    # Metrics (real-time)
    async def update_metrics(self, metrics: dict):
        await redis.hmset("metrics:knowledge", metrics)
```

### DB Intelligence Control (`/infrastructure/AI-office-infrastructure/db-intelligence/`)

**Role**: Optimize knowledge storage & placement

```python
class KnowledgeDBIntelligence:
    """
    Controls knowledge database operations

    Responsibilities:
    1. Decide: Redis (hot) vs PostgreSQL (cold)
    2. Optimize queries
    3. Manage TTLs
    4. Monitor performance
    """

    async def optimize_placement(self, scenario: Scenario):
        """Decide where to store scenario"""

        # Calculate hotness score
        hotness = await self.calculate_hotness(scenario)

        if hotness > 0.7:
            # Hot: Redis + PostgreSQL
            await redis.cache_hot_scenario(scenario)
            await postgres.store_scenario(scenario)
        else:
            # Cold: PostgreSQL only
            await postgres.store_scenario(scenario)

    async def calculate_hotness(self, scenario: Scenario) -> float:
        """Calculate scenario hotness (0-1)"""

        # Factors:
        usage_count = await self.get_usage_count(scenario.id)
        recency = (datetime.now() - scenario.created_at).days
        user_rating = await self.get_avg_rating(scenario.id)

        hotness = (
            (usage_count / 100) * 0.5 +    # 50% weight on usage
            (1 / (recency + 1)) * 0.3 +     # 30% weight on recency
            user_rating * 0.2               # 20% weight on rating
        )

        return min(hotness, 1.0)
```

---

## 📊 Metrics & Monitoring

### Dashboard Metrics

```python
{
    "knowledge_coverage": {
        "iso_22301": 0.85,        # 85% of ISO clauses documented
        "platform_services": 0.72, # 72% of endpoints documented
        "user_needs": 0.68         # 68% of user questions answerable
    },

    "knowledge_quality": {
        "validation_rate": 0.88,
        "expert_approval": 0.92,
        "usage_rate": 0.65,
        "avg_confidence": 0.84
    },

    "generation_stats": {
        "scenarios_generated_this_week": 12,
        "pending_validation": 3,
        "approved_this_month": 47
    },

    "gaps_detected": {
        "standard_gaps": 15,        # ISO requirements not documented
        "capability_gaps": 8,        # Features without docs
        "user_request_gaps": 23      # Unanswered questions
    },

    "performance": {
        "search_latency_ms": 45,
        "generation_time_min": 2.3,
        "cache_hit_rate": 0.78
    }
}
```

---

## 🚀 Implementation Plan

### Phase 1: Foundation (Week 1-2)
```bash
# 1. Create KQM service structure
mkdir -p /platform-services/AI-services-management/{tools,analytics,validation}

# 2. Setup database schemas
psql < knowledge_schemas.sql

# 3. Configure Redis
# Add knowledge cache keys

# 4. Integrate with existing components
# - AI Foundation (RAG)
# - Expertise Center
# - Predictive Engine
```

**Deliverables**:
- [x] Architecture designed
- [ ] Database schemas created
- [ ] Redis integration configured
- [ ] KQM service skeleton

### Phase 2: Core Features (Week 3-4)
- [ ] Scenario Generator (tools/)
- [ ] Knowledge Monitor (analytics/)
- [ ] Compliance Controller (validation/)
- [ ] Gap Detection algorithm

**Deliverables**:
- Auto-generation working
- Coverage monitoring active
- Compliance validation ready

### Phase 3: Intelligence (Week 5-6)
- [ ] Predictive knowledge needs
- [ ] Community pattern integration
- [ ] Expert review workflow
- [ ] Quality scoring

**Deliverables**:
- Predictive generation
- Community-driven scenarios
- Expert validation loop

### Phase 4: Automation (Week 7-8)
- [ ] 24-hour orchestration cycle
- [ ] Auto-approval for high-confidence
- [ ] Metrics dashboard
- [ ] Alerting system

**Deliverables**:
- Fully automated KQM
- Real-time monitoring
- Self-improving system

---

## 🎯 Success Criteria

### Week 2
- ✅ KQM service running
- ✅ Database schemas deployed
- ✅ Basic gap detection working

### Month 1
- ✅ Auto-generate 20+ scenarios
- ✅ 90% validation pass rate
- ✅ ISO coverage > 80%

### Month 3
- ✅ 200+ scenarios generated
- ✅ Platform coverage > 85%
- ✅ User satisfaction > 90%

---

**Status**: ✅ Architecture Complete
**Next**: Implement Phase 1 (Foundation)
**Owner**: Knowledge Quality Manager Service
