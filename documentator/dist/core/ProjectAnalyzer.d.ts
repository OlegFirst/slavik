import { ProjectAnalysis } from '../types';
export declare class ProjectAnalyzer {
    private supportedExtensions;
    private templatePatterns;
    analyzeProject(projectPath: string): Promise<ProjectAnalysis>;
    private scanDirectory;
    private isTemplate;
    private analyzeTemplate;
    private analyzeMarkdownTemplate;
    private extractVariables;
    private extractStructure;
    private extractVariablesFromLine;
    private generateTemplateId;
    private generateSectionId;
}
//# sourceMappingURL=ProjectAnalyzer.d.ts.map