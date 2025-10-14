# 🗄️ Inventory Documentation

Инвентаризация компонентов BCM Platform: сервисы, события, модели, маршруты.

## 📚 Содержание

| Файл | Описание |
|------|----------|
| [SERVICES_INVENTORY_COMPLETE.md](SERVICES_INVENTORY_COMPLETE.md) | Полный инвентарь всех сервисов системы |
| [events_catalog.md](events_catalog.md) | Каталог всех событий EventBus |
| [odoo_models.md](odoo_models.md) | Все модели Odoo BCM |
| [routes_eventbus.md](routes_eventbus.md) | Маршруты EventBus сервиса |
| [routes_orchestrator.md](routes_orchestrator.md) | Маршруты AI Orchestrator |

## 🎯 Категории инвентаря

### 1. Services Inventory
**Файл**: [SERVICES_INVENTORY_COMPLETE.md](SERVICES_INVENTORY_COMPLETE.md)

Полный список всех 39 микросервисов:
- **Порты** - какой сервис на каком порту
- **Статус** - активен/неактивен
- **Зависимости** - от чего зависит
- **Назначение** - для чего нужен

### 2. Events Catalog
**Файл**: [events_catalog.md](events_catalog.md)

Каталог всех событий EventBus:
- **Типы событий** - категории
- **Publishers** - кто публикует
- **Subscribers** - кто подписан
- **Payload** - структура данных

Примеры событий:
- `bcm.incident.opened`
- `bcm.bia.completed`
- `bcm.risk.updated`
- `bcm.doc.analyzed`
- `bcm.thehive.case_created`

### 3. Odoo Models
**Файл**: [odoo_models.md](odoo_models.md)

Все модели Odoo BCM:
- **Model name** - техническое имя
- **Description** - описание
- **Module** - в каком модуле
- **Fields** - ключевые поля
- **Relations** - связи с другими моделями

Примеры:
- `bcm.business.process` - Бизнес-процессы
- `bcm.risk` - Риски
- `bcm.incident` - Инциденты
- `bcm.plan` - Планы
- `bcm.exercise` - Учения

### 4. Routes (Endpoints)
**Файлы**:
- [routes_eventbus.md](routes_eventbus.md) - EventBus API
- [routes_orchestrator.md](routes_orchestrator.md) - AI Orchestrator API

Все HTTP endpoints:
- **Method** - GET/POST/PUT/DELETE
- **Path** - URL путь
- **Parameters** - параметры
- **Response** - формат ответа
- **Authentication** - требования

## 🎯 Для разных ролей

### Backend Developer
1. [SERVICES_INVENTORY_COMPLETE.md](SERVICES_INVENTORY_COMPLETE.md) - узнать какие сервисы есть
2. [routes_eventbus.md](routes_eventbus.md) - API EventBus
3. [routes_orchestrator.md](routes_orchestrator.md) - API Orchestrator
4. [events_catalog.md](events_catalog.md) - какие события использовать

### Odoo Developer
1. [odoo_models.md](odoo_models.md) - все модели BCM
2. [events_catalog.md](events_catalog.md) - интеграция с EventBus

### DevOps Engineer
1. [SERVICES_INVENTORY_COMPLETE.md](SERVICES_INVENTORY_COMPLETE.md) - какие сервисы деплоить
2. Порты и зависимости для docker-compose

### QA Engineer
1. [events_catalog.md](events_catalog.md) - тестировать события
2. [routes_eventbus.md](routes_eventbus.md) - тестировать API
3. [routes_orchestrator.md](routes_orchestrator.md) - тестировать AI API

## 📊 Статистика

- **Сервисов**: 39
- **Активных сервисов**: 7 (18%)
- **События EventBus**: 50+
- **Odoo моделей BCM**: 30+
- **API endpoints**: 200+

## 🔗 Связанная документация

- [Architecture](../architecture/) - как компоненты связаны
- [API Documentation](../api/) - детальная API документация
- [Modules](../modules/) - модули Odoo
- [AI Services](../ai/) - AI компоненты

---

**Последнее обновление**: 2025-09-28