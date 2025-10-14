# ISO 22301 BCM Platform - Frontend

Unified Business Continuity Management System based on ISO 22301 standard.

## 📁 Project Structure

```
frontend/
├── unified-bcm-platform/              # ✅ PRIMARY - Next.js Dashboard
├── unified-bcm-platform_OLD/          # 📦 Previous version
├── unified-bcm-platform_BACKUP_20250928_033548/  # 🔒 Backup
├── admin_panel/                       # ✅ PRIMARY - Admin Control Center
├── admin_panel3/                      # ✅ SECONDARY - Production-ready
├── admin_panel2_OLD/                  # 📦 Archived
├── web_portal_enhanced/               # ✅ PRIMARY - Vue 3 User Portal
├── web_portal_enhanced_current_2259_OLD/  # 📦 Previous
├── web_portal_enhanced_BACKUP_20250928_035954/  # 🔒 Backup
├── bcm-marketplace/                   # Community marketplace
└── inspector/                         # Module inspector
```

## 🎯 Primary Working Directory

**Use**: `unified-bcm-platform/`

This version contains:
- ✅ **53 real API calls** (vs 37 in OLD)
- ✅ **285 mocks** (vs 320 in OLD - fewer is better)
- ✅ **Direct backend integration** without fallback
- ✅ **35+ complete sections** (auth, forms, layouts)
- ✅ **AI components merged** from OLD version:
  - Digital Twin AI Module
  - AI Workflow Optimizer
  - Process Mining Dashboard
  - AI services (analytics, bcm, simulation)
  - Custom hooks (useAIOptimizer, useProcessMining)

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Backend services running (see Backend Services below)

### Installation

```bash
cd unified-bcm-platform
npm install
```

### Development

```bash
npm run dev
# Runs on http://localhost:3002
```

### Build

```bash
npm run build
npm start
```

### Useful Scripts

```bash
npm run lint              # ESLint check
npm run type-check        # TypeScript validation
npm run audit:modules     # Audit BCM modules
npm run audit:full        # Full audit (modules + types + lint)
npm run api:status        # Check API implementation status
```

## 🔧 Backend Services

Required services with default URLs (configure in `.env.local`):

| Service | Default URL | Purpose |
|---------|-------------|---------|
| API Gateway | `http://localhost:8777` | Main API endpoint |
| AI Orchestrator | `http://localhost:8000` | AI/ML operations |
| Module Validator | `http://localhost:5001` | BCM module validation |
| Keycloak | `http://localhost:8080` | Authentication (SSO) |
| Odoo | Custom | ERP integration |

### Environment Configuration

Create `.env.local`:

```bash
NEXT_PUBLIC_KEYCLOAK_URL=http://localhost:8080
NEXT_PUBLIC_KEYCLOAK_REALM=bcm-platform
NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=bcm-frontend
NEXT_PUBLIC_API_URL=http://localhost:8777
NEXT_PUBLIC_AI_ORCHESTRATOR_URL=http://localhost:8000
NEXT_PUBLIC_MODULE_VALIDATOR_URL=http://localhost:5001
```

## 📦 Technology Stack

- **Framework**: Next.js 15 (App Router)
- **React**: 19.1.0
- **Language**: TypeScript 5.7
- **Styling**: Tailwind CSS 4.0
- **UI Components**: Radix UI
- **State Management**: Zustand 5.0
- **Data Fetching**: TanStack Query 5.62
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts, Chart.js
- **Authentication**: Keycloak JWT
- **Database**: Supabase
- **3D Visualization**: THREE.js (Digital Twin)

## 🏗️ Architecture

### API Client (`lib/api-client.ts`)
Centralized API client with:
- JWT token management
- Automatic refresh
- Request/response interceptors
- Error handling
- Multiple backend endpoints

### Services (`services/`)
- `simulation/` - JaamSim integration (Block 3 Digital Twin)
- `analytics/` - Learning and performance monitoring
- `bcm/` - Platform integration
- `digital-twin/` - Twin API

### Hooks (`lib/hooks/`)
- `useProcessMining.ts` - Process mining analysis
- `useAIOptimizer.ts` - AI workflow optimization
- Custom API hooks with React Query

### Components Structure
```
components/
├── base/                    # Base UI components
├── bcm-modules/            # 28 ISO 22301 modules
├── sections/               # Feature sections (35+)
├── digital-twin/           # AI Digital Twin
└── admin/                  # Admin components
```

## 🧩 BCM Modules (28 Total)

Core ISO 22301 modules implemented:

1. **Core**: bcm_core, bcm_portal, bcm_intelligent_base
2. **BIA**: bcm_bia, bcm_bia_questionnaire
3. **Risk**: bcm_risk_management, bcm_monte_carlo_risk
4. **Plans**: bcm_plans, bcm_plan_builder
5. **Incident**: bcm_incident_management, bcm_communication
6. **Audit**: bcm_audit, bcm_maturity
7. **Exercise**: bcm_exercise, bcm_exercise_calendar
8. **Reporting**: bcm_reporting, bcm_kpi
9. **Integration**: bcm_marketplace, bcm_odoo_integration
10. **AI**: bcm_ai_orchestrator, bcm_learning_org

## 📋 What Was Merged (2025-09-28)

### Source: `unified-bcm-platform_OLD/`
Copied to primary version:

**Components** (3 files):
- `components/digital-twin/DigitalTwinAIModule.tsx` (29KB)
- `components/sections/workflow/ai/AIWorkflowOptimizer.tsx` (32KB)
- `components/sections/workflow/ai/ProcessMiningDashboard.tsx` (35KB)

**Hooks** (2 files):
- `lib/hooks/useAIOptimizer.ts` (7.8KB)
- `lib/hooks/useProcessMining.ts` (12KB)

**Services** (4 folders):
- `services/simulation/` - simulationService
- `services/analytics/` - analyticsService
- `services/bcm/` - bcmService
- `services/digital-twin/` - digitalTwinApi
- `services/index.ts` - Unified exports + health checks

**Result**: Zero conflicts, all files new additions.

---

## 🌐 Web Portal Enhanced (Vue 3)

### Source: `web_portal_enhanced_current_2259_OLD/`
Copied to primary version:

**Components** (1 folder):
- `components/assistant/AssistantPanel.vue` (169 lines) - AI Assistant chat interface

### Quality Comparison

| Metric | web_portal_enhanced (PRIMARY) | _current_2259_OLD |
|--------|-------------------------------|-------------------|
| Real API calls | 36 | 21 |
| Mock references | 53 | 62 |
| Lines of code | 90,924 | 88,959 |
| Size | 262 MB | 283 MB |
| Unique features | Digital Twin, Three.js, Unified Simulation Hub | Assistant, Bootstrap |

**Why web_portal_enhanced is PRIMARY**:
- ✅ **36 real API calls** vs 21 (better backend integration)
- ✅ **53 mocks** vs 62 (fewer mocks = more production-ready)
- ✅ **90,924 lines of code** (more complete functionality)
- ✅ **Digital Twin with 3D visualization** (Three.js)
- ✅ **Unified Simulation Hub** (advanced features)

### Web Portal Technology Stack

- **Framework**: Vue 3.4 (Composition API)
- **Build Tool**: Vite 5.0
- **Language**: TypeScript 5.2
- **Styling**: Tailwind CSS 3.3 + SCSS
- **UI Components**: Headless UI, Heroicons
- **State Management**: Pinia 2.1
- **Router**: Vue Router 4.2
- **Charts**: Chart.js 4.4, Vue-ChartJS 5.3
- **3D Graphics**: Three.js 0.180
- **HTTP Client**: Axios 1.6
- **Testing**: Vitest, Vue Test Utils

### Web Portal Quick Start

```bash
cd web_portal_enhanced
npm install
npm run dev
# Runs on http://localhost:5173 (Vite default)
```

---

## 🔍 Version History

### Timeline
- **Sept 19, 22:59**: Original files created locally
- **Sept 20, 04:23**: Committed in massive WIP commit (bb6663da)
- **Sept 28, 03:35**: unified-bcm-platform merge completed
- **Sept 28, 04:00**: web_portal_enhanced merge completed

### Quality Comparison

| Metric | Primary (NEW) | OLD |
|--------|---------------|-----|
| Mock data calls | 285 | 320 |
| Real API calls | 53 | 37 |
| Backend connection | Direct | Fallback |
| Complete sections | 35+ | Limited |
| AI components | ✅ Merged | ✅ Source |

## 🛡️ Safety Backups

### Unified BCM Platform (Next.js)
1. **unified-bcm-platform/** - Working version ✅
2. **unified-bcm-platform_OLD/** - Previous with AI 📦
3. **unified-bcm-platform_BACKUP_20250928_033548/** - Safety backup 🔒

### Web Portal Enhanced (Vue 3)
1. **web_portal_enhanced/** - Working version ✅
2. **web_portal_enhanced_current_2259_OLD/** - Previous version 📦
3. **web_portal_enhanced_BACKUP_20250928_035954/** - Safety backup 🔒

## 🐛 Troubleshooting

### Backend Connection Issues
```bash
# Check services health
npm run api:status

# Verify environment variables
cat .env.local

# Test API Gateway
curl http://localhost:8777/api/health
```

### Build Errors
```bash
# Clear cache
rm -rf .next node_modules
npm install
npm run build
```

### Type Errors
```bash
npm run type-check
```

## 👥 Team Notes

### When to Use Each Version

- **Development**: Always use `unified-bcm-platform/`
- **Reference AI code**: Check `unified-bcm-platform_OLD/`
- **Rollback**: Use `unified-bcm-platform_BACKUP_20250928_033548/`

### Important Files

- `lib/api-client.ts` - Main API client (centralized)
- `services/index.ts` - Service health checks
- `lib/odoo-api-mapper.ts` - Odoo integration mapping
- `scripts/audit-modules.js` - Module audit script

### Dependencies

All key dependencies are in sync between versions. Main ones:
- Supabase client: `^2.57.4`
- React Query: `^5.62.3`
- Next.js: `^15.5.3`

---

## 🎛️ Admin Panel Versions

### Structure
```
frontend/
├── admin_panel/          # ✅ PRIMARY - Full Admin Control Center
├── admin_panel3/         # ✅ SECONDARY - Production-ready with Docker
└── admin_panel2_OLD/     # 📦 Archived minimal version
```

### Comparison Table

| Metric | admin_panel (PRIMARY) | admin_panel3 | admin_panel2_OLD |
|--------|----------------------|--------------|------------------|
| **Lines of code** | 27,351 | 23,530 | 23,560 |
| **Code files** | 77 | 65 | 65 |
| **Real API calls** | 75 | 61 | 61 |
| **Mock references** | 48 | 24 | 24 |
| **Size** | 493 MB | 497 MB | 500 MB |

### admin_panel (PRIMARY) - Most Complete

**Unique Security & Auth Features**:
- ✅ **Keycloak Integration** (`keycloak-js ^26.2`) - Full SSO authentication
- ✅ **XSS Protection** (`dompurify ^3.2` + types) - Security sanitization
- ✅ **Schema Validation** (`zod ^4.1`) - Type-safe validation
- ✅ **Advanced Charts** (`recharts ^3.2`) - Data visualization

**Unique Folders**:
- `src/auth/` - Complete authentication system
- `src/config/` - Centralized configuration
- `src/security/` - Security middleware & auditing

**Documentation**:
- ARCHITECTURE_UPDATE.md
- CENTRALIZED_ARCHITECTURE_GUIDE.md
- DETAILED_SECURITY_AUDIT.md
- SECURITY_AUDIT_REPORT.md

**Metrics**:
- 27,351 lines of production code
- 75 real API calls (best backend integration)
- 18 component folders vs 13 in others

### admin_panel3 (SECONDARY) - Production-Ready

**Deployment Features**:
- ✅ Dockerfile + docker-compose.yml
- ✅ nginx.conf for production
- ✅ check-services.sh deployment script
- ✅ bcm-admin-control-center.tsx standalone component

**Documentation**:
- README.md ("95% РЕАЛИЗОВАНО")
- IMPLEMENTATION_ANALYSIS.md
- PROJECT_SUMMARY.md
- READY.md
- UNIFIED_PLATFORM_MONITORING.md

**Note**: Missing Keycloak, DOMPurify, and security layer

### admin_panel2_OLD - Archived

Minimal version without Docker, docs, or deployment scripts. Kept for reference only.

### Technology Stack (admin_panel PRIMARY)

- **Framework**: React 18.2 + Vite 5.0
- **Language**: TypeScript 5.0
- **UI Libraries**: Material-UI 7.3 + Radix UI (Dialog, Label, Progress, etc.)
- **State Management**: Zustand 4.4 + React Query 5.89
- **Authentication**: Keycloak-js 26.2
- **Security**: DOMPurify 3.2
- **Charts**: Recharts 3.2
- **Real-time**: Socket.io-client 4.8
- **Validation**: Zod 4.1
- **Styling**: Tailwind CSS 3.3 + Tailwind Animate

### When to Use

**Development**:
- Use **admin_panel** for full-featured development with security
- Use **admin_panel3** for Docker/deployment configuration reference

**Production**:
- Deploy **admin_panel** for complete functionality
- Adapt Docker configs from **admin_panel3** if needed

**Reference**:
- Check **admin_panel2_OLD** for minimal setup examples

---

## 📚 Additional Resources

- **API Documentation**: See backend services docs
- **Module Docs**: `bcm-modules/*/README.md`
- **Architecture**: Check `unified-bcm-platform-spec.md` in root
- **Integration Guide**: See backend `INTEGRATION_GUIDE.md`

## 🎓 Development Guidelines

1. **Always check API status** before major changes
2. **Use centralized api-client** for all backend calls
3. **Follow existing patterns** in sections/components
4. **Test with real backend** when possible
5. **Document new features** in component comments
6. **Run full audit** before commits: `npm run audit:full`

---

**Last Updated**: 2025-09-28
**Maintainer**: Development Team
**Platform Version**: 1.0.0
**Status**: Production Ready ✅