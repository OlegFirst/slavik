import { DigitalOfficeService, ServiceMetadata, ServiceStatus } from '../types/ServiceInterface';
import { Tool } from '@modelcontextprotocol/sdk/types.js';
export declare abstract class BaseService implements DigitalOfficeService {
    abstract metadata: ServiceMetadata;
    private initialized;
    private healthy;
    initialize(): Promise<void>;
    shutdown(): Promise<void>;
    isHealthy(): Promise<boolean>;
    getStatus(): ServiceStatus;
    protected abstract onInitialize(): Promise<void>;
    protected abstract onShutdown(): Promise<void>;
    protected performHealthCheck(): Promise<boolean>;
    getTools(): Tool[];
    handleToolCall(toolName: string, args: any): Promise<any>;
}
//# sourceMappingURL=BaseService.d.ts.map