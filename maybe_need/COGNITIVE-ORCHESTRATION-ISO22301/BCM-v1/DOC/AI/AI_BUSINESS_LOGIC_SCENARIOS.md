# AI Business Logic Scenarios - BCM Platform

## 🧠 AI Components Architecture & Data Flow

### Core AI Ecosystem
```
🎯 Main Assistant (Frontend)
    ↓ communicates with
🧠 AI Orchestrator (8000) ← ГЛАВНЫЙ КОММУНИКАТОР
    ↓ routes to specialists
🤖 Unified AI (8090)     🎭 Scenario Engine (8085)    📋 PDCA Assistant (8010)
    ↓ integrates via            ↓ generates scenarios        ↓ provides context
🔧 MCP Server (8087) ← BCM TOOLS & DATA ACCESS
    ↓ connects to
💾 PostgreSQL + Redis + Odoo (BCM Data)
```

## 📊 Scenario 1: Incident Response Workflow

### Business Process Flow
```
1. 🚨 INCIDENT REPORTED (User → Frontend Assistant)
   ├── Frontend sends to AI Orchestrator (8000)
   └── "Критический сбой базы данных клиентского сервиса"

2. 🧠 AI ORCHESTRATOR DECISION (8000)
   ├── Calls MCP Server: bcm_incident_classify
   ├── Routes to Unified AI (8090) for analysis
   ├── Routes to PDCA Assistant (8010) for context
   └── Coordinates response

3. 🔧 MCP SERVER TOOLS (8087)
   ├── bcm_incident_classify(description) → category: "technology", severity: "critical"
   ├── bcm_process_analyze(affected_processes) → RTO analysis
   └── bcm_incident_create(incident_record) → database entry

4. 🤖 UNIFIED AI PROCESSING (8090)
   ├── Impact analysis using BIA data
   ├── Resource requirement calculation
   └── Response team recommendation

5. 📋 PDCA ASSISTANT CONTEXT (8010)
   ├── Previous incident patterns
   ├── Lessons learned integration
   └── Improvement suggestions

6. 🎯 ORCHESTRATOR RESPONSE COORDINATION (8000)
   ├── Combines all AI insights
   ├── Generates response plan
   ├── Sends to Notification Service (8002)
   └── Updates frontend with actionable plan
```

### Data Flow Details
```json
{
  "incident_input": {
    "source": "frontend_assistant",
    "description": "Database server critical failure",
    "user_id": "operator_123",
    "timestamp": "2025-09-14T10:00:00Z"
  },
  "orchestrator_routing": {
    "primary_handler": "unified_ai_service:8090",
    "context_provider": "pdca_assistant:8010",
    "tools_access": "mcp_server:8087",
    "notification": "notification_service:8002"
  },
  "ai_analysis_result": {
    "incident_category": "technology_critical",
    "estimated_downtime": "2-4 hours",
    "affected_processes": ["customer_service", "billing"],
    "response_team": ["db_admin", "network_team", "communications"],
    "immediate_actions": [
      "Activate backup database",
      "Notify affected customers",
      "Escalate to L3 support"
    ]
  }
}
```

## 📊 Scenario 2: BIA Generation Workflow

### Process Flow
```
1. 📋 BIA REQUEST (Business User → Frontend)
   └── "Нужен анализ влияния для процесса 'Обработка заказов'"

2. 🧠 AI ORCHESTRATOR (8000)
   ├── Routes to Scenario Engine (8085) for scenario generation
   ├── Uses MCP Server (8087) for process data
   └── Coordinates analysis

3. 🎭 SCENARIO ENGINE (8085)
   ├── Generates disruption scenarios
   ├── Models different impact levels
   └── Calculates RTO/RPO recommendations

4. 🔧 MCP SERVER DATA ACCESS (8087)
   ├── bcm_process_list(tenant_id) → process inventory
   ├── bcm_process_analyze(process_id, "bia") → current metrics
   └── Historical incident data

5. 🤖 UNIFIED AI ANALYSIS (8090)
   ├── Financial impact modeling
   ├── Operational dependency mapping
   └── Regulatory compliance assessment

6. 🎯 COORDINATED BIA REPORT (8000)
   ├── Combines scenario analysis + data + AI insights
   ├── Generates comprehensive BIA document
   └── Sends to frontend with recommendations
```

## 📊 Scenario 3: PDCA Cycle Automation

### Continuous Improvement Flow
```
1. 📈 PDCA CYCLE TRIGGER
   ├── Scheduled review (monthly)
   ├── Incident follow-up
   └── Management review request

2. 📋 PDCA ASSISTANT ANALYSIS (8010)
   ├── Reviews current cycle phase
   ├── Analyzes performance metrics
   └── Suggests next best actions

3. 🧠 ORCHESTRATOR COORDINATION (8000)
   ├── Routes to appropriate specialists
   ├── Coordinates data collection
   └── Manages workflow progression

4. 🎭 SCENARIO ENGINE PLANNING (8085)
   ├── Generates improvement scenarios
   ├── Models implementation options
   └── Predicts outcomes

5. 🔧 MCP DATA INTEGRATION (8087)
   ├── Audit evidence collection
   ├── KPI metrics analysis
   └── Compliance gap assessment

6. 📢 NOTIFICATION & REPORTING (8002)
   ├── Stakeholder notifications
   ├── Progress reporting
   └── Action item assignments
```

## 🏢 Main Assistant Communicator Logic

### Frontend ↔ Backend Communication
```python
# Frontend Assistant (Vue.js component)
class BCMAssistant:
    def send_request(self, user_input):
        # Always routes through AI Orchestrator
        response = await api.post("http://localhost:8000/ai/process", {
            "capability": self.detect_capability(user_input),
            "data": user_input,
            "context": {"user_id": self.user_id, "session": self.session_id}
        })
        return self.format_response(response)

# AI Orchestrator acts as main communicator
class AIOrchestrator:
    async def process_user_request(self, request):
        # Determines which AI services to use
        if "incident" in request.data:
            return await self.route_to_incident_pipeline()
        elif "bia" in request.data:
            return await self.route_to_bia_pipeline()
        elif "scenario" in request.data:
            return await self.route_to_scenario_pipeline()
```

### Communication Pattern
```
👤 User → 🖥️ Frontend Assistant → 🧠 AI Orchestrator (8000) → 🤖 Specialist Services
                ↑                          ↓
           📱 Response         🔄 Coordinates & Integrates Results
```

## 💾 AI Memory & Storage Architecture

### Memory Strategy
```yaml
# Persistent Storage
volumes:
  # 1. AI Models Cache (Local LLM)
  ai_models_cache:
    driver: local
    driver_opts:
      device: /var/lib/docker/ai_models
      size: 10GB

  # 2. Conversation Memory (Sessions)
  ai_conversation_memory:
    driver: local
    driver_opts:
      device: /var/lib/docker/ai_memory

  # 3. Learning Data (Model Improvements)
  ai_learning_data:
    driver: local
    driver_opts:
      device: /var/lib/docker/ai_learning

# Database Storage
postgres_ai_tables:
  - ai_conversations
  - ai_decisions_history
  - ai_model_performance
  - ai_user_feedback

# Redis Cache
redis_ai_cache:
  - Session contexts (TTL: 1 hour)
  - Recent AI responses (TTL: 24 hours)
  - Model inference cache (TTL: 1 week)
```

### Memory Implementation
```python
# Redis-based conversation memory
class AIMemoryManager:
    async def store_conversation(self, session_id, message, response):
        await redis.setex(
            f"ai_session:{session_id}",
            3600,  # 1 hour TTL
            json.dumps({
                "messages": [...],
                "context": {...},
                "last_services_used": [...]
            })
        )

    async def get_context(self, session_id):
        return await redis.get(f"ai_session:{session_id}")

# PostgreSQL persistent learning
class AILearningStore:
    async def record_decision(self, decision_data):
        await db.execute("""
            INSERT INTO ai_decisions_history
            (orchestrator_service, decision_type, input_data, output_data,
             user_feedback, performance_metrics, timestamp)
            VALUES (%(service)s, %(type)s, %(input)s, %(output)s,
                    %(feedback)s, %(metrics)s, NOW())
        """, decision_data)
```

## ☁️ Cloud AI Configuration

### Current Settings
```env
# Cloud AI Strategy
AI_MODE=cloud                    # local | cloud | hybrid
CLOUD_LLM_PROVIDER=openai       # openai | anthropic | azure

# Model Selection by Use Case
INCIDENT_ANALYSIS_MODEL=gpt-4-turbo       # Fastest response
BIA_ANALYSIS_MODEL=gpt-4                  # Deep analysis
SCENARIO_GENERATION_MODEL=claude-3-sonnet # Creative scenarios
COMPLIANCE_MODEL=gpt-4                    # Precision required
```

### Docker Desktop AI Menu Integration
```yaml
# Docker AI models auto-configuration
docker_ai_models:
  default_model: "llama3.2:3b"
  available_models:
    - "llama3.2:3b"      # General purpose
    - "codellama:7b"     # Code analysis
    - "mistral:7b"       # Business analysis

  auto_download: true
  gpu_acceleration: false  # Enable if GPU available
```

## 📝 Comprehensive Prompts System

### Prompt Templates by Service
```python
# AI Orchestrator (8000) - Main Coordinator
ORCHESTRATOR_PROMPTS = {
    "incident_coordination": """
    You are the AI Orchestrator for a BCM platform managing incident response.

    CONTEXT: Critical incident reported requiring multi-service coordination
    CAPABILITIES: Route to incident specialists, coordinate response, ensure compliance

    INPUT: {incident_description}

    COORDINATE:
    1. Classify incident via MCP Server
    2. Route to Unified AI for impact analysis
    3. Get PDCA context for lessons learned
    4. Generate coordinated response plan

    OUTPUT: Structured response plan with clear actions and service assignments
    """,

    "bia_orchestration": """
    You are coordinating Business Impact Analysis across multiple AI specialists.

    CONTEXT: Business process needs comprehensive impact assessment
    OBJECTIVE: Generate complete BIA with RTO/RPO recommendations

    COORDINATE BETWEEN:
    - Scenario Engine: Generate disruption scenarios
    - MCP Server: Access process data and dependencies
    - Unified AI: Calculate financial and operational impacts

    OUTPUT: Complete BIA report with quantified impacts and recovery targets
    """
}

# Unified AI Service (8090) - Multi-capability Processor
UNIFIED_AI_PROMPTS = {
    "bia_analysis": """
    You are a specialized Business Impact Analysis expert.

    CONTEXT: Analyzing business process: {process_name}
    OBJECTIVE: Calculate comprehensive business impact metrics

    ANALYZE:
    - Financial impact (direct costs, revenue loss, penalties)
    - Operational impact (process dependencies, resource requirements)
    - Regulatory impact (compliance requirements, reporting obligations)
    - Reputational impact (customer satisfaction, market position)

    CALCULATE:
    - Maximum Tolerable Period of Disruption (MTPD)
    - Recovery Time Objective (RTO) recommendation
    - Recovery Point Objective (RPO) recommendation

    OUTPUT: Quantified impact assessment with specific RTO/RPO targets
    """,

    "incident_impact_analysis": """
    You are analyzing incident impact for business continuity.

    INCIDENT: {incident_description}
    AFFECTED_PROCESSES: {affected_processes}

    ASSESS:
    1. Immediate impact (what's broken now)
    2. Cascade effects (what will break next)
    3. Recovery complexity (what's needed to fix)
    4. Stakeholder impact (who needs notification)

    RECOMMEND:
    - Response team activation
    - Communication strategy
    - Recovery priorities
    - Escalation triggers

    OUTPUT: Comprehensive incident impact analysis with response recommendations
    """
}

# Scenario Orchestrator (8085) - Creative Scenario Generation
SCENARIO_PROMPTS = {
    "scenario_generation": """
    You are a BCM scenario generation specialist creating realistic business disruption scenarios.

    BUSINESS_PROCESS: {process_name}
    SCENARIO_TYPE: {scenario_type}  # natural_disaster | cyber_attack | supply_chain | pandemic

    GENERATE realistic scenarios considering:
    - Industry-specific threats
    - Geographic location factors
    - Seasonal/temporal considerations
    - Supply chain vulnerabilities
    - Technology dependencies

    FOR EACH SCENARIO:
    1. Trigger event description
    2. Escalation timeline (hour by hour)
    3. Cascading effects on other processes
    4. Resource impact assessment
    5. Recovery complexity rating

    OUTPUT: 3-5 detailed scenarios with quantified impacts and recovery estimates
    """,

    "scenario_optimization": """
    You are optimizing business continuity scenarios for maximum preparedness.

    EXISTING_SCENARIOS: {current_scenarios}
    PERFORMANCE_DATA: {past_incidents}

    OPTIMIZE by:
    1. Identifying scenario gaps
    2. Enhancing realism based on actual incidents
    3. Adjusting probability assessments
    4. Refining impact calculations
    5. Improving response procedures

    OUTPUT: Enhanced scenario set with improved accuracy and coverage
    """
}

# PDCA Assistant (8010) - Contextual Intelligence
PDCA_PROMPTS = {
    "context_analysis": """
    You are the PDCA cycle intelligence providing contextual insights.

    CURRENT_PHASE: {pdca_phase}  # plan | do | check | act
    BUSINESS_CONTEXT: {context}
    HISTORICAL_DATA: {past_cycles}

    PROVIDE contextual intelligence:
    - What worked well in similar situations
    - Common pitfalls to avoid
    - Best practices for current phase
    - Recommended next steps
    - Success metrics to track

    CONSIDER:
    - Organizational maturity level
    - Resource constraints
    - Regulatory requirements
    - Industry benchmarks

    OUTPUT: Contextual recommendations with reasoning and supporting data
    """,

    "improvement_suggestions": """
    You are suggesting continuous improvements based on PDCA cycle analysis.

    PERFORMANCE_DATA: {kpi_metrics}
    RECENT_INCIDENTS: {incident_patterns}
    AUDIT_FINDINGS: {audit_results}

    ANALYZE trends and patterns to suggest:
    1. Process improvements
    2. Technology enhancements
    3. Training needs
    4. Policy updates
    5. Resource optimizations

    PRIORITIZE suggestions by:
    - Risk reduction impact
    - Implementation effort
    - Resource requirements
    - ROI potential

    OUTPUT: Prioritized improvement roadmap with business justification
    """
}

# MCP Server (8087) - Data Access & Tools
MCP_PROMPTS = {
    "data_synthesis": """
    You are synthesizing BCM platform data for AI analysis.

    DATA_SOURCES: Odoo, PostgreSQL, Redis, Keycloak
    ANALYSIS_TYPE: {analysis_type}

    COMBINE data from:
    - Business process definitions
    - Historical incident records
    - Audit findings and evidence
    - KPI performance metrics
    - User roles and permissions

    ENSURE data quality:
    - Validate completeness
    - Check consistency
    - Anonymize sensitive data
    - Maintain audit trail

    OUTPUT: Clean, structured data ready for AI analysis
    """
}
```

## 💾 AI Memory Architecture

### Storage Strategy
```yaml
# 1. SHORT-TERM MEMORY (Redis)
session_memory:
  location: "redis://redis:6379/0"
  ttl: 3600  # 1 hour
  data:
    - Current conversation context
    - Active AI processing state
    - Temporary analysis results
    - User preferences

# 2. MEDIUM-TERM MEMORY (Redis)
working_memory:
  location: "redis://redis:6379/1"
  ttl: 86400  # 24 hours
  data:
    - Recent AI decisions
    - Cached analysis results
    - Model inference cache
    - Cross-service communication

# 3. LONG-TERM MEMORY (PostgreSQL)
persistent_memory:
  location: "postgres://bcm_platform"
  tables:
    ai_conversations:
      - session_id, user_id, conversation_data, timestamp
    ai_decisions_history:
      - decision_id, service_name, input_data, output_data, feedback
    ai_model_performance:
      - model_name, task_type, accuracy_metrics, usage_stats
    ai_learning_feedback:
      - feedback_id, decision_id, user_rating, improvement_notes

# 4. AI MODELS STORAGE
model_storage:
  local_models: "/var/lib/docker/volumes/ai_models_cache"
  cloud_cache: "redis://redis:6379/2"
  size_limit: "10GB"
```

### Memory Implementation
```python
class AIMemoryManager:
    def __init__(self):
        self.redis_session = redis.from_url("redis://redis:6379/0")
        self.redis_working = redis.from_url("redis://redis:6379/1")
        self.postgres = asyncpg.connect("postgres://...")

    async def store_conversation_context(self, session_id, context):
        """Store conversation context with TTL"""
        await self.redis_session.setex(
            f"session:{session_id}:context",
            3600,
            json.dumps(context)
        )

    async def get_working_memory(self, task_id):
        """Get cached results from previous AI processing"""
        return await self.redis_working.get(f"task:{task_id}:result")

    async def record_ai_decision(self, service_name, decision_data):
        """Record AI decision for learning and audit"""
        await self.postgres.execute("""
            INSERT INTO ai_decisions_history
            (service_name, decision_type, input_data, output_data, timestamp)
            VALUES ($1, $2, $3, $4, NOW())
        """, service_name, decision_data['type'],
             decision_data['input'], decision_data['output'])
```

## ☁️ Cloud AI Models Configuration

### Model Selection Strategy
```python
CLOUD_AI_MODELS = {
    # OpenAI Configuration
    "openai": {
        "incident_analysis": {
            "model": "gpt-4-turbo",
            "temperature": 0.1,  # Precise for critical incidents
            "max_tokens": 1000,
            "system_prompt": "You are a critical incident analysis expert..."
        },
        "bia_analysis": {
            "model": "gpt-4",
            "temperature": 0.2,
            "max_tokens": 2000,
            "system_prompt": "You are a business impact analysis specialist..."
        },
        "scenario_generation": {
            "model": "gpt-4-turbo",
            "temperature": 0.7,  # Creative for scenarios
            "max_tokens": 3000,
            "system_prompt": "You are a creative scenario planning expert..."
        }
    },

    # Anthropic Configuration
    "anthropic": {
        "compliance_analysis": {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 2000,
            "temperature": 0.1,
            "system_prompt": "You are an ISO 22301 compliance expert..."
        },
        "report_generation": {
            "model": "claude-3-opus-20240229",
            "max_tokens": 4000,
            "temperature": 0.3,
            "system_prompt": "You are generating professional BCM reports..."
        }
    }
}
```

### Docker Desktop AI Menu Configuration
```json
{
  "docker_ai_config": {
    "models": {
      "llama3.2:3b": {
        "use_case": "General BCM queries",
        "memory_required": "4GB",
        "download_size": "2.2GB"
      },
      "codellama:7b": {
        "use_case": "Technical analysis",
        "memory_required": "6GB",
        "download_size": "3.8GB"
      },
      "mistral:7b": {
        "use_case": "Business analysis",
        "memory_required": "6GB",
        "download_size": "4.1GB"
      }
    },
    "auto_download": true,
    "gpu_optimization": false
  }
}
```

## 🔄 Main Assistant Communication Logic

### Is This Logic Implemented?

**❓ ВОПРОС**: Есть ли главный assistant в frontend, который коммуницирует с клиентом?

**🔍 ПРОВЕРИМ:**