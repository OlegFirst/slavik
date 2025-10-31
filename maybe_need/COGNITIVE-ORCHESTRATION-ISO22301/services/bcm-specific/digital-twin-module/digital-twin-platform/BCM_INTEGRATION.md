# BCM Digital Twin Platform Integration

## Overview
This Digital Twin platform has been integrated into the ISO-22301 BCM ecosystem as a core service component.

## Integration Architecture

### Service Location
- **Original path**: `/Users/MD/digital-twin-bcm-integration/digital-twin-main`
- **New integrated path**: `/Users/MD/ISO-22301/services/digital-twin-platform`
- **Integration mode**: Hybrid (Odoo + Node.js + PostgreSQL)

### BCM Platform Integration Points

#### 1. Odoo Integration
- **Connection**: HTTP API bridge to Odoo 18 on localhost:8069
- **Database**: bcm_platform
- **Models integrated**:
  - `bcm.digital.twin` - Digital Twin organizations
  - `bcm.digital.copy` - Snapshot/version management
  - `bcm.ai.consultant` - AI-powered BCM consultant
  - `bcm.client` - BCM clients and organizations

#### 2. Service Architecture
```
ISO-22301/
├── core/odoo-18.0/
│   └── addons/
│       ├── bcm_digital_twin_core/     # Core DT models
│       ├── bcm_digital_copy_manager/  # Snapshot system
│       └── bcm_ai_consultant/         # AI consultant
└── services/
    ├── digital-twin-platform/         # This service
    ├── ai_orchestrator/              # AI organs coordinator
    ├── web-dashboard/                # Web interface
    └── shared/                       # Common utilities
```

#### 3. API Bridge
- **File**: `src/odoo-bridge.js`
- **Port**: 3000 (Node.js service)
- **Odoo Port**: 8069
- **Functions**:
  - Digital Twin CRUD operations
  - Snapshot creation/restoration
  - AI consultant messaging
  - BCM client management

### Environment Configuration

Key environment variables for BCM integration:
```bash
# BCM Platform Integration
ODOO_URL=http://localhost:8069
ODOO_DATABASE=bcm_platform
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
INTEGRATION_MODE=hybrid

# Paths
BCM_PLATFORM_ROOT=/Users/MD/ISO-22301
SERVICES_ROOT=/Users/MD/ISO-22301/services
DIGITAL_TWIN_SERVICE_PATH=/Users/MD/ISO-22301/services/digital-twin-platform
```

### Database Integration

#### PostgreSQL Database
- **Host**: localhost:5432
- **Database**: digital_twin_db
- **User**: odoo
- **Purpose**: High-performance simulations and analytics

#### Hybrid Mode Benefits
- **Odoo**: Business logic, BCM workflows, user management
- **PostgreSQL**: Time-series data, simulation results, large datasets
- **Node.js**: Real-time processing, external API integration

### AI Organs Integration

The platform integrates with 10 AI Organs managed by the BCM AI Orchestrator:

1. **Governance Brain** - Strategic BCM governance
2. **Emergency Response** - Incident response coordination
3. **Impact Oracle** - Business impact prediction
4. **Scenario Creator** - Risk scenario generation
5. **Risk Advisor** - Risk assessment and mitigation
6. **Compliance Guardian** - ISO 22301 compliance monitoring
7. **Performance Analyst** - BCM effectiveness metrics
8. **Learning Coach** - Training and awareness
9. **Plan Generator** - BCM plan creation
10. **Lifecycle Monitor** - Continuous improvement

### Web Interface Integration

- **Dashboard**: Available at `http://localhost:3000`
- **BCM Menu**: Integrated into Odoo BCM Platform → AI Tools → Digital Twin
- **Real-time monitoring**: WebSocket connection for AI organs status

### Development Workflow

#### Starting the Integrated Platform
```bash
cd /Users/MD/ISO-22301

# Start Odoo BCM Platform
cd core && docker-compose up -d

# Start Digital Twin Service
cd services/digital-twin-platform && npm run simple
```

#### Testing Integration
```bash
# Test Odoo connection
curl http://localhost:8069/web/health

# Test Digital Twin service
curl http://localhost:3000/health

# Test integration bridge
curl http://localhost:3000/api/odoo/health
```

### Deployment Notes

1. **Dependencies**: Requires Odoo 18 with BCM modules installed
2. **Network**: Services communicate via localhost (development) or Docker network (production)
3. **Data Flow**: Web UI → Node.js API → Odoo RPC → PostgreSQL
4. **Monitoring**: Integrated logs in `/services/digital-twin-platform/logs/`

### Support & Documentation

- **BCM Platform**: `/Users/MD/ISO-22301/README.md`
- **Technical Spec**: `/Users/MD/ISO-22301/services/docs/TECHNICAL_SPECIFICATION.md`
- **GitHub**: https://github.com/SEH-foundation/ISO-22301

---
*Integrated on September 16, 2025*
*Part of the ISO-22301 BCM Platform Ecosystem*