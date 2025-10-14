# 📊 ТЗ: Система Мониторинга и Административная Панель

**Проект**: AI Platform ISO 22301 - Unified Monitoring & Administration
**Версия**: 1.0.1 (Updated)
**Дата**: 2025-10-09
**Статус**: Требует реализации

---

## ⚠️ ВАЖНОЕ ОБНОВЛЕНИЕ (2025-10-09 23:45)

**КОРРЕКЦИЯ ПУТЕЙ К ADMIN ПАНЕЛИ**:

В оригинальной версии этого ТЗ были указаны пути к `/interface/admin-control-center/`.

**ЭТО НЕПРАВИЛЬНО!**

**ПРАВИЛЬНЫЙ путь для реализации**: `/interface/admin_panel/`

Это полная версия v1 проекта, которая должна быть основой для интеграции мониторинга.

Все упоминания `admin-control-center` в этом документе следует читать как `admin_panel`.

---

## 🎯 Цель Проекта

Создать **единую административную панель** для управления и мониторинга всей платформы BCM с возможностью:
- Визуализации метрик в реальном времени (Prometheus + Grafana)
- Управления конфигурациями сервисов
- Мониторинга PDCA циклов
- Настройки алертов и уведомлений
- Управления пользователями и правами
- Просмотра логов и трейсинга
- Управления инфраструктурой

---

## 📋 Содержание

1. [Общая Архитектура](#общая-архитектура)
2. [Компоненты Системы](#компоненты-системы)
3. [Функциональные Требования](#функциональные-требования)
4. [Технический Стек](#технический-стек)
5. [API Спецификация](#api-спецификация)
6. [UI/UX Дизайн](#uiux-дизайн)
7. [Этапы Реализации](#этапы-реализации)
8. [Безопасность](#безопасность)

---

## 🏗️ Общая Архитектура

### Существующая инфраструктура (что уже есть):

```
┌─────────────────────────────────────────────────────────────┐
│                    Существующие Компоненты                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ✅ Prometheus (port 9090)                                   │
│     - Сбор метрик из всех сервисов                           │
│     - 50+ метрик (BCM, PDCA, EventBus, Services)            │
│                                                               │
│  ✅ Grafana (port 3001)                                      │
│     - 4 dashboard (BCM, Services, Performance, Events)       │
│     - Визуализация метрик                                    │
│                                                               │
│  ✅ Loki (port 3100)                                         │
│     - Централизованные логи                                  │
│                                                               │
│  ✅ Tempo (port 3200)                                        │
│     - Distributed tracing                                    │
│                                                               │
│  ✅ AlertManager (port 9093)                                 │
│     - Уведомления и алерты                                   │
│                                                               │
│  ✅ PostgreSQL (Supabase)                                    │
│     - PDCA cycles, events, metrics history                   │
│                                                               │
│  ✅ Redis                                                    │
│     - Кэш, EventBus backend                                  │
│                                                               │
│  ✅ Admin Control Center UI (React + MUI)                   │
│     - Существующий интерфейс управления                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Новая архитектура (что нужно добавить):

```
┌───────────────────────────────────────────────────────────────────┐
│                     MONITORING ADMIN PANEL                         │
│                        (New React App)                             │
├───────────────────────────────────────────────────────────────────┤
│                                                                     │
│  📊 Dashboard Hub                                                  │
│  ├─ Real-time Metrics (Prometheus)                                │
│  ├─ Grafana Dashboards (Embedded iframes)                         │
│  ├─ PDCA Analytics                                                │
│  ├─ EventBus Monitor                                              │
│  └─ Service Health Map                                            │
│                                                                     │
│  ⚙️ Configuration Management                                       │
│  ├─ Service Configs (CRUD)                                        │
│  ├─ Environment Variables                                         │
│  ├─ Feature Flags                                                 │
│  ├─ Alert Rules                                                   │
│  └─ Prometheus Targets                                            │
│                                                                     │
│  🔔 Alert Management                                               │
│  ├─ Alert Rules Editor                                            │
│  ├─ Notification Channels (Email, Slack, Telegram)               │
│  ├─ Alert History                                                 │
│  └─ Silences & Inhibitions                                        │
│                                                                     │
│  📈 PDCA Analytics                                                 │
│  ├─ Cycles Dashboard                                              │
│  ├─ Quality Trends                                                │
│  ├─ Lessons Learned Browser                                       │
│  └─ Pattern Detection Results                                     │
│                                                                     │
│  🗂️ Logs & Tracing                                                │
│  ├─ Loki Log Viewer                                               │
│  ├─ Tempo Trace Viewer                                            │
│  ├─ Log Search & Filters                                          │
│  └─ Trace Analysis                                                │
│                                                                     │
│  👥 User Management                                                │
│  ├─ Users CRUD                                                    │
│  ├─ Roles & Permissions (RBAC)                                   │
│  ├─ Team Management                                               │
│  └─ Audit Log                                                     │
│                                                                     │
│  🔧 Infrastructure Control                                         │
│  ├─ Service Start/Stop/Restart                                   │
│  ├─ Docker Container Management                                   │
│  ├─ Database Migrations                                           │
│  └─ Backup/Restore                                                │
│                                                                     │
└───────────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────┐
│                     MONITORING BACKEND API                         │
│                   (New FastAPI Service - port 8050)                │
├───────────────────────────────────────────────────────────────────┤
│                                                                     │
│  🔌 API Endpoints                                                  │
│  ├─ /api/metrics/* - Prometheus query proxy                      │
│  ├─ /api/alerts/* - Alert management                             │
│  ├─ /api/configs/* - Configuration CRUD                          │
│  ├─ /api/pdca/* - PDCA analytics                                 │
│  ├─ /api/logs/* - Loki query proxy                               │
│  ├─ /api/traces/* - Tempo query proxy                            │
│  ├─ /api/services/* - Service control                            │
│  └─ /api/users/* - User management                               │
│                                                                     │
│  🔐 Authentication & Authorization                                 │
│  ├─ JWT tokens                                                    │
│  ├─ RBAC (Role-Based Access Control)                             │
│  ├─ Keycloak integration                                          │
│  └─ API key management                                            │
│                                                                     │
│  📊 Data Aggregation                                               │
│  ├─ Prometheus PromQL queries                                    │
│  ├─ PostgreSQL analytics queries                                 │
│  ├─ Redis caching layer                                          │
│  └─ Real-time WebSocket updates                                  │
│                                                                     │
└───────────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────┐
│                      EXISTING INFRASTRUCTURE                       │
├───────────────────────────────────────────────────────────────────┤
│  Prometheus | Grafana | Loki | Tempo | PostgreSQL | Redis         │
└───────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Компоненты Системы

### 1. Monitoring Backend API (NEW)

**Технологии**: FastAPI + Python 3.11+
**Порт**: 8050
**Расположение**: `/infrastructure/observability/admin-api/`

**Ответственность**:
- Proxy для Prometheus/Grafana/Loki/Tempo
- CRUD операции над конфигурациями
- Аутентификация и авторизация
- WebSocket для real-time updates
- Интеграция с PDCA system
- Управление алертами

### 2. Monitoring Admin Panel (NEW)

**Технологии**: React 18 + TypeScript + MUI + TailwindCSS
**Порт**: 3002 (dev), встраивается в admin-control-center
**Расположение**: `/interface/admin-control-center/src/pages/monitoring/`

**Ответственность**:
- UI для всех функций мониторинга
- Интерактивные дашборды
- Конфигурация в реальном времени
- Управление пользователями
- Просмотр логов и трейсов

### 3. Monitoring Configuration Store (NEW)

**Технологии**: PostgreSQL (existing Supabase)
**Schema**: `monitoring` schema

**Хранит**:
- Service configurations
- Alert rules
- User preferences
- Dashboard layouts
- Notification channels

---

## 📝 Функциональные Требования

### 1. Dashboard Hub 📊

#### 1.1 Real-time Metrics Overview

**Требования**:
- [ ] Отображение ключевых метрик платформы в реальном времени
- [ ] Автообновление каждые 5 секунд
- [ ] Настраиваемый период времени (1h, 6h, 24h, 7d, 30d)
- [ ] Drill-down по каждой метрике

**Метрики для отображения**:
```
Система:
├─ Total Requests/sec
├─ Error Rate (%)
├─ Avg Response Time (ms)
├─ Active Services (count)
├─ CPU Usage (%)
├─ Memory Usage (%)
└─ Database Connections (active/total)

PDCA:
├─ Cycles Completed Today
├─ Average Quality Score
├─ Lessons Learned (total)
├─ Patterns Detected (total)
└─ Current Active Cycles

EventBus:
├─ Events/sec (published)
├─ Events/sec (consumed)
├─ Queue Length
└─ Processing Latency (avg)

Services:
└─ [For each service]
    ├─ Status (healthy/degraded/down)
    ├─ Requests/min
    ├─ Error Rate
    └─ Response Time (p95)
```

#### 1.2 Grafana Dashboard Embed

**Требования**:
- [ ] Встраивание существующих Grafana dashboards через iframe
- [ ] Single Sign-On (SSO) с Grafana
- [ ] Быстрое переключение между дашбордами
- [ ] Full-screen режим

**Dashboards для встраивания**:
1. BCM Platform Overview
2. Service Performance
3. Event Analytics
4. Gateway Metrics
5. Database Performance
6. **NEW: PDCA Analytics Dashboard** (создать)

#### 1.3 Service Health Map

**Требования**:
- [ ] Визуальная карта всех сервисов платформы
- [ ] Статус каждого сервиса (🟢 healthy / 🟡 degraded / 🔴 down / ⚪ unknown)
- [ ] Зависимости между сервисами (граф)
- [ ] Клик на сервис → подробная информация

**Пример визуализации**:
```
┌─────────────┐     ┌─────────────┐
│  Gateway    │────▶│  EventBus   │
│    🟢       │     │    🟢       │
└─────────────┘     └─────────────┘
       │                    │
       ▼                    ▼
┌─────────────┐     ┌─────────────┐
│ Workflow    │     │  Community  │
│ Intelligence│     │ Intelligence│
│    🟢       │     │    🟡       │
└─────────────┘     └─────────────┘
       │                    │
       ▼                    ▼
┌─────────────┐     ┌─────────────┐
│ PostgreSQL  │     │   Redis     │
│    🟢       │     │    🟢       │
└─────────────┘     └─────────────┘
```

---

### 2. Configuration Management ⚙️

#### 2.1 Service Configuration Editor

**Требования**:
- [ ] CRUD операции над конфигурациями сервисов
- [ ] JSON/YAML редактор с подсветкой синтаксиса
- [ ] Валидация схем (JSON Schema)
- [ ] История изменений (audit trail)
- [ ] Rollback к предыдущей версии
- [ ] Применение изменений без перезапуска (hot reload)

**UI Компоненты**:
```tsx
<ServiceConfigEditor>
  <ServiceSelector services={allServices} />
  <ConfigEditor
    value={currentConfig}
    schema={configSchema}
    onChange={handleChange}
    validate={true}
  />
  <VersionHistory versions={configVersions} />
  <ActionButtons>
    <Button variant="primary" onClick={saveConfig}>Save</Button>
    <Button variant="secondary" onClick={applyHotReload}>Apply & Reload</Button>
    <Button variant="ghost" onClick={rollback}>Rollback</Button>
  </ActionButtons>
</ServiceConfigEditor>
```

#### 2.2 Environment Variables Manager

**Требования**:
- [ ] Просмотр всех ENV переменных по сервисам
- [ ] Добавление/редактирование/удаление ENV
- [ ] Секреты хранятся зашифрованно
- [ ] Поддержка .env файлов (upload/download)
- [ ] Применение изменений с перезапуском сервиса

**Структура**:
```
Service: workflow-intelligence
├─ DATABASE_URL: ******** (secret)
├─ REDIS_URL: redis://localhost:6379 (public)
├─ PORT: 8037 (public)
├─ LOG_LEVEL: INFO (public)
└─ TENANT_ID: default-tenant (public)

[Add Variable] [Import .env] [Export .env] [Apply Changes]
```

#### 2.3 Feature Flags Control

**Требования**:
- [ ] Включение/выключение фич в реальном времени
- [ ] Процент rollout (A/B тестирование)
- [ ] Targeting по пользователям/организациям
- [ ] История изменений флагов

**Пример флагов**:
```
Feature: PDCA_RULES_ENGINE
├─ Status: ✅ Enabled
├─ Rollout: 100% (all users)
├─ Environment: production
└─ Last changed: 2025-10-09 by admin@platform.com

Feature: EXPERIMENTAL_AI_RECOMMENDATIONS
├─ Status: 🟡 Partial
├─ Rollout: 25% (beta users only)
├─ Environment: staging
└─ Last changed: 2025-10-08 by developer@platform.com

[Create New Flag] [Export Flags]
```

---

### 3. Alert Management 🔔

#### 3.1 Alert Rules Editor

**Требования**:
- [ ] Визуальный редактор правил алертов (no-code)
- [ ] Prometheus PromQL запросы с подсказками
- [ ] Настройка порогов (thresholds)
- [ ] Severity levels (critical, warning, info)
- [ ] Test alert перед сохранением

**UI Flow**:
```
1. Choose Metric: [Dropdown: pdca_quality_score]
2. Condition: [Dropdown: less than] [Input: 70]
3. Duration: Alert if condition lasts [Input: 5] [Dropdown: minutes]
4. Severity: [Radio: Critical / Warning / Info]
5. Message: Quality score dropped below 70% for {module}
6. Notification Channels: [✓ Email] [✓ Slack] [ ] Telegram
7. [Test Alert] [Save Rule]
```

**Пример правила**:
```yaml
alert: PDCALowQualityScore
expr: pdca_quality_score < 70
for: 5m
severity: warning
annotations:
  summary: "PDCA quality score below threshold"
  description: "Module {{ $labels.module }} quality score is {{ $value }}"
labels:
  team: platform
  component: pdca
actions:
  - notify: email
  - notify: slack
```

#### 3.2 Notification Channels

**Требования**:
- [ ] Email notifications (SMTP)
- [ ] Slack webhooks
- [ ] Telegram bot
- [ ] Webhook (custom HTTP endpoint)
- [ ] Тестирование канала перед сохранением

**Интеграции**:
```
Email Configuration:
├─ SMTP Host: smtp.gmail.com
├─ Port: 587
├─ Username: alerts@platform.com
├─ Password: ********
└─ [Test Email]

Slack Configuration:
├─ Webhook URL: https://hooks.slack.com/services/T00/B00/XX
├─ Channel: #alerts
├─ Username: Platform Alerts Bot
└─ [Test Message]

Telegram Configuration:
├─ Bot Token: ********
├─ Chat ID: -1001234567890
└─ [Test Message]
```

#### 3.3 Alert History & Management

**Требования**:
- [ ] Список всех активных алертов
- [ ] История алертов (archive)
- [ ] Фильтрация по severity/service/date
- [ ] Acknowledge alert (mark as seen)
- [ ] Silence alert (mute for period)
- [ ] Alert annotations (комментарии)

**UI**:
```
Active Alerts (3)
┌─────────────────────────────────────────────────────────────┐
│ 🔴 CRITICAL | PDCA Quality Score < 70                       │
│    Module: bia | Score: 65.2 | Duration: 12m                │
│    [Acknowledge] [Silence 1h] [View Details]                │
├─────────────────────────────────────────────────────────────┤
│ 🟡 WARNING | High EventBus Queue Length                     │
│    Queue: workflow.events | Length: 1523 | Duration: 5m     │
│    [Acknowledge] [Silence 30m] [View Details]               │
├─────────────────────────────────────────────────────────────┤
│ 🟡 WARNING | Service Response Time High                     │
│    Service: workflow-intelligence | P95: 856ms | Duration: 3m│
│    [Acknowledge] [Silence 15m] [View Details]               │
└─────────────────────────────────────────────────────────────┘

[Filters: All Services ▼ | All Severities ▼ | Last 24h ▼]
```

---

### 4. PDCA Analytics 📈

#### 4.1 PDCA Cycles Dashboard

**Требования**:
- [ ] Список всех PDCA циклов с фильтрацией
- [ ] Timeline визуализация
- [ ] Статистика по модулям
- [ ] Drill-down в детали цикла

**Визуализация**:
```
PDCA Cycles Overview
┌─────────────────────────────────────────────────────────────┐
│ Total Cycles: 1,234 | Completed: 1,180 | In Progress: 54   │
│ Avg Quality Score: 87.5 | Avg Duration: 12.3 min            │
└─────────────────────────────────────────────────────────────┘

By Module:
├─ BIA: 456 cycles (Avg Quality: 89.2)
├─ Risk: 342 cycles (Avg Quality: 85.7)
├─ Compliance: 289 cycles (Avg Quality: 88.1)
└─ Response: 147 cycles (Avg Quality: 86.3)

Recent Cycles:
┌─────────────────────────────────────────────────────────────┐
│ workflow-123 | bia | ✅ Completed | Quality: 92 | 10m      │
│ [View Details] [Export Report]                              │
├─────────────────────────────────────────────────────────────┤
│ workflow-124 | risk | 🟡 In Progress | CHECK phase | 5m    │
│ [View Details] [Monitor Live]                               │
└─────────────────────────────────────────────────────────────┘
```

#### 4.2 Quality Trends Analysis

**Требования**:
- [ ] Графики качества по времени
- [ ] Сравнение модулей
- [ ] Тренды (improving/declining)
- [ ] Аномалии detection

**Charts**:
```
Quality Score Over Time (Last 30 Days)
  100 ┤                                          ●
   90 ┤              ●        ●    ●        ●  ●
   80 ┤        ●   ●    ●  ●    ●    ●  ●
   70 ┤    ●  ●
   60 ┤
      └────────────────────────────────────────────
       Oct 1        Oct 15        Oct 30

[BIA: 89.2 ↗] [Risk: 85.7 →] [Compliance: 88.1 ↗] [Response: 86.3 ↘]
```

#### 4.3 Lessons Learned Browser

**Требования**:
- [ ] Полнотекстовый поиск по урокам
- [ ] Фильтрация по модулю/quality/date
- [ ] Экспорт в PDF/Markdown
- [ ] Категоризация уроков

**UI**:
```
Lessons Learned (Total: 3,456)

Search: [_________________________] [🔍]

Filters: Module [All ▼] | Quality Score [>70 ▼] | Date [Last 30d ▼]

Results (showing 1-10 of 245):
┌─────────────────────────────────────────────────────────────┐
│ 🎯 Lesson #1234 | BIA Module | Quality: 95                  │
│ "Stakeholder workshops increase assessment quality by 30%"  │
│ Pattern: early_stakeholder_engagement | Date: 2025-10-05    │
│ Applied in: 15 workflows | Success rate: 94%                │
│ [View Full Lesson] [Apply to New Workflow] [Export PDF]    │
└─────────────────────────────────────────────────────────────┘
```

#### 4.4 Pattern Detection Results

**Требования**:
- [ ] Визуализация обнаруженных паттернов
- [ ] Частота встречаемости
- [ ] Корреляция с качеством
- [ ] Рекомендации на основе паттернов

---

### 5. Logs & Tracing 🗂️

#### 5.1 Loki Log Viewer

**Требования**:
- [ ] Real-time log streaming
- [ ] Поиск по тексту (regex)
- [ ] Фильтры по service/level/time
- [ ] Подсветка синтаксиса
- [ ] Export logs (JSON/CSV/TXT)

**UI**:
```
Log Viewer
┌─────────────────────────────────────────────────────────────┐
│ Service: [workflow-intelligence ▼] | Level: [All ▼]        │
│ Search: [error|exception] [🔍] | Time: [Last 1h ▼]         │
├─────────────────────────────────────────────────────────────┤
│ 2025-10-09 23:15:42 | INFO  | PDCA cycle started          │
│ 2025-10-09 23:15:45 | DEBUG | Querying CaseLibrary        │
│ 2025-10-09 23:15:46 | ERROR | Failed to connect to Redis  │
│   ↳ ConnectionError: [Errno 111] Connection refused        │
│   ↳ Stack trace: ...                                        │
│ 2025-10-09 23:15:47 | WARN  | Retrying connection...      │
│ 2025-10-09 23:15:48 | INFO  | Connection restored         │
└─────────────────────────────────────────────────────────────┘
[Auto-scroll ✓] [Tail mode] [Export]
```

#### 5.2 Tempo Trace Viewer

**Требования**:
- [ ] Визуализация distributed traces
- [ ] Waterfall диаграммы
- [ ] Span details
- [ ] Trace search по trace ID или операции

---

### 6. User Management 👥

#### 6.1 Users CRUD

**Требования**:
- [ ] Создание/редактирование/удаление пользователей
- [ ] Импорт пользователей (CSV)
- [ ] Блокировка/разблокировка аккаунтов
- [ ] Сброс паролей

#### 6.2 Roles & Permissions (RBAC)

**Требования**:
- [ ] Роли: Admin, Operator, Viewer, Auditor
- [ ] Гранулярные права (permissions)
- [ ] Назначение ролей пользователям
- [ ] Custom роли

**Предопределенные роли**:
```
Admin (полный доступ):
├─ View all metrics ✓
├─ Edit configurations ✓
├─ Manage alerts ✓
├─ Manage users ✓
├─ Control services ✓
└─ View audit logs ✓

Operator (операционный доступ):
├─ View all metrics ✓
├─ Edit configurations ✓
├─ Manage alerts ✓
├─ Manage users ✗
├─ Control services ✓
└─ View audit logs ✗

Viewer (только чтение):
├─ View all metrics ✓
├─ Edit configurations ✗
├─ Manage alerts ✗
├─ Manage users ✗
├─ Control services ✗
└─ View audit logs ✗

Auditor (аудит):
├─ View all metrics ✓
├─ Edit configurations ✗
├─ Manage alerts ✗
├─ Manage users ✗
├─ Control services ✗
└─ View audit logs ✓
```

---

### 7. Infrastructure Control 🔧

#### 7.1 Service Control Panel

**Требования**:
- [ ] Start/Stop/Restart сервисов
- [ ] View service status
- [ ] View service logs (last 100 lines)
- [ ] View service environment variables
- [ ] Health check сервиса

**UI**:
```
Services (12 total)
┌─────────────────────────────────────────────────────────────┐
│ workflow-intelligence | 🟢 Running | Port: 8037             │
│ Uptime: 3d 12h | Memory: 245MB / 512MB | CPU: 12%          │
│ [Restart] [Stop] [View Logs] [Config] [Health Check]       │
├─────────────────────────────────────────────────────────────┤
│ community-intelligence | 🟡 Degraded | Port: 8033          │
│ Uptime: 1d 5h | Memory: 487MB / 512MB | CPU: 78%           │
│ ⚠️ High memory usage!                                       │
│ [Restart] [Stop] [View Logs] [Config] [Health Check]       │
└─────────────────────────────────────────────────────────────┘
```

#### 7.2 Docker Container Management

**Требования**:
- [ ] Список всех контейнеров
- [ ] Start/Stop/Remove контейнеров
- [ ] View контейнер logs
- [ ] Exec команд в контейнере (terminal)

#### 7.3 Database Migrations

**Требования**:
- [ ] Список всех миграций
- [ ] Текущая версия схемы
- [ ] Применение новых миграций
- [ ] Rollback миграций
- [ ] Тестирование миграций (dry-run)

---

## 🛠️ Технический Стек

### Backend (Monitoring Admin API)

```python
# Core
FastAPI==0.109.0
uvicorn[standard]==0.27.0
python==3.11+

# Database
asyncpg==0.29.0
SQLAlchemy==2.0.25
alembic==1.13.1

# Monitoring Integrations
prometheus-client==0.19.0
prometheus-api-client==0.5.3  # For PromQL queries
httpx==0.26.0  # For API calls to Grafana/Loki/Tempo

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-keycloak==3.8.0

# WebSocket
websockets==12.0
python-socketio==5.11.0

# Redis
redis==5.0.1
aioredis==2.0.1

# Utilities
pydantic==2.5.3
python-dotenv==1.0.0
loguru==0.7.2
```

### Frontend (Monitoring Admin Panel)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "@mui/material": "^7.3.2",
    "recharts": "^3.2.1",
    "axios": "^1.6.0",
    "socket.io-client": "^4.8.1",
    "react-query": "^5.89.0",
    "zustand": "^4.4.0",
    "date-fns": "^3.0.6",
    "monaco-editor": "^0.45.0",
    "react-json-view": "^1.21.3",
    "react-virtualized": "^9.22.5"
  }
}
```

---

## 🔌 API Спецификация

### Base URL
```
http://localhost:8050/api/v1
```

### Authentication
```
Authorization: Bearer <JWT_TOKEN>
```

### Endpoints

#### Metrics API

```typescript
// Get real-time metrics
GET /metrics/current
Response: {
  system: {
    requests_per_sec: number,
    error_rate: number,
    avg_response_time: number,
    active_services: number
  },
  pdca: {
    cycles_today: number,
    avg_quality_score: number,
    lessons_learned: number,
    patterns_detected: number
  }
}

// Query Prometheus (PromQL)
POST /metrics/query
Body: {
  query: string,  // PromQL query
  start?: string, // ISO timestamp
  end?: string,   // ISO timestamp
  step?: string   // e.g., "5m"
}
Response: {
  status: "success",
  data: {
    resultType: "matrix" | "vector",
    result: Array<{...}>
  }
}

// Get service health
GET /metrics/services/health
Response: {
  services: Array<{
    name: string,
    status: "healthy" | "degraded" | "down",
    uptime: number,
    last_check: string
  }>
}
```

#### Configuration API

```typescript
// Get service config
GET /configs/:service_name
Response: {
  service: string,
  config: object,
  version: number,
  updated_at: string
}

// Update service config
PUT /configs/:service_name
Body: {
  config: object,
  apply_immediately: boolean
}
Response: {
  success: boolean,
  version: number
}

// Get config history
GET /configs/:service_name/history
Response: {
  versions: Array<{
    version: number,
    config: object,
    updated_by: string,
    updated_at: string
  }>
}

// Rollback config
POST /configs/:service_name/rollback
Body: {
  version: number
}
```

#### Alert API

```typescript
// Get all alert rules
GET /alerts/rules
Response: {
  rules: Array<{
    id: string,
    name: string,
    expr: string,
    severity: "critical" | "warning" | "info",
    enabled: boolean,
    channels: string[]
  }>
}

// Create alert rule
POST /alerts/rules
Body: {
  name: string,
  expr: string,
  duration: string,
  severity: string,
  message: string,
  channels: string[]
}

// Get active alerts
GET /alerts/active
Response: {
  alerts: Array<{
    id: string,
    rule: string,
    severity: string,
    started_at: string,
    labels: object,
    annotations: object
  }>
}

// Acknowledge alert
POST /alerts/:alert_id/acknowledge

// Silence alert
POST /alerts/:alert_id/silence
Body: {
  duration: string  // e.g., "1h"
}
```

#### PDCA API

```typescript
// Get PDCA cycles
GET /pdca/cycles
Query: {
  module?: string,
  from?: string,
  to?: string,
  limit?: number
}
Response: {
  cycles: Array<{
    id: string,
    workflow_id: string,
    module: string,
    quality_score: number,
    started_at: string,
    completed_at: string
  }>,
  total: number
}

// Get PDCA statistics
GET /pdca/statistics
Query: {
  module?: string,
  period?: "day" | "week" | "month"
}
Response: {
  total_cycles: number,
  avg_quality_score: number,
  lessons_learned: number,
  patterns_detected: number
}

// Get lessons learned
GET /pdca/lessons
Query: {
  module?: string,
  min_quality?: number,
  search?: string
}
Response: {
  lessons: Array<{
    id: string,
    module: string,
    lesson: string,
    quality_score: number,
    created_at: string
  }>
}
```

#### Logs API

```typescript
// Query logs (Loki)
POST /logs/query
Body: {
  query: string,  // LogQL query
  limit: number,
  start?: string,
  end?: string
}
Response: {
  streams: Array<{
    stream: object,
    values: Array<[timestamp, log_line]>
  }>
}

// Tail logs (WebSocket)
WS /logs/tail/:service
```

#### Services API

```typescript
// Get all services
GET /services
Response: {
  services: Array<{
    name: string,
    status: string,
    port: number,
    uptime: number
  }>
}

// Control service
POST /services/:service_name/:action
Params: action = "start" | "stop" | "restart"
Response: {
  success: boolean,
  status: string
}

// Get service logs
GET /services/:service_name/logs
Query: {
  lines?: number,  // default 100
  follow?: boolean
}
```

#### Users API

```typescript
// Get all users
GET /users
Response: {
  users: Array<{
    id: string,
    email: string,
    role: string,
    created_at: string,
    last_login: string
  }>
}

// Create user
POST /users
Body: {
  email: string,
  password: string,
  role: string
}

// Update user
PUT /users/:user_id
Body: {
  email?: string,
  role?: string,
  is_active?: boolean
}

// Delete user
DELETE /users/:user_id
```

---

## 🎨 UI/UX Дизайн

### Layout Structure

```
┌───────────────────────────────────────────────────────────┐
│  Top Navigation Bar                                        │
│  [Logo] [Dashboard] [Metrics] [PDCA] [Alerts] [Users] [@] │
├─────────┬─────────────────────────────────────────────────┤
│ Side    │                                                 │
│ Menu    │           Main Content Area                     │
│         │                                                 │
│ 📊 Dash │                                                 │
│ 📈 Metr │                                                 │
│ 🔄 PDCA │                                                 │
│ 🔔 Aler │                                                 │
│ ⚙️  Conf│                                                 │
│ 🗂️  Logs│                                                 │
│ 👥 User │                                                 │
│ 🔧 Infr │                                                 │
│         │                                                 │
└─────────┴─────────────────────────────────────────────────┘
```

### Color Scheme

```css
:root {
  /* Status Colors */
  --status-healthy: #10b981;    /* Green */
  --status-warning: #f59e0b;    /* Yellow */
  --status-error: #ef4444;      /* Red */
  --status-unknown: #6b7280;    /* Gray */

  /* Severity Colors */
  --severity-critical: #dc2626;
  --severity-warning: #f59e0b;
  --severity-info: #3b82f6;

  /* UI Colors */
  --primary: #3b82f6;
  --secondary: #8b5cf6;
  --background: #0f172a;
  --surface: #1e293b;
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
}
```

### Component Library

**Используем существующие компоненты**:
- MUI для основных компонентов
- Recharts для графиков
- Monaco Editor для редактирования кода
- React JSON View для просмотра JSON

---

## 📅 Этапы Реализации

### Phase 1: Core Infrastructure (2 weeks)

**Week 1**:
- [ ] Создать Monitoring Backend API (FastAPI)
- [ ] Реализовать аутентификацию (JWT + Keycloak)
- [ ] Создать PostgreSQL schema для конфигураций
- [ ] Proxy endpoints для Prometheus/Grafana

**Week 2**:
- [ ] Создать базовую структуру React app
- [ ] Интегрировать с существующим admin-control-center
- [ ] Реализовать Dashboard Hub (metrics overview)
- [ ] WebSocket для real-time updates

### Phase 2: Configuration & Alerts (2 weeks)

**Week 3**:
- [ ] Configuration Management UI
- [ ] Service config CRUD
- [ ] Environment variables manager
- [ ] Feature flags control

**Week 4**:
- [ ] Alert Management UI
- [ ] Alert rules editor
- [ ] Notification channels setup
- [ ] Alert history & acknowledgment

### Phase 3: PDCA Analytics (1 week)

**Week 5**:
- [ ] PDCA cycles dashboard
- [ ] Quality trends visualization
- [ ] Lessons learned browser
- [ ] Pattern detection results

### Phase 4: Logs & Advanced Features (1 week)

**Week 6**:
- [ ] Loki log viewer
- [ ] Tempo trace viewer
- [ ] Service health map
- [ ] Infrastructure control panel

### Phase 5: User Management & Polish (1 week)

**Week 7**:
- [ ] User CRUD
- [ ] RBAC implementation
- [ ] Audit log
- [ ] UI/UX polish & testing

---

## 🔐 Безопасность

### Authentication

- JWT tokens (access + refresh)
- Integration с Keycloak SSO
- Multi-factor authentication (MFA)
- Session management

### Authorization

- Role-Based Access Control (RBAC)
- Permission-based access to API endpoints
- Row-level security для PostgreSQL queries

### Security Measures

- Rate limiting (per user)
- API key management
- Audit logging всех действий
- HTTPS обязателен в production
- Secrets encryption (Vault integration)

### Compliance

- GDPR compliance для user data
- Audit trail для всех изменений конфигураций
- Data retention policies

---

## 📊 Метрики Успеха

### Технические метрики:
- [ ] API response time < 200ms (p95)
- [ ] UI loading time < 2s
- [ ] WebSocket latency < 100ms
- [ ] 99.9% uptime

### Бизнес-метрики:
- [ ] Сокращение времени реагирования на алерты на 50%
- [ ] Увеличение видимости PDCA циклов
- [ ] Уменьшение времени troubleshooting на 40%

---

## 📦 Deliverables

### Код:
1. `/infrastructure/observability/admin-api/` - Backend API
2. `/interface/admin-control-center/src/pages/monitoring/` - Frontend UI
3. `/infrastructure/observability/database/migrations/` - DB migrations

### Документация:
1. API Documentation (OpenAPI/Swagger)
2. User Guide
3. Admin Guide
4. Development Guide

### Дашборды:
1. PDCA Analytics Dashboard (Grafana)
2. Monitoring Overview Dashboard
3. Custom dashboards по запросу

---

## 🚀 Deployment

### Development:
```bash
# Backend
cd infrastructure/observability/admin-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8050

# Frontend
cd interface/admin-control-center
npm install
npm run dev
```

### Production:
```bash
# Docker Compose
cd infrastructure/observability
docker-compose -f docker-compose.monitoring.yml up -d
docker-compose -f docker-compose.admin-api.yml up -d
```

---

## ✅ Acceptance Criteria

- [ ] Все API endpoints работают и задокументированы
- [ ] UI responsive на всех разрешениях
- [ ] Real-time updates работают через WebSocket
- [ ] Аутентификация и авторизация функционируют
- [ ] Grafana dashboards встраиваются корректно
- [ ] PDCA аналитика отображает актуальные данные
- [ ] Alerts можно создавать/редактировать/удалять
- [ ] Service control работает (start/stop/restart)
- [ ] Logs можно просматривать в реальном времени
- [ ] Конфигурации сохраняются и применяются
- [ ] User management полностью функционален
- [ ] Audit log записывает все действия

---

**Prepared by**: Claude (AI Assistant)
**Date**: 2025-10-09
**Status**: Ready for Review & Implementation
