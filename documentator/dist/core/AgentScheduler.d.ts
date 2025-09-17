import { BaseAgent } from './BaseAgent';
export declare class AgentScheduler {
    private agents;
    private intervals;
    private timeouts;
    private running;
    start(): Promise<void>;
    stop(): Promise<void>;
    registerAgent(agent: BaseAgent): Promise<void>;
    unregisterAgent(agentName: string): Promise<void>;
    private scheduleAgent;
    private scheduleInterval;
    private scheduleCron;
    private scheduleOnce;
    private scheduleEventDriven;
    private unscheduleAgent;
    getScheduledAgents(): string[];
    getAgentStatus(agentName: string): import("../types/AgentInterface").AgentStatus | null;
    executeAgentNow(agentName: string): Promise<void>;
    pauseAgent(agentName: string): Promise<void>;
    resumeAgent(agentName: string): Promise<void>;
    isRunning(): boolean;
}
//# sourceMappingURL=AgentScheduler.d.ts.map