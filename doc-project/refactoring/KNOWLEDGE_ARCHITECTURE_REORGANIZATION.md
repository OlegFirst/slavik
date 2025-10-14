# Knowledge Architecture Reorganization Plan

**Date:** 2025-10-14
**Purpose:** Организовать правильную архитектуру для каталогов и систем знаний
**Status:** Plan & Execution Guide

---

## 🎯 Проблема

**Текущая ситуация:**
- Каталоги лежат в корне `/catalogs` (временно, для удобства разработки)
- Сценарии в `/data/knowledge/scenarios`
- Стандарты в `/data/knowledge/standards`
- Нет единой системы управления знаниями
- Дублирование и неоптимальная навигация

**Целевое состояние:**
- Единая интегрированная система знаний
- Логическая структура: стандарты → сценарии → каталоги → кейсы
- Доступ через AI Foundation (learning-knowledge)
- Версионирование и управление контентом

---

## 📚 Предлагаемая Архитектура

### Вариант A: Централизованная Knowledge System (РЕКОМЕНДУЕТСЯ)

```
/intelligent-core/ai-foundation/learning-knowledge/
├── README.md (Master index для всей системы знаний)
├── knowledge/
│   ├── standards/          # ISO, WHO, и другие стандарты
│   │   ├── iso/
│   │   │   ├── iso-22301/
│   │   │   │   ├── ISO_22301_FLOWS_INDEX.md
│   │   │   │   ├── ISO_22301_BUSINESS_FLOWS.md
│   │   │   │   ├── ISO_22301_BUSINESS_FLOWS_PART2.md
│   │   │   │   ├── clauses_breakdown.md
│   │   │   │   └── metadata.json
│   │   │   └── iso-27001/ (будущее)
│   │   ├── who/
│   │   │   ├── WHO_HEALTHCARE_BCM_FLOWS.md
│   │   │   ├── health_emergency_bcm.md
│   │   │   └── metadata.json
│   │   └── README.md (Index стандартов)
│   │
│   ├── scenarios/          # Тестовые и training сценарии
│   │   ├── governance/     # Phase 1.1 verification scenarios
│   │   │   ├── README.md
│   │   │   ├── iso-22301/
│   │   │   │   ├── incident_response.md
│   │   │   │   ├── risk_assessment.md
│   │   │   │   └── audit_execution.md
│   │   │   ├── who-healthcare/
│   │   │   │   ├── pandemic_staff_shortage.md
│   │   │   │   ├── supply_chain_disruption.md
│   │   │   │   └── infrastructure_failure.md
│   │   │   └── case-library-links/
│   │   │       ├── staff_shortage_cases.md
│   │   │       └── supply_disruption_cases.md
│   │   ├── business-processes/ (будущее)
│   │   └── README.md (Master scenario index)
│   │
│   ├── catalogs/           # Service catalogs, event catalogs
│   │   ├── services/
│   │   │   ├── SERVICE_CATALOG_DETAILED.yaml
│   │   │   ├── platform-services/
│   │   │   ├── intelligent-core/
│   │   │   └── infrastructure/
│   │   ├── events/
│   │   │   ├── EVENT_CATALOG.yaml
│   │   │   └── event_types/
│   │   ├── scenarios/
│   │   │   └── SCENARIO_GENERATION_SYSTEM_DESIGN.md
│   │   └── README.md (Catalog index)
│   │
│   ├── business_flows/     # Business process flows
│   │   ├── bcm/
│   │   │   ├── bia_flows.md
│   │   │   ├── risk_flows.md
│   │   │   └── response_flows.md
│   │   ├── healthcare/
│   │   │   └── WHO_HEALTHCARE_BCM_FLOWS.md (symlink)
│   │   └── README.md
│   │
│   ├── cases/              # Anonymized case library (metadata)
│   │   ├── README.md
│   │   ├── problem_types.json
│   │   └── case_statistics.json
│   │   # Note: Actual case data in database (community_intelligence schema)
│   │
│   └── templates/          # Reusable templates
│       ├── scenarios/
│       │   └── scenario_template.md
│       ├── policies/
│       │   └── policy_template.yaml
│       └── README.md
│
├── integrations/           # Knowledge integration adapters
│   ├── qdrant_adapter.py   # Vector DB for RAG
│   ├── case_library_adapter.py
│   ├── standards_loader.py
│   └── scenario_loader.py
│
└── api/                    # Knowledge API
    ├── knowledge_api.py
    ├── search.py
    └── recommendations.py
```

**Преимущества:**
- ✅ Единая точка входа для всех знаний
- ✅ Интеграция с AI Foundation (RAG, LLM routing)
- ✅ Версионирование через Git
- ✅ API для программного доступа
- ✅ Легко индексировать в Qdrant (vector DB)

---

### Вариант B: Распределённая система (альтернатива)

```
/data/knowledge/            # Статические знания (стандарты, reference)
├── standards/
├── business_flows/
└── README.md

/intelligent-core/ai-foundation/learning-knowledge/
├── knowledge/              # Динамические знания (scenarios, catalogs)
│   ├── scenarios/
│   ├── catalogs/
│   └── cases/
└── integrations/

/catalogs/                  # Legacy location (deprecated)
└── (to be moved)
```

**Минусы:**
- ⚠️ Знания разбросаны по нескольким местам
- ⚠️ Сложнее поддерживать консистентность
- ⚠️ Дублирование путей в коде

---

## 🚀 Рекомендуемое Решение: Вариант A

### Phase 1: Migration Plan

#### Step 1: Prepare Target Structure
```bash
# Create new structure in learning-knowledge
mkdir -p /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/learning-knowledge/knowledge/{standards,scenarios,catalogs,business_flows,cases,templates}
```

#### Step 2: Move Catalogs
```bash
# Move service catalogs
mv /Users/MD/AI-Platform-ISO/catalogs/* \
   /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/learning-knowledge/knowledge/catalogs/

# Keep symlink in root for backward compatibility
ln -s intelligent-core/ai-foundation/learning-knowledge/knowledge/catalogs \
      /Users/MD/AI-Platform-ISO/catalogs
```

#### Step 3: Consolidate Standards
```bash
# Standards already in data/knowledge/standards - create symlink or move
ln -s /Users/MD/AI-Platform-ISO/data/knowledge/standards \
      /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/learning-knowledge/knowledge/standards
```

#### Step 4: Move Scenarios
```bash
# Scenarios already created correctly
mv /Users/MD/AI-Platform-ISO/data/knowledge/scenarios \
   /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/learning-knowledge/knowledge/scenarios
```

#### Step 5: Update References
```python
# Update all code references from:
/catalogs/ → intelligent-core/ai-foundation/learning-knowledge/knowledge/catalogs/
/data/knowledge/standards → intelligent-core/ai-foundation/learning-knowledge/knowledge/standards/
/data/knowledge/scenarios → intelligent-core/ai-foundation/learning-knowledge/knowledge/scenarios/
```

---

## 📋 Implementation Checklist

### Phase 1: Restructure (1-2 hours)

- ✅ Create target directory structure
- ✅ Move catalogs to learning-knowledge/knowledge/catalogs
- ✅ Move scenarios to learning-knowledge/knowledge/scenarios
- ✅ Create symlinks for standards (or move)
- ✅ Create backward-compatibility symlinks
- ✅ Update README.md files

### Phase 2: Update Code References (2-3 hours)

- ⏳ Grep all Python files for `/catalogs/`
- ⏳ Update imports to new paths
- ⏳ Update configuration files
- ⏳ Update documentation links
- ⏳ Test all affected services

### Phase 3: Create Knowledge API (3-4 hours)

- ⏳ Create knowledge_api.py
- ⏳ Add standards loader
- ⏳ Add scenarios loader
- ⏳ Add catalog access API
- ⏳ Integrate with Qdrant (vector indexing)

### Phase 4: Integration with AI Services (2-3 hours)

- ⏳ Connect RAG pipeline to knowledge base
- ⏳ Add knowledge search to LLM router
- ⏳ Integrate with case library
- ⏳ Add knowledge recommendations

---

## 🔧 Detailed Migration Steps

### Step-by-Step Execution

#### 1. Create Master Knowledge Structure

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/learning-knowledge

# Create full structure
mkdir -p knowledge/{standards,scenarios,catalogs,business_flows,cases,templates}
mkdir -p knowledge/catalogs/{services,events,scenarios}
mkdir -p knowledge/scenarios/{governance,business-processes}
mkdir -p knowledge/standards/{iso,who}
mkdir -p knowledge/cases/{by_problem_type,statistics}
mkdir -p knowledge/templates/{scenarios,policies,workflows}

# Create integrations directory
mkdir -p integrations

# Create API directory
mkdir -p api
```

#### 2. Move Catalogs

```bash
# Move service catalog
cp -r /Users/MD/AI-Platform-ISO/catalogs/* \
      /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/learning-knowledge/knowledge/catalogs/

# Create backward-compatibility symlink
cd /Users/MD/AI-Platform-ISO
mv catalogs catalogs.old
ln -s intelligent-core/ai-foundation/learning-knowledge/knowledge/catalogs catalogs
```

#### 3. Move Scenarios

```bash
# Move scenarios (already created in correct place)
cp -r /Users/MD/AI-Platform-ISO/data/knowledge/scenarios/* \
      /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/learning-knowledge/knowledge/scenarios/
```

#### 4. Create Knowledge Index

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/learning-knowledge

# Create master README
cat > README.md << 'EOF'
# AI Platform Knowledge System

**Version:** 2.0.0
**Date:** 2025-10-14
**Purpose:** Centralized knowledge management for AI-Platform-ISO

## Overview

This is the central knowledge repository for the entire AI Platform, containing:

- **Standards**: ISO 22301, WHO BCM, and other compliance standards
- **Scenarios**: Test and training scenarios for all platform components
- **Catalogs**: Service, event, and scenario catalogs
- **Business Flows**: Process flows for BCM, healthcare, and other domains
- **Cases**: Metadata for anonymized case library (actual data in database)
- **Templates**: Reusable templates for scenarios, policies, workflows

## Structure

See `/knowledge/README.md` for detailed structure.

## Access

### Programmatic Access

```python
from intelligent_core.ai_foundation.learning_knowledge import KnowledgeAPI

kb = KnowledgeAPI()

# Search standards
iso_flows = kb.standards.get_iso_22301_flows()

# Load scenario
scenario = kb.scenarios.get("governance/pandemic_staff_shortage")

# Query case library
cases = await kb.cases.find_by_problem_type("staff_shortage")
```

### Direct Access

All knowledge is also accessible as files in `/knowledge/` directory.

## Integration

- **RAG Pipeline**: Standards and flows indexed in Qdrant
- **LLM Router**: Knowledge-augmented prompt engineering
- **Case Library**: Community intelligence integration
- **Workflow Intelligence**: Process flows for PDCA cycles

---

**Maintained by:** AI Foundation Team
**Next Review:** 2026-01-14
EOF
```

#### 5. Update Service Catalog References

```python
# Create migration helper script
cat > /Users/MD/AI-Platform-ISO/infrastructure/tools/migrate_catalog_refs.py << 'PYTHON'
"""
Migrate catalog references to new knowledge system location
"""
import os
import re
from pathlib import Path

OLD_PATHS = [
    "/catalogs/",
    "catalogs/",
    "../catalogs/",
    "../../catalogs/",
]

NEW_PATH = "intelligent-core/ai-foundation/learning-knowledge/knowledge/catalogs/"

def update_file(file_path: Path):
    """Update catalog references in a file"""
    with open(file_path, 'r') as f:
        content = f.read()

    updated = content
    for old_path in OLD_PATHS:
        updated = updated.replace(old_path, NEW_PATH)

    if updated != content:
        with open(file_path, 'w') as f:
            f.write(updated)
        print(f"✅ Updated: {file_path}")
        return True
    return False

def scan_project():
    """Scan project for catalog references"""
    project_root = Path("/Users/MD/AI-Platform-ISO")

    # Scan Python files
    python_files = list(project_root.rglob("*.py"))
    yaml_files = list(project_root.rglob("*.yaml"))
    md_files = list(project_root.rglob("*.md"))

    all_files = python_files + yaml_files + md_files

    updated_count = 0
    for file_path in all_files:
        # Skip archived/backup files
        if '.old' in str(file_path) or '_archive' in str(file_path):
            continue

        if update_file(file_path):
            updated_count += 1

    print(f"\n📊 Summary: {updated_count} files updated")

if __name__ == "__main__":
    scan_project()
PYTHON

# Run migration (dry-run first)
# python /Users/MD/AI-Platform-ISO/infrastructure/tools/migrate_catalog_refs.py
```

---

## 🎯 Knowledge API Design

### Core API

```python
# File: intelligent-core/ai-foundation/learning-knowledge/api/knowledge_api.py

from typing import List, Dict, Any, Optional
from pathlib import Path
import yaml
import json

class KnowledgeAPI:
    """
    Central API for accessing all platform knowledge
    """

    def __init__(self):
        self.knowledge_root = Path(__file__).parent.parent / "knowledge"
        self.standards = StandardsAPI(self.knowledge_root / "standards")
        self.scenarios = ScenariosAPI(self.knowledge_root / "scenarios")
        self.catalogs = CatalogsAPI(self.knowledge_root / "catalogs")
        self.cases = CasesAPI(self.knowledge_root / "cases")

class StandardsAPI:
    """Access ISO, WHO, and other standards"""

    def __init__(self, root: Path):
        self.root = root

    def get_iso_22301_flows(self) -> List[Dict]:
        """Get all ISO 22301 flows"""
        index_path = self.root / "iso/iso-22301/ISO_22301_FLOWS_INDEX.md"
        # Parse and return flows
        pass

    def get_who_healthcare_flows(self) -> List[Dict]:
        """Get WHO healthcare BCM flows"""
        flows_path = self.root / "who/WHO_HEALTHCARE_BCM_FLOWS.md"
        pass

    def search(self, query: str) -> List[Dict]:
        """Search across all standards"""
        # Use Qdrant vector search
        pass

class ScenariosAPI:
    """Access test and training scenarios"""

    def __init__(self, root: Path):
        self.root = root

    def get(self, scenario_path: str) -> Dict:
        """Get specific scenario"""
        full_path = self.root / f"{scenario_path}.md"
        # Parse markdown and return structured data
        pass

    def list_by_category(self, category: str) -> List[str]:
        """List scenarios in category (governance, business-processes, etc.)"""
        pass

    def search(self, tags: List[str]) -> List[Dict]:
        """Search scenarios by tags"""
        pass

class CatalogsAPI:
    """Access service, event, and scenario catalogs"""

    def __init__(self, root: Path):
        self.root = root

    def get_services(self) -> Dict:
        """Get service catalog"""
        catalog_path = self.root / "services/SERVICE_CATALOG_DETAILED.yaml"
        with open(catalog_path) as f:
            return yaml.safe_load(f)

    def get_events(self) -> Dict:
        """Get event catalog"""
        catalog_path = self.root / "events/EVENT_CATALOG.yaml"
        with open(catalog_path) as f:
            return yaml.safe_load(f)

    def get_service_by_name(self, name: str) -> Optional[Dict]:
        """Get specific service details"""
        services = self.get_services()
        return services.get('services', {}).get(name)

class CasesAPI:
    """Access case library metadata"""

    def __init__(self, root: Path):
        self.root = root

    async def find_by_problem_type(self, problem_type: str) -> List[Dict]:
        """Find cases by problem type (queries database)"""
        # Delegate to CaseLibrary service
        from intelligent_core.collective.services.case_library import CaseLibrary
        # ...
        pass

    def get_problem_types(self) -> List[str]:
        """Get all available problem types"""
        stats_path = self.root / "problem_types.json"
        with open(stats_path) as f:
            return json.load(f)
```

---

## 📊 Benefits of Reorganization

### For Developers

- ✅ **Single source of truth** for all knowledge
- ✅ **Programmatic API** instead of file paths
- ✅ **Type safety** with API methods
- ✅ **Easy testing** with mock knowledge API

### For AI Services

- ✅ **RAG integration** - Standards indexed in Qdrant
- ✅ **LLM context** - Relevant knowledge injected into prompts
- ✅ **Recommendations** - AI can suggest relevant scenarios/cases
- ✅ **Learning** - Platform learns from case library patterns

### For Users

- ✅ **Discoverability** - Easy to find relevant knowledge
- ✅ **Consistency** - All knowledge follows same structure
- ✅ **Traceability** - Standards → Scenarios → Cases linked
- ✅ **Reusability** - Templates for common needs

---

## 🚦 Migration Safety

### Backward Compatibility

```bash
# Keep old paths working via symlinks
/catalogs → intelligent-core/ai-foundation/learning-knowledge/knowledge/catalogs
/data/knowledge/scenarios → intelligent-core/ai-foundation/learning-knowledge/knowledge/scenarios
```

### Gradual Migration

- ✅ Create new structure first
- ✅ Copy (don't move) initially
- ✅ Update code gradually
- ✅ Test each component
- ✅ Remove old files only when all tests pass

### Rollback Plan

```bash
# If issues found:
1. Restore from backup
2. Keep using /catalogs (old location)
3. Fix issues in new structure
4. Re-attempt migration
```

---

## 📅 Timeline

### Week 1: Structure & Migration
- Day 1-2: Create structure, move files
- Day 3: Update references, test
- Day 4-5: Fix issues, verify all services work

### Week 2: API & Integration
- Day 1-2: Create Knowledge API
- Day 3-4: Integrate with RAG, LLM Router
- Day 5: Testing and documentation

---

## ✅ Acceptance Criteria

Migration complete when:

- ✅ All knowledge in `/intelligent-core/ai-foundation/learning-knowledge/knowledge/`
- ✅ Knowledge API works (standards, scenarios, catalogs accessible)
- ✅ All services use new paths
- ✅ RAG pipeline indexes new location
- ✅ Documentation updated
- ✅ Tests pass
- ✅ No broken links

---

**Created:** 2025-10-14
**Status:** Plan Ready
**Next Step:** Execute Phase 1 migration

---

**🎯 Comprehensive knowledge architecture reorganization plan ready for execution!**
