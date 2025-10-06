# Expertise Center

AI Infrastructure for domain expertise management. Provides centralized AI orchestration, tools, RAG, ML, and learning capabilities for all AI components across the platform.

## Architecture

### Layer 2: AI Management & Domain Expertise

```
expertise-center/
├── core/                          # AI Orchestration
│   ├── chief_executive.py         # Main AI orchestrator
│   ├── domain_loader.py           # Dynamic domain plugin loader
│   └── expert_registry.py         # Central expert registry
│
├── domains/                       # Domain Plugins (Plug & Play)
│   │
│   └── bcm/                       # BCM Domain
│       ├── experts/               # BCM experts (bia, risk, compliance, etc.)
│       ├── tools/                 # BCM-specific tools
│       ├── organs/                # BCM LLM analyzers
│       ├── knowledge/             # ISO 22301, standards
│       └── services/              # BCM service integrations
│
└── shared/                        # AI Infrastructure (for ALL domains)
    ├── rag/                       # RAG pipeline
    ├── ml/                        # ML models
    └── learning/                  # Self-learning engine
```

## Core Components

### ChiefExecutiveAI

Main AI orchestrator that:
1. Analyzes user requests
2. Detects domain and expertise area
3. Routes to appropriate expert via registry
4. Monitors and learns from interactions

**Usage:**
```python
from expertise_center.core import ChiefExecutiveAI, DomainLoader, ExpertRegistry

# Setup
registry = ExpertRegistry()
loader = DomainLoader(registry)
loader.load_all_domains()

# Create orchestrator
chief = ChiefExecutiveAI(registry, loader, llm_client=None)

# Handle request
result = await chief.handle_request(
    user_query="Calculate BIA for payment processing",
    context={"organization": "acme_corp", "user_id": "user123"}
)
```

### DomainLoader

Dynamically loads domain plugins from `domains/` directory:
- Discovers available domains
- Loads experts, tools, organs, knowledge
- Registers with ExpertRegistry
- Supports hot-reload for development

**Usage:**
```python
from expertise_center.core import DomainLoader, ExpertRegistry

registry = ExpertRegistry()
loader = DomainLoader(registry)

# Discover and load all domains
domains = loader.load_all_domains()

# Or load specific domain
bcm_info = loader.load_domain("bcm")
```

### ExpertRegistry

Central registry for all domain experts:
- Stores experts in format: `{domain}.{expertise}` → Expert class
- Supports search by capability, domain, or query
- Tracks statistics and metadata

**Usage:**
```python
from expertise_center.core import ExpertRegistry

registry = ExpertRegistry()

# Register expert
registry.register_expert(
    domain="bcm",
    expertise="bia",
    expert_class=BIASpecialist,
    capabilities=["business_impact_analysis", "criticality_assessment"],
    tools=["BIATool", "DependencyMapper"]
)

# Retrieve expert
expert_class = registry.get_expert("bcm", "bia")

# Search
experts = registry.search_experts("risk analysis", domain="bcm")
```

## Domain Plugins

### Creating a New Domain

1. **Create domain directory:**
```bash
mkdir -p expertise-center/domains/finance/{experts,tools,organs,knowledge}
```

2. **Create domain expert:**
```python
# domains/finance/experts/audit_specialist.py

class AuditSpecialist:
    """Finance audit expert"""

    capabilities = ["financial_audit", "compliance_check"]
    tools = ["AuditTool", "ComplianceTool"]

    async def handle(self, query, context):
        # Implementation
        return {"success": True, "data": ...}
```

3. **Load domain:**
```python
loader.load_domain("finance")
# Expert automatically registered as "finance.audit_specialist"
```

### BCM Domain (Example)

The BCM domain provides Business Continuity Management expertise:

- **Experts**: BIA, Risk, Compliance, Response, Planning, etc.
- **Tools**: BIA analysis, dependency mapping, risk assessment
- **Organs**: LLM-based analyzers for deep analysis
- **Knowledge**: ISO 22301, industry standards

## Shared AI Infrastructure

### RAG Pipeline (`shared/rag/`)

Retrieval-Augmented Generation for all domains:
- Hybrid search (semantic + keyword)
- Re-ranking
- Context assembly

### ML Models (`shared/ml/`)

Machine learning capabilities:
- Predictive models (Random Forest, Gradient Boosting)
- Anomaly detection
- Training pipelines

### Learning System (`shared/learning/`)

Self-learning engine:
- Pattern extraction
- Rule generation
- Continuous improvement

## Initialization

### Quick Start

```python
from expertise_center.initialize import initialize_expertise_center

# Auto-load all domains
chief = initialize_expertise_center(
    llm_client=None,  # Optional
    auto_load_domains=True
)

# Handle request
result = await chief.handle_request(
    user_query="Calculate BIA for payment processing",
    context={"organization": "acme", "user_id": "user123"}
)
```

### Manual Setup

```python
from expertise_center.core import ChiefExecutiveAI, DomainLoader, ExpertRegistry

# Create components
registry = ExpertRegistry()
loader = DomainLoader(registry)

# Load specific domains
loader.load_domain("bcm")
loader.load_domain("finance")

# Create orchestrator
chief = ChiefExecutiveAI(registry, loader)

# Ready to use
status = chief.get_status()
```

## How It Works

### Request Flow

```
1. User Request
   "Calculate BIA for payment processing"
        ↓
2. ChiefExecutiveAI.handle_request()
   - Analyzes query
   - Detects: domain="bcm", expertise="bia"
        ↓
3. ExpertRegistry.get_expert("bcm", "bia")
   - Returns BIASpecialist class
        ↓
4. Instantiate expert with domain tools/organs/knowledge
        ↓
5. Expert.handle(query, context)
   - Uses BCM tools
   - Uses shared RAG/ML
        ↓
6. Return result with metadata
```

### Domain Detection

1. **Keyword-based** (fast):
   - Matches query against domain keywords
   - Calculates confidence score

2. **LLM-based** (fallback):
   - Uses LLM when keywords don't match
   - More accurate but slower

### Expert Instantiation

DomainLoader provides domain-specific dependencies:
- Tools from `domains/{domain}/tools/`
- Organs from `domains/{domain}/organs/`
- Knowledge from `domains/{domain}/knowledge/`

## Integration

### With coordination-center (Layer 0)

```python
# coordination-center receives intent
intent = {"action": "calculate_bia", "params": {...}}

# Converts to query
query = "Calculate BIA for payment processing"

# Sends to expertise-center
result = await chief_executive.handle_request(query, context)
```

### With platform-core (Layer 1)

Experts use platform-core services:
- Workflow engine for orchestration
- Case library for best practices
- Learning system for improvement

### With MEGA-BRAIN (Layer 3)

MEGA-BRAIN monitors via tentacles:
- Observes all expert interactions
- Identifies patterns
- Suggests improvements

## Development

### Adding New Expert to BCM

1. Create expert file:
```python
# domains/bcm/experts/new_expert.py

class NewExpert:
    capabilities = ["capability1", "capability2"]

    async def handle(self, query, context):
        return {"success": True}
```

2. Reload domain:
```python
loader.reload_domain("bcm")
```

Expert automatically registered as `bcm.new_expert`.

### Testing

```bash
cd expertise-center
python initialize.py
```

This will:
1. Load all domains
2. Show registry stats
3. Run test queries

## Status & Metrics

```python
# Get status
status = chief.get_status()

print(f"Total requests: {status['metrics']['total_requests']}")
print(f"Success rate: {status['metrics']['success_rate']}")
print(f"Loaded domains: {status['loaded_domains']}")
print(f"Registry: {status['registry_stats']}")
```

## Key Benefits

1. **Modularity**: Add domains by creating a folder
2. **Centralization**: One orchestrator, one registry
3. **Shared Infrastructure**: RAG, ML, Learning for all
4. **Auto-discovery**: DomainLoader finds and loads plugins
5. **Type Safety**: ExpertInfo dataclass for metadata

## Naming Convention

**Why "Expertise Center" not "AI Experts"?**

- ❌ "AI Experts" sounds like hierarchical "top experts"
- ✅ "Expertise Center" clearly indicates it's infrastructure
- Similar to: "Coordination Center", "Learning System"
- Provides: Expert management as a service

---

**Version:** 1.0.0
**Layer:** 2 (AI Management & Domain Expertise)
**Dependencies:** Layer 0 (Infrastructure), Layer 1 (Platform Core)
