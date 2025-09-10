export declare class ProjectInitializer {
    private projectManager;
    private projectsDir;
    constructor(baseDir?: string);
    initializeDefaultProjects(): Promise<void>;
    private createItReportsProject;
    private createBusinessPlansProject;
    private createTechDocsProject;
    private createFile;
    private projectExists;
}
//# sourceMappingURL=ProjectInitializer.d.ts.map