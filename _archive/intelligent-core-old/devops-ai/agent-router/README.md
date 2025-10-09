# AI Agent Router

## Overview
Intelligent service routing for BCM Platform implementing Docker AI Agent pattern with GitHub App integration.

## Extracted From
- **Source**: `/intelligent-core/orchestration/ai_agent_router.py`
- **Date**: 2025-10-04
- **Original Size**: 295 lines

## What This Module Does
- Routes AI requests to appropriate microservices based on capability
- Load balancing across multiple AI agents
- Health monitoring and automatic failover
- Request tracking and analytics via Redis
- Support for multiple agent roles (Orchestrator, Processor, Assistant, Specialist, Bridge)

## Status
**Production-Ready**

## Dependencies
- `httpx` - HTTP client for agent communication
- `redis.asyncio` - Request logging and analytics
- Python 3.11+

## Agent Roles Supported
1. **ORCHESTRATOR** - Main coordination brain (PDCA, Workflow, Decision Support)
2. **PROCESSOR** - Multi-service processor (BIA, Documents, Compliance)
3. **ASSISTANT** - Context-aware helper (PDCA Assistant)
4. **SPECIALIST** - Domain-specific expert (Document AI)
5. **BRIDGE** - External integration (GitHub App)
6. **REGISTRY** - Service discovery

## Usage Example
```python
from agent_router import AIAgentRouter, AgentCapability

router = AIAgentRouter(redis_url="redis://localhost:6379/0")

# Route a BIA analysis request
result = await router.route_request(
    capability=AgentCapability.BIA_ANALYSIS,
    request_data={"organization": "Acme Corp"},
    context={"user_id": "123", "priority": "high"}
)

# Check agent health
health_status = await router.health_check_all_agents()

# Get analytics
analytics = router.get_agent_analytics()
```

## Integration Points
- **Redis**: Request logging, analytics storage
- **Microservices**: ai_orchestrator, unified_ai, pdca_assistant, github_app, document_ai
- **EventBus**: Can be extended to publish routing events

## Next Steps
1. Add Prometheus metrics for routing performance
2. Implement circuit breaker pattern
3. Add distributed tracing (OpenTelemetry)
4. Support dynamic agent registration
