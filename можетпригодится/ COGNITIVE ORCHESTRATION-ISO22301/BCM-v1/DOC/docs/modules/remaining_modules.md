# Остальные BCM модули - Краткое описание

## bcm_clients - Управление клиентами
**Назначение**: Мульти-тенантная архитектура с полной изоляцией данных клиентов
- **Модели**: BCMClient, ClientConfiguration, ClientBranding
- **Функции**: Изоляция данных, кастомизация, биллинг, управление подписками
- **API**: `/bcm/clients/onboard`, `/bcm/clients/configure`

## bcm_config - Конфигурация системы
**Назначение**: Централизованная конфигурация BCM платформы
- **Модели**: BCMConfiguration, SystemParameter, IntegrationConfig
- **Функции**: Системные настройки, интеграции, пользовательские параметры
- **API**: `/bcm/config/get`, `/bcm/config/update`

## bcm_context - Управление контекстом
**Назначение**: Контекстуальная индексация и поиск по BCM данным
- **Модели**: ContextIndex, SearchableEntity, ContextRelation
- **Функции**: Семантический поиск, связанные данные, контекстная навигация
- **Интеграция**: Elasticsearch для индексирования

## bcm_audit - Аудит и соответствие
**Назначение**: Комплексный аудит BCM процессов и соответствие стандартам
- **Модели**: AuditPlan, AuditFinding, ComplianceCheck, AuditEvidence
- **Функции**: Планирование аудитов, трекинг findings, compliance мониторинг
- **Стандарты**: ISO 22301, ISO 27001, SOX, GDPR
- **API**: `/bcm/audit/plan`, `/bcm/audit/findings`

## bcm_exercise - Тестирование и учения
**Назначение**: Планирование, проведение и анализ BCM тестирований
- **Модели**: Exercise, ExerciseScenario, ExerciseParticipant, ExerciseResults
- **Типы**: Tabletop, Walkthrough, Simulation, Full-scale
- **Функции**: Планирование, выполнение, анализ результатов, уроки
- **API**: `/bcm/exercise/schedule`, `/bcm/exercise/results`

## bcm_governance - Корпоративное управление
**Назначение**: Управление BCM governance и надзор
- **Модели**: GovernanceStructure, BCMCommittee, PolicyDocument, Stakeholder  
- **Функции**: Структуры управления, политики, роли и ответственность
- **Процессы**: Утверждения, пересмотры, эскалации
- **API**: `/bcm/governance/policies`, `/bcm/governance/approvals`

## bcm_kpi - Ключевые показатели
**Назначение**: Управление BCM метриками и KPI
- **Модели**: KPIDefinition, KPIMeasurement, KPIDashboard, KPITarget
- **Категории**: Operational, Strategic, Compliance, Financial
- **Функции**: Определение KPI, измерение, дашборды, целевые значения
- **API**: `/bcm/kpi/metrics`, `/bcm/kpi/dashboard`

## bcm_reporting - Отчетность
**Назначение**: Генерация BCM отчетов и аналитики
- **Модели**: ReportTemplate, ScheduledReport, ReportDistribution
- **Типы отчетов**: Executive, Operational, Compliance, Technical
- **Форматы**: PDF, Excel, HTML, CSV
- **API**: `/bcm/reports/generate`, `/bcm/reports/schedule`

## bcm_scenario_hub - Центр сценариев
**Назначение**: Маркетплейс BCM сценариев и лучших практик
- **Модели**: ScenarioTemplate, ScenarioMarketplace, ScenarioRating
- **Функции**: Шаблоны сценариев, рейтинги, комментарии, адаптация
- **Категории**: Industry-specific, Geographic, Threat-based
- **API**: `/bcm/scenarios/marketplace`, `/bcm/scenarios/apply`

## bcm_templates - Шаблоны документов  
**Назначение**: Управление шаблонами BCM документов
- **Модели**: DocumentTemplate, TemplateCategory, TemplateVersion
- **Типы**: Планы, процедуры, отчеты, коммуникации
- **Функции**: Создание, версионирование, кастомизация
- **API**: `/bcm/templates/list`, `/bcm/templates/generate`

## bcm_training - Обучение и тренинги
**Назначение**: Управление BCM обучением и повышением осведомленности
- **Модели**: TrainingProgram, TrainingSession, TrainingMaterial, Competency
- **Типы**: Online, Classroom, Simulation, Certification
- **Функции**: Планирование, отслеживание прогресса, сертификация
- **API**: `/bcm/training/enroll`, `/bcm/training/progress`

## bcm_incident - Базовая модель инцидентов
**Назначение**: Упрощенная модель инцидентов (используется как основа)
- **Модели**: BasicIncident, IncidentType, IncidentImpact
- **Функции**: Базовая регистрация, типизация, классификация
- **Связь**: Расширяется в bcm_incident_management

---

## Интеграционная матрица модулей

| Модуль | Зависимости | Интегрируется с |
|--------|-------------|-----------------|
| bcm_clients | bcm_core | Все модули |
| bcm_config | bcm_core | bcm_intelligent_base |
| bcm_context | bcm_core | Все модули для индексации |
| bcm_audit | bcm_core, bcm_governance | bcm_plans, bcm_risk_management |
| bcm_exercise | bcm_core, bcm_plans | bcm_bia, bcm_incident_management |
| bcm_governance | bcm_core | bcm_audit, bcm_templates |
| bcm_kpi | bcm_core | bcm_reporting, bcm_portal |
| bcm_reporting | bcm_core | Все модули (источники данных) |
| bcm_scenario_hub | bcm_core | bcm_plans, bcm_exercise |
| bcm_templates | bcm_core | bcm_plans, bcm_governance |
| bcm_training | bcm_core | bcm_exercise, bcm_governance |

## Архитектурные паттерны

### 1. Наследование от bcm_core:
Все модули наследуют базовые модели от bcm_core для единообразия

### 2. Мульти-тенантность:
Каждый модуль поддерживает изоляцию данных через bcm_clients

### 3. AI-интеграция:
Большинство модулей интегрируется с bcm_intelligent_base для AI-анализа

### 4. Event-driven архитектура:
Модули взаимодействуют через события и webhook'и

### 5. API-first подход:
Каждый модуль предоставляет REST API для интеграций