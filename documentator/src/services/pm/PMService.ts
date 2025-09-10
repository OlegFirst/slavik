import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { BaseService } from '../../core/BaseService';
import { ServiceMetadata } from '../../types/ServiceInterface';
import { ContentGenerator } from './ContentGenerator';
import { PRESS_RELEASE_PROMPT } from './prompts/PressReleasePrompts';
import { PROJECT_POINT_PROMPT } from './prompts/ProjectPointPrompts';
import { ContentRequest, ContentPrompt, PromptField } from './types';
import * as path from 'path';
import * as fs from 'fs-extra';

export class PMService extends BaseService {
  public metadata: ServiceMetadata = {
    name: 'pm',
    version: '1.0.0',
    description: 'Просунутий генератор текстового контенту з потужними системними промптами для PR та проект-менеджменту',
    author: 'Digital Office Team',
    category: 'Контент і комунікації'
  };

  private contentGenerator!: ContentGenerator;
  private outputDirectory: string;

  constructor() {
    super();
    this.outputDirectory = path.join(process.cwd(), 'output', 'pm');
  }

  protected async onInitialize(): Promise<void> {
    this.contentGenerator = new ContentGenerator();
    
    // Реєструємо вбудовані промпти
    this.contentGenerator.registerPrompt(PRESS_RELEASE_PROMPT);
    this.contentGenerator.registerPrompt(PROJECT_POINT_PROMPT);
    
    // Створюємо директорію для виводу
    await fs.ensureDir(this.outputDirectory);
    
    console.log('PMService: Генератор контенту ініціалізовано');
  }

  protected async onShutdown(): Promise<void> {
    console.log('PMService: Сервіс зупинено');
  }

  protected async performHealthCheck(): Promise<boolean> {
    try {
      // Перевіряємо доступність директорії та базових промптів
      await fs.access(this.outputDirectory);
      const prompts = this.contentGenerator.getAllPrompts();
      return prompts.length > 0;
    } catch (error) {
      console.error('PMService health check failed:', error);
      return false;
    }
  }

  public getTools(): Tool[] {
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
              properties: this.generateJsonSchemaFromPrompt(PRESS_RELEASE_PROMPT)
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
              properties: this.generateJsonSchemaFromPrompt(PROJECT_POINT_PROMPT)
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

  public async handleToolCall(toolName: string, args: any): Promise<any> {
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

  private async handleRelease(args: any) {
    const { interactive = true, data, outputPath } = args;
    
    if (interactive) {
      return this.startInteractiveSession('press-release', outputPath);
    } else if (data) {
      return this.generateContent('press-release', data, outputPath);
    } else {
      throw new Error('Необхідно надати дані або використовувати інтерактивний режим');
    }
  }

  private async handlePoint(args: any) {
    const { interactive = true, data, outputPath } = args;
    
    if (interactive) {
      return this.startInteractiveSession('project-point', outputPath);
    } else if (data) {
      return this.generateContent('project-point', data, outputPath);
    } else {
      throw new Error('Необхідно надати дані або використовувати інтерактивний режим');
    }
  }

  private async handleListPrompts(args: any) {
    const { category } = args;
    
    let prompts = this.contentGenerator.getAllPrompts();
    if (category) {
      prompts = this.contentGenerator.getPromptsByCategory(category);
    }

    const promptsList = prompts.map(prompt => 
      `**${prompt.name}** (ID: ${prompt.id})\n` +
      `  📂 Категорія: ${prompt.category}\n` +
      `  📝 Опис: ${prompt.description}\n` +
      `  📋 Обов'язкових полів: ${prompt.requiredFields.length}\n` +
      `  📋 Опціональних полів: ${prompt.optionalFields?.length || 0}\n` +
      `  📤 Формат: ${prompt.outputFormat}`
    ).join('\n\n');

    return {
      content: [
        {
          type: 'text',
          text: `# 🛠️ Доступні промпти PM сервісу\n\n${promptsList}`,
        },
      ],
    };
  }

  private async handleGetPromptInfo(args: any) {
    const { promptId } = args;
    const prompt = this.contentGenerator.getPrompt(promptId);
    
    if (!prompt) {
      throw new Error(`Промпт з ID ${promptId} не знайдено`);
    }

    const requiredFieldsList = prompt.requiredFields.map(field => 
      `  - **${field.name}** (${field.type}): ${field.description}${field.required ? ' *обов\'язково*' : ''}`
    ).join('\n');

    const optionalFieldsList = prompt.optionalFields?.map(field => 
      `  - **${field.name}** (${field.type}): ${field.description}`
    ).join('\n') || 'Немає опціональних полів';

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

  private async handleGenerateCustom(args: any) {
    const { promptId, interactive = true, data, outputPath } = args;
    
    if (!this.contentGenerator.getPrompt(promptId)) {
      throw new Error(`Промпт з ID ${promptId} не знайдено`);
    }
    
    if (interactive) {
      return this.startInteractiveSession(promptId, outputPath);
    } else if (data) {
      return this.generateContent(promptId, data, outputPath);
    } else {
      throw new Error('Необхідно надати дані або використовувати інтерактивний режим');
    }
  }

  private async startInteractiveSession(promptId: string, outputPath?: string) {
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

  private buildInteractiveForm(prompt: ContentPrompt): string {
    let form = '';
    
    form += '### 🔴 Обов\'язкові поля:\n';
    for (const field of prompt.requiredFields) {
      form += `**${field.description}** *(${field.name})*\n`;
      form += `Тип: ${field.type}\n`;
      if (field.placeholder) form += `Приклад: ${field.placeholder}\n`;
      if (field.options) form += `Варіанти: ${field.options.join(', ')}\n`;
      form += '\n';
    }
    
    if (prompt.optionalFields && prompt.optionalFields.length > 0) {
      form += '### ⚪ Опціональні поля:\n';
      for (const field of prompt.optionalFields) {
        form += `**${field.description}** *(${field.name})*\n`;
        form += `Тип: ${field.type}\n`;
        if (field.placeholder) form += `Приклад: ${field.placeholder}\n`;
        if (field.options) form += `Варіанти: ${field.options.join(', ')}\n`;
        form += '\n';
      }
    }
    
    return form;
  }

  private async generateContent(promptId: string, data: Record<string, any>, outputPath?: string) {
    // Генеруємо шлях файлу, якщо не надано
    const finalOutputPath = outputPath || this.generateDefaultOutputPath(promptId);
    
    const request: ContentRequest = {
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
    } else {
      throw new Error(response.error);
    }
  }

  private generateDefaultOutputPath(promptId: string): string {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
    const filename = `${promptId}-${timestamp}`;
    return path.join(this.outputDirectory, filename);
  }

  private generateJsonSchemaFromPrompt(prompt: ContentPrompt): any {
    const properties: any = {};
    
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

  private fieldToJsonSchema(field: PromptField): any {
    const schema: any = {
      description: field.description
    };

    switch (field.type) {
      case 'text':
      case 'textarea':
        schema.type = 'string';
        if (field.validation?.minLength) schema.minLength = field.validation.minLength;
        if (field.validation?.maxLength) schema.maxLength = field.validation.maxLength;
        if (field.placeholder) schema.example = field.placeholder;
        break;
      
      case 'select':
        schema.type = 'string';
        if (field.options) schema.enum = field.options;
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