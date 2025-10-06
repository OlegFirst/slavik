# Infrastructure

Production-ready infrastructure services для BCM Platform.

**📚 Документация:**
- **[INDEX.md](INDEX.md)** - Полный индекс всей документации
- **[OVERVIEW.md](OVERVIEW.md)** - Обзор архитектуры и сервисов
- **[TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md)** - Техническое руководство для разработчиков
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Быстрая справка (commands, status, links)
- **[DOCUMENTATION_SUMMARY.md](DOCUMENTATION_SUMMARY.md)** - Summary организации документации

---

## 📁 Структура

### ✅ Fully Operational Services (с кодом, работают)

**Core Infrastructure:**
- **database/** - PostgreSQL (Supabase) + Redis managers
- **eventbus/** - Event-driven messaging (Memory + Redis Streams)
- **auth/** - JWT authentication service
- **monitoring/** - Prometheus + Grafana monitoring
- **service-discovery/** - Service registry + health monitoring

**Security:**
- **security/api-gateway/** - API Gateway (4,345 строк кода!)
  - Auth middleware (JWT)
  - Rate limiting
  - Audit logging
  - Load balancing
  - Request routing

**Integration & Deployment:**
- **deployment-service/** - Deployment automation (223 строк)
- **github-integration/** - GitHub webhooks + Copilot (99 строк)

**Data & Storage:**
- **vector-db/** - Qdrant Cloud для RAG + Case Library (ГОТОВО! ✅)

---

### ⚠️ Needs Configuration (код есть, нужна настройка)

- **notification-service/** - Email, Slack, Telegram notifications
- **realtime-websocket/** - WebSocket server для real-time updates
- **message-queue/** - RabbitMQ manager для async tasks
- **intelligent-gateway/** - AI-powered gateway (архитектура готова, 495 строк README)
- **secrets-manager/** - Vault integration для secrets
- **docker-management/** - Docker orchestration
- **mcp-server/** - MCP protocol для collective agents
- **process_mining_service/** - Process mining analytics

---

### ❌ To Be Created

- **kubernetes/** - K8s manifests (пустые папки)
- **observability/** - Distributed tracing + centralized logging

---

## 🗂️ Архивировано

### _archive_empty_patterns/
Содержит пустые папки паттернов (0 строк кода):
- reliability/ - circuit breaker, retry patterns, etc.
- performance/ - caching, pooling, etc.
- scalability/ - scaling patterns

**Решение:** Заархивировано, создадим когда понадобится или используем готовые библиотеки.

---

## 🏗️ Архитектура

Все сервисы - это микросервисы, общающиеся через:
- **EventBus** - event-driven messaging
- **HTTP/REST** - синхронные вызовы
- **Shared Library** (`/shared/`) - общий код (database, auth, cache, integrations)

### Принципы:
- Каждый сервис в своем Docker контейнере
- Изоляция и независимость
- Плоская структура для простоты (15-20 сервисов)
- Shared библиотека с плоской структурой (оптимально для 127 импортов)

---

## 🚀 Приоритеты развития

### Tier 0 - КРИТИЧНО
1. ✅ **vector-db/** (Qdrant) - ГОТОВО!
2. **notification-service/** - 4-6 часов
3. **realtime-websocket/** - 6-8 часов
4. **message-queue/** - 4-6 часов

### Tier 1 - ПОЛЕЗНО (для production)
5. **secrets-manager/** (Vault) - для production безопасности
6. **kubernetes/** manifests - если деплоим в K8s
7. **intelligent-gateway/** - AI-powered routing (если нужен)

### Tier 2 - ОПЦИОНАЛЬНО
8. **observability/** - distributed tracing + logging
9. **process_mining_service/** - analytics
10. **mcp-server/** - специфичный use case

---

## 📚 Документация

Каждый сервис содержит собственный README с:
- Описанием функциональности
- API endpoints (если есть)
- Конфигурацией
- Примерами использования

См. README в папках отдельных сервисов.

---

## 🔗 Связь с другими модулями

**Infrastructure** работает с:
- `/shared/` - общая библиотека (database, auth, cache, integrations)
- `/platform-services/` - бизнес-сервисы (BIA, Risk, Planning, etc.)
- `/intelligent-core/` - AI компоненты (workflow intelligence, learning, etc.)

**Коммуникация:**
- EventBus (event-driven)
- HTTP/REST (синхронные вызовы)
- Shared library (code reuse)

---

## ⚡ Производительность

**Shared Library:**
- Плоская структура (1-2 уровня вложенности)
- Оптимизировано для 127 импортов
- 20-30% быстрее чем глубокая вложенность

**Infrastructure:**
- Микросервисная архитектура
- Docker изоляция
- EventBus для async communication
- Service discovery для health checks

---

Для вопросов и улучшений см. документацию отдельных сервисов.
