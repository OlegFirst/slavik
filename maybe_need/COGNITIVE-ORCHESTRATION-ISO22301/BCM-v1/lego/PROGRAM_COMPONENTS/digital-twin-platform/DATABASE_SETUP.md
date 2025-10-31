# Настройка реальной базы данных для Digital Twin Platform

## 🗄️ Варианты подключения БД

### Вариант 1: PostgreSQL (Рекомендуется)

#### 1.1 Установка PostgreSQL локально:

```bash
# MacOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### 1.2 Создание базы данных:

```sql
-- Подключиться к PostgreSQL
psql -U postgres

-- Создать базу данных
CREATE DATABASE digital_twin_db;

-- Создать пользователя
CREATE USER dt_user WITH PASSWORD 'secure_password_here';

-- Дать права
GRANT ALL PRIVILEGES ON DATABASE digital_twin_db TO dt_user;
```

#### 1.3 Создание таблиц:

```sql
\c digital_twin_db

-- Таблица организаций
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    domain_type VARCHAR(50),
    industry_sector VARCHAR(50),
    annual_budget DECIMAL(15,2),
    staff_count INTEGER,
    bcm_client_id INTEGER,
    health_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица Digital Twins
CREATE TABLE digital_twins (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    twin_status VARCHAR(50) DEFAULT 'active',
    twin_config JSONB,
    simulation_results JSONB,
    ai_insights JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица симуляций
CREATE TABLE simulations (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    scenario_type VARCHAR(100),
    parameters JSONB,
    results JSONB,
    confidence_score DECIMAL(5,2),
    state VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица AI анализов
CREATE TABLE ai_analyses (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    analysis_type VARCHAR(100),
    organs_used JSONB,
    insights JSONB,
    recommendations JSONB,
    confidence_level DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица метрик
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    metric_type VARCHAR(100),
    metric_value DECIMAL(10,2),
    metric_data JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для производительности
CREATE INDEX idx_organizations_domain ON organizations(domain_type);
CREATE INDEX idx_simulations_org ON simulations(organization_id);
CREATE INDEX idx_simulations_state ON simulations(state);
CREATE INDEX idx_metrics_org_time ON metrics(organization_id, timestamp DESC);
```

#### 1.4 Обновление .env файла:

```bash
# Реальная конфигурация PostgreSQL
DATABASE_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=digital_twin_db
POSTGRES_USER=dt_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_SSL=false

# Удалить или закомментировать mock настройки
# SUPABASE_URL=https://mock-supabase-url.supabase.co
# DATABASE_TYPE=memory
```

### Вариант 2: Supabase (Cloud PostgreSQL)

#### 2.1 Создание проекта в Supabase:

1. Зайти на https://supabase.com
2. Создать новый проект
3. Получить URL и ключи из Settings → API

#### 2.2 Обновление .env:

```bash
# Реальные Supabase credentials
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-key-here
```

#### 2.3 Создание таблиц в Supabase:

Использовать Supabase SQL Editor и выполнить SQL из пункта 1.3

### Вариант 3: MongoDB (NoSQL альтернатива)

#### 3.1 Установка MongoDB:

```bash
# MacOS
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# Ubuntu
sudo apt install mongodb
sudo systemctl start mongodb
```

#### 3.2 Конфигурация:

```bash
# .env для MongoDB
DATABASE_TYPE=mongodb
MONGODB_URI=mongodb://localhost:27017/digital_twin
MONGODB_USER=dt_user
MONGODB_PASSWORD=secure_password
```

## 🔄 Подключение базы данных в Node.js

### Создать новый файл database.js:

```javascript
// /Users/MD/digital-twin-bcm-integration/digital-twin-main/src/database.js

const { Pool } = require('pg');
const mongoose = require('mongoose');

class DatabaseConnection {
    constructor() {
        this.type = process.env.DATABASE_TYPE || 'memory';
        this.connection = null;
    }

    async connect() {
        switch (this.type) {
            case 'postgresql':
                await this.connectPostgreSQL();
                break;
            case 'mongodb':
                await this.connectMongoDB();
                break;
            case 'memory':
                this.connectMemory();
                break;
            default:
                throw new Error(`Unsupported database type: ${this.type}`);
        }
    }

    async connectPostgreSQL() {
        this.connection = new Pool({
            host: process.env.POSTGRES_HOST,
            port: process.env.POSTGRES_PORT,
            database: process.env.POSTGRES_DATABASE,
            user: process.env.POSTGRES_USER,
            password: process.env.POSTGRES_PASSWORD,
            ssl: process.env.POSTGRES_SSL === 'true'
        });

        // Test connection
        try {
            const client = await this.connection.connect();
            console.log('✅ PostgreSQL connected successfully');
            client.release();
        } catch (error) {
            console.error('❌ PostgreSQL connection failed:', error);
            throw error;
        }
    }

    async connectMongoDB() {
        const uri = process.env.MONGODB_URI;
        this.connection = await mongoose.connect(uri, {
            useNewUrlParser: true,
            useUnifiedTopology: true
        });
        console.log('✅ MongoDB connected successfully');
    }

    connectMemory() {
        // In-memory storage
        this.connection = {
            organizations: new Map(),
            twins: new Map(),
            simulations: new Map(),
            metrics: new Map()
        };
        console.log('⚠️ Using in-memory database (data will not persist)');
    }

    // Database operations
    async createOrganization(data) {
        if (this.type === 'postgresql') {
            const query = `
                INSERT INTO organizations (name, domain_type, industry_sector, annual_budget, staff_count)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
            `;
            const values = [data.name, data.domain_type, data.industry_sector, data.annual_budget, data.staff_count];
            const result = await this.connection.query(query, values);
            return result.rows[0];
        } else if (this.type === 'memory') {
            const id = Date.now();
            const org = { id, ...data, created_at: new Date() };
            this.connection.organizations.set(id, org);
            return org;
        }
    }

    async getOrganization(id) {
        if (this.type === 'postgresql') {
            const query = 'SELECT * FROM organizations WHERE id = $1';
            const result = await this.connection.query(query, [id]);
            return result.rows[0];
        } else if (this.type === 'memory') {
            return this.connection.organizations.get(parseInt(id));
        }
    }

    async createSimulation(data) {
        if (this.type === 'postgresql') {
            const query = `
                INSERT INTO simulations (organization_id, scenario_type, parameters, results, confidence_score, state)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
            `;
            const values = [
                data.organization_id,
                data.scenario_type,
                JSON.stringify(data.parameters),
                JSON.stringify(data.results),
                data.confidence_score,
                data.state || 'pending'
            ];
            const result = await this.connection.query(query, values);
            return result.rows[0];
        } else if (this.type === 'memory') {
            const id = Date.now();
            const sim = { id, ...data, created_at: new Date() };
            this.connection.simulations.set(id, sim);
            return sim;
        }
    }

    async saveMetrics(organizationId, metrics) {
        if (this.type === 'postgresql') {
            const query = `
                INSERT INTO metrics (organization_id, metric_type, metric_value, metric_data)
                VALUES ($1, $2, $3, $4)
                RETURNING *
            `;

            const promises = Object.entries(metrics).map(([type, value]) => {
                return this.connection.query(query, [
                    organizationId,
                    type,
                    typeof value === 'object' ? value.value : value,
                    JSON.stringify(typeof value === 'object' ? value : { value })
                ]);
            });

            await Promise.all(promises);
            return metrics;
        } else if (this.type === 'memory') {
            const id = `${organizationId}_${Date.now()}`;
            this.connection.metrics.set(id, { organizationId, metrics, timestamp: new Date() });
            return metrics;
        }
    }

    async getLatestMetrics(organizationId) {
        if (this.type === 'postgresql') {
            const query = `
                SELECT DISTINCT ON (metric_type)
                    metric_type, metric_value, metric_data, timestamp
                FROM metrics
                WHERE organization_id = $1
                ORDER BY metric_type, timestamp DESC
            `;
            const result = await this.connection.query(query, [organizationId]);

            const metrics = {};
            result.rows.forEach(row => {
                metrics[row.metric_type] = row.metric_value;
            });
            return metrics;
        } else if (this.type === 'memory') {
            // Return mock metrics for memory mode
            return {
                overall_health: 85,
                financial_health: 90,
                operational_efficiency: 82,
                technology_maturity: 88
            };
        }
    }
}

module.exports = new DatabaseConnection();
```

## 📝 Обновление simple-web-server.js

После настройки БД, обновите основной сервер:

```javascript
// В начале файла добавить:
const database = require('./src/database');

// При запуске сервера:
async function startServer() {
    // Подключиться к БД
    await database.connect();

    // Запустить сервер
    app.listen(PORT, () => {
        console.log(`Server started on port ${PORT}`);
    });
}

startServer().catch(console.error);

// Обновить endpoints для использования реальной БД:
app.post('/api/organizations', async (req, res) => {
    try {
        const organization = await database.createOrganization(req.body);
        res.status(201).json(organization);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/organizations/:id', async (req, res) => {
    try {
        const organization = await database.getOrganization(req.params.id);
        if (!organization) {
            return res.status(404).json({ error: 'Organization not found' });
        }
        res.json(organization);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});
```

## ✅ После подключения БД вы получите:

1. **Persistent хранилище** - данные сохраняются между перезапусками
2. **Реальные организации** - можно создавать и управлять настоящими Digital Twins
3. **История симуляций** - все анализы сохраняются для отчетности
4. **Метрики и аналитика** - накапливаются реальные данные для трендов
5. **Multi-user поддержка** - несколько пользователей могут работать одновременно

## 🚨 Важные замечания:

- Сейчас система **полностью функциональна**, но работает с **временными данными в памяти**
- После подключения БД все созданные организации и симуляции будут **сохраняться постоянно**
- Рекомендую начать с **PostgreSQL** как наиболее совместимого с Odoo решения
- Для production используйте **Supabase** или managed PostgreSQL для надежности