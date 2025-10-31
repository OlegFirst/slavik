# 🧠 КАРТА КОМПОНЕНТОВ ЯДРА СИСТЕМЫ

## Основываясь на BCM_ORGANISM_ARCHITECTURE.md

### 🎯 ЯДРО СИСТЕМЫ (что MUST HAVE для работы):

```yaml
Центральная нервная система:
  1. BCM Integration Hub:
     - Старое: /services/integration_hub/
     - Новое: /platform-framework/orchestrator/
     - Роль: Координатор всех органов

  2. Event Bus:
     - Старое: /backend/eventbus/
     - Новое: /platform-framework/event-bus/  ✅ УЖЕ ЕСТЬ
     - Роль: Нервные импульсы между органами

  3. AI Bridge:
     - Старое: /services/ai_orchestrator/
     - Новое: /platform-framework/orchestrator/ai/  ✅ УЖЕ ЕСТЬ
     - Роль: Связь с AI компонентами

  4. Module Registry:
     - Старое: /backend/service_registry/
     - Новое: /platform-framework/service-registry/  ✅ УЖЕ ЕСТЬ
     - Роль: Знает о всех живых органах

Кровеносная система (Workflows):
  5. BPMN/Workflow Engine:
     - Старое: /backend/bpmn_service/
     - Новое: /platform-framework/services/bpmn_service/  ✅ УЖЕ ЕСТЬ
     - Роль: Исполнение процессов

Базовая инфраструктура:
  6. PostgreSQL:
     - База данных для всех
     - Port: 5432

  7. Redis:
     - Кэш и сессии
     - Port: 6379

  8. RabbitMQ/EventQueue:
     - Очереди сообщений
     - Port: 5672
```

## 🔄 КАК ОНИ ВЗАИМОДЕЙСТВУЮТ:

```
1. Module Registry знает кто живой
2. Event Bus передает события между модулями
3. Integration Hub координирует взаимодействие
4. Workflow Engine исполняет бизнес-процессы
5. AI Bridge подключает интеллект
```

## ✅ ЧТО УЖЕ ГОТОВО В НОВОЙ СТРУКТУРЕ:

- EventBus ✅
- Service Registry ✅
- Orchestrator (AI части) ✅
- BPMN Service ✅
- PostgreSQL config ✅
- Redis config ✅

## ❌ ЧЕГО НЕ ХВАТАЕТ:

1. **BCM Integration Hub** - нужно создать или найти
2. **RabbitMQ** - нужно добавить в docker-compose
3. **Связи между компонентами** - нужно настроить

## 🎯 ПРИОРИТЕТ ЗАПУСКА:

1. PostgreSQL + Redis (база)
2. EventBus (нервы)
3. Service Registry (память)
4. Integration Hub (координатор)
5. Workflow Engine (исполнитель)
6. AI Bridge (интеллект)