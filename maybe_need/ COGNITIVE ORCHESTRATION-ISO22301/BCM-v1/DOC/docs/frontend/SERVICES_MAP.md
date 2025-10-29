# BCM Platform Services Map

## 📍 Where Everything Is Located

### **🎯 SCENARIO ORCHESTRATOR** ⭐ **MAIN SERVICE**

**Location**: `/Users/MD/ISO-22301/ai_orchestrator/`
**Container**: `scenario_orchestrator`
**Port**: `http://localhost:8085`
**Status**: ✅ HEALTHY
**Updated**: Added AI integration for scenario generation

**Key Endpoints**:
- `POST /scenarios/generate` - AI scenario generation
- `GET /scenarios/available` - Available scenarios from Odoo
- `GET /health` - Service health check
- `GET /docs` - API documentation

### **🤖 AI ORCHESTRATOR**

**Location**: `/Users/MD/ISO-22301/services/ai_orchestrator/`
**Container**: `ai_orchestrator`
**Port**: `http://localhost:8000`
**Status**: ✅ HEALTHY
**Function**: Main AI coordination hub

### **🔄 BPMN SERVICE**

**Location**: `/Users/MD/ISO-22301/backend/bpmn_service/`
**Container**: `bpmn_service`
**Port**: `http://localhost:8005`
**Function**: BPMN workflow execution engine

### **🏛️ COMMUNITY SERVICE**

**Location**: `/Users/MD/ISO-22301/services/community/`
**Status**: ❓ Not in docker-compose (standalone)
**Function**: Forum & knowledge base
**Integration**: NEW bcm_community Odoo module created

### **🔔 NOTIFICATION SERVICE**

**Location**: `/Users/MD/ISO-22301/services/notification_service/`
**Container**: `notification_service`
**Port**: `http://localhost:8002`
**Updated**: Added Teams/Slack/SMS integrations

## 📁 **DOCUMENTATION LOCATIONS**

### **Main Architecture Document**
📄 `/Users/MD/ISO-22301/docs/integration-architecture.md`
- Complete integration architecture
- Community Service → Odoo strategy
- External service integrations
- Data flow diagrams

### **This Services Map**
📄 `/Users/MD/ISO-22301/docs/SERVICES_MAP.md`
- Service locations and ports
- Container mappings
- Status overview

### **New Odoo Module**
📁 `/Users/MD/ISO-22301/core/odoo-18.0/addons/bcm_community/`
- Forum integration with Community Service
- Models: forum_topic, forum_integration, etc.
- Bridges Odoo data with external forum

## 🔧 **Service Integration Flow**

```
USER REQUEST
    ↓
Scenario Orchestrator (localhost:8085)
    ↓
AI Orchestrator (localhost:8000)
    ↓
Local LLM Generation
    ↓
Odoo BCM Scenario Hub (localhost:8069)
    ↓
bcm_community Module (NEW)
    ↓
Community Service Forum Discussion
    ↓
BPMN Service Workflow (localhost:8005)
    ↓
Exercise Simulators (JaamSim + NICS)
    ↓
Notification Service (Teams/Slack/SMS)
```

## 🎯 **Key URLs for Testing**

### **Scenario Generation** ⭐
```bash
POST http://localhost:8085/scenarios/generate
{
  "category": "cyber",
  "complexity": 3,
  "duration_hours": 4,
  "participants": 8
}
```

### **Service Health Checks**
```bash
curl http://localhost:8085/health  # Scenario Orchestrator
curl http://localhost:8000/health  # AI Orchestrator
curl http://localhost:8005/health  # BPMN Service
curl http://localhost:8002/health  # Notification Service
```

### **Odoo Scenario Hub**
```
http://localhost:8069/web
Menu: Scenario Hub → Scenario Catalog
```

## 🚨 **Potential Issues Found**

### **Duplicate Orchestrators**
Found multiple orchestrator directories:
- `/backend/orchestrator_service/` ❓ (duplicate?)
- `/backend/orchestrator/` ❓ (duplicate?)

### **Community Service Not Containerized**
- Community Service exists but not in docker-compose
- Created bcm_community module to bridge this gap
- Recommendation: Update Community Service to use Odoo API

## 📋 **Next Steps**

1. **Test Scenario Generation**: Use POST /scenarios/generate endpoint
2. **Verify Odoo Integration**: Check if scenarios appear in BCM Scenario Hub
3. **Community Integration**: Install bcm_community module in Odoo
4. **Clean Up**: Remove duplicate orchestrator services if confirmed unused