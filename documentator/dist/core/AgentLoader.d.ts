import { BaseAgent } from './BaseAgent';
import { AgentRegistry } from './AgentRegistry';
export interface AgentManifest {
    name: string;
    version: string;
    description: string;
    category: string;
    entryPoint: string;
    className: string;
    dependencies?: string[];
    config?: Record<string, any>;
    autoStart?: boolean;
    enabled?: boolean;
}
export interface LoadedAgent {
    manifest: AgentManifest;
    agentClass: typeof BaseAgent;
    instance?: BaseAgent;
    loadedAt: Date;
    error?: string;
}
export declare class AgentLoader {
    private agentsPath;
    private loadedAgents;
    private registry;
    private eventBus;
    private watchMode;
    private watcher;
    constructor(agentsPath: string, registry: AgentRegistry);
    initialize(): Promise<void>;
    loadAllAgents(): Promise<Map<string, LoadedAgent>>;
    loadAgent(manifestPath: string): Promise<LoadedAgent | null>;
    instantiateAgent(agentName: string): Promise<BaseAgent | null>;
    reloadAgent(agentName: string): Promise<boolean>;
    unloadAgent(agentName: string): Promise<boolean>;
    startWatching(): Promise<void>;
    stopWatching(): Promise<void>;
    getLoadedAgents(): LoadedAgent[];
    getAgentInfo(agentName: string): LoadedAgent | undefined;
    isAgentLoaded(agentName: string): boolean;
    getAgentsByCategory(category: string): LoadedAgent[];
    private createDefaultStructure;
    private getAgentCategories;
    private loadAgentsFromCategory;
    private instantiateEnabledAgents;
    private findAgentManifest;
    private getAgentNameFromManifest;
}
//# sourceMappingURL=AgentLoader.d.ts.map