# BCM Platform AI Components - Detailed Documentation

## 🤖 AI Architecture Overview

```mermaid
graph TB
    %% User Interaction
    USER[User Request] --> FRONTEND[Frontend Interface]
    FRONTEND --> SO[Scenario Orchestrator<br/>:8085]

    %% AI Processing Layer
    SO --> AI_ORCH[AI Orchestrator<br/>:8000]
    AI_ORCH --> LLM{Local LLM<br/>Selection}

    %% Model Router
    LLM --> GEMMA[Gemma3 Model<br/>General Purpose]
    LLM --> MISTRAL[Mistral Model<br/>Business Logic]
    LLM --> DEEPSEEK[DeepSeek Model<br/>Analysis]
    LLM --> SMOLLM[SmolLM Model<br/>Fast Response]

    %% Specialized AI Services
    AI_ORCH --> BIA[BIA Engine<br/>:8082]
    AI_ORCH --> DOC[Document Processor<br/>:8083]
    AI_ORCH --> COMP[Compliance Checker<br/>:8084]
    AI_ORCH --> UNIFIED[Docker AI PoC<br/>:8090]

    %% Integration Layer
    AI_ORCH --> MCP[MCP Server<br/>:8087]
    MCP --> TOOLS{BCM Tools}
    TOOLS --> ODOO_API[Odoo API]
    TOOLS --> PG_API[PostgreSQL API]
    TOOLS --> REDIS_API[Redis API]

    %% Data Storage
    SO --> STORAGE[Generated Scenarios<br/>Local Storage]
    AI_ORCH --> CONTEXT[AI Context<br/>Supabase]
    BIA --> CACHE[Analysis Cache<br/>Redis]

    %% Output Processing
    STORAGE --> ODOO[Odoo BCM Platform]
    ODOO --> COMMUNITY[Community Forum]
    COMMUNITY --> KNOWLEDGE[Knowledge Base]

    %% Styling
    classDef ai fill:#e1bee7,stroke:#9c27b0
    classDef model fill:#f3e5f5,stroke:#673ab7
    classDef integration fill:#e8f5e8,stroke:#4caf50
    classDef storage fill:#e3f2fd,stroke:#2196f3
    classDef output fill:#fff3e0,stroke:#ff9800

    class SO,AI_ORCH,BIA,DOC,COMP,UNIFIED ai
    class GEMMA,MISTRAL,DEEPSEEK,SMOLLM model
    class MCP,TOOLS integration
    class STORAGE,CONTEXT,CACHE storage
    class ODOO,COMMUNITY,KNOWLEDGE output
```

## 🧠 AI Orchestrator (Port 8000)

### **Location**: `/services/ai_orchestrator/main.py`

### **Core Capabilities**:
```python
# Available AI capabilities from health check:
{
  "ai_capabilities": [
    "risk_analysis",           # Business process risk assessment
    "incident_classification", # Automatic incident categorization
    "recovery_planning",       # BCM plan generation
    "nlp_queries",            # Natural language processing
    "bia_automation"          # Business Impact Analysis automation
  ]
}
```

### **Key Endpoints**:
- `POST /analyze/process-risk` - Analyze business process risks
- `POST /analyze/incident` - Classify and analyze incidents
- `POST /nlp/query` - Natural language query processing
- `GET /health` - Service health and capabilities

### **AI Processing Flow**:
```mermaid
sequenceDiagram
    participant Client
    participant AI_Orch as AI Orchestrator
    participant Redis
    participant LLM as Local LLM
    participant Supabase

    Client->>AI_Orch: NLP Query Request
    AI_Orch->>Redis: Check cache
    Redis-->>AI_Orch: Cache miss
    AI_Orch->>Supabase: Get AI context
    Supabase-->>AI_Orch: Historical context
    AI_Orch->>LLM: Process with context
    LLM-->>AI_Orch: Generated response
    AI_Orch->>Redis: Cache result
    AI_Orch->>Supabase: Store learning data
    AI_Orch-->>Client: Structured response
```

---

## 🎯 Scenario Orchestrator (Port 8085)

### **Location**: `/services/scenario_orchestrator/main.py`

### **Primary Function**: AI-powered BCM scenario generation

### **Generation Process**:
```mermaid
flowchart TD
    START[User Request] --> PARSE[Parse Parameters]
    PARSE --> BUILD[Build AI Prompt]
    BUILD --> AI_CALL[Call AI Orchestrator]
    AI_CALL --> PROCESS[Process AI Response]
    PROCESS --> FORMAT[Format to Markdown]
    FORMAT --> JAAMSIM{Complexity >= 4?}
    JAAMSIM -->|Yes| GEN_SIM[Generate JaamSim Config]
    JAAMSIM -->|No| SAVE[Save Scenario]
    GEN_SIM --> SAVE
    SAVE --> RESPONSE[Return Success Response]

    %% Error Handling
    AI_CALL -->|Failure| FALLBACK[Use Fallback Scenario]
    FALLBACK --> SAVE

    classDef process fill:#bbdefb
    classDef decision fill:#fff9c4
    classDef action fill:#c8e6c9
    classDef error fill:#ffcdd2

    class PARSE,PROCESS,FORMAT process
    class JAAMSIM decision
    class BUILD,AI_CALL,GEN_SIM,SAVE action
    class FALLBACK error
```

### **Scenario Categories Supported**:
- `epidemic` - Pandemic/health crisis scenarios
- `blackout` - Power outage and infrastructure failure
- `cyber` - Cybersecurity incident scenarios
- `supply` - Supply chain disruption scenarios
- `natural` - Natural disaster scenarios
- `terrorism` - Security threat scenarios
- `financial` - Financial crisis scenarios
- `other` - Custom scenario types

### **Generated Scenario Structure**:
```json
{
  "title": "Generated scenario title",
  "category": "cyber|blackout|epidemic|etc",
  "level": "tabletop|full",
  "meta_duration": 4,
  "meta_participants": 8,
  "content_md": "Full scenario in Markdown format",
  "is_ai_generated": true,
  "ai_generation_params": {
    "complexity": 3,
    "ai_model": "existing_ai_orchestrator",
    "generated_at": "2025-09-14T17:57:57"
  },
  "jaamsim_config": "BPMN configuration for complex scenarios"
}
```

---

## 🔧 Specialized AI Engines

### **BIA Engine (Port 8082)**
```mermaid
graph LR
    INPUT[Business Process Data] --> ANALYSIS[Impact Analysis ML]
    ANALYSIS --> CRITICALITY[Criticality Assessment]
    CRITICALITY --> RTO[RTO/RPO Calculation]
    RTO --> DEPENDENCIES[Dependency Mapping]
    DEPENDENCIES --> OUTPUT[BIA Report]

    classDef input fill:#e3f2fd
    classDef process fill:#e8f5e8
    classDef output fill:#fff3e0

    class INPUT input
    class ANALYSIS,CRITICALITY,RTO,DEPENDENCIES process
    class OUTPUT output
```

**Function**: Machine Learning-powered Business Impact Analysis
**Dependencies**: Redis for caching, RabbitMQ for async processing
**Input**: Business process definitions, resource requirements
**Output**: Impact assessments, criticality scores, RTO/RPO recommendations

### **Document Processor (Port 8083)**
```mermaid
graph LR
    DOC[Document Upload] --> EXTRACT[Text Extraction]
    EXTRACT --> NLP[NLP Processing]
    NLP --> CLASSIFY[Document Classification]
    CLASSIFY --> METADATA[Metadata Extraction]
    METADATA --> INDEX[Search Indexing]
    INDEX --> STORE[Document Store]

    classDef input fill:#e3f2fd
    classDef process fill:#e8f5e8
    classDef output fill:#fff3e0

    class DOC input
    class EXTRACT,NLP,CLASSIFY,METADATA,INDEX process
    class STORE output
```

**Function**: AI-powered document intelligence for BCM documents
**Capabilities**: PDF processing, content extraction, automatic classification
**Use Cases**: Policy analysis, plan review, compliance checking

### **Compliance Checker (Port 8084)**
```mermaid
graph LR
    POLICY[BCM Policies] --> ISO_CHECK[ISO 22301 Validation]
    PLAN[BCM Plans] --> REQUIREMENTS[Requirements Check]
    PROCESS[Business Processes] --> GAP_ANALYSIS[Gap Analysis]

    ISO_CHECK --> COMPLIANCE[Compliance Score]
    REQUIREMENTS --> COMPLIANCE
    GAP_ANALYSIS --> COMPLIANCE

    COMPLIANCE --> RECOMMENDATIONS[Improvement Recommendations]
    RECOMMENDATIONS --> REPORT[Compliance Report]

    classDef input fill:#e3f2fd
    classDef check fill:#fff9c4
    classDef output fill:#c8e6c9

    class POLICY,PLAN,PROCESS input
    class ISO_CHECK,REQUIREMENTS,GAP_ANALYSIS check
    class COMPLIANCE,RECOMMENDATIONS,REPORT output
```

**Function**: Automated ISO 22301 compliance validation
**Capabilities**: Policy gap analysis, plan adequacy assessment, requirement mapping

---

## 🔗 MCP Server (Port 8087)

### **Location**: `/integrations/mcp-server/main.py`

### **Model Context Protocol Integration**:
```mermaid
graph TD
    AI_MODELS[AI Models] --> MCP[MCP Server]
    MCP --> TOOLS{Available Tools}

    TOOLS --> ODOO_TOOL[Odoo Integration Tool]
    TOOLS --> PG_TOOL[PostgreSQL Tool]
    TOOLS --> REDIS_TOOL[Redis Tool]
    TOOLS --> GRAFANA_TOOL[Grafana Tool]
    TOOLS --> THEHIVE_TOOL[TheHive Tool]

    ODOO_TOOL --> ODOO[Odoo BCM Platform]
    PG_TOOL --> PG[(PostgreSQL)]
    REDIS_TOOL --> REDIS[(Redis)]
    GRAFANA_TOOL --> GRAFANA[Grafana Monitoring]
    THEHIVE_TOOL --> THEHIVE[TheHive Security]

    classDef mcp fill:#f3e5f5
    classDef tools fill:#e8f5e8
    classDef targets fill:#e3f2fd

    class MCP mcp
    class ODOO_TOOL,PG_TOOL,REDIS_TOOL,GRAFANA_TOOL,THEHIVE_TOOL tools
    class ODOO,PG,REDIS,GRAFANA,THEHIVE targets
```

**Function**: Standardized tool integration for AI models
**Tools Available**:
- `odoo` - Direct Odoo API access for AI
- `postgres` - Database queries for AI context
- `redis` - Cache access for AI memory
- `grafana` - Monitoring data for AI insights
- `thehive` - Security context for AI analysis

---

## 📊 AI Model Configuration

### **Model Runner Strategy** (when enabled):
```yaml
# Enterprise BCM Model Routing
MODEL_STRATEGY: bcm_enterprise

Primary Models:
  - GEMMA3: General purpose (2.3GB)
  - MISTRAL: Business logic (4.1GB)
  - DEEPSEEK: Deep analysis (4.6GB)
  - SMOLLM2: Emergency fast response (100MB)

Use Cases:
  - Scenario Generation → GEMMA3
  - Business Analysis → MISTRAL
  - Risk Assessment → DEEPSEEK
  - Quick Responses → SMOLLM2
```

### **AI Learning Pipeline**:
```mermaid
graph LR
    EXERCISE[Exercise Results] --> METRICS[Metrics Collection]
    FEEDBACK[User Feedback] --> ANALYSIS[AI Analysis]
    METRICS --> ANALYSIS
    ANALYSIS --> LEARNING[Model Learning]
    LEARNING --> IMPROVEMENT[Scenario Improvement]
    IMPROVEMENT --> LIBRARY[Scenario Library Update]

    classDef data fill:#e3f2fd
    classDef process fill:#e8f5e8
    classDef output fill:#fff3e0

    class EXERCISE,FEEDBACK,METRICS data
    class ANALYSIS,LEARNING,IMPROVEMENT process
    class LIBRARY output
```

## 🔄 Integration Patterns

### **API Communication Pattern**:
- **Synchronous**: Direct HTTP calls for real-time operations
- **Asynchronous**: RabbitMQ for background processing
- **Caching**: Redis for frequently accessed data
- **Persistence**: PostgreSQL for all business data

### **Error Handling Strategy**:
- **Circuit Breaker**: Prevent cascade failures
- **Retry Logic**: Exponential backoff for transient failures
- **Graceful Degradation**: Fallback responses when AI unavailable
- **Health Checks**: Continuous monitoring of all components

### **Security Model**:
- **Authentication**: Keycloak SSO integration
- **Authorization**: Odoo security groups
- **API Security**: Token-based authentication
- **Data Isolation**: Multi-tenant data separation

---

**This documentation provides the technical foundation for understanding the complete AI integration architecture.**