# Scenario Generation System Architecture

**Date**: 2025-10-11
**Status**: 🏗️ Design Complete, Ready for Implementation
**Purpose**: Self-learning system that generates new scenarios from real usage

---

## 🎯 System Overview

### Mission
**Automatically generate new business scenarios** by learning from:
1. Real platform usage (Event Bus)
2. Workflow patterns (Workflow Intelligence)
3. User interactions (Analytics)
4. Community knowledge (Collective Intelligence)
5. Audit logs (Event Sourcing)

### Output
- **New scenarios** (auto-documented)
- **Edge cases** (rare but valid patterns)
- **Integration patterns** (cross-service workflows)
- **Evolution paths** (how scenarios evolve)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│          INPUT SOURCES (Real Usage Data)                 │
└─────────────────────────────────────────────────────────┘
    │
    ├──► Event Bus (60+ event types, real workflows)
    ├──► Workflow Intelligence (stuck/success patterns)
    ├──► Analytics (API usage, trends)
    ├──► Community Intelligence (k=5 anonymized cases)
    └──► Audit Logs (execution history)
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│         PROCESSING LAYER (Pattern Detection)             │
└─────────────────────────────────────────────────────────┘
    │
    ├──► Pattern Detector (new use cases, edge cases)
    ├──► Domain Analyzer (classify: service, category, theme)
    ├──► Predictive Engine (emerging trends)
    └──► Evolution Tracker (how patterns change)
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│         GENERATION LAYER (Create Scenarios)              │
└─────────────────────────────────────────────────────────┘
    │
    ├──► RAG Search (find similar scenarios)
    ├──► Domain Specialists (expert validation)
    ├──► LLM Generator (Claude Opus - detailed scenario)
    └──► Validation (quality + ISO compliance check)
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│          OUTPUT & STORAGE (Knowledge Base)               │
└─────────────────────────────────────────────────────────┘
    │
    ├──► File System (markdown files in /generated/)
    ├──► RAG Collection (Qdrant: generated_scenarios)
    ├──► Expertise Center (domain specialists learn)
    └──► Community Intelligence (share anonymized)
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│         FEEDBACK LOOP (Continuous Improvement)           │
└─────────────────────────────────────────────────────────┘
    Loop back to Input Sources ♾️
```

---

## 🔧 Component Design

### 1. Pattern Detection Engine

**Location**: `/intelligent-core/scenario-intelligence/pattern-detector/`

```python
class PatternDetectionEngine:
    """Detects new usage patterns from real data"""

    def __init__(self):
        self.min_occurrence = 3  # Pattern must occur 3+ times
        self.min_support = 0.05  # 5% of workflows
        self.window = timedelta(days=7)  # Look back 7 days

    async def detect_new_use_cases(self, events: List[Event]) -> List[UseCase]:
        """
        Find new usage patterns

        Algorithm:
        1. Extract event sequences (temporal mining)
        2. Find frequent patterns (min_support=0.05)
        3. Filter out known patterns
        4. Convert to use case descriptions
        """

        # 1. Build sequences (service call chains)
        sequences = []
        for workflow in group_by_workflow(events):
            seq = extract_sequence(workflow)
            sequences.append(seq)

        # 2. Frequent pattern mining
        patterns = apriori_algorithm(
            sequences,
            min_support=self.min_support
        )

        # 3. Filter new patterns
        known = load_known_patterns()
        new_patterns = [p for p in patterns if p not in known]

        # 4. Convert to use cases
        use_cases = []
        for pattern in new_patterns:
            use_case = {
                'pattern': pattern,
                'frequency': pattern.support,
                'services': pattern.services,
                'description': await generate_description(pattern),
                'confidence': calculate_confidence(pattern)
            }
            use_cases.append(use_case)

        return use_cases

    async def detect_edge_cases(self, workflows: List[Workflow]) -> List[EdgeCase]:
        """
        Find rare but successful patterns

        Algorithm:
        1. Statistical outlier detection
        2. Filter for successful completions
        3. Check if truly new (not just errors)
        """

        # Isolation Forest for anomaly detection
        outliers = IsolationForest().fit_predict(workflows)

        # Keep only successful outliers
        edge_cases = []
        for workflow in workflows[outliers == -1]:
            if workflow.status == "completed":
                edge_cases.append({
                    'workflow': workflow,
                    'rarity_score': calculate_rarity(workflow),
                    'value': assess_business_value(workflow)
                })

        return edge_cases

    async def detect_integration_patterns(self, api_logs: List[APICall]) -> List[Integration]:
        """
        Find popular service integrations

        Algorithm:
        1. Build service call graph
        2. Community detection (find clusters)
        3. Rank by frequency
        """

        # Services as nodes, API calls as edges
        graph = nx.DiGraph()
        for call in api_logs:
            graph.add_edge(call.from_service, call.to_service, weight=1)

        # Find communities (frequent integrations)
        communities = nx.community.louvain_communities(graph)

        # Rank by edge weight
        integrations = []
        for community in communities:
            score = sum(graph[u][v]['weight'] for u, v in graph.edges(community))
            integrations.append({
                'services': list(community),
                'frequency': score,
                'pattern': describe_integration(community, graph)
            })

        return sorted(integrations, key=lambda x: x['frequency'], reverse=True)
```

**Input**: Event Bus data (last 7 days)
**Output**: New use cases, edge cases, integration patterns

---

### 2. Domain Analyzer

**Location**: `/intelligent-core/scenario-intelligence/domain-analyzer/`

```python
class DomainAnalyzer:
    """Classifies patterns by domain, sphere, theme"""

    def __init__(self):
        self.domains = [
            "bia", "risk", "planning", "compliance", "response",
            "exercise", "documents", "learning", "governance"
        ]
        self.spheres = [
            "healthcare", "finance", "manufacturing", "saas",
            "retail", "government", "education"
        ]
        self.themes = [
            "iso_certification", "incident_response",
            "continuous_improvement", "regulatory_compliance",
            "business_resilience"
        ]

    async def classify(self, use_case: UseCase) -> Classification:
        """Multi-label classification"""

        # 1. Domain classification (which services)
        domains = await self.classify_by_domain(use_case)

        # 2. Sphere classification (which industries)
        spheres = await self.classify_by_sphere(use_case)

        # 3. Theme classification (which business goals)
        themes = await self.classify_by_theme(use_case)

        return Classification(
            domains=domains,
            spheres=spheres,
            themes=themes,
            confidence=calculate_confidence(domains, spheres, themes)
        )

    async def classify_by_domain(self, use_case: UseCase) -> List[str]:
        """Determine which services this use case involves"""

        # Method 1: Direct (from pattern)
        services_used = use_case.pattern.services

        # Method 2: Embedding similarity
        embedding = embed(use_case.description)
        domain_scores = {}
        for domain in self.domains:
            domain_emb = get_domain_embedding(domain)
            score = cosine_similarity(embedding, domain_emb)
            domain_scores[domain] = score

        # Combine
        relevant_domains = services_used + [
            d for d, s in domain_scores.items() if s > 0.7
        ]

        return list(set(relevant_domains))

    async def classify_by_sphere(self, use_case: UseCase) -> List[str]:
        """Determine which industries use this pattern"""

        # Find organizations using this pattern
        orgs = await get_organizations_using(use_case.pattern)

        # Aggregate industry distribution
        industry_counts = Counter([org.industry for org in orgs])

        # Significant if used by 20%+ of orgs in that sphere
        total = len(orgs)
        relevant_spheres = [
            sphere for sphere, count in industry_counts.items()
            if count / total >= 0.2
        ]

        return relevant_spheres

    async def classify_by_theme(self, use_case: UseCase) -> List[str]:
        """Determine business goals/themes"""

        # Semantic similarity to theme definitions
        theme_scores = {}
        for theme in self.themes:
            theme_def = get_theme_definition(theme)
            score = await semantic_similarity(
                use_case.description,
                theme_def
            )
            theme_scores[theme] = score

        relevant_themes = [
            t for t, s in theme_scores.items() if s > 0.65
        ]

        return relevant_themes
```

**Input**: Use case from Pattern Detector
**Output**: Classification (domains, spheres, themes)

---

### 3. Predictive Engine

**Location**: `/intelligent-core/predictive/` (extend existing)

```python
class ScenarioPredictiveEngine:
    """Predicts future scenario trends"""

    async def predict_emerging_use_cases(
        self,
        time_horizon: str = "3_months"
    ) -> List[Prediction]:
        """
        Predict which scenarios will become popular

        Methods:
        1. Trend extrapolation (current growth rates)
        2. Leading indicators (early adopter signals)
        3. Cross-industry transfer (what works elsewhere)
        """

        # 1. Trend analysis
        trends = await analyze_usage_trends(last_6_months)
        extrapolated = extrapolate_trends(trends, horizon=time_horizon)

        # 2. Leading indicators
        early_signals = await detect_early_adopters()

        # 3. Cross-industry patterns
        cross_industry = await community_intelligence.get_patterns()

        # Combine predictions
        predictions = []
        for trend in extrapolated:
            prediction = {
                'use_case': trend.use_case,
                'predicted_adoption': trend.adoption_rate,
                'confidence': trend.confidence,
                'rationale': generate_rationale(
                    trend, early_signals, cross_industry
                ),
                'priority': calculate_priority(trend)
            }
            predictions.append(prediction)

        return sorted(predictions, key=lambda x: x['priority'], reverse=True)

    async def simulate_evolution(
        self,
        scenario: Scenario,
        steps: int = 5
    ) -> Evolution:
        """
        Simulate how a scenario evolves over time

        Example:
        Basic BIA → AI BIA → Continuous BIA → Predictive BIA
        """

        current = scenario
        path = [current]

        for step in range(steps):
            # What enhancements are adjacent?
            enhancements = get_adjacent_capabilities(current)

            # Which has highest value?
            best = max(enhancements, key=lambda e: e.value_score)

            # Simulate combined scenario
            next_state = combine_scenarios(current, best)
            path.append(next_state)
            current = next_state

        return Evolution(path=path, value_increase=calculate_value(path))
```

**Input**: Historical trends, early signals
**Output**: Predictions, evolution paths

---

### 4. Scenario Generator

**Location**: `/intelligent-core/scenario-intelligence/generator/`

```python
class ScenarioGenerator:
    """Generates detailed scenarios using LLM"""

    def __init__(self):
        self.llm = LLMRouter()
        self.rag = RAGPipeline()
        self.expertise_center = ExpertiseCenter()

    async def generate_scenario(
        self,
        use_case: UseCase,
        classification: Classification,
        examples: List[RealExample]
    ) -> DetailedScenario:
        """
        Generate detailed scenario document

        Quality goal: Match existing detailed scenarios
        """

        # 1. RAG: Find similar existing scenarios
        similar = await self.rag.search(
            query=use_case.description,
            collection="business_scenarios",
            top_k=5
        )

        # 2. Domain Expert: Get specialist analysis
        domain_expert = self.expertise_center.get_specialist(
            classification.domains[0]
        )
        expert_analysis = await domain_expert.analyze(use_case, examples)

        # 3. LLM: Generate detailed scenario
        prompt = self._build_generation_prompt(
            use_case, classification, examples,
            similar, expert_analysis
        )

        scenario_content = await self.llm.generate(
            prompt=prompt,
            model="claude-opus",  # Best quality
            temperature=0.3,  # More consistent
            max_tokens=4000
        )

        # 4. Validate completeness
        validated = await self.validate_scenario(scenario_content)

        # 5. Enrich with cross-references
        enriched = await self.enrich(validated, similar)

        return DetailedScenario(
            id=generate_id(),
            use_case=use_case,
            classification=classification,
            content=enriched,
            examples_count=len(examples),
            confidence=calculate_confidence(examples, expert_analysis),
            generated_at=datetime.now()
        )

    def _build_generation_prompt(self, use_case, classification, examples, similar, expert):
        """Build comprehensive prompt for LLM"""

        return f"""
        Generate a detailed business scenario document following the exact format of existing scenarios.

        **New Use Case Detected:**
        - Description: {use_case.description}
        - Pattern: {use_case.pattern}
        - Frequency: {use_case.frequency} occurrences
        - Services involved: {', '.join(use_case.services)}

        **Classification:**
        - Domains: {', '.join(classification.domains)}
        - Industries: {', '.join(classification.spheres)}
        - Themes: {', '.join(classification.themes)}
        - Confidence: {classification.confidence:.2f}

        **Real Examples** (from {len(examples)} organizations):
        {self._format_examples(examples)}

        **Similar Existing Scenarios**:
        {self._format_similar(similar)}

        **Domain Expert Analysis**:
        {expert.analysis}
        {expert.recommendations}

        **Generate the following sections:**

        1. **Business Context** (2-3 sentences explaining why this is needed)

        2. **Inputs** (detailed JSON example with realistic data)

        3. **API Endpoint** (HTTP method + path)

        4. **Process Flow** (step-by-step numbered list)

        5. **Response** (comprehensive JSON with all fields)

        6. **Events Published** (YAML format with event types and payloads)

        7. **Components Used** (list of services and their roles)

        8. **Business Value** (quantified impact, e.g., "$50K-$500K savings")

        9. **Error Handling** (common errors and responses)

        Match the quality and detail level of existing detailed scenarios.
        Use realistic data and specific examples.
        Include ISO 22301 compliance notes where relevant.
        """

    async def validate_scenario(self, content: str) -> str:
        """Validate generated scenario completeness"""

        required_sections = [
            "Business Context",
            "Inputs",
            "API Endpoint",
            "Process Flow",
            "Response",
            "Events Published",
            "Components Used",
            "Business Value"
        ]

        for section in required_sections:
            if section not in content:
                raise ValidationError(f"Missing section: {section}")

        # Check JSON validity
        if not validate_json_blocks(content):
            raise ValidationError("Invalid JSON in scenario")

        return content

    async def batch_generate(
        self,
        use_cases: List[UseCase],
        max_concurrent: int = 3
    ) -> List[DetailedScenario]:
        """Generate multiple scenarios in parallel"""

        semaphore = asyncio.Semaphore(max_concurrent)

        async def generate_limited(uc):
            async with semaphore:
                return await self.generate_scenario(uc)

        tasks = [generate_limited(uc) for uc in use_cases]
        scenarios = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failures
        successful = [s for s in scenarios if not isinstance(s, Exception)]
        failed = [s for s in scenarios if isinstance(s, Exception)]

        logger.info(f"Generated: {len(successful)}, Failed: {len(failed)}")

        return successful
```

**Input**: Use case + classification + real examples
**Output**: Detailed scenario (markdown format)

---

### 5. Orchestrator (Main Loop)

**Location**: `/intelligent-core/scenario-intelligence/orchestrator.py`

```python
class ScenarioIntelligenceOrchestrator:
    """Coordinates the entire self-learning cycle"""

    def __init__(self):
        self.pattern_detector = PatternDetectionEngine()
        self.domain_analyzer = DomainAnalyzer()
        self.predictive_engine = ScenarioPredictiveEngine()
        self.generator = ScenarioGenerator()
        self.storage = ScenarioStorage()

    async def run_continuous_cycle(self):
        """
        Continuous learning loop (runs every 24 hours)
        """

        while True:
            logger.info("🔄 Starting new learning cycle")

            try:
                # 1. COLLECT data
                events = await event_bus.get_events(last_24h)
                workflows = await workflow_intelligence.get_workflows(last_24h)
                cases = await community_intelligence.get_new_cases(last_24h)

                logger.info(f"📊 Collected: {len(events)} events, {len(workflows)} workflows")

                # 2. DETECT patterns
                new_use_cases = await self.pattern_detector.detect_new_use_cases(events)
                edge_cases = await self.pattern_detector.detect_edge_cases(workflows)

                logger.info(f"🔍 Detected: {len(new_use_cases)} new patterns")

                # 3. CLASSIFY
                classified = []
                for uc in new_use_cases:
                    classification = await self.domain_analyzer.classify(uc)
                    classified.append((uc, classification))

                # 4. PREDICT trends
                predictions = await self.predictive_engine.predict_emerging_use_cases()

                logger.info(f"🔮 Predictions: {len(predictions)}")

                # 5. GENERATE scenarios (top 10 by confidence)
                top_patterns = sorted(
                    classified,
                    key=lambda x: x[1].confidence,
                    reverse=True
                )[:10]

                scenarios = await self.generator.batch_generate(
                    [uc for uc, _ in top_patterns]
                )

                logger.info(f"✅ Generated: {len(scenarios)} scenarios")

                # 6. SAVE to file system
                timestamp = datetime.now().strftime("%Y-%m")
                for scenario in scenarios:
                    path = f"/platform-services/docs/business-scenarios/generated/{timestamp}/"
                    await self.storage.save_scenario(scenario, path)

                # 7. LOAD to RAG
                await rag_pipeline.load_scenarios(scenarios)

                logger.info(f"🧠 Loaded {len(scenarios)} to RAG")

                # 8. TEACH domain specialists
                for specialist in expertise_center.get_all():
                    await specialist.learn_from_scenarios(scenarios)

                # 9. SHARE with community (anonymized)
                anonymized = [anonymize(s, k=5) for s in scenarios]
                await community_intelligence.share_patterns(anonymized)

                # 10. METRICS
                await self.record_metrics({
                    'cycle_timestamp': datetime.now(),
                    'scenarios_generated': len(scenarios),
                    'patterns_detected': len(new_use_cases),
                    'avg_confidence': mean([s.confidence for s in scenarios])
                })

                logger.info("✅ Cycle complete. Sleeping 24 hours...")

            except Exception as e:
                logger.error(f"Cycle failed: {e}", exc_info=True)

            # Sleep 24 hours
            await asyncio.sleep(86400)
```

---

## 📁 File Organization

```
/platform-services/docs/business-scenarios/

├── ALL_USAGE_SCENARIOS_CATALOG.md     # Original catalog (328 scenarios)
├── scenarios_parsed.json               # Parsed version for RAG

├── detailed/                           # Manual detailed scenarios
│   ├── BIA_SERVICE_SCENARIOS_DETAILED.md (25 scenarios)
│   ├── RISK_SERVICE_SCENARIOS_DETAILED.md (22 scenarios)
│   └── ... (other services)

├── generated/                          # 🆕 AUTO-GENERATED
│   ├── 2025-10/                        # By month
│   │   ├── bia/
│   │   │   ├── ai-assisted-real-time-updates.md
│   │   │   └── multi-site-continuous-sync.md
│   │   ├── risk/
│   │   └── ...
│   ├── 2025-11/
│   └── index.json                      # Catalog of generated

├── evolution/                          # 🆕 EVOLUTION PATHS
│   ├── basic-bia-evolution.md
│   │   # Basic → AI → Continuous → Predictive
│   └── ...

└── simulations/                        # 🆕 SIMULATIONS
    ├── iso-journey-acceleration.md
    └── ...
```

---

## 🎯 Quality Control

### Validation Pipeline

```python
async def validate_generated_scenario(scenario: DetailedScenario) -> ValidationResult:
    """Multi-step validation"""

    checks = []

    # 1. Completeness check
    checks.append(check_all_sections_present(scenario))

    # 2. JSON validity check
    checks.append(validate_json_examples(scenario))

    # 3. Domain expert review
    expert = expertise_center.get_specialist(scenario.domain)
    checks.append(await expert.review(scenario))

    # 4. ISO compliance check (if applicable)
    if scenario.iso_clause:
        checks.append(iso_checker.validate(scenario))

    # 5. Similarity check (not duplicate)
    similar = await rag.search(scenario.title, top_k=1)
    if similar[0].score > 0.95:
        checks.append(ValidationCheck(
            name="uniqueness",
            passed=False,
            reason="Too similar to existing scenario"
        ))

    # 6. Confidence threshold
    checks.append(ValidationCheck(
        name="confidence",
        passed=scenario.confidence >= 0.7,
        reason=f"Confidence: {scenario.confidence}"
    ))

    return ValidationResult(
        scenario_id=scenario.id,
        checks=checks,
        overall_passed=all(c.passed for c in checks)
    )
```

---

## 📈 Success Metrics

### Generation Quality
```python
{
    "scenarios_generated_per_week": 10-15,
    "validation_pass_rate": 0.85,
    "expert_approval_rate": 0.90,
    "user_adoption_rate": 0.65  # Actually used in production
}
```

### System Performance
```python
{
    "pattern_detection_latency": "< 5 min",
    "scenario_generation_latency": "< 2 min per scenario",
    "total_cycle_time": "< 30 min",
    "accuracy": {
        "3_month_predictions_realized": 0.71,
        "classification_accuracy": 0.89
    }
}
```

---

## 🚀 Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [x] Pattern Detection Engine
- [x] Domain Analyzer
- [x] File organization structure
- [ ] Integration with Event Bus

**Deliverables**:
- Pattern detection working
- Classification working
- Can detect new use cases

### Phase 2: Generation (Weeks 3-4)
- [ ] Scenario Generator with LLM
- [ ] Validation pipeline
- [ ] RAG integration
- [ ] Storage system

**Deliverables**:
- First auto-generated scenarios
- Quality validation working
- Auto-load to RAG

### Phase 3: Automation (Weeks 5-6)
- [ ] Orchestrator (continuous loop)
- [ ] Predictive engine
- [ ] Metrics dashboard
- [ ] Community sharing

**Deliverables**:
- 24-hour cycle running
- Predictions generated
- Metrics tracked

### Phase 4: Optimization (Weeks 7-8)
- [ ] Fine-tuning based on feedback
- [ ] Performance optimization
- [ ] Advanced simulations
- [ ] Evolution tracking

**Deliverables**:
- Optimized generation quality
- Fast processing
- Evolution paths documented

---

## 🔗 Integration Points

### With Existing Systems

```python
# Event Bus
event_bus.subscribe("*", pattern_detector.on_event)

# Workflow Intelligence
workflow_intelligence.register_observer(pattern_detector)

# Community Intelligence
community.register_pattern_contributor(orchestrator)

# Expertise Center
for specialist in expertise_center.get_all():
    specialist.subscribe_to_new_scenarios(orchestrator)

# RAG Pipeline
rag.register_auto_loader(orchestrator.on_scenario_generated)
```

---

## 📝 Next Actions

### Immediate:
1. ✅ Design complete (this document)
2. ⏭️ Create directory structure
3. ⏭️ Implement Pattern Detector (basic version)
4. ⏭️ Test on last 7 days of data

### This Week:
1. Pattern detection working
2. Domain classification working
3. First manual generation test
4. RAG integration test

### This Month:
1. Full orchestrator loop
2. Automated generation (10-15/week)
3. Validation pipeline
4. Metrics dashboard

---

**Status**: ✅ Design Complete
**Next**: Create directory structure + implement Pattern Detector
**ETA**: 2 weeks for Phase 1
