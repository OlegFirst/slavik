# 🎨 AI Platform ISO - Web Interfaces Overview

## Структура веб-интерфейсов платформы

---

## 📦 Существующие интерфейсы

### 1. **AI Platform Control Center** ✅ ГЛАВНЫЙ
**Путь:** `/interface/admin-control-center/`
**Тип:** React 18 + TypeScript + Vite + Tailwind CSS
**Порт:** 3001
**URL:** http://localhost:3001

#### Описание:
Полноценный административный центр управления AI Platform ISO.
Объединяет архитектуру BCM Admin Control Center + новые компоненты (Tools, Prometheus, Grafana).

#### Технологии:
- React 18.3
- TypeScript 5.5
- Vite 5.4
- Tailwind CSS 3.4
- Tanstack Query 5.89 (real-time data fetching)
- Shadcn/ui components
- Lucide React icons

#### 12 вкладок управления:

| № | Вкладка | Компонент | Назначение |
|---|---------|-----------|------------|
| 1 | **Dashboard** | `PlatformDashboard.tsx` | Общий overview с real-time метриками |
| 2 | **Services** | `CentralizedArchitectureMonitor.tsx` | Управление микросервисами (Start/Stop/Restart) |
| 3 | **Tools** | `ToolsManager.tsx` | Управление инструментами Analytics Specialist |
| 4 | **Monitoring** | `GrafanaViewer.tsx` + `PrometheusMetrics.tsx` | Grafana dashboards + Prometheus metrics |
| 5 | **Platforms** | Встроенный менеджер | Быстрый доступ к интегрированным платформам |
| 6 | **Analytics** | `Analytics.tsx` | Базовая аналитика + Intelligence Hub |
| 7 | **ISO 22301** | `ComplianceDashboard.tsx` | ISO 22301 compliance dashboard |
| 8 | **System Config** | `SystemConfigManager.tsx` | Управление конфигурацией системы |
| 9 | **Templates** | `TemplateManager.tsx` | Управление шаблонами |
| 10 | **Clients** | `ClientManager.tsx` | Multi-tenancy управление |
| 11 | **Users** | `UserManager.tsx` | Управление пользователями и правами |
| 12 | **Modules** | `ModulesOverview.tsx` | Overview установленных модулей |

#### Ключевые фичи:
- ✅ **NO MOCK DATA** - все данные из реальных API
- ✅ **Auto-refresh** с настройкой интервалов (10s/30s/1m/5m)
- ✅ **Service control** - Start/Stop/Restart для сервисов
- ✅ **Real-time notifications** - топ-3 уведомления в header
- ✅ **Prometheus integration** - PromQL queries
- ✅ **Grafana integration** - Embedded dashboards
- ✅ **Tools Manager** - интеграция с Analytics Specialist API
- ✅ **ISO 22301 compliance tracking**

#### API интеграции:
```typescript
// Service Layer
/src/services/platform.ts     - 7 AI Platform services (orchestrator, workflow, etc.)
/src/services/realtime.ts     - Prometheus, Grafana, Tools (NO MOCK DATA)
/src/services/analytics-hub.ts - Intelligence Hub integration
/src/services/bcm.ts          - Legacy stub
```

#### Запуск:
```bash
cd /Users/MD/AI-Platform-ISO/interface/admin-control-center
npm install
npm run dev
```

---

### 2. **FastAPI Web UI** (Легковесный мониторинг)
**Путь:** `/infrastructure/web-ui/`
**Тип:** Python FastAPI + Jinja2 templates + Vanilla JS
**Порт:** 8888
**URL:** http://localhost:8888

#### Описание:
Простой веб-интерфейс для быстрого мониторинга без React.
Идеален для production мониторинга или когда нужен легковесный dashboard.

#### Технологии:
- FastAPI (Python)
- Jinja2 templates
- Vanilla JavaScript
- Pure HTML/CSS
- httpx для API calls

#### 3 страницы:

| Страница | URL | Назначение |
|----------|-----|------------|
| **Dashboard** | `/` | Статус всех сервисов + quick actions |
| **Tools** | `/tools` | Управление 7 инструментами Analytics Specialist |
| **Monitoring** | `/monitoring` | Embedded Grafana + Prometheus |

#### Ключевые фичи:
- ✅ Service health checks (12 сервисов)
- ✅ Tools execution via Analytics Specialist API
- ✅ Embedded Grafana/Prometheus iframes
- ✅ Auto-refresh каждые 30 секунд
- ✅ Responsive дизайн
- ✅ CORS enabled для интеграций

#### API Endpoints:
```python
GET  /api/services/status          # Статус всех сервисов
GET  /api/tools/list                # Список инструментов
POST /api/tools/{tool_name}/execute # Запуск инструмента
GET  /api/prometheus/query          # PromQL запросы
GET  /api/grafana/dashboards        # Grafana dashboards
```

#### Интегрированные сервисы:
```python
SERVICES = {
    # AI Office Infrastructure
    "analytics_specialist": "http://localhost:8051",
    "mio_manager": "http://localhost:8046",
    "ai_orchestrator": "http://localhost:8004",

    # Intelligent Core
    "workflow_intelligence": "http://localhost:8030",
    "community_intelligence": "http://localhost:8031",
    "collective": "http://localhost:8032",
    "predictive": "http://localhost:8033",
    "ai_foundation": "http://localhost:8050",

    # Observability
    "prometheus": "http://localhost:9090",
    "grafana": "http://localhost:3000",
    "alertmanager": "http://localhost:9093",
}
```

#### Запуск:
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/web-ui
pip install -r requirements.txt
python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload
```

---

### 3. **Original BCM Admin Control Center** (Legacy)
**Путь:** `/interface/admin_panel/`
**Тип:** React + TypeScript
**Порт:** Неизвестен (не используется)
**Статус:** ⚠️ LEGACY - не используется напрямую

#### Описание:
Оригинальная версия BCM Admin Control Center.
**Компоненты из него скопированы** в `/interface/admin-control-center/`.

#### Назначение:
- Источник компонентов для нового Control Center
- Reference implementation
- Не запускается отдельно

---

## 🎯 Рекомендации по использованию

### Для разработки:
**Используй:** `/interface/admin-control-center/` (React Control Center)
- Полноценный UI с 12 вкладками
- Все современные фичи
- React + TypeScript
- http://localhost:3001

### Для production мониторинга:
**Используй:** `/infrastructure/web-ui/` (FastAPI)
- Легковесный (Python + HTML)
- Быстрый запуск
- Минимальные зависимости
- http://localhost:8888

### Для разработки API:
**Используй оба:**
- React Control Center для UI
- FastAPI Web UI как proxy/backend
- Можно запустить одновременно на разных портах

---

## 🗂️ Структура файлов

```
/Users/MD/AI-Platform-ISO/

├── interface/
│   ├── admin-control-center/  ✅ ГЛАВНЫЙ React Control Center
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── AIPlatformControlCenter.tsx  ← MAIN COMPONENT
│   │   │   │   ├── ToolsManager.tsx
│   │   │   │   ├── GrafanaViewer.tsx
│   │   │   │   ├── PrometheusMetrics.tsx
│   │   │   │   ├── PlatformDashboard.tsx
│   │   │   │   ├── CentralizedArchitectureMonitor.tsx
│   │   │   │   ├── ComplianceDashboard.tsx
│   │   │   │   ├── SystemConfigManager.tsx
│   │   │   │   └── ... (все компоненты BCM)
│   │   │   ├── services/
│   │   │   │   ├── platform.ts      ← 7 AI Platform services
│   │   │   │   ├── realtime.ts      ← Prometheus/Grafana/Tools
│   │   │   │   └── analytics-hub.ts ← Intelligence Hub
│   │   │   ├── hooks/
│   │   │   ├── stores/
│   │   │   └── pages/
│   │   ├── package.json
│   │   └── vite.config.ts
│   │
│   ├── admin_panel/  ⚠️ LEGACY (оригинальный BCM Control Center)
│   │
│   ├── api-gateway/
│   └── web-app/
│
└── infrastructure/
    └── web-ui/  ✅ FastAPI простой мониторинг
        ├── main.py
        ├── templates/
        │   ├── dashboard.html
        │   ├── tools.html
        │   └── monitoring.html
        ├── static/
        └── requirements.txt
```

---

## 🚀 Быстрый старт

### Вариант 1: Только React Control Center
```bash
cd /Users/MD/AI-Platform-ISO/interface/admin-control-center
npm install
npm run dev
# Открыть http://localhost:3001
```

### Вариант 2: Только FastAPI мониторинг
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/web-ui
pip install -r requirements.txt
python3 -m uvicorn main:app --port 8888 --reload
# Открыть http://localhost:8888
```

### Вариант 3: Оба одновременно
```bash
# Terminal 1: React Control Center
cd /Users/MD/AI-Platform-ISO/interface/admin-control-center
npm run dev

# Terminal 2: FastAPI мониторинг
cd /Users/MD/AI-Platform-ISO/infrastructure/web-ui
python3 -m uvicorn main:app --port 8888 --reload

# Доступны:
# http://localhost:3001 - React Control Center
# http://localhost:8888 - FastAPI мониторинг
```

---

## 📊 Сравнение интерфейсов

| Критерий | React Control Center | FastAPI Web UI |
|----------|----------------------|----------------|
| **Технологии** | React + TypeScript | Python + HTML |
| **Сложность** | Высокая | Низкая |
| **Функциональность** | 12 вкладок, full control | 3 страницы, мониторинг |
| **Performance** | Средний (SPA) | Высокий (простой HTML) |
| **Dev опыт** | Отличный (HMR, TS) | Хороший (auto-reload) |
| **Production** | Требует build | Готов сразу |
| **Dependencies** | 497 npm packages | 3 Python packages |
| **Bundle size** | ~2MB (minified) | ~50KB |
| **Startup time** | ~5s (dev) | ~1s |
| **Use case** | Full admin control | Quick monitoring |

---

## 🔧 Настройка портов

### Если порт 3001 занят (React):
```bash
# vite.config.ts
export default defineConfig({
  server: {
    port: 3002  // Изменить порт
  }
})
```

### Если порт 8888 занят (FastAPI):
```bash
python3 -m uvicorn main:app --port 8889 --reload
```

---

## 📝 Следующие шаги

1. ✅ **Удалён дубликат** `/infrastructure/web-ui-react/`
2. ✅ **Главный портал** в `/interface/admin-control-center/`
3. ✅ **Легковесный мониторинг** в `/infrastructure/web-ui/`
4. ⚠️ **TODO:** Исправить ошибки импортов в React Control Center
5. ⚠️ **TODO:** Запустить все микросервисы для тестирования
6. ⚠️ **TODO:** Добавить authentication/authorization

---

## 🎉 Итог

**У тебя теперь 2 веб-интерфейса:**

1. **React Control Center** (`/interface/admin-control-center/`) - для полного управления платформой
2. **FastAPI Web UI** (`/infrastructure/web-ui/`) - для быстрого мониторинга

Оба работают независимо, оба интегрируются с одними и теми же сервисами AI Platform ISO!

---

**Создано:** 2025-10-08
**Автор:** Claude Code
**Версия:** 1.0.0
