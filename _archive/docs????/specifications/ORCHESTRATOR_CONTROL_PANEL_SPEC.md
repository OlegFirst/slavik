# ТЗ: Пульт Управления AI Orchestrator

**Дата:** 2025-10-10
**Версия:** 1.0
**Статус:** Ready for Implementation

---

## 1. Обзор

### Цель
Создать административную панель в `/interface/admin_panel` для управления AI Orchestrator в реальном времени с мониторингом производительности, эффективности и возможностью управления.

### Интеграция
- **URL Route:** `/orchestrator`
- **API Backend:** `http://localhost:8050` (AI Orchestrator API)
- **Технологии:** React 18, TypeScript, Tailwind, shadcn/ui, Recharts
- **Обновление:** WebSocket real-time + polling

---

## 2. Структура компонентов

### 2.1. Главный компонент

**Файл:** `/src/pages/OrchestratorControlPanel.tsx`

```typescript
// Главная страница пульта управления
export default function OrchestratorControlPanel() {
  return (
    <div className="orchestrator-control-panel">
      <OrchestratorHeader />
      <div className="grid grid-cols-12 gap-4">
        {/* Левая колонка - Статус и управление */}
        <div className="col-span-3">
          <SystemStatus />
          <QuickActions />
          <ActiveCrises />
        </div>

        {/* Центральная колонка - Метрики и графики */}
        <div className="col-span-6">
          <PerformanceMetrics />
          <DecisionFlow />
          <ServiceHealth />
        </div>

        {/* Правая колонка - Детали и лог */}
        <div className="col-span-3">
          <RecentDecisions />
          <AIExpertsDelegations />
          <AlertsPanel />
        </div>
      </div>

      {/* Нижняя панель - Детальные графики */}
      <DetailedCharts />
    </div>
  );
}
```

---

## 3. Компоненты (14 штук)

### 3.1. OrchestratorHeader
**Файл:** `/src/components/Orchestrator/OrchestratorHeader.tsx`

**Функции:**
- Название страницы "AI Orchestrator Control Panel"
- Статус подключения к API (🟢 Online / 🔴 Offline)
- Кнопка "Emergency Stop" (красная, подтверждение)
- Кнопка "Reload Config"
- Переключатель Auto-Refresh (вкл/выкл)

**UI:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🤖 AI Orchestrator Control Panel    🟢 Online   [Emergency] │
│                                                    [Reload]   │
└─────────────────────────────────────────────────────────────┘
```

**API:**
- `GET /health` - проверка статуса
- `POST /admin/emergency-stop` - аварийная остановка
- `POST /admin/reload-config` - перезагрузка конфига

---

### 3.2. SystemStatus
**Файл:** `/src/components/Orchestrator/SystemStatus.tsx`

**Показатели:**
- **Status:** Healthy / Degraded / Critical (цветной badge)
- **Uptime:** Время работы с момента старта
- **Total Decisions:** Всего решений
- **Success Rate:** Процент успешных (цветной progress bar)

**Компоненты системы (индикаторы):**
- ✅ Context Aggregator
- ✅ Priority Engine
- ✅ Strategy Selector
- ✅ Safety Monitor
- ✅ PDCA Engine
- ✅ Crisis Coordinator
- ✅ Decision Center

**UI:**
```
┌─ System Status ──────────────┐
│ Status: 🟢 Healthy           │
│ Uptime: 3h 24m               │
│                              │
│ Total Decisions: 1,247       │
│ Success Rate: 96.3%          │
│ [████████████░░] 96.3%       │
│                              │
│ Components:                  │
│ ✅ Context Aggregator        │
│ ✅ Priority Engine           │
│ ✅ Strategy Selector         │
│ ✅ Safety Monitor            │
│ ✅ PDCA Engine               │
│ ✅ Crisis Coordinator        │
│ ✅ Decision Center           │
└──────────────────────────────┘
```

**API:**
- `GET /health` - статус компонентов
- `GET /stats` - статистика

---

### 3.3. QuickActions
**Файл:** `/src/components/Orchestrator/QuickActions.tsx`

**Кнопки действий:**
1. **Trigger Evolution** - Запустить цикл эволюции
2. **Clear Cache** - Очистить strategy cache
3. **Test Decision** - Тестовое решение
4. **Export Metrics** - Скачать метрики (JSON)
5. **View Logs** - Открыть логи в модальном окне

**UI:**
```
┌─ Quick Actions ──────────────┐
│ [Trigger Evolution]          │
│ [Clear Cache]                │
│ [Test Decision]              │
│ [Export Metrics]             │
│ [View Logs]                  │
└──────────────────────────────┘
```

**API:**
- `POST /admin/evolve`
- `POST /admin/cache/clear`
- `POST /api/v1/decide` (test)
- `GET /metrics` (export)
- `GET /admin/logs`

---

### 3.4. ActiveCrises
**Файл:** `/src/components/Orchestrator/ActiveCrises.tsx`

**Отображение:**
- Список активных кризисов
- Каждый кризис:
  - ID кризиса
  - Уровень (MAJOR, CRITICAL, CATASTROPHIC)
  - Длительность
  - Статус (ACTIVATING, COORDINATING, RECOVERING)
  - Кнопка "Details"

**UI:**
```
┌─ Active Crises ──────────────┐
│ 🚨 2 Active                  │
│                              │
│ crisis_001                   │
│ 🔴 CRITICAL                  │
│ Duration: 15m 23s            │
│ Status: COORDINATING         │
│ [Details]                    │
│                              │
│ crisis_002                   │
│ 🟠 MAJOR                     │
│ Duration: 3m 45s             │
│ Status: ACTIVATING           │
│ [Details]                    │
└──────────────────────────────┘
```

**API:**
- `GET /admin/stats` - active_crises
- `GET /api/v1/crisis/{id}/status` - детали кризиса

---

### 3.5. PerformanceMetrics
**Файл:** `/src/components/Orchestrator/PerformanceMetrics.tsx`

**4 ключевые метрики (карточки):**

1. **Decision Latency P95**
   - Значение в ms
   - Целевое значение: < 100ms
   - Цветной индикатор (зеленый/желтый/красный)
   - Мини-график (sparkline) за последний час

2. **Auto-Resolution Rate**
   - Значение в %
   - Целевое значение: > 60%
   - Прогресс-бар
   - Тренд (↑↓)

3. **Human Intervention**
   - Значение в %
   - Целевое значение: < 30%
   - Прогресс-бар
   - Тренд (↑↓)

4. **Safety Approval**
   - Значение в %
   - Целевое значение: > 95%
   - Прогресс-бар
   - Тренд (↑↓)

**UI:**
```
┌─────────────────────────────────────────────────────────────┐
│ ⚡ Decision Latency P95  │ 📊 Auto-Resolution  │ 👤 Human   │
│    87.3ms               │    94.2%            │    12.5%   │
│    Target: <100ms       │    Target: >60%     │    <30%    │
│    🟢 Good              │    🟢 Excellent     │    🟢 Good │
│    [mini chart]         │    [████████░]      │    [███░]  │
│────────────────────────────────────────────────────────────│
│ ✅ Safety Approval      │                                   │
│    97.8%                │                                   │
│    Target: >95%         │                                   │
│    🟢 Excellent         │                                   │
└─────────────────────────────────────────────────────────────┘
```

**Источник данных:**
- Prometheus метрики через `/metrics`
- Или кастомный endpoint `/admin/metrics/summary`

---

### 3.6. DecisionFlow
**Файл:** `/src/components/Orchestrator/DecisionFlow.tsx`

**Real-time граф решений:**
- Sankey diagram или Flow diagram
- Показывает поток решений:
  - Входящие ситуации
  - → Priority Assessment
  - → Strategy Selection
  - → Safety Check
  - → Actions (AUTO_RESOLVE, DELEGATE, ESCALATE, etc.)

**Цифры на каждом узле:**
- Количество решений за выбранный период (1h, 6h, 24h)

**UI:**
```
┌─ Decision Flow (Last 1h) ────────────────────────────────┐
│                                                           │
│  Situations (450) ──→ Priority ──→ Strategy ──→ Safety   │
│                         │             │          │       │
│                         ↓             ↓          ↓       │
│                     Critical(45)  Selected    Approved   │
│                     High(180)      (425)       (432)     │
│                     Normal(225)                          │
│                                                           │
│  Actions:                                                │
│    AUTO_RESOLVE: 325 (72%)                              │
│    DELEGATE: 87 (19%)                                   │
│    ESCALATE: 28 (6%)                                    │
│    EMERGENCY_STOP: 2 (0.4%)                             │
│                                                           │
│  [Selector: 1h | 6h | 24h]                              │
└───────────────────────────────────────────────────────────┘
```

**API:**
- Prometheus queries для подсчета по типам

---

### 3.7. ServiceHealth
**Файл:** `/src/components/Orchestrator/ServiceHealth.tsx`

**Статус всех зарегистрированных сервисов:**

Для каждого сервиса:
- Название сервиса
- Статус (HEALTHY, DEGRADED, UNHEALTHY)
- Latency P95
- Circuit Breaker Status (OPEN/CLOSED)
- Last Check (время последней проверки)

**UI:**
```
┌─ Service Health ─────────────────────────────────────────┐
│                                                           │
│ Service         Status      P95 Latency  Circuit Breaker│
│ bia             🟢 Healthy  23ms         CLOSED         │
│ risk            🟢 Healthy  31ms         CLOSED         │
│ planning        🟡 Degraded 89ms         CLOSED         │
│ compliance      🟢 Healthy  18ms         CLOSED         │
│ governance      🟢 Healthy  25ms         CLOSED         │
│ response        🟢 Healthy  42ms         CLOSED         │
│ documents       🟢 Healthy  35ms         CLOSED         │
│ learning        🔴 Unhealthy 245ms       OPEN ⚠️        │
│ validation      🟢 Healthy  28ms         CLOSED         │
│                                                           │
│ Last Update: 2s ago                      [Refresh]       │
└───────────────────────────────────────────────────────────┘
```

**API:**
- Custom endpoint: `GET /admin/services/health`
- Агрегирует данные из ServiceRegistry

---

### 3.8. RecentDecisions
**Файл:** `/src/components/Orchestrator/RecentDecisions.tsx`

**Список последних 10 решений:**

Для каждого решения:
- Timestamp
- Decision ID
- Action Type (badge с цветом)
- Priority
- Confidence (прогресс-бар)
- Latency
- Кнопка "Details"

**UI:**
```
┌─ Recent Decisions ───────────────┐
│                                  │
│ 14:32:15 | dec_001              │
│ AUTO_RESOLVE | HIGH             │
│ Confidence: ██████████░ 92%     │
│ Latency: 78ms                   │
│ [Details]                       │
│ ───────────────────────────────│
│ 14:31:48 | dec_002              │
│ DELEGATE | NORMAL               │
│ Confidence: ████████░░░ 78%     │
│ Latency: 65ms                   │
│ [Details]                       │
│ ───────────────────────────────│
│ 14:31:22 | dec_003              │
│ ESCALATE | CRITICAL             │
│ Confidence: ████░░░░░░░ 45%     │
│ Latency: 123ms                  │
│ [Details]                       │
│                                  │
│ [Load More]                     │
└──────────────────────────────────┘
```

**API:**
- Custom endpoint: `GET /admin/decisions/recent?limit=10`

---

### 3.9. AIExpertsDelegations
**Файл:** `/src/components/Orchestrator/AIExpertsDelegations.tsx`

**Статистика делегирований к AI Experts:**

**3 секции:**

1. **BCM Advisor**
   - Количество делегирований (за час/день)
   - Последняя делегация (время)
   - Типичные задачи

2. **Compliance Auditor**
   - Аналогично

3. **Strategic Planner**
   - Аналогично

**UI:**
```
┌─ AI Experts Delegations ─────────┐
│                                  │
│ 🎓 BCM Advisor                   │
│ Today: 23 delegations            │
│ Last hour: 5                     │
│ Last: 3m ago                     │
│ Common: BCM planning, Recovery   │
│                                  │
│ 📋 Compliance Auditor            │
│ Today: 18 delegations            │
│ Last hour: 3                     │
│ Last: 15m ago                    │
│ Common: Gap analysis, ISO cert   │
│                                  │
│ 📊 Strategic Planner             │
│ Today: 12 delegations            │
│ Last hour: 2                     │
│ Last: 8m ago                     │
│ Common: Roadmaps, Long-term      │
│                                  │
│ [View All Delegations]           │
└──────────────────────────────────┘
```

**API:**
- Prometheus: `orchestrator_delegations_total{specialist_type="ai-expert-*"}`

---

### 3.10. AlertsPanel
**Файл:** `/src/components/Orchestrator/AlertsPanel.tsx`

**Активные алерты из Prometheus:**

Группировка по severity:
- 🔴 CRITICAL
- 🟠 WARNING
- 🔵 INFO

Для каждого алерта:
- Alert name
- Description
- Started at
- Кнопка "Acknowledge"

**UI:**
```
┌─ Active Alerts ──────────────────┐
│                                  │
│ 🔴 CRITICAL (1)                  │
│ OrchestratorHighLatency          │
│ P95 latency is 112ms > 100ms    │
│ Started: 5m ago                  │
│ [Acknowledge]                    │
│                                  │
│ 🟠 WARNING (2)                   │
│ OrchestratorLowCacheHitRate      │
│ Cache hit rate: 62% < 70%       │
│ Started: 15m ago                 │
│ [Acknowledge]                    │
│                                  │
│ OrchestratorServiceCallSlow      │
│ learning service P95: 89ms       │
│ Started: 8m ago                  │
│ [Acknowledge]                    │
│                                  │
│ 🔵 INFO (1)                      │
│ OrchestratorCrisisDetected       │
│ 2 active crises                  │
│ Started: 12m ago                 │
│                                  │
│ [View All Alerts]                │
└──────────────────────────────────┘
```

**Источник:**
- Prometheus Alertmanager API
- Или кастомный endpoint с парсингом alert rules

---

### 3.11. DetailedCharts
**Файл:** `/src/components/Orchestrator/DetailedCharts.tsx`

**Табы с детальными графиками:**

**Tab 1: Performance**
- Decision Latency (линейный график P50/P95/P99)
- Throughput (решений в секунду)
- Context Aggregation Time
- Strategy Selection Time

**Tab 2: Efficiency**
- Auto-Resolution Rate (%)
- Human Intervention Rate (%)
- Delegation Rate (%)
- Safety Approval Rate (%)

**Tab 3: Services**
- Service Call Latency (по каждому сервису)
- Retry Rate
- Circuit Breaker Trips
- Success Rate

**Tab 4: PDCA**
- PDCA Cycles (Plan/Do/Check/Act)
- Lessons Learned (quantity)
- Patterns Detected
- Quality Score

**Tab 5: Business Impact**
- MTTR (Mean Time To Resolution)
- Incidents Prevented
- Cost Savings (estimated)
- ROI

**UI:**
```
┌─ Detailed Analytics ──────────────────────────────────────┐
│ [Performance] [Efficiency] [Services] [PDCA] [Business]  │
│                                                           │
│ ┌─ Decision Latency (Last 6 hours) ──────────────────┐  │
│ │ 150ms ┐                                             │  │
│ │       │     ╱╲                                      │  │
│ │ 100ms ├────╱  ╲─────────────────  P95              │  │
│ │       │   ╱    ╲    ╱╲                             │  │
│ │  50ms ├──╱──────╲──╱──╲──────────  P50             │  │
│ │       │                ╲                           │  │
│ │   0ms └────────────────────────────────────────────│  │
│ │       10:00  11:00  12:00  13:00  14:00  15:00    │  │
│ └─────────────────────────────────────────────────────┘  │
│                                                           │
│ ┌─ Throughput ───────────────────────────────────────┐  │
│ │ (График столбчатый - решений в минуту)             │  │
│ └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

**Данные:**
- Prometheus queries + Recharts

---

### 3.12. DecisionDetailsModal
**Файл:** `/src/components/Orchestrator/modals/DecisionDetailsModal.tsx`

**Открывается при клике "Details" на решении:**

**Разделы:**

1. **Overview**
   - Decision ID
   - Timestamp
   - Action Type
   - Priority Level
   - Confidence Score
   - Latency
   - Safety Approved (yes/no)

2. **Context**
   - Situation (JSON formatted)
   - Tenant ID
   - Source

3. **Strategy**
   - Action
   - Rationale
   - Learned From (если есть)

4. **Execution**
   - Status (success/failure)
   - Result
   - Service Called
   - Errors (если есть)

5. **Policy Check**
   - Policy Validated (yes/no)
   - Policy Reference
   - Compliance Status

**UI:**
```
┌─ Decision Details: dec_20251010_143215 ──────────────────┐
│ [X]                                                       │
│                                                           │
│ Tab: [Overview] [Context] [Strategy] [Execution] [Policy]│
│                                                           │
│ Decision ID: dec_20251010_143215                         │
│ Timestamp: 2025-10-10 14:32:15                          │
│ Action: AUTO_RESOLVE                                     │
│ Priority: HIGH                                           │
│ Confidence: 92%                                          │
│ Latency: 78ms                                            │
│ Safety Approved: ✅ Yes                                  │
│                                                           │
│ [Close]                                                  │
└───────────────────────────────────────────────────────────┘
```

---

### 3.13. CrisisDetailsModal
**Файл:** `/src/components/Orchestrator/modals/CrisisDetailsModal.tsx`

**Открывается при клике "Details" на кризисе:**

**Разделы:**

1. **Overview**
   - Crisis ID
   - Level (MAJOR/CRITICAL/CATASTROPHIC)
   - Status
   - Duration
   - Detected At
   - Resolved At (если resolved)

2. **Situation**
   - Critical Services Affected
   - Unhealthy Services
   - Error Rate
   - Source

3. **Response**
   - BC Plans Activated (ID, Type)
   - Coordinated Services
   - Actions Taken

4. **Timeline**
   - Список событий (detected → activated → coordinating → resolved)

**UI:**
```
┌─ Crisis Details: crisis_20251010_140022 ─────────────────┐
│ [X]                                                       │
│                                                           │
│ Tab: [Overview] [Situation] [Response] [Timeline]        │
│                                                           │
│ Crisis ID: crisis_20251010_140022                        │
│ Level: 🔴 CRITICAL                                       │
│ Status: COORDINATING                                     │
│ Duration: 15m 23s                                        │
│ Detected At: 2025-10-10 14:00:22                        │
│                                                           │
│ Critical Services: bia, risk                             │
│ Unhealthy Services: planning, compliance                 │
│ Error Rate: 35%                                          │
│                                                           │
│ BC Plan: bc_plan_001 (default)                          │
│ Coordinated: 4 services                                  │
│                                                           │
│ [Resolve Crisis] [Export Report]                        │
└───────────────────────────────────────────────────────────┘
```

---

### 3.14. TestDecisionModal
**Файл:** `/src/components/Orchestrator/modals/TestDecisionModal.tsx`

**Форма для тестового решения:**

**Поля:**
- Workflow ID (текст)
- Module (select: bia, risk, planning, etc.)
- Priority (select: CRITICAL, HIGH, NORMAL, LOW)
- Custom Situation (JSON editor)

**Кнопки:**
- "Send Test Decision"
- "Load Example"
- "Cancel"

**После отправки:**
- Показать результат:
  - Decision ID
  - Action
  - Confidence
  - Latency
  - Rationale

**UI:**
```
┌─ Test Decision ───────────────────────────────────────────┐
│ [X]                                                       │
│                                                           │
│ Workflow ID:                                             │
│ [test_workflow_001________________]                      │
│                                                           │
│ Module:                                                  │
│ [Select: bia ▼]                                          │
│                                                           │
│ Priority:                                                │
│ [Select: NORMAL ▼]                                       │
│                                                           │
│ Custom Situation (JSON):                                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ {                                                   │ │
│ │   "workflow_stuck": true,                          │ │
│ │   "stuck_duration_minutes": 15                     │ │
│ │ }                                                   │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                           │
│ [Load Example] [Send Test Decision] [Cancel]            │
│                                                           │
│ ─────────────────────────────────────────────────────────│
│ Result:                                                  │
│ ✅ Decision made successfully                            │
│ Decision ID: dec_test_001                                │
│ Action: AUTO_RESOLVE                                     │
│ Confidence: 85%                                          │
│ Latency: 67ms                                            │
└───────────────────────────────────────────────────────────┘
```

---

## 4. API Endpoints для админки

### 4.1. Новые эндпоинты (добавить в api.py)

```python
# Уже есть:
GET  /health
GET  /stats
POST /api/v1/decide
GET  /metrics
POST /admin/evolve

# Нужно добавить:
GET  /admin/services/health          # Здоровье всех сервисов
GET  /admin/decisions/recent         # Последние решения (query: limit)
GET  /admin/decisions/{id}           # Детали решения
GET  /admin/metrics/summary          # Сводка метрик для dashboard
POST /admin/cache/clear              # Очистка cache
POST /admin/emergency-stop           # Аварийная остановка
GET  /admin/logs                     # Логи (query: lines, level)
POST /admin/reload-config            # Перезагрузка конфигурации
GET  /admin/alerts                   # Активные алерты
POST /admin/alerts/{id}/acknowledge  # Подтверждение алерта
```

### 4.2. WebSocket для real-time

```python
# WebSocket endpoint: ws://localhost:8050/ws
# События:
# - decision_made
# - crisis_detected
# - crisis_resolved
# - service_health_changed
# - alert_triggered
```

---

## 5. Структура файлов

```
/interface/admin_panel/src/
├── pages/
│   └── OrchestratorControlPanel.tsx      # Главная страница
│
├── components/
│   └── Orchestrator/
│       ├── OrchestratorHeader.tsx
│       ├── SystemStatus.tsx
│       ├── QuickActions.tsx
│       ├── ActiveCrises.tsx
│       ├── PerformanceMetrics.tsx
│       ├── DecisionFlow.tsx
│       ├── ServiceHealth.tsx
│       ├── RecentDecisions.tsx
│       ├── AIExpertsDelegations.tsx
│       ├── AlertsPanel.tsx
│       ├── DetailedCharts.tsx
│       │
│       └── modals/
│           ├── DecisionDetailsModal.tsx
│           ├── CrisisDetailsModal.tsx
│           └── TestDecisionModal.tsx
│
├── services/
│   └── orchestrator-api.ts              # API клиент
│
├── hooks/
│   ├── useOrchestratorHealth.ts         # Hook для health check
│   ├── useOrchestratorMetrics.ts        # Hook для метрик
│   ├── useOrchestratorWebSocket.ts      # Hook для WebSocket
│   └── useOrchestratorDecisions.ts      # Hook для решений
│
└── types/
    └── orchestrator.ts                   # TypeScript types
```

---

## 6. Технические требования

### 6.1. Real-time обновление

**Стратегия:**
1. **WebSocket** для критических событий:
   - Новые решения
   - Кризисы
   - Изменения статуса сервисов

2. **Polling (каждые 5s)** для метрик:
   - Performance metrics
   - Service health
   - Recent decisions

3. **Manual refresh** для:
   - Detailed charts (по клику)
   - Logs

### 6.2. Performance

- Виртуализация списков (react-window) для больших списков решений
- Debounce для поиска/фильтров
- Мемоизация компонентов графиков
- Lazy loading для модальных окон

### 6.3. Responsive

- Desktop-first (минимум 1280px)
- Адаптация для планшетов (768px+)
- Мобильная версия - упрощенная

---

## 7. Настройки (Settings)

### Секция "Orchestrator Settings"

**Файл:** `/src/components/Orchestrator/OrchestratorSettings.tsx`

**Настройки:**

1. **Auto-Refresh**
   - Enable/Disable
   - Interval (5s, 10s, 30s, 60s)

2. **Notifications**
   - Enable browser notifications
   - Sound alerts
   - Alert levels to notify (CRITICAL only, WARNING+, All)

3. **Display**
   - Chart time range (1h, 6h, 24h, 7d)
   - Metrics refresh rate
   - Theme (dark/light)

4. **Performance**
   - Enable WebSocket
   - Max decisions to show
   - Cache settings visibility

**UI:**
```
┌─ Orchestrator Settings ───────────────────────────────────┐
│                                                           │
│ Auto-Refresh                                             │
│ [✓] Enable auto-refresh                                  │
│ Interval: [Select: 5s ▼]                                │
│                                                           │
│ Notifications                                            │
│ [✓] Browser notifications                                │
│ [✓] Sound alerts                                         │
│ Alert levels: [Select: WARNING+ ▼]                      │
│                                                           │
│ Display                                                  │
│ Chart time range: [Select: 6h ▼]                        │
│ Metrics refresh: [Select: 5s ▼]                         │
│ Theme: [Select: Dark ▼]                                  │
│                                                           │
│ Performance                                              │
│ [✓] Enable WebSocket                                     │
│ Max decisions: [Select: 50 ▼]                           │
│ [✓] Show cache statistics                                │
│                                                           │
│ [Save Settings] [Reset to Defaults]                     │
└───────────────────────────────────────────────────────────┘
```

**Хранение:**
- localStorage для настроек пользователя

---

## 8. Фазы реализации

### Фаза 1: Core (2 дня)
- [x] Структура файлов
- [ ] OrchestratorControlPanel (layout)
- [ ] OrchestratorHeader
- [ ] SystemStatus
- [ ] API client (orchestrator-api.ts)
- [ ] Базовые hooks

### Фаза 2: Metrics & Performance (2 дня)
- [ ] PerformanceMetrics
- [ ] DetailedCharts (Performance tab)
- [ ] ServiceHealth
- [ ] useOrchestratorMetrics hook

### Фаза 3: Decisions & Actions (2 дня)
- [ ] RecentDecisions
- [ ] DecisionDetailsModal
- [ ] QuickActions
- [ ] TestDecisionModal

### Фаза 4: Crisis & Experts (1 день)
- [ ] ActiveCrises
- [ ] CrisisDetailsModal
- [ ] AIExpertsDelegations

### Фаза 5: Alerts & Real-time (2 дня)
- [ ] AlertsPanel
- [ ] WebSocket integration
- [ ] useOrchestratorWebSocket hook
- [ ] Real-time updates

### Фаза 6: Polish & Settings (1 день)
- [ ] OrchestratorSettings
- [ ] Responsive design
- [ ] Error handling
- [ ] Loading states

**Итого:** 10 дней (2 недели)

---

## 9. Дополнительные возможности (Future)

### 9.1. Advanced Features
- [ ] Strategy debugging - пошаговый просмотр выбора стратегии
- [ ] A/B testing - сравнение разных конфигураций
- [ ] Playback - воспроизведение решений
- [ ] What-if analysis - симуляция решений

### 9.2. Integrations
- [ ] Slack notifications
- [ ] PagerDuty integration
- [ ] Jira ticket creation
- [ ] Email reports

### 9.3. Analytics
- [ ] Custom dashboards
- [ ] Saved queries
- [ ] Export to PDF
- [ ] Scheduled reports

---

## 10. Checklist готовности

### Must Have (MVP)
- [ ] Отображение статуса системы
- [ ] 4 ключевые метрики
- [ ] Список последних решений
- [ ] Health check сервисов
- [ ] Quick actions (evolve, cache clear)
- [ ] Real-time updates (WebSocket)

### Should Have
- [ ] Детальные графики (5 табов)
- [ ] Crisis management
- [ ] AI Experts delegations
- [ ] Alerts panel
- [ ] Settings panel

### Nice to Have
- [ ] Test decision form
- [ ] Logs viewer
- [ ] Export capabilities
- [ ] Advanced filters

---

## 11. Интеграция в App.tsx

```typescript
// Добавить в routes:
import OrchestratorControlPanel from '@/pages/OrchestratorControlPanel';

// ...
<Route path="/orchestrator" element={<OrchestratorControlPanel />} />
```

**Добавить в навигацию:**
```typescript
// В BCMUnifiedWorkspace или главное меню
{
  label: 'AI Orchestrator',
  path: '/orchestrator',
  icon: <BrainIcon />
}
```

---

## 12. Mockup (ASCII)

```
┌────────────────────────────────────────────────────────────────────────┐
│ 🤖 AI Orchestrator Control Panel              🟢 Online  [Emergency]  │
│────────────────────────────────────────────────────────────────────────│
│                                                                        │
│ ┌─ System Status ──┐ ┌─ Performance Metrics ───────────────────────┐ │
│ │ 🟢 Healthy       │ │ ⚡ Latency: 87ms  📊 Auto-Res: 94%          │ │
│ │ Uptime: 3h 24m   │ │ 👤 Human: 12%    ✅ Safety: 97%             │ │
│ │                  │ └──────────────────────────────────────────────┘ │
│ │ Decisions: 1,247 │ ┌─ Decision Flow ─────────────────────────────┐ │
│ │ Success: 96.3%   │ │ Situations(450)→Priority→Strategy→Actions   │ │
│ └──────────────────┘ │ AUTO_RESOLVE: 325 (72%)                     │ │
│                      │ DELEGATE: 87 (19%)                          │ │
│ ┌─ Quick Actions ─┐ └──────────────────────────────────────────────┘ │
│ │ [Evolution]     │ ┌─ Service Health ────────────────────────────┐ │
│ │ [Clear Cache]   │ │ bia: 🟢 23ms    risk: 🟢 31ms               │ │
│ │ [Test]          │ │ planning: 🟡 89ms  compliance: 🟢 18ms      │ │
│ └─────────────────┘ └──────────────────────────────────────────────┘ │
│                                                                        │
│ ┌─ Active Crises ─┐ ┌─ Recent Decisions ──────────────────────────┐ │
│ │ 🚨 2 Active     │ │ 14:32:15 AUTO_RESOLVE 92% 78ms              │ │
│ │ crisis_001 🔴   │ │ 14:31:48 DELEGATE 78% 65ms                  │ │
│ │ [Details]       │ │ 14:31:22 ESCALATE 45% 123ms                 │ │
│ └─────────────────┘ └──────────────────────────────────────────────┘ │
│                                                                        │
│ ┌─ Detailed Analytics ──────────────────────────────────────────────┐ │
│ │ [Performance] [Efficiency] [Services] [PDCA] [Business Impact]   │ │
│ │ [График Decision Latency P50/P95/P99 за последние 6 часов]      │ │
│ └────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

---

**ТЗ готово к реализации!** 🚀

Хочешь, чтобы я начал реализацию? Начнем с Фазы 1?
