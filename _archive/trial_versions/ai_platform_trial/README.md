# AI Platform - Unified AI System

**Business-first architecture for all AI operations**

## 🎯 Philosophy

Instead of "gluing" modules together, we follow simple business logic:
- Clear management hierarchy (like a real company)
- Three business segments
- Unified standards and ecosystem

## 📊 Management Hierarchy

```
Level 0: Chief Executive AI (CEO)
         ↓
Level 1: TOP Managers (3)
         ├─ Governance Manager
         ├─ Platform Manager
         └─ Domain/BCM Manager
         ↓
Level 2: Experts (18 total)
         ├─ Governance (3 experts)
         ├─ Platform (5 experts)
         └─ Domain/BCM (10 experts)
         ↓
Level 3: Tools (~30)
         ├─ Governance tools
         ├─ Platform tools
         └─ Domain tools
         ↓
Level 4: Organs (~15)
         ├─ Governance organs
         ├─ Platform organs
         └─ Domain organs
```

## 🏢 Three Segments

### 1. GOVERNANCE
**Система управления**
- Compliance, audit, governance
- ISO standards, regulations
- Policies and frameworks

**Experts:**
- Compliance Auditor
- Governance Expert
- Audit Manager

### 2. PLATFORM
**Система платформы (архитектура)**
- Workflow automation
- Architecture and orchestration
- Deployment and performance
- Machine learning

**Experts:**
- Workflow Expert
- MIO Expert
- Deployment Expert
- Performance Expert
- Learning Expert

### 3. DOMAIN (BCM)
**Программная часть (доменная - ВСМ)**
- Business Continuity Management
- BIA, Risk, Planning
- Incidents, Exercises
- Knowledge and Collective Intelligence

**Experts:**
- BIA Specialist
- Risk Analyst
- Planning Specialist
- Incident Expert
- Exercise Designer
- Supply Chain Expert
- Collective Expert
- Documentation Expert
- Knowledge Manager
- Predictive Analyst

## 🔧 Components

### Base Classes
- **BaseExpert** - User-facing consultants
- **BaseTool** - Structured operations
- **BaseOrgan** - Heavy computations (библиотека/должностные инструкции)
- **BaseManager** - Segment coordinators

### Chief Executive AI
- Analyzes user intent
- Routes to appropriate manager
- Monitors overall performance

### Managers
- Coordinate experts in their segment
- Select best expert for each request
- Track delegation efficiency

### Experts
- Provide advice and guidance
- Use Tools for structured operations
- Delegate to Organs for heavy work

### Tools
- Anthropic tool calling format
- Structured interfaces
- Parameter validation

### Organs
- Execution workers
- Autonomous task processing
- Like body organs doing heavy lifting

## 🚀 Usage

### Quick Start

```python
from ai_platform import create_platform

# Create platform with all components
chief = create_platform(llm_client=your_llm_client)

# Handle user request
result = await chief.handle_request(
    user_query="How do I conduct a BIA for my hospital?",
    context={
        "user_id": "user-123",
        "organization": "hospital",
        "industry": "healthcare"
    }
)

# Result includes:
# - Response from appropriate expert
# - Intent analysis
# - Routing metadata
```

### Manual Setup

```python
from ai_platform import ChiefExecutiveAI
from ai_platform.managers import GovernanceManager, PlatformManager, DomainManager

# Create managers
governance = GovernanceManager(llm_client=llm_client)
platform = PlatformManager(llm_client=llm_client)
domain = DomainManager(llm_client=llm_client)

# Add experts to managers
from ai_platform.experts.domain import BIASpecialist

bia_expert = BIASpecialist(tools=[], organs=[], llm_client=llm_client)
domain.add_expert(bia_expert)

# Create Chief
chief = ChiefExecutiveAI(
    governance_manager=governance,
    platform_manager=platform,
    domain_manager=domain,
    llm_client=llm_client
)

# Use
result = await chief.handle_request(query, context)
```

### Creating Custom Expert

```python
from ai_platform import BaseExpert

class MyExpert(BaseExpert):
    def __init__(self, tools, organs, llm_client):
        super().__init__(
            name="My Expert",
            segment="domain",  # or 'governance', 'platform'
            specialization="My specialization",
            description="What I do...",
            tools=tools,
            organs=organs,
            llm_client=llm_client
        )

    async def handle_request(self, user_query, context):
        # Use LLM for reasoning
        response = await self._query_llm(user_query, context)

        # Use a tool
        tool_result = await self.use_tool("tool_name", parameters)

        # Delegate to organ
        organ_result = await self.delegate_to_organ("organ_name", task)

        return {
            "success": True,
            "advice": response,
            "actions": [tool_result, organ_result]
        }

    def can_handle(self, user_query, context):
        # Return confidence score 0.0-1.0
        if "my_keyword" in user_query.lower():
            return 0.9
        return 0.1
```

### Creating Custom Tool

```python
from ai_platform import BaseTool, ToolParameter

class MyTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            segment="domain",
            description="What this tool does",
            parameters=[
                ToolParameter(
                    name="param1",
                    type="string",
                    description="Description",
                    required=True
                )
            ]
        )

    async def execute(self, parameters):
        # Tool logic
        result = do_something(parameters["param1"])

        return {
            "result": result
        }
```

### Creating Custom Organ

```python
from ai_platform import BaseOrgan

class MyOrgan(BaseOrgan):
    def __init__(self, llm_client):
        super().__init__(
            name="My Organ",
            segment="domain",
            function="Heavy computation",
            description="What this organ does",
            llm_client=llm_client
        )

    async def process(self, task):
        # Heavy computation logic
        result = await heavy_computation(task)

        return {
            "result": result
        }

# Start organ
organ = MyOrgan(llm_client)
await organ.start()  # Starts background workers

# Submit task
future = await organ.submit_task({"data": "..."})
result = await future  # Wait for result
```

## 📁 Structure

```
ai_platform/
├── __init__.py                 # Main exports
├── README.md                   # This file
│
├── chief/                      # Level 0
│   ├── __init__.py
│   └── chief_executive.py      # Chief Executive AI
│
├── managers/                   # Level 1
│   ├── __init__.py
│   ├── governance_manager.py   # Governance Manager
│   ├── platform_manager.py     # Platform Manager
│   └── domain_manager.py       # Domain/BCM Manager
│
├── experts/                    # Level 2
│   ├── governance/             # 3 governance experts
│   ├── platform/               # 5 platform experts
│   └── domain/                 # 10 BCM experts
│
├── tools/                      # Level 3
│   ├── governance/             # Governance tools
│   ├── platform/               # Platform tools
│   └── domain/                 # Domain/BCM tools
│
├── organs/                     # Level 4
│   ├── governance/             # Governance organs
│   ├── platform/               # Platform organs
│   └── domain/                 # Domain/BCM organs
│
└── shared/                     # Shared components
    ├── base/                   # Base classes
    │   ├── base_expert.py
    │   ├── base_tool.py
    │   ├── base_organ.py
    │   └── base_manager.py
    ├── rag/                    # RAG pipeline
    ├── ml/                     # Machine learning
    └── learning/               # Continuous learning
```

## 🎯 Design Principles

1. **Business-First**: Architecture follows business logic, not technical constraints
2. **Clear Hierarchy**: Every component knows its level and manager
3. **Segment Separation**: Three clear segments with no overlap
4. **Unified Standards**: All components use same base classes
5. **Single Ecosystem**: One module, one entry point

## 🔄 Request Flow

```
User request
    ↓
Chief Executive AI
    ├─ Analyze intent (keywords + LLM)
    └─ Determine segment
    ↓
TOP Manager (Governance/Platform/Domain)
    ├─ Select best expert
    └─ Delegate
    ↓
Expert
    ├─ Reason with LLM
    ├─ Use Tools (structured operations)
    └─ Delegate to Organs (heavy computations)
    ↓
Response to user
```

## 📊 Metrics

All components track:
- Request/execution counts
- Average response/processing time
- Success rates
- Efficiency metrics

Access via:
```python
status = chief.get_status()
# Returns full hierarchy status with metrics
```

## 🤝 Integration

This module integrates with:
- Community Intelligence (collective wisdom)
- Workflow Intelligence (self-learning workflows)
- Living Documentation (self-evolving docs)
- Collective Agents (privacy-preserving collaboration)

## 📝 Migration from Old Modules

Existing `ai-office` and `ai_experts` modules are NOT deleted.
They remain as reference and will be migrated gradually.

Organs from `ai-office` = библиотека/должностные инструкции for experts.

## 🚀 Future

- Auto-discovery of experts and tools
- Dynamic expert creation based on needs
- Cross-segment collaboration
- Continuous learning from user interactions
