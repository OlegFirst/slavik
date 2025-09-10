import { ProjectAnalysis } from '../types';
export interface ProjectInfo {
    id: string;
    name: string;
    path: string;
    description?: string;
    createdAt: Date;
    lastModified: Date;
    templatesCount: number;
    documentTypes: string[];
}
export interface CreateProjectRequest {
    name: string;
    description?: string;
    copyFromTemplate?: string;
}
export declare class ProjectManager {
    private projectsDir;
    private projectAnalyzer;
    constructor(baseDir?: string);
    private ensureProjectsDirectory;
    listProjects(): Promise<ProjectInfo[]>;
    getProject(projectId: string): Promise<ProjectInfo | null>;
    createProject(request: CreateProjectRequest): Promise<ProjectInfo>;
    deleteProject(projectId: string): Promise<boolean>;
    analyzeProject(projectId: string): Promise<ProjectAnalysis>;
    updateProjectMetadata(projectId: string, updates: Partial<{
        name: string;
        description: string;
    }>): Promise<ProjectInfo | null>;
    uploadFile(projectId: string, fileName: string, content: Buffer | string): Promise<string>;
    deleteFile(projectId: string, fileName: string): Promise<boolean>;
    getProjectFiles(projectId: string): Promise<string[]>;
    getProjectPath(projectId: string): string;
    private getProjectInfo;
    private createProjectStructure;
    private copyFromTemplate;
    private getFilesRecursively;
    private sanitizeProjectName;
}
//# sourceMappingURL=ProjectManager.d.ts.map