# Orchestrator - Unified Architecture

**Version:** 2.0.0
**Type:** Consolidated Microservice
**Sources:** 8 → 1
**Philosophy:** Single Responsibility, Layered Architecture, Zero Loss

---

## 🏗️ ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                    UNIFIED CONTROLLER                        │
│            (Coordinates all orchestrators)                   │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┴────────┬──────────────┬─────────────┐
    │                 │              │             │
┌───▼────┐    ┌──────▼─────┐  ┌────▼──────┐  ┌──▼────────┐
│Platform│    │     AI     │  │ Scenario  │  │ Workflow  │
│Orch.   │    │  Orch.     │  │  Orch.    │  │  Orch.    │
└───┬────┘    └──────┬─────┘  └────┬──────┘  └──┬────────┘
    │                │              │             │
    └────────────────┴──────────────┴─────────────┘
                     │
            ┌────────▼─────────┐
            │   CORE LAYER     │
            │  (Shared Logic)  │
            └────────┬─────────┘
                     │
            ┌────────▼─────────┐
            │  INTEGRATION     │
            │     LAYER        │
            └──────────────────┘
```

---

## 📦 MODULE STRUCTURE

```
orchestrator/
│
├── core/                           # Shared orchestration logic
│   ├── __init__.py
│   ├── base_orchestrator.py       # BaseOrchestrator abstract class
│   ├── service_registry.py        # Service discovery & registry
│   ├── health_monitor.py          # Health check system
│   ├── event_coordinator.py       # EventBus coordination
│   └── docker_manager.py          # Docker API wrapper
│
├── platform/                       # Platform orchestration
│   ├── __init__.py
│   ├── service_groups.py          # ServiceGroup definitions
│   ├── platform_orchestrator.py   # Main platform orchestrator
│   └── deployment_manager.py      # Deployment logic (merged from deployer)
│
├── ai/                             # AI orchestration
│   ├── __init__.py
│   ├── ai_orchestrator.py         # Main AI coordinator
│   ├── intelligence_engine.py     # BCM intelligence + rule engine
│   ├── devops_engine.py           # AI DevOps automation
│   ├── claude_engine.py           # Anthropic Claude integration
│   ├── agent_router.py            # Multi-agent routing
│   └── model_selector.py          # Model selection logic
│
├── scenario/                       # Scenario orchestration
│   ├── __init__.py
│   ├── scenario_orchestrator.py   # Scenario generation
│   ├── learning_engine.py         # Exercise learning system
│   └── jaamsim_config.py          # JaamSim configuration
│
├── workflow/                       # Workflow orchestration (future)
│   ├── __init__.py
│   ├── bpmn_orchestrator.py       # BPMN workflows
│   └── task_scheduler.py          # Task scheduling
│
├── control_center/                 # Unified control
│   ├── __init__.py
│   ├── unified_controller.py      # Master controller
│   ├── dashboard_api.py           # Dashboard data
│   └── monitoring_dashboard.py    # Monitoring UI data
│
├── integrations/                   # External integrations
│   ├── __init__.py
│   ├── eventbus.py                # EventBus client
│   ├── docker_client.py           # Docker wrapper
│   ├── redis_client.py            # Redis client
│   ├── postgres_client.py         # PostgreSQL client
│   ├── anthropic_client.py        # Claude API client
│   ├── supabase_client.py         # Supabase client
│   ├── github_client.py           # GitHub API client
│   └── odoo_client.py             # Odoo integration
│
├── api/                            # REST API layer
│   ├── __init__.py
│   ├── platform_routes.py         # Platform endpoints
│   ├── ai_routes.py               # AI endpoints
│   ├── scenario_routes.py         # Scenario endpoints
│   ├── deployment_routes.py       # Deployment endpoints
│   └── orchestration_routes.py    # Orchestration endpoints
│
├── models/                         # Data models
│   ├── __init__.py
│   ├── platform_models.py         # Platform entities
│   ├── ai_models.py               # AI entities
│   ├── scenario_models.py         # Scenario entities
│   └── deployment_models.py       # Deployment entities
│
├── config/
│   ├── __init__.py
│   └── settings.py                # Configuration management
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── main.py                         # FastAPI application entry
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container definition
├── docker-compose.yml              # Local development
├── README.md                       # Documentation
├── INTEGRATION_SPEC.md             # ✅ Created
├── CODE_INVENTORY.md               # ✅ Created
├── ARCHITECTURE.md                 # ✅ This file
└── QUALITY_CHECKLIST.md            # To be created
```

---

## 🎯 LAYER RESPONSIBILITIES

### Layer 1: CORE (Foundation)

**Purpose:** Shared logic for all orchestrators

#### 1.1 BaseOrchestrator (Abstract Class)

```python
class BaseOrchestrator(ABC):
    """Base class for all orchestrators"""

    def __init__(self):
        self.service_registry = ServiceRegistry()
        self.eventbus = EventBusClient()
        self.health_monitor = HealthMonitor()
        self.docker_manager = DockerManager()
        self.running = False

    @abstractmethod
    async def start(self) -> None:
        """Start the orchestrator"""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the orchestrator"""
        pass

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        pass

    async def publish_event(self, event: Event) -> None:
        """Publish event to EventBus"""
        await self.eventbus.publish(event)

    async def register_service(self, service: Service) -> None:
        """Register service in registry"""
        await self.service_registry.register(service)
```

#### 1.2 ServiceRegistry

```python
class ServiceRegistry:
    """Service discovery and registration"""

    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.redis_client = None

    async def register(self, service: Service) -> None:
        """Register a service"""
        self.services[service.name] = service
        await self._persist_to_redis(service)

    async def unregister(self, service_name: str) -> None:
        """Unregister a service"""
        pass

    async def get_service(self, service_name: str) -> Optional[Service]:
        """Get service by name"""
        return self.services.get(service_name)

    async def list_services(self, filters: Dict = None) -> List[Service]:
        """List all services"""
        pass

    async def get_dependencies(self, service_name: str) -> List[str]:
        """Get service dependencies"""
        pass
```

#### 1.3 HealthMonitor

```python
class HealthMonitor:
    """Health monitoring for all services"""

    def __init__(self):
        self.checks: Dict[str, HealthCheck] = {}
        self.monitoring = False

    async def register_check(self, check: HealthCheck) -> None:
        """Register health check"""
        pass

    async def run_check(self, service_name: str) -> HealthStatus:
        """Run health check for service"""
        pass

    async def monitor_continuously(self, interval: int = 30) -> None:
        """Continuous health monitoring"""
        while self.monitoring:
            for service_name in self.checks.keys():
                status = await self.run_check(service_name)
                if status.healthy == False:
                    await self._handle_unhealthy(service_name, status)
            await asyncio.sleep(interval)

    async def _handle_unhealthy(self, service_name: str, status: HealthStatus) -> None:
        """Handle unhealthy service"""
        pass
```

#### 1.4 EventCoordinator

```python
class EventCoordinator:
    """EventBus coordination and routing"""

    def __init__(self):
        self.eventbus_client = None
        self.handlers: Dict[str, List[Callable]] = {}

    async def subscribe(self, event_pattern: str, handler: Callable) -> None:
        """Subscribe to event pattern"""
        pass

    async def publish(self, event: Event) -> None:
        """Publish event"""
        await self.eventbus_client.publish(event)

    async def route_event(self, event: Event) -> None:
        """Route event to appropriate handlers"""
        pass
```

#### 1.5 DockerManager

```python
class DockerManager:
    """Docker API wrapper"""

    def __init__(self):
        self.client = docker.from_env()

    async def start_container(self, service_name: str) -> bool:
        """Start Docker container"""
        pass

    async def stop_container(self, service_name: str) -> bool:
        """Stop Docker container"""
        pass

    async def restart_container(self, service_name: str) -> bool:
        """Restart Docker container"""
        pass

    async def get_container_status(self, service_name: str) -> ContainerStatus:
        """Get container status"""
        pass

    async def get_container_logs(self, service_name: str, tail: int = 100) -> List[str]:
        """Get container logs"""
        pass
```

---

### Layer 2: SPECIALIZED ORCHESTRATORS

#### 2.1 PlatformOrchestrator

**Source:** #1 + #4 (merged)
**Purpose:** Infrastructure lifecycle management

```python
class PlatformOrchestrator(BaseOrchestrator):
    """Platform infrastructure orchestrator"""

    def __init__(self):
        super().__init__()
        self.redis_client = None
        self.pg_pool = None
        self.groups = self._define_service_groups()

    def _define_service_groups(self) -> Dict[str, ServiceGroup]:
        """Define service groups with dependencies"""
        return {
            'foundation': ServiceGroup(
                name='foundation',
                services=['postgres', 'redis', 'rabbitmq'],
                dependencies=[]
            ),
            'infrastructure': ServiceGroup(
                name='infrastructure',
                services=['eventbus', 'unified_database_gateway', 'unified_api_gateway'],
                dependencies=['foundation']
            ),
            'business': ServiceGroup(
                name='business',
                services=['odoo', 'bia_engine', 'compliance_checker', 'bpmn_service'],
                dependencies=['foundation', 'infrastructure']
            ),
            'intelligence': ServiceGroup(
                name='intelligence',
                services=['ai_orchestrator', 'ai_control_center', 'digital_twin'],
                dependencies=['foundation', 'infrastructure']
            ),
            'applications': ServiceGroup(
                name='applications',
                services=['admin_panel', 'web_portal', 'mobile_backend'],
                dependencies=['foundation', 'infrastructure', 'business', 'intelligence']
            )
        }

    async def start(self) -> None:
        """Start platform - level by level"""
        await self.connect_services()
        await self.initialize_database()

        # Start groups in dependency order
        await self.start_group('foundation')
        await self.start_group('infrastructure')

        # Parallel start for independent groups
        await asyncio.gather(
            self.start_group('business'),
            self.start_group('intelligence')
        )

        await self.start_group('applications')

        # Publish platform.ready event
        await self.publish_event(Event(
            type='platform.ready',
            data={'groups': [g.name for g in self.groups.values()]}
        ))

    async def start_group(self, group_name: str) -> None:
        """Start service group"""
        group = self.groups[group_name]

        # Wait for dependencies
        await self.wait_for_dependencies(group_name)

        # Start each service
        for service in group.services:
            await self.docker_manager.start_container(service)
            await self._wait_for_healthy(service)

        # Publish group.ready event
        await self.publish_event(Event(
            type=f'group.{group_name}.ready',
            data={'services': group.services}
        ))

    async def wait_for_dependencies(self, group_name: str) -> None:
        """Wait for dependency groups"""
        group = self.groups[group_name]
        for dep_name in group.dependencies:
            dep_group = self.groups[dep_name]
            while not await dep_group.is_ready():
                await asyncio.sleep(2)

    async def monitor_platform(self) -> None:
        """Continuous platform monitoring"""
        while self.running:
            for group_name, group in self.groups.items():
                if not await group.is_ready():
                    logger.warning(f"Group {group_name} unhealthy - restarting")
                    await self.start_group(group_name)
            await asyncio.sleep(30)
```

#### 2.2 AIOrchestrator

**Sources:** #2 + #5 + #6 (merged)
**Purpose:** AI-powered decision making and automation

```python
class AIOrchestrator(BaseOrchestrator):
    """AI orchestration and intelligence"""

    def __init__(self):
        super().__init__()
        self.intelligence_engine = IntelligenceEngine()
        self.devops_engine = DevOpsEngine()
        self.claude_engine = ClaudeEngine()
        self.agent_router = AgentRouter()
        self.rules = []
        self.decisions = []

    async def start(self) -> None:
        """Start AI orchestrator"""
        await self._initialize_rules()
        await self._subscribe_to_events()
        self.running = True

    async def _initialize_rules(self) -> None:
        """Initialize orchestration rules"""
        self.rules = [
            OrchestratorRule(
                name="auto_generate_bcp",
                event_type="bcm.bia.completed",
                conditions={"has_critical_processes": True},
                actions=["GENERATE_PLAN", "SEND_NOTIFICATION"],
                priority=1
            ),
            OrchestratorRule(
                name="incident_response",
                event_type="bcm.incident.opened",
                conditions={"severity": ["high", "critical"]},
                actions=["SUGGEST_RESPONSE", "TRIGGER_WORKFLOW"],
                priority=1
            ),
            # ... more rules
        ]

    async def process_event(self, event: Event) -> None:
        """Process incoming event"""
        # Find matching rules
        matching_rules = [r for r in self.rules if r.event_type == event.type]

        for rule in matching_rules:
            if await self._check_conditions(event, rule.conditions):
                decision = await self._make_decision(event, rule)
                await self._execute_decision(decision)
                self.decisions.append(decision)

    async def _make_decision(self, event: Event, rule: OrchestratorRule) -> Decision:
        """Make AI decision"""
        # Use intelligence engine for reasoning
        reasoning = await self.intelligence_engine.analyze(event, rule)

        decision = Decision(
            id=str(uuid.uuid4()),
            event=event,
            rule=rule.name,
            reasoning=reasoning,
            confidence=0.85,
            actions=rule.actions
        )

        return decision

    async def _execute_decision(self, decision: Decision) -> None:
        """Execute decision actions"""
        for action in decision.actions:
            if action == "GENERATE_PLAN":
                await self.intelligence_engine.generate_plan(decision.event)
            elif action == "SUGGEST_RESPONSE":
                await self.intelligence_engine.suggest_response(decision.event)
            # ... more actions
```

#### 2.3 ScenarioOrchestrator

**Source:** #3
**Purpose:** BCM scenario generation and learning

```python
class ScenarioOrchestrator(BaseOrchestrator):
    """Scenario generation and learning"""

    def __init__(self):
        super().__init__()
        self.learning_engine = LearningEngine()
        self.scenario_db = {}

    async def generate_scenario(self, request: ScenarioGenerationRequest) -> Scenario:
        """Generate AI-powered scenario"""
        # Query AI orchestrator for generation
        ai_prompt = self._build_generation_prompt(request)
        ai_response = await self._query_ai_orchestrator(ai_prompt)

        # Format to scenario structure
        scenario = self._format_scenario(ai_response, request)

        # Generate JaamSim config if complex
        if request.complexity >= 4:
            scenario.jaamsim_config = self._generate_jaamsim_config(request)

        # Save to Odoo
        await self._save_to_odoo(scenario)

        return scenario

    async def collect_exercise_result(self, result: ExerciseResult) -> None:
        """Collect exercise results for learning"""
        scenario_key = f"scenario_{result.scenario_id}"

        # Update learning data
        if scenario_key not in self.scenario_db:
            self.scenario_db[scenario_key] = {
                'total_uses': 0,
                'effectiveness_scores': [],
                'patterns': {'successful': [], 'issues': []}
            }

        learning_data = self.scenario_db[scenario_key]
        learning_data['total_uses'] += 1
        learning_data['effectiveness_scores'].append(result.effectiveness_score)

        # Extract patterns
        await self.learning_engine.extract_patterns(result, learning_data)

        # Generate improvements if enough data
        if learning_data['total_uses'] >= 3:
            improvements = await self.learning_engine.generate_improvements(learning_data)
            learning_data['improvements'] = improvements

        # Notify AI orchestrator
        await self._notify_learning_update(result, learning_data)
```

---

### Layer 3: UNIFIED CONTROLLER

```python
class UnifiedController:
    """Master controller coordinating all orchestrators"""

    def __init__(self):
        self.platform = PlatformOrchestrator()
        self.ai = AIOrchestrator()
        self.scenario = ScenarioOrchestrator()
        self.workflow = WorkflowOrchestrator()  # Future
        self.eventbus = EventBusClient()

    async def start_all(self) -> None:
        """Start all orchestrators"""
        logger.info("Starting Unified Orchestrator Controller...")

        # Start platform first (infrastructure)
        await self.platform.start()

        # Start AI and scenario in parallel
        await asyncio.gather(
            self.ai.start(),
            self.scenario.start()
        )

        logger.info("All orchestrators started successfully")

    async def stop_all(self) -> None:
        """Stop all orchestrators"""
        await asyncio.gather(
            self.platform.stop(),
            self.ai.stop(),
            self.scenario.stop()
        )

    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        statuses = await asyncio.gather(
            self.platform.get_status(),
            self.ai.get_status(),
            self.scenario.get_status()
        )

        return {
            'platform': statuses[0],
            'ai': statuses[1],
            'scenario': statuses[2],
            'timestamp': datetime.utcnow().isoformat()
        }
```

---

## 🔌 INTEGRATION LAYER

### EventBus Integration

```python
class EventBusClient:
    """EventBus client for pub/sub"""

    def __init__(self):
        self.redis_client = None
        self.http_client = None
        self.subscribers = {}

    async def connect(self) -> None:
        """Connect to EventBus"""
        self.redis_client = await redis.from_url(REDIS_URL)
        self.http_client = httpx.AsyncClient()

    async def subscribe(self, pattern: str, handler: Callable) -> None:
        """Subscribe to event pattern"""
        pubsub = self.redis_client.pubsub()
        await pubsub.psubscribe(pattern)

        async for message in pubsub.listen():
            if message['type'] == 'pmessage':
                event = Event.from_json(message['data'])
                await handler(event)

    async def publish(self, event: Event) -> None:
        """Publish event"""
        await self.http_client.post(
            f"{EVENTBUS_URL}/api/events/publish",
            json=event.dict()
        )
```

---

## 📊 DATA FLOW

### 1. Platform Startup Flow

```
User/Script
    │
    ▼
UnifiedController.start_all()
    │
    ├──> PlatformOrchestrator.start()
    │       ├──> start_group('foundation')
    │       │       ├──> docker-compose up postgres
    │       │       ├──> docker-compose up redis
    │       │       └──> docker-compose up rabbitmq
    │       ├──> start_group('infrastructure')
    │       ├──> start_group('business') ║ parallel
    │       ├──> start_group('intelligence') ║
    │       └──> start_group('applications')
    │
    ├──> AIOrchestrator.start()
    │       ├──> Initialize rules
    │       └──> Subscribe to events
    │
    └──> ScenarioOrchestrator.start()
            └──> Load learning data
```

### 2. AI Decision Flow

```
Event Published (bcm.bia.completed)
    │
    ▼
AIOrchestrator.process_event()
    │
    ├──> Find matching rules
    ├──> Check conditions
    ├──> Make decision (AI reasoning)
    │       └──> IntelligenceEngine.analyze()
    ├──> Store decision
    └──> Execute actions
            ├──> GENERATE_PLAN
            │       └──> Generate BCP draft
            └──> SEND_NOTIFICATION
                    └──> Notify stakeholders
```

### 3. Scenario Learning Flow

```
Exercise Completed
    │
    ▼
ScenarioOrchestrator.collect_exercise_result()
    │
    ├──> Update learning database
    ├──> Extract patterns (LearningEngine)
    ├──> Calculate metrics
    ├──> Generate improvements (if data >= 3)
    │       └──> Query AI Orchestrator for suggestions
    └──> Notify AI Orchestrator
            └──> Cross-service learning
```

---

## 🔒 SECURITY & AUTH

### Authentication Flow

```python
# GitHub JWT exchange (for Copilot users)
GitHubTokenManager.exchange_github_token(jwt)
    └──> Validate JWT signature
    └──> Extract user data
    └──> Create internal token
    └──> Store in Redis
    └──> Return internal token

# Token verification middleware
async def verify_token(request: Request):
    token = request.headers.get("Authorization")
    user = await token_manager.get_user_from_token(token)
    if not user:
        raise HTTPException(401)
    return user
```

---

## 📈 MONITORING & OBSERVABILITY

### Health Checks

```python
# Service-level health
GET /health
{
    "status": "healthy",
    "orchestrators": {
        "platform": "running",
        "ai": "running",
        "scenario": "running"
    },
    "services": {
        "postgres": "healthy",
        "redis": "healthy",
        ...
    }
}

# Detailed status
GET /status
{
    "platform": {
        "groups": {
            "foundation": "ready",
            "infrastructure": "ready",
            ...
        },
        "services": {...}
    },
    "ai": {
        "rules_active": 5,
        "decisions_pending": 2,
        "agents_healthy": true
    },
    "scenario": {
        "scenarios_generated": 42,
        "avg_effectiveness": 8.5
    }
}
```

---

## 🚀 DEPLOYMENT

### Docker Compose

```yaml
version: '3.8'

services:
  orchestrator:
    build: .
    container_name: bcm-orchestrator
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - POSTGRES_URL=postgresql://user:pass@postgres:5432/bcm
      - EVENTBUS_URL=http://eventbus:8001
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - SUPABASE_URL=${SUPABASE_URL}
    depends_on:
      - redis
      - postgres
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped
```

---

## ✅ QUALITY METRICS

### Code Quality
- Type hints: 100%
- Docstrings: 100% (public API)
- Test coverage: >80%
- Linting: pylint score >9.0

### Performance
- Platform startup: <5 minutes
- AI decision latency: <500ms
- Event processing: <100ms
- Health check interval: 30s

### Reliability
- Auto-restart on failure
- Graceful degradation
- Circuit breakers on external calls
- Retry logic with exponential backoff

---

**Architecture Status:** ✅ Complete
**Next Step:** BUILD - implement modules one by one