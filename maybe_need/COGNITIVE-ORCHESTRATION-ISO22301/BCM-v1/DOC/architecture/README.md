# 🏗️ Architecture Documentation

Детальная архитектурная документация BCM Platform.

## 📚 Содержание

### Основные архитектурные документы

| Файл | Описание | Строк |
|------|----------|-------|
| [BCM_COMPONENT_INTEGRATION_GUIDE.md](BCM_COMPONENT_INTEGRATION_GUIDE.md) | Полное руководство по интеграции всех компонентов системы | ~1,041 |
| [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md) | Архитектурные диаграммы всех уровней | ~732 |
| [BCM_PLATFORM_DETAILED_DIAGRAMS.md](BCM_PLATFORM_DETAILED_DIAGRAMS.md) | Детализированные диаграммы платформы | ~685 |
| [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md) | Backend архитектура и API | ~461 |
| [BCM_PLATFORM_ARCHITECTURE_MAP.md](BCM_PLATFORM_ARCHITECTURE_MAP.md) | Карта архитектуры с Mermaid диаграммами | ~442 |

### Дополнительные документы

| Файл | Описание |
|------|----------|
| [BCM_PLATFORM_USER_EXPERIENCE_ARCHITECTURE.md](BCM_PLATFORM_USER_EXPERIENCE_ARCHITECTURE.md) | UX архитектура и user journeys |
| [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) | Полная техническая архитектура системы |
| [PLATFORM_OVERVIEW.md](PLATFORM_OVERVIEW.md) | Общий обзор платформы |
| [MODULE_DEPENDENCIES_AND_TABLES.md](MODULE_DEPENDENCIES_AND_TABLES.md) | Зависимости модулей и таблицы БД |
| [BCM_PLATFORM_ARCHITECTURE_STRATEGY.md](BCM_PLATFORM_ARCHITECTURE_STRATEGY.md) | Стратегия развития архитектуры |
| [CURRENT_SYSTEM_ARCHITECTURE.md](CURRENT_SYSTEM_ARCHITECTURE.md) | Текущая архитектура системы |
| [BCM_DEV_TEAM_HANDOVER.md](BCM_DEV_TEAM_HANDOVER.md) | Документация для передачи команде разработки |
| [integration-architecture.md](integration-architecture.md) | Архитектура интеграций |

## 🎯 Быстрый старт

### Для новых участников команды
1. Начните с [PLATFORM_OVERVIEW.md](PLATFORM_OVERVIEW.md)
2. Изучите [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md)
3. Перейдите к [BCM_COMPONENT_INTEGRATION_GUIDE.md](BCM_COMPONENT_INTEGRATION_GUIDE.md)

### Для архитекторов
1. [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md)
2. [BCM_PLATFORM_ARCHITECTURE_MAP.md](BCM_PLATFORM_ARCHITECTURE_MAP.md)
3. [MODULE_DEPENDENCIES_AND_TABLES.md](MODULE_DEPENDENCIES_AND_TABLES.md)

### Для Backend разработчиков
1. [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md)
2. [integration-architecture.md](integration-architecture.md)

## 📊 Ключевые концепции

- **Microservices Architecture** - 39 микросервисов
- **Event-Driven** - EventBus на Redis + PostgreSQL
- **Multi-tenant** - Изоляция данных по организациям
- **AI-Powered** - 10 AI "органов"
- **ISO 22301 Compliance** - Соответствие стандарту

---

**Последнее обновление**: 2025-09-28