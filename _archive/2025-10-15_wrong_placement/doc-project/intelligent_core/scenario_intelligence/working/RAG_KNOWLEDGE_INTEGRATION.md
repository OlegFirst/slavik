# RAG and Knowledge Base Integration

**Purpose**: How scenarios integrate with RAG, knowledge systems, and workflow intelligence
**Version**: 1.0.0
**Created**: 2025-10-12

---

## 🎯 Overview

Scenario Intelligence System is not just a testing tool - it's a **living knowledge base** that:
- Learns from every execution
- Provides context for AI decision-making
- Integrates with platform workflows
- Feeds RAG for intelligent recommendations

---

## 🗄️ Storage Architecture

### 1. PostgreSQL (Structured Data)

```sql
-- Location: Supabase PostgreSQL
CREATE SCHEMA scenario_intelligence;

-- All scenarios (652+ L1-L3, variable L4)
CREATE TABLE scenario_intelligence.scenarios (
  id UUID PRIMARY KEY,
  level INT NOT NULL,              -- 1, 2, 3, 4
  category TEXT,                    -- infrastructure, security, ai, etc.
  name TEXT NOT NULL,
  content JSONB NOT NULL,           -- Full scenario YAML as JSON
  version TEXT NOT NULL,
  status TEXT NOT NULL,             -- active, deprecated, archived
  metadata JSONB,                   -- Tags, compliance mappings, etc.
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Full-text search
  search_vector tsvector GENERATED ALWAYS AS (
    to_tsvector('english', name || ' ' || (content->>'description'))
  ) STORED
);

-- Execution history
CREATE TABLE scenario_intelligence.executions (
  id UUID PRIMARY KEY,
  scenario_id UUID REFERENCES scenarios(id),
  triggered_by TEXT NOT NULL,      -- scheduled, manual, event, workflow
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  status TEXT NOT NULL,             -- running, passed, failed, error
  results JSONB,                    -- Detailed results
  metrics JSONB,                    -- Performance metrics
  errors JSONB,                     -- Error details if failed

  -- Link to workflow execution
  workflow_execution_id UUID
);

-- AI learning data
CREATE TABLE scenario_intelligence.learning (
  id UUID PRIMARY KEY,
  scenario_id UUID REFERENCES scenarios(id),

  -- Detected patterns
  patterns JSONB,                   -- Common failure patterns

  -- Predictions
  predictions JSONB,                -- Future failure predictions

  -- Recommendations
  recommendations JSONB,            -- Improvement suggestions

  -- Quality metrics
  quality_score DECIMAL(3,2),       -- 0.00 to 1.00
  reliability_score DECIMAL(3,2),
  false_positive_rate DECIMAL(3,2),

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Version archive
CREATE TABLE scenario_intelligence.archive (
  id UUID PRIMARY KEY,
  scenario_id UUID REFERENCES scenarios(id),
  version TEXT NOT NULL,
  content JSONB NOT NULL,           -- Old version
  archived_at TIMESTAMPTZ DEFAULT NOW(),
  reason TEXT,                      -- Why archived
  improvements TEXT                 -- What changed
);

-- Indexes for performance
CREATE INDEX idx_scenarios_level ON scenarios(level);
CREATE INDEX idx_scenarios_category ON scenarios(category);
CREATE INDEX idx_scenarios_status ON scenarios(status);
CREATE INDEX idx_scenarios_search ON scenarios USING GIN(search_vector);
CREATE INDEX idx_executions_scenario ON executions(scenario_id);
CREATE INDEX idx_executions_status ON executions(status);
CREATE INDEX idx_executions_started ON executions(started_at DESC);
```

### 2. Qdrant (Vector Embeddings for RAG)

```python
# Qdrant collections for semantic search
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(url="http://qdrant:6333")

# Collection 1: Scenario embeddings
client.create_collection(
    collection_name="scenario_intelligence_scenarios",
    vectors_config=VectorParams(
        size=1536,  # OpenAI text-embedding-ada-002
        distance=Distance.COSINE
    )
)

# Collection 2: Execution result embeddings
client.create_collection(
    collection_name="scenario_intelligence_executions",
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE
    )
)

# Collection 3: Pattern embeddings
client.create_collection(
    collection_name="scenario_intelligence_patterns",
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE
    )
)

# Collection 4: Template embeddings
client.create_collection(
    collection_name="scenario_intelligence_templates",
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE
    )
)
```

### 3. File System (Generated Scenarios)

```
/intelligent-core/scenario-intelligence/
├── generated/
│   ├── l1/
│   │   ├── services/
│   │   │   ├── mio-manager.yaml
│   │   │   ├── analytics-specialist.yaml
│   │   │   └── ... (46 files)
│   │   └── applications/
│   │       ├── bcm-portal.yaml
│   │       ├── simulation-platform.yaml
│   │       └── ... (16 files)
│   ├── l2/
│   │   └── subsystems/
│   │       ├── database-infrastructure.yaml
│   │       ├── runtime-services.yaml
│   │       └── ... (12 files)
│   ├── l3/
│   │   └── systems/
│   │       ├── startup-orchestration.yaml
│   │       ├── resilience-system.yaml
│   │       └── ... (19 files)
│   └── l4/
│       └── workflows/
│           ├── bcm-manager-onboarding.yaml
│           ├── bia-creation-workflow.yaml
│           └── ... (variable)
└── knowledge-base/
    ├── embeddings/         # Generated embeddings
    ├── metadata/           # Scenario metadata JSON
    ├── relationships/      # Dependency graphs
    ├── patterns/           # Detected patterns
    └── best_practices/     # Extracted best practices
```

---

## 🔍 Embedding Strategy

### When to Create Embeddings

```python
class EmbeddingStrategy:
    """When and what to embed for RAG."""

    def on_scenario_generation(self, scenario):
        """Create embedding when scenario is generated."""
        text = self._prepare_text(scenario)
        embedding = self.openai.create_embedding(text)

        self.qdrant.upsert(
            collection_name="scenario_intelligence_scenarios",
            points=[{
                "id": scenario.id,
                "vector": embedding,
                "payload": {
                    "level": scenario.level,
                    "category": scenario.category,
                    "name": scenario.name,
                    "systems": scenario.systems_involved,
                    "compliance": scenario.compliance_requirements,
                    "created_at": scenario.created_at
                }
            }]
        )

    def on_scenario_execution(self, execution):
        """Create embedding from execution results."""
        text = self._prepare_execution_text(execution)
        embedding = self.openai.create_embedding(text)

        self.qdrant.upsert(
            collection_name="scenario_intelligence_executions",
            points=[{
                "id": execution.id,
                "vector": embedding,
                "payload": {
                    "scenario_id": execution.scenario_id,
                    "status": execution.status,
                    "duration": execution.duration,
                    "errors": execution.errors,
                    "insights": execution.insights
                }
            }]
        )

    def on_pattern_detection(self, pattern):
        """Create embedding from detected patterns."""
        text = self._prepare_pattern_text(pattern)
        embedding = self.openai.create_embedding(text)

        self.qdrant.upsert(
            collection_name="scenario_intelligence_patterns",
            points=[{
                "id": pattern.id,
                "vector": embedding,
                "payload": {
                    "pattern_type": pattern.type,
                    "frequency": pattern.frequency,
                    "scenarios": pattern.scenario_ids,
                    "recommendation": pattern.recommendation
                }
            }]
        )

    def _prepare_text(self, scenario):
        """Prepare text for embedding."""
        return f"""
        Scenario: {scenario.name}
        Level: {scenario.level}
        Category: {scenario.category}
        Description: {scenario.description}
        Purpose: {scenario.purpose}
        Systems: {', '.join(scenario.systems)}
        Test Scenarios: {self._summarize_tests(scenario.tests)}
        Business Objectives: {scenario.business_objectives}
        Compliance: {', '.join(scenario.compliance)}
        """.strip()
```

### What Gets Embedded

**1. Scenario Metadata** (Always)
- Name and description
- Level and category
- Systems involved
- Business objectives
- Compliance requirements

**2. Test Steps** (Summary)
- Key test actions
- Expected outcomes
- Success criteria

**3. Execution History** (After runs)
- Pass/fail patterns
- Common errors
- Performance metrics
- Business impact

**4. Learning Insights** (Continuously)
- Detected patterns
- Improvement recommendations
- Best practices discovered

---

## 🔎 RAG Use Cases

### Use Case 1: Find Similar Scenarios

```python
# User query: "database failure recovery scenarios"
query_embedding = openai.create_embedding("database failure recovery")

results = qdrant.search(
    collection_name="scenario_intelligence_scenarios",
    query_vector=query_embedding,
    limit=10,
    query_filter={
        "must": [
            {"key": "status", "match": {"value": "active"}}
        ]
    }
)

# Returns:
# - L1: PostgreSQL failure recovery
# - L1: Redis failover testing
# - L2: Database subsystem resilience
# - L3: Data storage system failure scenarios
# - Execution history: Previous database failures
```

### Use Case 2: Recommend Scenarios for New Service

```python
# New service added: payment-processor
new_service = {
    "name": "payment-processor",
    "type": "api_service",
    "dependencies": ["postgresql", "redis", "api_gateway"],
    "criticality": "critical",
    "handles_pii": True
}

# Find similar services
similar_services_query = f"""
API service that depends on PostgreSQL, Redis, and API Gateway.
Critical service that handles PII.
"""

similar = qdrant.search(
    collection_name="scenario_intelligence_scenarios",
    query_vector=openai.create_embedding(similar_services_query),
    query_filter={
        "must": [
            {"key": "level", "match": {"value": 1}},
            {"key": "category", "match": {"value": "service"}}
        ]
    },
    limit=5
)

# RAG recommends scenarios from similar services:
recommended_scenarios = [
    "API health check validation",
    "Database connection pool testing",
    "Redis cache failure handling",
    "API Gateway integration testing",
    "PII encryption validation",  # Because handles_pii=True
    "Performance under load",
    "Error handling and retry logic"
]
```

### Use Case 3: Learn from Failures

```python
# Scenario failed: l3-database-resilience-test
failed_execution = {
    "scenario_id": "l3-database-resilience-test",
    "error": "PostgreSQL failover took 5 minutes (target: 2 minutes)",
    "root_cause": "Redis connection pool exhaustion during failover"
}

# Find similar failures
similar_failures_query = f"""
Database failover failure.
Redis connection pool exhaustion.
Recovery time exceeded target.
"""

similar_failures = qdrant.search(
    collection_name="scenario_intelligence_executions",
    query_vector=openai.create_embedding(similar_failures_query),
    query_filter={
        "must": [
            {"key": "status", "match": {"value": "failed"}}
        ]
    },
    limit=10
)

# RAG analysis:
analysis = {
    "similar_failures_count": 3,
    "common_pattern": "Redis connection pool exhaustion",
    "affected_scenarios": [
        "l1-redis-connection-test",
        "l2-database-subsystem-failover",
        "l3-resilience-system-recovery"
    ],
    "recommendation": "Increase Redis connection pool size from 50 to 100",
    "confidence": 0.89
}

# Automatically improve scenarios
for scenario_id in analysis["affected_scenarios"]:
    improve_scenario(
        scenario_id=scenario_id,
        improvement="Add test: Verify Redis connection pool size > 100"
    )
```

### Use Case 4: Generate L4 Workflows with Context

```python
# AI generates L4 workflow with RAG context
def generate_l4_workflow(request):
    """Generate L4 user workflow using RAG for context."""

    # 1. Get user context
    context = {
        "workflow_name": "BCM Manager Onboarding",
        "user_role": "BCM Manager",
        "business_objective": "Train new BCM manager",
        "systems_involved": ["bcm_portal", "bia_service", "risk_service"]
    }

    # 2. RAG: Find relevant L1/L2/L3 scenarios
    context_query = f"""
    BCM Manager user workflows.
    BIA service operations.
    Risk assessment processes.
    Training and onboarding.
    """

    relevant_scenarios = qdrant.search(
        collection_name="scenario_intelligence_scenarios",
        query_vector=openai.create_embedding(context_query),
        limit=20
    )

    # 3. RAG: Find execution patterns
    execution_patterns = qdrant.search(
        collection_name="scenario_intelligence_patterns",
        query_vector=openai.create_embedding("successful onboarding patterns"),
        limit=5
    )

    # 4. Build AI prompt with RAG context
    prompt = f"""
    Generate a detailed L4 user workflow for: {context['workflow_name']}

    User Role: {context['user_role']}
    Business Objective: {context['business_objective']}

    Relevant Platform Scenarios (from RAG):
    {format_scenarios(relevant_scenarios)}

    Successful Patterns (from past executions):
    {format_patterns(execution_patterns)}

    Systems Involved:
    {context['systems_involved']}

    Generate:
    1. Complete step-by-step user journey
    2. Expected outcomes at each step
    3. Error handling scenarios
    4. Success criteria
    5. Training checkpoints

    Use the golden_standard_l4.yaml template structure.
    """

    # 5. Generate with AI
    workflow = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return workflow
```

### Use Case 5: Compliance Validation

```python
# Query: "Which scenarios cover ISO 22301 clause 8.4?"
compliance_query = "ISO 22301 clause 8.4 business continuity plans"

results = qdrant.search(
    collection_name="scenario_intelligence_scenarios",
    query_vector=openai.create_embedding(compliance_query),
    query_filter={
        "must": [
            {"key": "compliance", "match": {"any": ["ISO 22301"]}}
        ]
    },
    limit=50
)

# Group by level
coverage = {
    "L1": [s for s in results if s.payload["level"] == 1],
    "L2": [s for s in results if s.payload["level"] == 2],
    "L3": [s for s in results if s.payload["level"] == 3],
    "L4": [s for s in results if s.payload["level"] == 4]
}

# Generate compliance report
report = {
    "standard": "ISO 22301",
    "clause": "8.4",
    "requirement": "Business continuity plans must be tested",
    "coverage": {
        "L1_scenarios": len(coverage["L1"]),
        "L2_scenarios": len(coverage["L2"]),
        "L3_scenarios": len(coverage["L3"]),
        "L4_scenarios": len(coverage["L4"]),
        "total": len(results)
    },
    "compliant": len(results) > 0,
    "gaps": identify_gaps(results)
}
```

---

## 🧠 Knowledge Extraction

### Pattern Detection

```python
class PatternDetector:
    """Detect patterns from execution history."""

    def detect_failure_patterns(self):
        """Find common failure patterns."""

        # Query all failed executions
        failed = db.query("""
            SELECT scenario_id, errors, COUNT(*) as frequency
            FROM scenario_intelligence.executions
            WHERE status = 'failed'
            GROUP BY scenario_id, errors
            HAVING COUNT(*) >= 3
            ORDER BY frequency DESC
        """)

        patterns = []
        for failure in failed:
            pattern = {
                "type": "failure",
                "error": failure.errors,
                "frequency": failure.frequency,
                "scenarios": [failure.scenario_id],
                "recommendation": self._generate_recommendation(failure)
            }
            patterns.append(pattern)

        # Store patterns
        for pattern in patterns:
            # Create embedding
            embedding = openai.create_embedding(
                f"Failure pattern: {pattern['error']}"
            )

            # Store in Qdrant
            qdrant.upsert(
                collection_name="scenario_intelligence_patterns",
                points=[{
                    "id": generate_uuid(),
                    "vector": embedding,
                    "payload": pattern
                }]
            )

            # Store in PostgreSQL
            db.insert("scenario_intelligence.learning", {
                "scenario_id": pattern["scenarios"][0],
                "patterns": {"failures": [pattern]},
                "recommendations": {"text": pattern["recommendation"]}
            })

        return patterns

    def _generate_recommendation(self, failure):
        """Generate recommendation using AI."""
        prompt = f"""
        Failure pattern detected:
        Error: {failure.errors}
        Frequency: {failure.frequency}

        Generate a specific, actionable recommendation to prevent this failure.
        """

        return openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content
```

### Best Practice Extraction

```python
def extract_best_practices():
    """Extract best practices from successful scenarios."""

    # Find scenarios with 100% success rate
    successful = db.query("""
        SELECT
            s.id,
            s.name,
            s.content,
            COUNT(e.id) as execution_count,
            AVG(e.metrics->>'duration_seconds')::float as avg_duration
        FROM scenario_intelligence.scenarios s
        JOIN scenario_intelligence.executions e ON s.id = e.scenario_id
        WHERE e.status = 'passed'
        GROUP BY s.id
        HAVING COUNT(e.id) >= 10
        AND (
            SELECT COUNT(*)
            FROM scenario_intelligence.executions
            WHERE scenario_id = s.id AND status = 'failed'
        ) = 0
    """)

    best_practices = []
    for scenario in successful:
        practice = {
            "source_scenario": scenario.id,
            "practice": extract_practice_from_scenario(scenario),
            "success_rate": 1.0,
            "execution_count": scenario.execution_count,
            "reliability": "high"
        }
        best_practices.append(practice)

        # Store in knowledge base
        save_best_practice(practice)

    return best_practices
```

### Dependency Graph Construction

```python
def build_dependency_graph():
    """Build service dependency graph from scenarios."""

    graph = nx.DiGraph()

    # Extract dependencies from all scenarios
    scenarios = db.query("SELECT * FROM scenario_intelligence.scenarios")

    for scenario in scenarios:
        content = scenario.content

        # Add service node
        if "service_info" in content:
            service = content["service_info"]["name"]
            graph.add_node(service, type="service", scenario=scenario.id)

            # Add dependencies
            for dep in content.get("dependencies", {}).get("internal", []):
                graph.add_edge(service, dep, type="internal")

            for dep in content.get("dependencies", {}).get("external", []):
                graph.add_edge(service, dep, type="external")

    # Save graph
    nx.write_gpickle(graph, "knowledge-base/relationships/service_dependencies.gpickle")

    # Generate insights
    insights = {
        "most_depended_on": get_top_dependencies(graph, n=10),
        "critical_path": find_critical_path(graph),
        "single_points_of_failure": find_spofs(graph),
        "clusters": detect_clusters(graph)
    }

    return graph, insights
```

---

## 🔗 Integration with Workflow Intelligence

### Scenario as Workflow

```python
# Each scenario execution becomes a Temporal workflow
from temporalio import workflow

@workflow.defn
class ScenarioExecutionWorkflow:
    """Execute scenario as Temporal workflow."""

    @workflow.run
    async def run(self, scenario_id: str) -> dict:
        """Execute scenario."""

        # 1. Load scenario from database
        scenario = await workflow.execute_activity(
            load_scenario,
            scenario_id,
            start_to_close_timeout=timedelta(seconds=30)
        )

        # 2. Validate preconditions
        await workflow.execute_activity(
            validate_preconditions,
            scenario,
            start_to_close_timeout=timedelta(minutes=5)
        )

        # 3. Execute test scenarios (parallel where possible)
        results = await asyncio.gather(*[
            workflow.execute_activity(
                execute_test_scenario,
                test,
                start_to_close_timeout=timedelta(minutes=10)
            )
            for test in scenario.test_scenarios
        ])

        # 4. Collect metrics
        metrics = await workflow.execute_activity(
            collect_metrics,
            results,
            start_to_close_timeout=timedelta(minutes=2)
        )

        # 5. Publish results to EventBus
        await workflow.execute_activity(
            publish_results,
            {
                "scenario_id": scenario_id,
                "status": "passed" if all_passed(results) else "failed",
                "results": results,
                "metrics": metrics
            },
            start_to_close_timeout=timedelta(seconds=30)
        )

        # 6. Trigger learning if failed
        if not all_passed(results):
            await workflow.execute_child_workflow(
                ScenarioImprovementWorkflow,
                args=[scenario_id, results]
            )

        return {
            "status": "completed",
            "results": results,
            "metrics": metrics
        }
```

### Fundamental Scenarios Auto-Execute

```yaml
# In workflow_intelligence config
fundamental_scenarios:
  startup:
    scenario_id: "l3-startup-orchestration-complete"
    workflow: "scenario_execution_workflow"
    trigger: "platform_start"
    auto_execute: true
    timeout: "15 minutes"

  resilience:
    scenario_id: "l3-resilience-self-healing"
    workflow: "scenario_execution_workflow"
    trigger: "service_failure_detected"
    auto_execute: true
    timeout: "10 minutes"

  security:
    scenario_id: "l3-security-penetration-test"
    workflow: "scenario_execution_workflow"
    trigger: "cron:0 2 * * *"  # Daily at 2 AM
    auto_execute: true
    timeout: "30 minutes"
```

---

## 📊 Knowledge Graph

### Graph Structure

```python
from neo4j import GraphDatabase

class ScenarioKnowledgeGraph:
    """Build knowledge graph of scenarios."""

    def build_graph(self):
        """Build complete knowledge graph."""

        with self.driver.session() as session:
            # Create scenario nodes
            scenarios = db.query("SELECT * FROM scenario_intelligence.scenarios")
            for scenario in scenarios:
                session.run("""
                    CREATE (s:Scenario {
                        id: $id,
                        name: $name,
                        level: $level,
                        category: $category
                    })
                """, scenario._asdict())

            # Create relationships
            self._create_dependency_relationships()
            self._create_test_relationships()
            self._create_validation_relationships()
            self._create_coverage_relationships()

    def _create_dependency_relationships(self):
        """Create depends_on relationships."""
        # Example: L2 depends on L1, L3 depends on L2
        pass

    def query_coverage(self, requirement: str):
        """Query which scenarios cover a requirement."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Scenario)-[:COVERS]->(r:Requirement {name: $requirement})
                RETURN s
            """, requirement=requirement)
            return [record["s"] for record in result]
```

---

## 🎯 Summary

### Storage Strategy

| Data Type | Primary Storage | Secondary Storage | Purpose |
|-----------|----------------|-------------------|---------|
| Scenarios | PostgreSQL | Filesystem (YAML) | CRUD operations |
| Embeddings | Qdrant | - | Semantic search |
| Executions | PostgreSQL | Qdrant (summary) | History & learning |
| Patterns | PostgreSQL + Qdrant | - | Knowledge extraction |
| Dependencies | PostgreSQL | Neo4j (optional) | Graph queries |

### RAG Use Cases Summary

1. **Find Similar** - Semantic search across 652+ scenarios
2. **Recommend** - Suggest scenarios for new services
3. **Learn** - Analyze failures and improve
4. **Generate** - AI-powered L4 workflow generation
5. **Validate** - Compliance coverage verification

### Integration Points

1. **Workflow Intelligence** - Scenarios as Temporal workflows
2. **Learning System** - Continuous improvement feedback
3. **AI Office** - Context for AI decision-making
4. **Knowledge System** - ISO 22301 standards integration
5. **Simulation Service** - Technical → BCM exercise conversion

---

**Status**: ✅ Architecture Complete
**Next**: Implementation of RAG integration

