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
exports.ServiceRegistry = void 0;
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
class ServiceRegistry {
    constructor(configPath) {
        this.services = new Map();
        this.serviceStatuses = new Map();
        this.configPath = configPath || path.join(process.cwd(), 'digital-office-config.json');
    }
    async registerService(service) {
        const serviceName = service.metadata.name;
        if (this.services.has(serviceName)) {
            throw new Error(`Сервіс ${serviceName} вже зареєстровано`);
        }
        this.services.set(serviceName, service);
        this.serviceStatuses.set(serviceName, {
            name: serviceName,
            enabled: await this.isServiceEnabled(serviceName),
            running: false,
            healthCheck: false
        });
        console.log(`Сервіс ${serviceName} зареєстровано`);
    }
    async unregisterService(serviceName) {
        const service = this.services.get(serviceName);
        if (service) {
            await this.stopService(serviceName);
            this.services.delete(serviceName);
            this.serviceStatuses.delete(serviceName);
            console.log(`Сервіс ${serviceName} відреєстровано`);
        }
    }
    async startService(serviceName) {
        const service = this.services.get(serviceName);
        const status = this.serviceStatuses.get(serviceName);
        if (!service || !status) {
            throw new Error(`Сервіс ${serviceName} не знайдено`);
        }
        if (!status.enabled) {
            throw new Error(`Сервіс ${serviceName} відключено в конфігурації`);
        }
        if (status.running) {
            console.log(`Сервіс ${serviceName} вже запущено`);
            return;
        }
        try {
            await service.initialize();
            status.running = true;
            status.lastStarted = new Date();
            status.lastError = undefined;
            console.log(`Сервіс ${serviceName} успішно запущено`);
        }
        catch (error) {
            status.lastError = error instanceof Error ? error.message : 'Невідома помилка';
            throw new Error(`Помилка запуску сервісу ${serviceName}: ${status.lastError}`);
        }
    }
    async stopService(serviceName) {
        const service = this.services.get(serviceName);
        const status = this.serviceStatuses.get(serviceName);
        if (!service || !status) {
            throw new Error(`Сервіс ${serviceName} не знайдено`);
        }
        if (!status.running) {
            console.log(`Сервіс ${serviceName} вже зупинено`);
            return;
        }
        try {
            await service.shutdown();
            status.running = false;
            console.log(`Сервіс ${serviceName} зупинено`);
        }
        catch (error) {
            status.lastError = error instanceof Error ? error.message : 'Невідома помилка';
            console.error(`Помилка зупинки сервісу ${serviceName}: ${status.lastError}`);
        }
    }
    async startAllEnabledServices() {
        const enabledServices = Array.from(this.serviceStatuses.entries())
            .filter(([_, status]) => status.enabled)
            .map(([name, _]) => name);
        for (const serviceName of enabledServices) {
            try {
                await this.startService(serviceName);
            }
            catch (error) {
                console.error(`Не вдалося запустити сервіс ${serviceName}:`, error);
            }
        }
    }
    async stopAllServices() {
        const runningServices = Array.from(this.serviceStatuses.entries())
            .filter(([_, status]) => status.running)
            .map(([name, _]) => name);
        for (const serviceName of runningServices) {
            await this.stopService(serviceName);
        }
    }
    async enableService(serviceName) {
        const status = this.serviceStatuses.get(serviceName);
        if (!status) {
            throw new Error(`Сервіс ${serviceName} не знайдено`);
        }
        status.enabled = true;
        await this.saveServiceConfig(serviceName, true);
        console.log(`Сервіс ${serviceName} увімкнено`);
    }
    async disableService(serviceName) {
        const status = this.serviceStatuses.get(serviceName);
        if (!status) {
            throw new Error(`Сервіс ${serviceName} не знайдено`);
        }
        if (status.running) {
            await this.stopService(serviceName);
        }
        status.enabled = false;
        await this.saveServiceConfig(serviceName, false);
        console.log(`Сервіс ${serviceName} вимкнено`);
    }
    getService(serviceName) {
        return this.services.get(serviceName);
    }
    getAllServices() {
        return Array.from(this.services.values());
    }
    getEnabledServices() {
        return Array.from(this.services.entries())
            .filter(([name, _]) => this.serviceStatuses.get(name)?.enabled)
            .map(([_, service]) => service);
    }
    getRunningServices() {
        return Array.from(this.services.entries())
            .filter(([name, _]) => this.serviceStatuses.get(name)?.running)
            .map(([_, service]) => service);
    }
    getServiceStatus(serviceName) {
        return this.serviceStatuses.get(serviceName);
    }
    getAllServiceStatuses() {
        return Array.from(this.serviceStatuses.values());
    }
    async performHealthChecks() {
        for (const [serviceName, service] of this.services.entries()) {
            const status = this.serviceStatuses.get(serviceName);
            if (status && status.running) {
                try {
                    status.healthCheck = await service.isHealthy();
                }
                catch (error) {
                    status.healthCheck = false;
                    status.lastError = error instanceof Error ? error.message : 'Health check failed';
                }
            }
        }
    }
    async isServiceEnabled(serviceName) {
        try {
            const config = await this.loadConfig();
            const serviceConfig = config.services.find(s => s.name === serviceName);
            return serviceConfig?.enabled ?? true; // За замовчуванням увімкнено
        }
        catch (error) {
            return true; // За замовчуванням увімкнено, якщо конфіг не існує
        }
    }
    async saveServiceConfig(serviceName, enabled) {
        try {
            const config = await this.loadConfig();
            const serviceIndex = config.services.findIndex(s => s.name === serviceName);
            if (serviceIndex >= 0) {
                config.services[serviceIndex].enabled = enabled;
            }
            else {
                config.services.push({ name: serviceName, enabled });
            }
            await fs.writeJson(this.configPath, config, { spaces: 2 });
        }
        catch (error) {
            console.error('Помилка збереження конфігурації:', error);
        }
    }
    async loadConfig() {
        try {
            if (await fs.pathExists(this.configPath)) {
                return await fs.readJson(this.configPath);
            }
        }
        catch (error) {
            console.warn('Помилка завантаження конфігурації, використовуємо значення за замовчуванням');
        }
        return { services: [] };
    }
}
exports.ServiceRegistry = ServiceRegistry;
//# sourceMappingURL=ServiceRegistry.js.map