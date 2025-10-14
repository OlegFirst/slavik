# AI-Platform-ISO v2.0

**Business Continuity Management Platform with AI Intelligence**
**ISO 22301:2019 Compliant | Healthcare-Focused | Non-Commercial**

[![Status](https://img.shields.io/badge/Status-Phase%201%20Complete-green)]()
[![ISO](https://img.shields.io/badge/ISO%2022301-2019-blue)]()
[![License](https://img.shields.io/badge/License-Non--Commercial-orange)]()

---

## 🎯 Quick Start

### For New Users
```bash
# 1. Clone repository
git clone <repository-url>
cd AI-Platform-ISO

# 2. Read documentation
open docs/README.md
open docs/GETTING_STARTED.md

# 3. Start Phase 1 Infrastructure
open PHASE1_QUICK_START.md
```

### For Developers
```bash
# Deploy monitoring stack
cd infrastructure/observability
docker-compose -f docker-compose.monitoring.yml up -d

# Start infrastructure coordinator
cd infrastructure/eventbus/coordination
python3 infrastructure_coordinator.py
```

### For Architects
- [Complete Architecture](docs/ARCHITECTURE.md)
- [Phase 1 Analysis](doc-project/PHASE1_CRITICAL_ANALYSIS.md)
- [Governance Gap](doc-project/PHASE1_GOVERNANCE_GAP_SUMMARY.md)

---

## 📊 Project Status

### ✅ Phase 1: Infrastructure Coordination (COMPLETE)

**Completed (2025-10-09):**
- Health Monitoring with EventBus integration
- Auto-Recovery Service (exponential backoff)
- Resource Optimizer (5-minute cycles)
- Infrastructure Coordinator
- Metrics API (Prometheus integration)
- Event Catalog (133 events)
- Comprehensive documentation

**Status:** ✅ Technically complete
**Governance:** ⚠️ Requires governance layer (see critical analysis)

**Quick Links:**
- [Phase 1 Complete Summary](doc-project/PHASE_1_COMPLETE_SUMMARY.md)
- [Deployment Guide](infrastructure/observability/PHASE1_DEPLOYMENT_GUIDE.md)
- [Critical Analysis](doc-project/PHASE1_CRITICAL_ANALYSIS.md)
- [Quick Start](PHASE1_QUICK_START.md)

---

## 🏗️ Architecture

### 4-Level Coordination Architecture

```
┌─────────────────────────────────────────────┐
│ PROGRAM LEVEL (Strategic)                   │
│ Goal Setting | Policy Definition | KPIs     │
└─────────────────┬───────────────────────────┘
                  │ (Goals & Policies)
                  ↓
┌─────────────────────────────────────────────┐
│ CENTER LEVEL (Coordination)                 │
│ Decision Center | Context | Priorities      │
└─────────────────┬───────────────────────────┘
                  │ (Decisions & Context)
                  ↓
┌─────────────────────────────────────────────┐
│ CORE LEVEL (Intelligence) - 11 Modules      │
│ AI Orchestrator | Workflows | Expertise     │
│ Predictive | Collective | System BCM        │
└─────────────────┬───────────────────────────┘
                  │ (Insights & Recommendations)
                  ↓
┌─────────────────────────────────────────────┐
│ INFRASTRUCTURE LEVEL - ✅ Phase 1 Complete  │
│ Health Monitor | Auto-Recovery | Optimizer  │
│ Metrics API | EventBus | Observability      │
└─────────────────┬───────────────────────────┘
                  │ (Monitoring & Actions)
                  ↓
┌─────────────────────────────────────────────┐
│ SERVICES LEVEL - 12 BCM Services            │
│ BIA | Risk | Planning | Compliance | etc.   │
└─────────────────────────────────────────────┘
```

### Technology Stack

**Infrastructure:**
- EventBus: Redis Streams + RabbitMQ
- Database: PostgreSQL (Supabase)
- Monitoring: Prometheus + Grafana
- Security: Vault + JWT
- Orchestration: Docker + Docker Compose

**Intelligent Core:**
- AI: OpenAI GPT-4, Anthropic Claude
- ML: Scikit-learn, TensorFlow
- Workflows: Temporal
- RAG: Qdrant vector database
- NLP: spaCy, transformers

**Platform Services:**
- FastAPI (Python 3.9+)
- AsyncIO event-driven
- ISO 22301 compliant

---

## 📁 Project Structure

```
AI-Platform-ISO/
├── infrastructure/           # Infrastructure Layer
│   ├── eventbus/            # ✅ Redis Streams + EventBus
│   │   ├── coordination/    # ✅ Phase 1 Services
│   │   └── events/          # ✅ Event Catalog (133 events)
│   ├── observability/       # ✅ Prometheus + Grafana
│   ├── database/            # PostgreSQL + migrations
│   └── security/            # Vault + auth
│
├── intelligent-core/         # AI Intelligence Layer
│   ├── orchestration/       # AI Orchestrator + Metrics API
│   ├── workflow_intelligence/ # Temporal workflows
│   ├── expertise-center/    # 14 AI specialists
│   ├── ai-foundation/       # LLM, RAG, ML
│   │   └── utils/           # ✨ NEW: ResourceTracker (shared utility)
│   ├── predictive/          # ML predictions
│   ├── collective/          # 347+ case library
│   └── system-bcm-service/  # Platform BCM (port 8050) + ResourceTracker integration
│
├── platform-services/        # BCM Services
│   ├── bia-service/         # Business Impact Analysis
│   ├── risk-service/        # Risk Assessment
│   ├── compliance-service/  # ISO 22301 Compliance
│   ├── planning-service/    # BC Planning
│   ├── governance-service/  # Governance
│   ├── learning-service/    # Training
│   └── ... (6 more)
│
├── docs/                     # Platform Documentation
│   ├── 13 sections          # Organized documentation
│   └── 125+ files           # Complete platform docs
│
├── doc-project/              # Project Documentation
│   ├── PHASE_1_COMPLETE_SUMMARY.md
│   ├── PHASE1_CRITICAL_ANALYSIS.md ⚠️ IMPORTANT
│   ├── PHASE1_GOVERNANCE_GAP_SUMMARY.md
│   └── ... (277 files)
│
└── comprehensive-platform-docs/  # AI Capabilities
    └── 570+ usage scenarios
```

---

## 🚀 Features

### ✅ Infrastructure Level (Phase 1)

**Health Monitoring:**
- 30-second health checks for critical services
- Event-driven status change detection
- Publishes: `infrastructure.health.*` events

**Auto-Recovery:**
- Exponential backoff recovery strategies
- Supports: restart, failover, circuit_breaker
- Publishes: `infrastructure.recovery.*` events
- ⚠️ **NEEDS:** Escalation mechanism (see critical analysis)

**Resource Optimization:**
- 5-minute optimization cycles
- CPU/Memory/Disk utilization analysis
- Efficiency score calculation (0-100)
- Publishes: `infrastructure.optimization.completed`

**Observability:**
- Prometheus metrics on port 9091
- Grafana dashboards
- AlertManager integration
- Complete event catalog

### 🧠 Intelligent Core

**AI Orchestrator:**
- 6-step cognitive loop
- Multi-agent coordination
- Context management
- Decision making

**Expertise Center:**
- 14 AI specialists (Database, Security, Performance, etc.)
- Domain expertise consultation
- Best practices recommendations

**Workflow Intelligence:**
- Temporal workflow orchestration
- State machines
- Saga patterns
- Distributed transactions

**Predictive Intelligence:**
- ML-based predictions (87% accuracy)
- Anomaly detection
- Trend analysis
- Forecasting

**Collective Intelligence:**
- 347+ anonymized case library
- Pattern recognition
- Peer learning

**✨ ResourceTracker (NEW - 2025-10-11):**
- Platform resource monitoring (CPU, Memory, Disk I/O, Network)
- Trend analysis and deficit prediction
- Integrated into System BCM Service
- Available as shared utility for all services

### 📋 BCM Platform Services

**12 ISO 22301 Compliant Services:**
1. BIA Service (Clause 8.2.2)
2. Risk Service (Clause 6.1)
3. Planning Service (Clause 8.3)
4. Plans Service (Clause 8.4)
5. Compliance Service (Clause 9.2, 10.1, 10.2)
6. Validation Service (Clause 8.5)
7. Documents Service (Clause 7.5)
8. Response Service (Clause 8.4)
9. Learning Service (Clause 7.2)
10. Governance Service (Clause 5.3, 7.1, 7.3)
11. Community Service (Clause 7.4)
12. Simulation Service

---

## 📊 Statistics

### Platform
- **Services:** 23 total (12 platform + 11 intelligent-core)
- **Ports:** 20+ mapped services
- **Events:** 133 event types
- **API Endpoints:** 150+
- **ISO Coverage:** 10/10 clauses (ISO 22301)

### AI Capabilities
- **AI Modules:** 11
- **AI Specialists:** 14
- **Case Library:** 347+ anonymized cases
- **Usage Scenarios:** 570+
- **Prediction Accuracy:** 87% average

### Documentation
- **Total Files:** 420+ documents
- **Platform Docs:** 125+ files
- **Project Docs:** 277 files
- **Code Documentation:** Comprehensive

---

## ⚠️ Critical Governance Gap

**READ THIS:** [Phase 1 Critical Analysis](doc-project/PHASE1_CRITICAL_ANALYSIS.md)

### Key Issues Identified:

1. **❌ No Decision Center** - System operates autonomously
2. **❌ No Accountability** - Not reporting to higher levels
3. **❌ No Goal Management** - Goals hardcoded by developer
4. **❌ Weak AI Integration** - Not using existing AI capabilities
5. **❌ No Escalation** - Auto-recovery can loop indefinitely

### Governance Maturity: 20/100

```
Decision Making:     ████░░░░░░ 20/100  ❌
Accountability:      ██░░░░░░░░ 10/100  ❌
Goal Management:     ███░░░░░░░ 15/100  ❌
Policy Compliance:   ███░░░░░░░ 25/100  ❌
AI Integration:      ████░░░░░░ 40/100  ⚠️

Overall:             ███░░░░░░░ 20/100  ❌ CRITICAL
```

### Required Before Production:

**MUST HAVE (Blockers):**
- [ ] Minimal Decision Center
- [ ] Escalation mechanism
- [ ] Audit logging (ISO 22301)
- [ ] Policy configuration (YAML)

**SHOULD HAVE:**
- [ ] AI Orchestrator integration
- [ ] Workflow Intelligence integration
- [ ] Expertise Center consultation

**See:** [Governance Gap Summary](doc-project/PHASE1_GOVERNANCE_GAP_SUMMARY.md)

---

## 🎯 Roadmap

### ✅ Phase 1: Infrastructure Level (COMPLETE)
- Health monitoring
- Auto-recovery
- Resource optimization
- Metrics & observability

### 🔄 Phase 1.1: Minimal Governance (URGENT - 1-2 days)
- [ ] Minimal Decision Center
- [ ] Escalation mechanism
- [ ] Enhanced audit logging
- [ ] Policy configuration

### 🔄 Phase 1.5: AI Integration (IMPORTANT - 1 week)
- [ ] AI Orchestrator integration
- [ ] Expertise Center consultation
- [ ] Workflow Intelligence for complex recovery
- [ ] Predictive analytics

### 🔜 Phase 2: Core Level Coordination (2 weeks)
- [ ] Workflow Intelligence coordination
- [ ] AI Foundation coordination
- [ ] Expertise Center coordination
- [ ] Proactive intelligence

### 🔜 Phase 3: Center Level Orchestration (3 weeks)
- [ ] Decision Center (full version)
- [ ] Context Aggregator
- [ ] Priority Engine
- [ ] Conflict Resolution

### 🔜 Phase 4: Program Level Governance (4 weeks)
- [ ] Strategic Planning
- [ ] Resource Allocation
- [ ] Compliance Oversight
- [ ] Business Alignment

---

## 📚 Documentation

### Getting Started
- [Platform README](docs/README.md)
- [Getting Started Guide](docs/GETTING_STARTED.md)
- [Architecture Overview](docs/ARCHITECTURE.md)

### Phase 1 Documentation
- [Quick Start Guide](PHASE1_QUICK_START.md) - Deploy in 3 commands
- [Complete Summary](doc-project/PHASE_1_COMPLETE_SUMMARY.md) - Full details
- [Deployment Guide](infrastructure/observability/PHASE1_DEPLOYMENT_GUIDE.md) - Step-by-step
- [Infrastructure Events](infrastructure/eventbus/events/INFRASTRUCTURE_EVENTS.md) - Event catalog

### ⚠️ Critical Analysis
- [Critical Analysis](doc-project/PHASE1_CRITICAL_ANALYSIS.md) - Deep dive into issues
- [Governance Gap Summary](doc-project/PHASE1_GOVERNANCE_GAP_SUMMARY.md) - Quick overview
- [Integration Plan](doc-project/PHASE_1_INTEGRATION_PLAN.md) - Original plan

### Technical Documentation
- [EventBus Architecture](infrastructure/eventbus/ARCHITECTURE.md)
- [AI Orchestrator](docs/ai-capabilities/AI_ORCHESTRATION_CAPABILITIES.md)
- [API Reference](docs/API_REFERENCE.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)

---

## 🔧 Development

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- PostgreSQL (or Supabase)
- Redis
- Node.js 16+ (for EventCatalog)

### Environment Variables
```bash
DATABASE_URL="postgresql://user:pass@host:5432/db"
REDIS_URL="redis://localhost:6379"
SUPABASE_URL="https://xxx.supabase.co"
SUPABASE_SERVICE_ROLE_KEY="xxx"
OPENAI_API_KEY="sk-xxx"
ANTHROPIC_API_KEY="sk-ant-xxx"
```

### Local Development
```bash
# Start infrastructure
cd infrastructure/observability
docker-compose -f docker-compose.monitoring.yml up -d

# Start metrics API
cd intelligent-core/orchestration/api
python3 metrics_api.py

# Start infrastructure coordinator
cd infrastructure/eventbus/coordination
python3 infrastructure_coordinator.py
```

### Access Points
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)
- Metrics API: http://localhost:9091
- EventCatalog: http://localhost:3002 (npm run dev)
- System BCM: http://localhost:8050
- **Admin Panel**: http://localhost:3000 ([Setup Guide](docs/ADMIN_PANEL_CONSOLIDATION_PLAN.md))

### 🖥️ Admin Control Center

**Location**: `/interface/admin_panel/`

Unified administrative dashboard for platform management and monitoring.

**Quick Start**:
```bash
cd interface/admin_panel
npm install
npm run dev
# Open http://localhost:3000
```

**Features**:
- Real-time service monitoring
- AI organisms management
- System configuration
- PDCA analytics (planned)
- Alert management (planned)
- User & role management (planned)

**Documentation**:
- [Monitoring System Specification](docs/TZ_MONITORING_ADMIN_PANEL.md) - Complete technical specification
- [Consolidation Plan](docs/ADMIN_PANEL_CONSOLIDATION_PLAN.md) - Setup and integration guide
- [Quick Reference](docs/QUICK_REFERENCE_INDEX.md) - Complete documentation index

---

## 🤝 Contributing

**Note:** This is a non-commercial social impact project for healthcare BCM.

### Project Philosophy
1. **Healthcare Focus** - Designed for healthcare BCM needs
2. **Non-Commercial** - Social impact, not profit
3. **ISO Compliance** - Strict ISO 22301:2019 adherence
4. **AI-Powered** - Leverage AI for better BCM
5. **Community-Driven** - Learning from practice

### Development Principles
- Choreography over Orchestration (Infrastructure level)
- Event-Driven Architecture
- Microservices patterns
- ISO 22301 compliance by design
- Comprehensive documentation

---

## 📞 Support & Contact

### Documentation
- Project Index: [PROJECT_INDEX.md](PROJECT_INDEX.md)
- Platform Docs: [docs/](docs/)
- Project Docs: [doc-project/](doc-project/)

### Issues & Feedback
- GitHub Issues: (configure repository URL)
- Documentation Feedback: See docs README

### Community
- Healthcare BCM practitioners
- ISO 22301 consultants
- Humanitarian organizations
- Non-profit healthcare providers

---

## 📄 License

**Non-Commercial Use Only**

This platform is designed for:
- Healthcare organizations
- Humanitarian aid organizations
- Non-profit BCM practitioners
- Educational institutions
- ISO 22301 consultants (non-commercial)

Commercial use requires separate licensing.

---

## 🙏 Acknowledgments

**Built With:**
- EventBus Architecture (Redis Streams)
- AI Foundation (OpenAI, Anthropic)
- Temporal Workflows
- Prometheus & Grafana
- ISO 22301:2019 Framework

**Special Thanks:**
- Healthcare BCM community
- ISO Technical Committee
- Open-source contributors

---

## 🚨 Important Notes

### Before Production Deployment:

1. **READ:** [Phase 1 Critical Analysis](doc-project/PHASE1_CRITICAL_ANALYSIS.md)
2. **IMPLEMENT:** Phase 1.1 Minimal Governance (see Governance Gap Summary)
3. **VERIFY:** All database migrations applied
4. **CONFIGURE:** Environment variables
5. **TEST:** Integration tests
6. **REVIEW:** Security configuration

### Known Limitations:

- **No Decision Center** - System operates autonomously (⚠️ RISK)
- **No Escalation** - Auto-recovery may loop indefinitely (⚠️ RISK)
- **Limited AI Integration** - Not using full AI capabilities
- **Hardcoded Goals** - Goals not from governance layer
- **No Accountability** - Not reporting to higher levels

**See Governance Gap Summary for complete analysis.**

---

## 📊 Project Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Infrastructure Level | ✅ Complete | Phase 1 done |
| Governance Layer | ❌ Missing | Phase 1.1 needed |
| AI Integration | ⚠️ Partial | Phase 1.5 needed |
| Core Level | 🔜 Planned | Phase 2 |
| Center Level | 🔜 Planned | Phase 3 |
| Program Level | 🔜 Planned | Phase 4 |
| **Production Ready** | ⚠️ **After 1.1** | Governance required |

---

**Version:** 2.0.0-phase1
**Last Updated:** 2025-10-09
**Status:** Phase 1 Complete, Governance Layer Required

**Next Steps:** Implement Phase 1.1 Minimal Governance → See [Governance Gap Summary](doc-project/PHASE1_GOVERNANCE_GAP_SUMMARY.md)

---

**🤖 Built with AI Partnership | 🏥 For Healthcare BCM | 🌍 Social Impact Project**
