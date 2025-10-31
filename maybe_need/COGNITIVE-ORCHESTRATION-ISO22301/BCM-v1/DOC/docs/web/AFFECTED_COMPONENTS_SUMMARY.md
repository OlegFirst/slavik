# Затронутые Компоненты - Сводка для Команды Интерфейсов

## 🎯 Краткая сводка для команды

### **📋 Какие модули затронуты:**

#### **1. Odoo BCM Modules (Backend)**
- **`bcm_scenario_hub`** - добавлена AI generation + forum integration
- **`bcm_community`** - НОВЫЙ модуль (создан полностью)
- **`bcm_exercise`** - планируется BPMN integration
- **`bcm_notification`** - планируется централизация уведомлений

#### **2. Frontend Components (Vue.js/React)**
- **`BCMScenarioHub.vue`** - уже обновлен командой
- **Web Portal v2** - упомянут в docker-compose
- **Admin Panel** - нужен health monitoring dashboard

#### **3. API Services (New Endpoints)**
- **Scenario Orchestrator** (8085) - AI generation API
- **Notification Service** (8002) - external integrations
- **AI Orchestrator** (8000) - enhanced capabilities

---

## 🚀 **ЧТО НУЖНО КОМАНДЕ ИНТЕРФЕЙСОВ:**

### **ПРИОРИТЕТ 1: AI Scenario Generation UI**

#### **Где**: Web Portal (Vue.js) - обновить или создать
```yaml
Файл: /frontend/web_portal/src/components/ai/AIScenarioWizard.vue
API: POST http://localhost:8085/scenarios/generate
Функция: Wizard для создания AI сценариев

Требования:
  - 3-step wizard (parameters → context → generation)
  - Real-time AI generation progress
  - Scenario preview с markdown rendering
  - Integration с существующим BCMScenarioHub.vue
```

#### **JSON API для интеграции**:
```json
// Request to AI generation
{
  "category": "cyber|epidemic|blackout|supply|natural|terrorism|financial",
  "complexity": 1-5,
  "duration_hours": 2-24,
  "participants": 5-100,
  "affected_systems": ["IT", "Operations", "Communications"],
  "organization_context": "Healthcare|Financial|Manufacturing|Government"
}

// Response from AI
{
  "status": "success",
  "scenario_id": "ai_20250914_181500",
  "title": "Generated Scenario Title",
  "file_path": "/app/generated_scenarios/scenario_xxx.json",
  "ai_generated": true,
  "created_at": "2025-09-14T18:15:00Z"
}
```

---

### **ПРИОРИТЕТ 2: Service Health Dashboard**

#### **Где**: Admin Panel (React)
```yaml
Файл: /frontend/admin_panel/src/components/ServiceHealthDashboard.jsx
API: Multiple health endpoints (см. ниже)
Функция: Real-time мониторинг всех сервисов

Endpoints для мониторинга:
  - http://localhost:8000/health  # AI Orchestrator
  - http://localhost:8085/health  # Scenario Orchestrator
  - http://localhost:8069/web/health  # Odoo
  - http://localhost:8087/health  # MCP Server
  - http://localhost:8001/health  # EventBus
  - [+ 15 других сервисов]
```

#### **Health Check Response Format**:
```json
{
  "status": "healthy",
  "service": "ai_orchestrator",
  "version": "1.0.0",
  "capabilities": ["risk_analysis", "incident_classification"],
  "timestamp": "2025-09-14T18:15:00Z"
}
```

---

### **ПРИОРИТЕТ 3: Community Integration UI**

#### **Где**: Odoo bcm_community module
```yaml
Статус: Модуль создан, нужны view файлы
Локация: /core/odoo-18.0/addons/bcm_community/views/

Файлы созданы:
  ✅ models/forum_integration.py
  ✅ models/forum_topic.py
  ✅ security/ir.model.access.csv
  ✅ views/menu.xml
  ✅ views/forum_topic_views.xml

Нужно создать:
  - forum_integration_dashboard.xml  # Dashboard для forum integration
  - community_analytics_view.xml     # Community statistics
  - knowledge_base_view.xml          # Knowledge base management
```

---

## 🔧 **Технические детали для команды:**

### **API Endpoints готовые к использованию:**

```bash
# AI Scenario Generation
POST http://localhost:8085/scenarios/generate
GET  http://localhost:8085/scenarios/available

# AI Chat/Query
POST http://localhost:8000/nlp/query

# Service Health
GET  http://localhost:8000/health
GET  http://localhost:8085/health
GET  http://localhost:8069/web/health

# Notifications (готов к настройке)
POST http://localhost:8002/external/notify
```

### **Environment Variables для frontend:**
```env
# AI Integration
VUE_APP_AI_URL=http://localhost:8000
VUE_APP_SCENARIO_URL=http://localhost:8085
VUE_APP_NOTIFICATION_URL=http://localhost:8002

# Existing
VUE_APP_API_URL=http://localhost:8069
```

---

## 🎯 **Конкретное ТЗ для команды:**

### **ЗАДАЧА 1**: AI Scenario Generation Wizard
- **Время**: 2-3 дня разработки
- **Технологии**: Vue.js 3, Bootstrap 5
- **API**: Готово и протестировано
- **Дизайн**: 3-step wizard с прогресс индикатором

### **ЗАДАЧА 2**: Service Health Dashboard
- **Время**: 1-2 дня разработки
- **Технологии**: React, Bootstrap
- **API**: 21 health endpoint готовы
- **Дизайн**: Grid layout с real-time updates

### **ЗАДАЧА 3**: bcm_community Module UI
- **Время**: 2-3 дня разработки
- **Технологии**: Odoo XML views
- **Backend**: Модели созданы, API готово
- **Дизайн**: Odoo стандартный + custom dashboard

---

## 📄 **Документация создана:**

✅ **`/docs/frontend/UI_TECHNICAL_SPECIFICATION.md`** - Полная техническая спецификация
✅ **`/docs/frontend/AFFECTED_COMPONENTS_SUMMARY.md`** - Эта сводка

**Передавай команде - все готово для разработки интерфейсов!** 🎨🚀