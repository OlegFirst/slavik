import { DigitalOfficeService, ServiceStatus } from '../types/ServiceInterface';
export declare class ServiceRegistry {
    private services;
    private serviceStatuses;
    private configPath;
    constructor(configPath?: string);
    registerService(service: DigitalOfficeService): Promise<void>;
    unregisterService(serviceName: string): Promise<void>;
    startService(serviceName: string): Promise<void>;
    stopService(serviceName: string): Promise<void>;
    startAllEnabledServices(): Promise<void>;
    stopAllServices(): Promise<void>;
    enableService(serviceName: string): Promise<void>;
    disableService(serviceName: string): Promise<void>;
    getService(serviceName: string): DigitalOfficeService | undefined;
    getAllServices(): DigitalOfficeService[];
    getEnabledServices(): DigitalOfficeService[];
    getRunningServices(): DigitalOfficeService[];
    getServiceStatus(serviceName: string): ServiceStatus | undefined;
    getAllServiceStatuses(): ServiceStatus[];
    performHealthChecks(): Promise<void>;
    private isServiceEnabled;
    private saveServiceConfig;
    private loadConfig;
}
//# sourceMappingURL=ServiceRegistry.d.ts.map