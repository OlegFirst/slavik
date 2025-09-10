import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { BaseService } from '../../core/BaseService';
import { ServiceMetadata } from '../../types/ServiceInterface';
import { ProjectAnalyzer } from '../../core/ProjectAnalyzer';
import { ReportGenerator } from '../../core/ReportGenerator';
import { SimpleProjectManager } from '../../core/SimpleProjectManager';
import { DocumentChecker } from '../../core/DocumentChecker';
import { DocumentFiller } from '../../core/DocumentFiller';
import { ProjectAnalysis, Template, ReportRequest } from '../../types/index';

export class DocumentatorService extends BaseService {
  public metadata: ServiceMetadata = {
    name: 'documentator',
    version: '1.0.0',
    description: 'Система автоматизації створення звітної документації з аналізом проектних папок',
    author: 'Digital Office Team',
    category: 'Документообіг'
  };

  private projectAnalyzer!: ProjectAnalyzer;
  private reportGenerator!: ReportGenerator;
  private projectManager!: SimpleProjectManager;
  private documentChecker!: DocumentChecker;
  private documentFiller!: DocumentFiller;
  private projectCache: Map<string, ProjectAnalysis> = new Map();

  protected async onInitialize(): Promise<void> {
    this.projectAnalyzer = new ProjectAnalyzer();
    this.reportGenerator = new ReportGenerator();
    this.projectManager = new SimpleProjectManager();
    this.documentChecker = new DocumentChecker();
    this.documentFiller = new DocumentFiller();
    
    console.log('DocumentatorService: Всі компоненти ініціалізовано');
  }

  protected async onShutdown(): Promise<void> {
    this.projectCache.clear();
    console.log('DocumentatorService: Кеш очищено');
  }

  protected async performHealthCheck(): Promise<boolean> {
    try {
      // Перевіряємо доступність папки projects
      const projects = await this.projectManager.listProjects();
      return true;
    } catch (error) {
      console.error('DocumentatorService health check failed:', error);
      return false;
    }
  }

  public getTools(): Tool[] {
    return [
      {
        name: 'analyze_project',
        description: 'Аналізує папку проекту та знаходить доступні шаблони документації',
        inputSchema: {
          type: 'object',
          properties: {
            projectPath: {
              type: 'string',
              description: 'Шлях до папки проекту для аналізу',
            },
            forceRefresh: {
              type: 'boolean',
              description: 'Примусово оновити кеш аналізу',
              default: false,
            },
          },
          required: ['projectPath'],
        },
      },
      {
        name: 'list_templates',
        description: 'Отримує список доступних шаблонів для проекту',
        inputSchema: {
          type: 'object',
          properties: {
            projectPath: {
              type: 'string',
              description: 'Шлях до папки проекту',
            },
          },
          required: ['projectPath'],
        },
      },
      {
        name: 'get_template_variables',
        description: 'Отримує список змінних для конкретного шаблону',
        inputSchema: {
          type: 'object',
          properties: {
            projectPath: {
              type: 'string',
              description: 'Шлях до папки проекту',
            },
            templateId: {
              type: 'string',
              description: 'ID шаблону',
            },
          },
          required: ['projectPath', 'templateId'],
        },
      },
      {
        name: 'generate_report',
        description: 'Генерує звіт на основі шаблону та наданих змінних',
        inputSchema: {
          type: 'object',
          properties: {
            projectPath: {
              type: 'string',
              description: 'Шлях до папки проекту',
            },
            templateId: {
              type: 'string',
              description: 'ID шаблону для генерації',
            },
            variables: {
              type: 'object',
              description: 'Значення змінних для заповнення шаблону',
            },
            outputPath: {
              type: 'string',
              description: 'Опціональний шлях для збереження звіту',
            },
            format: {
              type: 'string',
              enum: ['markdown', 'docx', 'pdf', 'html'],
              description: 'Формат вихідного файлу',
            },
          },
          required: ['projectPath', 'templateId', 'variables'],
        },
      },
      {
        name: 'list_projects',
        description: 'Отримує список проектів з папки projects/',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'analyze_project_by_id',
        description: 'Аналізує проект з папки projects/ за його ID (назвою папки)',
        inputSchema: {
          type: 'object',
          properties: {
            projectId: {
              type: 'string',
              description: 'ID проекту (назва папки в projects/)',
            },
          },
          required: ['projectId'],
        },
      },
      {
        name: 'generate_report_by_id',
        description: 'Генерує звіт з проекту в папці projects/',
        inputSchema: {
          type: 'object',
          properties: {
            projectId: {
              type: 'string',
              description: 'ID проекту (назва папки в projects/)',
            },
            templateId: {
              type: 'string',
              description: 'ID шаблону для генерації',
            },
            variables: {
              type: 'object',
              description: 'Значення змінних для заповнення шаблону',
            },
            format: {
              type: 'string',
              enum: ['markdown', 'html'],
              description: 'Формат вихідного файлу',
            },
          },
          required: ['projectId', 'templateId', 'variables'],
        },
      },
      {
        name: 'generate_templates_for_project',
        description: 'Генерує шаблони на основі існуючих документів у проекті',
        inputSchema: {
          type: 'object',
          properties: {
            projectId: {
              type: 'string',
              description: 'ID проекту (назва папки в projects/)',
            },
            templateBaseName: {
              type: 'string',
              description: 'Базова назва для генерованих шаблонів (опціонально)',
            },
          },
          required: ['projectId'],
        },
      },
      {
        name: 'save_generated_template',
        description: 'Зберігає згенерований шаблон в проект',
        inputSchema: {
          type: 'object',
          properties: {
            projectId: {
              type: 'string',
              description: 'ID проекту (назва папки в projects/)',
            },
            templateName: {
              type: 'string',
              description: 'Назва шаблону',
            },
            templateContent: {
              type: 'string',
              description: 'Вміст шаблону',
            },
            extractedVariables: {
              type: 'array',
              items: { type: 'string' },
              description: 'Список виділених змінних',
            },
            originalDocument: {
              type: 'string',
              description: 'Шлях до оригінального документу',
            },
          },
          required: ['projectId', 'templateName', 'templateContent', 'extractedVariables', 'originalDocument'],
        },
      },
      {
        name: 'check_document',
        description: 'Перевіряє та виправляє помилки у тексті документу, зберігаючи структуру',
        inputSchema: {
          type: 'object',
          properties: {
            filePath: {
              type: 'string',
              description: 'Повний шлях до файлу для перевірки',
            },
            textContent: {
              type: 'string',
              description: 'Текст для перевірки (альтернатива filePath)',
            },
            fileExtension: {
              type: 'string',
              description: 'Розширення файлу для визначення типу (.md, .txt, .html)',
              default: '.md'
            },
            autoFix: {
              type: 'boolean',
              description: 'Чи автоматично виправляти знайдені помилки',
              default: true
            },
            saveBackup: {
              type: 'boolean',
              description: 'Чи створювати резервну копію оригіналу',
              default: true
            },
            outputPath: {
              type: 'string',
              description: 'Шлях для збереження виправленого файлу (опціонально)',
            }
          }
        },
      },
      {
        name: 'fill_document',
        description: 'Аналізує документ для заповнення та розпочинає інтерактивний процес заповнення полів',
        inputSchema: {
          type: 'object',
          properties: {
            filePath: {
              type: 'string',
              description: 'Повний шлях до документу для заповнення',
            },
            sourceDocuments: {
              type: 'array',
              items: { type: 'string' },
              description: 'Список шляхів до додаткових документів для автозаповнення',
            },
          },
          required: ['filePath'],
        },
      },
      {
        name: 'fill_next_question',
        description: 'Отримує наступне питання для заповнення документу',
        inputSchema: {
          type: 'object',
          properties: {
            sessionId: {
              type: 'string',
              description: 'ID сесії заповнення',
            },
          },
          required: ['sessionId'],
        },
      },
      {
        name: 'fill_submit_answer',
        description: 'Відправляє відповідь на питання та отримує наступне питання',
        inputSchema: {
          type: 'object',
          properties: {
            sessionId: {
              type: 'string',
              description: 'ID сесії заповнення',
            },
            fieldId: {
              type: 'string',
              description: 'ID поля, на яке відповідаємо',
            },
            answer: {
              description: 'Відповідь користувача (може бути текст, число, дата тощо)',
            },
          },
          required: ['sessionId', 'fieldId', 'answer'],
        },
      },
      {
        name: 'fill_complete',
        description: 'Завершує заповнення документу та генерує остаточний файл',
        inputSchema: {
          type: 'object',
          properties: {
            sessionId: {
              type: 'string',
              description: 'ID сесії заповнення',
            },
          },
          required: ['sessionId'],
        },
      },
      {
        name: 'fill_cancel',
        description: 'Скасовує сесію заповнення документу',
        inputSchema: {
          type: 'object',
          properties: {
            sessionId: {
              type: 'string',
              description: 'ID сесії заповнення',
            },
          },
          required: ['sessionId'],
        },
      },
      {
        name: 'fill_get_status',
        description: 'Отримує статус сесії заповнення та прогрес',
        inputSchema: {
          type: 'object',
          properties: {
            sessionId: {
              type: 'string',
              description: 'ID сесії заповнення',
            },
          },
          required: ['sessionId'],
        },
      },
    ];
  }

  public async handleToolCall(toolName: string, args: any): Promise<any> {
    try {
      switch (toolName) {
        case 'analyze_project':
          return this.handleAnalyzeProject(args);
        
        case 'list_templates':
          return this.handleListTemplates(args);
        
        case 'generate_report':
          return this.handleGenerateReport(args);
        
        case 'get_template_variables':
          return this.handleGetTemplateVariables(args);
        
        case 'list_projects':
          return this.handleListProjects(args);
        
        case 'analyze_project_by_id':
          return this.handleAnalyzeProjectById(args);
        
        case 'generate_report_by_id':
          return this.handleGenerateReportById(args);
        
        case 'generate_templates_for_project':
          return this.handleGenerateTemplatesForProject(args);
        
        case 'save_generated_template':
          return this.handleSaveGeneratedTemplate(args);
        
        case 'check_document':
          return this.handleCheckDocument(args);
        
        case 'fill_document':
          return this.handleFillDocument(args);
        
        case 'fill_next_question':
          return this.handleFillNextQuestion(args);
        
        case 'fill_submit_answer':
          return this.handleFillSubmitAnswer(args);
        
        case 'fill_complete':
          return this.handleFillComplete(args);
        
        case 'fill_cancel':
          return this.handleFillCancel(args);
        
        case 'fill_get_status':
          return this.handleFillGetStatus(args);
        
        default:
          throw new Error(`Невідомий інструмент: ${toolName}`);
      }
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Помилка: ${error instanceof Error ? error.message : 'Невідома помилка'}`,
          },
        ],
        isError: true,
      };
    }
  }

  private async handleAnalyzeProject(args: any) {
    const { projectPath, forceRefresh = false } = args;

    if (!forceRefresh && this.projectCache.has(projectPath)) {
      const cached = this.projectCache.get(projectPath)!;
      return {
        content: [
          {
            type: 'text',
            text: `Проект проаналізовано (з кешу):\n` +
                  `Назва: ${cached.projectName}\n` +
                  `Типи документів: ${cached.documentTypes.join(', ')}\n` +
                  `Знайдено шаблонів: ${cached.templates.length}\n` +
                  `Остання перевірка: ${cached.lastAnalyzed.toLocaleString()}`,
          },
        ],
      };
    }

    const analysis = await this.projectAnalyzer.analyzeProject(projectPath);
    this.projectCache.set(projectPath, analysis);

    return {
      content: [
        {
          type: 'text',
          text: `Проект успішно проаналізовано:\n` +
                `Назва: ${analysis.projectName}\n` +
                `Типи документів: ${analysis.documentTypes.join(', ')}\n` +
                `Знайдено шаблонів: ${analysis.templates.length}\n` +
                `Шаблони: ${analysis.templates.map(t => t.name).join(', ')}`,
        },
      ],
    };
  }

  private async handleListTemplates(args: any) {
    const { projectPath } = args;
    const analysis = await this.getProjectAnalysis(projectPath);

    const templatesList = analysis.templates.map(template => 
      `- ${template.name} (${template.type}): ${template.variables.length} змінних`
    ).join('\n');

    return {
      content: [
        {
          type: 'text',
          text: `Доступні шаблони для проекту ${analysis.projectName}:\n${templatesList}`,
        },
      ],
    };
  }

  private async handleGetTemplateVariables(args: any) {
    const { projectPath, templateId } = args;
    const analysis = await this.getProjectAnalysis(projectPath);
    const template = analysis.templates.find(t => t.id === templateId);

    if (!template) {
      throw new Error(`Шаблон з ID ${templateId} не знайдено`);
    }

    const variablesList = template.variables.map(variable => 
      `- ${variable.name} (${variable.type})${variable.required ? ' *обов\'язково*' : ''}: ${variable.description || 'Без опису'}`
    ).join('\n');

    return {
      content: [
        {
          type: 'text',
          text: `Змінні шаблону "${template.name}":\n${variablesList}`,
        },
      ],
    };
  }

  private async handleGenerateReport(args: any) {
    const { projectPath, templateId, variables, outputPath, format } = args;
    const analysis = await this.getProjectAnalysis(projectPath);
    const template = analysis.templates.find(t => t.id === templateId);

    if (!template) {
      throw new Error(`Шаблон з ID ${templateId} не знайдено`);
    }

    const request: ReportRequest = {
      templateId,
      projectPath,
      variables,
      outputPath,
      format,
    };

    const response = await this.reportGenerator.generateReport(request, template, analysis);

    if (response.success) {
      return {
        content: [
          {
            type: 'text',
            text: `Звіт успішно згенеровано!\nФайл: ${response.outputPath}\nЧас створення: ${response.generatedAt.toLocaleString()}`,
          },
        ],
      };
    } else {
      throw new Error(response.error);
    }
  }

  private async getProjectAnalysis(projectPath: string): Promise<ProjectAnalysis> {
    if (this.projectCache.has(projectPath)) {
      return this.projectCache.get(projectPath)!;
    }

    const analysis = await this.projectAnalyzer.analyzeProject(projectPath);
    this.projectCache.set(projectPath, analysis);
    return analysis;
  }

  private async handleListProjects(args: any) {
    const projects = await this.projectManager.listProjects();

    if (projects.length === 0) {
      return {
        content: [
          {
            type: 'text',
            text: `Проекти не знайдено.\n\nСтворіть папку в: ${this.projectManager.getProjectsDirectory()}\nта додайте туди підпапки з файлами шаблонів.`,
          },
        ],
      };
    }

    return {
      content: [
        {
          type: 'text',
          text: `Знайдено проекти в: ${this.projectManager.getProjectsDirectory()}\n\n` +
                projects.map(project => 
                  `- **${project.name}** (ID: ${project.id})`
                ).join('\n') +
                `\n\nДля аналізу проекту використайте команду analyze_project_by_id`,
        },
      ],
    };
  }

  private async handleAnalyzeProjectById(args: any) {
    const { projectId } = args;

    if (!await this.projectManager.projectExists(projectId)) {
      throw new Error(`Проект з ID "${projectId}" не знайдено в папці projects/`);
    }

    const analysis = await this.projectManager.analyzeProject(projectId);

    return {
      content: [
        {
          type: 'text',
          text: `Проект "${analysis.projectName}" проаналізовано:\n` +
                `Шлях: ${analysis.projectPath}\n` +
                `Типи документів: ${analysis.documentTypes.join(', ') || 'Немає'}\n` +
                `Знайдено шаблонів: ${analysis.templates.length}\n\n` +
                (analysis.templates.length > 0 ? 
                  `Доступні шаблони:\n` +
                  analysis.templates.map(template => 
                    `- **${template.name}** (ID: ${template.id})\n` +
                    `  Тип: ${template.type}\n` +
                    `  Змінних: ${template.variables.length}\n` +
                    `  Секцій: ${template.structure.sections.length}`
                  ).join('\n') :
                  `Шаблони не знайдено. Додайте файли .md з шаблонами в папку проекту.`
                ),
        },
      ],
    };
  }

  private async handleGenerateReportById(args: any) {
    const { projectId, templateId, variables, format } = args;

    if (!await this.projectManager.projectExists(projectId)) {
      throw new Error(`Проект з ID "${projectId}" не знайдено в папці projects/`);
    }

    const analysis = await this.projectManager.analyzeProject(projectId);
    const template = analysis.templates.find(t => t.id === templateId);

    if (!template) {
      throw new Error(`Шаблон з ID "${templateId}" не знайдено в проекті "${projectId}"`);
    }

    const request: ReportRequest = {
      templateId,
      projectPath: this.projectManager.getProjectPath(projectId),
      variables,
      format: format || template.structure.format,
    };

    const response = await this.reportGenerator.generateReport(request, template, analysis);

    if (response.success) {
      return {
        content: [
          {
            type: 'text',
            text: `Звіт успішно згенеровано з проекту "${projectId}"!\n` +
                  `Шаблон: ${template.name}\n` +
                  `Файл: ${response.outputPath}\n` +
                  `Час створення: ${response.generatedAt.toLocaleString()}\n` +
                  `Формат: ${request.format}`,
          },
        ],
      };
    } else {
      throw new Error(response.error);
    }
  }

  private async handleGenerateTemplatesForProject(args: any) {
    const { projectId, templateBaseName } = args;

    if (!await this.projectManager.projectExists(projectId)) {
      throw new Error(`Проект з ID "${projectId}" не знайдено в папці projects/`);
    }

    const templates = await this.projectManager.generateTemplatesForProject(projectId, templateBaseName);

    if (templates.length === 0) {
      return {
        content: [
          {
            type: 'text',
            text: `В проекті "${projectId}" не знайдено документів для створення шаблонів.\nПідтримувані формати: .md, .txt, .docx, .doc`,
          },
        ],
      };
    }

    const templatesList = templates.map(template => 
      `### ${template.templateName}\n` +
      `- Базується на: ${template.originalDocument}\n` +
      `- Змінних знайдено: ${template.extractedVariables.length}\n` +
      `- Змінні: ${template.extractedVariables.join(', ') || 'Немає'}\n` +
      `\n**Прев'ю шаблону:**\n\`\`\`\n${template.templateContent.substring(0, 200)}${template.templateContent.length > 200 ? '...' : ''}\n\`\`\`\n`
    ).join('\n');

    return {
      content: [
        {
          type: 'text',
          text: `Згенеровано ${templates.length} шаблонів для проекту "${projectId}":\n\n${templatesList}\n` +
                `Для збереження шаблону використайте команду save_generated_template`,
        },
      ],
    };
  }

  private async handleSaveGeneratedTemplate(args: any) {
    const { projectId, templateName, templateContent, extractedVariables, originalDocument } = args;

    if (!await this.projectManager.projectExists(projectId)) {
      throw new Error(`Проект з ID "${projectId}" не знайдено в папці projects/`);
    }

    const template = {
      templateName,
      templateContent,
      extractedVariables,
      originalDocument
    };

    const savedPath = await this.projectManager.saveGeneratedTemplate(projectId, template);

    return {
      content: [
        {
          type: 'text',
          text: `Шаблон "${templateName}" успішно збережено!\n` +
                `Файл: ${savedPath}\n` +
                `Базується на: ${originalDocument}\n` +
                `Змінних: ${extractedVariables.length}`,
        },
      ],
    };
  }

  private async handleCheckDocument(args: any) {
    const { filePath, textContent, fileExtension = '.md', autoFix = true, saveBackup = true, outputPath } = args;

    if (!filePath && !textContent) {
      throw new Error('Необхідно надати або filePath, або textContent');
    }

    try {
      let checkResult;
      
      if (filePath) {
        // Перевіряємо файл
        checkResult = await this.documentChecker.checkDocument(filePath);
        
        if (autoFix && checkResult.summary.fixedErrors > 0) {
          // Зберігаємо виправлений файл
          const savePath = outputPath || filePath;
          await this.documentChecker.saveCheckedDocument(savePath, checkResult.correctedText, saveBackup);
        }
      } else {
        // Перевіряємо текст напряму
        checkResult = this.documentChecker.checkText(textContent, fileExtension);
      }

      // Форматуємо результат для відображення
      const errorsSummary = this.formatErrorsSummary(checkResult);
      const structureInfo = this.formatStructureInfo(checkResult.structure);

      return {
        content: [
          {
            type: 'text',
            text: `# 📝 Результат перевірки документу\n\n` +
                  `## 📊 Підсумок\n` +
                  `- **Всього помилок:** ${checkResult.summary.totalErrors}\n` +
                  `- **Автоматично виправлено:** ${checkResult.summary.fixedErrors}\n` +
                  `- **Тип документу:** ${checkResult.structure.type}\n\n` +
                  `## 🔍 Помилки за типами\n${errorsSummary}\n\n` +
                  `## 📋 Структура документу\n${structureInfo}\n\n` +
                  (checkResult.errors.length > 0 ? 
                    `## 🚨 Детальний список помилок\n${this.formatDetailedErrors(checkResult.errors)}\n\n` : 
                    `✅ **Помилок не знайдено!**\n\n`
                  ) +
                  (autoFix && filePath && checkResult.summary.fixedErrors > 0 ? 
                    `✅ **Файл автоматично виправлено**${saveBackup ? ' (створено резервну копію .backup)' : ''}\n\n` : 
                    ''
                  ) +
                  (checkResult.summary.fixedErrors < checkResult.summary.totalErrors ?
                    `📌 **Рекомендації:** Деякі помилки потребують ручного виправлення для збереження контексту.\n\n` :
                    ''
                  ) +
                  `---\n*Перевірка виконана Digital Office Documentator*`,
          },
        ],
      };

    } catch (error) {
      throw new Error(`Помилка перевірки документу: ${error instanceof Error ? error.message : 'Невідома помилка'}`);
    }
  }

  private formatErrorsSummary(checkResult: any): string {
    const errorsByType = checkResult.summary.errorsByType;
    if (Object.keys(errorsByType).length === 0) {
      return '✅ Помилок не виявлено';
    }

    const typeNames: Record<string, string> = {
      'spelling': '📝 Орфографія',
      'grammar': '📚 Граматика', 
      'punctuation': '✏️ Пунктуація',
      'style': '🎨 Стиль'
    };

    return Object.entries(errorsByType)
      .map(([type, count]) => `- ${typeNames[type] || type}: ${count}`)
      .join('\n');
  }

  private formatStructureInfo(structure: any): string {
    const parts = [];
    
    if (structure.headers.length > 0) {
      parts.push(`📑 Заголовків: ${structure.headers.length}`);
    }
    
    if (structure.lists.length > 0) {
      parts.push(`📋 Списків: ${structure.lists.length}`);
    }
    
    if (structure.codeBlocks.length > 0) {
      parts.push(`💻 Блоків коду: ${structure.codeBlocks.length}`);
    }
    
    if (structure.links.length > 0) {
      parts.push(`🔗 Посилань: ${structure.links.length}`);
    }
    
    if (structure.formatting.length > 0) {
      parts.push(`✨ Форматування: ${structure.formatting.length}`);
    }

    return parts.length > 0 ? parts.join(' • ') : 'Проста текстова структура';
  }

  private formatDetailedErrors(errors: any[]): string {
    if (errors.length === 0) {
      return 'Помилок не знайдено';
    }

    return errors.slice(0, 10).map((error, index) => {
      const severityIcons: Record<string, string> = {
        'low': '🟡',
        'medium': '🟠', 
        'high': '🔴'
      };
      const severityIcon = severityIcons[error.severity] || '⚪';

      return `${index + 1}. ${severityIcon} **Рядок ${error.line}**: ${error.description}\n` +
             `   📝 "${error.originalText}" → "${error.correctedText}"`;
    }).join('\n\n') + 
    (errors.length > 10 ? `\n\n... та ще ${errors.length - 10} помилок` : '');
  }

  private async handleFillDocument(args: any) {
    const { filePath, sourceDocuments } = args;

    try {
      const session = await this.documentFiller.analyzeDocument(filePath, sourceDocuments);
      
      // Отримуємо перше питання
      const firstQuestion = await this.documentFiller.getNextQuestion(session.sessionId);
      
      if (!firstQuestion) {
        return {
          content: [
            {
              type: 'text',
              text: `🔍 **Документ проаналізовано**\\n\\n` +
                    `📄 Файл: ${filePath}\\n` +
                    `📊 Знайдено полів: ${session.fields.length}\\n` +
                    `🤖 Автоматично заповнено: ${Array.from(session.responses.values()).filter(r => r.source === 'auto').length}\\n\\n` +
                    `✅ **Всі поля вже заповнені!** Використайте \`fill_complete\` для генерації остаточного документу.\\n\\n` +
                    `🆔 **ID сесії:** ${session.sessionId}`,
            },
          ],
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: `🚀 **Розпочато заповнення документу**\\n\\n` +
                  `📄 Файл: ${filePath}\\n` +
                  `📊 Знайдено полів: ${session.fields.length}\\n` +
                  `🤖 Автоматично заповнено: ${Array.from(session.responses.values()).filter(r => r.source === 'auto').length}\\n` +
                  `📝 Додаткових документів: ${session.sourceDocuments.length}\\n\\n` +
                  `**Перше питання (${firstQuestion.context.fieldNumber}/${firstQuestion.context.totalFields}):**\\n\\n` +
                  `${firstQuestion.question}\\n\\n` +
                  `🔤 **Тип поля:** ${firstQuestion.field.type}\\n` +
                  `${firstQuestion.context.isRequired ? "❗ **Обов'язкове поле**" : "💡 Опціональне поле"}\\n` +
                  (firstQuestion.context.examples.length > 0 ? 
                    `\\n📚 **Приклади:** ${firstQuestion.context.examples.join(', ')}\\n` : '') +
                  `\\n🆔 **ID сесії:** ${session.sessionId}\\n` +
                  `🔑 **ID поля:** ${firstQuestion.field.id}\\n\\n` +
                  `Для відповіді використайте: \`fill_submit_answer\``,
          },
        ],
      };

    } catch (error) {
      throw new Error(`Помилка аналізу документу для заповнення: ${error instanceof Error ? error.message : 'Невідома помилка'}`);
    }
  }

  private async handleFillNextQuestion(args: any) {
    const { sessionId } = args;

    try {
      const question = await this.documentFiller.getNextQuestion(sessionId);
      
      if (!question) {
        const session = this.documentFiller.getSession(sessionId);
        if (!session) {
          throw new Error('Сесію не знайдено');
        }

        if (session.status === 'filling') {
          return {
            content: [
              {
                type: 'text',
                text: `✅ **Всі питання завершено!**\\n\\n` +
                      `📊 Заповнено полів: ${session.responses.size}/${session.fields.length}\\n` +
                      `🎯 **Готово до генерації документу**\\n\\n` +
                      `Використайте \`fill_complete\` для створення остаточного файлу.`,
              },
            ],
          };
        }

        return {
          content: [
            {
              type: 'text',
              text: `❌ Сесія завершена або скасована. Статус: ${session.status}`,
            },
          ],
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: `**Питання (${question.context.fieldNumber}/${question.context.totalFields}):**\\n\\n` +
                  `${question.question}\\n\\n` +
                  `🔤 **Тип поля:** ${question.field.type}\\n` +
                  `${question.context.isRequired ? "❗ **Обов'язкове поле**" : "💡 Опціональне поле"}\\n` +
                  (question.context.examples.length > 0 ? 
                    `\\n📚 **Приклади:** ${question.context.examples.join(', ')}\\n` : '') +
                  (question.context.relatedFields.length > 0 ?
                    `\\n🔗 **Пов'язані поля:** ${question.context.relatedFields.join(', ')}\\n` : '') +
                  `\\n🔑 **ID поля:** ${question.field.id}\\n\\n` +
                  `Для відповіді використайте: \`fill_submit_answer\``,
          },
        ],
      };

    } catch (error) {
      throw new Error(`Помилка отримання питання: ${error instanceof Error ? error.message : 'Невідома помилка'}`);
    }
  }

  private async handleFillSubmitAnswer(args: any) {
    const { sessionId, fieldId, answer } = args;

    try {
      const result = await this.documentFiller.submitResponse(sessionId, fieldId, answer);
      
      if (!result.accepted) {
        return {
          content: [
            {
              type: 'text',
              text: `❌ **Відповідь відхилено**\\n\\n` +
                    `🚨 Помилка: ${result.error}\\n\\n` +
                    `Спробуйте ще раз або використайте \`fill_next_question\` для повторного отримання питання.`,
            },
          ],
        };
      }

      if (result.nextField) {
        return {
          content: [
            {
              type: 'text',
              text: `✅ **Відповідь прийнята!**\\n\\n` +
                    `**Наступне питання (${result.nextField.context.fieldNumber}/${result.nextField.context.totalFields}):**\\n\\n` +
                    `${result.nextField.question}\\n\\n` +
                    `🔤 **Тип поля:** ${result.nextField.field.type}\\n` +
                    `${result.nextField.context.isRequired ? "❗ **Обов'язкове поле**" : "💡 Опціональне поле"}\\n` +
                    (result.nextField.context.examples.length > 0 ? 
                      `\\n📚 **Приклади:** ${result.nextField.context.examples.join(', ')}\\n` : '') +
                    `\\n🔑 **ID поля:** ${result.nextField.field.id}`,
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: 'text',
              text: `✅ **Відповідь прийнята!**\\n\\n` +
                    `🎉 **Всі питання завершено!**\\n\\n` +
                    `Використайте \`fill_complete\` для створення остаточного файлу.`,
            },
          ],
        };
      }

    } catch (error) {
      throw new Error(`Помилка обробки відповіді: ${error instanceof Error ? error.message : 'Невідома помилка'}`);
    }
  }

  private async handleFillComplete(args: any) {
    const { sessionId } = args;

    try {
      const result = await this.documentFiller.fillDocument(sessionId);
      
      if (!result.success) {
        throw new Error(result.error || 'Невдала спроба заповнення документу');
      }

      const session = this.documentFiller.getSession(sessionId);
      const totalResponses = session ? session.responses.size : 0;
      const totalFields = session ? session.fields.length : 0;
      const autoFilled = session ? Array.from(session.responses.values()).filter(r => r.source === 'auto').length : 0;
      const userFilled = session ? Array.from(session.responses.values()).filter(r => r.source === 'user').length : 0;

      return {
        content: [
          {
            type: 'text',
            text: `🎉 **Документ успішно заповнено!**\\n\\n` +
                  `📄 **Вихідний файл:** ${result.outputPath}\\n\\n` +
                  `📊 **Статистика заповнення:**\\n` +
                  `- Всього полів: ${totalFields}\\n` +
                  `- Заповнено: ${totalResponses}\\n` +
                  `- 🤖 Автоматично: ${autoFilled}\\n` +
                  `- 👤 Користувачем: ${userFilled}\\n\\n` +
                  `✅ Документ готовий до використання!`,
          },
        ],
      };

    } catch (error) {
      throw new Error(`Помилка завершення заповнення: ${error instanceof Error ? error.message : 'Невідома помилка'}`);
    }
  }

  private async handleFillCancel(args: any) {
    const { sessionId } = args;

    try {
      const cancelled = this.documentFiller.cancelSession(sessionId);
      
      if (!cancelled) {
        throw new Error('Сесію не знайдено або вже завершено');
      }

      return {
        content: [
          {
            type: 'text',
            text: `🚫 **Сесію заповнення скасовано**\\n\\n` +
                  `🆔 ID сесії: ${sessionId}\\n\\n` +
                  `Всі дані сесії збережено. Ви можете розпочати нову сесію командою \`fill_document\`.`,
          },
        ],
      };

    } catch (error) {
      throw new Error(`Помилка скасування сесії: ${error instanceof Error ? error.message : 'Невідома помилка'}`);
    }
  }

  private async handleFillGetStatus(args: any) {
    const { sessionId } = args;

    try {
      const session = this.documentFiller.getSession(sessionId);
      
      if (!session) {
        throw new Error('Сесію не знайдено');
      }

      const progress = session.fields.length > 0 ? 
        Math.round((session.responses.size / session.fields.length) * 100) : 0;
      
      const autoFilled = Array.from(session.responses.values()).filter(r => r.source === 'auto').length;
      const userFilled = Array.from(session.responses.values()).filter(r => r.source === 'user').length;

      const statusEmoji = {
        'analyzing': '🔍',
        'questioning': '❓',
        'filling': '📝',
        'completed': '✅',
        'cancelled': '❌'
      };

      return {
        content: [
          {
            type: 'text',
            text: `📊 **Статус сесії заповнення**\\n\\n` +
                  `🆔 **ID:** ${sessionId}\\n` +
                  `${statusEmoji[session.status]} **Статус:** ${session.status}\\n` +
                  `📄 **Документ:** ${session.targetDocument}\\n` +
                  `📈 **Прогрес:** ${progress}% (${session.responses.size}/${session.fields.length})\\n\\n` +
                  `📊 **Деталі заповнення:**\\n` +
                  `- 🤖 Автоматично: ${autoFilled}\\n` +
                  `- 👤 Користувачем: ${userFilled}\\n` +
                  `- 📝 Додаткових документів: ${session.sourceDocuments.length}\\n\\n` +
                  `⏰ **Час:**\\n` +
                  `- Створено: ${session.createdAt.toLocaleString()}\\n` +
                  `- Оновлено: ${session.lastUpdated.toLocaleString()}\\n\\n` +
                  (session.status === 'questioning' ? 
                    `Використайте \`fill_next_question\` для продовження.` : 
                    session.status === 'filling' ?
                    `Використайте \`fill_complete\` для генерації документу.` :
                    ''),
          },
        ],
      };

    } catch (error) {
      throw new Error(`Помилка отримання статусу: ${error instanceof Error ? error.message : 'Невідома помилка'}`);
    }
  }
}