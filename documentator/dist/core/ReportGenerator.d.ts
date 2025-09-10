import { ReportRequest, ReportResponse, Template, ProjectAnalysis } from '../types';
export declare class ReportGenerator {
    generateReport(request: ReportRequest, template: Template, projectAnalysis: ProjectAnalysis): Promise<ReportResponse>;
    private processTemplate;
    private processDefaultValues;
    private processConditionals;
    private processLoops;
    private generateOutputPath;
    validateTemplate(template: Template): Promise<string[]>;
    private extractTemplateVariables;
}
//# sourceMappingURL=ReportGenerator.d.ts.map