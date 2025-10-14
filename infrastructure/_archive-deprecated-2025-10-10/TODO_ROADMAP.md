# TODO Roadmap - Infrastructure Platform
**Дата создания:** 11 октября 2025
**Статус:** Приоритетные задачи после анализа

---

## ✅ Завершено (Priority 1 - Частично)

### Исправлены конфликты портов
- ✅ **GitHub Integration:** 8001 → 8085 (уже в коде)
- ✅ **Real-time WebSocket:** 8050 → 8053 (исправлено)
- ✅ **DevOps Agent API:** 8060 → 8061 (исправлено)

---

## 🔴 Priority 1 - КРИТИЧНО (Эта неделя)

### 1. Создать .env.example для всех сервисов ⏳ IN PROGRESS
**Компоненты:** 8 AI Office сервисов + 3 integration
**Статус:** В процессе
**Задачи:**
- [ ] MIO Manager .env.example
- [ ] DB Intelligence .env.example
- [ ] AI Event Manager .env.example
- [ ] Analytics Specialist .env.example
- [ ] DevOps Agent .env.example
- [ ] Agent Router .env.example
- [ ] Project Agent .env.example
- [ ] Orchestrator .env.example
- [ ] GitHub Integration .env.example
- [ ] Balancer Service .env.example
- [ ] Policy Engine .env.example

### 2. Обновить service-catalog.yaml
**Файл:** `/infrastructure/runtime/service-discovery/service-catalog.yaml`
**Статус:** Pending
**Изменения:**
- [ ] GitHub Integration: port 8085
- [ ] Real-time WebSocket: port 8053
- [ ] DevOps Agent API: port 8061
- [ ] Analytics Specialist: port 8051 (стандартизировать)
- [ ] Добавить policy-engine (9091)
- [ ] Добавить balancer-service (9092 metrics)

### 3. Запустить и протестировать core services
**Сервисы для запуска:**
- [ ] MIO Manager (8046) - EYES Observatory
- [ ] DB Intelligence (8050) - Database monitoring
- [ ] AI Event Manager (8055) - Event analysis
- [ ] Analytics Specialist (8051) - Platform intelligence
- [ ] DevOps Agent (8058) - Infrastructure & compliance

**Проверки:**
- [ ] Все сервисы успешно стартуют
- [ ] EventBus соединения работают
- [ ] Prometheus метрики доступны
- [ ] Health endpoints отвечают
- [ ] Интеграции между сервисами функционируют

---

## 🟡 Priority 2 - ВАЖНО (2-3 недели)

### 4. Добавить Prometheus метрики (4 компонента без метрик)
**Компоненты:**
- [ ] Analytics Specialist (8051) - добавить /metrics endpoint
- [ ] DevOps Agent (8058) - добавить prometheus_client
- [ ] Agent Router - добавить метрики
- [ ] Project Agent (8060) - добавить метрики
- [ ] Orchestrator - добавить метрики

**Метрики для добавления:**
```python
# Стандартные метрики для каждого сервиса
- service_up (Gauge)
- requests_total (Counter)
- request_duration_seconds (Histogram)
- errors_total (Counter)
- tasks_processed_total (Counter) # для agents
- integration_calls_total (Counter)
```

### 5. Завершить EventBus интеграцию
**Компоненты без интеграции:**
- [ ] Agent Router - добавить _shared/eventbus_helper
- [ ] Orchestrator - добавить EventBus клиент

**Задачи:**
- [ ] Создать EventBusHelper для Agent Router
- [ ] Создать EventBusHelper для Orchestrator
- [ ] Зарегистрировать capabilities
- [ ] Подписаться на релевантные события
- [ ] Тестирование интеграции

### 6. Тестирование policy-engine API
**Статус:** Production Ready, требует тестирования
**Задачи:**
- [ ] Unit tests для PolicyEngine
- [ ] Integration tests с EventBus
- [ ] API endpoint tests (13 endpoints)
- [ ] Load testing
- [ ] Валидация YAML политик
- [ ] Hot reload проверка

### 7. Тестирование balancer-service Phase 2.1
**Статус:** MVP 2.4.0, требует тестирования
**Задачи:**
- [ ] Проверка SystemBalancer (GLOBAL BRAIN)
- [ ] Проверка ImpactEvidenceTracker (RATIONAL)
- [ ] Проверка PredictiveROIOptimizer (INTUITIVE+PRAGMATIC)
- [ ] Проверка ThreeDimensionalBalancer (3D BALANCE)
- [ ] Тестирование infrastructure-aware logic
- [ ] EventBus subscriptions (7 событий)
- [ ] Emergency mode проверка
- [ ] Интеграция с AI Event Manager

---

## 🟢 Priority 3 - ЖЕЛАТЕЛЬНО (1-2 месяца)

### 8. Создать unified docker-compose.yml для AI Office
**Файл:** `/infrastructure/AI-office-infrastructure/docker-compose.yml`
**Статус:** Planned
**Содержание:**
- [ ] Все 8 AI Office сервисов
- [ ] EventBus (Redis)
- [ ] PostgreSQL (Supabase ref)
- [ ] Prometheus + Grafana
- [ ] Health checks
- [ ] Resource limits
- [ ] Networks configuration
- [ ] Volumes для persistence

### 9. Grafana Dashboards
**Создать dashboards для:**
- [ ] AI Office Overview (все 8 сервисов)
- [ ] MIO Manager EYES (Observatory metrics)
- [ ] Event-Driven Architecture (EventBus flow)
- [ ] Policy Engine (governance decisions)
- [ ] Balancer Service (3D balancing)
- [ ] Infrastructure Health

### 10. CI/CD Integration (Tools)
**Инструменты для интеграции:**
- [ ] Module Scanner - документация check
- [ ] Dependency Validator - dependency conflicts
- [ ] Security Scanner - безопасность кода
- [ ] API Mapper - API regression check
- [ ] Event Catalog Generator - event schema validation

**GitHub Actions workflows:**
```yaml
# .github/workflows/infrastructure-checks.yml
- Module Scanner (on PR)
- Dependency Validator (on PR)
- Security Scanner (daily)
- API Docs Generator (on merge to main)
```

### 11. Migration Guides
**Создать документацию:**
- [ ] **PORT_MIGRATION_GUIDE.md** - как мигрировать на новые порты
- [ ] **EVENTBUS_MIGRATION_GUIDE.md** - как добавить EventBus
- [ ] **PROMETHEUS_MIGRATION_GUIDE.md** - как добавить метрики
- [ ] **TESTING_GUIDE.md** - стандарты тестирования
- [ ] **DEPLOYMENT_GUIDE.md** - процесс деплоя

---

## 📊 Дополнительные задачи (Backlog)

### Documentation
- [ ] Создать Architecture Decision Records (ADRs)
- [ ] API versioning strategy
- [ ] Event schema registry
- [ ] Runbook для каждого сервиса

### Infrastructure
- [ ] Kubernetes manifests (альтернатива docker-compose)
- [ ] Helm charts
- [ ] Terraform для cloud resources
- [ ] Service Mesh оценка (Istio/Linkerd)

### Observability
- [ ] Distributed tracing (Jaeger/Tempo)
- [ ] Log aggregation enhancement
- [ ] APM integration (возможно)
- [ ] Alert rules refinement

### Security
- [ ] Secrets rotation strategy
- [ ] mTLS между сервисами
- [ ] RBAC для EventBus
- [ ] Audit logging enhancement

### Performance
- [ ] Load testing framework
- [ ] Performance benchmarks
- [ ] Caching strategy review
- [ ] Database query optimization

### Developer Experience
- [ ] Local development setup guide
- [ ] Hot reload для всех сервисов
- [ ] Debug configuration (VS Code)
- [ ] Onboarding documentation

---

## 🎯 Метрики успеха

### По завершении Priority 1:
- ✅ 0 конфликтов портов
- ✅ Все сервисы имеют .env.example
- ✅ service-catalog.yaml актуален
- ✅ 5/8 core services запущены и работают

### По завершении Priority 2:
- ✅ 100% Prometheus coverage (8/8)
- ✅ 100% EventBus integration (8/8)
- ✅ Policy Engine протестирован (100+ tests)
- ✅ Balancer Service validated (Phase 2.1)

### По завершении Priority 3:
- ✅ Unified deployment (docker-compose)
- ✅ Complete observability (Grafana)
- ✅ CI/CD automation (tools integrated)
- ✅ Migration guides (5 guides)

---

## 📅 Timeline (Ориентировочно)

**Week 1 (Priority 1):**
- Days 1-2: .env.example + service-catalog.yaml
- Days 3-5: Запуск и тестирование core services
- Days 6-7: Фиксы и стабилизация

**Weeks 2-3 (Priority 2):**
- Week 2: Prometheus метрики + EventBus integration
- Week 3: Policy Engine + Balancer testing

**Weeks 4-8 (Priority 3):**
- Week 4-5: Docker Compose + Grafana
- Week 6-7: CI/CD integration
- Week 8: Migration guides + Documentation

---

## 📝 Заметки

### Технический долг
- Некоторые компоненты имеют смешанные async/sync паттерны
- Database connection pooling нуждается в review
- Error handling стандартизация требуется

### Решения отложены
- **MCP Server Integration:** Partisia blockchain - low priority
- **VS Code Extension:** Development tooling - backlog
- **Auto-generated configs regeneration:** Нужна документация процесса

### Зависимости между задачами
```
Priority 1.3 (Запуск services)
    ↓
Priority 2.4 (Prometheus метрики) - нужны running services
    ↓
Priority 3.9 (Grafana dashboards) - нужны метрики
```

---

**Последнее обновление:** 11 октября 2025
**Следующий review:** После завершения Priority 1

Используйте этот roadmap для отслеживания прогресса!
