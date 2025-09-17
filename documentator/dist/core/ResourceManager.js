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
exports.ResourceManager = void 0;
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
const os = __importStar(require("os"));
const EventBus_1 = require("./EventBus");
const DataStore_1 = require("./DataStore");
const child_process_1 = require("child_process");
const util_1 = require("util");
const execAsync = (0, util_1.promisify)(child_process_1.exec);
class ResourceManager {
    constructor() {
        this.serviceRegistry = null;
        this.apiResources = new Map();
        this.resourceQuotas = new Map();
        this.resourceUsage = new Map();
        this.monitoringInterval = null;
        this.eventBus = EventBus_1.EventBus.getInstance();
        this.dataStore = DataStore_1.DataStore.getInstance();
    }
    static getInstance() {
        if (!ResourceManager.instance) {
            ResourceManager.instance = new ResourceManager();
        }
        return ResourceManager.instance;
    }
    setServiceRegistry(registry) {
        this.serviceRegistry = registry;
    }
    async getSystemResources() {
        const cpus = os.cpus();
        const totalMem = os.totalmem();
        const freeMem = os.freemem();
        const usedMem = totalMem - freeMem;
        let diskInfo = { total: 0, free: 0, used: 0, usagePercent: 0 };
        try {
            if (process.platform === 'win32') {
                const { stdout } = await execAsync('wmic logicaldisk get size,freespace,caption');
                const lines = stdout.trim().split('\n').slice(1);
                for (const line of lines) {
                    const parts = line.trim().split(/\s+/);
                    // Find primary drive (any drive letter with colon)
                    if (parts[0] && parts[0].match(/^[A-Z]:$/)) {
                        const free = parseInt(parts[1]) || 0;
                        const total = parseInt(parts[2]) || 0;
                        if (total > 0) { // Only use drives with actual storage
                            diskInfo = {
                                total,
                                free,
                                used: total - free,
                                usagePercent: ((total - free) / total) * 100
                            };
                            break; // Use the first valid drive found
                        }
                    }
                }
            }
            else {
                const { stdout } = await execAsync('df -B1 /');
                const lines = stdout.trim().split('\n');
                if (lines.length > 1) {
                    const parts = lines[1].split(/\s+/);
                    const total = parseInt(parts[1]) || 0;
                    const used = parseInt(parts[2]) || 0;
                    const free = parseInt(parts[3]) || 0;
                    diskInfo = {
                        total,
                        free,
                        used,
                        usagePercent: total > 0 ? (used / total) * 100 : 0
                    };
                }
            }
        }
        catch (error) {
            console.error('[ResourceManager] Помилка отримання інформації про диск:', error);
        }
        let cpuUsage = 0;
        const startUsage = process.cpuUsage();
        await new Promise(resolve => setTimeout(resolve, 100));
        const endUsage = process.cpuUsage(startUsage);
        cpuUsage = ((endUsage.user + endUsage.system) / 100000) * 100;
        return {
            cpu: {
                usage: Math.min(cpuUsage, 100),
                cores: cpus.length
            },
            memory: {
                total: totalMem,
                free: freeMem,
                used: usedMem,
                usagePercent: (usedMem / totalMem) * 100
            },
            disk: diskInfo,
            network: {
                interfaces: Object.keys(os.networkInterfaces())
            }
        };
    }
    async getFileResource(filePath) {
        const absolutePath = path.resolve(filePath);
        try {
            const exists = await fs.pathExists(absolutePath);
            if (!exists) {
                return { path: absolutePath, exists: false };
            }
            const stats = await fs.stat(absolutePath);
            return {
                path: absolutePath,
                exists: true,
                size: stats.size,
                isDirectory: stats.isDirectory(),
                permissions: stats.mode.toString(8).slice(-3),
                lastModified: stats.mtime
            };
        }
        catch (error) {
            console.error(`[ResourceManager] Помилка доступу до файлу ${filePath}:`, error);
            return { path: absolutePath, exists: false };
        }
    }
    async readFile(filePath, encoding = 'utf8') {
        try {
            this.trackResourceUsage('fileOperations', 1);
            return await fs.readFile(filePath, encoding);
        }
        catch (error) {
            console.error(`[ResourceManager] Помилка читання файлу ${filePath}:`, error);
            return null;
        }
    }
    async writeFile(filePath, content) {
        try {
            this.trackResourceUsage('fileOperations', 1);
            await fs.writeFile(filePath, content);
            this.eventBus.publishSync('resource.file.written', 'ResourceManager', {
                path: filePath,
                size: content.length
            });
            return true;
        }
        catch (error) {
            console.error(`[ResourceManager] Помилка запису файлу ${filePath}:`, error);
            return false;
        }
    }
    async ensureDirectory(dirPath) {
        try {
            await fs.ensureDir(dirPath);
            return true;
        }
        catch (error) {
            console.error(`[ResourceManager] Помилка створення директорії ${dirPath}:`, error);
            return false;
        }
    }
    async listDirectory(dirPath) {
        try {
            this.trackResourceUsage('fileOperations', 1);
            return await fs.readdir(dirPath);
        }
        catch (error) {
            console.error(`[ResourceManager] Помилка читання директорії ${dirPath}:`, error);
            return [];
        }
    }
    registerApiResource(name, config) {
        this.apiResources.set(name, config);
        console.log(`[ResourceManager] Зареєстровано API ресурс: ${name}`);
    }
    getApiResource(name) {
        return this.apiResources.get(name);
    }
    async fetchApiResource(apiName, endpoint, options) {
        const api = this.apiResources.get(apiName);
        if (!api) {
            throw new Error(`API ресурс ${apiName} не знайдено`);
        }
        this.trackResourceUsage('apiCalls', 1);
        const url = `${api.baseUrl}${endpoint}`;
        const headers = {
            ...api.headers,
            ...options?.headers
        };
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), api.timeout || 30000);
            const response = await fetch(url, {
                ...options,
                headers,
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const contentType = response.headers.get('content-type');
            if (contentType?.includes('application/json')) {
                return await response.json();
            }
            else {
                return await response.text();
            }
        }
        catch (error) {
            console.error(`[ResourceManager] Помилка API запиту до ${apiName}:`, error);
            throw error;
        }
    }
    getService(serviceName) {
        if (!this.serviceRegistry) {
            console.warn('[ResourceManager] ServiceRegistry не встановлено');
            return null;
        }
        return this.serviceRegistry.getService(serviceName);
    }
    async getDataStore() {
        if (!this.dataStore.initialized) {
            await this.dataStore.initialize();
        }
        return this.dataStore;
    }
    getEventBus() {
        return this.eventBus;
    }
    setResourceQuota(agentName, quota) {
        this.resourceQuotas.set(agentName, quota);
        console.log(`[ResourceManager] Встановлено квоту для ${agentName}`);
    }
    checkResourceQuota(agentName, resource) {
        const quota = this.resourceQuotas.get(agentName);
        if (!quota)
            return true;
        const usage = this.resourceUsage.get(`${agentName}:${resource}`) || 0;
        switch (resource) {
            case 'maxFileOperations':
                return !quota.maxFileOperations || usage < quota.maxFileOperations;
            case 'maxApiCalls':
                return !quota.maxApiCalls || usage < quota.maxApiCalls;
            default:
                return true;
        }
    }
    async executeCommand(command, options) {
        try {
            this.trackResourceUsage('commands', 1);
            const result = await execAsync(command, options);
            return {
                stdout: result.stdout.toString(),
                stderr: result.stderr.toString()
            };
        }
        catch (error) {
            console.error(`[ResourceManager] Помилка виконання команди:`, error);
            return { stdout: '', stderr: error.message };
        }
    }
    async getEnvironmentVariable(key) {
        return process.env[key];
    }
    async setEnvironmentVariable(key, value) {
        process.env[key] = value;
    }
    startResourceMonitoring(intervalMs = 60000) {
        if (this.monitoringInterval) {
            return;
        }
        this.monitoringInterval = setInterval(async () => {
            const resources = await this.getSystemResources();
            this.eventBus.publishSync('resource.monitoring', 'ResourceManager', resources);
            await this.dataStore.create('resource_monitoring', {
                timestamp: new Date(),
                resources
            });
            for (const [agentName, quota] of this.resourceQuotas) {
                if (quota.maxCpuPercent && resources.cpu.usage > quota.maxCpuPercent) {
                    this.eventBus.publishSync('resource.quota.exceeded', 'ResourceManager', {
                        agent: agentName,
                        resource: 'cpu',
                        usage: resources.cpu.usage,
                        limit: quota.maxCpuPercent
                    });
                }
                if (quota.maxMemoryMb) {
                    const usedMb = resources.memory.used / (1024 * 1024);
                    if (usedMb > quota.maxMemoryMb) {
                        this.eventBus.publishSync('resource.quota.exceeded', 'ResourceManager', {
                            agent: agentName,
                            resource: 'memory',
                            usage: usedMb,
                            limit: quota.maxMemoryMb
                        });
                    }
                }
            }
        }, intervalMs);
        console.log(`[ResourceManager] Моніторинг ресурсів запущено (інтервал: ${intervalMs}мс)`);
    }
    stopResourceMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
            console.log('[ResourceManager] Моніторинг ресурсів зупинено');
        }
    }
    trackResourceUsage(type, amount = 1) {
        const current = this.resourceUsage.get(type) || 0;
        this.resourceUsage.set(type, current + amount);
    }
    getResourceUsageStats() {
        return new Map(this.resourceUsage);
    }
    resetResourceUsage(type) {
        if (type) {
            this.resourceUsage.delete(type);
        }
        else {
            this.resourceUsage.clear();
        }
    }
    async cleanup() {
        this.stopResourceMonitoring();
        this.apiResources.clear();
        this.resourceQuotas.clear();
        this.resourceUsage.clear();
        console.log('[ResourceManager] Очищено');
    }
}
exports.ResourceManager = ResourceManager;
//# sourceMappingURL=ResourceManager.js.map