import { BaseService } from '../../core/BaseService';
import { ServiceMetadata } from '../../types/ServiceInterface';
import { Tool } from '@modelcontextprotocol/sdk/types.js';
export interface CalendarEvent {
    title: string;
    description?: string;
    startTime: Date | string;
    endTime?: Date | string;
    location?: string;
    attendees?: string[];
    reminders?: number[];
    recurrence?: 'daily' | 'weekly' | 'monthly' | 'yearly';
    timezone?: string;
}
export interface AsanaTask {
    name: string;
    notes?: string;
    dueDate?: Date | string;
    assignee?: string;
    project?: string;
    section?: string;
    tags?: string[];
    priority?: 'low' | 'medium' | 'high' | 'urgent';
    followers?: string[];
    customFields?: Record<string, any>;
}
export interface TodoistTask {
    content: string;
    description?: string;
    due?: {
        date: string;
        datetime?: string;
        timezone?: string;
    };
    priority?: 1 | 2 | 3 | 4;
    project?: string;
    labels?: string[];
    sectionId?: string;
}
export interface NotionTask {
    title: string;
    content?: string;
    status?: 'To Do' | 'In Progress' | 'Done';
    dueDate?: Date | string;
    assignee?: string;
    tags?: string[];
    priority?: 'Low' | 'Medium' | 'High';
    database?: string;
    properties?: Record<string, any>;
}
export interface JiraIssue {
    summary: string;
    description?: string;
    issueType: 'Task' | 'Bug' | 'Story' | 'Epic';
    project: string;
    assignee?: string;
    priority?: 'Lowest' | 'Low' | 'Medium' | 'High' | 'Highest';
    dueDate?: Date | string;
    labels?: string[];
    components?: string[];
    fixVersion?: string;
    epicLink?: string;
    storyPoints?: number;
}
export interface IntegrationConfig {
    calendar?: {
        provider: 'google' | 'outlook' | 'apple' | 'caldav';
        defaultCalendar?: string;
        defaultReminders?: number[];
    };
    taskManagement?: {
        provider: 'asana' | 'todoist' | 'notion' | 'jira' | 'trello';
        defaultProject?: string;
        defaultAssignee?: string;
    };
    notifications?: {
        enabled: boolean;
        channels?: ('email' | 'slack' | 'teams' | 'discord')[];
    };
}
export declare class IntegrationService extends BaseService {
    metadata: ServiceMetadata;
    private config;
    private eventsQueue;
    private tasksQueue;
    private dataPath;
    constructor(config?: IntegrationConfig);
    private loadDefaultConfig;
    protected onInitialize(): Promise<void>;
    protected onShutdown(): Promise<void>;
    protected performHealthCheck(): Promise<boolean>;
    handleToolCall(toolName: string, args: any): Promise<any>;
    getTools(): Tool[];
    createCalendarEvent(event: CalendarEvent): Promise<any>;
    createAsanaTask(task: AsanaTask): Promise<any>;
    createNotionTask(task: NotionTask): Promise<any>;
    createJiraIssue(issue: JiraIssue): Promise<any>;
    createTodoistTask(task: TodoistTask): Promise<any>;
    getIntegrationStatus(): Promise<any>;
    private calculateEndTime;
    private isExternalMCPAvailable;
    private sendToExternalMCP;
    private logActivity;
    private countStoredItems;
    createMultipleEvents(events: CalendarEvent[]): Promise<any[]>;
    createMultipleTasks(tasks: Array<AsanaTask | NotionTask | JiraIssue | TodoistTask>, provider: string): Promise<any[]>;
    scheduleAgentMeeting(title: string, participants: string[], duration?: number, description?: string): Promise<any>;
    createAgentTask(title: string, description: string, priority?: 'low' | 'medium' | 'high' | 'urgent', dueDate?: Date): Promise<any>;
    private findNextAvailableSlot;
    private getDefaultDueDate;
    private mapPriorityToJira;
}
//# sourceMappingURL=IntegrationService.d.ts.map