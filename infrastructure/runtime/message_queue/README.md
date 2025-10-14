# RabbitMQ Message Queue

Асинхронная очередь сообщений для event-driven архитектуры BCM Platform.

## 🚀 Возможности

- **Publish/Subscribe** - событийная модель
- **Work Queues** - распределение задач между воркерами
- **Topic Routing** - маршрутизация по паттернам
- **Dead Letter Queue** - обработка failed messages
- **Message Priority** - приоритетные сообщения
- **Message Persistence** - сохранение при сбоях
- **Auto-reconnection** - автопереподключение

## 📦 Установка

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить RabbitMQ (Docker)
docker-compose up rabbitmq

# Или standalone
docker run -d \
  --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3.12-management-alpine
```

## 🔧 Использование

### 1. Publisher (отправка событий)

```python
from rabbitmq_manager import get_rabbitmq_manager

# Получить менеджер
mq = await get_rabbitmq_manager("amqp://guest:guest@localhost/")

# Отправить событие
await mq.publish(
    routing_key="user.created",
    message={
        "user_id": "123",
        "email": "user@example.com",
        "timestamp": "2025-10-03T12:00:00Z"
    },
    priority=5  # 0-9, где 9 - высший
)

# Отправить с TTL
await mq.publish(
    routing_key="notification.email",
    message={"to": "user@example.com", "subject": "Welcome!"},
    ttl=60000  # 60 секунд
)
```

### 2. Consumer (обработка событий)

```python
# Обработчик сообщений
async def handle_user_events(message: dict):
    data = message["data"]
    print(f"User event: {data}")

    # Ваша логика обработки
    user_id = data["user_id"]
    # ...

# Подписаться на события
await mq.subscribe(
    routing_key="user.*",  # user.created, user.updated, etc.
    callback=handle_user_events,
    queue_name="user_events_queue",
    durable=True
)

# Паттерны маршрутизации:
# - "user.*" -> user.created, user.updated, user.deleted
# - "*.important" -> user.important, order.important
# - "#" -> все сообщения
```

### 3. Work Queue (распределение задач)

```python
# Создать Work Queue
async def process_email_task(task: dict):
    data = task["data"]
    print(f"Sending email to {data['to']}")

    # Отправка email
    await send_email(data["to"], data["subject"], data["body"])

await mq.create_work_queue(
    queue_name="email_tasks",
    callback=process_email_task,
    max_priority=10
)

# Добавить задачу в очередь
await mq.publish_task(
    queue_name="email_tasks",
    task={
        "to": "user@example.com",
        "subject": "Welcome!",
        "body": "Thank you for signing up!"
    },
    priority=5
)
```

### 4. Dead Letter Queue (DLQ)

Если задача failed, она автоматически попадет в DLQ:

```python
# DLQ создается автоматически при создании Work Queue
# Формат: {queue_name}.dlq

# Проверить failed tasks
stats = await mq.get_queue_stats("email_tasks.dlq")
print(f"Failed tasks: {stats['message_count']}")
```

## 📊 Мониторинг

### Management UI

Открыть в браузере: http://localhost:15672
- Username: `guest`
- Password: `guest`

### Программная проверка

```python
# Статистика очереди
stats = await mq.get_queue_stats("user_events_queue")

print(f"Messages: {stats['message_count']}")
print(f"Consumers: {stats['consumer_count']}")
```

## 🎯 Примеры использования в BCM Platform

### User Service → Notification Service

```python
# user_service.py
await mq.publish(
    routing_key="user.registered",
    message={
        "user_id": user.id,
        "email": user.email,
        "name": user.full_name
    }
)

# notification_service.py
async def send_welcome_email(message: dict):
    data = message["data"]
    await send_email(
        to=data["email"],
        subject=f"Welcome, {data['name']}!",
        template="welcome"
    )

await mq.subscribe("user.registered", send_welcome_email)
```

### BIA Service → Audit Log Service

```python
# bia_service.py
await mq.publish(
    routing_key="bia.analysis.completed",
    message={
        "bia_id": bia.id,
        "organization_id": org.id,
        "results": bia.results
    }
)

# audit_service.py
async def log_bia_completion(message: dict):
    data = message["data"]
    await create_audit_log(
        event_type="bia_analysis_completed",
        organization_id=data["organization_id"],
        details=data
    )

await mq.subscribe("bia.*.completed", log_bia_completion)
```

### Background Tasks (Long-running)

```python
# Создать Work Queue для heavy tasks
async def process_monte_carlo_simulation(task: dict):
    data = task["data"]
    simulation_id = data["simulation_id"]

    # Запуск симуляции (может занять минуты)
    results = await run_monte_carlo(
        scenario=data["scenario"],
        iterations=data["iterations"]
    )

    # Сохранить результаты
    await save_simulation_results(simulation_id, results)

await mq.create_work_queue(
    "simulation_tasks",
    process_monte_carlo_simulation
)

# Добавить задачу
await mq.publish_task(
    "simulation_tasks",
    {
        "simulation_id": "sim-123",
        "scenario": {...},
        "iterations": 10000
    },
    priority=8  # Высокий приоритет
)
```

## 🔐 Production Recommendations

1. **Security**:
   - Используй надежные credentials (не `guest:guest`)
   - Включи SSL/TLS для production
   - Настрой vhosts для разных сред

2. **Performance**:
   - Настрой `prefetch_count` (по умолчанию 10)
   - Используй connection pooling
   - Мониторь queue depth

3. **Reliability**:
   - Всегда используй `durable=True` для важных queues
   - Настрой Dead Letter Queues
   - Включи message persistence

4. **Monitoring**:
   - Интеграция с Prometheus
   - Alert на длинные queues
   - Мониторинг consumer lag

## 📚 Дополнительно

- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [aio-pika Documentation](https://aio-pika.readthedocs.io/)
- [AMQP Protocol](https://www.amqp.org/)
