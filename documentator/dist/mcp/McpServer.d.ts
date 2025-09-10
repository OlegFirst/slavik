export declare class McpServer {
    private server;
    private projectAnalyzer;
    private reportGenerator;
    private projectManager;
    private projectCache;
    constructor();
    private setupToolHandlers;
    private getAvailableTools;
    private handleAnalyzeProject;
    private handleListTemplates;
    private handleGetTemplateVariables;
    private handleGenerateReport;
    private getProjectAnalysis;
    private handleListProjects;
    private handleAnalyzeProjectById;
    private handleGenerateReportById;
    private handleGenerateTemplatesForProject;
    private handleSaveGeneratedTemplate;
    start(): Promise<void>;
}
//# sourceMappingURL=McpServer.d.ts.map