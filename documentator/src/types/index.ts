export interface ProjectAnalysis {
  projectPath: string;
  projectName: string;
  documentTypes: string[];
  templates: Template[];
  lastAnalyzed: Date;
}

export interface Template {
  id: string;
  name: string;
  type: string;
  filePath: string;
  variables: Variable[];
  structure: TemplateStructure;
}

export interface Variable {
  name: string;
  type: 'string' | 'number' | 'date' | 'array' | 'object';
  required: boolean;
  defaultValue?: any;
  description?: string;
}

export interface TemplateStructure {
  sections: Section[];
  format: 'markdown' | 'docx' | 'pdf' | 'html';
}

export interface Section {
  id: string;
  title: string;
  content: string;
  variables: string[];
  subsections?: Section[];
}

export interface ReportRequest {
  templateId: string;
  projectPath: string;
  variables: Record<string, any>;
  outputPath?: string;
  format?: 'markdown' | 'docx' | 'pdf' | 'html';
}

export interface ReportResponse {
  success: boolean;
  outputPath?: string;
  error?: string;
  generatedAt: Date;
}

export interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'user';
  createdAt: Date;
}

export interface AuthToken {
  userId: string;
  username: string;
  role: string;
  iat: number;
  exp: number;
}

// Re-export service types for convenience
export * from './ServiceInterface';