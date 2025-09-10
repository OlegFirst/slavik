import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { BaseService } from '../../core/BaseService';
import { ServiceMetadata } from '../../types/ServiceInterface';
export declare class DocumentatorService extends BaseService {
    metadata: ServiceMetadata;
    private projectAnalyzer;
    private reportGenerator;
    private projectManager;
    private documentChecker;
    private documentFiller;
    private projectCache;
    protected onInitialize(): Promise<void>;
    protected onShutdown(): Promise<void>;
    protected performHealthCheck(): Promise<boolean>;
    getTools(): Tool[];
    handleToolCall(toolName: string, args: any): Promise<any>;
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
    private handleCheckDocument;
    private formatErrorsSummary;
    private formatStructureInfo;
    private formatDetailedErrors;
    private handleFillDocument;
    private handleFillNextQuestion;
    private handleFillSubmitAnswer;
    private handleFillComplete;
    private handleFillCancel;
    private handleFillGetStatus;
}
//# sourceMappingURL=DocumentatorService.d.ts.map