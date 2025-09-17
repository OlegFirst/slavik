import { BaseAgent } from '../../core/BaseAgent';
import { ScheduleConfig } from '../../types/AgentInterface';
import { ServiceMetadata } from '../../types/ServiceInterface';
/**
 * Приклад агента, який демонструє використання інтеграцій
 * з календарями та системами управління завданнями
 */
export declare class TaskPlannerAgent extends BaseAgent {
    metadata: ServiceMetadata;
    constructor();
    getScheduleConfig(): ScheduleConfig;
    protected onInitialize(): Promise<void>;
    protected onShutdown(): Promise<void>;
    protected performHealthCheck(): Promise<boolean>;
    protected executeAutonomously(): Promise<void>;
    private generateWeekPlan;
    private createWeeklyTasks;
    private scheduleWeeklyMeetings;
    private createReminders;
    private generatePlanningReport;
    private getNextMonday;
    private getNextDate;
    private getDayName;
    protected log(message: string, level?: 'info' | 'error' | 'warn'): void;
}
export default TaskPlannerAgent;
//# sourceMappingURL=TaskPlannerAgent.d.ts.map