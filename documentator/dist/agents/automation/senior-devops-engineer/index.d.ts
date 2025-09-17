import { BaseAgent } from '../../../core/BaseAgent';
import { ScheduleConfig, AgentConfig } from '../../../types/AgentInterface';
export interface DevOpsConfig extends AgentConfig {
    deploymentInterval: number;
    monitoringInterval: number;
    environments: {
        [key: string]: {
            type: string;
            autoDeployBranch?: string;
            requireApproval?: boolean;
        };
    };
    alerting: {
        slack?: {
            webhook: string;
            channel: string;
        };
    };
    cloudProviders: {
        aws?: {
            enabled: boolean;
            region: string;
            accessKeyId?: string;
            secretAccessKey?: string;
        };
        azure?: {
            enabled: boolean;
            subscriptionId?: string;
            clientId?: string;
            clientSecret?: string;
            tenantId?: string;
        };
        gcp?: {
            enabled: boolean;
            projectId?: string;
            keyFile?: string;
        };
        docker?: {
            enabled: boolean;
            registry: string;
            username?: string;
            token?: string;
        };
    };
    kubernetes: {
        enabled: boolean;
        configPath?: string;
        namespace?: string;
        autoScaling?: boolean;
    };
    monitoring: {
        prometheus?: {
            enabled: boolean;
            endpoint?: string;
        };
        grafana?: {
            enabled: boolean;
            endpoint?: string;
        };
        elk?: {
            enabled: boolean;
            elasticsearchUrl?: string;
        };
    };
    security: {
        vulnerabilityScanning: boolean;
        secretScanning: boolean;
        complianceChecks: boolean;
        accessControlAudits: boolean;
    };
    automation: {
        autoScaling: boolean;
        selfHealing: boolean;
        loadBalancing: boolean;
        backupAutomation: boolean;
    };
}
export declare class SeniorDevOpsEngineerAgent extends BaseAgent {
    private config;
    private cloudClients;
    private kubernetesClient;
    private monitoringClients;
    private deploymentHistory;
    private infrastructureMetrics;
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
    private initializeCloudClients;
    private initializeKubernetesClient;
    private initializeMonitoringClients;
    private checkInfrastructure;
    private checkAWSInfrastructure;
    private checkAzureInfrastructure;
    private checkGCPInfrastructure;
    private checkDockerInfrastructure;
    private monitorKubernetesClusters;
    private getKubernetesClusterStatus;
    private getKubernetesPodStatus;
    private getKubernetesNodeStatus;
    private checkPendingDeployments;
    private getPendingDeployments;
    private shouldAutoApproveDeployment;
    private approveDeployment;
    private performAutoScaling;
    private scaleUp;
    private scaleDown;
    private performSelfHealing;
    private detectUnhealthyServices;
    private healService;
    private restartService;
    private scaleService;
    private performScheduledBackups;
    private backupDatabases;
    private backupConfigurations;
    private backupApplicationData;
    private performSecurityScans;
    private scanForVulnerabilities;
    private scanForSecrets;
    private performComplianceChecks;
    private auditAccessControls;
    private optimizeCloudResources;
    private identifyOptimizations;
    private applyOptimization;
    private generateInfrastructureInsights;
    private saveInfrastructureStatus;
    private saveKubernetesStatus;
    private saveInfrastructureInsights;
    private checkInfrastructureAlerts;
    private checkKubernetesAutoScaling;
    private analyzeCostOptimization;
    private analyzePerformance;
    private generateSecurityRecommendations;
    private generateScalingRecommendations;
    private handleBuildSuccess;
    private handleTestsPassed;
    private handleQualityGateFailed;
    private handleInfrastructureAlert;
    private considerRollback;
    private cleanupOldData;
    private sendSlackAlert;
    private getTargetEnvironment;
    private deployApplication;
    getTools(): any[];
    handleToolCall(toolName: string, args: any): Promise<any>;
    private handleKubernetesAction;
    private performBackup;
    private performSecurityScan;
}
//# sourceMappingURL=index.d.ts.map