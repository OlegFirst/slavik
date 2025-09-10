export declare class ServiceManagerCLI {
    private serviceRegistry;
    constructor();
    initialize(): Promise<void>;
    listServices(filter?: 'all' | 'enabled' | 'running' | 'disabled'): Promise<void>;
    serviceStatus(serviceName: string): Promise<void>;
    enableService(serviceName: string): Promise<void>;
    disableService(serviceName: string): Promise<void>;
    startService(serviceName: string): Promise<void>;
    stopService(serviceName: string): Promise<void>;
    healthCheck(): Promise<void>;
    showConfig(): Promise<void>;
    createDefaultConfig(): Promise<void>;
}
//# sourceMappingURL=ServiceManager.d.ts.map