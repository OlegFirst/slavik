import * as fs from 'fs-extra';
import * as path from 'path';
import * as os from 'os';
import { EventBus } from './EventBus';
import { DataStore } from './DataStore';
import { ServiceRegistry } from './ServiceRegistry';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export interface SystemResources {
  cpu: {
    usage: number;
    cores: number;
  };
  memory: {
    total: number;
    free: number;
    used: number;
    usagePercent: number;
  };
  disk: {
    total: number;
    free: number;
    used: number;
    usagePercent: number;
  };
  network: {
    interfaces: string[];
  };
}

export interface FileResource {
  path: string;
  exists: boolean;
  size?: number;
  isDirectory?: boolean;
  permissions?: string;
  lastModified?: Date;
}

export interface ApiResource {
  name: string;
  baseUrl: string;
  headers?: Record<string, string>;
  timeout?: number;
}

export interface ResourceQuota {
  maxCpuPercent?: number;
  maxMemoryMb?: number;
  maxDiskMb?: number;
  maxFileOperations?: number;
  maxApiCalls?: number;
}

export class ResourceManager {
  private static instance: ResourceManager;
  private eventBus: EventBus;
  private dataStore: DataStore;
  private serviceRegistry: ServiceRegistry | null = null;
  private apiResources: Map<string, ApiResource> = new Map();
  private resourceQuotas: Map<string, ResourceQuota> = new Map();
  private resourceUsage: Map<string, any> = new Map();
  private monitoringInterval: NodeJS.Timeout | null = null;

  private constructor() {
    this.eventBus = EventBus.getInstance();
    this.dataStore = DataStore.getInstance();
  }

  static getInstance(): ResourceManager {
    if (!ResourceManager.instance) {
      ResourceManager.instance = new ResourceManager();
    }
    return ResourceManager.instance;
  }

  setServiceRegistry(registry: ServiceRegistry): void {
    this.serviceRegistry = registry;
  }

  async getSystemResources(): Promise<SystemResources> {
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
      } else {
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
    } catch (error) {
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

  async getFileResource(filePath: string): Promise<FileResource> {
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
    } catch (error) {
      console.error(`[ResourceManager] Помилка доступу до файлу ${filePath}:`, error);
      return { path: absolutePath, exists: false };
    }
  }

  async readFile(filePath: string, encoding: BufferEncoding = 'utf8'): Promise<string | null> {
    try {
      this.trackResourceUsage('fileOperations', 1);
      return await fs.readFile(filePath, encoding);
    } catch (error) {
      console.error(`[ResourceManager] Помилка читання файлу ${filePath}:`, error);
      return null;
    }
  }

  async writeFile(filePath: string, content: string): Promise<boolean> {
    try {
      this.trackResourceUsage('fileOperations', 1);
      await fs.writeFile(filePath, content);

      this.eventBus.publishSync('resource.file.written', 'ResourceManager', {
        path: filePath,
        size: content.length
      });

      return true;
    } catch (error) {
      console.error(`[ResourceManager] Помилка запису файлу ${filePath}:`, error);
      return false;
    }
  }

  async ensureDirectory(dirPath: string): Promise<boolean> {
    try {
      await fs.ensureDir(dirPath);
      return true;
    } catch (error) {
      console.error(`[ResourceManager] Помилка створення директорії ${dirPath}:`, error);
      return false;
    }
  }

  async listDirectory(dirPath: string): Promise<string[]> {
    try {
      this.trackResourceUsage('fileOperations', 1);
      return await fs.readdir(dirPath);
    } catch (error) {
      console.error(`[ResourceManager] Помилка читання директорії ${dirPath}:`, error);
      return [];
    }
  }

  registerApiResource(name: string, config: ApiResource): void {
    this.apiResources.set(name, config);
    console.log(`[ResourceManager] Зареєстровано API ресурс: ${name}`);
  }

  getApiResource(name: string): ApiResource | undefined {
    return this.apiResources.get(name);
  }

  async fetchApiResource(
    apiName: string,
    endpoint: string,
    options?: RequestInit
  ): Promise<any> {
    const api = this.apiResources.get(apiName);

    if (!api) {
      throw new Error(`API ресурс ${apiName} не знайдено`);
    }

    this.trackResourceUsage('apiCalls', 1);

    const url = `${api.baseUrl}${endpoint}`;
    const headers = {
      ...api.headers,
      ...(options?.headers as Record<string, string>)
    };

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(
        () => controller.abort(),
        api.timeout || 30000
      );

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
      } else {
        return await response.text();
      }
    } catch (error) {
      console.error(`[ResourceManager] Помилка API запиту до ${apiName}:`, error);
      throw error;
    }
  }

  getService(serviceName: string): any {
    if (!this.serviceRegistry) {
      console.warn('[ResourceManager] ServiceRegistry не встановлено');
      return null;
    }

    return this.serviceRegistry.getService(serviceName);
  }

  async getDataStore(): Promise<DataStore> {
    if (!(this.dataStore as any).initialized) {
      await this.dataStore.initialize();
    }
    return this.dataStore;
  }

  getEventBus(): EventBus {
    return this.eventBus;
  }

  setResourceQuota(agentName: string, quota: ResourceQuota): void {
    this.resourceQuotas.set(agentName, quota);
    console.log(`[ResourceManager] Встановлено квоту для ${agentName}`);
  }

  checkResourceQuota(agentName: string, resource: keyof ResourceQuota): boolean {
    const quota = this.resourceQuotas.get(agentName);
    if (!quota) return true;

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

  async executeCommand(command: string, options?: any): Promise<{ stdout: string; stderr: string }> {
    try {
      this.trackResourceUsage('commands', 1);
      const result = await execAsync(command, options);
      return {
        stdout: result.stdout.toString(),
        stderr: result.stderr.toString()
      };
    } catch (error: any) {
      console.error(`[ResourceManager] Помилка виконання команди:`, error);
      return { stdout: '', stderr: error.message };
    }
  }

  async getEnvironmentVariable(key: string): Promise<string | undefined> {
    return process.env[key];
  }

  async setEnvironmentVariable(key: string, value: string): Promise<void> {
    process.env[key] = value;
  }

  startResourceMonitoring(intervalMs: number = 60000): void {
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

  stopResourceMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
      console.log('[ResourceManager] Моніторинг ресурсів зупинено');
    }
  }

  private trackResourceUsage(type: string, amount: number = 1): void {
    const current = this.resourceUsage.get(type) || 0;
    this.resourceUsage.set(type, current + amount);
  }

  getResourceUsageStats(): Map<string, any> {
    return new Map(this.resourceUsage);
  }

  resetResourceUsage(type?: string): void {
    if (type) {
      this.resourceUsage.delete(type);
    } else {
      this.resourceUsage.clear();
    }
  }

  async cleanup(): Promise<void> {
    this.stopResourceMonitoring();
    this.apiResources.clear();
    this.resourceQuotas.clear();
    this.resourceUsage.clear();
    console.log('[ResourceManager] Очищено');
  }
}