# 🎯 ISO-22301 BCM Platform - Обзор Проекта

**Версия**: 1.0
**Дата**: 2025-09-28
**Статус**: В разработке (35-40% готовности)

---

## 📋 Основная информация

**Название**: ISO-22301 Business Continuity Management Platform
**Репозиторий**: https://github.com/SEH-foundation/ISO-22301
**Текущая ветка**: `unified-complete-iso22301-20250920`
**Версия Odoo**: 18.0 Community Edition

---

## 🎯 Назначение

Комплексная платформа управления непрерывностью бизнеса (BCM) с интеграцией искусственного интеллекта для автоматизации процессов обеспечения непрерывности бизнеса согласно стандарту ISO 22301:2019.

---

## 🏗️ Архитектура

### Уровни системы:

```
┌─────────────────────────────────────────────┐
│         FRONTEND LAYER (4 приложения)       │
│  Next.js 15 | React 19 | Vue.js            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         API GATEWAY (Порт 8090)             │
│  FastAPI | WebSocket | REST API            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      MICROSERVICES (39 сервисов)            │
│  Core | AI Services | Integrations         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         ODOO 18.0 (29 BCM модулей)          │
│  Business Logic | Data Models | Workflows   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│     INFRASTRUCTURE (Docker)                 │
│  PostgreSQL | Redis | RabbitMQ | Keycloak  │
└─────────────────────────────────────────────┘
```

---

## 📊 Статистика проекта

| Компонент | Количество | Статус |
|-----------|------------|--------|
| BCM модули Odoo | 29 (28 с манифестами) | 70% готовы |
| Микросервисы | 39 запланировано, 7 активных | 18% работают |
| AI "органы" | 10 | 60% реализованы |
| Frontend приложения | 4 | 40% готовы |
| Интеграции | 8 | 5 работают |
| Строк кода | ~100,000+ | - |

---

## 🔑 Ключевые компоненты

### 1. Odoo BCM модули (29)
- **bcm_base** - Базовый модуль с AI Foundation
- **bcm_governance** - Управление и комплаенс
- **bcm_bia** - Business Impact Analysis
- **bcm_risk_management** - Управление рисками
- **bcm_incident_management** - Управление инцидентами
- **bcm_exercise** - Учения и тренировки
- И ещё 23 модуля

### 2. AI Сервисы (10 "органов")
1. 🧠 Governance Brain - Стратегическое управление
2. 🚨 Emergency Response - Кризисное реагирование
3. 🔮 Impact Oracle - Прогнозирование
4. 🎭 Scenario Creator - Генерация сценариев
5. ⚠️ Risk Advisor - Анализ рисков
6. 🛡️ Compliance Guardian - Мониторинг соответствия
7. 📈 Performance Analyst - KPI анализ
8. 🎓 Learning Coach - Адаптивное обучение
9. 📋 Plan Generator - Генерация планов
10. 📊 Lifecycle Monitor - Мониторинг BCMS

### 3. Интеграции
- **TheHive** - SOAR платформа (✅ работает)
- **Moodle** - LMS для обучения (✅ работает)
- **MCP Server** - Claude Desktop интеграция (✅ работает)
- **Exercise Simulators** - JaamSim + NICS (✅ работает)
- **Governance Service** - Data governance (✅ работает)

---

## 🚀 Технологический стек

### Backend:
- **Python 3.11+** - Основной язык
- **Odoo 18.0** - ERP платформа
- **FastAPI** - Микросервисы
- **PostgreSQL 15** - База данных
- **Redis 7** - Кэширование
- **RabbitMQ** - Message broker

### Frontend:
- **Next.js 15** - React фреймворк
- **React 19** - UI библиотека
- **TypeScript** - Типизация
- **Tailwind CSS 4** - Стили
- **shadcn/ui** - UI компоненты

### AI/ML:
- **Anthropic Claude** - Основной AI
- **Local LLM (Gemma3)** - Локальная генерация
- **Custom ML models** - BIA и Risk Assessment

### Infrastructure:
- **Docker** - Контейнеризация
- **Docker Compose** - Оркестрация
- **Prometheus + Grafana** - Мониторинг (настроен, не запущен)
- **Keycloak** - SSO

---

## 📁 Структура проекта

```
ISO-22301/
├── core/odoo-18.0/addons/     # 29 BCM модулей
├── services/                   # Микросервисы
├── integrations/               # Внешние интеграции
├── frontend/                   # 4 фронтенд приложения
├── api/                        # API Gateway
├── backend/                    # Backend сервисы
├── monitoring/                 # Prometheus + Grafana
├── tests/                      # Тесты (нужно восстановить!)
└── docs/                       # Документация
```

---

## 🎯 Текущий статус

### Готово:
✅ Базовая архитектура Odoo модулей (70%)
✅ Ключевые AI сервисы (60%)
✅ Основные интеграции (TheHive, Moodle)
✅ API Gateway (85%)
✅ Monitoring конфигурация (95%)

### В разработке:
⚠️ Фронтенд приложения (40%)
⚠️ Остальные микросервисы (18% активны)
⚠️ CI/CD pipeline (0%)
⚠️ Тестирование (5% покрытие)

### Критические проблемы:
❌ Тесты архивированы (нужно восстановить)
❌ Мониторинг не запущен
❌ Нет метрик в сервисах
❌ Проблемы безопасности (hardcoded credentials)

---

## 📍 Ссылки на документацию

### Аналитические отчёты:
- [01-TECHNICAL_ARCHITECTURE_ANALYSIS.md](../analysis-reports/01-TECHNICAL_ARCHITECTURE_ANALYSIS.md) - Полный технический анализ
- [02-INCOMPLETE_SERVICES_ANALYSIS.md](../analysis-reports/02-INCOMPLETE_SERVICES_ANALYSIS.md) - Анализ незавершённых сервисов

### Техническая документация:
- [02-ODOO_MODULES.md](02-ODOO_MODULES.md) - BCM модули Odoo
- [03-MICROSERVICES.md](03-MICROSERVICES.md) - Микросервисы
- [04-INTEGRATIONS.md](04-INTEGRATIONS.md) - Интеграции
- [05-AI_SERVICES.md](05-AI_SERVICES.md) - AI компоненты
- [06-DEPLOYMENT.md](06-DEPLOYMENT.md) - Развёртывание

### Существующая документация:
- [README.md](../../README.md) - Основное описание (устарело!)
- [SERVICES_LIST.md](../../SERVICES_LIST.md) - Список сервисов

---

## 🎯 Цели проекта

1. **Автоматизация BCM** - 80%+ процессов автоматизированы
2. **AI-усиление** - Интеллектуальные рекомендации и прогнозы
3. **ISO 22301 соответствие** - Полное покрытие стандарта
4. **Масштабируемость** - Multi-tenant, микросервисы
5. **Open Source** - LGPL-3 лицензия

---

**Последнее обновление**: 2025-09-28
**Версия документа**: 1.0