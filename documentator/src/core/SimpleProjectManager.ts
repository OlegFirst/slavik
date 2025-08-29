import * as fs from 'fs-extra';
import * as path from 'path';
import * as os from 'os';
import { ProjectAnalysis } from '../types';
import { ProjectAnalyzer } from './ProjectAnalyzer';
import { TemplateGenerator, TemplateGenerationResult } from './TemplateGenerator';

export interface SimpleProjectInfo {
  id: string;
  name: string;
  path: string;
}

export class SimpleProjectManager {
  private projectsDir: string;
  private projectAnalyzer: ProjectAnalyzer;
  private templateGenerator: TemplateGenerator;

  constructor(baseDir?: string) {
    if (baseDir) {
      this.projectsDir = path.join(baseDir, 'projects');
    } else {
      // Використовуємо папку projects всередині Documentator
      // __dirname вказує на dist/core, тому йдемо на 2 рівні вгору до кореня проекту
      const documentatorRoot = path.resolve(__dirname, '..', '..');
      this.projectsDir = path.join(documentatorRoot, 'projects');
    }
    
    this.projectAnalyzer = new ProjectAnalyzer();
    this.templateGenerator = new TemplateGenerator();
    this.ensureProjectsDirectory();
  }

  private async ensureProjectsDirectory(): Promise<void> {
    await fs.ensureDir(this.projectsDir);
  }

  async listProjects(): Promise<SimpleProjectInfo[]> {
    await this.ensureProjectsDirectory();
    
    const projects: SimpleProjectInfo[] = [];
    const items = await fs.readdir(this.projectsDir, { withFileTypes: true });

    for (const item of items) {
      if (item.isDirectory()) {
        const projectPath = path.join(this.projectsDir, item.name);
        projects.push({
          id: item.name,
          name: item.name,
          path: projectPath
        });
      }
    }

    return projects;
  }

  async analyzeProject(projectId: string): Promise<ProjectAnalysis> {
    const projectPath = path.join(this.projectsDir, projectId);
    
    if (!await fs.pathExists(projectPath)) {
      throw new Error(`Проект "${projectId}" не знайдено`);
    }

    return await this.projectAnalyzer.analyzeProject(projectPath);
  }

  getProjectPath(projectId: string): string {
    return path.join(this.projectsDir, projectId);
  }

  async projectExists(projectId: string): Promise<boolean> {
    const projectPath = path.join(this.projectsDir, projectId);
    return await fs.pathExists(projectPath);
  }

  getProjectsDirectory(): string {
    return this.projectsDir;
  }

  async generateTemplatesForProject(projectId: string, templateBaseName?: string): Promise<TemplateGenerationResult[]> {
    const projectPath = path.join(this.projectsDir, projectId);
    
    if (!await fs.pathExists(projectPath)) {
      throw new Error(`Проект "${projectId}" не знайдено`);
    }

    const baseName = templateBaseName || `${projectId}-template`;
    return await this.templateGenerator.generateTemplateFromProject(projectPath, baseName);
  }

  async saveGeneratedTemplate(projectId: string, template: TemplateGenerationResult): Promise<string> {
    const projectPath = path.join(this.projectsDir, projectId);
    
    if (!await fs.pathExists(projectPath)) {
      throw new Error(`Проект "${projectId}" не знайдено`);
    }

    return await this.templateGenerator.saveTemplate(projectPath, template);
  }
}