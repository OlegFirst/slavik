# Digital Twin System v3.0 - System Flow Diagrams and Architecture
## Enhanced with AnyLogic Pypeline Integration

## 1. Основной поток данных системы

```mermaid
graph TB
    subgraph "Источники данных"
        ORG[NPO Организация]
        API[Внешние API]
        USER[Пользователи]
    end
    
    subgraph "Слой приема данных"
        COLL[Organization Data Collector]
        AUTH[Auth Manager]
        VAL[Validators]
    end
    
    subgraph "Обработка и хранение"
        DB[(Supabase PostgreSQL)]
        CACHE[Cache Layer]
        QUEUE[Task Queue]
    end
    
    subgraph "Digital Twin Core v3.0"
        DT[Digital Twin Engine]
        SIM[Enhanced Simulation Engine]
        PRED[ML-Enhanced Prediction Module]
        METRIC[Metrics Calculator]
        HYBRID[AnyLogic Hybrid Engine]
        ML[ML/AI Pipeline]
    end
    
    subgraph "Визуализация и вывод"
        WEB[Web Interface]
        VIS[3D Visualization]
        REP[Reports Generator]
        DASH[Dashboard]
    end
    
    ORG --> COLL
    API --> COLL
    USER --> AUTH
    
    COLL --> VAL
    AUTH --> VAL
    VAL --> DB
    
    DB --> CACHE
    CACHE --> DT
    
    DT --> SIM
    DT --> PRED
    DT --> METRIC
    DT --> HYBRID
    HYBRID --> ML
    ML --> PRED
    
    SIM --> QUEUE
    PRED --> QUEUE
    METRIC --> DB
    
    DB --> WEB
    WEB --> VIS
    WEB --> DASH
    METRIC --> REP
```

## 2. Процесс создания Digital Twin

```mermaid
sequenceDiagram
    participant U as User
    participant API as API Server
    participant Auth as Auth Service
    participant Val as Validator
    participant DB as Database
    participant DT as Digital Twin Engine
    participant Sim as Enhanced Simulation Engine
    participant AL as AnyLogic Pypeline
    participant ML as ML Pipeline
    
    U->>API: POST /api/organizations
    API->>Auth: Verify credentials
    Auth-->>API: Token validated
    API->>Val: Validate organization data
    Val-->>API: Data valid
    API->>DB: Insert organization_profile
    DB-->>API: Organization created
    
    API->>DT: Initialize Digital Twin
    DT->>DB: Create digital_twin record
    DT->>Sim: Initialize 30 experiments
    DT->>AL: Setup AnyLogic Pypeline
    AL->>ML: Initialize ML models
    Sim->>DB: Store configuration
    AL->>DB: Store hybrid model config
    
    DT-->>API: Twin created
    API-->>U: Return twin_id and status
```

## 3. Процесс симуляции

```mermaid
flowchart LR
    START([Запуск симуляции])
    LOAD[Загрузка данных организации]
    SELECT[Выбор сценария]
    PARAMS[Установка параметров]
    
    subgraph "Enhanced Simulation Engine v3.0"
        INIT[Initialization - 30 Experiments]
        ROUTE[Routing to Adapters]
        CALC[Calculations]
        HYBRID_SIM[AnyLogic Hybrid Simulation]
        ML_PRED[ML-Enhanced Predictions]
        OPT[Optimization]
    end
    
    SAVE[Сохранение результатов]
    VIS[Визуализация]
    END([Готовый отчет])
    
    START --> LOAD
    LOAD --> SELECT
    SELECT --> PARAMS
    PARAMS --> INIT
    INIT --> ROUTE
    ROUTE --> CALC
    ROUTE --> HYBRID_SIM
    CALC --> ML_PRED
    HYBRID_SIM --> ML_PRED
    ML_PRED --> OPT
    OPT --> SAVE
    SAVE --> VIS
    VIS --> END
```

## 4. Архитектура компонентов

```mermaid
graph TD
    subgraph "Frontend Layer"
        UI[User Interface]
        CHART[Chart.js]
        D3[D3.js]
        VIS_NET[Vis-network]
    end
    
    subgraph "API Gateway"
        REST[REST API]
        WS[WebSocket]
        MCP[MCP Protocol]
    end
    
    subgraph "Enhanced Business Logic v3.0"
        TWIN[Digital Twin Core]
        SIM_ENG[30-Experiment Simulation Engine]
        ANALYTICS[Enhanced Analytics Module]
        ML_CORE[ML/AI Core]
        ANYLOGIC[AnyLogic Pypeline]
        HYBRID[Hybrid Simulation Controller]
    end
    
    subgraph "Data Layer"
        SUPA[Supabase Client]
        REDIS[Redis Cache]
        S3[File Storage]
    end
    
    subgraph "External Services"
        AI[AI Agents]
        THIRD[3rd Party APIs]
        NOTIF[Notifications]
    end
    
    UI --> REST
    UI --> WS
    CHART --> UI
    D3 --> UI
    VIS_NET --> UI
    
    REST --> TWIN
    WS --> TWIN
    MCP --> AI
    
    TWIN --> SIM_ENG
    TWIN --> ANALYTICS
    TWIN --> ANYLOGIC
    SIM_ENG --> HYBRID
    ANYLOGIC --> ML_CORE
    ANALYTICS --> ML_CORE
    HYBRID --> ML_CORE
    
    TWIN --> SUPA
    TWIN --> REDIS
    ML --> SUPA
    
    AI --> MCP
    THIRD --> REST
    TWIN --> NOTIF
```

## 5. Поток метрик и аналитики

```mermaid
stateDiagram-v2
    [*] --> DataCollection: Сбор данных
    DataCollection --> Validation: Валидация
    Validation --> Processing: Обработка
    
    Processing --> HealthMetrics: Расчет здоровья
    Processing --> FinancialMetrics: Финансовые метрики
    Processing --> OperationalMetrics: Операционные метрики
    Processing --> TechnologyMetrics: Технологические метрики
    
    HealthMetrics --> Aggregation: Агрегация
    FinancialMetrics --> Aggregation
    OperationalMetrics --> Aggregation
    TechnologyMetrics --> Aggregation
    
    Aggregation --> Storage: Сохранение в БД
    Storage --> Visualization: Визуализация
    Storage --> Reporting: Отчетность
    
    Visualization --> Dashboard: Дашборд
    Reporting --> PDFReport: PDF отчет
    Reporting --> ExcelExport: Excel экспорт
    
    Dashboard --> [*]
    PDFReport --> [*]
    ExcelExport --> [*]
```

## 6. Жизненный цикл Digital Twin

```mermaid
journey
    title Жизненный цикл Digital Twin организации
    
    section Инициализация
      Регистрация организации: 5: User
      Сбор первичных данных: 4: System
      Создание профиля: 5: System
      
    section Настройка
      Конфигурация параметров: 4: User
      Выбор модулей: 4: User
      Установка KPI: 3: User
      
    section Активная работа
      Ежедневный мониторинг: 5: System
      Запуск симуляций: 5: User
      Анализ метрик: 5: System
      Генерация прогнозов: 4: System
      
    section Оптимизация
      Выявление проблем: 5: System
      Рекомендации: 4: System
      Применение изменений: 3: User
      Измерение эффекта: 5: System
      
    section Масштабирование
      Добавление отделов: 4: User
      Интеграция систем: 3: System
      Расширение метрик: 4: System
```

## 7. Интеграционная схема

```mermaid
graph LR
    subgraph "Digital Twin Platform"
        CORE[Core System]
        API_GW[API Gateway]
        AUTH[Auth Service]
    end
    
    subgraph "External Systems"
        CRM[CRM Systems]
        ERP[ERP Systems]
        FIN[Financial Systems]
        HR[HR Systems]
    end
    
    subgraph "External Simulation Adapters"
        SIMPY[SimPy Adapter - Port 7001]
        MESA[Mesa ABM - Port 7002]
        EPINOW[EpiNow2 - Port 7003]
        ANYLOGIC_EXT[AnyLogic Pypeline - Port 7004]
    end
    
    subgraph "AI Services"
        CLAUDE[Claude AI]
        GPT[GPT Models]
        CUSTOM[Custom Models]
    end
    
    subgraph "Инфраструктура"
        SUPA[Supabase]
        AWS[AWS Services]
        MONITOR[Monitoring]
    end
    
    CRM --> API_GW
    ERP --> API_GW
    FIN --> API_GW
    HR --> API_GW
    
    API_GW --> AUTH
    AUTH --> CORE
    
    CORE <--> SUPA
    CORE <--> AWS
    CORE --> MONITOR
    
    CORE <--> CLAUDE
    CORE <--> GPT
    CORE <--> CUSTOM
    CORE <--> SIMPY
    CORE <--> MESA
    CORE <--> EPINOW
    CORE <--> ANYLOGIC_EXT
```

## 8. Безопасность и права доступа

```mermaid
flowchart TD
    USER[User Request]
    
    subgraph "Security Layers"
        CORS[CORS Check]
        RATE[Rate Limiting]
        AUTH[Authentication]
        AUTHZ[Authorization]
        VAL[Input Validation]
        SANIT[Sanitization]
    end
    
    subgraph "Access Control"
        ADMIN[Admin Role]
        MANAGER[Manager Role]
        ANALYST[Analyst Role]
        VIEWER[Viewer Role]
    end
    
    subgraph "Resources"
        CREATE[Create Operations]
        READ[Read Operations]
        UPDATE[Update Operations]
        DELETE[Delete Operations]
    end
    
    USER --> CORS
    CORS --> RATE
    RATE --> AUTH
    AUTH --> AUTHZ
    AUTHZ --> VAL
    VAL --> SANIT
    
    AUTHZ --> ADMIN
    AUTHZ --> MANAGER
    AUTHZ --> ANALYST
    AUTHZ --> VIEWER
    
    ADMIN --> CREATE
    ADMIN --> READ
    ADMIN --> UPDATE
    ADMIN --> DELETE
    
    MANAGER --> CREATE
    MANAGER --> READ
    MANAGER --> UPDATE
    
    ANALYST --> READ
    ANALYST --> UPDATE
    
    VIEWER --> READ
```

## Описание потоков

### 1. **Enhanced Data Flow v3.0**
- Data flows from organizations, external APIs, and users
- Validation and authentication processing
- Storage in Supabase PostgreSQL with ML model persistence
- Processing through enhanced Digital Twin engine with 30 experiments
- AnyLogic Pypeline integration for hybrid simulation
- ML/AI enhancement through TensorFlow/PyTorch pipeline
- Advanced visualization in web interface with 3D capabilities

### 2. **Enhanced Digital Twin Creation**
- User registers NPO organization
- System validates data with ML assistance
- Profile created in database with ML model preparation
- Digital twin initialized with 30 experiment capabilities
- AnyLogic Pypeline configured for hybrid simulation
- ML models trained on organization-specific data
- All simulation scenarios configured and validated

### 3. **Enhanced Simulation Process**
- Organization data loaded with ML feature engineering
- Selection from 30 available experiments across 4 categories
- Intelligent routing to appropriate simulation engine
- AnyLogic hybrid simulation with multi-paradigm modeling
- ML-enhanced predictions and optimization
- Advanced result generation with confidence scoring
- Results stored with ML model updates and visualized in 3D

### 4. **ML-Enhanced Metrics and Analytics**
- Continuous data collection with ML pattern recognition
- Calculation of 4 metric categories enhanced by AI predictions
- Advanced aggregation with statistical learning
- Real-time visualization with predictive insights
- Automated report generation with ML-driven recommendations
- Continuous model improvement through feedback loops

---
*Диаграммы созданы с использованием Mermaid синтаксиса и могут быть отрендерены в любом Markdown viewer с поддержкой Mermaid*