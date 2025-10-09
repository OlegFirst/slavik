# Полный каталог спецификаций AI-Platform-ISO

**Дата**: 2025-10-09
**Версия платформы**: 2.0.0
**Всего спецификаций**: 108 документов

---

## 📋 Содержание

1. [Главные спецификации платформы](#главные-спецификации-платформы) (14 документов)
2. [Спецификации сервисов](#спецификации-сервисов) (34 документа)
3. [Спецификации Intelligent Core](#спецификации-intelligent-core) (45 документов)
4. [Frontend спецификации](#frontend-спецификации) (3 документа)
5. [API спецификации](#api-спецификации) (2 документа)
6. [Infrastructure спецификации](#infrastructure-спецификации) (10 документов)

---

## Главные спецификации платформы

**Расположение**: `/docs/` и `/doc-project/`
**Количество**: 14 документов
**Общий размер**: ~463 KB

### 🎯 Основные спецификации (НАЧАТЬ С ЭТОГО)

| Документ | Размер | Описание |
|----------|--------|----------|
| [**TZ_USER_INTERFACE.md**](TZ_USER_INTERFACE.md) | 35 KB | **Техническое задание UI/UX** - Полное ТЗ пользовательского интерфейса и админ-панели |
| [**TZ_AI_BCM_PLATFORM.md**](TZ_AI_BCM_PLATFORM.md) | 63 KB | **Главное ТЗ платформы** - Полное техническое задание AI-Platform-ISO |
| [**docs/ARCHITECTURE.md**](../docs/ARCHITECTURE.md) | 73 KB | **Архитектура платформы** - Детальное описание всей архитектуры |
| [**docs/API_REFERENCE.md**](../docs/API_REFERENCE.md) | 40 KB | **API Reference** - 150+ endpoints всех сервисов |
| [**docs/DEPLOYMENT_GUIDE.md**](../docs/DEPLOYMENT_GUIDE.md) | 27 KB | **Deployment Guide** - Полное руководство по развертыванию |
| [**docs/STANDARDS_COMPLIANCE.md**](../docs/STANDARDS_COMPLIANCE.md) | 28 KB | **ISO/NIST Compliance** - Соответствие стандартам ISO 22301, NIST |

### 📐 Архитектурные спецификации

| Документ | Размер | Описание |
|----------|--------|----------|
| [architecture/FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md](architecture/FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md) | 97 KB | Унифицированная архитектурная спецификация (финальная) |
| [architecture/ARCHITECTURE_FINAL_SPEC.md](architecture/ARCHITECTURE_FINAL_SPEC.md) | 23 KB | Финальная архитектурная спецификация |
| [architecture/PLATFORM_SPECIFICATION.md](architecture/PLATFORM_SPECIFICATION.md) | 19 KB | Спецификация платформы |
| [architecture/PARALLEL_TASK_SPECIFICATION.md](architecture/PARALLEL_TASK_SPECIFICATION.md) | 10 KB | Спецификация параллельных задач |

### 🛠️ Технические спецификации

| Документ | Размер | Описание |
|----------|--------|----------|
| [TECHNICAL_SPECS_BY_LAYER.md](TECHNICAL_SPECS_BY_LAYER.md) | 24 KB | Технические спецификации по слоям платформы |
| [ORCHESTRATOR_SUPER_BRAIN_SPEC.md](ORCHESTRATOR_SUPER_BRAIN_SPEC.md) | 21 KB | Спецификация AI Orchestrator ("Супер-мозг") |
| [DEPLOYMENT_PORT_MAP.md](DEPLOYMENT_PORT_MAP.md) | 15 KB | Карта портов для deployment (20 сервисов) |

---

## Спецификации сервисов

**Расположение**: `/platform-services/*/docs/`
**Количество**: 34 документа
**Общий размер**: ~337 KB

### 📊 Главные спецификации сервисов

| Документ | Размер | Описание |
|----------|--------|----------|
| [**platform-services/API_REFERENCE.md**](../platform-services/API_REFERENCE.md) | 23 KB | API Reference всех Platform Services |
| [**platform-services/ARCHITECTURE.md**](../platform-services/ARCHITECTURE.md) | 8 KB | Архитектура слоя Platform Services |
| [**platform-services/docs/deployment/DEPLOYMENT_GUIDE.md**](../platform-services/docs/deployment/DEPLOYMENT_GUIDE.md) | 16 KB | Deployment guide для всех сервисов |

### 🎓 Frontend спецификации сервисов

| Сервис | Документ | Размер | Описание |
|--------|----------|--------|----------|
| **Learning Service** | [FRONTEND_SPECIFICATION.md](../platform-services/learning-service/FRONTEND_SPECIFICATION.md) | 59 KB | Спецификация интерфейса обучающей системы |
| **Digital Twin** | [FRONTEND_SPECIFICATION.md](../platform-services/simulation/digital-twin/docs/FRONTEND_SPECIFICATION.md) | 44 KB | Спецификация интерфейса Digital Twin симуляций |
| **Community Service** | [FRONTEND_SPECIFICATION_SUMMARY.md](../platform-services/community-service/FRONTEND_SPECIFICATION_SUMMARY.md) | 20 KB | Спецификация интерфейса Community Portal |

### 🔧 Технические спецификации по сервисам

#### BCM Core Services

| Сервис | Technical Spec | Deployment |
|--------|---------------|------------|
| **BIA Service** | [TECHNICAL_SPECIFICATION.md](../platform-services/bia-service/docs/TECHNICAL_SPECIFICATION.md) (15 KB) | [DEPLOYMENT.md](../platform-services/bia-service/docs/DEPLOYMENT.md) (16 KB) |
| **Risk Service** | [TECHNICAL_SPECIFICATION.md](../platform-services/risk-service/docs/TECHNICAL_SPECIFICATION.md) (0.3 KB) | [DEPLOYMENT.md](../platform-services/risk-service/docs/DEPLOYMENT.md) (0.3 KB) |
| **Compliance Service** | [TECHNICAL_SPECIFICATION.md](../platform-services/compliance-service/docs/TECHNICAL_SPECIFICATION.md) (0.3 KB) | [DEPLOYMENT.md](../platform-services/compliance-service/docs/DEPLOYMENT.md) (0.3 KB) |
| **Governance Service** | [TECHNICAL_SPECIFICATION.md](../platform-services/governance-service/docs/TECHNICAL_SPECIFICATION.md) (0.3 KB) | [DEPLOYMENT.md](../platform-services/governance-service/docs/DEPLOYMENT.md) (0.3 KB) |

#### Planning & Execution Services

| Сервис | Technical Spec | Deployment |
|--------|---------------|------------|
| **Planning Service** | [TECHNICAL_SPECIFICATION.md](../platform-services/planning-service/docs/TECHNICAL_SPECIFICATION.md) (0.3 KB) | [DEPLOYMENT.md](../platform-services/planning-service/docs/DEPLOYMENT.md) (0.3 KB) |
| **Plans Service** | [TECHNICAL_SPECIFICATION.md](../platform-services/plans-service/docs/TECHNICAL_SPECIFICATION.md) (0.3 KB) | [DEPLOYMENT.md](../platform-services/plans-service/docs/DEPLOYMENT.md) (0.3 KB) |
| **Response Service** | [TECHNICAL_SPECIFICATION.md](../platform-services/response-service/docs/TECHNICAL_SPECIFICATION.md) (0.3 KB) | [DEPLOYMENT.md](../platform-services/response-service/docs/DEPLOYMENT.md) (0.3 KB) |

#### Support Services

| Сервис | Technical Spec | Deployment |
|--------|---------------|------------|
| **Documents Service** | [TECHNICAL_SPECIFICATION.md](../platform-services/documents-service/docs/TECHNICAL_SPECIFICATION.md) (0.3 KB) | [DEPLOYMENT.md](../platform-services/documents-service/docs/DEPLOYMENT.md) (0.3 KB) |
| **Validation Service** | [TECHNICAL_SPECIFICATION.md](../platform-services/validation-service/docs/TECHNICAL_SPECIFICATION.md) (0.3 KB) | [DEPLOYMENT.md](../platform-services/validation-service/docs/DEPLOYMENT.md) (0.3 KB) |
| **Learning Service** | [TECHNICAL_SPECIFICATION.md](../platform-services/learning-service/docs/TECHNICAL_SPECIFICATION.md) (0.3 KB) | [DEPLOYMENT.md](../platform-services/learning-service/docs/DEPLOYMENT.md) (0.3 KB) |
| **Community Service** | [TECHNICAL_SPECIFICATION.md](../platform-services/community-service/docs/TECHNICAL_SPECIFICATION.md) (0.3 KB) | [DEPLOYMENT.md](../platform-services/community-service/docs/DEPLOYMENT.md) (0.3 KB) |
| **BCM Coordination** | [TECHNICAL_SPECIFICATION.md](../platform-services/bcm-coordination-service/docs/TECHNICAL_SPECIFICATION.md) (0.3 KB) | [DEPLOYMENT.md](../platform-services/bcm-coordination-service/docs/DEPLOYMENT.md) (0.3 KB) |

#### Advanced Services

| Сервис | Documents |
|--------|-----------|
| **Living Docs** | [ARCHITECTURE.md](../platform-services/living-docs/docs/ARCHITECTURE.md) (25 KB) |
| **Digital Twin** | [DEPLOYMENT.md](../platform-services/simulation/digital-twin/docs/DEPLOYMENT.md) (12 KB), [FRONTEND_SPEC](../platform-services/simulation/digital-twin/docs/FRONTEND_SPECIFICATION.md) (44 KB) |
| **Community Portal** | [DEPLOYMENT.md](../platform-services/community-service/portal/DEPLOYMENT.md) (7 KB) |
| **Marketplace** | [IMPLEMENTATION_SPEC.md](../platform-services/community-service/marketplace/IMPLEMENTATION_SPEC.md) (6 KB) |

---

## Спецификации Intelligent Core

**Расположение**: `/intelligent-core/*/docs/`
**Количество**: 45 документов
**Общий размер**: ~550 KB

### 🧠 AI Foundation & Core Modules

| Модуль | Architecture | Deployment | Technical Spec |
|--------|--------------|------------|----------------|
| **AI Foundation** | [ARCHITECTURE.md](../intelligent-core/ai-foundation/docs/ARCHITECTURE.md) (0.8 KB) | [DEPLOYMENT.md](../intelligent-core/ai-foundation/docs/DEPLOYMENT.md) (0.2 KB) | - |
| **Orchestration** | [ARCHITECTURE.md](../intelligent-core/orchestration/docs/ARCHITECTURE.md) (1 KB) | [DEPLOYMENT.md](../intelligent-core/orchestration/docs/DEPLOYMENT.md) (1.1 KB) | - |
| **Expertise Center** | [ARCHITECTURE.md](../intelligent-core/expertise-center/docs/ARCHITECTURE.md) (0.8 KB) | [DEPLOYMENT.md](../intelligent-core/expertise-center/docs/DEPLOYMENT.md) (0.2 KB) | - |
| **Shared** | [ARCHITECTURE.md](../intelligent-core/shared/docs/ARCHITECTURE.md) (0.9 KB) | [DEPLOYMENT.md](../intelligent-core/shared/docs/DEPLOYMENT.md) (1.1 KB) | - |
| **Wrappers** | [ARCHITECTURE.md](../intelligent-core/wrappers/docs/ARCHITECTURE.md) (0.9 KB) | [DEPLOYMENT.md](../intelligent-core/wrappers/docs/DEPLOYMENT.md) (1.1 KB) | - |

### 🤖 AI Specialists

| Модуль | Architecture | Deployment | Technical Spec |
|--------|--------------|------------|----------------|
| **Collective Intelligence** | [ARCHITECTURE.md](../intelligent-core/collective/docs/ARCHITECTURE.md) (19 KB) | - | [TECHNICAL_SPECIFICATION.md](../intelligent-core/collective/docs/TECHNICAL_SPECIFICATION.md) (13 KB) |
| **Community Intelligence** | [ARCHITECTURE.md](../intelligent-core/community_intelligence/docs/ARCHITECTURE.md) (1.1 KB) | [DEPLOYMENT.md](../intelligent-core/community_intelligence/docs/DEPLOYMENT.md) (1.2 KB) | [TECHNICAL_SPECIFICATION.md](../intelligent-core/community_intelligence/docs/TECHNICAL_SPECIFICATION.md) (67 KB) |
| **Predictive Intelligence** | [ARCHITECTURE.md](../intelligent-core/predictive/docs/ARCHITECTURE.md) (20 KB) | [DEPLOYMENT.md](../intelligent-core/predictive/docs/DEPLOYMENT.md) (19 KB) | [TECHNICAL_SPECIFICATION.md](../intelligent-core/predictive/docs/TECHNICAL_SPECIFICATION.md) (21 KB) |
| **Event Intelligence** | [ARCHITECTURE.md](../intelligent-core/event_intelligence/ARCHITECTURE.md) (13 KB) | [DEPLOYMENT.md](../intelligent-core/event_intelligence/docs/DEPLOYMENT.md) (1.2 KB) | - |
| **Learning System** | [ARCHITECTURE.md](../intelligent-core/learning-system/docs/ARCHITECTURE.md) (1 KB) | [DEPLOYMENT.md](../intelligent-core/learning-system/docs/DEPLOYMENT.md) (1.1 KB) | [TECHNICAL_SPECIFICATION.md](../intelligent-core/learning-system/docs/TECHNICAL_SPECIFICATION.md) (40 KB) |
| **Knowledge System** | [ARCHITECTURE.md](../intelligent-core/knowledge-system/docs/ARCHITECTURE.md) (1 KB) | [DEPLOYMENT.md](../intelligent-core/knowledge-system/docs/DEPLOYMENT.md) (1.2 KB) | - |

### 🔄 Workflow & Optimization

| Модуль | Architecture | Deployment | Additional |
|--------|--------------|------------|------------|
| **Workflow Engine** | [ARCHITECTURE.md](../intelligent-core/workflow-engine/docs/ARCHITECTURE.md) (1 KB) | [DEPLOYMENT.md](../intelligent-core/workflow-engine/docs/DEPLOYMENT.md) (1.1 KB) | - |
| **Workflow Intelligence** | [ARCHITECTURE.md](../intelligent-core/workflow_intelligence/docs/temporal/ARCHITECTURE.md) (31 KB) | - | - |
| **AI Workflow Optimizer** | [ARCHITECTURE.md](../intelligent-core/ai_workflow_optimizer/docs/ARCHITECTURE.md) (1 KB) | [DEPLOYMENT.md](../intelligent-core/ai_workflow_optimizer/docs/DEPLOYMENT.md) (1.2 KB) | - |

### 🎯 Orchestration Subsystem

| Документ | Размер | Описание |
|----------|--------|----------|
| [AI Orchestration ARCHITECTURE](../intelligent-core/orchestration/ai-orchestration/ARCHITECTURE.md) | 26 KB | Детальная архитектура AI Orchestrator |
| [AI Orchestration DEPLOYMENT_GUIDE](../intelligent-core/orchestration/ai-orchestration/DEPLOYMENT_GUIDE.md) | 8 KB | Руководство по развертыванию |
| [AI Orchestration INTEGRATION_SPEC](../intelligent-core/orchestration/ai-orchestration/INTEGRATION_SPEC.md) | 16 KB | Спецификация интеграции |

### 👨‍💼 Expertise Center

| Документ | Размер | Описание |
|----------|--------|----------|
| [Expertise Center DEPLOYMENT_GUIDE](../intelligent-core/expertise-center/service/DEPLOYMENT_GUIDE.md) | 12 KB | Руководство по развертыванию 14 AI специалистов |

### 📚 Общая архитектура Intelligent Core

| Документ | Размер | Описание |
|----------|--------|----------|
| [intelligent-core/ARCHITECTURE.md](../intelligent-core/ARCHITECTURE.md) | 6 KB | Общая архитектура всего Intelligent Core |

---

## Frontend спецификации

**Расположение**: Разные папки
**Количество**: 3 документа
**Общий размер**: ~89 KB

| Документ | Размер | Описание |
|----------|--------|----------|
| [**interface/FRONTEND_SPECIFICATION_BRIEF.md**](../interface/FRONTEND_SPECIFICATION_BRIEF.md) | 11 KB | Краткая спецификация frontend интерфейса |
| [infrastructure/security/DEPLOYMENT_GUIDE.md](../infrastructure/security/DEPLOYMENT_GUIDE.md) | 14 KB | Security deployment guide |
| [_archive/docs-old-backup/guides/SECURITY_SPECIFICATIONS.md](../_archive/docs-old-backup/guides/SECURITY_SPECIFICATIONS.md) | 64 KB | Детальные спецификации безопасности (архив) |

---

## API спецификации

**Расположение**: `/docs/` и `/_archive/docs-old-backup/api/`
**Количество**: 2 документа
**Общий размер**: ~66 KB

| Документ | Размер | Описание | Статус |
|----------|--------|----------|--------|
| [**docs/API_REFERENCE.md**](../docs/API_REFERENCE.md) | 40 KB | **Актуальный API Reference** - 150+ endpoints | ✅ Актуально |
| [_archive/OPENAPI_SPECIFICATION.md](../_archive/docs-old-backup/api/OPENAPI_SPECIFICATION.md) | 37 KB | OpenAPI 3.0 specification | 📦 Архив |
| [_archive/ASYNCAPI_SPECIFICATION.md](../_archive/docs-old-backup/api/ASYNCAPI_SPECIFICATION.md) | 29 KB | AsyncAPI specification (EventBus) | 📦 Архив |

---

## Infrastructure спецификации

**Расположение**: `/infrastructure/*/`
**Количество**: 10 документов
**Общий размер**: ~168 KB

### 🏗️ Общие спецификации Infrastructure

| Документ | Размер | Описание |
|----------|--------|----------|
| [**infrastructure/DEPLOYMENT_ROADMAP.md**](../infrastructure/DEPLOYMENT_ROADMAP.md) | 26 KB | Roadmap развертывания инфраструктуры |
| [infrastructure/eventbus/ARCHITECTURE.md](../infrastructure/eventbus/ARCHITECTURE.md) | 13 KB | Архитектура EventBus (Redis Streams + RabbitMQ) |

### 📦 Спецификации компонентов Infrastructure

| Компонент | Документ | Размер |
|-----------|----------|--------|
| **Database** | [SERVICE_SPEC.md](../infrastructure/database/SERVICE_SPEC.md) | 14 KB |
| **Gateway** | [SERVICE_SPEC.md](../infrastructure/gateway/SERVICE_SPEC.md) | 15 KB |
| **Runtime** | [SERVICE_SPEC.md](../infrastructure/runtime/SERVICE_SPEC.md) | 19 KB |
| **Security** | [SERVICE_SPEC.md](../infrastructure/security/SERVICE_SPEC.md) | 17 KB |

### 🤖 AI Office Infrastructure

| Компонент | Документ | Размер |
|-----------|----------|--------|
| **MIO Manager** | [WORKFLOW_SPECIFICATION.md](../infrastructure/AI-office-infrastructure/mio-manager/WORKFLOW_SPECIFICATION.md) | 22 KB |
| **Agent Router** | [WORKFLOW_SPECIFICATION.md](../infrastructure/AI-office-infrastructure/agent-router/WORKFLOW_SPECIFICATION.md) | 16 KB |
| **DevOps Agent** | [DEVOPS_AGENT_SPECIFICATION.md](../infrastructure/AI-office-infrastructure/devops-agent/DEVOPS_AGENT_SPECIFICATION.md) | 13 KB |

---

## 🎯 Рекомендуемый порядок изучения

### Для Product Manager / Stakeholder

1. **[TZ_AI_BCM_PLATFORM.md](TZ_AI_BCM_PLATFORM.md)** (63 KB) - Главное ТЗ платформы
2. **[docs/EXECUTIVE_SUMMARY.md](../docs/EXECUTIVE_SUMMARY.md)** - Executive summary
3. **[docs/STANDARDS_COMPLIANCE.md](../docs/STANDARDS_COMPLIANCE.md)** (28 KB) - Соответствие ISO/NIST
4. **[docs/DEPLOYMENT_GUIDE.md](../docs/DEPLOYMENT_GUIDE.md)** (27 KB) - Deployment roadmap

### Для UI/UX Designer

1. **[TZ_USER_INTERFACE.md](TZ_USER_INTERFACE.md)** (35 KB) - Полное ТЗ UI/UX
2. **[diagrams/user-scenarios/](diagrams/)** - Диаграммы пользовательских сценариев
3. **[learning-service/FRONTEND_SPECIFICATION.md](../platform-services/learning-service/FRONTEND_SPECIFICATION.md)** (59 KB)
4. **[digital-twin/FRONTEND_SPECIFICATION.md](../platform-services/simulation/digital-twin/docs/FRONTEND_SPECIFICATION.md)** (44 KB)

### Для Backend Developer

1. **[docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)** (73 KB) - Архитектура платформы
2. **[docs/API_REFERENCE.md](../docs/API_REFERENCE.md)** (40 KB) - API Reference
3. **[platform-services/API_REFERENCE.md](../platform-services/API_REFERENCE.md)** (23 KB) - Services API
4. **[infrastructure/eventbus/ARCHITECTURE.md](../infrastructure/eventbus/ARCHITECTURE.md)** (13 KB) - EventBus
5. Выбрать нужный сервис из [Спецификации сервисов](#спецификации-сервисов)

### Для AI/ML Engineer

1. **[intelligent-core/ARCHITECTURE.md](../intelligent-core/ARCHITECTURE.md)** (6 KB) - Общая архитектура
2. **[ai-foundation/docs/ARCHITECTURE.md](../intelligent-core/ai-foundation/docs/ARCHITECTURE.md)** - AI Foundation
3. **[orchestration/ai-orchestration/ARCHITECTURE.md](../intelligent-core/orchestration/ai-orchestration/ARCHITECTURE.md)** (26 KB) - AI Orchestrator
4. **[community_intelligence/TECHNICAL_SPECIFICATION.md](../intelligent-core/community_intelligence/docs/TECHNICAL_SPECIFICATION.md)** (67 KB)
5. **[learning-system/TECHNICAL_SPECIFICATION.md](../intelligent-core/learning-system/docs/TECHNICAL_SPECIFICATION.md)** (40 KB)

### Для DevOps Engineer

1. **[infrastructure/DEPLOYMENT_ROADMAP.md](../infrastructure/DEPLOYMENT_ROADMAP.md)** (26 KB)
2. **[docs/DEPLOYMENT_GUIDE.md](../docs/DEPLOYMENT_GUIDE.md)** (27 KB)
3. **[DEPLOYMENT_PORT_MAP.md](DEPLOYMENT_PORT_MAP.md)** (15 KB) - Карта портов
4. **[platform-services/docs/deployment/DEPLOYMENT_GUIDE.md](../platform-services/docs/deployment/DEPLOYMENT_GUIDE.md)** (16 KB)
5. Deployment guides отдельных модулей

---

## 📊 Статистика

### По категориям

| Категория | Количество | Общий размер | Процент |
|-----------|------------|--------------|---------|
| Intelligent Core | 45 | ~550 KB | 41.7% |
| Platform Services | 34 | ~337 KB | 31.5% |
| Platform (общие) | 14 | ~463 KB | 13.0% |
| Infrastructure | 10 | ~168 KB | 9.3% |
| Frontend | 3 | ~89 KB | 2.8% |
| API | 2 | ~66 KB | 1.9% |
| **ВСЕГО** | **108** | **~1.67 MB** | **100%** |

### По типам документов

| Тип | Количество |
|-----|------------|
| ARCHITECTURE.md | ~35 |
| TECHNICAL_SPECIFICATION.md | ~20 |
| DEPLOYMENT.md / DEPLOYMENT_GUIDE.md | ~30 |
| FRONTEND_SPECIFICATION.md | ~6 |
| API_REFERENCE.md | ~3 |
| SERVICE_SPEC.md | ~5 |
| Прочие спецификации | ~9 |

---

## 🔗 Связанные документы

- [**README.md**](../README.md) - Главный README проекта
- [**PROJECT_INDEX.md**](../PROJECT_INDEX.md) - Мастер-индекс проекта
- [**diagrams/README.md**](diagrams/README.md) - Каталог всех диаграмм (36 шт)
- [**docs/INDEX.md**](../docs/INDEX.md) - Индекс основной документации
- [**docs/COMPLETE_DOCUMENTATION_MAP.md**](../docs/COMPLETE_DOCUMENTATION_MAP.md) - Полная карта документации

---

## 📝 Заметки

### Статус спецификаций

- ✅ **Актуальные** - Документы в `/docs/` и `/doc-project/` (обновлены 2025-10-09)
- 📦 **Архивные** - Документы в `/_archive/` (сохранены для истории)
- ⚠️ **Заглушки** - Некоторые TECHNICAL_SPECIFICATION.md в сервисах (~0.3 KB)

### Приоритетные задачи

1. ⚠️ Заполнить заглушки TECHNICAL_SPECIFICATION.md в Platform Services
2. 🔄 Обновить архивные API спецификации (OpenAPI, AsyncAPI)
3. 📝 Создать единую спецификацию Frontend UI (консолидация 6 документов)

---

**Версия**: 1.0.0
**Дата последнего обновления**: 2025-10-09
**Составлено**: Claude Code Agent
