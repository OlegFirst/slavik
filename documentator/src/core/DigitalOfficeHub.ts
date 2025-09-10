import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from '@modelcontextprotocol/sdk/types.js';
import { ServiceRegistry } from './ServiceRegistry';
import { DigitalOfficeService } from '../types/ServiceInterface';

export class DigitalOfficeHub {
  private server: Server;
  private serviceRegistry: ServiceRegistry;
  private hubTools: Tool[] = [];

  constructor() {
    this.server = new Server(
      {
        name: 'digital-office',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.serviceRegistry = new ServiceRegistry();
    this.setupHubTools();
    this.setupToolHandlers();
  }

  private setupHubTools(): void {
    this.hubTools = [
      {
        name: 'list_services',
        description: 'Показує список всіх сервісів та їх статуси',
        inputSchema: {
          type: 'object',
          properties: {
            filter: {
              type: 'string',
              enum: ['all', 'enabled', 'running', 'disabled'],
              description: 'Фільтр для відображення сервісів',
              default: 'all'
            }
          }
        },
      },
      {
        name: 'service_status',
        description: 'Отримує детальний статус конкретного сервісу',
        inputSchema: {
          type: 'object',
          properties: {
            serviceName: {
              type: 'string',
              description: 'Назва сервісу для перевірки статусу',
            },
          },
          required: ['serviceName'],
        },
      },
      {
        name: 'enable_service',
        description: 'Вмикає сервіс',
        inputSchema: {
          type: 'object',
          properties: {
            serviceName: {
              type: 'string',
              description: 'Назва сервісу для включення',
            },
          },
          required: ['serviceName'],
        },
      },
      {
        name: 'disable_service',
        description: 'Вимикає сервіс',
        inputSchema: {
          type: 'object',
          properties: {
            serviceName: {
              type: 'string',
              description: 'Назва сервісу для відключення',
            },
          },
          required: ['serviceName'],
        },
      },
      {
        name: 'start_service',
        description: 'Запускає сервіс',
        inputSchema: {
          type: 'object',
          properties: {
            serviceName: {
              type: 'string',
              description: 'Назва сервісу для запуску',
            },
          },
          required: ['serviceName'],
        },
      },
      {
        name: 'stop_service',
        description: 'Зупиняє сервіс',
        inputSchema: {
          type: 'object',
          properties: {
            serviceName: {
              type: 'string',
              description: 'Назва сервісу для зупинки',
            },
          },
          required: ['serviceName'],
        },
      },
      {
        name: 'health_check',
        description: 'Виконує перевірку здоров\'я всіх запущених сервісів',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
    ];
  }

  private setupToolHandlers(): void {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      const allTools: Tool[] = [];
      
      // Додаємо інструменти хабу
      allTools.push(...this.hubTools);
      
      // Додаємо інструменти з усіх запущених сервісів
      const runningServices = this.serviceRegistry.getRunningServices();
      for (const service of runningServices) {
        const serviceTools = service.getTools();
        // Додаємо префікс сервісу до назв інструментів для унікальності
        const prefixedTools = serviceTools.map(tool => ({
          ...tool,
          name: `${service.metadata.name}:${tool.name}`,
          description: `[${service.metadata.name}] ${tool.description}`
        }));
        allTools.push(...prefixedTools);
      }

      return { tools: allTools };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const toolName = request.params.name;
      
      // Перевіряємо, чи це команда хабу
      if (this.hubTools.some(tool => tool.name === toolName)) {
        return this.handleHubToolCall(toolName, request.params.arguments);
      }
      
      // Перевіряємо, чи це команда сервісу (з префіксом)
      if (toolName.includes(':')) {
        const [serviceName, serviceToolName] = toolName.split(':', 2);
        const service = this.serviceRegistry.getService(serviceName);
        
        if (!service) {
          throw new Error(`Сервіс ${serviceName} не знайдено або не запущено`);
        }
        
        const status = this.serviceRegistry.getServiceStatus(serviceName);
        if (!status?.running) {
          throw new Error(`Сервіс ${serviceName} не запущено`);
        }
        
        return service.handleToolCall(serviceToolName, request.params.arguments);
      }
      
      throw new Error(`Невідомий інструмент: ${toolName}`);
    });
  }

  private async handleHubToolCall(toolName: string, args: any) {
    try {
      switch (toolName) {
        case 'list_services':
          return this.handleListServices(args);
        
        case 'service_status':
          return this.handleServiceStatus(args);
        
        case 'enable_service':
          return this.handleEnableService(args);
        
        case 'disable_service':
          return this.handleDisableService(args);
        
        case 'start_service':
          return this.handleStartService(args);
        
        case 'stop_service':
          return this.handleStopService(args);
        
        case 'health_check':
          return this.handleHealthCheck(args);
        
        default:
          throw new Error(`Невідомий інструмент хабу: ${toolName}`);
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

  private async handleListServices(args: any) {
    const { filter = 'all' } = args;
    const allStatuses = this.serviceRegistry.getAllServiceStatuses();
    
    let filteredStatuses = allStatuses;
    switch (filter) {
      case 'enabled':
        filteredStatuses = allStatuses.filter(s => s.enabled);
        break;
      case 'running':
        filteredStatuses = allStatuses.filter(s => s.running);
        break;
      case 'disabled':
        filteredStatuses = allStatuses.filter(s => !s.enabled);
        break;
    }
    
    if (filteredStatuses.length === 0) {
      return {
        content: [
          {
            type: 'text',
            text: `Не знайдено сервісів з фільтром "${filter}"`,
          },
        ],
      };
    }
    
    const servicesList = filteredStatuses.map(status => {
      const service = this.serviceRegistry.getService(status.name);
      const statusIcon = status.running ? '🟢' : (status.enabled ? '🟡' : '🔴');
      const healthIcon = status.healthCheck ? '💚' : (status.running ? '⚠️' : '');
      
      return `${statusIcon} **${status.name}** ${healthIcon}\n` +
             `   - Статус: ${status.enabled ? 'Увімкнено' : 'Вимкнено'} | ${status.running ? 'Запущено' : 'Зупинено'}\n` +
             `   - Опис: ${service?.metadata.description || 'Немає опису'}\n` +
             `   - Версія: ${service?.metadata.version || 'Невідома'}\n` +
             (status.lastStarted ? `   - Запущено: ${status.lastStarted.toLocaleString()}\n` : '') +
             (status.lastError ? `   - Остання помилка: ${status.lastError}\n` : '');
    }).join('\n');
    
    return {
      content: [
        {
          type: 'text',
          text: `**Digital Office Сервіси** (фільтр: ${filter})\n\n${servicesList}`,
        },
      ],
    };
  }

  private async handleServiceStatus(args: any) {
    const { serviceName } = args;
    const status = this.serviceRegistry.getServiceStatus(serviceName);
    const service = this.serviceRegistry.getService(serviceName);
    
    if (!status || !service) {
      throw new Error(`Сервіс ${serviceName} не знайдено`);
    }
    
    const tools = service.getTools();
    const toolsList = tools.length > 0 ? 
      tools.map(tool => `  - ${tool.name}: ${tool.description}`).join('\n') :
      '  Немає доступних інструментів';
    
    return {
      content: [
        {
          type: 'text',
          text: `**Статус сервісу: ${serviceName}**\n\n` +
                `📋 **Метадані:**\n` +
                `  - Назва: ${service.metadata.name}\n` +
                `  - Версія: ${service.metadata.version}\n` +
                `  - Опис: ${service.metadata.description}\n` +
                `  - Категорія: ${service.metadata.category || 'Загальна'}\n\n` +
                `⚡ **Статус:**\n` +
                `  - Увімкнено: ${status.enabled ? '✅' : '❌'}\n` +
                `  - Запущено: ${status.running ? '✅' : '❌'}\n` +
                `  - Здоров'я: ${status.healthCheck ? '💚' : (status.running ? '⚠️ Потребує перевірки' : 'N/A')}\n` +
                (status.lastStarted ? `  - Останній запуск: ${status.lastStarted.toLocaleString()}\n` : '') +
                (status.lastError ? `  - Остання помилка: ${status.lastError}\n` : '') +
                `\n🛠️ **Доступні інструменти:**\n${toolsList}`,
        },
      ],
    };
  }

  private async handleEnableService(args: any) {
    const { serviceName } = args;
    await this.serviceRegistry.enableService(serviceName);
    
    return {
      content: [
        {
          type: 'text',
          text: `✅ Сервіс ${serviceName} успішно увімкнено`,
        },
      ],
    };
  }

  private async handleDisableService(args: any) {
    const { serviceName } = args;
    await this.serviceRegistry.disableService(serviceName);
    
    return {
      content: [
        {
          type: 'text',
          text: `❌ Сервіс ${serviceName} вимкнено`,
        },
      ],
    };
  }

  private async handleStartService(args: any) {
    const { serviceName } = args;
    await this.serviceRegistry.startService(serviceName);
    
    return {
      content: [
        {
          type: 'text',
          text: `🚀 Сервіс ${serviceName} успішно запущено`,
        },
      ],
    };
  }

  private async handleStopService(args: any) {
    const { serviceName } = args;
    await this.serviceRegistry.stopService(serviceName);
    
    return {
      content: [
        {
          type: 'text',
          text: `⏹️ Сервіс ${serviceName} зупинено`,
        },
      ],
    };
  }

  private async handleHealthCheck(args: any) {
    await this.serviceRegistry.performHealthChecks();
    const statuses = this.serviceRegistry.getAllServiceStatuses()
      .filter(s => s.running);
    
    if (statuses.length === 0) {
      return {
        content: [
          {
            type: 'text',
            text: '🔍 Немає запущених сервісів для перевірки',
          },
        ],
      };
    }
    
    const healthReport = statuses.map(status => {
      const icon = status.healthCheck ? '💚' : '💔';
      return `${icon} ${status.name}: ${status.healthCheck ? 'Здоровий' : 'Потребує уваги'}`;
    }).join('\n');
    
    const healthyCount = statuses.filter(s => s.healthCheck).length;
    
    return {
      content: [
        {
          type: 'text',
          text: `🏥 **Перевірка здоров'я сервісів**\n\n` +
                `📊 **Загальна статистика:** ${healthyCount}/${statuses.length} сервісів здорові\n\n` +
                `**Детальний звіт:**\n${healthReport}`,
        },
      ],
    };
  }

  async registerService(service: DigitalOfficeService): Promise<void> {
    await this.serviceRegistry.registerService(service);
  }

  async start(): Promise<void> {
    // Запускаємо всі увімкнені сервіси
    await this.serviceRegistry.startAllEnabledServices();
    
    // Запускаємо MCP сервер
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Digital Office Hub запущено');
  }

  async shutdown(): Promise<void> {
    await this.serviceRegistry.stopAllServices();
    console.error('Digital Office Hub зупинено');
  }

  getServiceRegistry(): ServiceRegistry {
    return this.serviceRegistry;
  }
}