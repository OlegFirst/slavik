# Infrastructure Tools - Quick Reference

> **Last Updated**: 2025-10-08
> **Full Catalog**: See `TOOLS_COMPREHENSIVE_CATALOG.md`

## Quick Commands

### Analysis & Discovery
```bash
# Scan all modules
python3 infrastructure/tools/analyzers/module_scanner.py --section intelligent-core

# Discover all APIs
python3 infrastructure/tools/analyzers/api_mapper.py

# Map business logic
python3 infrastructure/tools/analyzers/business_logic_mapper.py

# Analyze dependencies
python3 infrastructure/tools/analyzers/dependency_mapper.py

# Discover services
python3 infrastructure/tools/analyzers/discover_services.py

# Find all metrics
python3 infrastructure/tools/analyzers/metrics_discovery.py
```

### Validation & Reconciliation
```bash
# Validate SERVICE_CATALOG
python3 infrastructure/tools/analyzers/dependency_validator.py

# Auto-fix documentation
python3 infrastructure/tools/analyzers/dependency_reconciler.py
```

### Documentation Generation
```bash
# Generate all docs
python3 infrastructure/tools/doc-generators/documentation_generator.py --all

# AI-powered docs (requires ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY="your-key"
python3 infrastructure/tools/doc-generators/ai_documentation_generator.py --full --ai

# Generate event catalog
python3 infrastructure/tools/doc-generators/event_catalog_generator.py

# Generate API docs (requires running services)
python3 infrastructure/tools/doc-generators/api_docs_generator.py

# Generate tests
python3 infrastructure/tools/doc-generators/test_generator.py
```

### Infrastructure Generation
```bash
# Generate docker-compose
python3 infrastructure/tools/analyzers/generate_improved_compose.py

# Generate Prometheus config
python3 infrastructure/tools/doc-generators/prometheus_config_generator.py
```

### Visualization
```bash
# Create interactive dashboards
python3 infrastructure/tools/dashboards/module_dashboard.py
```

---

## Tool Categories & Priorities

### CRITICAL Priority (Must-Run Regularly)
1. **business_logic_mapper.py** - Runtime behavior patterns
2. **dependency_validator.py** - Documentation compliance
3. **service_discovery.py** - Service inventory
4. **module_scanner.py** - Module analysis
5. **event_catalog_generator.py** - Event tracking
6. **prometheus_config_generator.py** - Monitoring setup

### HIGH Priority (Weekly/Monthly)
1. **api_mapper.py** - API discovery
2. **dependency_mapper.py** - Dependency analysis
3. **dependency_reconciler.py** - Auto-fix docs
4. **metrics_discovery.py** - Metrics coverage
5. **generate_improved_compose.py** - Docker configs
6. **ai_documentation_generator.py** - Quality docs

### MEDIUM Priority (As Needed)
1. **ast_analyzer.py** - Code metrics
2. **documentation_generator.py** - Basic docs
3. **test_generator.py** - Test scaffolding
4. **api_docs_generator.py** - OpenAPI docs
5. **module_dashboard.py** - Visualizations

### LOW Priority (Optional)
1. **ui_blueprint_gen.py** - UI planning

---

## Integration Checklist

### CI/CD Pipeline
- [ ] Add dependency_validator to pre-deployment
- [ ] Run module_scanner on PR
- [ ] Generate prometheus config before monitoring updates
- [ ] Update event catalog weekly

### AI Event Manager Integration
- [ ] Import business_logic_mapper patterns
- [ ] Connect api_mapper for endpoint tracking
- [ ] Use docker_manager for container operations
- [ ] Feed event_catalog to event router

### Monitoring Integration
- [ ] Automate prometheus_config_generator
- [ ] Run metrics_discovery before config updates
- [ ] Use service_discovery for target discovery

### Documentation System
- [ ] Schedule module_scanner weekly
- [ ] Enable ai_documentation_generator for critical modules
- [ ] Run event_catalog_generator on events changes
- [ ] Generate module_dashboard monthly

---

## Output Locations

### Reports (usually in `tools/reports/`)
- `api_map.json` / `api_map.md` - API inventory
- `ast_analysis.json` / `ast_analysis.md` - AST analysis
- `business_logic.json` / `business_logic.md` - Business patterns
- `dependencies.json` / `dependencies.md` - Dependency graph
- `dependency_graph.png` - Visual dependency graph
- `{module}_scan.json` / `{module}_scan.md` - Module scans
- `dashboard.html` - Interactive dashboard
- `endpoint_map.html` - API endpoint visualization
- `dependency_network.html` - Dependency network graph

### Infrastructure Configs
- `docker-compose.auto.yml` - Generated compose file
- `prometheus-auto.yml` - Prometheus configuration
- `sd_configs/services.json` - Service discovery config
- `gateway-routes.auto.json` - API Gateway routes

### Documentation
- Module `README.md` files - Auto-generated documentation
- Module `API.md` files - API documentation
- Layer `ARCHITECTURE.md` files - Architecture overviews
- `EVENTS.md` - Event catalog
- `EVENT_FLOW.md` - Event flow diagrams

### Tests (in `tests/generated/`)
- `test_{service}_api.py` - API tests
- `test_{service}_unit.py` - Unit tests
- `tavern_test_{service}.yaml` - Tavern scenarios

---

## Common Issues

### Missing Dependencies
```bash
pip install anthropic plotly networkx matplotlib pyyaml jinja2 httpx docker
```

### Docker Connection Failed
```bash
# Check Docker
docker ps

# Verify docker-compose
docker-compose -f docker-compose.yml config
```

### Config Not Found
```bash
# Create config directory
mkdir -p infrastructure/tools/config
```

### API Key Not Set (for AI tools)
```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
```

---

## Tool Capabilities Matrix

| Tool | Analysis | Generation | Validation | AI-Powered |
|------|----------|------------|------------|------------|
| api_mapper | ✓ | | | |
| ast_analyzer | ✓ | | | |
| business_logic_mapper | ✓ | | | |
| dependency_mapper | ✓ | ✓ | | |
| dependency_validator | | | ✓ | |
| dependency_reconciler | ✓ | ✓ | ✓ | |
| service_discovery | ✓ | ✓ | | |
| metrics_discovery | ✓ | ✓ | | |
| module_scanner | ✓ | | | |
| generate_improved_compose | | ✓ | | |
| documentation_generator | | ✓ | | |
| event_catalog_generator | ✓ | ✓ | | |
| test_generator | | ✓ | | |
| ui_blueprint_gen | | ✓ | | |
| prometheus_config_generator | | ✓ | | |
| api_docs_generator | ✓ | ✓ | | |
| ai_documentation_generator | | ✓ | | ✓ |
| module_dashboard | ✓ | ✓ | | |
| docker_manager | | | | |

---

## Recommended Workflows

### 1. New Module Setup
```bash
# 1. Scan module
python3 tools/analyzers/module_scanner.py --module new-module

# 2. Generate documentation
python3 tools/doc-generators/ai_documentation_generator.py --module new-module --ai

# 3. Generate tests
python3 tools/doc-generators/test_generator.py

# 4. Update service catalog
python3 tools/analyzers/dependency_reconciler.py
```

### 2. Pre-Deployment Validation
```bash
# 1. Validate documentation
python3 tools/analyzers/dependency_validator.py

# 2. Update service discovery
python3 tools/analyzers/discover_services.py

# 3. Generate docker-compose
python3 tools/analyzers/generate_improved_compose.py

# 4. Update Prometheus
python3 tools/doc-generators/prometheus_config_generator.py
```

### 3. Weekly Maintenance
```bash
# 1. Scan all modules
python3 tools/analyzers/module_scanner.py --section intelligent-core

# 2. Update event catalog
python3 tools/doc-generators/event_catalog_generator.py

# 3. Analyze dependencies
python3 tools/analyzers/dependency_mapper.py

# 4. Validate and reconcile
python3 tools/analyzers/dependency_validator.py
python3 tools/analyzers/dependency_reconciler.py
```

### 4. Monthly Reports
```bash
# 1. Generate dashboard
python3 tools/dashboards/module_dashboard.py

# 2. Full API discovery
python3 tools/analyzers/api_mapper.py

# 3. Business logic analysis
python3 tools/analyzers/business_logic_mapper.py

# 4. Update all documentation
python3 tools/doc-generators/documentation_generator.py --all
```

---

## Docker Manager Usage (Python API)

```python
from infrastructure.tools.docker_management.docker_manager import DockerManager

# Initialize
docker_mgr = DockerManager()

# Start service
await docker_mgr.start_service("community-intelligence")

# Check status
status = await docker_mgr.get_container_status("community-intelligence")
if status.is_healthy():
    print("Service is running and healthy")

# Get logs
logs = await docker_mgr.get_container_logs("community-intelligence", tail=100)

# Restart service
await docker_mgr.restart_service("community-intelligence")

# Scale service
await docker_mgr.scale_service("community-intelligence", replicas=3)
```

---

## Next Steps

1. **Review full catalog**: `/infrastructure/tools/TOOLS_COMPREHENSIVE_CATALOG.md`
2. **Set up CI/CD integration**: Add tools to pipeline
3. **Enable AI documentation**: Set ANTHROPIC_API_KEY
4. **Schedule automated runs**: Weekly scans and updates
5. **Integrate with monitoring**: Connect to AI Event Manager

---

**For detailed information, see**: `TOOLS_COMPREHENSIVE_CATALOG.md`
