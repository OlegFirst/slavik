import { EventBus } from './EventBus';
import { DataStore } from './DataStore';
import { ServiceRegistry } from './ServiceRegistry';
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
export declare class ResourceManager {
    private static instance;
    private eventBus;
    private dataStore;
    private serviceRegistry;
    private apiResources;
    private resourceQuotas;
    private resourceUsage;
    private monitoringInterval;
    private constructor();
    static getInstance(): ResourceManager;
    setServiceRegistry(registry: ServiceRegistry): void;
    getSystemResources(): Promise<SystemResources>;
    getFileResource(filePath: string): Promise<FileResource>;
    readFile(filePath: string, encoding?: BufferEncoding): Promise<string | null>;
    writeFile(filePath: string, content: string): Promise<boolean>;
    ensureDirectory(dirPath: string): Promise<boolean>;
    listDirectory(dirPath: string): Promise<string[]>;
    registerApiResource(name: string, config: ApiResource): void;
    getApiResource(name: string): ApiResource | undefined;
    fetchApiResource(apiName: string, endpoint: string, options?: RequestInit): Promise<any>;
    getService(serviceName: string): any;
    getDataStore(): Promise<DataStore>;
    getEventBus(): EventBus;
    setResourceQuota(agentName: string, quota: ResourceQuota): void;
    checkResourceQuota(agentName: string, resource: keyof ResourceQuota): boolean;
    executeCommand(command: string, options?: any): Promise<{
        stdout: string;
        stderr: string;
    }>;
    getEnvironmentVariable(key: string): Promise<string | undefined>;
    setEnvironmentVariable(key: string, value: string): Promise<void>;
    startResourceMonitoring(intervalMs?: number): void;
    stopResourceMonitoring(): void;
    private trackResourceUsage;
    getResourceUsageStats(): Map<string, any>;
    resetResourceUsage(type?: string): void;
    cleanup(): Promise<void>;
}
//# sourceMappingURL=ResourceManager.d.ts.map