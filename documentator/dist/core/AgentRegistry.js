"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.AgentRegistry = void 0;
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
class AgentRegistry {
    constructor(scheduler, config = {
        agentsConfigPath: './data/agents-config.json',
        enableAutoLoad: true,
        logLevel: 'info'
    }) {
        this.agents = new Map();
        this.initialized = false;
        this.scheduler = scheduler;
        this.config = config;
    }
    async initialize() {
        if (this.initialized) {
            console.log('AgentRegistry вже ініціалізовано');
            return;
        }
        await this.ensureConfigFile();
        if (this.config.enableAutoLoad) {
            await this.loadAgentsFromConfig();
        }
        this.initialized = true;
        console.log('AgentRegistry ініціалізовано');
    }
    async shutdown() {
        if (!this.initialized) {
            return;
        }
        // Зупиняємо всі агенти
        for (const agent of this.agents.values()) {
            try {
                await this.scheduler.unregisterAgent(agent.metadata.name);
                await agent.shutdown();
            }
            catch (error) {
                console.error(`Помилка зупинки агента ${agent.metadata.name}:`, error);
            }
        }
        this.agents.clear();
        this.initialized = false;
        console.log('AgentRegistry зупинено');
    }
    async registerAgent(agent) {
        const agentName = agent.metadata.name;
        if (this.agents.has(agentName)) {
            throw new Error(`Агент ${agentName} вже зареєстровано`);
        }
        // Ініціалізуємо агента
        await agent.initialize();
        // Реєструємо в реєстрі
        this.agents.set(agentName, agent);
        // Реєструємо в планувальнику
        await this.scheduler.registerAgent(agent);
        await this.saveAgentConfig(agentName, agent.getAgentStatus().config);
        this.log(`Агент ${agentName} зареєстровано`);
    }
    async unregisterAgent(agentName) {
        const agent = this.agents.get(agentName);
        if (!agent) {
            throw new Error(`Агент ${agentName} не знайдено`);
        }
        // Видаляємо з планувальника
        await this.scheduler.unregisterAgent(agentName);
        // Зупиняємо агента
        await agent.shutdown();
        // Видаляємо з реєстру
        this.agents.delete(agentName);
        await this.removeAgentConfig(agentName);
        this.log(`Агент ${agentName} видалено`);
    }
    async enableAgent(agentName) {
        const agent = this.agents.get(agentName);
        if (!agent) {
            throw new Error(`Агент ${agentName} не знайдено`);
        }
        agent.updateConfig({ enabled: true });
        await this.scheduler.resumeAgent(agentName);
        await this.saveAgentConfig(agentName, agent.getAgentStatus().config);
        this.log(`Агент ${agentName} увімкнено`);
    }
    async disableAgent(agentName) {
        const agent = this.agents.get(agentName);
        if (!agent) {
            throw new Error(`Агент ${agentName} не знайдено`);
        }
        agent.updateConfig({ enabled: false });
        await this.scheduler.pauseAgent(agentName);
        await this.saveAgentConfig(agentName, agent.getAgentStatus().config);
        this.log(`Агент ${agentName} вимкнено`);
    }
    async pauseAgent(agentName) {
        await this.scheduler.pauseAgent(agentName);
        this.log(`Агент ${agentName} призупинено`);
    }
    async resumeAgent(agentName) {
        await this.scheduler.resumeAgent(agentName);
        this.log(`Агент ${agentName} відновлено`);
    }
    async executeAgentNow(agentName) {
        await this.scheduler.executeAgentNow(agentName);
        this.log(`Агент ${agentName} виконано вручну`);
    }
    getAgent(agentName) {
        return this.agents.get(agentName);
    }
    getAllAgents() {
        return Array.from(this.agents.values());
    }
    getAgentNames() {
        return Array.from(this.agents.keys());
    }
    getAgentStatus(agentName) {
        const agent = this.agents.get(agentName);
        return agent ? agent.getAgentStatus() : null;
    }
    getAllAgentStatuses() {
        return this.getAllAgents().map(agent => agent.getAgentStatus());
    }
    async updateAgentConfig(agentName, config) {
        const agent = this.agents.get(agentName);
        if (!agent) {
            throw new Error(`Агент ${agentName} не знайдено`);
        }
        agent.updateConfig(config);
        await this.saveAgentConfig(agentName, agent.getAgentStatus().config);
        this.log(`Конфігурація агента ${agentName} оновлено`);
    }
    async clearAgentErrors(agentName) {
        const agent = this.agents.get(agentName);
        if (!agent) {
            throw new Error(`Агент ${agentName} не знайдено`);
        }
        agent.clearErrors();
        this.log(`Помилки агента ${agentName} очищено`);
    }
    async ensureConfigFile() {
        const configPath = this.config.agentsConfigPath;
        const configDir = path.dirname(configPath);
        await fs.ensureDir(configDir);
        if (!await fs.pathExists(configPath)) {
            const initialConfig = {
                agents: {},
                registry: {
                    version: '1.0.0',
                    lastUpdated: new Date().toISOString()
                }
            };
            await fs.writeJson(configPath, initialConfig, { spaces: 2 });
            this.log('Створено файл конфігурації агентів');
        }
    }
    async loadAgentsFromConfig() {
        try {
            const configPath = this.config.agentsConfigPath;
            const config = await fs.readJson(configPath);
            // TODO: Реалізувати автоматичне завантаження агентів з конфігурації
            // Це буде потребувати системи плагінів для динамічного завантаження агентів
            this.log('Конфігурація агентів завантажена');
        }
        catch (error) {
            console.error('Помилка завантаження конфігурації агентів:', error);
        }
    }
    async saveAgentConfig(agentName, agentConfig) {
        try {
            const configPath = this.config.agentsConfigPath;
            const config = await fs.readJson(configPath);
            config.agents[agentName] = {
                ...agentConfig,
                lastUpdated: new Date().toISOString()
            };
            config.registry.lastUpdated = new Date().toISOString();
            await fs.writeJson(configPath, config, { spaces: 2 });
        }
        catch (error) {
            console.error(`Помилка збереження конфігурації агента ${agentName}:`, error);
        }
    }
    async removeAgentConfig(agentName) {
        try {
            const configPath = this.config.agentsConfigPath;
            const config = await fs.readJson(configPath);
            delete config.agents[agentName];
            config.registry.lastUpdated = new Date().toISOString();
            await fs.writeJson(configPath, config, { spaces: 2 });
        }
        catch (error) {
            console.error(`Помилка видалення конфігурації агента ${agentName}:`, error);
        }
    }
    getRegistryHealth() {
        const statuses = this.getAllAgentStatuses();
        return {
            totalAgents: statuses.length,
            runningAgents: statuses.filter(s => s.isRunning).length,
            healthyAgents: statuses.filter(s => s.healthCheck).length,
            schedulerRunning: this.scheduler.isRunning()
        };
    }
    log(message, level = 'info') {
        if (this.config.logLevel === 'error' && level !== 'error')
            return;
        if (this.config.logLevel === 'warn' && level === 'info')
            return;
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] [AgentRegistry] ${message}`;
        switch (level) {
            case 'error':
                console.error(logMessage);
                break;
            case 'warn':
                console.warn(logMessage);
                break;
            default:
                console.log(logMessage);
        }
    }
}
exports.AgentRegistry = AgentRegistry;
//# sourceMappingURL=AgentRegistry.js.map