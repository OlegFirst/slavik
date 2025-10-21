/**
 * Simple Web Server for Digital Twin
 * Минимальный рабочий сервер
 */

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import fetch from 'node-fetch';
import { createClient } from '@supabase/supabase-js';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import sehRouter from './api/seh-endpoints.js';
import { ImpactValidationBridge } from './src/impact-validation-bridge.js';
import { ImpactPassportGenerator } from './src/impact-passport-generator.js';
import { SimulationRouter } from './src/simulation-router.js';
import { createImpactRoutes } from './src/api/impact-endpoints.js';
import database from './src/database.js';
import odooBridge from './src/odoo-bridge.js';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Initialize Supabase (with fallback for development)
let supabase = null;
try {
    if (process.env.SUPABASE_URL && process.env.SUPABASE_URL !== 'https://mock-supabase-url.supabase.co') {
        supabase = createClient(
            process.env.SUPABASE_URL,
            process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY
        );
    } else {
        console.log(' Development mode: Supabase disabled');
        supabase = {
            // Mock Supabase interface for development
            from: () => ({
                select: () => Promise.resolve({ data: [], error: null }),
                insert: () => Promise.resolve({ data: null, error: null }),
                update: () => Promise.resolve({ data: null, error: null }),
                delete: () => Promise.resolve({ data: null, error: null })
            })
        };
    }
} catch (error) {
    console.log('️ Supabase connection failed, using mock interface:', error.message);
    supabase = {
        from: () => ({
            select: () => Promise.resolve({ data: [], error: null }),
            insert: () => Promise.resolve({ data: null, error: null }),
            update: () => Promise.resolve({ data: null, error: null }),
            delete: () => Promise.resolve({ data: null, error: null })
        })
    };
}

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Initialize Impact components
const validationBridge = new ImpactValidationBridge();
const passportGenerator = new ImpactPassportGenerator();
const simulationRouter = new SimulationRouter();

// Initialize components with dependencies
async function initializeComponents() {
    try {
        // Initialize validation bridge with Impact Proof System (if available)
        await validationBridge.initialize(null); // IPS будет подключен позже
        
        // Initialize passport generator with Supabase
        await passportGenerator.initialize(null, supabase);
        
        console.log('[SUCCESS] Impact components initialized');
    } catch (error) {
        console.error('[ERROR] Failed to initialize Impact components:', error);
    }
}

// Initialize on startup
initializeComponents();

// Add supabase to all requests
app.use((req, res, next) => {
    req.supabase = supabase;
    req.validationBridge = validationBridge;
    req.passportGenerator = passportGenerator;
    req.simulationRouter = simulationRouter;
    next();
});

// Mount SEH API endpoints
app.use('/api/seh', sehRouter);

// Mount Impact API endpoints
const impactRoutes = createImpactRoutes(validationBridge, passportGenerator, simulationRouter);
app.use('/api/impact', impactRoutes);

// Serve static files from web-interface
app.use('/static', express.static(join(__dirname, 'web-interface', 'static')));

// Serve the main visualization interface
app.get('/', (req, res) => {
    res.sendFile(join(__dirname, 'web-interface', 'templates', 'index.html'));
});


// Health check
app.get('/health', async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('organization_profiles')
            .select('count')
            .limit(1);
        
        // Check adapter status
        const adapters = {};
        const adapterUrls = {
            simpy: process.env.SIMPY_ADAPTER_URL || 'http://localhost:7001',
            mesa: process.env.MESA_ADAPTER_URL || 'http://localhost:7002',
            epinow2: process.env.EPINOW2_ADAPTER_URL || 'http://localhost:7003'
        };
        
        for (const [name, url] of Object.entries(adapterUrls)) {
            try {
                const response = await fetch(`${url.replace('/run', '/docs')}`, { timeout: 5000 });
                adapters[name] = response.ok ? 'healthy' : 'unhealthy';
            } catch (e) {
                adapters[name] = 'unreachable';
            }
        }
        
        res.json({
            status: 'healthy',
            database: error ? 'disconnected' : 'connected',
            adapters,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            status: 'unhealthy',
            error: error.message
        });
    }
});

// Get all organizations (hybrid: Odoo + PostgreSQL)
app.get('/api/organizations', async (req, res) => {
    try {
        const integrationMode = process.env.INTEGRATION_MODE || 'hybrid';
        let organizations = [];

        if (integrationMode === 'odoo-only' || integrationMode === 'hybrid') {
            // Получаем данные из Odoo
            try {
                const odooOrganizations = await odooBridge.getOrganizations();
                organizations = odooOrganizations.map(org => ({
                    id: org.id,
                    name: org.organization_name,
                    domain_type: org.domain_type,
                    health_score: org.health_score,
                    risk_level: org.risk_level,
                    is_active: org.is_active,
                    source: 'odoo',
                    bcm_client_id: org.bcm_client_id?.[0] || null,
                    last_updated: org.last_updated
                }));
                console.log(` Retrieved ${organizations.length} organizations from Odoo`);
            } catch (odooError) {
                console.log('️ Odoo unavailable, falling back to PostgreSQL:', odooError.message);
            }
        }

        if (integrationMode === 'postgres-only' || (integrationMode === 'hybrid' && organizations.length === 0)) {
            // Fallback к PostgreSQL
            const pgOrganizations = await database.getOrganizations();
            organizations = organizations.concat(pgOrganizations.map(org => ({
                ...org,
                source: 'postgresql'
            })));
        }

        res.json({
            success: true,
            data: organizations,
            meta: {
                count: organizations.length,
                integration_mode: integrationMode,
                timestamp: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('Error getting organizations:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            fallback: 'Check Odoo connection and database status'
        });
    }
});

// Create organization (hybrid: Odoo + PostgreSQL)
app.post('/api/organizations', async (req, res) => {
    try {
        const integrationMode = process.env.INTEGRATION_MODE || 'hybrid';
        let organization = null;
        let createdInOdoo = false;

        // Подготавливаем данные для Odoo формата
        const odooData = {
            organization_name: req.body.name,
            domain_type: req.body.domain_type || 'corporate',
            health_score: req.body.health_score || 0.0,
            risk_level: req.body.risk_level || 'low',
            is_active: req.body.is_active !== false,
            current_state: req.body.current_state || '{}',
            metadata: req.body.metadata || '{}'
        };

        if (integrationMode === 'odoo-only' || integrationMode === 'hybrid') {
            // Создаем в Odoo
            try {
                const odooId = await odooBridge.createDigitalTwin(odooData);
                organization = {
                    id: odooId,
                    name: odooData.organization_name,
                    domain_type: odooData.domain_type,
                    health_score: odooData.health_score,
                    risk_level: odooData.risk_level,
                    is_active: odooData.is_active,
                    source: 'odoo',
                    created_at: new Date().toISOString()
                };
                createdInOdoo = true;
                console.log(` Organization created in Odoo with ID: ${odooId}`);
            } catch (odooError) {
                console.log('️ Failed to create in Odoo:', odooError.message);
                if (integrationMode === 'odoo-only') {
                    throw odooError;
                }
            }
        }

        if (!createdInOdoo && (integrationMode === 'postgres-only' || integrationMode === 'hybrid')) {
            // Fallback к PostgreSQL
            const pgOrganization = await database.createOrganization(req.body);
            organization = { ...pgOrganization, source: 'postgresql' };
            console.log(` Organization created in PostgreSQL with ID: ${pgOrganization.id}`);
        }

        res.status(201).json({
            success: true,
            data: organization,
            meta: {
                created_in_odoo: createdInOdoo,
                integration_mode: integrationMode,
                timestamp: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('Error creating organization:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Get organization by ID
app.get('/api/organizations/:id', async (req, res) => {
    try {
        const organization = await database.getOrganization(req.params.id);
        if (!organization) return res.status(404).json({ error: 'Organization not found' });
        res.json(organization);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Create digital twin
app.post('/api/digital-twins', async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('digital_twins')
            .insert(req.body)
            .select()
            .single();
        
        if (error) throw error;
        res.status(201).json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get digital twin
app.get('/api/digital-twins/:id', async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('digital_twins')
            .select('*')
            .eq('id', req.params.id)
            .single();
        
        if (error) throw error;
        if (!data) return res.status(404).json({ error: 'Digital twin not found' });
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Create simulation
app.post('/api/simulations', async (req, res) => {
    try {
        const simulationData = {
            ...req.body,
            simulation_id: `sim_${Date.now()}`,
            status: 'running'
        };
        
        const { data, error } = await supabase
            .from('simulations')
            .insert(simulationData)
            .select()
            .single();
        
        if (error) throw error;
        
        // Simulate completion after 2 seconds
        setTimeout(async () => {
            await supabase
                .from('simulations')
                .update({ 
                    status: 'completed',
                    results: {
                        success: true,
                        optimizations: Math.floor(Math.random() * 10) + 1,
                        savings: Math.floor(Math.random() * 50000) + 10000
                    }
                })
                .eq('id', data.id);
        }, 2000);
        
        res.status(201).json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get metrics
app.get('/api/metrics/:twinId', async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('metrics')
            .select('*')
            .eq('twin_id', req.params.twinId)
            .order('timestamp', { ascending: false })
            .limit(100);
        
        if (error) throw error;
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// BCM Digital Twin Bridge API Endpoints
// Health check for Odoo Bridge
app.get('/api/health', async (req, res) => {
    try {
        res.json({
            status: 'healthy',
            version: '2.0.0',
            uptime: process.uptime(),
            timestamp: new Date().toISOString(),
            services: {
                'impact-validation': validationBridge ? 'active' : 'inactive',
                'passport-generator': passportGenerator ? 'active' : 'inactive',
                'simulation-router': simulationRouter ? 'active' : 'inactive'
            }
        });
    } catch (error) {
        res.status(500).json({
            status: 'unhealthy',
            error: error.message
        });
    }
});

// Sync organization data with BCM
app.put('/api/digital-twins/:id/sync', async (req, res) => {
    try {
        const organizationId = req.params.id;
        const syncData = req.body;

        console.log(` Syncing organization ${organizationId} with BCM data`);

        // Mock sync process - в реальности здесь будет обращение к базе данных
        const updatedConfig = {
            ...syncData.configuration || {},
            lastSync: new Date().toISOString(),
            bcmDataVersion: '2.0',
            syncStatus: 'completed'
        };

        // Simulate health score calculation
        const healthScore = Math.floor(Math.random() * 30) + 70; // 70-100

        res.json({
            success: true,
            updated_config: updatedConfig,
            health_score: healthScore,
            sync_timestamp: new Date().toISOString(),
            message: 'Data synchronized successfully'
        });

    } catch (error) {
        console.error(' Sync failed:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Get organization metrics for BCM
app.get('/api/digital-twins/:id/metrics', async (req, res) => {
    try {
        const organizationId = req.params.id;

        // Get metrics from real database
        let metrics = await database.getLatestMetrics(organizationId);

        // If no metrics found, generate and save initial metrics
        if (!metrics || Object.keys(metrics).length === 0) {
            metrics = {
                overall_health: Math.floor(Math.random() * 30) + 70,
                financial_health: Math.floor(Math.random() * 40) + 60,
                operational_efficiency: Math.floor(Math.random() * 35) + 65,
                technology_maturity: Math.floor(Math.random() * 25) + 75,
                compliance_score: Math.floor(Math.random() * 20) + 80,
                risk_level: Math.floor(Math.random() * 30) + 20
            };
            await database.saveMetrics(organizationId, metrics);
        }

        res.json({
            metrics,
            last_updated: new Date().toISOString(),
            data_freshness: 'real-time'
        });

    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get AI predictions for organization
app.get('/api/digital-twins/:id/predictions', async (req, res) => {
    try {
        const organizationId = req.params.id;
        const predictionType = req.query.type;

        // Mock AI predictions
        const basePredictions = [
            {
                type: 'financial',
                confidence: 0.87,
                prediction: 'Budget optimization could yield 15-20% savings in next quarter',
                impact: 'high',
                timeline: '3 months',
                recommendation: 'Implement automated expense tracking'
            },
            {
                type: 'operational',
                confidence: 0.92,
                prediction: 'Process automation will improve efficiency by 35%',
                impact: 'high',
                timeline: '6 months',
                recommendation: 'Start with document management automation'
            },
            {
                type: 'risk',
                confidence: 0.74,
                prediction: 'Cybersecurity risks may increase due to remote work',
                impact: 'medium',
                timeline: '1 month',
                recommendation: 'Enhanced security training for staff'
            }
        ];

        let predictions = basePredictions;
        if (predictionType) {
            predictions = basePredictions.filter(p => p.type === predictionType);
        }

        res.json({ predictions });

    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// AI Consultant Chat API
app.post('/api/ai-consultant/chat', async (req, res) => {
    try {
        const { message, context } = req.body;

        // Simulate AI response with BCM expertise
        const aiResponse = await generateAIConsultantResponse(message, context);

        res.json({
            success: true,
            response: aiResponse,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Generate AI consultant response
async function generateAIConsultantResponse(message, context) {
    // Analyze message for BCM keywords
    const lowerMessage = message.toLowerCase();

    if (lowerMessage.includes('риск') || lowerMessage.includes('risk')) {
        return {
            text: `Анализирую риски вашей организации...

На основе данных Digital Twin, я выявил следующие ключевые риски:
1. **Операционные риски** (35%) - связаны с зависимостью от ключевых поставщиков
2. **Кибер-риски** (28%) - требуется усиление защиты данных
3. **Финансовые риски** (20%) - волатильность доходов
4. **Репутационные риски** (17%) - необходим план кризисных коммуникаций

Рекомендую приоритизировать работу с операционными рисками и разработать альтернативные цепочки поставок.`,
            insights: {
                riskLevel: 35,
                priority: 'Операционные риски',
                recommendation: 'Разработка альтернативных поставщиков'
            }
        };
    } else if (lowerMessage.includes('готовность') || lowerMessage.includes('readiness')) {
        return {
            text: `Оценка готовности к кризисам показывает:

 **Сильные стороны:**
- Наличие базового плана BCM
- Обученная команда реагирования
- Резервные системы данных

️ **Области для улучшения:**
- Тестирование планов (последнее - 6 месяцев назад)
- Обновление контактов экстренной связи
- Интеграция с поставщиками

**Общий уровень готовности: 72%**
Рекомендую провести полномасштабные учения в следующем квартале.`,
            insights: {
                readinessScore: 72,
                nextSteps: 'Планирование учений',
                timeline: 'Q2 2025'
            }
        };
    } else if (lowerMessage.includes('план') || lowerMessage.includes('plan')) {
        return {
            text: `Создаю план восстановления для вашей организации:

** План восстановления бизнеса**

**1. Критические процессы (RTO < 4 часа):**
- Обработка платежей клиентов
- Системы безопасности
- Коммуникации с клиентами

**2. Важные процессы (RTO < 24 часа):**
- Внутренние коммуникации
- Финансовая отчетность
- Управление поставками

**3. Ресурсы восстановления:**
- Резервный офис: готов
- IT-инфраструктура: облачный backup
- Персонал: 85% может работать удаленно

**4. Контрольные точки:**
- T+1ч: Активация кризисной команды
- T+4ч: Восстановление критических систем
- T+24ч: Полное операционное восстановление`,
            insights: {
                rto: '4 часа',
                rpo: '1 час',
                readiness: 'Высокая'
            }
        };
    } else if (lowerMessage.includes('iso') || lowerMessage.includes('22301')) {
        return {
            text: `Проверка соответствия ISO 22301:

** Результаты аудита:**

 **Соответствует (78%):**
- Контекст организации
- Лидерство и обязательства
- Планирование BCM
- Документированная информация

️ **Частично соответствует (15%):**
- Оценка эффективности
- Внутренний аудит

 **Требует доработки (7%):**
- Непрерывное улучшение
- Метрики производительности

**Рекомендации для сертификации:**
1. Внедрить KPI для BCM процессов
2. Провести внутренний аудит до конца квартала
3. Документировать уроки последних инцидентов

**Готовность к сертификации: 78%**`,
            insights: {
                compliance: 78,
                gaps: 3,
                timeline: '3-4 месяца до полной готовности'
            }
        };
    } else {
        // Default intelligent response
        return {
            text: `Понял ваш вопрос: "${message}"

Анализирую данные вашей организации через Digital Twin...

На основе текущих метрик:
- Общее здоровье организации: 85%
- Уровень риска: Умеренный (35%)
- Готовность к кризисам: Хорошая

Могу предоставить детальный анализ по следующим направлениям:
-  Анализ рисков
- ️ Оценка готовности
-  Планы восстановления
-  Соответствие ISO 22301

Что именно вас интересует?`,
            insights: {
                healthScore: 85,
                riskLevel: 35,
                suggestion: 'Выберите область для углубленного анализа'
            }
        };
    }
}

// Advanced BCM Business Scenarios API
app.post('/api/bcm/scenarios/business-continuity', async (req, res) => {
    try {
        const { scenarioType, organizationData, parameters } = req.body;

        console.log(` Running BCM scenario: ${scenarioType}`);

        // Advanced business continuity scenario simulation
        const scenarioResults = await runBCMScenarioSimulation(scenarioType, organizationData, parameters);

        res.json({
            success: true,
            scenario: scenarioType,
            results: scenarioResults,
            timestamp: new Date().toISOString(),
            confidence: scenarioResults.confidence || 85
        });

    } catch (error) {
        console.error(' BCM scenario failed:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Crisis Response Planning Simulation
app.post('/api/bcm/scenarios/crisis-response', async (req, res) => {
    try {
        const { crisisType, severity, timeline, organizationProfile } = req.body;

        const crisisResults = simulateCrisisResponse(crisisType, severity, timeline, organizationProfile);

        res.json({
            success: true,
            crisisType,
            severity,
            results: crisisResults,
            timestamp: new Date().toISOString()
        });

    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Risk Scenario Monte Carlo Simulation
app.post('/api/bcm/scenarios/monte-carlo-risk', async (req, res) => {
    try {
        const { riskFactors, simulationRuns, timeHorizon } = req.body;

        const monteCarloResults = runMonteCarloRiskSimulation(riskFactors, simulationRuns || 10000, timeHorizon || 12);

        res.json({
            success: true,
            simulationRuns,
            results: monteCarloResults,
            timestamp: new Date().toISOString()
        });

    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Compliance Gap Analysis
app.post('/api/bcm/scenarios/compliance-gap-analysis', async (req, res) => {
    try {
        const { framework, currentState, targetState } = req.body;

        const gapAnalysis = performComplianceGapAnalysis(framework || 'ISO22301', currentState, targetState);

        res.json({
            success: true,
            framework,
            analysis: gapAnalysis,
            timestamp: new Date().toISOString()
        });

    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Advanced scenario simulation functions
async function runBCMScenarioSimulation(scenarioType, orgData, params) {
    const scenarioLogic = {
        'supply_chain_disruption': () => simulateSupplyChainDisruption(orgData, params),
        'cyber_incident': () => simulateCyberIncident(orgData, params),
        'pandemic_response': () => simulatePandemicResponse(orgData, params),
        'natural_disaster': () => simulateNaturalDisaster(orgData, params),
        'key_personnel_loss': () => simulateKeyPersonnelLoss(orgData, params),
        'technology_failure': () => simulateTechnologyFailure(orgData, params),
        'regulatory_change': () => simulateRegulatoryChange(orgData, params)
    };

    const simulator = scenarioLogic[scenarioType];
    if (!simulator) {
        throw new Error(`Unknown scenario type: ${scenarioType}`);
    }

    return simulator();
}

function simulateSupplyChainDisruption(orgData, params) {
    const disruptionSeverity = params.severity || 0.7;
    const recoveryTime = params.recoveryTimeWeeks || 8;
    const alternativeSuppliers = params.alternativeSuppliers || 2;

    // Calculate impact metrics
    const operationalImpact = disruptionSeverity * (1 - (alternativeSuppliers * 0.1));
    const financialImpact = orgData.annualBudget * operationalImpact * (recoveryTime / 52);
    const reputationImpact = Math.min(0.9, operationalImpact * 1.2);

    // Recovery strategies
    const recoveryStrategies = [
        { strategy: 'Emergency supplier activation', effectiveness: 0.6, cost: financialImpact * 0.15 },
        { strategy: 'Internal production scaling', effectiveness: 0.4, cost: financialImpact * 0.25 },
        { strategy: 'Alternative logistics routes', effectiveness: 0.3, cost: financialImpact * 0.1 }
    ];

    return {
        impact: {
            operational: Math.round(operationalImpact * 100),
            financial: Math.round(financialImpact),
            reputation: Math.round(reputationImpact * 100),
            recovery_weeks: recoveryTime
        },
        strategies: recoveryStrategies,
        recommendations: [
            'Diversify supplier base to reduce single points of failure',
            'Establish strategic supplier partnerships with guaranteed capacity',
            'Implement supply chain monitoring and early warning systems'
        ],
        confidence: 87
    };
}

function simulateCyberIncident(orgData, params) {
    const incidentType = params.incidentType || 'ransomware';
    const systemsAffected = params.systemsAffected || 0.6;
    const recoveryComplexity = params.recoveryComplexity || 'high';

    const downtime = {
        'low': 24,
        'medium': 72,
        'high': 168
    }[recoveryComplexity];

    const financialImpact = (orgData.annualBudget / 365) * (downtime / 24) * systemsAffected;
    const dataLoss = systemsAffected * 0.1; // 10% of affected systems lose data
    const complianceImpact = incidentType === 'data_breach' ? 0.8 : 0.3;

    return {
        impact: {
            downtime_hours: downtime,
            financial_loss: Math.round(financialImpact),
            systems_affected: Math.round(systemsAffected * 100),
            data_loss_percentage: Math.round(dataLoss * 100),
            compliance_risk: Math.round(complianceImpact * 100)
        },
        recovery_phases: [
            { phase: 'Immediate Response', duration: '0-4 hours', actions: ['Incident containment', 'Stakeholder notification'] },
            { phase: 'Assessment', duration: '4-24 hours', actions: ['Damage assessment', 'Recovery planning'] },
            { phase: 'Recovery', duration: '1-7 days', actions: ['System restoration', 'Data recovery'] },
            { phase: 'Lessons Learned', duration: '1-2 weeks', actions: ['Post-incident review', 'Control improvements'] }
        ],
        recommendations: [
            'Implement zero-trust security architecture',
            'Regular backup testing and validation',
            'Comprehensive incident response training',
            'Cyber insurance coverage review'
        ],
        confidence: 92
    };
}

function simulatePandemicResponse(orgData, params) {
    const remoteWorkCapacity = params.remoteWorkCapacity || 0.7;
    const pandemicDuration = params.durationMonths || 18;
    const staffAvailability = params.staffAvailability || 0.8;

    const productivityImpact = (1 - remoteWorkCapacity) * (1 - staffAvailability);
    const operationalContinuity = 1 - productivityImpact;
    const additionalCosts = orgData.annualBudget * 0.15; // 15% increase for remote work setup

    return {
        impact: {
            operational_continuity: Math.round(operationalContinuity * 100),
            productivity_change: Math.round((productivityImpact - 1) * 100),
            additional_costs: Math.round(additionalCosts),
            staff_availability: Math.round(staffAvailability * 100)
        },
        adaptation_measures: [
            { measure: 'Remote work technology deployment', effectiveness: 85, cost: additionalCosts * 0.4 },
            { measure: 'Digital collaboration tools', effectiveness: 75, cost: additionalCosts * 0.2 },
            { measure: 'Staff health and safety protocols', effectiveness: 90, cost: additionalCosts * 0.3 },
            { measure: 'Supply chain diversification', effectiveness: 70, cost: additionalCosts * 0.1 }
        ],
        lessons_learned: [
            'Invest in robust remote work infrastructure',
            'Develop digital-first business processes',
            'Build organizational resilience and agility',
            'Strengthen crisis communication capabilities'
        ],
        confidence: 89
    };
}

function simulateCrisisResponse(crisisType, severity, timeline, orgProfile) {
    const crisisModifiers = {
        'financial': { recoveryTime: 1.5, stakeholderImpact: 1.2, operationalImpact: 0.8 },
        'operational': { recoveryTime: 1.0, stakeholderImpact: 0.8, operationalImpact: 1.5 },
        'reputational': { recoveryTime: 2.0, stakeholderImpact: 1.8, operationalImpact: 0.6 },
        'regulatory': { recoveryTime: 1.8, stakeholderImpact: 1.4, operationalImpact: 1.1 }
    };

    const modifier = crisisModifiers[crisisType] || crisisModifiers['operational'];

    return {
        response_timeline: {
            immediate: '0-4 hours',
            short_term: '4-24 hours',
            medium_term: '1-7 days',
            long_term: '1-4 weeks'
        },
        impact_assessment: {
            severity_score: severity * 100,
            estimated_recovery: Math.round(timeline * modifier.recoveryTime),
            stakeholder_impact: Math.round(severity * modifier.stakeholderImpact * 100),
            operational_impact: Math.round(severity * modifier.operationalImpact * 100)
        },
        response_actions: generateCrisisResponseActions(crisisType, severity),
        success_metrics: [
            'Response time to initial crisis notification',
            'Stakeholder communication effectiveness',
            'Operational continuity maintenance',
            'Financial impact minimization'
        ]
    };
}

function runMonteCarloRiskSimulation(riskFactors, runs, timeHorizon) {
    const simulations = [];

    for (let i = 0; i < runs; i++) {
        let totalRisk = 0;

        riskFactors.forEach(factor => {
            const probability = Math.random();
            const impact = factor.minImpact + Math.random() * (factor.maxImpact - factor.minImpact);

            if (probability <= factor.probability) {
                totalRisk += impact;
            }
        });

        simulations.push(totalRisk);
    }

    simulations.sort((a, b) => a - b);

    const percentile = (p) => simulations[Math.floor(runs * p / 100)];

    return {
        statistics: {
            mean: simulations.reduce((a, b) => a + b) / runs,
            median: percentile(50),
            p95: percentile(95),
            p99: percentile(99),
            max: Math.max(...simulations)
        },
        risk_distribution: {
            low_risk: simulations.filter(s => s < percentile(25)).length / runs * 100,
            medium_risk: simulations.filter(s => s >= percentile(25) && s < percentile(75)).length / runs * 100,
            high_risk: simulations.filter(s => s >= percentile(75)).length / runs * 100
        },
        recommendations: generateRiskRecommendations(percentile(95))
    };
}

function performComplianceGapAnalysis(framework, currentState, targetState) {
    const frameworkControls = {
        'ISO22301': [
            'Context of organization', 'Leadership', 'Planning', 'Support',
            'Operation', 'Performance evaluation', 'Improvement'
        ]
    };

    const controls = frameworkControls[framework] || frameworkControls['ISO22301'];
    const gaps = [];

    controls.forEach((control, index) => {
        const current = currentState?.[index] || Math.random() * 100;
        const target = targetState?.[index] || 95;

        if (current < target) {
            gaps.push({
                control: control,
                current_score: Math.round(current),
                target_score: target,
                gap: Math.round(target - current),
                priority: target - current > 20 ? 'High' : target - current > 10 ? 'Medium' : 'Low'
            });
        }
    });

    return {
        overall_compliance: Math.round(gaps.reduce((sum, gap) => sum + gap.current_score, 0) / gaps.length),
        target_compliance: 95,
        gaps: gaps.sort((a, b) => b.gap - a.gap),
        improvement_plan: generateImprovementPlan(gaps)
    };
}

function generateCrisisResponseActions(crisisType, severity) {
    const baseActions = [
        'Activate crisis management team',
        'Assess situation and gather information',
        'Communicate with key stakeholders',
        'Implement business continuity plans'
    ];

    const specificActions = {
        'financial': ['Engage financial advisors', 'Review cash flow', 'Contact creditors'],
        'operational': ['Assess operational capacity', 'Activate backup systems', 'Coordinate with suppliers'],
        'reputational': ['Prepare public statements', 'Monitor social media', 'Engage PR specialists'],
        'regulatory': ['Contact legal counsel', 'Review compliance status', 'Prepare regulatory reports']
    };

    return [...baseActions, ...(specificActions[crisisType] || [])];
}

function generateRiskRecommendations(riskScore) {
    if (riskScore > 80) {
        return [
            'Immediate risk mitigation required',
            'Consider risk transfer mechanisms',
            'Develop comprehensive contingency plans',
            'Increase monitoring and early warning systems'
        ];
    } else if (riskScore > 50) {
        return [
            'Moderate risk management needed',
            'Regular risk assessment updates',
            'Improve existing controls',
            'Consider additional risk mitigation'
        ];
    } else {
        return [
            'Current risk levels acceptable',
            'Continue regular monitoring',
            'Maintain existing controls',
            'Periodic risk assessment reviews'
        ];
    }
}

function generateImprovementPlan(gaps) {
    return gaps.slice(0, 5).map((gap, index) => ({
        priority: index + 1,
        control: gap.control,
        action: `Improve ${gap.control.toLowerCase()} implementation`,
        timeline: gap.priority === 'High' ? '3 months' : gap.priority === 'Medium' ? '6 months' : '12 months',
        resources_required: gap.priority === 'High' ? 'Significant' : 'Moderate'
    }));
}

// ===== DIGITAL COPY (SNAPSHOTS) ENDPOINTS =====

// Create snapshot of Digital Twin
app.post('/api/digital-twins/:id/snapshots', async (req, res) => {
    try {
        const twinId = req.params.id;
        const { name, description } = req.body;

        const snapshot = await odooBridge.createSnapshot(twinId, name, description);

        res.status(201).json({
            success: true,
            data: {
                id: snapshot,
                twin_id: twinId,
                name: name,
                description: description,
                created_at: new Date().toISOString()
            },
            message: 'Snapshot created successfully'
        });
    } catch (error) {
        console.error('Error creating snapshot:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Get snapshots for Digital Twin
app.get('/api/digital-twins/:id/snapshots', async (req, res) => {
    try {
        const twinId = req.params.id;
        const snapshots = await odooBridge.getSnapshots(twinId);

        res.json({
            success: true,
            data: snapshots,
            meta: {
                count: snapshots.length,
                twin_id: twinId
            }
        });
    } catch (error) {
        console.error('Error getting snapshots:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Restore Digital Twin from snapshot
app.post('/api/snapshots/:id/restore', async (req, res) => {
    try {
        const snapshotId = req.params.id;
        await odooBridge.restoreFromSnapshot(snapshotId);

        res.json({
            success: true,
            message: 'Digital Twin restored from snapshot successfully',
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error('Error restoring from snapshot:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// ===== AI CONSULTANT ENDPOINTS =====

// Enhanced AI Consultant chat with Odoo integration
app.post('/api/ai-consultant/chat', async (req, res) => {
    try {
        const { message, sessionId, organizationId } = req.body;

        if (!message) {
            return res.status(400).json({
                success: false,
                error: 'Message is required'
            });
        }

        // Try Odoo AI consultant first
        try {
            const context = {
                sessionId: sessionId,
                organizationId: organizationId,
                timestamp: new Date().toISOString()
            };

            const aiResponse = await odooBridge.sendMessageToAI(message, context);

            res.json({
                success: true,
                data: {
                    message: aiResponse.response,
                    sessionId: aiResponse.sessionId,
                    recommendations: aiResponse.recommendations,
                    source: 'odoo_ai_consultant',
                    timestamp: new Date().toISOString()
                }
            });
        } catch (odooError) {
            console.log('Odoo AI consultant unavailable, using fallback:', odooError.message);

            // Fallback to existing AI logic
            const aiResponse = await generateAIConsultantResponse(message, { organizationId });

            res.json({
                success: true,
                data: {
                    message: aiResponse,
                    source: 'fallback_ai',
                    timestamp: new Date().toISOString()
                }
            });
        }
    } catch (error) {
        console.error('Error in AI consultant:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Get AI Organs status from Odoo
app.get('/api/ai-organs/status', async (req, res) => {
    try {
        const organs = await odooBridge.getAIOrganStatus();

        res.json({
            success: true,
            data: organs,
            meta: {
                count: organs.length,
                last_updated: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('Error getting AI organs status:', error);

        // Fallback to mock data
        const mockOrgans = [
            { name: 'Governance Brain', status: 'active', health: 95 },
            { name: 'Risk Advisor', status: 'active', health: 87 },
            { name: 'Impact Oracle', status: 'warning', health: 72 },
            { name: 'Scenario Creator', status: 'active', health: 91 },
            { name: 'Emergency Response', status: 'active', health: 89 }
        ];

        res.json({
            success: true,
            data: mockOrgans,
            source: 'fallback',
            meta: {
                count: mockOrgans.length,
                last_updated: new Date().toISOString()
            }
        });
    }
});

// Run simulation through Odoo
app.post('/api/simulations/odoo', async (req, res) => {
    try {
        const { twinId, scenario } = req.body;

        if (!twinId || !scenario) {
            return res.status(400).json({
                success: false,
                error: 'twinId and scenario are required'
            });
        }

        const result = await odooBridge.runSimulation(twinId, scenario);

        res.json({
            success: true,
            data: result,
            meta: {
                twin_id: twinId,
                scenario_type: scenario.type || 'unknown',
                timestamp: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('Error running Odoo simulation:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Health check for Odoo integration
app.get('/api/odoo/health', async (req, res) => {
    try {
        const healthStatus = await odooBridge.healthCheck();
        const systemInfo = await odooBridge.getSystemInfo();

        res.json({
            success: true,
            odoo_status: healthStatus,
            system_info: systemInfo,
            integration_mode: process.env.INTEGRATION_MODE || 'hybrid',
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message,
            odoo_status: 'unhealthy'
        });
    }
});

// Start server with database connection
async function startServer() {
    try {
        // Connect to database
        const dbConnected = await database.connect();

        app.listen(PORT, () => {
            console.log(`
╔═══════════════════════════════════════════╗
║   Digital Twin Server Started!            ║
║                                           ║
║   URL: http://localhost:${PORT}               ║
║   API: http://localhost:${PORT}/api           ║
║   Database: ${dbConnected ? ' Connected' : '️ In-Memory'}    ║
║                                           ║
║   Press Ctrl+C to stop                   ║
╚═══════════════════════════════════════════╝
    `);
        });
    } catch (error) {
        console.error('Failed to start server:', error);
        process.exit(1);
    }
}

startServer();