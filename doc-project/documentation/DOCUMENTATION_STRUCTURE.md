# Documentation Structure & Organization

**Date**: 2025-10-08
**Status**: Complete Organization Map

## Directory Structure

```
AI-Platform-ISO/
│
├── doc-project/                          # 📚 ЦЕНТР ДОКУМЕНТАЦИИ
│   ├── _archived_docs/                   # 🗄️ Архивы старой документации
│   │   ├── intelligent-core/             # 10 архивов модулей
│   │   ├── platform-services/            # 11 архивов сервисов
│   │   ├── infrastructure/               # 7 архивов компонентов
│   │   ├── shared_README_*.md            # 1 архив shared
│   │   └── tests_README_*.md             # 1 архив tests
│   │
│   ├── COMPLETE_SYSTEM_DOCUMENTATION.md  # 🏆 ГЛАВНЫЙ ДОКУМЕНТ
│   ├── FINAL_DOCUMENTATION_STATUS.md     # ✅ Финальный статус
│   ├── DOCUMENTATION_UPDATE_COMPLETE_REPORT.md  # Полный отчёт
│   ├── DOCUMENTATION_UPDATE_SUMMARY.md   # Краткая сводка
│   ├── DOCUMENTATION_UPDATE_PROGRESS.md  # Прогресс по фазам
│   └── DOCUMENTATION_STRUCTURE.md        # 📂 Этот файл (карта)
│
├── intelligent-core/                     # 🧠 AI МОДУЛИ
│   ├── README.md                         # Layer index (10 модулей)
│   ├── ai-foundation/README.md           # 23,019 LOC
│   ├── workflow_intelligence/README.md   # 24,392 LOC
│   ├── collective/README.md              # 5,230 LOC
│   ├── community_intelligence/README.md  # 8,116 LOC
│   ├── predictive/README.md              # 4,761 LOC
│   ├── orchestration/README.md           # 25,171 LOC
│   ├── expertise-center/README.md        # 11,846 LOC
│   ├── workflow-engine/README.md         # 6,361 LOC
│   ├── event_intelligence/README.md      # 3,545 LOC
│   └── ai_workflow_optimizer/README.md   # 1,701 LOC
│
├── platform-services/                    # 🏢 BCM СЕРВИСЫ
│   ├── README.md                         # Layer index (11 сервисов)
│   ├── bia-service/
│   │   ├── README.md                     # 11,474 LOC
│   │   └── API.md                        # 54 endpoints
│   ├── risk-service/
│   │   ├── README.md                     # 10,842 LOC
│   │   └── API.md                        # 49 endpoints
│   ├── compliance-service/
│   │   ├── README.md                     # 11,651 LOC
│   │   └── API.md                        # 58 endpoints
│   ├── governance-service/
│   │   ├── README.md                     # 11,058 LOC
│   │   └── API.md                        # 52 endpoints
│   ├── documents-service/
│   │   ├── README.md                     # 11,163 LOC
│   │   └── API.md                        # 51 endpoints
│   ├── validation-service/
│   │   ├── README.md                     # 7,567 LOC
│   │   └── API.md                        # 49 endpoints
│   ├── response-service/README.md        # ~8,000 LOC
│   ├── community-service/README.md       # ~6,000 LOC
│   ├── learning-service/README.md        # ~7,500 LOC
│   ├── planning_service/README.md        # ~6,500 LOC
│   └── plans_service/README.md           # ~6,200 LOC
│
├── infrastructure/                       # ⚙️ ИНФРАСТРУКТУРА
│   ├── README.md                         # Layer index (7 компонентов)
│   ├── database/README.md                # 3,830 LOC
│   ├── eventbus/README.md                # 3,445 LOC
│   ├── observability/README.md           # ~2,500 LOC
│   ├── tools/README.md                   # 7,749 LOC
│   ├── security/README.md                # ~1,800 LOC
│   ├── gateway/README.md                 # ~2,200 LOC
│   └── runtime/README.md                 # ~1,500 LOC
│
├── shared/                               # 🔧 ОБЩИЕ УТИЛИТЫ
│   └── README.md                         # Shared library
│
├── tests/                                # 🧪 ТЕСТЫ
│   └── README.md                         # Testing suite
│
└── interface/                            # 🖥️ ИНТЕРФЕЙСЫ
    ├── README.md                         # Layer index (интерфейсы)
    ├── FRONTEND_SPECIFICATION_BRIEF.md   # 🎯 ТЗ для Frontend
    ├── admin-control-center/             # Main admin UI
    ├── admin_panel/                      # Admin panel
    ├── web-app/                          # User app
    └── fastapi-dashboard/                # Dashboard
```

## 📚 Documentation Categories

### 1. Main Documentation Hub: `/doc-project/`

**Purpose**: Centralized documentation repository

**Key Documents**:
- `COMPLETE_SYSTEM_DOCUMENTATION.md` - **НАЧИНАЙТЕ ЗДЕСЬ** (главный документ)
- `FINAL_DOCUMENTATION_STATUS.md` - Текущий статус всей документации
- `DOCUMENTATION_UPDATE_COMPLETE_REPORT.md` - Полный отчёт по обновлению
- `DOCUMENTATION_UPDATE_SUMMARY.md` - Executive summary
- `DOCUMENTATION_STRUCTURE.md` - **ЭТОТ ФАЙЛ** (навигация)

**Archives**: `_archived_docs/`
- 30 timestamped backups всей старой документации
- Организовано по слоям (intelligent-core, platform-services, infrastructure)

### 2. Layer Documentation (4 слоя)

Each layer has:
- **Layer README.md** - Overview, architecture, metrics
- **Component READMEs** - Individual component documentation

**Layers**:
1. `intelligent-core/README.md` - 10 AI modules
2. `platform-services/README.md` - 11 BCM services
3. `infrastructure/README.md` - 7 infrastructure components
4. `interface/README.md` - Frontend applications

### 3. Component Documentation

Each component has:
- **README.md** - Overview, installation, usage, standards
- **API.md** (services) - Complete API reference
- **Last Updated**: 2025-10-08

**Example Structure**:
```
platform-services/bia-service/
├── README.md          # Component overview
├── API.md             # 54 API endpoints
└── (source code...)
```

### 4. Cross-Cutting Documentation

**Shared Library**: `shared/README.md`
- Authentication, Database, Cache, Event Bus patterns
- Used by all layers

**Tests**: `tests/README.md`
- Unit, Integration, E2E, Load tests
- Testing infrastructure

### 5. Frontend Documentation

**Location**: `interface/`

**Key Documents**:
- `interface/README.md` - Frontend layer overview
- `interface/FRONTEND_SPECIFICATION_BRIEF.md` - **ПОЛНОЕ ТЗ**
  - 513+ API endpoints reference
  - Data models
  - UI/UX requirements
  - Technical stack
  - Development phases

### 6. Tools Documentation

**Location**: `infrastructure/tools/`

**Created Tools** (8):
1. `archive-old-docs.sh`
2. `generate-module-docs.py`
3. `generate-service-docs.py`
4. `generate-infrastructure-docs.py`
5. `batch-update-docs.sh`
6. `batch-update-all-platform-services.sh`
7. `batch-update-infrastructure.sh`
8. `check-docs-freshness.sh`

## 🗺️ Navigation Guide

### For Developers

**Starting Point**: `/doc-project/COMPLETE_SYSTEM_DOCUMENTATION.md`

**Backend Development**:
1. Read layer README (intelligent-core, platform-services, infrastructure)
2. Read specific component README
3. Check API.md for service endpoints
4. Review architecture diagrams (Mermaid)

**Frontend Development**:
1. Read `interface/FRONTEND_SPECIFICATION_BRIEF.md`
2. Check service API.md files for endpoints
3. Review data models section
4. Follow technical recommendations

**DevOps/Infrastructure**:
1. Read `infrastructure/README.md`
2. Check component READMEs
3. Review deployment guides
4. Use automation tools

### For Management

**Executive View**: `/doc-project/DOCUMENTATION_UPDATE_SUMMARY.md`
**Status Report**: `/doc-project/FINAL_DOCUMENTATION_STATUS.md`
**Complete Overview**: `/doc-project/COMPLETE_SYSTEM_DOCUMENTATION.md`

## 📊 Documentation Statistics

### By Category

| Category | Files | Lines | Status |
|----------|-------|-------|--------|
| Layer Indexes | 4 | ~2,000 | ✅ |
| Core Modules | 10 | 114,142 LOC | ✅ |
| Services | 11 | 97,955 LOC | ✅ |
| Infrastructure | 7 | 23,024 LOC | ✅ |
| Cross-Cutting | 2 | - | ✅ |
| Frontend Spec | 1 | - | ✅ |
| Reports | 5 | ~15,000 | ✅ |
| **TOTAL** | **40** | **~252,121** | ✅ |

### Quality Metrics

- ✅ **Language**: 100% English
- ✅ **Style**: Professional, third-person
- ✅ **Standards**: ISO/IEC/IEEE 26514:2022
- ✅ **Diagrams**: Mermaid in all layer docs
- ✅ **Dates**: All current (2025-10-08)
- ✅ **Archives**: 30 backups preserved

## 🔍 Search & Discovery

### Find Documentation

```bash
# Find all READMEs
find . -name "README.md" -type f

# Find API documentation
find platform-services -name "API.md"

# Find specific component
ls -la intelligent-core/ai-foundation/README.md
ls -la platform-services/bia-service/README.md
ls -la infrastructure/database/README.md

# Check documentation age
./infrastructure/tools/check-docs-freshness.sh
```

### Key Paths

```bash
# Main docs hub
cd doc-project/

# Layer documentation
cd intelligent-core/
cd platform-services/
cd infrastructure/
cd interface/

# Archives
cd doc-project/_archived_docs/

# Tools
cd infrastructure/tools/
```

## 🎯 Quick Access Links

### Main Documents
- [Complete System Documentation](./COMPLETE_SYSTEM_DOCUMENTATION.md) ⭐
- [Final Status](./FINAL_DOCUMENTATION_STATUS.md)
- [Summary](./DOCUMENTATION_UPDATE_SUMMARY.md)

### Layer Documentation
- [Intelligent Core](../intelligent-core/README.md)
- [Platform Services](../platform-services/README.md)
- [Infrastructure](../infrastructure/README.md)
- [Interface](../interface/README.md)

### Frontend Development
- [Frontend Specification](../interface/FRONTEND_SPECIFICATION_BRIEF.md) 🎯

### Cross-Cutting
- [Shared Library](../shared/README.md)
- [Tests](../tests/README.md)

## 📝 Documentation Standards

All documentation follows:

1. **ISO/IEC/IEEE 26514:2022** - Software documentation
2. **English only** - No mixed languages
3. **Professional tone** - Third-person, formal
4. **No emojis** - Except status indicators (✅ ⚠️ ❌)
5. **Last Updated date** - In every README
6. **Mermaid diagrams** - Architecture visualization
7. **Cross-references** - Links to related components

## 🔄 Maintenance

### Regular Updates

```bash
# Check documentation age
./infrastructure/tools/check-docs-freshness.sh

# Archive before updating
./infrastructure/tools/archive-old-docs.sh <component>

# Batch update layer
./infrastructure/tools/batch-update-*.sh
```

### Update Frequency

- **Weekly**: Freshness check
- **Monthly**: Active component updates
- **Quarterly**: Full audit

---

**Last Updated**: 2025-10-08
**Maintainer**: Documentation Team
**Status**: ✅ Complete & Organized
