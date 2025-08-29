import * as fs from 'fs-extra';
import * as path from 'path';
import { ProjectAnalysis, Template, Variable, TemplateStructure, Section } from '../types';

export class ProjectAnalyzer {
  private supportedExtensions = ['.md', '.txt', '.docx', '.pdf', '.html'];
  private templatePatterns = [
    /template/i,
    /шаблон/i,
    /звіт/i,
    /report/i,
    /документ/i,
    /document/i
  ];

  async analyzeProject(projectPath: string): Promise<ProjectAnalysis> {
    if (!await fs.pathExists(projectPath)) {
      throw new Error(`Шлях проекту не існує: ${projectPath}`);
    }

    const projectName = path.basename(projectPath);
    const documentTypes: string[] = [];
    const templates: Template[] = [];

    await this.scanDirectory(projectPath, documentTypes, templates);

    return {
      projectPath,
      projectName,
      documentTypes: [...new Set(documentTypes)],
      templates,
      lastAnalyzed: new Date()
    };
  }

  private async scanDirectory(dirPath: string, documentTypes: string[], templates: Template[]): Promise<void> {
    const items = await fs.readdir(dirPath, { withFileTypes: true });

    for (const item of items) {
      const fullPath = path.join(dirPath, item.name);

      if (item.isDirectory()) {
        await this.scanDirectory(fullPath, documentTypes, templates);
      } else if (item.isFile()) {
        const ext = path.extname(item.name).toLowerCase();
        
        if (this.supportedExtensions.includes(ext)) {
          documentTypes.push(ext);

          if (this.isTemplate(item.name)) {
            const template = await this.analyzeTemplate(fullPath);
            if (template) {
              templates.push(template);
            }
          }
        }
      }
    }
  }

  private isTemplate(fileName: string): boolean {
    return this.templatePatterns.some(pattern => pattern.test(fileName));
  }

  private async analyzeTemplate(filePath: string): Promise<Template | null> {
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      const ext = path.extname(filePath).toLowerCase();
      
      if (ext === '.md') {
        return this.analyzeMarkdownTemplate(filePath, content);
      }
      
      return null;
    } catch (error) {
      console.error(`Помилка аналізу шаблону ${filePath}:`, error);
      return null;
    }
  }

  private analyzeMarkdownTemplate(filePath: string, content: string): Template {
    const variables = this.extractVariables(content);
    const structure = this.extractStructure(content);
    
    return {
      id: this.generateTemplateId(filePath),
      name: path.basename(filePath, path.extname(filePath)),
      type: 'markdown',
      filePath,
      variables,
      structure
    };
  }

  private extractVariables(content: string): Variable[] {
    const variables: Variable[] = [];
    const variablePattern = /\{\{(\w+)(?::(\w+))?(?:\|(.+?))?\}\}/g;
    const matches = content.matchAll(variablePattern);

    for (const match of matches) {
      const name = match[1];
      const type = (match[2] as any) || 'string';
      const defaultValue = match[3];

      if (!variables.find(v => v.name === name)) {
        variables.push({
          name,
          type,
          required: !defaultValue,
          defaultValue,
          description: `Змінна ${name} типу ${type}`
        });
      }
    }

    return variables;
  }

  private extractStructure(content: string): TemplateStructure {
    const sections: Section[] = [];
    const lines = content.split('\n');
    let currentSection: Section | null = null;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      if (line.startsWith('#')) {
        if (currentSection) {
          sections.push(currentSection);
        }

        const level = line.match(/^#+/)?.[0].length || 1;
        const title = line.replace(/^#+\s*/, '');
        
        currentSection = {
          id: this.generateSectionId(title),
          title,
          content: '',
          variables: []
        };
      } else if (currentSection && line) {
        currentSection.content += line + '\n';
        
        const variables = this.extractVariablesFromLine(line);
        currentSection.variables.push(...variables);
      }
    }

    if (currentSection) {
      sections.push(currentSection);
    }

    return {
      sections,
      format: 'markdown'
    };
  }

  private extractVariablesFromLine(line: string): string[] {
    const variables: string[] = [];
    const variablePattern = /\{\{(\w+)(?::(\w+))?(?:\|(.+?))?\}\}/g;
    const matches = line.matchAll(variablePattern);

    for (const match of matches) {
      variables.push(match[1]);
    }

    return variables;
  }

  private generateTemplateId(filePath: string): string {
    return Buffer.from(filePath).toString('base64').replace(/[^a-zA-Z0-9]/g, '').substring(0, 16);
  }

  private generateSectionId(title: string): string {
    return title.toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();
  }
}