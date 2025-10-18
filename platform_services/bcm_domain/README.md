# BCM Domain Package

**Business Continuity Management for ISO 22301:2019 Compliance**

---

## 📋 Overview

This package consolidates all BCM (Business Continuity Management) functionality in one place:

- **12 Platform Services** - BIA, Risk, Planning, Compliance, etc.
- **9 AI Colleagues** - Intelligent BCM assistants
- **Knowledge Base** - ISO 22301, BCI GPG, scenarios, cases
- **Knowledge Quality Manager** - Auto-scenario generation and knowledge QA
- **Workflows** - BCM-specific process definitions

---

## 🏗️ Architecture

```
bcm_domain/
│
├── services/                    # BCM Platform Services (Port 80XX)
│   ├── bia_service/            # Business Impact Analysis (8012)
│   ├── risk_service/           # Risk Assessment (8015)
│   ├── compliance_service/     # ISO Compliance (8014)
│   ├── planning_service/       # BC Planning (8011)
│   ├── governance_service/     # Governance (8017)
│   ├── plans_service/          # Plans & Procedures (8023)
│   ├── response_service/       # Incident Response (8016)
│   ├── documents_service/      # Document Management (8018)
│   ├── validation_service/     # Testing & Validation (8021)
│   ├── learning_service/       # Training (8019)
│   ├── community_service/      # Community (8020)
│   └── simulation_service/     # Simulations (8095)
│
├── ai_colleagues/               # BCM AI Colleagues
│   ├── coordinator.py          # Routes to appropriate colleague
│   ├── base_bcm_colleague.py   # Base class for BCM colleagues
│   ├── bia_specialist/         # BIA expertise (RTO/RPO)
│   ├── risk_analyst/           # Risk analysis
│   ├── compliance_copilot/     # ISO 22301 compliance
│   ├── exercise_designer/      # BC exercise design
│   ├── incident_advisor/       # Incident response
│   ├── plan_generator/         # BC plan generation
│   ├── project_manager/        # BCM project management
│   └── project_intelligence/   # Project analytics
│
├── knowledge/                   # BCM Knowledge Base
│   ├── iso_22301/              # ISO 22301:2019 standard
│   ├── bci_gpg/                # BCI Good Practice Guidelines
│   ├── scenarios/              # BCM scenarios library
│   └── case_library/           # Anonymized BCM cases
│
├── workflows/                   # BCM Workflow Definitions
│   └── bcm_processes.py        # Standard BCM processes
│
└── knowledge_quality_manager/   # Knowledge QA Service (Port 8090)
    ├── main.py                 # FastAPI service
    ├── scenario_generator.py   # Auto-scenario generation
    ├── knowledge_monitor.py    # Knowledge coverage monitoring
    └── compliance_controller.py # Compliance validation
```

---

## 🚀 Quick Start

### Using BCM AI Colleagues

```python
from platform_services.bcm_domain.ai_colleagues import BIASpecialistAI
from intelligent_core.ai_foundation import RAGPipeline

# Initialize RAG pipeline
rag = RAGPipeline(config={...})

# Create BIA Specialist
bia_ai = BIASpecialistAI(rag_pipeline=rag, config={
    "model": "claude-sonnet-3.5",
    "temperature": 0.7
})

# Ask for help
response = await bia_ai.process_message(
    "Help me determine RTO and RPO for our payment processing system"
)

print(response.message)
# Output: "For payment processing (critical financial system),
#          I recommend RTO: 2-4 hours, RPO: 15 minutes..."
```

### Using BCM Services

```python
from platform_services.bcm_domain.services.bia_service import conduct_bia

# Conduct BIA for a process
result = await conduct_bia(
    process_id="proc-payment-001",
    process_name="Payment Processing",
    context={...}
)

print(f"RTO: {result.rto_hours}h, RPO: {result.rpo_minutes}min")
```

### Using Knowledge Quality Manager

```bash
# Start KQM service
cd platform_services/bcm_domain/knowledge_quality_manager
python main.py

# Access on http://localhost:8090
# - Auto-generates scenarios every 24 hours
# - Monitors knowledge coverage
# - Validates ISO compliance
```

---

## 🔌 Integration

### With Intelligent Core

BCM Domain uses generic AI capabilities from `intelligent_core`:

```python
# RAG for knowledge retrieval
from intelligent_core.ai_foundation import RAGPipeline

# LLM for text generation
from intelligent_core.ai_foundation import LLMRouter

# ML for predictions
from intelligent_core.ai_foundation import WorkflowPredictor

# Workflow engine
from intelligent_core.workflow_intelligence import WorkflowEngine
```

### With Infrastructure

```python
# EventBus for event choreography
from infrastructure.eventbus import EventBus

# Decision Center for governance
from infrastructure.decision_center import DecisionCenter

# Policy Engine
from infrastructure.policy_engine import PolicyEngine
```

---

## 📊 Services Overview

| Service | Port | ISO Clause | Purpose |
|---------|------|-----------|---------|
| **BIA Service** | 8012 | 8.2.2 | Business Impact Analysis |
| **Planning Service** | 8011 | 8.3 | BC Strategy & Planning |
| **Plans Service** | 8023 | 8.4 | Plans & Procedures |
| **Compliance Service** | 8014 | 9.2, 10.1, 10.2 | Audits & Compliance |
| **Risk Service** | 8015 | 6.1 | Risk Assessment |
| **Governance Service** | 8017 | 5.3, 7.1, 7.3 | Governance & Leadership |
| **Response Service** | 8016 | 8.4.4 | Incident Response |
| **Documents Service** | 8018 | 7.5 | Document Management |
| **Validation Service** | 8021 | 8.5 | Testing & Exercises |
| **Learning Service** | 8019 | 7.2 | Training & Awareness |
| **Community Service** | 8020 | 7.4 | Community & Knowledge Sharing |
| **Simulation Service** | 8095 | - | BC Simulations |

---

## 🤖 AI Colleagues Overview

| Colleague | Specialty | Use Cases |
|-----------|-----------|-----------|
| **BIA Specialist** | RTO/RPO determination, Impact assessment | "What should be the RTO for payroll?" |
| **Risk Analyst** | Risk identification, Threat assessment | "Analyze risks to our data center" |
| **Compliance Copilot** | ISO 22301 compliance, Gap analysis | "Check compliance with Clause 8.2" |
| **Exercise Designer** | BC exercise planning, Scenario design | "Design a ransomware tabletop exercise" |
| **Incident Advisor** | Incident response, Recovery coordination | "We have a datacenter fire, what now?" |
| **Plan Generator** | BC plan creation, Procedure development | "Generate BCP for IT department" |
| **Project Manager** | BCM project management, Task coordination | "Create BCM implementation roadmap" |
| **Project Intelligence** | Project analytics, Status reporting | "Show BCM program maturity" |

---

## 📚 Knowledge Base

### ISO 22301:2019 Coverage

- ✅ All 10 clauses documented
- ✅ 1000+ scenarios covering requirements
- ✅ Clause-to-service mapping
- ✅ Compliance validation rules

### Standards Included

- **ISO 22301:2019** - Business Continuity Management Systems
- **ISO 22313:2020** - Guidance for BCM
- **BCI GPG 2018** - BCI Good Practice Guidelines
- **WHO ERF** - WHO Emergency Response Framework

---

## 🔄 Migration Notes

This package consolidates functionality from:

**Old Structure:**
```
intelligent_core/expertise_center/ai_office/ВСМ-colleagues/
platform_services/bia_service/
platform_services/AI_services_management/
```

**New Structure:**
```
platform_services/bcm_domain/
├── ai_colleagues/          (from ai_office)
├── services/               (from platform_services/)
└── knowledge_quality_manager/  (from AI_services_management)
```

**Backward Compatibility:**
Symlinks maintain compatibility during transition:
```bash
intelligent_core/expertise_center/ai_office → symlink → bcm_domain/ai_colleagues
```

---

## 🎯 Roadmap

### Phase 1: Consolidation (Current)
- [x] Create bcm_domain structure
- [ ] Migrate AI colleagues
- [ ] Migrate BCM services
- [ ] Migrate knowledge base
- [ ] Update imports

### Phase 2: Enhancement
- [ ] Add more AI colleagues
- [ ] Expand scenario library
- [ ] Enhance KQM with ML
- [ ] Add predictive analytics

### Phase 3: Multi-Standard
- [ ] Prepare for ISO 27001 (security_domain)
- [ ] Prepare for GDPR (privacy_domain)
- [ ] Cross-domain knowledge sharing

---

## 📞 Support

- **Documentation**: See individual service READMEs
- **API Docs**: http://localhost:8090/docs (KQM)
- **Issues**: GitHub Issues

---

**Version:** 1.0.0
**ISO Compliance:** ISO 22301:2019
**License:** Non-Commercial (Social Impact)
