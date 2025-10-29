# BCM Platform Architecture - Правильная организация

## 🎯 Концепция: Платформа, а не Odoo с надстройками

### Уровни запуска:

```
┌─────────────────────────────────────────────────────────┐
│                   PLATFORM ORCHESTRATOR                  │
│                  (Единая точка управления)                │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐           ┌───────▼────────┐
│   EventBus     │           │   Health       │
│   (События)    │           │   Monitor      │
└───────┬────────┘           └────────────────┘
        │
        ├──────────────────────────────────────┐
        │                                      │
┌───────▼────────┐                    ┌───────▼────────┐
│  LEVEL 1:      │                    │  LEVEL 1:      │
│  Core Services │                    │  Databases     │
├────────────────┤                    ├────────────────┤
│ • Redis        │                    │ • PostgreSQL   │
│ • RabbitMQ     │                    │ • MongoDB      │
│ • Vault        │                    │ • ClickHouse   │
└───────┬────────┘                    └───────┬────────┘
        │                                      │
        └──────────────┬───────────────────────┘
                       │
                ┌──────┴──────┐
                │             │
        ┌───────▼────────┐   ┌───────▼────────┐
        │  LEVEL 2:      │   │  LEVEL 2:      │
        │  Gateways      │   │  Auth          │
        ├────────────────┤   ├────────────────┤
        │ • API Gateway  │   │ • Keycloak     │
        │ • DB Gateway   │   │ • Auth Service │
        │ • Traefik      │   │ • LDAP Bridge  │
        └───────┬────────┘   └───────┬────────┘
                │                     │
                └──────┬──────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐           ┌───────▼────────┐
│  LEVEL 3:      │           │  LEVEL 3:      │
│  Business      │           │  AI Services   │
├────────────────┤           ├────────────────┤
│ • Odoo (ERP)   │           │ • AI Control   │
│ • CRM Bridge   │           │ • Digital Twin │
│ • BIA Engine   │           │ • AI Consultant│
└───────┬────────┘           └───────┬────────┘
        │                             │
        └──────────┬──────────────────┘
                   │
           ┌───────▼────────┐
           │  LEVEL 4:      │
           │  Applications  │
           ├────────────────┤
           │ • Admin Panel  │
           │ • Web Portal   │
           │ • Mobile Apps  │
           └────────────────┘
```

## 🚀 Группы сервисов

### Group 1: Foundation (Фундамент)
```yaml
foundation:
  databases:
    - postgres-main    # Основная БД для всех сервисов
    - postgres-odoo    # Отдельная БД для Odoo
    - redis           # Кэш и сессии
    - mongodb         # NoSQL для логов и событий

  messaging:
    - rabbitmq        # Очереди сообщений
    - eventbus        # Шина событий платформы

  storage:
    - minio           # S3-совместимое хранилище
    - vault           # Секреты и конфигурации
```

### Group 2: Infrastructure (Инфраструктура)
```yaml
infrastructure:
  gateways:
    - unified_api_gateway      # Единая точка входа API
    - unified_database_gateway # Управление БД
    - traefik                  # Reverse proxy

  auth:
    - keycloak        # SSO и управление доступом
    - ldap_bridge     # LDAP интеграция

  monitoring:
    - health_monitor  # Мониторинг здоровья
    - grafana        # Метрики
    - prometheus     # Сбор метрик
```

### Group 3: Business Logic (Бизнес-логика)
```yaml
business:
  erp:
    - odoo           # ERP система (как компонент)

  bcm_core:
    - bia_engine     # Business Impact Analysis
    - risk_manager   # Управление рисками
    - compliance     # Соответствие стандартам

  integrations:
    - crm_bridge     # CRM интеграции
    - erp_bridges    # ERP интеграции
    - api_adapters   # Внешние API
```

### Group 4: Intelligence (Интеллект)
```yaml
intelligence:
  ai_core:
    - ai_orchestrator      # Оркестратор AI
    - ai_control_center    # Центр управления AI

  ai_services:
    - digital_twin         # Цифровые двойники
    - ai_consultant        # AI консультант
    - predictive_analytics # Предиктивная аналитика
```

### Group 5: Applications (Приложения)
```yaml
applications:
  web:
    - admin_panel          # Админ-панель
    - web_portal          # Веб-портал
    - mobile_backend      # Backend для мобильных

  clients:
    - desktop_app         # Desktop клиент
    - mobile_apps         # Мобильные приложения
```

## 🔧 Platform Orchestrator - Главный дирижер

```python
# services/platform-orchestrator/main.py

class PlatformOrchestrator:
    """
    Единая точка управления всей платформой
    """

    def __init__(self):
        self.groups = {
            'foundation': FoundationGroup(),
            'infrastructure': InfrastructureGroup(),
            'business': BusinessGroup(),
            'intelligence': IntelligenceGroup(),
            'applications': ApplicationGroup()
        }
        self.eventbus = EventBus()
        self.health_monitor = HealthMonitor()

    async def start_platform(self):
        """Запуск платформы по уровням"""

        # Level 1: Foundation
        await self.start_group('foundation')
        await self.wait_healthy('foundation')

        # Level 2: Infrastructure
        await self.start_group('infrastructure')
        await self.wait_healthy('infrastructure')

        # Level 3: Business & Intelligence (параллельно)
        await asyncio.gather(
            self.start_group('business'),
            self.start_group('intelligence')
        )

        # Level 4: Applications
        await self.start_group('applications')

        # Публикуем событие готовности
        await self.eventbus.publish('platform.ready')

    async def start_group(self, group_name):
        """Запуск группы сервисов"""
        group = self.groups[group_name]

        # Запускаем сервисы группы
        for service in group.services:
            await self.start_service(service)

        # Ждем готовности группы
        await group.wait_ready()

        # Публикуем событие
        await self.eventbus.publish(f'group.{group_name}.ready')

    async def start_service(self, service):
        """Запуск отдельного сервиса"""

        # Проверяем зависимости
        await self.check_dependencies(service)

        # Инициализация БД если нужно
        if service.needs_database:
            await self.init_database(service)

        # Запуск
        await service.start()

        # Регистрация в health monitor
        self.health_monitor.register(service)
```

## 🗄️ Database Manager - Централизованное управление БД

```python
# services/database-manager/main.py

class DatabaseManager:
    """
    Управляет всеми БД платформы
    """

    def __init__(self):
        self.databases = {
            'platform': PostgresDB(host='postgres-main', db='platform'),
            'odoo': PostgresDB(host='postgres-odoo', db='odoo'),
            'logs': MongoDB(host='mongodb', db='logs'),
            'metrics': ClickHouseDB(host='clickhouse', db='metrics')
        }
        self.migrations = MigrationManager()

    async def initialize_platform(self):
        """Одноразовая инициализация всех БД"""

        # Создаем БД
        for name, db in self.databases.items():
            await db.create_if_not_exists()

        # Запускаем миграции
        await self.migrations.run_all()

        # Создаем пользователей для сервисов
        await self.create_service_users()

        # Инициализация Odoo БД
        if not await self.odoo_initialized():
            await self.init_odoo_database()

    async def init_odoo_database(self):
        """Инициализация БД Odoo с модулями"""

        # Создаем БД
        await self.databases['odoo'].create_database('bcm_platform')

        # Устанавливаем модули через SQL
        await self.install_odoo_modules([
            'base', 'web', 'mail',  # Основные
            'hr', 'project', 'website',  # Стандартные
            'bcm_base', 'bcm_core', 'bcm_*'  # BCM модули
        ])

        # Создаем admin пользователя
        await self.create_odoo_admin()

        # Маркируем как инициализированную
        await self.mark_initialized('odoo')
```

## 🔥 EventBus - Коммуникация между сервисами

```python
# services/eventbus/main.py

class EventBus:
    """
    Централизованная шина событий
    """

    def __init__(self):
        self.redis = Redis()
        self.subscribers = {}

    async def publish(self, event, data=None):
        """Публикация события"""

        payload = {
            'event': event,
            'data': data,
            'timestamp': datetime.now(),
            'source': self.service_id
        }

        # Публикуем в Redis
        await self.redis.publish(f'events:{event}', json.dumps(payload))

        # Логируем в MongoDB
        await self.log_event(payload)

    async def subscribe(self, pattern, handler):
        """Подписка на события"""

        async def listener():
            pubsub = self.redis.pubsub()
            await pubsub.psubscribe(f'events:{pattern}')

            async for message in pubsub.listen():
                if message['type'] == 'pmessage':
                    event = json.loads(message['data'])
                    await handler(event)

        # Запускаем listener в фоне
        asyncio.create_task(listener())
```

## 🏗️ Docker Compose структура

```yaml
# docker-compose.platform.yml

services:
  # ORCHESTRATOR - главный
  platform-orchestrator:
    build: ./services/platform-orchestrator
    environment:
      - PLATFORM_MODE=production
      - AUTO_INIT=true
    depends_on:
      - eventbus
      - database-manager
    networks:
      - bcm-platform

  # DATABASE MANAGER - управление БД
  database-manager:
    build: ./services/database-manager
    environment:
      - INIT_ON_START=true
      - ODOO_AUTO_SETUP=true
    volumes:
      - ./config/databases.yml:/config/databases.yml
    networks:
      - bcm-platform

  # EVENTBUS - коммуникации
  eventbus:
    build: ./services/eventbus
    depends_on:
      - redis
      - mongodb
    networks:
      - bcm-platform

  # Дальше идут группы сервисов...
```

## 🎯 Преимущества подхода:

1. **Odoo - просто компонент**, а не центр вселенной
2. **Единая инициализация** - настроил один раз и забыл
3. **Группы сервисов** - логичная организация
4. **EventBus** - асинхронная коммуникация
5. **Health Monitor** - автовосстановление
6. **Database Manager** - централизованное управление БД
7. **Platform Orchestrator** - единая точка управления

Это решает проблему "завтыка" при соединении Odoo и PostgreSQL - все управляется централизованно через Platform Orchestrator и Database Manager!