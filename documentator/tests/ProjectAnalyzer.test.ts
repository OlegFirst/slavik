import { ProjectAnalyzer } from '../src/core/ProjectAnalyzer';
import * as fs from 'fs-extra';
import * as path from 'path';

describe('ProjectAnalyzer', () => {
  let analyzer: ProjectAnalyzer;
  let tempDir: string;

  beforeEach(() => {
    analyzer = new ProjectAnalyzer();
    tempDir = path.join(__dirname, 'temp');
  });

  afterEach(async () => {
    await fs.remove(tempDir);
  });

  describe('analyzeProject', () => {
    it('should analyze an empty project', async () => {
      await fs.ensureDir(tempDir);
      
      const analysis = await analyzer.analyzeProject(tempDir);
      
      expect(analysis).toBeDefined();
      expect(analysis.projectName).toBe('temp');
      expect(analysis.documentTypes).toEqual([]);
      expect(analysis.templates).toEqual([]);
    });

    it('should find markdown templates', async () => {
      await fs.ensureDir(tempDir);
      
      const templateContent = `# {{title}}

Автор: {{author}}
Дата: {{date|2024-01-01}}`;
      
      await fs.writeFile(path.join(tempDir, 'template-report.md'), templateContent);
      
      const analysis = await analyzer.analyzeProject(tempDir);
      
      expect(analysis.documentTypes).toContain('.md');
      expect(analysis.templates).toHaveLength(1);
      expect(analysis.templates[0].name).toBe('template-report');
      expect(analysis.templates[0].variables).toHaveLength(3);
    });

    it('should extract variables from templates', async () => {
      await fs.ensureDir(tempDir);
      
      const templateContent = `# {{title}}
Required: {{requiredVar}}
Optional: {{optionalVar|default value}}
Typed: {{numberVar:number}}`;
      
      await fs.writeFile(path.join(tempDir, 'template.md'), templateContent);
      
      const analysis = await analyzer.analyzeProject(tempDir);
      const template = analysis.templates[0];
      
      expect(template.variables).toHaveLength(4);
      
      const titleVar = template.variables.find(v => v.name === 'title');
      expect(titleVar?.required).toBe(true);
      
      const optionalVar = template.variables.find(v => v.name === 'optionalVar');
      expect(optionalVar?.required).toBe(false);
      expect(optionalVar?.defaultValue).toBe('default value');
      
      const numberVar = template.variables.find(v => v.name === 'numberVar');
      expect(numberVar?.type).toBe('number');
    });

    it('should handle nested directories', async () => {
      await fs.ensureDir(path.join(tempDir, 'docs', 'templates'));
      
      const templateContent = `# {{title}}`;
      await fs.writeFile(
        path.join(tempDir, 'docs', 'templates', 'nested-template.md'), 
        templateContent
      );
      
      const analysis = await analyzer.analyzeProject(tempDir);
      
      expect(analysis.templates).toHaveLength(1);
      expect(analysis.templates[0].name).toBe('nested-template');
    });

    it('should throw error for non-existent path', async () => {
      const nonExistentPath = path.join(tempDir, 'does-not-exist');
      
      await expect(analyzer.analyzeProject(nonExistentPath))
        .rejects
        .toThrow('Шлях проекту не існує');
    });
  });

  describe('template detection', () => {
    it('should detect templates by keywords', async () => {
      await fs.ensureDir(tempDir);
      
      const testCases = [
        'template.md',
        'шаблон.md',
        'report-template.md',
        'звіт-2024.md',
        'document-template.md'
      ];
      
      for (const fileName of testCases) {
        await fs.writeFile(path.join(tempDir, fileName), '# {{title}}');
      }
      
      await fs.writeFile(path.join(tempDir, 'regular-file.md'), '# Regular File');
      
      const analysis = await analyzer.analyzeProject(tempDir);
      
      expect(analysis.templates).toHaveLength(testCases.length);
    });
  });

  describe('structure extraction', () => {
    it('should extract document structure from markdown', async () => {
      await fs.ensureDir(tempDir);
      
      const templateContent = `# Main Title {{title}}

## Section 1
Content for section 1 with {{var1}}

### Subsection 1.1
More content with {{var2}}

## Section 2
Content for section 2 with {{var3}}`;
      
      await fs.writeFile(path.join(tempDir, 'template.md'), templateContent);
      
      const analysis = await analyzer.analyzeProject(tempDir);
      const template = analysis.templates[0];
      
      expect(template.structure.sections).toHaveLength(2);
      expect(template.structure.sections[0].title).toBe('Main Title {{title}}');
      expect(template.structure.sections[1].title).toBe('Section 1');
    });
  });
});