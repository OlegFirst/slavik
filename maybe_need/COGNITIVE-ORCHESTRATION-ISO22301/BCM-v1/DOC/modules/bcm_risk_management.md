# BCM Risk Management - Управление рисками

## Обзор модуля

**Назначение**: Комплексное управление рисками непрерывности бизнеса. Модуль обеспечивает выявление, оценку, анализ и мониторинг рисков, которые могут повлиять на критичные бизнес-процессы и непрерывность деятельности организации.

**Расположение**: `core/odoo-18.0/addons/bcm_risk_management/`

## Ключевые компоненты

### Модели данных

#### 1. Risk (bcm.risk)
**Файл**: `models/risk.py:25`

**Назначение**: Основная модель управления рисками

**Поля**:
- `risk_id` (Char) - Уникальный идентификатор риска
- `title` (Char) - Название риска
- `description` (Text) - Детальное описание риска
- `category` (Selection) - Категория риска (operational, strategic, financial, compliance, cyber, natural)
- `source` (Selection) - Источник риска (internal, external, regulatory, technological)
- `risk_owner` (Many2one) - Владелец риска
- `identified_date` (Date) - Дата выявления
- `last_assessment_date` (Date) - Дата последней оценки
- `probability` (Selection) - Вероятность (very_low, low, medium, high, very_high)
- `impact` (Selection) - Воздействие (minimal, minor, moderate, major, severe)
- `inherent_risk_score` (Float) - Внутренний рейтинг риска
- `residual_risk_score` (Float) - Остаточный рейтинг риска
- `risk_appetite_status` (Selection) - Статус в рамках аппетита к риску (within, exceeds, critical)
- `status` (Selection) - Статус риска (active, monitoring, closed, archived)
- `treatment_strategy` (Selection) - Стратегия обработки (accept, avoid, mitigate, transfer)

**Ключевые методы**:
```python
def calculate_risk_score(self, probability, impact):
    """Расчет рейтинга риска на основе матрицы вероятность/воздействие"""
    
def update_risk_assessment(self, new_probability, new_impact, assessor):
    """Обновление оценки риска"""
    
def check_risk_appetite_compliance(self):
    """Проверка соответствия аппетиту к риску"""
    
def generate_treatment_recommendations(self):
    """Генерация рекомендаций по обработке риска"""
    
def get_ai_risk_prediction(self):
    """Получение AI-прогноза развития риска"""
```

#### 2. RiskAssessment (bcm.risk.assessment)
**Файл**: `models/risk_assessment.py:30`

**Назначение**: Управление процессами оценки рисков

**Поля**:
- `assessment_name` (Char) - Название оценки
- `assessment_date` (Date) - Дата оценки
- `assessor_id` (Many2one) - Оценщик
- `methodology` (Selection) - Методология (qualitative, quantitative, semi_quantitative)
- `scope` (Text) - Область оценки
- `risk_ids` (One2many) - Связанные риски
- `assessment_criteria` (Text) - Критерии оценки
- `assumptions` (Text) - Допущения
- `limitations` (Text) - Ограничения
- `completion_status` (Selection) - Статус завершения
- `review_frequency` (Selection) - Частота пересмотра
- `next_review_date` (Date) - Дата следующего пересмотра

#### 3. RiskTreatment (bcm.risk.treatment)
**Файл**: `models/risk_treatment.py:22`

**Назначение**: Управление мерами по обработке рисков

**Поля**:
- `risk_id` (Many2one) - Связанный риск
- `treatment_name` (Char) - Название меры
- `treatment_type` (Selection) - Тип обработки (preventive, detective, corrective, compensating)
- `description` (Text) - Описание меры
- `responsible_person` (Many2one) - Ответственное лицо
- `implementation_date` (Date) - Дата внедрения
- `target_completion_date` (Date) - Плановая дата завершения
- `actual_completion_date` (Date) - Фактическая дата завершения
- `status` (Selection) - Статус (planned, in_progress, completed, overdue, cancelled)
- `effectiveness_rating` (Selection) - Оценка эффективности
- `cost_estimate` (Float) - Оценочная стоимость
- `actual_cost` (Float) - Фактическая стоимость

#### 4. RiskScenario (bcm.risk.scenario)
**Файл**: `models/risk_scenario.py:28`

**Назначение**: Моделирование сценариев рисков

**Поля**:
- `scenario_name` (Char) - Название сценария
- `risk_ids` (Many2many) - Связанные риски
- `trigger_events` (Text) - Триггерные события
- `timeline` (Text) - Временная шкала развития
- `affected_processes` (Many2many) - Затронутые процессы
- `financial_impact_min` (Float) - Минимальное финансовое воздействие
- `financial_impact_max` (Float) - Максимальное финансовое воздействие
- `recovery_time_estimate` (Integer) - Оценочное время восстановления (часы)
- `scenario_probability` (Float) - Вероятность сценария
- `mitigation_strategies` (Text) - Стратегии митигации

### Контроллеры и API

#### 1. RiskManagementController
**Файл**: `controllers/risk_controller.py:20`

**Эндпоинты**:
```python
@http.route('/bcm/risk/calculate-score', type='json', auth='user')
def calculate_risk_score(self, probability, impact, methodology):
    """Расчет рейтинга риска"""

@http.route('/bcm/risk/matrix-analysis', type='json', auth='user')
def get_risk_matrix_data(self, assessment_id):
    """Получение данных для матрицы рисков"""

@http.route('/bcm/risk/trend-analysis', type='json', auth='user')
def analyze_risk_trends(self, risk_id, period_months):
    """Анализ трендов риска"""
    
@http.route('/bcm/risk/scenario-modeling', type='json', auth='user')
def model_risk_scenario(self, scenario_params):
    """Моделирование сценария риска"""
    
@http.route('/bcm/risk/ai-assessment', type='json', auth='user')
def trigger_ai_risk_assessment(self, risk_data):
    """Запуск AI-анализа риска"""
```

### Представления (Views)

#### 1. Risk Register
**Файл**: `views/risk_register_views.xml:25`

- Реестр рисков с фильтрацией по категориям
- Матрица рисков (heat map)
- Канбан-представление по статусам обработки
- Временная шкала рисков

#### 2. Risk Dashboard
**Файл**: `views/risk_dashboard.xml:40`

- KPI по управлению рисками
- Топ критичных рисков
- Статус выполнения мер по обработке
- Тренды изменения рисковой экспозиции

#### 3. Treatment Tracking
**Файл**: `views/treatment_views.xml:30`

- Отслеживание мер по обработке рисков
- Календарь дедлайнов
- Анализ эффективности мер
- Бюджетирование мер по рискам

### Методология оценки рисков

#### 1. Qualitative Assessment:
```python
PROBABILITY_LEVELS = [
    ('very_low', 'Очень низкая (< 5%)'),
    ('low', 'Низкая (5-15%)'),
    ('medium', 'Средняя (15-50%)'),
    ('high', 'Высокая (50-85%)'),
    ('very_high', 'Очень высокая (> 85%)')
]

IMPACT_LEVELS = [
    ('minimal', 'Минимальное'),
    ('minor', 'Незначительное'),  
    ('moderate', 'Умеренное'),
    ('major', 'Значительное'),
    ('severe', 'Критическое')
]
```

#### 2. Quantitative Assessment:
```python
def calculate_quantitative_risk(self, probability_percent, impact_amount):
    """Количественная оценка риска"""
    annual_loss_expectancy = probability_percent * impact_amount
    return {
        'ale': annual_loss_expectancy,
        'single_loss_expectancy': impact_amount,
        'annual_rate_of_occurrence': probability_percent
    }
```

#### 3. Risk Matrix:
- 5x5 матрица рисков
- Цветовое кодирование (зеленый/желтый/красный)
- Пороги для принятия решений
- Настраиваемые критерии оценки

### AI-интеграция

#### 1. Predictive Risk Analytics:
```python
class RiskPredictionService:
    def predict_risk_evolution(self, risk_id, time_horizon_months):
        """Прогнозирование развития риска"""
        
    def identify_emerging_risks(self, industry_data, company_context):
        """Выявление новых рисков на основе AI"""
        
    def correlate_risks(self, risk_portfolio):
        """Анализ корреляций между рисками"""
        
    def optimize_treatment_portfolio(self, risks, budget_constraints):
        """Оптимизация портфеля мер по обработке рисков"""
```

#### 2. Natural Language Processing:
- Автоматическое извлечение рисков из документов
- Анализ настроений в новостях и соцсетях
- Классификация рисков по категориям
- Генерация описаний рисков

### Интеграции с другими модулями

#### С BCM BIA:
```python
def link_risks_to_processes(self, risk_id, process_ids):
    """Связывание рисков с критичными процессами"""
    
def assess_process_risk_exposure(self, process_id):
    """Оценка рисковой экспозиции процесса"""
    
def calculate_risk_adjusted_rto(self, process_id, risk_scenarios):
    """Расчет RTO с учетом рисков"""
```

#### С BCM Incident Management:
```python
def convert_incident_to_risk(self, incident_id):
    """Конвертация инцидента в риск"""
    
def update_risk_from_incident_lessons(self, incident_id, risk_id):
    """Обновление риска на основе уроков инцидента"""
```

#### С BCM Plans:
```python
def generate_risk_based_scenarios(self, plan_id):
    """Генерация сценариев для планов на основе рисков"""
    
def validate_plan_risk_coverage(self, plan_id, risk_ids):
    """Проверка покрытия рисков в планах"""
```

### Отчетность

#### 1. Risk Register Report
**Файл**: `reports/risk_register_report.xml:25`

- Полный реестр рисков
- Фильтрация по критериям
- Экспорт в различные форматы
- Сравнение между оценками

#### 2. Risk Matrix Report
**Файл**: `reports/risk_matrix_report.xml:20`

- Визуализация матрицы рисков
- Тепловая карта
- Распределение по квадрантам
- Динамика изменений

#### 3. Treatment Effectiveness Report
**Файл**: `reports/treatment_report.xml:30`

- Анализ эффективности мер
- ROI мер по обработке рисков
- Статус выполнения планов
- Бюджетный анализ

### Compliance и стандарты

#### ISO 27005 Risk Management:
- Установление контекста
- Идентификация рисков
- Анализ рисков
- Оценка рисков
- Обработка рисков

#### ISO 31000 Risk Management:
- Принципы управления рисками
- Структура управления
- Процесс управления рисками

#### COSO ERM Framework:
- Внутренняя среда
- Установление целей
- Идентификация событий
- Оценка рисков
- Реагирование на риски

### Автоматизация

#### 1. Автоматическое обновление:
- Периодический пересмотр рисков
- Обновление статусов мер
- Эскалация просроченных задач
- Уведомления заинтересованным сторонам

#### 2. Интеграция с внешними источниками:
- Мониторинг новостей и событий
- Интеграция с threat intelligence feeds
- Анализ регуляторных изменений
- Мониторинг cyber threat landscape

### Безопасность и права доступа

#### Группы пользователей:
- `bcm_risk_management.group_risk_admin` - Администраторы рисков
- `bcm_risk_management.group_risk_manager` - Менеджеры по рискам
- `bcm_risk_management.group_risk_owner` - Владельцы рисков
- `bcm_risk_management.group_risk_viewer` - Просмотр рисков

#### Конфиденциальность:
- Классификация рисков по уровням доступа
- Шифрование чувствительной информации
- Аудит доступа к данным о рисках
- Ограничения на экспорт данных

### KPI и метрики

#### Основные KPI:
- Количество идентифицированных рисков
- Процент рисков в рамках аппетита
- Средний рейтинг рисков по категориям
- Процент завершения мер по обработке рисков в срок
- ROI мер по управлению рисками

#### Аналитические метрики:
- Тренды изменения рисковой экспозиции
- Распределение рисков по вероятности/воздействию
- Эффективность различных стратегий обработки
- Корреляция между рисками и инцидентами

### Workflow управления рисками

#### 1. Выявление риска:
Идентификация → Регистрация → Первичная оценка → Назначение владельца → Детальная оценка

#### 2. Оценка риска:
Анализ вероятности → Анализ воздействия → Расчет рейтинга → Сравнение с аппетитом → Утверждение оценки

#### 3. Обработка риска:
Выбор стратегии → Планирование мер → Выделение ресурсов → Реализация → Мониторинг эффективности

#### 4. Мониторинг и пересмотр:
Периодический пересмотр → Обновление оценки → Корректировка мер → Отчетность → Архивирование

### Планы развития

- Интеграция с external risk intelligence платформами
- Развитие predictive analytics возможностей
- Внедрение blockchain для immutable risk records
- Расширение AI capabilities для автоматической идентификации рисков
- Интеграция с IoT для real-time risk monitoring