"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.BaseService = void 0;
class BaseService {
    constructor() {
        this.initialized = false;
        this.healthy = false;
    }
    async initialize() {
        if (this.initialized) {
            console.log(`Сервіс ${this.metadata.name} вже ініціалізовано`);
            return;
        }
        try {
            await this.onInitialize();
            this.initialized = true;
            this.healthy = true;
            console.log(`Сервіс ${this.metadata.name} v${this.metadata.version} ініціалізовано`);
        }
        catch (error) {
            this.healthy = false;
            throw error;
        }
    }
    async shutdown() {
        if (!this.initialized) {
            return;
        }
        try {
            await this.onShutdown();
            this.initialized = false;
            this.healthy = false;
            console.log(`Сервіс ${this.metadata.name} зупинено`);
        }
        catch (error) {
            console.error(`Помилка зупинки сервісу ${this.metadata.name}:`, error);
            throw error;
        }
    }
    async isHealthy() {
        if (!this.initialized) {
            return false;
        }
        try {
            const customHealthCheck = await this.performHealthCheck();
            this.healthy = customHealthCheck;
            return this.healthy;
        }
        catch (error) {
            this.healthy = false;
            return false;
        }
    }
    getStatus() {
        return {
            name: this.metadata.name,
            enabled: true, // Буде встановлено ServiceRegistry
            running: this.initialized,
            healthCheck: this.healthy,
            lastStarted: this.initialized ? new Date() : undefined
        };
    }
    async performHealthCheck() {
        // За замовчуванням, якщо сервіс ініціалізовано - він здоровий
        return this.initialized;
    }
    // Методи для інструментів - можуть бути перевизначені в підкласах
    getTools() {
        return [];
    }
    async handleToolCall(toolName, args) {
        throw new Error(`Tool ${toolName} not implemented in ${this.metadata.name}`);
    }
}
exports.BaseService = BaseService;
//# sourceMappingURL=BaseService.js.map