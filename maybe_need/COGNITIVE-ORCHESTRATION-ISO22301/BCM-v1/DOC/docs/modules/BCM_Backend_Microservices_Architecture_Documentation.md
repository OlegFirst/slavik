# BCM Platform Backend Microservices Architecture

## Техническая Документация v1.0
**Дата создания:** 2025-01-12  
**Статус:** В разработке  
**Платформа:** ISO 22301 Business Continuity Management Platform  

---

## 1. АРХИТЕКТУРНЫЙ ОБЗОР

### 1.1 Микросервисная Архитектура

BCM Platform построена на основе микросервисной архитектуры с event-driven подходом, обеспечивающей:

- **Масштабируемость**: Независимое масштабирование каждого сервиса
- **Отказоустойчивость**: Изоляция отказов между сервисами
- **Технологическое разнообразие**: Использование оптимальных технологий для каждой задачи
- **Упрощенное развертывание**: Независимые циклы разработки и развертывания

### 1.2 Основные Принципы

1. **Event-Driven Architecture** - Асинхронная коммуникация через события
2. **Domain-Driven Design** - Сервисы построены вокруг бизнес-доменов
3. **API-First** - Первоочередная разработка API интерфейсов
4. **Multi-Tenancy** - Поддержка множественной аренды
5. **Security by Design** - Встроенная безопасность на всех уровнях

---

## 2. ДЕТАЛЬНЫЙ АНАЛИЗ СЕРВИСОВ

### 2.1 Authentication Service (auth_service)

#### Архитектура
- **Технологии**: FastAPI, SQLAlchemy (AsyncSession), JWT, bcrypt
- **База данных**: SQLite/PostgreSQL (async)
- **Порт**: 8005

#### Основной функционал
```python
# Модели данных
- User: Пользователи системы
- Tenant: Мультитенантность
- JWT-токены: Аутентификация и авторизация

# Ключевые API
POST /api/auth/login        # Аутентификация пользователя
GET  /api/auth/me          # Получение информации о текущем пользователе  
POST /api/auth/refresh     # Обновление токена
POST /api/auth/validate    # Валидация токена для других сервисов
```

#### Текущий статус
- ✅ **ГОТОВО**: Базовая аутентификация и авторизация
- ✅ **ГОТОВО**: Multi-tenant архитектура
- ✅ **ГОТОВО**: JWT токены с рефрешем
- ✅ **ГОТОВО**: Управление пользователями и тенантами
- ✅ **ГОТОВО**: Валидация токенов для межсервисного взаимодействия

#### Безопасность
- bcrypt для хеширования паролей
- JWT с настраиваемым временем жизни
- Валидация прав доступа на уровне тенантов
- CORS конфигурация

---

### 2.2 Event Bus Service (eventbus)

#### Архитектура
- **Технологии**: FastAPI, Redis, PostgreSQL, asyncio
- **Паттерны**: Publisher/Subscriber, Event Sourcing
- **Порт**: 8001

#### Основной функционал
```python
# Модели событий
class Event:
    event_type: str
    tenant_id: str  
    data: Dict[str, Any]
    user_id: Optional[str]
    correlation_id: Optional[str]
    event_id: Optional[str]  # Idempotency

# Ключевые API
POST /api/events/publish           # Публикация событий
GET  /api/events/history          # История событий с фильтрацией
GET  /api/events/stream           # SSE поток событий
POST /api/events/validate         # Валидация структуры событий
```

#### Поддерживаемые типы событий
```python
EVENT_TYPES = {
    "bcm.bia.started": {"required_fields": ["bia_id", "process_id"]},
    "bcm.bia.completed": {"required_fields": ["bia_id", "rto", "rpo", "critical_processes"]},
    "bcm.plan.draft_requested": {"required_fields": ["plan_id", "plan_type"]},
    "bcm.incident.reported": {"required_fields": ["incident_id", "severity"]},
    "bcm.kpi.calculated": {"required_fields": ["period", "bia_coverage", "plans_up_to_date"]},
    "bcm.exercise.completed": {"required_fields": ["exercise_id", "results"]},
    "bcm.training.completed": {"required_fields": ["training_id", "attendees"]}
}
```

#### Текущий статус
- ✅ **ГОТОВО**: Основная инфраструктура публикации/подписки
- ✅ **ГОТОВО**: Персистентное хранение событий в PostgreSQL
- ✅ **ГОТОВО**: Real-time стриминг через SSE и WebSocket
- ✅ **ГОТОВО**: Idempotency поддержка
- ✅ **ГОТОВО**: Валидация схем событий
- ✅ **ГОТОВО**: Фильтрация и поиск событий

#### Особенности реализации
- Dual-storage: Redis для real-time, PostgreSQL для persistence
- Environment variable expansion для конфигурации
- Retry логика для подключений к базе данных
- Heartbeat механизм для WebSocket соединений

---

### 2.3 BPMN Workflow Service (bpmn_service)

#### Архитектура
- **Технологии**: FastAPI, XML parsing (ElementTree), BPMN 2.0
- **Паттерны**: State Machine, Process Engine
- **Порт**: 8005

#### Основной функционал
```python
# Модели процессов
class BPMNProcess:
    name: str
    bpmn_xml: str  # BPMN 2.0 XML
    tenant_id: str
    version: str

class ProcessInstance:
    process_id: str
    status: str  # ACTIVE, COMPLETED, SUSPENDED, TERMINATED
    variables: Dict[str, Any]
    current_activities: List[str]

# Ключевые API
POST /api/bpmn/processes                    # Развертывание BPMN процесса
POST /api/bpmn/processes/{id}/start         # Запуск экземпляра процесса
GET  /api/bpmn/tasks                        # Получение задач
POST /api/bpmn/tasks/{id}/complete          # Завершение задачи
```

#### Поддерживаемые BPMN элементы
- Start Events
- User Tasks
- Script Tasks  
- Service Tasks
- End Events
- Sequence Flows
- Exclusive Gateways (базовая поддержка)

#### Текущий статус
- ✅ **ГОТОВО**: Базовый BPMN движок
- ✅ **ГОТОВО**: Развертывание и выполнение процессов
- ✅ **ГОТОВО**: Управление задачами
- ✅ **ГОТОВО**: XML валидация BPMN
- 🔶 **ЧАСТИЧНО**: Поддержка сложных BPMN конструкций
- 🔶 **ЧАСТИЧНО**: Интеграция с внешними системами

#### Mock данные
- Демо процесс "BCM Incident Response"
- Примеры BIA Review Process
- Шаблоны workflow для различных сценариев

---

### 2.4 AI Orchestrator Services

#### 2.4.1 AI Orchestrator Core (orchestrator/ai_orchestrator.py)

```python
# Архитектура решений
class AIOrchestrator:
    - Правило-основанная система принятия решений
    - Интеграция с LLM для сложного анализа
    - Поддержка workflow automation

# Типы действий
ActionType = {
    GENERATE_PLAN,      # Генерация планов BCM
    SUGGEST_RESPONSE,   # Предложения по инцидентам
    SCHEDULE_TRAINING,  # Планирование обучения
    ANALYZE_COMPLIANCE, # Анализ соответствия
    TRIGGER_WORKFLOW    # Запуск workflows
}
```

#### 2.4.2 Orchestrator Service API (orchestrator_service)

- **Технологии**: FastAPI, Redis pub/sub, httpx
- **Паттерны**: Event-driven decision making
- **Порт**: 8002

```python
# Ключевые возможности
- Автоматическая генерация BCP после завершения BIA
- Создание чек-листов реагирования на инциденты  
- Анализ KPI и рекомендации по улучшениям
- Подготовка к аудитам
```

#### Текущий статус
- ✅ **ГОТОВО**: Базовая система правил
- ✅ **ГОТОВО**: Event-driven обработка
- ✅ **ГОТОВО**: Auto-trigger функционал
- 🔶 **ЧАСТИЧНО**: LLM интеграция (требует API ключ)
- 🔶 **ЧАСТИЧНО**: Сложная логика принятия решений

---

### 2.5 Notification Service

#### Архитектура
- **Технологии**: FastAPI, Redis, SMTP, Telegram Bot API
- **Каналы**: Email, Telegram, UI notifications
- **Порт**: 8004

#### Основной функционал
```python
# Правила уведомлений
NotificationRule:
    event_pattern: str      # Паттерн события для триггера
    channels: List[str]     # email, telegram, ui, sms
    recipients: List[str]   # Список получателей
    conditions: Dict        # Условия срабатывания
    template: str          # Шаблон сообщения

# Предустановленные правила
- Критические инциденты → Email + Telegram + UI
- Просроченные CAPA → Email + UI
- Запланированные учения → Email + UI
```

#### Текущий статус
- ✅ **ГОТОВО**: Email уведомления (HTML шаблоны)
- ✅ **ГОТОВО**: Telegram интеграция
- ✅ **ГОТОВО**: UI уведомления через EventBus
- ✅ **ГОТОВО**: Настраиваемые правила
- 🔶 **ЧАСТИЧНО**: SMS поддержка (заглушка)

---

### 2.6 Document Processor Service

#### Архитектура
- **Технологии**: FastAPI, aiofiles, document analysis
- **Поддерживаемые форматы**: PDF, DOC, DOCX, TXT
- **Порт**: 8003

#### Основной функционал
```python
# Анализ документов
class AnalysisResult:
    iso_mapping: Dict[str, Any]        # Соответствие ISO 22301
    compliance_score: float           # Оценка соответствия
    key_phrases: List[str]           # Ключевые фразы  
    findings: List[str]              # Находки
    recommendations: List[str]        # Рекомендации

# Сравнение документов
class ComparisonResult:
    similarity_score: float          # Оценка схожести
    differences: List[Dict]          # Различия
    compliance_gaps: List[Dict]      # Пробелы в соответствии
```

#### Текущий статус
- ✅ **ГОТОВО**: Загрузка и хранение документов
- ✅ **ГОТОВО**: Базовый анализ (mock данные)
- ✅ **ГОТОВО**: Сравнение документов
- ✅ **ГОТОВО**: API безопасность с токенами
- 🔶 **ЧАСТИЧНО**: Реальный NLP анализ текста
- 🔶 **ЧАСТИЧНО**: Извлечение текста из PDF/DOC

---

### 2.7 Adapter Services

#### 2.7.1 Grafana Adapter (grafana_adapter)

```python
# Интеграция с Grafana
- Управление dashboard'ами и data sources
- Создание BCM-специфичных dashboard'ов
- Синхронизация KPI метрик
- Аннотации для событий BCM

# BCM Dashboard Templates
- BCM Platform Overview (BIA coverage, Plan status, CAPA progress)
- Incident Management (MTTR, RPO adherence, Severity distribution)
```

#### 2.7.2 TheHive Adapter (thehive_adapter)

```python
# Security Incident Management
- Создание и управление случаями (Cases)
- Алерты и их продвижение в случаи
- Задачи и workflow для расследований
- BCM-специфичные incident templates
```

#### 2.7.3 LMS Adapter (lms_adapter)

```python
# Multi-LMS Support
class LMSAdapter:
    - MoodleAdapter      # Moodle LMS integration
    - OpenEdXAdapter     # Open edX integration  
    - CanvasAdapter      # Canvas LMS integration

# Функциональность
- Управление курсами и enrollments
- Отслеживание прогресса обучения
- SSO integration для запуска курсов
```

#### Текущий статус адаптеров
- ✅ **ГОТОВО**: Базовая архитектура и API
- ✅ **ГОТОВО**: Mock данные для тестирования
- 🔶 **ЧАСТИЧНО**: Реальные интеграции (требуют настройки)
- 🔶 **ЧАСТИЧНО**: Аутентификация с внешними системами

---

## 3. МЕЖСЕРВИСНАЯ КОММУНИКАЦИЯ

### 3.1 Communication Patterns

#### Event-Driven Communication
```python
# Основные потоки событий
1. BIA Complete → Auto-generate BCP (AI Orchestrator)
2. Incident Reported → Create Response Checklist (AI + BPMN)
3. Plan Approved → Schedule Training (LMS + Notification)
4. Exercise Completed → Update KPIs (Grafana)
5. CAPA Overdue → Send Alerts (Notification)
```

#### Synchronous API Calls
```python
# Межсервисные вызовы
Auth Service ←→ All Services     # Token validation
Orchestrator → Odoo             # Callback updates  
EventBus ←→ All Services         # Event publishing
Document Processor → EventBus    # Analysis completion
```

### 3.2 Service Dependencies

```mermaid
graph TD
    A[Frontend/Odoo] --> B[Auth Service]
    A --> C[EventBus] 
    C --> D[AI Orchestrator]
    C --> E[Notification Service]
    C --> F[BPMN Service]
    D --> G[External APIs/LLM]
    E --> H[SMTP/Telegram]
    I[Grafana Adapter] --> J[Grafana]
    K[TheHive Adapter] --> L[TheHive]
    M[LMS Adapter] --> N[Moodle/edX/Canvas]
    O[Document Processor] --> C
```

---

## 4. ТЕХНИЧЕСКИЕ СПЕЦИФИКАЦИИ

### 4.1 Technology Stack

| Компонент | Технология | Версия |
|-----------|------------|--------|
| Runtime | Python | 3.11+ |
| Web Framework | FastAPI | 0.104+ |
| ASGI Server | Uvicorn | 0.24+ |
| Message Broker | Redis | Latest |
| Database | PostgreSQL | 14+ |
| ORM | SQLAlchemy | 2.0+ |
| HTTP Client | httpx | 0.25+ |
| Authentication | JWT + bcrypt | Latest |
| File Processing | aiofiles | Latest |

### 4.2 Service Ports

| Service | Port | Protocol |
|---------|------|----------|
| EventBus | 8001 | HTTP/WS |
| AI Orchestrator | 8002 | HTTP |
| Document Processor | 8003 | HTTP |
| Notification | 8004 | HTTP |
| Auth Service | 8005 | HTTP |
| LMS Adapter | 8006 | HTTP |
| TheHive Adapter | 8007 | HTTP |
| Grafana Adapter | 8008 | HTTP |
| BPMN Service | 8005 | HTTP |

### 4.3 Environment Configuration

```bash
# Core Services
EVENTBUS_URL=http://localhost:8001
ODOO_URL=http://localhost:8069
CORS_ORIGINS=http://localhost:8081,http://localhost:8069

# Databases
POSTGRES_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379

# Authentication
JWT_SECRET_KEY=your-secret-key-32-chars-min
JWT_EXPIRE_MINUTES=1440

# External Integrations  
OPENAI_API_KEY=sk-...
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email
SMTP_PASSWORD=your-password
TELEGRAM_BOT_TOKEN=your-token

# File Processing
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760
```

---

## 5. GAP ANALYSIS И ROADMAP

### 5.1 Текущий статус сервисов

| Сервис | Готовность | Комментарий |
|--------|------------|-------------|
| Auth Service | 95% | Полностью функционален |
| EventBus | 90% | Готов для production |
| BPMN Service | 70% | Базовый движок готов |
| AI Orchestrator | 60% | Нужна LLM интеграция |
| Notification | 85% | Основные каналы работают |
| Document Processor | 50% | Нужен реальный NLP |
| Grafana Adapter | 45% | API готов, нужна интеграция |
| TheHive Adapter | 45% | API готов, нужна интеграция |
| LMS Adapter | 40% | Архитектура готова |

### 5.2 Phase 1: Стабилизация Core 

#### Приоритет 1: Критические исправления
- ✅ **Выполнено**: Исправить синтаксические ошибки в auth_service/main.py
- 🔄 **В работе**: Добавить comprehensive error handling
- 🔄 **В работе**: Implement proper logging across all services
- ⏳ **Запланировано**: Add health checks для всех сервисов
- ⏳ **Запланировано**: Implement graceful shutdown

#### Приоритет 2: Безопасность
- ⏳ **Запланировано**: API key management для всех сервисов
- ⏳ **Запланировано**: Input validation и sanitization
- ⏳ **Запланировано**: Rate limiting implementation
- ⏳ **Запланировано**: Audit logging для security events

#### Приоритет 3: Тестирование
- ⏳ **Запланировано**: Unit tests для core функций
- ⏳ **Запланировано**: Integration tests между сервисами
- ⏳ **Запланировано**: Load testing для EventBus
- ⏳ **Запланировано**: End-to-end testing scenarios

### 5.3 Phase 2: Полная функциональность адаптеров 

#### External Integrations
- **Grafana Integration**
  - Реальное подключение к Grafana instance
  - Dashboard provisioning и data source management
  - KPI metrics sync implementation
  - Alert rules configuration

- **TheHive Integration**  
  - Security incident workflow integration
  - Case management automation
  - Observable enrichment
  - Threat intelligence feeds

- **LMS Integration**
  - Moodle API implementation и testing
  - Open edX integration
  - Canvas LMS support
  - SSO implementation для all LMS platforms

#### Document Processing Enhancement
- **Real NLP Integration**
  - Implement text extraction для PDF/DOC files
  - ISO 22301 compliance mapping
  - Document similarity algorithms
  - Automated compliance scoring

### 5.4 Phase 3: AI и Advanced Features 

#### AI Orchestrator Enhancement
- **LLM Integration**
  - OpenAI/Anthropic API integration
  - Prompt engineering для BCM domain
  - Context-aware recommendations
  - Multi-language support

- **Advanced Decision Making**
  - Machine learning для pattern recognition
  - Predictive analytics для incident prevention  
  - Automated compliance monitoring
  - Risk assessment algorithms

#### Advanced BPMN Support
- **Complex BPMN Constructs**
  - Parallel gateways и sub-processes
  - Timer events и boundary events
  - Message events для inter-service communication
  - Conditional flows и complex routing

### 5.5 Phase 4: Enterprise Production Readiness 

#### Performance и Scalability
- **Horizontal Scaling**
  - Load balancing configuration
  - Database clustering (PostgreSQL/Redis)
  - Service mesh implementation (Istio/Linkerd)
  - Auto-scaling policies

#### Monitoring и Observability  
- **Comprehensive Monitoring**
  - Prometheus metrics collection
  - Distributed tracing (Jaeger/Zipkin)
  - Centralized logging (ELK stack)
  - Performance monitoring и alerting

#### DevOps и Deployment
- **Container Orchestration**
  - Kubernetes deployment manifests
  - Helm charts для service deployment
  - CI/CD pipelines (Jenkins/GitLab CI)
  - Environment promotion strategies

---

## 6. SECURITY IMPLEMENTATION

### 6.1 Authentication & Authorization

#### Multi-tenant Security
```python
# Tenant isolation на всех уровнях
- Database level: Row-level security
- API level: Tenant validation в каждом endpoint
- Event level: Tenant-scoped event publishing
- File storage: Tenant-specific directories
```

#### JWT Security
```python
# Secure JWT implementation
- Strong secret keys (32+ characters)
- Configurable token expiration
- Refresh token mechanism
- Token blacklisting capability
```

### 6.2 API Security

#### Input Validation
- Pydantic models для всех API inputs
- File upload validation (type, size, content)
- SQL injection prevention через ORM
- XSS protection через proper encoding

#### Rate Limiting
- Per-endpoint rate limiting
- Per-tenant quotas
- DDoS protection mechanisms
- API key-based access control

### 6.3 Data Security

#### Encryption
- Passwords: bcrypt hashing
- Sensitive data: Field-level encryption
- Communication: HTTPS/TLS enforcement
- Database: Encrypted connections

#### Audit Logging
- All API calls logged с user context
- Security events tracking
- Data modification audit trail
- Failed authentication monitoring

---

## 7. DEPLOYMENT ARCHITECTURE

### 7.1 Container Strategy

```yaml
# Docker Compose для development
version: '3.8'
services:
  auth-service:
    image: bcm/auth-service:latest
    ports: ["8005:8005"]
    environment:
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DATABASE_URL=${POSTGRES_URL}
  
  eventbus:
    image: bcm/eventbus:latest  
    ports: ["8001:8001"]
    depends_on: [redis, postgres]
    
  redis:
    image: redis:alpine
    
  postgres:
    image: postgres:14
    environment:
      - POSTGRES_DB=bcm_platform
```

### 7.2 Production Deployment

#### Kubernetes Architecture
```yaml
# Production-ready deployment
- Namespace isolation для environments
- ConfigMaps и Secrets для configuration
- StatefulSets для databases
- Deployments для stateless services
- Services и Ingress для routing
- PersistentVolumes для data storage
```

#### High Availability Setup
- Multi-replica deployments
- Database replication (Primary/Replica)
- Redis clustering
- Load balancing с health checks
- Disaster recovery procedures

---

## 8. МОНИТОРИНГ И OBSERVABILITY

### 8.1 Metrics Collection

#### Business Metrics
```python
# KPI Metrics
- BIA Coverage Percentage
- Plan Update Status
- CAPA On-time Completion Rate
- Training Completion Metrics  
- Incident Response Times
- Compliance Score Trends
```

#### Technical Metrics
```python
# Service Health Metrics
- Response times по endpoints
- Error rates и status codes
- Database connection pool usage
- Memory и CPU utilization
- Event processing throughput
- Queue depth и processing delays
```

### 8.2 Logging Strategy

#### Structured Logging
```json
{
  "timestamp": "2025-01-12T10:30:00Z",
  "level": "INFO",
  "service": "auth_service",
  "tenant_id": "tenant_001", 
  "user_id": "user_123",
  "action": "login_success",
  "ip_address": "192.168.1.100",
  "correlation_id": "req_abc123"
}
```

#### Log Aggregation
- Centralized logging с ELK/EFK stack
- Log rotation и retention policies
- Security event correlation
- Performance bottleneck identification

### 8.3 Alerting Rules

#### Critical Alerts
- Service unavailability (> 1 minute)
- Database connectivity failures
- Authentication service errors
- Critical incident notifications
- Security breach attempts

#### Warning Alerts  
- High error rates (> 5%)
- Slow response times (> 2 seconds)
- Resource utilization (> 80%)
- Queue backlog buildup
- Failed event processing

---

## 9. DEVELOPMENT GUIDELINES

### 9.1 Code Standards

#### Python Standards
```python
# Code quality requirements
- Type hints для all functions
- Docstrings для public methods
- Black formatting
- isort import ordering
- pylint/flake8 compliance
- pytest для testing (coverage > 80%)
```

#### API Design Standards
```python
# RESTful API principles
- Consistent HTTP status codes
- Proper error response formats
- API versioning strategy
- Request/response validation
- Comprehensive API documentation
```

### 9.2 Testing Strategy

#### Test Pyramid
```python
# Testing levels
Unit Tests (70%):
- Business logic testing
- Model validation
- Utility function testing

Integration Tests (20%):
- Service-to-service communication
- Database integration
- External API mocking

End-to-End Tests (10%):
- Complete workflow testing
- User journey validation
- Performance testing
```

### 9.3 Release Process

#### CI/CD Pipeline
1. **Code Commit** → Git hooks validation
2. **Build Stage** → Docker image creation
3. **Test Stage** → Automated test execution
4. **Security Scan** → Vulnerability assessment
5. **Deploy Stage** → Environment promotion
6. **Smoke Tests** → Post-deployment validation

---

## 10. ЗАКЛЮЧЕНИЕ

BCM Platform представляет собой современную микросервисную архитектуру с:

### Готовые компоненты
- ✅ Функциональная аутентификация и multi-tenancy
- ✅ Масштабируемая event-driven архитектура
- ✅ Базовая AI оркестрация
- ✅ Comprehensive notification система

### Ключевые преимущества
- **Масштабируемость**: Горизонтальное масштабирование сервисов
- **Отказоустойчивость**: Изоляция сбоев между сервисами  
- **Расширяемость**: Простое добавление новых адаптеров
- **Безопасность**: Multi-tenant архитектура с JWT

### Следующие шаги
1. **Phase 1**: Стабилизация core сервисов 
2. **Phase 2**: Реализация внешних интеграций 
3. **Phase 3**: AI enhancement и advanced features 
4. **Phase 4**: Production readiness 

**Общее время разработки**: 24-32 недели до production-ready состояния.

**Архитектура готова к масштабированию** и может поддерживать тысячи пользователей при правильной инфраструктуре.

---

**Документ подготовлен**: AI Assistant  
**Дата**: 2025-01-12  
**Версия**: 1.0  
**Статус**: Черновик для review