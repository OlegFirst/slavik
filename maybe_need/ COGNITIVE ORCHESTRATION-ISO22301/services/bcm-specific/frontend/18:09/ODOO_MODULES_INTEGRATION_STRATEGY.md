# 📋 ИТОГОВЫЙ ДОКУМЕНТ: МОДУЛИ ODOO ДЛЯ BCM PLATFORM

## 🔐 МОДУЛИ БЕЗОПАСНОСТИ И АУТЕНТИФИКАЦИИ (КРИТИЧЕСКИ ВАЖНЫ!)

### Обязательные для безопасности:
```python
'auth_signup'              # Регистрация пользователей
'auth_totp'               # 2FA аутентификация - КРИТИЧНО для ISO 27001
'auth_totp_portal'        # 2FA для внешних пользователей
'auth_password_policy'    # Политики паролей - требование compliance
'auth_ldap'               # Интеграция с корпоративным LDAP
'auth_passkey'            # Современная биометрическая аутентификация
```

### API и интеграции:
```python
'iap'                     # In-App Purchase - API framework
'base_api'                # REST API базовый функционал
'http_routing'            # HTTP маршрутизация для API
```

## 🏗️ ФИНАЛЬНАЯ АРХИТЕКТУРА МОДУЛЕЙ

### 1️⃣ ЯДРО СИСТЕМЫ (обязательные):
```python
CORE_REQUIRED = {
    # Базовая инфраструктура
    'base':                 "Ядро Odoo",
    'web':                  "Web framework и UI",
    'mail':                 "Система сообщений и уведомлений",
    'bus':                  "WebSocket real-time коммуникации",
    'http_routing':         "REST API routing",

    # Безопасность - КРИТИЧНО!
    'auth_signup':          "Регистрация пользователей",
    'auth_totp':            "2FA аутентификация",
    'auth_password_policy': "Политики паролей ISO 27001",
}
```

### 2️⃣ BCM-СПЕЦИФИЧНЫЕ ФУНКЦИИ:
```python
BCM_FEATURES = {
    # Управление проектами и клиентами
    'crm':                  "Pipeline консалтинговых проектов",
    'portal':               "Доступ для внешних аудиторов/клиентов",

    # Документы и контент
    'attachment_indexation': "Поиск в планах BCM и документах",
    'spreadsheet':          "Экспорт отчётов для аудиторов",

    # Коммуникации в кризис
    'sms':                  "SMS оповещения при инцидентах",
    'mass_mailing':         "Массовые уведомления stakeholders",
    'mail_group':           "Группы рассылки для кризисных команд",
    'calendar':             "Планирование учений, аудитов, пересмотров",

    # Обучение и оценка
    'survey':               "Тесты знаний ISO 22301, оценки готовности",
    'gamification':         "Мотивация обучения, рейтинги консультантов",
}
```

### 3️⃣ РАСШИРЕННЫЕ ВОЗМОЖНОСТИ:
```python
ADVANCED_FEATURES = {
    # Поддержка и коммуникации
    'im_livechat':          "Онлайн-консультации по BCM",
    'knowledge':            "База знаний ISO 22301 (если не своя)",

    # Интеграции с внешними системами
    'google_calendar':      "Синхронизация с Google Workspace",
    'microsoft_calendar':   "Синхронизация с Microsoft 365",
    'auth_ldap':           "SSO с корпоративными системами",
    'auth_oauth':          "OAuth для интеграций",

    # Аналитика и отчетность
    'analytic':            "Аналитические счета для BCM проектов",
    'board':               "Дашборды для руководства",

    # E-Learning платформа
    'website_slides':      "Обучающие курсы по BCM (если планируете)",

    # HR функции для больших организаций
    'hr_skills':           "Матрица навыков BCM команд",
    'hr_attendance':       "Учет присутствия в кризис",
}
```

## 📂 БЕЗОПАСНОЕ АРХИВИРОВАНИЕ МОДУЛЕЙ

### ✅ МОЖНО безопасно переместить в архив:
```bash
# Локализации (если не нужны конкретные страны)
l10n_* (кроме нужных стран)

# Специфичные индустрии
pos_*              # Point of Sale - касса
stock_*            # Складской учет
mrp_*              # Производство
fleet              # Автопарк
lunch              # Обеды
maintenance        # ТО оборудования

# Бухгалтерия (если не ведете)
account_*          # Все бухгалтерские модули

# E-commerce (если не продаете онлайн)
website_sale_*     # Интернет-магазин
payment_*          # Платежные шлюзы

# Специфичные интеграции
hw_*               # Hardware для POS
iot_*              # IoT устройства
```

### ⚠️ НЕ ПЕРЕМЕЩАЙТЕ в архив:
```bash
# Системные модули
base
web
mail
bus

# Модули аутентификации
auth_*             # ВСЕ auth модули нужны для безопасности

# Базовые расширения
base_*             # Расширения базового функционала

# HTTP и API
http_routing
iap
```

## 🔌 ИНТЕГРАЦИЯ BCM МОДУЛЕЙ С ODOO

### Структура зависимостей BCM модулей:

```python
# bcm_core/__manifest__.py - Базовый модуль
'depends': [
    'base', 'mail', 'web', 'bus',
    'crm',                    # Управление проектами
    'portal',                 # Внешний доступ
    'auth_totp',             # 2FA безопасность
    'analytic',              # Аналитика
]

# bcm_incident/__manifest__.py - Управление инцидентами
'depends': [
    'bcm_core',
    'sms',                   # SMS оповещения
    'mass_mailing',          # Массовые рассылки
    'calendar',              # Планирование реагирования
]

# bcm_audit/__manifest__.py - Аудиты и соответствие
'depends': [
    'bcm_core',
    'survey',                # Чек-листы аудита
    'attachment_indexation', # Поиск в документах
    'spreadsheet',          # Экспорт отчетов
]

# bcm_training/__manifest__.py - Обучение и развитие
'depends': [
    'bcm_core',
    'survey',               # Тесты знаний
    'gamification',         # Мотивация
    'hr_skills',           # Навыки персонала
]

# bcm_crm_bridge/__manifest__.py - Связка с CRM
'depends': [
    'bcm_core',
    'crm',                  # CRM функционал
    'bcm_audit',
    'bcm_training',
    'bcm_incident',
]

# bcm_community/__manifest__.py - Сообщество и marketplace
'depends': [
    'bcm_core',
    'gamification',         # Рейтинги
    'im_livechat',         # Поддержка
    'knowledge',           # База знаний
]
```

## 🔄 CRM КАК ЦЕНТР УПРАВЛЕНИЯ BCM ПРОЕКТАМИ

### Адаптация CRM под BCM консалтинг:
```python
# Переименовываем CRM в "BCM Workspace"
class BcmWorkspace(models.Model):
    _inherit = 'crm.lead'
    _description = 'BCM Consulting Project'

    # Pipeline стадии для BCM консалтинга
    STAGES = [
        'initial_contact',      # Первичный контакт
        'maturity_assessment',  # Оценка зрелости BCM
        'proposal',            # Коммерческое предложение
        'contract_signed',     # Контракт подписан
        'implementation',      # Внедрение BCM
        'support',            # Поддержка и сопровождение
    ]

    # BCM-специфичные поля
    bcm_maturity_score = fields.Float('Current BCM Maturity')
    iso_compliance = fields.Float('ISO 22301 Compliance %')
    organization_context = fields.Many2one('bcm.context')

    # Связи с BCM модулями
    bcm_audits = fields.One2many('bcm.audit', 'crm_project_id')
    bcm_incidents = fields.One2many('bcm.incident', 'crm_project_id')
    bcm_plans = fields.One2many('bcm.plan', 'crm_project_id')
    bcm_trainings = fields.One2many('bcm.training', 'crm_project_id')

    # Автоматический расчёт прогресса
    implementation_progress = fields.Float(
        compute='_compute_from_bcm_modules',
        string='BCM Implementation Progress'
    )
```

### Event Bus - связывает CRM с BCM модулями:
```python
class BcmEventBus:
    """Центральная шина событий BCM платформы"""

    # Когда проект выигран в CRM
    @on_event('crm.project.won')
    def initialize_bcm_workspace(project):
        # Автоматически создаем структуру BCM
        bcm_context.create_organization_profile(project)
        bcm_audit.schedule_initial_audit(project)
        bcm_plan.create_plan_templates(project)
        bcm_training.schedule_awareness_sessions(project)

    # Когда аудит завершен
    @on_event('bcm.audit.completed')
    def update_crm_compliance(audit):
        # Обновляем прогресс в CRM
        audit.crm_project_id.iso_compliance = audit.compliance_score
        # Уведомляем менеджера проекта
        audit.crm_project_id.user_id.notify('Audit completed')

    # Когда происходит инцидент
    @on_event('bcm.incident.critical')
    def escalate_to_crm(incident):
        # Эскалация в CRM для видимости руководства
        incident.crm_project_id.priority = 'urgent'
        incident.crm_project_id.tag_ids += 'active_incident'
```

### Два режима использования CRM:

#### Режим 1: Для BCM консультантов (полный функционал)
- Pipeline консалтинговых проектов
- Управление портфелем клиентов
- Прогнозирование выручки от BCM услуг
- KPI по эффективности консультантов
- Аналитика по типам проектов

#### Режим 2: Для организаций (упрощенный)
- Только управление заинтересованными сторонами
- Контакты для кризисных коммуникаций
- История взаимодействий
- БЕЗ коммерческих функций

## 🎯 ФУНКЦИОНАЛЬНАЯ КАРТА ПЛАТФОРМЫ

### Для консультантов/аудиторов:
- **CRM как BCM Workspace** - центр управления всеми проектами
- Pipeline от лида до поддержки клиента
- Автоматическая генерация BCM структуры при выигрыше проекта
- Инструменты проведения аудитов (survey + bcm_audit)
- Генерация отчетов (spreadsheet + bcm_reporting)
- База знаний и шаблоны (knowledge + bcm_templates)
- Рейтинги и достижения (gamification)
- Единый дашборд консультанта с метриками из всех модулей

### Для организаций-клиентов:
- Портал доступа к своим данным (portal)
- Обучающие материалы (survey + website_slides)
- Управление инцидентами (bcm_incident + sms)
- Планы и документы (bcm_plans + attachment_indexation)
- Календарь BCM активностей (calendar)
- Просмотр прогресса внедрения BCM из CRM

### Для платформы (SaaS):
- Безопасная мультитенантность (auth_* модули)
- API для интеграций (http_routing + iap)
- **Биллинг через CRM** - подписки, инвойсы, платежи
- **Marketplace консультантов** - рейтинги из CRM + gamification
- Аналитика использования (analytic + board)
- **Автоматизация через Event Bus** - связь CRM со всеми BCM модулями

## 🔧 ПРАКТИЧЕСКИЕ ПРИМЕРЫ РАСШИРЕНИЯ СТАНДАРТНЫХ МОДУЛЕЙ

### 📊 Survey → BCM Assessment Tool
```python
# bcm_survey/__manifest__.py
{
    'name': 'BCM Assessment Tool',
    'depends': ['survey', 'bcm_core'],
}

# models/bcm_survey.py
class BcmSurvey(models.Model):
    _inherit = 'survey.survey'

    # Добавляем BCM-специфичные поля
    assessment_type = fields.Selection([
        ('iso_22301_audit', 'ISO 22301 Compliance Audit'),
        ('maturity_assessment', 'BCM Maturity Assessment'),
        ('bia_questionnaire', 'Business Impact Analysis'),
        ('risk_assessment', 'Risk Assessment Survey'),
    ])
    iso_clause_mapping = fields.Text('ISO 22301 Clause Mapping')
    auto_calculate_maturity = fields.Boolean(default=True)

    # Готовые шаблоны BCM опросов
    @api.model
    def create_iso_22301_template(self):
        return self.create({
            'title': 'ISO 22301:2019 Compliance Checklist',
            'assessment_type': 'iso_22301_audit',
            'questions': self._get_iso_22301_questions(),
        })
```

### 📅 Calendar + SMS → BCM Crisis Calendar
```python
# bcm_calendar/__manifest__.py
{
    'name': 'BCM Crisis Calendar',
    'depends': ['calendar', 'sms', 'bcm_incident'],
}

# models/bcm_calendar.py
class BcmCalendarEvent(models.Model):
    _inherit = 'calendar.event'

    # BCM типы событий
    bcm_event_type = fields.Selection([
        ('drill', 'Emergency Drill'),
        ('audit', 'BCM Audit'),
        ('review', 'Plan Review'),
        ('training', 'Training Session'),
        ('incident', 'Active Incident'),
    ])

    # Автоматические SMS напоминания
    send_sms_reminder = fields.Boolean('Send SMS Alert')
    emergency_contacts = fields.Many2many('res.partner',
                                         domain=[('is_emergency_contact', '=', True)])

    # При создании инцидента - автоматическое событие
    @api.model
    def create_from_incident(self, incident):
        return self.create({
            'name': f'INCIDENT: {incident.name}',
            'bcm_event_type': 'incident',
            'start': fields.Datetime.now(),
            'attendee_ids': incident.response_team_ids,
            'send_sms_reminder': True,
            'priority': '1',  # Высший приоритет
        })
```

### 🎮 Gamification → BCM Achievements System
```python
# bcm_gamification/__manifest__.py
{
    'name': 'BCM Achievements & Certification',
    'depends': ['gamification', 'bcm_training', 'bcm_audit'],
}

# models/bcm_achievements.py
class BcmGoal(models.Model):
    _inherit = 'gamification.goal'

    # BCM-специфичные цели
    bcm_goal_type = fields.Selection([
        ('audits_completed', 'Complete N Audits'),
        ('iso_certified', 'Get ISO 22301 Certified'),
        ('incidents_resolved', 'Resolve N Incidents'),
        ('plans_reviewed', 'Review N Plans'),
        ('training_hours', 'Complete N Training Hours'),
    ])

    # Автоматические бейджи за BCM достижения
    @api.model
    def _create_bcm_badges(self):
        badges = [
            {'name': '🏆 ISO 22301 Expert', 'rule': 'Pass certification exam'},
            {'name': '🚨 Crisis Manager', 'rule': 'Manage 10+ incidents'},
            {'name': '📋 Audit Master', 'rule': 'Conduct 50+ audits'},
            {'name': '🎓 BCM Trainer', 'rule': 'Train 100+ people'},
            {'name': '⭐ BCM Champion', 'rule': '95%+ compliance score'},
        ]
        return badges
```

### 💬 Im_livechat → BCM Crisis Communication Center
```python
# bcm_livechat/__manifest__.py
{
    'name': 'BCM Crisis Communication Center',
    'depends': ['im_livechat', 'bcm_incident', 'mass_mailing_sms'],
}

# models/bcm_livechat.py
class BcmLivechatChannel(models.Model):
    _inherit = 'im_livechat.channel'

    # Кризисные каналы с приоритетами
    is_crisis_channel = fields.Boolean('Crisis Communication Channel')
    incident_id = fields.Many2one('bcm.incident', 'Related Incident')

    # Автоматическая эскалация
    auto_escalate = fields.Boolean(default=True)
    escalation_time = fields.Integer('Escalate after (min)', default=5)

    # Массовые оповещения из чата
    @api.multi
    def send_mass_alert(self, message):
        if self.is_crisis_channel:
            # SMS всем участникам инцидента
            self.incident_id.send_sms_to_response_team(message)
            # Email всем stakeholders
            self.incident_id.send_email_to_stakeholders(message)
            # Запись в лог инцидента
            self.incident_id.log_communication(message)
```

### 📚 Knowledge → BCM Knowledge Base
```python
# bcm_knowledge/__manifest__.py
{
    'name': 'BCM Knowledge Management',
    'depends': ['knowledge', 'bcm_core', 'bcm_community'],
}

# models/bcm_knowledge.py
class BcmKnowledgeArticle(models.Model):
    _inherit = 'knowledge.article'

    # Категоризация по ISO 22301
    iso_clause = fields.Char('ISO 22301 Clause Reference')
    article_type = fields.Selection([
        ('procedure', 'BCM Procedure'),
        ('template', 'Document Template'),
        ('guideline', 'Implementation Guide'),
        ('case_study', 'Case Study'),
        ('best_practice', 'Best Practice'),
    ])

    # Версионирование для compliance
    is_controlled_document = fields.Boolean('Controlled Document')
    approval_required = fields.Boolean('Requires Approval')
    review_frequency = fields.Integer('Review Every (months)', default=12)

    # Автоматическая генерация из аудитов
    @api.model
    def create_from_audit_findings(self, audit):
        for finding in audit.findings:
            self.create({
                'name': f'Lesson Learned: {finding.name}',
                'body': finding.recommendation,
                'iso_clause': finding.iso_clause,
                'article_type': 'best_practice',
            })
```

### 📊 Mass_mailing + SMS → BCM Alert System
```python
# bcm_alerts/__manifest__.py
{
    'name': 'BCM Multi-Channel Alert System',
    'depends': ['mass_mailing', 'sms', 'mail_group', 'bcm_incident'],
}

# models/bcm_alert.py
class BcmAlertCampaign(models.Model):
    _inherit = 'mailing.mailing'

    # BCM-специфичные типы оповещений
    alert_type = fields.Selection([
        ('test', 'Test Alert'),
        ('drill', 'Drill Notification'),
        ('incident', 'Incident Alert'),
        ('activation', 'Plan Activation'),
        ('all_clear', 'All Clear Message'),
    ])

    # Приоритетные каналы
    priority_channels = fields.Selection([
        ('sms_first', 'SMS → Email → Call'),
        ('email_first', 'Email → SMS → Call'),
        ('all_simultaneous', 'All Channels at Once'),
    ])

    # Шаблоны для разных сценариев
    @api.model
    def get_incident_template(self, incident_type):
        templates = {
            'fire': 'FIRE ALERT: Evacuate immediately via...',
            'cyber': 'CYBER INCIDENT: Disconnect all systems...',
            'pandemic': 'HEALTH ALERT: Remote work activated...',
        }
        return templates.get(incident_type, 'ALERT: Please stand by...')
```

### 🔄 CRM + Portal → BCM Client Portal
```python
# bcm_portal/__manifest__.py
{
    'name': 'BCM Client Self-Service Portal',
    'depends': ['portal', 'crm', 'bcm_core', 'bcm_audit'],
}

# models/bcm_portal.py
class BcmPortalAccess(models.Model):
    _inherit = 'portal.wizard'

    # Разные уровни доступа для BCM
    bcm_access_level = fields.Selection([
        ('viewer', 'View Only - Stakeholder'),
        ('contributor', 'Contribute - Team Member'),
        ('manager', 'Manage - BCM Coordinator'),
        ('auditor', 'Audit - External Auditor'),
    ])

    # Что видит клиент в портале
    def _get_portal_access_rights(self):
        return {
            'viewer': ['view_plans', 'view_reports'],
            'contributor': ['view_all', 'submit_updates', 'participate_drills'],
            'manager': ['full_access', 'approve_changes', 'manage_team'],
            'auditor': ['audit_access', 'view_evidence', 'create_findings'],
        }
```

## ⚡ КОМАНДА ДЛЯ АРХИВИРОВАНИЯ

```bash
# Создаем директорию для неиспользуемых модулей
mkdir -p /Users/MD/ISO-22301/archive/unused-odoo-modules/

# Перемещаем ненужные модули (безопасно)
cd /Users/MD/ISO-22301/core/odoo-18.0/addons/
mv pos_* stock_* mrp_* fleet lunch maintenance \
   account_* website_sale_* payment_* hw_* iot_* \
   /Users/MD/ISO-22301/archive/unused-odoo-modules/

# Оставляем все auth_*, base_*, mail, web, bus и выбранные модули
```

## 📊 ИТОГОВАЯ СТАТИСТИКА

- **Всего модулей в Odoo:** 496
- **Необходимо для BCM Platform:** ~35-40 модулей
- **Можно архивировать:** ~300+ модулей
- **Критически важны:** 8 модулей (core)
- **Важны для безопасности:** 6 модулей (auth_*)
- **BCM-специфичные:** 11 модулей
- **Расширенные возможности:** 15 модулей

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **ВСЕ `auth_*` модули критичны для безопасности** - НЕ удаляйте!
2. **Модули в `/addons/` не влияют на запуск**, пока не установлены
3. **Можно безопасно архивировать** ~300+ ненужных модулей
4. **CRM модуль** - использовать как основу для управления консалтинговыми проектами
5. **Event Bus** - связывает CRM с BCM модулями для полной автоматизации

## 🚀 РЕЗУЛЬТАТ

Получаем мощную BCM платформу с:
- Полным циклом от продажи до поддержки (CRM + BCM модули)
- Безопасной аутентификацией (auth_* модули)
- Готовыми инструментами для консультантов
- API для интеграций с внешними системами
- Минимальным количеством зависимостей (35-40 из 496)