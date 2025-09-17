"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.BaseAgent = void 0;
const BaseService_1 = require("./BaseService");
const EventBus_1 = require("./EventBus");
const DataStore_1 = require("./DataStore");
const ResourceManager_1 = require("./ResourceManager");
const IntegrationService_1 = require("../services/integration/IntegrationService");
class BaseAgent extends BaseService_1.BaseService {
    constructor(config) {
        super();
        this.isRunning = false;
        this.executionCount = 0;
        this.errors = [];
        this.agentConfig = config;
        this.eventBus = EventBus_1.EventBus.getInstance();
        this.dataStore = DataStore_1.DataStore.getInstance();
        this.resourceManager = ResourceManager_1.ResourceManager.getInstance();
        this.agentName = config.name || 'BaseAgent';
        // Ініціалізуємо сервіс інтеграції якщо потрібно
        if (config.enableIntegrations) {
            this.integrationService = new IntegrationService_1.IntegrationService();
        }
    }
    async startAutonomousExecution() {
        if (this.isRunning) {
            console.log(`Агент ${this.agentName} вже запущено`);
            return;
        }
        if (!this.agentConfig.enabled) {
            console.log(`Агент ${this.agentName} відключено`);
            return;
        }
        this.isRunning = true;
        console.log(`Агент ${this.agentName} запущено в автономному режимі`);
    }
    async stopAutonomousExecution() {
        if (!this.isRunning) {
            return;
        }
        this.isRunning = false;
        console.log(`Агент ${this.agentName} зупинено`);
    }
    async executeOnce() {
        if (!this.initialized) {
            throw new Error(`Агент ${this.agentName} не ініціалізовано`);
        }
        try {
            this.lastExecution = new Date();
            // Публікуємо подію про початок виконання
            await this.eventBus.publish('agent.execution.start', this.agentName, {
                executionCount: this.executionCount + 1,
                timestamp: this.lastExecution
            });
            // Виконуємо основну логіку агента
            await this.executeAutonomously();
            this.executionCount++;
            // Зберігаємо статистику виконання
            await this.dataStore.create(`agent_executions_${this.agentName}`, {
                executionNumber: this.executionCount,
                startTime: this.lastExecution,
                endTime: new Date(),
                success: true
            });
            // Публікуємо подію про успішне виконання
            await this.eventBus.publish('agent.execution.success', this.agentName, {
                executionCount: this.executionCount,
                duration: Date.now() - this.lastExecution.getTime()
            });
            console.log(`Агент ${this.agentName} виконано успішно (виконання #${this.executionCount})`);
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Невідома помилка';
            this.errors.push(`${new Date().toISOString()}: ${errorMessage}`);
            // Зберігаємо інформацію про помилку
            await this.dataStore.create(`agent_errors_${this.agentName}`, {
                executionCount: this.executionCount,
                error: errorMessage,
                timestamp: new Date()
            });
            // Публікуємо подію про помилку
            await this.eventBus.publish('agent.execution.error', this.agentName, {
                error: errorMessage,
                executionCount: this.executionCount
            });
            console.error(`Помилка виконання агента ${this.agentName}:`, error);
            throw error;
        }
    }
    getAgentStatus() {
        return {
            ...this.getStatus(),
            isRunning: this.isRunning,
            lastExecution: this.lastExecution,
            nextExecution: this.nextExecution,
            executionCount: this.executionCount,
            recentErrors: this.errors.slice(-5),
            schedule: this.getScheduleConfig(),
            config: this.agentConfig
        };
    }
    updateNextExecution(nextExecution) {
        this.nextExecution = nextExecution;
    }
    isAutonomousRunning() {
        return this.isRunning;
    }
    clearErrors() {
        this.errors = [];
    }
    updateConfig(newConfig) {
        this.agentConfig = { ...this.agentConfig, ...newConfig };
    }
    log(message, level = 'info') {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] [${this.agentName}] ${message}`;
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
    // Допоміжні методи для роботи з інфраструктурою
    async emit(event, data) {
        await this.eventBus.publish(event, this.agentName, data);
    }
    async on(event, handler) {
        return this.eventBus.subscribe(event, async (payload) => {
            await handler(payload.data);
        });
    }
    async saveData(key, data) {
        await this.dataStore.set(`agent_${this.agentName}`, key, data);
    }
    async loadData(key) {
        return await this.dataStore.get(`agent_${this.agentName}`, key);
    }
    async queryData(filter, options) {
        return await this.dataStore.query({
            collection: `agent_${this.agentName}`,
            filter,
            ...options
        });
    }
    async readFile(path) {
        return await this.resourceManager.readFile(path);
    }
    async writeFile(path, content) {
        return await this.resourceManager.writeFile(path, content);
    }
    async getSystemResources() {
        return await this.resourceManager.getSystemResources();
    }
    async fetchApi(apiName, endpoint, options) {
        return await this.resourceManager.fetchApiResource(apiName, endpoint, options);
    }
    async executeCommand(command) {
        return await this.resourceManager.executeCommand(command);
    }
    getService(serviceName) {
        return this.resourceManager.getService(serviceName);
    }
    // Data persistence methods
    async persistentStore(key, data) {
        return await this.saveData(key, data);
    }
    async persistentLoad(key) {
        return await this.loadData(key);
    }
    // Integration methods
    async scheduleCalendarEvent(event) {
        if (!this.integrationService) {
            throw new Error('Integration service not enabled. Set enableIntegrations: true in agent config');
        }
        return await this.integrationService.createCalendarEvent(event);
    }
    async scheduleMeeting(title, participants, duration = 60, description) {
        if (!this.integrationService) {
            throw new Error('Integration service not enabled');
        }
        return await this.integrationService.scheduleAgentMeeting(title, participants, duration, description);
    }
    async createTask(title, description, priority = 'medium', dueDate) {
        if (!this.integrationService) {
            throw new Error('Integration service not enabled');
        }
        return await this.integrationService.createAgentTask(title, description, priority, dueDate);
    }
    async createAsanaTask(task) {
        if (!this.integrationService) {
            throw new Error('Integration service not enabled');
        }
        return await this.integrationService.createAsanaTask(task);
    }
    async createNotionTask(task) {
        if (!this.integrationService) {
            throw new Error('Integration service not enabled');
        }
        return await this.integrationService.createNotionTask(task);
    }
    async createJiraIssue(issue) {
        if (!this.integrationService) {
            throw new Error('Integration service not enabled');
        }
        return await this.integrationService.createJiraIssue(issue);
    }
    async createTodoistTask(task) {
        if (!this.integrationService) {
            throw new Error('Integration service not enabled');
        }
        return await this.integrationService.createTodoistTask(task);
    }
    async getIntegrationStatus() {
        if (!this.integrationService) {
            return { enabled: false };
        }
        return await this.integrationService.getIntegrationStatus();
    }
    // Batch operations
    async scheduleMultipleEvents(events) {
        if (!this.integrationService) {
            throw new Error('Integration service not enabled');
        }
        return await this.integrationService.createMultipleEvents(events);
    }
    async createMultipleTasks(tasks, provider) {
        if (!this.integrationService) {
            throw new Error('Integration service not enabled');
        }
        return await this.integrationService.createMultipleTasks(tasks, provider);
    }
    // Helper method for agents to schedule their own review meetings
    async scheduleReviewMeeting(topic, participants) {
        const defaultParticipants = participants || ['team@company.com'];
        return await this.scheduleMeeting(`Agent Review: ${topic}`, defaultParticipants, 30, `Автоматичний огляд від агента ${this.agentName}: ${topic}`);
    }
    // Helper method to create follow-up tasks
    async createFollowUpTask(originalTask, followUpAction, daysTillDue = 7) {
        const dueDate = new Date();
        dueDate.setDate(dueDate.getDate() + daysTillDue);
        return await this.createTask(`Follow-up: ${originalTask}`, `Необхідно виконати: ${followUpAction}\n\nПов'язано з: ${originalTask}`, 'medium', dueDate);
    }
}
exports.BaseAgent = BaseAgent;
//# sourceMappingURL=BaseAgent.js.map