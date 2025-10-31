# Анализ интеграции SEH и Digital Twin архитектур

## Сравнительный анализ архитектур

### SEH (Social & Economic Hub) - Ключевые компоненты:

1. **Каноническая модель данных (CDM)**
   - Community, Program, Service, ServiceDelivery, Outcome, Indicator, Measurement
   - FundingProgram, GrantAward, Disbursement
   - BCMScenario (Business Continuity Management)
   - PoIClaim/PoIVerification (Proof of Impact)

2. **Слойная архитектура**
   - Источники данных → Consent & IAM → Data Lake → Salesforce → Dashboards
   - Analytics & ML → AnyLogic симуляции
   - Public/Open API для исследователей

3. **Стандарты**
   - ISO/IEC 38505, ISO/IEC 27001, ISO 8000
   - GDPR, FAIR/CARE принципы
   - ISO 22301/22313/22317 (BCM)
   - DTDL, OpenUSD, OPC UA для интероперабельности

### Digital Twin (текущая реализация) - Что есть:

1. **Модель данных**
   - organization_profiles (вместо Community)
   - digital_twins (базовая модель)
   - simulations (6 сценариев)
   - metrics, predictions, reports

2. **Архитектура**
   - Supabase PostgreSQL
   - REST API на Express
   - Базовая визуализация (Chart.js, D3.js, Vis-network)
   - MCP протокол для AI агентов

3. **Возможности**
   - Базовые симуляции (budget_optimization, crisis_management)
   - Простые метрики здоровья организации
   - JWT аутентификация (частично)

## Таблица соответствия компонентов

| SEH Component | Digital Twin Equivalent | Готовность | Что нужно добавить |
|--------------|------------------------|------------|-------------------|
| **Community** | organization_profiles | ✅ 80% | Добавить vulnerability_tags, consent management |
| **Program** | - | ❌ 0% | Создать таблицу programs с domain, geography |
| **Service** | - | ❌ 0% | Создать модель услуг с unit, delivery_mode |
| **ServiceDelivery** | - | ❌ 0% | Критично для отслеживания оказанных услуг |
| **Participant** | - | ❌ 0% | Нужна модель получателей услуг |
| **Outcome** | simulations (частично) | ⚠️ 30% | Нужна полная модель результатов |
| **Indicator** | metrics (базово) | ⚠️ 40% | Расширить с targets, disaggregation |
| **Measurement** | metrics | ⚠️ 50% | Добавить confidence, evidence_ref |
| **Evidence** | - | ❌ 0% | Критично для верификации |
| **FundingProgram** | - | ❌ 0% | Нужна модель грантов |
| **GrantAward** | annual_budget (примитивно) | ⚠️ 10% | Полная модель грантового финансирования |
| **BCMScenario** | crisis_management (базово) | ⚠️ 20% | Добавить RTO/RPO, dependencies |
| **PoIClaim** | - | ❌ 0% | Blockchain/ledger верификация |
| **Consent & IAM** | JWT auth (частично) | ⚠️ 30% | GDPR-compliant consent management |
| **Data Lake** | Supabase | ⚠️ 40% | Нужен staging layer, CDC |
| **Salesforce Integration** | - | ❌ 0% | Критично для enterprise |
| **AnyLogic Integration** | simulation-engine.js | ⚠️ 15% | Нужна полная интеграция |
| **IoT/Sensors** | - | ❌ 0% | Edge computing, streaming |

## Готовность к SEH сценариям

### 1. Грантовое управление (Grant Management)
**Готовность: 10%**
- ❌ Нет модели FundingProgram
- ❌ Нет Application workflow
- ❌ Нет Disbursement tracking
- ❌ Нет ReportingRequirement
- ⚠️ Есть базовый budget в organization_profiles

### 2. Управление результатами (Outcome Management)
**Готовность: 25%**
- ⚠️ Есть базовые metrics
- ⚠️ Есть predictions
- ❌ Нет Outcome hierarchy (output/outcome/impact)
- ❌ Нет Evidence collection
- ❌ Нет Target vs Actual сравнения

### 3. Оказание услуг (Service Delivery)
**Готовность: 5%**
- ❌ Нет модели Services
- ❌ Нет Participants
- ❌ Нет ServiceDelivery tracking
- ❌ Нет геолокации и логистики
- ⚠️ Есть базовая структура организации

### 4. Business Continuity Management (BCM)
**Готовность: 20%**
- ⚠️ Есть crisis_management сценарий
- ❌ Нет RTO/RPO метрик
- ❌ Нет dependency mapping
- ❌ Нет BCMTest с evidence
- ❌ Нет automated failover

### 5. Proof of Impact (PoI)
**Готовность: 0%**
- ❌ Нет PoIClaim структуры
- ❌ Нет криптографических хешей
- ❌ Нет ledger интеграции
- ❌ Нет verification workflow
- ❌ Нет публичного API для верификации

### 6. IoT и реальное время
**Готовность: 5%**
- ❌ Нет Edge computing
- ❌ Нет streaming (Kafka/NATS)
- ❌ Нет sensor интеграции
- ⚠️ Есть базовый real-time через Supabase
- ❌ Нет offline-first архитектуры

## Критические пробелы для соответствия SEH

### КРИТИЧНО (блокеры):
1. **Модель данных Program/Service/ServiceDelivery** - без этого невозможно отслеживать услуги
2. **Evidence collection** - без доказательств нет верификации результатов
3. **Consent management** - GDPR требование
4. **Participant privacy** - псевдонимизация PII

### ВАЖНО (для production):
1. **Salesforce интеграция** - стандарт для NPO
2. **Grant management** - ключевой процесс финансирования
3. **BCM полный цикл** - для устойчивости
4. **Data Lake архитектура** - для масштабирования

### ЖЕЛАТЕЛЬНО (для полноты):
1. **AnyLogic API** - продвинутые симуляции
2. **IoT/Edge** - real-time данные
3. **Blockchain/Ledger** - неизменяемость доказательств
4. **Multi-tenant** - для консорциумов

## План интеграции (поэтапный)

### Фаза 1: Базовая совместимость (2 недели)
```sql
-- Новые таблицы
CREATE TABLE programs (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organization_profiles(id),
    name VARCHAR(255),
    domain VARCHAR(100), -- health, education, etc
    geography JSONB,
    start_at DATE,
    end_at DATE,
    status VARCHAR(50)
);

CREATE TABLE services (
    id UUID PRIMARY KEY,
    program_id UUID REFERENCES programs(id),
    name VARCHAR(255),
    unit VARCHAR(50), -- hour, session, meal
    delivery_mode VARCHAR(50), -- in-person, remote, hybrid
    capacity INTEGER,
    cost_per_unit DECIMAL
);

CREATE TABLE participants (
    id UUID PRIMARY KEY,
    identity_hash VARCHAR(255), -- псевдонимизация
    cohort VARCHAR(100),
    vulnerability_tags JSONB,
    consent_status VARCHAR(50),
    consent_date TIMESTAMP
);

CREATE TABLE service_deliveries (
    id UUID PRIMARY KEY,
    service_id UUID REFERENCES services(id),
    participant_id UUID REFERENCES participants(id),
    quantity DECIMAL,
    delivered_at TIMESTAMP,
    location_id UUID,
    provider_id UUID,
    evidence_urls JSONB
);

CREATE TABLE outcomes (
    id UUID PRIMARY KEY,
    program_id UUID REFERENCES programs(id),
    level VARCHAR(20), -- output, outcome, impact
    name VARCHAR(255),
    description TEXT,
    theory_of_change TEXT
);

CREATE TABLE indicators (
    id UUID PRIMARY KEY,
    outcome_id UUID REFERENCES outcomes(id),
    name VARCHAR(255),
    unit VARCHAR(50),
    direction VARCHAR(10), -- up, down
    frequency VARCHAR(20), -- daily, weekly, monthly
    disaggregation JSONB,
    data_source VARCHAR(255)
);

CREATE TABLE targets (
    id UUID PRIMARY KEY,
    indicator_id UUID REFERENCES indicators(id),
    period_start DATE,
    period_end DATE,
    value DECIMAL,
    geography VARCHAR(255),
    cohort VARCHAR(100)
);

CREATE TABLE measurements (
    id UUID PRIMARY KEY,
    indicator_id UUID REFERENCES indicators(id),
    period_start DATE,
    period_end DATE,
    value DECIMAL,
    confidence DECIMAL CHECK (confidence >= 0 AND confidence <= 1),
    evidence_ref VARCHAR(255),
    collected_at TIMESTAMP,
    collector_id UUID
);

CREATE TABLE evidence (
    id UUID PRIMARY KEY,
    ref_type VARCHAR(50), -- measurement, service_delivery, etc
    ref_id UUID,
    uri TEXT,
    media_hash VARCHAR(255),
    qa_status VARCHAR(50),
    created_at TIMESTAMP
);
```

### Фаза 2: Grant Management (1 неделя)
```sql
CREATE TABLE funding_programs (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    funder VARCHAR(255),
    total_budget DECIMAL,
    start_date DATE,
    end_date DATE,
    eligibility_criteria JSONB
);

CREATE TABLE grant_applications (
    id UUID PRIMARY KEY,
    funding_program_id UUID REFERENCES funding_programs(id),
    organization_id UUID REFERENCES organization_profiles(id),
    requested_amount DECIMAL,
    application_date DATE,
    status VARCHAR(50)
);

CREATE TABLE grant_awards (
    id UUID PRIMARY KEY,
    application_id UUID REFERENCES grant_applications(id),
    awarded_amount DECIMAL,
    award_date DATE,
    conditions JSONB
);

CREATE TABLE disbursements (
    id UUID PRIMARY KEY,
    grant_award_id UUID REFERENCES grant_awards(id),
    amount DECIMAL,
    disbursement_date DATE,
    tranche_number INTEGER
);
```

### Фаза 3: BCM Enhancement (1 неделя)
```sql
CREATE TABLE bcm_scenarios (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organization_profiles(id),
    scenario_type VARCHAR(100),
    rto_hours INTEGER, -- Recovery Time Objective
    rpo_hours INTEGER, -- Recovery Point Objective
    dependencies JSONB,
    impact_assessment JSONB
);

CREATE TABLE bcm_tests (
    id UUID PRIMARY KEY,
    scenario_id UUID REFERENCES bcm_scenarios(id),
    test_date TIMESTAMP,
    result VARCHAR(50),
    weaknesses JSONB,
    improvements JSONB,
    evidence_refs JSONB
);
```

### Фаза 4: Proof of Impact (2 недели)
```sql
CREATE TABLE poi_claims (
    id UUID PRIMARY KEY,
    indicator_id UUID REFERENCES indicators(id),
    claim_value DECIMAL,
    claim_date DATE,
    evidence_hash VARCHAR(255),
    status VARCHAR(50)
);

CREATE TABLE poi_verifications (
    id UUID PRIMARY KEY,
    claim_id UUID REFERENCES poi_claims(id),
    verifier_id UUID,
    verification_date TIMESTAMP,
    verification_result BOOLEAN,
    verification_evidence JSONB
);

CREATE TABLE ledger_entries (
    id UUID PRIMARY KEY,
    entry_type VARCHAR(50),
    entry_ref_id UUID,
    hash VARCHAR(255),
    previous_hash VARCHAR(255),
    timestamp TIMESTAMP,
    block_number INTEGER
);
```

## Интеграционные точки

### 1. Salesforce Sync
```javascript
// Пример интеграции
class SalesforceSync {
    async syncPrograms() {
        const programs = await supabase.from('programs').select('*');
        await salesforce.sobject('PMM__Program__c').create(
            programs.map(p => ({
                Name: p.name,
                PMM__Domain__c: p.domain,
                PMM__StartDate__c: p.start_at,
                PMM__EndDate__c: p.end_at
            }))
        );
    }
    
    async syncMeasurements() {
        // Salesforce → Supabase через Platform Events
        salesforce.streaming.topic('/event/Measurement__e')
            .subscribe(async (message) => {
                await supabase.from('measurements').insert({
                    indicator_id: message.Indicator_ID__c,
                    value: message.Value__c,
                    period_start: message.Period_Start__c,
                    period_end: message.Period_End__c
                });
            });
    }
}
```

### 2. AnyLogic Integration
```javascript
class AnyLogicConnector {
    async runSimulation(scenario) {
        const params = await this.prepareParameters(scenario);
        
        const response = await fetch('https://anylogic.cloud/api/v1/models/run', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${ANYLOGIC_TOKEN}` },
            body: JSON.stringify({
                model: 'ServiceDeliveryOptimization',
                inputs: params,
                outputs: ['optimal_schedule', 'resource_allocation', 'sla_forecast']
            })
        });
        
        const results = await response.json();
        await this.saveSimulationResults(results);
    }
}
```

### 3. IoT/Streaming
```javascript
class StreamingPipeline {
    constructor() {
        this.kafka = new Kafka({ brokers: ['localhost:9092'] });
    }
    
    async processSensorData(topic) {
        const consumer = this.kafka.consumer({ groupId: 'digital-twin' });
        await consumer.subscribe({ topic });
        
        await consumer.run({
            eachMessage: async ({ message }) => {
                const data = JSON.parse(message.value.toString());
                
                // Real-time update
                if (data.type === 'service_delivery') {
                    await supabase.from('service_deliveries').insert({
                        service_id: data.service_id,
                        participant_id: data.participant_id,
                        quantity: data.quantity,
                        delivered_at: data.timestamp,
                        location_id: data.location_id
                    });
                    
                    // Update metrics
                    await this.updateRealTimeMetrics(data);
                }
            }
        });
    }
}
```

## Оценка готовности системы

### Общая готовность к SEH: **15%**

| Компонент | Готовность | Критичность |
|-----------|------------|-------------|
| Модель данных | 20% | КРИТИЧНО |
| API совместимость | 30% | КРИТИЧНО |
| Безопасность/GDPR | 25% | КРИТИЧНО |
| Симуляции | 15% | ВАЖНО |
| Интеграции | 5% | ВАЖНО |
| IoT/Realtime | 5% | ЖЕЛАТЕЛЬНО |
| Blockchain/PoI | 0% | ЖЕЛАТЕЛЬНО |

## Рекомендации

### Немедленные действия (Sprint 1):
1. **Расширить модель данных** - добавить Program, Service, ServiceDelivery
2. **Implement Evidence collection** - критично для верификации
3. **GDPR Consent** - обязательное требование
4. **API versioning** - подготовка к интеграциям

### Краткосрочные (Sprint 2-3):
1. **Grant management** - ключевой функционал
2. **Salesforce connector** - базовая синхронизация
3. **Enhanced BCM** - полный цикл непрерывности
4. **Outcome hierarchy** - структурированные результаты

### Среднесрочные (Quarter):
1. **AnyLogic API** - продвинутые симуляции
2. **Streaming pipeline** - real-time данные
3. **PoI blockchain** - доказательная база
4. **Multi-tenant** - масштабирование

## Выводы

**Digital Twin система имеет хорошую базу, но требует существенной доработки для соответствия SEH стандартам:**

✅ **Сильные стороны:**
- Рабочая база данных и API
- Базовые симуляции
- Готовая визуализация
- MCP для AI интеграции

❌ **Критические пробелы:**
- Отсутствует модель услуг и их доставки
- Нет управления грантами
- Нет evidence и верификации
- Не соответствует GDPR по consent
- Нет интеграции с Salesforce
- Примитивные симуляции

**Для полного соответствия SEH потребуется 6-8 недель разработки при команде 3-4 человека.**

---
*Документ подготовлен на основе анализа SEH Master Spec v1.0 и текущей архитектуры Digital Twin v2.0.0*