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
exports.ServiceManagerCLI = void 0;
const ServiceRegistry_1 = require("../core/ServiceRegistry");
const DocumentatorService_1 = require("../services/documentator/DocumentatorService");
const PMService_1 = require("../services/pm/PMService");
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
class ServiceManagerCLI {
    constructor() {
        this.serviceRegistry = new ServiceRegistry_1.ServiceRegistry();
    }
    async initialize() {
        // Реєструємо доступні сервіси
        const documentatorService = new DocumentatorService_1.DocumentatorService();
        await this.serviceRegistry.registerService(documentatorService);
        const pmService = new PMService_1.PMService();
        await this.serviceRegistry.registerService(pmService);
    }
    async listServices(filter = 'all') {
        const statuses = this.serviceRegistry.getAllServiceStatuses();
        let filteredStatuses = statuses;
        switch (filter) {
            case 'enabled':
                filteredStatuses = statuses.filter(s => s.enabled);
                break;
            case 'running':
                filteredStatuses = statuses.filter(s => s.running);
                break;
            case 'disabled':
                filteredStatuses = statuses.filter(s => !s.enabled);
                break;
        }
        console.log(`\n📋 Digital Office Сервіси (фільтр: ${filter})\n`);
        console.log('='.repeat(50));
        if (filteredStatuses.length === 0) {
            console.log(`Не знайдено сервісів з фільтром "${filter}"`);
            return;
        }
        for (const status of filteredStatuses) {
            const service = this.serviceRegistry.getService(status.name);
            const statusIcon = status.running ? '🟢' : (status.enabled ? '🟡' : '🔴');
            const healthIcon = status.healthCheck ? '💚' : (status.running ? '⚠️' : '');
            console.log(`${statusIcon} ${status.name} ${healthIcon}`);
            console.log(`   Опис: ${service?.metadata.description || 'Немає опису'}`);
            console.log(`   Версія: ${service?.metadata.version || 'Невідома'}`);
            console.log(`   Статус: ${status.enabled ? 'Увімкнено' : 'Вимкнено'} | ${status.running ? 'Запущено' : 'Зупинено'}`);
            if (status.lastStarted) {
                console.log(`   Запущено: ${status.lastStarted.toLocaleString()}`);
            }
            if (status.lastError) {
                console.log(`   Остання помилка: ${status.lastError}`);
            }
            console.log();
        }
    }
    async serviceStatus(serviceName) {
        const status = this.serviceRegistry.getServiceStatus(serviceName);
        const service = this.serviceRegistry.getService(serviceName);
        if (!status || !service) {
            console.error(`❌ Сервіс ${serviceName} не знайдено`);
            return;
        }
        console.log(`\n📊 Статус сервісу: ${serviceName}\n`);
        console.log('='.repeat(40));
        console.log(`📋 Метадані:`);
        console.log(`  Назва: ${service.metadata.name}`);
        console.log(`  Версія: ${service.metadata.version}`);
        console.log(`  Опис: ${service.metadata.description}`);
        console.log(`  Категорія: ${service.metadata.category || 'Загальна'}`);
        console.log(`\n⚡ Статус:`);
        console.log(`  Увімкнено: ${status.enabled ? '✅' : '❌'}`);
        console.log(`  Запущено: ${status.running ? '✅' : '❌'}`);
        console.log(`  Здоров'я: ${status.healthCheck ? '💚' : (status.running ? '⚠️ Потребує перевірки' : 'N/A')}`);
        if (status.lastStarted) {
            console.log(`  Останній запуск: ${status.lastStarted.toLocaleString()}`);
        }
        if (status.lastError) {
            console.log(`  Остання помилка: ${status.lastError}`);
        }
        const tools = service.getTools();
        console.log(`\n🛠️ Доступні інструменти (${tools.length}):`);
        if (tools.length > 0) {
            for (const tool of tools) {
                console.log(`  - ${tool.name}: ${tool.description}`);
            }
        }
        else {
            console.log('  Немає доступних інструментів');
        }
    }
    async enableService(serviceName) {
        try {
            await this.serviceRegistry.enableService(serviceName);
            console.log(`✅ Сервіс ${serviceName} успішно увімкнено`);
        }
        catch (error) {
            console.error(`❌ Помилка включення сервісу: ${error instanceof Error ? error.message : 'Невідома помилка'}`);
        }
    }
    async disableService(serviceName) {
        try {
            await this.serviceRegistry.disableService(serviceName);
            console.log(`❌ Сервіс ${serviceName} вимкнено`);
        }
        catch (error) {
            console.error(`❌ Помилка відключення сервісу: ${error instanceof Error ? error.message : 'Невідома помилка'}`);
        }
    }
    async startService(serviceName) {
        try {
            await this.serviceRegistry.startService(serviceName);
            console.log(`🚀 Сервіс ${serviceName} успішно запущено`);
        }
        catch (error) {
            console.error(`❌ Помилка запуску сервісу: ${error instanceof Error ? error.message : 'Невідома помилка'}`);
        }
    }
    async stopService(serviceName) {
        try {
            await this.serviceRegistry.stopService(serviceName);
            console.log(`⏹️ Сервіс ${serviceName} зупинено`);
        }
        catch (error) {
            console.error(`❌ Помилка зупинки сервісу: ${error instanceof Error ? error.message : 'Невідома помилка'}`);
        }
    }
    async healthCheck() {
        console.log('🏥 Перевірка здоров\'я сервісів...\n');
        await this.serviceRegistry.performHealthChecks();
        const statuses = this.serviceRegistry.getAllServiceStatuses()
            .filter(s => s.running);
        if (statuses.length === 0) {
            console.log('🔍 Немає запущених сервісів для перевірки');
            return;
        }
        const healthyCount = statuses.filter(s => s.healthCheck).length;
        console.log(`📊 Загальна статистика: ${healthyCount}/${statuses.length} сервісів здорові\n`);
        console.log('Детальний звіт:');
        for (const status of statuses) {
            const icon = status.healthCheck ? '💚' : '💔';
            console.log(`${icon} ${status.name}: ${status.healthCheck ? 'Здоровий' : 'Потребує уваги'}`);
        }
    }
    async showConfig() {
        const configPath = path.join(process.cwd(), 'digital-office-config.json');
        if (await fs.pathExists(configPath)) {
            const config = await fs.readJson(configPath);
            console.log('\n⚙️ Поточна конфігурація:\n');
            console.log(JSON.stringify(config, null, 2));
        }
        else {
            console.log('⚠️ Файл конфігурації не знайдено');
        }
    }
    async createDefaultConfig() {
        const configPath = path.join(process.cwd(), 'digital-office-config.json');
        if (await fs.pathExists(configPath)) {
            console.log('⚠️ Файл конфігурації вже існує');
            return;
        }
        const defaultConfig = {
            services: [
                {
                    name: 'documentator',
                    enabled: true,
                    config: {
                        projectsPath: './projects',
                        templatesPath: './templates',
                        outputPath: './output'
                    }
                }
            ],
            globalConfig: {
                logLevel: 'info',
                apiPort: 3000,
                mcpServerName: 'digital-office'
            }
        };
        await fs.writeJson(configPath, defaultConfig, { spaces: 2 });
        console.log(`✅ Створено файл конфігурації: ${configPath}`);
    }
}
exports.ServiceManagerCLI = ServiceManagerCLI;
//# sourceMappingURL=ServiceManager.js.map