"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.PMService = void 0;
const BaseService_1 = require("../../core/BaseService");
const ContentGenerator_1 = require("./ContentGenerator");
const PressReleasePrompts_1 = require("./prompts/PressReleasePrompts");
const ProjectPointPrompts_1 = require("./prompts/ProjectPointPrompts");
const path = __importStar(require("path"));
const fs = __importStar(require("fs-extra"));
class PMService extends BaseService_1.BaseService {
    constructor() {
        super();
        this.metadata = {
            name: 'pm',
            version: '1.0.0',
            description: 'Просунутий генератор текстового контенту з потужними системними промптами для PR та проект-менеджменту',
            author: 'Digital Office Team',
            category: 'Контент і комунікації'
        };
        this.outputDirectory = path.join(process.cwd(), 'output', 'pm');
    }
    async onInitialize() {
        this.contentGenerator = new ContentGenerator_1.ContentGenerator();
        // Реєструємо вбудовані промпти
        this.contentGenerator.registerPrompt(PressReleasePrompts_1.PRESS_RELEASE_PROMPT);
        this.contentGenerator.registerPrompt(ProjectPointPrompts_1.PROJECT_POINT_PROMPT);
        // Створюємо директорію для виводу
        await fs.ensureDir(this.outputDirectory);
        console.log('PMService: Генератор контенту ініціалізовано');
    }
    async onShutdown() {
        console.log('PMService: Сервіс зупинено');
    }
    async performHealthCheck() {
        try {
            // Перевіряємо доступність директорії та базових промптів
            await fs.access(this.outputDirectory);
            const prompts = this.contentGenerator.getAllPrompts();
            return prompts.length > 0;
        }
        catch (error) {
            console.error('PMService health check failed:', error);
            return false;
        }
    }
    getTools() {
        return [
            {
                name: 'release',
                description: 'Створити професійний прес-реліз з потужним системним промптом',
                inputSchema: {
                    type: 'object',
                    properties: {
                        interactive: {
                            type: 'boolean',
                            description: 'Чи використовувати інтерактивний режим збору даних',
                            default: true
                        },
                        data: {
                            type: 'object',
                            description: 'Дані для прес-релізу (якщо не інтерактивний режим)',
                            properties: this.generateJsonSchemaFromPrompt(PressReleasePrompts_1.PRESS_RELEASE_PROMPT)
                        },
                        outputPath: {
                            type: 'string',
                            description: 'Шлях для збереження файлу (опціонально)'
                        }
                    }
                },
            },
            {
                name: 'point',
                description: 'Створити короткий виклад проміжного досягнення проекту',
                inputSchema: {
                    type: 'object',
                    properties: {
                        interactive: {
                            type: 'boolean',
                            description: 'Чи використовувати інтерактивний режим збору даних',
                            default: true
                        },
                        data: {
                            type: 'object',
                            description: 'Дані для project point (якщо не інтерактивний режим)',
                            properties: this.generateJsonSchemaFromPrompt(ProjectPointPrompts_1.PROJECT_POINT_PROMPT)
                        },
                        outputPath: {
                            type: 'string',
                            description: 'Шлях для збереження файлу (опціонально)'
                        }
                    }
                },
            },
            {
                name: 'list_prompts',
                description: 'Показати всі доступні промпти для генерації контенту',
                inputSchema: {
                    type: 'object',
                    properties: {
                        category: {
                            type: 'string',
                            description: 'Фільтр за категорією (опціонально)'
                        }
                    }
                },
            },
            {
                name: 'get_prompt_info',
                description: 'Отримати детальну інформацію про конкретний промпт',
                inputSchema: {
                    type: 'object',
                    properties: {
                        promptId: {
                            type: 'string',
                            description: 'ID промпту для отримання інформації',
                        },
                    },
                    required: ['promptId'],
                },
            },
            {
                name: 'generate_custom',
                description: 'Згенерувати контент за допомогою будь-якого доступного промпту',
                inputSchema: {
                    type: 'object',
                    properties: {
                        promptId: {
                            type: 'string',
                            description: 'ID промпту для використання',
                        },
                        interactive: {
                            type: 'boolean',
                            description: 'Чи використовувати інтерактивний режим',
                            default: true
                        },
                        data: {
                            type: 'object',
                            description: 'Дані для промпту (якщо не інтерактивний режим)'
                        },
                        outputPath: {
                            type: 'string',
                            description: 'Шлях для збереження файлу (опціонально)'
                        }
                    },
                    required: ['promptId'],
                },
            },
        ];
    }
    async handleToolCall(toolName, args) {
        try {
            switch (toolName) {
                case 'release':
                    return this.handleRelease(args);
                case 'point':
                    return this.handlePoint(args);
                case 'list_prompts':
                    return this.handleListPrompts(args);
                case 'get_prompt_info':
                    return this.handleGetPromptInfo(args);
                case 'generate_custom':
                    return this.handleGenerateCustom(args);
                default:
                    throw new Error(`Невідомий інструмент: ${toolName}`);
            }
        }
        catch (error) {
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
    async handleRelease(args) {
        const { interactive = true, data, outputPath } = args;
        if (interactive) {
            return this.startInteractiveSession('press-release', outputPath);
        }
        else if (data) {
            return this.generateContent('press-release', data, outputPath);
        }
        else {
            throw new Error('Необхідно надати дані або використовувати інтерактивний режим');
        }
    }
    async handlePoint(args) {
        const { interactive = true, data, outputPath } = args;
        if (interactive) {
            return this.startInteractiveSession('project-point', outputPath);
        }
        else if (data) {
            return this.generateContent('project-point', data, outputPath);
        }
        else {
            throw new Error('Необхідно надати дані або використовувати інтерактивний режим');
        }
    }
    async handleListPrompts(args) {
        const { category } = args;
        let prompts = this.contentGenerator.getAllPrompts();
        if (category) {
            prompts = this.contentGenerator.getPromptsByCategory(category);
        }
        const promptsList = prompts.map(prompt => `**${prompt.name}** (ID: ${prompt.id})\n` +
            `  📂 Категорія: ${prompt.category}\n` +
            `  📝 Опис: ${prompt.description}\n` +
            `  📋 Обов'язкових полів: ${prompt.requiredFields.length}\n` +
            `  📋 Опціональних полів: ${prompt.optionalFields?.length || 0}\n` +
            `  📤 Формат: ${prompt.outputFormat}`).join('\n\n');
        return {
            content: [
                {
                    type: 'text',
                    text: `# 🛠️ Доступні промпти PM сервісу\n\n${promptsList}`,
                },
            ],
        };
    }
    async handleGetPromptInfo(args) {
        const { promptId } = args;
        const prompt = this.contentGenerator.getPrompt(promptId);
        if (!prompt) {
            throw new Error(`Промпт з ID ${promptId} не знайдено`);
        }
        const requiredFieldsList = prompt.requiredFields.map(field => `  - **${field.name}** (${field.type}): ${field.description}${field.required ? ' *обов\'язково*' : ''}`).join('\n');
        const optionalFieldsList = prompt.optionalFields?.map(field => `  - **${field.name}** (${field.type}): ${field.description}`).join('\n') || 'Немає опціональних полів';
        return {
            content: [
                {
                    type: 'text',
                    text: `# 📋 Інформація про промпт: ${prompt.name}\n\n` +
                        `**ID:** ${prompt.id}\n` +
                        `**Категорія:** ${prompt.category}\n` +
                        `**Формат виводу:** ${prompt.outputFormat}\n\n` +
                        `**Опис:**\n${prompt.description}\n\n` +
                        `## Обов'язкові поля:\n${requiredFieldsList}\n\n` +
                        `## Опціональні поля:\n${optionalFieldsList}\n\n` +
                        `**Системний промпт (перші 200 символів):**\n` +
                        `\`\`\`\n${prompt.systemPrompt.substring(0, 200)}...\n\`\`\``,
                },
            ],
        };
    }
    async handleGenerateCustom(args) {
        const { promptId, interactive = true, data, outputPath } = args;
        if (!this.contentGenerator.getPrompt(promptId)) {
            throw new Error(`Промпт з ID ${promptId} не знайдено`);
        }
        if (interactive) {
            return this.startInteractiveSession(promptId, outputPath);
        }
        else if (data) {
            return this.generateContent(promptId, data, outputPath);
        }
        else {
            throw new Error('Необхідно надати дані або використовувати інтерактивний режим');
        }
    }
    async startInteractiveSession(promptId, outputPath) {
        const prompt = this.contentGenerator.getPrompt(promptId);
        if (!prompt) {
            throw new Error(`Промпт з ID ${promptId} не знайдено`);
        }
        // Формуємо інтерактивну форму
        const formFields = this.buildInteractiveForm(prompt);
        return {
            content: [
                {
                    type: 'text',
                    text: `# 📝 Інтерактивна генерація: ${prompt.name}\n\n` +
                        `${prompt.description}\n\n` +
                        `## Будь ласка, надайте наступну інформацію:\n\n${formFields}\n\n` +
                        `**Після заповнення всіх полів, використайте команду з даними:**\n` +
                        `\`\`\`json\n{\n  "interactive": false,\n  "data": {\n    // ваші дані тут\n  }\n}\n\`\`\``,
                },
            ],
        };
    }
    buildInteractiveForm(prompt) {
        let form = '';
        form += '### 🔴 Обов\'язкові поля:\n';
        for (const field of prompt.requiredFields) {
            form += `**${field.description}** *(${field.name})*\n`;
            form += `Тип: ${field.type}\n`;
            if (field.placeholder)
                form += `Приклад: ${field.placeholder}\n`;
            if (field.options)
                form += `Варіанти: ${field.options.join(', ')}\n`;
            form += '\n';
        }
        if (prompt.optionalFields && prompt.optionalFields.length > 0) {
            form += '### ⚪ Опціональні поля:\n';
            for (const field of prompt.optionalFields) {
                form += `**${field.description}** *(${field.name})*\n`;
                form += `Тип: ${field.type}\n`;
                if (field.placeholder)
                    form += `Приклад: ${field.placeholder}\n`;
                if (field.options)
                    form += `Варіанти: ${field.options.join(', ')}\n`;
                form += '\n';
            }
        }
        return form;
    }
    async generateContent(promptId, data, outputPath) {
        // Генеруємо шлях файлу, якщо не надано
        const finalOutputPath = outputPath || this.generateDefaultOutputPath(promptId);
        const request = {
            promptId,
            data,
            outputPath: finalOutputPath
        };
        const response = await this.contentGenerator.generateContent(request);
        if (response.success) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `# ✅ Контент успішно згенеровано!\n\n` +
                            `**Тип:** ${promptId}\n` +
                            `**Файл:** ${response.outputPath}\n` +
                            `**Створено:** ${response.generatedAt.toLocaleString('uk-UA')}\n\n` +
                            `---\n\n${response.content}`,
                    },
                ],
            };
        }
        else {
            throw new Error(response.error);
        }
    }
    generateDefaultOutputPath(promptId) {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
        const filename = `${promptId}-${timestamp}`;
        return path.join(this.outputDirectory, filename);
    }
    generateJsonSchemaFromPrompt(prompt) {
        const properties = {};
        // Додаємо обов'язкові поля
        for (const field of prompt.requiredFields) {
            properties[field.name] = this.fieldToJsonSchema(field);
        }
        // Додаємо опціональні поля
        if (prompt.optionalFields) {
            for (const field of prompt.optionalFields) {
                properties[field.name] = this.fieldToJsonSchema(field);
            }
        }
        return properties;
    }
    fieldToJsonSchema(field) {
        const schema = {
            description: field.description
        };
        switch (field.type) {
            case 'text':
            case 'textarea':
                schema.type = 'string';
                if (field.validation?.minLength)
                    schema.minLength = field.validation.minLength;
                if (field.validation?.maxLength)
                    schema.maxLength = field.validation.maxLength;
                if (field.placeholder)
                    schema.example = field.placeholder;
                break;
            case 'select':
                schema.type = 'string';
                if (field.options)
                    schema.enum = field.options;
                break;
            case 'multiselect':
                schema.type = 'array';
                if (field.options) {
                    schema.items = {
                        type: 'string',
                        enum: field.options
                    };
                }
                break;
            case 'number':
                schema.type = 'number';
                break;
            case 'date':
                schema.type = 'string';
                schema.format = 'date';
                break;
        }
        return schema;
    }
}
exports.PMService = PMService;
//# sourceMappingURL=PMService.js.map