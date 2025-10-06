# Learning System - Индекс Документации

## 📚 Основная Документация

Актуальная документация модуля Learning System.

### 1. [README.md](README.md)
**Назначение**: Общий обзор и быстрый старт

**Содержание**:
- Обзор сервиса и основные возможности
- Архитектура системы
- Технический стек
- База данных и схемы
- API endpoints (полный список)
- Быстрый старт и установка
- Мониторинг и производительность
- Безопасность

**Для кого**: Все (разработчики, администраторы, архитекторы)

---

### 2. [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md)
**Назначение**: Детальная техническая спецификация

**Содержание**:
- Полная архитектура системы (Layered, Component diagrams)
- Детальное описание всех компонентов (10 engines)
- Алгоритмы и формулы расчётов
- API спецификация (OpenAPI)
- Модели данных (Database schemas, Pydantic models)
- Интеграции (RAG, ML Platform, KB, Event Bus)
- Безопасность (Authentication, Authorization, RLS)
- Производительность и оптимизация
- Развёртывание (Docker, Kubernetes)

**Для кого**: Backend разработчики, DevOps, архитекторы

---

### 3. [USER_GUIDE.md](USER_GUIDE.md)
**Назначение**: Руководство пользователя

**Содержание**:
- Введение (что такое Learning System, для кого)
- Быстрый старт (3 шага)
- Основные функции:
  - Обнаружение паттернов
  - Отслеживание компетенций
  - Анализ команды
  - Геймификация
  - ML предсказания
  - Персонализированные рекомендации
- Практические примеры (3 сценария)
- API использование
- Интеграция с платформой
- FAQ и Troubleshooting

**Для кого**: Пользователи сервиса, BCM координаторы, Team Leads

---

### 4. [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md)
**Назначение**: План развития и эволюция системы

**Содержание**:
- Текущее состояние (v2.0.0)
  - Реализовано (Phases 1-4: 100%)
  - Требует доработки
- Roadmap 2025-2026:
  - Q4 2025: Production Readiness (v2.1.0)
  - Q4 2025: Platform Services (v2.2.0)
  - Q1 2026: Advanced Learning (v2.3.0)
  - Q1 2026: AI-Powered Insights (v2.4.0)
  - Q2 2026: Multi-Tenancy & Scale (v3.0.0)
  - Q2 2026: Mobile & Integrations (v3.0.0)
- Долгосрочное видение (2027+)
- Приоритизация (Must/Should/Nice to Have)
- Метрики успеха
- Ресурсы и команда
- Риски и митигация

**Для кого**: Product Managers, Team Leads, Stakeholders

---

### 5. [PLATFORM_INTEGRATION_ARCHITECTURE.md](PLATFORM_INTEGRATION_ARCHITECTURE.md)
**Назначение**: Архитектура интеграции с платформой (детальная)

**Содержание**:
- Обзор интеграции
- Созданные компоненты (shared connectors)
- Примеры использования RAG/ML Platform/KB
- Преимущества интеграции
- Архитектурные паттерны

**Для кого**: Backend разработчики, архитекторы

---

## 📁 Архив Документации

Историческая документация процесса разработки (moved to `/archive/docs/`).

### Документы Разработки

- **PLATFORM_INTEGRATION_COMPLETE.md** - Полный отчёт о реализации Phase 4
- **PHASE_2A_IMPLEMENTATION_COMPLETE.md** - Отчёт о Phase 2A (self-learning)
- **ENHANCEMENT_IMPLEMENTATION_COMPLETE.md** - Отчёт о Phase 2 (enhancements)
- **FULL_LEARNING_CYCLE.md** - Дизайн полного цикла обучения
- **MISSING_COMPONENTS_DESIGN.md** - Дизайн недостающих компонентов (Phase 3)
- **INTEGRATION_ARCHITECTURE_DIAGRAM.md** - Визуальные диаграммы интеграции
- **ENHANCEMENT_ROADMAP.md** - Первоначальный roadmap фич
- **WHATS_NEXT.md** - Что дальше после Phase 2A
- **ANALYSIS_AND_INTEGRATION_PLAN.md** - План анализа и интеграции
- **BUSINESS_VALUE_DEEP_DIVE.md** - Бизнес-ценность Learning System

**Для кого**: Для исторического контекста и понимания эволюции системы

---

## 🔗 Связанная Документация

### В Корне Проекта

- [/PLATFORM_INTEGRATION_SUMMARY.md](/Users/MD/AI-Platform-ISO/PLATFORM_INTEGRATION_SUMMARY.md) - Executive summary интеграции с платформой

### Shared Components

- `/shared/integrations/` - Shared connectors (RAG, ML Platform, KB)
  - `rag_connector.py` - RAG Service connector
  - `ml_platform_client.py` - ML Platform client
  - `knowledge_client.py` - Knowledge Base client

### Database

- `/infrastructure/database/migrations_source/043_learning_system_enhancements.sql` - Phase 2 миграция

### Examples

- `examples/platform_integration_example.py` - Рабочие примеры интеграции (6 examples)

---

## 🎯 Как Использовать Документацию

### Если вы новый разработчик:
1. Начните с [README.md](README.md) - общий обзор
2. Изучите [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md) - глубокое погружение
3. Посмотрите `examples/` - практические примеры
4. Ознакомьтесь с [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) - куда движемся

### Если вы пользователь/BCM координатор:
1. [USER_GUIDE.md](USER_GUIDE.md) - всё, что нужно знать
2. API docs - http://localhost:8033/docs
3. FAQ в User Guide для решения проблем

### Если вы архитектор:
1. [README.md](README.md) - архитектура высокого уровня
2. [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md) - детальная архитектура
3. [PLATFORM_INTEGRATION_ARCHITECTURE.md](PLATFORM_INTEGRATION_ARCHITECTURE.md) - интеграции
4. [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) - будущие планы

### Если вы product manager:
1. [README.md](README.md) - что умеет система
2. [USER_GUIDE.md](USER_GUIDE.md) - как пользователи будут работать
3. [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) - планы развития, приоритеты
4. Archive docs - как мы пришли к текущему состоянию

---

## 📝 Обновление Документации

### Частота Обновлений

- **README.md** - при изменении API или архитектуры
- **TECHNICAL_SPECIFICATION.md** - при добавлении компонентов
- **USER_GUIDE.md** - при добавлении функций
- **DEVELOPMENT_ROADMAP.md** - quarterly (каждый квартал)

### Процесс Обновления

1. Внести изменения в соответствующий документ
2. Обновить версию и дату
3. Создать PR с описанием изменений
4. Review от tech lead
5. Merge и уведомление команды

### Контакты

**Поддержка документации**: AI Platform Team
**Email**: docs@ai-platform.com
**Slack**: #learning-system-docs

---

**Последнее обновление**: 2025-10-05
**Версия документации**: 2.0.0
