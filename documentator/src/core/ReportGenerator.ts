import * as fs from 'fs-extra';
import * as path from 'path';
import { ReportRequest, ReportResponse, Template, ProjectAnalysis } from '../types';

export class ReportGenerator {
  async generateReport(
    request: ReportRequest,
    template: Template,
    projectAnalysis: ProjectAnalysis
  ): Promise<ReportResponse> {
    try {
      const templateContent = await fs.readFile(template.filePath, 'utf-8');
      const processedContent = this.processTemplate(templateContent, request.variables);
      
      const outputPath = request.outputPath || this.generateOutputPath(
        projectAnalysis.projectPath,
        template.name,
        request.format || template.structure.format
      );

      await fs.ensureDir(path.dirname(outputPath));
      await fs.writeFile(outputPath, processedContent, 'utf-8');

      return {
        success: true,
        outputPath,
        generatedAt: new Date()
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Невідома помилка',
        generatedAt: new Date()
      };
    }
  }

  private processTemplate(content: string, variables: Record<string, any>): string {
    let processedContent = content;

    Object.entries(variables).forEach(([key, value]) => {
      const regex = new RegExp(`\\{\\{${key}(?::[^}]*)?(?:\\|[^}]*)?\\}\\}`, 'g');
      processedContent = processedContent.replace(regex, String(value));
    });

    processedContent = this.processDefaultValues(processedContent);
    processedContent = this.processConditionals(processedContent, variables);
    processedContent = this.processLoops(processedContent, variables);

    return processedContent;
  }

  private processDefaultValues(content: string): string {
    const defaultValuePattern = /\{\{(\w+)(?::(\w+))?\|(.+?)\}\}/g;
    
    return content.replace(defaultValuePattern, (match, varName, type, defaultValue) => {
      return defaultValue;
    });
  }

  private processConditionals(content: string, variables: Record<string, any>): string {
    const conditionalPattern = /\{\{#if\s+(\w+)\}\}(.*?)\{\{\/if\}\}/gs;
    
    return content.replace(conditionalPattern, (match, condition, block) => {
      const value = variables[condition];
      return value ? block : '';
    });
  }

  private processLoops(content: string, variables: Record<string, any>): string {
    const loopPattern = /\{\{#each\s+(\w+)\s+as\s+(\w+)\}\}(.*?)\{\{\/each\}\}/gs;
    
    return content.replace(loopPattern, (match, arrayName, itemName, block) => {
      const array = variables[arrayName];
      if (!Array.isArray(array)) return '';

      return array.map(item => {
        let processedBlock = block;
        if (typeof item === 'object') {
          Object.entries(item).forEach(([key, value]) => {
            const regex = new RegExp(`\\{\\{${itemName}\\.${key}\\}\\}`, 'g');
            processedBlock = processedBlock.replace(regex, String(value));
          });
        } else {
          const regex = new RegExp(`\\{\\{${itemName}\\}\\}`, 'g');
          processedBlock = processedBlock.replace(regex, String(item));
        }
        return processedBlock;
      }).join('');
    });
  }

  private generateOutputPath(projectPath: string, templateName: string, format: string): string {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const fileName = `${templateName}-${timestamp}.${format}`;
    return path.join(projectPath, 'generated-reports', fileName);
  }

  async validateTemplate(template: Template): Promise<string[]> {
    const errors: string[] = [];

    if (!await fs.pathExists(template.filePath)) {
      errors.push(`Файл шаблону не знайдено: ${template.filePath}`);
    }

    try {
      const content = await fs.readFile(template.filePath, 'utf-8');
      const variables = this.extractTemplateVariables(content);
      
      for (const variable of template.variables) {
        if (variable.required && !variables.includes(variable.name)) {
          errors.push(`Обов'язкова змінна ${variable.name} не знайдена в шаблоні`);
        }
      }
    } catch (error) {
      errors.push(`Помилка читання шаблону: ${error instanceof Error ? error.message : 'Невідома помилка'}`);
    }

    return errors;
  }

  private extractTemplateVariables(content: string): string[] {
    const variables: string[] = [];
    const variablePattern = /\{\{(\w+)(?::(\w+))?(?:\|(.+?))?\}\}/g;
    const matches = content.matchAll(variablePattern);

    for (const match of matches) {
      if (!variables.includes(match[1])) {
        variables.push(match[1]);
      }
    }

    return variables;
  }
}