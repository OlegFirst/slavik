# BCM BIA - Анализ воздействия на бизнес

## Обзор модуля

**Назначение**: Business Impact Analysis (BIA) - анализ воздействия на бизнес. Модуль обеспечивает комплексную оценку критичности бизнес-процессов, определение RTO/RPO и финансового воздействия при нарушении непрерывности.

**Расположение**: `core/odoo-18.0/addons/bcm_bia/`

## Ключевые компоненты

### Модели данных

#### 1. BusinessProcess (bcm.business.process)
**Файл**: `models/business_process.py:20`

**Назначение**: Основная модель бизнес-процессов для BIA

**Поля**:
- `name` (Char) - Название бизнес-процесса
- `description` (Text) - Детальное описание процесса
- `process_owner` (Many2one) - Владелец процесса
- `department_id` (Many2one) - Подразделение
- `criticality_level` (Selection) - Уровень критичности (critical, high, medium, low)
- `rto_hours` (Integer) - Recovery Time Objective (часы)
- `rpo_hours` (Integer) - Recovery Point Objective (часы)  
- `mao_hours` (Integer) - Maximum Allowable Outage (часы)
- `mtd_hours` (Integer) - Maximum Tolerable Downtime (часы)
- `financial_impact_hourly` (Float) - Финансовые потери за час (руб.)
- `regulatory_impact` (Boolean) - Есть ли регуляторные требования
- `reputational_impact` (Integer) - Репутационные риски (1-10)
- `customer_impact` (Integer) - Влияние на клиентов (1-10)
- `operational_impact` (Integer) - Операционное воздействие (1-10)

**Ключевые методы**:
```python
def calculate_total_impact(self, outage_duration_hours):
    """Расчет общего воздействия при простое заданной длительности"""
    
def get_ai_optimized_rto_rpo(self):
    """Получение AI-оптимизированных RTO/RPO рекомендаций"""
    
def validate_rto_rpo_constraints(self):
    """Валидация ограничений RTO/RPO (RTO >= RPO)"""
    
def generate_impact_scenario(self, scenario_type):
    """Генерация сценария воздействия"""
```

#### 2. BIAAssessment (bcm.bia.assessment)
**Файл**: `models/bia_assessment.py:35`

**Назначение**: Управление BIA оценками и их жизненным циклом

**Поля**:
- `assessment_name` (Char) - Название оценки
- `assessment_date` (Date) - Дата проведения оценки
- `assessor_id` (Many2one) - Оценщик
- `business_process_ids` (One2many) - Связанные бизнес-процессы
- `status` (Selection) - Статус (draft, in_progress, completed, reviewed, approved)
- `methodology` (Selection) - Методология (quantitative, qualitative, mixed)
- `scope_description` (Text) - Описание области оценки
- `assumptions` (Text) - Допущения при оценке
- `limitations` (Text) - Ограничения оценки
- `next_review_date` (Date) - Дата следующего пересмотра
- `approval_date` (Date) - Дата утверждения
- `approved_by` (Many2one) - Кто утвердил

**Методы**:
```python
def start_assessment(self):
    """Запуск процесса BIA оценки"""
    
def complete_assessment(self):
    """Завершение BIA оценки с валидацией"""
    
def schedule_review(self, review_period_months):
    """Планирование пересмотра BIA"""
    
def generate_bia_report(self):
    """Генерация отчета по BIA"""
```

#### 3. DependencyMapping (bcm.dependency.mapping)
**Файл**: `models/dependency_mapping.py:28`

**Назначение**: Картирование зависимостей между бизнес-процессами

**Поля**:
- `source_process_id` (Many2one) - Исходный процесс
- `target_process_id` (Many2one) - Зависимый процесс  
- `dependency_type` (Selection) - Тип зависимости (sequential, parallel, conditional)
- `criticality` (Selection) - Критичность зависимости
- `failure_impact` (Text) - Описание воздействия при сбое
- `recovery_sequence` (Integer) - Порядок восстановления
- `dependency_strength` (Float) - Сила зависимости (0.0-1.0)

#### 4. ResourceRequirement (bcm.resource.requirement)
**Файл**: `models/resource_requirement.py:18`

**Назначение**: Управление требованиями к ресурсам для бизнес-процессов

**Поля**:
- `business_process_id` (Many2one) - Связанный бизнес-процесс
- `resource_type` (Selection) - Тип ресурса (human, technical, facility, data)
- `resource_name` (Char) - Название ресурса
- `quantity_required` (Float) - Требуемое количество
- `unit_of_measure` (Char) - Единица измерения
- `criticality` (Selection) - Критичность ресурса
- `alternative_available` (Boolean) - Доступна ли альтернатива
- `recovery_priority` (Integer) - Приоритет восстановления
- `cost_per_unit` (Float) - Стоимость за единицу

### Контроллеры и API

#### 1. BIAController
**Файл**: `controllers/bia_controller.py:25`

**Эндпоинты**:
```python
@http.route('/bcm/bia/calculate-impact', type='json', auth='user')
def calculate_business_impact(self, process_id, outage_hours):
    """Расчет воздействия на бизнес для процесса"""

@http.route('/bcm/bia/optimize-rto-rpo', type='json', auth='user')
def optimize_rto_rpo(self, process_id):
    """AI-оптимизация RTO/RPO параметров"""

@http.route('/bcm/bia/dependency-analysis', type='json', auth='user')
def analyze_dependencies(self, process_id):
    """Анализ зависимостей процесса"""
    
@http.route('/bcm/bia/generate-report', type='json', auth='user')
def generate_bia_report(self, assessment_id, report_format):
    """Генерация BIA отчета"""
```

### Представления (Views)

#### 1. Business Process Management
**Файл**: `views/business_process_views.xml:30`

- Канбан-представление процессов по критичности
- Форма детального редактирования процесса
- Граф зависимостей между процессами
- Календарь планирования BIA оценок

#### 2. BIA Dashboard  
**Файл**: `views/bia_dashboard.xml:45`

- Метрики по критичности процессов
- Тепловая карта RTO/RPO
- Финансовое воздействие по департаментам
- Статус BIA оценок

#### 3. Impact Analysis Views
**Файл**: `views/impact_analysis_views.xml:25`

- Матрица воздействия по времени
- Графики финансовых потерь
- Сравнительный анализ процессов

### Отчеты

#### 1. BIA Executive Summary
**Файл**: `reports/bia_executive_report.xml:20`

- Краткий обзор для руководства
- Критичные процессы и их RTO/RPO  
- Финансовые риски
- Рекомендации по улучшению

#### 2. Detailed Process Analysis
**Файл**: `reports/process_analysis_report.xml:40`

- Детальный анализ каждого процесса
- Зависимости и ресурсы
- Сценарии воздействия
- Планы восстановления

#### 3. Dependency Map Report
**Файл**: `reports/dependency_report.xml:15`

- Визуализация зависимостей
- Критические пути восстановления
- Анализ каскадных сбоев

### Интеграции

#### С BCM Intelligent Base:
```python
def get_ai_rto_rpo_recommendations(self, process_data):
    """Получение AI рекомендаций по оптимизации RTO/RPO"""
    
def predict_cascading_failures(self, failed_process_id):
    """Прогнозирование каскадных сбоев"""
    
def optimize_recovery_sequence(self, affected_processes):
    """Оптимизация последовательности восстановления"""
```

#### С BCM Risk Management:
```python
def assess_process_risks(self, process_id):
    """Оценка рисков для бизнес-процесса"""
    
def link_bia_to_risk_register(self, assessment_id):
    """Связывание BIA с реестром рисков"""
```

#### С BCM Plans:
```python
def generate_recovery_strategies(self, process_id):
    """Генерация стратегий восстановления на основе BIA"""
    
def validate_plan_rto_compliance(self, plan_id, process_id):
    """Проверка соответствия планов RTO требованиям"""
```

### Методология BIA

#### 1. Quantitative Analysis:
- Прямые финансовые потери
- Косвенные затраты  
- Альтернативная стоимость
- Штрафы и пени

#### 2. Qualitative Analysis:
- Репутационные риски
- Влияние на клиентов
- Регуляторные последствия  
- Конкурентные преимущества

#### 3. Time-based Analysis:
- Немедленное воздействие (0-4 часа)
- Краткосрочное воздействие (4-24 часа)  
- Среднесрочное воздействие (1-7 дней)
- Долгосрочное воздействие (>7 дней)

### Автоматизация и AI

#### ML-модели для оптимизации:
```python
class RTORPOOptimizer:
    def optimize_parameters(self, process_characteristics, constraints):
        """Оптимизация RTO/RPO с учетом ограничений"""
        
    def predict_optimal_mao(self, historical_data, business_context):
        """Прогнозирование оптимального MAO"""
        
    def recommend_resource_allocation(self, processes, available_resources):
        """Рекомендации по распределению ресурсов"""
```

#### Автоматическое планирование:
- Планирование BIA оценок
- Напоминания о пересмотре
- Автоматическая валидация данных
- Генерация отчетов по расписанию

### Compliance и стандарты

#### ISO 22301 соответствие:
- Раздел 8.2.1 - Анализ воздействия на бизнес  
- Определение критичных процессов
- Установление RTO и RPO
- Оценка зависимостей

#### Дополнительные стандарты:
- NIST SP 800-34 (IT Contingency Planning)
- BS 25999 (Business Continuity)
- ISO 27031 (ICT continuity)

### Безопасность

#### Права доступа:
- `bcm_bia.group_bia_admin` - Администраторы BIA
- `bcm_bia.group_bia_analyst` - BIA аналитики  
- `bcm_bia.group_process_owner` - Владельцы процессов
- `bcm_bia.group_bia_viewer` - Просмотр BIA данных

#### Конфиденциальность:
- Шифрование финансовых данных
- Ограниченный доступ к критичной информации
- Аудит доступа к BIA данным

### KPI и метрики

#### Основные KPI:
- Покрытие бизнес-процессов BIA оценками (%)
- Среднее RTO по критичным процессам
- Среднее RPO по критичным процессам
- Общие финансовые риски (руб./день)
- Количество процессов по уровням критичности

#### Аналитические метрики:
- Распределение RTO/RPO по департаментам
- Корреляция между критичностью и ресурсами
- Эффективность AI-оптимизации параметров
- Скорость завершения BIA оценок

### Планы развития

- Интеграция с внешними ERP системами для автоматического сбора данных
- Развитие ML моделей для более точного прогнозирования
- Внедрение real-time мониторинга критичных процессов
- Расширение методологии BIA для облачных сервисов