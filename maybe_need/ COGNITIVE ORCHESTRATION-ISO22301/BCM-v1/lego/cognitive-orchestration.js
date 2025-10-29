const SystemOrchestrator = require('./ORCHESTRATORS/system-orchestrator');
const BridgeOrchestrator = require('./ORCHESTRATORS/bridge-orchestrator');
const ProgramOrchestrator = require('./ORCHESTRATORS/program-orchestrator');
const ClientOrchestrator = require('./ORCHESTRATORS/client-orchestrator');
const SandboxOrchestrator = require('./ORCHESTRATORS/sandbox-orchestrator');

class CognitiveOrchestration {
    constructor(config = {}) {
        this.config = config;
        this.orchestrators = new Map();
        this.status = 'initialized';
        this.metrics = {
            totalRequests: 0,
            successfulRequests: 0,
            failedRequests: 0,
            averageResponseTime: 0,
            systemUptime: 0
        };
        this.startTime = Date.now();
        this.requestHistory = [];

        this.initializeOrchestrators();
        this.setupEventRouting();
    }

    initializeOrchestrators() {
        console.log('🏗️  Инициализация Cognitive Orchestration System...\n');

        this.orchestrators.set('system', new SystemOrchestrator(this.config.system || {}));
        this.orchestrators.set('bridge', new BridgeOrchestrator(this.config.bridge || {}));
        this.orchestrators.set('program', new ProgramOrchestrator(this.config.program || {}));
        this.orchestrators.set('client', new ClientOrchestrator(this.config.client || {}));
        this.orchestrators.set('sandbox', new SandboxOrchestrator(this.config.sandbox || {}));

        console.log('✅ Все оркестраторы созданы');
    }

    setupEventRouting() {
        const system = this.orchestrators.get('system');
        const bridge = this.orchestrators.get('bridge');
        const program = this.orchestrators.get('program');
        const client = this.orchestrators.get('client');
        const sandbox = this.orchestrators.get('sandbox');

        system.subscribe(bridge);
        bridge.subscribe(program);
        client.subscribe(system);

        sandbox.on('experiment-completed', (experiment, result) => {
            if (result.success && result.improvement > 1.2) {
                console.log(`🧪 Эксперимент ${experiment.id} показал улучшение ${result.improvement}x`);
                this.applyOptimization(result);
            }
        });

        console.log('✅ Маршрутизация событий настроена');
    }

    async start() {
        console.log('\n🚀 Запуск Cognitive Orchestration System...\n');

        try {
            for (const [name, orchestrator] of this.orchestrators) {
                console.log(`Инициализация ${name} orchestrator...`);
                await orchestrator.initialize();
                console.log(`✅ ${name} готов\n`);
            }

            this.status = 'running';
            console.log('🎉 Cognitive Orchestration System запущена!\n');

            this.startMetricsCollection();
            this.startHealthMonitoring();

            return true;

        } catch (error) {
            console.error('❌ Ошибка запуска системы:', error);
            this.status = 'failed';
            throw error;
        }
    }

    async handle(request, context = {}) {
        const startTime = Date.now();
        const requestId = this.generateRequestId();

        this.metrics.totalRequests++;

        try {
            request.id = requestId;
            request.timestamp = startTime;

            let result;

            switch (request.level || this.determineLevel(request)) {
                case 'client':
                    result = await this.orchestrators.get('client').handle(request, context);
                    break;

                case 'system':
                    result = await this.orchestrators.get('system').handle(request, context);
                    break;

                case 'bridge':
                    result = await this.orchestrators.get('bridge').handle(request, context);
                    break;

                case 'program':
                    result = await this.orchestrators.get('program').handle(request, context);
                    break;

                case 'sandbox':
                    result = await this.orchestrators.get('sandbox').handle(request, context);
                    break;

                default:
                    result = await this.handleGenericRequest(request, context);
            }

            const duration = Date.now() - startTime;
            this.updateMetrics(true, duration);

            this.requestHistory.push({
                requestId,
                level: request.level,
                type: request.type,
                success: true,
                duration,
                timestamp: startTime
            });

            return {
                success: true,
                requestId,
                result,
                duration,
                processedBy: request.level || 'auto'
            };

        } catch (error) {
            const duration = Date.now() - startTime;
            this.updateMetrics(false, duration);

            this.requestHistory.push({
                requestId,
                level: request.level,
                type: request.type,
                success: false,
                error: error.message,
                duration,
                timestamp: startTime
            });

            throw error;
        }
    }

    determineLevel(request) {
        if (request.type === 'authenticate' || request.type === 'authorize') {
            return 'client';
        }

        if (request.type === 'experiment' || request.type === 'evolve' || request.type === 'optimize') {
            return 'sandbox';
        }

        if (request.type === 'business-logic' || request.module || request.domain) {
            return 'program';
        }

        if (request.type === 'translate' || request.from || request.to) {
            return 'bridge';
        }

        return 'system';
    }

    async handleGenericRequest(request, context) {
        console.log(`🔄 Автоматическая обработка запроса: ${request.type}`);

        if (request.type === 'health-check') {
            return await this.getSystemHealth();
        }

        if (request.type === 'metrics') {
            return this.getMetrics();
        }

        if (request.type === 'status') {
            return this.getSystemStatus();
        }

        return await this.orchestrators.get('system').handle(request, context);
    }

    async getSystemHealth() {
        const health = {
            status: this.status,
            uptime: Date.now() - this.startTime,
            orchestrators: {},
            overall: 'healthy'
        };

        for (const [name, orchestrator] of this.orchestrators) {
            try {
                health.orchestrators[name] = await orchestrator.getHealthStatus();
            } catch (error) {
                health.orchestrators[name] = { status: 'error', error: error.message };
                health.overall = 'degraded';
            }
        }

        return health;
    }

    getMetrics() {
        return {
            ...this.metrics,
            uptime: Date.now() - this.startTime,
            orchestrators: Array.from(this.orchestrators.keys()),
            recentRequests: this.requestHistory.slice(-10)
        };
    }

    getSystemStatus() {
        return {
            status: this.status,
            orchestrators: this.orchestrators.size,
            uptime: Date.now() - this.startTime,
            version: '1.0.0',
            architecture: 'parallel-orchestrators',
            domain: 'universal'
        };
    }

    startMetricsCollection() {
        setInterval(() => {
            this.metrics.systemUptime = Date.now() - this.startTime;

            for (const orchestrator of this.orchestrators.values()) {
                orchestrator.emit('metrics.collect');
            }

        }, 60000);
    }

    startHealthMonitoring() {
        setInterval(async () => {
            try {
                const health = await this.getSystemHealth();

                if (health.overall === 'degraded') {
                    console.log('⚠️  Обнаружены проблемы со здоровьем системы');
                    await this.performSelfHealing();
                }

            } catch (error) {
                console.error('❌ Ошибка мониторинга:', error);
            }
        }, 30000);
    }

    async performSelfHealing() {
        console.log('🔧 Попытка самовосстановления...');

        for (const [name, orchestrator] of this.orchestrators) {
            try {
                const health = await orchestrator.getHealthStatus();

                if (health.status === 'error' || health.status === 'degraded') {
                    console.log(`🔄 Перезапуск ${name} orchestrator...`);
                    await orchestrator.initialize();
                }

            } catch (error) {
                console.error(`❌ Не удалось восстановить ${name}:`, error);
            }
        }
    }

    async createExperiment(code, config = {}) {
        return await this.orchestrators.get('sandbox').handle({
            type: 'create-experiment',
            code,
            ...config
        });
    }

    async evolveComponent(component, parameters = {}) {
        return await this.orchestrators.get('sandbox').handle({
            type: 'evolve-component',
            component,
            ...parameters
        });
    }

    async executeBusinessLogic(domain, module, action, data, context = {}) {
        return await this.orchestrators.get('program').handle({
            type: 'business-logic',
            domain,
            module,
            action,
            data
        }, context);
    }

    async authenticateUser(credentials) {
        return await this.orchestrators.get('client').handle({
            type: 'authenticate',
            credentials
        });
    }

    async optimizeSystem() {
        const results = [];

        for (const [name, orchestrator] of this.orchestrators) {
            try {
                const optimization = await this.orchestrators.get('sandbox').handle({
                    type: 'optimize-code',
                    target: name,
                    optimizationType: 'performance'
                });

                results.push({ orchestrator: name, optimization });

            } catch (error) {
                results.push({ orchestrator: name, error: error.message });
            }
        }

        return results;
    }

    applyOptimization(optimizationResult) {
        console.log(`🚀 Применяю оптимизацию: ${optimizationResult.type}`);
    }

    updateMetrics(success, duration) {
        if (success) {
            this.metrics.successfulRequests++;
        } else {
            this.metrics.failedRequests++;
        }

        const totalRequests = this.metrics.totalRequests;
        this.metrics.averageResponseTime =
            ((this.metrics.averageResponseTime * (totalRequests - 1)) + duration) / totalRequests;
    }

    generateRequestId() {
        return `co-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    async shutdown() {
        console.log('\n🛑 Остановка Cognitive Orchestration System...');

        this.status = 'shutting_down';

        for (const [name, orchestrator] of this.orchestrators) {
            try {
                console.log(`Остановка ${name}...`);
                await orchestrator.shutdown();
            } catch (error) {
                console.error(`Ошибка остановки ${name}:`, error);
            }
        }

        this.status = 'stopped';
        console.log('✅ Cognitive Orchestration System остановлена');
    }
}

async function createCognitiveOrchestration(config = {}) {
    const system = new CognitiveOrchestration(config);
    await system.start();
    return system;
}

if (require.main === module) {
    (async () => {
        try {
            console.log('🌟 Запуск демонстрации Cognitive Orchestration\n');

            const system = await createCognitiveOrchestration({
                client: { maxConcurrentRequests: 100 },
                sandbox: { maxConcurrentExperiments: 3 }
            });

            console.log('\n🧪 Тестирование различных типов запросов...\n');

            const results = await Promise.all([
                system.handle({ type: 'health-check' }),
                system.handle({ type: 'metrics' }),
                system.executeBusinessLogic('bcm', 'risk-assessment', 'assess', { riskId: 'test-001' }),
                system.authenticateUser({ username: 'demo', password: 'demo' }),
                system.createExperiment('console.log("Hello from experiment!");', { autoRun: false })
            ]);

            console.log('✅ Все тесты выполнены успешно!');

            results.forEach((result, i) => {
                console.log(`   ${i + 1}. ${result.success ? '✅' : '❌'} ${result.processedBy || 'unknown'} (${result.duration}ms)`);
            });

            const finalHealth = await system.getSystemHealth();
            console.log(`\n📊 Финальное состояние: ${finalHealth.overall}`);
            console.log(`🕐 Время работы: ${Math.round(finalHealth.uptime / 1000)}s`);

            await system.shutdown();

        } catch (error) {
            console.error('❌ Ошибка демонстрации:', error);
            process.exit(1);
        }
    })();
}

module.exports = { CognitiveOrchestration, createCognitiveOrchestration };