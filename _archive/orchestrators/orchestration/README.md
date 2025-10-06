# Orchestration Service - BCM Platform

**Purpose:** AI-powered service orchestration and workflow coordination

**Technology:** FastAPI + Redis + AI/ML

**Port:** 8002

---

## 🎯 Features

### Core Functionality
- ✅ **AI Agent Routing** - Route requests to appropriate AI models (GPT-4, Claude, etc.)
- ✅ **Service Coordination** - Coordinate multiple service calls
- ✅ **Workflow Automation** - Automate BCM workflows
- ✅ **Risk Analysis** - AI-powered risk assessment
- ✅ **Incident Classification** - Automatic incident categorization
- ✅ **NLP Queries** - Natural language processing for BCM queries
- ✅ **BIA Automation** - Automated Business Impact Analysis

### AI Capabilities
- ✅ **Multi-Model Support** - OpenAI GPT-4, Anthropic Claude, local models
- ✅ **Intelligent Routing** - Route to best model based on task
- ✅ **Context Management** - Maintain conversation context
- ✅ **Prompt Library** - Reusable BCM-specific prompts

---

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

### AI Agent Routing
```bash
POST /api/ai/route
{
  "task": "analyze_risk",
  "input": {...},
  "model_preference": "gpt-4"
}
```

### Risk Analysis
```bash
POST /api/intelligence/analyze-risk
{
  "process_id": 123,
  "criticality": 5,
  "rto_hours": 4,
  "dependencies": [1, 2, 3]
}
```

### Incident Classification
```bash
POST /api/intelligence/classify-incident
{
  "title": "Server outage",
  "description": "Production server is down",
  "affected_systems": ["web", "api"]
}
```

---

## 🚀 Integration

Orchestration service integrates with:
- **EventBus** - Publish orchestration events
- **Gateway** - Receive requests from gateway
- **BCM Services** - Coordinate BIA, Risk, Plans
- **AI Models** - OpenAI, Anthropic, local models

---

**Version:** 1.0
**Status:** ✅ Consolidated
**Port:** 8002
