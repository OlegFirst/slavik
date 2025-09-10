import { ServiceRegistry } from './ServiceRegistry';
import { DigitalOfficeService } from '../types/ServiceInterface';
export declare class DigitalOfficeHub {
    private server;
    private serviceRegistry;
    private hubTools;
    constructor();
    private setupHubTools;
    private setupToolHandlers;
    private handleHubToolCall;
    private handleListServices;
    private handleServiceStatus;
    private handleEnableService;
    private handleDisableService;
    private handleStartService;
    private handleStopService;
    private handleHealthCheck;
    registerService(service: DigitalOfficeService): Promise<void>;
    start(): Promise<void>;
    shutdown(): Promise<void>;
    getServiceRegistry(): ServiceRegistry;
}
//# sourceMappingURL=DigitalOfficeHub.d.ts.map