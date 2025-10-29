# 📊 BCM Portal - Группировка страниц и компонентов
*Детальная структура страниц портала с группировкой функций*

---

## 🎯 Принципы группировки страниц

### **Логика объединения функций на одной странице:**
1. **Связанные данные** - функции, работающие с одним типом данных
2. **Общий workflow** - этапы одного бизнес-процесса
3. **Одинаковая частота использования** - функции, используемые в одно время
4. **Схожая аудитория** - функции для одной роли или команды
5. **Контекстная связанность** - функции, дополняющие друг друга

---

## 📱 **СТРАНИЦА 1: Main Dashboard**
*Центральная точка входа для всех ролей*

```mermaid
graph TB
    subgraph "📊 Main Dashboard Page"

        subgraph "🎯 Role-Based Header"
            ROLE_SELECTOR[Role Selector<br/>👤 Переключение ролей]
            USER_PROFILE[User Profile<br/>⚙️ Профиль и настройки]
            NOTIFICATIONS[Notification Center<br/>🔔 Центр уведомлений]
            QUICK_ACTIONS[Quick Actions<br/>⚡ Быстрые действия]
        end

        subgraph "📈 Main Content Area"
            KPI_OVERVIEW[KPI Overview<br/>📊 Ключевые метрики]
            STATUS_CARDS[Status Cards<br/>🃏 Статусные карточки]
            ACTIVITY_FEED[Activity Feed<br/>📰 Лента активности]
            PRIORITY_ALERTS[Priority Alerts<br/>🚨 Приоритетные алерты]
        end

        subgraph "🔧 Side Panel"
            CURRENT_INCIDENTS[Current Incidents<br/>⚡ Текущие инциденты]
            UPCOMING_TASKS[Upcoming Tasks<br/>📅 Предстоящие задачи]
            TEAM_STATUS[Team Status<br/>👥 Статус команды]
            WEATHER_WIDGET[Business Weather<br/>🌤️ Бизнес-погода]
        end

        subgraph "📊 Bottom Widgets Bar"
            RISK_SUMMARY[Risk Summary<br/>⚠️ Сводка по рискам]
            COMPLIANCE_BAR[Compliance Bar<br/>✅ Индикатор соответствия]
            EXERCISE_COUNTDOWN[Exercise Countdown<br/>⏱️ До следующего учения]
            BUDGET_INDICATOR[Budget Indicator<br/>💰 Индикатор бюджета]
        end
    end
```

**На одной странице потому что:**
- Все пользователи начинают работу отсюда
- Нужен общий обзор состояния системы
- Быстрый доступ к критической информации
- Персонализация по ролям через виджеты

---

## 🔍 **СТРАНИЦА 2: Risk & Analysis Hub**
*Комплексный анализ рисков и воздействия*

```mermaid
graph TB
    subgraph "🔍 Risk & Analysis Hub Page"

        subgraph "🎯 Analysis Control Panel"
            ANALYSIS_MODE[Analysis Mode<br/>🎭 Режим анализа]
            AI_ASSISTANT[AI Risk Assistant<br/>🤖 AI помощник]
            FILTER_PANEL[Advanced Filters<br/>🔍 Расширенные фильтры]
            EXPORT_TOOLS[Export Tools<br/>📤 Инструменты экспорта]
        end

        subgraph "📊 Main Analysis Area - Left Column"
            RISK_HEATMAP[Risk Heat Map<br/>🔥 Интерактивная тепловая карта]
            BIA_PROCESS_MAP[BIA Process Map<br/>⚙️ Карта процессов BIA]
            DEPENDENCY_GRAPH[Dependency Graph<br/>🕸️ Граф зависимостей]
        end

        subgraph "📈 Analysis Details - Right Column"
            RISK_DETAILS[Risk Details Panel<br/>📋 Детали выбранного риска]
            IMPACT_CALCULATOR[Impact Calculator<br/>🧮 Калькулятор воздействия]
            AI_RECOMMENDATIONS[AI Recommendations<br/>💡 AI рекомендации]
            SCENARIO_MODELING[Scenario Modeling<br/>🎬 Моделирование сценариев]
        end

        subgraph "🔗 Integration Panel"
            THREAT_INTEL_FEED[Threat Intel Feed<br/>🛡️ Лента разведданных]
            INDUSTRY_BENCHMARKS[Industry Benchmarks<br/>🏭 Отраслевые сравнения]
            REGULATORY_UPDATES[Regulatory Updates<br/>📋 Обновления требований]
        end
    end
```

**На одной странице потому что:**
- Risk и BIA анализы взаимосвязаны
- Общие данные о процессах и зависимостях
- Единый workflow анализа "от риска к воздействию"
- AI помощник работает с обоими типами анализа

---

## 🚨 **СТРАНИЦА 3: Crisis Command Center**
*Управление кризисными ситуациями и инцидентами*

```mermaid
graph TB
    subgraph "🚨 Crisis Command Center Page"

        subgraph "🎯 Crisis Status Bar"
            CRISIS_LEVEL[Crisis Level Indicator<br/>🔴 Уровень кризиса]
            ACTIVE_INCIDENTS[Active Incidents Counter<br/>⚡ Счетчик инцидентов]
            RESPONSE_TIME[Response Time<br/>⏱️ Время реагирования]
            ESCALATION_STATUS[Escalation Status<br/>🔺 Статус эскалации]
        end

        subgraph "🗺️ Situation Map - Main Area"
            INCIDENT_MAP[Incident Situation Map<br/>🗺️ Карта ситуации]
            TIMELINE_VIEW[Crisis Timeline<br/>📅 Временная линия кризиса]
            STATUS_BOARD[Digital Status Board<br/>📊 Цифровая статусная доска]
        end

        subgraph "👥 Team Coordination - Left Panel"
            RESPONSE_TEAMS[Response Teams<br/>👨‍🚒 Команды реагирования]
            TEAM_COMMUNICATIONS[Team Communications<br/>💬 Коммуникации команд]
            RESOURCE_STATUS[Resource Status<br/>🎯 Статус ресурсов]
            EXTERNAL_CONTACTS[External Contacts<br/>📞 Внешние контакты]
        end

        subgraph "⚡ Action Center - Right Panel"
            CRITICAL_DECISIONS[Critical Decisions<br/>⚖️ Критические решения]
            QUICK_ACTIONS[Crisis Quick Actions<br/>🚀 Быстрые действия]
            COMMUNICATION_TEMPLATES[Communication Templates<br/>📝 Шаблоны коммуникаций]
            RECOVERY_CHECKLIST[Recovery Checklist<br/>✅ Чек-лист восстановления]
        end

        subgraph "📊 Crisis Analytics"
            IMPACT_ASSESSMENT[Real-time Impact<br/>💥 Воздействие в реальном времени]
            RECOVERY_PROGRESS[Recovery Progress<br/>📈 Прогресс восстановления]
            STAKEHOLDER_UPDATES[Stakeholder Updates<br/>👥 Обновления для заинтересованных лиц]
        end
    end
```

**На одной странице потому что:**
- Кризисное управление требует единого центра координации
- Все критические функции должны быть доступны одновременно
- Real-time collaboration между всеми участниками
- Минимизация переходов между экранами в критической ситуации

---

## 📋 **СТРАНИЦА 4: Plans & Procedures Workspace**
*Управление планами непрерывности и процедурами*

```mermaid
graph TB
    subgraph "📋 Plans & Procedures Workspace Page"

        subgraph "📚 Plan Library - Left Panel"
            PLAN_CATEGORIES[Plan Categories<br/>📂 Категории планов]
            PLAN_SEARCH[Plan Search<br/>🔍 Поиск планов]
            RECENT_PLANS[Recently Accessed<br/>🕐 Недавно открытые]
            FAVORITES[Favorite Plans<br/>⭐ Избранные планы]
        end

        subgraph "📝 Plan Editor - Main Area"
            PLAN_HEADER[Plan Header<br/>📄 Заголовок плана]
            PLAN_CONTENT[Plan Content Editor<br/>✏️ Редактор содержимого]
            PROCEDURE_STEPS[Procedure Steps<br/>👣 Шаги процедуры]
            ATTACHMENTS[Plan Attachments<br/>📎 Вложения плана]
        end

        subgraph "🔧 Plan Tools - Right Panel"
            VERSION_CONTROL[Version Control<br/>🔄 Контроль версий]
            APPROVAL_WORKFLOW[Approval Workflow<br/>✅ Workflow утверждения]
            PLAN_TESTING[Plan Testing<br/>🧪 Тестирование плана]
            INTEGRATION_LINKS[Integration Links<br/>🔗 Интеграционные связи]
        end

        subgraph "📊 Plan Analytics - Bottom Bar"
            USAGE_STATISTICS[Usage Statistics<br/>📈 Статистика использования]
            EFFECTIVENESS_METRICS[Effectiveness Metrics<br/>🎯 Метрики эффективности]
            COMPLIANCE_STATUS[Compliance Status<br/>✅ Статус соответствия]
            REVIEW_SCHEDULE[Review Schedule<br/>📅 График пересмотра]
        end
    end
```

**На одной странице потому что:**
- Plans и procedures тесно связаны
- Единый workflow создания/редактирования/утверждения
- Нужен доступ к библиотеке и инструментам одновременно
- Версионирование и тестирование - часть одного процесса

---

## 🎓 **СТРАНИЦА 5: Training & Exercise Hub**
*Обучение, учения и развитие компетенций*

```mermaid
graph TB
    subgraph "🎓 Training & Exercise Hub Page"

        subgraph "📅 Schedule Manager - Top Bar"
            CALENDAR_VIEW[Calendar View<br/>📅 Календарный вид]
            UPCOMING_EVENTS[Upcoming Events<br/>⏰ Предстоящие события]
            MY_ASSIGNMENTS[My Assignments<br/>👤 Мои назначения]
            DEADLINES[Training Deadlines<br/>⚠️ Сроки обучения]
        end

        subgraph "🎯 Exercise Center - Left Column"
            EXERCISE_LIBRARY[Exercise Library<br/>📚 Библиотека учений]
            EXERCISE_BUILDER[Exercise Builder<br/>🏗️ Конструктор учений]
            SIMULATION_TOOLS[Simulation Tools<br/>🎮 Инструменты симуляции]
            RESULTS_ANALYSIS[Results Analysis<br/>📊 Анализ результатов]
        end

        subgraph "📚 Learning Center - Right Column"
            COURSE_CATALOG[Course Catalog<br/>📖 Каталог курсов]
            LEARNING_PATHS[Learning Paths<br/>🛤️ Траектории обучения]
            AI_TUTOR[AI Learning Coach<br/>🤖 AI тренер]
            COMPETENCY_TRACKER[Competency Tracker<br/>📈 Трекер компетенций]
        end

        subgraph "👥 Collaboration Area - Center"
            TEAM_EXERCISES[Team Exercises<br/>👨‍👨‍👧‍👦 Командные учения]
            PEER_LEARNING[Peer Learning<br/>🤝 Взаимное обучение]
            DISCUSSION_FORUMS[Discussion Forums<br/>💬 Форумы обсуждений]
            KNOWLEDGE_SHARING[Knowledge Sharing<br/>🧠 Обмен знаниями]
        end

        subgraph "📊 Progress Dashboard - Bottom"
            INDIVIDUAL_PROGRESS[Individual Progress<br/>👤 Индивидуальный прогресс]
            TEAM_PERFORMANCE[Team Performance<br/>👥 Производительность команды]
            CERTIFICATION_STATUS[Certification Status<br/>🏆 Статус сертификации]
            IMPROVEMENT_RECOMMENDATIONS[Improvement Recommendations<br/>💡 Рекомендации по улучшению]
        end
    end
```

**На одной странице потому что:**
- Training и exercises - единый цикл развития компетенций
- Календарь нужен и для обучения, и для учений
- AI coach работает с обеими активностями
- Результаты учений влияют на потребности в обучении

---

## 📊 **СТРАНИЦА 6: Analytics & Reporting Suite**
*Аналитика, отчетность и бизнес-аналитика*

```mermaid
graph TB
    subgraph "📊 Analytics & Reporting Suite Page"

        subgraph "🎛️ Report Control Panel - Top"
            REPORT_BUILDER[Report Builder<br/>🏗️ Конструктор отчетов]
            TEMPLATE_LIBRARY[Template Library<br/>📚 Библиотека шаблонов]
            SCHEDULE_MANAGER[Schedule Manager<br/>⏰ Менеджер расписания]
            DISTRIBUTION_LIST[Distribution Lists<br/>📮 Списки рассылки]
        end

        subgraph "📈 Visual Analytics - Left Side"
            INTERACTIVE_DASHBOARDS[Interactive Dashboards<br/>📊 Интерактивные дашборды]
            KPI_SCORECARDS[KPI Scorecards<br/>🎯 KPI карточки]
            TREND_ANALYSIS[Trend Analysis<br/>📈 Анализ трендов]
            BENCHMARKING[Benchmarking<br/>🏆 Бенчмаркинг]
        end

        subgraph "📋 Report Generation - Center"
            EXECUTIVE_REPORTS[Executive Reports<br/>👔 Отчеты руководству]
            COMPLIANCE_REPORTS[Compliance Reports<br/>✅ Отчеты соответствия]
            OPERATIONAL_REPORTS[Operational Reports<br/>⚙️ Операционные отчеты]
            CUSTOM_REPORTS[Custom Reports<br/>🎨 Кастомные отчеты]
        end

        subgraph "🤖 AI Analytics - Right Side"
            PREDICTIVE_ANALYTICS[Predictive Analytics<br/>🔮 Предиктивная аналитика]
            ANOMALY_DETECTION[Anomaly Detection<br/>🚨 Обнаружение аномалий]
            INSIGHTS_GENERATOR[Insights Generator<br/>💡 Генератор инсайтов]
            RECOMMENDATION_ENGINE[Recommendation Engine<br/>🎯 Движок рекомендаций]
        end

        subgraph "📊 Data Integration - Bottom"
            DATA_SOURCES[Data Sources<br/>🗄️ Источники данных]
            DATA_QUALITY[Data Quality<br/>✨ Качество данных]
            EXPORT_OPTIONS[Export Options<br/>📤 Опции экспорта]
            API_CONNECTORS[API Connectors<br/>🔗 API коннекторы]
        end
    end
```

**На одной странице потому что:**
- Analytics и reporting - единый workflow от данных к инсайтам
- Визуализация и генерация отчетов используют одни данные
- AI analytics дополняет традиционную отчетность
- Нужен единый контроль качества данных и экспорта

---

## 👥 **СТРАНИЦА 7: Collaboration & Knowledge Portal**
*Сотрудничество, база знаний и сообщество*

```mermaid
graph TB
    subgraph "👥 Collaboration & Knowledge Portal Page"

        subgraph "🔍 Knowledge Discovery - Top Bar"
            GLOBAL_SEARCH[Global Search<br/>🔍 Глобальный поиск]
            SMART_TAGS[Smart Tags<br/>🏷️ Умные теги]
            CONTENT_FILTERS[Content Filters<br/>🔽 Фильтры контента]
            RECENT_ACTIVITY[Recent Activity<br/>🕐 Недавняя активность]
        end

        subgraph "📚 Knowledge Base - Left Column"
            DOCUMENT_LIBRARY[Document Library<br/>📄 Библиотека документов]
            BEST_PRACTICES[Best Practices<br/>⭐ Лучшие практики]
            LESSONS_LEARNED[Lessons Learned<br/>🎓 Извлеченные уроки]
            POLICY_LIBRARY[Policy Library<br/>📋 Библиотека политик]
        end

        subgraph "💬 Community Hub - Center"
            DISCUSSION_FORUMS[Discussion Forums<br/>💬 Форумы обсуждений]
            EXPERT_NETWORK[Expert Network<br/>🎯 Сеть экспертов]
            Q_AND_A[Q&A Section<br/>❓ Раздел вопросов и ответов]
            COMMUNITY_GROUPS[Community Groups<br/>👥 Группы сообщества]
        end

        subgraph "🤝 Collaboration Tools - Right Column"
            PROJECT_WORKSPACES[Project Workspaces<br/>🏗️ Проектные рабочие области]
            SHARED_CALENDARS[Shared Calendars<br/>📅 Общие календари]
            FILE_SHARING[File Sharing<br/>📁 Обмен файлами]
            VIDEO_CONFERENCING[Video Conferencing<br/>📹 Видеоконференции]
        end

        subgraph "🧠 AI Knowledge Assistant - Bottom"
            AI_CHATBOT[AI Knowledge Chatbot<br/>🤖 AI чат-бот знаний]
            CONTENT_RECOMMENDATIONS[Content Recommendations<br/>💡 Рекомендации контента]
            AUTO_CATEGORIZATION[Auto Categorization<br/>🏷️ Авто-категоризация]
            SMART_SUMMARIZATION[Smart Summarization<br/>📝 Умное резюмирование]
        end
    end
```

**На одной странице потому что:**
- Knowledge sharing и collaboration - взаимосвязанные процессы
- Поиск работает по всем типам контента
- Community discussions дополняют knowledge base
- AI assistant помогает с поиском и рекомендациями по всему контенту

---

## ⚙️ **СТРАНИЦА 8: System Administration Center**
*Администрирование системы и управление конфигурацией*

```mermaid
graph TB
    subgraph "⚙️ System Administration Center Page"

        subgraph "🎛️ Admin Control Panel - Top"
            SYSTEM_STATUS[System Status<br/>🚦 Статус системы]
            MAINTENANCE_MODE[Maintenance Mode<br/>🔧 Режим обслуживания]
            BACKUP_STATUS[Backup Status<br/>💾 Статус резервирования]
            SECURITY_ALERTS[Security Alerts<br/>🔒 Алерты безопасности]
        end

        subgraph "👥 User Management - Left Column"
            USER_DIRECTORY[User Directory<br/>👤 Каталог пользователей]
            ROLE_MANAGEMENT[Role Management<br/>🎭 Управление ролями]
            ACCESS_CONTROL[Access Control<br/>🔐 Контроль доступа]
            AUDIT_LOGS[Audit Logs<br/>📝 Журналы аудита]
        end

        subgraph "🏢 Organization Config - Center"
            TENANT_MANAGEMENT[Tenant Management<br/>🏢 Управление арендаторами]
            ORG_STRUCTURE[Organization Structure<br/>🏗️ Структура организации]
            WORKFLOW_CONFIG[Workflow Configuration<br/>🔄 Конфигурация workflow]
            INTEGRATION_SETTINGS[Integration Settings<br/>🔗 Настройки интеграций]
        end

        subgraph "🔧 System Config - Right Column"
            GLOBAL_SETTINGS[Global Settings<br/>🌍 Глобальные настройки]
            MODULE_MANAGEMENT[Module Management<br/>📦 Управление модулями]
            API_MANAGEMENT[API Management<br/>🔌 Управление API]
            PERFORMANCE_MONITORING[Performance Monitoring<br/>📊 Мониторинг производительности]
        end

        subgraph "📊 Admin Analytics - Bottom"
            USAGE_ANALYTICS[Usage Analytics<br/>📈 Аналитика использования]
            RESOURCE_UTILIZATION[Resource Utilization<br/>💻 Использование ресурсов]
            ERROR_TRACKING[Error Tracking<br/>🐛 Отслеживание ошибок]
            CAPACITY_PLANNING[Capacity Planning<br/>📊 Планирование мощностей]
        end
    end
```

**На одной странице потому что:**
- Все административные функции требуют высоких привилегий
- System monitoring и configuration взаимосвязаны
- User management и security settings работают вместе
- Admin analytics нужна для всех административных решений

---

## 📱 **МОБИЛЬНЫЕ СТРАНИЦЫ**

### 📱 **Mobile Page 1: Emergency Dashboard**
```mermaid
graph TB
    subgraph "📱 Emergency Mobile Dashboard"
        CRISIS_STATUS[Crisis Status<br/>🔴 Статус кризиса]
        QUICK_ACTIONS[Quick Actions<br/>⚡ Быстрые действия]
        EMERGENCY_CONTACTS[Emergency Contacts<br/>📞 Экстренные контакты]
        MY_TASKS[My Crisis Tasks<br/>✅ Мои задачи в кризисе]
        TEAM_CHAT[Team Chat<br/>💬 Командный чат]
    end
```

### 📱 **Mobile Page 2: Daily BCM Companion**
```mermaid
graph TB
    subgraph "📱 Daily BCM Mobile Companion"
        TODAY_TASKS[Today's Tasks<br/>📅 Задачи на сегодня]
        NOTIFICATIONS[Notifications<br/>🔔 Уведомления]
        QUICK_REPORTS[Quick Reports<br/>📊 Быстрые отчеты]
        DOCUMENT_SCANNER[Document Scanner<br/>📷 Сканер документов]
        OFFLINE_ACCESS[Offline Access<br/>📱 Оффлайн доступ]
    end
```

---

## 🔄 **Логика навигации между страницами**

```mermaid
graph LR
    MAIN[Main Dashboard<br/>📊 Главный дашборд]
    RISK[Risk & Analysis<br/>🔍 Риски и анализ]
    CRISIS[Crisis Command<br/>🚨 Кризисное управление]
    PLANS[Plans & Procedures<br/>📋 Планы и процедуры]
    TRAINING[Training & Exercise<br/>🎓 Обучение и учения]
    ANALYTICS[Analytics & Reports<br/>📊 Аналитика и отчеты]
    KNOWLEDGE[Knowledge Portal<br/>👥 Портал знаний]
    ADMIN[System Admin<br/>⚙️ Администрирование]

    MAIN --> RISK
    MAIN --> CRISIS
    MAIN --> PLANS
    MAIN --> TRAINING

    RISK --> PLANS
    CRISIS --> PLANS
    PLANS --> TRAINING

    ANALYTICS --> MAIN
    KNOWLEDGE --> TRAINING
    ADMIN --> MAIN

    %% Bidirectional flows
    RISK <--> CRISIS
    TRAINING <--> KNOWLEDGE
    ANALYTICS <--> RISK
```

---

## 🎯 **Преимущества такой группировки:**

### ✅ **Снижение когнитивной нагрузки**
- Связанные функции на одной странице
- Минимум переходов между экранами
- Контекстная группировка информации

### ✅ **Повышение эффективности**
- Быстрый доступ к связанным данным
- Унифицированные инструменты для схожих задач
- Оптимизированные workflow

### ✅ **Улучшение пользовательского опыта**
- Интуитивная логика группировки
- Персонализация по ролям
- Адаптивный интерфейс

### ✅ **Техническая оптимизация**
- Меньше API вызовов
- Общие компоненты и данные
- Лучшая производительность

**Такая структура обеспечивает оптимальный баланс между функциональностью и простотой использования!** 🚀