import { BaseAgent } from './BaseAgent';
import { AgentScheduler } from './AgentScheduler';
import { AgentConfig, AgentStatus } from '../types/AgentInterface';
export interface AgentRegistryConfig {
    agentsConfigPath: string;
    enableAutoLoad: boolean;
    logLevel: 'info' | 'warn' | 'error';
}
export declare class AgentRegistry {
    private agents;
    private scheduler;
    private config;
    private initialized;
    constructor(scheduler: AgentScheduler, config?: AgentRegistryConfig);
    initialize(): Promise<void>;
    shutdown(): Promise<void>;
    registerAgent(agent: BaseAgent): Promise<void>;
    unregisterAgent(agentName: string): Promise<void>;
    enableAgent(agentName: string): Promise<void>;
    disableAgent(agentName: string): Promise<void>;
    pauseAgent(agentName: string): Promise<void>;
    resumeAgent(agentName: string): Promise<void>;
    executeAgentNow(agentName: string): Promise<void>;
    getAgent(agentName: string): BaseAgent | undefined;
    getAllAgents(): BaseAgent[];
    getAgentNames(): string[];
    getAgentStatus(agentName: string): AgentStatus | null;
    getAllAgentStatuses(): AgentStatus[];
    updateAgentConfig(agentName: string, config: Partial<AgentConfig>): Promise<void>;
    clearAgentErrors(agentName: string): Promise<void>;
    private ensureConfigFile;
    private loadAgentsFromConfig;
    private saveAgentConfig;
    private removeAgentConfig;
    getRegistryHealth(): {
        totalAgents: number;
        runningAgents: number;
        healthyAgents: number;
        schedulerRunning: boolean;
    };
    private log;
}
//# sourceMappingURL=AgentRegistry.d.ts.map