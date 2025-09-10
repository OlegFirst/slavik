import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { BaseService } from '../../core/BaseService';
import { ServiceMetadata } from '../../types/ServiceInterface';
export declare class PMService extends BaseService {
    metadata: ServiceMetadata;
    private contentGenerator;
    private outputDirectory;
    constructor();
    protected onInitialize(): Promise<void>;
    protected onShutdown(): Promise<void>;
    protected performHealthCheck(): Promise<boolean>;
    getTools(): Tool[];
    handleToolCall(toolName: string, args: any): Promise<any>;
    private handleRelease;
    private handlePoint;
    private handleListPrompts;
    private handleGetPromptInfo;
    private handleGenerateCustom;
    private startInteractiveSession;
    private buildInteractiveForm;
    private generateContent;
    private generateDefaultOutputPath;
    private generateJsonSchemaFromPrompt;
    private fieldToJsonSchema;
}
//# sourceMappingURL=PMService.d.ts.map