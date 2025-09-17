import { Tool } from '@modelcontextprotocol/sdk/types.js';
export interface ServiceMetadata {
    name: string;
    version: string;
    description: string;
    author?: string;
    category?: string;
    dependencies?: string[];
    tags?: string[];
    status?: string;
}
export interface DigitalOfficeService {
    metadata: ServiceMetadata;
    initialize(): Promise<void>;
    shutdown(): Promise<void>;
    getTools(): Tool[];
    handleToolCall(toolName: string, args: any): Promise<any>;
    isHealthy(): Promise<boolean>;
    getStatus(): ServiceStatus;
}
export interface ServiceStatus {
    name: string;
    enabled: boolean;
    running: boolean;
    lastStarted?: Date;
    lastError?: string;
    healthCheck?: boolean;
}
export interface ServiceConfig {
    name: string;
    enabled: boolean;
    config?: Record<string, any>;
}
export interface DigitalOfficeConfig {
    services: ServiceConfig[];
    globalConfig: {
        logLevel: 'debug' | 'info' | 'warn' | 'error';
        apiPort?: number;
        mcpServerName?: string;
    };
}
//# sourceMappingURL=ServiceInterface.d.ts.map