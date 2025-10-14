# AI-Platform-ISO: Complete Platform Map

**Generated**: 2025-10-09
**Version**: 2.0.0

## Platform Statistics

- **Total Services**: 12
- **Total Modules**: 10
- **Total Infrastructure Components**: 6
- **Total Dependencies**: 70
- **Total Ports**: 19
- **Total Documentation Files**: ~320+
- **Iso Clauses Covered**: 10

## Layers

### Infrastructure Layer
Core infrastructure: EventBus, Database, Security, Observability

**Components**: eventbus, database, observability, security, gateway, vector-db

### Intelligent Core Layer
AI modules: LLM routing, RAG, Specialists, Orchestration

**Components**: ai-foundation, workflow_intelligence, expertise-center, collective, predictive, community_intelligence, event_intelligence, orchestration, ai_workflow_optimizer, workflow-engine

### Platform Services Layer
BCM services mapped to ISO 22301 clauses

**Components**: bia-service, risk-service, compliance-service, planning-service, response-service, documents-service, governance-service, validation-service, learning-service, bcm-coordination-service, community-service, monitoring

### Integration Layer
External integrations and APIs

**Components**: API Gateway, EventBus, WebSocket


## Services

### bia-service
- **Port**: 8001
- **ISO Clause**: 8.2
- **Description**: Business Impact Analysis service
- **Capabilities**: BIA planning, Data collection, Dependency mapping, RTO/RPO analysis

### risk-service
- **Port**: 8002
- **ISO Clause**: 8.3
- **Description**: Risk Assessment & Treatment service
- **Capabilities**: Risk assessment, Treatment planning, Risk monitoring

### compliance-service
- **Port**: 8003
- **ISO Clause**: 9.1
- **Description**: ISO 22301 Compliance Monitoring
- **Capabilities**: Real-time compliance, Gap analysis, Evidence collection, Audit prep

### planning-service
- **Port**: 8004
- **ISO Clause**: 8.4
- **Description**: BC Plan Development & Journey Planning
- **Capabilities**: Journey planning, BC plans, Timeline prediction, Exercise planning

### response-service
- **Port**: 8005
- **ISO Clause**: 8.4
- **Description**: Incident Response & Crisis Management
- **Capabilities**: Incident detection, Plan activation, RTO tracking, Crisis coordination

### documents-service
- **Port**: 8006
- **ISO Clause**: 7.5
- **Description**: Document Management & Living Docs
- **Capabilities**: Living docs, Version control, Templates, Collaboration

### governance-service
- **Port**: 8007
- **ISO Clause**: 5.0
- **Description**: Leadership & Governance
- **Capabilities**: Policy management, Management review, Stakeholder engagement

### validation-service
- **Port**: 8008
- **ISO Clause**: 8.5
- **Description**: Exercise & Testing
- **Capabilities**: Exercise planning, Digital twin, Scenario generation, AAR

### learning-service
- **Port**: 8009
- **ISO Clause**: 7.3
- **Description**: Training & Awareness
- **Capabilities**: Training programs, Certification tracking, Awareness campaigns

### bcm-coordination-service
- **Port**: 8010
- **ISO Clause**: None
- **Description**: Cross-service BCM coordination
- **Capabilities**: Service orchestration, Workflow coordination

### community-service
- **Port**: 8011
- **ISO Clause**: None
- **Description**: Community & Knowledge sharing
- **Capabilities**: Community forums, Knowledge sharing, Peer learning

### monitoring
- **Port**: 8012
- **ISO Clause**: 9.0
- **Description**: Performance Monitoring & Analytics
- **Capabilities**: Real-time monitoring, Metrics, Dashboards, Alerting


## Modules

### ai-foundation
- **Description**: Multi-model LLM orchestration, RAG pipeline, ML predictions
- **Capabilities**: LLM routing, RAG, ML models, Self-learning

### workflow_intelligence
- **Port**: 8037
- **Description**: Workflow orchestration with Temporal Cloud
- **Capabilities**: Temporal workflows, Orchestration, State management

### expertise-center
- **Port**: 8036
- **Description**: 14 domain specialists and tactical assistants
- **Capabilities**: BIA specialist, Risk specialist, Compliance specialist, 14 total

### collective
- **Port**: 8032
- **Description**: Collective intelligence with privacy-preserving agents
- **Capabilities**: Case library (347+), k-anonymity (k=5), Pattern matching

### predictive
- **Port**: 8031
- **Description**: Risk forecasting and scenario simulation
- **Capabilities**: Timeline prediction, Certification forecasting, Challenge prediction

### community_intelligence
- **Port**: 8038
- **Description**: Community knowledge and peer learning
- **Capabilities**: Community learning, Peer collaboration

### event_intelligence
- **Port**: 8039
- **Description**: Real-time event pattern detection
- **Capabilities**: Pattern learning, Anomaly detection, Event sequences

### orchestration
- **Description**: Service coordination and cognitive loop
- **Capabilities**: Cognitive Loop (6 steps), MONITOR-UNDERSTAND-DECIDE-ACT-MEASURE-LEARN

### ai_workflow_optimizer
- **Description**: Workflow optimization with AI
- **Capabilities**: Workflow analysis, Optimization suggestions

### workflow-engine
- **Port**: 8041
- **Description**: BPMN workflow execution engine
- **Capabilities**: BPMN execution, Process automation
