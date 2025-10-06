# AI Platform - Examples

Practical examples of using the AI Platform

## 📋 Table of Contents

1. [Basic Usage](#basic-usage)
2. [Creating Experts](#creating-experts)
3. [Creating Tools](#creating-tools)
4. [Creating Organs](#creating-organs)
5. [Full Integration Example](#full-integration-example)
6. [Real-World Scenarios](#real-world-scenarios)

---

## Basic Usage

### Example 1: Simple Request

```python
from ai_platform import create_platform

# Initialize platform
chief = create_platform(llm_client=anthropic_client)

# User asks about BIA
result = await chief.handle_request(
    user_query="How do I identify critical processes for my hospital?",
    context={
        "user_id": "user-123",
        "organization_id": "hospital-456",
        "industry": "healthcare",
        "org_size": "medium"
    }
)

print(result)
# {
#     "success": True,
#     "advice": "To identify critical processes...",
#     "expert": "BIA Specialist",
#     "tools_used": ["process_identification_tool"],
#     "metadata": {
#         "intent": "domain",
#         "confidence": 0.92,
#         "response_time": 1.2,
#         "routed_to": "domain"
#     }
# }
```

### Example 2: Governance Request

```python
# User asks about ISO compliance
result = await chief.handle_request(
    user_query="What are the requirements for ISO 22301 certification?",
    context={
        "user_id": "user-123",
        "organization_id": "company-789"
    }
)

# Automatically routed to Governance Manager → Compliance Auditor
```

### Example 3: Platform Request

```python
# User asks about workflow optimization
result = await chief.handle_request(
    user_query="How can I automate my BIA workflow?",
    context={
        "user_id": "user-123",
        "current_workflow": "manual"
    }
)

# Automatically routed to Platform Manager → Workflow Expert
```

---

## Creating Experts

### Example 4: BIA Specialist

```python
from ai_platform import BaseExpert
from typing import Dict, Any

class BIASpecialist(BaseExpert):
    """
    Business Impact Analysis Specialist

    Helps users:
    - Identify critical processes
    - Calculate RTOs and RPOs
    - Map dependencies
    - Assess business impact
    """

    def __init__(self, tools, organs, llm_client):
        super().__init__(
            name="BIA Specialist",
            segment="domain",
            specialization="Business Impact Analysis",
            description="""Expert in business impact analysis.

Capabilities:
- Process identification
- RTO/RPO calculation
- Dependency mapping
- Impact assessment
- Industry-specific guidance (healthcare, finance, manufacturing)
""",
            tools=tools,
            organs=organs,
            llm_client=llm_client
        )

    async def handle_request(self, user_query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle BIA request"""

        # Step 1: Use LLM to understand request
        advice = await self._query_llm(user_query, context, temperature=0.3)

        # Step 2: Check if we need to use tools
        actions = []

        if "identify" in user_query.lower() and "process" in user_query.lower():
            # Use process identification tool
            tool_result = await self.use_tool(
                "process_identification_tool",
                {
                    "industry": context.get("industry", "general"),
                    "org_size": context.get("org_size", "medium")
                }
            )
            actions.append(tool_result)

        if "rto" in user_query.lower() or "rpo" in user_query.lower():
            # Use RTO/RPO calculator tool
            tool_result = await self.use_tool(
                "rto_calculator",
                {
                    "process_type": self._extract_process_type(user_query)
                }
            )
            actions.append(tool_result)

        # Step 3: Check if we need heavy computation from organs
        if "dependency" in user_query.lower() or "map" in user_query.lower():
            # Delegate to Impact Oracle organ for dependency mapping
            organ_result = await self.delegate_to_organ(
                "Impact Oracle",
                {
                    "organization_id": context.get("organization_id"),
                    "analyze": "dependencies"
                }
            )
            actions.append(organ_result)

        return {
            "success": True,
            "advice": advice,
            "actions": actions,
            "expert": self.name,
            "tools_used": [action.get("tool") for action in actions if "tool" in action],
            "next_steps": self._suggest_next_steps(user_query)
        }

    def can_handle(self, user_query: str, context: Dict[str, Any]) -> float:
        """Determine if this expert can handle the request"""

        query_lower = user_query.lower()

        # BIA keywords
        bia_keywords = [
            "bia", "business impact", "critical process", "rto", "rpo",
            "recovery time", "recovery point", "dependency", "impact analysis"
        ]

        matches = sum(1 for keyword in bia_keywords if keyword in query_lower)

        if matches >= 2:
            return 0.9
        elif matches == 1:
            return 0.7
        else:
            return 0.2

    def _extract_process_type(self, query: str) -> str:
        """Extract process type from query"""
        # Simple keyword extraction
        if "emergency" in query.lower() or "er" in query.lower():
            return "emergency_services"
        elif "it" in query.lower() or "technology" in query.lower():
            return "it_systems"
        elif "supply" in query.lower():
            return "supply_chain"
        else:
            return "general"

    def _suggest_next_steps(self, query: str) -> list:
        """Suggest next steps based on query"""
        return [
            "Review identified critical processes",
            "Validate RTOs with stakeholders",
            "Document dependencies",
            "Conduct risk assessment for each process"
        ]
```

### Example 5: Adding Expert to Manager

```python
from ai_platform.managers import DomainManager
from ai_platform.experts.domain import BIASpecialist
from ai_platform.tools.domain import ProcessIdentificationTool, RTOCalculator
from ai_platform.organs.domain import ImpactOracle

# Create tools
tools = [
    ProcessIdentificationTool(),
    RTOCalculator()
]

# Create organs
organs = [
    ImpactOracle(llm_client=llm_client)
]

# Create expert
bia_expert = BIASpecialist(
    tools=tools,
    organs=organs,
    llm_client=llm_client
)

# Add to manager
domain_manager = DomainManager(llm_client=llm_client)
domain_manager.add_expert(bia_expert)
```

---

## Creating Tools

### Example 6: RTO Calculator Tool

```python
from ai_platform import BaseTool, ToolParameter
from typing import Dict, Any

class RTOCalculator(BaseTool):
    """
    RTO (Recovery Time Objective) Calculator

    Calculates appropriate RTO based on:
    - Process type
    - Industry
    - Business impact
    - Regulatory requirements
    """

    def __init__(self):
        super().__init__(
            name="rto_calculator",
            segment="domain",
            description="Calculate Recovery Time Objective (RTO) for business processes",
            parameters=[
                ToolParameter(
                    name="process_type",
                    type="string",
                    description="Type of process (emergency_services, it_systems, supply_chain, etc.)",
                    required=True
                ),
                ToolParameter(
                    name="industry",
                    type="string",
                    description="Industry (healthcare, finance, manufacturing, etc.)",
                    required=False,
                    default="general"
                ),
                ToolParameter(
                    name="criticality",
                    type="string",
                    description="Criticality level (critical, high, medium, low)",
                    required=False,
                    default="high"
                )
            ]
        )

        # RTO guidelines by industry and process type
        self.rto_guidelines = {
            "healthcare": {
                "emergency_services": "4h",
                "patient_care": "4h",
                "pharmacy": "8h",
                "it_systems": "24h",
                "supply_chain": "24h",
                "administrative": "48h"
            },
            "finance": {
                "trading": "1h",
                "payment_processing": "4h",
                "customer_service": "8h",
                "it_systems": "12h",
                "administrative": "24h"
            },
            "general": {
                "critical": "4h",
                "high": "24h",
                "medium": "72h",
                "low": "1week"
            }
        }

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute RTO calculation"""

        process_type = parameters["process_type"]
        industry = parameters.get("industry", "general")
        criticality = parameters.get("criticality", "high")

        # Get RTO from guidelines
        if industry in self.rto_guidelines:
            industry_guidelines = self.rto_guidelines[industry]
            rto = industry_guidelines.get(process_type, self.rto_guidelines["general"][criticality])
        else:
            rto = self.rto_guidelines["general"][criticality]

        # Parse RTO to hours
        rto_hours = self._parse_rto_to_hours(rto)

        return {
            "rto": rto,
            "rto_hours": rto_hours,
            "process_type": process_type,
            "industry": industry,
            "criticality": criticality,
            "explanation": self._generate_explanation(process_type, industry, rto),
            "regulatory_notes": self._get_regulatory_notes(industry)
        }

    def _parse_rto_to_hours(self, rto: str) -> float:
        """Parse RTO string to hours"""
        if "h" in rto:
            return float(rto.replace("h", ""))
        elif "week" in rto:
            return float(rto.replace("week", "")) * 168
        elif "day" in rto:
            return float(rto.replace("day", "")) * 24
        else:
            return 24.0

    def _generate_explanation(self, process_type: str, industry: str, rto: str) -> str:
        """Generate explanation for RTO"""
        return f"""The recommended RTO for {process_type} in {industry} industry is {rto}.

This is based on:
- Industry best practices
- Regulatory requirements
- Typical business impact patterns
- Recovery complexity

Consider:
- Your specific business needs may differ
- Stakeholder input is critical
- Cost-benefit analysis of faster recovery
- Testing RTO feasibility
"""

    def _get_regulatory_notes(self, industry: str) -> str:
        """Get regulatory notes for industry"""
        regulatory_notes = {
            "healthcare": "HIPAA requires patient data availability. Emergency services must meet local regulations.",
            "finance": "PCI-DSS, SOX, and banking regulations may impose specific RTOs for payment processing.",
            "general": "Check ISO 22301 requirements for your organization type."
        }
        return regulatory_notes.get(industry, regulatory_notes["general"])
```

---

## Creating Organs

### Example 7: Impact Oracle Organ

```python
from ai_platform import BaseOrgan
from typing import Dict, Any
import asyncio

class ImpactOracle(BaseOrgan):
    """
    Impact Oracle Organ

    Heavy computation for:
    - Dependency mapping
    - Impact analysis
    - Cascading failure simulation
    - Resource requirement estimation
    """

    def __init__(self, llm_client, db_client=None):
        super().__init__(
            name="Impact Oracle",
            segment="domain",
            function="Business impact analysis and simulation",
            description="""Performs heavy computations for BIA:
- Analyzes process dependencies
- Simulates cascading failures
- Estimates recovery resources
- Calculates financial impact
""",
            llm_client=llm_client,
            max_concurrent_tasks=3
        )
        self.db_client = db_client

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process BIA computation task"""

        task_type = task.get("analyze")

        if task_type == "dependencies":
            return await self._analyze_dependencies(task)
        elif task_type == "impact":
            return await self._analyze_impact(task)
        elif task_type == "simulation":
            return await self._run_simulation(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def _analyze_dependencies(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze process dependencies"""

        organization_id = task.get("organization_id")

        # Step 1: Fetch organization data
        if self.db_client:
            processes = await self._fetch_processes(organization_id)
        else:
            processes = []  # Mock data

        # Step 2: Use LLM to analyze dependencies
        system_prompt = """You are analyzing business process dependencies.

Identify:
- Direct dependencies (process A requires process B)
- Indirect dependencies (process A → B → C)
- Critical paths (most important chains)
- Single points of failure
"""

        user_prompt = f"""Organization processes:
{processes}

Analyze dependencies and identify:
1. Direct dependencies
2. Critical paths
3. Single points of failure
4. Recommendations
"""

        analysis = await self._query_llm(system_prompt, user_prompt)

        # Step 3: Build dependency graph
        dependency_graph = await self._build_dependency_graph(processes)

        return {
            "dependencies": dependency_graph,
            "analysis": analysis,
            "critical_paths": self._identify_critical_paths(dependency_graph),
            "single_points_of_failure": self._identify_spof(dependency_graph)
        }

    async def _analyze_impact(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze business impact"""

        process_id = task.get("process_id")
        downtime_hours = task.get("downtime_hours", 24)

        # Simulate impact
        await asyncio.sleep(0.5)  # Simulate heavy computation

        return {
            "financial_impact": self._calculate_financial_impact(downtime_hours),
            "operational_impact": self._assess_operational_impact(downtime_hours),
            "reputational_impact": self._assess_reputational_impact(downtime_hours),
            "regulatory_impact": self._assess_regulatory_impact(downtime_hours)
        }

    async def _run_simulation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Run cascading failure simulation"""

        initial_failure = task.get("initial_failure")
        time_horizon = task.get("time_horizon", 72)  # hours

        # Simulate cascading failures
        await asyncio.sleep(1.0)  # Simulate heavy computation

        return {
            "timeline": self._simulate_timeline(initial_failure, time_horizon),
            "affected_processes": [],
            "total_impact": {},
            "recommendations": []
        }

    async def _fetch_processes(self, organization_id: str) -> list:
        """Fetch processes from database"""
        # Implementation depends on database schema
        return []

    async def _build_dependency_graph(self, processes: list) -> Dict[str, list]:
        """Build dependency graph"""
        # Simplified version
        return {}

    def _identify_critical_paths(self, graph: Dict) -> list:
        """Identify critical paths in dependency graph"""
        return []

    def _identify_spof(self, graph: Dict) -> list:
        """Identify single points of failure"""
        return []

    def _calculate_financial_impact(self, hours: float) -> Dict[str, Any]:
        """Calculate financial impact of downtime"""
        # Simplified calculation
        hourly_cost = 10000  # Example
        return {
            "total_cost": hours * hourly_cost,
            "breakdown": {
                "lost_revenue": hours * hourly_cost * 0.6,
                "recovery_costs": hours * hourly_cost * 0.3,
                "other_costs": hours * hourly_cost * 0.1
            }
        }

    def _assess_operational_impact(self, hours: float) -> str:
        """Assess operational impact"""
        if hours < 4:
            return "Minimal - Normal operations largely unaffected"
        elif hours < 24:
            return "Moderate - Some disruption to operations"
        else:
            return "Severe - Major operational disruption"

    def _assess_reputational_impact(self, hours: float) -> str:
        """Assess reputational impact"""
        if hours < 8:
            return "Low - Unlikely to affect reputation"
        elif hours < 48:
            return "Medium - May affect customer confidence"
        else:
            return "High - Significant reputational damage likely"

    def _assess_regulatory_impact(self, hours: float) -> str:
        """Assess regulatory impact"""
        if hours < 24:
            return "Low - Likely within acceptable limits"
        else:
            return "High - May violate regulatory requirements"

    def _simulate_timeline(self, initial_failure: str, hours: int) -> list:
        """Simulate failure timeline"""
        return [
            {"time": "T+0h", "event": f"{initial_failure} fails"},
            {"time": "T+2h", "event": "Dependent processes start degrading"},
            {"time": "T+4h", "event": "Cascading failures begin"},
            {"time": f"T+{hours}h", "event": "Full impact realized"}
        ]
```

---

## Full Integration Example

### Example 8: Complete Platform Setup

```python
import asyncio
from anthropic import AsyncAnthropic
from ai_platform import ChiefExecutiveAI
from ai_platform.managers import GovernanceManager, PlatformManager, DomainManager
from ai_platform.experts.domain import BIASpecialist, RiskAnalyst
from ai_platform.tools.domain import RTOCalculator, ProcessIdentificationTool
from ai_platform.organs.domain import ImpactOracle

async def setup_platform():
    """Setup complete AI Platform"""

    # Initialize LLM client
    llm_client = AsyncAnthropic(api_key="your_key_here")

    # Create tools
    rto_calc = RTOCalculator()
    process_id_tool = ProcessIdentificationTool()

    # Create organs
    impact_oracle = ImpactOracle(llm_client=llm_client)
    await impact_oracle.start()  # Start organ workers

    # Create experts
    bia_expert = BIASpecialist(
        tools=[rto_calc, process_id_tool],
        organs=[impact_oracle],
        llm_client=llm_client
    )

    risk_expert = RiskAnalyst(
        tools=[],
        organs=[],
        llm_client=llm_client
    )

    # Create managers
    governance_mgr = GovernanceManager(llm_client=llm_client)
    platform_mgr = PlatformManager(llm_client=llm_client)
    domain_mgr = DomainManager(llm_client=llm_client)

    # Add experts to domain manager
    domain_mgr.add_expert(bia_expert)
    domain_mgr.add_expert(risk_expert)

    # Create Chief Executive AI
    chief = ChiefExecutiveAI(
        governance_manager=governance_mgr,
        platform_manager=platform_mgr,
        domain_manager=domain_mgr,
        llm_client=llm_client
    )

    return chief, impact_oracle

async def main():
    """Main example"""

    # Setup
    chief, impact_oracle = await setup_platform()

    # Example requests
    requests = [
        {
            "query": "How do I calculate RTO for my hospital emergency department?",
            "context": {"user_id": "user-1", "industry": "healthcare"}
        },
        {
            "query": "What are ISO 22301 requirements?",
            "context": {"user_id": "user-2"}
        },
        {
            "query": "How can I optimize my workflow?",
            "context": {"user_id": "user-3"}
        }
    ]

    # Process requests
    for req in requests:
        print(f"\n{'='*60}")
        print(f"Query: {req['query']}")
        print(f"{'='*60}")

        result = await chief.handle_request(req["query"], req["context"])

        print(f"Success: {result['success']}")
        print(f"Routed to: {result['metadata']['routed_to']}")
        print(f"Confidence: {result['metadata']['confidence']:.2f}")
        print(f"Response time: {result['metadata']['response_time']:.2f}s")

    # Cleanup
    await impact_oracle.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Real-World Scenarios

### Example 9: Hospital BIA Workflow

```python
async def hospital_bia_workflow(chief):
    """Complete BIA workflow for hospital"""

    context = {
        "user_id": "hospital-admin-1",
        "organization_id": "hospital-123",
        "industry": "healthcare",
        "org_size": "large"
    }

    # Step 1: Identify critical processes
    result1 = await chief.handle_request(
        "Help me identify critical processes for a 500-bed hospital",
        context
    )
    print("Critical processes:", result1.get("processes"))

    # Step 2: Calculate RTOs
    result2 = await chief.handle_request(
        "Calculate RTO for emergency department operations",
        context
    )
    print("RTO:", result2.get("rto"))

    # Step 3: Analyze dependencies
    result3 = await chief.handle_request(
        "Map dependencies for emergency department",
        context
    )
    print("Dependencies:", result3.get("dependencies"))

    # Step 4: Assess impact
    result4 = await chief.handle_request(
        "What's the impact of 24-hour emergency department downtime?",
        context
    )
    print("Impact:", result4.get("impact"))

    return {
        "processes": result1,
        "rto": result2,
        "dependencies": result3,
        "impact": result4
    }
```

### Example 10: Multi-Segment Request

```python
async def compliance_and_technical(chief):
    """Request involving multiple segments"""

    context = {"user_id": "user-1"}

    # This request involves both governance and platform
    result = await chief.handle_request(
        "How do I implement ISO 22301-compliant automated workflows?",
        context
    )

    # Chief will route to best segment
    # Could route to Governance (ISO compliance)
    # Or Platform (automated workflows)
    # Or coordinate between both

    return result
```

---

## 🎯 Key Takeaways

1. **Chief routes automatically** - No need to know which expert to use
2. **Experts use tools and organs** - Separation of concerns
3. **Organs handle heavy work** - Keep experts fast and responsive
4. **All components track metrics** - Monitor performance
5. **Easy to extend** - Add new experts, tools, organs following patterns

## 📚 Next Steps

- Check [README.md](README.md) for architecture overview
- See base classes in `shared/base/` for implementation details
- Look at existing experts in `experts/` for more examples
