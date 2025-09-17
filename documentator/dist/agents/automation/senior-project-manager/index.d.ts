import { BaseAgent } from '../../../core/BaseAgent';
import { ScheduleConfig, AgentConfig } from '../../../types/AgentInterface';
export interface ProjectManagerConfig extends AgentConfig {
    reportingInterval: number;
    statusCheckInterval: number;
    defaultSprintDuration: number;
    integrations: {
        jira?: {
            enabled: boolean;
            url?: string;
            token?: string;
        };
        slack?: {
            enabled: boolean;
            webhook?: string;
            channel?: string;
        };
    };
}
export interface Task {
    id: string;
    title: string;
    description: string;
    status: 'todo' | 'in_progress' | 'review' | 'done';
    assignee?: string;
    estimatedHours: number;
    actualHours: number;
    priority: 'high' | 'medium' | 'low';
    createdAt: Date;
    updatedAt: Date;
}
export interface Project {
    id: string;
    name: string;
    description: string;
    status: 'planning' | 'active' | 'on_hold' | 'completed';
    startDate: Date;
    estimatedEndDate: Date;
    actualEndDate?: Date;
    team: string[];
    tasks: Task[];
}
export declare class SeniorProjectManagerAgent extends BaseAgent {
    private config;
    private projects;
    private currentSprint;
    metadata: {
        name: string;
        version: string;
        description: string;
        category: string;
    };
    constructor(config: AgentConfig);
    getScheduleConfig(): ScheduleConfig;
    protected onInitialize(): Promise<void>;
    protected onShutdown(): Promise<void>;
    executeAutonomously(): Promise<void>;
    private loadProjects;
    private saveProjects;
    private updateProjectStatuses;
    private analyzeSprint;
    private generateStatusReports;
    private planNextSprint;
    private assessRisks;
    private getActiveProjects;
    private getAllTasks;
    private getSprintTasks;
    private calculateProjectProgress;
    private updateTaskProgress;
    private updateProjectStatus;
    getTools(): any[];
    handleToolCall(toolName: string, args: any): Promise<any>;
}
//# sourceMappingURL=index.d.ts.map