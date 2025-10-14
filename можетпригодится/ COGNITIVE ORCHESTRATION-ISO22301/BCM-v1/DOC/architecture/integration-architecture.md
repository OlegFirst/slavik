# BCM Platform Integration Architecture

## 🎯 Цель
Интеграция всех компонентов через Odoo модули как центральную систему управления.

## 🏗 Новая архитектура

### Уровень 1: Odoo Core (Data & Logic)
```
bcm_scenario_hub     → Сценарии и marketplace
bcm_community        → NEW: Community forum integration
bcm_workflow         → NEW: BPMN process management
bcm_exercise         → Упражнения и симуляции
bcm_notification     → Уведомления и алерты
```

### Уровень 2: API Services (Processing)
```
Scenario Orchestrator → AI generation + Odoo integration
BPMN Service         → Workflow execution engine
Notification Service → External communications
Exercise Simulators  → JaamSim + NICS execution
```

### Уровень 3: External Integrations
```
Teams/Slack    → Notifications
TheHive        → Security incidents
NICS Platform  → Command structure
GitHub         → Development workflow
```

## 🔄 Integration Flows

### Scenario Lifecycle
```
1. AI Generation:
   Scenario Orchestrator → bcm_scenario_hub.create()

2. Community Review:
   bcm_community → Rating/Discussion threads

3. Workflow Creation:
   bcm_workflow → BPMN Process Template

4. Exercise Execution:
   bcm_exercise → Exercise Simulators

5. Results Analysis:
   Exercise Results → AI Learning → Scenario Improvement
```

### Data Flow
```
Odoo PostgreSQL (Single Source of Truth)
    ↕
bcm_* modules (Business Logic)
    ↕
API Services (Processing & Integration)
    ↕
External Systems (Teams, NICS, etc.)
```

## 📋 Migration Plan

### Phase 1: Community Integration
- Create `bcm_community` Odoo module
- Migrate forum data to Odoo models
- Update Community Service to use Odoo API

### Phase 2: BPMN Integration
- Create `bcm_workflow` Odoo module
- Integrate BPMN Service with Odoo workflows
- Create workflow templates for scenarios

### Phase 3: Notification Integration
- Create `bcm_notification` Odoo module
- Centralize all notification logic in Odoo
- External services as notification channels

### Phase 4: Exercise Integration
- Enhance `bcm_exercise` module
- Full JaamSim/NICS integration
- Real-time exercise monitoring

## 🎯 Benefits

### Consistency
- Single data model across all components
- Unified user management and permissions
- Consistent API patterns

### Maintainability
- All business logic in Odoo modules
- Services focus on processing/integration
- Clear separation of concerns

### Scalability
- Odoo's multi-tenant architecture
- Modular component architecture
- External service independence

## 🔧 Implementation

### New Odoo Modules Needed:

1. **bcm_community**
   - Forum topics/posts models
   - Integration with res.users
   - Knowledge base management

2. **bcm_workflow**
   - BPMN process templates
   - Workflow instance tracking
   - Task assignment integration

3. **bcm_notification**
   - Notification templates
   - Channel management (Teams/Slack/SMS)
   - Escalation rules

### Service Updates:

1. **Community Service → API Gateway**
   - Remove duplicate models
   - Use Odoo API for all operations
   - Focus on WebSocket/real-time features

2. **BPMN Service → Engine Only**
   - Process execution engine
   - Integrate with bcm_workflow module
   - Task completion callbacks

3. **Notification Service → Channel Handler**
   - External API integrations only
   - Receive from bcm_notification module
   - Status reporting back to Odoo