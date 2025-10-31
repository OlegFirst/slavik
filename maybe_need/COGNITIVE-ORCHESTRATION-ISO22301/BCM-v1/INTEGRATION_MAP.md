# 🔗 КАРТА ИНТЕГРАЦИЙ И ВЗАИМОСВЯЗЕЙ

## ⚠️ КРИТИЧНО: Сохранить работающие связи!

### 📊 Текущие рабочие интеграции:

## 1. **Orchestrator** - центральный хаб
```
Orchestrator взаимодействует с:
├── Document Processor (обработка документов)
├── BIA Engine (бизнес-анализ)
├── Compliance Checker (проверка соответствия)
├── Notification Service (уведомления)
├── AI Services (AI решения)
└── Odoo Modules (BCM модули)
```

### Рабочие связи Orchestrator:
- **→ Document Processor**: Отправляет документы на обработку
- **← Document Processor**: Получает результаты анализа
- **→ BIA Engine**: Запрашивает бизнес-анализ
- **← BIA Engine**: Получает метрики воздействия
- **↔ Event Bus**: Публикует и подписывается на события

## 2. **Document Processor** - обработчик документов
```
Document Processor связан с:
├── Orchestrator (получает задачи)
├── Compliance Checker (проверка документов)
├── AI Services (NLP анализ)
└── Storage (хранение)
```

### Версии Document Processor (нужно объединить):
1. `/BCM-v1/backend/document_processor/` - основная логика (17KB main.py)
2. `/BCM-v1/services/document_processor/` - сервисная версия (22KB app.py)
3. `/BCM-v1/core/odoo-18.0/services/document_processor/` - Odoo интеграция
4. `/platform-framework/adapters/document-processor/` - адаптер

## 3. **Event Bus** - центральная шина событий
```
ВСЕ компоненты общаются через Event Bus:
├── События оркестрации
├── События документов
├── События compliance
├── События уведомлений
└── События AI решений
```

### Критические события:
- `document.processed` - документ обработан
- `compliance.checked` - проверка завершена
- `bia.calculated` - BIA расчет выполнен
- `workflow.started` - workflow запущен
- `task.completed` - задача выполнена

## 4. **API Gateway** - точка входа
```
API Gateway маршрутизирует к:
├── Orchestrator API
├── Document API
├── Compliance API
├── BIA API
└── Notification API
```

## 5. **Важные интеграции для сохранения:**

### Odoo ↔ Микросервисы
- Odoo модули используют микросервисы через API Gateway
- Микросервисы обновляют данные в Odoo через XML-RPC

### AI Services ↔ Business Logic
- AI Orchestrator принимает решения
- Business сервисы выполняют действия
- Результаты возвращаются для обучения

### Monitoring ↔ All Services
- Prometheus собирает метрики
- Grafana визуализирует
- Health checks для всех сервисов

## 🚨 ЧТО НЕЛЬЗЯ ЛОМАТЬ:

1. **Event Bus подписки** - все сервисы слушают события
2. **API endpoints** - внешние системы используют их
3. **Database connections** - связи с PostgreSQL/MongoDB
4. **Message Queue** - RabbitMQ очереди
5. **WebSocket connections** - real-time обновления

## 📈 КАК УЛУЧШИТЬ ИНТЕГРАЦИЮ:

### 1. Унификация через Event Bus
```python
# Вместо прямых вызовов:
document_processor.process(doc)  # ❌

# Использовать события:
event_bus.publish('document.process', doc)  # ✅
```

### 2. Service Registry для discovery
```python
# Вместо хардкода:
url = "http://localhost:8082"  # ❌

# Использовать registry:
service = registry.get_service('bia_engine')  # ✅
url = service.endpoint
```

### 3. Config Service для конфигураций
```python
# Вместо локальных config:
config = {'timeout': 30}  # ❌

# Централизованный config:
config = config_service.get('document_processor')  # ✅
```

## 🔄 ПЛАН МИГРАЦИИ С СОХРАНЕНИЕМ СВЯЗЕЙ:

### Шаг 1: Document Processor
1. Объединить все версии в один модуль
2. Сохранить все API endpoints
3. Сохранить Event Bus события
4. Добавить недостающие интеграции

### Шаг 2: Усилить Event Bus
1. Добавить все события в каталог
2. Создать схемы событий
3. Добавить retry логику
4. Добавить dead letter queue

### Шаг 3: Service Registry
1. Зарегистрировать все сервисы
2. Добавить health checks
3. Автоматическое обнаружение
4. Балансировка нагрузки

## 📝 Критические зависимости:

```yaml
Document Processor:
  requires:
    - Event Bus
    - Storage Service
    - AI Services (optional)
  provides:
    - Document analysis API
    - Processing events

Orchestrator:
  requires:
    - Event Bus
    - Service Registry
    - All microservices
  provides:
    - Workflow orchestration
    - Task management
    - Scenario execution

BIA Engine:
  requires:
    - Database
    - Event Bus
  provides:
    - Impact analysis
    - Risk calculations

Compliance Checker:
  requires:
    - Document Processor
    - Rule Engine
  provides:
    - Compliance reports
    - Validation results
```

---

**ВАЖНО**: При переносе компонентов проверять что все зависимости сохранены!