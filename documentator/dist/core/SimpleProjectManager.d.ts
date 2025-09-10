import { ProjectAnalysis } from '../types';
import { TemplateGenerationResult } from './TemplateGenerator';
export interface SimpleProjectInfo {
    id: string;
    name: string;
    path: string;
}
export declare class SimpleProjectManager {
    private projectsDir;
    private projectAnalyzer;
    private templateGenerator;
    constructor(baseDir?: string);
    private ensureProjectsDirectory;
    listProjects(): Promise<SimpleProjectInfo[]>;
    analyzeProject(projectId: string): Promise<ProjectAnalysis>;
    getProjectPath(projectId: string): string;
    projectExists(projectId: string): Promise<boolean>;
    getProjectsDirectory(): string;
    generateTemplatesForProject(projectId: string, templateBaseName?: string): Promise<TemplateGenerationResult[]>;
    saveGeneratedTemplate(projectId: string, template: TemplateGenerationResult): Promise<string>;
}
//# sourceMappingURL=SimpleProjectManager.d.ts.map