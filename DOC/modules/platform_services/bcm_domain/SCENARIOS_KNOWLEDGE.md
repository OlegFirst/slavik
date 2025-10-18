# BCM Domain Scenarios Knowledge Base

**Location**: `platform_services/bcm_domain/knowledge/scenarios/`
**Purpose**: BCM-specific scenario knowledge for AI colleagues and services

---

## Overview

This directory contains BCM scenario knowledge that:
- Feeds AI colleagues (BIA Specialist, Risk Analyst, etc.)
- Provides case studies and examples
- Links to platform-wide scenario catalog
- Supports case-based learning

---

## Architecture

```
BCM Knowledge Architecture:
┌─────────────────────────────────────────────────────────┐
│  bcm_domain/knowledge/scenarios/                        │
│  ├── bcm_scenarios_index.yaml   # Scenario index       │
│  ├── bia_cases/                 # BIA case studies     │
│  ├── risk_cases/                # Risk analysis cases  │
│  └── plan_cases/                # Plan examples        │
└─────────────────────────────────────────────────────────┘
                    ↓ indexed in
┌─────────────────────────────────────────────────────────┐
│  intelligent_core/ai_foundation/                        │
│  - RAG Pipeline (Qdrant vector DB)                     │
│  - Semantic search                                      │
│  - Case-based retrieval                                 │
└─────────────────────────────────────────────────────────┘
                    ↓ references
┌─────────────────────────────────────────────────────────┐
│  /catalogs/scenarios/                                   │
│  ├── WORKFLOW_INTELLIGENCE_BUSINESS_SCENARIOS.md        │
│  │   (BCM workflows, PDCA, benchmarking)               │
│  ├── process-framework/         # Standard processes   │
│  ├── simulation-templates/      # Simulation scenarios │
│  └── theory-of-change/          # ToC models          │
└─────────────────────────────────────────────────────────┘
```

---

## Relationship with Platform Catalog

### Catalog Reference
Primary scenario source:
```
/catalogs/scenarios/WORKFLOW_INTELLIGENCE_BUSINESS_SCENARIOS.md
```

**Contains**:
- ✅ BCM workflow scenarios (BIA, Risk Assessment, Plan Development)
- ✅ Case-based learning examples
- ✅ Benchmarking scenarios
- ✅ PDCA automation patterns
- ✅ Integration scenarios

### How This Directory Uses Catalog

1. **Index Creation**
   - `bcm_scenarios_index.yaml` references catalog scenarios
   - Maps catalog scenarios to BCM domain concepts
   - Provides metadata for RAG pipeline

2. **AI Colleague Access**
   - AI colleagues query RAG pipeline
   - RAG retrieves relevant catalog scenarios
   - Scenarios provide context for answers

3. **Case Studies**
   - Local case studies complement catalog scenarios
   - Stored in subdirectories (bia_cases, risk_cases, etc.)
   - Indexed alongside catalog scenarios

---

## Scenario Categories

### 1. BIA Scenarios
**Directory**: `bia_cases/`
**Catalog Reference**: `/catalogs/scenarios/WORKFLOW_INTELLIGENCE_BUSINESS_SCENARIOS.md#управление-bcm-workflows`

**Content**:
- Critical process identification examples
- RTO/RPO determination case studies
- Dependency mapping scenarios
- Impact assessment templates

**Example**:
```yaml
# bia_cases/financial-services-bia.yaml
case_id: "bia-001"
title: "BIA for Financial Services Company"
organization:
  industry: "Financial Services"
  size: "250-500 employees"
  revenue: "$50M-$100M"
scenario:
  description: "Payment processing outage"
  critical_process: "Payment Processing"
  rto: "4 hours"
  rpo: "15 minutes"
  impact:
    financial: "$500K/day"
    reputational: "High"
    regulatory: "PCI-DSS violation risk"
lessons_learned:
  - "Cloud redundancy critical for payment systems"
  - "RTO must account for vendor dependencies"
catalog_ref: "/catalogs/scenarios/WORKFLOW_INTELLIGENCE_BUSINESS_SCENARIOS.md#bia-workflow"
```

### 2. Risk Assessment Scenarios
**Directory**: `risk_cases/`
**Catalog Reference**: `/catalogs/scenarios/WORKFLOW_INTELLIGENCE_BUSINESS_SCENARIOS.md#risk-assessment`

**Content**:
- Threat scenario libraries
- Risk quantification examples
- Treatment strategy case studies
- Industry-specific risks

### 3. Plan Development Scenarios
**Directory**: `plan_cases/`
**Catalog Reference**: `/catalogs/scenarios/WORKFLOW_INTELLIGENCE_BUSINESS_SCENARIOS.md#plan-development`

**Content**:
- BC plan templates
- Recovery strategy examples
- Resource allocation case studies
- Testing scenarios

### 4. Exercise Scenarios
**Directory**: `exercise_cases/`
**Catalog Reference**: `/catalogs/scenarios/simulation-templates/`

**Content**:
- Tabletop exercise scenarios
- Simulation templates
- After-action review examples

---

## Integration with AI Colleagues

### How AI Colleagues Use Scenarios

1. **Query Time**
   ```python
   # User asks BIA Specialist AI
   user_query = "What should be the RTO for our payment processing?"

   # AI colleague queries RAG pipeline
   relevant_scenarios = rag_pipeline.retrieve(
       query=user_query,
       filter={"domain": "bcm", "category": "bia"},
       top_k=5
   )
   # Returns BIA cases from both local and catalog scenarios
   ```

2. **Answer Generation**
   - AI colleague receives relevant scenarios
   - Uses scenarios as context for answer
   - Cites specific case studies
   - Provides recommendations based on similar cases

3. **Case-Based Learning**
   - Similar organization scenarios retrieved
   - Benchmarking data applied
   - Lessons learned incorporated
   - Best practices recommended

---

## Scenario Index Structure

### Main Index File
**File**: `bcm_scenarios_index.yaml`

```yaml
version: "1.0"
last_updated: "2025-10-18"

# Catalog references
catalog_sources:
  - path: "/catalogs/scenarios/WORKFLOW_INTELLIGENCE_BUSINESS_SCENARIOS.md"
    sections:
      - "управление-bcm-workflows"
      - "case-based-learning"
      - "benchmarking"
      - "pdca-automation"

  - path: "/catalogs/scenarios/process-framework/"
    types:
      - "bia-templates"
      - "risk-templates"
      - "plan-templates"

  - path: "/catalogs/scenarios/simulation-templates/"
    types:
      - "tabletop-exercises"
      - "crisis-simulations"

# Local case studies
local_cases:
  bia_cases:
    count: 0  # TODO: Add cases
    path: "./bia_cases/"

  risk_cases:
    count: 0  # TODO: Add cases
    path: "./risk_cases/"

  plan_cases:
    count: 0  # TODO: Add cases
    path: "./plan_cases/"

# RAG indexing configuration
rag_indexing:
  collection_name: "bcm_scenarios"
  embedding_model: "text-embedding-3-small"
  chunk_size: 1000
  chunk_overlap: 200
  metadata_fields:
    - domain        # "bcm"
    - category      # "bia", "risk", "plan", "exercise"
    - industry      # "financial", "healthcare", etc.
    - org_size      # "small", "medium", "large"
    - source        # "catalog" or "local"
```

---

## Usage Examples

### Load Scenarios for RAG
```python
from platform_services.bcm_domain.knowledge.scenarios import load_scenario_index
from intelligent_core.ai_foundation import RAGPipeline

# Load scenario index
scenario_index = load_scenario_index()

# Initialize RAG with BCM scenarios
rag = RAGPipeline(config={
    "collection": "bcm_scenarios",
    "sources": scenario_index.get_all_sources()
})

# Index catalog + local scenarios
await rag.index_scenarios(scenario_index)
```

### Query Scenarios via AI Colleague
```python
from platform_services.bcm_domain.ai_colleagues import BIASpecialistAI

bia_ai = BIASpecialistAI(rag_pipeline=rag, config={})

# AI automatically retrieves relevant scenarios
response = await bia_ai.process_message(
    "What RTO should we use for payment processing in financial services?"
)
# Response includes references to relevant BIA case studies
```

---

## Directory Structure

```
scenarios/
├── README.md                    # This file
├── bcm_scenarios_index.yaml     # Scenario index and catalog refs
├── bia_cases/                   # BIA case studies
│   ├── financial-services-bia.yaml
│   ├── healthcare-bia.yaml
│   └── manufacturing-bia.yaml
├── risk_cases/                  # Risk assessment cases
│   ├── cyber-risk-financial.yaml
│   ├── supply-chain-risk.yaml
│   └── pandemic-risk.yaml
├── plan_cases/                  # Plan examples
│   ├── payment-recovery-plan.yaml
│   ├── data-center-recovery.yaml
│   └── supplier-contingency.yaml
├── exercise_cases/              # Exercise scenarios
│   ├── tabletop-ransomware.yaml
│   ├── tabletop-flood.yaml
│   └── simulation-power-outage.yaml
└── loaders/
    ├── __init__.py
    ├── scenario_loader.py      # Load and parse scenarios
    └── catalog_resolver.py     # Resolve catalog references
```

---

## Catalog vs Local Scenarios

### When to Use Catalog
Use `/catalogs/scenarios/` for:
- ✅ Generic BCM workflows
- ✅ Standard process frameworks
- ✅ Cross-domain scenarios
- ✅ Platform-wide simulation templates

### When to Use Local
Use `bcm_domain/knowledge/scenarios/` for:
- ✅ BCM-specific case studies
- ✅ Anonymized customer examples
- ✅ Industry-specific scenarios
- ✅ Organization templates

### Relationship
```
/catalogs/scenarios/              # Platform-wide, generic
        ↓ referenced by
bcm_domain/knowledge/scenarios/   # BCM-specific, detailed
        ↓ indexed together in
intelligent_core/ai_foundation/   # RAG pipeline, unified search
```

---

## Future Development

### Phase 1 (Current)
- ✅ Directory structure created
- ✅ Architecture defined
- ✅ Catalog integration documented
- ⏳ Scenario index YAML (TODO)
- ⏳ Catalog reference resolver (TODO)

### Phase 2 (Next)
- [ ] Add 10-15 BIA case studies
- [ ] Add 10-15 risk assessment cases
- [ ] Add 5-10 plan examples
- [ ] Implement RAG indexing
- [ ] Test AI colleague retrieval

### Phase 3 (Future)
- [ ] Case contribution workflow (allow users to add cases)
- [ ] Scenario marketplace (share scenarios)
- [ ] Multi-language scenarios
- [ ] Automated scenario generation from completed workflows

---

## Related Documentation

- **Workflow Scenarios**: `/platform_services/bcm_domain/workflows/README.md`
- **Platform Catalog**: `/catalogs/scenarios/README.md`
- **AI Foundation**: `/intelligent_core/ai_foundation/README.md`
- **AI Colleagues**: `/platform_services/bcm_domain/ai_colleagues/README.md`

---

## Status

- ✅ Directory structure created
- ✅ Integration architecture defined
- ✅ Catalog references documented
- ⏳ Scenario index YAML (pending)
- ⏳ Case studies (pending)
- ⏳ RAG indexing (pending)

**Last Updated**: 2025-10-18
**Version**: 1.0.0
