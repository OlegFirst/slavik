# Module Documentation

Complete documentation for all platform modules organized by layer.

**Last Updated**: 2025-10-09

---

## Module Organization

### Infrastructure Layer
Documentation for infrastructure components:
- EventBus (Redis Streams + RabbitMQ)
- Database (PostgreSQL + Supabase)
- Security (Vault + JWT)
- Observability (Prometheus + Grafana)
- API Gateway
- Vector DB (Qdrant)

**Location**: `/infrastructure/{component}/README.md`

---

### Intelligent Core Layer (11 Modules)

Each module has complete documentation package:

```
{module}/
├── README.md
└── docs/
    ├── ARCHITECTURE.md
    ├── TECHNICAL_SPECIFICATION.md
    ├── BUSINESS_LOGIC.md
    ├── API.md
    ├── INTEGRATION.md
    └── DEPLOYMENT.md
```

**Modules**:
1. ai-foundation
2. workflow_intelligence (Port 8037)
3. expertise-center (Port 8036)
4. collective (Port 8032)
5. predictive (Port 8031)
6. community_intelligence (Port 8038)
7. event_intelligence (Port 8039)
8. orchestration
9. ai_workflow_optimizer
10. workflow-engine (Port 8041)
11. system-bcm-service (Port 8050)

**Total**: ~77 technical documents (11 × 7)

---

### Platform Services Layer (12 Services)

Each service has documentation package:

```
{service}/
├── README.md
└── docs/
    ├── TECHNICAL_SPECIFICATION.md
    ├── API.md
    ├── BUSINESS_LOGIC.md
    ├── INTEGRATION.md
    └── DEPLOYMENT.md
```

**Services** (ISO 22301 mapped):
1. bia-service (8.2) - Port 8001
2. risk-service (8.3) - Port 8002
3. compliance-service (9.1) - Port 8003
4. planning-service (8.4) - Port 8004
5. response-service (8.4) - Port 8005
6. documents-service (7.5) - Port 8006
7. governance-service (5.0) - Port 8007
8. validation-service (8.5) - Port 8008
9. learning-service (7.3) - Port 8009
10. bcm-coordination-service - Port 8010
11. community-service - Port 8011
12. monitoring (9.0) - Port 8012

**Total**: ~72 technical documents (12 × 6)

---

## Documentation Standards

All module documentation follows:
- ISO/IEC/IEEE 26514:2022 (Software documentation)
- Professional English only
- Consistent structure across modules
- Code examples tested and working
- API documentation with request/response samples

---

## Quick Access

### By Layer
- Infrastructure: `/infrastructure/*/README.md`
- Intelligent Core: `/intelligent-core/*/README.md`
- Platform Services: `/platform-services/*/README.md`

### By Function
- AI Capabilities: `/intelligent-core/ai-foundation/`
- Workflows: `/intelligent-core/workflow_intelligence/`
- BCM Services: `/platform-services/{bia,risk,compliance,...}/`

---

**Total Module Documentation**: ~149 files (infrastructure + modules + services)
**Last Updated**: 2025-10-09
