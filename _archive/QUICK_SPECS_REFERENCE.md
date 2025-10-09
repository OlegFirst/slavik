# Быстрая справка по спецификациям

**Версия**: 2.0.0 | **Дата**: 2025-10-09

---

## 🎯 ТОП-10 главных документов

### 1. Техническое задание UI/UX
📄 [**doc-project/TZ_USER_INTERFACE.md**](doc-project/TZ_USER_INTERFACE.md) (35 KB)
- Полное ТЗ пользовательского интерфейса
- 10 разделов пользователя + 10 разделов админа
- Технологический стек: Next.js 14, TypeScript, Tailwind
- Timeline: 14-21 недель

### 2. Главное ТЗ платформы
📄 [**doc-project/TZ_AI_BCM_PLATFORM.md**](doc-project/TZ_AI_BCM_PLATFORM.md) (63 KB)
- Полное техническое задание AI-Platform-ISO
- Все модули, сервисы, интеграции
- ISO 22301 compliance

### 3. Архитектура платформы
📄 [**docs/ARCHITECTURE.md**](docs/ARCHITECTURE.md) (73 KB)
- Детальное описание всей архитектуры
- 4 слоя: Infrastructure, Intelligent Core, Platform Services, Integration
- 23 сервиса, 20 портов

### 4. API Reference
📄 [**docs/API_REFERENCE.md**](docs/API_REFERENCE.md) (40 KB)
- 150+ endpoints всех сервисов
- REST API спецификация
- Примеры requests/responses

### 5. Deployment Guide
📄 [**docs/DEPLOYMENT_GUIDE.md**](docs/DEPLOYMENT_GUIDE.md) (27 KB)
- Полное руководство по развертыванию
- Docker Compose (dev)
- Kubernetes (production)

### 6. ISO/NIST Compliance
📄 [**docs/STANDARDS_COMPLIANCE.md**](docs/STANDARDS_COMPLIANCE.md) (28 KB)
- Соответствие ISO 22301:2019
- NIST Cybersecurity Framework
- GDPR, SOC 2

### 7. Диаграммы (36 шт)
📁 [**doc-project/diagrams/**](doc-project/diagrams/)
- Architecture (24)
- User Scenarios (4)
- Dependencies (1)
- Flows (3)
- Integration (4)
- [README диаграмм](doc-project/diagrams/README.md)

### 8. Унифицированная архитектурная спецификация
📄 [**doc-project/architecture/FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md**](doc-project/architecture/FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md) (97 KB)
- Финальная унифицированная архитектура
- Все компоненты детально

### 9. Platform Services API
📄 [**platform-services/API_REFERENCE.md**](platform-services/API_REFERENCE.md) (23 KB)
- API Reference всех Platform Services
- 12 сервисов

### 10. EventBus Architecture
📄 [**infrastructure/eventbus/ARCHITECTURE.md**](infrastructure/eventbus/ARCHITECTURE.md) (13 KB)
- Архитектура EventBus
- Redis Streams + RabbitMQ
- Event-driven patterns

---

## 📊 Полный каталог

📄 [**SPECIFICATIONS_CATALOG.md**](doc-project/SPECIFICATIONS_CATALOG.md)
- **108 спецификаций** всего
- Организованы по категориям
- Полные описания и размеры

---

## 🗂️ По ролям

### Product Manager / Stakeholder
1. [TZ_AI_BCM_PLATFORM.md](doc-project/TZ_AI_BCM_PLATFORM.md)
2. [docs/EXECUTIVE_SUMMARY.md](docs/EXECUTIVE_SUMMARY.md)
3. [docs/STANDARDS_COMPLIANCE.md](docs/STANDARDS_COMPLIANCE.md)

### UI/UX Designer
1. [TZ_USER_INTERFACE.md](doc-project/TZ_USER_INTERFACE.md)
2. [diagrams/user-scenarios/](doc-project/diagrams/user-scenarios/)
3. [learning-service/FRONTEND_SPECIFICATION.md](platform-services/learning-service/FRONTEND_SPECIFICATION.md)

### Backend Developer
1. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
2. [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
3. [platform-services/API_REFERENCE.md](platform-services/API_REFERENCE.md)
4. [Выбрать сервис](doc-project/SPECIFICATIONS_CATALOG.md#спецификации-сервисов)

### AI/ML Engineer
1. [intelligent-core/ARCHITECTURE.md](intelligent-core/ARCHITECTURE.md)
2. [orchestration/ai-orchestration/ARCHITECTURE.md](intelligent-core/orchestration/ai-orchestration/ARCHITECTURE.md)
3. [community_intelligence/TECHNICAL_SPECIFICATION.md](intelligent-core/community_intelligence/docs/TECHNICAL_SPECIFICATION.md)

### DevOps Engineer
1. [infrastructure/DEPLOYMENT_ROADMAP.md](infrastructure/DEPLOYMENT_ROADMAP.md)
2. [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
3. [DEPLOYMENT_PORT_MAP.md](doc-project/DEPLOYMENT_PORT_MAP.md)

---

## 📍 Быстрые ссылки

- 📚 [Главный README](README.md)
- 🗺️ [PROJECT_INDEX](PROJECT_INDEX.md)
- 📊 [Диаграммы](doc-project/diagrams/README.md)
- 📋 [Полный каталог спецификаций](doc-project/SPECIFICATIONS_CATALOG.md)
- 🏗️ [Architecture Map](docs/PLATFORM_ARCHITECTURE_MAP.md)

---

**Всего спецификаций**: 108 документов (~1.67 MB)
