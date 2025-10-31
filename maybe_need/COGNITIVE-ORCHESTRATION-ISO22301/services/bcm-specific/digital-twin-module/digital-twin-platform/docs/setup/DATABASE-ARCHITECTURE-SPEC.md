# DATABASE ARCHITECTURE SPECIFICATION
## Digital Twin Standalone Module

**Date**: 2025-01-15  
**Version**: 2.0.0  
**Status**: PRODUCTION READY

---

## 🎯 EXECUTIVE SUMMARY

Digital Twin модулю нужна гибридная архитектура баз данных для разных типов данных и нагрузок:

### Рекомендуемый Stack:
1. **Supabase (PostgreSQL)** - Основная БД для структурированных данных
2. **Redis** - Кэширование и real-time данные
3. **MongoDB** - Опционально для документов и неструктурированных данных

---

## 📊 1. SUPABASE (ОСНОВНАЯ БД)

### Почему Supabase?
- **Готовая инфраструктура** - Auth, Realtime, Storage из коробки
- **PostgreSQL** - Мощная реляционная БД с JSONB поддержкой
- **Edge Functions** - Serverless функции для бизнес-логики
- **Row Level Security** - Безопасность на уровне строк
- **Realtime subscriptions** - Автоматические обновления данных
- **Бесплатный tier** - 500MB БД, 2GB storage, 50K MAU

### Схема таблиц для Supabase:

```sql
-- ORGANIZATIONS (Организации)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) CHECK (type IN ('non-profit', 'charity', 'foundation', 'association')),
    mission TEXT,
    description TEXT,
    size INTEGER,
    annual_budget DECIMAL(15, 2),
    website VARCHAR(255),
    contact_info JSONB,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    is_active BOOLEAN DEFAULT true
);

-- Индексы
CREATE INDEX idx_org_type ON organizations(type);
CREATE INDEX idx_org_active ON organizations(is_active);
CREATE INDEX idx_org_created ON organizations(created_at DESC);

-- DIGITAL_TWINS (Цифровые двойники)
CREATE TABLE digital_twins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id VARCHAR(255) UNIQUE NOT NULL,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) DEFAULT '1.0.0',
    configuration JSONB NOT NULL DEFAULT '{}',
    state JSONB DEFAULT '{}',
    health_score DECIMAL(3, 2) CHECK (health_score >= 0 AND health_score <= 1),
    efficiency_score DECIMAL(3, 2) CHECK (efficiency_score >= 0 AND efficiency_score <= 1),
    last_simulation_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    
    -- Дополнительные поля для аналитики
    total_simulations INTEGER DEFAULT 0,
    total_predictions INTEGER DEFAULT 0,
    accuracy_rate DECIMAL(3, 2)
);

-- Индексы
CREATE INDEX idx_twin_org ON digital_twins(organization_id);
CREATE INDEX idx_twin_active ON digital_twins(is_active);
CREATE INDEX idx_twin_health ON digital_twins(health_score);

-- DEPARTMENTS (Департаменты организации)
CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    staff_count INTEGER DEFAULT 0,
    budget_allocation DECIMAL(15, 2),
    efficiency_score DECIMAL(3, 2),
    responsibilities TEXT[],
    kpis JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(organization_id, name)
);

-- SIMULATIONS (Симуляции)
CREATE TABLE simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    simulation_id VARCHAR(255) UNIQUE NOT NULL,
    twin_id UUID REFERENCES digital_twins(id) ON DELETE CASCADE,
    scenario VARCHAR(100) NOT NULL,
    scenario_category VARCHAR(50),
    parameters JSONB NOT NULL DEFAULT '{}',
    initial_state JSONB,
    final_state JSONB,
    results JSONB,
    recommendations JSONB DEFAULT '[]',
    confidence_score DECIMAL(3, 2),
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'))
);

-- Индексы
CREATE INDEX idx_sim_twin ON simulations(twin_id);
CREATE INDEX idx_sim_scenario ON simulations(scenario);
CREATE INDEX idx_sim_status ON simulations(status);
CREATE INDEX idx_sim_created ON simulations(created_at DESC);

-- METRICS (Метрики)
CREATE TABLE metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id UUID REFERENCES digital_twins(id) ON DELETE CASCADE,
    metric_type VARCHAR(100) NOT NULL,
    metric_category VARCHAR(50),
    value DECIMAL(15, 4) NOT NULL,
    unit VARCHAR(50),
    target_value DECIMAL(15, 4),
    threshold_min DECIMAL(15, 4),
    threshold_max DECIMAL(15, 4),
    is_critical BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Индексы для аналитики
CREATE INDEX idx_metrics_twin ON metrics(twin_id);
CREATE INDEX idx_metrics_type ON metrics(metric_type);
CREATE INDEX idx_metrics_timestamp ON metrics(timestamp DESC);
CREATE INDEX idx_metrics_critical ON metrics(is_critical) WHERE is_critical = true;

-- Партиционирование по времени для больших объемов
CREATE TABLE metrics_2025_q1 PARTITION OF metrics
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');

-- PREDICTIONS (Предсказания AI)
CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id UUID REFERENCES digital_twins(id) ON DELETE CASCADE,
    prediction_type VARCHAR(100) NOT NULL,
    target_date DATE NOT NULL,
    predicted_value DECIMAL(15, 4),
    confidence_interval JSONB,
    confidence_score DECIMAL(3, 2),
    actual_value DECIMAL(15, 4),
    accuracy DECIMAL(3, 2),
    model_used VARCHAR(100),
    factors JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    validated_at TIMESTAMPTZ
);

-- Индексы
CREATE INDEX idx_pred_twin ON predictions(twin_id);
CREATE INDEX idx_pred_type ON predictions(prediction_type);
CREATE INDEX idx_pred_target ON predictions(target_date);

-- AUDIT_LOGS (Аудит)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id UUID REFERENCES auth.users(id),
    actor_email VARCHAR(255),
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Индексы для поиска
CREATE INDEX idx_audit_actor ON audit_logs(actor_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);

-- SESSIONS (Сессии пользователей)
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    twin_id UUID REFERENCES digital_twins(id),
    data JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Индекс для очистки истекших сессий
CREATE INDEX idx_sessions_expires ON sessions(expires_at);
CREATE INDEX idx_sessions_user ON sessions(user_id);

-- REPORTS (Сохраненные отчеты)
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id UUID REFERENCES digital_twins(id) ON DELETE CASCADE,
    report_type VARCHAR(100) NOT NULL,
    title VARCHAR(255),
    content JSONB NOT NULL,
    format VARCHAR(20) DEFAULT 'json',
    file_url TEXT,
    generated_by UUID REFERENCES auth.users(id),
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    is_public BOOLEAN DEFAULT false
);

-- SCENARIOS (Библиотека сценариев)
CREATE TABLE scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    parameters_schema JSONB NOT NULL,
    default_parameters JSONB,
    complexity VARCHAR(20) CHECK (complexity IN ('simple', 'moderate', 'complex')),
    estimated_duration_ms INTEGER,
    tags TEXT[],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Row Level Security (RLS)
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE digital_twins ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulations ENABLE ROW LEVEL SECURITY;

-- Политики безопасности
CREATE POLICY "Users can view their organization's data" ON organizations
    FOR SELECT USING (created_by = auth.uid() OR is_active = true);

CREATE POLICY "Users can manage their twins" ON digital_twins
    FOR ALL USING (
        organization_id IN (
            SELECT id FROM organizations WHERE created_by = auth.uid()
        )
    );

-- Функции и триггеры
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Применяем триггер ко всем таблицам с updated_at
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    
CREATE TRIGGER update_digital_twins_updated_at BEFORE UPDATE ON digital_twins
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Функция для расчета health score
CREATE OR REPLACE FUNCTION calculate_health_score(twin_id UUID)
RETURNS DECIMAL AS $$
DECLARE
    health_score DECIMAL;
BEGIN
    SELECT AVG(
        CASE 
            WHEN metric_type = 'efficiency' THEN value
            WHEN metric_type = 'financial_health' THEN value / 100
            WHEN metric_type = 'staff_satisfaction' THEN value / 10
            ELSE 0.5
        END
    ) INTO health_score
    FROM metrics
    WHERE metrics.twin_id = $1
    AND timestamp > NOW() - INTERVAL '30 days';
    
    RETURN COALESCE(health_score, 0.5);
END;
$$ LANGUAGE plpgsql;
```

### Настройка Supabase:

```javascript
// .env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
```

```javascript
// supabase-client.js
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.SUPABASE_URL
const supabaseKey = process.env.SUPABASE_SERVICE_KEY // для сервера

export const supabase = createClient(supabaseUrl, supabaseKey, {
    auth: {
        autoRefreshToken: true,
        persistSession: true
    },
    db: {
        schema: 'public'
    },
    realtime: {
        params: {
            eventsPerSecond: 10
        }
    }
})
```

---

## 🚀 2. REDIS (КЭШИРОВАНИЕ И REAL-TIME)

### Для чего используем Redis:
- **Кэш запросов** - Результаты сложных вычислений
- **Сессии** - Хранение активных сессий
- **Rate limiting** - Ограничение запросов
- **Pub/Sub** - Real-time обновления
- **Очереди** - Фоновые задачи

### Структура ключей Redis:

```javascript
// Naming convention для ключей
const RedisKeys = {
    // Кэш
    cache: {
        twin: (id) => `cache:twin:${id}`,
        metrics: (twinId, type) => `cache:metrics:${twinId}:${type}`,
        simulation: (id) => `cache:simulation:${id}`,
        report: (twinId, type) => `cache:report:${twinId}:${type}`
    },
    
    // Сессии
    session: (sessionId) => `session:${sessionId}`,
    userSessions: (userId) => `user:sessions:${userId}`,
    
    // Rate limiting
    rateLimit: (ip, endpoint) => `rate:${ip}:${endpoint}`,
    
    // Real-time
    channels: {
        twinUpdates: (twinId) => `channel:twin:${twinId}`,
        simulations: (twinId) => `channel:sim:${twinId}`,
        metrics: (twinId) => `channel:metrics:${twinId}`
    },
    
    // Очереди
    queues: {
        simulations: 'queue:simulations',
        reports: 'queue:reports',
        predictions: 'queue:predictions'
    }
}

// TTL (время жизни) для разных типов
const RedisTTL = {
    cache: {
        twin: 3600,        // 1 час
        metrics: 300,      // 5 минут
        simulation: 1800,  // 30 минут
        report: 7200       // 2 часа
    },
    session: 86400,        // 24 часа
    rateLimit: 900        // 15 минут
}
```

### Настройка Redis:

```javascript
// redis-client.js
import Redis from 'ioredis'

// Основной клиент
export const redis = new Redis({
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379,
    password: process.env.REDIS_PASSWORD,
    db: 0,
    retryStrategy: (times) => Math.min(times * 50, 2000),
    maxRetriesPerRequest: 3
})

// Клиент для Pub/Sub
export const subscriber = new Redis({
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379,
    password: process.env.REDIS_PASSWORD,
    db: 0
})

// Клиент для публикации
export const publisher = new Redis({
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379,
    password: process.env.REDIS_PASSWORD,
    db: 0
})
```

---

## 📦 3. MONGODB (ОПЦИОНАЛЬНО)

### Когда нужна MongoDB:
- **Большие документы** - Полные отчеты, исследования
- **Гибкая схема** - Часто меняющиеся структуры данных
- **Полнотекстовый поиск** - Поиск по документам
- **Агрегация** - Сложная аналитика

### Коллекции MongoDB:

```javascript
// MongoDB схемы
const schemas = {
    // Архив полных отчетов
    reports: {
        _id: ObjectId,
        twinId: String,
        reportType: String,
        generatedAt: Date,
        content: {
            // Произвольная структура отчета
            executive_summary: String,
            sections: Array,
            charts: Array,
            data_tables: Array
        },
        metadata: {
            format: String,
            size: Number,
            pages: Number
        },
        tags: [String],
        searchableText: String // для полнотекстового поиска
    },
    
    // История изменений (Event Sourcing)
    events: {
        _id: ObjectId,
        aggregateId: String,
        aggregateType: String,
        eventType: String,
        eventData: Object,
        eventMetadata: {
            userId: String,
            timestamp: Date,
            version: Number
        }
    },
    
    // Документы и файлы
    documents: {
        _id: ObjectId,
        organizationId: String,
        type: String,
        title: String,
        content: Binary, // GridFS для больших файлов
        metadata: Object,
        uploadedAt: Date,
        uploadedBy: String
    }
}

// Индексы
db.reports.createIndex({ twinId: 1, reportType: 1 })
db.reports.createIndex({ searchableText: "text" })
db.events.createIndex({ aggregateId: 1, eventType: 1 })
db.events.createIndex({ "eventMetadata.timestamp": -1 })
```

---

## 🏗️ 4. АРХИТЕКТУРА ИСПОЛЬЗОВАНИЯ

### Стратегия выбора БД для операций:

```javascript
class DatabaseRouter {
    // Структурированные данные -> Supabase
    async saveOrganization(data) {
        return await supabase
            .from('organizations')
            .insert(data)
    }
    
    // Кэширование -> Redis
    async getCachedMetrics(twinId) {
        const cacheKey = RedisKeys.cache.metrics(twinId)
        let metrics = await redis.get(cacheKey)
        
        if (!metrics) {
            metrics = await supabase
                .from('metrics')
                .select('*')
                .eq('twin_id', twinId)
                .order('timestamp', { ascending: false })
                .limit(100)
            
            await redis.setex(cacheKey, RedisTTL.cache.metrics, JSON.stringify(metrics))
        }
        
        return JSON.parse(metrics)
    }
    
    // Real-time -> Redis Pub/Sub + Supabase Realtime
    async publishUpdate(twinId, data) {
        // Сохраняем в БД
        await supabase.from('digital_twins').update(data).eq('id', twinId)
        
        // Публикуем в Redis для подписчиков
        await publisher.publish(
            RedisKeys.channels.twinUpdates(twinId),
            JSON.stringify(data)
        )
    }
    
    // Большие документы -> MongoDB
    async saveReport(report) {
        // Метаданные в Supabase
        const { data: meta } = await supabase
            .from('reports')
            .insert({
                twin_id: report.twinId,
                report_type: report.type,
                title: report.title
            })
            .select()
            .single()
        
        // Полный документ в MongoDB
        await mongodb.collection('reports').insertOne({
            ...report,
            supabaseId: meta.id
        })
        
        return meta.id
    }
}
```

---

## 🔄 5. МИГРАЦИИ И ИНИЦИАЛИЗАЦИЯ

### Порядок настройки:

1. **Supabase**:
```bash
# Создать проект на supabase.com
# Получить ключи из Settings -> API
# Выполнить SQL миграции через Dashboard или CLI
npx supabase init
npx supabase db push
```

2. **Redis**:
```bash
# Docker
docker run -d -p 6379:6379 --name redis-digital-twin redis:alpine

# Или Redis Cloud (бесплатно 30MB)
# cloud.redis.io
```

3. **MongoDB** (опционально):
```bash
# Docker
docker run -d -p 27017:27017 --name mongo-digital-twin mongo

# Или MongoDB Atlas (бесплатно 512MB)
# cloud.mongodb.com
```

---

## 📊 6. МОНИТОРИНГ И ОПТИМИЗАЦИЯ

### Метрики для отслеживания:

```javascript
const DatabaseMetrics = {
    supabase: {
        queryTime: [], // Время выполнения запросов
        activeConnections: 0,
        errorRate: 0,
        rowsRead: 0,
        rowsWritten: 0
    },
    
    redis: {
        hitRate: 0, // Процент попаданий в кэш
        memoryUsage: 0,
        evictedKeys: 0,
        connectedClients: 0
    },
    
    mongodb: {
        documentCount: 0,
        indexUsage: {},
        queryExecutionTime: []
    }
}

// Логирование медленных запросов
supabase.from('organizations')
    .select('*')
    .then(({ data, error, count }) => {
        if (queryTime > 1000) {
            logger.warn('Slow query detected', { queryTime })
        }
    })
```

---

## 🚦 7. BACKUP И DISASTER RECOVERY

### Стратегия резервного копирования:

1. **Supabase**:
   - Автоматические бэкапы (Pro план)
   - Point-in-time recovery
   - Экспорт через pg_dump

2. **Redis**:
   - RDB snapshots каждый час
   - AOF (Append Only File) для durability
   - Репликация master-slave

3. **MongoDB**:
   - mongodump/mongorestore
   - Replica Set для HA
   - Snapshots на уровне файловой системы

---

## 💰 8. СТОИМОСТЬ И МАСШТАБИРОВАНИЕ

### Бесплатные лимиты:

| Сервис | Бесплатно | Достаточно для |
|--------|-----------|-----------------|
| **Supabase** | 500MB DB, 1GB transfer, 2GB storage | ~10K организаций |
| **Redis Cloud** | 30MB RAM | Кэш для 1K активных пользователей |
| **MongoDB Atlas** | 512MB storage | ~100K документов |

### План масштабирования:

1. **Начальный этап** (0-1K пользователей):
   - Supabase Free
   - Redis в Docker локально
   - MongoDB не нужна

2. **Рост** (1K-10K пользователей):
   - Supabase Pro ($25/месяц)
   - Redis Cloud ($5/месяц)
   - MongoDB Atlas M0 (бесплатно)

3. **Масштаб** (10K+ пользователей):
   - Supabase Team/Custom
   - Redis Enterprise
   - MongoDB Atlas M10+

---

## 🔐 9. БЕЗОПАСНОСТЬ

### Ключевые меры:

1. **Шифрование**:
   - TLS для всех соединений
   - Шифрование at rest в Supabase
   - Поля с PII шифровать дополнительно

2. **Доступ**:
   - Row Level Security в Supabase
   - API ключи в переменных окружения
   - Ротация ключей каждые 90 дней

3. **Аудит**:
   - Все операции логировать в audit_logs
   - Алерты на подозрительную активность
   - GDPR compliance для EU пользователей

---

## 📝 10. CHECKLIST ДЛЯ ЗАПУСКА

- [ ] Создать Supabase проект
- [ ] Выполнить SQL миграции
- [ ] Настроить Row Level Security
- [ ] Запустить Redis (Docker или Cloud)
- [ ] Настроить переменные окружения
- [ ] Протестировать соединения
- [ ] Настроить мониторинг
- [ ] Создать backup план
- [ ] Документировать API endpoints
- [ ] Провести load testing

---

## 🎯 ИТОГОВАЯ РЕКОМЕНДАЦИЯ

**Для быстрого старта:**
1. **Supabase** - основная БД (бесплатно)
2. **Redis** - в Docker локально (бесплатно)
3. **MongoDB** - пока не нужна

**Преимущества этого стека:**
- Минимальные затраты на старте
- Легкое масштабирование
- Готовая инфраструктура (auth, realtime, storage)
- Отличная документация
- Быстрый time-to-market

**Команды для запуска:**
```bash
# 1. Установить Supabase CLI
npm install -g supabase

# 2. Инициализировать проект
supabase init

# 3. Запустить Redis
docker run -d -p 6379:6379 redis:alpine

# 4. Установить зависимости
npm install @supabase/supabase-js ioredis

# 5. Запустить приложение
npm start
```

---

*Документ подготовлен согласно стандартам PARTNERSHIP-EXCELLENCE*