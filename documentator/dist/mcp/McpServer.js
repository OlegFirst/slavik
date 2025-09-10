"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.McpServer = void 0;
const index_js_1 = require("@modelcontextprotocol/sdk/server/index.js");
const stdio_js_1 = require("@modelcontextprotocol/sdk/server/stdio.js");
const types_js_1 = require("@modelcontextprotocol/sdk/types.js");
const ProjectAnalyzer_js_1 = require("../core/ProjectAnalyzer.js");
const ReportGenerator_js_1 = require("../core/ReportGenerator.js");
const SimpleProjectManager_js_1 = require("../core/SimpleProjectManager.js");
class McpServer {
    constructor() {
        this.projectCache = new Map();
        this.server = new index_js_1.Server({
            name: 'documentator',
            version: '1.0.0',
        }, {
            capabilities: {
                tools: {},
            },
        });
        this.projectAnalyzer = new ProjectAnalyzer_js_1.ProjectAnalyzer();
        this.reportGenerator = new ReportGenerator_js_1.ReportGenerator();
        this.projectManager = new SimpleProjectManager_js_1.SimpleProjectManager();
        this.setupToolHandlers();
    }
    setupToolHandlers() {
        this.server.setRequestHandler(types_js_1.ListToolsRequestSchema, async () => {
            return {
                tools: this.getAvailableTools(),
            };
        });
        this.server.setRequestHandler(types_js_1.CallToolRequestSchema, async (request) => {
            switch (request.params.name) {
                case 'analyze_project':
                    return this.handleAnalyzeProject(request.params.arguments);
                case 'list_templates':
                    return this.handleListTemplates(request.params.arguments);
                case 'generate_report':
                    return this.handleGenerateReport(request.params.arguments);
                case 'get_template_variables':
                    return this.handleGetTemplateVariables(request.params.arguments);
                case 'list_projects':
                    return this.handleListProjects(request.params.arguments);
                case 'analyze_project_by_id':
                    return this.handleAnalyzeProjectById(request.params.arguments);
                case 'generate_report_by_id':
                    return this.handleGenerateReportById(request.params.arguments);
                case 'generate_templates_for_project':
                    return this.handleGenerateTemplatesForProject(request.params.arguments);
                case 'save_generated_template':
                    return this.handleSaveGeneratedTemplate(request.params.arguments);
                default:
                    throw new Error(`Невідомий інструмент: ${request.params.name}`);
            }
        });
    }
    getAvailableTools() {
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
        ];
    }
    async handleAnalyzeProject(args) {
        try {
            const { projectPath, forceRefresh = false } = args;
            if (!forceRefresh && this.projectCache.has(projectPath)) {
                const cached = this.projectCache.get(projectPath);
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
        catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Помилка аналізу проекту: ${error instanceof Error ? error.message : 'Невідома помилка'}`,
                    },
                ],
                isError: true,
            };
        }
    }
    async handleListTemplates(args) {
        try {
            const { projectPath } = args;
            const analysis = await this.getProjectAnalysis(projectPath);
            const templatesList = analysis.templates.map(template => `- ${template.name} (${template.type}): ${template.variables.length} змінних`).join('\n');
            return {
                content: [
                    {
                        type: 'text',
                        text: `Доступні шаблони для проекту ${analysis.projectName}:\n${templatesList}`,
                    },
                ],
            };
        }
        catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Помилка отримання шаблонів: ${error instanceof Error ? error.message : 'Невідома помилка'}`,
                    },
                ],
                isError: true,
            };
        }
    }
    async handleGetTemplateVariables(args) {
        try {
            const { projectPath, templateId } = args;
            const analysis = await this.getProjectAnalysis(projectPath);
            const template = analysis.templates.find(t => t.id === templateId);
            if (!template) {
                throw new Error(`Шаблон з ID ${templateId} не знайдено`);
            }
            const variablesList = template.variables.map(variable => `- ${variable.name} (${variable.type})${variable.required ? ' *обов\'язково*' : ''}: ${variable.description || 'Без опису'}`).join('\n');
            return {
                content: [
                    {
                        type: 'text',
                        text: `Змінні шаблону "${template.name}":\n${variablesList}`,
                    },
                ],
            };
        }
        catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Помилка отримання змінних шаблону: ${error instanceof Error ? error.message : 'Невідома помилка'}`,
                    },
                ],
                isError: true,
            };
        }
    }
    async handleGenerateReport(args) {
        try {
            const { projectPath, templateId, variables, outputPath, format } = args;
            const analysis = await this.getProjectAnalysis(projectPath);
            const template = analysis.templates.find(t => t.id === templateId);
            if (!template) {
                throw new Error(`Шаблон з ID ${templateId} не знайдено`);
            }
            const request = {
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
            }
            else {
                throw new Error(response.error);
            }
        }
        catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Помилка генерації звіту: ${error instanceof Error ? error.message : 'Невідома помилка'}`,
                    },
                ],
                isError: true,
            };
        }
    }
    async getProjectAnalysis(projectPath) {
        if (this.projectCache.has(projectPath)) {
            return this.projectCache.get(projectPath);
        }
        const analysis = await this.projectAnalyzer.analyzeProject(projectPath);
        this.projectCache.set(projectPath, analysis);
        return analysis;
    }
    async handleListProjects(args) {
        try {
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
                            projects.map(project => `- **${project.name}** (ID: ${project.id})`).join('\n') +
                            `\n\nДля аналізу проекту використайте команду analyze_project_by_id`,
                    },
                ],
            };
        }
        catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Помилка отримання списку проектів: ${error instanceof Error ? error.message : 'Невідома помилка'}`,
                    },
                ],
                isError: true,
            };
        }
    }
    async handleAnalyzeProjectById(args) {
        try {
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
                                    analysis.templates.map(template => `- **${template.name}** (ID: ${template.id})\n` +
                                        `  Тип: ${template.type}\n` +
                                        `  Змінних: ${template.variables.length}\n` +
                                        `  Секцій: ${template.structure.sections.length}`).join('\n') :
                                `Шаблони не знайдено. Додайте файли .md з шаблонами в папку проекту.`),
                    },
                ],
            };
        }
        catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Помилка аналізу проекту: ${error instanceof Error ? error.message : 'Невідома помилка'}`,
                    },
                ],
                isError: true,
            };
        }
    }
    async handleGenerateReportById(args) {
        try {
            const { projectId, templateId, variables, format } = args;
            if (!await this.projectManager.projectExists(projectId)) {
                throw new Error(`Проект з ID "${projectId}" не знайдено в папці projects/`);
            }
            const analysis = await this.projectManager.analyzeProject(projectId);
            const template = analysis.templates.find(t => t.id === templateId);
            if (!template) {
                throw new Error(`Шаблон з ID "${templateId}" не знайдено в проекті "${projectId}"`);
            }
            const request = {
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
            }
            else {
                throw new Error(response.error);
            }
        }
        catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Помилка генерації звіту: ${error instanceof Error ? error.message : 'Невідома помилка'}`,
                    },
                ],
                isError: true,
            };
        }
    }
    async handleGenerateTemplatesForProject(args) {
        try {
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
            const templatesList = templates.map(template => `### ${template.templateName}\n` +
                `- Базується на: ${template.originalDocument}\n` +
                `- Змінних знайдено: ${template.extractedVariables.length}\n` +
                `- Змінні: ${template.extractedVariables.join(', ') || 'Немає'}\n` +
                `\n**Прев'ю шаблону:**\n\`\`\`\n${template.templateContent.substring(0, 200)}${template.templateContent.length > 200 ? '...' : ''}\n\`\`\`\n`).join('\n');
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
        catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Помилка генерації шаблонів: ${error instanceof Error ? error.message : 'Невідома помилка'}`,
                    },
                ],
                isError: true,
            };
        }
    }
    async handleSaveGeneratedTemplate(args) {
        try {
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
        catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Помилка збереження шаблону: ${error instanceof Error ? error.message : 'Невідома помилка'}`,
                    },
                ],
                isError: true,
            };
        }
    }
    async start() {
        const transport = new stdio_js_1.StdioServerTransport();
        await this.server.connect(transport);
        console.error('Documentator MCP сервер запущено');
    }
}
exports.McpServer = McpServer;
//# sourceMappingURL=McpServer.js.map