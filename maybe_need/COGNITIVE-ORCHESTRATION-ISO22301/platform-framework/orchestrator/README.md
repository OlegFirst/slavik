# 🎯 UNIFIED ORCHESTRATOR MODULE

## ✅ Все компоненты orchestrator'а собраны в один модуль!

### Текущая структура (реальные файлы):

```
orchestrator/
│
├── 🧠 core/                      # Ядро оркестратора (перенесено)
│   ├── ai_orchestrator.py       # AI оркестрация
│   ├── workflow_handlers.py     # Обработчики workflow
│   ├── event_bus.py            # Интеграция с Event Bus
│   ├── api_endpoints.py        # API endpoints
│   └── bpmn_to_issues.py       # BPMN конвертер
│
├── 🤖 ai/                       # AI компоненты (из ai_orchestrator)
│   ├── main.py                 # Основной AI orchestrator (51KB!)
│   ├── ai_agent_router.py      # Роутер AI агентов
│   ├── model_router.py         # Роутинг между моделями
│   ├── anthropic_integration.py # Интеграция с Anthropic
│   └── prompts_library/        # Библиотека промптов
│
├── 📝 scenarios/                # Сценарии (из scenario_orchestrator)
│   ├── main.py                 # Основной движок сценариев
│   ├── app/                    # Приложение сценариев
│   │   ├── models/            # Модели данных
│   │   └── api/              # API сценариев
│   ├── src/                   # Исходники
│   └── generated_scenarios/   # Сгенерированные сценарии
│
├── 🎮 platform/                # Платформенная оркестрация
│   ├── main.py                # Platform orchestrator
│   └── Dockerfile             # Контейнер
│
├── 🔌 service/                 # Сервисный слой
│   ├── main.py               # Главный сервис
│   └── Dockerfile            # Контейнер сервиса
│
└── 📚 README.md              # Документация
```

## 🔄 Взаимодействие с системой

### Event Bus интеграция:
```python
# Подписка на события системы
orchestrator.subscribe([
    'service.registered',
    'task.created',
    'workflow.triggered',
    'alert.raised'
])

# Публикация событий
orchestrator.publish('workflow.completed', result)
```

### Service Registry:
```python
# Регистрация в реестре
registry.register({
    'name': 'orchestrator',
    'version': '2.0.0',
    'endpoints': ['http', 'websocket', 'grpc'],
    'capabilities': ['workflow', 'ai', 'scenarios']
})
```

### Config Service:
```python
# Получение конфигурации
config = config_service.get('orchestrator')
```

## 🎯 Основные возможности

1. **Оркестрация workflow** - BPMN, State Machines
2. **AI-driven оркестрация** - Интеллектуальная маршрутизация
3. **Сценарии** - Выполнение комплексных сценариев
4. **Мульти-протокол** - REST, WebSocket, gRPC
5. **Масштабируемость** - Горизонтальное масштабирование
6. **Отказоустойчивость** - Circuit breakers, retry logic
7. **Мониторинг** - Метрики, трейсинг, логи

## 📡 API Endpoints

### REST API:
- `POST /workflows` - Создать workflow
- `GET /workflows/{id}` - Статус workflow
- `POST /tasks` - Создать задачу
- `GET /scenarios` - Список сценариев
- `POST /scenarios/{id}/execute` - Выполнить сценарий

### WebSocket:
- `/ws/orchestrator` - Реал-тайм обновления
- События: `workflow.update`, `task.progress`, `scenario.event`

### gRPC:
- `OrchestrationService` - Основной сервис
- `ScenarioService` - Работа со сценариями
- `MonitoringService` - Мониторинг

## 🚀 Запуск

### Standalone:
```bash
python main.py
```

### Docker:
```bash
docker build -t orchestrator:latest .
docker run -p 8000:8000 orchestrator:latest
```

### Docker Compose:
```bash
docker-compose up
```

### Kubernetes:
```bash
kubectl apply -f k8s/
```

## 🔧 Конфигурация

```yaml
orchestrator:
  core:
    workers: 4
    max_workflows: 1000

  ai:
    enabled: true
    model: "gpt-4"
    decision_threshold: 0.8

  monitoring:
    metrics_port: 9090
    tracing: true

  interfaces:
    http_port: 8000
    ws_port: 8001
    grpc_port: 50051
```

## 📊 Метрики

- `orchestrator_workflows_total` - Всего workflow
- `orchestrator_tasks_completed` - Выполнено задач
- `orchestrator_scenarios_executed` - Выполнено сценариев
- `orchestrator_ai_decisions` - AI решений принято
- `orchestrator_errors_total` - Всего ошибок

## 🔒 Безопасность

- JWT авторизация
- TLS/SSL для всех endpoint'ов
- Rate limiting
- Input validation
- Audit logging

## 📚 Зависимости

- FastAPI - REST API
- asyncio - Асинхронность
- Redis - Кеш и очереди
- PostgreSQL - Персистентность
- Prometheus - Метрики
- OpenTelemetry - Трейсинг

---

**Unified Orchestrator - мозг системной оркестрации**