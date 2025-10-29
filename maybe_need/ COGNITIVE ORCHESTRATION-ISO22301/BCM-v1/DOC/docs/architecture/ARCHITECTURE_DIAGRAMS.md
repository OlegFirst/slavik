# Архитектурные диаграммы BCM Platform

## 1. Общая архитектура системы

```mermaid
graph TB
    subgraph "Client Layer"
        WebApp[Web Application]
        MobileApp[Mobile App]
        Portal[Client Portal]
        API_Consumers[External API Consumers]
    end
    
    subgraph "Load Balancer"
        LB[Nginx Load Balancer]
    end
    
    subgraph "Application Layer"
        subgraph "Odoo Instances"
            Odoo1[Odoo Instance 1]
            Odoo2[Odoo Instance 2]
            Odoo3[Odoo Instance N]
        end
        
        subgraph "AI Services"
            AI1[AI Optimization Service:8001]
            AI2[AI Risk Analysis Service:8002] 
            AI3[AI Resource Allocation:8003]
            AI4[AI Predictive Analytics:8004]
        end
    end
    
    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL Master)]
        PG_Slave[(PostgreSQL Slaves)]
        Redis[(Redis Cluster)]
        Elasticsearch[(Elasticsearch)]
        MinIO[(MinIO Object Storage)]
    end
    
    subgraph "Infrastructure"
        Kafka[Apache Kafka]
        Prometheus[Prometheus]
        Grafana[Grafana]
        ELK[ELK Stack]
    end
    
    WebApp --> LB
    MobileApp --> LB
    Portal --> LB
    API_Consumers --> LB
    
    LB --> Odoo1
    LB --> Odoo2
    LB --> Odoo3
    
    Odoo1 --> PostgreSQL
    Odoo2 --> PostgreSQL
    Odoo3 --> PostgreSQL
    
    PostgreSQL --> PG_Slave
    
    Odoo1 --> Redis
    Odoo2 --> Redis
    Odoo3 --> Redis
    
    Odoo1 --> AI1
    Odoo1 --> AI2
    Odoo1 --> AI3
    Odoo1 --> AI4
    
    Odoo1 --> Elasticsearch
    Odoo1 --> MinIO
    Odoo1 --> Kafka
    
    Prometheus --> Grafana
    Kafka --> ELK
```

## 2. Модульная архитектура BCM

```mermaid
graph TD
    subgraph "Foundation Layer"
        Core[bcm_core<br/>Base Models & Utils]
        Config[bcm_config<br/>System Configuration]
        Clients[bcm_clients<br/>Multi-Tenancy]
    end
    
    subgraph "Intelligence Layer"  
        Intelligence[bcm_intelligent_base<br/>AI/ML Hub]
        Context[bcm_context<br/>Search & Indexing]
    end
    
    subgraph "Core Business Layer"
        BIA[bcm_bia<br/>Business Impact Analysis]
        Risk[bcm_risk_management<br/>Risk Management]
        Incident[bcm_incident_management<br/>Incident Management]  
        Plans[bcm_plans<br/>Continuity Plans]
    end
    
    subgraph "Governance Layer"
        Audit[bcm_audit<br/>Audit & Compliance]
        Governance[bcm_governance<br/>Corporate Governance]
        Exercise[bcm_exercise<br/>Testing & Exercises]
        Training[bcm_training<br/>Training Management]
    end
    
    subgraph "Analytics Layer"
        KPI[bcm_kpi<br/>Key Performance Indicators]
        Reporting[bcm_reporting<br/>Reports & Analytics]
    end
    
    subgraph "Interface Layer"
        Portal[bcm_portal<br/>Client Portal]
        ScenarioHub[bcm_scenario_hub<br/>Scenario Marketplace]
        Templates[bcm_templates<br/>Document Templates]
    end
    
    %% Dependencies
    Core --> Intelligence
    Core --> BIA
    Core --> Risk
    Core --> Incident
    Core --> Plans
    Core --> Audit
    Core --> Governance
    Core --> Exercise
    Core --> Training
    Core --> KPI
    Core --> Reporting
    
    Config --> Intelligence
    Clients --> Portal
    
    Intelligence --> BIA
    Intelligence --> Risk
    Intelligence --> Incident
    
    Context --> Portal
    Context --> ScenarioHub
    
    BIA --> Risk
    BIA --> Plans
    Risk --> Incident
    Incident --> Plans
    Plans --> Exercise
    
    Governance --> Audit
    Governance --> Templates
    
    KPI --> Reporting
    Reporting --> Portal
    
    Templates --> Plans
    ScenarioHub --> Plans
    ScenarioHub --> Exercise
```

## 3. Диаграмма потоков данных - BIA Process

```mermaid
sequenceDiagram
    participant User as BIA Analyst
    participant UI as Web Interface
    participant API as BCM API
    participant BIA as BIA Service
    participant AI as AI Service
    participant DB as Database
    participant Cache as Redis Cache
    
    User->>UI: Create Business Process
    UI->>API: POST /bcm/bia/processes
    API->>BIA: Validate Process Data
    BIA->>DB: Save Process
    DB-->>BIA: Process ID
    BIA-->>API: Process Created
    API-->>UI: Success Response
    UI-->>User: Process Created
    
    User->>UI: Request AI Optimization
    UI->>API: POST /bcm/bia/optimize-rto-rpo
    API->>AI: Trigger Optimization
    AI->>Cache: Get Historical Data
    AI->>DB: Get Process Dependencies
    AI->>AI: Run ML Model
    AI-->>API: Optimization Results
    API->>DB: Save Results
    API-->>UI: Optimization Complete
    UI-->>User: Show Recommendations
    
    User->>UI: Accept Recommendations
    UI->>API: PUT /bcm/bia/processes/{id}
    API->>BIA: Update Process
    BIA->>DB: Update RTO/RPO
    BIA-->>API: Updated
    API-->>UI: Success
    UI-->>User: Process Updated
```

## 4. Архитектура управления инцидентами

```mermaid
graph LR
    subgraph "Incident Detection"
        Manual[Manual Reporting]
        Automated[Automated Detection]
        IoT[IoT Sensors]
        Monitoring[System Monitoring]
    end
    
    subgraph "Incident Processing"
        Intake[Incident Intake]
        Classification[AI Classification]
        Triage[Triage & Prioritization]
        Assignment[Assignment]
    end
    
    subgraph "Response Coordination"
        CommandCenter[Incident Command Center]
        TeamNotification[Team Notification]
        PlanActivation[Plan Activation]
        ResourceAllocation[Resource Allocation]
    end
    
    subgraph "Communication"
        Internal[Internal Comms]
        External[External Comms]
        Stakeholders[Stakeholder Updates]
        Media[Media Relations]
    end
    
    subgraph "Resolution"
        Investigation[Investigation]
        Remediation[Remediation]
        Recovery[Recovery]
        PostMortem[Post-Mortem]
    end
    
    Manual --> Intake
    Automated --> Intake
    IoT --> Intake
    Monitoring --> Intake
    
    Intake --> Classification
    Classification --> Triage
    Triage --> Assignment
    
    Assignment --> CommandCenter
    CommandCenter --> TeamNotification
    CommandCenter --> PlanActivation
    CommandCenter --> ResourceAllocation
    
    CommandCenter --> Internal
    CommandCenter --> External
    CommandCenter --> Stakeholders
    CommandCenter --> Media
    
    ResourceAllocation --> Investigation
    Investigation --> Remediation
    Remediation --> Recovery
    Recovery --> PostMortem
```

## 5. AI/ML Архитектура

```mermaid
graph TB
    subgraph "Data Sources"
        BIA_Data[BIA Data]
        Risk_Data[Risk Data]
        Incident_Data[Incident Data]
        External_Data[External Data Sources]
        Historical_Data[Historical Data]
    end
    
    subgraph "Data Processing Layer"
        DataPrep[Data Preprocessing]
        FeatureEng[Feature Engineering]
        DataValidation[Data Validation]
    end
    
    subgraph "AI Services"
        Optimization[Optimization Service<br/>Port 8001]
        RiskAnalysis[Risk Analysis Service<br/>Port 8002]
        ResourceAlloc[Resource Allocation Service<br/>Port 8003]
        Predictive[Predictive Analytics Service<br/>Port 8004]
    end
    
    subgraph "ML Models"
        RTO_RPO_Model[RTO/RPO Optimization Model]
        Risk_Prediction_Model[Risk Prediction Model]
        Resource_Model[Resource Optimization Model]
        Time_Series_Model[Time Series Forecasting]
    end
    
    subgraph "Model Management"
        ModelTraining[Model Training]
        ModelValidation[Model Validation]
        ModelDeployment[Model Deployment]
        ModelMonitoring[Model Monitoring]
    end
    
    subgraph "Results Processing"
        ResultsValidation[Results Validation]
        Confidence_Scoring[Confidence Scoring]
        Recommendations[Recommendations Engine]
    end
    
    BIA_Data --> DataPrep
    Risk_Data --> DataPrep
    Incident_Data --> DataPrep
    External_Data --> DataPrep
    Historical_Data --> DataPrep
    
    DataPrep --> FeatureEng
    FeatureEng --> DataValidation
    
    DataValidation --> Optimization
    DataValidation --> RiskAnalysis
    DataValidation --> ResourceAlloc
    DataValidation --> Predictive
    
    Optimization --> RTO_RPO_Model
    RiskAnalysis --> Risk_Prediction_Model
    ResourceAlloc --> Resource_Model
    Predictive --> Time_Series_Model
    
    RTO_RPO_Model --> ResultsValidation
    Risk_Prediction_Model --> ResultsValidation
    Resource_Model --> ResultsValidation
    Time_Series_Model --> ResultsValidation
    
    ResultsValidation --> Confidence_Scoring
    Confidence_Scoring --> Recommendations
    
    ModelTraining --> ModelValidation
    ModelValidation --> ModelDeployment
    ModelDeployment --> ModelMonitoring
```

## 6. Диаграмма безопасности и аутентификации

```mermaid
graph TB
    subgraph "Client Authentication"
        WebClient[Web Client]
        MobileClient[Mobile Client]
        APIClient[API Client]
    end
    
    subgraph "Authentication Layer"
        AuthGateway[Authentication Gateway]
        JWT_Service[JWT Token Service]
        OAuth_Provider[OAuth Provider]
        LDAP[LDAP/Active Directory]
        MFA[Multi-Factor Authentication]
    end
    
    subgraph "Authorization Layer"
        RBAC[Role-Based Access Control]
        ClientIsolation[Client Data Isolation]
        ResourcePermissions[Resource Permissions]
        FieldLevelSecurity[Field-Level Security]
    end
    
    subgraph "Security Services"
        AuditLogging[Audit Logging]
        SecurityMonitoring[Security Monitoring]
        ThreatDetection[Threat Detection]
        DataEncryption[Data Encryption]
    end
    
    subgraph "Compliance"
        GDPR[GDPR Compliance]
        SOX[SOX Compliance]
        ISO27001[ISO 27001]
        AuditTrail[Audit Trail]
    end
    
    WebClient --> AuthGateway
    MobileClient --> AuthGateway
    APIClient --> AuthGateway
    
    AuthGateway --> JWT_Service
    AuthGateway --> OAuth_Provider
    AuthGateway --> LDAP
    AuthGateway --> MFA
    
    JWT_Service --> RBAC
    RBAC --> ClientIsolation
    RBAC --> ResourcePermissions
    RBAC --> FieldLevelSecurity
    
    RBAC --> AuditLogging
    RBAC --> SecurityMonitoring
    SecurityMonitoring --> ThreatDetection
    
    AuditLogging --> GDPR
    AuditLogging --> SOX
    AuditLogging --> ISO27001
    AuditLogging --> AuditTrail
    
    DataEncryption --> GDPR
```

## 7. Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        subgraph "Load Balancer Tier"
            LB1[Load Balancer 1]
            LB2[Load Balancer 2]
        end
        
        subgraph "Application Tier"
            App1[Odoo App Server 1]
            App2[Odoo App Server 2]  
            App3[Odoo App Server 3]
        end
        
        subgraph "AI Services Tier"
            AI_Pod1[AI Services Pod 1]
            AI_Pod2[AI Services Pod 2]
        end
        
        subgraph "Database Tier"
            DB_Master[(PostgreSQL Master)]
            DB_Slave1[(PostgreSQL Slave 1)]
            DB_Slave2[(PostgreSQL Slave 2)]
        end
        
        subgraph "Cache Tier"
            Redis1[(Redis Master)]
            Redis2[(Redis Slave)]
            Redis3[(Redis Sentinel)]
        end
        
        subgraph "Storage Tier"
            MinIO1[MinIO Node 1]
            MinIO2[MinIO Node 2]
            MinIO3[MinIO Node 3]
            MinIO4[MinIO Node 4]
        end
        
        subgraph "Search Tier"
            ES1[Elasticsearch Node 1]
            ES2[Elasticsearch Node 2]
            ES3[Elasticsearch Node 3]
        end
    end
    
    subgraph "Staging Environment"
        Stage_LB[Staging Load Balancer]
        Stage_App[Staging App Server]
        Stage_DB[(Staging Database)]
        Stage_Redis[(Staging Redis)]
    end
    
    subgraph "Development Environment"
        Dev_App[Development Server]
        Dev_DB[(Development Database)]
        Dev_Services[Development Services]
    end
    
    subgraph "Monitoring & Logging"
        Prometheus[Prometheus]
        Grafana[Grafana]
        ELK_Stack[ELK Stack]
        Jaeger[Jaeger Tracing]
    end
    
    %% Production connections
    LB1 --> App1
    LB1 --> App2
    LB1 --> App3
    LB2 --> App1
    LB2 --> App2
    LB2 --> App3
    
    App1 --> DB_Master
    App2 --> DB_Master
    App3 --> DB_Master
    
    DB_Master --> DB_Slave1
    DB_Master --> DB_Slave2
    
    App1 --> Redis1
    App2 --> Redis1
    App3 --> Redis1
    Redis1 --> Redis2
    Redis3 --> Redis1
    
    App1 --> AI_Pod1
    App1 --> AI_Pod2
    
    %% Monitoring connections
    App1 --> Prometheus
    App2 --> Prometheus
    App3 --> Prometheus
    Prometheus --> Grafana
    
    App1 --> ELK_Stack
    App2 --> ELK_Stack
    App3 --> ELK_Stack
```

## 8. CI/CD Pipeline

```mermaid
graph LR
    subgraph "Source Control"
        Git[Git Repository]
        PR[Pull Request]
    end
    
    subgraph "CI Pipeline"
        Trigger[Webhook Trigger]
        Build[Build & Test]
        Security[Security Scan]
        Quality[Code Quality]
        Docker[Docker Build]
    end
    
    subgraph "Testing Stages"
        Unit[Unit Tests]
        Integration[Integration Tests]
        E2E[E2E Tests]
        Performance[Performance Tests]
    end
    
    subgraph "Deployment Stages"
        Dev_Deploy[Deploy to Dev]
        Stage_Deploy[Deploy to Staging]
        Prod_Deploy[Deploy to Production]
    end
    
    subgraph "Post-Deployment"
        HealthCheck[Health Checks]
        Monitoring[Monitoring Setup]
        Rollback[Rollback Capability]
    end
    
    Git --> Trigger
    PR --> Trigger
    
    Trigger --> Build
    Build --> Security
    Security --> Quality
    Quality --> Docker
    
    Docker --> Unit
    Unit --> Integration
    Integration --> E2E
    E2E --> Performance
    
    Performance --> Dev_Deploy
    Dev_Deploy --> Stage_Deploy
    Stage_Deploy --> Prod_Deploy
    
    Prod_Deploy --> HealthCheck
    HealthCheck --> Monitoring
    Monitoring --> Rollback
```

## 9. Data Flow Architecture

```mermaid
graph TD
    subgraph "Data Sources"
        UserInput[User Input]
        SystemEvents[System Events]
        ExternalAPIs[External APIs]
        IoTSensors[IoT Sensors]
        FileUploads[File Uploads]
    end
    
    subgraph "Data Ingestion"
        APIGateway[API Gateway]
        EventStreaming[Event Streaming]
        FileProcessor[File Processor]
        DataValidation[Data Validation]
    end
    
    subgraph "Data Processing"
        ETL[ETL Pipeline]
        RealTimeProcessing[Real-time Processing]
        BatchProcessing[Batch Processing]
        DataEnrichment[Data Enrichment]
    end
    
    subgraph "Data Storage"
        OLTP[(OLTP Database)]
        OLAP[(OLAP Database)]
        ObjectStorage[(Object Storage)]
        SearchIndex[(Search Index)]
        Cache[(Cache Layer)]
    end
    
    subgraph "Data Access"
        APIs[REST APIs]
        GraphQL[GraphQL APIs]
        ReportsEngine[Reports Engine]
        Analytics[Analytics Engine]
        ML_Pipeline[ML Pipeline]
    end
    
    subgraph "Data Consumption"
        WebApp[Web Application]
        MobileApp[Mobile App]
        Dashboards[Dashboards]
        Reports[Reports]
        Alerts[Alerts & Notifications]
    end
    
    UserInput --> APIGateway
    SystemEvents --> EventStreaming
    ExternalAPIs --> APIGateway
    IoTSensors --> EventStreaming
    FileUploads --> FileProcessor
    
    APIGateway --> DataValidation
    EventStreaming --> RealTimeProcessing
    FileProcessor --> BatchProcessing
    DataValidation --> ETL
    
    ETL --> OLTP
    RealTimeProcessing --> Cache
    BatchProcessing --> OLAP
    DataEnrichment --> SearchIndex
    
    OLTP --> APIs
    OLAP --> Analytics
    ObjectStorage --> ReportsEngine
    SearchIndex --> GraphQL
    Cache --> APIs
    
    APIs --> WebApp
    GraphQL --> MobileApp
    Analytics --> Dashboards
    ReportsEngine --> Reports
    ML_Pipeline --> Alerts
```

## 10. Microservices Communication

```mermaid
graph TB
    subgraph "API Gateway Layer"
        Gateway[API Gateway<br/>Kong/Zuul]
    end
    
    subgraph "Core Services"
        Auth[Authentication Service]
        BIAService[BIA Service]
        RiskService[Risk Service]
        IncidentService[Incident Service]
        PlansService[Plans Service]
    end
    
    subgraph "AI Services"
        AIOrchestrator[AI Orchestrator]
        OptimizationService[Optimization Service]
        RiskAnalysisService[Risk Analysis Service]
        ResourceService[Resource Service]
        PredictiveService[Predictive Service]
    end
    
    subgraph "Supporting Services"
        NotificationService[Notification Service]
        ReportingService[Reporting Service]
        AuditService[Audit Service]
        FileService[File Service]
    end
    
    subgraph "Message Queue"
        EventBus[Apache Kafka<br/>Event Bus]
    end
    
    subgraph "Service Discovery"
        Registry[Service Registry<br/>Consul/Eureka]
    end
    
    subgraph "Configuration"
        ConfigServer[Config Server]
    end
    
    Gateway --> Auth
    Gateway --> BIAService
    Gateway --> RiskService
    Gateway --> IncidentService
    Gateway --> PlansService
    
    BIAService --> AIOrchestrator
    RiskService --> AIOrchestrator
    IncidentService --> AIOrchestrator
    
    AIOrchestrator --> OptimizationService
    AIOrchestrator --> RiskAnalysisService
    AIOrchestrator --> ResourceService
    AIOrchestrator --> PredictiveService
    
    BIAService --> EventBus
    RiskService --> EventBus
    IncidentService --> EventBus
    PlansService --> EventBus
    
    EventBus --> NotificationService
    EventBus --> ReportingService
    EventBus --> AuditService
    
    Auth --> Registry
    BIAService --> Registry
    RiskService --> Registry
    IncidentService --> Registry
    
    Registry --> ConfigServer
```

Эти диаграммы показывают:

1. **Общую архитектуру** - все уровни системы от клиентов до данных
2. **Модульную структуру** - взаимосвязи 19 BCM модулей
3. **Потоки данных** - как данные проходят через систему
4. **AI архитектуру** - специализированные AI сервисы
5. **Безопасность** - многоуровневую защиту
6. **Deployment** - production ready инфраструктуру
7. **CI/CD** - процесс разработки и развертывания
8. **Обработку данных** - от источников до потребления
9. **Микросервисы** - современную архитектуру сервисов

Диаграммы созданы в формате Mermaid и могут быть легко встроены в документацию или презентации.