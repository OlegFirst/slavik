"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DigitalOfficeHub = void 0;
const index_js_1 = require("@modelcontextprotocol/sdk/server/index.js");
const stdio_js_1 = require("@modelcontextprotocol/sdk/server/stdio.js");
const types_js_1 = require("@modelcontextprotocol/sdk/types.js");
const ServiceRegistry_1 = require("./ServiceRegistry");
const AgentRegistry_1 = require("./AgentRegistry");
const AgentScheduler_1 = require("./AgentScheduler");
const AgentLoader_1 = require("./AgentLoader");
const EventBus_1 = require("./EventBus");
const DataStore_1 = require("./DataStore");
const ResourceManager_1 = require("./ResourceManager");
class DigitalOfficeHub {
    constructor() {
        this.hubTools = [];
        this.server = new index_js_1.Server({
            name: 'digital-office',
            version: '1.0.0',
        }, {
            capabilities: {
                tools: {},
            },
        });
        this.serviceRegistry = new ServiceRegistry_1.ServiceRegistry();
        this.agentScheduler = new AgentScheduler_1.AgentScheduler();
        this.agentRegistry = new AgentRegistry_1.AgentRegistry(this.agentScheduler);
        this.agentLoader = new AgentLoader_1.AgentLoader('./src/agents', this.agentRegistry);
        this.eventBus = EventBus_1.EventBus.getInstance();
        this.dataStore = DataStore_1.DataStore.getInstance();
        this.resourceManager = ResourceManager_1.ResourceManager.getInstance();
        // Встановлюємо зв'язок з ResourceManager
        this.resourceManager.setServiceRegistry(this.serviceRegistry);
        this.setupHubTools();
        this.setupToolHandlers();
    }
    setupHubTools() {
        this.hubTools = [
            {
                name: 'list_services',
                description: 'Показує список всіх сервісів та їх статуси',
                inputSchema: {
                    type: 'object',
                    properties: {
                        filter: {
                            type: 'string',
                            enum: ['all', 'enabled', 'running', 'disabled'],
                            description: 'Фільтр для відображення сервісів',
                            default: 'all'
                        }
                    }
                },
            },
            {
                name: 'service_status',
                description: 'Отримує детальний статус конкретного сервісу',
                inputSchema: {
                    type: 'object',
                    properties: {
                        serviceName: {
                            type: 'string',
                            description: 'Назва сервісу для перевірки статусу',
                        },
                    },
                    required: ['serviceName'],
                },
            },
            {
                name: 'enable_service',
                description: 'Вмикає сервіс',
                inputSchema: {
                    type: 'object',
                    properties: {
                        serviceName: {
                            type: 'string',
                            description: 'Назва сервісу для включення',
                        },
                    },
                    required: ['serviceName'],
                },
            },
            {
                name: 'disable_service',
                description: 'Вимикає сервіс',
                inputSchema: {
                    type: 'object',
                    properties: {
                        serviceName: {
                            type: 'string',
                            description: 'Назва сервісу для відключення',
                        },
                    },
                    required: ['serviceName'],
                },
            },
            {
                name: 'start_service',
                description: 'Запускає сервіс',
                inputSchema: {
                    type: 'object',
                    properties: {
                        serviceName: {
                            type: 'string',
                            description: 'Назва сервісу для запуску',
                        },
                    },
                    required: ['serviceName'],
                },
            },
            {
                name: 'stop_service',
                description: 'Зупиняє сервіс',
                inputSchema: {
                    type: 'object',
                    properties: {
                        serviceName: {
                            type: 'string',
                            description: 'Назва сервісу для зупинки',
                        },
                    },
                    required: ['serviceName'],
                },
            },
            {
                name: 'health_check',
                description: 'Виконує перевірку здоров\'я всіх запущених сервісів',
                inputSchema: {
                    type: 'object',
                    properties: {},
                },
            },
            {
                name: 'list_agents',
                description: 'Показує список всіх автономних агентів та їх статуси',
                inputSchema: {
                    type: 'object',
                    properties: {
                        filter: {
                            type: 'string',
                            enum: ['all', 'running', 'enabled', 'disabled'],
                            description: 'Фільтр для відображення агентів',
                            default: 'all'
                        }
                    }
                },
            },
            {
                name: 'agent_status',
                description: 'Отримує детальний статус конкретного агента',
                inputSchema: {
                    type: 'object',
                    properties: {
                        agentName: {
                            type: 'string',
                            description: 'Назва агента для перевірки статусу',
                        },
                    },
                    required: ['agentName'],
                },
            },
            {
                name: 'enable_agent',
                description: 'Вмикає автономного агента',
                inputSchema: {
                    type: 'object',
                    properties: {
                        agentName: {
                            type: 'string',
                            description: 'Назва агента для включення',
                        },
                    },
                    required: ['agentName'],
                },
            },
            {
                name: 'disable_agent',
                description: 'Вимикає автономного агента',
                inputSchema: {
                    type: 'object',
                    properties: {
                        agentName: {
                            type: 'string',
                            description: 'Назва агента для відключення',
                        },
                    },
                    required: ['agentName'],
                },
            },
            {
                name: 'pause_agent',
                description: 'Призупиняє виконання автономного агента',
                inputSchema: {
                    type: 'object',
                    properties: {
                        agentName: {
                            type: 'string',
                            description: 'Назва агента для призупинення',
                        },
                    },
                    required: ['agentName'],
                },
            },
            {
                name: 'resume_agent',
                description: 'Відновлює виконання автономного агента',
                inputSchema: {
                    type: 'object',
                    properties: {
                        agentName: {
                            type: 'string',
                            description: 'Назва агента для відновлення',
                        },
                    },
                    required: ['agentName'],
                },
            },
            {
                name: 'execute_agent',
                description: 'Виконує агента вручну (одноразово)',
                inputSchema: {
                    type: 'object',
                    properties: {
                        agentName: {
                            type: 'string',
                            description: 'Назва агента для виконання',
                        },
                    },
                    required: ['agentName'],
                },
            },
            {
                name: 'agent_health_check',
                description: 'Виконує перевірку здоров\'я всіх автономних агентів',
                inputSchema: {
                    type: 'object',
                    properties: {},
                },
            },
        ];
    }
    setupToolHandlers() {
        this.server.setRequestHandler(types_js_1.ListToolsRequestSchema, async () => {
            const allTools = [];
            // Додаємо інструменти хабу
            allTools.push(...this.hubTools);
            // Додаємо інструменти з усіх запущених сервісів
            const runningServices = this.serviceRegistry.getRunningServices();
            for (const service of runningServices) {
                const serviceTools = service.getTools();
                // Додаємо префікс сервісу до назв інструментів для унікальності
                const prefixedTools = serviceTools.map(tool => ({
                    ...tool,
                    name: `${service.metadata.name}:${tool.name}`,
                    description: `[${service.metadata.name}] ${tool.description}`
                }));
                allTools.push(...prefixedTools);
            }
            return { tools: allTools };
        });
        this.server.setRequestHandler(types_js_1.CallToolRequestSchema, async (request) => {
            const toolName = request.params.name;
            // Перевіряємо, чи це команда хабу
            if (this.hubTools.some(tool => tool.name === toolName)) {
                return this.handleHubToolCall(toolName, request.params.arguments);
            }
            // Перевіряємо, чи це команда сервісу (з префіксом)
            if (toolName.includes(':')) {
                const [serviceName, serviceToolName] = toolName.split(':', 2);
                const service = this.serviceRegistry.getService(serviceName);
                if (!service) {
                    throw new Error(`Сервіс ${serviceName} не знайдено або не запущено`);
                }
                const status = this.serviceRegistry.getServiceStatus(serviceName);
                if (!status?.running) {
                    throw new Error(`Сервіс ${serviceName} не запущено`);
                }
                return service.handleToolCall(serviceToolName, request.params.arguments);
            }
            throw new Error(`Невідомий інструмент: ${toolName}`);
        });
    }
    async handleHubToolCall(toolName, args) {
        try {
            switch (toolName) {
                case 'list_services':
                    return this.handleListServices(args);
                case 'service_status':
                    return this.handleServiceStatus(args);
                case 'enable_service':
                    return this.handleEnableService(args);
                case 'disable_service':
                    return this.handleDisableService(args);
                case 'start_service':
                    return this.handleStartService(args);
                case 'stop_service':
                    return this.handleStopService(args);
                case 'health_check':
                    return this.handleHealthCheck(args);
                case 'list_agents':
                    return this.handleListAgents(args);
                case 'agent_status':
                    return this.handleAgentStatus(args);
                case 'enable_agent':
                    return this.handleEnableAgent(args);
                case 'disable_agent':
                    return this.handleDisableAgent(args);
                case 'pause_agent':
                    return this.handlePauseAgent(args);
                case 'resume_agent':
                    return this.handleResumeAgent(args);
                case 'execute_agent':
                    return this.handleExecuteAgent(args);
                case 'agent_health_check':
                    return this.handleAgentHealthCheck(args);
                default:
                    throw new Error(`Невідомий інструмент хабу: ${toolName}`);
            }
        }
        catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Помилка: ${error instanceof Error ? error.message : 'Невідома помилка'}`,
                    },
                ],
                isError: true,
            };
        }
    }
    async handleListServices(args) {
        const { filter = 'all' } = args;
        const allStatuses = this.serviceRegistry.getAllServiceStatuses();
        let filteredStatuses = allStatuses;
        switch (filter) {
            case 'enabled':
                filteredStatuses = allStatuses.filter(s => s.enabled);
                break;
            case 'running':
                filteredStatuses = allStatuses.filter(s => s.running);
                break;
            case 'disabled':
                filteredStatuses = allStatuses.filter(s => !s.enabled);
                break;
        }
        if (filteredStatuses.length === 0) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Не знайдено сервісів з фільтром "${filter}"`,
                    },
                ],
            };
        }
        const servicesList = filteredStatuses.map(status => {
            const service = this.serviceRegistry.getService(status.name);
            const statusIcon = status.running ? '🟢' : (status.enabled ? '🟡' : '🔴');
            const healthIcon = status.healthCheck ? '💚' : (status.running ? '⚠️' : '');
            return `${statusIcon} **${status.name}** ${healthIcon}\n` +
                `   - Статус: ${status.enabled ? 'Увімкнено' : 'Вимкнено'} | ${status.running ? 'Запущено' : 'Зупинено'}\n` +
                `   - Опис: ${service?.metadata.description || 'Немає опису'}\n` +
                `   - Версія: ${service?.metadata.version || 'Невідома'}\n` +
                (status.lastStarted ? `   - Запущено: ${status.lastStarted.toLocaleString()}\n` : '') +
                (status.lastError ? `   - Остання помилка: ${status.lastError}\n` : '');
        }).join('\n');
        return {
            content: [
                {
                    type: 'text',
                    text: `**Digital Office Сервіси** (фільтр: ${filter})\n\n${servicesList}`,
                },
            ],
        };
    }
    async handleServiceStatus(args) {
        const { serviceName } = args;
        const status = this.serviceRegistry.getServiceStatus(serviceName);
        const service = this.serviceRegistry.getService(serviceName);
        if (!status || !service) {
            throw new Error(`Сервіс ${serviceName} не знайдено`);
        }
        const tools = service.getTools();
        const toolsList = tools.length > 0 ?
            tools.map(tool => `  - ${tool.name}: ${tool.description}`).join('\n') :
            '  Немає доступних інструментів';
        return {
            content: [
                {
                    type: 'text',
                    text: `**Статус сервісу: ${serviceName}**\n\n` +
                        `📋 **Метадані:**\n` +
                        `  - Назва: ${service.metadata.name}\n` +
                        `  - Версія: ${service.metadata.version}\n` +
                        `  - Опис: ${service.metadata.description}\n` +
                        `  - Категорія: ${service.metadata.category || 'Загальна'}\n\n` +
                        `⚡ **Статус:**\n` +
                        `  - Увімкнено: ${status.enabled ? '✅' : '❌'}\n` +
                        `  - Запущено: ${status.running ? '✅' : '❌'}\n` +
                        `  - Здоров'я: ${status.healthCheck ? '💚' : (status.running ? '⚠️ Потребує перевірки' : 'N/A')}\n` +
                        (status.lastStarted ? `  - Останній запуск: ${status.lastStarted.toLocaleString()}\n` : '') +
                        (status.lastError ? `  - Остання помилка: ${status.lastError}\n` : '') +
                        `\n🛠️ **Доступні інструменти:**\n${toolsList}`,
                },
            ],
        };
    }
    async handleEnableService(args) {
        const { serviceName } = args;
        await this.serviceRegistry.enableService(serviceName);
        return {
            content: [
                {
                    type: 'text',
                    text: `✅ Сервіс ${serviceName} успішно увімкнено`,
                },
            ],
        };
    }
    async handleDisableService(args) {
        const { serviceName } = args;
        await this.serviceRegistry.disableService(serviceName);
        return {
            content: [
                {
                    type: 'text',
                    text: `❌ Сервіс ${serviceName} вимкнено`,
                },
            ],
        };
    }
    async handleStartService(args) {
        const { serviceName } = args;
        await this.serviceRegistry.startService(serviceName);
        return {
            content: [
                {
                    type: 'text',
                    text: `🚀 Сервіс ${serviceName} успішно запущено`,
                },
            ],
        };
    }
    async handleStopService(args) {
        const { serviceName } = args;
        await this.serviceRegistry.stopService(serviceName);
        return {
            content: [
                {
                    type: 'text',
                    text: `⏹️ Сервіс ${serviceName} зупинено`,
                },
            ],
        };
    }
    async handleHealthCheck(args) {
        await this.serviceRegistry.performHealthChecks();
        const statuses = this.serviceRegistry.getAllServiceStatuses()
            .filter(s => s.running);
        if (statuses.length === 0) {
            return {
                content: [
                    {
                        type: 'text',
                        text: '🔍 Немає запущених сервісів для перевірки',
                    },
                ],
            };
        }
        const healthReport = statuses.map(status => {
            const icon = status.healthCheck ? '💚' : '💔';
            return `${icon} ${status.name}: ${status.healthCheck ? 'Здоровий' : 'Потребує уваги'}`;
        }).join('\n');
        const healthyCount = statuses.filter(s => s.healthCheck).length;
        return {
            content: [
                {
                    type: 'text',
                    text: `🏥 **Перевірка здоров'я сервісів**\n\n` +
                        `📊 **Загальна статистика:** ${healthyCount}/${statuses.length} сервісів здорові\n\n` +
                        `**Детальний звіт:**\n${healthReport}`,
                },
            ],
        };
    }
    async handleListAgents(args) {
        const { filter = 'all' } = args;
        const allStatuses = this.agentRegistry.getAllAgentStatuses();
        let filteredStatuses = allStatuses;
        switch (filter) {
            case 'enabled':
                filteredStatuses = allStatuses.filter(s => s.config.enabled);
                break;
            case 'running':
                filteredStatuses = allStatuses.filter(s => s.isRunning);
                break;
            case 'disabled':
                filteredStatuses = allStatuses.filter(s => !s.config.enabled);
                break;
        }
        if (filteredStatuses.length === 0) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Не знайдено агентів з фільтром "${filter}"`,
                    },
                ],
            };
        }
        const agentsList = filteredStatuses.map(status => {
            const agent = this.agentRegistry.getAgent(status.name);
            const statusIcon = status.isRunning ? '🤖' : (status.config.enabled ? '🟡' : '🔴');
            const healthIcon = status.healthCheck ? '💚' : (status.isRunning ? '⚠️' : '');
            return `${statusIcon} **${status.name}** ${healthIcon}\n` +
                `   - Статус: ${status.config.enabled ? 'Увімкнено' : 'Вимкнено'} | ${status.isRunning ? 'Запущено' : 'Зупинено'}\n` +
                `   - Опис: ${agent?.metadata.description || 'Немає опису'}\n` +
                `   - Планування: ${status.schedule.type} (${status.schedule.enabled ? 'Активне' : 'Неактивне'})\n` +
                `   - Виконань: ${status.executionCount}\n` +
                (status.lastExecution ? `   - Останнє виконання: ${status.lastExecution.toLocaleString()}\n` : '') +
                (status.nextExecution ? `   - Наступне виконання: ${status.nextExecution.toLocaleString()}\n` : '') +
                (status.recentErrors.length > 0 ? `   - Помилки: ${status.recentErrors.length}\n` : '');
        }).join('\n');
        return {
            content: [
                {
                    type: 'text',
                    text: `**🤖 Автономні Агенти** (фільтр: ${filter})\n\n${agentsList}`,
                },
            ],
        };
    }
    async handleAgentStatus(args) {
        const { agentName } = args;
        const status = this.agentRegistry.getAgentStatus(agentName);
        const agent = this.agentRegistry.getAgent(agentName);
        if (!status || !agent) {
            throw new Error(`Агент ${agentName} не знайдено`);
        }
        const tools = agent.getTools();
        const toolsList = tools.length > 0 ?
            tools.map(tool => `  - ${tool.name}: ${tool.description}`).join('\n') :
            '  Немає доступних інструментів';
        const errorsList = status.recentErrors.length > 0 ?
            status.recentErrors.slice(-3).map(err => `  - ${err}`).join('\n') :
            '  Немає помилок';
        return {
            content: [
                {
                    type: 'text',
                    text: `**🤖 Статус агента: ${agentName}**\n\n` +
                        `📋 **Метадані:**\n` +
                        `  - Назва: ${agent.metadata.name}\n` +
                        `  - Версія: ${agent.metadata.version}\n` +
                        `  - Опис: ${agent.metadata.description}\n` +
                        `  - Категорія: ${agent.metadata.category || 'Автономний'}\n\n` +
                        `⚡ **Статус:**\n` +
                        `  - Увімкнено: ${status.config.enabled ? '✅' : '❌'}\n` +
                        `  - Запущено: ${status.isRunning ? '✅' : '❌'}\n` +
                        `  - Здоров'я: ${status.healthCheck ? '💚' : (status.isRunning ? '⚠️ Потребує перевірки' : 'N/A')}\n` +
                        `  - Виконань: ${status.executionCount}\n` +
                        (status.lastExecution ? `  - Останнє виконання: ${status.lastExecution.toLocaleString()}\n` : '') +
                        (status.nextExecution ? `  - Наступне виконання: ${status.nextExecution.toLocaleString()}\n` : '') +
                        `\n📅 **Планування:**\n` +
                        `  - Тип: ${status.schedule.type}\n` +
                        `  - Активне: ${status.schedule.enabled ? '✅' : '❌'}\n` +
                        (status.schedule.intervalMs ? `  - Інтервал: ${status.schedule.intervalMs}мс\n` : '') +
                        (status.schedule.cronExpression ? `  - Cron: ${status.schedule.cronExpression}\n` : '') +
                        `\n🛠️ **Доступні інструменти:**\n${toolsList}\n` +
                        `\n❌ **Останні помилки:**\n${errorsList}`,
                },
            ],
        };
    }
    async handleEnableAgent(args) {
        const { agentName } = args;
        await this.agentRegistry.enableAgent(agentName);
        return {
            content: [
                {
                    type: 'text',
                    text: `🤖✅ Агент ${agentName} успішно увімкнено`,
                },
            ],
        };
    }
    async handleDisableAgent(args) {
        const { agentName } = args;
        await this.agentRegistry.disableAgent(agentName);
        return {
            content: [
                {
                    type: 'text',
                    text: `🤖❌ Агент ${agentName} вимкнено`,
                },
            ],
        };
    }
    async handlePauseAgent(args) {
        const { agentName } = args;
        await this.agentRegistry.pauseAgent(agentName);
        return {
            content: [
                {
                    type: 'text',
                    text: `🤖⏸️ Агент ${agentName} призупинено`,
                },
            ],
        };
    }
    async handleResumeAgent(args) {
        const { agentName } = args;
        await this.agentRegistry.resumeAgent(agentName);
        return {
            content: [
                {
                    type: 'text',
                    text: `🤖▶️ Агент ${agentName} відновлено`,
                },
            ],
        };
    }
    async handleExecuteAgent(args) {
        const { agentName } = args;
        await this.agentRegistry.executeAgentNow(agentName);
        return {
            content: [
                {
                    type: 'text',
                    text: `🤖⚡ Агент ${agentName} виконано вручну`,
                },
            ],
        };
    }
    async handleAgentHealthCheck(args) {
        const registryHealth = this.agentRegistry.getRegistryHealth();
        const statuses = this.agentRegistry.getAllAgentStatuses()
            .filter(s => s.isRunning);
        if (statuses.length === 0) {
            return {
                content: [
                    {
                        type: 'text',
                        text: '🔍 Немає запущених агентів для перевірки',
                    },
                ],
            };
        }
        const healthReport = statuses.map(status => {
            const icon = status.healthCheck ? '💚' : '💔';
            const errorsCount = status.recentErrors.length;
            const errorInfo = errorsCount > 0 ? ` (${errorsCount} помилок)` : '';
            return `${icon} ${status.name}: ${status.healthCheck ? 'Здоровий' : 'Потребує уваги'}${errorInfo}`;
        }).join('\n');
        return {
            content: [
                {
                    type: 'text',
                    text: `🤖🏥 **Перевірка здоров'я агентів**\n\n` +
                        `📊 **Загальна статистика:**\n` +
                        `  - Всього агентів: ${registryHealth.totalAgents}\n` +
                        `  - Запущено: ${registryHealth.runningAgents}\n` +
                        `  - Здорові: ${registryHealth.healthyAgents}\n` +
                        `  - Планувальник: ${registryHealth.schedulerRunning ? '✅' : '❌'}\n\n` +
                        `**Детальний звіт:**\n${healthReport}`,
                },
            ],
        };
    }
    async registerService(service) {
        await this.serviceRegistry.registerService(service);
    }
    async registerAgent(agent) {
        await this.agentRegistry.registerAgent(agent);
    }
    async start() {
        // Ініціалізуємо інфраструктуру
        await this.dataStore.initialize();
        await this.resourceManager.startResourceMonitoring();
        // Ініціалізуємо агентську систему
        await this.agentRegistry.initialize();
        await this.agentLoader.initialize();
        await this.agentScheduler.start();
        // Завантажуємо всі агенти
        await this.agentLoader.loadAllAgents();
        // Запускаємо спостереження за змінами агентів
        await this.agentLoader.startWatching();
        // Запускаємо всі увімкнені сервіси
        await this.serviceRegistry.startAllEnabledServices();
        // Запускаємо MCP сервер
        const transport = new stdio_js_1.StdioServerTransport();
        await this.server.connect(transport);
        console.error('Digital Office Hub запущено');
    }
    async shutdown() {
        // Зупиняємо спостереження за агентами
        await this.agentLoader.stopWatching();
        // Зупиняємо агентську систему
        await this.agentScheduler.stop();
        await this.agentRegistry.shutdown();
        // Зупиняємо сервіси
        await this.serviceRegistry.stopAllServices();
        // Зупиняємо інфраструктуру
        await this.resourceManager.cleanup();
        await this.dataStore.shutdown();
        console.error('Digital Office Hub зупинено');
    }
    getServiceRegistry() {
        return this.serviceRegistry;
    }
    getAgentRegistry() {
        return this.agentRegistry;
    }
    getAgentScheduler() {
        return this.agentScheduler;
    }
    getAgentLoader() {
        return this.agentLoader;
    }
    getEventBus() {
        return this.eventBus;
    }
    getDataStore() {
        return this.dataStore;
    }
    getResourceManager() {
        return this.resourceManager;
    }
}
exports.DigitalOfficeHub = DigitalOfficeHub;
//# sourceMappingURL=DigitalOfficeHub.js.map