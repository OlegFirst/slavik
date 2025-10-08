# EventBus Setup Guide - BCM Platform

## 🚨 Текущая проблема

EventBus **закомментирован** в docker-compose.yml, но используется в **126 местах!**

**Критические зависимости:**
- AI Orchestrator (25 использований)
- Community Intelligence (интеграция через EVENTBUS_URL)
- Platform Services (11 сервисов подписываются на события)

---

## ✅ Решение (выбери один вариант)

### Вариант A: RabbitMQ через Docker (рекомендуется)

1. **Добавить в docker-compose.yml:**

```yaml
  rabbitmq:
    image: rabbitmq:3-management-alpine
    container_name: bcm-rabbitmq
    ports:
      - "5672:5672"    # AMQP port
      - "15672:15672"  # Management UI
    environment:
      - RABBITMQ_DEFAULT_USER=bcm_user
      - RABBITMQ_DEFAULT_PASS=SecurePassword123  # CHANGE IN PRODUCTION!
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
    networks:
      - intelligent-core-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

volumes:
  rabbitmq-data:
    name: bcm-rabbitmq-data
```

2. **Добавить в .env:**

```bash
RABBITMQ_URL=amqp://bcm_user:SecurePassword123@localhost:5672/
```

3. **Запустить:**

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core
docker-compose up -d rabbitmq
```

4. **Проверить:**

```bash
# Management UI
open http://localhost:15672
# Login: bcm_user / SecurePassword123
```

---

### Вариант B: CloudAMQP (managed RabbitMQ)

**Плюсы:** Без Docker, managed, высокая доступность

1. **Зарегистрироваться:** https://www.cloudamqp.com/ (free tier)

2. **Получить URL** (формат: `amqp://user:pass@host/vhost`)

3. **Добавить в .env:**

```bash
RABBITMQ_URL=amqp://your-cloudamqp-url
```

4. **Готово!** Без Docker, без конфигурации.

---

### Вариант C: Redis Streams (альтернатива)

Уже используете Redis Cloud! Можно использовать Redis Streams вместо RabbitMQ.

**Плюсы:**
- Уже настроено (REDIS_URL в .env)
- Нет дополнительного сервиса
- Быстрее чем RabbitMQ

**Минусы:**
- Меньше фичей чем RabbitMQ
- Нужно переписать EventBus client

---

## 🎯 Моя рекомендация: Вариант A (RabbitMQ Docker)

**Почему:**
- ✅ Работает локально
- ✅ Management UI для отладки
- ✅ Полная совместимость с текущим кодом
- ✅ ISO-compliant (audit trail событий)

---

## 📊 Что будет после настройки

После запуска RabbitMQ у вас будет:

**126 событий работают:**
```
bcm.bia.started → AI Orchestrator обработает
bcm.incident.opened → Response Service среагирует
document.approved → Audit Service запишет
exercise.completed → Learning Service обучится
```

**EventBus Dashboard доступен:**
- Exchanges: 1 (bcm_events)
- Queues: ~20 (по количеству subscribers)
- Messages: Real-time мониторинг

---

## 🔧 Тестирование после запуска

```bash
# 1. Проверить что RabbitMQ запущен
curl http://localhost:15672/api/overview \
  -u bcm_user:SecurePassword123

# 2. Протестировать publish
python3 << 'EOF'
import asyncio
from shared.eventbus import init_eventbus

async def test():
    eventbus = init_eventbus("amqp://bcm_user:SecurePassword123@localhost:5672/")
    await eventbus.connect()

    await eventbus.publish(
        "test.event",
        {"message": "Hello EventBus!"},
        tenant_id="test"
    )

    print("✅ Event published!")
    await eventbus.disconnect()

asyncio.run(test())
EOF

# 3. Проверить в RabbitMQ UI
open http://localhost:15672/#/queues
# Должно быть сообщение в очереди!
```

---

## 📚 Документация событий

Теперь у тебя есть:

1. **AsyncAPI спецификация**
   - `/infrastructure/events/asyncapi.yaml`
   - Стандартный формат, совместимый с EventCatalog

2. **Полный каталог событий**
   - `/infrastructure/events/EVENTS.md`
   - 126 событий с publishers/subscribers

3. **Event Flow диаграмма**
   - `/infrastructure/events/EVENT_FLOW.md`
   - Mermaid визуализация

4. **JSON для автоматизации**
   - `/infrastructure/events/events_catalog.json`
   - Для CI/CD, code generation

---

## 🚀 Следующие шаги

1. ✅ Выбрать Вариант A/B/C
2. ✅ Настроить RabbitMQ
3. ✅ Обновить .env
4. ✅ Запустить тесты
5. ✅ Uncomment EventBus в docker-compose.yml (если Вариант A)

---

**Готов настроить RabbitMQ?** Скажи какой вариант выбираешь!
