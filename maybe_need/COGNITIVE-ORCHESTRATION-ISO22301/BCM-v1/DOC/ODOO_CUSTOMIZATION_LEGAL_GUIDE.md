# 📜 Правовые аспекты кастомизации Odoo модулей для BCM

## ⚖️ Лицензирование Odoo

### Odoo Community Edition (что вы используете)
```
Лицензия: LGPL-3.0 (Lesser General Public License)
Версия: Odoo 18.0 Community
```

### Что это значит для вас:

✅ **МОЖНО:**
- Свободно использовать в коммерческих целях
- Модифицировать любые модули
- Создавать производные модули
- Не публиковать ваши модули (если они отдельные)
- Продавать ваше решение как SaaS

⚠️ **НУЖНО УЧИТЫВАТЬ:**
- Если вы ИЗМЕНЯЕТЕ существующие модули Odoo - изменения под LGPL
- Если вы НАСЛЕДУЕТЕ (_inherit) - ваш модуль может быть proprietary
- Если вы КОПИРУЕТЕ код - нужно сохранять лицензию

❌ **НЕЛЬЗЯ:**
- Удалять копирайты Odoo S.A.
- Использовать Odoo Enterprise модули без лицензии
- Называть свой продукт "Odoo" (trademark)

---

## 🎯 Стратегии кастомизации модулей

### Стратегия 1: НАСЛЕДОВАНИЕ (Рекомендую!)

**Правовой статус:** ✅ Полностью легально, ваш код - ваша собственность

```python
# bcm_project/__manifest__.py
{
    'name': 'BCM Project Management',
    'version': '1.0',
    'license': 'OPL-1',  # Ваша проприетарная лицензия!
    'author': 'Your Company',
    'depends': ['project'],  # Наследуем стандартный модуль
    'data': [
        'views/bcm_project_views.xml',
    ],
}

# bcm_project/models/project.py
from odoo import models, fields, api

class BCMProject(models.Model):
    _inherit = 'project.project'  # Расширяем, не копируем!

    # Добавляем BCM-специфичные поля
    bcm_type = fields.Selection([
        ('recovery', 'Recovery Plan'),
        ('exercise', 'Exercise'),
        ('audit', 'BCM Audit'),
        ('incident', 'Incident Response'),
    ], string='BCM Type')

    recovery_time_objective = fields.Float('RTO (hours)')
    recovery_point_objective = fields.Float('RPO (hours)')
    criticality_level = fields.Selection([
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ])

    # BCM-специфичные методы
    def generate_recovery_tasks(self):
        """Генерация задач восстановления через AI"""
        # Ваш проприетарный код
        pass

class BCMTask(models.Model):
    _inherit = 'project.task'

    # BCM расширения для задач
    task_criticality = fields.Selection([
        ('immediate', 'Immediate Action'),
        ('urgent', 'Urgent'),
        ('normal', 'Normal'),
        ('low', 'Low Priority'),
    ])

    recovery_sequence = fields.Integer('Recovery Sequence')
    dependencies = fields.Many2many('project.task', 'task_dependencies_rel',
                                   'task_id', 'depends_on_id',
                                   string='Dependencies')
```

### Стратегия 2: КОМПОЗИЦИЯ (Создание новых моделей)

**Правовой статус:** ✅ 100% ваш код

```python
# bcm_planning/models/bcm_planning.py
class BCMPlanning(models.Model):
    _name = 'bcm.planning'
    _description = 'BCM Planning Management'

    # Связь со стандартными модулями
    project_id = fields.Many2one('project.project', 'Related Project')
    calendar_event_ids = fields.One2many('calendar.event', 'bcm_planning_id')

    # Ваша BCM логика
    def sync_with_project(self):
        """Синхронизация с project module"""
        if not self.project_id:
            self.project_id = self.env['project.project'].create({
                'name': f'BCM: {self.name}',
                'user_id': self.responsible_id.id,
            })
```

### Стратегия 3: OVERRIDE (Переопределение)

**Правовой статус:** ⚠️ Осторожно с лицензией

```python
# bcm_documents/models/documents.py
class BCMDocument(models.Model):
    _inherit = 'documents.document'

    # Переопределяем метод (осторожно!)
    @api.model
    def create(self, vals):
        # Добавляем BCM логику
        if vals.get('folder_id') == self.get_bcm_folder_id():
            vals['tag_ids'] = self._get_bcm_tags()

            # AI обработка
            self.env['bcm.ai.processor'].process_document(vals)

        return super().create(vals)
```

---

## 🔧 Практические примеры трансформации

### 1. Project → BCM Project Management

```python
# bcm_project_management/__manifest__.py
{
    'name': 'BCM Project Management',
    'version': '18.0.1.0.0',
    'category': 'BCM/Management',
    'summary': 'BCM-enhanced Project Management',
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'license': 'OPL-1',  # Ваша лицензия
    'depends': [
        'project',
        'project_forecast',  # Если есть
        'hr_timesheet',      # Для учета времени
        'bcm_core',          # Ваш базовый модуль
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/bcm_project_views.xml',
        'views/bcm_project_templates.xml',
        'data/bcm_project_stages.xml',
        'wizard/generate_recovery_plan.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'bcm_project_management/static/src/js/gantt_view.js',
            'bcm_project_management/static/src/css/bcm_styles.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

```xml
<!-- views/bcm_project_views.xml -->
<odoo>
    <!-- Расширяем стандартную форму проекта -->
    <record id="view_project_form_bcm" model="ir.ui.view">
        <field name="name">project.project.form.bcm</field>
        <field name="model">project.project</field>
        <field name="inherit_id" ref="project.edit_project"/>
        <field name="arch" type="xml">
            <!-- Добавляем BCM вкладку -->
            <notebook position="inside">
                <page string="BCM Configuration">
                    <group>
                        <group>
                            <field name="bcm_type"/>
                            <field name="criticality_level"/>
                            <field name="recovery_time_objective" widget="float_time"/>
                            <field name="recovery_point_objective" widget="float_time"/>
                        </group>
                        <group>
                            <field name="risk_assessment_ids">
                                <tree>
                                    <field name="risk_type"/>
                                    <field name="probability"/>
                                    <field name="impact"/>
                                    <field name="mitigation_plan"/>
                                </tree>
                            </field>
                        </group>
                    </group>

                    <!-- AI Actions -->
                    <footer>
                        <button name="generate_recovery_tasks"
                                type="object"
                                string="Generate Recovery Tasks (AI)"
                                class="btn-primary"/>
                        <button name="analyze_dependencies"
                                type="object"
                                string="Analyze Dependencies"/>
                    </footer>
                </page>
            </notebook>
        </field>
    </record>

    <!-- Новое BCM меню -->
    <menuitem id="menu_bcm_projects"
              name="BCM Projects"
              parent="project.menu_main_pm"
              action="project.open_view_project_all"
              sequence="5"/>
</odoo>
```

### 2. Calendar → BCM Exercise Planning

```python
# bcm_exercise_calendar/models/calendar.py
class BCMCalendarEvent(models.Model):
    _inherit = 'calendar.event'

    # BCM Exercise fields
    is_bcm_exercise = fields.Boolean('Is BCM Exercise')
    exercise_type = fields.Selection([
        ('tabletop', 'Tabletop Exercise'),
        ('functional', 'Functional Exercise'),
        ('full_scale', 'Full Scale Exercise'),
        ('drill', 'Drill'),
    ])

    scenario_id = fields.Many2one('bcm.scenario', 'Exercise Scenario')
    participant_ids = fields.Many2many('res.partner', 'bcm_exercise_participants_rel')
    success_criteria = fields.Text('Success Criteria')

    # AI интеграция
    @api.model
    def create(self, vals):
        event = super().create(vals)
        if event.is_bcm_exercise:
            # AI генерирует сценарий
            self.env['bcm.ai.orchestrator'].generate_exercise_scenario(event)
        return event
```

### 3. Documents → BCM Document Management

```python
# bcm_documents/models/bcm_documents.py
class BCMDocumentFolder(models.Model):
    _inherit = 'documents.folder'

    is_bcm_folder = fields.Boolean('BCM Folder')
    bcm_category = fields.Selection([
        ('plans', 'BCM Plans'),
        ('procedures', 'Procedures'),
        ('templates', 'Templates'),
        ('reports', 'Reports'),
        ('evidence', 'Audit Evidence'),
    ])

    iso_22301_mapping = fields.Char('ISO 22301 Clause')
    retention_period = fields.Integer('Retention Period (years)')

class BCMDocument(models.Model):
    _inherit = 'documents.document'

    # BCM metadata
    document_criticality = fields.Selection([
        ('vital', 'Vital Record'),
        ('important', 'Important'),
        ('useful', 'Useful'),
        ('non_essential', 'Non-Essential'),
    ])

    recovery_priority = fields.Integer('Recovery Priority')
    last_review_date = fields.Date('Last Review Date')
    next_review_date = fields.Date('Next Review Date')

    # AI processing
    ai_summary = fields.Text('AI Generated Summary')
    ai_tags = fields.Many2many('documents.tag', 'bcm_doc_ai_tags_rel')

    @api.model
    def create(self, vals):
        doc = super().create(vals)
        if doc.folder_id.is_bcm_folder:
            # AI обработка
            self.env['bcm.document.ai'].process_document(doc)
        return doc
```

---

## 📋 Чек-лист легальной кастомизации

### ✅ Всегда безопасно:
```python
# 1. Наследование через _inherit
class MyModel(models.Model):
    _inherit = 'standard.model'
    my_field = fields.Char()  # Ваше поле

# 2. Создание своих моделей
class MyNewModel(models.Model):
    _name = 'my.new.model'
    standard_link = fields.Many2one('standard.model')

# 3. Переопределение views
<field name="inherit_id" ref="module.view_id"/>

# 4. Добавление меню и actions
<menuitem id="my_menu" parent="standard.menu"/>
```

### ⚠️ Требует внимания:
```python
# 1. Полное переопределение методов
def create(self, vals):
    # Много своего кода
    return super().create(vals)

# 2. Monkey patching
original_method = Model.method
def new_method(self):
    # ...
Model.method = new_method

# 3. Прямое изменение исходников Odoo
# НЕ ДЕЛАЙТЕ ТАК!
```

### ❌ Избегайте:
- Копирование целых модулей Odoo
- Удаление копирайтов
- Изменение core файлов Odoo
- Использование Enterprise модулей без лицензии

---

## 🚀 Рекомендуемый план действий

### Шаг 1: Создайте базовые BCM расширения
```bash
bcm_modules/
├── bcm_project_management/     # Extends project
├── bcm_calendar_planning/       # Extends calendar
├── bcm_document_management/     # Extends documents
├── bcm_automation_rules/        # Extends base_automation
└── bcm_reporting_dashboards/    # Extends board, web_dashboard
```

### Шаг 2: Сохраняйте правильную структуру
```python
# Каждый модуль:
module/
├── __init__.py
├── __manifest__.py          # license: 'OPL-1' или ваша
├── models/
│   ├── __init__.py
│   └── inherited_model.py   # _inherit = 'original.model'
├── views/
│   └── inherited_views.xml  # inherit_id
├── security/
│   └── ir.model.access.csv
└── static/
    └── description/
        └── icon.png
```

### Шаг 3: Документируйте изменения
```python
class ProjectInherit(models.Model):
    """
    BCM Extension for project.project

    This module extends standard Odoo Project Management with:
    - BCM-specific fields (RTO, RPO, criticality)
    - Recovery planning functionality
    - AI-powered task generation

    License: Proprietary
    Copyright: Your Company 2024
    Based on: Odoo Community 18.0 (LGPL-3.0)
    """
    _inherit = 'project.project'
```

---

## 💡 Итоговые рекомендации

### Можете смело:
1. **Наследовать** все нужные модули через `_inherit`
2. **Добавлять** BCM-специфичные поля и методы
3. **Создавать** свои views и меню
4. **Интегрировать** с вашими AI сервисами
5. **Лицензировать** свои модули как proprietary

### Юридическая безопасность:
- Ваши BCM модули = Ваша интеллектуальная собственность
- Odoo Community = Остается LGPL
- Можете продавать как SaaS
- Можете не публиковать исходники

### Техническая стратегия:
```
Odoo стандартные модули (LGPL)
        ↓
    _inherit
        ↓
Ваши BCM модули (Proprietary)
        ↓
    API calls
        ↓
Ваши AI сервисы (Proprietary)
```

Это полностью легально и это стандартная практика в экосистеме Odoo!

---

*Документ подготовлен: 2025-01-29*
*Disclaimer: Это техническая рекомендация, для юридических вопросов консультируйтесь с юристом*