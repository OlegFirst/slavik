import { BaseAgent } from '../../../core/BaseAgent';
import { ScheduleConfig, AgentConfig } from '../../../types/AgentInterface';
export interface SmartQAConfig extends AgentConfig {
    testFrameworks: {
        unit: string;
        e2e: string;
        api: string;
        performance: string;
    };
    qualityGates: {
        unitTestCoverage: number;
        codeComplexity: number;
        duplicatedLines: number;
        securityHotspots: number;
        bugs: number;
    };
    testEnvironments: {
        [key: string]: {
            baseUrl: string;
            database?: string;
            apiKeys?: {
                [key: string]: string;
            };
        };
    };
    integrations: {
        jira: {
            enabled: boolean;
            url?: string;
            token?: string;
            autoBugReporting: boolean;
        };
        sonarqube: {
            enabled: boolean;
            url?: string;
            token?: string;
        };
        slack: {
            enabled: boolean;
            webhook?: string;
            channel: string;
        };
    };
    aiTesting: {
        enabled: boolean;
        testGeneration: boolean;
        bugPrediction: boolean;
        flakyTestDetection: boolean;
        smartTestSelection: boolean;
    };
    notifications: {
        testFailures: boolean;
        qualityGateFailures: boolean;
        newBugsFound: boolean;
        coverageDrops: boolean;
    };
}
export interface TestResult {
    id: string;
    testSuite: string;
    testCase: string;
    status: 'passed' | 'failed' | 'skipped' | 'flaky';
    duration: number;
    errorMessage?: string;
    stackTrace?: string;
    screenshot?: string;
    logs?: string[];
    coverage?: CoverageData;
    timestamp: Date;
    environment: string;
    browser?: string;
    retry?: number;
}
export interface CoverageData {
    statements: number;
    branches: number;
    functions: number;
    lines: number;
    files: {
        [filename: string]: FileCoverage;
    };
}
export interface FileCoverage {
    lines: number;
    covered: number;
    percentage: number;
    uncoveredLines: number[];
}
export interface BugReport {
    id: string;
    title: string;
    description: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
    priority: 'urgent' | 'high' | 'medium' | 'low';
    status: 'open' | 'in_progress' | 'resolved' | 'closed';
    assignee?: string;
    reporter: string;
    steps: string[];
    expectedResult: string;
    actualResult: string;
    environment: string;
    browser?: string;
    attachments: string[];
    tags: string[];
    createdAt: Date;
    updatedAt: Date;
    resolvedAt?: Date;
}
export interface QualityMetrics {
    testCoverage: {
        overall: number;
        unit: number;
        integration: number;
        e2e: number;
    };
    codeQuality: {
        complexity: number;
        duplicatedLines: number;
        codeSmells: number;
        maintainabilityIndex: number;
    };
    testHealth: {
        totalTests: number;
        passingTests: number;
        flakyTests: number;
        averageExecutionTime: number;
    };
    bugs: {
        openBugs: number;
        resolvedBugs: number;
        bugRate: number;
        averageResolutionTime: number;
    };
    trends: {
        coverageTrend: number[];
        bugTrend: number[];
        testStabilityTrend: number[];
    };
}
export interface TestGenerationRequest {
    sourceFile: string;
    testType: 'unit' | 'integration' | 'e2e';
    framework: string;
    includeEdgeCases: boolean;
    mockDependencies: boolean;
}
export interface SmartTestSuite {
    id: string;
    name: string;
    tests: GeneratedTest[];
    coverage: number;
    aiGenerated: boolean;
    lastUpdated: Date;
}
export interface GeneratedTest {
    name: string;
    description: string;
    code: string;
    testType: 'unit' | 'integration' | 'e2e';
    confidence: number;
    edgeCases: string[];
    dependencies: string[];
}
export declare class SmartQAEngineerAgent extends BaseAgent {
    private config;
    private testResults;
    private bugReports;
    private qualityMetrics;
    private flakyTests;
    private aiModels;
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
    protected executeAutonomously(): Promise<void>;
    private initializeAITestingModels;
    private executeSmartTestSelection;
    private predictPotentialBugs;
    private analyzeFlakyTests;
    private generateMissingTests;
    runTestSuite(projectPath: string, options: any): Promise<TestResult[]>;
    analyzeCodeQuality(projectPath: string, options: any): Promise<any>;
    generateTestCases(sourceFile: string, options: TestGenerationRequest): Promise<GeneratedTest[]>;
    reportBug(bugData: Partial<BugReport>): Promise<BugReport>;
    private trainFlakyTestPredictor;
    private trainBugPredictor;
    private initializeTestGenerator;
    private loadHistoricalQAData;
    private generateId;
    getTools(): any[];
    handleToolCall(toolName: string, args: any): Promise<any>;
    private setupQAEventListeners;
    private saveTestResults;
    private saveQualityMetrics;
    private saveAIInsights;
    private executeScheduledTests;
    private analyzeQualityMetrics;
    private processAutomatedBugReports;
    private detectPerformanceRegressions;
    private performSecurityScanning;
    private coordinateWithOtherAgents;
    private getRecentCodeChanges;
    private selectRelevantTests;
    private executeTestSuite;
    private processTestResults;
    private getTotalTestCount;
    private getCurrentCoverage;
    private analyzeCodeMetrics;
    private calculateBugProbability;
    private createPredictedBugReport;
    private generateBugPreventionRecommendations;
    private getRecentTestResults;
    private identifyFlakyTestCandidates;
    private analyzeFlakyTestPattern;
    private createFlakyTestBugReport;
    private identifyUncoveredCode;
    private generateTestsForFile;
    private estimateTestCoverage;
    private saveGeneratedTestSuite;
    private runUnitTests;
    private runIntegrationTests;
    private runE2ETests;
    private runPerformanceTests;
    private storeTestResults;
    private updateQualityMetrics;
    private generateTestSummary;
    private analyzeCoverage;
    private analyzeComplexity;
    private analyzeDuplication;
    private analyzeCodeSmells;
    private analyzeSecurity;
    private analyzeMaintainability;
    private checkQualityGates;
    private getFailedQualityGates;
    private generateTestsFromSource;
    private createJiraBug;
    private getUnitTestTemplates;
    private getIntegrationTestTemplates;
    private getE2ETestTemplates;
    private getTestPatterns;
    private trainSmartTestSelector;
    private generateTestInsights;
    private generateQualityPredictions;
    private predictBugsForProject;
    private detectFlakyTestsForProject;
    private generateQualityInsights;
}
export declare function createSmartQAEngineer(config?: Partial<SmartQAConfig>): Promise<SmartQAEngineerAgent>;
//# sourceMappingURL=index.d.ts.map