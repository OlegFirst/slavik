# Scenario Intelligence - Quick Reference

## 🚀 Quick Start

### Generate All Scenarios

\`\`\`bash
cd /intelligent-core/scenario-intelligence

# Via Generation Manager
python3 managers/generation_manager.py

# Via REST API
cd /infrastructure/AI-office-infrastructure/scenario-orchestrator
PORT=8060 python3 main.py &
curl -X POST http://localhost:8060/api/v1/generate/start
\`\`\`

### Generate Specific Level

\`\`\`bash
# L1 Platform (46 services)
python3 generators/l1_platform_generator.py

# L1 Applications (16 apps)
python3 generators/l1_application_generator.py

# L2 Subsystems (12 subsystems)
python3 generators/l2_subsystem_generator.py

# L3 Systems (19 systems)
python3 generators/l3_system_generator.py
\`\`\`

## 📁 File Structure

\`\`\`
scenario-intelligence/
├── templates/                          # 16 templates
│   ├── golden_standard_l1.yaml
│   ├── golden_standard_l1_application.yaml
│   ├── golden_standard_l2.yaml
│   ├── golden_standard_l3.yaml
│   ├── golden_standard_l4.yaml
│   └── l3-specialized/                # 11 files
│
├── generators/                         # 5 generators
│   ├── __init__.py
│   ├── base_generator.py
│   ├── platform_services_catalog.py
│   ├── l1_platform_generator.py
│   ├── l1_application_generator.py
│   ├── l2_subsystem_generator.py
│   └── l3_system_generator.py
│
├── managers/
│   ├── __init__.py
│   └── generation_manager.py
│
├── storage/
│   ├── __init__.py
│   └── registry.py
│
├── generated/                          # 93 scenarios
│   ├── l1/
│   │   ├── services/                  # 46 files
│   │   └── applications/              # 16 files
│   ├── l2/                             # 12 files
│   └── l3/                             # 19 files
│
├── template_loader.py
├── ARCHITECTURE_FINAL.md
├── GENERATORS_COMPLETE.md
├── SESSION_2025_10_13_SUMMARY.md
└── QUICK_REFERENCE.md (this file)
\`\`\`

## 📊 Statistics

- **Templates:** 16 (5 base + 11 specialized)
- **Generators:** 4 working + 1 TODO
- **Scenarios:** 93 generated (100% success)
- **Generation time:** 0.7s total
- **Speed:** 133 scenarios/sec

## 🎯 Component Overview

### Generators

| Generator | Count | Template | Status |
|-----------|-------|----------|--------|
| L1 Platform | 46 | golden_standard_l1.yaml | ✅ |
| L1 Applications | 16 | golden_standard_l1_application.yaml | ✅ |
| L2 Subsystems | 12 | golden_standard_l2.yaml | ✅ |
| L3 Systems | 19 | 11 specialized templates | ✅ |
| L4 Workflows | TBD | golden_standard_l4.yaml | 🔄 |

### Templates

**Base (5):**
1. golden_standard_l1.yaml (400 lines)
2. golden_standard_l1_application.yaml (820 lines)
3. golden_standard_l2.yaml (600 lines)
4. golden_standard_l3.yaml (750 lines)
5. golden_standard_l4.yaml (900 lines)

**Specialized L3 (11):**
1. l3_infrastructure_system.yaml
2. l3_security_system.yaml
3. l3_reliability_system.yaml
4. l3_ai_system.yaml
5. l3_operations_system.yaml
6. l3_intelligence_system.yaml
7. l3_business_system.yaml
8. l3_orchestration_system.yaml
9. l3_quality_system.yaml
10. l3_frontend_system.yaml
11. l3_infrastructure_management_system.yaml

## 🔧 Python API

### Basic Usage

\`\`\`python
import asyncio
from managers.generation_manager import GenerationManager

async def main():
    manager = GenerationManager()
    report = await manager.generate_all(
        levels=["l1_platform", "l1_applications", "l2", "l3"]
    )
    print(f"Generated: {report['total_scenarios_generated']}")

asyncio.run(main())
\`\`\`

### Individual Generator

\`\`\`python
from template_loader import TemplateLoader
from storage.registry import ScenarioRegistry
from generators.l1_platform_generator import L1PlatformGenerator

loader = TemplateLoader()
registry = ScenarioRegistry()
generator = L1PlatformGenerator(loader, registry)

scenario_ids = await generator.generate_all()
stats = generator.get_statistics()
print(f"Generated: {stats['generated']}/{stats['total']}")
\`\`\`

## 🌐 REST API

### Endpoints

\`\`\`http
# Generation Control
POST /api/v1/generate/start
POST /api/v1/generate/stop
GET  /api/v1/generate/status
GET  /api/v1/generate/progress/:id

# Level-Specific
POST /api/v1/generate/l1/platform
POST /api/v1/generate/l1/applications
POST /api/v1/generate/l2
POST /api/v1/generate/l3
POST /api/v1/generate/l4

# Monitoring
GET  /health
GET  /metrics
GET  /api/v1/statistics
\`\`\`

### Example Requests

\`\`\`bash
# Start generation
curl -X POST http://localhost:8060/api/v1/generate/start \\
  -H "Content-Type: application/json" \\
  -d '{"levels": ["l1_platform", "l1_applications", "l2", "l3"]}'

# Check status
curl http://localhost:8060/api/v1/generate/status

# Get statistics
curl http://localhost:8060/api/v1/statistics
\`\`\`

## 📝 Scenario Format

Each generated scenario:

\`\`\`yaml
meta:
  id: l1-service-mio-manager
  level: 1
  type: service
  generated_at: 2025-10-13T...

component_info:
  name: mio-manager
  port: 8025
  criticality: critical

dependencies:
  internal: [service-discovery, eventbus]
  external: [postgresql, redis]

test_scenarios:
  - name: Service Startup & Health Check
  - name: Dependency Availability Check
  - name: Load & Stress Testing
  # ... 3-5 more scenarios
\`\`\`

## 🔗 Documentation

- **[ARCHITECTURE_FINAL.md](./ARCHITECTURE_FINAL.md)** - Complete architecture
- **[GENERATORS_COMPLETE.md](./GENERATORS_COMPLETE.md)** - Implementation guide
- **[SESSION_2025_10_13_SUMMARY.md](./SESSION_2025_10_13_SUMMARY.md)** - Latest session
- **[RAG_KNOWLEDGE_INTEGRATION.md](./RAG_KNOWLEDGE_INTEGRATION.md)** - RAG integration
- **[Scenario Orchestrator README](/infrastructure/AI-office-infrastructure/scenario-orchestrator/README.md)** - REST API docs

## 🎯 Next Steps

1. **L4 Workflow Generator** (AI-powered)
2. **PostgreSQL Integration**
3. **Qdrant Integration**
4. **EventBus Integration**
5. **MIO Manager Integration**

## ⚡ Performance Tips

1. Use GenerationManager for bulk generation
2. Cache template loader instance
3. Reuse registry instance
4. Generate levels in parallel (future)
5. Use REST API for remote generation

## 🐛 Troubleshooting

### Import Errors

\`\`\`bash
# Ensure you're in the right directory
cd /intelligent-core/scenario-intelligence

# Run from module directory
python3 -m generators.l1_platform_generator
\`\`\`

### Template Not Found

\`\`\`bash
# Check templates directory exists
ls templates/

# Verify template loader path
python3 -c "from template_loader import TemplateLoader; print(TemplateLoader().templates_dir)"
\`\`\`

### Generation Failures

\`\`\`bash
# Check logs
python3 managers/generation_manager.py 2>&1 | grep ERROR

# Run individual generator
python3 generators/l1_platform_generator.py

# Check registry
python3 -c "from storage.registry import ScenarioRegistry; r = ScenarioRegistry(); print(len(r.scenarios))"
\`\`\`

## 📞 Support

For issues or questions:
1. Check documentation in this directory
2. Review [ARCHITECTURE_FINAL.md](./ARCHITECTURE_FINAL.md)
3. See [GENERATORS_COMPLETE.md](./GENERATORS_COMPLETE.md) for detailed implementation

---

**Status:** ✅ Production Ready (L1, L2, L3)
**Last Updated:** 2025-10-13
**Version:** 1.0.0
