import { BaseAgent } from '../../../core/BaseAgent';
import { ScheduleConfig, AgentConfig } from '../../../types/AgentInterface';
export interface QAConfig extends AgentConfig {
    testingInterval: number;
    qualityCheckInterval: number;
    qualityGates: {
        unitTestCoverage: number;
        codeComplexity: number;
        duplicatedLines: number;
        securityHotspots: number;
    };
    frameworks: {
        unit: string;
        e2e: string;
        api: string;
    };
}
export declare class QAEngineerAgent extends BaseAgent {
    private config;
    private testResults;
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
    private runScheduledTests;
    private runTestSuite;
    private simulateTestRun;
    private analyzeCodeQuality;
    private runCodeAnalysis;
    private generateTestCases;
    private checkQualityGates;
    private evaluateQualityGate;
    private reportResults;
    private calculateAverageCoverage;
    private getProjectsForTesting;
    private saveTestResults;
    private runTestsForCommit;
    private runDeploymentTests;
    getTools(): any[];
    handleToolCall(toolName: string, args: any): Promise<any>;
}
//# sourceMappingURL=index.d.ts.map