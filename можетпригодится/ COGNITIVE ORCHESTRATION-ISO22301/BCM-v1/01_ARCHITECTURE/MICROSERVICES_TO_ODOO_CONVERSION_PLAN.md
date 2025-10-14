# 🔄 План превращения микросервисов в Odoo модули

## 🎯 СТРАТЕГИЯ КОНВЕРСИИ

### **Зачем превращать микросервисы в Odoo модули?**

1. **Unified Data Model** - все данные в одной PostgreSQL базе
2. **Living Organism Integration** - модули становятся органами
3. **BCM Event Bus** - единая нервная система
4. **Odoo UI/UX** - стандартизированный интерфейс
5. **Security Model** - единая система прав доступа
6. **Workflow Engine** - встроенные Odoo workflow

## 📊 ПРИОРИТЕТНЫЕ МИКРОСЕРВИСЫ ДЛЯ КОНВЕРСИИ

### **PHASE 1: Critical BCM Services (Week 1-2)**

#### 1. **ai_orchestrator** → **bcm_ai_orchestrator**
```
services/ai_orchestrator/ → core/odoo-18.0/addons/bcm_ai_orchestrator/

ПРИЧИНА: Центральный AI компонент, критичен для организма
СЛОЖНОСТЬ: Высокая (много AI логики)
ВЫГОДА: Прямая интеграция с BCM AI Bridge
```

#### 2. **notification_service** → **bcm_notification**
```
services/notification_service/ → core/odoo-18.0/addons/bcm_notification/

ПРИЧИНА: Критично для всех workflow уведомлений
СЛОЖНОСТЬ: Средняя (стандартные REST API)
ВЫГОДА: Интеграция с Odoo mail/SMS системой
```

#### 3. **monitoring_service** → **bcm_monitoring**
```
services/monitoring_service/ → core/odoo-18.0/addons/bcm_monitoring/

ПРИЧИНА: Health monitoring для живого организма
СЛОЖНОСТЬ: Средняя (метрики и дашборды)
ВЫГОДА: Odoo dashboard + reporting интеграция
```

### **PHASE 2: Document & Process Services (Week 3-4)**

#### 4. **document_processor** → **bcm_document_processor**
```
services/document_processor/ → core/odoo-18.0/addons/bcm_document_processor/

ПРИЧИНА: Множественное дублирование в проекте
СЛОЖНОСТЬ: Высокая (файловые операции)
ВЫГОДА: Интеграция с Odoo Documents/Attachments
```

#### 5. **process_mining_service** → **bcm_process_mining**
```
services/process_mining_service/ → core/odoo-18.0/addons/bcm_process_mining/

ПРИЧИНА: Анализ BCM процессов
СЛОЖНОСТЬ: Высокая (алгоритмы анализа)
ВЫГОДА: Интеграция с BCM workflow данными
```

### **PHASE 3: Integration Services (Week 5-6)**

#### 6. **bia_engine** → **bcm_bia_enhanced**
```
services/bia_engine/ → core/odoo-18.0/addons/bcm_bia_enhanced/

ПРИЧИНА: Дополнить существующий bcm_bia
СЛОЖНОСТЬ: Средняя (бизнес логика)
ВЫГОДА: Полная интеграция с BCM organism
```

## 🔧 ШАБЛОН КОНВЕРСИИ

### **Conversion Template для каждого микросервиса:**

```python
# services/ai_orchestrator/main.py →
# core/odoo-18.0/addons/bcm_ai_orchestrator/models/ai_orchestrator.py

class BCMAIOrchestrator(models.Model):
    _name = 'bcm.ai.orchestrator'
    _description = 'AI Orchestration within BCM Organism'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Odoo features

    # STEP 1: Migrate data models
    workflow_name = fields.Char('Workflow Name', required=True)
    workflow_type = fields.Selection([...])  # From microservice
    workflow_data = fields.Json('Workflow Data')

    # STEP 2: Migrate core logic
    def orchestrate_ai_workflow(self, workflow_data):
        """Migrated from microservice main logic"""
        # Original microservice logic here
        pass

    # STEP 3: Add Odoo integration
    def create(self, vals):
        result = super().create(vals)
        # Publish to BCM Event Bus
        result._publish_integration_event('ai_workflow_created', {...})
        return result

    # STEP 4: Add organism integration
    @api.model
    def handle_event(self, event_type, event_data, source_module):
        """Handle events from other BCM organs"""
        if event_type == 'project_needs_ai_analysis':
            return self._handle_project_analysis_request(event_data)
        # ... other event handlers

    # STEP 5: Add web API compatibility (for legacy clients)
    @http.route('/api/ai/orchestrate', type='json', auth='public', methods=['POST'])
    def api_orchestrate_legacy(self, **kwargs):
        """Backward compatibility for external API calls"""
        return self.orchestrate_ai_workflow(kwargs)
```

## 🔄 MIGRATION WORKFLOW

### **1. Анализ микросервиса**
```bash
# Анализируем структуру сервиса
ls -la services/ai_orchestrator/
cat services/ai_orchestrator/main.py
cat services/ai_orchestrator/requirements.txt
```

### **2. Создание Odoo модуля**
```bash
# Создаем структуру модуля
mkdir -p core/odoo-18.0/addons/bcm_ai_orchestrator/{models,views,data,security}
```

### **3. Миграция данных и логики**
```python
# Переносим:
# - API endpoints → Odoo controllers
# - Data models → Odoo models (fields)
# - Business logic → model methods
# - Database → PostgreSQL tables через Odoo ORM
```

### **4. Интеграция с организмом**
```python
# Добавляем:
# - Event handlers (handle_event method)
# - Event publishing (_publish_integration_event)
# - Health monitoring (get_organ_health_status)
# - AI Bridge integration
```

### **5. Backward compatibility**
```python
# Создаем API эндпоинты для legacy clients:
@http.route('/api/legacy/service_name', ...)
def legacy_api_compatibility(self):
    # Wrap Odoo methods as REST API
    pass
```

## 📋 КОНКРЕТНЫЙ ПРИМЕР: ai_orchestrator → bcm_ai_orchestrator

### **1. Анализ исходного сервиса:**
```python
# services/ai_orchestrator/main.py (предполагаемая структура)
class AIOrchestrator:
    def __init__(self):
        self.workflows = {}

    def orchestrate(self, workflow_type, data):
        # AI orchestration logic
        return result

    def register_workflow(self, name, handler):
        self.workflows[name] = handler
```

### **2. Odoo модуль:**
```python
# core/odoo-18.0/addons/bcm_ai_orchestrator/models/ai_orchestrator.py
class BCMAIOrchestrator(models.Model):
    _name = 'bcm.ai.orchestrator'

    # Migrate data model
    name = fields.Char('Workflow Name')
    workflow_type = fields.Selection([
        ('risk_analysis', 'Risk Analysis'),
        ('project_optimization', 'Project Optimization'),
        ('incident_response', 'Incident Response')
    ])
    workflow_data = fields.Json('Workflow Data')
    status = fields.Selection([('draft', 'Draft'), ('running', 'Running'), ('completed', 'Completed')])

    # Migrate core logic
    def orchestrate_workflow(self, workflow_type, data):
        """Migrated from microservice orchestrate() method"""
        workflow_record = self.create({
            'name': f'Workflow {workflow_type}',
            'workflow_type': workflow_type,
            'workflow_data': data,
            'status': 'running'
        })

        # Original AI orchestration logic here
        result = self._execute_ai_workflow(workflow_type, data)

        workflow_record.status = 'completed'
        return result

    # Add organism integration
    def create(self, vals):
        result = super().create(vals)
        # Notify organism
        self.env['bcm.event.bus'].publish_event(
            'ai_workflow_started',
            'bcm_ai_orchestrator',
            {'workflow_id': result.id, 'workflow_type': result.workflow_type}
        )
        return result

    @api.model
    def handle_event(self, event_type, event_data, source_module):
        """React to organism events"""
        if event_type == 'risk_identified' and source_module == 'bcm_risk_management':
            # Automatically start AI analysis for new risks
            self.orchestrate_workflow('risk_analysis', event_data)
            return {'status': 'success', 'action': 'risk_analysis_started'}

        return {'status': 'ignored'}

    # Legacy API compatibility
    @http.route('/api/ai/orchestrate', type='json', auth='public', methods=['POST'])
    def api_orchestrate_legacy(self, workflow_type, data):
        """Backward compatibility for external clients"""
        result = self.orchestrate_workflow(workflow_type, data)
        return {'status': 'success', 'data': result}
```

## 🎖️ ПРЕИМУЩЕСТВА КОНВЕРСИИ

### **После конверсии получаем:**

1. **Unified Data Access** - все AI workflows в Odoo database
2. **Event-Driven Reactions** - AI запускается автоматически от событий других органов
3. **Odoo UI** - встроенные формы, списки, дашборды для управления AI
4. **Security Integration** - права доступа через Odoo groups/users
5. **Backup/Restore** - AI конфигурации в общем бэкапе Odoo
6. **Reporting** - AI метрики через Odoo reporting engine
7. **Workflow Engine** - AI процессы через Odoo workflow system

## 🚀 IMMEDIATE NEXT STEPS

### **Начать с ai_orchestrator:**

```bash
# 1. Создать модуль
mkdir -p /Users/MD/ISO-22301/sandbox/golden-pr-26-modules/bcm_ai_orchestrator/

# 2. Проанализировать исходный сервис
ls -la /Users/MD/ISO-22301/services/ai_orchestrator/
cat /Users/MD/ISO-22301/services/ai_orchestrator/main.py

# 3. Создать Odoo модуль по шаблону выше

# 4. Протестировать интеграцию с BCM Bridge
```

### **Готов начать конверсию любого сервиса! Какой выбираешь?** 🎯

1. **ai_orchestrator** (самый важный)
2. **notification_service** (самый простой)
3. **monitoring_service** (самый полезный)
4. **document_processor** (избавляемся от дубликатов)

**Какой микросервис конвертируем первым?** 🤔