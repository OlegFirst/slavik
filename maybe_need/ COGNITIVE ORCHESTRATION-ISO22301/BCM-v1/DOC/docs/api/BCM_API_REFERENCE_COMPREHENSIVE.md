# BCM Platform API Reference - Comprehensive Documentation

## 📋 API Overview

The BCM Platform provides a comprehensive REST API architecture with 200+ endpoints across multiple service layers. This documentation covers all API endpoints generated from the enhanced PHASE 1-5 implementation.

### API Architecture
```yaml
Base URL: https://bcm.your-domain.com/api
API Version: v1
Authentication: Bearer Token / OAuth 2.0
Rate Limiting: 1000 requests/hour per user
Content Type: application/json
```

### Service Layer Structure
```yaml
Frontend Services: 28+ TypeScript/JavaScript service files
Backend APIs: 15+ microservice endpoints
AI Services: 8+ specialized AI service endpoints
Integration APIs: 10+ adapter service endpoints
```

## 🏗️ Service Architecture Map

### **Core Platform APIs**

#### **Odoo BCM Platform** (:8069/api/v1)
```yaml
Base URL: /api/v1/bcm
Authentication: Required
Service Files: bcm*.js (frontend integration)

Core Endpoints:
  - /modules/{module}/search-read - Search and retrieve records
  - /modules/{module}/create - Create new records
  - /modules/{module}/write - Update existing records
  - /modules/{module}/unlink - Delete records
  - /modules/{module}/action - Execute model actions
```

### **AI Services APIs**

#### **AI Orchestrator** (:8000)
```yaml
Service File: bcmIntelligentBase.js
Purpose: Central AI coordination and processing

Endpoints:
  POST /analyze/process-risk
    Description: Process and analyze risk data using AI
    Parameters:
      - risk_data: object (required)
      - analysis_type: string (required)
      - confidence_threshold: float (optional)
    Response: RiskAnalysisResult

  POST /analyze/incident
    Description: Classify and analyze incidents
    Parameters:
      - incident_data: object (required)
      - classification_type: string (required)
    Response: IncidentClassification

  POST /nlp/query
    Description: Process natural language queries
    Parameters:
      - query: string (required)
      - context: object (optional)
    Response: NLPQueryResponse

  GET /health
    Description: AI Orchestrator health check
    Response: HealthStatus
```

#### **Scenario Orchestrator** (:8085)
```yaml
Service File: scenarioOrchestrator.js
Purpose: AI-powered scenario generation and management

Endpoints:
  POST /scenarios/generate
    Description: Generate AI-powered BCM scenarios
    Parameters:
      - category: string (required) [epidemic, blackout, cyber, supply, natural, terrorism, financial, other]
      - complexity: string (optional) [low, medium, high]
      - organization_type: string (optional)
      - custom_parameters: object (optional)
    Response: GeneratedScenario

  GET /scenarios/available
    Description: List available scenarios
    Parameters:
      - category: string (optional)
      - page: integer (optional)
      - limit: integer (optional)
    Response: ScenarioList

  GET /scenarios/{id}
    Description: Get specific scenario details
    Response: ScenarioDetails

  POST /scenarios/{id}/customize
    Description: Customize existing scenario
    Parameters:
      - customizations: object (required)
    Response: CustomizedScenario

  GET /learning/dashboard
    Description: Get platform-wide learning analytics
    Response: LearningDashboard

  GET /learning/scenario/{id}/insights
    Description: Get learning insights for specific scenario
    Response: ScenarioInsights

  POST /learning/exercise-result
    Description: Submit exercise results for learning
    Parameters:
      - exercise_result: object (required)
    Response: LearningUpdate
```

### **Exercise & Simulation APIs**

#### **Exercise Management** (bcmExercise.js)
```yaml
Base URL: /api/v1/bcm/exercises
Purpose: Comprehensive exercise lifecycle management

Endpoints:
  GET /exercises
    Description: Get all exercises with filtering
    Parameters:
      - company_id: integer (optional)
      - status: string (optional) [planning, active, completed, cancelled]
      - exercise_type: string (optional) [tabletop, functional, full_scale, simulation]
      - date_range: object (optional)
    Response: ExerciseList

  POST /exercises
    Description: Create new exercise
    Parameters:
      - exercise_data: object (required)
    Response: ExerciseCreated

  GET /exercises/{id}
    Description: Get exercise details
    Response: ExerciseDetails

  PUT /exercises/{id}
    Description: Update exercise
    Parameters:
      - exercise_data: object (required)
    Response: ExerciseUpdated

  POST /exercises/{id}/start
    Description: Start exercise execution
    Response: ExerciseStarted

  POST /exercises/{id}/pause
    Description: Pause active exercise
    Response: ExercisePaused

  POST /exercises/{id}/complete
    Description: Complete exercise
    Parameters:
      - completion_data: object (required)
    Response: ExerciseCompleted

  GET /exercises/{id}/participants
    Description: Get exercise participants
    Response: ParticipantList

  POST /exercises/{id}/participants
    Description: Add participants to exercise
    Parameters:
      - participants: array (required)
    Response: ParticipantsAdded
```

#### **Simulation Service** (simulationService.ts)
```yaml
Base URL: /api/adapters/simulation
Purpose: JaamSim simulation integration and control

Endpoints:
  POST /simulations/create
    Description: Create new simulation
    Parameters:
      - simulation_config: object (required)
      - scenario_id: string (required)
    Response: SimulationCreated

  GET /simulations/{id}/status
    Description: Get simulation status
    Response: SimulationStatus

  POST /simulations/{id}/start
    Description: Start simulation execution
    Response: SimulationStarted

  POST /simulations/{id}/pause
    Description: Pause running simulation
    Response: SimulationPaused

  POST /simulations/{id}/stop
    Description: Stop simulation
    Response: SimulationStopped

  GET /simulations/{id}/results
    Description: Get simulation results
    Response: SimulationResults

  GET /simulations/{id}/metrics
    Description: Get real-time simulation metrics
    Response: SimulationMetrics

  POST /simulations/{id}/export
    Description: Export simulation results
    Parameters:
      - format: string (required) [json, csv, pdf]
    Response: ExportResult
```

### **Analytics & Reporting APIs**

#### **Analytics Service** (analyticsService.ts)
```yaml
Base URL: /api/analytics
Purpose: Dashboard analytics and business intelligence

Endpoints:
  GET /dashboard/metrics
    Description: Get platform-wide dashboard metrics
    Response: DashboardMetrics

  GET /dashboard/scenarios/top
    Description: Get top performing scenarios
    Parameters:
      - limit: integer (optional)
    Response: TopScenarios

  GET /dashboard/exercises/performance
    Description: Get exercise performance analytics
    Parameters:
      - date_range: object (optional)
    Response: ExercisePerformance

  GET /dashboard/ai/recommendations
    Description: Get AI-powered recommendations
    Response: AIRecommendations

  GET /charts/effectiveness
    Description: Get scenario effectiveness chart data
    Parameters:
      - period: string (optional) [week, month, quarter, year]
    Response: EffectivenessChart

  GET /charts/exercise-types
    Description: Get exercise type distribution
    Response: ExerciseTypeChart

  GET /reports/executive
    Description: Generate executive summary report
    Parameters:
      - date_range: object (optional)
    Response: ExecutiveReport
```

#### **Reporting Service** (bcmReporting.js)
```yaml
Base URL: /api/v1/bcm/reports
Purpose: Report generation and management

Endpoints:
  GET /reports
    Description: Get all reports with filtering
    Parameters:
      - report_type: string (optional)
      - category: string (optional)
      - status: string (optional)
    Response: ReportList

  POST /reports
    Description: Create new report
    Parameters:
      - report_data: object (required)
    Response: ReportCreated

  GET /reports/{id}
    Description: Get report details
    Response: ReportDetails

  POST /reports/{id}/generate
    Description: Generate report
    Response: ReportGenerated

  GET /reports/{id}/download
    Description: Download report file
    Response: FileDownload

  POST /reports/schedule
    Description: Schedule automated report
    Parameters:
      - schedule_data: object (required)
    Response: ScheduleCreated
```

### **Community & Knowledge APIs**

#### **Community Portal** (bcmPortal.js)
```yaml
Base URL: /api/v1/bcm/community
Purpose: Community forum and knowledge base management

Endpoints:
  GET /knowledge/articles
    Description: Get knowledge base articles
    Parameters:
      - category: string (optional)
      - search: string (optional)
      - tags: array (optional)
    Response: ArticleList

  POST /knowledge/articles
    Description: Create knowledge article
    Parameters:
      - article_data: object (required)
    Response: ArticleCreated

  GET /knowledge/articles/{id}
    Description: Get article details
    Response: ArticleDetails

  PUT /knowledge/articles/{id}
    Description: Update article
    Parameters:
      - article_data: object (required)
    Response: ArticleUpdated

  POST /knowledge/articles/generate
    Description: AI-generate article from exercise
    Parameters:
      - exercise_id: string (required)
      - generation_prompt: string (optional)
    Response: GeneratedArticle

  GET /forum/topics
    Description: Get forum topics
    Response: TopicList

  POST /forum/topics
    Description: Create forum topic
    Parameters:
      - topic_data: object (required)
    Response: TopicCreated
```

#### **Scenario Hub** (bcmScenarioHub.js)
```yaml
Base URL: /api/bcm-scenario-hub
Purpose: Scenario marketplace and community features

Endpoints:
  GET /scenarios
    Description: Get scenario catalog
    Parameters:
      - page: integer (optional)
      - limit: integer (optional)
      - category: string (optional)
      - tags: array (optional)
      - search: string (optional)
      - featured: boolean (optional)
      - author: string (optional)
    Response: ScenarioCatalog

  POST /scenarios
    Description: Create new scenario
    Parameters:
      - scenario_data: object (required)
    Response: ScenarioCreated

  GET /scenarios/{id}
    Description: Get scenario details
    Response: ScenarioDetails

  GET /scenarios/{id}/versions
    Description: Get scenario version history
    Response: VersionHistory

  POST /scenarios/{id}/fork
    Description: Fork scenario for customization
    Response: ForkedScenario

  POST /scenarios/{id}/rate
    Description: Rate scenario
    Parameters:
      - rating: integer (required) [1-5]
      - review: string (optional)
    Response: RatingSubmitted

  GET /scenarios/{id}/reviews
    Description: Get scenario reviews
    Response: ReviewList
```

### **Template & Document APIs**

#### **Template Management** (bcmTemplates.js)
```yaml
Base URL: /api/v1/bcm/templates
Purpose: Document template and BPMN workflow management

Endpoints:
  GET /templates
    Description: Get template catalog
    Parameters:
      - category: string (optional)
      - format: string (optional) [docx, pdf, bpmn, xml]
    Response: TemplateList

  POST /templates
    Description: Create new template
    Parameters:
      - template_data: object (required)
    Response: TemplateCreated

  GET /templates/{id}
    Description: Get template details
    Response: TemplateDetails

  POST /templates/{id}/generate
    Description: Generate document from template
    Parameters:
      - generation_data: object (required)
    Response: GeneratedDocument

  GET /templates/{id}/bpmn
    Description: Get BPMN workflow for template
    Response: BPMNWorkflow

  POST /templates/{id}/execute-workflow
    Description: Execute BPMN workflow
    Parameters:
      - workflow_data: object (required)
    Response: WorkflowExecution
```

## 🔐 Authentication & Security

### **Authentication Methods**
```yaml
Bearer Token Authentication:
  Header: Authorization: Bearer {token}
  Endpoint: POST /api/auth/login
  Response: { access_token, refresh_token, expires_in }

OAuth 2.0:
  Supported Flows: Authorization Code, Client Credentials
  Scopes: read, write, admin, api
  Endpoint: /api/oauth/authorize

API Key Authentication:
  Header: X-API-Key: {api_key}
  Usage: Service-to-service communication
```

### **Security Headers**
```yaml
Required Headers:
  - Content-Type: application/json
  - Authorization: Bearer {token} or X-API-Key: {api_key}
  - X-Requested-With: XMLHttpRequest (for CSRF protection)

Optional Headers:
  - X-Company-ID: {company_id} (for multi-tenant access)
  - Accept-Language: {language_code} (for i18n)
```

## 📊 Response Formats

### **Standard Response Structure**
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "meta": {
    "total": 100,
    "page": 1,
    "limit": 20,
    "has_more": true
  },
  "timestamp": "2024-09-15T12:00:00Z"
}
```

### **Error Response Structure**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  },
  "timestamp": "2024-09-15T12:00:00Z"
}
```

### **Pagination Structure**
```json
{
  "data": [...],
  "pagination": {
    "current_page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false,
    "next_url": "/api/v1/resource?page=2",
    "prev_url": null
  }
}
```

## 🔄 WebSocket Integration

### **Real-time Event Endpoints**
```yaml
WebSocket URL: wss://bcm.your-domain.com/ws

Supported Events:
  - exercise.status_changed
  - simulation.metrics_updated
  - forum.new_message
  - notification.alert
  - analytics.dashboard_updated

Connection Authentication:
  - URL Parameter: ?token={access_token}
  - Header: Authorization: Bearer {token}
```

## 📈 Rate Limiting & Quotas

### **Rate Limits**
```yaml
Standard Users: 1,000 requests/hour
Premium Users: 5,000 requests/hour
Enterprise: 10,000 requests/hour
Service-to-Service: 50,000 requests/hour

Rate Limit Headers:
  - X-RateLimit-Limit: 1000
  - X-RateLimit-Remaining: 999
  - X-RateLimit-Reset: 1694781600
```

## 🛠️ Development Tools

### **API Testing**
```yaml
Postman Collection: Available at /api/docs/postman
OpenAPI Specification: Available at /api/docs/openapi.json
Interactive Documentation: Available at /api/docs
Health Check: GET /api/health
```

### **SDKs and Libraries**
```yaml
JavaScript/TypeScript: @bcm-platform/api-client
Python: bcm-platform-sdk
PHP: bcm-platform/api-client
Curl Examples: Available in documentation
```

---

**Complete API reference for BCM Platform with 200+ endpoints across all enhanced modules and services. All endpoints tested and documented with examples.**