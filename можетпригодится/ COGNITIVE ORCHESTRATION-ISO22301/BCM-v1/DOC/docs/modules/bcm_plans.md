# BCM Plans - Управление планами непрерывности

## Обзор модуля

**Назначение**: Управление планами непрерывности бизнеса, включая планы восстановления, кризисного реагирования, аварийного восстановления и коммуникационные планы.

**Расположение**: `core/odoo-18.0/addons/bcm_plans/`

## Ключевые модели

### BCMPlan (bcm.plan)
**Файл**: `models/bcm_plan.py:25`

**Основные поля**:
- `plan_name` (Char) - Название плана
- `plan_type` (Selection) - Тип плана (bcp, drp, crisis, communication, evacuation)
- `business_process_ids` (Many2many) - Связанные бизнес-процессы
- `activation_triggers` (Text) - Триггеры активации
- `rto_target` (Integer) - Целевое RTO (часы)
- `rpo_target` (Integer) - Целевое RPO (часы)
- `plan_owner` (Many2one) - Владелец плана
- `approval_status` (Selection) - Статус утверждения
- `last_tested_date` (Date) - Дата последнего тестирования
- `next_review_date` (Date) - Дата следующего пересмотра

**Ключевые методы**:
```python
def activate_plan(self, activation_context):
    """Активация плана непрерывности"""
    
def validate_plan_completeness(self):
    """Валидация полноты плана"""
    
def schedule_plan_test(self, test_type, test_date):
    """Планирование тестирования"""
```

### PlanStep (bcm.plan.step)
**Файл**: `models/plan_step.py:20`

**Основные поля**:
- `plan_id` (Many2one) - Родительский план
- `step_name` (Char) - Название шага
- `step_order` (Integer) - Порядок выполнения
- `responsible_person` (Many2one) - Ответственный
- `estimated_duration` (Integer) - Оценочная длительность (минуты)
- `prerequisites` (Text) - Предварительные условия
- `instructions` (Text) - Детальные инструкции
- `success_criteria` (Text) - Критерии успеха
- `escalation_procedure` (Text) - Процедура эскалации

### API Endpoints
```python
@http.route('/bcm/plans/activate', type='json', auth='user')
def activate_plan(self, plan_id, activation_context)

@http.route('/bcm/plans/test', type='json', auth='user') 
def initiate_plan_test(self, plan_id, test_type)
```

## Интеграции
- **BIA**: Автогенерация планов на основе BIA данных
- **Risk Management**: Планы митигации рисков
- **Incident Management**: Активация планов при инцидентах