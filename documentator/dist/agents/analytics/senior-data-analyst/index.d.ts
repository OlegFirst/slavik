import { BaseAgent } from '../../../core/BaseAgent';
import { ScheduleConfig, AgentConfig } from '../../../types/AgentInterface';
export interface AnalysisConfig {
    projects: string[];
    analysisTypes: ('code-quality' | 'commits' | 'coverage' | 'performance' | 'dependencies')[];
    reportFormats: ('json' | 'html' | 'csv')[];
    outputPath: string;
    thresholds: {
        codeQuality: number;
        testCoverage: number;
        techDebt: number;
    };
}
export interface DataAnalystConfig extends AgentConfig {
    analysisInterval: number;
    projects: string[];
    outputPath: string;
    reportSchedule: {
        daily?: string;
        weekly?: string;
    };
    thresholds: {
        codeQuality: number;
        testCoverage: number;
        techDebt: number;
    };
    integrations: {
        github?: {
            enabled: boolean;
            token?: string;
        };
        sonarqube?: {
            enabled: boolean;
            url?: string;
            token?: string;
        };
    };
    machineLearning: {
        enabled: boolean;
        modelUpdateInterval?: number;
        predictionAccuracy?: number;
        autoOptimization?: boolean;
    };
    advancedAnalytics: {
        trendPrediction: boolean;
        anomalyDetection: boolean;
        riskAssessment: boolean;
        performancePrediction: boolean;
    };
}
export interface ProjectMetrics {
    projectName: string;
    timestamp: Date;
    codeQuality: {
        complexity: number;
        maintainabilityIndex: number;
        technicalDebt: number;
        codeSmells: number;
    };
    testing: {
        coverage: number;
        testCount: number;
        passRate: number;
    };
    development: {
        commits: number;
        contributors: number;
        linesOfCode: number;
        filesChanged: number;
    };
    performance: {
        buildTime: number;
        testTime: number;
        deploymentFrequency: number;
    };
}
export declare class SeniorDataAnalystAgent extends BaseAgent {
    private config;
    private analysisResults;
    private mlModels;
    private predictionCache;
    private anomalyDetector;
    private trendAnalyzer;
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
    private analyzeProject;
    private analyzeCodeQuality;
    private analyzeTestingMetrics;
    private analyzeDevelopmentMetrics;
    private analyzePerformanceMetrics;
    private getProjectStats;
    private calculateComplexity;
    private findTestFiles;
    private getCoverageData;
    private getGitStats;
    private getBuildMetrics;
    private isCodeFile;
    private isTestFile;
    private generateScheduledReports;
    private generateDailyReport;
    private generateWeeklyReport;
    private generateSummary;
    private analyzeTrends;
    private generateRecommendations;
    private checkThresholds;
    private updateDashboards;
    private calculateTrend;
    private saveProjectMetrics;
    private saveAllAnalysisResults;
    private getWeekString;
    private updateCommitMetrics;
    private updateTestMetrics;
    private updateBuildMetrics;
    getTools(): any[];
    private initializeMLComponents;
    private loadMLModels;
    private performMLAnalysis;
    private predictCodeQuality;
    private predictProjectTimeline;
    private generateOptimizationSuggestions;
    private detectAnomalies;
    private predictTrends;
    private assessRisks;
    private calculateQualityTrend;
    private calculateConfidence;
    private calculateVarianceFromMetrics;
    private calculateVelocity;
    private calculateTimelineConfidence;
    private identifyRiskFactors;
    private assessQualityRisk;
    private assessTimelineRisk;
    private assessPerformanceRisk;
    private handleAnomalies;
    private savePrediction;
    handleToolCall(toolName: string, args: any): Promise<any>;
    private loadHistoricalData;
    private saveCurrentState;
    private analyzeProjectWithMemory;
    private storeProjectMetricsInMemory;
    private getCachedAnalysis;
    private isCacheValid;
    private cacheAnalysisResult;
    private performMLAnalysisWithMemory;
    private enhancedMLPrediction;
    private storePredictionInMemory;
    private detectAnomaliesWithMemory;
    private createBaseline;
    private enhancedAnomalyDetection;
    private calculateEnhancedTrend;
    private calculateLinearTrend;
    private predictValue;
    private calculatePredictionConfidence;
    private calculateVariance;
    private assessProjectRisk;
    private generateEnhancedRecommendations;
    private calculateAnomalySeverity;
}
//# sourceMappingURL=index.d.ts.map