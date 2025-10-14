# 🔍 Быстрый Справочник: Документация Проекта

**Обновлено**: 2025-10-09 23:55
**Назначение**: Быстрый доступ ко всем важным документам проекта

---

## 🚨 КРИТИЧЕСКИЕ ДОКУМЕНТЫ (Прочитать Сначала)

### 1. [SESSION_SUMMARY_2025-10-09.md](SESSION_SUMMARY_2025-10-09.md)
**Резюме последней сессии работы**
- ✅ Исправление PDCA метрик
- ✅ Создание ТЗ мониторинга
- ⚠️ Коррекция ошибки с admin панелями
- Статус всех изменений

### 2. [ADMIN_PANEL_CONSOLIDATION_PLAN.md](ADMIN_PANEL_CONSOLIDATION_PLAN.md)
**План консолидации двух admin панелей**
- Детальный анализ различий
- Пошаговый план на 4.5 часа
- Чеклисты выполнения
- **ВАЖНО**: Определяет `/interface/admin_panel/` как основную версию

### 3. [TZ_MONITORING_ADMIN_PANEL.md](TZ_MONITORING_ADMIN_PANEL.md)
**Техническое задание системы мониторинга** (126KB)
- 7 модулей мониторинга
- 50+ API endpoints
- UI/UX дизайн
- План реализации на 7 недель
- ⚠️ **КОРРЕКЦИЯ**: Правильный путь `/interface/admin_panel/`

---

## 📊 ОТЧЁТЫ О СОСТОЯНИИ

### Платформа

- [COMPLIANCE_REPORT.md](COMPLIANCE_REPORT.md) - Compliance score 75.2%, статус всех модулей
- [INDEX.md](INDEX.md) - Общий индекс документации проекта
- [README.md](README.md) - Главный README проекта

### PDCA Система

- [PDCA_FINAL_HONEST_REPORT.md](PDCA_FINAL_HONEST_REPORT.md) - Финальный отчёт о фиксе метрик
- [PDCA_HONEST_STATUS.md](PDCA_HONEST_STATUS.md) - Честный отчёт о проблеме

### Admin Панели

- [ADMIN_PANELS_ANALYSIS.md](ADMIN_PANELS_ANALYSIS.md) - Анализ дублирования (с критической коррекцией)
- ⚠️ **ВАЖНО**: Первая секция содержит коррекцию моего неправильного анализа

---

## 🏗️ АРХИТЕКТУРА

### Общая Архитектура

📁 **docs/architecture/**
- `PLATFORM_ARCHITECTURE.md` - Общая архитектура платформы
- `C4_LEVEL1_SYSTEM_CONTEXT.md` - C4 диаграмма уровня 1
- `C4_LEVEL2_CONTAINERS.md` - C4 диаграмма уровня 2
- `SERVICE_CATALOG.yaml` - Каталог всех сервисов

### Модули

📁 **docs/modules/**

**Intelligent Core:**
- `intelligent-core/workflow_intelligence.md` - Workflow Intelligence + PDCA
- `intelligent-core/ai-foundation.md` - AI Foundation
- `intelligent-core/event-intelligence.md` - Event Intelligence
- `intelligent-core/collective.md` - Collective Agents
- `intelligent-core/community-intelligence.md` - Community Intelligence

**Platform Services:**
- `platform-services/risk-service.md`
- `platform-services/bia-service.md`
- `platform-services/governance-service.md`
- ... (всего 13 сервисов)

**Infrastructure:**
- `infrastructure/eventbus.md` - EventBus система
- `infrastructure/database.md` - Supabase, PostgreSQL
- `infrastructure/observability.md` - Prometheus, Grafana

---

## 💼 БИЗНЕС АНАЛИЗ

📁 **docs/business-analysis/**
- `COMPLETE_BUSINESS_FLOWS_CATALOG.md` - Полный каталог бизнес-процессов
- `README.md` - Обзор бизнес-анализа

📁 **docs/knowledge-library/**
- `README.md` - Библиотека знаний BCM
- ISO 22301, NIST, WHO материалы

---

## 🔧 ТЕХНИЧЕСКИЕ СПЕЦИФИКАЦИИ

### API

📁 **docs/api/**
- `OPENAPI_SPECIFICATION.md` - OpenAPI спецификация всех сервисов
- `ASYNCAPI_SPECIFICATION.md` - AsyncAPI для EventBus

### Безопасность

📁 **docs/guides/**
- `SECURITY_SPECIFICATIONS.md` - Спецификации безопасности
- `ISO_22301_COMPLIANCE.md` - Соответствие ISO 22301

### Деплоймент

📁 **docs/deployment/**
- `DEPLOYMENT_PORT_MAP.md` - Карта портов всех сервисов
- `INFRASTRUCTURE_DEPLOYMENT_COMPLETE.md` - Инструкции по деплою

---

## 🧪 ТЕСТИРОВАНИЕ

📁 **docs/testing/**
- `TESTING_SPECIFICATION.md` - Спецификация тестирования
- `TEST_AUTOMATION_GUIDE.md` - Руководство по автоматизации тестов

---

## 📈 ИСПОЛНИТЕЛЬНЫЕ ОТЧЁТЫ

📁 **docs/executive/**
- `EXECUTIVE_SUMMARY.md` - Исполнительное резюме проекта
- `COMPLETENESS_ASSESSMENT.md` - Оценка полноты реализации
- `FINAL_CHECKLIST.md` - Финальный чеклист

📁 **docs/reports/**
- `DOCUMENTATION_SUMMARY.md` - Резюме документации
- `EVENT_INTELLIGENCE_COMPLETE.md` - Отчёт Event Intelligence

---

## 🎯 ИНТЕГРАЦИЯ

📁 **docs/integration/**
- `EVENT_BUS_COMPLETE_INTEGRATION.md` - Интеграция EventBus
- `KNOWLEDGE_INTEGRATION_COMPLETE.md` - Интеграция Knowledge Library
- `FINAL_INTEGRATION_SUMMARY.md` - Финальное резюме интеграций

---

## 🔄 PDCA И WORKFLOW

### Документация PDCA

**Код**: `/intelligent-core/workflow_intelligence/`
- `core/pdca_rules.py` - Основной движок PDCA (✅ метрики подключены)
- `metrics/pdca_metrics.py` - Prometheus метрики
- `enable_pdca.py` - Инициализация системы
- `KPI.yaml` - KPI метрики модуля

**Отчёты**:
- [PDCA_FINAL_HONEST_REPORT.md](PDCA_FINAL_HONEST_REPORT.md) - Статус интеграции метрик
- [PDCA_HONEST_STATUS.md](PDCA_HONEST_STATUS.md) - Честный отчёт о проблеме

### Workflow Intelligence

**Файл**: `/intelligent-core/workflow_intelligence/main.py`
- FastAPI сервис
- Порт: 8007
- Endpoints: `/workflows`, `/pdca`, `/metrics`, `/health`

---

## 🖥️ ADMIN ПАНЕЛЬ

### Структура

**Основная версия** (v1 полная): `/interface/admin_panel/`
**Экспериментальная**: `/interface/admin-control-center/` (архивировать)

### Документация

- [ADMIN_PANEL_CONSOLIDATION_PLAN.md](ADMIN_PANEL_CONSOLIDATION_PLAN.md) - План консолидации
- [ADMIN_PANELS_ANALYSIS.md](ADMIN_PANELS_ANALYSIS.md) - Анализ различий
- [TZ_MONITORING_ADMIN_PANEL.md](TZ_MONITORING_ADMIN_PANEL.md) - ТЗ мониторинга

### Запуск

```bash
cd /Users/MD/AI-Platform-ISO/interface/admin_panel
npm install
npm run dev
# http://localhost:3000
```

---

## 📊 МОНИТОРИНГ И OBSERVABILITY

### Существующая Инфраструктура

- **Prometheus**: http://localhost:9090 - Сбор метрик
- **Grafana**: http://localhost:3001 - Визуализация
- **Loki**: http://localhost:3100 - Логи
- **Tempo**: http://localhost:3200 - Трейсинг
- **AlertManager**: http://localhost:9093 - Алерты

### Dashboards

📁 **infrastructure/observability/grafana/dashboards/**
- `bcm-overview.json`
- `services-monitoring.json`
- `performance-metrics.json`
- `event-intelligence.json`

### KPI Files

Каждый модуль имеет `KPI.yaml`:
- Определяет метрики модуля
- Prometheus metric names
- Целевые значения (targets)

**Пример**: `/intelligent-core/workflow_intelligence/KPI.yaml`

---

## 🔍 ПОИСК ПО ТИПУ ЗАДАЧИ

### Хочу Начать Разработку

1. Прочитать [SESSION_SUMMARY_2025-10-09.md](SESSION_SUMMARY_2025-10-09.md)
2. Выполнить [ADMIN_PANEL_CONSOLIDATION_PLAN.md](ADMIN_PANEL_CONSOLIDATION_PLAN.md)
3. Начать реализацию по [TZ_MONITORING_ADMIN_PANEL.md](TZ_MONITORING_ADMIN_PANEL.md)

### Хочу Понять Архитектуру

1. `docs/architecture/PLATFORM_ARCHITECTURE.md`
2. `docs/architecture/SERVICE_CATALOG.yaml`
3. `docs/modules/intelligent-core/README.md`

### Хочу Добавить Метрики

1. Изучить `KPI.yaml` существующего модуля
2. Посмотреть `/intelligent-core/workflow_intelligence/metrics/pdca_metrics.py`
3. Прочитать [PDCA_FINAL_HONEST_REPORT.md](PDCA_FINAL_HONEST_REPORT.md)

### Хочу Настроить Деплоймент

1. `docs/deployment/DEPLOYMENT_PORT_MAP.md`
2. `docs/deployment/INFRASTRUCTURE_DEPLOYMENT_COMPLETE.md`
3. `docker-compose.yml` (корневая директория)

### Хочу Понять Бизнес-Процессы

1. `docs/business-analysis/COMPLETE_BUSINESS_FLOWS_CATALOG.md`
2. `docs/knowledge-library/README.md`
3. `docs/guides/ISO_22301_COMPLIANCE.md`

---

## 🚀 БЫСТРЫЙ СТАРТ

### 1. Запустить Инфраструктуру

```bash
cd /Users/MD/AI-Platform-ISO
docker-compose up -d prometheus grafana loki tempo alertmanager
```

### 2. Запустить Backend Сервисы

```bash
# Workflow Intelligence (включая PDCA)
cd intelligent-core/workflow_intelligence
python enable_pdca.py

# Community Intelligence
cd ../community_intelligence
python main.py

# И так далее для других сервисов...
```

### 3. Запустить Admin Панель

```bash
cd interface/admin_panel
npm install  # Первый раз
npm run dev
```

### 4. Проверить Метрики

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001
- Admin Panel: http://localhost:3000

---

## 📞 КУДА ОБРАЩАТЬСЯ ПРИ ПРОБЛЕМАХ

### Метрики не собираются
→ Проверить [PDCA_FINAL_HONEST_REPORT.md](PDCA_FINAL_HONEST_REPORT.md)
→ Проверить что сервис экспортирует `/metrics` endpoint

### Admin панель не запускается
→ [ADMIN_PANEL_CONSOLIDATION_PLAN.md](ADMIN_PANEL_CONSOLIDATION_PLAN.md)
→ Проверить `npm install` выполнен

### Не понимаю архитектуру
→ `docs/architecture/PLATFORM_ARCHITECTURE.md`
→ [SESSION_SUMMARY_2025-10-09.md](SESSION_SUMMARY_2025-10-09.md)

### Нужно реализовать мониторинг
→ [TZ_MONITORING_ADMIN_PANEL.md](TZ_MONITORING_ADMIN_PANEL.md)
→ [ADMIN_PANEL_CONSOLIDATION_PLAN.md](ADMIN_PANEL_CONSOLIDATION_PLAN.md)

### Нужен статус модуля
→ [COMPLIANCE_REPORT.md](COMPLIANCE_REPORT.md)
→ Проверить `KPI.yaml` модуля

---

## 🎯 ПРИОРИТЕТЫ НА БЛИЖАЙШЕЕ ВРЕМЯ

### Высокий Приоритет

1. ✅ **PDCA Метрики** - ИСПРАВЛЕНО
2. ⏳ **Консолидация Admin Панелей** - План готов, ожидает выполнения
3. 📋 **Реализация Мониторинга** - ТЗ готово, можно начинать

### Средний Приоритет

4. ⚠️ **Добавить /metrics в модули с низким compliance** (50-65% score)
   - expertise-center
   - orchestration
   - knowledge-system
   - shared
   - simulation

5. 📊 **Dashboard Hub** (модуль 1 из ТЗ мониторинга)

### Низкий Приоритет

6. 🔔 **Alert Management** (модуль 3)
7. 📈 **PDCA Analytics** (модуль 4)
8. 📝 **Configuration Management** (модуль 2)

---

## 📚 ПОЛЕЗНЫЕ КОМАНДЫ

### Проверка Статуса

```bash
# Проверить compliance
python infrastructure/observability/services/compliance-monitoring/check_compliance.py

# Проверить все метрики
curl http://localhost:9090/api/v1/targets

# Проверить здоровье сервисов
for port in 8001 8002 8003 8004 8005 8006 8007; do
  curl -s http://localhost:$port/health || echo "Port $port: DOWN"
done
```

### Логи

```bash
# Логи Docker сервисов
docker-compose logs -f prometheus grafana

# Логи Python сервисов
tail -f intelligent-core/*/logs/*.log
```

### Разработка

```bash
# Обновить документацию модуля
python infrastructure/tools/update-docs.sh

# Генерация архитектурных диаграмм
python infrastructure/tools/generate-architecture-diagrams.py
```

---

## 🔗 ВНЕШНИЕ РЕСУРСЫ

### Стандарты

- [ISO 22301:2019](https://www.iso.org/standard/75106.html) - Business Continuity
- [NIST SP 800-34](https://csrc.nist.gov/publications/detail/sp/800-34/rev-1/final) - Contingency Planning

### Технологии

- [Prometheus Docs](https://prometheus.io/docs/)
- [Grafana Docs](https://grafana.com/docs/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React + MUI](https://mui.com/)

---

## 📋 CHANGELOG

### 2025-10-09
- ✅ Исправлена интеграция PDCA метрик
- ✅ Создано ТЗ системы мониторинга (126KB)
- ✅ Создан план консолидации admin панелей
- ⚠️ Исправлен неправильный анализ admin панелей
- 📄 Создан этот Quick Reference Index

---

**Последнее обновление**: 2025-10-09 23:55
**Статус**: Актуально
**Следующий шаг**: Консолидация admin панелей или начало реализации мониторинга
