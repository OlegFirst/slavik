// Database connection module for Digital Twin Platform
import pg from 'pg';
const { Pool } = pg;

class Database {
    constructor() {
        this.pool = null;
        this.isConnected = false;
    }

    async connect() {
        try {
            // PostgreSQL connection configuration
            this.pool = new Pool({
                host: process.env.POSTGRES_HOST || 'localhost',
                port: process.env.POSTGRES_PORT || 5432,
                database: process.env.POSTGRES_DATABASE || 'digital_twin_db',
                user: process.env.POSTGRES_USER || 'odoo',
                password: process.env.POSTGRES_PASSWORD || 'odoo',
                max: 20, // Maximum number of clients in the pool
                idleTimeoutMillis: 30000,
                connectionTimeoutMillis: 2000,
            });

            // Test connection
            const client = await this.pool.connect();
            const res = await client.query('SELECT NOW()');
            client.release();

            console.log('✅ PostgreSQL connected successfully at', res.rows[0].now);
            this.isConnected = true;

            // Verify tables exist
            await this.verifyTables();

            return true;
        } catch (error) {
            console.error('❌ Database connection failed:', error.message);
            console.log('⚠️ Falling back to in-memory storage');
            this.isConnected = false;
            return false;
        }
    }

    async verifyTables() {
        const tables = ['organizations', 'digital_twins', 'simulations', 'metrics', 'ai_analyses'];
        for (const table of tables) {
            const result = await this.pool.query(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = $1)",
                [table]
            );
            if (!result.rows[0].exists) {
                console.warn(`⚠️ Table ${table} does not exist`);
            } else {
                console.log(`✓ Table ${table} verified`);
            }
        }
    }

    // Organizations
    async createOrganization(data) {
        if (!this.isConnected) return this.mockCreateOrganization(data);

        const query = `
            INSERT INTO organizations
            (name, domain_type, industry_sector, annual_budget, staff_count, description, health_score)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        `;
        const values = [
            data.name,
            data.domain_type || 'corporate',
            data.industry_sector || 'general',
            data.annual_budget || 0,
            data.staff_count || 0,
            data.description || '',
            data.health_score || 75
        ];

        const result = await this.pool.query(query, values);
        return result.rows[0];
    }

    async getOrganizations() {
        if (!this.isConnected) return this.mockGetOrganizations();

        const query = 'SELECT * FROM organizations ORDER BY created_at DESC';
        const result = await this.pool.query(query);
        return result.rows;
    }

    async getOrganization(id) {
        if (!this.isConnected) return this.mockGetOrganization(id);

        const query = 'SELECT * FROM organizations WHERE id = $1';
        const result = await this.pool.query(query, [id]);
        return result.rows[0];
    }

    async updateOrganization(id, data) {
        if (!this.isConnected) return data;

        const fields = [];
        const values = [];
        let index = 1;

        Object.keys(data).forEach(key => {
            if (key !== 'id') {
                fields.push(`${key} = $${index}`);
                values.push(data[key]);
                index++;
            }
        });

        values.push(id);
        const query = `
            UPDATE organizations
            SET ${fields.join(', ')}
            WHERE id = $${index}
            RETURNING *
        `;

        const result = await this.pool.query(query, values);
        return result.rows[0];
    }

    // Digital Twins
    async createDigitalTwin(data) {
        if (!this.isConnected) return this.mockCreateDigitalTwin(data);

        const query = `
            INSERT INTO digital_twins
            (organization_id, twin_status, twin_config, simulation_results, ai_insights)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
        `;
        const values = [
            data.organization_id,
            data.twin_status || 'active',
            JSON.stringify(data.twin_config || {}),
            JSON.stringify(data.simulation_results || {}),
            JSON.stringify(data.ai_insights || {})
        ];

        const result = await this.pool.query(query, values);
        return result.rows[0];
    }

    async getDigitalTwin(organizationId) {
        if (!this.isConnected) return null;

        const query = 'SELECT * FROM digital_twins WHERE organization_id = $1';
        const result = await this.pool.query(query, [organizationId]);
        return result.rows[0];
    }

    // Simulations
    async createSimulation(data) {
        if (!this.isConnected) return this.mockCreateSimulation(data);

        const simulationId = `sim_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const query = `
            INSERT INTO simulations
            (simulation_id, organization_id, scenario_type, parameters, results, confidence_score, state)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        `;
        const values = [
            simulationId,
            data.organization_id,
            data.scenario_type,
            JSON.stringify(data.parameters || {}),
            JSON.stringify(data.results || {}),
            data.confidence_score || 0,
            data.state || 'pending'
        ];

        const result = await this.pool.query(query, values);
        return result.rows[0];
    }

    async updateSimulation(id, data) {
        if (!this.isConnected) return data;

        const query = `
            UPDATE simulations
            SET results = $1, state = $2, confidence_score = $3, completed_at = NOW()
            WHERE id = $4
            RETURNING *
        `;
        const values = [
            JSON.stringify(data.results || {}),
            data.state || 'completed',
            data.confidence_score || 0,
            id
        ];

        const result = await this.pool.query(query, values);
        return result.rows[0];
    }

    async getSimulations(organizationId) {
        if (!this.isConnected) return [];

        const query = `
            SELECT * FROM simulations
            WHERE organization_id = $1
            ORDER BY created_at DESC
            LIMIT 50
        `;
        const result = await this.pool.query(query, [organizationId]);
        return result.rows;
    }

    // Metrics
    async saveMetrics(organizationId, metrics) {
        if (!this.isConnected) return metrics;

        const promises = Object.entries(metrics).map(async ([type, value]) => {
            const query = `
                INSERT INTO metrics (organization_id, metric_type, metric_value, metric_data)
                VALUES ($1, $2, $3, $4)
                RETURNING *
            `;
            const values = [
                organizationId,
                type,
                typeof value === 'object' ? value.value : value,
                JSON.stringify(typeof value === 'object' ? value : { value })
            ];

            return this.pool.query(query, values);
        });

        await Promise.all(promises);
        return metrics;
    }

    async getLatestMetrics(organizationId) {
        if (!this.isConnected) return this.mockGetMetrics();

        const query = `
            SELECT DISTINCT ON (metric_type)
                metric_type, metric_value, metric_data, timestamp
            FROM metrics
            WHERE organization_id = $1
            ORDER BY metric_type, timestamp DESC
        `;
        const result = await this.pool.query(query, [organizationId]);

        const metrics = {};
        result.rows.forEach(row => {
            metrics[row.metric_type] = row.metric_value;
        });

        return metrics;
    }

    // AI Analyses
    async saveAIAnalysis(data) {
        if (!this.isConnected) return data;

        const query = `
            INSERT INTO ai_analyses
            (organization_id, analysis_type, organs_used, insights, recommendations, confidence_level)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
        `;
        const values = [
            data.organization_id,
            data.analysis_type,
            JSON.stringify(data.organs_used || []),
            JSON.stringify(data.insights || {}),
            JSON.stringify(data.recommendations || []),
            data.confidence_level || 0
        ];

        const result = await this.pool.query(query, values);
        return result.rows[0];
    }

    async getAIAnalyses(organizationId) {
        if (!this.isConnected) return [];

        const query = `
            SELECT * FROM ai_analyses
            WHERE organization_id = $1
            ORDER BY created_at DESC
            LIMIT 20
        `;
        const result = await this.pool.query(query, [organizationId]);
        return result.rows;
    }

    // Scenarios
    async getScenarios() {
        if (!this.isConnected) return this.mockGetScenarios();

        const query = 'SELECT * FROM scenarios WHERE is_active = true ORDER BY name';
        const result = await this.pool.query(query);
        return result.rows;
    }

    // Mock functions for when database is not connected
    mockCreateOrganization(data) {
        return {
            id: Date.now(),
            ...data,
            created_at: new Date(),
            updated_at: new Date()
        };
    }

    mockGetOrganizations() {
        return [
            {
                id: 1,
                name: 'Hope Foundation (Demo)',
                domain_type: 'npo',
                health_score: 91,
                staff_count: 350,
                annual_budget: 75000000
            },
            {
                id: 2,
                name: 'TechCorp Industries (Demo)',
                domain_type: 'corporate',
                health_score: 87,
                staff_count: 2500,
                annual_budget: 500000000
            }
        ];
    }

    mockGetOrganization(id) {
        return {
            id: id,
            name: 'Demo Organization',
            domain_type: 'corporate',
            health_score: 85,
            staff_count: 100,
            annual_budget: 10000000
        };
    }

    mockCreateDigitalTwin(data) {
        return {
            id: Date.now(),
            ...data,
            created_at: new Date()
        };
    }

    mockCreateSimulation(data) {
        return {
            id: Date.now(),
            simulation_id: `sim_${Date.now()}`,
            ...data,
            created_at: new Date()
        };
    }

    mockGetMetrics() {
        return {
            overall_health: 85,
            financial_health: 90,
            operational_efficiency: 82,
            technology_maturity: 88,
            compliance_score: 91,
            risk_level: 35
        };
    }

    mockGetScenarios() {
        return [
            {
                id: 1,
                name: 'Supply Chain Disruption',
                scenario_type: 'supply_chain_disruption',
                description: 'Simulates supply chain interruption impacts'
            },
            {
                id: 2,
                name: 'Cyber Security Incident',
                scenario_type: 'cyber_incident',
                description: 'Ransomware and data breach scenarios'
            },
            {
                id: 3,
                name: 'Pandemic Response',
                scenario_type: 'pandemic_response',
                description: 'COVID-like pandemic business continuity'
            }
        ];
    }

    async disconnect() {
        if (this.pool) {
            await this.pool.end();
            console.log('Database connection closed');
        }
    }
}

export default new Database();