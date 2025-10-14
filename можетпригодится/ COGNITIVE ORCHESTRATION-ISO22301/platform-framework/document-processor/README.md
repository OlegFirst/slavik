# 📄 UNIFIED DOCUMENT PROCESSOR MODULE

## ✅ Объединение всех версий Document Processor

### 📊 Что объединяем:
1. `/BCM-v1/backend/document_processor/` - основная логика
2. `/BCM-v1/services/document_processor/` - сервисная версия
3. `/BCM-v1/core/odoo-18.0/services/document_processor/` - Odoo интеграция
4. `/platform-framework/adapters/document-processor/` - адаптер

### 🔗 Сохраненные интеграции:

#### API Endpoints (все сохранены):
```
# Backend версия:
POST /api/documents/upload        - загрузка документов
GET  /api/documents               - список документов
GET  /api/documents/{id}         - получить документ
POST /api/documents/analyze      - анализ документа
GET  /api/documents/analysis/{id} - результат анализа
POST /api/documents/compare      - сравнение документов
GET  /api/documents/stats        - статистика

# Service версия:
POST /upload                     - загрузка (упрощенная)
GET  /documents                  - список
GET  /documents/{id}            - документ
GET  /search                    - поиск
GET  /analytics/compliance      - compliance аналитика
DELETE /documents/{id}          - удаление

# Unified версия (комбинированная):
Все endpoints из обеих версий!
```

#### Event Bus события:
- `document.uploaded` - документ загружен
- `document.analyzed` - анализ завершен
- `document.compliance_checked` - compliance проверен
- `document.compared` - сравнение выполнено
- `document.deleted` - документ удален

### 📁 Структура модуля:

```
document-processor/
├── core/                       # Основная логика
│   ├── processor.py           # Главный процессор
│   ├── analyzer.py           # Анализатор документов
│   └── storage.py            # Хранение документов
│
├── validators/                # Валидаторы
│   ├── document_validator.py # Из backend версии
│   ├── compliance.py         # Compliance проверки
│   └── format_checker.py     # Проверка форматов
│
├── parsers/                   # Парсеры форматов
│   ├── pdf_parser.py         # PDF обработка
│   ├── docx_parser.py        # Word документы
│   ├── txt_parser.py         # Текстовые файлы
│   └── universal.py          # Универсальный парсер
│
├── api/                       # API слой
│   ├── main.py               # Объединенное API
│   ├── backend_routes.py     # Routes из backend
│   └── service_routes.py     # Routes из service
│
├── integrations/              # Интеграции
│   ├── event_bus.py          # Event Bus клиент
│   ├── odoo_bridge.py        # Odoo интеграция
│   ├── ai_connector.py       # AI сервисы
│   └── storage_adapter.py    # Storage адаптер
│
├── models/                    # Модели данных
│   ├── document.py           # Document модель
│   ├── analysis.py           # Analysis результаты
│   └── compliance.py         # Compliance модели
│
└── config/                    # Конфигурация
    ├── settings.py           # Настройки
    └── constants.py          # Константы
```

### 🔄 Взаимодействие с системой:

```python
# Event Bus интеграция
async def publish_document_event(event_type: str, data: dict):
    """Публикация событий документов"""
    await event_bus.publish(f"document.{event_type}", {
        "timestamp": datetime.utcnow(),
        "document_id": data.get("id"),
        "data": data
    })

# Service Registry
registry.register({
    "name": "document-processor",
    "version": "2.0.0",
    "endpoints": {
        "upload": "/api/documents/upload",
        "analyze": "/api/documents/analyze",
        "search": "/search"
    }
})

# Orchestrator интеграция
@event_bus.subscribe("workflow.document_needed")
async def handle_workflow_request(event):
    """Обработка запросов от Orchestrator"""
    document = await process_for_workflow(event.data)
    await event_bus.publish("document.ready_for_workflow", document)
```

### 🚀 Запуск:

```bash
# Standalone
python api/main.py

# Docker
docker build -t document-processor:latest .
docker run -p 8083:8083 document-processor:latest

# С Event Bus
EVENTBUS_URL=http://eventbus:8001 python api/main.py
```

### ⚙️ Конфигурация:

```yaml
document_processor:
  api:
    port: 8083
    workers: 4

  storage:
    type: "local"  # или "s3", "mongodb"
    path: "./uploads"

  limits:
    max_file_size: 10485760  # 10MB
    allowed_types:
      - application/pdf
      - application/msword
      - text/plain

  integrations:
    eventbus_url: "http://eventbus:8001"
    orchestrator_url: "http://orchestrator:8000"
    ai_service_url: "http://ai:8090"

  compliance:
    iso_22301: true
    gdpr: true
    custom_rules: "./rules/"
```

### 📊 Метрики:

- `document_processor_uploads_total` - всего загружено
- `document_processor_analysis_duration` - время анализа
- `document_processor_compliance_checks` - проверок compliance
- `document_processor_errors_total` - ошибок

### 🔒 Безопасность:

- API key аутентификация
- JWT токены для сессий
- Антивирусная проверка
- Валидация форматов
- Rate limiting

---

**Document Processor готов к интеграции со всей системой!**