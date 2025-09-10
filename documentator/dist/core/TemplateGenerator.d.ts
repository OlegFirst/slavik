export interface TemplateGenerationResult {
    templateName: string;
    templateContent: string;
    extractedVariables: string[];
    originalDocument: string;
}
export declare class TemplateGenerator {
    generateTemplateFromDocument(documentPath: string, templateName?: string): Promise<TemplateGenerationResult>;
    private extractVariablesFromDocument;
    private replacePattern;
    generateTemplateFromProject(projectPath: string, templateName: string): Promise<TemplateGenerationResult[]>;
    private getAllDocuments;
    saveTemplate(projectPath: string, template: TemplateGenerationResult): Promise<string>;
}
//# sourceMappingURL=TemplateGenerator.d.ts.map